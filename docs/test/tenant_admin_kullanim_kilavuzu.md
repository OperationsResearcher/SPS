# Tenant Admin Kullanım Kılavuzu

> **Versiyon:** 1.0
> **Tarih:** 2026-05-24
> **Hedef:** Tenant Admin rolündeki kullanıcı (kurum yöneticisi)
> **Amaç:** Hangi ekranda ne yapacağınızı eksiksiz anlatmak

---

## İçindekiler

1. [Hoş Geldiniz](#1-hoş-geldiniz)
2. [İlk Girişte Yapacaklarınız](#2-i̇lk-girişte-yapacaklarınız)
3. [Stratejik Planlama](#3-stratejik-planlama)
4. [Süreç Yönetimi](#4-süreç-yönetimi)
5. [Bireysel Performans](#5-bireysel-performans)
6. [K-Radar (KPI İzleme)](#6-k-radar-kpi-i̇zleme)
7. [Proje Portföyü](#7-proje-portföyü)
8. [Raporlama (K-Rapor)](#8-raporlama-k-rapor)
9. [Kurum Ayarları](#9-kurum-ayarları)
10. [Kullanıcı Yönetimi](#10-kullanıcı-yönetimi)
11. [AI Yapılandırması](#11-ai-yapılandırması)
12. [Bildirim ve E-posta](#12-bildirim-ve-e-posta)
13. [Yedekleme ve Veri](#13-yedekleme-ve-veri)
14. [Sık Karşılaşılan Sorunlar](#14-sık-karşılaşılan-sorunlar)
15. [Yetki Hiyerarşisi](#15-yetki-hiyerarşisi)

---

## 1. Hoş Geldiniz

Tenant Admin olarak Kokpitim'de **kurumunuzun tüm yetkili kullanıcısısınız**. Sistemin tüm yönlerini kontrol edebilirsiniz:

- Strateji oluşturma, plan yılı yönetimi, senaryo dallandırma
- KPI tanımlama, süreç yapılandırma
- Initiative açma, milestone takibi
- AI yapılandırması (kendi API key'inizle veya sistem AI'sıyla)
- Kullanıcı ekleme, rol atama
- Raporlama, dışa aktarma
- Kurum profili, logo, e-posta ayarları

**Bu kılavuzu okurken:**
- Her aksiyon `Sayfa → Buton → Aksiyon` formatında
- 🔒 işareti = "yetki gereksin" uyarısı
- ⚠️ işareti = dikkat edilmesi gereken nokta
- ✅ işareti = doğru/önerilen yaklaşım

---

## 2. İlk Girişte Yapacaklarınız

Bir tenant ilk açıldığında **5 dakika içinde** yapmanız gereken kurulum:

### Adım 1: Profil tamamla
**Sayfa:** Sağ üst köşe → kullanıcı avatarı → "Profil"

- Adınız, telefonunuz, fotoğrafınız
- Şifrenizi karmaşık bir şeye çevirin
- (Önerilen) 2FA etkinleştirin

### Adım 2: Kurum profilini doldur
**Sayfa:** Sol menü → **Kurum Paneli** → **Ayarlar**

- Kurum adı, logo (PNG/JPG), açıklama
- İletişim e-posta, telefon, web sitesi
- Sektör (KOBİ Dijital Dönüşüm raporları için önemli)

### Adım 3: Kurumsal kimliği yaz
**Sayfa:** Sol menü → **Stratejik Planlama** → ana sayfa → "Misyon" / "Vizyon" / "Değerler" sekmeleri

- **Misyon:** Kurumun var olma sebebi (2-3 cümle)
- **Vizyon:** Olmak istediğiniz yer (2-3 cümle)
- **Değerler:** Davranış ilkeleri (madde madde)

### Adım 4: Plan yılı aç
**Sayfa:** Sol menü → **Stratejik Planlama** → **Plan Yılları**

- "Yeni Plan Yılı" butonuna tıkla
- Yıl seç (örnek: 2026)
- "Boş başla" veya "Şablondan başla" (SBB Kamu / sektörel)

### Adım 5: İlk stratejilerinizi ekle
**Sayfa:** Sol menü → **Stratejik Planlama** → ana sayfa → "Stratejiler"

- En az 3-5 ana strateji tanımlayın
- Her stratejinin altına 2-4 alt strateji ekleyin

### Adım 6: Kullanıcıları çağırın
**Sayfa:** Sol menü → **Admin** → **Yönetim Paneli**

- Kullanıcı ekle → e-posta + rol seç (manager, kullanıcı, lider vb.)
- Sistem geçici şifre üretir, kullanıcıya mail gider

### Adım 7: (Opsiyonel) AI'yı yapılandırın
**Sayfa:** Sol menü → **Stratejik Planlama** → **AI Ayarları**

- "Sistem AI" → ücretsiz başla
- Veya "Kendi anahtarım" → BYOK (kendi Gemini/OpenAI key'iniz)

---

## 3. Stratejik Planlama

### 3.1 Ana Sayfa
**Sayfa:** `/sp`

Stratejik planlama akışınızın merkezi sayfası. Üst kısımda **akış olgunluk göstergesi** (4 adım: Misyon, Vizyon, Değerler, Stratejiler) — kaçı tamamlanmış görürsünüz.

**Bileşenler:**
- Misyon kartı (düzenle butonu)
- Vizyon kartı (düzenle butonu)
- Değerler kartı (düzenle butonu)
- Stratejiler tablosu (Strategy ↔ SubStrategy hiyerarşi)

**Buton: "Strateji Ekle"** → modal açılır:
- Kod (örn: AS1)
- Başlık
- Açıklama
- K-Vektor ağırlığı (Finansal/Müşteri/Süreç/Öğrenme yüzdesi)

**🔒 Yetki:** `tenant_admin`, `executive_manager`, `ust_yonetim` veya `Admin`

### 3.2 Plan Yılı Yönetimi
**Sayfa:** `/sp/donemler`

Burada **tüm plan yıllarınızı görür** ve yönetirsiniz.

**Aksiyonlar:**

| Buton | Ne yapar |
|---|---|
| **Yeni Plan Yılı** | Boş yıl açar |
| **Klonla** | Mevcut yıldan kopyalama (Full Clone) |
| **Aktif Yap** | Bu yılı çalışılan yıl olarak ata |
| **Kapat** | Status'u `closed` yap, üzerine yazılamasın |
| **Arşivle** | Listede gizle |

**Yeni Yıl Sihirbazı** (`/sp/sihirbaz/yeni-yil`):
1. Kaynak yıl seç
2. Önizleme: hangi stratejiler/süreçler kopyalanacak göster
3. "Uygula" → klon tamamlanır

⚠️ Aynı yıla iki normal plan açılamaz (`uq_plan_year_tenant_year_main` partial unique). Ama **senaryolar** açılabilir.

### 3.3 Senaryolar (What-if)
**Sayfa:** `/sp/scenarios`

Aynı plan yılından paralel senaryo dalları:
- **Baseline:** standart varsayım
- **Optimistic:** iyimser (örn: yatırım büyütüldü)
- **Pessimistic:** kötümser (örn: kriz)

**Adım adım:**
1. "Yeni Senaryo" → kaynak plan year seç
2. Etiket: baseline / optimistic / pessimistic
3. Sistem tüm yapıyı klonlar (`scenario_of_id` ile bağlı)
4. Senaryoyu açıp KPI hedeflerini, Initiative'leri değiştirebilirsiniz

✅ Senaryolar bağımsız — birinde KPI hedefi değiştirmek diğerini etkilemez.

### 3.4 Initiative'ler (Çok Yıllı Girişimler)
**Sayfa:** `/sp/initiatives`

Çok yıla yayılan stratejik projeler (örn: "Dijital Dönüşüm 2026-2028"):

**Buton: "Yeni Initiative"**
- Kod, ad, açıklama
- start_year, end_year
- Strateji/alt strateji bağlantısı (opsiyonel)
- Durum (planned/in_progress/on_hold/completed)
- Öncelik (critical/high/medium/low)
- Toplam bütçe (opsiyonel)

**Milestone ekleme:** Initiative kartına tıkla → "Milestone Ekle":
- Ad, hedef tarih, sıralama

### 3.5 Replan Trigger'lar (Otomatik Yeniden Planlama)
**Sayfa:** `/sp/replan-triggers`

Belirli koşullar gerçekleştiğinde otomatik strateji yeniden değerlendirme:

**Trigger tipleri:**
- `kpi_below_target` — KPI N dönem üst üste hedef altında
- `overdue_activity_pct` — Gecikmiş faaliyet oranı %X'i aştı
- `risk_score` — Risk skoru threshold'u geçti
- `anomaly_high` — Yüksek-severity KPI anomalisi

**Buton: "Yeni Trigger"**
- Ad, tip
- Target KPI ID (sadece kpi_below_target için)
- Operatör (< / > / vb.) + eşik değer
- Consecutive periods (ardışık dönem sayısı)
- Aksiyon (notify / suggest_pivot / create_review)
- Önem seviyesi

**Buton: "Şimdi Değerlendir"** → tüm aktif trigger'ları test eder, tetiklenen olur ise event açar + AI Pivot'a yönlendirir.

### 3.6 Çeyreklik Review
**Sayfa:** `/sp/ceyreklik-review`

Modern strateji cadence pattern'ı: yıllık vizyon → çeyreklik ayarlama → aylık check-in.

**Adımlar:**
1. Yıl ve çeyrek seç (Q1/Q2/Q3/Q4)
2. "Review Oluştur"
3. Otomatik olarak gelir:
   - KPI durumu (toplam, veri olan, hedef üstü %)
   - Strateji + alt strateji sayısı
   - OKR ortalama ilerleme
   - Faaliyet (aktif, gecikmiş, kapanan)
   - Risk (açık, kritik)
   - Anomali (yüksek, orta)
   - **Aksiyon önerileri** (heuristik kural motoru)

### 3.7 Exec Dashboard
**Sayfa:** `/sp/exec-dashboard`

Üst yönetim için tek bakışta strateji sağlığı:

**Hero kart:** Strateji Sağlık Skoru (0-100, ağırlıklı 4 boyut)

**6 KPI tile:**
- KPI Hedef Üstü %
- Initiative Sağlığı (devam edenlerin ortalama ilerleme)
- Gecikmiş Faaliyet
- Kritik Risk
- Yüksek Anomali
- Aktif Trigger

**"AI Pivot Önerisi Al" butonu:**
- LLM çağrısı (Gemini veya BYOK)
- 3-5 somut pivot önerisi gelir: pivot_type, title, rationale, action, priority, timeframe
- Maliyet ve kota durumu panel başlığında görünür

### 3.8 Hoshin Kanri X-Matrix
**Sayfa:** `/sp/xmatrix`

4 çeyrekli korelasyon matrisi:
- **Kuzey:** Uzun Vadeli Stratejiler
- **Doğu:** Yıllık Hedefler (alt stratejiler)
- **Güney:** İnitiative'ler
- **Batı:** Ölçülebilir KPI'lar

Kesişim hücrelerinde dolu nokta (●) = bağlantı var. Üst yönetim toplantısında **"hangi strateji hangi KPI ile ölçülüyor?"** sorusunu görsel cevaplar.

### 3.9 Blue Ocean Strategy
**Sayfa:** `/sp/blue-ocean`

**Buton: "Yeni Canvas"**
- Ad, sektör, açıklama
- Rakipler (virgülle ayrılmış)

Canvas açtıktan sonra:

**Faktör Ekleme:**
- Ad (Fiyat, Kalite, Hız, Dijital Entegrasyon vb.)
- Kendi puanınız (1-10)
- Rakip puanları (JSON: {"RakipA": 7, "RakipB": 4})

Chart.js otomatik **Value Curve** çizer — kim hangi faktörde önde görsel.

**ERRC Grid:**
- ❌ **Eliminate** (Kaldır)
- ⬇️ **Reduce** (Azalt)
- ⬆️ **Raise** (Yükselt)
- ⭐ **Create** (Yarat)

Her aksiyon için: metin + gerekçe + etki (high/medium/low).

### 3.10 VRIO Analizi
**Sayfa:** `/sp/vrio`

Kurumsal kaynak/yetenek matrisi. Her kaynak için **4 soruyu işaretlersiniz**:

- **V**aluable (Değerli mi?)
- **R**are (Nadir mi?)
- **I**nimitable (Taklit zor mu?)
- **O**rganized (Kurumsallaşmış mı?)

Sistem otomatik Barney karar ağacına göre etiket basar:
- Hiç V yok → "Rekabetçi Dezavantaj"
- V var, R yok → "Rekabet Paritesi"
- V+R var, I yok → "Geçici Rekabet Avantajı"
- V+R+I var, O yok → "Kullanılmayan Avantaj"
- V+R+I+O hepsi → **"Sürdürülebilir Rekabet Avantajı"** ⭐

### 3.11 OKR
**Sayfa:** `/sp/okr`

Objective + Key Result yapılandırması:
- "Yeni Objective" → ad, sahip, hedef tarih
- Her objective'in 2-5 KR'si olur
- KR → ProcessKpi'ya bağlanabilir (gerçek veri ile beslensin)

### 3.12 Şablon Marketplace
**Sayfa:** `/sp/templates`

Hazır plan şablonları:
- **SBB Kamu** (Cumhurbaşkanlığı Strateji Bütçe Başkanlığı uyumlu)
- **OKR Sade** (sadece OKR yapısı)
- (gelecekte) Sektörel şablonlar (SaaS, Sağlık, Üretim)

**Buton: "Bu şablonu uygula"** → hedef yıl seç → tüm strateji/alt strateji/KPI ağacı tek tıkla oluşur.

### 3.13 Strateji Haritası
**Sayfa:** `/sp/strateji-haritasi`

vis-network interaktif grafik:
- Düğümler: Strategy (mor), SubStrategy (açık mor), Process (yeşil), KPI (turuncu), Initiative (pembe)
- Kenarlar: ilişkiler
- Tıkla → detaya in

---

## 4. Süreç Yönetimi

### 4.1 Süreç Listesi
**Sayfa:** `/process` (veya `/surec`)

Tüm süreçleri görürsünüz. Filtreler:
- Durum (Aktif/Pasif)
- Rol (Lider/Üye olduklarınız)
- Plan yılı

**Buton: "Yeni Süreç"** → modal:
- Ad, kod, açıklama
- Lider seç (en az 1)
- Üyeler (multi-select)
- Bağlı alt stratejiler (contribution_pct ile)
- Ağırlık

### 4.2 Süreç Karnesi
**Sayfa:** `/process/<id>/karne`

KPI'ların aylık matris görünümü:

| KPI | Hedef | Birim | Oca | Şub | Mar | ... |
|---|---|---|---|---|---|---|
| Müşteri Memn. | 75 | % | 72 | 74 | 76 ✅ | ... |
| Şikayet Süresi | 15 | gün | 18 ❌ | 16 | 14 ✅ | ... |

Hücreye tıkla → veri giriş modal'ı:
- Aktual değer
- Hedef (admin tarafından)
- Not (opsiyonel)
- Kaydet → `KpiData` tablosuna yazılır + audit log

**Buton: "Excel İndir"** → tüm KPI verisi xlsx olarak iner.
**Buton: "Toplu İmport"** → Excel'den toplu veri yükle.

### 4.3 Faaliyetler
**Sayfa:** `/process/<id>/faaliyetler`

Sürece bağlı operasyonel faaliyetler:
- Ad, durum (Planlandı/Devam Ediyor/Tamamlandı/İptal/Ertelendi)
- Sorumlu kişi(ler)
- Başlangıç/bitiş tarihi
- İlerleme yüzdesi

**Aksiyonlar:** Ekle, güncelle, tamamla, ertele, iptal et, takip et (ay işareti).

### 4.4 KPI Yönetimi
**Buton:** Süreç detayında "KPI Ekle"

- Kod, ad, birim, hedef değer
- Yön (higher better / lower better)
- Dönem (Günlük/Haftalık/Aylık/Çeyreklik/Yıllık)
- Veri toplama yöntemi (RG/HKY/HK/SH/DH/SGH)
- Başarı aralıkları
- Ağırlık (toplam süreç içinde)
- Önemli mi (`is_important` flag)

---

## 5. Bireysel Performans

### 5.1 Bireysel Karne (Kullanıcı için)
Bu sayfaya **siz de kendi karnenize bakabilirsiniz** — bireysel performansınız.

**Sayfa:** `/bireysel/karne`

Atadığınız diğer kullanıcıların karnelerini görmek için admin paneli kullanın.

### 5.2 Bireysel Performans Göstergesi (PG) Atama
Manager rolündeki kullanıcılar kendi PG'lerini açar. Admin olarak siz **toplu açma** yapabilirsiniz:

**API:** `POST /bireysel/api/pg/ensure-from-process-kpi`
- Bir süreç KPI'sından otomatik bireysel PG oluşturur

---

## 6. K-Radar (KPI İzleme)

### 6.1 K-Radar Hub
**Sayfa:** `/k_radar`

Üst seviye özet kartlar:
- Toplam risk sayısı
- Kritik risk sayısı
- Anomali listesi
- Erken uyarı sayısı

### 6.2 Risk Yönetimi
**Sayfa:** `/k_radar/risk`

**Buton: "Risk Ekle"**
- Risk tanımı, kategori
- Olasılık (1-5), Etki (1-5)
- Skor: probability × impact (16+ = kritik)
- Mitigation planı
- Sahibi

Risk Heat Map: 5x5 grid, sıcaklığa göre renk.

### 6.3 Paydaş Analizi
**Sayfa:** `/k_radar/cross/paydas`

Stakeholder map: Etki vs İlgi düzeyi 2x2 grid.

### 6.4 KP Modülleri (Kalite Parametreleri)
- `/k_radar/kp/darbogaz` — Darboğaz analizi
- `/k_radar/kp/oee` — OEE (Overall Equipment Effectiveness)
- `/k_radar/kp/vsm` — Value Stream Map
- `/k_radar/kp/kapasite` — Kapasite planlama
- `/k_radar/kp/olgunluk` — Süreç olgunluk modeli (CMMI tarzı)
- `/k_radar/kp/benchmark` — Benchmarking

### 6.5 KPR (Proje Radar)
- `/k_radar/kpr/cpm` — Critical Path Method
- `/k_radar/kpr/evm` — Earned Value
- `/k_radar/kpr/risk` — Proje risk
- `/k_radar/kpr/gantt` — Gantt görünümü

### 6.6 KS (Strateji Radar)
- `/k_radar/api/ks/swot-summary` — SWOT özet
- `/k_radar/api/ks/bsc` — Balanced Scorecard
- `/k_radar/api/ks/efqm` — EFQM RADAR
- `/k_radar/api/ks/hoshin` — Hoshin Kanri analiz
- `/k_radar/api/ks/ansoff` — Ansoff matrisi
- `/k_radar/api/ks/bcg` — BCG matrisi

---

## 7. Proje Portföyü

### 7.1 Proje Listesi
**Sayfa:** `/project/list`

Tüm projeler tablo halinde. Filtreler: durum, sahip, plan yılı, tarih aralığı.

**Buton: "Yeni Proje"** → form:
- Ad, açıklama, kod
- Başlangıç/bitiş tarihi
- Sorumlu (PM)
- Plan yılı
- Strateji bağlantısı (opsiyonel)

### 7.2 Proje Detay
**Sayfa:** `/project/<id>`

Sekmeli görünüm:
- **Özet:** Toplam görev, ilerleme %, bütçe kullanımı
- **Görevler:** Task listesi
- **Gantt:** `/project/<id>/views/gantt`
- **Kanban:** `/project/<id>/views/kanban`
- **RAID:** `/project/<id>/views/raid` (Risks/Assumptions/Issues/Dependencies)
- **Takvim:** `/project/<id>/views/calendar`
- **EVM:** API `/sp/api/projects/<id>/evm` (PV/EV/AC + CPI/SPI + Kritik Yol)

### 7.3 Görev Yönetimi
Görev ekleme: Liste sayfasında "Hızlı Ekle" veya detay sayfasında "Yeni Görev".

**Görev alanları:**
- Ad, açıklama
- Sorumlu
- Başlangıç/bitiş tarihi
- İlerleme (%) — EVM hesabında kritik
- Planlanan bütçe (EVM için)
- Gerçek maliyet (EVM için)
- Bağımlılık (`depends_on_task_id` — CPM için)
- Durum

---

## 8. Raporlama (K-Rapor)

### 8.1 K-Rapor Dashboard
**Sayfa:** `/k_rapor`

Kurumsal sağlık özeti widget'ları.

### 8.2 30+ API Endpoint'i
- Trend analizi
- Forecast (tahmin)
- Kurumsal özet
- Uyum analizi (alignment)
- Risk raporu
- EVM
- Stratejik analiz
- Paydaş analizi
- Rekabet analizi
- PG dağılımı
- Faaliyet matrisi
- Aktivite takvimi
- Kurum karşılaştırması (multi-tenant)
- Strateji kapsama
- SWOT trend

### 8.3 Excel Export
**Sayfa:** `/k_rapor` → "Excel İndir"
Tüm dönem verisini xlsx olarak.

### 8.4 PDF Export
"PDF İndir" → WeasyPrint ile (yoksa reportlab fallback).

### 8.5 Haftalık Digest
**Sayfa:** `/sp/digest/weekly.pdf` (PDF) veya `/sp/digest/weekly.html` (HTML)

Strateji sağlık özetinin haftalık otomatik raporu. Üst yönetim e-postasına gitsin diye (cron ile zamanlanabilir).

### 8.6 Webhook / Slack
**Buton:** "Webhook Test"

Anomali tespit edildiğinde Slack/Teams/Discord'a otomatik bildirim gönderir.

---

## 9. Kurum Ayarları

### 9.1 Kurum Profili
**Sayfa:** `/kurum/ayarlar`

- Kurum adı, açıklama
- Logo yükleme (PNG/JPG, max 5MB)
- İletişim bilgileri
- Web sitesi

### 9.2 K-Vektor Ağırlıkları
**Sayfa:** Kurum panelinde "K-Vektor"

BSC perspektif yüzdeleri:
- Finansal: %20
- Müşteri: %30
- İşletme: %30
- Öğrenme: %20

(Toplam 100 olmalı)

### 9.3 Yıla Özgü Kurumsal Kimlik (TenantYearIdentity)
Her plan yılı için ayrı misyon/vizyon/değer tutabilirsiniz. Önceki yıldan klonlanır, isteğe göre düzenlenir.

---

## 10. Kullanıcı Yönetimi

### 10.1 Yönetim Paneli
**Sayfa:** `/admin/yonetim-paneli`

Tenant içindeki tüm kullanıcıları görür ve yönetirsiniz.

**Sekmeler:**
- Kullanıcılar (liste)
- İstatistikler (login sayısı, aktivite)
- Kullanıcı Detay
- Aktiviteler (audit log)

### 10.2 Yeni Kullanıcı Ekle
**Buton:** "Yeni Kullanıcı"

- E-posta (zorunlu)
- Ad, soyad
- Rol (manager, kullanıcı, surec_lideri, vb.)
- Geçici şifre üretilir veya manuel girilir
- Aktiflik durumu

⚠️ Tenant Admin yalnızca **kendi tenant'ı içinde** kullanıcı yönetebilir. Platform Admin tüm tenant'ları görür.

### 10.3 Rol Değiştirme
Kullanıcı detayında "Rol Değiştir" dropdown'ı.

**🔒 İzin verilen roller:** manager, kullanıcı, surec_lideri, kalite, izleyici, executive_manager. Diğer roller Platform Admin tarafından atanır.

### 10.4 Şifre Sıfırlama
Kullanıcı detayında "Şifre Sıfırla" butonu → geçici şifre üretilir, mail gönderilir.

### 10.5 Pasifleştirme
"Pasif Yap" → kullanıcı login olamaz ama verisi korunur (soft delete).

---

## 11. AI Yapılandırması

### 11.1 AI Ayarları Sayfası
**Sayfa:** `/sp/ayarlar/ai`

**İki mod var:**

**Mod 1: Kokpitim Sistem AI'sı**
- Ücretsiz, kotalı
- Günlük 50 / aylık 500 çağrı
- Gemini 2.5 Flash Lite (varsayılan)
- Kotaları aşılırsa kural motoruna düşer

**Mod 2: Kendi API Anahtarımı Kullan (BYOK)**
- Sağlayıcı seçin:
  - Google Gemini
  - OpenAI (ChatGPT)
  - Anthropic (Claude)
  - Groq (hızlı, ücretsiz katman geniş)
  - OpenRouter (200+ model)
- Model adı (boş bırakırsanız varsayılan)
- API Key (şifreli saklanır)
- (OpenRouter için) Base URL
- KVKK PII maskeleme açık/kapalı

**Buton: "Anahtarı Test Et"**
- Hello world tarzında 1 token'lık çağrı
- ✓ Başarılı / ✗ Hata
- Son test bilgisi sayfada görünür

✅ BYOK kullanırken sistem kotanız harcanmaz, kendi sağlayıcınızın faturasına gider.

### 11.2 LLM Kullanım Paneli
**Sayfa:** `/sp/llm-usage`

- Bugünkü kullanım (X/50)
- Aylık çağrı (X/500)
- Aylık maliyet ($X/$2)
- Son 50 çağrı detayı (provider, model, token, maliyet, durum)
- 14 günlük breakdown grafiği

---

## 12. Bildirim ve E-posta

### 12.1 E-posta Yapılandırması
**Sayfa:** `/ayarlar/eposta`

SMTP ayarları:
- Sunucu (örn: smtp.gmail.com)
- Port (587 TLS, 465 SSL)
- Kullanıcı adı, şifre
- Gönderici adres
- TLS/SSL seçimi

**Buton: "Test E-posta Gönder"** → kendinize test maili.

### 12.2 Bildirim Merkezi
**Sayfa:** `/bildirim`

Sistem bildirimleri listesi:
- Yeni süreç atandı
- KPI hedef altında
- Faaliyet bitiş tarihi yaklaşıyor
- Trigger ateşlendi

**Aksiyonlar:**
- "Tümünü Okundu İşaretle"
- Tek tek okundu işaretleme

---

## 13. Yedekleme ve Veri

### 13.1 Yedekleme Sayfası
**Sayfa:** `/ayarlar/yedekleme`

- **Yedek önizleme (veri):** Tablolar + satır sayıları
- **Yedek önizleme (tam sistem):** + dosyalar
- **Takvim ayarı:** Otomatik yedek günleri
- **İndir:** Tek seferlik dışa aktarma

### 13.2 KVKK Veri Dışa Aktarma
**API:** `POST /api/user/export-my-data`

Kullanıcının kendi verisini JSON olarak alabilmesi (KVKK Madde 11 — Taşınabilirlik).

### 13.3 KVKK Hesap Silme
**API:** `POST /api/user/delete-my-account`

KVKK Madde 7 — kişisel veri imha hakkı. Soft delete + anonimleştirme (e-posta → `deleted_{hash}@anonim.local`).

⚠️ Son tenant admin silinemez — önce yetki transferi yapılmalı.

---

## 14. Sık Karşılaşılan Sorunlar

### S1: "Yetkim yok" hatası alıyorum
**Sebep:** Rolünüz `tenant_admin` değil.
**Çözüm:** Platform Admin'e başvurun veya kendi rolünüzü kontrol edin: `/admin/yonetim-paneli` → kullanıcı listesi → kendinizi bulun.

### S2: Plan year aktif değil
**Belirti:** "Dönem seçilmemiş" uyarısı.
**Çözüm:** `/sp/donemler` → en az bir plan yılı oluşturun ve "Aktif Yap".

### S3: AI önerisi gelmiyor
**Olası sebepler:**
1. Sistem `GEMINI_API_KEY` tanımlı değil → kural motoru çalışır
2. Kotanız doldu → `/sp/llm-usage` kontrol et
3. BYOK key yanlış → `/sp/ayarlar/ai` → "Test Et"

**Hızlı çözüm:** `/sp/ayarlar/ai` → "Sistem AI" modunu seç (ücretsiz, başlangıçta yeter).

### S4: KPI veri girişi yapamıyorum
**Sebepler:**
1. KPI pasif (`is_active=False`)
2. Plan yılı kapalı (status=`closed`)
3. Sürecin üyesi/lideri değilsiniz

**Çözüm:** KPI'yı `/process/api/kpi/update/<id>` ile aktif yap. Plan year status'ü `active` olmalı.

### S5: Senaryo silmek istiyorum ama olmuyor
**Önemli:** Yalnızca **senaryo** olan plan yılları silinebilir (`scenario_of_id != NULL`). Ana plan yılları silinmez (sadece kapatılır).

### S6: Plan yılı klonlandı ama veriler yok
**Sebep:** "Overlay Clone" (sadece YearConfig) seçilmiş.
**Çözüm:** Tekrar oluştururken **"Full Clone"** seçeneğini kullanın. Tüm strateji/KPI/süreç klonlanır.

### S7: Strateji haritasında her şey yığılmış görünüyor
**Sebep:** Çok fazla node (200+) varsa vis-network görünümü karmaşıklaşır.
**Çözüm:** Sadece aktif plan yılı stratejilerini filtrele. Strategy seviyesinde başla, gerek oldukça expand et.

### S8: Excel raporu indiriliyor ama açılmıyor
**Sebep:** Tarayıcı pop-up engelliyor olabilir.
**Çözüm:** İndirme bildirimlerini izin verin veya sayfayı yenileyip tekrar deneyin.

### S9: Logo yükleyemiyorum, "dosya çok büyük" diyor
**Çözüm:** Logo PNG/JPG, max 5MB olmalı. Tinify, Squoosh gibi araçlarla küçültün.

### S10: Yeni kullanıcı mail almıyor
**Sebep:** E-posta yapılandırması eksik.
**Çözüm:** `/ayarlar/eposta` → SMTP ayarlarını yapın + "Test E-posta Gönder" ile doğrulayın.

---

## 15. Yetki Hiyerarşisi

```
PLATFORM ADMIN
├── Tüm tenant'lar
├── Sistem ayarları
├── Bakım modu
└── Paket yönetimi

    │
    ▼ (Tenant Admin'e devr)

TENANT ADMIN ← SİZ
├── SP modülü → tam yetki
├── Kurum ayarları → tam
├── Süreç yönetimi → tam (+ activity ek kontrol)
├── Proje → tam (PRIVILEGED_ROLES içinde)
├── Bireysel → kendi + ekibi
├── K-Rapor → tam (digest gönderme dahil)
├── K-Radar → görüntüleme
├── Admin paneli → kendi tenant kullanıcıları
├── E-posta/yedekleme ayarları → tam
└── Bildirim → tam

    │
    ▼

EXECUTIVE MANAGER (SP açısından eşit)
├── SP → tam
├── Kurum → tam
└── Diğerleri kısıtlı

    │
    ▼

MANAGER / NORMAL ROLES
├── Kendi hedefleri/görevleri
├── Atandığı süreç KPI'ları
└── Sistem yönetim erişimi YOK
```

---

## Hızlı Aksiyon Kartı (Cheat Sheet)

| İhtiyacım | Sayfa |
|---|---|
| Yeni plan yılı açmak | `/sp/donemler` → "Yeni Plan Yılı" |
| Strateji eklemek | `/sp` → "Strateji Ekle" |
| KPI tanımlamak | `/process/<id>` → "KPI Ekle" |
| Çeyrek raporu | `/sp/ceyreklik-review` |
| AI yapılandırması | `/sp/ayarlar/ai` |
| Senaryo oluşturmak | `/sp/scenarios` → "Yeni Senaryo" |
| Initiative açmak | `/sp/initiatives` → "Yeni Initiative" |
| Kullanıcı eklemek | `/admin/yonetim-paneli` → "Yeni Kullanıcı" |
| Logo yüklemek | `/kurum/ayarlar` |
| E-posta ayarı | `/ayarlar/eposta` |
| Excel rapor | `/k_rapor` → "Excel İndir" |
| Haftalık PDF | `/sp/digest/weekly.pdf` |
| LLM kullanım | `/sp/llm-usage` |
| Exec dashboard | `/sp/exec-dashboard` |

---

## Bağlantılı Belgeler

- [`docs/test/kokpitimtanitim.md`](kokpitimtanitim.md) — Genel proje tanıtımı
- [`docs/test/tenant_kullanici_kilavuzu.md`](tenant_kullanici_kilavuzu.md) — Standart kullanıcı için
- [`docs/AI-POLITIKASI.md`](../AI-POLITIKASI.md) — AI kuralları
- [`docs/UI-KILAVUZU.md`](../UI-KILAVUZU.md) — Tasarım sistemi

**Sorun çözülmüyor mu?** Platform Admin'inize başvurun veya destek talebi açın.
