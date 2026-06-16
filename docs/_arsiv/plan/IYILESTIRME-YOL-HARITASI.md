# Kokpitim — İyileştirme Yol Haritası (Master)

> **Tek gerçek kaynak (kurallar):** `docs/KURALLAR-MASTER.md`  
> **Görev günlüğü:** `docs/TASKLOG.md`  
> **Son güncelleme:** 2026-05-19 | Dalga A–D tamamlandı (TASK-106 → TASK-109)

Bu belge, mimari borç, güvenlik, test ve legacy kapanışını **faz + dalga** olarak tanımlar.

---

## Özet durum

| Alan | Durum | Not |
|------|--------|-----|
| Platform UI (`app_bp` / `micro/`) | ✅ Aktif | Yeni özellikler burada |
| Legacy `main/routes/` paketi | ✅ Modüler | 5 alt modül + yedek monolit |
| `models` paketi | 🟡 Shim | `app/models/*_legacy.py` — B2 planı |
| CI guard'lar | ✅ | tek db, portföy, raw models |
| Test suite | ✅ **66** | E2E, tenant, N+1, sunset |
| Prod güvenlik | ✅ | CSP, HGS, Redis rate limit |
| Tailwind CDN | 🔵 Bilinçli | Kullanıcı tercihi |

---

## Faz 0 — Temel ✅

TASK-100 → TASK-105. Bkz. `docs/TASKLOG.md`.

---

## Faz 1 — Dalga A: Legacy sunset ✅

| Madde | Durum |
|-------|--------|
| `legacy_sunset` middleware | ✅ |
| `LEGACY_*_BP_ENABLED` | ✅ |
| `LEGACY_REDIRECT_MAP.md` | ✅ |
| `tests/test_legacy_sunset.py` | ✅ |

---

## Faz 2 — Dalga B: Model / API birliği ✅

| Madde | Durum | Referans |
|-------|--------|----------|
| `legacy_bridge` → `user_legacy`, `strategy_legacy`, `legacy_extras` | ✅ | `app/models/` |
| Runtime `from models` yalnızca shim dosyalarında | ✅ | CI guard |
| Süreç API canonical | ✅ | `docs/PROCESS_API_CANONICAL.md` |
| Model birleştirme planı (B2 uzun vade) | 📋 | `docs/MODEL_MERGE_PLAN.md` |
| `tests/test_process_api_surface.py` | ✅ | |

---

## Faz 3 — Dalga C: Route budama / modülerleştirme ✅

| Madde | Durum |
|-------|--------|
| `main/routes/` paket bölünmesi | ✅ `_common`, `pages`, `kurum_panel`, `strategy_api`, `projects` |
| `@legacy_html_to_platform` yedek yönlendirme | ✅ `main/deprecated.py` |
| Budama listesi + log analizi | ✅ `docs/LEGACY_ROUTE_DEPRECATION.md` |
| Monolit yedek | ✅ `main/routes_monolith_backup.py` |

---

## Faz 4 — Dalga D: Test ve kalite ✅

| Madde | Durum |
|-------|--------|
| Platform akış testleri | ✅ `tests/test_e2e_flow.py` |
| Tenant izolasyonu | ✅ `tests/test_tenant_isolation.py` |
| N+1 regression (süreç+KPI) | ✅ `tests/test_process_n1_guard.py` |
| `/process/api/*` JSON hata yanıtı | ✅ `error_handlers._wants_json_response` |

---

## Dalga özeti

| Dalga | Odak | Durum |
|-------|------|--------|
| **A** | Legacy HTML yönlendirme, 410 | ✅ |
| **B** | Model shim, süreç API tek kaynak | ✅ |
| **C** | main/routes paket, deprecated decorator | ✅ |
| **D** | E2E, tenant, N+1 testleri | ✅ |

---

## Faz 5–7 (sonraki işler)

- **Faz 5:** Tailwind build, JS modül bölme, console.log temizliği
- **Faz 6:** Sentry release, yapılandırılmış log, Redis zorunlu prod
- **Faz 7:** SaaS onboarding, plan limitleri, API v1 sözleşmesi

---

## Ortam değişkenleri

| Değişken | Varsayılan |
|----------|------------|
| `LEGACY_SUNSET_ENABLED` | `true` |
| `LEGACY_PROCESS_BP_ENABLED` | `false` |
| `LEGACY_DASHBOARD_BP_ENABLED` | `false` |

---

## İlgili belgeler

| Belge | İçerik |
|-------|--------|
| `docs/LEGACY_REDIRECT_MAP.md` | Yönlendirme tablosu |
| `docs/LEGACY_ROUTE_DEPRECATION.md` | Budama önceliği |
| `docs/MODEL_MERGE_PLAN.md` | Tablo birleştirme |
| `docs/PROCESS_API_CANONICAL.md` | Süreç API |
| `docs/DEPLOY_SMOKE_CHECKLIST.md` | Canlı smoke |

---

## Sonraki adım

**Faz 5** veya **B2.2** strateji tablo migrasyonu — ayrı TASK ile.
