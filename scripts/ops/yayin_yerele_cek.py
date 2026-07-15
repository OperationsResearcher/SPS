# -*- coding: utf-8 -*-
"""YAYIN -> YEREL veri cekme. Tek giris noktasi.

Tetikleyici: kullanici "yayindaki verileri yerele cek" der. KURALLAR-MASTER §8.6.

YON KURALI — karistirmak felakettir:
    Sema (yapi) : YEREL -> YAYIN   (alembic, kod deploy)   ⬆
    Veri        : YAYIN -> YEREL   (bu script, kopya)      ⬇
Bu script YALNIZCA asagi yonde calisir. YAYIN'A HICBIR SEY YAZMAZ — Yayin'da
yaptigi tek is `pg_dump` (salt okunur).

NEDEN LISTE YOK:
    Hicbir tablo adi bu dosyada YAZILI DEGIL. Bilerek. Elle tutulan tablo
    listesi bakilmadigi gun yalan soyler; atlanan tablo sessizce veri kaybettirir.
    (Canli ornek: scripts/ops/compare_db_counts.py 6 tablo listeliyor — 169 tablo var.)
    Onun yerine: pg_dump her seyi alir, kiyas araci her seyi pg_tables'tan sayar.
    Yeni tablo eklendiginde ikisi de otomatik kapsar. Bakim gerekmez.

AKIS:
    1. KIYAS       — "yerelde Yayin'da olmayan ne var?"  -> varsa DUR
    2. YEREL YEDEK — geri donus noktasi
    3. YAYIN DUMP  — pg_dump (salt okunur); bu dosya AYNI ZAMANDA Yayin yedegidir
    4. RESTORE     — yerele tam yazim
    5. ALEMBIC     — upgrade head (semayi geri getirir)
    6. KIYAS       — kayip dogrula

Kullanim:
    python scripts/ops/yayin_yerele_cek.py                 # KONTROL (varsayilan, yazmaz)
    python scripts/ops/yayin_yerele_cek.py --calistir      # tam akis
    python scripts/ops/yayin_yerele_cek.py --calistir --yine-de   # "yerelde fazla" varken bile
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

SSH_KEY = "C:/crt/ssh-key-2026-04-18_v4.key"
SSH_HOST = "ubuntu@129.159.30.175"
YAYIN_CONTAINER = "kokpitim-web"
YEDEK_DIZIN = ROOT / "backups" / "yayin"

# pg_dump >= 18 sart (yerel PG 18) — memory: project_yedekleme_ve_db
PG_BIN = Path(r"C:\pgdata\bin")


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H%M")


def _kos(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def _yerel_db_url() -> str:
    from config import Config
    u = os.environ.get("DATABASE_URL") or getattr(Config, "SQLALCHEMY_DATABASE_URI", "")
    if not u or not u.startswith("postgres"):
        raise RuntimeError(f"Yerel DB PostgreSQL degil / bulunamadi: {u[:30]}")
    return u


# ── 1 & 6: kiyas ──────────────────────────────────────────────────────────────
def kiyas() -> list[dict]:
    """Mevcut kiyas aracini cagirir — tablo listesini pg_tables'tan okur."""
    sys.path.insert(0, str(ROOT / "scripts" / "ops"))
    import importlib
    m = importlib.import_module("yayin_yerel_kiyas")
    return m.kiyasla(m.yayin_sayimlari(), m.yerel_sayimlari())


def _yerelde_fazla(satirlar: list[dict]) -> list[dict]:
    return [s for s in satirlar if s["durum"] == "yerelde fazla"]


# ── 2: yerel yedek ────────────────────────────────────────────────────────────
def yerel_yedek() -> Path:
    YEDEK_DIZIN.mkdir(parents=True, exist_ok=True)
    hedef = YEDEK_DIZIN / f"yerel_ONCESI_{_ts()}.dump"
    pg_dump = PG_BIN / "pg_dump.exe"
    if not pg_dump.is_file():
        raise RuntimeError(f"pg_dump yok: {pg_dump} (PG 18 sart)")
    p = _kos([str(pg_dump), "-Fc", "-f", str(hedef), _yerel_db_url()])
    if p.returncode != 0:
        raise RuntimeError(f"Yerel yedek basarisiz:\n{p.stderr[-400:]}")
    print(f"  yerel yedek: {hedef.name} ({hedef.stat().st_size/1e6:.1f} MB)")
    return hedef


# ── 3: Yayin dump (SALT OKUNUR) ───────────────────────────────────────────────
def yayin_dump() -> Path:
    """Yayin'da pg_dump. Kimlik bilgisi (DATABASE_URL) DISARI CIKARILMAZ —
    dump container'in kendi icinde uretilir, sonra dosya olarak cekilir."""
    YEDEK_DIZIN.mkdir(parents=True, exist_ok=True)
    uzak_yol = f"/tmp/yayin_{_ts()}.dump"
    hedef = YEDEK_DIZIN / f"yayin_{_ts()}.dump"

    # Container ICINDE dump — kimlik disari cikmaz
    p = _kos(["ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no", SSH_HOST,
              f'sudo docker exec {YAYIN_CONTAINER} sh -c '
              f'\'pg_dump -Fc -f {uzak_yol} "$DATABASE_URL"\''], timeout=1800)
    if p.returncode != 0:
        raise RuntimeError(f"Yayin dump basarisiz:\n{p.stderr[-400:]}")

    p = _kos(["ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no", SSH_HOST,
              f"sudo docker cp {YAYIN_CONTAINER}:{uzak_yol} {uzak_yol}"], timeout=600)
    if p.returncode != 0:
        raise RuntimeError(f"docker cp basarisiz:\n{p.stderr[-400:]}")

    p = _kos(["scp", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no",
              f"{SSH_HOST}:{uzak_yol}", str(hedef)], timeout=1800)
    if p.returncode != 0:
        raise RuntimeError(f"scp basarisiz:\n{p.stderr[-400:]}")

    # Yayin'da iz birakma
    _kos(["ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no", SSH_HOST,
          f"sudo rm -f {uzak_yol}; sudo docker exec {YAYIN_CONTAINER} rm -f {uzak_yol}"])
    print(f"  yayin dump : {hedef.name} ({hedef.stat().st_size/1e6:.1f} MB)")
    print(f"               ^ bu dosya AYNI ZAMANDA Yayin yedegidir — silme")
    return hedef


# ── 4: restore ────────────────────────────────────────────────────────────────
def restore(dump: Path) -> None:
    pg_restore = PG_BIN / "pg_restore.exe"
    if not pg_restore.is_file():
        raise RuntimeError(f"pg_restore yok: {pg_restore}")
    p = _kos([str(pg_restore), "--clean", "--if-exists", "--no-owner", "--no-privileges",
              "-d", _yerel_db_url(), str(dump)], timeout=3600)
    # pg_restore uyari verse de rc!=0 olabilir; gercek hatayi ayirt et
    if p.returncode != 0 and "error" in p.stderr.lower():
        raise RuntimeError(f"Restore basarisiz:\n{p.stderr[-600:]}")
    print("  restore tamam")


# ── 5: alembic (semayi geri getirir) ──────────────────────────────────────────
def alembic_upgrade() -> None:
    p = _kos([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=str(ROOT), timeout=900)
    if p.returncode != 0:
        raise RuntimeError(f"Alembic basarisiz:\n{p.stderr[-500:]}")
    print("  alembic upgrade head tamam")


def main() -> int:
    ap = argparse.ArgumentParser(description="Yayin -> Yerel veri cekme")
    ap.add_argument("--calistir", action="store_true", help="gercekten cek (varsayilan: yalniz kontrol)")
    ap.add_argument("--yine-de", action="store_true", help="'yerelde fazla' varken bile devam et")
    a = ap.parse_args()

    print("=" * 62)
    print("YAYIN -> YEREL veri cekme" + ("" if a.calistir else "   [KONTROL — hicbir sey yazilmaz]"))
    print("=" * 62)

    print("\n[1/6] Kiyas — yerelde Yayin'da olmayan ne var?")
    satirlar = kiyas()
    fazla = _yerelde_fazla(satirlar)
    for s in sorted(fazla, key=lambda x: x["fark"]):
        print(f"      {s['tablo']:<34} yayin={s['yayin']:<7} yerel={s['yerel']:<7} ({s['fark']:+d})")
    if not fazla:
        print("      yok — cekme guvenli")

    if not a.calistir:
        print("\nKONTROL bitti. Cekmek icin:  --calistir")
        if fazla:
            print(f"UYARI: {len(fazla)} tabloda yerel onde. Cekilirse BU SATIRLAR SILINIR.")
        return 0

    if fazla and not a.yine_de:
        print(f"\nDURDU: {len(fazla)} tabloda yerelde fazla veri var; cekme bunlari SILER.")
        print("Bilerek yapiyorsan: --yine-de")
        return 2

    print("\n[2/6] Yerel yedek (geri donus noktasi)")
    yedek = yerel_yedek()
    print("\n[3/6] Yayin dump (salt okunur)")
    dump = yayin_dump()
    print("\n[4/6] Yerele restore")
    restore(dump)
    print("\n[5/6] Alembic — sema geri")
    alembic_upgrade()
    print("\n[6/6] Kiyas — dogrulama")
    son = kiyas()
    kalan = [s for s in son if s["durum"] == "YAYINDA FAZLA"]
    if kalan:
        print(f"      UYARI: {len(kalan)} tabloda hala Yayin onde:")
        for s in kalan[:10]:
            print(f"        {s['tablo']:<34} ({s['fark']:+d})")
    else:
        print("      veri tablolari senkron")

    print("\n" + "=" * 62)
    print("TAMAM")
    print(f"  geri donus : {yedek}")
    print(f"  yayin yedek: {dump}")
    print("\nSONRAKI: seed'ler yapi tablolarini geri getirir (system_cards vb.)")
    print("         kart keşfi -> Admin > Kart Yonetimi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
