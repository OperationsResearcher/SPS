# -*- coding: utf-8 -*-
"""Yonetim Ozeti sayfasi kart meta seed'i — ad + short_id + aciklama.

NEDEN: Sayfa `data-card-code` ile dogru isaretlenmisti ve kesif servisi 9 karti
da goruyordu, ama KESIF HIC KOSTURULMAMISTI -> system_cards'ta kayit yoktu ->
(i) butonu aciklama gosteremiyordu. Kod hatasi degil, ATLANMIS ADIM
(bkz. memory: seed script deploy acigi — kod deploy DB seed calistirmaz).

Kesif kaydi acar ama short_id/description ATAMAZ. Bu script onu yapar.

short_id oneki: YO (yonetim_ozeti). KART-KATMANI-TASARIM.md §Sayfa-harf
eslemesinde yoktu (yeni sayfa); YO onekinin bos oldugu DB'den dogrulandi.

Basliklar UYDURULMADI — sablondan (`ui/templates/platform/masaustu/
yonetim_ozeti.html`) okundu.

Kullanim:  python scripts/seed_yonetim_ozeti_kartlari.py
Tekrar kosturulabilir (idempotent).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# (code, short_id, ad, aciklama)
# Aciklama = (i) butonunun gosterecegi metin. Kartin NE OLDUGUNU ve
# NEREDEN geldigini anlatir — sayiyi tekrar etmez.
KARTLAR = [
    (
        "yonetim_ozeti.kurum_skoru", "YO01", "Kurum Skoru",
        "Kurumun genel performans skoru. Strateji, Süreç, Proje ve Bireysel "
        "skorlarının K-Vektör ağırlıklarıyla birleşiminden hesaplanır — düz "
        "ortalama değildir; kurumun kendi belirlediği öncelikler dikkate alınır.",
    ),
    (
        "yonetim_ozeti.ks_skoru", "YO02", "Strateji Skoru (KS)",
        "Stratejik hedeflerin gerçekleşme düzeyi. Ana ve alt stratejilere bağlı "
        "performans göstergelerinin başarı oranından üretilir.",
    ),
    (
        "yonetim_ozeti.kp_skoru", "YO03", "Süreç Skoru (KP)",
        "Süreçlerin performans düzeyi. Süreçlere bağlı performans göstergelerinin "
        "hedefe ulaşma oranından hesaplanır.",
    ),
    (
        "yonetim_ozeti.kpr_skoru", "YO04", "Proje Skoru (KPR)",
        "Proje portföyünün sağlığı. Görev tamamlanma, gecikme ve kazanılmış değer "
        "(EVM) göstergelerinden beslenir.",
    ),
    (
        "yonetim_ozeti.bireysel_skoru", "YO05", "Bireysel Skor",
        "Bireysel performans göstergelerinin ortalama başarı düzeyi. Kişi bazlı "
        "detay için Bireysel Karne ekranına bakın.",
    ),
    (
        "yonetim_ozeti.geciken_isler", "YO06", "Dikkat Gereken",
        "Süresi geçmiş ya da yaklaşan faaliyet ve görevler. Buradaki sayı "
        "artıyorsa planlama ile gerçekleşme arasında açılma var demektir.",
    ),
    (
        "yonetim_ozeti.kpi_ozet", "YO07", "KPI Özeti",
        "Performans göstergelerinin hedefe göre dağılımı: hedefte, risk altında "
        "ve hedef dışı olanların sayısı.",
    ),
    (
        "yonetim_ozeti.en_dusuk_5", "YO08", "En Düşük Performanslı Stratejiler",
        "Başarı oranı en düşük stratejiler. Müdahale önceliği belirlemek için "
        "kullanılır — en alttaki, en çok ilgi bekleyendir.",
    ),
    (
        "yonetim_ozeti.hedef_radar", "YO09", "Hedef Değişiklik Radarı",
        "Hedeflerin sonradan değiştirilip değiştirilmediğini gösterir: kim, ne "
        "zaman, hangi yönde. Dönem kapanışına yakın aşağı çekilen hedefler ayrıca "
        "işaretlenir. Yalnızca bu özelliğin devreye girdiği tarihten SONRAKİ "
        "değişiklikler görünür; geçmiş değişiklikler kayıt altında değildi.",
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
                print(f"  ATLANDI  {code} — system_cards'ta yok. "
                      f"Once kart kesfi calistirin (Admin > Kart Yonetimi > Kesfet).")
                atlanan += 1
                continue
            kart.name = ad
            kart.short_id = short_id
            kart.description = aciklama
            yazilan += 1
            print(f"  {short_id}  {ad}")
        db.session.commit()
        print(f"\n{yazilan} kart guncellendi" + (f", {atlanan} atlandi" if atlanan else ""))
        print("\nNOT: (i) modali basligi DOM'dan okur; aciklama DB'den gelir.")
        print("     Aciklama TR yazildi — EN icin .po'ya msgid eklenmeli (KURALLAR §5.1).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
