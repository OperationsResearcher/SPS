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
    # KAYNAK: uygulamanin GERCEKTE cozdugu URL (create_app). os.environ'i ONCE
    # okumak yanlisti — shell'de takili kalan eski DATABASE_URL=sqlite yuzunden
    # script yanlis DB'yi (sqlite) goruyordu; kiyas ise create_app uzerinden
    # PostgreSQL'i kullaniyordu. Ikisi ayni kaynaktan gelmeli.
    from app import create_app
    app = create_app()
    u = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if not u or not u.startswith("postgres"):
        sema = u.split(":")[0] if u else "YOK"
        raise RuntimeError(f"Yerel DB PostgreSQL degil (sema={sema}) — pg_dump yapilamaz")
    # pg_dump/pg_restore SQLAlchemy surucü ekini (+psycopg2/+psycopg) anlamaz
    return u.replace("+psycopg2", "").replace("+psycopg", "")


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
# YAYIN DB MIMARISI (kanonik: scripts/ops/oracle/oracle_safe_deploy.sh:19):
#   PostgreSQL HOST makinede calisir (container'da DEGIL) -> `sudo -u postgres`.
#   Test/Demo farkli: onlarda DB container icinde. Bu yuzden `docker exec ...
#   pg_dump` Test'te calisti ama Yayin'da socket hatasi verdi (2026-07-16).
YAYIN_PG_DB = "kokpitim_db"   # KURALLAR-MASTER §8.1 + deploy script PG_DB


def yayin_dump() -> Path:
    """Yayin DB'sini HOST'ta `sudo -u postgres pg_dump` ile alir (kanonik yol).
    Kimlik bilgisi kullanilmaz — postgres peer-auth ile baglanir, sifre gecmez."""
    YEDEK_DIZIN.mkdir(parents=True, exist_ok=True)
    uzak_yol = f"/tmp/yayin_{_ts()}.dump"
    hedef = YEDEK_DIZIN / f"yayin_{_ts()}.dump"

    # HOST'ta dump — DB host'ta calisiyor, peer-auth (sifre yok, disari cikmaz)
    p = _kos(["ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no", SSH_HOST,
              f'sudo -u postgres pg_dump -Fc -f {uzak_yol} {YAYIN_PG_DB}'], timeout=1800)
    if p.returncode != 0:
        raise RuntimeError(f"Yayin dump basarisiz:\n{p.stderr[-400:]}")

    # postgres kullanicisinin yazdigi dosyayi cekmeden once okunur yap
    _kos(["ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no", SSH_HOST,
          f"sudo chmod 644 {uzak_yol}"])

    p = _kos(["scp", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no",
              f"{SSH_HOST}:{uzak_yol}", str(hedef)], timeout=1800)
    if p.returncode != 0:
        raise RuntimeError(f"scp basarisiz:\n{p.stderr[-400:]}")

    # Yayin'da iz birakma
    _kos(["ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no", SSH_HOST,
          f"sudo rm -f {uzak_yol}"])
    print(f"  yayin dump : {hedef.name} ({hedef.stat().st_size/1e6:.1f} MB)")
    print(f"               ^ bu dosya AYNI ZAMANDA Yayin yedegidir — silme")
    return hedef


# ── 4: restore ────────────────────────────────────────────────────────────────
def restore(dump: Path) -> None:
    """Semayi BASTAN kurar (public schema drop+create), sonra restore.

    NEDEN --clean --if-exists DEGIL: o yontem tablolari tek tek dusurup kurar
    ama FK bagimlilik sirasini cozemez -> "tenant_id=61 not present" gibi 76
    hata verdi (2026-07-16). Sema bastan bos kurulunca pg_restore FK'lari
    dogru sirada olusturur (once tum veri, sonra constraint).

    Yerel DB bozulmaz: hata olursa main() adim 2'deki yedekten geri donulur."""
    pg_restore = PG_BIN / "pg_restore.exe"
    psql = PG_BIN / "psql.exe"
    if not pg_restore.is_file():
        raise RuntimeError(f"pg_restore yok: {pg_restore}")
    url = _yerel_db_url()

    # 1) public schema'yi bastan kur — temiz zemin (FK sirasi sorunu biter)
    p = _kos([str(psql), "-d", url, "-v", "ON_ERROR_STOP=1", "-c",
              "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"], timeout=300)
    if p.returncode != 0:
        raise RuntimeError(f"Schema sifirlama basarisiz:\n{p.stderr[-400:]}")

    # 2) restore. --exit-on-error KULLANMA: Yayin'in KENDI verisi bazi FK'lari
    #    ihlal ediyor (orphan — silinmis user'a bagli kpi_data; olculdu: 202 satir,
    #    TASK-253 ile ayni). Bu FK'lar kurulamaz ve bu BEKLENEN. Alembic upgrade
    #    (adim 5) orphan'lari NULL'a cekip FK'lari dogru kurar. Restore'un bu
    #    yuzden durmasi YANLIS olurdu — veri tamamen yuklenmis olur, yalniz birkac
    #    constraint eksik kalir; onlari migration tamamlar.
    p = _kos([str(pg_restore), "--no-owner", "--no-privileges",
              "-d", url, str(dump)], timeout=3600)
    # Veri yuklendi mi? Kritik tablolari say — asil basari olcutu bu, rc degil.
    kontrol = _kos([str(psql), "-d", url, "-At", "-c",
                    "select count(*) from kpi_data"], timeout=120)
    n = (kontrol.stdout or "").strip()
    if not n.isdigit() or int(n) == 0:
        raise RuntimeError(f"Restore basarisiz — kpi_data bos/okunamiyor:\n{p.stderr[-500:]}")
    # rc!=0 olabilir (atlanmis FK'lar) ama veri geldi. FK'lari alembic tamamlar.
    print(f"  restore tamam (kpi_data={n}; eksik FK'lar alembic'te tamamlanir)")


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
