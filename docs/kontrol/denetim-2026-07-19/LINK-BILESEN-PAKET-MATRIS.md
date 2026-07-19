# Link → Bileşen → Paket → Sağlık → Ulaşılabilirlik Matrisi

> Kullanıcı isteği: "Ana sayfadan (Admin ve Kurum Yöneticisi ayrı ayrı) girildiğinde
> hangi linklerimiz var, hangi bileşenleri çalıştırıyor, hangi pakette açılabilir.
> Sayfa sağlığı + paket yapısı + 'bileşen var ama tıklayarak ulaşabiliyor muyuz?'"
> Yöntem: 3 paralel ajan + doğrudan ölçüm (Flask test_client + Playwright). Tahmin yok.
> Tarih: 2026-07-19 · 266 sayfa route · 4 rol · 4 paket

---

## 🔴 YÖNETİCİ ÖZETİ — 3 KRİTİK HATA (hepsi ölçülüp doğrulandı)

### K1. Rapor katmanı KURUM KULLANICILARINA TAMAMEN KAPALI
`micro/modules/raporlar/routes.py` + `routes_faz2/4.py`: 46 rapor sayfası
`@require_module("raporlar")` ile korunuyor. AMA **"raporlar" diye bir sistem
modülü YOK** — sistemde yalnız `k_rapor_modulu` var. `require_module` var olmayan
modülü hiçbir kullanıcının paketinde bulamaz → **/desktop'a atar.**

- **Etki:** Master paketi (her modül açık) olan Tomofil admin'i bile CFO/ESG/CMMI/
  risk-heatmap raporlarına GİREMİYOR. Yalnız platform Admin (`role=='Admin'`) bypass'la geçer.
- **Doğrulama:** uid 8173 (tenant_admin, Master paket) → `/k-report/cfo-dashboard` = **302 /desktop**. uid 1 (Admin) → 200.
- **Düzeltme:** `require_module("raporlar")` → `require_module("k_rapor")` (tüm raporlar dosyalarında). Tek kelime, 46 sayfayı açar.

### K2. Legacy sayfalar HER KULLANICIDA 500 — ölü endpoint
`templates/base.html:63` ve `:145` (KÖK base, platform değil) `url_for('admin_bp.tenants')`
çağırıyor — bu endpoint **yeniden adlandırılmış, artık yok** (`admin_bp.tenants_archive` var).
Rol koşulunun DIŞINDA olduğu için bu base'i extend eden HER sayfa BuildError 500 verir.

- **Etki:** `/yardim-merkezi`, `/ai-chat`, `/ai-coach`, `/2fa/setup`, `/portfoy-ozeti`,
  `/admin/strategy-management`, `/admin/kule-iletisim`, `/admin/feedback` → 500.
- **Not:** Modern `ui/templates/platform/base.html` TEMİZ — platform sayfaları etkilenmez.
  Yalnız kök base'i kullanan legacy sayfalar çöküyor.
- **Düzeltme:** `templates/base.html:63,145` → `admin_bp.tenants_archive` (veya `app_bp.admin_tenants`). 9+ sayfayı kurtarır.

### K3. Sidebar linki görünür ama route ENGELLİYOR — 2 çelişki
Link görünürlük koşulu ile route paket-gate'i UYUŞMUYOR → kullanıcı linki görür,
tıklar, açılmaz:
- **K-Radar:** sidebar koşulu `k_radar OR k_rapor` (Yönetim paketinde görünür) ama route `paket_gate=k_radar` (Yönetim'de yok) → Yönetim paketinde link var, tıklanınca engellenir.
- **Savaş Odası:** sidebar koşulu `sp` (tüm paketlerde) ama route `paket_gate=k_radar` → Başlangıç/Yönetim'de görünür, açılmaz.

---

## PAKET YAPISI (DB'den ölçüldü)

| Paket | Modül sayısı | İçindeki modüller |
|---|---|---|
| **Başlangıç** | 2 | stratejik_planlama, kurum_paneli |
| **Yönetim** | 7 | + surec, proje, bireysel, performans_analitigi, k_rapor |
| **Strateji** | 8 | + k_radar |
| **Master** | 13 | hepsi (ileri modüller dahil) |

**Modül → paket erişimi:**

| Modül | Başlangıç | Yönetim | Strateji | Master |
|---|:-:|:-:|:-:|:-:|
| stratejik_planlama (sp) | ✅ | ✅ | ✅ | ✅ |
| kurum_paneli | ✅ | ✅ | ✅ | ✅ |
| surec / proje / bireysel / performans_analitigi | — | ✅ | ✅ | ✅ |
| k_rapor | — | ✅ | ✅ | ✅ |
| k_radar | — | — | ✅ | ✅ |

---

## ROL BAZLI SIDEBAR (Playwright ile ölçüldü)

| Rol | Bölümler | Link sayısı |
|---|---|---|
| **Admin** (platform) | GİRDİ · TEŞHİS · RAPORLAR · YÖNETİM · ADMİN ARAÇLARI · SİSTEM | 19 |
| **tenant_admin / executive_manager** | GİRDİ · TEŞHİS · RAPORLAR · YÖNETİM · SİSTEM | 16 |
| **standard_user** | **GİRDİ · SİSTEM** | **4** (Masaüstüm, Bireysel Karne, Bildirimler, Ayarlar) |

**Kurum Yöneticisi GÖRMEZ** (yalnız `role=='Admin'`): SaaS Paketler, API Dokümantasyonu, Admin Araçları.

---

## MATRİS — ADMIN GÖRÜNÜMÜ

Link | URL | endpoint | bileşen | rol koşulu | paketler | sağlık
---|---|---|---|---|---|---
Masaüstüm | /desktop | masaustu | masaustu/index.html | herkes | Tümü | ✅ 200
**GİRDİ** ||||||
Stratejik Planlama | /k-plan/strategy/menu | sp_menu | sp/menu.html (HUB) | rol+sp | Tümü | ✅
Kurum Paneli | /organization | kurum | kurum template | rol+kurum | Tümü | ✅ ⚠️(std_user'a da açık)
Alt Kurum | /admin/sub-tenants | admin_sub_tenants_page | admin/sub_tenants.html | rol+dealer/holding | tenant tipi | ✅
Süreç Yönetimi | /k-plan/process | surec | surec template | surec | Yön,Str,Mas | ✅
Proje Yönetimi | /k-plan/project | project_list | project/list.html | proje | Yön,Str,Mas | ✅
Bireysel Performans | /k-plan/individual/scorecard | bireysel_karne | karne template | bireysel | Yön,Str,Mas | ✅
**TEŞHİS** ||||||
K-Radar | /k-radar | k_radar_hub | k_radar/hub.html (HUB) | k_radar\|k_rapor | Str,Mas | ✅ ⚠️K3
Performans Analitiği | /k-radar/analysis | analiz | analiz template | rol+analiz | Yön,Str,Mas | ✅
Savaş Odası | /k-radar/savas-odasi | sp_tv_mode | TV template | rol+sp | Str,Mas | ⚠️K3
**RAPORLAR** ||||||
Yönetim Özeti | /yonetim-ozeti | yonetim_ozeti | yonetim template | rol+k_rapor | Yön,Str,Mas | ✅
Raporlar | /k-report | k_rapor | k_rapor/index.html (HUB, 22 sekme) | rol+k_rapor | Yön,Str,Mas | ✅ katalog / ❌ K1 tekil raporlar
Holding Görünümü | /holding/dashboard | holding_dashboard_page | admin/holding_dashboard.html | rol+holding | tenant tipi | ✅
**YÖNETİM** ||||||
Kullanıcılar | /admin/users | admin_users | admin/users.html | rol | paketsiz | ✅
Kurumlar | /admin/tenants | admin_tenants | admin/tenants.html | rol | paketsiz | ✅
Bildirim Merkezi | /admin/notifications | admin_notifications | admin/notifications.html | rol | paketsiz | ✅
SaaS Paketler | /admin/packages | admin_packages | admin/packages.html | **Admin** | paketsiz | ✅
API Dokümantasyonu | /api/docs | api_docs | api/docs.html | **Admin** | paketsiz | ✅
Admin Araçları | /admin/araclar | admin_tools_home | araclar.html | **Admin** | paketsiz | ✅
**SİSTEM** ||||||
Bildirimler | /notification | bildirim | bildirim/index.html | herkes | Tümü | ✅
Ayarlar | /settings | ayarlar | ayarlar/index.html | herkes | Tümü | ✅

## MATRİS — KURUM YÖNETİCİSİ (tenant_admin / executive_manager)
Admin matrisinin aynısı, EKSİ: SaaS Paketler, API Dokümantasyonu, Admin Araçları
(bunlar `role=='Admin'` özel). Her modül linki tenant paketine bağlı — Başlangıç
paketinde yalnız Stratejik Planlama + Kurum Paneli + Yönetim(paketsiz) + Sistem görünür.

⚠️ **Kurum Yöneticisi için K1 kritik:** "Raporlar" linkini görür, katalog açılır,
ama tekil rapor sayfaları (CFO/ESG/CMMI...) `require_module("raporlar")` yüzünden
/desktop'a atar. **Rapor katmanı kurum yöneticisi için fiilen çalışmıyor.**

---

## İKİNCİ SEVİYE — HUB İÇİ LİNKLER

- **K-Radar hub** (`/k-radar`): Teşhis Radarları şeridi → KS, KP (2 link). 5 kart grubu (66 kart) → çoğu `/k-report/*` (K1'den etkilenir).
- **Raporlar hub** (`/k-report`): 22 sekme kartı — katalog çalışır ama tekil raporlar K1.
- **SP menü** (`/k-plan/strategy/menu`): 17 araç kartı → hepsi çalışır (sp, tüm paketlerde).

---

## ULAŞILABİLİRLİK — "bileşen var ama tıklayarak ulaşabiliyor muyuz?"

### GERÇEK YETİM (hiçbir yerden linklenmiyor)
| Kategori | Sayı | Örnekler |
|---|---|---|
| `main.*` legacy sayfalar | 37+ | /risks, /crisis, /gemba, /mtbp, /muda-hunter, /black-swan, /metaverse, /yardim-merkezi, /dokuman-merkezi |
| SP alt sayfaları | 7 | mission, vision, values, flow, periodic-report, wizard/new-year, llm-usage |
| Admin araçları | 2 | kilavuz-olusturucu, setup-import |
| Bağımsız | 2 | /k-analiz hub, /k-report/anomalies |

**Not:** `/k-radar/ks` sorunu ARTIK YOK — hub'a Teşhis Radarları şeridi eklendi (bugün düzeltildi). K-Radar ağacı erişilebilir.

### MEŞRU (yetim değil)
Legacy redirect'ler (/sp, /surec, /reports...), auth/altyapı (/login, /health, /2fa),
pazarlama sitesi (/home, /ozellikler/*), indirme (export.csv, .ics, .pdf), saf API,
dev route'lar (/debug/*, /admin/seed_db).

---

## SAĞLIK — 500/404 (test_client ile ölçüldü, 262 URL × 2 rol)

| Durum | tenant_admin | platform Admin |
|---|---|---|
| 200 sağlıklı | 118 | 179 |
| redirect (301/302/307) | 101 | 57 |
| 403 gating (normal) | 26 | 1 |
| **500 çökme** | **13** | **15** |
| **404 kırık** | **4** | **9** |

**500'ler (kök nedene göre):**
- K2 (`admin_bp.tenants` ölü endpoint): /yardim-merkezi, /ai-chat, /ai-coach, /2fa/setup, /portfoy-ozeti, /admin/strategy-management, /admin/kule-iletisim, /admin/feedback → tek satır düzeltmeyle çözülür
- Model hataları: /debug/surec-data (`User.username` yok), /dokuman-merkezi (`ProjectFile.scope` yok), /dashboard/executive (flask_caching yanlış kullanım)
- Config: /vapid-key (VAPID yok — 500 yerine 503 dönmeli)

**404'ler:** /demo* (demo modu kapalı — feature flag), admin araç alt-eylemleri (POST bekleyen endpoint'ler GET'te 404).

---

## ÖNCELİK SIRASI

| # | Sorun | Düzeltme | Etki |
|---|---|---|---|
| 1 | **K1** rapor katmanı kapalı | `require_module("raporlar")` → `"k_rapor"` | 46 rapor sayfası kurum kullanıcılarına açılır |
| 2 | **K2** legacy 500 | `templates/base.html:63,145` endpoint düzelt | 9+ sayfa 500'den kurtulur |
| 3 | **K3** link/route gating uyumsuz | K-Radar + Savaş Odası sidebar koşulunu route gate'iyle hizala | "tıkladım açılmadı" biter |
| 4 | model 500'leri | User.username / ProjectFile.scope / cache düzelt | 3 sayfa |
| 5 | yetim main.* | ürün kararı: bağla ya da kaldır (çoğu legacy) | 37+ sayfa |
| 6 | /organization gating sızıntısı | route'a paket/rol gate ekle | standard_user erişimi kapanır |
