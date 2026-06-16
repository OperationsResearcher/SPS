# ⚡ PERFORMANS ANALİZİ — Tomofil Tenant (id=27)

> **Tarih:** 2026-05-23
> **Tenant ölçeği:** 97 kullanıcı · 28 strategy · 135 sub_strategy · 46 process · 221 KPI · **48.283 KpiData** · 6 yıllık geçmiş
> **Yöntem:** `scripts/benchmark_tomofil.py` ile gerçek DB sorgu süreleri + sorgu sayısı sayımı

---

## 🎯 EN ÖNEMLI BULGU: N+1 DOĞRULANDI

| Sorgu | Süre | Sorgu Sayısı | İyileştirme |
|---|---:|---:|:-:|
| 46 process listing (lazy) | **151ms** | **139** | baseline |
| 46 process listing (joinedload) | **22.8ms** | **1** | **6.6x hızlı, %99.3 sorgu azalması** ✅ |
| 28 strategy listing (lazy) | 30ms | 29 | baseline |
| 28 strategy listing (selectinload) | 9.3ms | 2 | **3.2x hızlı** ✅ |

**Sonuç:** Audit'in N+1 tespit doğru. **eager loading uygulanan yerlerde 6.6x performans artışı garantili.**

---

## 📊 Tam Benchmark Tablosu

### Baseline (basit COUNT)
| | Süre | Sorgu |
|---|---:|---:|
| count(users) | 55.2ms* | 1 |
| count(processes) | 2.6ms | 1 |
| count(kpi_data) — 48K satır | 9.2ms | 1 |

\* İlk sorgu connection warmup içeriyor.

### Aggregation (büyük tablo)
| | Süre |
|---|---:|
| 50 KPI başına KpiData count (GROUP BY) | 8.4ms |
| Yıl bazlı KpiData özet (6 yıl) | 39.4ms |
| Overview (5 count) | 2.8ms |

### Yıl Bazlı KpiData Dağılımı (Tomofil)
| Yıl | Satır |
|:-:|---:|
| 2021 | 7.195 |
| 2022 | 7.231 |
| 2023 | 8.542 |
| 2024 | 9.674 |
| 2025 | 10.373 |
| 2026 | 5.268 |
| **TOPLAM** | **48.283** |

---

## 🔍 Index Sağlığı

### `kpi_data` (8 indeks) ✅
- `kpi_data_pkey`
- `idx_kpi_data_lookup` (composite)
- `ix_kpi_data_data_date`
- `ix_kpi_data_deleted_at`
- `ix_kpi_data_deleted_by_id`
- `ix_kpi_data_is_active`
- `ix_kpi_data_process_kpi_id` ✅ — kritik FK indexi
- `ix_kpi_data_year` ✅

**Değerlendirme:** Index seti güçlü. 48K satır × yıl aggregate 39ms — kabul edilebilir.

### `processes` (7 indeks) ✅
- pkey, code, is_active, name, parent_id, plan_year_id, tenant_id

**Değerlendirme:** Tüm kritik kolonlar indexli.

---

## 🎬 Bottleneck Senaryoları

### Senaryo 1: Süreç listesi sayfası (`/process`)
- **Şu an (lazy):** ~151ms backend + UI render
- **Eager loading sonrası:** ~23ms (6.6x hızlı)
- **Action:** `Process.query.options(joinedload(...))` zorunlu hale getir.

### Senaryo 2: Strateji ana sayfası (`/sp`)
- **Şu an:** ~30ms (selectinload zaten var)
- **Sorun:** Eğer process_sub_strategy_links zincirine erişilirse N+1 patlar
- **Action:** Audit-sourced uyarı: SubStrategy.process_sub_strategy_links lazy=True

### Senaryo 3: k_rapor `/api/kurumsal`
- **Audit tespiti:** N+1 (routes.py:71-89, 278-308)
- **Production scale:** 100+ Strategy × 5 SubStrategy = 500+ sorgu potansiyeli
- **Action:** selectinload chain eklenmeli

### Senaryo 4: KpiData karne (`/process/<id>/karne`)
- Tomofil'de 48K satır — yıl bazlı 7-10K satır
- Karne sayfası `KpiData.year.in_([year, prev_y])` ile filtreliyor → ~17K satır gelir
- **Önemli:** Bu sayfanın yıl filtresi düzgün çalışmazsa 48K satır gelir
- **Action:** Plan year filter sıkı uygulanmalı (Sprint 1 helper kullanılmalı)

---

## 🟢 İYİ HABER

1. ✅ Tüm kritik index'ler mevcut
2. ✅ 48K KpiData üzerinde aggregate 39ms — production-ready
3. ✅ Sprint 1'de eklenen `plan_year_filter` helper N+1 prevention için altyapı
4. ✅ Sprint 3'te eklenen `query_counter` regression test'leri yapılabilir
5. ✅ joinedload + selectinload eklenmesi tek dosya, tek satır çözüm

---

## 🔴 KRİTİK ÖNERİ — Sprint 11

### Acil eylem listesi (~6-8 saat efor)

| # | İş | Konum | Tahmin |
|---|---|---|:-:|
| 1 | `Process.query.options(joinedload(leaders, members, owners))` | surec/routes_process.py:84-88 | 30 dk |
| 2 | Aynı eager loading: parent + child queries | surec/routes_process.py:211-224 | 30 dk |
| 3 | `Strategy.query.options(selectinload(sub_strategies))` zincirlerine | k_rapor/routes.py:71-89 | 1 saat |
| 4 | k_rapor User lookup'larını batch'le (`User.query.filter(User.id.in_(...))`) | k_rapor/routes.py:443-444 | 1 saat |
| 5 | ProcessMaturity sorgusuna pagination + index | k_radar/routes_kp.py:74-78 | 1 saat |
| 6 | Karne yıl filtresi sıkı plan_year_filter helper | surec/routes_karne.py | 1 saat |
| 7 | N+1 regression test (Process listing için) | tests/test_query_counter.py | 1 saat |
| 8 | Benchmark script'i CI'a ekle (her commit'te performance regression kontrolü) | .github/workflows/ | 1 saat |

**Beklenen sonuç:** Tüm liste sayfalarında **3-7x performans artışı**.

---

## ⚙️ Bu Raporun Tekrarlanması

```bash
python scripts/benchmark_tomofil.py
```

Çıktıyı snapshot olarak saklamak için:
```bash
python scripts/benchmark_tomofil.py | tee benchmarks/bench_$(date +%Y%m%d_%H%M).log
```

CI/CD entegrasyonu için: her PR'da çalıştırıp önceki snapshot ile karşılaştır → regression varsa fail.

---

> **Sonuç:** Performans altyapı güçlü (index'ler, query counter, helper'lar var).
> Eksik olan tek şey: bunları **mevcut route'larda uygulamak**.
> 1 sprint × 6-8 saat efor ile production-grade performansa ulaşılır.
