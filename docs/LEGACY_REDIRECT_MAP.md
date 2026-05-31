# Legacy → Platform Yönlendirme Haritası

> Uygulama: `app/middleware/legacy_sunset.py`  
> Yalnızca **GET/HEAD**. API, `/process`, platform kök yolları atlanır.  
> Kapatma: `LEGACY_SUNSET_ENABLED=false`

---

## Tam yol eşleşmeleri (301 → `url_for`)

| Legacy yol | Platform endpoint | Platform URL (örnek) |
|------------|-------------------|----------------------|
| `/dashboard` | `app_bp.masaustu` | `/masaustu` |
| `/surec-karnesi` | `app_bp.surec` | `/surec` |
| `/surec-paneli` | `app_bp.surec` | `/surec` |
| `/gorevlerim` | `app_bp.bireysel_karne` | `/bireysel/karne` |
| `/performans-kartim` | `app_bp.bireysel_karne` | `/bireysel/karne` |
| `/kurum-paneli` | `app_bp.kurum` | `/kurum` |
| `/kurum-yonetim` | `app_bp.kurum_ayarlar` | `/kurum/ayarlar` |
| `/admin-panel` | `app_bp.yonetim_paneli` | (admin panel route) |
| `/easy-login` | `public_login` | `/login` |
| `/hgs`, `/hizli-giris`, `/Hgs_mfg`, `/hgs/login/*` | — | **404** (güvenlik; canlı HGS yalnızca `/MfG_hgs`) |
| `/projeler` | `app_bp.project_list` | `/project` |
| `/projeler/yeni` | `app_bp.project_new` | `/project/new` |
| `/stratejik-planlama-akisi` | `app_bp.sp` | `/sp` |
| `/stratejik-planlama-akisi/dinamik` | `app_bp.sp_flow` | `/sp/...` (flow) |
| `/stratejik-asistan` | `app_bp.sp` | `/sp` |
| `/redmine`, `/bireysel-panel` | `app_bp.bireysel_karne` | `/bireysel/karne` |
| `/login-user` | `public_login` | `/login` |

Query string korunur (`?next=…` vb.).

---

## Önek yeniden yazma (301, path rewrite)

| Legacy önek | Platform önek |
|-------------|----------------|
| `/projeler/` | `/project/` |
| `/v3/kurum-paneli/visual` | `/kurum` |
| `/v3/kurum-paneli` | `/kurum` |
| `/v3/skor-motoru` | `/kurum` |

### `/projeler/<id>/…` kuralları

| Legacy alt yol | Platform |
|----------------|----------|
| `/projeler/<id>` | `/project/<id>` |
| `.../duzenle` | `/project/<id>/edit` |
| `.../gorevler/yeni` | `/project/<id>/task/new` |
| `.../gorevler/<tid>/duzenle` | `/project/<id>/task/<tid>/edit` |
| `.../gorevler/<tid>` | `/project/<id>/task/<tid>` |
| `kanban` / `takvim` / `gantt` / `raid` | `/project/<id>/views/...` |

---

## 410 Gone (bilinçli kapatma)

| Yol | Davranış |
|-----|----------|
| `/v2`, `/v2/*` | 410 |
| `/v3`, `/v3/*` (yukarıdaki rewrite dışı) | 410 |
| `/bsc`, `/bsc/*` | 410 |

---

## Atlanan yollar (middleware dokunmaz)

- `/process`, `/process/*` — micro süreç + API
- `/surec/*` — platform süreç alt yolları
- `/api/`, `/process/api/`, `/micro/api/`
- `/m/`, `/static/`, `/auth/`, `/login`, `/logout`
- `/health`, `/swagger`, `/docs`
- Marketing: `/marketing`, `/ozellikler`, `/blog`, `/demo`, `/iletisim`
- Platform canonical: `/kurum`, `/kurum/…`, `/project/…`, `/masaustu`, `/sp`, `/bireysel`, vb.

---

## Kök `/`

`main_bp.index` → giriş yoksa `/login`, varsa `app_bp.launcher` (middleware değil, route).

---

## Log analizi

```bash
python scripts/dev/analyze_legacy_access_log.py /path/to/access.log
```

Çıktı: en çok hit alan legacy path’ler → Dalga C budama önceliği.

---

## Smoke (deploy sonrası)

- [ ] `GET /dashboard` → 301, `Location` içinde `/masaustu`
- [ ] `GET /projeler` → 301, `/project`
- [ ] `GET /v2/foo` → 410
- [ ] `GET /surec` → 200 (platform; middleware atlar)

Bkz. `docs/DEPLOY_SMOKE_CHECKLIST.md`
