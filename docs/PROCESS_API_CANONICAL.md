# Süreç API — Canonical Yüzey (Dalga B4)

## Tek kaynak

| Yol | Blueprint | Durum |
|-----|-----------|--------|
| `/process`, `/process/<id>/karne` | `app_bp` (`micro/modules/surec/`) | ✅ Canonical |
| `/process/api/*` | `app_bp` | ✅ Canonical |
| `/process/api/*` | `process_bp` (`app/routes/process.py`) | 🔴 Varsayılan **kapalı** |

## Ortam

```bash
LEGACY_PROCESS_BP_ENABLED=false   # varsayılan — çift yüzey yok
```

Acil geri alma: `LEGACY_PROCESS_BP_ENABLED=true`

## Middleware

`legacy_sunset` `/process` ve `/process/api/` yollarını **atlar** — platform süreç API'si doğrudan çalışır.

## Yeni geliştirme

- Yalnızca `micro/modules/surec/routes_*.py` içine endpoint ekleyin.
- `app/routes/process.py` yalnızca bakım; yeni route eklenmez.
