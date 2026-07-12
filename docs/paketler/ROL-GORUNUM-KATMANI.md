# ROL BAZLI GÖRÜNÜM KATMANI — Tasarım Belgesi

> **Durum:** Tasarım mutabakatı tamamlandı — kodlama başlamadı.
> **Tarih:** 2026-07-11
> **Sahip:** Kullanıcı + Claude Code oturumu
> **İlgili belgeler:** [`PAKETLEME-STRATEJISI.md`](PAKETLEME-STRATEJISI.md) · [`KART-SISTEMI-MIMARI.md`](KART-SISTEMI-MIMARI.md) · `KURALLAR-MASTER.md §9`
> **Kural:** Bu belge "önce yaz, mutabakat sonra kodla" (KURALLAR §9) yordamına uygun olarak, kod yazılmadan önce hazırlanmıştır. Karar değişirse önce bu belge güncellenir.

---

## 1. Problem — neyi çözüyoruz

Sahadan gelen geri bildirim: **"Sistem güzel ama çok karışık, çok fazla ekran karmaşası var."** Özellikle:
- Kurum yöneticileri / üst yönetim, şirkette işlerin nasıl gittiğini **kısa ve hızlı** görebilmeli.
- Veri girecek sıradan personel, kendisini ilgilendirmeyen onlarca ekran arasında **kaybolmamalı**.

### Kök neden (kod ile doğrulanmış)
Karmaşa *ekran sayısından* değil, **"hangi rol neyi görmeli" kararının tek merkezde verilmemesinden** kaynaklanıyor. Bu karar bugün 4 ayrı yere dağılmış:
1. Paket (subscription) kontrolü — `get_accessible_modules`
2. `ui/templates/platform/base.html` içindeki dağınık hardcoded `if role.name in [...]` blokları
3. `module_registry.py::_ROLE_RESTRICTED` — yalnızca 3 modül
4. `@role_required` decorator — yalnızca 9 route

**Önemli bulgu:** Backend'de "kim ne *yapabilir*" (yetki) sorusu zaten doğru ve zengin biçimde çözülmüş. Sorun UI'ın "kim ne *görmeli*" sorusunu bu yetki gerçeğini **okumadan** cevaplaması. Bu iş yeni bir yetki sistemi kurmaz; UI görünürlüğünü var olan yetki gerçeğine bağlar ve dağınık kararı tek merkeze toplar.

---

## 2. Model — iki eksen

Görünürlük iki bağımsız eksenin kesişimidir. **Bu ikisi karıştırılmamalı.**

### Eksen A — Kalıcı kurum rolü (kullanıcı düzeyi)
`User.role` (tekil FK — bir kullanıcı aynı anda tek rol taşır; `app/models/core.py:124,147`).

| UI adı | `role.name` (ham — MERKEZ biçim) | DB kullanıcı (2026-07-11) | Görünüm davranışı |
|--------|----------------------------------|---------------------------|-------------------|
| **Kurum Yöneticisi** | `tenant_admin` | 12 | Her şey + kurum yönetimi (Kullanıcılar/Kurumlar) |
| **Kurum Üst Yönetimi** | `executive_manager` | 110 | Tüm veriyi görür/değiştirir → sadeleştirme = **özet**, gizleme DEĞİL |
| **Kullanıcı** (personel) | `standard_user` | 323 | En sade taban; ekstralar liderlikle açılır |
| *(Platform Admin)* | `Admin` | 2 | Kurum dışı — Kokpitim ekibi; her şeyi bypass eder |

> **Merkez biçim kararı:** Ham `role.name` (İngilizce) merkez alınır. Gerekçe: aktif/modern katman (`app/`, `micro/`, `ui/`) zaten bunu kullanıyor (103 kullanım / 44 dosya) ve `app/constants/roles.py` kısmi tek-kaynak olarak mevcut. `sistem_rol` (Türkçe alias, `core.py:157-172`) legacy `main/`+`api/` katmanının kullandığı uyum katmanıdır; erimeye bırakılır, dokunulmaz.

> **Rol adı çeşitliliği notu:** `app/constants/roles.py::STANDARD_ROLES` `standard_user` yanında eski `"User"`/`"user"` de içeriyor. DB doğrulaması (2026-07-11): `standard_user`=323 kullanıcı, `User`=0 kullanıcı (ölü kayıt), `user`=rol bile yok. Yani bugün "personel = `standard_user`" güvenli. Yine de yeni görünürlük yardımcısı personel kontrolünü **tek string yerine `STANDARD_ROLES` seti** üzerinden yapmalı ki ileride eski rol yeniden atanırsa kırılmasın.

### Eksen B — Bağlamsal liderlik (kullanıcı × bağlam)
Kalıcı rolden **bağımsız** atama durumu. Zaten kodda kurulu; yeni tablo/alan gerekmez.

| Bağlam | Yönetici tabloları | Üye/izleyici | Hazır fonksiyon |
|--------|--------------------|--------------| ----------------|
| Süreç | `process_leaders`, `process_owners` | `process_members` | `user_is_process_leader()` — `micro/modules/surec/permissions.py:46-57` |
| Proje | `manager_id`, `project_leaders` | `project_members`, `project_observers` | `user_is_project_leader()` — `micro/modules/proje/permissions.py:103-110` |

**Mutabakat:** Süreçte "lider" ile "sahip (owner)" görünüm katmanında **tek kavram**: ikisi de "yönetici". `user_is_process_leader()` zaten `leader VEYA owner VEYA privileged` döndürüyor — UI bu fonksiyonu okur, ayrım kullanıcıya yansımaz.

**Privileged kısa-devre (çift durum):** `user_is_process_leader()` ve `accessible_processes_filter()` ikisi de önce `is_privileged(user)` kontrol edip erken `True`/tam sorgu dönüyor. Yani bir `executive_manager` aynı zamanda bir süreçte üye ise **çelişki yok — rol kazanır**. Yeni yardımcı bu kısa-devreye güvenmeli; çift durum için özel-durum kodu yazılmamalı.

---

## 3. Görünürlük kuralı

```
Bir menü/modül görünür  ⟺  PAKET açık  VE  (ROL uygun  VEYA  bağlamsal liderlik/üyelik uygun)
```

- **Paket = tenant düzeyi** (`tenant.package`; `User`'da paket YOK — `core.py:24`). Kurumun neye hakkı olduğunu belirler.
- **Rol/liderlik = kullanıcı düzeyi.** Paketin açtığı şeyin içinde kişinin neyi göreceğini belirler.
- İlişki **AND**: rol/liderlik ekseni her zaman paket ekseninin **alt kümesidir**. Paketi olmayan bir modülü hiçbir rol/liderlik açamaz. Bu yüzden **L1/L2/L3 paket kararları bu işten etkilenmez** — sadece paketin içi kişiye göre süzülür.
- Mevcut `get_accessible_modules` (`micro/core/module_registry.py:204-255`) zaten "paket `continue` → rol `continue`" ardışık AND iskeletini taşıyor; yeni kural bu iskeleti genişletir.

> **⚠️ Import yolu / dosya konumu (kodlayıcı dikkat):** Runtime import `from app_platform.core.module_registry import get_accessible_modules` (`app/__init__.py:264`) biçimindedir; `app_platform.core` bir **alias/shim**tir ve fiziksel dosya `micro/core/module_registry.py`'dir. "Tek merkezi genişletiyorum" derken **`micro/core/module_registry.py`** düzenlenir — `app_platform/` altında ayrı bir kopya aranmamalı.

---

## 4. Kim Neyi Görür — nihai tablo

| Menü | Kullanıcı (personel) | Üst Yönetim | Kurum Yöneticisi |
|------|:--------------------:|:-----------:|:----------------:|
| Masaüstüm | ✓ | ✓ | ✓ |
| Bireysel Performans | ✓ | ✓ | ✓ |
| Bildirimler · Ayarlar | ✓ | ✓ | ✓ |
| **Süreç Yönetimi** | **üye VEYA lider ise ✓** | ✓ | ✓ |
| **Proje Yönetimi** | **üye VEYA lider ise ✓** | ✓ | ✓ |
| Kurum Paneli | ✓ *(içerik zaten kapsama süzülüyor)* | ✓ | ✓ |
| **K-Radar / K-Analiz** | **lider ise ✓** (üye ise ✗ — bkz. §5) | ✓ kurum geneli | ✓ kurum geneli |
| Stratejik Planlama | ✗ | ✓ | ✓ |
| Savaş Odası | ✗ | ✓ | ✓ |
| Performans Analitiği | ✗ | ✓ | ✓ |
| Yönetim (Kullanıcılar / Kurumlar / Bildirim Merkezi) | ✗ | ✗ | ✓ |
| SaaS Paketler / API Dok. / Admin Araçları | ✗ | ✗ | ✗ *(yalnız Platform Admin)* |

> Tüm satırlar ayrıca **paket** kapısına tabidir (§3). Örn. Süreç modülü L1 pakette yoksa, tabloda "✓" olsa bile hiç kimse görmez.

### Karar gerekçeleri (kayıt)
- **Süreç/Proje = üye VEYA lider:** Üye olarak veri girecek kişi de menüyü görmeli (içeride: üye=veri girer, lider=yönetir; backend farkı zaten uyguluyor). Hiçbir ilişkisi yoksa menü gizli.
- **K-Radar = sadece lider (üye HARİÇ):** Süreç/Proje menüsünü *üye* olarak gören personel K-Radar/K-Analiz'i **görmez**. Gerekçe: K-Radar bir **yönetim/izleme aracıdır**, veri giriş aracı değil. Üye kişi işini Süreç Yönetimi ekranından yapar; kurumun/sürecin analiz panosu yönetici konumundakilere (lider + üst yönetim + kurum yöneticisi) aittir. Bu, "Süreç menüsünü gören K-Radar'ı da görür" beklentisini bilinçli olarak kırar — sadeleştirme hedefi gereği.
- **Kurum Paneli açık kalıyor:** `build_kurum_overview` içeriği privileged değilse `accessible_*` filtreleriyle zaten personelin kapsamına indiriyor; yönetim aksiyonları `can_edit_kurum` ile gizli. Ek iş gerektirmez.
- **Üst yönetim için gizleme yok:** "Tüm veriyi görür" ilkesi gereği menü kısıtlanmaz; onların sadeleştirmesi ayrı bir **özet dashboard** meselesidir (bu belgenin kapsamı dışında, ayrı iş).

---

## 5. K-Radar scope filtresi (Faz 1'e dahil)

**Menü görünürlüğü:** K-Radar/K-Analiz menüsü personele **yalnızca en az bir süreç/projede LİDER ise** açılır. Sadece üye olan (lider olmayan) personel bu menüyü **görmez** (§4 gerekçesi). Üst yönetim ve kurum yöneticisi her zaman görür.

**Karar (lider içeriği):** Lider K-Radar/K-Analiz'e girdiğinde:
- **Bölünebilir veri** (süreç KPI, proje EVM/risk) → yalnızca lider olduğu süreç/projelere göre **kişiye özel süzülür**.
- **Kurum-tekil veri** (SWOT, PESTEL, Porter, ana strateji listesi — süreç kapsamına bölünemez) → lidere **kurum geneli (okuma)** gösterilir.
- **UX borcu:** Aynı ekranda kapsam karışıklığı olmaması için kurum-tekil kartlara **"Kurum geneli" rozeti** eklenir. (Uygulama sırasında unutulmayacak.)
- Üst yönetim / kurum yöneticisi: her şey kurum geneli (bugünkü davranış).

**Fizibilite: ORTA (~1-2 gün).** Gerekçe:
- İstenen mantık zaten var: `accessible_processes_filter()` (`surec/permissions.py:89-101`), `accessible_projects_query()` (`proje/permissions.py:148-169`) — ve `kurum_overview.py` bunları **zaten kullanıyor** (pattern kanıtlı).
- Ama K-Radar servisi (`services/k_radar_service.py`) bunu hiç kullanmıyor; ~10+ fonksiyon `filter_by(tenant_id=...)` → `Process.id.in_(scoped_query)` biçimine çevrilmeli.
- `@cache.memoize` anahtarı `tenant_id`'den `(tenant_id, user_id)`'ye genişletilmeli.
- Kurum-tekil bileşenler (SWOT/PESTEL) bölünemez → kurum geneli kalır (yukarıdaki karar).

---

## 6. Kapsam sınırları (Faz 1'de YAPILMAYACAK)

- **Kart/bileşen düzeyi rol süzme:** Bugün kart görünürlüğü (`card_visible`/`component_visible`, `app/__init__.py:169-250`) yalnızca pakete bakıyor, role hiç bakmıyor. Faz 1 **modül/menü düzeyiyle** sınırlı (sidebar + launcher). Kart-içi rol enforcement ayrı ve daha büyük iş.
- **Üst yönetim özet dashboard'u:** "5 saniyede durum" ekranı ayrı bir iştir; bu belge menü görünürlüğüne odaklanır.
- **`sistem_rol` / legacy `main/`+`api/` temizliği:** Dokunulmaz, erimeye bırakılır.
- **Süreç lideri'ni kalıcı rol yapmak:** Gerekmez — liderlik bağlamsal atama olarak zaten doğru modelde.

---

## 7. Uygulama yaklaşımı (henüz plan değil — yön)

1. **Merkez:** `app/constants/roles.py` genişletilir (rol sabitleri + rol→görünürlük eşlemesi tek kaynak).
2. **Yardımcı:** `base.html`'deki dağınık `if role.name in [...]` blokları tek bir `can_see_menu(user, item)` benzeri yardımcıya iner; yardımcı hem rolü hem (gerektiğinde) liderlik/üyelik durumunu okur.
3. **Modül kapısı:** `get_accessible_modules` rol kuralı `_ROLE_RESTRICTED` genişletilerek veya döngüye ikinci AND koşulu eklenerek uygulanır — mevcut paket kapısıyla doğal AND'lenir.
4. **Süreç/Proje üyelik sinyali:** Sidebar'a "kullanıcının herhangi bir süreç/proje ilişkisi var mı" sorgusu eklenir (var olan `process_members`/`process_leaders` üzerinden).
5. **K-Radar scope:** §5'teki refactor.

---

## 8. Açık kararlar / notlar

- Faz 1 kapsamı: sidebar/launcher görünürlüğü **+** K-Radar scope refactor (kullanıcı onayıyla dahil edildi).
- Deploy: KURALLAR §8 + memory'deki L-paketleri kuralı gereği bu iş **yerelde birikir**, kullanıcı açıkça istemeden Test/Demo/Yayın'a çıkılmaz.
- **Fail-open riski (iki katmanlı — dikkatli okuyun):**
  1. `get_accessible_modules` (`micro/core/module_registry.py:204-255`) **hata halinde `None` DÖNMEZ.** Davranışı: `user is None` → `[]`; paket okuma hatası → `allowed_module_ids=None` (yalnız *paket kapısı* devre dışı = o katmanda fail-open) ama fonksiyon liste döndürmeye devam eder ve rol kapısı yine işler.
  2. Sidebar context processor `_inject_sidebar_modules` (`app/__init__.py:252-269`) **kendi `except` bloğunda `sidebar_module_ids=None`** döndürür (fail-open, satır ~268) — bu durumda `base.html` tüm modülleri gösterir.
  - **Karar gereği:** Yeni rol/liderlik AND koşulu **`get_accessible_modules` içine** (katman 1) eklenmeli, `_inject_sidebar_modules`'ün `except` fallback'ine değil. Böylece asıl mantık hatasında bile rol kapısı korunur; yalnızca beklenmedik exception'da (katman 2) menü açılır — bu mevcut kabul edilmiş davranıştır. Alternatif: katman 2 fallback'ini de "boş set = hiçbir ek modül" yapmak (daha güvenli ama daha agresif) — uygulama sırasında karar verilecek.

- **Platform `Admin` tenant-null güvenliği:** `get_accessible_modules:218` `role_name == "Admin"` → tüm `MODULES` (tenant'a hiç bakmadan). Yani Admin'in tenant'ı/paketi olmasa bile menü kırılmaz. Yeni rol kuralı bu erken-return'den SONRA çalışmalı; Admin bypass'ı bozulmamalı.
