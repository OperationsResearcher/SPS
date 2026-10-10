# 12 — Birleşik Yol Haritası (7 / 30 / 60 / 90 gün)

> Tarih: 2026-10-10. Teknik (11), ürün (05), pazar ve satış (07-09) ve denetim (10) birleştirildi.
> Süreler tek kişilik ekip varsayımıyladır ve taahhüt değildir. Ekip kapasitesi ve bütçe doğrulanmadı.
> Not: Proje kuralına göre tüm L paketleri bitmeden Yayın'a çıkış yok. Pilotlar Test veya Demo üzerinden yürür.

## Karar ilkesi

Önce **güven** (veri izolasyonu, yedek, test), sonra **değer döngüsü** (veri toplama, onboarding), sonra **satış deneyi**. Yeni modül geliştirme, ilk pilot geri bildirimine kadar dondurulur.

## İlk 7 gün — Gerçeği kesinleştir, acil riskleri kapat

| # | Faaliyet | Kaynak | Fayda | Efor | Tamamlanma kriteri |
|---|---|---|---|---|---|
| 1 | Commit edilmemiş ağacı gözden geçir, dalda commit et | 10, 11 P0-0 | Düzeltmeler kaybolmaz, deploy edilebilir | 1 gün | Temiz `git status` |
| 2 | Yayın commit'i ve env değerlerini (Redis, worker, demo bayrağı) teyit et | 10 belirsizlik 1-2 | Hangi bulgunun canlıda açık olduğu netleşir | 0,5 gün | Yazılı kayıt |
| 3 | Dosya indirme/silme uçlarını kapat | P0-1 | Kiracılar arası veri sızıntısı riski biter | 0,5 gün | Çapraz kurum testi 403/404 |
| 4 | SSRF korumasını LLM gateway'e bağla | P0-4 | İç ağ ve anahtar sızıntısı engellenir | 0,5 gün | Metadata IP testi reddedilir |
| 5 | Sunucudaki yedek/cron durumunu teyit et; off-site kopya başlat | P0-3 | Tek sunucu kaybında veri kurtulur | 1 gün | Off-site'ta ilk dump |
| 6 | İlk segment ve 90 günlük bütçe kararı | 10 belirsizlik 4-5 | Satış işi odaklanır | Karar | Yazılı karar |

## İlk 30 gün — Kritik düzeltmeler ve müşteri ihtiyacını doğrulama

- **Teknik:** Legacy IDOR taraması (P0-2). Test paketini bitirilebilir hale getir (P1-1, P1-2). Deploy geri alma (P1-3). Bağımlılık güncellemesi (P1-4). Restore tatbikatı.
- **Ürün:** Şifremi unuttum (P1-7). "Başlarken" rehberi ve sade ilk ekran tasarımı (05 önerisi). Uygulama için kanıt: 05'teki onboarding bulguları.
- **Pazar:** 10-15 keşif görüşmesi. Önerilen sıra (denetçi çözümü): danışmanlık firmaları ve KalDer eğitmenleri, ardından EFQM veya ISO 9001 belgeli orta ölçekli firmalar. Bimser Ensemble ve 2 global rakibin demosu.
- **Ölçüt:** Görüşmelerin en az yarısında "Excel ile strateji ve KPI takibi acı veriyor" hipotezinin teyidi. Teyit gelmezse segment değişir.

## İlk 60 gün — Değer döngüsü ve ilk pazarlama deneyleri

- **Ürün:** Veri toplama döngüsü. Dönem görevi, hatırlatma, onay ve dönem kilidi (05'in en zayıf 3. maddesi). Tek hesap motoru borcunun kapatılması.
- **Teknik:** P2 listesi. Açık yönlendirme, CSRF istisnaları, N+1, `/health` derinleştirme, migration kontrolü.
- **Satış:** 2-3 danışman ortağıyla pilot anlaşması taslağı. Demo ortamına yönlendiren 1 içerik serisi (TR SEO) ve LinkedIn erişimi. Fuar, Google Ads ve EKAP bu aşamada yok (denetçi: yüksek maliyet, düşük etki).
- **Fiyat deneyi:** 09'daki kurum bazlı kademeli abonelik, 2 fiyat noktasıyla görüşmede test edilir.

## İlk 90 gün — Pilotlar ve doğrulanmış sonuçlara göre ölçekleme

- 2-3 pilot kurum, Test ortamında, yazılı başarı kriteriyle (ör. bir çeyreklik PG verisinin sistemde toplanması).
- Pilot sonunda ödeme kararı: en az 1 ücretli dönüşüm hedefi.
- Referans vaka çalışması ve danışman komisyon modelinin netleşmesi.
- Self-servis kayıt ve ödeme ancak pilot sonucu olumluysa planlanır.
- Vakıf üniversitesi ve belediye segmenti, kamu satın alma yolu hukuken teyit edildikten sonra açılır.

## Ana risk ve belirsizlikler

1. Yayın'da hangi kodun çalıştığı bilinmiyor.
2. Hiç müşteri doğrulaması yok. Fiyatlar ve gelir senaryoları hipotezdir.
3. Tek sunucuda Test, Demo ve Yayın birlikte. Sunucu kaybı her şeyi etkiler.
4. LLM'e kurum verisi gönderimi KVKK yurt dışı aktarım kapsamında incelenmedi.
5. Kapsam çok geniş. Yüzey sadeleştirilmezse satış ve onboarding zorlaşır.
