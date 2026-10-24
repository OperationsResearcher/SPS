# -*- coding: utf-8 -*-
"""Masaüstü yeni kartları: bekleyen_pg (MA21), ilk_kurulum (MA22), temel_akis.serit (TA01).

NEDEN: KalDer P5 ile gelen 3 kart kart keşfinde "yeni" bulunur; short_id/ad/açıklaması yoktur.
Mevcut MA01–MA20 numaralarına DOKUNMAZ (ana projede farklı sırayla atanmış). Yalnız boş alanları
doldurur; short_id başka kartta ise ATLAR. İdempotent. Kart keşfi (Admin > Kart Yönetimi) önce koşmalıdır.

Kullanım:  python scripts/seed_masaustu_yeni_kartlar.py
Deploy: kod deploy'u seed çalıştırmaz → Test/Yayın'da ayrıca koşulmalı (docs/kontrol/seed_calistirma_kaydi.md).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

KARTLAR = [
    (
        "masaustu.bekleyen_pg", "MA21", "Veri girişi bekleyen PG'lerim",
        "Sorumlu olduğunuz süreçlerde bu dönem için veri girişi eksik olan performans "
        "göstergelerini listeler. Her satırdan doğrudan süreç karnesine geçebilirsiniz.",
    ),
    (
        "masaustu.ilk_kurulum", "MA22", "İlk kurulum",
        "Yeni kurumun kullanıma hazırlanması için sıralı kontrol listesi: plan yılı, "
        "strateji, süreç, performans göstergesi ve ilk veri. Yalnızca yöneticilere ve "
        "tamamlanmamışsa görünür; hepsi bitince kendiliğinden kaybolur.",
    ),
    (
        "temel_akis.serit", "TA01", "Temel akış",
        "Kokpitim'in temel kullanım sırasını gösteren kısa yol şeridi: strateji, süreç ve PG, "
        "veri girişi, karne ve rapor. Yetkinize göre görünen adımlar değişir.",
    ),
]


def main() -> int:
    from app import create_app
    from extensions import db
    from app.models.saas import SystemCard

    app = create_app()
    with app.app_context():
        yazilan = atlanan = 0
        for code, short_id, ad, aciklama in KARTLAR:
            kart = SystemCard.query.filter_by(code=code).first()
            if not kart:
                print(f"  ATLANDI  {code} — system_cards'ta yok (önce kart keşfi).")
                atlanan += 1
                continue
            if not kart.short_id:
                clash = SystemCard.query.filter_by(short_id=short_id).first()
                if clash and clash.id != kart.id:
                    print(f"  ATLANDI  {code} — {short_id} başka kartta ({clash.code}).")
                    atlanan += 1
                    continue
                kart.short_id = short_id
            if ad and (not kart.name or kart.name == kart.code):
                kart.name = ad
            if aciklama and not kart.description:
                kart.description = aciklama
            yazilan += 1
            print(f"  {kart.short_id}  {code}")
        db.session.commit()
        print(f"\n{yazilan} kart işlendi" + (f", {atlanan} atlandı" if atlanan else ""))
        print("NOT: yeni açıklamalar için EN .po msgid'i gerekir (KURALLAR §5.1).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
