# -*- coding: utf-8 -*-
"""Yayin'da olup yerelde OLMAYAN PGV satirlarini yerele kopyalar.

YON: Yayin -> Yerel (KURALLAR-MASTER §8.6). Yayin'a HICBIR SEY YAZILMAZ.

ESLESTIRME
    PGV'ler dogru PG'ye baglanmali. Yerelde yil bazli KLON var (KMF: 7 yil,
    77 surec, 870 PG); Yayin'da tek yapi (11 surec, 126 PG).
    Bu yuzden hedef PG su sirayla aranir:
        1. PGV'nin yilina ait plan_year'daki ayni adli PG
        2. plan_year'i olmayan (NULL) ayni adli PG
        3. bulunamazsa satir ATLANIR ve raporlanir
    Eslestirme PG ADI + SUREC ADI uzerinden yapilir — KMF'de kodlar NULL.

Kullanim:
    python scripts/ops/pgv_eksik_cek.py                 # KONTROL
    python scripts/ops/pgv_eksik_cek.py --calistir
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

# ── Yayin'dan TUM PGV'leri oku (salt okunur) ────────────────────────────────
OKU_KODU = r'''
import json
from app import create_app
from extensions import db
import sqlalchemy as sa
a = create_app()
with a.app_context():
    rows = db.session.execute(sa.text("""
        SELECT kd.id, p.name surec_ad, pk.name pg_ad,
               kd.year, kd.period_type, kd.period_no, kd.period_month,
               kd.data_date, kd.target_value, kd.actual_value,
               kd.status, kd.status_percentage, kd.description,
               kd.is_active, kd.created_at, u.email giren
        FROM kpi_data kd
        JOIN process_kpis pk ON pk.id = kd.process_kpi_id
        JOIN processes    p  ON p.id  = pk.process_id
        JOIN tenants      t  ON t.id  = p.tenant_id
        LEFT JOIN users   u  ON u.id  = kd.user_id
        WHERE t.name ILIKE :k
    """), {"k": "%" + ARG + "%"}).fetchall()
    out = [{
        "yayin_id": r.id, "surec_ad": r.surec_ad, "pg_ad": r.pg_ad,
        "year": r.year, "period_type": r.period_type, "period_no": r.period_no,
        "period_month": r.period_month,
        "data_date": str(r.data_date) if r.data_date else None,
        "target_value": r.target_value, "actual_value": r.actual_value,
        "status": r.status,
        "status_percentage": float(r.status_percentage) if r.status_percentage is not None else None,
        "description": r.description, "is_active": bool(r.is_active),
        "created_at": str(r.created_at) if r.created_at else None,
        "giren": r.giren,
    } for r in rows]
    print("@@JSON@@" + json.dumps(out, default=str))
'''


def _sarmala(kod: str, arg: str) -> str:
    return "ARG = " + repr(arg) + "\n" + kod


def _ayikla(cikti: str) -> object:
    for s in cikti.splitlines():
        if s.startswith("@@JSON@@"):
            return json.loads(s[8:])
    raise RuntimeError("JSON yok:\n" + cikti[-600:])


def yayindan_oku(kurum: str) -> list:
    p = subprocess.run(
        ["ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=25", SSH_HOST,
         f"sudo docker exec -i {YAYIN_CONTAINER} python -"],
        input=_sarmala(OKU_KODU, kurum), capture_output=True, text=True, timeout=600)
    if p.returncode != 0:
        raise RuntimeError(f"Yayin okuma basarisiz:\n{p.stderr[-1200:]}")
    return _ayikla(p.stdout)


def anahtar(d: dict) -> str:
    return "|".join(str(d.get(k) or "") for k in
                    ("surec_ad", "pg_ad", "year", "period_type",
                     "period_no", "period_month", "data_date", "actual_value"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kurum", default="Kayseri Model Fabrika")
    ap.add_argument("--calistir", action="store_true")
    args = ap.parse_args()

    print(f"\n  {args.kurum} — eksik PGV çekimi "
          f"{'(UYGULANIYOR)' if args.calistir else '(KONTROL — yazma yok)'}\n")

    print("  1) Yayın okunuyor…")
    yayin = yayindan_oku(args.kurum)
    print(f"     {len(yayin)} PGV")

    from app import create_app
    from extensions import db
    from app.models.process import KpiData
    import sqlalchemy as sa

    app = create_app()
    with app.app_context():
        S = db.session

        # Yereldeki mevcut PGV'ler
        mevcut = S.execute(sa.text("""
            SELECT p.name surec_ad, pk.name pg_ad, kd.year, kd.period_type,
                   kd.period_no, kd.period_month, kd.data_date, kd.actual_value
            FROM kpi_data kd
            JOIN process_kpis pk ON pk.id = kd.process_kpi_id
            JOIN processes    p  ON p.id  = pk.process_id
            JOIN tenants      t  ON t.id  = p.tenant_id
            WHERE t.name ILIKE :k
        """), {"k": "%" + args.kurum + "%"}).fetchall()
        var = {anahtar({
            "surec_ad": r.surec_ad, "pg_ad": r.pg_ad, "year": r.year,
            "period_type": r.period_type, "period_no": r.period_no,
            "period_month": r.period_month,
            "data_date": str(r.data_date) if r.data_date else None,
            "actual_value": r.actual_value}) for r in mevcut}
        print(f"  2) Yerelde mevcut: {len(mevcut)} PGV ({len(var)} benzersiz)")

        eksik = [y for y in yayin if anahtar(y) not in var]
        print(f"  3) EKSİK: {len(eksik)}")

        # Yerel PG haritasi: (surec_ad, pg_ad, plan_yili) -> pg_id
        pgler = S.execute(sa.text("""
            SELECT pk.id pg_id, p.name surec_ad, pk.name pg_ad, py.year plan_yili
            FROM process_kpis pk
            JOIN processes p ON p.id = pk.process_id
            JOIN tenants   t ON t.id = p.tenant_id
            LEFT JOIN plan_years py ON py.id = p.plan_year_id
            WHERE t.name ILIKE :k AND pk.is_active
        """), {"k": "%" + args.kurum + "%"}).fetchall()
        harita: dict = {}
        for r in pgler:
            harita.setdefault((r.surec_ad, r.pg_ad, r.plan_yili), r.pg_id)

        eslesen, eslesmeyen = [], []
        for e in eksik:
            pg = (harita.get((e["surec_ad"], e["pg_ad"], e["year"]))
                  or harita.get((e["surec_ad"], e["pg_ad"], None)))
            (eslesen if pg else eslesmeyen).append((e, pg))

        print(f"  4) PG eşleşen: {len(eslesen)}   eşleşmeyen: {len(eslesmeyen)}")
        if eslesmeyen:
            from collections import Counter
            c = Counter("%s · %s · %s" % (x[0]["surec_ad"], x[0]["pg_ad"], x[0]["year"])
                        for x in eslesmeyen)
            print("     eşleşmeyenler (o yılda karşılık PG yok):")
            for ad, n in c.most_common(12):
                print(f"       {n:>3}x  {ad[:74]}")

        if not args.calistir:
            print(f"\n  {len(eslesen)} satır çekilecek. Uygulamak için: --calistir")
            return 0

        # Kullanici e-postasi -> yerel user_id
        kullanicilar = {r[0]: r[1] for r in S.execute(sa.text(
            "SELECT email, id FROM users")).fetchall()}

        n = 0
        for e, pg_id in eslesen:
            S.add(KpiData(
                process_kpi_id=pg_id, year=e["year"],
                data_date=e["data_date"], period_type=e["period_type"],
                period_no=e["period_no"], period_month=e["period_month"],
                target_value=e["target_value"], actual_value=e["actual_value"],
                status=e["status"], status_percentage=e["status_percentage"],
                description=e["description"], is_active=e["is_active"],
                user_id=kullanicilar.get(e["giren"]),
            ))
            n += 1
        S.commit()
        print(f"\n  ✅ {n} PGV yerele eklendi.")

        son = S.execute(sa.text("""
            SELECT kd.year, COUNT(*) FROM kpi_data kd
            JOIN process_kpis pk ON pk.id = kd.process_kpi_id
            JOIN processes p ON p.id = pk.process_id
            JOIN tenants t ON t.id = p.tenant_id
            WHERE t.name ILIKE :k GROUP BY 1 ORDER BY 1
        """), {"k": "%" + args.kurum + "%"}).fetchall()
        print("     yerel yıl dağılımı: " + "  ".join(f"{y}={c}" for y, c in son))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
