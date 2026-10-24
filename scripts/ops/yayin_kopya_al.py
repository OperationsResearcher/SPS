# -*- coding: utf-8 -*-
"""YAYIN'ın tam kopyasını AYRI bir yerel veritabanına alır (yerel `kokpitim_db`'ye DOKUNMAZ).

Kullanım (deploy ÖNCESİ referans ve deploy SONRASI doğrulama için aynı komut):
    python scripts/ops/yayin_kopya_al.py --db kokpitim_yayin_oncesi        # deploy'dan hemen önce
    python scripts/ops/yayin_kopya_al.py --db kokpitim_yayin_sonrasi       # deploy'dan sonra
    python scripts/ops/kurum_veri_kiyas.py kiyas kokpitim_yayin_oncesi kokpitim_yayin_sonrasi --kurum KMF

NE YAPAR: (1) Yayın'da yalnız `sudo -u postgres pg_dump` (SALT OKUNUR; kimlik bilgisi dışarı çıkmaz) +
(2) sunucudaki kullanıcı dosyalarını (uploads: kurum logoları vb.) salt okunur tar ile alır,
(3) sha256 yazar, (4) YENİ yerel DB'ye pg_restore eder. Dosyalar `backups/yayin/` altında kalır (git'e girmez):
bu dump AYNI ZAMANDA Yayın yedeğidir — silme; yerel kopya tek başına yedek DEĞİLDİR, dosyayı ayrı diske de kopyala.

GÜVENLİK: hedef DB adı `kokpitim_yayin_` ile başlamalı (ana `kokpitim_db` ezilemez); var olan DB'yi ezmek için `--yeniden`.
Yayın'a hiçbir yazma yapılmaz. Bağlantı: SSH anahtarı `C:/crt/...` (yayin_yerele_cek.py ile aynı).
"""
from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "ops"))
PG_BIN = Path(r"C:\pgdata\bin")
SSH_KEY = "C:/crt/ssh-key-2026-04-18_v4.key"
SSH_HOST = "ubuntu@129.159.30.175"
YAYIN_CONTAINER = "kokpitim-web"


def _env():
    uri = ""
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("SQLALCHEMY_DATABASE_URI="):
            uri = line.split("=", 1)[1].strip().strip("\"'")
    u = urllib.parse.urlparse(uri.replace("postgresql+psycopg2", "postgresql"))
    if u.hostname not in ("localhost", "127.0.0.1", "::1"):
        raise SystemExit("Yerel DB localhost değil")
    return u, dict(os.environ, PGPASSWORD=urllib.parse.unquote(u.password or ""), PGCLIENTENCODING="UTF8")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def instance_dosyalari(hedef: Path) -> Path | None:
    """Yayın container'ındaki kalıcı kullanıcı dosyaları (uploads vb.; `yedekler` HARİÇ) — salt okunur tar."""
    ssh = ["ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes", SSH_HOST]
    komut = f'sudo docker exec {YAYIN_CONTAINER} sh -c "cd /app/instance && tar -czf - uploads hata_kontrol_runs"'
    p = subprocess.run(ssh + [komut], capture_output=True, timeout=600)
    if p.returncode != 0 or len(p.stdout) < 50:
        print(f"  UYARI: instance dosyaları alınamadı (rc={p.returncode}): {p.stderr[-200:]!r}")
        return None
    hedef.write_bytes(p.stdout)
    return hedef


def main() -> int:
    ap = argparse.ArgumentParser(description="Yayın -> AYRI yerel DB kopyası (kokpitim_db'ye dokunmaz)")
    ap.add_argument("--db", required=True, help="hedef DB adı (kokpitim_yayin_ ile başlamalı)")
    ap.add_argument("--yeniden", action="store_true", help="hedef DB varsa silip yeniden kur")
    ap.add_argument("--dump", help="yeni dump alma; mevcut dump dosyasını yükle")
    a = ap.parse_args()
    if not a.db.startswith("kokpitim_yayin_"):
        raise SystemExit("Hedef DB adı 'kokpitim_yayin_' ile başlamalı (ana kokpitim_db korunur)")
    u, env = _env()
    psql_admin = [str(PG_BIN / "psql.exe"), "-h", u.hostname, "-U", "postgres", "-d", "postgres", "-w", "-tA"]
    var = subprocess.run(psql_admin + ["-c", f"select 1 from pg_database where datname='{a.db}'"], capture_output=True, text=True, env=env)
    if var.stdout.strip() == "1":
        if not a.yeniden:
            raise SystemExit(f"DB '{a.db}' zaten var. Ezmek için --yeniden")
        subprocess.run(psql_admin + ["-c", f'drop database "{a.db}"'], check=True, env=env)

    ts = datetime.now().strftime("%Y-%m-%d_%H%M")
    if a.dump:
        dump = Path(a.dump)
    else:
        import importlib
        m = importlib.import_module("yayin_yerele_cek")
        print("[1/4] Yayın dump (salt okunur)")
        dump = m.yayin_dump()
        print("[2/4] Yayın kullanıcı dosyaları (salt okunur)")
        inst = instance_dosyalari(m.YEDEK_DIZIN / f"yayin_instance_{ts}.tar.gz")
        if inst:
            (inst.parent / (inst.name + ".sha256")).write_text(sha256(inst) + "\n")
            print(f"  {inst.name} ({inst.stat().st_size} bayt)")
    h = sha256(dump)
    Path(str(dump) + ".sha256").write_text(h + "\n")
    print(f"  sha256: {h}")
    print(f"[3/4] Yerel DB oluştur: {a.db}")
    subprocess.run(psql_admin + ["-c", f'create database "{a.db}" owner {u.username} template template0 encoding \'UTF8\''], check=True, env=env)
    print("[4/4] pg_restore")
    r = subprocess.run([str(PG_BIN / "pg_restore.exe"), "-h", u.hostname, "-U", u.username, "-d", a.db, "--no-owner", "--no-privileges", str(dump)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=3600)
    hata = [l for l in (r.stderr or "").splitlines() if l.startswith("pg_restore: error")]
    n = subprocess.run([str(PG_BIN / "psql.exe"), "-h", u.hostname, "-U", u.username, "-d", a.db, "-tA", "-c", "select count(*) from kpi_data"],
                       capture_output=True, text=True, env=env).stdout.strip()
    print(f"  restore hata satırı: {len(hata)} | kpi_data: {n}")
    if not n.isdigit() or int(n) == 0:
        raise SystemExit("Restore doğrulanamadı (kpi_data boş)")
    print(f"\nTAMAM: {a.db}  |  dump: {dump}\nSONRAKİ: python scripts/ops/kurum_veri_kiyas.py envanter {a.db} --kurum KMF")
    return 0


if __name__ == "__main__":
    sys.exit(main())
