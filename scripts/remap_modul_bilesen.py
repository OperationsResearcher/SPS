# -*- coding: utf-8 -*-
"""Modül↔Bileşen eşlemesini temizle + doğru dağıt.

Sorun: mevcut module_component_slugs eski/karışık — 35 bileşen sadece sp+surec'e
(üstelik SWOT süreç modülünde gibi mantıksız) bağlı; kurum/k_radar/bireysel/
proje/analiz/k_rapor modüllerinde hiç bileşen yok. Ağaç bu yüzden boş görünüyor.

Bu script: TÜM module_component_slugs'ı siler, aşağıdaki temiz dağıtımı kurar.
Bileşenler anlamlarına göre doğru modüllere bağlanır (kullanıcı onaylı, 2026-06-20).

İdempotent: her koşuda sıfırlayıp yeniden kurar (tek doğru kaynak).
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from __init__ import create_app
from extensions import db
from app.models.saas import SystemModule, ModuleComponentSlug

# modül code → bileşen code listesi (temiz, anlamlı dağıtım)
MAPPING = {
    "kurum_paneli_modulu": [
        "misyon_karti", "amac_karti", "degerler_karti",
        "etik_kurallar_karti", "kalite_politikalari_karti",
    ],
    "stratejik_planlama_modulu": [
        "dinamik_stratejik_planlama", "donem_muhurleme", "revizyon_baslatma",
        "stratejik_asistan_karti", "stratejik_ilerleme_karti",
        "karar_destek_ozeti_karti", "oncelik_analizi_karti",
        "kaynak_dagilimi_karti", "interaktif_rehber_sistemi",
        "hizli_erisim_menusu_karti", "hizli_istatistikler_karti",
        "son_aktiviteler_karti", "kiyaslama",
    ],
    "ileri_stratejik_planlama_modulu": [
        "swot_analizi", "tows_analizi", "pestel_analizi",
        "porter_5_kuvvet_analizi", "ansoff_analizi", "bcg_matrisi_analizi",
        "vrio_analizi", "deger_zinciri_analizi",
    ],
    "surec_yonetimi_modulu": [
        "performans_gostergesi", "performans_gostergesi_verisi",
        "surec_performansi_karti", "surec_faaliyetleri",
        "surec_faaliyetlerim_karti", "son_faaliyetler_karti",
        "basari_puani_yapilandirmasi",
    ],
    "ileri_surec_yonetimi_modulu": [
        "surec_verimlilik_analizi_karti", "performans_trend_analizi_karti",
    ],
}


def remap(dry_run=False):
    app = create_app()
    with app.app_context():
        mod_by_code = {m.code: m for m in SystemModule.query.all()}
        # 1. mevcut tüm eşlemeyi sil
        eski = ModuleComponentSlug.query.count()
        if not dry_run:
            ModuleComponentSlug.query.delete()
            db.session.flush()
        print(f"Eski eşleme silindi: {eski} satır")

        # 2. temiz dağıtımı kur
        toplam = 0
        for mod_code, comps in MAPPING.items():
            mod = mod_by_code.get(mod_code)
            if not mod:
                print(f"  HATA: modül yok: {mod_code}")
                continue
            for ccode in comps:
                print(f"  {mod_code} += {ccode}" + (" (DRY)" if dry_run else ""))
                if not dry_run:
                    db.session.add(ModuleComponentSlug(module_id=mod.id, component_slug=ccode))
                toplam += 1

        if dry_run:
            db.session.rollback()
            print(f"\nDRY-RUN: yazılmadı. {toplam} bağ kurulacaktı.")
        else:
            db.session.commit()
            print(f"\nTamamlandı. {toplam} modül-bileşen bağı kuruldu.")
    return 0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    sys.exit(remap(dry_run=args.dry_run))
