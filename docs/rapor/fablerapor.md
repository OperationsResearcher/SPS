# KOKPİTİM — Kapsamlı Durum Değerlendirme Raporu

> **Hazırlayan:** Claude (Fable 5) — yerel kod tabanı taraması (3 paralel derin analiz: mimari/teknik borç, güvenlik/operasyon, ürün envanteri)
> **Tarih:** 2026-07-08 · **Kaynak:** `c:\kokpitim` (son commit `964dd55`)
> **Kapsam:** Güçlü yönler · İyileştirmeye açık alanlar · Rakip karşılaştırması (avantaj/dezavantaj + giderme yolları) · Yol haritası

---

## 1. YÖNETİCİ ÖZETİ

Kokpitim, **871 route, ~29 bin satırlık modern `micro/` katmanı, 343 kart, 13 modül** ile olgunlaşmış bir çok-kiracılı kurumsal performans ve strateji yönetim SaaS'ıdır. Ürün tarafında rakiplerin çoğunda bulunmayan **uçtan uca entegre zincir** (Vizyon → Strateji → Süreç → PG → Bireysel Karne → Proje) ve özgün **K-Vektör Vizyon Skoru (1000 puan)** ile net bir farklılaşma vardır. Strangler modernizasyonu %86 oranında tamamlanmıştır (593 modern / 96 legacy route).

**En kritik 5 bulgu:**

1. **S3 rate limit borcu fiilen açık:** 8 worker'lı gunicorn + `memory://` storage → login brute-force limiti pratikte 8 kat gevşek. Tek satırlık `.env` düzeltmesiyle kapanır.
2. **Tenant izolasyonu merkezi değil:** 414 elle yazılmış `tenant_id` filtresi; tek unutulan filtre cross-tenant veri sızıntısı demektir. Çok-kiracılı SaaS'ta bu en yüksek yapısal risktir.
3. **142 sessiz `except...pass`** — TASK-228'de kanıtlanmış veri kaybı kaynağı (PostgreSQL aborted transaction → sessiz rollback).
4. **171 relationship'te sıfır eager-load** → sistemik N+1 riski; guard testleri var ama kök tanımlar düzeltilmemiş.
5. **`api/routes.py` 4550 satır / 89 route** — tek dosyada dev API yüzeyi; bakım ve regresyon riski.

Bunların hiçbiri "yeniden yazım" gerektirmez; strangler stratejisiyle uyumlu, kademeli kapatılabilir borçlardır.

---

## 2. GÜÇLÜ YÖNLER

### 2.1 Ürün / İş değeri
- **Entegre zincir (temel farklılaştırıcı):** Strateji → Süreç → KPI/PG → Bireysel Karne → Proje tek platformda ve **canlı bağlı** — PG verisi girildiğinde K-Vektör Vizyon Skoru anında güncellenir. Rakiplerin çoğu bu katmanları ayrı ürün/modül olarak satar.
- **K-Vektör (özgün IP):** 1000 puanlık vizyon bütçesi modeli + `k_vektor_config_snapshots` ile geriye dönük denetim izi. Taklit edilmesi zor, anlatması kolay bir metrik.
- **K-Radar (27 bileşen):** BSC, EFQM, EVM, CPM, VSM, OEE, SLA, Pareto, Sankey, AI koçluk — üst yönetim karar-destek paketi olarak L3 amiral gemisi.
- **Zengin strateji araç kutusu:** SWOT/TOWS, PESTEL, Porter 5 Güç, VRIO, BCG, Ansoff, Mavi Okyanus, Hoshin X-Matrix, Strateji Haritası, OKR, senaryo planlama — akademik/danışmanlık literatürünün neredeyse tamamı üründe.
- **AI katmanı yaygın:** Stratejik Asistan, AI Koç/Danışman raporları, AI Sunum üretici, doğal dil sorgulama, AI Yapı-Danışmanı (KOE üstüne).
- **KOE + Başlangıç paketi stratejisi:** Veri girecek personeli olmayan, olgunlaşmamış kurumlara "yarı-kurulu + AI-yorumlu" deneyim — rakiplerin kaçındığı segmente bilinçli konumlanma.
- **Holding/bayi çok-kurum mimarisi:** `parent_tenant_id` alt kurumlar, konsolide dashboard + drilldown — Türkiye'deki holding/bayi yapısına doğrudan uyar.
- **Giriş engelsiz canlı demo:** 4 kurum (Tom1/2/3/Tomofil) her biri bir tier'ı temsil eder; Tomofil'de 7 yıllık gerçek veri (~99k satır). Satış hunisi için güçlü araç.
- **Entegrasyon yüzeyi:** REST API + Swagger/OpenAPI 3.0, BI connector (Power BI/Tableau), Excel export, Celery ile zamanlanmış raporlar, KVKK veri sahibi endpoint'leri.

### 2.2 Mühendislik / Süreç disiplini
- **Strangler disiplini kodla zorlanıyor:** CI'daki import-policy guard'ları (`check_no_raw_models_import` vb.) legacy'ye geri dönüşü mekanik olarak engelliyor. %86 modern oran somut ilerleme.
- **Auth kapsaması fiilen tam:** 769 route'un korunması gerekenlerinin tamamı `@login_required` (+ admin route'larda ikinci `_is_admin()` katmanı). Tarama korumasız route açığı **bulamadı**.
- **2FA (TOTP) + SSO + brute-force kilidi** mevcut; `SECRET_KEY` yoksa uygulama açılmıyor; hardcoded secret yok; `.env` git'te takip edilmiyor.
- **SQL injection riski düşük:** ORM ağırlıklı; raw SQL'lerde değerler parametreli, f-string yalnızca iç sabitlerle.
- **Deploy güvenliği düşünülmüş:** `oracle_safe_deploy.sh` — yedek → satır sayısı before/after karşılaştırması → fark varsa alarm. 30 gün retention'lı otomatik yedekler.
- **48 test dosyası + CI:** Karne hesapları, N+1 guard'ları, login throttle, legacy sunset testleri — kritik iş mantığı test altında.
- **Dokümantasyon kültürü:** TASKLOG (228 task), SISTEM-HARITASI, KURALLAR-MASTER tek-kaynak disiplini — kurumsal hafıza güçlü, bu ölçekte tek kişilik projede nadir görülür.

---

## 3. İYİLEŞTİRMEYE AÇIK ALANLAR

Öncelik sırasıyla; her madde etki × çaba değerlendirmesi içerir.

### 🔴 P1 — Güvenlik/veri bütünlüğü (hemen)

| # | Sorun | Kanıt | Çözüm | Çaba |
|---|---|---|---|---|
| 1 | **Rate limit fiilen etkisiz (S3)** — `memory://` + 8 worker → limit ×8 gevşek | `config.py:127`, `security.py:25-32` uyarı logu | Yayın/Test/Demo `.env`'e `RATELIMIT_STORAGE_URL=redis://...` | Saatlik |
| 2 | **Tenant izolasyonu elle** — 414 dağınık `tenant_id` filtresi, merkezi guard yok | `micro/` genelinde | SQLAlchemy `with_loader_criteria` ile global tenant filtresi + cross-tenant erişim regresyon testi | 2-3 gün |
| 3 | **142 sessiz `except...pass`** — kanıtlı veri kaybı (TASK-228) | tarama + TASKLOG-228 | Toplu tarama: her birine `app.logger.error()` + gerekiyorsa re-raise; transaction içindekiler öncelikli | 1-2 gün |
| 4 | **CSP `'unsafe-inline' 'unsafe-eval'`** — XSS'e karşı CSP kalkanı delik | `app/__init__.py:87-91` | Inline script kalıntılarını temizle (kural §3 zaten yasaklıyor), sonra CSP'den çıkar; `unsafe-eval` bağımlısı kütüphaneyi tespit et | 2-4 gün |
| 5 | **74 `@csrf.exempt`** — SameSite=Strict tek savunma | micro/main/app geneli | JSON API'lerde header tabanlı CSRF token'a geçir veya muafiyetleri gerekçelendirip azalt | 2-3 gün |

### 🟠 P2 — Performans ve sağlamlık

| # | Sorun | Kanıt | Çözüm | Çaba |
|---|---|---|---|---|
| 6 | **Sistemik N+1** — 171 relationship, 0 `joined/subquery`, yalnız 3 `selectin` | model taraması | Sıcak yollardan başlayarak (karne, k_rapor, proje listesi) `lazy='selectin'` veya sorgu-bazlı `selectinload()`; mevcut N+1 guard testlerini genişlet | 3-5 gün |
| 7 | **`api/routes.py` 4550 satır / 89 route** | dosya | Alan bazlı bölme (projects/process/analytics/ai); davranış değişmeden taşıma | 2-3 gün |
| 8 | **Log rotasyonu yok** — `error.log` sınırsız büyüyor | `error_tracking.py` | `RotatingFileHandler` (10MB × 5) | Saatlik |
| 9 | **X-Frame-Options çelişkisi** — Talisman `DENY` vs `security.py` `SAMEORIGIN` | iki dosya | Tek değere sabitle (`DENY` öner) | Saatlik |
| 10 | **Bağımlılık pin'sizliği** — 36 paketten 29'u pinsiz; `eventlet==0.33.3` (2021) | requirements.txt | `pip-compile` ile lock dosyası; eventlet → yerine `gevent` veya threading değerlendirmesi; CI Python 3.11 = prod eşleşmesini koru | 1 gün |

### 🟡 P3 — Kod sağlığı ve süreç

| # | Sorun | Çözüm | Çaba |
|---|---|---|---|
| 11 | **Üç servis dizini + 7 çift-isimli dosya** (`services/`, `app/services/`, `micro/services/`) | `app/services/` canonical ilan et; çiftleri diff'leyip birleştir, kök `services/`'i strangler'a al | 3-5 gün |
| 12 | **51 template'te Jinja2-in-JS** | TASK-227'deki `tojson` yaklaşımını kalan dosyalara yay; `data-*` attribute standardı | Kademeli |
| 13 | **CI'da lint/type-check/coverage gate yok** | `ruff` (hızlı kazanım) + `--cov-fail-under=50` aktifleştir; mypy'yi yeni koda sınırla | 1 gün |
| 14 | **`docker-compose.yml` bayat** — `sps-web` + SQLite (config reddediyor) | Gerçek PG'li compose yaz veya dosyayı `scripts/_arsiv/`'e taşı | Saatlik |
| 15 | **console.log kalıntıları** (114 satır) + `.env`'de `HGS_BYPASS_ENABLED` artığı | Toplu temizlik | Saatlik |
| 16 | **Legacy çift yüzey (S1)** — `main/` 96 route hâlâ canlı | Mevcut sunset middleware ile trafiği ölç → sıfır trafikli route'ları çeyreklik dalgalarla kapat (route silme refleksi: url_for ref'lerini aynı commit'te tara) | Sürekli |

### 🟢 P4 — Ürün olgunlaşması

| # | Alan | Not |
|---|---|---|
| 17 | **Kart-düzeyi lisans zorlaması yok** — gating modül granülerliğinde; Başlangıç paketinde L2/L3 kartları sızabiliyor | Tier stratejisi ciddiyse `system_cards` tablosu zaten var — kart→paket eşlemesi + render-time enforcement |
| 18 | **PDF export bazı yerlerde placeholder** | Satış öncesi "mevcut" kolonuna yazılmadan tamamlanmalı |
| 19 | **i18n EN kataloğu** — altyapı bağlı, statik katman TR'de tam; EN çeviri olgunlaşıyor; deploy edilmedi | Yurtdışı/İngilizce satış hedefine bağlı önceliklendirme |
| 20 | **`mock_*` deney modülleri** (metaverse/DAO vb.) | Satış yüzeyinden ve repodan ayıkla — demo gösterimlerinde güven zedeler |

---

## 4. RAKİP KARŞILAŞTIRMASI

Karşılaştırma seti: küresel strateji-yürütme platformları (Cascade Strategy, Quantive/Gtmhub, ClearPoint Strategy, Spider Impact, KPI Fire, Perdoo, Workboard) + genel OKR/BI araçları (monday, Asana Goals, Power BI) + Türkiye'de yaygın pratik (Excel + danışman).

> Not: Bu bölüm modelin sektör bilgisine dayanır (bilgi kesimi Ocak 2026); fiyat/özellik teyidi gereken yerlerde güncel doğrulama önerilir.

### 4.1 Avantajlarımız

| Avantaj | Rakiplerdeki durum | Değeri |
|---|---|---|
| **Uçtan uca zincir tek üründe** (strateji+süreç+KPI+birey+proje) | Cascade/Quantive strateji-OKR odaklı, süreç karnesi ve bireysel performans zayıf; proje yönetimi çoğunda entegrasyonla | Tek sözleşme, tek veri modeli, tek skor — CIO'ya "5 araç yerine 1" anlatısı |
| **K-Vektör Vizyon Skoru** | Benzeri yok; ClearPoint/Spider skorlama sunar ama vizyon-bütçesi matematiği özgün | Yönetim kuruluna tek sayı; denetim izli (snapshot) |
| **Türkçe-öncelikli + yerel kavram seti** (karne, PG, kamu SP mevzuat uyumu potansiyeli) | Küresel rakipler TR lokalizasyonunda zayıf/yok; TR yerli rakipler ise dar kapsamlı | Kamu + KOBİ + holding segmentinde dil/mevzuat bariyeri bizim lehimize |
| **Holding/bayi alt-kurum konsolidasyonu** | Kurumsal tier'larda ve pahalı; çoğunda yok | Türkiye'nin holding/bayi ağı yapısına doğal uyum |
| **Olgunlaşmamış kurum segmenti (KOE + AI Yapı-Danışmanı)** | Rakipler "verisi hazır" kurumları hedefler | Rekabetsiz alan (mavi okyanus): veri girmeden değer üreten endeks |
| **Fiyat esnekliği** | Cascade/Quantive kullanıcı başına $/ay, kurumsal tier'lar yüksek | Küresel SaaS'a TL bazlı, tier'lı alternatif |
| **Giriş engelsiz gerçek-verili demo** | Rakiplerde tipik olarak satış görüşmesi sonrası sandbox | Satış huni sürtünmesi düşük |
| **AI katmanı bütün modüllere yayılmış** | Rakiplerde AI çoğunlukla özet/asistan düzeyinde, üst tier | Koç/danışman/sunum/NLP sorgu — segment farklılaştırıcı |

### 4.2 Dezavantajlarımız ve giderme yolları

| Dezavantaj | Rakip kıyası | Giderme yolu |
|---|---|---|
| **Marka/referans eksikliği** | Cascade "binlerce kurum", ClearPoint kamu referansları | 2-3 pilot kurumdan vaka çalışması + KPI'lı başarı hikâyesi; demo ortamı zaten hazır — pazarlama sitesine vaka sayfaları |
| **Tek geliştirici / bus factor = 1** | Rakipler ekip + 7/24 destek | Dokümantasyon zaten güçlü (TASKLOG/HARITA); ek olarak: kritik akışların runbook'u, en az bir yedek geliştirici/ajans anlaşması, SLA tanımı |
| **Entegrasyon ekosistemi dar** | Quantive/Workboard: Jira, Slack, Teams, Salesforce, ERP konnektörleri | Öncelik sırası: (1) Excel/CSV import sihirbazı — TR pazarında en kritik, (2) Microsoft Teams bildirim webhook'u, (3) Logo/Netsis/SAP mali veri konnektörü. Swagger altyapısı hazır — konnektör başına 1-2 hafta |
| **Mobil uygulama yok** | Rakiplerin çoğunda native/PWA mobil | `requirements-pwa.txt` başlangıcı var — PWA'yı tamamlamak (push zaten var: pywebpush) native'den önce yeterli |
| **Tek sunucu, tek bölge** (Oracle VM, dikey ölçek) | Rakipler çoklu-bölge bulut | Kısa vade: mevcut yedek disiplini + restore tatbikatı yeterli; müşteri sayısı artınca managed PG + container orkestrasyon. Şimdiden: aylık restore tatbikatını takvime bağla |
| **Sertifikasyon yok (ISO 27001, SOC2, KVKK belgeleme)** | Kurumsal satışta rakipler SOC2 sunar | Kamu/kurumsal ihalede şart olacak: önce KVKK uyum dokümanı (VERBİS, aydınlatma, veri envanteri — API'de KVKK endpoint'leri zaten var), sonra ISO 27001 hedefi |
| **EN/uluslararası hazırlık yarım** | Rakipler çok dilli | i18n altyapısı bağlı; TR pazarı doyana kadar bilinçli erteleme savunulabilir — karar netleştirilmeli |
| **Özellik genişliği > özellik derinliği algısı riski** | Perdoo gibi dar-odaklı rakipler "basitlik" satar | Paketleme/L1-L2-L3 maruz-kalma stratejisi tam da bunu çözüyor — kart-düzeyi gating (P4-17) tamamlanınca "overwhelm" itirazı kapanır |
| **Placeholder özellikler** (bazı PDF exportlar, mock modüller) | — | Satış yüzeyinden ayıkla; "mevcut/yol haritası" ayrımını pazarlama sitesinde dürüst tut |

---

## 5. YOL HARİTASI

### Faz 0 — "Hızlı kapanışlar" (1 hafta, toplam ~2-3 gün efor)
- [ ] Yayın/Test/Demo `.env` → `RATELIMIT_STORAGE_URL=redis://...` (**S3 kapanır**)
- [ ] `RotatingFileHandler` (P2-8)
- [ ] X-Frame-Options tek değere (P2-9)
- [ ] `docker-compose.yml` düzelt/arşivle (P3-14)
- [ ] `.env` `HGS_BYPASS_ENABLED` artığı + console.log temizliği (P3-15)
- [ ] CI'ya `ruff` + coverage gate %50 (P3-13)

### Faz 1 — "Veri güvenliği ve bütünlüğü" (2-4 hafta)
- [ ] **Merkezi tenant izolasyonu:** `with_loader_criteria` global filtre + cross-tenant regresyon test paketi (P1-2) — çok-kiracılı SaaS'ın sigortası
- [ ] **`except...pass` seferberliği:** 142 blok; transaction içindekiler önce (P1-3)
- [ ] `@csrf.exempt` envanteri ve azaltma (P1-5)
- [ ] Bağımlılık lock dosyası + eventlet kararı (P2-10)
- [ ] Aylık **restore tatbikatı** rutini (yedeğin geri dönebildiğinin kanıtı)

### Faz 2 — "Performans ve borç eritme" (1-2 ay, paralel yürür)
- [ ] N+1: karne → k_rapor → proje listesi sırasıyla eager-load (P2-6); N+1 guard testlerini bu sayfalara genişlet
- [ ] `api/routes.py` parçalama (P2-7)
- [ ] Servis katmanı konsolidasyonu — 7 çift dosyadan başla (P3-11)
- [ ] CSP sıkılaştırma: inline script temizliği → `unsafe-inline` kaldır (P1-4)
- [ ] Legacy sunset: `main/` trafik ölçümü → sıfır trafikli route dalgası (P3-16)

### Faz 3 — "Ticari olgunlaşma" (2-4 ay, iş önceliklerine göre)
- [ ] **Kart-düzeyi paket zorlaması** (P4-17) — tier stratejisinin teknik tamamlayıcısı
- [ ] Placeholder PDF exportların tamamlanması (P4-18)
- [ ] **Excel/CSV veri import sihirbazı** — TR pazarında en çok istenecek entegrasyon
- [ ] Pilot müşteri vaka çalışmaları → pazarlama sitesine referans sayfaları
- [ ] KVKK uyum dosyası (aydınlatma metni, veri envanteri, VERBİS)
- [ ] Teams/Slack bildirim webhook'u

### Faz 4 — "Ölçek ve genişleme" (6+ ay, tetikleyici: müşteri sayısı)
- [ ] PWA tamamlama (mobil deneyim)
- [ ] ERP/mali yazılım konnektörleri (Logo/Netsis öncelikli)
- [ ] i18n EN kataloğunun deploy'u (yurtdışı kararına bağlı)
- [ ] Managed PostgreSQL + çoklu-instance mimari değerlendirmesi
- [ ] ISO 27001 yol haritası
- [ ] Demo v2: per-session schema izolasyonu (trafik artarsa — mevcut Yol B mutabakatı geçerli)

### Yol haritası ilkeleri
1. **Faz 0-1 pazarlıksızdır** — güvenlik/bütünlük borcu ticari büyümeden önce kapanmalı; tek bir cross-tenant sızıntı olayı ürünün en güçlü satış argümanını (güvenilir tek-kaynak) yok eder.
2. **Strangler devam** — sıfırdan yazma reddedildi (doğru karar); her faz mevcut dokuya kademeli işler.
3. **L paketleri kuralı geçerli** — biriken işler yerelde tamamlanır, deploy kullanıcı kararıyla.
4. **Her fazın çıkışında TASKLOG + test** — mevcut disiplin korunur.

---

## 6. SONUÇ

Kokpitim, ürün vizyonu ve kapsam genişliği açısından küresel rakiplerle yarışabilecek, Türkiye pazarında ise dil/mevzuat/segment konumlanmasıyla **yapısal avantaja sahip** bir platformdur. Kod tabanı, tek geliştiricili bir proje için istisnai bir dokümantasyon ve süreç disipliniyle yönetilmektedir. Teknik borç gerçektir ama **ölümcül değildir** ve tamamı kademeli kapatılabilir niteliktedir.

Kritik denklem şudur: ürünün en güçlü satış vaadi "kurumun tüm performans gerçeğini tek güvenilir kaynakta toplamak"tır — bu vaadi taşıyan teknik temel (tenant izolasyonu, veri bütünlüğü, rate limit) Faz 0-1'de sağlamlaştırılmalı, ticari genişleme (kart-gating, import sihirbazı, referanslar) bunun üzerine inşa edilmelidir.
