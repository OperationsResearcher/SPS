# KOKPİTİM — Claude için Master Proje Özeti
> Bu dosya Claude Projects'e yüklenir. Her oturumda bağlam bu dosyadan kurulur.
> Son güncelleme: 2026-03-23 | Proje versiyonu: TASK-034

---

## 1. PROJENİN TANIMI

**Kokpitim**, Türkiye pazarına özel, kurumsal strateji-süreç-bireysel performans yönetimini tek platformda birleştiren çok kiracılı (multi-tenant) bir SaaS uygulamasıdır.

**Benzersiz değer:** Strateji → Süreç → KPI → Bireysel Performans zinciri entegre — rakipler bunu ayrı modüllerle çözüyor.

**Kullanıcı rolleri:** `Admin`, `tenant_admin`, `executive_manager`, `user` (ve alt roller)

**Çalışma portu:** 5001 (5000 yasak)

---

## 2. TEKNOLOJİ STACK

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python 3.11, Flask (Application Factory pattern) |
| ORM | Flask-SQLAlchemy (tek instance: `extensions.py::db`) |
| Migration | Flask-Migrate / Alembic |
| Auth | Flask-Login (`session_protection = 'strong'`) |
| CSRF | Flask-WTF CSRFProtect |
| Güvenlik | Flask-Talisman (⚠️ `init_app` çağrısı eksik — pasif!) |
| Rate Limit | Flask-Limiter (⚠️ TAMAMEN DEVRE DIŞI — FakeLimiter mock) |
| Cache | Flask-Caching (SimpleCache, Redis opsiyonel) |
| WebSocket | Flask-SocketIO 5.3.5 + eventlet |
| Serialization | marshmallow 3.20.1 |
| Excel | openpyxl, pandas |
| JWT | PyJWT 2.8.0 |
| Hata Takip | Sentry SDK |
| Frontend CSS | Tailwind CSS (CDN — ⚠️ build yok) + özel CSS token sistemi |
| Frontend JS | Alpine.js, Chart.js 4.4.0, SweetAlert2 11 |
| Veritabanı | SQLite → `instance/kokpitim.db` |
| API Docs | flask-swagger-ui (`/micro/api/docs`) |

**Kritik bağımlılık notu:** `requirements.txt`'te paket versiyonları sabitlenmemiş — deployment kırılma riski.

---

## 3. MİMARİ YAPI

### 3.1 Uygulama Başlangıcı
```
app.py → create_app() → config.py → extensions init → blueprints register → app.run(5001)
```

### 3.2 Blueprint Haritası

| Blueprint | Prefix | Durum |
|-----------|--------|-------|
| `micro_bp` | `/micro` | ✅ AKTİF PLATFORM |
| `auth_bp` | `/auth` | Legacy (kök) |
| `main_bp` | `/` | Legacy (kök) |
| `api_bp` | — | Legacy (kök) |
| `admin_bp` | — | Legacy (kök) |
| `v2_bp`, `v3_bp` | — | Deneysel/eski |
| `bsc_bp`, `analysis_bp` | — | Legacy |

**Kritik:** `login_manager.login_view = 'auth.login'` → Korunan micro route'lara erişimde kök login'e yönlendiriyor, micro login'e değil.

### 3.3 Micro Modüller ve Route Sayıları

| Modül | Route | Açıklama |
|-------|-------|----------|
| admin | 22 | Kullanıcı, tenant, paket yönetimi |
| surec | 21 | Süreç yönetimi, KPI takibi |
| api | 15 | REST API (Swagger UI) |
| shared/auth | 5 | Profil, login |
| sp | 12 | Stratejik Planlama, SWOT |
| bireysel | 11 | Bireysel performans, karne |
| kurum | 8 | Kurum yönetimi, strateji |
| shared/ayarlar | 4 | E-posta ayarları |
| shared/bildirim | 4 | Bildirim yönetimi |
| analiz | 7 | Analiz modülü |
| hgs | 2 | ⚠️ KRİTİK: Login bypass riski var |
| masaustu | 1 | İskelet |
| proje | 1 | İskelet |

**Toplam micro route: ~113**

### 3.4 Veritabanı Modelleri

**Yeni katman (`app/models/`):** ~50 model — Tenant, Role, User, Process, ProcessKpi, Strategy, Individual*, Project, Task ve daha fazlası. Çoğunda `is_active` soft delete ✅

**Legacy katman (`models/`):** ~30 model — LegacyUser, LegacyNotification, Surec, AnaStrateji, AltStrateji vb.

---

## 4. KRİTİK GÜVENLİK SORUNLARI (Acil)

| # | Sorun | Risk | Çözüm |
|---|-------|------|-------|
| S1 | Rate Limiter devre dışı (FakeLimiter) | Brute force, DDoS | `extensions.py`'de gerçek Flask-Limiter aktif et |
| S2 | Hardcoded `SECRET_KEY` fallback | Session hijack | `config.py` ve `app/__init__.py` satır 32 temizle |
| S3 | `SESSION_COOKIE_SECURE` yok | HTTP'de cookie sızıntısı | `config.py`'ye ekle |
| S4 | Talisman `init_app` yok | CSP koruma pasif | `app/__init__.py`'de `talisman.init_app(app)` ekle |
| S5 | HGS login bypass | Kimlik doğrulamasız giriş | Production'da feature flag ile kapat |
| S6 | Scriptlerde hardcoded DB URL/şifre | Credential sızıntısı | `verify_count.py`, `transfer_data.py` temizle |

---

## 5. TEKNİK BORÇ HARİTASI

### 5.1 Yüksek Öncelik
- **Test coverage ~%5-15** — en büyük risk
- **Paralel iki sistem** — 130 legacy template + kök routes hâlâ aktif
- **Kök dizin kaosu** — 250+ debug/fix/seed script temizlenmemiş

### 5.2 Orta Öncelik
- N+1 sorgu riski — `karne_data()`, `hgs/routes.py`, `admin/routes.py`
- `process.py` 1397 satır — parçalanmalı
- Multi-tenant izolasyon manuel
- Tailwind CDN → yerel build gerekiyor

### 5.3 Düşük Öncelik
- `app/extensions.py` dead file — silinmeli
- `console.log` kalıntıları JS dosyalarında
- Legacy `alert()`/`confirm()` kalıntıları

---

## 6. FRONTEND DURUMU

| Dosya | Durum |
|-------|-------|
| `ui/static/platform/css/` | ✅ CSS token sistemi tutarlı |
| `ui/static/platform/js/` | ✅ SweetAlert2, data-* pattern doğru |
| `static/` (kök) | ⚠️ Legacy karmaşası |
| Responsive | ✅ Micro yapısı responsive |
| Tailwind | ⚠️ CDN kullanılıyor, build yok |

---

## 7. ÇALIŞMA KURALLARI (Tüm IDE'ler İçin)

1. **Altın kural:** Oku → Plan göster → Onay al → Uygula → TASKLOG → Test → Push
2. **Bildirim:** Sadece SweetAlert2, Türkçe
3. **PG:** Performans Göstergesi (PostgreSQL değil)
4. **Port:** 5001
5. **Backend:** İngilizce/snake_case | **Frontend:** Türkçe
6. **Hata:** `except: pass` yasak, `app.logger.error` zorunlu
7. **Silme:** Hard delete yasak, soft delete (`is_active=False`)
8. **Frontend:** Inline JS/CSS yasak, Jinja2 in JS yasak
9. **Mimari:** Blueprint zorunlu, `@login_required` zorunlu
10. **Görev sonu:** `Test et → TASKLOG güncelle → github_sync.py çalıştır`

---

## 8. TASKLOG ÖZETİ

- **Toplam task:** 34 (TASK-001 → TASK-034)
- **Tamamlanan:** 34 / Devam eden: 0 / Hata: 0
- **En çok sorun yaşanan:** `admin/users` (13 task), `auth/profil` (7 task)
- **Son task:** TASK-034 — Google Cloud deploy, veri migration, Docker image güncelleme

---

## 9. ÖLÇEKLENEBİLİRLİK

| Yapı | Kapasite |
|------|---------|
| SQLite + tek process | ~20-50 eşzamanlı kullanıcı |
| + Gunicorn 4 worker | ~100-150 |
| + PostgreSQL geçişi | ~200-500 |

---

## 10. REKABET KONUMU

**Rakipler:** Cascade Strategy, Perdoo, ClearPoint, Monday.com, Power BI

**Kokpitim'in avantajı:** Türkçe, strateji+süreç+bireysel performans entegre, multi-tenant SaaS altyapısı

---

## 11. CLAUDE İÇİN ÇALIŞMA PROTOKOLÜ

### Her Oturumda Yapılacak
1. Bu dosyayı oku (Projects'ten geliyor)
2. GitHub'dan güncel TASKLOG'u çek: `https://raw.githubusercontent.com/OperationsResearcher/SPS/main/docs/TASKLOG.md`
3. Son 5 task'ı oku, nerede kaldığımızı anla
4. "Hazırım. Son durum: TASK-[X]. [Kısa özet]." de

### Benim Rolüm
- Kiro/Cursor/AG için prompt yazmak
- Mimari kararlar için analiz ve öneri
- Güvenlik/teknik borç önceliklendirme
- TASKLOG'dan bağlam okuyarak nerede olduğumuzu takip etmek
- Hata yaptığımda "bilmiyorum, dosyayı göster" demek

---

## 12. GOOGLE CLOUD DEPLOY BİLGİLERİ

### GCP Hesap & Proje
- **Hesap:** mfgulen4660@gmail.com
- **Proje ID:** project-ab214714-b5d6-43db-b33

### VM Bilgileri
- **Instance adı:** sps-server-v2
- **Zone:** europe-west3-c
- **Makine tipi:** e2-medium
- **External IP:** 34.89.231.89
- **Durum:** RUNNING

### Bağlantı Komutu
```bash
gcloud compute ssh sps-server-v2 --zone=europe-west3-c
```

### Uygulama Yapısı
- Uygulama **Docker container** içinde çalışıyor
- Container adı: **sps-web**
- Image: sps_web_final:latest
- Port: 80 → 5000
- Dockerfile: `/home/kokpitim.com/public_html/Dockerfile`
- Python versiyonu: 3.11-slim

### Aktif Veritabanı
- **Container içi yol:** `/app/instance/kokpitim.db`
- **VM üzerindeki yol:** `/home/kokpitim.com/public_html/instance/kokpitim.db`
- **SQLAlchemy URI:** `sqlite:////app/instance/kokpitim.db`
- ⚠️ VM'deki diğer .db dosyaları BOŞ (0 byte) — karıştırma!

### Faydalı Komutlar
```bash
# Container içine gir
sudo docker exec -it sps-web bash

# DB'ye Python ile bağlan
sudo docker exec sps-web python3 -c "import sqlite3; ..."

# Docker loglarına bak
sudo docker logs sps-web --tail=50

# DB yedeği al (VM'de)
sudo docker cp sps-web:/app/instance/kokpitim.db /tmp/yedek_$(date +%Y%m%d).db

# Yedeği yerel bilgisayara indir (local terminalde)
gcloud compute scp sps-server-v2:/tmp/yedek_*.db ./ --zone=europe-west3-c

# Yereldeki DB'yi sunucuya gönder (local terminalde)
gcloud compute scp C:\kokpitim\instance\kokpitim.db sps-server-v2:/tmp/kokpitim_new.db --zone=europe-west3-c
```

---

## 13. VERİ MİGRASYON NOTLARI

### Durum: ✅ Tamamlandı (2026-03-23)

### Taşınan Veriler
| Tablo | Kayıt |
|-------|-------|
| kurum/tenants | 17 |
| user/users | 82 |
| surec/processes | 64 |
| surec_performans_gostergesi/kpi_data | 4.674 |
| bireysel_performans_gostergesi | 1.627 |
| audit_logs | 606 |

### Dikkat
- Eski tablo adları (`user`, `kurum`) → Yeni tablo adları (`users`, `tenants`)
- Migration script: `migrate_old_data.py`

---

## 14. CLAUDE İLE ÇALIŞMA KURALLARI

1. **Deneme yanılma yasak** — Bir çözüm önerilmeden önce tam analiz yapılmalı
2. **Tek seferde çöz** — "Şunu dene, olmazsa bunu" yaklaşımı kabul edilmez
3. **Önce analiz, sonra çözüm** — Sorunun kökü bulunmadan komut önerilmez
4. **Komut sayısı minimize** — Kullanıcıya yazdırılan komut sayısı en az olmalı
5. **Cursor'un kapasitesini kullan** — Kod değişiklikleri için Cursor'a prompt yaz, manuel komutla uğraşma
6. **Hata çıkarsa dur** — Aynı hataya farklı çözümler denemek yerine kökten analiz et
7. **"Bunu deneyelim" deme** — Ya kesin çözümü sun ya da "bilmiyorum" de
8. **Aynı komutu tekrar verme** — Çalışmayan bir komut tekrar verilmez, kök neden araştırılır

---

## 15. DEPLOY KONTROL LİSTESİ

### Her Deploy Öncesi
1. **DB yedeği al** — deploy öncesi mutlaka
2. **DB git'e dahil değil** — `.gitignore`'da, git push DB'yi taşımaz
3. **DB değişikliği varsa** — yereldeki `instance/kokpitim.db`'yi `gcloud compute scp` ile sunucuya gönder
4. **Siteyi test et** — login, veriler, sayfalar kontrol edilmeli

### Standart Deploy Komutları

**Yerelde (Cursor terminali — sırayla):**
```bash
git add -A
git commit -m "açıklama"
git push origin main
```

**Sunucuda (VM — tek komut):**
```bash
cd /home/kokpitim.com/public_html && sudo git pull origin main && sudo docker build -t sps_web_final:latest . && sudo docker stop sps-web && sudo docker rm sps-web && sudo docker run -d --name sps-web -p 80:5000 -v /home/kokpitim.com/public_html/instance:/app/instance sps_web_final:latest
```

**Log Kontrolü (VM):**
```bash
sudo docker logs sps-web 2>&1 | grep "No module\|OperationalError\|Listening" | head -5
```

### ⚠️ Kritik Uyarılar
- `git reset --hard` KULLANMA — sunucudaki manuel düzeltmeleri siler, `git pull` kullan
- DB deploy'a dahil değil — elle kopyalanmalı
- Container rebuild her seferinde tüm paketleri yeniden kurar — uzun sürer, normaldir
- `scikit-learn` ve `pywebpush` requirements.txt'te olmalı — eksikse site açılmaz