# Masaüstü + Bireysel Karne — Yol haritası (Micro)

> **Faz 0 — Hizalama**  
> - **Micro** (`/masaustu`, `/bireysel/karne`) birincil giriş; veri kaynağı: `IndividualPerformanceIndicator`, `IndividualKpiData`, `IndividualActivity`, `IndividualActivityTrack`, `Notification` (`app.models.core`).  
> - **Klasik Kokpitim** `LEGACY_URL_PREFIX` altında (ör. `/kok`); yeni özellikler **Micro modellerine** yazılır.  
> - Eski **V3 Dashboard** (`/v3/dashboard`) artık ürün kapsamında değil; arayüzden kaldırıldı (blueprint kod tabanında duruyorsa bakım/emeklilik ayrı karar).

## Uygulanan fazlar (özet)

| Faz | Bireysel karne | Masaüstü |
|-----|----------------|----------|
| **1** | PG ay hücrelerinde ısı vurgusu; satıra tıklayınca yıllık veri serisi (modal) | Bugün özeti, hızlı işlemler, bildirimde okundu, bu ay eksik PG uyarısı |
| **2** | Zaman çizgisi (PG verisi + tamamlanan faaliyet ayları) | Benim Masam: Bugün / 7 gün / Geciken sekmeleri |
| **3** | Hedef–gerçekleşen özet şeridi; PG detayında mini sparkline | Widget sırası (sürükle) + görünürlük (localStorage); karalama defteri (localStorage) |
| **4** | Dokümantasyon + TASKLOG | Aynı |

## Eski “V3” fikirlerinin Micro karşılığı

- Hızlı işlemler, Benim Masam, karalama, bildirimler, eksik veri uyarıları → **Masaüstü** üzerinde.

## Uygulama durumu (kod)

- **Faz 0:** Bu dosya + `TASKLOG` kaydı.  
- **Faz 1–3 (Micro):** `/masaustu` — bugün özeti, hızlı işlemler, Benim Masam sekmeleri, ay eksik PG listesi, bildirim **Okundu**, karalama (localStorage), widget sürükleme (SortableJS) + widget gizleme. `/bireysel/karne` — yıl özeti şeridi, zaman çizgisi, PG ısı hücreleri, satır detay modal + mini sparkline.

## Sonraki adımlar (ürün)

- Karne PDF/Excel dışa aktarım.  
- Scratchpad / widget düzenini isteğe bağlı sunucu tarafında saklama (model).
