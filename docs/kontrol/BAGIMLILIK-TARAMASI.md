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

## ⚠ Python sürümü uyarısı (deploy öncesi okunmalı)
- Testler **Python 3.13**'te koştu. Docker imajı **3.11-slim** ve `requirements.txt`'ten kuruyor (kilitten değil).
- `requirements.lock` içinde **numpy 2.5.4, scipy 1.18.1, Deprecated 3.0.0 Python ≥3.12 ister** → kilit 3.11'de
  KURULAMAZ. Docker'da kullanma; kilit yalnız Yerel (3.13) ve sürüm referansı/tarama içindir.
- `marshmallow 3.26.2` ve `python-socketio 5.16.2` 3.11 ile uyumlu (Requires-Python ihlali yok).
- Docker 3.11'de `requirements.txt` daha eski numpy/scipy çözer; o kombinasyon bu çalışmada test EDİLMEDİ
  (mevcut "ortam paritesi yok" borcu). Yayın'dan önce Test'te Docker build + test şart.
- Kalıcı çözüm: Docker'ı 3.13'e çıkarmak (ayrı karar) ya da 3.11 için ayrı kilit.

## Yapılmayanlar
Kök bağımlılıkların majör güncellemesi (cryptography/aiohttp vb.) gerekmedi: taze venv zaten en güncel sürümleri
çözdü ve testler geçti; `requirements.txt` alt sınırları (>=) değişmedi.
