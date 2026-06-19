# -*- coding: utf-8 -*-
"""L2 Dal 2 — gerçek paketleri tanımla: Başlangıç (L1) / Yönetim (L2) / Strateji (L3).

Paketleme stratejisi §3-4 + kullanıcı kararları (2026-06-19):
  - Başlangıç (L1): kurum (kimlik) + sp (strateji ağacı dahil, modül-içi ayrım yok)
  - Yönetim (L2):  Başlangıç + surec (PG/PGV) + bireysel + proje + analiz + k_rapor
  - Strateji (L3): Yönetim + k_radar (ileri analiz / AI koçluk)
  - masaustu/ayarlar/bildirim = _MINIMUM_MODULE_IDS (her pakette otomatik açık) → eklenmez
  - admin = rol-kısıtlı (her pakette, yalnız yönetici görür) → eklenmez

Bu script YALNIZCA paketleri + modül bağlarını kurar. Tenant'ları yeni paketlere
TAŞIMAZ (mevcut Master Package tenant'ları full kalır — taşıma ayrı/bilinçli karar).

İdempotent: paket code UNIQUE; modül bağı varsa tekrar eklenmez.

Kullanım:
    python scripts/seed_l2_paketler.py            # uygula
    python scripts/seed_l2_paketler.py --dry-run  # rapor, yazma
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

# Paket tanımları: code → (ad, açıklama, system_modules.code listesi)
# Modül kodları seed_l2_module_gating.py + mevcut DB ile uyumlu.
_BASLANGIC = ["kurum_paneli_modulu", "stratejik_planlama_modulu"]
_YONETIM = _BASLANGIC + [
    "surec_yonetimi_modulu", "bireysel_performans_modulu",
    "proje_yonetimi_modulu", "performans_analitigi_modulu", "k_rapor_modulu",
]
_STRATEJI = _YONETIM + ["k_radar_modulu"]

_PAKETLER = [
    ("baslangic", "Başlangıç", "L1 — Başlat ve gör: kurum kimliği + stratejik planlama.", _BASLANGIC),
    ("yonetim", "Yönetim", "L2 — Yönet ve ölç: süreç/PG/PGV, bireysel, proje, analiz, rapor.", _YONETIM),
    ("strateji", "Strateji", "L3 — Optimize et: tüm Yönetim + K-Radar (ileri analiz/AI).", _STRATEJI),
]


def seed(dry_run=False):
    app = create_app()
    with app.app_context():
        # PG sequence drift'i (master_package id=1, seq=1 → çakışma) önle
        if not dry_run:
            from app.utils.db_sequence import sync_pg_sequence_if_needed
            sync_pg_sequence_if_needed("subscription_packages", "id")

        # Modül code → SystemModule (eksik kod = sert hata; yanlış paket kurma)
        kod_to_mod = {m.code: m for m in SystemModule.query.all()}

        for pkg_code, ad, aciklama, modul_kodlari in _PAKETLER:
            # Eksik modül kodu var mı? (önce doğrula — yarım paket kurma)
            eksik = [c for c in modul_kodlari if c not in kod_to_mod]
            if eksik:
                print(f"  HATA: '{pkg_code}' için eksik modül kodu: {eksik} — atlandı.")
                continue

            pkg = SubscriptionPackage.query.filter_by(code=pkg_code).first()
            if pkg is None:
                print(f"  [paket] oluştur: {pkg_code} ({ad})" + (" (DRY)" if dry_run else ""))
                if not dry_run:
                    pkg = SubscriptionPackage(
                        code=pkg_code, name=ad, description=aciklama, is_active=True
                    )
                    db.session.add(pkg)
                    db.session.flush()
            else:
                print(f"  [paket] var: {pkg_code} — modül bağları kontrol ediliyor")

            if dry_run:
                print(f"          modüller: {modul_kodlari}")
                continue

            mevcut = {m.code for m in pkg.modules}
            for code in modul_kodlari:
                if code in mevcut:
                    continue
                pkg.modules.append(kod_to_mod[code])
                print(f"          += {code}")

        if dry_run:
            print("\nDRY-RUN: hiçbir şey yazılmadı.")
            db.session.rollback()
        else:
            db.session.commit()
            print("\nTamamlandı. Paketler tanımlandı (tenant ataması yapılmadı).")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    sys.exit(seed(dry_run=args.dry_run))
