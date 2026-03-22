# Micro kök URL + klasik arayüz `/kok` (ve `/isr` alias)

## Özet

- **Yeni (Micro) arayüz** artık **site kökünde** (`/`, `/process`, `/project`, …). **Giriş sayfası kökte** **`/login`** (URL çubuğunda `/kok` yok).
- **Önceki (klasik) Kokpitim** blueprint’leri **`LEGACY_URL_PREFIX`** altında — varsayılan **`/kok`** (örn. `/kok/dashboard`, `/kok/projeler`, `/kok/process`).
- Eski yer imleri **`/micro/...`** için **302 yönlendirme** vardır → aynı yol kökte (örn. `/micro/process` → `/process`).
- **`/isr`** ve **`/isr/...`**, **`/kok`** ile aynı hedefe yönlendirir (klasik arayüz alias).

## Ortam değişkeni

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `LEGACY_URL_PREFIX` | `/kok` | Klasik arayüzün URL öneki (başında `/` olmalı) |

## Sağlık kontrolü

- **`GET /health`** — yük dengeleyici / izleme (JSON; klasik arayüz önekinden bağımsız, kökte kalır).

## Statik dosyalar

Micro blueprint statikleri uygulama `static/` ile çakışmaması için **`/m/<path>`** altında sunulur (`url_for('micro_bp.static', ...)` otomatik üretir).

## Giriş / çıkış

- `login_manager.login_view` → **`public_login`** — **klasik giriş şablonu** (`templates/auth/login.html`) **kökta** **`/login`** (`next` sorgu parametresi korunur).
- Aynı giriş görünümü legacy yolda da durur: **`/kok/login`** (`auth_bp.login`) — eski yer imleri çalışır.
- Başarılı giriş sonrası varsayılan yönlendirme: **`micro_bp.launcher`** (`/`).
- Çıkış: **`public_logout`** → **`/logout`** (veya legacy **`/kok/logout`**).

## Swagger (klasik REST)

- UI: **`{LEGACY_URL_PREFIX}/api/docs`**
- Örnek: `/kok/api/docs`

Micro içi API dokümantasyon sayfası: **`/api/docs`** (uygulama içi liste; REST uçları `/api/v1/...` kökte).

## Not

Kök dizindeki alternatif fabrika `kokpitim/__init__.py` (`create_app`) bu yapılandırmayı **otomatik uygulamaz**; üretim ve geliştirme **`app.py` → `app.create_app`** kullanır.
