# 00 — Yönetici Özeti: Kokpitim Uçtan Uca Denetim

> Tarih: 2026-10-10 · Salt okunur denetim. Kod, DB ve sunuculara dokunulmadı.
> Çalışma: 6 uzman ajan + pazarlama/ticari ajan + kaynakça ajanı + bağımsız denetçi.
> Etiketler: **[D]** doğrulanmış · **[K]** kaynak iddiası · **[Ç]** analitik çıkarım · **[H]** hipotez · **[Ö]** öneri · **[?]** doğrulanamadı.

## Ürün nedir?

**[D]** Kokpitim, Türk kurumları için strateji, süreç, performans göstergesi ve bireysel karne zincirini tek bir çok kiracılı SaaS'ta birleştiren bir kurumsal performans yönetimi platformudur. Flask, SQLAlchemy ve PostgreSQL üzerinde çalışır. Çalışma zamanında 851 route, yaklaşık 131 model ve 889 toplanan test vardır. K-Radar, EFQM skoru, proje portföyü, rapor seti ve sağlayıcıdan bağımsız bir AI katmanı içerir.

**[D]** Ürün kapsamı geniş ve teknik olarak olgun. Satışa hazır değil. Ödeme, self-servis kayıt ve şifre sıfırlama yok. Hiç müşteri doğrulaması yapılmamış.

## En önemli bulgular

1. **[D] Kiracılar arası dosya indirme açığı.** Kurumsal dosya indirme ucunda kurum kontrolü yok. Model alanları uyuşmadığı için uç büyük olasılıkla hata veriyor, bu da istismarı şimdilik engelliyor olabilir. Kapatılmalı.
2. **[D] Off-site yedek yok.** Yedekler uygulamayla aynı sunucuda. Test, Demo ve Yayın da aynı sunucuda. Sunucu kaybı veri kaybı demek.
3. **[D] SSRF.** AI geçidi kurumun girdiği adresi doğrulamıyor. Koruma kodu yazılmış ama bağlanmamış.
4. **[D] Düzeltmeler Yayın'da değil.** Zamanlayıcı lider kilidi ve SSRF koruması git'te izlenmeyen dosyalarda. Yaklaşık 100 dosyalık değişiklik commit edilmemiş.
5. **[D] Test güvencesi zayıf.** Tam test paketi 8 dakikada bitmedi. CI kilitli. Test ortamında kiracı koruması kapalı.
6. **[K] Rekabet.** Doğrulanan güçlü yerli rakip Bimser Ensemble. Global araçlar Türkçe arayüz, EFQM ve kamu stratejik plan odağı sunmuyor görünüyor **[Ç]**. Asıl rakip Excel ve danışmanlık.
7. **[H] Ticari model.** Kurum bazlı kademeli yıllık abonelik, ücretli kurulum ve danışman komisyonu önerildi. TL fiyat aralıkları müşteriyle test edilmedi.

## Önerilen strateji

**[Ö]** Önce güven, sonra değer döngüsü, sonra satış deneyi. İlk segment olarak danışmanlık firmaları ve KalDer eğitmenleri üzerinden EFQM veya ISO 9001 belgeli orta ölçekli firmalar seçilmeli. Kamu ve üniversite segmenti, satın alma yolu teyit edildikten sonra açılmalı. Yeni modül geliştirme ilk pilot geri bildirimine kadar durmalı.

## İlk yapılacaklar

1. Commit edilmemiş değişiklikleri gözden geçirip dalda commit etmek.
2. Yayın'da çalışan commit'i ve Redis, worker, demo bayrağı değerlerini teyit etmek.
3. Dosya indirme ve silme uçlarını kapatmak, SSRF korumasını bağlamak.
4. Off-site yedeği başlatmak ve bir geri yükleme tatbikatı yapmak.
5. İlk segmentte 10-15 keşif görüşmesi planlamak.

## Rapor dizini

| Dosya | İçerik |
|---|---|
| 01-mevcut-durum-ve-mimari.md | Mevcut durum, yığın, modül olgunluğu |
| 02-kod-kalitesi.md | Kod kalitesi, test koşusu, kural ihlalleri |
| 03-guvenlik.md | Güvenlik ve veri koruma |
| 04-performans-altyapi.md | Performans, deploy, yedek |
| 05-urun-ux.md | Ürün değeri, UX, öneriler |
| 06-rekabet-analizi.md | Rakipler ve karşılaştırma matrisi |
| 07-pazar-musteri.md | Segmentler, pazar evreni |
| 08-pazarlama-satis-plani.md | Kanallar, kazanım programı, 30/60/90 |
| 09-ticari-model.md | İş modelleri, fiyat ve finansal senaryolar |
| 10-bagimsiz-denetim.md | Çapraz doğrulama, çelişkiler |
| 11-duzeltme-eylem-plani.md | P0-P3 teknik iş listesi |
| 12-birlesik-yol-haritasi.md | 7/30/60/90 günlük ana plan |
| 13-kaynakca-kanit-kutugu.md | Kaynaklar ve doğrulama durumu |

## Tamamlanamayanlar

- Tam test paketi sonucu alınamadı.
- Sunucu, cron, env ve nginx durumu incelenmedi. Sunucuya erişilmedi.
- Legacy yüzeyin tamamında IDOR taraması ve JS XSS taraması yapılmadı.
- Yerli rakip taraması eksik. Bimser fiyatı, ISO 9001 belgeli firma sayısı ve KalDer üye sayısı bulunamadı.
- TAM, SAM ve SOM hesaplanmadı, çünkü kaynaklı fiyat ve ödeme isteği verisi yok.
- KVKK açısından LLM'e veri aktarımı incelenmedi.
- UX sayılarının çoğu projedeki Ekim 2026 analiz belgesinden alındı ve bağımsız doğrulanmadı.
