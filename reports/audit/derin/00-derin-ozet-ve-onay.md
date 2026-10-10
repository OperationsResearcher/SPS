# Derin Denetim — Özet ve Onay Listesi

> Tarih: 2026-10-10 · Salt okunur analiz. Kodlama ONAYINIZDAN sonra başlar.
> Ayrıntılı raporlar: A (hesaplama), B (strateji/rapor), C (legacy IDOR), D (veri modeli), E (frontend), F (yetki/paket), G (özellik önerileri), H (yerli rekabet), I (KOBİ pazar).
> **[D✓]** = orkestratör tarafından kodda ayrıca doğrulandı.

## 1. Sayılarla

| Alan | Kesin hata | Not |
|---|---|---|
| A — Hesaplama doğruluğu | 14 (+6 olası) | Aynı PG için 7 ayrı hesap yolu |
| B — Strateji / rapor | 35 (+5 olası) | Okuma/export uçlarında rol kapısı yok |
| C — Legacy kiracı izolasyonu | 4 IDOR + 1 dosya silme | Guard bu modelleri kapsamıyor |
| D — Veri modeli / servisler | 28 | Kodda olmayan model alanları, ölü zamanlayıcılar |
| E — Frontend | 7 saklı XSS | CSRF token'sız fetch'ler büyük olasılıkla kırık |
| F — Yetki / paket | 20 | Paket kısıtı fiilen yalnız menüde |

Önceki turun az bulgu çıkarmasının nedeni yüzey taramasıydı. Bu tur kod yollarını izledi ve küçük denemelerle kanıtladı.

## 2. Düzeltme dalgaları — ONAY GEREKİR

### Dalga 1 — Güvenlik ve veri bütünlüğü (tahmini 4-5 gün)

| ID | Sorun | Etki |
|---|---|---|
| C-005 **[D✓]** | Logo yolu ile sunucuda rastgele dosya silme (`api/routes_admin.py`), rol kontrolü yok | `.env` dahil dosya silinebilir |
| F-001 **[D✓]** | Kurum yöneticisi kendi paketini, lisans bitişini, kullanıcı sınırını değiştirebiliyor | Ücretli modüller bedava açılır |
| F-002/F-004 | Paket kısıtı POST, AJAX ve `/api/` isteklerinde uygulanmıyor | Paket dışı modül API ile kullanılır |
| F-003, C-001, C-002 | Legacy proje API'sinde rol yok; gövdedeki PG/kullanıcı ID'leri kiracı kontrolsüz | Başka kurumun KPI'sına veri yazma, kullanıcı adı sızıntısı |
| F-005, F-008 | Üst Yönetim, eş rollü hesabın 2FA'sını sıfırlayıp devralabiliyor | Hesap ele geçirme |
| F-006 | Yayın'da DB geri yükleme ucu açık, denetim kaydı ve 2FA yok | Tek hata ile tüm veri ezilir |
| E-001…E-007 | 7 saklı XSS; en kritiği destek bileti → sistem yöneticisi | Admin oturumu ele geçirme |
| D-017 | PG silme, tüm geçmiş veri ve denetim izini kalıcı siliyor | Geri dönüşsüz veri kaybı |
| D-012 | Socket olayı başka kurumun odasına e-posta yayınlıyor | Kişisel veri sızıntısı |
| B-002/B-003 | Bireysel karne ZIP'i, audit paketi, 2FA'sız yönetici listesi, CFO paneli en düşük role açık | Kurum içi kişisel veri sızıntısı |
| B-001, B-009 | Başka kurumun KPI değeri ve kayıt adları SP/rapor uçlarından okunabiliyor | Kiracılar arası sızıntı |
| B-004 | Mühürlü plan yılına strateji/SWOT yazılabiliyor | Kapanmış yılın verisi değişir |

### Dalga 2 — Kırık işlevler (tahmini 3-4 gün)

| ID | Sorun |
|---|---|
| D-001 **[D✓]** | Proje görevi güncellemesi kaydedilmiyor ama "başarılı" dönüyor |
| D-002/D-003/D-007 | Modelde olmayan alanlar yüzünden proje dosya/risk/klonlama ve admin bileşen senkronu bozuk |
| D-005 | Görev bildirimleri boş legacy tabloya yazılıyor, hiç üretilmiyor ve isteği geri alıyor |
| D-006 | Görev ve faaliyet hatırlatma zamanlayıcıları hiç başlatılmıyor; saat 3 saat kayık |
| D-009/D-010 | Erken uyarı işi günlük tekrar üretiyor (yerelde 11.584 kiracısız bildirim) |
| E-010 | SP proje CRUD, sektör AI yorumu ve kurulum içe aktarma CSRF token göndermiyor |
| W1-E ek | Legacy PG GET/add (`main/routes/pages.py` ~225, ~311; `process_performance_service.py:57`) modelde olmayan `alt_stratejiler`/`alt_strateji` ilişkisini kullanıyor → her çağrı 500; `alt_strateji_id` hiçbir modelde kolon değil (tasarım kararı) |

### Dalga 3 — Hesaplama doğruluğu (tahmini 5-7 gün, ÜRÜN KARARI GEREKİR)

Müşterinin gördüğü skorların güvenilirliği bu dalgaya bağlıdır.

| ID | Sorun | Gereken karar |
|---|---|---|
| A-003 **[D✓]** | "0.125" → 125, "98.750" → 98750 okunuyor | Veri girişinde sayı biçimi: Türkçe (1.234,5) zorunlu mu, alan bazında ondalık mı? |
| A-002, A-006, A-007, A-008, A-009 | Karne, skor motoru, health ve raporlar aynı PG'yi farklı hesaplıyor | **Tek hesap motoru** kabulü: tüm ekranlar motoru çağırır |
| A-001 | Alt süreçleri ölçülmemiş üst süreç 0 alıyor (olması gereken: ölçülmedi) | — |
| A-004, A-005, A-011, A-012, A-010 | Bant boşluğunda uydurma puan, ağırlık 1/2 tutarsızlığı, negatif hedef, EFQM yön/yıl, JS yön hatası | — |
| A-016 | `calculated_score` yıldan bağımsız üzerine yazılıyor | — |
| B-005 | Savaş Odası ve strateji skorları yön gözetmiyor; "azalması iyi" PG'ler ters çıkıyor | — |
| B-006, B-007 | K-Radar KS skoru sayımdan uydurulmuş; yatırımcı sunumunda yer tutucu içerik | Kaldır mı, düzelt mi? |

### Dalga 4 — Kalite (sonra)

CSP `unsafe-inline` kaldırma, modal erişilebilirliği (44 modal), JS i18n (33 rapor dosyası), ölü JS/şablon temizliği, `Kalder/` (kullanıcı kararı: SİLİNMEZ; yalnız taramalardan/imajdan hariç tutulabilir), TestingConfig'te guard'ın açılması.

## 3. Özellik önerileri — ONAY GEREKİR

Ayrıntılar G raporunda. Önerilen ilk 5 koyu.

| No | Öneri | Efor (gün) | Onay | Ret | Sonra |
|---|---|---|---|---|---|
| **Ö-01** | Dönem açma + PG veri girişi hatırlatma | 7 | | | |
| **Ö-02** | Onay akışı + dönem kilidi | 6 | | | |
| **Ö-03** | "Başlarken" sihirbazı + rol bazlı sade menü | 6 | | | |
| **Ö-04** | Sektör şablonları | 8 | | | |
| **Ö-06** | Excel dönem şablonu indir/yükle | 4 | | | |
| Ö-05 | KOBİ PG kütüphanesi | 5 | | | |
| Ö-07 | AI sapma açıklama taslağı | 4 | | | |
| Ö-08 | EFQM RADAR öz değerlendirme | 9 | | | |
| Ö-09 | Danışman paneli (çoklu müşteri) | 8 | | | |
| Ö-10 | Yönetim toplantısı paketi | 4 | | | |
| Ö-11 | Teams/Slack hatırlatma | 2 | | | |
| Ö-12 | WhatsApp hatırlatma | 6 | | | |
| Ö-13 | Google Sheets salt okunur bağlantı | 3 | | | |
| Ö-14 | ERP CSV köprüsü | 5 | | | |
| Ö-15 | Self-servis deneme | 7 | | | |
| Ö-16 | Ödeme (iyzico/PayTR) | 8 | | | |
| Ö-17 | Fiyat sayfası | 2 | | | |
| Ö-18 | Kullanım ölçümü | 3 | | | |
| Ö-19 | DÖF + YGG | 4+ | | | |

Not: Ö-01 hatırlatma işi, Dalga 2'deki ölü zamanlayıcı (D-006) düzeltilmeden çalışmaz. Ö-02 dönem kilidi, Dalga 3'teki tek hesap motoruyla birlikte anlamlıdır.

## 4. Pazar — güçlendirilmiş sonuçlar

- **Rakip haritası (H):** 19 firma sitesinden doğrulandı. Doğrudan strateji/BSC rakibi az: Bimser Ensemble (kurumsal), kamuda Vadi DİGİKENT ve Element. Kalite (ISODECK, PaKalite, Datalms) ve İK performans (Kolay İK, idenfit) alanları kalabalık. Hiçbirinde yayımlı fiyat yok.
- **Boşluk (H):** Yerli EFQM yazılımı bulunamadı. KOBİ ölçeğinde strateji → süreç KPI → bireysel karne zincirini veren yerli ürün bulunamadı. Bu bir yokluk kanıtı değil, arama bulgusudur.
- **Uyarı (H):** "Türkiye'nin ilk/tek" ve kanıtsız 5018 iddiası kullanılmamalı.
- **Pazar (I):** 50-249 çalışanlı yaklaşık 33.500 KOBİ, ücretli bulut kullanımı %31,8. Orta senaryoda SAM yaklaşık 2.660 kurum, 3. yıl SOM yaklaşık 40 kurum. Bunlar varsayıma bağlı mertebelerdir. KOBİ sayıları ikincil kaynaktan, TÜİK bülteniyle teyit edilmeli.
- **KOSGEB (I):** Hibe değil, kredi faizi desteği. Yalnız imalat KOBİ'leri. SaaS aboneliğinin kapsamda olduğu belirsiz. Dijital olgunluk raporu veren danışmanlar (TÜSSİDE, MEXT, İHKİB) bir kanal olabilir.
- **ISO 9001:** Türkiye'de yaklaşık 18.500 geçerli belge (TÜRKAK paylaşımı, yıl belirsiz).

## 5. Sizden beklenen kararlar

1. Hangi düzeltme dalgaları onaylı? Önerim: Dalga 1 ve 2 hemen, Dalga 3 sayı biçimi kararından sonra.
2. Sayı biçimi kararı (A-003).
3. Tek hesap motoru kabulü (Dalga 3).
4. Özellik tablosunda Onay / Ret / Sonra işaretleri.

## 6. Kullanıcı kararları (2026-10-10)

1. Düzeltme dalgaları: **hepsi, sırayla** (1 → 2 → 3 → 4).
2. Sayı biçimi: **Türkçe zorunlu** (1.234,5).
3. Tek hesap motoru: **kabul**.
4. B-006 (K-Radar KS skoru) ve B-007 (yatırımcı sunumu yer tutucu): **SONRAKİ İŞLER** — kod dalgaları bittikten sonra.
5. Özellik önerileri: **onaylı**; öncelik kod. Özellik kodlamasına geçmeden önce sıra kullanıcıya teyit ettirilecek.
6. Model politikası: basit iş Haiku, mantık gerektiren iş Sonnet, Opus yalnız zorunlu hallerde.
