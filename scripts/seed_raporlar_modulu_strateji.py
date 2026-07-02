# -*- coding: utf-8 -*-
"""Sistem taraması bulgusu (2026-07-02): raporlar modülü (101 route — CFO/CHRO/COO
panoları, ESG, OKR cascade, VRIO portföy vb.) hiçbir pakete bağlı değildi, herhangi
bir @require_module koruması yoktu — tüm paket seviyeleri erişebiliyordu.

Bu script:
  1. Yeni bir `raporlar_modulu` SystemModule kaydı oluşturur (idempotent).
  2. Onu yalnızca Strateji (L3) paketine bağlar — kullanıcı kararı: "en üst pakete
     alalım L3". Başlangıç/Yönetim paketlerinde raporlar modülü artık görünmez.

Kod tarafı (micro/core/module_registry.py) zaten güncellendi: MODULES listesine
"raporlar" launcher id'si + _SYSTEM_CODE_TO_LAUNCHER_ID'ye "raporlar_modulu" → "raporlar"
eşlemesi eklendi; micro/modules/raporlar/routes*.py içindeki 101 route'a
@require_module("raporlar") uygulandı.

İdempotent: modül/paket bağı varsa tekrar eklenmez.

Kullanım:
    python scripts/seed_raporlar_modulu_strateji.py            # uygula
    python scripts/seed_raporlar_modulu_strateji.py --dry-run  # rapor, yazma
"""
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from __init__ import create_app
from extensions import db
from app.models.saas import SubscriptionPackage, SystemModule

_MODULE_CODE = "raporlar_modulu"
_MODULE_NAME = "Raporlar Modülü"
# Strateji (L3, kullanıcı kararı) + Master (full erişim — mevcut 7 gerçek tenant
# kayıp yaşamasın; §4.B'deki "Master = full, kimse modül kaybetmesin" ilkesiyle tutarlı).
_TARGET_PACKAGE_CODES = ["strateji", "master_package"]


def seed(dry_run=False):
    app = create_app()
    with app.app_context():
        if not dry_run:
            from app.utils.db_sequence import sync_pg_sequence_if_needed
            sync_pg_sequence_if_needed("system_modules", "id")

        mod = SystemModule.query.filter_by(code=_MODULE_CODE).first()
        if mod is None:
            print(f"  [modül] oluştur: {_MODULE_CODE} ({_MODULE_NAME})" + (" (DRY)" if dry_run else ""))
            if not dry_run:
                mod = SystemModule(code=_MODULE_CODE, name=_MODULE_NAME, is_active=True)
                db.session.add(mod)
                db.session.flush()
        else:
            print(f"  [modül] var: {_MODULE_CODE}")

        for pkg_code in _TARGET_PACKAGE_CODES:
            pkg = SubscriptionPackage.query.filter_by(code=pkg_code).first()
            if pkg is None:
                print(f"  HATA: paket '{pkg_code}' bulunamadı — atlandı.")
                continue
            if dry_run:
                already = _MODULE_CODE in {m.code for m in pkg.modules}
                print(f"  [paket bağı] {pkg_code} += {_MODULE_CODE}"
                      + (" (zaten var)" if already else " (DRY)"))
                continue
            already = mod in pkg.modules
            if not already:
                pkg.modules.append(mod)
                print(f"  [paket bağı] {pkg_code} += {_MODULE_CODE}")
            else:
                print(f"  [paket bağı] zaten var: {pkg_code} += {_MODULE_CODE}")

        if dry_run:
            print("\nDRY-RUN: hiçbir şey yazılmadı.")
            db.session.rollback()
        else:
            db.session.commit()
            print("\nTamamlandı.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    sys.exit(seed(dry_run=args.dry_run))
