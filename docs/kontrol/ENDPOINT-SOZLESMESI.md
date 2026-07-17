# Endpoint Sözleşmesi — Faz 0 çıktısı

> Katman mimarisi uygulamasının güvenlik ağı. Ölçümle üretildi (elle değil).
> Tarih: 2026-07-17 · Kaynak: `micro/**/*.py` route taraması · Durum: DONMUŞ
> Tasarım: `KATMAN-MIMARISI-HEDEF.md` · Plan: `KATMAN-MIMARISI-YOL-HARITASI.md`

---

## Sözleşme — tek cümle

**Route `path`'i değişir. Endpoint `def` adı ASLA değişmez.**

Template'lerdeki `url_for('app_bp.sp_swot_page')` çağrıları endpoint ADINA bağlıdır.
Ad sabit kalırsa path değişince `url_for` yeni path'i otomatik üretir → **~64 template'e
dokunulmaz.** Bu sözleşme bozulursa iş 10× büyür.

```python
# DOĞRU — path değişti, ad korundu
@app_bp.route("/k-plan/strateji/swot")   # eski: "/sp/swot"
def sp_swot_page():                       # ← AD AYNI (sözleşme)

# YANLIŞ — ad değişti → 64 template kırılır
def k_plan_strateji_swot_page():          # ← YASAK
```

Endpoint adı ile URL'nin uyuşmaması **kabul edilen bedeldir**. Ad = tarihsel kimlik,
path = kullanıcıya görünen adres. Faz 6'da ad temizliği ayrı tartışılır (şimdi DEĞİL).

---

## Ölçüm — 610 route (2026-07-17)

| Modül | Route | Hedef katman |
|---|---:|---|
| sp | 127 | GİRDİ (+ Savaş Odası → Teşhis) |
| raporlar | 101 | RAPOR |
| admin | 90 | (katman dışı — altyapı) |
| k_radar | 88 | TEŞHİS |
| surec | 39 | GİRDİ |
| k_rapor | 35 | RAPOR |
| proje | 22 | GİRDİ + TEŞHİS |
| shared | 22 | (katman dışı) |
| bireysel | 18 | GİRDİ |
| api | 15 | (katman dışı) |
| kurum | 15 | (katman dışı) |
| marketing | 14 | (altyapı) |
| masaustu | 11 | TEŞHİS |
| analiz | 7 | TEŞHİS |
| demo | 4 | (altyapı) |

### ✅ ÇİFT ENDPOINT ADI: 0

**Ölçüldü: 610 route'un 610 farklı `def` adı var.** Sözleşme uygulanabilir —
`url_for` çakışma riski yok. Bu, yol haritasının temel varsayımının kanıtıdır.

---

## Faz 2 kapsamı — ölçümle düzeltildi

### Bulgu 1 — K-Radar path'leri ZATEN katman/konu şemasında

Yol haritası "`/k-radar/*` path'lerini katman/konu şemasına geçir" diyordu. Ölçüm:

| Path öneki | Route |
|---|---:|
| `/k-radar/api` | 60 |
| `/k-radar/kp` | 11 |
| `/k-radar/cross` | 6 |
| `/k-radar/kpr` | 6 |
| `/k-radar` (hub) | 1 |
| `/k-radar/ks` · `/k-radar/risk` · `/k-radar/takvim` | 3 |
| **`/k-analiz`** | **1** ← tek aykırı |

**Sonuç:** Faz 2'nin path işi neredeyse yok. Tek aykırı `/k-analiz`.

### Bulgu 2 — K-Radar'ın KENDİ 15 yazma route'u var (belge saymamıştı)

Hedef belge yazma borcunu SP'den ödünç alınan `sp_api_swot_save` sanıyordu. Gerçekte
K-Radar'ın kendine ait 15 POST/PUT/DELETE route'u var. **Kullanıcı kararı (2026-07-17):
kategori kategori ayrılır — her grup ait olduğu fazda ele alınır.**

| Grup | Route | Karar |
|---|---:|---|
| **SP save çağrıları** (ks.html/k_radar_ks.js → `sp_api_*_save`) | — | **FAZ 2: şimdi kaldırılır** |
| **Olgunluk** (`k_radar_kp_olgunluk_ekle`, `..._api_kp_olgunluk_create/update/delete`) | 4 | **FAZ 3**: Girdi'ye taşınır — şimdi DOKUNULMAZ |
| **Risk** (`k_radar_api_risk_add`, `k_radar_api_risk_modify`) | 2 | **FAZ 5**: `source_id` migration ile — şimdi DOKUNULMAZ |
| **Paydaş** (`cross_paydas_ekle`, `api_cross_paydas_create/update/delete`) | 4 | ⚠️ KARAR BEKLİYOR — tasarımda konuşulmadı |
| **Değer zinciri** (`api_vc_item_add/update/delete`) | 3 | ⚠️ KARAR BEKLİYOR |
| **Takvim** (`k_radar_schedule_save`) | 1 | ⚠️ KARAR BEKLİYOR |

⚠️ **Açık borç:** Paydaş + değer zinciri + takvim (9 route) tasarımda hiç konuşulmadı.
Teşhis katmanında sayıldılar ama yazma yüzeyleri var. Faz 2 bunlara dokunmaz;
katman ataması ayrı karar gerektirir.

### Bulgu 3 — "K-Analiz ölü izi" varsayımı YANLIŞ

Yol haritası (Faz 2): *"'K-Analiz' ikinci sidebar girişini kaldır (K-Radar zaten var)."*

**Ölçüm bunu çürüttü.** `base.html`'de iki giriş farklı hedefe gider:

| Sidebar | Endpoint | Kapsam |
|---|---|---|
| K-Radar (`:208`) | `k_radar_hub` | hub / genel bakış |
| K-Analiz (`:216`) | `k_radar_ks` | KS + KP + KPR + Cross ailesi |

`active` mantığı ikisini **bilinçli** ayırmış (`'k_radar_ks' not in ep` → hub girişi
KS'yi dışlar). Bu çift kayıt değil, K-Radar'ın alt-navigasyonu. Silinirse
KS/KP/KPR/Cross sayfalarına sidebar erişimi biter.

**Kullanıcı kararı (2026-07-17): giriş KALIR, yeniden adlandırılır** (K-Radar vs
K-Analiz karışıklığı gideriliyor; ekran metni Türkçe kuralı §2).

---

## Faz 2 — UYGULANDI ✅ (2026-07-17, TASK-273)

- [x] SP save çağrıları kaldırıldı → teşhis salt-oku (`ks.html` + `k_radar_ks.js`)
      · 3 katmanda kilit: route `can_manage=False` + template attr yok + JS `CAN_MANAGE=false`
      · kullanıcı kaybetmesin: modallarda "Stratejik Planlama'da düzenle" yönlendirmesi
- [x] Savaş Odası taşındı: `/sp/tv` → `/k-radar/savas-odasi` (`sp_tv_mode` adı KORUNDU)
- [x] `/sp/tv` → 301 redirect (`sp_tv_mode_legacy`) — bookmark kırılmadı
- [x] Sidebar "K-Analiz" → **"K-Radar Araçları"** (6 yerde: sidebar, ks/kp/kpr/cross
      breadcrumb, komut paleti, analiz linki) + `.po` elle + compile
- [x] `/k-analiz` alias korundu (→ `/k-radar/ks`, zaten redirect'ti)
- [x] DOKUNULMADI: olgunluk (Faz 3) · risk (Faz 5) · paydaş/VC/takvim (karar bekliyor)

**Doğrulama:** `pytest -q` 588 passed (baseline aynı) · 8/8 smoke · `node --check` temiz.

### Faz 2'nin bıraktığı borç — ÇÖZÜLDÜ (karar: 2026-07-17)

Ölçüm 8 route'u tek grup sanmıştı; gövdeleri okununca **3 ayrı şey** çıktı:

| Grup | Route | Ne yazıyor | Karar |
|---|---:|---|---|
| **Paydaş** | 4 | `StakeholderMap` — gerçek iş verisi | **Faz 3**: `/k-plan/strateji/paydas` evi inşa edilir |
| **Değer zinciri** | 3 | `ValueChainItem` — gerçek iş verisi | **Faz 3**: `/k-plan/surec/deger-zinciri` evi inşa edilir |
| **Takvim** | 1 | zamanlayıcı ayarı (açık/kapalı + saat) | **KAPSAM DIŞI** — iş verisi değil |

**Takvim neden istisna değil:** `k_radar_schedule_save` iş verisi yazmıyor, K-Radar'ın
kendi rapor zamanlayıcı *ayarını* kaydediyor. Katman kuralı ("her veri tek katmanda
yazılır") iş verisi içindir; bir modülün kendi ayarı bu kapsama girmez. Kural
esnetilmedi — kapsamı doğru okundu.

**Paydaş/VC neden Faz 3'e ertelendi (Faz 2'de yapılmadı):** Girdi katmanında evleri
yok. Faz 2 salt-oku yapabilirdi ama kullanıcı veriyi giremez hale gelirdi — yetenek
kaybı olurdu. Olgunluk'ta durum farklı: evi hazır (süreç modülü). Üçü birlikte Faz
3'te taşınır; K-Radar'da salt-oku görünüm kalır.

## Faz 3 — UYGULANDI ✅ (2026-07-17, TASK-274)

Girdi katmanı `/k-plan/` önekine taşındı: **202 route path** (sp 127 → `/k-plan/strategy`,
surec 39 → `/k-plan/process`, proje 22 → `/k-plan/project`, bireysel 18 →
`/k-plan/individual`). Endpoint adları DEĞİŞMEDİ → ~64 template'e dokunulmadı.

### ⚠️ EN ÖNEMLİ DERS — path kapıları sessizce açar

Route path'i değişince **path önekine bakan güvenlik kapıları sessizce devre dışı kalır.**
Kod hata vermez; kapı yalnızca "eşleşme yok" deyip isteği geçirir. Faz 3'te bu **3 yerde**
oldu ve yalnızca test yakaladı:

| Yer | Ne oldu | Kanıt |
|---|---|---|
| `platform_core/__init__.py::_ROLE_GATED_PREFIX_MODULE` | `/sp` kaydı vardı, `/k-plan/strategy` yoktu → **SP rol kapısı açıldı** | `test_sp_rol_kapisi_standart_kullaniciyi_engeller` 200 aldı (302 beklerken) |
| `platform_core/__init__.py::_GATED_PREFIX_MODULE` | Paket kapısı aynı şekilde girdi katmanında devre dışı | (aynı mekanizma) |
| `micro/core/module_registry.py` | Modül URL'leri `/sp`, `/process`… → sidebar/launcher eski adrese işaret ediyordu | sidebar denetimi |
| `app/middleware/legacy_sunset.py::_is_platform_canonical` | `/k-plan/` platform kanonik sayılmıyordu → legacy dönüşüme yakalanabilirdi | önlem olarak eklendi |

**Kural:** Bir modülün path'ini taşırken bu 4 dosya AYNI commit'te güncellenir.
Yeni bir katman öneki eklenirse (örn. Faz 4 `/k-report/`) hepsine eklenmelidir.

### Redirect: 307, 301 DEĞİL
`/sp`, `/process`, `/project`, `/individual` → **307** ile yeni adrese. 301 tarayıcıya
POST'u GET'e çevirme izni verir → form gönderimleri sessizce bozulurdu. Mevcut
`/surec → /process` redirect'i de 307 kullanıyordu; aynı kalıp sürdürüldü.
(İstisna: `/sp/tv` → `/k-radar/savas-odasi` 301 — Faz 2'de kondu, saf GET sayfası.)

### Girdi evleri inşa edildi (şablon paylaşımı)
| Araç | Girdi evi (yazar) | Teşhis (salt-oku) |
|---|---|---|
| Paydaş | `/k-plan/strategy/stakeholder` | `/k-radar/cross/stakeholder` |
| Değer zinciri | `/k-plan/process/value-chain` | `/k-radar/kp/value-chain` |
| Olgunluk | `/k-plan/process/maturity` | `/k-radar/kp/maturity` |

Tek şablon, iki adres, `can_manage` farkı — Faz 2'nin SWOT kalıbı. Yazma API'leri
`/k-plan/` altına taşındı; okuma uçları teşhiste kaldı (teşhis okuyabilir).

### Ölçümün düzelttiği 2 plan hatası daha
1. **"URL şeması `/k-plan/surec/...`"** → YANLIŞ. Girdi modülleri **zaten İngilizce'ye
   taşınmıştı** (`/process` 37, `/individual` 18, `/project` 21). Türkçe şema hem
   KURALLAR §2'yi ihlal ederdi hem kodu geri döndürürdü. **Karar: İngilizce konu adı.**
2. **"6 hardcoded URL"** → **27'ymiş** (5 template + 6 JS). Yol haritası JS'i saymamış.
   26'sı düzeltildi; 3'ü `sp_projeler.js`'te bilerek bırakıldı (legacy `/proje` üzerinden
   string türetiyor, çalışıyor, mantığı kırılgan).

### Yan bulgu (Faz 3'ten önce de kırıktı)
Komut paletinde `/project/gantt` ve `/project/kanban` girdileri vardı — **bu route'lar
hiç var olmamış**. Gerçek adres proje ID'si ister (`/k-plan/project/<id>/views/gantt`).
Girdiler kaldırıldı.

## Hatırlatmalar

- **CI çalışmıyor** → doğrulama `python -m pytest -q` (yerel) + `scripts/ci/yerel_kontrol.py`
- **pybabel update KULLANMA** → i18n katalogunu bozuyor; `.po` elle + compile
- **base.html/route değişince** `python pybasla.py` ile yeniden başlat
- Redirect kalıbı zaten var: `micro/modules/k_rapor/routes.py:88`
