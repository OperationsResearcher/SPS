# VM KMF salt okunur anlık görüntü (deploy öncesi)

**Amaç:** Canlı VM’de `tenant_id=16` (Kayseri Model Fabrika) için veri **okundu**, **hiçbir INSERT/UPDATE/DELETE yapılmadı**.

**Üretim:** `scripts/kmf_task084_counts.py` konteyner içinde çalıştırıldı (salt okuma).

## Tablo (VM — KMF)

| Metrik | Değer |
|--------|------:|
| tenant_id | 16 |
| Kurum | Kayseri Model Fabrika |
| Kullanıcı | 8 |
| Süreç | 11 |
| PG (process_kpis) | 135 |
| PGV (kpi_data, silinmemiş) | 318 |
| plan_years | 7 |
| Strateji | 6 |
| Alt strateji | 21 |

## Ham JSON

```json
{
  "tenant_id": 16,
  "tenant": {
    "id": 16,
    "name": "Kayseri Model Fabrika"
  },
  "kullanici": 8,
  "surec": 11,
  "pg": 135,
  "pgv": 318,
  "plan_years": 7,
  "strateji": 6,
  "alt_strateji": 21
}
```

## Deploy notu

`scripts/vm_safe_deploy.sh` önce **`pg_dump` tam yedek** alır, sonra `git pull` ve Docker imajı üretir; **tenant verisine yönelik toplu silme/yükleme yapmaz**. KMF satırları bu akışta değiştirilmez.
