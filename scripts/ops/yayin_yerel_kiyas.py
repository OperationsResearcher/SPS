# -*- coding: utf-8 -*-
"""Yayin (referans) ile Yerel DB'yi TABLO TABLO kiyaslar — SALT OKUNUR.

Amac: "Yayinda olup yerelde olmayan veri var mi?" sorusunu cevaplamak.
Referans = YAYIN. Yerel, Yayin'a gore eksik/fazla olarak raporlanir.

BU SCRIPT HICBIR SEY YAZMAZ. Ne Yayin'a, ne yerele. Yalnizca sayar ve raporlar.
Tasima islemi AYRI bir adimdir ve kullanici acikca istemeden yapilmaz.

Tablo listesi ELLE TUTULMAZ — pg_tables'tan okunur (169 tablo; elle liste
kacinilmaz sekilde bayatlar).

Kullanim:
    python scripts/ops/yayin_yerel_kiyas.py                # ozet
    python scripts/ops/yayin_yerel_kiyas.py --tam          # bos tablolar dahil
    python scripts/ops/yayin_yerel_kiyas.py --out rapor.md

Yayin'a erisim: SSH -> `docker exec kokpitim-web python`. Kimlik bilgisi
(DATABASE_URL) DISARI CIKARILMAZ; sorgu container'in kendi icinde kosar.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

SSH_KEY = "C:/crt/ssh-key-2026-04-18_v4.key"
SSH_HOST = "ubuntu@129.159.30.175"
YAYIN_CONTAINER = "kokpitim-web"

# Bu tablolar kiyasa girmez — ortama ozgu, farkli olmalari NORMAL.
YOKSAY = {
    "alembic_version",      # migration pozisyonu; ortamlar arasi farkli olabilir
    "flask_sessions",       # oturum verisi
    "audit_logs",           # ortamin kendi izi
    "user_activity_logs",   # ortamin kendi izi
}

# Sayim sorgusu — iki tarafta da AYNI kodu kosturuyoruz ki elma-elma olsun.
SAYIM_KODU = r"""
import json
from app import create_app
from extensions import db
import sqlalchemy as sa

a = create_app()
with a.app_context():
    tablolar = [r[0] for r in db.session.execute(sa.text(
        "select tablename from pg_tables where schemaname='public' order by 1"
    )).fetchall()]
    sonuc = {}
    for t in tablolar:
        try:
            sonuc[t] = int(db.session.execute(
                sa.text('select count(*) from "%s"' % t)
            ).scalar())
        except Exception as e:
            sonuc[t] = 'hata:' + type(e).__name__
    print('@@JSON@@' + json.dumps(sonuc))
"""


def _ayikla(ciktilar: str) -> dict:
    """Uygulama log'lari arasindan JSON satirini cikarir."""
    for satir in ciktilar.splitlines():
        if satir.startswith("@@JSON@@"):
            return json.loads(satir[len("@@JSON@@"):])
    raise RuntimeError("JSON satiri bulunamadi — sayim kosmadi:\n" + ciktilar[-500:])


def yayin_sayimlari() -> dict:
    """Yayin container'i ICINDE sayar. Kimlik bilgisi disari cikmaz."""
    uzak = f"sudo docker exec -i {YAYIN_CONTAINER} python -"
    p = subprocess.run(
        ["ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=20", SSH_HOST, uzak],
        input=SAYIM_KODU, capture_output=True, text=True, timeout=300,
    )
    if p.returncode != 0:
        raise RuntimeError(f"Yayin sayimi basarisiz (rc={p.returncode}):\n{p.stderr[-500:]}")
    return _ayikla(p.stdout)


def yerel_sayimlari() -> dict:
    p = subprocess.run(
        [sys.executable, "-c", SAYIM_KODU],
        capture_output=True, text=True, cwd=str(ROOT), timeout=300,
    )
    if p.returncode != 0:
        raise RuntimeError(f"Yerel sayim basarisiz:\n{p.stderr[-500:]}")
    return _ayikla(p.stdout)


def kiyasla(yayin: dict, yerel: dict) -> list[dict]:
    satirlar = []
    for t in sorted(set(yayin) | set(yerel)):
        if t in YOKSAY or t.startswith("mock_"):
            continue
        y, l = yayin.get(t, "TABLO_YOK"), yerel.get(t, "TABLO_YOK")
        if isinstance(y, int) and isinstance(l, int):
            fark = y - l
            if fark > 0:
                durum = "YAYINDA FAZLA"   # <- cekilecek veri BURADA
            elif fark < 0:
                durum = "yerelde fazla"
            else:
                durum = "ayni"
        else:
            fark, durum = None, "OKUNAMADI"
        satirlar.append({"tablo": t, "yayin": y, "yerel": l, "fark": fark, "durum": durum})
    return satirlar


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tam", action="store_true", help="iki tarafi da bos tablolari da goster")
    ap.add_argument("--out", help="Markdown rapor dosyasi")
    args = ap.parse_args()

    print("Yayin sayiliyor (salt okunur)...", flush=True)
    yayin = yayin_sayimlari()
    print(f"  {len(yayin)} tablo okundu")
    print("Yerel sayiliyor...", flush=True)
    yerel = yerel_sayimlari()
    print(f"  {len(yerel)} tablo okundu\n")

    satirlar = kiyasla(yayin, yerel)
    if not args.tam:
        satirlar = [s for s in satirlar if not (s["yayin"] == 0 and s["yerel"] == 0)]

    farkli = [s for s in satirlar if s["durum"] != "ayni"]
    cekilecek = [s for s in satirlar if s["durum"] == "YAYINDA FAZLA"]

    g = f"{'TABLO':<38} {'YAYIN':>9} {'YEREL':>9} {'FARK':>8}  DURUM"
    print(g); print("-" * len(g))
    for s in sorted(satirlar, key=lambda x: -(x["fark"] or 0)):
        if s["durum"] == "ayni" and not args.tam:
            continue
        f = "" if s["fark"] is None else f"{s['fark']:+d}"
        print(f"{s['tablo']:<38} {str(s['yayin']):>9} {str(s['yerel']):>9} {f:>8}  {s['durum']}")

    print(f"\nToplam kiyaslanan : {len(satirlar)} tablo")
    print(f"Ayni              : {len(satirlar) - len(farkli)}")
    print(f"Farkli            : {len(farkli)}")
    print(f"YAYINDA FAZLA     : {len(cekilecek)}  <- cekilmesi gerekebilecek veri")

    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        sat = ["# Yayin ↔ Yerel veri kiyasi", "",
               "> Referans = **Yayin**. Salt okunur; hicbir sey yazilmadi.", "",
               "| Tablo | Yayin | Yerel | Fark | Durum |", "|---|---:|---:|---:|---|"]
        for s in sorted(satirlar, key=lambda x: -(x["fark"] or 0)):
            f = "" if s["fark"] is None else f"{s['fark']:+d}"
            sat.append(f"| {s['tablo']} | {s['yayin']} | {s['yerel']} | {f} | {s['durum']} |")
        p.write_text("\n".join(sat) + "\n", encoding="utf-8")
        print(f"\nRapor: {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
