# 🪦 LEGACY SUNSET HARİTASI (Sprint 4 Çıktısı)

> **Hedef:** Sprint 9'a kadar ~4.700 satır legacy kod sil
> **Yöntem:** Önce referansları kıran → sonra silen kontrollü sunset

---

## Bağımlılık Grafiği

```
app/routes/dashboard.py  ──referans──>  admin.py:774, strategy.py:93, safe_urls.py
                                            │
                                            ▼
                                     Önce bunları kır
                                            │
                                            ▼
app/routes/dashboard.py  ──silinebilir──>  ✅
```

---

## Sunset Adayları

### 🔴 KOLAY (1-2 saat)

| Dosya | Satır | Referans sayısı | Plan |
|---|:-:|:-:|---|
| `decorators.py` (root) | 207 | 2 (api/routes.py, main/routes/_common.py) | api/routes.py'da import'u app/utils'a taşı |
| `app/routes/dashboard.py` | 264 | 3 (admin, strategy, safe_urls) | Referansları `app_bp.masaustu`'ya yönlendir |

### 🟡 ORTA (3-5 saat)

| Dosya | Satır | Referans | Plan |
|---|:-:|:-:|---|
| `app/routes/strategy.py` | 195 | 7 (template'ler) | Template'ler `app_bp.sp` benzerine güncelle |
| `app/routes/auth.py` | 302 | aktif (login/logout) | micro/shared/auth ile merge — bu daha büyük iş |

### 🟠 YÜKSEK (Sprint 9'da)

| Dosya | Satır | Plan |
|---|:-:|---|
| `app/routes/process.py` | **1.805** | LEGACY_PROCESS_BP_ENABLED=False; micro/surec canonical. Sprint 9'da sil |
| `app/routes/admin.py` | **1.141** | micro/admin ile merge sonrası sil |
| `main/routes/` | ~328 | Public site + legacy redirects — tam audit gerekir |

---

## Önerilen Sunset Sırası (Sprint 9)

```
1. Template'leri güncelle (strategy_bp → app_bp.sp.*)
2. admin.py:774 redirect'i app_bp.masaustu'ya çevir
3. dashboard.py sil (264 satır)
4. strategy.py sil (195 satır)
5. test_legacy_sunset.py genişlet — 410 Gone bekleyen route'lar
6. CI import guard: legacy import'ları yasakla
7. decorators.py: api/routes.py'daki kullanım app/utils/decorators.py'ya taşı
8. decorators.py sil (207 satır)
9. app/routes/process.py: KpiDataAudit logic'i micro/surec'e taşı, sil (1.805 satır)
10. app/routes/admin.py: micro/admin ile merge, sil (1.141 satır)

Toplam silinen: ~3.940 satır
```

---

## Tooling

- **Import guard:** `tests/test_import_guards.py` — legacy modüllerden import'ları yasakla
- **Safe URLs:** `app/utils/safe_urls.py` — eski endpoint name → yeni mapping
- **Test:** `tests/test_legacy_sunset.py` — silinen endpoint'lerin 410 Gone döndüğünü doğrula

---

**Sprint 4'te yapılan:** Bu harita yayınlandı. Asıl silme Sprint 9'da.
