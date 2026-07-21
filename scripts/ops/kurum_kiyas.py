# -*- coding: utf-8 -*-
"""TEK KURUMU Yayin ile Yerel arasinda kiyaslar — SALT OKUNUR.

`yayin_yerel_kiyas.py` tum tablolari sayar; bu script tek bir kurumun
(tenant) verisine odaklanir: strateji/surec/PG/olcum agaci, skor durumu,
plan yillari.

BU SCRIPT HICBIR SEY YAZMAZ. Ne Yayin'a, ne yerele.
Yayin'daki tek islem salt-okunur SELECT'lerdir.

Kurum EslesTIRME: id'ler iki tarafta FARKLI olabilir (bilinen tuzak, bkz.
CLAUDE.md "ID kaymasi"). Bu yuzden kurum ADIYLA eslesir, id ile degil.

Kullanim:
    python scripts/ops/kurum_kiyas.py "Kayseri Model Fabrika"
    python scripts/ops/kurum_kiyas.py "Kayseri" --yerel-only
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

# Iki tarafta AYNI kod kosar ki elma-elma olsun.
OLCUM_KODU = r'''
import json, sys
from app import create_app
from extensions import db
import sqlalchemy as sa

ARANAN = sys.argv[1] if len(sys.argv) > 1 else ""

a = create_app()
with a.app_context():
    S = db.session
    kurumlar = S.execute(sa.text(
        "select id, name from tenants where name ilike :p order by id"
    ), {"p": "%" + ARANAN + "%"}).fetchall()
    if not kurumlar:
        print("@@JSON@@" + json.dumps({"hata": "kurum bulunamadi", "aranan": ARANAN}))
        raise SystemExit(0)

    cikti = {"kurumlar": []}
    for tid, tad in kurumlar:
        d = {"id": tid, "ad": tad}
        tek = lambda q, **kw: S.execute(sa.text(q), dict(t=tid, **kw)).scalar()

        d["plan_yillari"] = [
            {"yil": r[0], "durum": r[1]} for r in S.execute(sa.text(
                "select year, status from plan_years where tenant_id=:t order by year"
            ), {"t": tid}).fetchall()
        ]
        d["strateji"]      = tek("select count(*) from strategies where tenant_id=:t and is_active")
        d["alt_strateji"]  = tek("""select count(*) from sub_strategies ss
                                    join strategies s on s.id=ss.strategy_id
                                    where s.tenant_id=:t and ss.is_active""")
        d["surec"]         = tek("select count(*) from processes where tenant_id=:t and is_active")
        d["pg"]            = tek("""select count(*) from process_kpis pk
                                    join processes p on p.id=pk.process_id
                                    where p.tenant_id=:t and pk.is_active""")
        d["kullanici"]     = tek("select count(*) from users where tenant_id=:t and is_active")
        d["olcum"]         = tek("""select count(*) from kpi_data kd
                                    join process_kpis pk on pk.id=kd.process_kpi_id
                                    join processes p on p.id=pk.process_id
                                    where p.tenant_id=:t""")
        d["olcum_skorsuz"] = tek("""select count(*) from kpi_data kd
                                    join process_kpis pk on pk.id=kd.process_kpi_id
                                    join processes p on p.id=pk.process_id
                                    where p.tenant_id=:t and kd.status_percentage is null""")
        d["pg_hedefsiz"]   = tek("""select count(*) from process_kpis pk
                                    join processes p on p.id=pk.process_id
                                    where p.tenant_id=:t and pk.is_active
                                      and (pk.target_value is null
                                           or btrim(pk.target_value) in ('', '-'))""")
        d["proje"]         = tek("select count(*) from project where tenant_id=:t and not is_archived")
        d["olcum_yillari"] = {
            str(r[0]): r[1] for r in S.execute(sa.text("""
                select kd.year, count(*) from kpi_data kd
                join process_kpis pk on pk.id=kd.process_kpi_id
                join processes p on p.id=pk.process_id
                where p.tenant_id=:t group by 1 order by 1
            """), {"t": tid}).fetchall()
        }
        cikti["kurumlar"].append(d)
    print("@@JSON@@" + json.dumps(cikti, default=str))
'''


def _ayikla(ciktilar: str) -> dict:
    for satir in ciktilar.splitlines():
        if satir.startswith("@@JSON@@"):
            return json.loads(satir[len("@@JSON@@"):])
    raise RuntimeError("JSON satiri bulunamadi:\n" + ciktilar[-800:])


def yayin_olcum(aranan: str) -> dict:
    uzak = f"sudo docker exec -i {YAYIN_CONTAINER} python - {aranan!r}"
    p = subprocess.run(
        ["ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=25", SSH_HOST, uzak],
        input=OLCUM_KODU, capture_output=True, text=True, timeout=300,
    )
    if p.returncode != 0:
        raise RuntimeError(f"Yayin olcumu basarisiz (rc={p.returncode}):\n{p.stderr[-800:]}")
    return _ayikla(p.stdout)


def yerel_olcum(aranan: str) -> dict:
    p = subprocess.run(
        [sys.executable, "-c", OLCUM_KODU, aranan],
        capture_output=True, text=True, cwd=str(ROOT), timeout=300,
    )
    if p.returncode != 0:
        raise RuntimeError(f"Yerel olcum basarisiz:\n{p.stderr[-800:]}")
    return _ayikla(p.stdout)


ALANLAR = [
    ("strateji", "Ana strateji"),
    ("alt_strateji", "Alt strateji"),
    ("surec", "Sürec"),
    ("pg", "Performans göstergesi"),
    ("pg_hedefsiz", "  ├ hedefi olmayan PG"),
    ("olcum", "PG ölçümü (kpi_data)"),
    ("olcum_skorsuz", "  ├ skorsuz ölçüm"),
    ("kullanici", "Kullanıcı"),
    ("proje", "Proje"),
]


def yazdir(yerel: dict, yayin: dict | None):
    yk = yerel.get("kurumlar", [])
    ak = (yayin or {}).get("kurumlar", [])
    if not yk:
        print("  ⚠ YERELDE kurum bulunamadı."); return
    if yayin and not ak:
        print("  ⚠ YAYINDA kurum bulunamadı.")

    ay_ad = {k["ad"]: k for k in ak}
    for y in yk:
        a = ay_ad.get(y["ad"])
        print("=" * 74)
        print(f"KURUM: {y['ad']}")
        print(f"  yerel id={y['id']}" + (f"   |   yayın id={a['id']}" if a else "   |   YAYINDA YOK"))
        print("=" * 74)
        print(f"{'':<30} {'YEREL':>10} {'YAYIN':>10} {'FARK':>10}")
        print("-" * 74)
        for anahtar, etiket in ALANLAR:
            yv = y.get(anahtar)
            av = a.get(anahtar) if a else None
            fark = "" if av is None else f"{(yv or 0) - (av or 0):+d}"
            isaret = "" if (av is None or yv == av) else "  ◄"
            print(f"{etiket:<30} {str(yv):>10} {str(av if a else '—'):>10} {fark:>10}{isaret}")

        def _py(kayit):
            parcalar = ["{}({})".format(p["yil"], p["durum"]) for p in kayit["plan_yillari"]]
            return ", ".join(parcalar) or "—"

        print("\n  Plan yılları")
        print("    yerel : " + _py(y))
        if a:
            print("    yayın : " + _py(a))

        print(f"\n  Ölçüm yılları (kayıt sayısı)")
        yy, ay = y.get("olcum_yillari", {}), (a or {}).get("olcum_yillari", {})
        for yil in sorted(set(yy) | set(ay)):
            yv, av = yy.get(yil, 0), ay.get(yil, 0)
            isaret = "" if (not a or yv == av) else "  ◄"
            print(f"    {yil}  yerel={yv:<8} yayın={av if a else '—':<8}{isaret}")
        print()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("kurum", help="kurum adı (kısmi eşleşme, ILIKE)")
    ap.add_argument("--yerel-only", action="store_true", help="Yayın'a bağlanma")
    args = ap.parse_args()

    print(f"\nKurum kıyası: {args.kurum!r}   (SALT OKUNUR — hiçbir şey yazılmaz)\n")
    yerel = yerel_olcum(args.kurum)
    yayin = None
    if not args.yerel_only:
        try:
            yayin = yayin_olcum(args.kurum)
        except Exception as e:
            print(f"  ⚠ Yayın'a ulaşılamadı: {e}\n  Yalnız yerel gösteriliyor.\n")
    yazdir(yerel, yayin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
