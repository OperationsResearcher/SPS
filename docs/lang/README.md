# docs/lang/ — Çoklu Dil (i18n) Çalışması

Kokpitim çoklu dil desteği için durum, analiz ve plan. (KURALLAR §9 mantığı: önce yaz, mutabakat sonra kodla.)

| Belge | İçerik |
|-------|--------|
| [`00-DURUM-RAPORU.md`](00-DURUM-RAPORU.md) | Mevcut durum envanteri — ne var, ne yok, neden yarım kaldı |
| [`01-ANALIZ.md`](01-ANALIZ.md) | İş hacmi, teknik kararlar, UI/içerik ayrımı, riskler |
| [`02-FAZ-PLANI.md`](02-FAZ-PLANI.md) | Fazlı uygulama planı (FAZ 0→7), dikey dilimler, disiplin |

## Tek bakışta durum (2026-06-23)
- Altyapı tasarlanmış (`app/i18n.py` locale zinciri sağlam) ama **flask-babel kurulu değil → i18n kapalı**
- Katalog iskeleti var (`translations/{tr,en}`) — sadece **33 string**
- **0 template** çeviriye işaretli; ~2.500 string'lik iş bekliyor
- Dil seçici UI / `/set-language` route yok
- İçerik (strateji/süreç/KPI adları) çevrilmez — yalnız UI metni çevrilir

## Önerilen başlangıç
**FAZ 0** (½ gün, risksiz): paketi kur, `/set-language` + dil seçici ekle, `<html lang>` dinamikleştir.
Sonunda dil değişimi mekanik çalışır. Kullanıcı onayı bekleniyor.
