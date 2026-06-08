"""Yedekleme servisi (Admin Araçları > Yedekleme).

İki tip yedek:
  - Otomatik (gece 02:00): her gece TAM DB (pg_dump -Fc) + kod arşivi. Kod, bir önceki
    tam yedekten bu yana DEĞİŞEN dosyalar (fark); haftada bir TAM kod baseline. Son N tutulur.
  - Manuel: admin tıklayınca ayrı ayrı DB veya kod yedeği üretip tarayıcıya indirir.

DB: PostgreSQL (pg_dump custom format, pg_restore ile geri yüklenir).
Kod: repo dosyaları tar.gz (.git/.venv/node_modules/instance/yedekler hariç; instance/uploads dahil).
Çıktı: instance/yedekler/otomatik/. Salt operatör/Admin.
"""
from __future__ import annotations

import os
import glob
import json
import tarfile
import subprocess
import datetime
from urllib.parse import urlparse, unquote

# Kod arşivinden tamamen dışlanan dizin adları (herhangi bir seviyede)
_EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "env", "__pycache__", "node_modules",
    ".pytest_cache", ".mypy_cache", ".idea", ".vscode", ".ruff_cache",
}
# instance altında yalnız yedekler/ (backup-of-backup) ve ham db dosyaları hariç; uploads dahil.
_EXCLUDE_REL_PREFIXES = ("instance/yedekler", "instance\\yedekler")
_KEEP_LAST = 14  # rotasyon: her tür için tutulacak en son yedek sayısı


# ─── Yollar ──────────────────────────────────────────────────────────────────

def _repo_root() -> str:
    # app/services/yedekleme_service.py → repo kökü iki üst
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def base_dir(app) -> str:
    d = os.path.join(app.instance_path, "yedekler")
    os.makedirs(d, exist_ok=True)
    return d


def auto_dir(app) -> str:
    d = os.path.join(base_dir(app), "otomatik")
    os.makedirs(d, exist_ok=True)
    return d


def _state_path(app) -> str:
    return os.path.join(auto_dir(app), "_state.json")


def _load_state(app) -> dict:
    try:
        with open(_state_path(app), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_state(app, st: dict) -> None:
    with open(_state_path(app), "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)


def _ts() -> str:
    # APScheduler/manuel anında çağrılır; gerçek zaman gerekli.
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


# ─── PostgreSQL araçları ─────────────────────────────────────────────────────

_PG_BIN_CACHE: dict = {}


def _pg_dump_version(bin_dir: str) -> tuple:
    """bin_dir'deki pg_dump'ın sürümünü (major, minor) döndürür; alınamazsa (0,)."""
    try:
        exe = os.path.join(bin_dir, _exe("pg_dump")) if bin_dir else _exe("pg_dump")
        out = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=10).stdout
        nums = [int(x) for x in __import__("re").findall(r"\d+", out)][:2]
        return tuple(nums) if nums else (0,)
    except Exception:
        return (0,)


def _resolve_pg_bin() -> str:
    """pg_dump'ın bulunduğu dizin — server sürümüyle uyum için EN YÜKSEK sürüm seçilir.

    Sunucu 18 ise pg_dump da >=18 olmalı (eski pg_dump yeni sunucuyu reddeder).
    PG_BIN env > aday dizinler içinde en yüksek pg_dump sürümü > PATH.
    """
    if "dir" in _PG_BIN_CACHE:
        return _PG_BIN_CACHE["dir"]
    env = os.environ.get("PG_BIN")
    if env and os.path.isfile(os.path.join(env, _exe("pg_dump"))):
        _PG_BIN_CACHE["dir"] = env
        return env
    candidates = [r"C:\pgdata\bin"]
    for base in (r"C:\Program Files\PostgreSQL", r"C:\Program Files (x86)\PostgreSQL"):
        if os.path.isdir(base):
            for ver in os.listdir(base):
                candidates.append(os.path.join(base, ver, "bin"))
    best_dir, best_ver = "", (0,)
    for cand in candidates:
        if os.path.isfile(os.path.join(cand, _exe("pg_dump"))):
            v = _pg_dump_version(cand)
            if v > best_ver:
                best_dir, best_ver = cand, v
    _PG_BIN_CACHE["dir"] = best_dir
    return best_dir


def _exe(name: str) -> str:
    return name + (".exe" if os.name == "nt" else "")


def _pg_tool(name: str) -> str:
    d = _resolve_pg_bin()
    return os.path.join(d, _exe(name)) if d else name


def _db_conn(app) -> tuple[dict, dict]:
    """SQLALCHEMY_DATABASE_URI → (conn dict, env with PGPASSWORD)."""
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    p = urlparse(uri)
    if not p.scheme.startswith("postgresql"):
        raise RuntimeError("Yedekleme yalnız PostgreSQL içindir (mevcut URI PostgreSQL değil).")
    conn = {
        "host": p.hostname or "localhost",
        "port": str(p.port or 5432),
        "user": unquote(p.username or ""),
        "dbname": (p.path or "/").lstrip("/"),
    }
    env = dict(os.environ)
    if p.password:
        env["PGPASSWORD"] = unquote(p.password)
    return conn, env


def dump_db(app, out_path: str) -> int:
    """Tam DB yedeği (pg_dump custom format -Fc). Döner: bayt boyutu."""
    conn, env = _db_conn(app)
    cmd = [
        _pg_tool("pg_dump"), "-h", conn["host"], "-p", conn["port"],
        "-U", conn["user"], "-d", conn["dbname"],
        "-Fc", "--no-owner", "--no-privileges", "-f", out_path,
    ]
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=1800)
    if r.returncode != 0:
        raise RuntimeError(f"pg_dump hatası: {(r.stderr or '').strip()[:400]}")
    return os.path.getsize(out_path)


def restore_db(app, dump_path: str) -> None:
    """DB'yi .dump'tan geri yükler (pg_restore --clean --if-exists). YIKICI."""
    conn, env = _db_conn(app)
    cmd = [
        _pg_tool("pg_restore"), "-h", conn["host"], "-p", conn["port"],
        "-U", conn["user"], "-d", conn["dbname"],
        "--clean", "--if-exists", "--no-owner", "--no-privileges", dump_path,
    ]
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=3600)
    # pg_restore bazı uyarılarda returncode!=0 verir; stderr'i kontrol et
    if r.returncode != 0 and "errors ignored on restore" not in (r.stderr or ""):
        # Yine de ciddi hatada raise
        err = (r.stderr or "").strip()
        # tolere edilebilir uyarılar dışında gerçek hata var mı?
        if "ERROR" in err and "already exists" not in err:
            raise RuntimeError(f"pg_restore hatası: {err[:500]}")


# ─── Kod arşivi ──────────────────────────────────────────────────────────────

def _iter_code_files(root: str, baseline_mtime: float | None):
    """Repo dosyalarını gez. baseline_mtime verilirse yalnız o andan SONRA değişenler (fark)."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _EXCLUDE_DIRS]
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir != "." and rel_dir.replace("\\", "/").startswith("instance/yedekler"):
            dirnames[:] = []
            continue
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace("\\", "/")
            if rel.startswith(_EXCLUDE_REL_PREFIXES):
                continue
            if fn.endswith((".pyc", ".pyo")):
                continue
            try:
                mt = os.path.getmtime(full)
            except OSError:
                continue
            if baseline_mtime is not None and mt <= baseline_mtime:
                continue
            yield rel, full


def make_code_archive(out_path: str, baseline_mtime: float | None = None) -> tuple[int, int]:
    """Kod tar.gz üretir. baseline_mtime=None → TAM; verilirse FARK. Döner: (boyut, dosya_sayısı)."""
    root = _repo_root()
    count = 0
    with tarfile.open(out_path, "w:gz") as tar:
        for arcname, full in _iter_code_files(root, baseline_mtime):
            try:
                tar.add(full, arcname=arcname, recursive=False)
                count += 1
            except (OSError, ValueError):
                continue
    return os.path.getsize(out_path), count


# ─── Rotasyon ────────────────────────────────────────────────────────────────

def _rotate(dirpath: str, pattern: str, keep: int = _KEEP_LAST) -> int:
    files = sorted(glob.glob(os.path.join(dirpath, pattern)), key=os.path.getmtime, reverse=True)
    removed = 0
    for old in files[keep:]:
        try:
            os.remove(old)
            removed += 1
        except OSError:
            pass
    return removed


# ─── Otomatik gece yedeği ────────────────────────────────────────────────────

def run_auto_backup(app, weekly_full_dow: int = 6) -> dict:
    """Gece işi: tam DB + (haftalık tam / günlük fark) kod. weekly_full_dow: 0=Pzt..6=Paz."""
    with app.app_context():
        d = auto_dir(app)
        ts = _ts()
        result = {"ts": ts, "db": None, "code": None, "code_kind": None, "errors": []}

        # 1) Tam DB
        try:
            db_path = os.path.join(d, f"db_{ts}.dump")
            size = dump_db(app, db_path)
            result["db"] = {"file": os.path.basename(db_path), "size": size}
        except Exception as e:
            result["errors"].append(f"DB: {e}")
            try:
                app.logger.error(f"[yedekleme] otomatik DB hatası: {e}")
            except Exception:
                pass

        # 2) Kod — haftalık tam / günlük fark
        st = _load_state(app)
        last_full = st.get("last_full_code_at")  # epoch float
        now = datetime.datetime.now()
        need_full = (
            last_full is None
            or now.weekday() == weekly_full_dow
            or (now.timestamp() - float(last_full)) > 7 * 86400
        )
        try:
            kind = "tam" if need_full else "fark"
            code_path = os.path.join(d, f"code_{kind}_{ts}.tar.gz")
            baseline = None if need_full else float(last_full)
            size, cnt = make_code_archive(code_path, baseline)
            result["code"] = {"file": os.path.basename(code_path), "size": size, "files": cnt}
            result["code_kind"] = kind
            if need_full:
                st["last_full_code_at"] = now.timestamp()
                st["last_full_code_file"] = os.path.basename(code_path)
                _save_state(app, st)
        except Exception as e:
            result["errors"].append(f"Kod: {e}")
            try:
                app.logger.error(f"[yedekleme] otomatik kod hatası: {e}")
            except Exception:
                pass

        # 3) Rotasyon
        _rotate(d, "db_*.dump")
        _rotate(d, "code_tam_*.tar.gz")
        _rotate(d, "code_fark_*.tar.gz")

        st = _load_state(app)
        st["last_run_at"] = now.timestamp()
        st["last_result"] = result
        _save_state(app, st)
        try:
            app.logger.info(f"[yedekleme] otomatik tamam: {result}")
        except Exception:
            pass
        return result


def list_auto_backups(app) -> list[dict]:
    """Otomatik yedek dosyalarını (yeni→eski) döndürür."""
    d = auto_dir(app)
    out = []
    for path in sorted(glob.glob(os.path.join(d, "*.dump")) + glob.glob(os.path.join(d, "*.tar.gz")),
                       key=os.path.getmtime, reverse=True):
        name = os.path.basename(path)
        if name.startswith("db_"):
            kind = "DB (tam)"
        elif name.startswith("code_tam_"):
            kind = "Kod (tam)"
        elif name.startswith("code_fark_"):
            kind = "Kod (fark)"
        else:
            kind = "?"
        out.append({
            "file": name, "kind": kind,
            "size": os.path.getsize(path),
            "mtime": datetime.datetime.fromtimestamp(os.path.getmtime(path)).astimezone().isoformat(),
        })
    return out


def auto_status(app) -> dict:
    st = _load_state(app)
    def _iso(e):
        return datetime.datetime.fromtimestamp(float(e)).astimezone().isoformat() if e else None
    return {
        "last_run_at": _iso(st.get("last_run_at")),
        "last_full_code_at": _iso(st.get("last_full_code_at")),
        "last_result": st.get("last_result"),
        "pg_bin": _resolve_pg_bin() or "(PATH)",
    }
