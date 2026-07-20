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

### S5 — `plan_year_enabled` flag'i (açık)
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
