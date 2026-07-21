"""Kurum başına BİRDEN FAZLA aktif plan yılını tekilleştirir.

SORUN (bulundu: 2026-07-21, K9 çalışması sırasında):
    `plan_years.status='active'` kurum başına TEK olmalı — `get_active_plan_year`
    (plan_year_service.py:61) böyle varsayıyor ama kısıt yok. Birden fazla
    aktif yıl varsa sorgu `ORDER BY year DESC` ile EN YÜKSEK yılı seçiyor.

    Ölçüm: 5 kurumda hem 2026 hem 2027 `active` idi. Kullanıcı 2026'da
    çalıştığını sanırken sistem sessizce 2027'yi aktif kabul ediyordu.
    2027 yıllarında HİÇ ÖLÇÜM YOKTU (yalnız yapı klonu) — yani skorlar boş
    bir yıl üzerinden hesaplanıyordu.

KULLANICI KARARI (2026-07-21): aktif kalacak yıl **2026**.

Bu script fazladan aktif yılları `draft`'a çeker. VERİ SİLMEZ — yalnız
`status` alanını değiştirir; yapı ve varsa ölçümler yerinde kalır.

Kullanım:
    python scripts/ops/cift_aktif_plan_yili_onar.py               # KONTROL
    python scripts/ops/cift_aktif_plan_yili_onar.py --calistir    # uygula
    python scripts/ops/cift_aktif_plan_yili_onar.py --calistir --yil 2026
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from sqlalchemy import text  # noqa: E402

SORGU = text("""
    SELECT py.id, py.tenant_id, t.name AS tenant_adi, py.year, py.status,
           (SELECT COUNT(*) FROM kpi_data kd
              JOIN process_kpis pk ON pk.id = kd.process_kpi_id
              JOIN processes p ON p.id = pk.process_id
             WHERE p.plan_year_id = py.id) AS olcum
    FROM plan_years py
    JOIN tenants t ON t.id = py.tenant_id
    WHERE py.status = 'active'
      AND py.tenant_id IN (
          SELECT tenant_id FROM plan_years
          WHERE status = 'active' GROUP BY tenant_id HAVING COUNT(*) > 1
      )
    ORDER BY py.tenant_id, py.year
""")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--calistir", action="store_true", help="değişikliği uygula")
    ap.add_argument("--yil", type=int, default=2026, help="aktif kalacak yıl (varsayılan 2026)")
    args = ap.parse_args()

    app = create_app()
    with app.app_context():
        satirlar = db.session.execute(SORGU).fetchall()
        if not satirlar:
            print("\n✅ Kurum başına birden fazla aktif plan yılı YOK.")
            return 0

        kurumlar: dict[int, list] = {}
        for r in satirlar:
            kurumlar.setdefault(r.tenant_id, []).append(r)

        print("\n" + "=" * 68)
        print("ÇİFT AKTİF PLAN YILI " + ("ONARIMI" if args.calistir else "KONTROLÜ (yazma yok)"))
        print(f"Aktif kalacak yıl: {args.yil}")
        print("=" * 68 + "\n")

        dusurulecek = []
        for tid, kayitlar in sorted(kurumlar.items()):
            ad = (kayitlar[0].tenant_adi or "")[:28]
            print(f"  t{tid:<4} {ad}")
            hedef_var = any(k.year == args.yil for k in kayitlar)
            for k in kayitlar:
                if k.year == args.yil:
                    print(f"      {k.year}  KALIYOR (active)   ölçüm={k.olcum}")
                elif not hedef_var:
                    print(f"      {k.year}  ⚠ {args.yil} yok — DOKUNULMUYOR   ölçüm={k.olcum}")
                else:
                    print(f"      {k.year}  → draft            ölçüm={k.olcum}")
                    dusurulecek.append(k)
            print()

        if not dusurulecek:
            print("Düşürülecek yıl yok.")
            return 0

        verili = [k for k in dusurulecek if k.olcum]
        if verili:
            print("⚠ DİKKAT — düşürülecek yıllardan bazılarında ÖLÇÜM VAR:")
            for k in verili:
                print(f"    t{k.tenant_id} {k.year}: {k.olcum} ölçüm")
            print("  (status değişikliği veri SİLMEZ, yalnız 'aktif yıl' seçimini etkiler)\n")

        if not args.calistir:
            print(f"{len(dusurulecek)} plan yılı draft'a çekilecek. Uygulamak için: --calistir")
            return 0

        db.session.execute(
            text("UPDATE plan_years SET status = 'draft' WHERE id = ANY(:ids)"),
            {"ids": [k.id for k in dusurulecek]},
        )
        db.session.commit()
        print(f"✅ {len(dusurulecek)} plan yılı draft'a çekildi.")

        kalan = db.session.execute(SORGU).fetchall()
        print(f"Onarım sonrası çift aktif kayıt: {len(kalan)}")
        return 0 if not kalan else 1


if __name__ == "__main__":
    raise SystemExit(main())
