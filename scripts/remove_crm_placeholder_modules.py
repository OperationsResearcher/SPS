# -*- coding: utf-8 -*-
"""CRM placeholder modüllerini kalıcı olarak kaldırır (kullanıcı kararı 2026-07-02).

musteri_iliskileri_yonetimi_modulu + ileri_iliskileri_yonetimi_modulu hiçbir
zaman kod tarafında karşılık bulmadı (route/model/template/launcher kartı
yok — tek iz module_registry.py'deki bir yorum satırıydı, o da temizlendi).
DB'de yalnızca Master Package'e bağlı 2 boş system_modules kaydı olarak
duruyorlardı (§4 PAKETLEME-STRATEJISI.md satır 22: "Henüz ürün değil").

Kapsam: bu iki modülün package_modules bağı + system_modules kaydının kendisi.
module_component_slugs'ta zaten hiç kaydı yoktu (0 bileşen, doğrulandı).

İdempotent: modül zaten yoksa atlanır.

Kullanım:
    python scripts/remove_crm_placeholder_modules.py            # uygula
    python scripts/remove_crm_placeholder_modules.py --dry-run  # rapor, yazma
"""
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from __init__ import create_app
from extensions import db
from app.models.saas import SystemModule

_CODES = ["musteri_iliskileri_yonetimi_modulu", "ileri_iliskileri_yonetimi_modulu"]


def seed(dry_run=False):
    app = create_app()
    with app.app_context():
        removed, missing = 0, 0
        for code in _CODES:
            mod = SystemModule.query.filter_by(code=code).first()
            if mod is None:
                print(f"  {code}: zaten yok — atlandı.")
                missing += 1
                continue

            from sqlalchemy import text
            pkg_count = db.session.execute(
                text("SELECT count(*) FROM package_modules WHERE module_id=:m"), {"m": mod.id}
            ).scalar()
            comp_count = mod.component_slugs.count()
            print(
                f"  [sil] {code} (id={mod.id}, paket bağı={pkg_count}, bileşen={comp_count})"
                + (" (DRY)" if dry_run else "")
            )
            if not dry_run:
                db.session.delete(mod)  # cascade: package_modules + module_component_slugs
            removed += 1

        print(f"\n  Silinecek: {removed}, zaten yok: {missing}")

        if dry_run:
            print("\nDRY-RUN: hiçbir şey yazılmadı.")
            db.session.rollback()
        else:
            db.session.commit()
            print(f"\nTamamlandı. {removed} placeholder modül kaldırıldı.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    sys.exit(seed(dry_run=args.dry_run))
