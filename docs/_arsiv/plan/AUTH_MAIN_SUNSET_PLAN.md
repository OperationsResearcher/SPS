# 🪦 Auth + main/routes Sunset Planı (Sprint 39-42)

> **Hedef:** ~880 satır legacy kod silinmesi
> **Risk seviyesi:** Auth = YÜKSEK (login flow), main = ORTA (gerçek kullanım az)

---

## Sprint 39-40 — Auth Sunset (~552 satır)

### Mevcut yapı

| Dosya | Satır | İçerik |
|---|:-:|---|
| `app/routes/auth.py` | 302 | `/login`, `/logout`, `/profile`, `/settings` (`auth_bp`) |
| `auth/routes.py` (root) | 250 | Legacy quick-login + kurum bazlı login (`auth_legacy`) |
| `micro/modules/shared/auth/` | ? | Yeni modüler auth (kontrol gerekli) |

### Sorun
- `app/routes/auth.py` modern, **aktif kullanımda**
- `auth/routes.py` legacy, "kurum kısa adıyla" hızlı giriş — quick_login bypass (Sprint 22'de PROD'da disable edildi)

### Adımlar

1. **micro/shared/auth/ ile auth.py paritesi:**
   ```bash
   grep -n "@auth_bp.route" app/routes/auth.py
   ```
   Eşdeğer route'ları micro'da bul. Eksik varsa taşı.

2. **`auth/routes.py` (root, legacy):** PROD'da quick-login disabled → silinmesi güvenli.
   - Önce import'ları kontrol et:
     ```bash
     grep -rn "from auth.routes import\|import auth.routes" --include="*.py"
     ```
   - Sıfır referans → sil.

3. **`app/routes/auth.py`:** TÜM kullanımları micro/shared/auth'a taşı, sonra sil.
   - **Sprint 40'a ertelenmeli** — login flow değişikliği high-risk.

### Beklenen kazanım
- ~552 satır legacy temizlik
- Tek doğru kaynak: `micro/shared/auth/`

---

## Sprint 41-42 — main/routes Sunset (~328 satır)

### Mevcut yapı

| Dosya | Satır | İşlev |
|---|:-:|---|
| `main/routes/__init__.py` | ~50 | Blueprint init |
| `main/routes/api.py` | ~80 | Legacy API (varsa) |
| `main/routes/dashboard.py` | ~50 | Eski masaustu route'ları |
| `main/routes/projeler.py` | ~80 | Eski proje route'ları |
| `main/routes/strateji.py` | ~70 | Eski strateji route'ları |
| `main/routes/_common.py` | ~50 | Ortak helper'lar |

### Kullanım analizi
- `main_bp` `app/__init__.py:227`'de register ediliyor
- `legacy_sunset` middleware'in çoğu yönlendirme '/projeler', '/strateji-api' gibi LEGACY pattern'leri yakalıyor → 301 redirect veya 410
- Yani **çoğu endpoint zaten unreachable**

### Adımlar (Sprint 41)

1. Her route için `legacy_sunset` rule'unu kontrol et:
   ```python
   # app/middleware/legacy_sunset.py
   GONE_PREFIXES, EXACT_ENDPOINT, PREFIX_REWRITE
   ```
2. Hangi route hâlâ ulaşılabilir? (legacy_sunset by-pass eden)
3. Bu route'ları micro modüllere taşı veya 410'a düşür.

### Sprint 42 — Final temizlik

- `main_bp` blueprint'ini app/__init__.py'dan kaldır
- `main/routes/` klasörünü sil
- `tests/test_legacy_sunset.py`'ı genişlet (silinen endpoint'lerin 410 döndüğünü doğrula)

### Beklenen kazanım
- ~328 satır legacy temizlik
- `main/routes/` klasörü tamamen kalkar

---

## Toplam Kazanım Beklentisi

```
Sprint 36 (strategy.py): erteleniyor — template'ler bağlı, 195 satır risk
Sprint 37 (process.py audit): rapor yayınlandı, sunset Sprint 38-39
Sprint 38-39 (auth):         552 satır (auth.py + auth/routes.py)
Sprint 41-42 (main/routes):  328 satır

TOPLAM hedef: ~1.075 satır + 1.805 (process.py) = ~2.880 satır
Sprint 1-35 sonrası kalan legacy: ~3.940 satır
Sprint 35 → 42 sonu: ~1.060 satır legacy kalır
                   = ~73% azalma (4.762 başlangıcından)
```

---

## SPRINT 36-42 SON DURUM (bu seansta)

| Sprint | Hedef | Sonuç |
|:-:|---|---|
| 36 | strategy.py sunset | Templates safe_url_for'a geçti; gerçek silme Sprint 41'e |
| 37 | process.py parity audit | ✅ `docs/PROCESS_BP_SUNSET_AUDIT.md` yayınlandı |
| 38 | i18n TR çevirileri | ✅ 33 mesaj, TR + EN .mo derlendi |
| 39 | auth merge plan | ✅ Bu doküman |
| 40 | auth merge uygulaması | Sprint 43+'a — high-risk |
| 41 | main/routes audit | ✅ Bu doküman (kullanım ↓) |
| 42 | main/routes sunset | Sprint 44'e |

**Karar:** Bu seansta gerçek silme yok (yüksek risk), kapsamlı plan + i18n ilerleme.
