# HAM BULGU — Uçtan Uca Kullanıcı Testi

> Kaynak: paralel ürün kalite uzmanı · **556 GET route gezildi**, 4 tenant, yıl/dil/mühür senaryoları
> Tarih: 2026-07-21 · **K1 ana oturumda DB'den ve koddan yeniden doğrulandı**
> Test verisi temizlendi ve doğrulandı (366604 → 366604)

---

## K1 — Girilen PG verisinin skoru HİÇ hesaplanmıyor ✅ ANA OTURUMDA DOĞRULANDI · **KRİTİK**

`micro/modules/surec/routes_kpi_data.py:158-176`

`KpiData(...)` nesnesi `status` ve `status_percentage` alanlarını **hiç set etmiyor**.

### Ana oturumda yapılan iki doğrulama

**1) DB ölçümü — desen kusursuz ayrışıyor:**

| Kurum | Toplam | Skorsuz | % |
|---|---|---|---|
| **Kayseri Model Fabrika (16)** — gerçek müşteri | 334 | 334 | **%100** |
| **Eskişehir Makine (28)** — gerçek müşteri | 289 | 289 | **%100** |
| **Default Corp (1)** | 2 | 2 | **%100** |
| Tomofil (27) — **seed verisi** | 91.408 | 0 | %0 |
| tomofiltest/tom2/tom3 (58/60/61) | 91.408 | 0 | %0 |

**2) Kod taraması — alanı yazan hiçbir yer yok:**

```
grep "status_percentage =" --include=*.py micro/ app/ services/
→ app/models/process.py:430  (sadece kolon tanımı)
→ app/models/process.py:674  (sadece kolon tanımı)
```

> **Elle veri giren her kurumda sistem skorsuz.** Tomofil'in 91k satırı seed script'iyle
> dolu geldiği için ekranlar sağlıklı görünüyor — **demo verisi hatayı maskeliyor.**

**Bu, K15'teki "ekranlar güncellenmiyor" bulgusunun da kök nedeni.**

---

## K2 — K-Radar hub karnesi yıl seçicisini tamamen yok sayıyor · KRİTİK

`services/k_radar_service.py:283` → `get_hub_summary(tenant_id, scope_process_ids, scope_project_ids)`
— **imzada yıl parametresi yok.**

2020 ↔ 2026 arasında yanıt **byte-byte aynı**: `kp.score=97.54, individual.score=87.09, ks=green`.
KMF'de de 2025 vs 2026 birebir aynı.

> DB'de her yıl için ayrı veri var (2020: 12.600 … 2026: 12.937 satır, ortalama başarı
> 68.86–69.64 arası değişiyor). **"Veri yok" mazereti geçersiz.**

---

## K3 — BI/Excel dışa aktarımı yanlış yılın verisini veriyor, üstelik sessizce kırpıyor · KRİTİK

`micro/modules/raporlar/routes_faz5.py:113-146` → `/k-report/api/bi/kpi-data.csv`

Yıl 2020 seçiliyken indirilen CSV'de bulunan tek yıl: **2024** (1536 kayıt). 2020 hiç yok.

İki ayrı kusur:
1. Sorguda **yıl filtresi yok**
2. `.limit(10000)` var ama **`ORDER BY` yok** → 91.408 satırdan PostgreSQL'in verdiği
   **rastgele** 10.000'lik dilim geliyor

> Bu uç Power BI/Tableau'ya bağlanmak için tasarlanmış. Müşteri raporunu **yanlış yılın
> rastgele üçte biri** üzerine kurar ve bunu fark etmez.

---

## K4 — Yeni kurumun ilk açtığı SP sayfası 500 veriyor · KRİTİK

`ui/templates/platform/sp/index.html:473`

```
jinja2.exceptions.UndefinedError: 'current_app' is undefined
  {{ url_for(...) if 'app_bp.sp_templates_page' in current_app.view_functions else ... }}
```

`current_app` Jinja context'inde tanımlı değil. Bu satır **yalnızca "Henüz ana strateji yok"
boş-durum bloğunda** render ediliyor.

> Yani hata **tam olarak yeni müşterinin ilk gününde** çıkıyor. Strateji girer girmez kayboluyor,
> bu yüzden mevcut müşterilerde görünmüyor ve fark edilmemiş.

Doğrulandı: tenant 29 (Kara Brothers) ve 31 (VolTure) → ikisinde de **HTTP 500**.

---

## K5 — Tanımsız değişken: projesi olan kurumda 4 uç birden çöküyor · YÜKSEK

`services/k_radar_service.py:659`

```
NameError: name 'today' is not defined
  if t.due_date and t.status != "Tamamlandı" and t.due_date < today:
```

`/k-radar/api/kpr/{evm,gantt,risk,resource-capacity}` → tenant 27'de 4 uç da 500.
Tenant 16'da 200, çünkü **projesi olmadığı için fonksiyon 630. satırda erken dönüyor.**

> Tehlikeli asimetri: hata **yalnızca proje modülünü gerçekten kullanan** kurumda tetikleniyor.
> Boş kurumda test edildiği için gözden kaçmış. **Tek satırlık düzeltme.**

---

## K6 — Holding yetki reddi 403 yerine 500 dönüyor · YÜKSEK

`micro/modules/admin/routes_holding.py:19, 68, 112`

Zincirleme sarmalama: `_403()` zaten `(response, 403)` tuple'ı döndürüyor →
`_validate_holding_access` bunu `(_403(), 403)` diye tekrar sarıyor → route `err[0], err[1]`
yapınca sonuç `((resp,403), 403)`.

> Güvenlik kontrolü **çalışıyor** (erişim engelleniyor), ama kullanıcı "yetkiniz yok" yerine
> **"sunucu hatası"** görüyor.

---

## K7 — Navbar'daki "Kule" butonu her kullanıcı için 500 · YÜKSEK

`templates/base.html:70` → `/admin/kule-iletisim` · **tıklanabilir canlı navbar butonu**

Aynı şekilde `/admin/strategy-management` de `templates/layouts/admin_base.html:33`'ten linkli
ve 500 veriyor.

> Kullanıcı kırık butona tıklamamalı — ya onarılmalı ya link kaldırılmalı.

---

## K8 — Süreç sayfası İngilizce'de Türkçe kalıyor · ORTA

İki ayrı kök neden:

1. **`_()` ile sarılmamış** — `surec/index.html:33` ("Süreç hiyerarşisi · performans
   göstergeleri…"), `:67` ("Yeni Süreç" butonu), `<title>` "Süreç Yönetimi — Kokpitim"
2. **Sarılmış ama çevirisi boş** — 3600 msgid'in **30'u çevirisiz**.
   Doğrulandı: `msgid "Teşhis Radarları:"` → `msgstr ""` (K-Radar üst barında Türkçe görünüyor)

*(Ana oturumda ayrıca doğrulandı: sidebar'daki **rol adı** ve **breadcrumb** de EN'de Türkçe kalıyor.)*

---

## K9 — Mühür açılınca yıl `active` yerine `draft`'a düşüyor · ORTA

Tomofil 2026 (`status=active`) mühürlenip geri açıldı → dönen `status: "draft"`.

> Kurumun **aktif plan yılı**, mühür açma sonrası sessizce taslağa dönüyor.
> `reopen` önceki statüyü saklayıp geri yüklemeli.

*(Bu, bu oturumda yazılan `reopen_plan_year` fonksiyonunun bilinçli kararıydı — docstring'de
"kurumun aktif yılı genellikle başkasıdır" deniyor. Ama aktif yılın kendisi mühürlenirse
davranış yanlış oluyor.)*

---

## K10 — Sparkline'lar hep "son 3 takvim ayı"nı gösteriyor · ORTA

`micro/modules/surec/routes_process.py:570-610` — SQL `CURRENT_DATE`'e sabitli
(`date_trunc('month', CURRENT_DATE) - INTERVAL '2 months'`), session'daki yılı hiç okumuyor.

2020, 2025, 2026'da aynı yanıt: `labels: ["2026-05","2026-06","2026-07"]`

> Süreç kartlarındaki mini trend geçmiş yıl görünümünde **boş çiziliyor**
> (KMF'de `[null, 50.0, null]`) — kullanıcı "veri yok" sanıyor, oysa o yılda veri var.

---

## K11 — Süreç karnesi puan detayı KMF'nin gerçek PG'sinde 404 · ORTA

`/k-plan/process/api/kpi/342/score-detail` → `404 {"message":"KPI bulunamadı."}`
(hem 2025 hem 2026'da). PG gerçekten var ve ölçüm verisi taşıyor.

> K1 ile bağlantılı olabilir. Ayrıca PG'nin `code` alanı `None` — **KMF verisinde PG kodları boş**,
> bu kart/rapor eşleştirmesini de bozabilir.

---

## K12 — Legacy blueprint'lerde ölü model alanları: 40+ uç 500 · ORTA

| Hata | Uç |
|---|---|
| `Process has no attribute 'liderler'` | `/surec/<id>` |
| `ProcessKpi has no attribute 'alt_strateji'` | `/surec/<id>/performans-gostergesi/<id>` |
| `Process has no attribute 'uyeler'` | `/api/surec/<id>/uyeler` |
| `name 'PerformansGostergeVeri' is not defined` | `/api/pg-veri/detay/<id>` |
| `'User' object has no attribute 'kurum'` | `/api/strategic-planning/graph` |
| **`<flask_caching.Cache object …>`** (mesaj olarak Cache nesnesi!) | `/api/dashboard/executive` |

Strangler yönüyle uyumlu (legacy erir) — **ama bazıları canlı template'lerden linkli**:
`templates/project_detail.html:33` → `main.strategy_project_detail` → 500.

---

## K13 — Boş kurumda "kurulum yapın" yönlendirmesi yok · DÜŞÜK

K4 hariç hepsi 200, çökme yok — bu iyi. Ancak K-Radar **104 KB'lık dolu görünen** bir sayfa
çiziyor, altındaki tüm API'ler boş (`hub-summary` 502 byte, `k-vektor` 58 byte).

> Kullanıcı sıfırlarla dolu bir gösterge paneli görüyor — yeni kullanıcıyı ürünün bozuk
> olduğuna inandırır.

---

## K14 — MÜHÜR DOĞRU ÇALIŞIYOR ✅

- Mühürleme → `200 {"status":"closed"}`
- Mühürlü yıla veri → **`423 {"error":"plan_year_sealed"}`** + açıklayıcı Türkçe mesaj
- Geri açma → 200

Ayrıca **yıl-varlık kontrolü de doğru**: 2020 PG'sine 2026 tarihli veri denemesi →
`409` + net mesaj (*"PG-AR01-2020 … 2026 planında bulunmuyor. Bu PG 2020 dönemine ait"*).

**Yıl bazlı veri bütünlüğü sağlam.** Tek kusuru K9.

---

## K15 — Veri girildiğinde çoğu ekran güncellenmiyor · ORTA

| Uç | Sonuç |
|---|---|
| `kpi-data/list/<pg>` | ✅ DEĞİŞTİ |
| `k-report/api/process-pg` | ✅ DEĞİŞTİ |
| `k-report/api/pi-dagilim` | ✅ DEĞİŞTİ |
| `k-radar/api/hub-summary` | ❌ AYNI |
| `k-radar/api/kp/radar` | ❌ AYNI |
| `k-report/api/k-vektor` | ❌ AYNI |
| `process/api/sparklines` | ❌ AYNI |
| `kpi/<pg>/score-detail` | ❌ AYNI |

**K1'in türevi** — skor NULL yazıldığı için skor tabanlı toplamalar değişmiyor.

---

# ÖZET TABLO 1 — 500 veren sayfalar (556 route içinde 55)

**Modern yüzey — öncelikli:**

| Yol | Kök neden | Kullanıcı erişebiliyor mu |
|---|---|---|
| `/k-plan/strategy` (boş kurum) | `current_app` Jinja'da tanımsız | ✅ **Yeni müşterinin ilk sayfası** |
| `/admin/kule-iletisim` | — | ✅ **navbar butonu** (`base.html:70`) |
| `/admin/strategy-management` | — | ✅ **menü** (`admin_base.html:33`) |
| `/holding/api/tenant/<id>/drilldown` | `_403()` çift tuple | ✅ yetkisiz kullanıcı |
| `/k-radar/api/kpr/{evm,gantt,risk,resource-capacity}` | `NameError: today` | ✅ **projesi olan kurum** |
| `/k-plan/strategy/api/projects/<id>/evm` | — | ✅ |
| `/api/v1/analytics/trend/<id>` · `/api/v1/reports/performance/<id>` | — | API |

**Legacy yüzey:** 42 uç (K12).

---

# ÖZET TABLO 2 — Yıl değişimine TEPKİ VERMEYEN uçlar

Tomofil (27), 2024 ↔ 2026, yanıt md5. **193 uçtan 94'ü byte-byte aynı.**

| Kategori | Uçlar |
|---|---|
| **K-Radar ana karne** | `hub-summary`, `kp/radar`, `kp/maturity` |
| **Tüm strateji teşhis radarları** | `ks`, `ks/bsc`, `ks/swot-summary`, `ks/okr`, `ks/bcg`, `ks/ansoff`, `ks/efqm`, `ks/gap`, `ks/hoshin`, `ks/pestle`, `ks/tows` |
| **Tüm süreç teşhisleri** | `kp/{benchmark,capacity,darbogaz,oee,pareto,sla,value-chain,vsm}` |
| Risk | `risk/list`, `risk/matrix` |
| **BI dışa aktarım** | `bi/kpi-data.csv` (K3) |
| **Zaman serisi raporları** | `evolution-film`, `strategy-story`, `swot-trend`, `target-revision` — *yıl değişmemesi özellikle anlamsız* |
| Üst yönetim panosu | `exec-snapshot`, `exec-trend`, `exec-strategy-scores` |
| Bireysel hizalama | `alignment-score`, `team-alignment` |

> **Doğru çalışanlar (kıyas için):** 99 uç yıla tepki veriyor — `early-warning` (903→283 byte),
> `data-quality` (6625→1300), `muda-analysis` (1951→9759), `strategies`, `xmatrix`, `k-vektor`.
> Yani **`resolve_request_year()` mekanizması çalışıyor — sadece yukarıdaki uçlar onu çağırmıyor.**

---

## Genel değerlendirme

**Sağlam olan:** mühür/kilit mekanizması (423), yıl-varlık bütünlük kontrolü (409),
çok kiracılı izolasyon, yetki katmanı (42 uçta doğru 403), boş kurumda çökmeme (1 istisna).

**Tekrar eden desen — en önemli gözlem:**
> **K1, K4, K5'in üçü de "veri az/yokken" veya "seed verisiyle" test edildiği için gözden
> kaçmış, gerçek kullanımda ortaya çıkıyor.** Tomofil'in zengin seed verisi bazı hataları
> gizlerken (K1), bazılarını tek başına ortaya çıkarıyor (K5).
