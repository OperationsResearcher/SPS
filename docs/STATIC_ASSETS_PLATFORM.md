# Platform Statik Varlıklar

Canonical konum: `ui/static/platform/`

| Varlık | Yol |
|--------|-----|
| Font Awesome 6.5.1 | `vendor/fontawesome/all.min.css` + `webfonts/*.woff2` |
| Bileşen CSS | `css/components.css`, `sidebar.css`, `app.css` |
| Modül JS | `js/*.js` |

URL öneki: `/m/...` (`app_bp.static_url_path`)

## Eski kök `static/vendor`

Legacy şablonlar için `static/vendor/fontawesome/` kalabilir; **yeni platform sayfaları** yalnızca `ui/static/platform/vendor` kullanır.

## Tailwind

Geliştirmede CDN (`base.html`); production uyarısı bilinçli kabul. İleride CLI build bu dosyaya eklenebilir.

## Güncelleme

```powershell
# Font Awesome webfont + css (6.5.1)
$fa = "ui\static\platform\vendor\fontawesome"
Invoke-WebRequest -Uri "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" -OutFile "$fa\all.min.css"
# webfonts: fa-solid-900.woff2, fa-regular-400.woff2, fa-brands-400.woff2
```
