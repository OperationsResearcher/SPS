# Hesap / Doğruluk Keşfi — 2026-07-23

> **Kapsam:** Derinlik C. Odak: hesap/doğruluk.
> **Kararlar uygulandı:** 1C · 2A · 3A · 4A · 5C · 6A · 7A · 8A (dal `claude/hesap-dogruluk-duzeltmeleri`)

---

## Karar → uygulama

| Kod | Karar | Uygulama |
|-----|--------|----------|
| SEM | C — etiket ayrımı | Masaüstü: «Hedef oranı» + «Başarı bandı» ayrı badge |
| D1 | A — fallback kaldır | `mapped_process_count` dürüst 0; mc-empty |
| D3 | A — mc-empty | OEE/VSM/olgunluk vb. None + `data_available` |
| D2 | A — trend yok | `trend=None` yetersiz veride |
| T1 | C — tek tablo | `app/services/rpn_severity.py` |
| DIR | A — direction zorunlu | `performance_service` + `project_service` |
| D0 doc | A — KAPALI | `KART-VERI-TUTARSIZLIKLARI.md` güncellendi |
| G1 | A — migration | `hd01a2b3c4d5` · `project_id` FK → `project` |

---

## Özet hüküm (keşif anı)

| Kod | Keşif | Şimdi |
|-----|--------|--------|
| D0 | Kod kapalı, belge açık | Belge KAPALI |
| SEM | P0 | Etiket ayrımı (backfill yok) |
| D1 | P0 | Düzeltildi |
| D3/İ1 OEE | P1 | mc-empty; diğer İ1 açık |
| D2 | P1 | Düzeltildi |
| T1 | P1 | Düzeltildi |
| DIR | P1 | Düzeltildi |
| G1 | P2 | Düzeltildi |

---

## Not

`pybasla.py` restart gerekir (base/JS/template). K-Radar cache 300sn.
