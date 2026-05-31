# KOKPİTİM — Claude için Master Proje Özeti
> Bu dosya Claude Projects'e yüklenir. Her oturumda bağlam bu dosyadan kurulur.
> Son güncelleme: 2026-05-19 | Proje versiyonu: TASK-105

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
| Güvenlik | Flask-Talisman (`FLASK_ENV=production` → CSP aktif) |
| Rate Limit | Flask-Limiter (login limit; prod’da `REDIS_URL` önerilir) |
| Cache | Flask-Caching (SimpleCache, Redis opsiyonel) |
| WebSocket | Flask-SocketIO 5.3.5 + eventlet |
| Serialization | marshmallow 3.20.1 |
| Excel | openpyxl, pandas |
| JWT | PyJWT 2.8.0 |
| Hata Takip | Sentry SDK |
| Frontend CSS | Tailwind CSS (CDN — bilinçli; prod uyarısı zararsız) + `ui/static/platform/css` |
| Frontend JS | Alpine.js, Chart.js 4.4.0, SweetAlert2 11 |
| Veritabanı | PostgreSQL (`SQLALCHEMY_DATABASE_URI` zorunlu) |
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
| `app_bp` (platform) | `/` (kök) | ✅ AKTİF PLATFORM (`ui/`) |
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
| hgs | 2 | Gizli `/MfG_hgs`; prod’da `HGS_BYPASS_ENABLED=false` zorunlu |
| masaustu | 6+ | Komuta merkezi, takvim, widget |
| proje | 20+ | Portföy CRUD, görevler |

**Toplam micro route: ~113**

### 3.4 Veritabanı Modelleri

**Yeni katman (`app/models/`):** ~50 model — Tenant, Role, User, Process, ProcessKpi, Strategy, Individual*, Project, Task ve daha fazlası. Çoğunda `is_active` soft delete ✅

**Legacy katman (`models/`):** ~30 model — LegacyUser, LegacyNotification, Surec, AnaStrateji, AltStrateji vb.

---

## 4. GÜVENLİK DURUMU (2026-05)

| # | Konu | Durum |
|---|------|--------|
| S1 | Rate limiter | ✅ Aktif; login limit; prod Redis önerilir |
| S2 | SECRET_KEY | ✅ Ortam değişkeni zorunlu |
| S3 | Session cookie secure | ✅ `config.py` |
| S4 | Talisman CSP | ✅ Production’da aktif |
| S5 | HGS bypass | ✅ `ProductionConfig.HGS_BYPASS_ENABLED = False` |
| S6 | Script credential | ⚠️ ARCHIVE/script’leri commit dışı tut |

Detay: `docs/KURALLAR-MASTER.md` §7, `docs/DEPLOY_SMOKE_CHECKLIST.md`

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
- Tailwind CDN → bilinçli (yerel build isteğe bağlı)
- Legacy route birleştirme → `docs/LEGACY_ROUTE_INVENTORY.md`

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

## 12. ÜRETİM SUNUCUSU (VM = ORACLE CLOUD)

> **Terim (2026-05-21):** Doküman ve sohbette **«VM»** = Oracle üretim. Tek referans: `docs/ORACLE-PROD-VM.md`

### Oracle VM (canlı — www.kokpitim.com)
| | |
|-|-|
| Instance | `kokpitim-v2` |
| IP | `129.159.30.175` |
| SSH | `ubuntu@129.159.30.175` (anahtar: yerel `.ssh` / `C:\crt\...`) |
| Uygulama dizini | `/opt/kokpitim/app` |
| Container | `kokpitim-web` (`kokpitim_web:latest`, `--network host`) |
| `.env` | `/opt/kokpitim/.env` |
| `instance/` | `/opt/kokpitim/instance` |
| Canlı DB | PostgreSQL `kokpitim_db` (yalnızca `127.0.0.1:5432`) |

### Bağlantı
```powershell
ssh -i C:\crt\ssh-key-2026-04-18_v4.key ubuntu@129.159.30.175
```

### Faydalı komutlar (Oracle VM)
```bash
# Container
docker logs kokpitim-web --tail=50
docker exec -it kokpitim-web bash

# PostgreSQL yedek (VM'de)
sudo -u postgres pg_dump -Fc kokpitim_db -f /opt/kokpitim/backups/manual_$(date +%Y%m%d).dump

# Satır sayısı
sudo -u postgres psql -d kokpitim_db -At -c "SELECT count(*) FROM tenants;"

# Güvenli deploy
cd /opt/kokpitim/app && sudo bash scripts/ops/oracle/oracle_safe_deploy.sh
```

Yerelden deploy paketi: `scripts/ops/oracle/oracle_deploy.ps1` — `docs/ORACLE_DEPLOY_ADIMLAR.md`

### GCP (eski ortam — arşiv)
- Instance `sps-server-v2` (Frankfurt) — **üretim değil**; geçiş öncesi yedekler `backups/oracle_migration/`
- Eski yol: `/home/kokpitim.com/public_html`, container `sps-web`
- Tarihsel `gcloud` komutları: `docs/gcp2oraclegecisplani.md` (Faz 0)

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

> **Güncel tam yordam (yerel → GitHub → VM):** `docs/YERELDEN_VM_YAYIN.md`  
> **VM → yerel senkron / dump:** `docs/VM_DEN_YERELE.md`  
> **VM terimi:** Oracle Cloud — `docs/ORACLE-PROD-VM.md`

### Her Deploy Öncesi
1. **DB yedeği al** — deploy öncesi mutlaka
2. **DB git'e dahil değil** — `.gitignore`'da, git push DB'yi taşımaz
3. **Şema değişikliği** — Alembic; canlı veri **PostgreSQL** (Oracle VM). Yerel SQLite sunucuya kopyalanmaz.
4. **Siteyi test et** — login, veriler, sayfalar kontrol edilmeli

### Standart Deploy Komutları

**Yerelde (Cursor terminali — sırayla):**
```bash
git add -A
git commit -m "açıklama"
git push origin main
```

**Oracle VM (tercih — tek komut):**
```bash
cd /opt/kokpitim/app && sudo bash scripts/ops/oracle/oracle_safe_deploy.sh
```

**Log kontrolü (VM):**
```bash
docker logs kokpitim-web 2>&1 | grep "No module\|OperationalError\|Listening" | head -5
```

### ⚠️ Kritik Uyarılar
- `git reset --hard` KULLANMA — sunucudaki manuel düzeltmeleri siler, `git pull` kullan
- DB deploy'a dahil değil — elle kopyalanmalı
- Container rebuild her seferinde tüm paketleri yeniden kurar — uzun sürer, normaldir
- `scikit-learn` ve `pywebpush` requirements.txt'te olmalı — eksikse site açılmaz