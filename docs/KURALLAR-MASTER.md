# KOKPİTİM — MASTER KURALLAR
> Tek gerçek kaynak. Tüm IDE'ler buraya referans verir.
> Kural değişince SADECE bu dosya güncellenir.
> Son güncelleme: 2026-04-03

---

## 1. ALTIN KURAL — Her görevde sıra bu

```
Oku → Plan göster → Onay al → Uygula → Test et → TASKLOG yaz → Dur
```

- **"Şunu deneyelim" deme** — kesin çözüm sun ya da "bilmiyorum, dosyayı göster" de
- **Deneme yanılma yasak** — kök nedeni bulmadan komut önerme
- **Bir dosyayı değiştirmeden önce tam oku**
- **Push kullanıcı istediğinde** — `github_sync.py` otomatik çalıştırılmaz

---

## 2. DİL KURALLARI

| Katman | Dil |
|--------|-----|
| Backend (routes, models, servisler) | İngilizce / snake_case |
| Frontend (kullanıcıya görünen her şey) | Türkçe (terminoloji sözlüğüne bağlı) |
| Bildirimler | SweetAlert2, Türkçe metin |
| Log mesajları | İngilizce |
| TASKLOG | Türkçe |

📖 **UI terminoloji sözlüğü:** [`docs/UI-TERMINOLOJI.md`](UI-TERMINOLOJI.md)
- "tenant" → **"Kurum"**, "user" → **"Kullanıcı"**, "sub_tenant" → **"Alt Kurum"** vb.
- Yeni UI metni yazarken bu sözlüğü kontrol et. Yeni terim önerin varsa sözlüğe ekle.

---

## 3. KOD KURALLARI

### Yasak olanlar
- `alert()` / `confirm()` — SweetAlert2 kullan
- Inline `<style>` veya `<script>` — harici dosyaya taşı
- Jinja2 `{{ }}` ifadeleri JS dosyalarında — `data-*` attribute kullan
- `except: pass` — `app.logger.error()` zorunlu
- Hard delete — `is_active=False` (soft delete) zorunlu
- Hardcoded URL JS'de — `data-*` attribute'tan oku

### Zorunlu olanlar
- `@login_required` — her korunan route'ta
- Blueprint — her modül için
- `extensions.py::db` — tek DB instance, başkası yasak
- `app.logger.error()` — her except bloğunda

---

## 4. MİMARİ HIZLI BAŞVURU

| Konu | Değer |
|------|-------|
| Port | **5001** (5000 yasak) |
| Ana blueprint | `micro_bp` → `/micro` prefix |
| DB instance | `extensions.py::db` |
| DB dosyası | `instance/kokpitim.db` |
| Login view | `auth.login` (kök — micro değil) |
| PG | Performans Göstergesi (PostgreSQL DEĞİL) |
| Bildirim | SweetAlert2 11 |
| CSS sistemi | `var(--text-*)`, `var(--color-*)` token'ları |

### Micro Modüller
```
micro/modules/
├── admin/           → kullanıcı, tenant, paket   (22 route)
├── surec/           → süreç, KPI takibi          (21 route)
├── api/             → REST API, Swagger           (15 route)
├── sp/              → Stratejik Planlama, SWOT   (12 route)
├── bireysel/        → bireysel performans         (11 route)
├── kurum/           → kurum yönetimi              (8 route)
├── analiz/          → analiz modülü               (7 route)
├── shared/auth/     → profil, login               (5 route)
├── shared/ayarlar/  → e-posta ayarları            (4 route)
├── shared/bildirim/ → bildirimler                 (4 route)
├── hgs/             → ⚠️ login bypass riski       (2 route)
├── masaustu/        → iskelet                     (1 route)
└── proje/           → iskelet                     (1 route)
```

### Model Katmanları
- **`app/models/`** → ~50 aktif model (Tenant, User, Process, Kpi…)
- **`models/`** → ~30 legacy model (LegacyUser, Surec, AnaStrateji…)

---

## 5. MODAL STANDARDI

Tüm modallar `components.css` yerel yapısını kullanır — SweetAlert2 modal olarak kullanılmaz:

```html
<div class="mc-modal-overlay" id="modal-ornek">
  <div class="mc-modal-lg">
    <div class="mc-modal-header">
      <h3>Başlık</h3>
      <button class="mc-modal-close">✕</button>
    </div>
    <div class="mc-modal-body">
      <!-- içerik -->
    </div>
    <div class="mc-modal-footer">
      <button class="mc-btn mc-btn-secondary">İptal</button>
      <button class="mc-btn mc-btn-primary">Kaydet</button>
    </div>
  </div>
</div>
```

SweetAlert2 yalnızca şunlar için kullanılır:
- Onay diyalogları (`swal.fire({ ... confirm ... }}`)
- Başarı/hata toast bildirimleri
- Basit bilgi mesajları

---

## 6. TASKLOG KAYIT FORMATI

Her görev sonunda `docs/TASKLOG.md` dosyasının **en üstüne** eklenir:

```markdown
## TASK-[numara] | [YYYY-MM-DD] | ✅ Tamamlandı

**Görev:** [Ne yapıldı — tek satır]
**Modül:** [modül adı]
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `dosya/yolu.py` → [ne değişti, tek satır]

### Yapılan İşlem
[2-3 cümle teknik açıklama]

### Notlar
[Varsa dikkat notu, yoksa "Yok."]
```

---

## 7. AKTİF GÜVENLİK BORCU

> Bunlara dokunmadan önce kullanıcıya danış.

| Kod | Sorun | Dosya | Not |
|-----|-------|-------|-----|
| S1 | Legacy route çift yüzey | `main/`, `app/routes/` | Yeni iş yalnızca `micro/` — `docs/LEGACY_ROUTE_INVENTORY.md` |
| S2 | HGS hızlı giriş | `micro/modules/hgs/` | Prod: `ProductionConfig` bypass kapalı |
| S3 | Rate limit storage | `config.py` | Prod’da `REDIS_URL` önerilir |
| ~~S4~~ | ~~FakeLimiter~~ | — | Kaldırıldı (2026-05) |
| ~~S5~~ | ~~CSP pasif~~ | — | Production’da aktif (2026-05) |

**Geri dönüş noktası:** `19mayisyedek` → `docs/19MAYISYEDEK_RESTORE.md`

---

## 8. ORTAMLAR VE DEPLOY PROTOKOLÜ

### 8.1 Dört ortam — terminoloji zorunlu

> Bu kelimeler bağlayıcıdır. "Üretim VM", "production VM", "live" gibi belirsiz terimler **kullanılmaz**. Hangi ortamdan bahsedildiği her zaman net olmalı. ("Canlı" = **Yayın** eş anlamlısıdır.)

| # | İsim | URL | Lokasyon | Amaç |
|---|---|---|---|---|
| 1 | **Yerel** | `http://127.0.0.1:5001` | Geliştirici makinesi (`C:\kokpitim`) | Geliştirme, deneme, hızlı iterasyon |
| 2 | **Test** | `https://test.kokpitim.com` | Oracle VM `/opt/kokpitim-test/` · port 5050 · DB `kokpitim_test_db` | Yayına çıkmadan önce staging doğrulaması |
| 3 | **Demo** | `https://demo.kokpitim.com` | Oracle VM `/opt/kokpitim-demo/` · port 5080 · DB `kokpitim_demo_db` | Ziyaretçilere Tomofil örnek tenant'ı üzerinde giriş-engelsiz deneyim |
| 4 | **Yayın** (Canlı) | `https://www.kokpitim.com` | Oracle VM `/opt/kokpitim/` · port 5000 · DB `kokpitim_db` | Müşterilere açık canlı sistem — **kullanıcı verisi kırmızı çizgi** |

**Yerelde çalışan değişikliği hiçbir zaman doğrudan yayına atma.** Akış: **Yerel → Test → Yayın** (Demo paralel hat: **Yerel → Demo**).

Test, Demo ve Yayın aynı fiziksel sunucudadır (`129.159.30.175`); izolasyon dizin/port/DB seviyesinde. **Demo'ya dokunan işlemler YALNIZCA `*-demo` hedeflerine erişir (`/opt/kokpitim-demo`, `kokpitim-demo-web`, `kokpitim_demo_db`); Test/Yayın hedefleri demo komutlarında ASLA geçmez.**

**Canlı (Yayın) kırmızı çizgi:** Yayında kod/DB her ne sebeple güncellenirse, **1. öncelik kullanıcı verisinin sağlıklı yedeği**.

### 8.2 SSH ve dizinler (yalnızca operatör)

```powershell
# Yerel Windows
ssh -i C:\crt\ssh-key-2026-04-18_v4.key ubuntu@129.159.30.175
```

| | **Test** | **Demo** | **Yayın** |
|--|----------|----------|-----------|
| Dizin | `/opt/kokpitim-test/app` | `/opt/kokpitim-demo/app` | `/opt/kokpitim/app` |
| `.env` | `/opt/kokpitim-test/.env` (+ `app/.env`) | `/opt/kokpitim-demo/.env` (+ `app/.env`) | `/opt/kokpitim/.env` |
| Container | `kokpitim-test-web` | `kokpitim-demo-web` | `kokpitim-web` |
| Port | 5050 | 5080 | 5000 |
| Nginx | `…/test.kokpitim.com.conf` | `…/demo.kokpitim.com.conf` | `…/www.kokpitim.com` |
| PG DB | `kokpitim_test_db` (`kokpitim_test_user`) | `kokpitim_demo_db` (`kokpitim_demo_user`) | `kokpitim_db` (`kokpitim_user`) |
| Backups | `/opt/kokpitim-test/backups` | `/opt/kokpitim-demo/backups` | `/opt/kokpitim/backups` |
| Özel flag | — | `KOKPITIM_DEMO_MODE=1` | — |

### 8.3 Deploy akışı

**Yerel → Test:**
1. `git push origin main`
2. Test VM'de kodu güncelle (rsync veya tarball; mevcut tooling: `scripts/ops/oracle/setup_test_env.sh` + manuel `docker restart kokpitim-test-web`)
3. `https://test.kokpitim.com/` smoke test

**Test → Yayın:**
1. Test'te doğrulama bitince yerelden: `git push origin main`
2. SSH yayın VM'i: `cd /opt/kokpitim/app && sudo bash scripts/ops/oracle/oracle_safe_deploy.sh` (PG yedek, pull, Docker rebuild, Alembic, satır sayısı doğrulaması)
3. `https://www.kokpitim.com/health` ile smoke test

**Push kullanıcı istediğinde yapılır.** Yayın deploy kullanıcı **"yayına çıkalım"** dediğinde yapılır — otomatik değil.

**Tam yordam:** `docs/YERELDEN_VM_YAYIN.md` · `docs/ORACLE-PROD-VM.md`

### 8.4 Demo ortamı — yapı + sıfırlama mutabakatı (2026-06-02)

> Kullanıcı ile mutabakat. Bağlayıcı. İlgili tasarım: `docs/DEMO-ORTAMI-PLAN.md`.

**Amaç:** Ziyaretçiler Tomofil örnek tenant'ı üzerinde giriş-engelsiz Kokpitim'i dener; ekler/siler/değiştirir, sonucu canlı görür. **Oturum bitince Tomofil verisi başlangıç haline (baseline) geri döner.**

**Seçilen mimari — Yol B (tek paylaşılan tenant + snapshot'tan geri yükleme):**
- Tek Tomofil tenant'ı (demo config `DEMO_TENANT_ID`, vars. 27). Per-session schema izolasyonu (S3) **YOK** — v2'ye ertelendi.
- **Baseline kaynağı:** yereldeki güncel Tomofil tenant'ının hali → demo DB'ye aktarılır + ayrı bir **baseline snapshot** olarak saklanır.
- **Sıfırlama tetikleri — HEPSİ:** (a) manuel çıkış `/demo/end`, (b) 60 dk süre dolumu, (c) inaktivite (heartbeat gelmez).
- **Sıfırlama mekaniği:** Tomofil tenant'ının verisini baseline snapshot'tan geri yükle (FK sırasında truncate + restore).

**Bilinçli kabul edilen sınır:** Eşzamanlı ziyaretçiler aynı Tomofil'i paylaşır; biri sıfırlama tetiklerse diğerinin oturumu da sıfırlanır. Düşük trafik için **kabul edildi** (engel değil). Trafik artarsa Yol A (S3 per-session clone).

**Demo kırmızı çizgileri:**
- Demo işlemleri **yalnızca `*-demo` hedeflerine** dokunur. Test/Yayın hedefleri demo komutlarında **ASLA** geçmez.
- Saf kod deploy'u DB'ye dokunmaz. Tomofil baseline / demo DB'yi etkileyecek işlemler (seed / wipe / Alembic migration) **yalnızca kullanıcı açıkça isteyince**.

**Demo deploy akışı (Yerel → Demo):** kullanıcı **"demo'ya gönderelim"** dediğinde — kod tarball/git → `/opt/kokpitim-demo/app/` → `docker restart kokpitim-demo-web`. SSH yalnızca operatör; otomatik değil.

### 8.5 GCP (eski — arşiv)
| | |
|-|-|
| Instance | `sps-server-v2` / `europe-west3-c` (STOP) |
| Geçiş yedekleri | `backups/oracle_migration/`, `docs/gcp2oraclegecisplani.md` |
