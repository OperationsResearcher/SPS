# Kart Verisi — Tespit Edilen Tutarsızlıklar

> Kaynak: 2026-07-20 kart açıklaması zenginleştirme çalışması sırasında yapılan
> kod incelemesi (`services/k_radar_service.py`, `micro/modules/k_radar/*`).
> Bulgular kart açıklamalarının **"Sınır:"** bölümlerine şeffaflık gereği yazıldı
> — kullanıcı yanılmasın diye. Ancak bunlar **düzeltilmesi gereken gerçek
> sorunlardır**; açıklama yazmak çözüm değil, geçici dürüstlüktür.

Öncelik sırası: **G (güvenlik) > D (doğruluk) > T (tutarlılık) > İ (isimlendirme)**

---

## D0 — "Azalması iyi" göstergeler rapor katmanında TERS hesaplanıyor ⚠️ EN KRİTİK

**Dosya:** `micro/modules/k_rapor/routes.py` satır **991**, **1901**, **2161**

Bu üç yerde şu koşul var:

```python
if kpi.direction == "lower_is_better":
```

**Ama veritabanında böyle bir değer yok.** Ölçüldü (2026-07-20):

| `direction` değeri | Kayıt |
|---|---|
| `Increasing` | 956 |
| `Decreasing` | **438** |
| `lower_is_better` | **0** |

Koşul hiçbir zaman doğru olmuyor. Sonuç: **438 "azalması iyi" göstergenin
tamamı, rapor katmanında artması iyiymiş gibi hesaplanıyor.**

Somut etki: Hedefi 5 olan bir hata oranı 2 ölçüldüğünde başarı `2/5 = %40`
görünüyor; doğrusu `5/2 = %100` (tavanla %100) olmalıydı. Yani **iyi performans
kötü raporlanıyor.**

Etkilenen kartlar: `k_rapor_pg_dagilim` (üç kart da), `k_rapor_uyari`
(kritik PG listesi), `k_rapor_kurum_karsilastirma` (iki kart).

Skor motoru (`score_engine_service.compute_pg_score`) DOĞRU değeri kullanıyor
(`"Decreasing"`). Bu yüzden **aynı gösterge Kurumsal sekmesinde farklı, PG
Dağılım sekmesinde farklı yüzde gösteriyor** — kullanıcının fark ettiği ama
nedenini bilemediği tutarsızlık büyük olasılıkla budur.

**Çözüm yönü:** Üç satırdaki `"lower_is_better"` → `"Decreasing"`. Daha iyisi:
skor motorundaki `compute_pg_score` bu endpoint'lerde de kullanılmalı — inline
formül tekrarı bu hatanın kaynağı. Düzeltme öncesi/sonrası birkaç göstergenin
yüzdesi elle doğrulanmalı.

---

## G1 — KPR risk kartı yetki kapsamı uygulamıyor

**Dosya:** `services/k_radar_service.py` (`get_kpr_extended_data`, risk bloğu)

`RiskHeatmapItem` tablosu `project_id` taşımadığı için proje kapsamı (scope)
filtresi uygulanamıyor. Sonuç: yalnızca belirli projelere yetkili bir kullanıcı,
kartta **kurum genelindeki** risk sayısını ve ortalama RPN'i görüyor.

Kodda bu durum yorumla not edilmiş ama çözülmemiş.

**Çözüm yönü:** `RiskHeatmapItem`'a `project_id` (nullable) eklenip scope
filtresine dahil edilmeli. Geçiş döneminde `project_id IS NULL` kayıtlar yalnız
kurum yöneticisine gösterilebilir.

---

## D1 — Değer zinciri "eşlenen süreç" boşken maksimum gösteriyor

**Dosya:** `services/k_radar_service.py` (`get_kp_extended_data`, deger_zinciri)

```
"mapped_process_count": mapped_process_count if mapped_process_count else int(process_count or 0)
```

Hiçbir faaliyet bir sürece bağlanmamışsa (`mapped=0`), kart **sıfır yerine
toplam aktif süreç sayısını** yazıyor. Kullanıcı "tüm süreçler eşlenmiş" sanıyor;
gerçek tam tersi.

**Çözüm yönü:** Fallback kaldırılmalı; 0 dürüst değerdir. Boş durumda kart
"henüz eşleme yapılmamış" mesajı göstermeli.

---

## D2 — Trend, önceki dönem verisi yokken yapay yön üretiyor

**Dosya:** `services/k_radar_service.py` (`trend_meta` bloğu)

Önceki 30 günde veri yoksa `previous_period_avg = 0.0` kabul ediliyor. Sonuç:
ilk kez veri girildiğinde delta yapay olarak büyük pozitif çıkıyor ve kart
**"iyileşiyor"** yazıyor. Tersine, bu ay veri girilmediyse `current=0` olup
**"düşüyor"** yazıyor.

Bu, kullanıcıyı en çok yanıltan davranış. Ayrıca **tek bir trend nesnesi**
darbogaz/deger_zinciri/pareto/sla/benchmark/oee/vsm/kapasite kartlarının
hepsine kopyalanıyor — kart-özel trend değil.

**Çözüm yönü:** Bir dönem boşsa trend `None`/"yetersiz veri" dönmeli, sayısal
karşılaştırma yapılmamalı. Kart-özel trend gerekiyorsa her modül kendi
kaynağından hesaplamalı.

---

## T1 — Risk eşiği iki ekranda farklı

| Yer | Eşik |
|-----|------|
| KPR risk özeti (`get_kpr_extended_data`) | `rpn >= 15` → yüksek |
| Risk listesi (`routes_risk.py`) | `rpn >= 16` kritik, `>= 10` yüksek |

Aynı risk iki ekranda farklı sınıflanıyor. RPN 15 olan bir kayıt özet kartında
"yüksek", listede "yüksek değil" görünüyor.

**Çözüm yönü:** Tek bir eşik sabiti tanımlanıp iki yerde de kullanılmalı.

---

## İ1 — Gösterge adları ölçülen şeyle örtüşmüyor

| Kart / alan | Adı ne diyor | Gerçekte ne ölçüyor |
|---|---|---|
| `kpr_gantt.on_time_ratio` | zamanında tamamlanma | yalnızca **tamamlanma** — bitiş/termin karşılaştırması yok |
| `kapasite.utilization_estimate` | kapasite kullanımı | **gösterge kapsama oranı** (KPI'sı olan süreç / tüm süreç) |
| `kaynak_kapasite.resource_load` | yük (yüzde izlenimi) | **sınırsız artabilen indeks**, yüzde değil |
| `oee.availability/performance/quality` | üç ayrı OEE bileşeni | tek performans ortalamasının **+4 / −3 / +0** ofsetli hali |
| `darbogaz.critical_kpi_count` | kritik KPI sayısı | **açık darboğaz kaydı** sayısı (KPI değil) |
| `kpr_cpm` | kritik yol analizi | **öncülü olmayan görevler** listesi; süre/float hesabı yok |

**Çözüm yönü:** Ya isim gerçeğe uydurulmalı, ya ölçüm isme. OEE için gerçek
ölçüm duruş/hız/fire verisi toplanmasını gerektirir — bu bir ürün kararıdır.

---

## D3 — Veri yokken türetilmiş sayı gösterme (yaygın desen)

`get_kp_extended_data` içinde çok sayıda metrik, ilgili tablo boşken **KP
skorundan** sayı türetiyor:

- `olgunluk.avg_level_estimate` — hiç değerlendirme yokken seviye gösteriyor
- `darbogaz.severity_index` — darboğaz kaydı yokken şiddet gösteriyor
- `deger_zinciri.muda_risk` — faaliyet yokken risk gösteriyor
- `pareto.top_impact_slice` — darboğaz yokken dilim gösteriyor
- `sla.breach_risk` — ölçüm yokken ihlal riski gösteriyor
- `oee.*` — veri yokken üç bileşen gösteriyor
- `vsm.flow_efficiency_estimate` — faaliyet yokken verimlilik gösteriyor

Kullanıcı boş bir modülde dolu sayı görüyor ve bunun ölçüme dayandığını sanıyor.

**Çözüm yönü:** Fallback'ler "veri yok" durumuna dönmeli; kartlar `mc-empty`
ile boş durum göstermeli. Bu, K-Radar'ın veri toplama teşvikini de artırır —
şu an boş modül dolu göründüğü için kimse veri girmeye ihtiyaç duymuyor.

---

## Not: 5 dakika önbellek

`get_*` fonksiyonları `@cache.memoize(timeout=300)`. Veri girildikten sonra kart
5 dakikaya kadar eski değeri gösterebiliyor. Bu bir hata değil ama kullanıcı
"kaydettim, değişmedi" diye tekrar kaydetmeye çalışıyor. Açıklamalara not
düşüldü; ayrıca veri girişi sonrası ilgili cache anahtarının
temizlenmesi düşünülebilir.
