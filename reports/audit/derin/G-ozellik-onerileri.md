# G — Ürüne Eklenmesi Gereken Özellikler: Öneri Raporu

Tarih: 2026-10-10 · Yöntem: salt okunur (kod değişikliği yok). Onay için sunulur; onaylananlar sonra kodlanır.
Varsayımlar: tek geliştirici, kıt bütçe, hedef KOBİ (50-250 çalışan, EFQM/ISO belgeli, danışman destekli). Her öneri ≤10 gün MVP. Efor = geliştirici günü (test + TASKLOG dahil, müşteri doğrulaması hariç). Kural: tüm L paketleri bitmeden Yayın yok; doğrulamalar Test/Demo'da.

Etiketler: [K] kodda/dokümanda görüldü · [D] denetim raporuna dayalı, bağımsız doğrulanmadı · [W] web · [Ç] çıkarım.

## 0. Okunan belgelerden ana çıkarım

- Denetim 05 [D]: en zayıf halka **veri toplama döngüsü** (dönem görevi, hatırlatma, onay, dönem kilidi yok), "Başlarken" rehberi yok, sektör şablonu yok (`reports/audit/05-urun-ux.md` §5, A2-A4, B1).
- Yol haritası 12: önce güven, sonra değer döngüsü (veri toplama + onboarding), sonra satış deneyi; self-servis kayıt/ödeme pilot sonucuna bağlı (`reports/audit/12-birlesik-yol-haritasi.md`).
- Paketleme: fiyat modeli açık; gating yalnız modül düzeyinde (`docs/paketler/PAKETLEME-STRATEJISI.md` §2.1).
- Rekabet 06: doğrulanmış tek yerli rakip Bimser Ensemble (kurumsal/ağır); global rakipler KOBİ için pahalı veya OKR odaklı; asıl ikame Excel (`reports/audit/06-rekabet-analizi.md`).

## 1. Kodda kontrol edilen mevcut durum

| Konu | Bulgu | Kanıt |
|---|---|---|
| Şifremi unuttum | **VAR.** Denetim 05'in "yok" bulgusu yanlış | `app/routes/password_reset.py:64` (`/forgot-password`) |
| Slack/Teams/Discord webhook | **VAR** (tenant bazlı), yalnız anomali bildirimi için | `app/services/slack_notification.py` (`send_teams_message`, `dispatch_webhook`) |
| E-posta özet / zamanlanmış rapor | **VAR** | `app/services/email_digest_service.py`, `weekly_digest_service.py`, `automated_reporting_service.py`, `app/models/email_config.py` |
| Faaliyet hatırlatması | **VAR** (faaliyet/proje); PG veri girişi için YOK | `process_activity_reminders` (Yetenekler §2.2), `app/models/notification.py`, `app/services/notification_service.py` |
| Excel içe aktarma sihirbazı | **VAR** (süreç+PG+strateji) | `app/services/bulk_import_service.py` |
| Dönem kilidi / onay durumu | **YOK** (grep `period_lock`, `approval_status` boş) | `KpiData.status` onay tutmuyor [D] |
| Başlarken / onboarding sihirbazı | **YOK**; yalnız kule turu altyapısı | `micro/modules/shared/kule/routes.py` [D] |
| Sektör şablonu / PG kütüphanesi | **YOK** (Tomofil klonu, plan yılı şablonu var) | `app/services/plan_year_template_service.py` |
| EFQM | **KISMİ** (türetilmiş skor; RADAR akışı yok) | `app/services/efqm_assessment.py` |
| AI yorum | **KISMİ** (koç/danışman/anomali; sapma açıklaması taslağı yok) | `ui/templates/platform/raporlar/ai_coach.html`, `app/services/llm_gateway.py` |
| Çoklu kurum (danışman) | **KISMİ** (alt-tenant/holding) | `app/services/sub_tenant_billing_service.py`, `holding_consolidated_service.py` |
| BI bağlayıcı | **KISMİ** | `ui/templates/platform/raporlar/bi_connector.html`, `micro/modules/raporlar/routes_faz5.py` |
| Ödeme (iyzico/PayTR) | **YOK** (paket modeli var) | `app/models/saas.py:163` `SubscriptionPackage` |
| Self-servis deneme | **KISMİ** (demo-talep formu + giriş-engelsiz Demo) | `micro/modules/marketing/routes.py:174` |
| WhatsApp, Google Sheets, ERP | **YOK** | grep sonucu yok (`app/api/data_connector.py` kapsamı doğrulanmadı) |

## 2. Pazar araştırması (WebSearch; sayfalar özet düzeyinde)

- Cascade: G2 4.8/5 (255 yorum); artı: kullanım kolaylığı, destek; eksi: "missing features". [G2](https://www.g2.com/compare/cascade-strategy-cascade-vs-clear-impact-scorecard) [W]
- ClearPoint: G2 4.6/5, destek övülür; rakip blog maliyet ve karmaşık kurulumu sayar (taraflı). [G2](https://www.g2.com/compare/clearpoint-strategy-vs-envisio), [Mooncamp](https://mooncamp.com/blog/clearpoint-strategy-alternatives) [W]
- Spider Impact: Capterra 4.6/5 (27 yorum); kısa öğrenme eğrisi. [Capterra](https://www.capterra.com/p/113352/SpiderImpact/reviews) [W]
- Perdoo: check-in hatırlatmaları beğenilir; şikayet: kaydedilmeyen/ezilen güncelleme, katı hiyerarşi, sınırlı mobil, strateji net değilse "raporlama ritüeli". [Capterra](https://www.capterra.com/p/158539/Perdoo/reviews/) [W]
- Profit.co: şikayet: kurulum karmaşıklığı, dağınık görünüm, önceki dönemden kopyalama yok; destek övülür. [Capterra](https://www.capterra.com/p/182965/Profit/reviews) [W]
- Quantive (eski Gtmhub): e-posta hatırlatma ve check-in sonrası tarih düzenleme istekleri; kanıt zayıf. [Capterra](https://www.capterra.co.uk/software/156365/gtmhub) [W]
- Bimser Ensemble: kullanıcı yorumu bulunamadı (bkz. rekabet raporu 06).

[Ç] KOBİ araçları **kurulum kolaylığı + destek + hatırlatma** ile seçilip terk ediliyor; güncelleme güvenilirliği güveni belirliyor; veri toplama döngüsü kurulmayan araç "ritüel"e dönüp ölüyor. Bu, Ö-01..Ö-06 önceliğinin gerekçesi.

## 3. Öneriler

### Kategori 1 — Olmazsa olmaz

#### Ö-01 Dönem açma + PG veri girişi görevleri + hatırlatma
- **Problem:** Kalite sorumlusu her çeyrek 30 PG için 12 süreç sahibine e-posta atıp Excel bekliyor; kim girdi/girmedi görünmüyor.
- **Mevcut durum:** KISMİ. Faaliyet hatırlatması, bildirim ve e-posta altyapısı var (§1); PG dönem görevi/hatırlatma yok.
- **Kapsam MVP:** tenant ayarı "dönem açılış + son giriş günü"; zamanlayıcı her PG sahibine bildirim + e-posta (T-3, T, T+2); "veri girilmedi" listesi (süreç bazlı yüzde). **Dışı:** çok kademeli eskalasyon, WhatsApp, şablon editörü.
- **Değer:** çok yüksek · **Satış:** çok yüksek ("kim girmedi" ekranı demonun en güçlü sahnesi)
- **Efor:** 7 g · **Risk:** Orta (arka plan iş güvenilirliği, çoklu worker'da çift gönderim)
- **Bağımlılık:** tenant SMTP çalışıyor olmalı; Ö-02 ile birlikte anlamlı.
- **Kabul:** sahipler dönem başına tam bir kez bilgilendirilir; girilen PG için hatırlatma gitmez; yönetici girmeyenleri listeler; idempotent.
- **Müşteride doğrulama:** pilot kurumda bir çeyrek, zamanında giriş oranı öncesi/sonrası (hedef ≥%80).

#### Ö-02 Onay akışı + dönem kilidi (tek kademe)
- **Problem:** Denetçi "bu rakam sonradan değişti mi?" diye sorar; kalite müdürü rakamı onaylayıp dondurmak ister.
- **Mevcut durum:** YOK (§1). Audit log var.
- **Kapsam MVP:** süreç sahibi "onaya gönder" -> kurum yöneticisi onayla/reddet (gerekçe) -> onaylı dönem kilitli; yönetici "kilidi aç" (audit kaydı). **Dışı:** çok kademeli zincir, delege.
- **Değer:** yüksek · **Satış:** yüksek (ISO/EFQM izlenebilirliği)
- **Efor:** 6 g · **Risk:** Orta (KpiData yazan tüm uçlarda kilit; atlanan uç kilidi deler, tam tarama şart)
- **Bağımlılık:** Ö-01 önerilir.
- **Kabul:** kilitli dönemde UI/API/içe aktarma yazması 403; kilit açma audit'e düşer.
- **Doğrulama:** karne toplantısı senaryosu; denetçiye audit log gösterimi.

#### Ö-03 "Başlarken" sihirbazı (5 adım) + rol bazlı sade menü
- **Problem:** Müşteri ilk girişte 20 kartlı masaüstünde kaybolur (Profit.co/ClearPoint şikayeti aynı [W]).
- **Mevcut durum:** YOK; kule turu altyapısı var [D]; masaüstü 20 kart, admin sidebar 21 öğe [D].
- **Kapsam MVP:** kurum yöneticisi kontrol listesi kartı (kimlik -> strateji -> süreç -> PG -> ilk veri -> kullanıcı davet), adımlar gerçek veriden otomatik tamamlanır; standart kullanıcıya 5-6 öğelik menü. **Dışı:** video tur, AI asistan.
- **Değer:** yüksek · **Satış:** yüksek (deneme dönüşümü)
- **Efor:** 6 g · **Risk:** Düşük
- **Bağımlılık:** yok. Kart standardı (§5.1: ID, i18n .po) uyulmalı.
- **Kabul:** kontrol listesi durumu veriden türetilir (elle işaret yok); yeni kurumda ilk veriye <1 gün.
- **Doğrulama:** 5 kullanıcıyla gözlem testi.

#### Ö-04 Sektör şablonları (imalat KOBİ / hizmet KOBİ / ISO 9001 kalite) tek tık kurulum
- **Problem:** Boş sistemle başlamak ilk haftayı alır.
- **Mevcut durum:** YOK; klonlama ve Excel sihirbazı altyapısı var (`plan_year_template_service.py`, `bulk_import_service.py`).
- **Kapsam MVP:** 3 şablon, mevcut içe aktarıcıdan geçer (önizleme + onay, upsert). **Dışı:** AI ile üretim, belediye/üniversite şablonları.
- **Değer:** çok yüksek · **Satış:** yüksek ("saatte kurulum")
- **Efor:** 8 g (içerik ağırlıklı, danışman girdisi gerekir) · **Risk:** Düşük (kod), Orta (içerik doğruluğu)
- **Bağımlılık:** Ö-05 ile içerik ortak.
- **Kabul:** boş kurumda <10 dk'da strateji+süreç+PG; tekrar çalıştırma çift kayıt üretmez.
- **Doğrulama:** 3 pilot kurumda kurulum süresi.

#### Ö-05 KOBİ hazır PG kütüphanesi
- **Problem:** "Hangi PG'yi izlemeliyim?" boş sayfa sorunu.
- **Mevcut durum:** YOK.
- **Kapsam MVP:** ~120 PG tanımı (ad, birim, yön, periyot, formül notu, ISO/EFQM etiketi), süreç ekranında "Kütüphaneden ekle". **Dışı:** benchmark/sektör ortalaması.
- **Değer:** yüksek · **Satış:** orta-yüksek · **Efor:** 5 g · **Risk:** Düşük (yön hatası riski: veri kalitesi, bkz. HATA-04 notu)
- **Bağımlılık:** Ö-04.
- **Kabul:** eklenen PG yön/birim/periyot doğru; mükerrer ekleme uyarılır.
- **Doğrulama:** danışman 10 dakikada süreç karnesi kurabiliyor mu.

#### Ö-06 Excel ile dönem verisi toplu girişi (şablon indir / yükle)
- **Problem:** Süreç sahipleri 30 PG'yi tek tek formdan girmek istemez; rakiplerde de manuel güncelleme şikayeti [W].
- **Mevcut durum:** KISMİ. Yapı içe aktarımı var; dönem değeri şablonu [D] doğrulanmadı.
- **Kapsam MVP:** "bu dönemin giriş şablonu" indir -> yükle -> hata önizleme -> kaydet. **Dışı:** Sheets canlı senkron.
- **Değer:** yüksek · **Satış:** yüksek ("Excel'inizi bırakmayın")
- **Efor:** 4 g · **Risk:** Düşük-Orta (yanlış eşleşme; Ö-02 kilidine uyum)
- **Bağımlılık:** Ö-02 kilit kontrolü.
- **Kabul:** hatalı satırlar raporlanır; yeniden yükleme çiftlemez; audit'e kaynak="excel".
- **Doğrulama:** pilotun gerçek karne dosyasıyla yükleme.

### Kategori 2 — Farklılaştırıcı

#### Ö-07 Sapma açıklaması taslağı (AI)
- **Problem:** Hedefi tutmayan PG için "neden" yazmak sevilmeyen iş; toplantı öncesi saatler gider.
- **Mevcut durum:** KISMİ (`ai_coach.html`, `llm_gateway.py`, kural motoru yedeği).
- **Kapsam MVP:** hedefi tutmayan PG'de "taslak öner" (son 6 dönem trendi + hedef + önceki yorumlar -> 3 cümle); kullanıcı düzenler; AI kapalıysa kural tabanlı cümle. **Dışı:** otomatik kaydetme, serbest sohbet.
- **Değer:** yüksek · **Satış:** orta-yüksek · **Efor:** 4 g
- **Risk:** Orta (KVKK yurt dışı LLM aktarımı incelenmedi — yol haritası riski 4; kapatma/BYOK şart)
- **Bağımlılık:** Ö-02 (açıklama onay akışının parçası).
- **Kabul:** kullanıcı onayı olmadan kaydedilmez; kişi adı gönderilmez; kota aşımında kural motoru.
- **Doğrulama:** 5 yönetici, taslağın düzenlenme oranı ve süre kazancı.

#### Ö-08 EFQM RADAR öz değerlendirme akışı
- **Problem:** EFQM belgeli firmalar öz değerlendirmeyi Word/Excel'de yapar; kanıt-puan bağı kopuk.
- **Mevcut durum:** KISMİ: `app/services/efqm_assessment.py` (türetilmiş skor); RADAR akışı yok.
- **Kapsam MVP:** kriter başına Yaklaşım/Uygulama/Ölçüm/Gözden geçirme puanı + kanıt notu + bağlı PG, toplam ve yıl karşılaştırma. **Dışı:** DÖF, YGG, resmi başvuru formatı.
- **Değer:** yüksek (niş) · **Satış:** KalDer/danışman kanalında yüksek · **Efor:** 9 g · **Risk:** Orta (model sürümü, alan bilgisi)
- **Bağımlılık:** danışman girdisi.
- **Kabul:** puan, danışmanın Excel hesabıyla birebir (en az 1 gerçek dosya).
- **Doğrulama:** KalDer danışmanıyla bir öz değerlendirme turu.

#### Ö-09 Danışman paneli (çoklu müşteri geçişi)
- **Problem:** Danışman 8 müşteriyi yönetir; ayrı giriş-çıkış, kimin veri girdiği tek bakışta görünmez.
- **Mevcut durum:** KISMİ: alt-tenant/holding; danışman rolü ve çapraz kurum geçişi yok.
- **Kapsam MVP:** "Danışman" kullanıcı tipi, atanmış kurum listesi, tek tık geçiş (audit: danışman olarak), kurum başına Ö-01 doluluk yüzdesi. **Dışı:** ortak faturalama, komisyon.
- **Değer:** yüksek · **Satış:** çok yüksek (denetçi: danışman kanalı) · **Efor:** 8 g · **Risk:** Yüksek (tenant izolasyonu)
- **Bağımlılık:** P0 IDOR düzeltmeleri (yol haritası 12) ve Ö-01.
- **Kabul:** yalnız atanmış kurumlar; her geçiş audit'te; çapraz kurum testi 403.
- **Doğrulama:** 2 danışman ortakla 1 hafta.

#### Ö-10 Yönetim toplantısı paketi (tek tık PDF/PPTX)
- **Problem:** Çeyrek toplantısı sunumu 1 gün sürüyor.
- **Mevcut durum:** KISMİ: 40+ rapor, `yatirimci_sunum`, `audit_paketi` şablonları.
- **Kapsam MVP:** kurum skoru, kırmızı PG'ler, sapma açıklamaları, açık faaliyetler; mevcut PDF/PPTX motoruyla. **Dışı:** şablon editörü.
- **Değer:** yüksek · **Satış:** yüksek · **Efor:** 4 g · **Risk:** Düşük
- **Bağımlılık:** Ö-02, Ö-07 (opsiyonel).
- **Kabul:** onaylı dönem için <30 sn üretim, ekran verisiyle tutarlı.
- **Doğrulama:** gerçek toplantıda kullanım.

### Kategori 3 — Entegrasyon

#### Ö-11 Hatırlatmaları Teams/Slack webhook'a da gönder
- **Mevcut durum:** KISMİ: `slack_notification.py` webhook gönderimi var, yalnız anomali için.
- **Kapsam MVP:** Ö-01 hatırlatmaları `dispatch_webhook` ile; kullanıcı tercihi (`notification_preferences`). **Dışı:** Teams'ten veri girme.
- **Değer:** orta · **Satış:** orta · **Efor:** 2 g · **Risk:** Düşük · **Bağımlılık:** Ö-01
- **Kabul:** webhook hatası hatırlatmayı durdurmaz (loglanır); kapatma tercihi çalışır.
- **Doğrulama:** Teams kanalı olan pilot.

#### Ö-12 WhatsApp hatırlatma (önerim: Sonra)
- **Mevcut durum:** YOK. Business API onayı, şablon mesaj onayı ve mesaj maliyeti gerekir.
- **Kapsam MVP:** tek şablon "veri bekleniyor + link". **Dışı:** geri yazma.
- **Değer:** orta · **Satış:** orta · **Efor:** 6 g · **Risk:** Yüksek (platform onayı) · **Bağımlılık:** Ö-01
- **Kabul:** teslim durumu loglanır; opt-out çalışır. **Doğrulama:** pilotta açılma oranı e-postaya göre.

#### Ö-13 Google Sheets / Excel salt-okunur bağlantı
- **Mevcut durum:** KISMİ: `bi_connector.html`, `routes_faz5.py`; Sheets yok.
- **Kapsam MVP:** tenant bazlı imzalı CSV/JSON bağlantısı (Sheets `IMPORTDATA`), PG dönem değerleri. **Dışı:** geri yazma, OAuth.
- **Değer:** orta · **Satış:** orta · **Efor:** 3 g · **Risk:** Orta (token sızıntısı = veri sızıntısı; döndürülebilir token, hız sınırı)
- **Bağımlılık:** BI bağlayıcı altyapısı.
- **Kabul:** token iptalinde erişim kesilir; yalnız kendi kurum verisi. **Doğrulama:** Sheets'te tek formülle veri çekilir.

#### Ö-14 ERP (Logo/Netsis/Mikro) CSV köprüsü
- **Mevcut durum:** YOK.
- **Kapsam MVP:** canlı bağlantı DEĞİL; ERP raporu CSV'si + kayıtlı sütun->PG eşleme profili (Ö-06 üzerine). **Dışı:** SQL/API bağlantısı.
- **Değer:** orta-yüksek · **Satış:** orta · **Efor:** 5 g · **Risk:** Orta · **Bağımlılık:** Ö-06
- **Kabul:** kayıtlı profille ikinci yüklemede tek tıkla veri akar. **Doğrulama:** pilotun gerçek ERP raporuyla.

### Kategori 4 — Ticari altyapı

#### Ö-15 Self-servis 14 günlük deneme (koşullu — pilot olumluysa)
- **Mevcut durum:** KISMİ: `marketing/routes.py:174` demo-talep; Demo ortamı.
- **Kapsam MVP:** form -> kurum + yönetici + Ö-04 şablonu otomatik; bitince salt okunur. **Dışı:** kart alma.
- **Değer:** orta (şimdilik) · **Satış:** yüksek (ileride) · **Efor:** 7 g · **Risk:** Orta (spam kayıt, e-posta doğrulama, KVKK açık rıza)
- **Bağımlılık:** Ö-03, Ö-04, Ö-17.
- **Kabul:** kayıttan ilk PG verisine <1 saat; süre dolunca veri silinmez, yazma kapanır. **Doğrulama:** 10 kayıtla huni ölçümü.

#### Ö-16 Ödeme (iyzico / PayTR) — önerim: Sonra
- **Mevcut durum:** YOK (`SubscriptionPackage`: `app/models/saas.py:163`). Fiyat modeli açık.
- **Kapsam MVP:** tek paket + kart ile yıllık ödeme + webhook ile paket atama; fatura elle. **Dışı:** otomatik yenileme, kupon, e-fatura.
- **Değer:** orta · **Satış:** orta (B2B'de havale/fatura yeterli olabilir) · **Efor:** 8 g · **Risk:** Yüksek (ödeme güvenliği, mali mevzuat)
- **Bağımlılık:** fiyat kararı, Ö-17.
- **Kabul:** başarısız ödemede paket atanmaz; webhook imzası doğrulanır; tekrar bildirim çift atama yapmaz. **Doğrulama:** sandbox + 1 düşük tutarlı gerçek işlem.

#### Ö-17 Fiyat sayfası + paket karşılaştırma
- **Mevcut durum:** YOK (`templates/marketing` var).
- **Kapsam MVP:** 3 paket özellik tablosu, "teklif iste" -> mevcut demo-talep formu; rakam görüşme testinden sonra. **Dışı:** hesap makinesi.
- **Değer:** orta · **Satış:** orta-yüksek · **Efor:** 2 g · **Risk:** Düşük (karar bağımlılığı)
- **Bağımlılık:** fiyat kararı.
- **Kabul:** tablo `system_modules` paket tanımıyla aynı kaynaktan üretilir. **Doğrulama:** 10 ziyaretçiyle anlaşılırlık testi.

#### Ö-18 Kullanım ölçümü (aktivasyon / terk sinyali)
- **Mevcut durum:** KISMİ: audit log, `sub_tenant_billing_service.py`.
- **Kapsam MVP:** admin ekranı: kurum başına son giriş, son PG verisi, aktif kullanıcı, dönem doluluğu; 30 gün hareketsiz kuruma elle onaylı e-posta. **Dışı:** analitik SaaS.
- **Değer:** orta · **Satış:** dolaylı (elde tutma) · **Efor:** 3 g · **Risk:** Düşük · **Bağımlılık:** Ö-01
- **Kabul:** sayılar veriden hesaplanır, ayrı sayaç tablosu yok. **Doğrulama:** pilot izlemede hafta hafta kıyas.

#### Ö-19 DÖF + YGG toplantı yönetimi (Sonra)
- **Mevcut durum:** YOK. Bimser QDMS alanıyla çakışır; efor L.
- **Kapsam MVP (bölünürse):** yalnız "toplantı kararı -> faaliyet" bağı. **Dışı:** DÖF, doküman, CAPA.
- **Değer:** orta · **Satış:** orta (belgeli firmalar) · **Efor:** 4+ g · **Risk:** Orta · **Bağımlılık:** Ö-08
- **Kabul:** karardan oluşan faaliyet atanır ve hatırlatılır. **Doğrulama:** pilot talebi gelirse.

### Kategori 5 — Bilinçli olarak YAPILMAMASI gerekenler

| # | Yapılmayacak | Gerekçe |
|---|---|---|
| Y-1 | Yeni modül/rapor (ESG, EVM, PESTEL varyantı, yeni K-Rapor sekmesi) | ~50 rapor şablonu, 22 sekme var; yüzey sadeleşmeden satış zorlaşır [D]. Pilot geri bildirimine kadar dondurma (yol haritası 12). |
| Y-2 | Native mobil uygulama | Perdoo bile mobilde eleştirilir [W]; bakım yükü. Duyarlı web + e-posta/Teams linki yeterli. |
| Y-3 | OKR modülü rekabeti | Rakipler güçlü ve ucuz; fark strateji-süreç-PG-EFQM bağı. |
| Y-4 | Canlı ERP bağlayıcıları (SQL/API) | Müşteriye özel, sürüm bağımlı; CSV köprüsü (Ö-14) yeter. |
| Y-5 | Kendi LLM / fine-tune / AI yönetim ekranı | Tek geçit zaten var; KVKK incelemesi bitmeden AI genişletme yok. |
| Y-6 | Özel rapor tasarımcısı / sürükle-bırak dashboard | Destek yükü; hazır paket (Ö-10) daha ucuz. |
| Y-7 | EN dışı dil genişletmesi | Hedef TR KOBİ; TR/EN yeterli. |
| Y-8 | Belediye/üniversite/kamu özellikleri (5018, SBB genişletme) | Kamu satın alma yolu teyit edilmeden açılmaz (yol haritası 12). |
| Y-9 | Kart açıklama zenginleştirmeye devam (405 kart) | Durdurulmuş karar; değer/efor düşük. |
| Y-10 | Doküman/CAPA/denetim yönetimi (QDMS alanı) | Kalite sistem yazılımına dönüşmek; kapsam şişmesi. |
| Y-11 | Gerçek zamanlı ortak düzenleme, sohbet, yorum thread'leri | Toplantı paketi + açıklama alanı yeterli. |

## 4. Bağımlılık özeti

Ö-01 -> Ö-02 -> (Ö-06, Ö-07, Ö-10) · Ö-04 ↔ Ö-05 · Ö-01 -> Ö-11, Ö-12, Ö-18 · Ö-03 + Ö-04 + Ö-17 -> Ö-15 · Ö-17 -> Ö-16 · Ö-09 tenant izolasyon düzeltmelerine (yol haritası 12 P0) bağlı · Ö-06 -> Ö-14 · Ö-08 -> Ö-19.

## 5. Önceliklendirme matrisi (değer × efor)

| | Düşük efor (≤4 g) | Orta (5-7 g) | Yüksek (8-10 g) |
|---|---|---|---|
| **Çok yüksek / yüksek değer** | Ö-06 (4), Ö-07 (4), Ö-10 (4) | Ö-01 (7), Ö-02 (6), Ö-03 (6), Ö-05 (5) | Ö-04 (8), Ö-09 (8), Ö-08 (9) |
| **Orta değer** | Ö-11 (2), Ö-13 (3), Ö-17 (2), Ö-18 (3) | Ö-14 (5), Ö-15 (7) | Ö-16 (8) |
| **Düşük / belirsiz** | Ö-19 (4+) | Ö-12 (6) | |

Toplam yaklaşık 106 g (19 öneri). Önümüzdeki ~60 günlük gerçekçi dilim (yol haritası 12 ile uyumlu): Ö-01, Ö-02, Ö-03, Ö-04, Ö-06 = 31 g çekirdek + test/hata payı.

## 6. Önerilen ilk 5

1. **Ö-01** Dönem açma + PG hatırlatma (7 g): ürünü "ritüele" çeviren çekirdek; rakip şikayetlerinin ortak noktası.
2. **Ö-02** Onay + dönem kilidi (6 g): EFQM/ISO denetimi, izlenebilirlik.
3. **Ö-03** Başlarken sihirbazı + sade menü (6 g): ilk 15 dakika başarısı.
4. **Ö-04** Sektör şablonları (8 g, Ö-05 ile içerik paylaşımlı): kurulum saate iner.
5. **Ö-06** Excel dönem şablonu yükleme (4 g): "Excel'inizi bırakmayın", giriş sürtünmesi.

Sonraki: Ö-05, Ö-07, Ö-10, Ö-09 (P0 izolasyon sonrası), Ö-08.

## 7. Onay kutuları

| No | Öneri | Efor (g) | Onay | Ret | Sonra |
|---|---|---|---|---|---|
| Ö-01 | Dönem açma + PG hatırlatma | 7 | | | |
| Ö-02 | Onay akışı + dönem kilidi | 6 | | | |
| Ö-03 | Başlarken sihirbazı + sade menü | 6 | | | |
| Ö-04 | Sektör şablonları | 8 | | | |
| Ö-05 | KOBİ PG kütüphanesi | 5 | | | |
| Ö-06 | Excel dönem şablonu yükleme | 4 | | | |
| Ö-07 | AI sapma açıklama taslağı | 4 | | | |
| Ö-08 | EFQM RADAR öz değerlendirme | 9 | | | |
| Ö-09 | Danışman paneli | 8 | | | |
| Ö-10 | Yönetim toplantısı paketi | 4 | | | |
| Ö-11 | Teams/Slack hatırlatma | 2 | | | |
| Ö-12 | WhatsApp hatırlatma | 6 | | | |
| Ö-13 | Sheets salt-okunur bağlantı | 3 | | | |
| Ö-14 | ERP CSV köprüsü | 5 | | | |
| Ö-15 | Self-servis deneme | 7 | | | |
| Ö-16 | Ödeme (iyzico/PayTR) | 8 | | | |
| Ö-17 | Fiyat sayfası | 2 | | | |
| Ö-18 | Kullanım ölçümü | 3 | | | |
| Ö-19 | DÖF + YGG | 4+ | | | |

## 8. Sınırlar

- Web araştırması özet düzeyinde; G2/Capterra sayfaları tam okunmadı, Bimser için yorum bulunamadı. Şikayet çıkarımları genel eğilimdir.
- Eforlar kod tabanı derin okunmadan verildi (özellikle Ö-02: KpiData yazan uç sayısı bilinmiyor). Onaylanan her öneri için kodlamadan önce 0,5 günlük keşif önerilir.
- Denetim 05'teki "şifremi unuttum yok" bulgusu yanlıştır (§1); diğer [D] bulgular doğrulanmadı.
- Çalışma ağacında çok sayıda commit edilmemiş değişiklik var; "mevcut durum" bu ağaca göre okundu.
