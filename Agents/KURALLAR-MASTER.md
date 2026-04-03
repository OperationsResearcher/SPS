# KOKPİTİM — MASTER KURALLAR
> Tek gerçek kaynak. Tüm IDE'ler buraya referans verir.
> Kural değişince SADECE bu dosya güncellenir.
> Son güncelleme: 2026-04-02

---

## 1. ALTIN KURAL — Her görevde sıra bu

```
Oku → Plan göster → Onay al → Uygula → Test et → TASKLOG yaz → Dur
```

- **"Şunu deneyelim" deme** — kesin çözüm sun ya da "bilmiyorum, dosyayı göster" de
- **Deneme yanılma yasak** — kök nedeni bulmadan komut önerme
- **Bir dosyayı değiştirmeden önce tam oku**
- **Push kullanıcı istediğinde** — `github_sync.py` otomatik çalıştırılmaz

### TASKLOG — Otomatik, her görev sonunda
TASKLOG güncellemesi görevin ayrılmaz parçasıdır — kullanıcı söylemese de yapılır:
```
1. docs/TASKLOG.md dosyasını aç
2. En üstteki TASK-[X] numarasını oku
3. TASK-[X+1] ile yeni kaydı en üste ekle
4. Kullanıcıya: "TASK-[X+1] TASKLOG'a eklendi" de
```

---

## 2. DİL KURALLARI

| Katman | Dil |
|--------|-----|
| Backend (routes, models, servisler) | İngilizce / snake_case |
| Frontend (kullanıcıya görünen her şey) | Türkçe |
| Bildirimler | SweetAlert2, Türkçe metin |
| Log mesajları | İngilizce |
| TASKLOG | Türkçe |

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
| Aktif app factory | `app/__init__.py` → `create_app()` |
| Aktif blueprint | `app_bp` |
| Legacy factory | `__init__.py` (kök) — dokunma |
| DB instance | `extensions.py::db` |
| DB dosyası | `instance/kokpitim.db` |
| Login view | `auth.login` |
| PG | Performans Göstergesi (PostgreSQL DEĞİL) |
| Bildirim | SweetAlert2 11 |
| CSS sistemi | `var(--text-*)`, `var(--color-*)` token'ları |

### ⚠️ Klasör Yapısı — Kritik

```
AKTİF (yaz buraya):
ui/templates/platform/   → HTML sayfaları
ui/static/platform/js/   → JavaScript
ui/static/platform/css/  → CSS

MODÜLLER (iş mantığı):
micro/modules/           → route'lar, servisler
app/models/              → veritabanı modelleri
micro/services/          → servis katmanı

LEGACY (dokunma):
templates/               → kök legacy templates
static/                  → kök legacy static
micro/templates/         → eski micro templates
micro/static/            → eski micro static
```

### Modüller (micro/modules/)
```
admin/      → kullanıcı, tenant, paket yönetimi
surec/      → süreç yönetimi, KPI takibi
api/        → REST API, Swagger
sp/         → Stratejik Planlama, SWOT
bireysel/   → bireysel performans
kurum/      → kurum yönetimi
analiz/     → analiz modülü
shared/     → auth, ayarlar, bildirim
hgs/        → ⚠️ login bypass riski
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

| Kod | Sorun | Dosya |
|-----|-------|-------|
| S1 | Rate Limiter devre dışı (FakeLimiter) | `extensions.py` |
| S2 | Hardcoded SECRET_KEY fallback | `config.py` |
| S3 | SESSION_COOKIE_SECURE eksik | `config.py` |
| S4 | Talisman init_app yok → CSP pasif | `__init__.py` |
| S5 | HGS login bypass riski | `micro/modules/hgs/` |

---

## 8. DEPLOY PROTOKOLÜ

### Yerelden GCP'ye
```bash
# 1. YERELDE
git add -A
git commit -m "TASK-[X]: açıklama"
git push origin main
# github_sync.py — sadece kullanıcı isterse

# 2. VM'DE (SSH)
cd /home/kokpitim.com/public_html && \
sudo git pull origin main && \
sudo docker build -t sps_web_final:latest . && \
sudo docker stop sps-web && sudo docker rm sps-web && \
sudo docker run -d --name sps-web -p 80:5000 \
  -v /home/kokpitim.com/public_html/instance:/app/instance \
  sps_web_final:latest

# 3. KONTROL
sudo docker logs sps-web 2>&1 | \
  grep "No module\|OperationalError\|Listening" | head -5
```

### GCP Bilgileri
| | |
|-|-|
| VM | `sps-server-v2` / zone: `europe-west3-c` |
| IP | `34.89.231.89` |
| Container | `sps-web` |
| DB | `/app/instance/kokpitim.db` |
