# Bağımlılık taraması ve kilit dosyası (KalDer P7, 2026-10-24)

## Yöntem
İzole venv (`C:\tmp\venv_p7`, Python 3.13) → `pip install -r requirements.txt -r requirements-test.txt` → tam test
(1141 geçti) → `python scripts/ops/kilit_uret.py` ile `requirements.lock` (102 paket, test edilen sürümler) →
`pip-audit -r requirements.lock --no-deps` (SSL kesme için `truststore.inject_into_ssl()` gerekir).

## Bulgu ve düzeltme
| Paket | Eski | Yeni | Neden |
|---|---|---|---|
| marshmallow | 3.20.1 | 3.26.2 | PYSEC-2026-1605 |
| python-socketio | 5.10.0 | 5.16.2 | PYSEC-2026-1854, PYSEC-2026-3042 |

Güncellemeden sonra tam test yeniden geçti (1141), `pip check` temiz, `pip-audit`: **bilinen açık yok**.

## Python sürümü doğrulaması (Docker'sız, 2026-10-24)
Yerel Docker kaldırıldı; Docker imajının yaptığı iş `python:3.11-slim` + `pip install -r requirements.txt` olduğundan bu **Docker'sız taklit edildi**:
- Python 3.11.17 (`uv python install 3.11`, kullanıcı klasörüne) ile temiz venv, `requirements.txt` + `requirements-test.txt` kurulumu (Docker'ın çözeceği sürümler: numpy 2.4.6, scipy 1.17.1, Deprecated 1.3.1).
- Tam test **3.11'de: 1211 geçti, 0 başarısız** (3.13'te 1209; bu makinede 3.13 + çok parçalı yükleme testleri takılıyor, 3.11'de iki upload testi de geçti → uygulama hatası değil test ortamı uyumsuzluğu).
- Bu çalışma bir çakışma da buldu: `requirements-test.txt` `marshmallow==3.20.1` sabitliyordu, `requirements.txt` 3.26.2 → ikisi birlikte kurulamıyordu; düzeltildi.
- `requirements.lock` 3.11'de doğrulanan sürümlerden **yeniden üretildi** (yalnız numpy, scipy, deprecated değişti). Hiçbir paketin `Requires-Python` kısıtı 3.11–3.13'ü dışlamıyor → kilit artık hem Docker (3.11) hem yerel (3.13) için kurulabilir.
- **Dockerfile hâlâ `requirements.txt` (alt sınırlı `>=`) kuruyor, kilidi değil**: build'ler zamanla farklı sürüm çekebilir. Kilide geçmek tek satırlık bir değişiklik ama dağıtım davranışını değiştirir → kullanıcı onayı + Test'te doğrulama gerekir (yapılmadı).
- Sunucuda gerçek Docker build yine de Test ortamında yapılmalı (sistem paketleri: gcc, libpq-dev bu doğrulamada yok).

## Yapılmayanlar
Kök bağımlılıkların majör güncellemesi (cryptography/aiohttp vb.) gerekmedi: taze venv zaten en güncel sürümleri
çözdü ve testler geçti; `requirements.txt` alt sınırları (>=) değişmedi.
