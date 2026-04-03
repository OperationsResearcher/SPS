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

| Kod | Sorun | Dosya |
|-----|-------|-------|
| S1 | Rate Limiter devre dışı (FakeLimiter) | `extensions.py` |
| S2 | Hardcoded SECRET_KEY fallback | `config.py` |
| S3 | SESSION_COOKIE_SECURE eksik | `config.py` |
| S4 | Talisman init_app yok → CSP pasif | `__init__.py` |
| S5 | HGS login bypass riski | `micro/modules/hgs/` |

---

## 8. DEPLOY PROTOKOLÜ

**Tam yordam:** `docs/YERELDEN_VM_YAYIN.md`

Özet: yerelde `git push origin main` → VM’de `sudo bash scripts/vm_safe_deploy.sh` (PostgreSQL yedek, pull, Docker, Alembic, satır sayısı doğrulaması).

### GCP Bilgileri
| | |
|-|-|
| VM | `sps-server-v2` / zone: `europe-west3-c` |
| IP | `34.89.231.89` |
| Container | `sps-web` |
| Canlı DB | PostgreSQL (`kokpitim_db`); SQLite tipik olarak yalnızca yerel geliştirme |
