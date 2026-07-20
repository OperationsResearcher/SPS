# Plan yılı — ham INSERT betikleri (ARŞİV)

> **Bu betikler ÇALIŞTIRILMAZ.** Arşivlenme tarihi: 2026-07-20
> Gerekçe: yıl bazlı program Faz 1.8 (S9 — seed açığı), `docs/yilbazli/`

## Neden arşivlendi

Bu dört betik `plan_years` tablosuna **servis katmanını atlayarak** ham `INSERT`
yazıyordu. Sonuç, yıl bazlı sistemin en sinsi hatasıydı:

> Plan yılı satırı oluşuyor, ama o yıla ait yapı (süreç, PG, hedef) **hiç
> doğmuyor**. Ekran yıl seçiciyi gösteriyor, kullanıcı yılı seçiyor, sistem
> hatasız çalışıyor — sadece veri yok.

Ölçüm (2026-07-20): yıl sistemi açık 3 kurumun **2'sinde** (KMF #16,
Eskişehir #28) hedefli `kpi_year_configs` satırı **sıfırdı**. Sebep buydu.

## Arşivlenen betikler

| Betik | Ne yapıyordu | Son dokunulma |
|---|---|---|
| `vm_apply_plan_years.py` | JSON'dan `plan_years`'a ham INSERT (önce DELETE) | 2026-04-12 |
| `kmf_hybrid_sync.py` | KMF yerel↔VM senkron | 2026-04-12 |
| `kmf_pull_plan_years_from_vm.py` | VM'den plan yılı çekme (**`gcloud` gerektirir** — GCP arşiv ortamı, KURALLAR §8.5) | 2026-04-12 |
| `migrate_genesis_plan_year.py` | Tek seferlik genesis PlanYear ataması | 2026-04-10 |

Dördü de tek seferlik göç işleriydi ve Nisan 2026'dan beri dokunulmamıştı.

## Bunun yerine ne kullanılır

Plan yılı **yalnızca servis katmanından** doğar:

```python
from app.services.plan_year_service import get_or_create_plan_year, initialize_plan_years

get_or_create_plan_year(tenant_id, year)   # tek yıl — önceki dolu yıldan klonlar
initialize_plan_years(tenant_id, 2020)     # zincir — start_year'dan bugüne
```

Faz 1.8'den itibaren `get_or_create_plan_year` bir önceki dolu yıldan
`clone_full_plan_year` ile **gerçek varlık kopyaları** üretir (T2: "yıl
devrinde her şey kopyalanır"). Seed artık ayrı bir adım değil — yıl
oluşturmanın kendisi. Atlanması mümkün değil.

Yerel bakım/onarım için: `scripts/ops/yilbazli_faz1_3_plan_yili_zinciri.py`
(kontrol modu varsayılan).

## Kayıt

Bu betiklere kalan referanslar yalnızca geçmiş kayıtlarda: `docs/TASKLOG.md`,
`migrations/_archive_versions/c2d3e4f5g6h7_*.py` ve bir yedek klasör adı
(`backups/kmf_hybrid_sync/` — betik değil, dizin). Çalışan hiçbir kod yolu
bu dosyalara bağlı değil (2026-07-20'de tarandı).
