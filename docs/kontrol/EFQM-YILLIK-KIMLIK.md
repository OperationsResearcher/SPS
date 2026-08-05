# EFQM yıllık skor + kimlik fallback

> 2026-08-05 · Dal: `claude/efqm-yillik-kimlik`

## Sorun

KMF’de amaç/vizyon `tenants`’ta dolu; EFQM yalnız `tenant_year_identities` okuyordu → 1.1 = 0.
Ayrıca skor seçili plan yılına net bağlanmalı.

## Karar

1. **Yıl:** API `?year=` veya session (`get_active_plan_year_for_user`). Üst bar yıl değişince sayfa yenilenir → kart/modal yeniden hesaplar.
2. **1.1 / 2.1:** Seçili yılın `tenant_year_identities` alanları; boş olanlar `tenants` fallback (SP ile aynı).
3. Modal hero’da **Plan yılı** gösterilir; kart badge’de yıl etiketi.

## Smoke (KMF 16)

| Yıl | Toplam | 1.1 |
|---|---|---|
| 2026 | 182 | 2/5 |
| 2025 | 208 | 2/5 |
| (fallback) | — | purpose+vision tenants |
