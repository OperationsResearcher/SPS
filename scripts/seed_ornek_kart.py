# -*- coding: utf-8 -*-
"""Örnek KART seed — kart-içi veri paket-farkındalığını kanıtlamak için.

'Kurum Özet Kartları' kartı (kurum_ozet_kartlar) + 3 veri kaynağı:
  user_count     → kısıtsız (her pakette)
  process_count  → surec_performansi_karti (L2 — süreç paketi)
  strategy_count → kısıtsız (L1)

Sonuç: L1 müşterisi kartı görür ama 'Aktif Süreç' (L2) satırı düşer.
Bu, otomatik kart keşfi gelene kadar manuel örnek. İdempotent.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from __init__ import create_app
from extensions import db
from app.models.saas import SystemCard, CardDataSource, SystemComponent


def seed():
    app = create_app()
    with app.app_context():
        card = SystemCard.query.filter_by(code="kurum_ozet_kartlar").first()
        if card:
            print(f"[atla] kart zaten var (id={card.id})")
            return 0
        comp = SystemComponent.query.filter_by(code="surec_performansi_karti").first()
        card = SystemCard(
            name="Kurum Özet Kartları", code="kurum_ozet_kartlar",
            component_id=comp.id if comp else None, sira=0, is_active=True,
        )
        db.session.add(card)
        db.session.flush()
        for dk, req, lbl in [
            ("user_count", None, "Aktif Kullanıcı"),
            ("process_count", "surec_performansi_karti", "Aktif Süreç"),
            ("strategy_count", None, "Ana Strateji"),
        ]:
            db.session.add(CardDataSource(
                card_id=card.id, data_key=dk,
                required_component_code=req, label=lbl, is_active=True,
            ))
        db.session.commit()
        print(f"[ok] kart + 3 veri kaynağı eklendi (card_id={card.id})")
    return 0


if __name__ == "__main__":
    sys.exit(seed())
