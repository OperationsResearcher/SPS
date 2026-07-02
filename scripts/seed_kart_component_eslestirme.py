# -*- coding: utf-8 -*-
"""Kart→Component eşleştirmesi — paket gating'in kart+veri düzeyine genişletilmesi.

Paketleme stratejisi §6 (b) — "daha çok kartı işaretle" adımının gating amaçlı sürümü.
699 system_cards kaydından 671'i (78 mevcut + 593 yeni component altında) bir
SystemComponent'e bağlanır; 28 kart pakete bağlı olmayan sabit/teknik öğe olduğu
için component_id NULL bırakılır (skip).

Kaynak veri: scripts/_data_kart_component_eslestirme.json — 10 paralel ajanın
(modül grubu başına biri) ürettiği eşleştirme, sayfa-prefix mirasıyla tamamlanmış
ve 1 bilinen hata (system_cards.id'nin component id sanılması) düzeltilmiş hâli.

İdempotent: SystemComponent code UNIQUE; kart zaten doğru component_id'ye
sahipse tekrar yazılmaz.

Kullanım:
    python scripts/seed_kart_component_eslestirme.py            # uygula
    python scripts/seed_kart_component_eslestirme.py --dry-run  # rapor, yazma
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
from app.models.saas import SystemComponent, SystemCard

DATA_PATH = PROJECT_ROOT / "scripts" / "_data_kart_component_eslestirme.json"


def seed(dry_run=False):
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    app = create_app()
    with app.app_context():
        if not dry_run:
            from app.utils.db_sequence import sync_pg_sequence_if_needed
            sync_pg_sequence_if_needed("system_components", "id")

        # 1) Yeni component'leri oluştur (code UNIQUE — idempotent)
        code_to_id = {c.code: c.id for c in SystemComponent.query.all()}
        created = 0
        for nc in data["new_components"]:
            if nc["code"] in code_to_id:
                continue
            print(f"  [component] oluştur: {nc['code']} ({nc['name']})" + (" (DRY)" if dry_run else ""))
            if dry_run:
                code_to_id[nc["code"]] = -1  # gerçek id yok, yalnızca 2. adımı "bulundu" saydırmak için
            else:
                comp = SystemComponent(code=nc["code"], name=nc["name"], is_active=True)
                db.session.add(comp)
                db.session.flush()
                code_to_id[nc["code"]] = comp.id
            created += 1

        if dry_run:
            print(f"\n  Toplam yeni component: {created}")

        # 2) Kartların component_id'sini güncelle
        cards_by_id = {c.id: c for c in SystemCard.query.all()}
        updated, already_ok, missing_card, missing_comp, skipped = 0, 0, 0, 0, 0

        for entry in data["card_assignments"]:
            if entry["mode"] == "skip" or entry["mode"] == "unresolved":
                skipped += 1
                continue

            card = cards_by_id.get(entry["card_id"])
            if card is None:
                print(f"  UYARI: card_id={entry['card_id']} ({entry['card_code']}) DB'de yok — atlandı.")
                missing_card += 1
                continue

            if entry["mode"] == "existing":
                target_component_id = entry["existing_component_id"]
            else:  # "new"
                target_component_id = code_to_id.get(entry["new_component_code"])
                if target_component_id is None:
                    print(f"  UYARI: component code '{entry['new_component_code']}' bulunamadı — atlandı.")
                    missing_comp += 1
                    continue

            if card.component_id == target_component_id:
                already_ok += 1
                continue

            if not dry_run:
                card.component_id = target_component_id
            updated += 1

        print(
            f"\n  Kartlar — güncellenecek: {updated}, zaten doğru: {already_ok}, "
            f"skip: {skipped}, eksik kart: {missing_card}, eksik component: {missing_comp}"
        )

        if dry_run:
            print("\nDRY-RUN: hiçbir şey yazılmadı.")
            db.session.rollback()
        else:
            db.session.commit()
            print(f"\nTamamlandı. {created} yeni component, {updated} kart güncellendi.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    sys.exit(seed(dry_run=args.dry_run))
