# Canlı Yayın — Smoke Checklist

VM / production deploy sonrası 10–15 dakikalık doğrulama.

## Ortam

- [ ] `FLASK_ENV=production`
- [ ] `SECRET_KEY` set (min 32 karakter)
- [ ] `SQLALCHEMY_DATABASE_URI` PostgreSQL
- [ ] `REDIS_URL` tanımlı (rate limit + cache için önerilir)
- [ ] `HGS_BYPASS_ENABLED` **tanımlı değil** veya `false`
- [ ] `alembic upgrade head` tamamlandı

## HTTP smoke

- [ ] `/auth/login` — giriş formu 200
- [ ] Başarılı login → launcher / masaüstü
- [ ] `/masaustu` — istatistik kartları + ikonlar görünür
- [ ] `/surec` — süreç listesi açılır
- [ ] `/sp` — stratejik plan sayfası
- [ ] `/MfG_hgs` — **yalnızca** `HGS_BYPASS_ENABLED=true` + debug/local; production’da bypass kapalı olmalı
- [ ] `/hgs` — **404** (legacy bookmark; canlı HGS yalnızca `/MfG_hgs` + flag)
- [ ] `GET /dashboard` → 301 → `/masaustu` (legacy sunset)
- [ ] `GET /projeler` → 301 → `/project`
- [ ] `GET /v2/test` → **410 Gone**

## Güvenlik

- [ ] Yanlış şifre 5+ deneme → rate limit (429 veya uyarı)
- [ ] Response header: `X-Content-Type-Options`, `X-Frame-Options`
- [ ] Tarayıcı konsolunda CSP font/script blokajı yok

## CI (yerel)

```bash
python scripts/ci/check_single_db.py
python scripts/ci/check_portfolio_imports.py
python scripts/ci/check_no_raw_models_import.py
set FLASK_ENV=testing
set SECRET_KEY=test-secret-key-32-chars-minimum!!
pytest tests/ -q --no-cov
```
