# -*- coding: utf-8 -*-
"""Bir kurumun belirli YIL(lar)a ait PGV verisini iki ortamdan da siler.

⚠ HARD DELETE — kullanici karari (2026-07-21). YAPIYA DOKUNMAZ:
   plan_year, processes, process_kpis, strategies AYNEN KALIR.
   Yalnizca `kpi_data` satirlari silinir.

   Yapiyi silmek riskli olurdu: KMF'de plan_year=2020 ana yapinin sahibi
   (11 surec / 151 PG / 6 strateji) ve diger 6 yil ondan klonlanmis —
   `source_*_id` baglari kirilirdi.

Kullanim:
    python scripts/ops/pgv_yil_sil.py --yil 2020                    # KONTROL
    python scripts/ops/pgv_yil_sil.py --yil 2020 --calistir
    python scripts/ops/pgv_yil_sil.py --yil 2020 --calistir --yalniz-yerel
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SSH_KEY = "C:/crt/ssh-key-2026-04-18_v4.key"
SSH_HOST = "ubuntu@129.159.30.175"
YAYIN_CONTAINER = "kokpitim-web"

KOD = r'''
import json
from app import create_app
from extensions import db
import sqlalchemy as sa

p = json.loads(ARG)
KURUM, YILLAR, UYGULA = p["kurum"], p["yillar"], p["uygula"]

a = create_app()
with a.app_context():
    S = db.session
    SORGU = """
        SELECT kd.id FROM kpi_data kd
        JOIN process_kpis pk ON pk.id = kd.process_kpi_id
        JOIN processes    p  ON p.id  = pk.process_id
        JOIN tenants      t  ON t.id  = p.tenant_id
        WHERE t.name ILIKE :k AND kd.year = ANY(:y)
    """
    par = {"k": "%" + KURUM + "%", "y": YILLAR}
    idler = [r[0] for r in S.execute(sa.text(SORGU), par).fetchall()]
    n = 0
    if UYGULA and idler:
        n = S.execute(sa.text("DELETE FROM kpi_data WHERE id = ANY(:i)"),
                      {"i": idler}).rowcount
        S.commit()
    kalan = len(S.execute(sa.text(SORGU), par).fetchall())
    print("@@JSON@@" + json.dumps({"bulunan": len(idler), "silinen": n, "kalan": kalan}))
'''


def _sarmala(kod: str, arg: str) -> str:
    return "ARG = " + repr(arg) + "\n" + kod


def yerelde(arg: str) -> dict:
    p = subprocess.run(
        [sys.executable, "-c", "import sys; sys.path.insert(0,'.')\n" + _sarmala(KOD, arg)],
        capture_output=True, text=True, cwd=str(ROOT), timeout=600)
    if p.returncode != 0:
        raise RuntimeError("Yerel islem basarisiz:\n" + p.stderr[-1200:])
    return _ayikla(p.stdout)


def yayinda(arg: str) -> dict:
    p = subprocess.run(
        ["ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=25", SSH_HOST,
         f"sudo docker exec -i {YAYIN_CONTAINER} python -"],
        input=_sarmala(KOD, arg), capture_output=True, text=True, timeout=600)
    if p.returncode != 0:
        raise RuntimeError(f"Yayin islemi basarisiz (rc={p.returncode}):\n{p.stderr[-1200:]}")
    return _ayikla(p.stdout)


def _ayikla(cikti: str) -> dict:
    for s in cikti.splitlines():
        if s.startswith("@@JSON@@"):
            return json.loads(s[8:])
    raise RuntimeError("JSON yok:\n" + cikti[-600:])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kurum", default="Kayseri Model Fabrika")
    ap.add_argument("--yil", type=int, nargs="+", required=True)
    ap.add_argument("--calistir", action="store_true")
    ap.add_argument("--yalniz-yerel", action="store_true")
    args = ap.parse_args()

    arg = json.dumps({"kurum": args.kurum, "yillar": args.yil, "uygula": args.calistir})
    mod = "SİLİNİYOR" if args.calistir else "KONTROL (yazma yok)"
    print(f"\n  {args.kurum} · yıl {args.yil} · PGV {mod}")
    print("  (yapı korunur: plan_year / süreç / PG / strateji SİLİNMEZ)\n")

    r1 = yerelde(arg)
    print(f"    YEREL  bulunan={r1['bulunan']:<5} silinen={r1['silinen']:<5} kalan={r1['kalan']}")
    if not args.yalniz_yerel:
        r2 = yayinda(arg)
        print(f"    YAYIN  bulunan={r2['bulunan']:<5} silinen={r2['silinen']:<5} kalan={r2['kalan']}")

    if not args.calistir:
        print("\n  Uygulamak için: --calistir")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
