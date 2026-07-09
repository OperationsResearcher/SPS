# -*- coding: utf-8 -*-
"""SP (Stratejik Planlama) kartlarının short_id + description alanlarını senkronize eder.

Sorun: Yerel'de SP modülü kartlarına (SP01-SP13) Admin panelinden short_id ve
açıklama atanmıştı; bu veri hiçbir deploy'da Yayın'a taşınmadı (system_cards
kod ile gelmez, veridir — KURALLAR-MASTER §5.1). Yayın'da bu kartlar hâlâ
short_id=None, description='' durumda; (i) butonu boş açılıyordu.

Kaynak veri: scripts/_data_sp_kart_export.json (Yerel'den export edilmiş 12 kayıt).

İdempotent: code ile eşleşen kart bulunur; short_id veya description zaten
doluysa ve farklıysa üzerine yazılır (Yerel = tek doğru kaynak kabul edilir).
Kart DB'de yoksa (code hiç keşfedilmemiş) atlanır ve uyarı basılır.

Kullanım:
    python scripts/seed_sp_kart_aciklamalari.py            # uygula
    python scripts/seed_sp_kart_aciklamalari.py --dry-run  # rapor, yazma
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
from app.models.saas import SystemCard

DATA_PATH = PROJECT_ROOT / "scripts" / "_data_sp_kart_export.json"


def seed(dry_run=False):
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    app = create_app()
    with app.app_context():
        updated, already_ok, missing = 0, 0, 0

        for entry in data:
            card = SystemCard.query.filter_by(code=entry["code"]).first()
            if card is None:
                print(f"  UYARI: kart bulunamadı — {entry['code']} (atlandı, önce sayfa ziyaret edilip keşfedilmeli)")
                missing += 1
                continue

            changed = False
            if card.short_id != entry["short_id"]:
                print(f"  [{entry['code']}] short_id: {card.short_id!r} -> {entry['short_id']!r}" + (" (DRY)" if dry_run else ""))
                if not dry_run:
                    card.short_id = entry["short_id"]
                changed = True
            if card.description != entry["description"]:
                print(f"  [{entry['code']}] description güncelleniyor" + (" (DRY)" if dry_run else ""))
                if not dry_run:
                    card.description = entry["description"]
                changed = True

            if changed:
                updated += 1
            else:
                already_ok += 1

        print(f"\n  Kartlar — güncellenecek: {updated}, zaten doğru: {already_ok}, eksik: {missing}")

        if dry_run:
            print("\nDRY-RUN: hiçbir şey yazılmadı.")
            db.session.rollback()
        else:
            db.session.commit()
            print(f"\nTamamlandı. {updated} kart güncellendi.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    sys.exit(seed(dry_run=args.dry_run))
