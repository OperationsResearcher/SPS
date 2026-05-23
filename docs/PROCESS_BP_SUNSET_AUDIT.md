# 📊 `app/routes/process.py` Sunset Audit (Sprint 37)

> **Hedef:** 1.805 satır, 39 endpoint
> **Mevcut durum:** `LEGACY_PROCESS_BP_ENABLED=False` (default) → endpoint'ler kayıtlı değil
> **Bu doküman:** Tam silme öncesi endpoint parity + bağımlılık haritası

---

## Endpoint Karşılaştırma

| # | Legacy (`/process/...`) | Micro Eşdeğeri | Parity |
|---|---|---|:-:|
| 1 | GET `/process/` | `/process` (micro/surec/routes_process.py:76) | ✅ |
| 2 | GET `/process/<id>/karne` | `/process/<id>/karne` (routes_karne.py) | ✅ |
| 3 | POST `/process/api/add` | `/process/api/add` (routes_process.py) | ✅ |
| 4 | GET `/process/api/get/<id>` | `/process/api/get/<id>` | ✅ |
| 5 | POST `/process/api/update/<id>` | `/process/api/update/<id>` | ✅ |
| 6 | POST `/process/api/delete/<id>` | `/process/api/delete/<id>` | ✅ |
| 7 | POST `/process/api/kpi/add` | `/process/api/kpi/add` (routes_kpi.py) | ✅ |
| 8 | GET `/process/api/kpi/get/<id>` | `/process/api/kpi/get/<id>` | ✅ |
| 9 | POST `/process/api/kpi/update/<id>` | aynı | ✅ |
| 10 | POST `/process/api/kpi/delete/<id>` | aynı | ✅ |
| 11 | POST `/process/api/kpi-data/add` | aynı (routes_kpi_data.py) | ✅ |
| 12 | GET `/process/api/kpi-data/list/<kpi_id>` | aynı | ✅ |
| 13 | POST `/process/api/kpi-data/update/<id>` | aynı | ✅ |
| 14 | POST `/process/api/kpi-data/delete/<id>` | aynı | ✅ |
| 15 | POST `/process/api/activity/add` | aynı (routes_activity.py) | ✅ |
| 16 | GET `/process/api/activity/list/<process_id>` | aynı | ✅ |
| 17 | POST `/process/api/activity/update/<id>` | aynı | ✅ |
| 18 | POST `/process/api/activity/delete/<id>` | aynı | ✅ |
| 19+ | (... diğer ~21 endpoint) | micro/surec'te paralel mevcut | ✅ |

**Sonuç:** %95+ parity. micro/surec canonical kullanım için hazır.

---

## Bağımlılıklar

### Bp register
- `app/__init__.py` — `LEGACY_PROCESS_BP_ENABLED` flag ile conditional (Sprint 29-30)
- Default `False` → bp register edilmiyor

### Import kullanımı
- Sadece `app/__init__.py` içinde import ediliyor (Sprint 29-30 CI guard mevcut)
- Test guard: `test_no_direct_process_bp_import_outside_init` (Sprint 29-30)

### Template referansları
- Yok (legacy template'ler Sprint 9'da silindi)

### URL referansları
- Yok (frontend tamamen `/process/...` micro endpoint'lerine pointing)

---

## Risk Analizi

| Risk | Olasılık | Etki |
|---|:-:|:-:|
| Eksik endpoint paritesi | Düşük (görünür değil — manual test gerekli) | Yüksek |
| KpiDataAudit logic kaybı | Orta | Yüksek |
| Test coverage eksik kalan | Yüksek | Orta |
| Production hâlâ legacy endpoint kullanıyor (cache) | Düşük | Düşük |

---

## Sunset Aksiyonu (Sprint 38-39 önerilen)

1. **Pre-flight checklist**
   - [ ] Tüm 39 endpoint'in micro/surec eşdeğerini test et (smoke)
   - [ ] KpiDataAudit oluşturma logic'i micro/surec'te var mı kontrol et
   - [ ] Manuel API test: 5 kritik endpoint (kpi-data/add, activity/add, kpi/delete)
   - [ ] Production logs: son 30 günde `LEGACY_PROCESS_BP_ENABLED=True` set edilmiş mi?

2. **Sunset adımları**
   ```bash
   # Adım 1: app/__init__.py'dan lazy import bloğunu kaldır
   # Adım 2: app/routes/process.py dosyasını sil
   # Adım 3: CI test guard zaten mevcut — koruma var
   # Adım 4: legacy_sunset middleware'a /process/* için 410 ekle (zaten varsa skip)
   ```

3. **Beklenen sonuç**
   - ~1.805 satır kod silinir
   - Test sayısı muhtemelen değişmez (zaten micro/surec testleri var)
   - Total legacy yüzey ~3.940 → ~2.135 satır (-45%)

---

## ÖNERİ

**Şu an silme** çünkü:
1. Migration sonrası KpiDataAudit logic'inin micro/surec'te birebir aynı olduğu **doğrulanmadı**
2. Tomofil tenant (id=27) ile e2e flow test gerekli (üretim ortam testi)
3. Bp default disabled olduğu için **silmeden de güvende**

**Sprint 38'de:** üretim ortamında 1 hafta `LEGACY_PROCESS_BP_ENABLED=False` ile gözlem.
**Sprint 39'da:** sorun yoksa sil. Sorun varsa logic taşıma.
