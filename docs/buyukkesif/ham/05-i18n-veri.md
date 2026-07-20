# HAM BULGU — i18n ve Veri/Model Tutarlılığı

> Kaynak: paralel i18n + veri akışı uzmanı · 3600 msgid, 170 tablo, 16 migration
> Tarih: 2026-07-21 · **D1/D2 ana oturumda DB'den yeniden doğrulandı**

---

## I1 — TR onarımı DOĞRU ve TAM ✅ (doğrulandı, bilgi)

Bu oturumda yapılan Türkçe çeviri onarımı teyit edildi:

| Kontrol | Sonuç |
|---|---|
| Toplam msgid | 3600 |
| `msgstr != msgid` olan | **0** |
| fuzzy | **0** |
| Kalan 18 dolu msgstr | hepsi `msgstr == msgid` (zararsız kimlik kaydı) |
| Eski bozukluğun imzası (`"Kurumlar" → "Kurum Paneli"`) | **tamamen yok** |

`.mo` dosyası `.po` ile senkron (02:13 vs 02:14).

---

## I2 — EN dosyasında AYNI kayma bozukluğu HÂLÂ DURUYOR · KRİTİK

Onarım yalnız TR'ye uygulandı. EN'de **45 fuzzy kayıt** var, msgid ile msgstr semantik
olarak **alakasız**:

```
'Dönem mühürlenirken hata oluştu.' → 'An error occurred while uploading the logo.'
'Mühür açma gerekçesi zorunludur.' → 'Process and level are required.'
'Mühür açılırken hata oluştu.'     → 'An error occurred while closing the year.'
'Demo Talepleri'                   → 'WO Strategies'
'Kurulum İçe Aktarma'              → 'Bulk Import'
'Raporlar'                         → 'A3 Reports'
'Tomofil'                          → 'Profile'          ← KURUM ADI!
'Tom1' / 'Tom2' / 'Tom3'           → 'TOTAL'  (üçü de)
'Yönetim Paketi'                   → 'Management Panel'
```

**Şu an görünmüyor** çünkü Babel fuzzy kayıtları `.mo`'ya derlemiyor
(EN `.po` 3600 → `.mo` 3525; fark tam 45 + 30 boş). **Bu bir şans eseri koruma.**

> Biri `pybabel compile --use-fuzzy` çalıştırırsa **anında yanlış İngilizce metin yayına çıkar**.

**Öneri:** 45 kaydın msgstr'sini boşalt (fuzzy silme değil, **değer silme**), sonra elle çevir.
`--use-fuzzy` bayrağını hiçbir build script'inde kullanma.

---

## I3 — EN'de placeholder uyumsuzluğu · YÜKSEK

```
msgid "hedef: %(v)s %(u)s"  →  msgstr "Target: %(v)s"     ← %(u)s KAYIP
msgid "<b>1. Yönetişim:</b> ... %(n)s ..."  →  msgstr "..." ← %(n)s KAYIP
```

Eksik placeholder Python'da `KeyError` **vermez** — çökme yok, ama **birim bilgisi kayboluyor**:
"Target: 85" yazar, "Target: 85 %" değil. Ters yön (msgstr'de fazla) olsaydı çökerdi — o durum yok.

**Öneri:** I2 ile birlikte düzelt + CI'ya placeholder lint ekle (5 satırlık regex kontrolü).

---

## I4 — EN'de 82 msgstr çelişkili şekilde birden çok msgid'e bağlı · ORTA

82 msgstr, 170 msgid tarafından paylaşılıyor. Çoğu zararsız eşanlam
(`Planlandı`/`Planlanan`/`Planlananlar` → `Planned`). Ama bazıları **anlam kaybı**:

| msgid'ler | Ortak msgstr | Sorun |
|---|---|---|
| `Yetkiniz yok.` + `Süreç silme yetkiniz yok.` | `...delete a Process.` | Genel hata yanlış bağlamda |
| `Tomofil` + `Profil` | `Profile` | **Kurum adı** çevriliyor |
| `Tom1`,`Tom2`,`Tom3` | `TOTAL` | Kurum adları |
| `Performans %` + `Performans` | `Performance` | **% birimi kayıp** |
| `Gerçekleşen` + `Hedef vs Gerçekleşen` | `Actual` | |
| `Mühür Geçmişi` + `Tarama Geçmişi` | `Scan History` | |
| `Yönetim Paketi` + `Yönetim Paneli` | `Management Panel` | |

> `Tomofil`/`Tom1-3` gibi **özel isimler** zaten `_()` ile sarılmamalıydı — kaynağı bul, wrap'i kaldır.

---

## I5 — 3009 farklı Türkçe metin `_()` ile SARILMAMIŞ · YÜKSEK

3009 farklı dize / 4015 geçiş. En sıkları:

| Geçiş | Metin | Örnek dosya |
|---|---|---|
| 45 | `Tamamlandı` | `routes.py` |
| 36 | `İptal` | `kurum_overview.py` |
| 27 | `Süreç` | `routes.py` |
| 21 | `Aylık` | `routes.py` |
| 20 | `Yükleniyor…` | `index.html` |
| 16 | `Süreç Yönetimi` | `ayarlar.html` |
| 15 | `Proje Yönetimi` | **`constants.py`** |
| 12 | `Bu veriye erişim yetkiniz yok` | `process_performance_service.py` |
| 9 | `Kurum Yönetimi` | **`constants.py`** |

~%20-30'u log mesajı/iç sabit (sarılmamalı, doğru). Geri kalanı gerçek UI sızıntısı.

> `constants.py` içindekiler **menüde doğrudan görünür** — en yüksek etkili grup.

**Öncelik:** (1) `constants.py` modül/menü adları → (2) şablon buton/başlıkları → (3) servis hata mesajları.

---

## I6 — JS i18n mekanizması VAR ama benimsenmesi yarım: 36/88 dosya · YÜKSEK

> ❗ **ANA OTURUM DÜZELTMESİ:** Uzman *"mekanizma hiç yok"* dedi — **yanlış**.
> `base.html:26-31`'de **`window.t()` yardımcısı ve `window._I18N` sözlüğü MEVCUT**
> (`js_i18n_map()` ile sunucudan besleniyor) ve **88 JS dosyasının 36'sında kullanılıyor**.
>
> Gerçek sorun: **benimsenme yarım kalmış** — 52 dosya hâlâ sabit Türkçe metin taşıyor.
> Bu, "sıfırdan altyapı kurulacak" ile "mevcut altyapı yaygınlaştırılacak" arasındaki fark;
> ikincisi çok daha ucuz.

En sık geçenler: `"Yükleniyor…"` (51) · `'Uyarı'` (48) · `"İptal"` (45) ·
`"Sunucu hatası: "` (41) · `'Başarılı'` (35) · `"Bağlantı hatası."` (25)

**SweetAlert2 bildirimlerinin tamamı** İngilizce arayüzde Türkçe çıkar.

> i18n devri (*"statik UI katmanı TAM, 4742 msgid"*) **yalnız sunucu tarafını kapsıyor** —
> JS katmanı hiç ele alınmamış.

**Öneri:** `base.html`'e sunucudan üretilen `window.I18N` sözlüğü + `window.t(key)` yardımcısı
(KURALLAR §3'e uygun: `data-*` veya tek `<script type="application/json">` bloğu).
**En sık 50 dizeyle başla — 3150'nin ~%40'ını kapsar.**

*(Not: F13'te tespit edilen `topbar_year.js` sorunu bu daha büyük eksiğin bir örneği.)*

---

## I7 — Arşiv JS'de mojibake · DÜŞÜK

`static/js/admin_panel.js` → `'Baþarılı'` (3 geçiş). Çift kodlama artığı.
Bu dosya **legacy** `static/js/` altında; aktif klasörde (`ui/static/platform/js/`) mojibake **0**.
Legacy erirken beraber gider.

---

## D1 — `process_kpis`'te DÖRT çakışan "yöntem" kolonu, ikisi ölü ✅ ANA OTURUMDA DOĞRULANDI · KRİTİK

```
calculation_method      : AVG=2389, SUM=10                                   ← kod, DOLU
data_collection_method  : Ortalama=1747, Toplama=493, Son Değer=124, AVG=35  ← Türkçe + KİRLİ
target_method           : NULL=1955, DH=193, HKY=179, SH=69, '-'=2, RG=1     ← ayrı kavram
target_setting_method   : NULL=2399  (2399/2399)                             ← TAMAMEN ÖLÜ
```

Bu oturumda göç sırasında yakalanan `calculation_method` / `data_collection_method` ikiliği
**tek örnek değil — dörtlü**. Üstelik `data_collection_method` içinde **35 satır Türkçe yerine
`AVG` kodu taşıyor** — kolon zaten kirlenmiş, iki dil karışmış.

**Etki:** Bir göçte/raporda hangi kolonun okunduğuna göre farklı sonuç; 35 satır her iki tarafta
da "AVG" olduğu için **kirlilik sessiz kalıyor**.

---

## D2 — `kpi_year_configs.calculation_method` TEK kolonda iki dil ✅ DOĞRULANDI · KRİTİK

```
Ortalama    1050
AVG           35     ← aynı anlam, farklı değer
(NULL)        24
Son Değer      5
```

D1'deki ikilik burada **tek kolonun içine göçmüş**.

> **D1'den daha tehlikeli** çünkü tek kolon içinde — kimse iki kolon olduğunu fark edip kontrol etmez.
> `WHERE calculation_method = 'AVG'` yazan kod 35 satır bulur, **1050'yi kaçırır**.

İki tarafta da 35 sayısının çıkması, D1'deki kirlilikle **aynı göç olayından** geldiğini gösteriyor.

---

## D3 — Üç ölü model + `IndividualKpiYearConfig` yazılıp okunmuyor · ORTA

| Model | Tablo | Kod ref | DB satır | Durum |
|---|---|---|---|---|
| `UserYearAssignment` | `user_year_assignments` | **0** | **0** | Tam ölü |
| `TenantYear` | *(tablo yok)* | **0** | tablo YOK | Model var, tablo hiç oluşmamış |
| `StrategyProcessMatrix` | `strategy_process_matrix` | 15 | **0** | Kod var, veri yok |
| `ReplanTrigger` | `replan_triggers` | 10 | **0** | Kod var, veri yok |
| `IndividualKpiYearConfig` | `individual_kpi_year_configs` | 5 | **525** | **Yazılıyor, okunmuyor** |

`IndividualKpiYearConfig`'in `calculation_method` ve `target_method` kolonlarının **ikisi de
525/525 NULL** — kayıtlar içi boş kabuk. *(Hasar tespitindeki S7 bulgusu hâlâ geçerli.)*

---

## D4 — `SwotAnalysis` İKİ dosyada, aynı `__tablename__`, FARKLI şema · YÜKSEK

`app/models/strategy.py:9` ve `app/models/swot.py:7` — 131 tablo adı tarandı, **tek çakışma bu**.

```
strategy.py : id, tenant_id, category(String32), content(Text), created_at, is_active
swot.py     : id, plan_year_id(FK), tenant_id, source_swot_id(FK self),
              strengths/weaknesses/opportunities/threats (Text, JSON dizisi)
```

`app/models/__init__.py:79` **swot.py sürümünü** import ediyor (kazanan bu).
`strategy.py` sürümü DB ile uyuşmuyor.

**Risk:** Birisi `from app.models.strategy import SwotAnalysis` yazdığı gün yanlış şemayla
sorgu atar → `category` kolonu DB'de olmadığı için `UndefinedColumn`.

---

## D5 — Migration zinciri TEMİZ ✅ (doğrulandı)

16 dosya, **16 farklı revision id** — tekrar yok. Bu oturumdaki `b2c3d4e5f6a7` çakışması onarılmış.
Zincir tek parça, kopuk yok, **tek head: `yb20c5e1a8d3`**.

> `migrations/versions/_disabled/` klasörü zincire dahil değil — kasıtlıysa sorun yok.

---

## D6 — Model ↔ DB uyumu neredeyse mükemmel: 4 sarkan kolon · DÜŞÜK

- Modelde olup DB'de olmayan kolon: **0**
- Modelde olup DB'de olmayan tablo: **0**
- DB'de olup **modelde olmayan**: **4**

```
individual_performance_indicators.is_included
process_maturity.plan_year_id
strategy_process_matrix.plan_year_id
strategy_map_link.plan_year_id
```

Dördü de bu oturumdaki yıl bazlı migration'ların eklediği ama **modele yansıtılmamış** kolonlar.
`is_included` özellikle kritik: ORM üzerinden yazılamaz/okunamaz, yalnız ham SQL görür.

---

## D7 — DB'de modelsiz 39 tablo: 30'u `mock_*` çöp · DÜŞÜK

170 tablonun 39'unun modeli yok. 9'u meşru (association tabloları, `db.Table` ile tanımlı).
Kalan **30'u `mock_*`**: `mock_daovote`, `mock_metaversedepartment`, `mock_doomsdayscenario`…

Fonksiyonel risk yok ama `pg_dump` her seferinde taşıyor ve §8.6 kıyas çıktısını gürültülendiriyor.

---

## En acil üç iş (bu bölümden)

1. **D2** — `kpi_year_configs` içindeki 35 `AVG` satırı (tek kolonda iki dil, sessiz veri hatası)
2. **I2** — EN `.po`'daki 45 kaymış fuzzy kayıt (`--use-fuzzy` bir gün çalışırsa anında yayına çıkar)
3. **D4** — `SwotAnalysis` çifte tanımı
