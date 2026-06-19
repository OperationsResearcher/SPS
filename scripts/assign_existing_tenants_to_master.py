# -*- coding: utf-8 -*-
"""L2 Dal 3 — mevcut TÜM tenant'ları en yüksek (full) pakete = Master Package'e ata.

Kullanıcı kararı (2026-06-19): mevcut tenant'lar full erişimli kalsın. Master
Package (13 modül) en kapsamlı paket. Paketsiz (NULL) ve farklı pakettekiler
dahil hepsi master_package'e atanır → kimse modül kaybetmez.

YENİ tenant'lar admin "Kurum Ekle" formundan paket seçer (özellik zaten var);
bu script yalnızca MEVCUT tenant'ları toplu atar.

İdempotent: zaten Master'da olan tenant atlanır.

Kullanım:
    python scripts/assign_existing_tenants_to_master.py            # uygula
    python scripts/assign_existing_tenants_to_master.py --dry-run  # rapor
"""
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from __init__ import create_app
from extensions import db
from app.models.core import Tenant
from app.models.saas import SubscriptionPackage

_HEDEF_CODE = "master_package"


def assign(dry_run=False):
    app = create_app()
    with app.app_context():
        master = SubscriptionPackage.query.filter_by(code=_HEDEF_CODE).first()
        if master is None:
            print(f"HATA: '{_HEDEF_CODE}' paketi bulunamadı.")
            return 1

        tenants = Tenant.query.all()
        degisecek = [t for t in tenants if t.package_id != master.id]
        print(f"Toplam tenant: {len(tenants)} | Master'a atanacak: {len(degisecek)} | "
              f"zaten Master: {len(tenants) - len(degisecek)}")
        for t in degisecek:
            eski = t.package_id
            print(f"  tenant {t.id} ({(t.name or '')[:30]}): {eski} -> {master.id}"
                  + (" (DRY)" if dry_run else ""))
            if not dry_run:
                t.package_id = master.id

        if dry_run:
            print("\nDRY-RUN: hiçbir şey yazılmadı.")
            db.session.rollback()
        else:
            db.session.commit()
            print(f"\nTamamlandı. {len(degisecek)} tenant Master Package'e atandı.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    sys.exit(assign(dry_run=args.dry_run))
