# -*- coding: utf-8 -*-
"""L2 Dal 1 — modül gating onarımı: eksik system_modules + Master Package tamamlama.

Sorun: paket gating fiilen kapalıydı. system_modules sadece sp/surec/proje/CRM
kodlarını içeriyordu; bireysel/analiz/k_radar/k_rapor/kurum için kayıt yoktu.
module_registry kod eşlemesi de `_modulu` son ekli kodları tanımıyordu.

Bu script (idempotent):
  1. Eksik 5 modülü (kurum, bireysel, analiz, k_radar, k_rapor) system_modules'a ekler.
  2. Master Package'e (full paket) bu modülleri + mevcut tüm modülleri bağlar
     → Master tenant'ları HİÇBİR modül kaybetmez (gating açılınca davranış aynı).

Eşleme onarımı (module_registry) ayrı commit. Bu script yalnızca DB seed.
"L1/L2 paket ayrımı" SONRAKİ dalın işi — bu dal yalnızca motoru çalışır yapar.

Kullanım:
    python scripts/seed_l2_module_gating.py            # uygula
    python scripts/seed_l2_module_gating.py --dry-run  # rapor, yazma
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

# Eklenecek modüller: (code, name) — code, module_registry eşlemesiyle uyumlu olmalı.
_EKLENECEK_MODULLER = [
    ("kurum_paneli_modulu", "Kurum Paneli Modülü"),
    ("bireysel_performans_modulu", "Bireysel Performans Modülü"),
    ("performans_analitigi_modulu", "Performans Analitiği Modülü"),
    ("k_radar_modulu", "K-Radar Modülü"),
    ("k_rapor_modulu", "K-Rapor Modülü"),
]

_MASTER_PACKAGE_NAME = "Master Package"


def seed(dry_run=False):
    app = create_app()
    with app.app_context():
        # 1. Eksik modülleri ekle (code UNIQUE → idempotent)
        eklenen = 0
        for code, name in _EKLENECEK_MODULLER:
            mevcut = SystemModule.query.filter_by(code=code).first()
            if mevcut:
                print(f"  [atla] system_modules: {code} zaten var")
                continue
            print(f"  [ekle] system_modules: {code}" + (" (DRY)" if dry_run else ""))
            if not dry_run:
                db.session.add(SystemModule(code=code, name=name, is_active=True))
                eklenen += 1
        if not dry_run:
            db.session.flush()  # id'ler oluşsun

        # 2. Master Package'e TÜM modülleri bağla (full paket = her şey)
        master = SubscriptionPackage.query.filter_by(name=_MASTER_PACKAGE_NAME).first()
        if not master:
            print(f"  HATA: '{_MASTER_PACKAGE_NAME}' bulunamadı — bağlama atlandı.")
            db.session.rollback()
            return 1

        mevcut_kodlar = {m.code for m in master.modules}
        baglanan = 0
        for sm in SystemModule.query.filter_by(is_active=True).all():
            if sm.code in mevcut_kodlar:
                continue
            print(f"  [bagla] Master Package += {sm.code}" + (" (DRY)" if dry_run else ""))
            if not dry_run:
                master.modules.append(sm)
                baglanan += 1

        if dry_run:
            print("\nDRY-RUN: hiçbir şey yazılmadı.")
            db.session.rollback()
        else:
            db.session.commit()
            print(f"\nTamamlandı. {eklenen} modül eklendi, {baglanan} bağ kuruldu.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    sys.exit(seed(dry_run=args.dry_run))
