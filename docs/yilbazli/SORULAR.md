# AÇIK SORULAR VE İSTEKLER

> **Bu belge kapanmadı — birikiyor.** Kullanıcının ek soruları ve istekleri
> buraya eklenir. Hasar tespiti bitmeden uygulama planı çıkarılmaz.

---

## A. Kullanıcının belirttiği hedef ilke (2026-07-20)

> "Tüm sistem yıl bazlı olmalı. SP'nin her aşaması, stratejiler, süreçler,
> projeler dahil. Süreçlerin ve projelerin içindeki tüm bilgiler, PG'ler, bağlar,
> PG ile ilgili tüm bilgiler — her şey ama her şey yıl bazlı olmalı. Kullanıcı
> hangi yılda çalışmak istediğini seçtiğinde o yıla göre gelmeli her şey,
> tüm K-Radar vs ama her şey."

**Alınmış kararlar:**

| # | Karar | Durum |
|---|---|---|
| K1 | Süreç ekranından hedef değişince **aktif yılın `KpiYearConfig`'ine yaz**; geçmiş yıl dokunulmaz, kapalı yıl reddedilir | Onaylandı, **uygulanmadı** |
| K2 | KMF veri onarımı: önce rapor, sonra karar | Rapor alındı → snapshot'lar güvenilmez çıktı, onarım **askıda** |
| K3 | Uygulama **başlamayacak**, hasar tespiti sürüyor | Aktif |
| K4 | Yayın'a dokunulmayacak, tüm iş yerelde | Aktif |

---

## B. Claude'un cevap bekleyen soruları

### S1 — Üretilmiş test verisi ✅ ÖLÇÜLDÜ, karar bekliyor
Kapsam çıkarıldı → [`OLCUMLER.md`](OLCUMLER.md) §4.

- 🔴 Tenant 27/58/60/61 (dört Tomofil klonu): `kpi_data`'nın **%98,6'sı**
  üretilmiş + 22.712 gelecek tarihli satır
- 🟠 **Tenant 16 (KMF — gerçek müşteri)**: 497 satırın **202'si** üretilmiş
  (%40,6), 189 ay-tutarsız, 38 gelecek tarihli
- 🟢 Tenant 1, 28: temiz

Ayırt edici imza mevcut: `created_at = 2026-03-26 19:08:23` +
`period_month ≠ data_date` ayı → temizlik teknik olarak mümkün.

**Kalan soru:** KMF'deki 202 satır temizlensin mi? Bu ayrı bir iş kalemi;
gerçek müşteri verisine dokunmak kullanıcı onayı gerektirir.

### S2 — Faz önceliklendirmesi (açık)
`HASAR-TESPITI.md` §6'daki 4 fazlık öneri onaylanmadı.

**Soru:** Hangi fazdan başlanacak? Özellikle Faz 4 (model değişikliği + migration)
kapsama dahil mi?

### S3 — Proje modülü ✅ CEVAPLANDI, yeni karar gerekiyor
Detay → [`HASAR-TESPITI-2.md`](HASAR-TESPITI-2.md) §10.

**Kaldırma gerekçesi mimari karar değil, hotfix:** commit `0bb0ad64` (2026-06-04).
`Project(...)` constructor'ına `plan_year_id` geçiliyordu ama `project` tablosunda
kolon yok → TypeError → 500. Sprint 53'ten (`973256c7`) kalmış ölü referans.

**Asıl bulgu — iki ayrı proje sistemi var:**

| Model | Tablo | Yıl | Kullanım |
|---|---|---|---|
| `portfolio_project.py::Project` | `project` | ❌ yok | **Aktif** (proje modülü) |
| `project.py::PlanProject` | `plan_projects` | ✅ `plan_year_id` + `source_project_id` | SP tarafı |

**Yeni soru:** "Projeler yıl bazlı olmalı" hangisini kastediyor — portföy
`Project`'ine yıl eklemek mi, iki sistemi birleştirmek mi?

### S4 — Çift mekanizma (açık)
Yıl bazlılık iki farklı yolla yapılıyor: full-clone (`plan_year_id` varlıkta) ve
override tabloları (`*_year_configs`). Strateji katmanında **ikisi de** var.

**Soru:** Hedef mimari hangisi olacak? Karışık kalırsa çakışma riski sürer.

### S5 — `plan_year_enabled` flag'i ✅ CEVAPLANDI (K5)
Bu flag false olan tenant'ta **hiçbir yıl filtresi çalışmıyor**; sistem tamamen
yıl-bağımsız.

**Soru:** "Her şey yıl bazlı olmalı" ilkesi flag'in kaldırılması anlamına mı
geliyor — yani tüm kurumlar için zorunlu mu? Yoksa flag korunacak mı?

---

## C. Kullanıcıdan beklenen ek girdiler

Kullanıcı "daha başka sorularım var, hepsini toplayalım" dedi (2026-07-20).
Gelen her yeni soru/istek buraya eklenecek.

| # | İstek | Tarih | Durum |
|---|---|---|---|
| — | _(bekleniyor)_ | | |

---

## D. 2. tur denetimden doğan yeni sorular

### S6 — Arka plan görevlerinde yıl kaynağı (yeni)
Gece 02:00 erken uyarı görevinde **session yok** → `get_view_year()` kullanılamaz.
Şu an `today.year`'a sabitlenmiş, yılsız hedefle karşılaştırıyor
(`early_warning_service.py:82,90`). Dashboard API'si ise plan yılına bakıyor —
**iki uç çelişik**.

**Soru:** Zamanlayıcılar hangi yılı esas alsın — tenant'ın aktif PlanYear'ı mı,
takvim yılı mı?

### S7 — `IndividualKpiYearConfig` ölü model (yeni)
Model var, seed/clone ediliyor, **hiç okunmuyor**. Bireysel ekranların hepsi
yılsız `IndividualPerformanceIndicator.target_value` okuyor.

**Soru:** Bireysel katmana da yıl bazlı hedef okuma yolu yazılsın mı, yoksa
model kaldırılsın mı?

### S8 — Frontend yıl taşıma stratejisi (yeni)
K-Radar'ın ~37 API çağrısının **hiçbiri** `?year` göndermiyor. Sadece K-Rapor
düzgün taşıyor (25 çağrının 21'i).

**İki seçenek:**
- (a) 40+ fetch çağrısını tek tek düzelt — geniş, kırılgan
- (b) **Backend'de `?year` yokken `session["sp_active_year"]`'a düş** — tek nokta,
  çok daha güvenli (denetimin önerisi)

**Soru:** Hangisi? (b) önerilir.

### S9 — Seed açığı sistemik (yeni)
Flag açık 3 tenant'ın **2'sinde** (KMF #16, Eskişehir #28) hedefli
`kpi_year_configs` satırı **sıfır**. Sadece Tomofil #27 düzgün seed'lenmiş.

**Soru:** Yeni plan yılı açılışında seed'in garanti çalışması için
`vm_apply_plan_years.py` gibi ham INSERT yolları kapatılsın mı?

---

## E. KULLANICI KARARLARI — 2026-07-20 (BAĞLAYICI)

> Kullanıcının doğrudan ifadesi. Bu kararlar önceki soruların bir kısmını kapatır,
> yeni gereksinimler getirir.

### K5 — Yıl bazlılık ZORUNLU, istisnasız
> "Tüm kullanıcılarımız artık yıl bazlı olmalı."

**Sonuç:** `plan_year_enabled` flag'i **kalkar**. Yıl bazlılık opsiyonel özellik
değil, sistemin temel çalışma biçimi. → **S5 kapandı.**

Etki: Şu an 12 kurumun **9'unda flag kapalı** (bkz `HASAR-TESPITI-2.md` §11).
Hepsi yıl bazlı hale gelecek → veri göçü gerekir.

### K6 — Sistem başlangıcı 2020
> "Sistem 2020 yılından itibaren olmalı."

Plan yılı ekseni **2020'de başlar**. Her kurum için 2020'den itibaren plan yılı
zinciri kurulmalı.

### K7 — Yıl yaşam döngüsü: veri girişi → kapatma (mühür)
> "Kurum 2022 verilerini girer (SP, vizyon, stratejiler, süreçler, PG, PGV),
> işi biter. Kurum üst yönetimi artık bu plan yılını **kapatabilmeli**."

Bir plan yılı, o yıla ait **tüm** girdileri kapsar: SP verileri (vizyon, strateji),
süreç tanımları, PG'ler, PG verileri (PGV).

### K8 — Kapalı yıl MUTLAK korumalı
> "Kapanmış bir yıla **asla** bir veri girişi, düzenlemesi, silmesi olmamalı."

Mutlak kural. İstisna yok.

### K9 — Mühür açma yetkisi: kurum üst yönetimi
> "Çok özel bir durum olursa, major bir eksiklik yakalanırsa, kurum üst yönetimi
> **mührü açıp** plan yılını tekrar aktif hale getirebilmeli."

Açma yolu **var olmalı**, ama yetki kurum üst yönetiminde.

---

## F. K7-K9'un DENETİM SONUCU — mühür yok

> Tam denetim: [`HASAR-TESPITI-2.md`](HASAR-TESPITI-2.md) §13

Kullanıcı "belki sorular değişir, bir kontrol et" dedi. Kontrol edildi —
**gereksinimlerin hiçbiri karşılanmıyor:**

| Gereksinim | Durum |
|---|---|
| K7 — Yıl kapatma | ⚠️ Var (`routes_plan_year.py:176`) ama sadece `status` string'i yazıyor |
| K8 — Kapalı yıl korumalı | ❌ **YOK** — kapalı yıla serbestçe veri girilip silinebiliyor |
| K9 — Üst yönetim mührü açabilmeli | ❌ **YOK** — açma route'u hiç yok, DB müdahalesi şart |

**En kötü kombinasyon:** Sistem mührü hem uygulamıyor, hem de yanlışlıkla
kapatılan bir yılı kurtarma yolu bırakmıyor.

Koruma sadece 2 endpoint'te var (ikisi de KPI hedef config'i). **Veri giriş
yollarının hiçbirinde yok** — `kpi-data/add`, `bulk-import`, `update`, `delete`,
harici API, bireysel veri girişi, SP yazma, proje CRUD: hepsi korumasız.

---

## G. YENİ SORULAR (K5-K9'dan doğan)

### S10 — `plan_year_enabled` kaldırma göçü
K5 gereği flag kalkacak. Şu an 9 kurumda kapalı, 2'sinde (KMF #16, Eskişehir #28)
plan yılı var ama **hedefli config sıfır**.

**Soru:** Flag kalkınca bu kurumlar ne olacak — 2020'den itibaren plan yılları
otomatik üretilip mevcut veriler yıllara mı dağıtılacak? Dağıtım kuralı ne
(`kpi_data.year` zaten var, ondan mı türetilecek)?

### S11 — Mevcut yılsız verinin 2020 eksenine oturtulması
K6 gereği sistem 2020'de başlıyor. Ama mevcut `ProcessKpi.target_value` yılsız —
hangi yıla ait olduğu bilinmiyor.

**Soru:** Mevcut yılsız hedefler hangi yıla yazılacak? Öneri: aktif yıla kopyala,
geçmiş yıllar `kpi_data` snapshot'ından türetilsin — **ama** KMF örneğinde
snapshot'ların bir kısmı üretilmiş veri çıktı (bkz `OLCUMLER.md` §4).

### S12 — Mühür kapsamı: neler kilitlenecek?
K8 "asla veri girişi/düzenlemesi/silmesi olmamalı" diyor.

**Soru:** Kilit hangi varlıkları kapsayacak?
- (a) Sadece o yıla ait veri (`KpiData.year`, `ActivityTrack.year`)
- (b) + O yıla ait tanımlar (PG hedefi, süreç, strateji, SWOT…)
- (c) + Yıl-agnostik varlıklar da (Proje, Blue Ocean, VRIO — bunların yılı yok)

(c) şu an teknik olarak imkânsız — o varlıkların yıl kolonu yok.

### S13 — Mühür açma: denetim izi
K9 açma yetkisi veriyor. Bu geri alınamaz bir güvenlik kapısı.

**Soru:** Açma işlemi loglanacak mı — kim, ne zaman, **neden** açtı? Yeniden
kapatma zorunlu mu, yoksa açık kalabilir mi? Öneri: gerekçe alanı zorunlu +
denetim tablosu.

### S14 — Kapatma route'unda CSRF muafiyeti
`routes_plan_year.py:172` `@csrf.exempt`. Kapatma tek yönlü ve (şu an) geri
alınamaz bir işlem.

**Soru:** CSRF muafiyeti kaldırılsın mı? (Öneri: evet.)

### S15 — Kilit nerede uygulanacak — mimari
Denetimin önerisi: endpoint başına elle `if` eklemek **tekrar kaçırılmaya açık**
(bugün 15+ yazma yolu korumasız).

**Öneri:**
1. `date_sovereign.resolve_plan_year_for_date` kapalı yıl sinyali versin
2. Ortak **`plan_year_writable_required`** dekoratörü tüm yazma route'larını sarsın
3. Ek güvenlik: DB seviyesinde trigger

**Soru:** Bu yaklaşım onaylanıyor mu?

---

## H. KULLANICI CEVAPLARI — 2026-07-20 (TÜM SORULAR KAPANDI)

> Kullanıcı S1-S15'in tamamını cevapladı. Bu bölüm bağlayıcıdır.

| Soru | Karar |
|---|---|
| **S1** | ✅ **Yerelde silindi**, Yayın'a dokunulmadı. Gerekçe: iş bitince yerelden Yayın'a tüm DB taşınacak — ayrı iş çıkmasın |
| **S2** | ✅ Model değişikliği + migration **dahil**. Uyarı: yeni değişiklik istekleri gelecek, migration **genişleyebilir** |
| **S3** | ✅ **İki proje sistemi birleştirilecek** (portföy `Project` + SP `PlanProject`) |
| **S4** | ✅ Doğru mimariyi Claude belirleyecek. Kullanıcı yönü: **tek yerde yıl bazlı yönetim** |
| **S5** | ✅ Tüm kurumlar için **zorunlu**. Yeni kurum 2026'dan başlar; geçmiş yıla veri girmek isteyen **yılı değiştirmek zorunda** |
| **S6** | ✅ Arka plan görevleri **tenant'ın aktif yılını** kullanacak |
| **S7** | ✅ Bireysel de yıl bazlı olacak — kişinin hedefleri yıllara göre değişebilir |
| **S8** | ✅ **Güvenli yol**: backend'de `?year` yokken session'a düş (40+ fetch düzeltmek yerine) |
| **S9** | ✅ Karar Claude'a bırakıldı — seed garantisi sağlanacak |
| **S10** | ✅ Plan yılları **otomatik üretilecek**, mevcut veri `kpi_data.year`'a göre yıllara dağıtılacak |
| **S11** | ✅ **Tek hedef varsa tüm yıllara yazılır** |
| **S12** | ✅ **(c)** — yıl-agnostik varlıkların verisi **her yıla yazılır** (teknik engel böyle çözülür) |
| **S13** | ✅ **Gerekçe alanı zorunlu + denetim tablosu** |
| **S14** | ✅ CSRF muafiyeti **kaldırılacak** |
| **S15** | ✅ Önerilen mimari onaylandı: `date_sovereign` sinyali + `plan_year_writable_required` dekoratörü |

### S1 uygulama kaydı (tamamlandı)

**Yerelde silindi** — 2026-07-20:

| | |
|---|---|
| Silinen | `kpi_data` **202** satır + `kpi_data_audits` **8** satır |
| İmza | `created_at = 2026-03-26 19:08:23` (202/202 tam eşleşme) |
| KMF toplam | 587 → **385** |
| Yedek | `backups/yerel_temizlik/kmf_uretilmis_kpi_data_2026-07-20_1558.json` + `kmf_uretilmis_audits.json` |

**Doğrulama:** kalan şüpheli **0** · ay-tutarsızlık **189 → 0** · gelecek tarihli 38 → **5**

Kalan 5 satır **meşru**: hepsi `2026-12-31` tarihli yıllık dönem kaydı
(`period_month = None`), farklı zamanlarda girilmiş gerçek kullanıcı verisi.
Yıllık PG'de dönem sonu tarihi normaldir — dokunulmadı.

**Yayın'a dokunulmadı.** Yayın'daki 202 satır duruyor; iş bitince yerelden
Yayın'a tam DB taşıması yapılacağı için ayrıca temizlenmeyecek.

### S3/S4'ten doğan tasarım görevi (Claude'a)

Kullanıcı yönü net: **"tek bir yerde yıl bazlı sistemi yönetmek"**.
Bugün iki mekanizma bir arada (full-clone `plan_year_id` + override `*_year_configs`)
ve iki proje sistemi var. Doğru hedef mimariyi Claude önerecek, kullanıcı onaylayacak.

Bu, uygulama planının **ilk maddesi**: mimari karar belgesi.

---

## I. TASARIM KARARLARI — 2026-07-20 (Claude'un soruları, kullanıcı cevapları)

> Mimari belgeden önce netleştirilen 6 nokta. Tümü onaylandı.

### T1 — Gecikmeli veri: TOLERANS YOK
Kapalı yıla ait unutulmuş veri için **tolerans süresi yok**. Tek yol: kurum üst
yönetimi **mührü açar**, veri girilir, yıl tekrar kapatılır.

K8'in mutlaklığı korunur. Denetim izi (T13) kim/ne zaman/neden sorusunu cevaplar.

### T2 — Yıl devri: HER ŞEY kopyalanır
Yeni yıl açılınca **hedefler dahil her şey** önceki yıldan kopyalanır — süreçler,
PG'ler, stratejiler, hedef değerleri, ağırlıklar.

Gerekirse kullanıcı değiştirir. Sıfırdan yazmaz.

### T3 — Yıl-agnostik varlıklar: gerçek `plan_year_id` alacak
S12'nin uygulaması: Blue Ocean, VRIO, Süreç-Strateji bağı vb. varlıklara **gerçek
`plan_year_id` verilir**.

- **İlk göçte:** mevcut kayıt **tüm yıllara kopyalanır**
- **Sonrası:** normal yıl bazlı davranır

> Böylece S12 ("her yıla yaz") ile K8 (kapalı yıl korumalı) **çakışmaz** —
> 2026'da yapılan düzenleme kapalı 2024'e sızmaz.

### T4 — Plan yılı başlangıcı: kurumun ilk verisi
Her kurum için plan yılı zinciri, **o kurumun ilk verisinin yılından** başlar.
Sistem geneli 2020'den başlar (K6) ama kuruma boş yıllar üretilmez.

Yeni kurum → 2026'dan başlar (K5).

### T5 — Migration kapsamı: TÜM tenant'lar, klonlar dahil
4 Tomofil klonu (tenant 58/60/61 + 27) migration'a **dahil**.
`kpi_data` 366.806 satırın %98'i bunlarda.

> Kullanıcı: *"hepsini yapalım, gerekirse uzun sürsün"*

Migration performansı değil, **bütünlük** önceliklidir.

### T6 — Uygulama sırası: model → mühür → yıl akışı

| # | Faz | Gerekçe |
|---|---|---|
| 1 | **Model + migration** | Temel; olmadan diğerleri yamalı kalır |
| 2 | **Mühür** (kilit + açma + denetim) | Veri güvenliği |
| 3 | **Yıl akışı** (`get_view_year` yayılımı, 72 hardcoded nokta, frontend) | Kullanıcı doğru veriyi görür |

---

## J. SONRAKİ ADIM

Tüm sorular kapandı (S1-S15 + T1-T6). Sıradaki iş: **mimari karar belgesi**
(`MIMARI-KARAR.md`) — S4'ün cevabı diğer her şeyi belirlediği için önce o yazılır:

- Hedef mekanizma: clone / override / hibrit → **tek yerde yıl yönetimi** (K-S4)
- İki proje sisteminin birleştirilmesi (S3)
- 2020-2026 plan yılı zinciri üretimi + mevcut verinin dağıtımı (S10, S11, T4)
- Mühür mimarisi: `plan_year_writable_required` + `date_sovereign` sinyali +
  denetim tablosu + gerekçe alanı (S13, S15, T1)
- Migration kapsamı ve sırası (S2, T5, T6)

> **Kullanıcı ek istekler bildirecek — migration kapsamı genişleyebilir (S2).**
> Mimari belge, o istekler alındıktan sonra yazılacak.

---

## K. MÜHÜR ARAYÜZÜ — YER KARARI (T7, 2026-07-20)

> Kullanıcı sordu: "Hangi sayfada yapılacağı da önemli. İlk fikrim Yönetici
> Paneli, ama senin fikrine de açığım." → Claude'un önerisi **onaylandı**.

### Mevcut durum — mühürleme bugün nasıl yapılıyor

**Yol:** SP → Dönemler sayfası (`/k-plan/strategy/periods`)

| Katman | Durum | Kaynak |
|---|---|---|
| Buton | ✅ `🔒 Bu Dönemi Kapat` — yalnız `sp_can_manage` rollerine | `sp/donemler.html:70` |
| Onay | ✅ SweetAlert2 uyarısı | `sp_donemler.js:48` |
| API | ✅ `POST .../plan-years/<id>/close` | `sp/routes_plan_year.py:171` |
| Servis | ⚠️ Sadece `status="closed"` + `closed_at` | `plan_year_service.py:297` |
| Denetim | ❌ `actor_id` sadece **log satırına** yazılıyor, tablo yok | `plan_year_service.py:305` |

**Onay metni gerçeği yansıtmıyor** — kullanıcıya iki söz veriliyor, ikisi de tutulmuyor:

| Ekranda yazan | Gerçek |
|---|---|
| "Kapalı dönemler artık düzenlenemez" | ❌ Düzenlenebiliyor (bkz. §13.3) |
| "Bu işlem geri alınamaz" | ⚠️ Doğru ama istenmeyen şekilde — açma yolu yok |

`close_plan_year` docstring'i de aynı yanlışı tekrarlıyor.

### T7 — Karar: Dönemler sayfası kalır, görünür hale getirilir

**Reddedilen alternatif:** Yönetici Paneli (`/exec-dashboard`).
Gerekçe: o sayfanın **her** bileşeni "durum nasıl?" sorusunu cevaplıyor (sağlık
skoru, K-Vektör, trendler, AI özet, uyarı kutucukları) — **izleme** ekranı.
Mühürleme ise dönem **yaşam döngüsü eylemi**. Farklı zihinsel mod.

**Kritik bulgu — asıl sorun sayfa seçimi değildi:**

> **Dönemler sayfası hiçbir menüde yok.** SP menüsünde 17 madde var, Dönemler
> yok. Sidebar'da yok. Yalnızca launcher, çeyreklik değerlendirme ve sihirbazdan
> dolaylı link var. URL de `/periods`.

Kullanıcının mühürlemeyi Yönetici Paneli'ne taşımak istemesinin muhtemel asıl
sebebi bu görünmezlik.

### Uygulanacaklar

| # | İş |
|---|---|
| **A** | Dönemler sayfası **SP menüsüne eklenecek** — ad: "Plan Dönemleri", ikon: takvim/kilit |
| **B** | Mühür işlemleri orada toplanacak: **kapat + aç + gerekçe modalı + denetim geçmişi** (örn. *"2024 — kapatıldı 15.01.2025 Ahmet Y. · açıldı 03.02.2025, gerekçe: …"*) |
| **C** | **Yönetici Paneli'ne durum göstergesi + kısayol**: `🔒 2025 dönemi açık — kapatılmadı [Dönemleri Yönet →]`. Görür ama yönetmez |
| **D** | Sidebar'a ekleme **ertelendi** — İ1 (Kurum Paneli karmaşası) çözülmeden menü kalabalığı artırılmayacak |
| **E** | Onay metni **yeniden yazılacak** — K9 ile açma mümkün olacağı için "geri alınamaz" ifadesi geçersiz; "düzenlenemez" ifadesi ancak kilit gerçekten uygulandığında doğru olacak |
| **F** | `close_plan_year` docstring'i gerçeğe uydurulacak |

**İlke:** Yönetici Paneli **görür**, Dönemler sayfası **yönetir**.
İzleme/eylem ayrımı korunur.

---

## L. SÜREÇ KARNESİ — ÇİFT YIL SEÇİCİ (T8, 2026-07-20)

> Kullanıcı: *"Süreç Karnesinde iki tane yıl var, bunlar ne işe yarıyor?"*
> → Tespit yapıldı, karar verildi.

### Tespit — iki seçici, tek işlev

| | Üstteki (Döküman No altı) | PK04 kartındaki |
|---|---|---|
| id | `#year-select` | `#pg-karne-yil-select` |
| Kaynak | `karne.html:100` | `karne.html:294` |
| Etiket | "Yıl:" | "Yıl" |
| Aria | *"Rapor yılı"* | *"Performans göstergeleri rapor yılı"* |
| Kapsam | **Sayfanın tamamı** | Sadece PG tablosu |
| Yıl listesi | `plan_years_for_karne` — **gerçek plan yılları**, durum işaretli (`✓` kapalı, `●` taslak) | `range(current_year+1, current_year-5)` — **hesaplanmış** |

**Üstteki değişince** (`surec.js:2933`):
1. `POST /plan-years/set-active` → **oturumun aktif yılını** değiştirir (`sp_active_year`)
2. Sürecin o yıldaki klonuna gider (`resolve_for_year`)
3. Karne yeniden yüklenir

**İkisi çift yönlü bağlı:**
- `surec.js:3138` — PK04 değişince `yearSelect.value` da güncelleniyor
- `surec.js:205` `syncPgKarneYilFromBanner()` — üstten PK04'e senkron

### Üç sorun

| # | Sorun |
|---|---|
| **S-1** | **Gereksiz ikilik** — aynı değeri gösteren, birbirini güncelleyen iki kutu. Kullanıcı hangisini kullanacağını bilemiyor |
| **S-2** | **Yıl listeleri farklı üretiliyor** — PK04 plan yıllarını bilmiyor. KMF'de 2020-2026 plan yılı var ama PK04 `2027…2022` gösteriyor: **2020-2021 yok, olmayan 2027 var** |
| **S-3** | Üstteki de `plan_year_enabled` flag'ine bağlı; kapalıysa hesaplanmış listeye düşüyor (`karne.html:108-110`) — **K5 ile bu dal ölecek** |

### T8 — Karar (kullanıcı onayı)

> *"Sadece bir tane olsun, başlığı da **Plan Yılı** olsun, üstteki kalsın,
> o değişince her şey değişsin."*

| # | İş |
|---|---|
| A | **PK04'teki seçici kaldırılacak** (`karne.html:293-298`) — kendi işlevi yok, üsttekinin aynası |
| B | Üstteki kalacak, etiketi **"Plan Yılı"** olacak (`karne.html:99`) |
| C | Senkronizasyon kodu temizlenecek — `surec.js:205` `syncPgKarneYilFromBanner()`, `surec.js:3138` listener |
| D | Yıl listesi **her zaman gerçek plan yıllarından** gelecek; hesaplanmış `range(...)` dalı silinecek (K5 ile flag zaten kalkıyor) |
| E | `.po` güncellenecek — yeni msgid "Plan Yılı" |

**İlke doğrulandı:** Yıl **tek yerden** seçilir, değişince **her şey** ona göre
gelir. Bu, yıl bazlı programın ana ilkesinin karne sayfasındaki karşılığıdır.

> Not: Aynı desen başka sayfalarda da olabilir — çoklu yıl seçici taraması
> uygulama fazında yapılacak.

---

## M. MİMARİ KARARLAR — 2026-07-20 (T9-T13, BAĞLAYICI)

> Uygulama planı yazılmadan önce netleştirilmesi gereken 5 nokta.
> Claude sordu, kullanıcı cevapladı. **S4'ün "doğru mimariyi Claude belirleyecek"
> maddesi bu bölümle kapanır.**

### T9 — Yıl mekanizması: FULL-CLONE tek mekanizma

**Karar:** Her varlık kendi `plan_year_id`'sini taşır. Override tabloları
(`*_year_configs`) **kaldırılır**.

| | |
|---|---|
| Kalan | `plan_year_id` kolonu varlığın kendisinde |
| Kaldırılacak | `kpi_year_configs` (3224) · `strategy_year_configs` (550) · `sub_strategy_year_configs` (1405) · `process_year_configs` (1035) · `individual_kpi_year_configs` (1575) |
| Toplam taşınacak override satırı | **7.789** |

**Gerekçe:**
- T2 (yıl devrinde her şey kopyalanır) ve T3 (agnostik varlıklara gerçek
  `plan_year_id`) zaten bu yöne işaret ediyordu — override ile ikisi de zorlama olurdu
- Mühür **tek kolondan** uygulanır: `plan_year_id` → `plan_years.status`.
  Override'da her tablo için ayrı kilit kontrolü gerekirdi (bugün 15+ yazma
  yolunun korumasız olmasının sebebi tam olarak bu dağınıklık)
- S4'ün sorduğu çakışma riski kökten biter: tek yıl kaynağı kalır

**Bedel (kabul edildi):** Migration ağır. Varlık satır sayısı yıl sayısıyla çarpılır.

### T10 — Proje birleşmesi: `PlanProject` ana model

**Karar:** İki proje sistemi `PlanProject` altında birleşir. Portföy `Project`/`Task`
verisi oraya taşınır, proje modülü `PlanProject` okur.

**Gerekçe:** `PlanProject` zaten `plan_year_id` NOT NULL + `source_project_id`
(yıl devri) taşıyor — yıl bazlı altyapısı hazır. Ters yön seçilse yıl devri
mekanizması sıfırdan yazılacaktı.

**Ölçüm — bu karar sanıldığından çok hafif:**

| Tablo | Satır |
|---|---|
| `project` | **1** |
| `task` | **0** |
| `plan_projects` | 21 |
| `plan_project_tasks` | 63 |

> Veri taşıma pratikte yok. İş, **kod bağlama** işi: `micro/modules/proje/` CRUD'ı
> `PlanProject`'e yönlendirilecek. 2026-06-04'teki `0bb0ad64` hotfix'i
> (`plan_year_id` kaldırma) bu kararla anlamını yitirir.

### T11 — Mühür devreye alma: mevcut kapalı yıllar TASLAĞA çevrilir

**Karar:** Migration sırasında tüm `closed` plan yılları **draft/active** yapılır.
Kurum verisini gözden geçirip hazır olduğunda **kendisi mühürler**.

**Mevcut durum (ölçüm 2026-07-20):**

| Durum | Satır |
|---|---|
| `closed` | **35** |
| `active` | 22 |
| `draft` | 1 |

**Gerekçe:** Bugünkü `closed` etiketi **hiçbir koruma sağlamıyordu** (§13) — kurum
onu bilinçli bir mühür kararı olarak vermedi, sadece bir durum string'iydi. Kilit
gerçek olunca kurum bilinçli karar versin. Aksi halde 35 yıl bir gecede kilitlenir
ve ilk iş mühür açma talebi olur.

**Not:** T1 (tolerans yok) bozulmaz — T1 kilit *yürürlükteyken* geçerli; bu madde
kilidin *ilk devreye alınışını* düzenler, tek seferlik.

### T12 — `kpi_data` bağı: yılın PG kopyasına bağlanır

**Karar:** Migration 366.604 `kpi_data` satırını **yeniden bağlar**. `year=2024`
olan satır, o PG'nin **2024 kopyasının** id'sine işaret eder.

```
ÖNCE                                    SONRA
kpi_data(process_kpi_id=417, year=2024) kpi_data(process_kpi_id=417) → PG 2024 kopyası
kpi_data(process_kpi_id=417, year=2025) kpi_data(process_kpi_id=982) → PG 2025 kopyası
```

**Neden şart:** T9 full-clone dediği için PG'ler yıl başına çoğalıyor. Veri taban
PG'de kalırsa **iki yıl kaynağı** yaşamaya devam eder (`PG.plan_year_id` +
`kpi_data.year`) — T9'un çözmek istediği sorunun aynısı.

**Sonuç:** Yıl **tek kaynaktan** okunur. Mühür `JOIN process_kpis → plan_years.status`
ile tek noktadan işler.

**Ölçüm — remap boyutu beklenenden küçük:**

| PG'nin yayıldığı yıl sayısı | PG adedi |
|---|---|
| 1 yıl | **913** |
| 2 yıl | 40 |
| 3 yıl | 10 |
| 4 yıl | 16 |
| 5 yıl | 44 |

> 1023 PG'nin **%89'u tek yıllık** — onlar için remap kimlik dönüşümü (kopya sayısı 1).
> Gerçek çoklu-yıl remap'i yalnızca **110 PG**'yi ilgilendiriyor.

**⚠️ Ek bulgu — `kpi_data`'da `tenant_id` YOK.** Tenant'a yalnızca
`kpi_data → process_kpis → processes.tenant_id` zinciriyle bağlanıyor.
Migration ve mühür sorguları bu JOIN'i kullanmak zorunda; doğrudan `tenant_id`
filtresi yazılamaz.

**Geri alınamaz nitelikte:** Migration öncesi tam DB yedeği **zorunlu**.

### T13 — Çalışma biçimi: plan bir kez onaylanır, kesintisiz uygulanır

**Karar:** Üç faz (T6: model → mühür → yıl akışı) arka arkaya yerelde uygulanır,
sonunda toplu doğrulama. Faz aralarında onay beklenmez.

**Bu kararın gerektirdiği güvenceler** (Claude'un sorumluluğu):
1. Her faz kendi commit'inde — geri dönüş noktası korunur
2. Migration öncesi tam DB yedeği (T12 geri alınamaz)
3. Toplu doğrulama betiği önceden yazılır, sonda koşar
4. Faz sonlarında **durulmaz ama rapor edilir** — hata çıkarsa orada durulur

---

---

## N. UYGULAMA SIRASINDA ALINAN KARARLAR — K10-K16 (BAĞLAYICI)

> Faz 1 uygulanırken ölçüm plandan sapma gösterdiğinde alınan kararlar.
> Hepsi kullanıcı onayıyla; script/migration docstring'lerinde de kayıtlı.

### K10 — Boş geçmiş plan yılları silinir, gelecek yıl kalır
Tomofil #27 ve 4 klonunda 2018-2019 vardı ama `kpi_data` = **0**. Silindi.
**2027 KALDI** — gelecek yıl planlaması meşru ihtiyaç. Sonuç: 2020-2027.

> ⚠ Silme öncesi FK taraması 2018/2019'a **6.066 satır bağlı** buldu. Ayrıştırıldı:
> 936'sı Faz 1.1'in T3 doldurması (gerçek veri → **2020'ye taşındı**),
> 5.130'u override config (T9 kaldırıyor + UNIQUE çakışması → silindi).
> Tarama yapılmasaydı Blue Ocean/olgunluk verisi sessizce kaybolacaktı.

### K11 — Eskişehir #28'e 2025 üretilir
Kurumun en eski verisi 2025'ti ama tek plan yılı 2026'ydı (T4 ihlali).
2025 üretildi; yapısı 2026'dan **geriye klonlandı**, 204 satır veri bağlandı.

### K12 — Verisi olana gerçek zincir, boş kuruma 2026
Default Corp #1 → 2021-2026 (ilk verisi 2021). #29/#31/#56/#57 → yalnız 2026 (K5).

### K13 — Yılsız kurumlar: ilk yıla bağla, sonra zincirle klonla
KMF #16 (11 süreç + 146 PG **tamamen yılsız**) önce 2020'ye bağlandı, sonra
2021→2026 zinciri klonlandı. Tomofil'deki düzgün yapının aynısı elde edildi.

### K14 — Pasif PG'nin verisi olduğu gibi bırakılır
T12 remap'inde hedefi bulunamayan **273 satırın tamamının PG'si `is_active=False`**
(silinmiş gösterge; "Deneme PG" vb.). Pasif oldukları için hiçbir yıl bazlı
ekranda görünmüyor, rapor rakamlarını etkilemiyorlar. Dokunulmadı.

### K15 — Varlıklara `is_included` kolonu eklenir
Override tablolarındaki 18 satır `is_included=FALSE` taşıyordu (KMF'nin gerçek
verisi): *"gösterge aktif ama bu yıl karneye dahil değil"*. Varlıkta karşılığı
yoktu — `is_active` farklı şey (kayıt silinmiş mi). Kolon açıldı
(migration `yb14a7c2e9f1`), bilgi kaybı olmadan taşındı.

### K16 — Proje birleşmesinde YÖN TERSİNE ÇEVRİLDİ
T10 "PlanProject ana model" diyordu. Ölçüm maliyeti gösterdi:

| | portföy `Project` | SP `PlanProject` |
|---|---|---|
| Veri | 1 proje, 0 görev | 21 proje, 63 görev |
| Kod | **2719 satır, 25 route, 20 dosya, 10 şablon** | 6 route |
| Eksik alan | — | Project +9, Task +16 |

`PlanProject`'i ana model yapmak gantt/kanban/RAID/kapasite/takvim ekranlarını
yeniden bağlamayı gerektiriyordu. **Portföy `Project` ana model oldu**, ona
`plan_year_id` + `source_project_id` eklendi; 21 proje + 63 görev taşındı.

> `manager_id`/`reporter_id` (NOT NULL) **uydurulmadı** — görevlerin
> atananından türetildi. `status`/`progress` karşılıksızdı; sessizce
> düşürülmeyip açıklamaya not olarak yazıldı.

---
