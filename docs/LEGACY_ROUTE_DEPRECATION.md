# Legacy Route Budama Listesi (Dalga C)

> GET HTML sayfaları: `legacy_sunset` + `@legacy_html_to_platform` ile platforma yönlenir.  
> POST/API: `main/routes/` paketinde kalır (taşınana kadar).

## Budama önceliği (log analizi sonrası güncellenir)

```bash
python scripts/dev/analyze_legacy_access_log.py /var/log/nginx/access.log
python scripts/dev/inventory_legacy_routes.py
```

| Öncelik | Yol grubusu | Aksiyon |
|---------|-------------|---------|
| P0 | `/dashboard`, `/projeler`, `/surec-karnesi` | GET → middleware (✅) |
| P1 | `/surec/<id>/performans-gostergesi/*` | POST API → micro süreç API'ye taşı |
| P2 | `/kurum/ana-stratejiler/*` | POST → `app_bp.kurum/api/*` ile birleştir |
| P3 | `main/routes/projects.py` içi redirect-only handler'lar | Handler silinebilir (middleware yeter) |

## Paket yapısı (C3 ✅)

```
main/routes/
  __init__.py      # main_bp
  _common.py       # import + yardımcılar + index
  pages.py         # dashboard, surec
  kurum_panel.py   # kurum paneli
  strategy_api.py  # kurum strateji CRUD + asistan
  projects.py      # proje redirect/API
```

Yedek monolit: `main/routes_monolith_backup.py`

## Kaldırma kuralı

1. 30 gün 0 hit (access log)
2. Eşdeğer platform endpoint var
3. pytest + smoke checklist geçer
4. TASKLOG kaydı
