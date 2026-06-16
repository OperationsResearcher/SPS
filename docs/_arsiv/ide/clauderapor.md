# KOKPİTİM — Claude Kapsamlı Proje Analiz Raporu
> Tarih: 2026-04-05 | Hazırlayan: Claude Sonnet 4.6 | Kapsam: Tüm kaynak kodu, mimari, güvenlik, rekabet

---

## İÇİNDEKİLER
1. [Yönetici Özeti](#1-yönetici-özeti)
2. [Güvenlik Analizi](#2-güvenlik-analizi)
3. [Mimari Değerlendirme](#3-mimari-değerlendirme)
4. [Kod Kalitesi](#4-kod-kalitesi)
5. [Performans ve Ölçeklenebilirlik](#5-performans-ve-ölçeklenebilirlik)
6. [Test ve CI/CD](#6-test-ve-cicd)
7. [SWOT Analizi](#7-swot-analizi)
8. [Tehdit ve Fırsat Analizi](#8-tehdit-ve-fırsat-analizi)
9. [Rekabet Analizi](#9-rekabet-analizi)
10. [Öncelikli Aksiyon Planı](#10-öncelikli-aksiyon-planı)

---

## 1. YÖNETİCİ ÖZETİ

Kokpitim; kurumsal stratejik planlama, süreç yönetimi, KPI takibi ve performans değerlendirmesini tek çatı altında toplayan Flask tabanlı bir SaaS platformudur. Kod tabanı aktif geliştirme altında, tüm modüller işlevsel durumdadır.

**Genel Skor:**

| Boyut | Puan | Açıklama |
|---|---|---|
| Güvenlik | 7/10 | Temel güvenlik altyapısı sağlam; iki pratik boşluk mevcut |
| Mimari | 7.5/10 | Blueprint yapısı temiz; legacy model katmanı teknik borç |
| Kod Kalitesi | 8/10 | Standartlar büyük ölçüde uygulanmış |
| Performans | 7/10 | Cache ve pool doğru; bazı modüllerde N+1 riski |
| Test | 5/10 | %50 coverage hedefi; CI/CD pipeline yok |
| Ürün Olgunluğu | 8/10 | Kapsamlı özellik seti; düzenli geliştirme |

---

## 2. GÜVENLİK ANALİZİ

### 2.1 Güvenlik Altyapısı — Genel Durum: ✅ SAĞLAM

Temel güvenlik bileşenleri doğru yapılandırılmıştır:

- **Flask-Talisman + CSP:** `__init__.py` içinde production ve development için ayrı CSP profilleri. Production'da `force_https=True`, HSTS (1 yıl), `frame-ancestors: none` (clickjacking koruması), `form-action: self`.
- **SECRET_KEY:** `config.py:34-35` — ortam değişkeni zorunlu, boş bırakılırsa `RuntimeError`. Hardcoded fallback yok.
- **SESSION_COOKIE_SECURE:** Production'da `True`, development'ta `False`. `HttpOnly=True`, `SameSite=Lax`.
- **Flask-Limiter 3.5.0:** Gerçek rate limiter aktif (200/gün, 50/saat varsayılan). FakeLimiter yok.
- **CSRF:** Flask-WTF ile tüm form route'larında aktif. API route'larında `@csrf.exempt` — makul (14 adet, REST semantiği).
- **SQL Injection:** SQLAlchemy ORM kullanımı nedeniyle düşük risk. String interpolasyonlu SQL bulunamadı.
- **XSS:** SweetAlert2 zorunluluğu, `data-*` attribute standartı, `bleach` kütüphanesi mevcut.

---

### 2.2 Güvenlik Açıkları

#### 🔴 S1 — HGS: @login_required EKSİK (Yüksek Risk)

**Konum:** `micro/modules/hgs/routes.py:57-64`

```python
@app_bp.route("/MfG_hgs")
def hgs():          # ← @login_required YOK
    return _hgs_index()

@app_bp.route("/MfG_hgs/login/<int:user_id>")
def hgs_login(user_id):   # ← @login_required YOK
    return _hgs_login(user_id)
```

URL gizli tutulmuş (`/MfG_hgs`) ve `HGS_BYPASS_ENABLED` flag koruması var, ancak:
- URL bir kez sızdıysa (log, hata mesajı, kaynak kodu erişimi) herhangi biri erişebilir.
- `HGS_BYPASS_ENABLED=false` ise zaten login sayfasına yönlendiriyor — ama bu kontrol runtime'da.
- **Düzeltme:** `@login_required` ekle + production'da route'u tamamen devre dışı bırak.

---

#### 🟡 S2 — docker-compose.yml SQLite (Orta Risk)

**Konum:** `docker-compose.yml:10`

```yaml
DATABASE_URL: sqlite:////app/data/spsv2.db
```

Production ortamı PostgreSQL kullanıyor (Oracle VM), ancak `docker-compose.yml` hâlâ SQLite'a işaret ediyor. Bu dosyayla container başlatan biri yanlış DB ile çalışır. Veri kaybı ve tutarsızlık riski.

**Düzeltme:** `docker-compose.yml`'de `DATABASE_URL` ortam değişkeninden okunacak şekilde ayarla.

---

#### 🟡 S3 — `except Exception:` (Sessiz Hata Yutma)

**Konum:** `admin/routes.py:175,960,1170`, `api/routes.py:175`, `k_radar/routes.py:876,880`, `masaustu/routes.py:41,47`, `proje/routes_list.py:292`, `proje/routes_project_crud.py:87`

Toplam **10 adet** `except Exception:` satırı `app.logger.error()` çağrısı olmadan kullanılmış. Bu, üretim hatalarının sessizce yutulmasına, debug edilememesine yol açar. KURALLAR-MASTER'da açıkça yasaklanmış ama bazı dosyalarda uygulanmamış.

**Düzeltme:** Her `except Exception:` bloğuna `app.logger.error(f"[modül_adı] {e}")` ekle.

---

#### 🟡 S4 — @login_required Sayı Tutarsızlığı

260 route'a karşılık 253 `@login_required` dekoratörü var. 7 adet route korumasız. HGS dışındaki 6 route incelenmeli.

**Kontrol komutu:**
```bash
diff <(grep -rn "^@app_bp.route" micro/modules/ | sort) \
     <(grep -rn "@login_required" micro/modules/ | sort)
```

---

#### 🟢 S5 — Güvenli Olan Notlar (KURALLAR-MASTER'dan sapma yok)

- `extensions.py` DB instance tekli — başka yerde `SQLAlchemy()` yok.
- Tüm korunan route'larda `@login_required` + role kontrolü (admin route'ları `@admin_required`).
- Jinja2 `{{ }}` JS dosyalarında yok — `data-*` attribute standardı uygulanmış.
- `alert()`/`confirm()` kullanımı yok — SweetAlert2 tam uyum.
- Hard delete yok — soft delete (`is_active=False`) uygulanmış.

---

## 3. MİMARİ DEĞERLENDİRME

### 3.1 Uygulama Yapısı

```
app.py → create_app() → config.py → extensions init → blueprints → app.run(5001)
                                                              ↓
                                            platform_core/app_bp (14 modül)
                                            main_bp / auth_bp / api_bp (legacy)
```

**Güçlü yönler:**
- `platform_core` → `app_bp` blueprint mimarisi temiz.
- Tüm DB işlemleri `extensions.db` üzerinden — tekli instance.
- PostgreSQL zorunlu, pool `pre_ping=True`, `recycle=280s` (Cloudflare 524 timeout koruması).
- Modüler yapı: her özellik `micro/modules/[ad]/routes.py` içinde izole.

### 3.2 Blueprint Haritası

| Blueprint | Prefix | Satır | Durum |
|---|---|---|---|
| `app_bp` (micro) | `/` | ~6.500+ | ✅ Aktif, birincil |
| `main_bp` | `/` | — | ⚠️ Legacy |
| `auth_bp` | `/auth` | — | ⚠️ Legacy |
| `api_bp` | — | — | ⚠️ Legacy |
| `v2_bp`, `v3_bp` | — | — | 🗑️ Eski/deney |

**Teknik Borç:** 3 legacy blueprint hâlâ kayıtlı. Bunların kaldırılması güvenli mi test edilmeli.

### 3.3 Model Katmanı İkilemi

```
app/models/  (yeni — PostgreSQL uyumlu)         ~2.100 satır
models/      (legacy — SQLite uyumlu)           ~1.370 satır (379+552+139+300)
```

**Sorun:** `models/` klasöründeki legacy modeller (`LegacyUser`, `Surec`, `AnaStrateji`, `Project`) hâlâ aktif referanslarla dolu. İki paralel model katmanı:
- Test sürecini karmaşıklaştırıyor.
- Migration'larda çakışma riski.
- Yeni geliştirici için anlama maliyeti yüksek.

**Öneri:** `models/` klasöründen `app/models/`'e tam migrasyon için bir task oluştur.

### 3.4 Modül Tamamlanma Durumu

| Modül | Satır | Durum |
|---|---|---|
| `surec` | 1.939 | ✅ Üretim kalitesi |
| `admin` | 1.465 | ✅ Üretim kalitesi |
| `proje` | ~1.117 | ✅ Dağıtılmış yapı |
| `k_radar` | 935 | ✅ Üretim kalitesi |
| `sp` | 753 | ✅ + Yıllık dönem eklendi |
| `masaustu` | 623 | ✅ Üretim kalitesi |
| `bireysel` | 535 | ✅ İşlevsel |
| `kurum` | 390 | ✅ İşlevsel |
| `api` | 318 | ✅ REST + Swagger |
| `shared/auth` | 152 | ✅ İşlevsel |
| `analiz` | 143 | ⚠️ İskelet düzeyi |
| `shared/ayarlar` | 143 | ✅ İşlevsel |
| `shared/bildirim` | 65 | ⚠️ Minimal |
| `hgs` | 74 | ⚠️ Sadece geliştirme |

---

## 4. KOD KALİTESİ

### 4.1 Uyumluluk Skoru (KURALLAR-MASTER'a göre)

| Kural | Uyum |
|---|---|
| `extensions.db` tek instance | ✅ %100 |
| SweetAlert2 zorunluluğu | ✅ %100 |
| Jinja2 JS'de yasak | ✅ %100 |
| Hardcoded URL yasak | ✅ %100 |
| `url_for()` kullanımı | ✅ %100 |
| Hard delete yasak | ✅ %100 |
| `@login_required` | ⚠️ %97 (7 eksik) |
| `app.logger.error()` except'lerde | ⚠️ %70 (10 adet yok) |
| `console.log` yasak | ⚠️ 1 kalıntı (`k_radar.js:11`) |

### 4.2 Dosya Boyutu Uyarıları

`surec/routes.py` 1.939 satır ile tek dosyada çok fazla sorumluluğu barındırıyor. Önerilen ayrım:

```
surec/
├── routes_karne.py    (karne + KPI veri API'leri)
├── routes_kpi.py      (KPI CRUD)
├── routes_activity.py (faaliyet CRUD)
└── routes_process.py  (süreç CRUD)
```

### 4.3 Frontend Bağımlılık Haritası

```
base.html → SweetAlert2 (CDN), FontAwesome (CDN)
sp/index.html → sp.css, sp.js, sp_plan_year.js
karne.html → surec.css, surec.js, pg_tablo_modal.js
```

**Risk:** CDN bağımlılığı — SweetAlert2 veya FontAwesome CDN'i erişilmez olursa UI tamamen bozulur. Self-hosted veya fallback önerilir.

---

## 5. PERFORMANS VE ÖLÇEKLENEBİLİRLİK

### 5.1 Veritabanı

| Konu | Durum |
|---|---|
| Connection pool | ✅ `pre_ping=True`, `pool_recycle=280s` |
| İndex coverage | ✅ `add_performance_indexes.sql` (143 satır) |
| Sequence recovery | ✅ `fix_postgres_sequences.py` mevcut |
| N+1 sorgu | ⚠️ Bazı modüllerde (`bireysel`, `kurum`) `joinedload` yok |

**N+1 yüksek riskli alanlar:**
- `micro/modules/bireysel/routes.py` — `joinedload`/`selectinload` 0
- `micro/modules/kurum/routes.py` — `joinedload`/`selectinload` 0
- `micro/modules/analiz/routes.py` — `joinedload`/`selectinload` 0

### 5.2 Cache

- `Flask-Caching` aktif, `CACHE_KEY_PREFIX=kokpitim_`
- Redis backend destekleniyor; fallback SimpleCache (tek process, ölçeklenmez)
- Vizyon skoru ve K-Vektör hesapları `cache_utils.py` üzerinden cache'leniyor

**Eksik:** HTTP response cache header'ları (`Cache-Control`, `ETag`) statik asset'ler için ayarlanmamış.

### 5.3 Arka Plan Görevleri

- **APScheduler:** Görev hatırlatma, süreç aktivite planlama
- **Celery:** Ağır iş yükleri (ML anomali, webhook)
- **SocketIO:** Real-time bildirimler (eventlet worker)

**Risk:** Gunicorn 4 worker + eventlet aynı anda çalışıyor. eventlet'in Gunicorn prefork modu ile tam uyumu belgelenmiş, ancak memory leak riski uzun süre çalışan işlemlerde gözlemlenebilir.

### 5.4 Ölçeklenebilirlik Kısıtları

| Kısıt | Etki |
|---|---|
| Tek Docker container | Yatay ölçeklenme yok |
| Session: Flask default (cookie) | Multi-instance'ta session paylaşımı yok |
| SimpleCache fallback | Redis yoksa in-memory, process restart'ta temizlenir |
| Background tasks: APScheduler | Her container ayrı scheduler başlatır → duplicate jobs |

---

## 6. TEST VE CI/CD

### 6.1 Test Altyapısı

| Metrik | Değer |
|---|---|
| Test dosya sayısı | 11 |
| Minimum coverage | %50 (pytest.ini) |
| Test framework | pytest + pytest-cov |
| CI/CD pipeline | ❌ Yok (.github/ klasörü bulunamadı) |
| Integration test DB | SQLite in-memory (production PostgreSQL farkı) |

**Kritik Sorun:** Test ortamında SQLite, production'da PostgreSQL kullanılıyor. PostgreSQL'e özgü özellikler (sequence, JSON operatörler, pg-specific sorgu optimizasyonları) test edilemiyor. Mevcut migration production'da başarısız olabilir.

### 6.2 Eksik Test Alanları

- Plan Year sistemi (yeni — hiç test yok)
- K-Vektör motor hesaplamaları
- Yıl bazlı KPI başarı hesabı
- Şablon kopyalama akışı (clone_plan_year)
- HGS bypass devre dışı bırakma

### 6.3 CI/CD Önerisi

```
GitHub Actions önerilen pipeline:
1. lint (flake8/ruff)
2. test (pytest --cov=app)
3. security scan (bandit, safety)
4. docker build
5. staging deploy (auto)
6. production deploy (manual onay)
```

---

## 7. SWOT ANALİZİ

### Güçlü Yönler (Strengths)

**Ürün:**
- Strateji → Alt Strateji → Süreç → KPI → Faaliyet zinciri tam ve entegre
- K-Vektör: differansiasyon sağlayan özgün algoritma (rakiplerde yok)
- Yıllık dönem sistemi (PlanYear) — geriye dönük karşılaştırma altyapısı
- Çok kiracılı (multi-tenant) SaaS mimarisi
- Türkçe arayüz — yerel pazar avantajı

**Teknik:**
- Flask + SQLAlchemy 2.0 — modern, async-ready
- Blueprint modüler mimarisi — bağımsız geliştirme
- PostgreSQL zorunlu — kurumsal güvenilirlik
- Sentry entegrasyonu — production hata takibi
- Alembic migration yönetimi — schema versiyonlama
- Docker + GCP — cloud-native deploy

**Süreç:**
- KURALLAR-MASTER.md — tek gerçek kural kaynağı
- TASKLOG.md — tam iş takibi (TASK-001'den TASK-061'e)
- Soft delete standartı — veri kaybı önleme

---

### Zayıf Yönler (Weaknesses)

**Teknik Borç:**
- **İki model katmanı:** `app/models/` ve `models/` birlikte var — karmaşıklık
- **3 legacy blueprint** kayıtlı (main_bp, auth_bp eski, v2_bp/v3_bp deney)
- **`surec/routes.py` 1.939 satır** — tek dosyada aşırı yük
- **CI/CD yok** — her deploy manuel, hata riski yüksek
- **CDN bağımlılığı** — SweetAlert2, FontAwesome offline çalışmaz
- **APScheduler multi-instance sorunu** — yatay ölçeklemede duplicate görev
- **Session: cookie-based** — stateless ölçekleme için Redis session gerekli

**Test Zayıflıkları:**
- %50 coverage hedefi düşük; kritik iş mantığı kapsanmamış olabilir
- Test DB'si (SQLite) ≠ Production DB (PostgreSQL)
- Yeni PlanYear sistemi hiç test edilmemiş

**Ürün Boşlukları:**
- `analiz` ve `bildirim` modülleri iskelet düzeyde
- Proje modülü henüz SP/KPI ile tam entegre değil
- Mobil uygulama yok — yalnızca responsive web
- Raporlama modülü zayıf (Excel export var, PDF yok)
- API dökümantasyonu (Swagger mevcut ama eksik endpoint'ler var)

---

### Fırsatlar (Opportunities)

**Pazar:**
- Türkiye'de kurumsal stratejik planlama yazılımı pazarı büyüyor
- Kamu kurumları ISO 9001 / KYS yükümlülükleri — doğrudan hedef kitle
- Orta ölçekli şirketlerin ERP'ye alternatif arayışı
- Uzaktan çalışma artışı → dijital performans takibine talep

**Teknik Fırsatlar:**
- PlanYear altyapısı → yıllar arası karşılaştırma ekranı hazır
- K-Vektör algoritması → makale, patent, beyaz kitap fırsatı
- ML anomali servisi (`anomaly_service.py`) → predictive analytics ürünü
- Webhook servisi → 3. taraf entegrasyonlar (Teams, Slack, Jira)
- API katmanı → mobile app / 3. taraf geliştirici ekosistemi
- Celery + APScheduler → otomatik rapor gönderimi özelliği

**İş Modeli:**
- Mevcut multi-tenant → beyaz etiket (white-label) satışı
- Danışmanlık + yazılım hibrit model
- Sektöre özgü paket versiyonlar (kamu, sağlık, imalat)

---

### Tehditler (Threats)

**Teknik:**
- PostgreSQL sequence hatası üretimde tekrarlanabilir (yaşandı, TASK-058)
- Docker container tek nokta başarısızlığı (SPOF) — yük dengeleme yok
- GCP faturası kontrolsüz büyüyebilir (ML servisleri ağır)
- Redis olmadan cache in-memory kalır — container restart'ta cache sıfırlanır

**Güvenlik:**
- HGS URL'si sızarsa kimlik doğrulama bypass riski
- CDN kesintisinde UI tamamen kullanılamaz hale gelir
- Celery worker'ların monitoring'i yok — sessiz başarısız görevler

**İş:**
- Microsoft (Power BI + Planner), SAP, Oracle gibi büyük oyuncuların yerel adaptasyonu
- Yerli rakipler: Logo, Mikro, Aselsan yazılım kolları
- Müşteri kilitleme riski — veri export standardı olmadan

---

## 8. TEHDİT VE FIRSAT ANALİZİ (Detay)

### 8.1 Kritik Tehditler

| Tehdit | Olasılık | Etki | Önlem |
|---|---|---|---|
| HGS URL sızıntısı | Orta | Yüksek | Route'u production'da kaldır veya IP kısıtla |
| PostgreSQL sequence hatası | Yüksek | Yüksek | `fix_postgres_sequences.py` otomatik zamanla |
| CDN kesintisi | Düşük | Yüksek | Self-hosted statik kütüphaneler |
| CI/CD yokluğu — hatalı deploy | Yüksek | Orta | GitHub Actions pipeline kur |
| Duplicate APScheduler görevleri | Orta | Orta | Celery Beat'e geç |
| Cache miss storm (restart) | Orta | Orta | Redis zorunlu hale getir |

### 8.2 Stratejik Fırsatlar (Öncelik Sırası)

1. **K-Vektör tanıtımı** — Rakiplerde olmayan özgün algoritmanın pazarlanması
2. **API ekosistemi** — Public API → partner entegrasyonları (HRMS, ERP, BI araçları)
3. **Otomatik raporlama** — Celery + APScheduler → haftalık/aylık otomatik PDF rapor
4. **Mobil PWA** — Mevcut responsive HTML'i progressive web app'e dönüştür
5. **Veri analitik katmanı** — `ml_service.py` ve `anomaly_service.py` ürüne entegre
6. **Kamu segmenti** — KYS/ISO 9001 sertifikasyon süreçlerini destekleyen şablon paket

---

## 9. REKABET ANALİZİ

### 9.1 Doğrudan Rakipler (Türkiye)

| Rakip | Güçlü Yön | Zayıf Yön | Kokpitim Farkı |
|---|---|---|---|
| **Logo Tiger/GO** | Büyük marka, ERP entegrasyonu | SP modülü yok, kompleks | Özelleşmiş SP + K-Vektör |
| **Mikro Yazılım** | Yerel destek, muhasebe entegrasyonu | Performans takibi zayıf | KPI odaklı, yıllık dönem sistemi |
| **Artı Yazılım (QDMS)** | Süreç yönetimi güçlü, ISO uyumu | Fiyat yüksek, ağır kurulum | SaaS, hızlı başlangıç |
| **IdeaSoft** | E-ticaret ağırlıklı | SP yok | Tam SP + süreç zinciri |

### 9.2 Uluslararası Rakipler (Pazar Baskısı)

| Rakip | Tehdit Düzeyi | Not |
|---|---|---|
| **Microsoft Viva Goals** | Orta | OKR odaklı, SP değil; Power BI entegrasyonu güçlü |
| **Workday** | Düşük | Büyük kurum hedefli, pahalı, İngilizce ağırlıklı |
| **SAP SuccessFactors** | Düşük | Bireysel performans odaklı, SP yok |
| **Cascade Strategy** | Orta | SP odaklı SaaS; Türkçe yok, yerel destek yok |
| **Perdoo** | Düşük | OKR aracı, SP değil |
| **Quantive (Gtmhub)** | Orta | OKR + strateji; Türkçe yok |

### 9.3 Rekabet Avantajı Matrisi

| Özellik | Kokpitim | Cascade | Microsoft Viva | QDMS |
|---|---|---|---|---|
| Türkçe arayüz | ✅ | ❌ | Kısmi | ✅ |
| Strateji → KPI zinciri | ✅ | ✅ | ⚠️ | ⚠️ |
| Süreç yönetimi | ✅ | ❌ | ❌ | ✅ |
| Yıllık dönem karşılaştırma | ✅ | ⚠️ | ❌ | ❌ |
| K-Vektör ağırlıklı skor | ✅ | ❌ | ❌ | ❌ |
| Bireysel performans | ✅ | ⚠️ | ✅ | ❌ |
| ISO/KYS uyumu | ✅ | ❌ | ❌ | ✅ |
| Fiyat (yerel pazar) | 🟢 Uygun | 🔴 Pahalı | 🟡 Orta | 🔴 Pahalı |
| Mobil uygulama | ❌ | ✅ | ✅ | ❌ |
| API / Entegrasyon | ⚠️ | ✅ | ✅ | ⚠️ |

**Sonuç:** Kokpitim; Türkçe, süreç + strateji bütünleşikliği, K-Vektör özgünlüğü ve fiyat avantajı ile orta ölçekli Türk kurum pazarında güçlü konumda. Mobil uygulama ve API ekosistemi boşlukları kapatılmalı.

---

## 10. ÖNCELİKLİ AKSİYON PLANI

### 🔴 Acil (Bu Sprint)

| # | Aksiyon | Dosya | Süre |
|---|---|---|---|
| A1 | HGS route'una `@login_required` ekle veya production'da kaldır | `micro/modules/hgs/routes.py` | 30 dk |
| A2 | `docker-compose.yml` SQLite → `${DATABASE_URL}` | `docker-compose.yml` | 15 dk |
| A3 | 10 adet `except Exception:` bloğuna `app.logger.error()` ekle | admin, api, k_radar, masaustu, proje | 2 saat |
| A4 | `k_radar.js:11` console.log kaldır | `ui/static/platform/js/k_radar.js` | 5 dk |

### 🟡 Yakın Vadeli (1-2 Hafta)

| # | Aksiyon | Etki |
|---|---|---|
| B1 | CI/CD: GitHub Actions pipeline kur (lint + test + build) | Kalite güvencesi |
| B2 | Test DB'yi PostgreSQL'e taşı (conftest.py) | Test güvenilirliği |
| B3 | CDN bağımlılıklarını self-hosted'a al | Offline güvenilirlik |
| B4 | 7 korumasız route'u tespit et ve `@login_required` ekle | Güvenlik |
| B5 | PlanYear sistemi için test yaz | Yeni özellik güvencesi |
| B6 | `surec/routes.py` dosyasını 4 dosyaya böl | Maintainability |

### 🟢 Orta Vadeli (1-3 Ay)

| # | Aksiyon | Etki |
|---|---|---|
| C1 | `models/` → `app/models/` legacy migration tamamla | Teknik borç |
| C2 | Redis'i zorunlu hale getir (cache + session + Celery broker) | Ölçeklenebilirlik |
| C3 | APScheduler → Celery Beat (multi-instance güvenli) | Güvenilirlik |
| C4 | `analiz` ve `bildirim` modüllerini tamamla | Ürün olgunluğu |
| C5 | Public API dökümantasyonu + partner programı | Ekosistem |
| C6 | Yıllar arası karşılaştırma ekranı (PlanYear Faz 6) | Ürün değeri |
| C7 | Otomatik PDF rapor gönderimi (Celery + APScheduler) | Müşteri değeri |
| C8 | Mobil PWA dönüşümü | Pazar erişimi |

---

## EKLER

### Ek A: Analiz Kapsamı

```
Taranan dosyalar: ~150 Python, ~20 JS, ~15 HTML, ~10 CSS
Toplam satır: ~25.000+ (tahmini)
Analiz yöntemi: Statik kod analizi + mimari inceleme
```

### Ek B: Komut Referansı (Sürekli İzleme)

```bash
# Güvenlik kontrolleri
grep -rn "except Exception:\s*$" micro/ | grep -v "as e"
grep -n "@app_bp.route" micro/modules/ -r | wc -l
grep -n "@login_required" micro/modules/ -r | wc -l

# Teknik borç
grep -rn "{{ " ui/static/platform/js/          # Jinja2 JS'de (sıfır olmalı)
grep -rn "console\.log" ui/static/platform/js/  # (sıfır olmalı)
grep -rn "alert\(\|confirm\(" ui/              # SweetAlert2 kuralı

# Performans
grep -rn "\.all()" micro/modules/ | wc -l       # Toplam sorgu sayısı
grep -rn "joinedload\|selectinload" micro/ | wc -l  # Eager loading

# Test
cd /kokpitim && pytest --cov=app --cov-report=term-missing
```

---

*Bu rapor Claude Sonnet 4.6 tarafından statik kod analizi yöntemiyle hazırlanmıştır. Dinamik analiz (çalışma zamanı profil, penetrasyon testi) için ayrıca profesyonel güvenlik denetimi önerilir.*
