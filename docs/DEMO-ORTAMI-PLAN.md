# Kokpitim Demo Ortamı — Tasarım Planı (S3 Yaklaşımı)

> **Durum:** Planlama. Kodlanmayacak — kullanıcı tetikleyince başlatılır.
> **Versiyon:** v0.1 — 2026-05-27
> **Karar:** S3 (per-session PostgreSQL schema clone) + ayrı demo DB
> **İlgili karar bağlamı:** ortam terminolojisi 4'e çıkar — Yerel / Test / **Demo** / Yayın

---

## 1. Hedef ve sınırlar

**Hedef:** Web sitesi ziyaretçileri **giriş engelsiz**, **kayıt zorunluluğu olmadan** Kokpitim'i Tomofil verisi üzerinde tam fonksiyonel olarak deneyebilsin.

**Bağlayıcı gereksinimler:**
- Tomofil 7 yıllık verisi (99k satır) tüm deneyim boyunca **gerçekçi** olarak çalışsın
- Kullanıcı PG verisi girer → K-Vektör puanı **anında değişir**, yıllar arası karşılaştırma çalışır, raporlar üretilebilir
- **İzolasyon:** eşzamanlı kullanıcılar birbirini etkilemez
- **Temizlik:** session bittiğinde verisi **iz bırakmadan** silinir
- **Prod güvenliği:** demo'da yapılan hiçbir şey yayın verisine **fiziksel olarak** dokunamaz
- Audit/log/email gönderim kirliliği **mümkün değil** (DB ayrı)

**Sınırlar (ilk versiyon yapılmaz):**
- Demo'da yaratılan veriyi "gerçek hesap"a kaydetme (conversion özelliği) — v2
- AI/LLM özelliklerinde gerçek API çağrısı (maliyet abuse riski) — mock cevap döner
- E-posta gönderimi (SMTP) — kapatılır, log'a yazılır

---

## 2. Mimari yapı

### 2.1 Üst düzey

```
Yerel (127.0.0.1:5001)         → kokpitim_db (PG, dev makine)
Test (test.kokpitim.com)       → kokpitim_test_db (Oracle VM /opt/kokpitim-test)
Demo (demo.kokpitim.com)       → kokpitim_demo_db (Oracle VM /opt/kokpitim-demo)  ← yeni
Yayın (www.kokpitim.com)       → kokpitim_db (Oracle VM /opt/kokpitim)
```

Demo container, test container'ın klonu. Konfigürasyon farkı:
- `PORT=5070`
- `SQLALCHEMY_DATABASE_URI=postgresql://kokpitim_demo_user:.../kokpitim_demo_db`
- `KOKPITIM_DEMO_MODE=1` (kod tarafında demo davranışları için flag)
- `SMTP` boş → mail giderken silent log
- `LLM` mock provider

### 2.2 Demo DB içi yapı (S3)

```
kokpitim_demo_db
├── public (SQLAlchemy default schema'sı — kullanılmaz/küçük)
│
├── master (gold snapshot — read-only)
│   ├── tenants (sadece Tomofil + 5-10 demo user)
│   ├── strategies, processes, process_kpis, kpi_data, …
│   └── plan_years (2020-2026)
│
├── demo_pool_001 (pre-warm)  ─┐
├── demo_pool_002 (pre-warm)   │  N adet hazır clone bekler
├── demo_pool_003 (pre-warm)   │  Her biri master'ın taze kopyası
├── …                          │
├── demo_pool_010 (pre-warm)  ─┘
│
├── demo_session_a3f8b… (aktif kullanıcı 1, pool'dan alındı + rename)
├── demo_session_91c2e… (aktif kullanıcı 2)
└── …
```

**Akış:**
1. Kullanıcı demo başlatır → boş `demo_pool_*` bulunur, `demo_session_<token>` olarak rename
2. Background worker yeni bir `demo_pool_*` üretir (havuz seviyesini koru)
3. Session bittiğinde `DROP SCHEMA demo_session_<token> CASCADE`
4. Background worker eksik kalan havuzu doldurur

### 2.3 Master snapshot stratejisi

**Master nasıl beslenir:**
- Manuel: `scripts/demo_seed_master.sh` → mevcut Tomofil tarball'ından temizlenmiş hali → `master` şemasına yükler
- Otomatik prod→demo senkronizasyon **YASAK** (canlı müşteri verisi sızma riski)
- Demo veri ailesi büyürse: master içine "Demo Co" eklenebilir (alternatif sektör örneği)

**Master demo kullanıcıları (Tomofil tenant'ı içinde):**

| Email | Rol | Kullanım |
|---|---|---|
| `kurum_yoneticisi@demo.kokpitim` | tenant_admin | Tam kontrol, ayarlar, dönem yönetimi |
| `ust_yonetim@demo.kokpitim` | executive_manager | Exec dashboard, raporlar |
| `surec_lideri@demo.kokpitim` | yonetici | Bir veya iki sürecin lideri |
| `surec_uyesi@demo.kokpitim` | calisan | Süreç üyesi, PG verisi girer |
| `izleyici@demo.kokpitim` | izleyici | Sadece görüntüleme |

Parola: yok / sahte; demo login bypass mekanizmasıyla giriş.

---

## 3. PostgreSQL schema clone mekaniği

### 3.1 Schema seviyesinde clone — yöntem

PostgreSQL native "CREATE SCHEMA AS TEMPLATE" desteklemez (DB seviyesinde var ama schema seviyesinde yok). Üç seçenek:

| Yöntem | Hız | Karmaşıklık | Ekibe uygunluk |
|---|---|---|---|
| **`pg_dump --schema=master \| sed \| psql`** | Yavaş (~10-30 sn) | Düşük | İlk versiyonda yapma, pool ile gizle |
| **DDL üret + `INSERT SELECT`** | Orta (~3-8 sn) | Orta | Önerilen |
| **`CREATE TABLE ... LIKE INCLUDING ALL` + bulk insert** | Hızlı (~2-5 sn) | Yüksek (FK sırası) | Pre-warm pool ile en iyi |

**Önerilen — DDL üret + bulk insert:**

```python
def clone_schema_from_master(target_schema: str):
    """master şemasını target_schema'ya tablo+veri olarak kopyala."""
    cur.execute(f"CREATE SCHEMA {target_schema}")
    # 1. Tüm tabloları yapısıyla yarat (FK'siz)
    for t in MASTER_TABLES_DEP_ORDER:
        cur.execute(f"""
            CREATE TABLE {target_schema}.{t} (LIKE master.{t}
                INCLUDING DEFAULTS INCLUDING IDENTITY INCLUDING CONSTRAINTS
                INCLUDING INDEXES)
        """)
    # 2. Verileri kopyala (FK bağımlılık sırasında)
    for t in MASTER_TABLES_DEP_ORDER:
        cur.execute(f"INSERT INTO {target_schema}.{t} SELECT * FROM master.{t}")
    # 3. FK'leri ekle (artık verilerde tutarlı)
    for fk in MASTER_FK_LIST:
        cur.execute(f"ALTER TABLE {target_schema}.{fk.table} ADD CONSTRAINT ...")
    # 4. Sequence'ları senkronize et
    for seq in MASTER_SEQUENCES:
        cur.execute(f"SELECT setval('{target_schema}.{seq}', ...)")
```

**Karmaşıklığı havuz gizler:** kullanıcı geldiğinde clone hazır, anında atama.

### 3.2 Pre-warm pool detay

```
Background worker (apscheduler veya basit cron):
  - Her 30 saniyede: SELECT COUNT FROM demo_pool_schemas WHERE state='ready'
  - Eğer < 5 ise: clone_schema_from_master('demo_pool_<random>') → state='ready'
  - Eğer > 10 ise: bekle (ya da en eskiyi temizle)

Tablo: public.demo_pool_schemas
  id, schema_name, state ('ready' | 'in_use' | 'cleanup'),
  created_at, assigned_at, assigned_session, cleanup_at
```

İlk versiyon için **havuz boyutu = 5** yeter. Trafik artarsa 20'ye çıkar.

### 3.3 Connection routing — kullanıcının doğru schema'yı görmesi

Flask-SQLAlchemy + connection pool ile **search_path**'i istemci başına ayarlamak kritik. PostgreSQL session'ı = connection bazlı, ve pool'dan çekilen bir bağlantının önceki search_path'i kalıntı kalmış olabilir.

**Yaklaşım:** SQLAlchemy event listener + Flask request bağlamı.

```python
from sqlalchemy import event
from flask import g, session as flask_session

@app.before_request
def stamp_demo_schema():
    """Demo modu açıksa session'dan schema_name'i g'ye al."""
    if not app.config.get('KOKPITIM_DEMO_MODE'):
        return
    g.demo_schema = flask_session.get('demo_schema_name')

@event.listens_for(db.engine, "checkout")
def set_search_path_on_checkout(dbapi_conn, conn_record, conn_proxy):
    """Connection pool'dan her çekilişte search_path'i ayarla."""
    if not app.config.get('KOKPITIM_DEMO_MODE'):
        return
    schema = getattr(g, 'demo_schema', None) or 'public'
    with dbapi_conn.cursor() as cur:
        cur.execute(f"SET search_path TO {schema}, public")
```

**Riskler:**
- `g` Flask request bağlamında, engine event ise daha düşük seviyede — bağlam kaybolabilir
- Background worker'lar (Celery, APScheduler) request bağlamı yoktan çalışır
- Çözüm: demo modda background işler **public** schema'da çalışır (Tomofil verisi dokunmaz, sadece pool yönetimi)

**Alternatif — daha güvenli:** her DB sorgusu öncesi açık `SET search_path` (transaction-scoped `SET LOCAL`). Performans cezası küçük ama izolasyon kesin.

```python
@app.before_request
def set_search_path():
    if 'demo_schema_name' in flask_session:
        db.session.execute(text(f"SET LOCAL search_path TO {schema}, public"))
```

İlk versiyonda **bu yol daha güvenli**.

---

## 4. Session lifecycle

### 4.1 Başlangıç

```
www.kokpitim.com → "Demo'yu Dene" → demo.kokpitim.com/baslat

Sayfa:
  ┌─────────────────────────────────────────────────────────┐
  │  Kokpitim'i Tomofil verisi üzerinde deneyin             │
  │                                                          │
  │  Hangi rolle başlamak istersiniz?                       │
  │                                                          │
  │  [Kurum Yöneticisi]   [Üst Yönetim]   [Süreç Lideri]   │
  │  [Süreç Üyesi]        [İzleyici]                       │
  │                                                          │
  │  ⓘ Verileriniz session sonunda silinecek (60 dk limit) │
  └─────────────────────────────────────────────────────────┘

Kullanıcı bir rol seçer → POST /demo/start
  Backend:
    1. demo_pool'dan bir 'ready' schema seç, kilitle (FOR UPDATE SKIP LOCKED)
    2. Schema'yı 'demo_session_<token>' olarak rename
    3. Token'ı Flask session'ına yaz: session['demo_schema_name'] = ...
                                     session['demo_role'] = 'tenant_admin'
                                     session['demo_started_at'] = now()
                                     session['demo_expires_at'] = now + 60dk
    4. İlgili role bağlı kullanıcıyla auto-login (flask_login)
    5. Yeni pool clone başlat (background)
  → redirect /launcher
```

### 4.2 Kullanım

Normal app çalışır. Tek farklar:
- Üst banner: `🧪 DEMO MODU — kalan süre: 42dk · [Çıkış ve Sıfırla]`
- Bazı menüler kapalı: "Kullanıcı yönetimi" (demo'da gerçek user oluşturma yok), "E-posta ayarları"
- E-posta gönderim noktalarında: log'a yaz, kullanıcıya "demo'da gerçek mail gitmez" toast'ı
- AI çağrılarında: mock cevap döner

### 4.3 Bitiş tetikleri

| Tetik | Mekanik |
|---|---|
| Manuel "Çıkış" butonu | POST /demo/end → schema cleanup queue'ya |
| Tarayıcı sekme kapanır | `navigator.sendBeacon('/demo/end-beacon')` (best-effort) |
| 60dk hard cap | Kullanıcı geldiğinde session_expired sayfası → cleanup tetik |
| 30dk inaktivite | Heartbeat ping geç gelmez → cleanup |
| Acil cleanup (ops) | `python -m scripts.demo_cleanup --schema=demo_session_xxx` |

### 4.4 Cleanup

```
def cleanup_demo_session(schema_name):
    # 1. Flask session'ı drop et (eğer hala aktifse)
    # 2. demo_pool_schemas tablosunda state='cleanup' yap
    # 3. DROP SCHEMA <schema_name> CASCADE
    # 4. Eğer havuz boşaldıysa yeni clone başlat
```

**Sigortalar:**
- Cron her saat: `assigned_at < now - 90min AND state='in_use'` olanları zorla cleanup
- Cron her gece: orphan schema'ları ara (`pg_namespace`'te var ama `demo_pool_schemas`'ta yok) → sil
- Maintenance script: `python scripts/demo_wipe_all.py --confirm` → tüm session'ları temizle

---

## 5. Authentication & güvenlik

### 5.1 Demo login bypass

```python
@app.route('/demo/start', methods=['POST'])
def demo_start():
    if not app.config.get('KOKPITIM_DEMO_MODE'):
        abort(404)
    role = request.form.get('role')
    if role not in DEMO_ROLES:
        abort(400)
    schema = assign_demo_schema()  # pool'dan al
    user = demo_user_for_role(role, schema)  # master'daki role karşılığı user
    flask_session['demo_schema_name'] = schema
    flask_session['demo_role'] = role
    flask_session['demo_started_at'] = datetime.utcnow().isoformat()
    login_user(user)  # flask_login
    return redirect('/launcher')
```

**KOKPITIM_DEMO_MODE flag prod'da kapalı** — yayın sunucusunda hiçbir demo endpoint çalışmaz.

### 5.2 Kötüye kullanım önlemleri

| Risk | Önlem |
|---|---|
| Spam demo session açma (DOS) | IP başına 5dk içinde max 3 session |
| AI maliyeti abuse | LLM çağrıları mock cevap (gerçek API key demo container'da yok) |
| E-posta abuse | SMTP kapalı, gönderim log'a yazılır |
| Yetkisiz endpoint deneme | Admin yetki yine `@role_required` kontrol eder; demo user'lar düşük yetkili |
| SQL injection schema_name üzerinden | Schema adları **whitelist regex** ile validate edilir (`^demo_[a-z0-9_]+$`) |
| Demo'dan prod DB'ye erişim | Container farklı, DB credentials farklı, network izolasyon olabilir |

---

## 6. UI/UX elementleri

### 6.1 Demo banner (her sayfada)

```
┌────────────────────────────────────────────────────────────────────┐
│  🧪 DEMO MODU — Tomofil verisi üzerinde inceleme                   │
│  Kalan süre: 42dk · Rol: Kurum Yöneticisi                          │
│  [Çıkış ve Sıfırla]  [Beğendiyseniz hesap açın →]                  │
└────────────────────────────────────────────────────────────────────┘
```

- Sabit, üstte; mor/turuncu (prod'la görsel ayrım)
- Banner kapatılamaz
- Kalan süre frontend'de countdown (her dakika güncellenir)

### 6.2 Devre dışı menüler

- **Kullanıcı Yönetimi** — "Demo'da yeni kullanıcı eklenemez"
- **E-posta Ayarları** — gri, "Demo'da SMTP yapılandırması yok"
- **Sub-Tenant** — demo Tomofil tek tenant
- **Push notifications** — kapalı

### 6.3 Demo-spesifik mesajlar

| Aksiyon | Sonuç |
|---|---|
| "Kaydet" → veri girişi | Normal, başarı toast'ı |
| "Bildirim gönder" → SMTP | "Demo'da gerçek e-posta gitmez. İçerik: …" |
| AI Pivot tıklama | Mock cevap, "Bu örnek bir öneridir, demo modda" notu |

### 6.4 Çıkış akışı (conversion noktası)

```
Kullanıcı "Çıkış" tıklar → modal:

  ┌──────────────────────────────────────────────────────┐
  │  Demo'yu sonlandırmak istediğinize emin misiniz?     │
  │  Verileriniz silinecek.                              │
  │                                                       │
  │  Beğendiyseniz Kokpitim'e geçin:                     │
  │  [Hesap aç ve verilerimi taşı]                       │
  │                                                       │
  │  [Çıkış (verilerim silinecek)]   [Vazgeç]            │
  └──────────────────────────────────────────────────────┘
```

İlk versiyonda "hesap aç ve taşı" sadece marketing link (signup formuna yönlendir). v2'de cross-schema veri taşıma yapılır.

---

## 7. Deployment & operasyon

### 7.1 Yeni ortam kurulumu (TASK-N planı)

`setup_test_env.sh` şablonundan kopya: `scripts/ops/oracle/setup_demo_env.sh`

```bash
TEST_DIR="/opt/kokpitim-demo"
DB_NAME="kokpitim_demo_db"
DB_USER="kokpitim_demo_user"
APP_PORT="5070"
DOMAIN="demo.kokpitim.com"
CONTAINER_NAME="kokpitim-demo-web"
```

Adımlar (tahmin: 1 günlük iş):
1. Postgres user + DB yarat
2. `/opt/kokpitim-demo/` dizini hazırla, `.env` yaz
3. master schema seed (Tomofil tarball'ından)
4. Docker container ayağa kalk (`KOKPITIM_DEMO_MODE=1`)
5. Nginx + Let's Encrypt `demo.kokpitim.com` için
6. DNS A record (eğer subdomain henüz yoksa)

### 7.2 Migration disiplini

Mevcut: yerel → test → yayın
Yeni: yerel → test → **demo** (paralel) → yayın

Demo migration komutu kendi Alembic'i kullanır (aynı `migrations/versions/`); master schema bir kez upgrade edilir, **session schema'lar kullanıcı geldiğinde clone'lanır**.

Migration sonrası: havuzdaki tüm pre-warm schema'lar **invalidate** → silinip yeniden clone (yapısı değişti).

### 7.3 İzleme

- Health check: `/demo/health` → pool durumu, aktif session sayısı, schema sayısı
- Prometheus metrik (opsiyonel): `demo_sessions_active`, `demo_pool_ready`, `demo_cleanup_lag`
- Alarm: pool < 1 olursa Slack/log uyarısı (kullanıcı kuyrukta beklemesin)

---

## 8. Görev kırılımı (uygulama zamanı için tahmin)

| # | İş | Tahmin | Bağımlılık |
|---|---|---|---|
| 1 | KURALLAR-MASTER §8'i 4-ortama güncelle | 30dk | — |
| 2 | `scripts/ops/oracle/setup_demo_env.sh` (test şablonundan) | 2-3 saat | — |
| 3 | DNS + Nginx + SSL `demo.kokpitim.com` | 1 saat | (2) |
| 4 | `master` schema seed scripti — Tomofil sade kopyası | 2-3 saat | (2) |
| 5 | `demo_pool_schemas` tablosu + model + migration | 1 saat | (2) |
| 6 | Schema clone servisi (`clone_schema_from_master`) | 4-6 saat | (5) |
| 7 | Background worker (havuz seviyesi koruma) | 2 saat | (6) |
| 8 | `before_request` search_path middleware | 1-2 saat | (6) |
| 9 | `/demo/start` rol seçici sayfası + endpoint | 3-4 saat | (8) |
| 10 | Demo session manager (assign, expire, end) | 3 saat | (9) |
| 11 | Demo banner template (`base.html`'e koşullu blok) | 2 saat | (10) |
| 12 | Devre dışı menüler + e-posta SMTP guard + LLM mock | 2 saat | (10) |
| 13 | Beacon + heartbeat + cleanup cron | 2 saat | (10) |
| 14 | UI: çıkış modali + conversion linki | 1 saat | (11) |
| 15 | Smoke test + dokümantasyon | 2 saat | — |
| **Toplam** | | **~30-40 saat** = **4-5 günlük iş** | |

İlk versiyon için 1 hafta makul, +1 hafta lansman cilası.

---

## 9. Açık sorular (uygulamaya başlarken karara bağlanacak)

1. **Master schema güncellemesi nasıl olacak?** — manuel script, otomatik trigger yok. Tomofil verisi statik kalır mı, mevsimsel güncellenir mi?
2. **Demo URL'leri paylaşılabilir mi?** — `demo.kokpitim.com/sp/donemler` linki — session yoksa "Demo başlat" sayfasına yönlendirilir (onboarding bozulmaz).
3. **Demo süresi 60dk doğru mu?** — A/B testi için 30 / 60 / 90 dk denenebilir; ilk versiyon 60.
4. **Pre-warm havuz boyutu = 5 yeterli mi?** — trafiğe göre ayarlanır, ilk versiyon 5.
5. **AI mock cevapları nereden?** — Tomofil için önceden çekilmiş 5-10 örnek cevap, rotasyonla servisten. Maliyet sıfır.
6. **Beacon API güvenilir mi?** — değil; sigortalı timeout cron'u gerekir.
7. **"Hesap aç ve verilerimi taşı" v1'de neye yönlendirir?** — sadece signup formuna; cross-schema veri taşıma v2.
8. **Demo subdomain SEO'da görünür mü?** — `noindex` header. Marketing'in ayrı landing page'i SEO için kullanılır.

---

## 10. Riskler & olası tuzaklar

| Risk | Etki | Hafifletme |
|---|---|---|
| `SET search_path` connection pool'da sızıntı | Kullanıcılar birbirinin verisini görür (kritik) | `SET LOCAL` ve transaction scope, ayrıca audit smoke test |
| Schema clone yavaşlığı (havuz tükenir) | Kullanıcı 30sn bekler | Pool boyutu artır, on-demand fallback ile sırada bekletme |
| Migration sonrası eski havuz invalidate olmazsa | Demo crash | Deploy hook: tüm `demo_pool_*` ve `demo_session_*` schema'larını DROP, havuzu yeniden inşa |
| Cleanup başarısız olursa | DB şişer | Cron sigortası + manuel `demo_wipe_all.py` |
| Demo container down → marketing kaybı | Yeni müşteri bulamaz | Health check + alarm |
| KOKPITIM_DEMO_MODE flag prod'da yanlışlıkla açık | Prod'da `/demo/start` çalışır (KRİTİK) | Config check + smoke test deploy sonrası |
| Background scheduler request context'siz çalışır | Pool yönetimi kırılır | Worker'lar `public.demo_pool_schemas` tablosuna dokunur; demo schema'lara değil |

---

## 11. Gelecek versiyon (v2+) — bu plana DAHIL DEĞİL

- **Cross-schema "demo → gerçek hesap" veri taşıma** — kullanıcı verilerini saklamak isterse
- **Çoklu demo dataset** — Tomofil dışında "Demo Co", "Sample Hospital" vb. alternatif örnekler
- **Demo analitiği** — hangi rol seçiliyor, kaç dakika geziliyor, en çok hangi sayfaya bakılıyor
- **Yönlendirmeli turlar** — Kule yardımcı sistemi demo için özel turlar
- **Kayıt videosu** — kullanıcı session'ını anonim olarak izle (UX araştırması, GDPR dikkat)

---

## 12. Başlamadan önce kullanıcıya soru

Uygulamaya geçerken bu sayfaya dönülecek ve şu kararlar netlenecek:

- [ ] Master schema güncel kalsın mı, statik mi? (öneri: statik)
- [ ] Demo URL: `demo.kokpitim.com` mu, `kokpitim.com/demo` mu? (öneri: subdomain)
- [ ] Pool boyutu 5 mi, 10 mu? (öneri: 5 → izle → 10)
- [ ] Demo süresi 60dk mı? (öneri: 60dk)
- [ ] AI çağrıları mock mi, ucuz model mi? (öneri: tamamen mock)
- [ ] Conversion: "hesap aç ve taşı" v1'de basit signup link mi? (öneri: evet)
- [ ] Lansman önce internal beta mi (10 kişi), direkt public mi? (öneri: 1 hafta internal)

Bu kararlar netleştikten sonra TASK-X olarak başlanır.

---

## Ek: ilgili mevcut altyapı

- `scripts/tomofil_sp_import.py` — master schema seed için referans
- `scripts/tomofil_hard_wipe.py` — cleanup mantığı için referans
- `scripts/ops/oracle/setup_test_env.sh` — demo ortam kurulumu şablonu
- `docs/TENANT-VERI-ENVANTERI.md` — clone edilecek tablolar listesi
- `app/services/date_sovereign.py` — demo'da PG verisi girişi (zaten doğru çalışıyor)
- `app/services/plan_year_diff_service.py` — yıl-diff demo'da değerli özellik

