# -*- coding: utf-8 -*-
"""Kart+Bileşen düzeyi gating'i modül→paket zincirine bağlar.

Bağlam: kart→component eşleştirmesi (scripts/seed_kart_component_eslestirme.py)
699 karttan 671'ini 211 SystemComponent'e bağladı, ama yalnızca ilk 35 component
module_component_slugs'a (gerçek enforcement tablosu — app/__init__.py::component_visible)
kayıtlıydı. Bu script, 176 yeni component'ten modül sınırı NET olan 132'sini
kaynak kart code prefix'inden çıkarılan system_modules'e bağlar.

Bilinçli kapsam dışı bırakılanlar (module_component_slugs'a YAZILMAZ):
  - admin/ayarlar/masaustu/misc grupları (44 component) — bu modüller zaten
    _MINIMUM_MODULE_IDS veya rol-kısıtlı olarak her pakette açık; DB'de
    system_modules kaydı yok, gating anlamsız (kart görsel/i18n işi kapsamı).
  - "raporlar" grubu → performans_analitigi_modulu'ne bağlandı (kullanıcı
    kararı 2026-07-02): /reports/* route'ları kavramsal olarak analiz'in
    parçası sayıldı, ama hiçbir require_module decorator'ıyla korunmuyor —
    bu script yalnızca KART görünürlüğünü (component_visible) kısıtlar,
    route erişimini DEĞİL. Route seviyesi ayrı bir karar/iş.

İdempotent: (module_id, component_slug) birincil anahtar; zaten varsa atlanır.

Kullanım:
    python scripts/seed_component_module_gating.py            # uygula
    python scripts/seed_component_module_gating.py --dry-run  # rapor, yazma
"""
import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from __init__ import create_app
from extensions import db
from app.models.saas import SystemModule, ModuleComponentSlug, SystemComponent

DATA_PATH = PROJECT_ROOT / "scripts" / "_data_component_module_map.json"


def seed(dry_run=False):
    with open(DATA_PATH, encoding="utf-8") as f:
        comp_to_module_code = json.load(f)

    app = create_app()
    with app.app_context():
        module_code_to_id = {m.code: m.id for m in SystemModule.query.all()}
        existing_component_codes = {c.code for c in SystemComponent.query.all()}
        existing_slugs = {
            (r.module_id, r.component_slug) for r in ModuleComponentSlug.query.all()
        }

        added, missing_module, missing_component, already_ok = 0, 0, 0, 0

        for comp_code, module_code in comp_to_module_code.items():
            if comp_code not in existing_component_codes:
                print(f"  UYARI: component '{comp_code}' system_components'te yok — atlandı.")
                missing_component += 1
                continue

            module_id = module_code_to_id.get(module_code)
            if module_id is None:
                print(f"  UYARI: modül kodu '{module_code}' system_modules'te yok — atlandı.")
                missing_module += 1
                continue

            key = (module_id, comp_code)
            if key in existing_slugs:
                already_ok += 1
                continue

            print(f"  [slug] {module_code} += {comp_code}" + (" (DRY)" if dry_run else ""))
            if not dry_run:
                db.session.add(ModuleComponentSlug(module_id=module_id, component_slug=comp_code))
            added += 1

        print(
            f"\n  Eklenecek: {added}, zaten var: {already_ok}, "
            f"eksik component: {missing_component}, eksik modül: {missing_module}"
        )

        if dry_run:
            print("\nDRY-RUN: hiçbir şey yazılmadı.")
            db.session.rollback()
        else:
            db.session.commit()
            print(f"\nTamamlandı. {added} yeni module_component_slugs kaydı eklendi.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    sys.exit(seed(dry_run=args.dry_run))
