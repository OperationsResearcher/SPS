# -*- coding: utf-8 -*-
"""L3 Dal 1 — ileri (advanced) modülleri Strateji paketine bağla.

Strateji (L3) tier'ı = "Optimize et ve öngör": K-Radar tam + ileri strateji
analizleri + ileri süreç/proje yetenekleri. L2 Dal 2'de Strateji paketi temel
modüllerle kuruldu ama `ileri_*` modülleri bağlanmamıştı → paket tanımı eksikti.

Bu script Strateji paketine ekler:
  - ileri_stratejik_planlama_modulu  (Porter/PESTEL/VRIO/Blue Ocean/BCG... ileri analizler)
  - ileri_surec_yonetimi_modulu       (ileri süreç analitiği)
  - ileri_proje_yonetimi_modulu       (Gantt/RAID/EVM/CPM/kapasite/portföy)

NOT: ileri_iliskileri_yonetimi_modulu (CRM) EKLENMEZ — launcher karşılığı yok
(placeholder, §4 satır 22). Eklemek gating'de işe yaramaz.

NOT: Bu modüller launcher'da sp/surec/proje'ye eşleşir (module_registry), yani
launcher YÜZEYİNİ değiştirmez (o kartlar Yönetim'den beri açık). Amaç paket
TANIMININ dürüstlüğü: "Strateji ileri yetenekleri içerir" gerçeğini DB'ye yazmak.

İdempotent: zaten bağlı modül atlanır.

Kullanım:
    python scripts/seed_l3_ileri_moduller.py            # uygula
    python scripts/seed_l3_ileri_moduller.py --dry-run  # rapor
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

_STRATEJI_CODE = "strateji"
_EKLENECEK_ILERI = [
    "ileri_stratejik_planlama_modulu",
    "ileri_surec_yonetimi_modulu",
    "ileri_proje_yonetimi_modulu",
]


def seed(dry_run=False):
    app = create_app()
    with app.app_context():
        strateji = SubscriptionPackage.query.filter_by(code=_STRATEJI_CODE).first()
        if strateji is None:
            print(f"HATA: '{_STRATEJI_CODE}' paketi bulunamadı.")
            return 1

        kod_to_mod = {m.code: m for m in SystemModule.query.all()}
        mevcut = {m.code for m in strateji.modules}

        for code in _EKLENECEK_ILERI:
            if code not in kod_to_mod:
                print(f"  HATA: '{code}' system_modules'ta yok — atlandı.")
                continue
            if code in mevcut:
                print(f"  [atla] Strateji zaten içeriyor: {code}")
                continue
            print(f"  [bagla] Strateji += {code}" + (" (DRY)" if dry_run else ""))
            if not dry_run:
                strateji.modules.append(kod_to_mod[code])

        if dry_run:
            print("\nDRY-RUN: hiçbir şey yazılmadı.")
            db.session.rollback()
        else:
            db.session.commit()
            print("\nTamamlandı. Strateji paketi ileri modüllerle güncellendi.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    sys.exit(seed(dry_run=args.dry_run))
