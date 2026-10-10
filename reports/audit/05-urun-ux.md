# 05 — Ürün ve Kullanıcı Deneyimi Denetimi (Kokpitim)

> Tarih: 2026-10-10 · Yöntem: salt okunur; uygulama çalıştırılmadı. Kaynaklar: `docs/Kokpitim_Yetenekler.md`, `PROJE-MASTER.md`, `ROADMAP-2026H2.md`, `paketler/*`, `DEMO-ORTAMI-PLAN.md`, `KMF/`, `kılavuz/`, `L1-L2-L3-UX-TEST.md`, `ekim2026/KOKPITIM-DETAYLI-ANALIZ-EKIM2026.md`, `kontrol/DAGINIKLIK-DENETIMI-2026-07-18.md`, `micro/modules`, `ui/templates/platform`, `templates/marketing`.
> Etiketler: **[K]** = kanıt (dosya/grep ile görüldü) · **[D]** = dokümana dayalı iddia (kodla bağımsız doğrulanmadı) · **[Ç]** = çıkarım/yorum.
> Rakip karşılaştırması bu raporun kapsamı dışındadır.

## 1. Ürün tanımı

Kokpitim; Türk kurumları için strateji (ana/alt strateji, SWOT/PESTEL/BSC/OKR) -> süreç -> PG (performans göstergesi) -> bireysel karne zincirini tek çok-kiracılı (multi-tenant) SaaS'ta birleştiren kurumsal performans yönetim platformudur [K: PROJE-MASTER §1, Yetenekler §1]. Üstüne K-Radar (teşhis), K-Rapor (40+ rapor), KOE (kurumsal olgunluk endeksi), EFQM skoru, proje portföyü (Gantt/RAID/EVM), ESG ve provider-bağımsız AI katmanı (BYOK, kural-motoru yedeği) biner [K: AI-POLITIKASI, `llm_gateway.py`].

Mimari: Flask + Jinja, PostgreSQL, `micro/` modern çekirdeği (route sayıları grep: sp 134, raporlar 101, k_radar 91, admin 90, surec 43, k_rapor 41) + legacy yüzey (strangler yaklaşımı) [K]. Prod: Oracle VM, 4 ortam (Yerel/Test/Demo/Yayın).

## 2. Hangi problemi çözüyor, kimin için

| Problem | Karşılık | Kanıt |
|---|---|---|
| Stratejik plan raftan inmiyor | Strateji ağacı -> süreç/PG bağı, plan yılı, yıl-bazlı klonlama, çeyreklik review | [K] sp modülü, `sihirbaz_yeni_yil.html`, `ceyreklik_review.html` |
| Süreç karnesi Excel'de | Süreç karnesi, PG, bantlı 1-5 puanlama (KMF tipi), periyot/ağırlık | [K] `docs/KMF/s11-xlsx-ozet.txt` (gerçek müşteri karnesi) |
| Bireysel performans stratejiye bağlanmıyor | Bireysel karne, Standart/Stratejik katman, strateji bağı | [K] L1-L2-L3-UX-TEST #3 |
| Kalite/EFQM/ESG raporlama | EFQM türetilmiş skor, ESG metrik, 5018/yatırımcı/audit paketi | [K] `ui/templates/platform/raporlar/` (esg_*, audit_paketi, yatirimci_sunum) |
| Proje/risk | Portföy, Gantt, EVM, RAID, kapasite, risk ısı haritası | [K] k_radar `kpr_*`, `risk_management.html` |
| Yöneticiye "yorum" | AI koç/danışman/sunum, anomali, KOE | [K] `ai_coach.html`, `ai_danisman.html`, `ml_anomaly.html` |

**Hedef kullanıcı:** (1) danışman eşliğinde kurulum yapan orta ölçekli Türk kurumları, KOBİ ve kalite odaklı kuruluşlar (KMF/KalDer/SBB verisi kodda ve docs'ta) [K]; (2) strateji vurgusu: yönetim sistemi oturmamış, veri girecek personeli ve yorum becerisi az "giriş seviyesi" kurumlar [K: PAKETLEME §0]; (3) bayi/holding (alt-tenant, konsolide kullanım raporu) [K: `sub_tenant_billing_service.py`]. Roller: Sistem Yöneticisi, Kurum Yöneticisi, Üst Yönetim, Kurum Kullanıcısı [K: `roles.py`]. [Ç] Gerçek alıcı büyük olasılıkla danışman aracılı kurumlardır; ürün henüz self-servis değildir.

## 3. Ana iş akışları

1. **Kur:** kimlik (vizyon/misyon/değer) -> strateji ağacı -> süreç -> PG tanımı. Araçlar: Excel içe aktarma sihirbazı (süreç+PG+strateji, upsert) [K: `routes_setup_import.py`, KURULUM-IMPORT-SIHIRBAZI.md], tenant klonlama (Tomofil şablonu), KMF tipi bant skorlaması.
2. **Ölç:** PG verisi girişi -> süreç karnesi -> bireysel karne; proje/görev; faaliyet atama + hatırlatma.
3. **Yorumla:** K-Radar (KS/KP/KPR/Cross), K-Rapor, KOE, AI koç, zamanlanmış rapor e-postası (tenant SMTP) [K: Yetenekler §5.3].
4. **Yönet:** paket gating (Başlangıç/Yönetim/Strateji/Master), alt kurum, rol, audit log, yedekleme.
5. **Satış/deneme:** pazarlama sitesi -> demo talep formu (e-posta) -> Demo ortamı (Tomofil, giriş-engelsiz, baseline'a sıfırlama) [K: `marketing/routes.py:174`, DEMO-ORTAMI-PLAN].

## 4. Gerçek değer ve karmaşıklık

**Gerçek değer (kanıtı güçlü):**
- Strateji -> süreç -> PG -> bireysel zincirinin tek modelde olması; PlanYear (çok yıllı) ve yıl bazlı klonlama [K].
- Excel/KMF/SBB gerçekliğine uyum: bantlı puanlama, ağırlıklı gösterge, "Excel'inizi getirin" sihirbazı [K].
- 7 yıllık Tomofil örnek verisi (99k satır) ile gerçekçi demo [K: DEMO plan §1].
- AI'nın "çökmeyen" tasarımı: tek geçit, kota, BYOK, kural-motoru yedeği [K: AI-POLITIKASI].
- Kart sistemi: (i) yardım + kart ID + `system_cards` DB'si; destek/denetim için sağlam altyapı [K: 501 kart, 0 kırık endpoint, DAGINIKLIK denetimi].
- KOE: veri girmeden yapı ölçümü; düşük olgunluk segmenti için doğru fikir [K: `koe_service.py`, PAKETLEME §4.A].

**Karmaşıklık / yüzey kirliliği:**
- Yüzey geniş: ~254 sayfa route'u, admin sidebar'ı 21 öğe, K-Rapor 22 sekme, masaüstü 20 kart [D: EKIM2026 Bölüm 3 #2]; `raporlar/` altında ~50 şablon [K].
- Kullanıcının kendi tespiti: "ekranların %90'ı hakkında fikrim yok" [K: PAKETLEME §0] — sorun özellik değil, maruz kalma.
- `mock_*` lab modülleri (metaverse, DAO, doomsday… ~30 tablo) ürün değeri taşımıyor [K: PAKETLEME satır 21].
- Çift K-Radar girişi, menüde olmayan rapor katmanı, iki ana sayfa (/desktop ve /desktop-launcher) [K: DAGINIKLIK #1-3; D: EKIM2026 #1].
- Legacy çift yüzey (`main_bp` 136 route, 130 legacy template) [K: CLAUDE.md, SISTEM-HARITASI].
- "Yakında" yarım sayfalar (`proje/index.html`, `raporlar/mobile.html`) [D].
- Aynı gösterge için 5 hesap yolu -> farklı sayı riski; ürün güveni için en kritik sorun [D: EKIM2026 §0.1-3].

## 5. Onboarding ve kullanılabilirlik sorunları

| # | Sorun | Etiket | Kanıt |
|---|---|---|---|
| 1 | "Başlarken" kontrol listesi / ilk giriş rehberi yok. Kule turu altyapısı (model `tour.py`, 5 API ucu) var; AI yardım (Faz 2) "sonraki proje" | [K]+[D] | `KULE-TANIM.md §5.2`; `shared/kule/routes.py`; EKIM2026 #12 |
| 2 | (i) açıklamalarının ~405/526'sı boş; kart yardımı vaadi tam çalışmıyor | [D] | EKIM2026 #12; kart açıklama zenginleştirme durduruldu (K-Radar 97/97 bitti, 405 kaldı) |
| 3 | Self-servis "şifremi unuttum" ucu bulunamadı (reset yalnız admin `reset-password` ve 2FA reset) | [K] grep | `routes_sub_tenants.py:255`, `admin/routes.py:679`; giriş şablonu ayrıca kontrol edilmeli |
| 4 | Self-servis kayıt/deneme yok; tek kapı demo-talep formu -> e-posta | [K] | `marketing/routes.py:174`; kayıt route'u yok |
| 5 | Mobil: `manifest.json` var, service worker yok; `mobile.css` ölü Bootstrap seçicileri; `raporlar/mobile.html` "Yakında" | [K]+[D] | `static/manifest.json`; sw dosyası yok (ls/grep); EKIM2026 #14 |
| 6 | Erişilebilirlik: focus-trap 0, 44 modalın 5'inde `role=dialog`, kontrast 2.6:1, ≤11px yazı | [D] | EKIM2026 #6 |
| 7 | Sessiz hatalar ("Yükleniyor"da takılan kartlar), SweetAlert'te İngilizce "OK" | [D] | EKIM2026 #7-8 |
| 8 | Kaydedilmemiş değişiklik uyarısı/autosave yok (1.103 satırlık karne formu) | [D] | EKIM2026 #9 |
| 9 | i18n: EN .po'da ~458 boş çeviri, JS'te sabit Türkçe, arayüzde "Tenant" (sözlük ihlali); i18n Yayın'a deploy edilmedi | [D]+[K] memory | EKIM2026 #11 |
| 10 | Sidebar mimariyi yansıtmıyor (girdi/teşhis/rapor karışık, 13 giriş) | [K] | DAGINIKLIK #1 |
| 11 | Gating yalnız modül/launcher düzeyinde; kart/özellik düzeyi yok. Çoğu tenant Master (hepsi görür) | [K] | PAKETLEME §2.1.3; L1-L2-L3 "hepsi Master" |
| 12 | Büyük tablolarda sayfalama yok; `admin/tenants.html` satır başına `count()` | [D] | EKIM2026 #13 |
| 13 | Veri girişi yükü: PGV "EN YÜKSEK yük"; hatırlatma/onay/dönem kilidi yok | [K]+[D] | PAKETLEME satır 12; EKIM2026 §4.2 P0 |
| 14 | UX testi manuel (yönerge dosyası); CI kapalı, kapsam %28.6 | [D] | `L1-L2-L3-UX-TEST.md`; EKIM2026 §0.1 |

## 6. Eksikler

- **Veri toplama döngüsü:** dönem açılışında görev + hatırlatma + eskalasyon yok (hatırlatma yalnız faaliyet/proje) [D].
- **Onay akışı ve dönem kilidi:** `KpiData.status` onay tutmuyor; onay zinciri MVP [D].
- **PG sapma açıklaması** (neden + aksiyon) zorunluluğu yok [D].
- **Kurumsal SSO:** yalnız Google (`app/routes/sso.py`); Entra/SAML/LDAP yok [K+D].
- **Formüllü PG**, holding PG konsolidasyonu (KalDer'de açık iş) [D].
- **EFQM RADAR öz-değerlendirme** (kanıt+konsensüs): bugün yalnız veriden türetilmiş skor [D].
- **Ödeme/abonelik/fatura:** ödeme sağlayıcı entegrasyonu kodda yok; tek faturalama kodu `sub_tenant_billing_service.py` bayi kullanım raporudur [K grep]. Pazarlama sitesinde fiyat/paket sayfası yok [K grep]. Paket ataması admin tarafından elle yapılıyor.
- **Entegrasyon:** `bi_connector.html` ve Slack bildirimi var; ERP/muhasebe/İK/Teams/OData yok [D].
- **Yardım/destek:** Kule turu + (i) + sesli mp4 kılavuz üretim hattı var; uygulama içi yardım merkezi ve destek bileti yok [K+Ç].
- **PWA / mobil veri girişi** yok [K].
- **KVKK:** veri dışa aktarma ve hesap silme uçları var (`app/routes/auth.py:192,272`) [K]; silme politikasının (soft delete/anonimleştirme) yasal yeterliliği doğrulanmalı [Ç].

## 7. AI / otomasyon / entegrasyon fırsatları

Mevcut [K]: AI koç, AI danışman, AI sunum, NLP sorgu (`nlp_query.html`), ML anomali, BSC otomatik sınıflandırma, LLM kullanım/maliyet ekranı, zamanlanmış rapor, KOE "AI ile zenginleştir".

Fırsatlar [Ç]:
1. AI karne yorumu + toplantı özeti (dönem sonunda "ne oldu / neden / ne yapmalı"); gateway ve veri hazır.
2. Excel yapıştırma/konuşmalı PG girişi ve LLM ile sütun eşleme (import sihirbazı zaten var).
3. Sapma açıklaması taslağı (AI önerir, kullanıcı onaylar).
4. Sektör şablonundan otomatik kurulum (belediye, üniversite, KOBİ): AI + klon altyapısı.
5. Teams/Slack/WhatsApp hatırlatma botu; veri girmeyen sorumluyu uyarma.
6. Kule Faz 2: bağlama duyarlı soru-cevap (kart (i) açıklamaları + kılavuz = hazır RAG korpusu).
7. OData/Power BI ve Entra SSO: kurumsal satış kapısı.

## 8. Pazara hazırlık

| Boyut | Durum | Etiket |
|---|---|---|
| Fatura/abonelik | Ödeme yok, fiyat yok, paket elle atanır | [K] |
| Self-servis kayıt | Yok; demo-talep formu + manuel kurulum | [K] |
| Parola sıfırlama | Self-servis uç bulunamadı | [K] grep, doğrulanmalı |
| Yardım | Kule turu + (i) + sesli mp4 kılavuz üretici (Playwright + edge-tts) + PDF kılavuz; kapsam kısmi | [K] |
| i18n | TR/EN altyapısı (~6.1k msgid), EN eksik/karışık; Yayın'a deploy edilmedi | [K]+[D] |
| Mobil | Responsive kısmi, PWA yok, mobil CSS ölü | [K]+[D] |
| Güvenlik/uyum | SOC2/ISO hazırlık dokümanı var; git'te sır, 8x scheduler, off-site yedek yok bulguları satışa engel | [D] EKIM2026 §0.1 |
| Pazarlama sitesi | Özellik sayfaları, blog, SEO (sitemap/robots) var | [K] |
| Deploy | Tüm L paketleri bitmeden Yayın'a çıkılmama kararı; Yayın'da paket gating fiilen sınanmamış | [K] memory |
| Güvenilirlik | 5 hesap yolu, CI kapalı; 762 test yeşil | [D] |

**Sonuç [Ç]:** Ürün danışman aracılı kurumsal satışa yakın; self-servis SaaS'a hazır değil.

## 9. Farklılaştırıcı ve taklidi zor yetenekler

1. **Türkiye bağlamı:** KMF tipi bantlı skorlama, SBB şablonu, KalDer/EFQM, 5018 yönelimi; birikmiş müşteri verisi (KMF, KalDer, EMS, HEOM klasörleri) [K].
2. **Tam zincir tek modelde** (strateji->süreç->PG->bireysel->proje) + çok yıllı PlanYear + klonlama [K].
3. **Kurulum hızlandırıcıları:** Excel sihirbazı, tenant klonlama, 7 yıllık örnek veri, demo baseline sıfırlama [K].
4. **AI yorum katmanı + BYOK + çökmeyen yedek + maliyet görünürlüğü** [K].
5. **Kart/katman altyapısı** (Paket->Modül->Bileşen->Kart->Veri; 501 kart) [K]; kart düzeyi gating henüz uygulanmadı.
6. **Sesli otomatik kılavuz üretimi** [K].

Taklit zorluğu [Ç]: hendek kod değil, alan bilgisi + yerel şablon/veri birikimi + danışman ilişkileri; teknik olarak kopyalanması kolaydır.

## 10. Öneriler

Efor: S (<1 hf) / M (1-4 hf) / L (>1 ay). Teknik risk: D (düşük) / O (orta) / Y (yüksek).

### A. Mevcut iyileştirme

| # | Öneri | Müşteri değeri | Etki | Efor | Risk | Doğrulama |
|---|---|---|---|---|---|---|
| A1 | Tek hesap motoru (karne/skor/rapor aynı sayı) | Güven, denetlenebilirlik | Çok yüksek | L | O | 111+ hesap testi; aynı PG için 5 ekranda eşit sayı kontrolü |
| A2 | PG veri toplama döngüsü (dönem aç -> görev -> hatırlatma -> eskalasyon) | Veri girilmeme sorununu çözer | Çok yüksek | M-L | D | Pilot kurumda dönem başına giriş oranı öncesi/sonrası |
| A3 | Onay + dönem kilidi + sapma açıklaması | EFQM/KalDer denetimi | Yüksek | M | O | Karne toplantısı senaryosu; audit log kontrolü |
| A4 | "Başlarken" 5 adımlı kontrol listesi + rol bazlı sade menü (standart kullanıcıda 5-6 öğe) | İlk 15 dk başarı | Yüksek | M | D | Kayıttan ilk PG verisine süre (hedef <1 gün); 5 kullanıcıyla gözlem testi |
| A5 | Sidebar'ı girdi/teşhis/rapor katmanına göre düzenle; çift ana sayfa ve çift K-Radar girişini birleştir | Yön bulma | Orta | S-M | D | Tıklama sayısı, ilk görev tamamlama oranı |
| A6 | Kart düzeyi gating; `mock_*` ve yarım sayfaları kaldır/flag | Overwhelm azalır | Yüksek | M | O | Başlangıç paketinde görünen sayfa sayısı (254 -> hedef <60) |
| A7 | Self-servis parola sıfırlama + Entra SSO | Destek yükü, kurumsal satış | Yüksek | M | O (güvenlik) | Akış testi; token ömrü/tek kullanım; sızma testi |
| A8 | Erişilebilirlik + sessiz hata + dirty-form koruması | Güven, 45+ yaş yönetici | Orta | M | D | axe taraması; hata senaryo testleri |
| A9 | EN i18n tamamlama + Yayın'a açma | EN kullanıcı | Orta | M | D | Boş msgstr = 0; EN smoke turu |
| A10 | Kalan ~405 kartın (i) açıklamasını tamamla veya boşları gizle | Yardım güvenilirliği | Orta | M | D | Boş açıklamalı kart = 0 |

### B. Yeni modül

| # | Öneri | Müşteri değeri | Etki | Efor | Risk | Doğrulama |
|---|---|---|---|---|---|---|
| B1 | Sektör şablon kütüphanesi (belediye, üniversite, hastane, KOBİ: strateji+süreç+PG seti, tek tık kur) | Kurulum günlerden saate iner | Çok yüksek | M-L | D | 3 pilot kurumda kurulum süresi |
| B2 | AI anlatısal dönem raporu + hedef/sapma önerisi | Düşük yetkinlik segmenti | Yüksek | M | O (halüsinasyon) | Danışman körleme değerlendirmesi; sayısal tutarlılık testi |
| B3 | 5018 PP/FR üreteci + kamu şeffaflık panosu | Kamu pazarı kapısı | Yüksek | L | O | Bir belediye çıktısı ile mevzuat formatı karşılaştırması |
| B4 | EFQM RADAR öz-değerlendirme + DÖF + YGG toplantı yönetimi | KalDer/kalite segmenti | Yüksek | L | O | KalDer danışmanıyla iş akışı onayı |
| B5 | PWA + mobil veri girişi (service worker, hızlı PG girişi, push) | Sahadaki veri girici | Orta-yüksek | M-L | O | Mobilde PG girişi süresi; çevrimdışı senaryo |
| B6 | Entegrasyon katmanı: OData/Power BI, Teams/Slack botu, ERP/Excel eşitleme | Veriyi elle girmeme | Yüksek | L | Y | 1 gerçek ERP/Excel kaynağıyla pilot |
| B7 | Holding PG konsolidasyonu | Bayi/holding segmenti | Orta-yüksek | M | O | KalDer mutabakatı |

### C. İş modeli / konum

| # | Öneri | Müşteri değeri | Etki | Efor | Risk | Doğrulama |
|---|---|---|---|---|---|---|
| C1 | Konum: "Türk kurumları için danışman destekli strateji-performans sistemi (Excel'den yarım günde)" — genel "BSC aracı" yerine yerel alan hendeği | Net mesaj | Yüksek | S | D | 10 potansiyel müşteri görüşmesinde mesaj testi; demo-talep dönüşümü |
| C2 | Danışman/partner kanalı (KMF örneği; alt-tenant/bayi altyapısı hazır) | Dağıtım, daha az doğrudan destek | Çok yüksek | M | D | 2-3 danışman firmasıyla pilot; kurulum başına gelir |
| C3 | Fiyat/paket sayfası + ödeme (iyzico/PayTR) + deneme hesabı | Self-servis giriş, nakit akışı | Yüksek | L | O (yasal/e-Fatura) | Deneme->ücretli dönüşüm oranı; muhasebe uyumu |
| C4 | Başlangıç paketi = "yarı kurulu + AI yorumlu" ücretli pilot (PAKETLEME stratejisi) | Düşük yetkinlik segmenti | Yüksek | M | O | 5 pilot kurumda ödeme isteği |
| C5 | Kurulum hizmeti + eğitim videosu/kılavuz gelir kalemi | Hızlı başarı | Orta | S | D | Kurulum başına süre/maliyet |
| C6 | Güven kanıtı: sırların döndürülmesi, off-site yedek, SOC2/ISO yol haritası ve KVKK belgesi | Kurumsal/kamu satış engeli kalkar | Yüksek | M | D | Müşteri güvenlik anketi geçme oranı |

**Önerilen sıra [Ç]:** (1) A1 + C6 -> (2) A2/A3/A4 -> (3) B1/B2 + C1/C2 -> (4) A7/C3 (self-servis) -> (5) B3-B6 segment bazlı.

## 11. Sınırlamalar

- Uygulama çalıştırılmadı; UX bulgularının çoğu EKIM2026 raporuna dayanır ([D]) ve bağımsız doğrulanmadı (yalnızca route/şablon/grep ile kısmi doğrulama).
- "Şifremi unuttum yok" bulgusu grep'e dayanır; giriş şablonunda bağlantı varsa dışarıda kalmış olabilir.
- Müşteri/segment yorumları [Ç].
