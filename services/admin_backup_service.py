# -*- coding: utf-8 -*-
"""Yalnizca Admin arayüzünden kullanilan PostgreSQL yedek/restore yardimcilari."""

from __future__ import annotations

import datetime
import json
import os
import re
import tempfile
import zipfile
from pathlib import Path

from flask import current_app
from sqlalchemy import text

from app.models import db
from app.constants.canonical_schema import CANONICAL_TABLES, SUMMARY_KEYS

CONFIRM_DATA = "KOKPITIM-VERI-GERIYUKLE"
CONFIRM_FULL = "KOKPITIM-TAMSISTEM-GERIYUKLE"
_SUMMARY_METRICS = {k: CANONICAL_TABLES[k] for k in SUMMARY_KEYS}


def _project_root() -> str:
    return os.path.abspath(os.path.join(current_app.root_path, os.pardir))


def require_postgres_uri() -> str:
    uri = (current_app.config.get("SQLALCHEMY_DATABASE_URI") or "").strip()
    if not uri:
        raise RuntimeError("Veritabani URI tanimli degil.")
    low = uri.lower().lstrip()
    if low.startswith("sqlite:"):
        raise RuntimeError("Web yedekleme yalnizca PostgreSQL ile calisir.")
    if not (low.startswith("postgresql://") or low.startswith("postgresql+")):
        raise RuntimeError("Desteklenen baglanti: postgresql:// veya postgresql+sürücü://")
    return uri


def dump_data_only_sql(temp_sql: str) -> None:
    from yedekleyici import run_pg_dump

    run_pg_dump(require_postgres_uri(), temp_sql, extra_args=["--data-only"])


def dump_full_sql(temp_sql: str) -> None:
    from yedekleyici import run_pg_dump

    run_pg_dump(require_postgres_uri(), temp_sql)


def build_full_system_zip_path() -> str:
    """Gecici tam sistem zip dosyasinin yolunu döner; cagiran silmek zorunda."""
    from yedekleyici import add_project_files_to_zip

    root = _project_root()
    db_uri = require_postgres_uri()
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    inner_zip_name = f"Kokpitim_Tam_Yedek_{ts}.zip"

    fd, zip_path = tempfile.mkstemp(suffix=".zip", prefix="kokpitim_tam_")
    os.close(fd)
    try:
        with tempfile.TemporaryDirectory() as work:
            dump_abs = os.path.join(work, "postgres_dump.sql")
            dump_full_sql(dump_abs)
            meta_path = os.path.join(work, "backup_meta.json")
            with open(meta_path, "w", encoding="utf-8") as mf:
                json.dump(
                    {
                        "created_at": ts,
                        "kind": "full_system",
                        "db_uri_scheme": db_uri.split("://", 1)[0] if "://" in db_uri else "unknown",
                        "db_backup_file": "db_backup/postgres_dump.sql",
                    },
                    mf,
                    ensure_ascii=False,
                    indent=2,
                )
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                add_project_files_to_zip(zf, root, inner_zip_name)
                zf.write(dump_abs, "db_backup/postgres_dump.sql")
                zf.write(meta_path, "backup_meta.json")
    except Exception:
        try:
            os.unlink(zip_path)
        except OSError:
            pass
        raise
    return zip_path


def restore_from_sql_file(sql_path: str) -> None:
    from yedekleyici import run_psql_restore

    run_psql_restore(require_postgres_uri(), sql_path)


def restore_from_full_zip(zip_path: str) -> None:
    with tempfile.TemporaryDirectory() as work:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(work)
        sql_path = os.path.join(work, "db_backup", "postgres_dump.sql")
        if not os.path.isfile(sql_path):
            raise RuntimeError("Zip icinde db_backup/postgres_dump.sql bulunamadi.")
        restore_from_sql_file(sql_path)


def get_live_system_summary() -> dict:
    """Sistemdeki temel kayıt sayılarını döndürür."""
    out = {}
    for metric, aliases in _SUMMARY_METRICS.items():
        counts = []
        used = []
        for table in aliases:
            exists = db.session.execute(
                text(
                    "SELECT EXISTS ("
                    "SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema='public' AND table_name=:table)"
                ),
                {"table": table},
            ).scalar()
            if not exists:
                continue
            cnt = db.session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            counts.append(int(cnt or 0))
            used.append(table)
        if not counts:
            out[metric] = {"count": None, "source": None}
        else:
            # Aynı metriği temsil eden tablo ailesinde dolu olanı göster.
            best_idx = max(range(len(counts)), key=lambda i: counts[i])
            out[metric] = {"count": counts[best_idx], "source": used[best_idx]}
    return out


def _scan_sql_counts(sql_text: str) -> dict:
    counts = {metric: 0 for metric in _SUMMARY_METRICS.keys()}
    for metric, aliases in _SUMMARY_METRICS.items():
        total = 0
        for table in aliases:
            p_copy = re.compile(rf"\bCOPY\s+(?:public\.)?{re.escape(table)}\b", flags=re.IGNORECASE)
            p_ins = re.compile(rf"\bINSERT\s+INTO\s+(?:public\.)?{re.escape(table)}\b", flags=re.IGNORECASE)
            total += len(p_copy.findall(sql_text)) + len(p_ins.findall(sql_text))
        counts[metric] = total
    return counts


def preview_sql_backup(sql_path: str) -> dict:
    """Yüklenen SQL yedeğinin içerik özeti."""
    if not os.path.isfile(sql_path):
        raise RuntimeError("SQL dosyası bulunamadı.")
    with open(sql_path, "r", encoding="utf-8", errors="ignore") as f:
        txt = f.read()
    return {
        "kind": "data_or_sql",
        "size_mb": round(os.path.getsize(sql_path) / (1024 * 1024), 2),
        "table_hits": _scan_sql_counts(txt),
    }


def preview_full_zip(zip_path: str) -> dict:
    """Tam sistem zip dosyasındaki SQL/metadata özetini döndürür."""
    if not os.path.isfile(zip_path):
        raise RuntimeError("Zip dosyası bulunamadı.")
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        has_sql = "db_backup/postgres_dump.sql" in names
        meta = None
        if "backup_meta.json" in names:
            with zf.open("backup_meta.json") as f:
                try:
                    meta = json.loads(f.read().decode("utf-8", errors="ignore"))
                except Exception:
                    meta = None
        if not has_sql:
            return {
                "kind": "full_zip",
                "size_mb": round(os.path.getsize(zip_path) / (1024 * 1024), 2),
                "meta": meta,
                "table_hits": {},
                "error": "db_backup/postgres_dump.sql bulunamadı",
            }
        with zf.open("db_backup/postgres_dump.sql") as f:
            sql_text = f.read().decode("utf-8", errors="ignore")
        return {
            "kind": "full_zip",
            "size_mb": round(os.path.getsize(zip_path) / (1024 * 1024), 2),
            "meta": meta,
            "table_hits": _scan_sql_counts(sql_text),
        }


def get_post_migration_assert() -> dict:
    """Show alembic version + legacy/canonical table sanity."""
    legacy_tables = [
        "surec",
        "surec_performans_gostergesi",
        "bireysel_performans_gostergesi",
        "bireysel_faaliyet",
        "performans_gosterge_veri",
        "surec_faaliyet",
    ]
    canonical_tables = [
        "processes",
        "process_kpis",
        "kpi_data",
        "individual_performance_indicators",
        "individual_activities",
        "individual_kpi_data",
        "project",
        "task",
    ]
    alembic_version = db.session.execute(text("SELECT version_num FROM alembic_version")).scalar()
    present_legacy = []
    missing_canonical = []
    for t in legacy_tables:
        ex = db.session.execute(
            text(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                "WHERE table_schema='public' AND table_name=:t)"
            ),
            {"t": t},
        ).scalar()
        if ex:
            present_legacy.append(t)
    for t in canonical_tables:
        ex = db.session.execute(
            text(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                "WHERE table_schema='public' AND table_name=:t)"
            ),
            {"t": t},
        ).scalar()
        if not ex:
            missing_canonical.append(t)
    return {
        "alembic_version": alembic_version,
        "legacy_tables_present": present_legacy,
        "canonical_tables_missing": missing_canonical,
        "is_clean": (not present_legacy) and (not missing_canonical),
    }


def get_language_unity_status() -> dict:
    """
    Check active code paths for legacy physical schema names.
    100% means zero matches in scanned runtime paths.
    """
    root = Path(current_app.root_path).parent
    scan_dirs = [
        root / "app",
        root / "api",
        root / "main",
        root / "micro",
        root / "services",
        root / "ui",
    ]
    skip_parts = {"Yedekler", "__pycache__", ".git", "docs", "backups", "ARCHIVE"}
    skip_files = {
        "app/constants/canonical_schema.py",
        "services/admin_backup_service.py",
    }
    token_patterns = [
        r"db\.ForeignKey\(\s*['\"]surec(\.id)?['\"]",
        r"table_name\s*=\s*['\"]surec['\"]",
        r"\b(from|join|into|update)\s+surec\b",
        r"['\"]surec_performans_gostergesi['\"]",
        r"['\"]bireysel_performans_gostergesi['\"]",
        r"['\"]bireysel_faaliyet['\"]",
        r"['\"]performans_gosterge_veri['\"]",
        r"['\"]surec_faaliyet['\"]",
    ]
    regexes = [re.compile(p) for p in token_patterns]
    hits = []
    scanned_files = 0
    for base in scan_dirs:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if any(x in skip_parts for x in p.parts):
                continue
            if p.suffix.lower() not in {".py", ".html", ".js", ".ts", ".css"}:
                continue
            rel = str(p.relative_to(root)).replace("\\", "/")
            if rel in skip_files or rel.startswith("migrations/versions/"):
                continue
            scanned_files += 1
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for i, line in enumerate(txt.splitlines(), 1):
                if any(rx.search(line) for rx in regexes):
                    hits.append(
                        {
                            "file": str(p.relative_to(root)),
                            "line": i,
                            "text": line.strip()[:180],
                        }
                    )
                    if len(hits) >= 50:
                        break
            if len(hits) >= 50:
                break
        if len(hits) >= 50:
            break
    score = 100 if not hits else max(0, 100 - min(100, len(hits)))
    return {
        "score": score,
        "is_clean": len(hits) == 0,
        "scanned_files": scanned_files,
        "issues": hits,
    }
