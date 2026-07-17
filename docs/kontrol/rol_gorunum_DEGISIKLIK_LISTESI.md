# Rol Görünüm Katmanı — Net Değişiklik Listesi (Faz 1–4)

> **Amaç:** "Kim artık neyi görüyor / göremiyor" — kod gerçeğinden çıkarılmış tam liste.
> **Tarih:** 2026-07-12 · **Dal:** `claude/rol-gorunum-katmani` · **Görevler:** TASK-242 … 247
> **İlgili:** [tam kontrol listesi](rol_gorunum_TAM_kontrol_listesi.html) · [tasarım belgesi](../paketler/ROL-GORUNUM-KATMANI.md)
>
> Aşağıdaki görünürlük tablosu spekülasyon değil; canlı sistemden (`can_see_module`,
> `default_landing_endpoint`) doğrudan çekildi.

---

## 1. Menü Görünürlüğü — Kim Neyi Görür

**Öncesi:** Herkes (paketi olan) neredeyse tüm menüyü görüyordu; rol filtresi yalnız 3 modülde vardı. Personel de Süreç / Proje / K-Radar menülerine bakıyordu.

**Sonrası:**

| Menü | İlişkisiz personel | Süreç üyesi | Süreç lideri | Üst yönetim | Kurum yön. | Platform admin |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Masaüstüm · Bireysel · Kurum Paneli · Ayarlar · Bildirim | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Süreç Yönetimi** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Proje Yönetimi** | ❌ | ❌ \* | ❌ \* | ✅ | ✅ | ✅ |
| **K-Radar / K-Analiz** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Stratejik Planlama** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Analitik · K-Rapor · Raporlar** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Yönetim Paneli** (Kullanıcılar / Kurumlar) | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **API Dokümantasyonu** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

\* Süreç üyesi/lideri **ayrıca bir projeye de** üye/lider ise Proje Yönetimi'ni görür. Örnek kullanıcılar projeye bağlı değildi.

**En önemli 3 değişiklik:**
- **İlişkisiz personel** artık Süreç / Proje / K-Radar / Strateji / Analitik / Yönetim menülerinin **hiçbirini görmüyor** — sade arayüz.
- **Süreç üyesi** Süreç Yönetimi'ni görüyor (veri girer) ama **K-Radar'ı görmüyor** (yönetim aracı).
- **Süreç lideri** olunca K-Radar / K-Analiz **açılıyor**.

> **İkinci eksen — paket:** Yukarısı "rol" eksenidir. Buna **paket** de AND'lenir: bir kurum örneğin K-Radar paketini almadıysa, üst yönetim bile o menüyü görmez (rolen görebilse de). Yani nihai kural = **paket açık VE rol/liderlik uygun**.

---

## 2. K-Radar Veri Kapsamı — Lider Ne Görür

**Öncesi:** K-Radar'a giren herkes kurum genelindeki **tüm** süreç/proje verisini görüyordu.

**Sonrası:**
- **Süreç / proje lideri** K-Radar'da yalnız **kendi lider/üye olduğu** süreç ve projelerin verisini görür (KPI'lar, skorlar, EVM, olgunluk, darboğaz, değer zinciri…).
- **Üst yönetim / kurum yöneticisi** kurum genelini görür (değişmedi).
- Bölünemeyen kurum-tekil veriler (SWOT, PESTEL, Porter, strateji, risk, rekabet) lidere de **kurum geneli** gösterilir.
- Lidere özel görünümde sayfa üstünde **bilgi şeridi** çıkar: *"Süreç ve proje kartları yalnızca sizin sorumlu olduğunuz süreç/projeleri gösterir. Strateji, rekabet ve risk kartları kurum genelidir."* — üst yönetime bu şerit **çıkmaz**.

**Somut örnek (doğrulandı):** Aynı kurumda lider K-Radar'da **3 KPI** görürken, üst yönetim **210 KPI** görüyor.

---

## 3. Route Güvenliği — URL ile Erişim

**Öncesi:** Menüde gizli bir sayfaya bile personel adres çubuğuna URL yazarak (örn `/k-radar`) girebiliyordu; sayfa açılıyordu.

**Sonrası:**
- Personel gizli bir sayfanın URL'sini elle yazarsa → **Masaüstü'ne geri atılır** + "Bu sayfaya erişim yetkiniz yok" uyarısı.
- Aynı sayfanın API'sini çağırırsa → **403** (yetkisiz).
- Yetkili kullanıcı (rolü + paketi uygunsa) → sayfa normal açılır.
- Kapsanan yollar: `/k-radar`, `/k-analiz`, `/analysis`, `/sp`.

---

## 4. Kart Görünürlüğü (Altyapı)

**Öncesi:** Kart görünürlüğü yalnız pakete bakıyordu, role hiç bakmıyordu.

**Sonrası:** **Görsel değişiklik YOK** (bilinçli karar). Artık "aynı sayfada bir kartı belirli role gizle" demek `app/constants/roles.py` içinde tek satır. Şu an liste boş — mekanizma hazır, gerçek ihtiyaç doğunca kullanılacak.

---

## 5. Login Sonrası İniş + Yeni Yönetim Özeti

**Öncesi:** Herkes login olunca aynı yere (launcher) düşüyordu.

**Sonrası:**

| Kullanıcı | Login sonrası iniş |
|---|---|
| İlişkisiz personel / üye / lider | launcher (değişmedi) |
| **Üst yönetim** | → **Yönetim Özeti** (yeni dashboard) |
| **Kurum yöneticisi** | → **Yönetim Özeti** (yeni dashboard) |
| Platform admin | launcher (dashboard tek-kuruma özel) |

**Yeni "Yönetim Özeti" dashboard'u** (yalnız üst yönetim + kurum yöneticisi) tek sayfada gösterir:
- **Kurum Skoru** + Strateji / Süreç / Proje / Bireysel alt skorları (renkli band)
- **Dikkat Gereken:** geciken görev / faaliyet / proje, düşük sağlıklı projeler, açık RAID
- **KPI Özeti:** toplam KPI, hedef-üstü %, açık risk
- **En Düşük Performanslı 5 Strateji** (yüzde barlı)
- Sol menüde ayrıca **"Yönetim Özeti"** linki (tekrar açmak için)

Sıfırdan hesaplama yok — mevcut 4 servis birleştirildi. Ekran salt-okunur; mevcut panolarla (Exec Dashboard, Savaş Odası, Masaüstü) çakışmaz.

---

## Değişen Dosyalar

**Yeni:**
- `app/constants/module_visibility.py` — merkezi görünürlük (`can_see_module` + route guard)
- `services/yonetim_ozeti_service.py` — dashboard veri birleştirici
- `ui/templates/platform/masaustu/yonetim_ozeti.html` — dashboard ekranı
- `ui/templates/platform/k_radar/_scope_notice.html` — kapsam bilgi şeridi
- `docs/paketler/ROL-GORUNUM-KATMANI.md` — tasarım belgesi

**Değişen:**
- `app/constants/roles.py` — kart-rol haritası + yardımcılar
- `micro/core/module_registry.py` — modül kapısına rol AND koşulu
- `platform_core/__init__.py` — route seviyesi yetki guard
- `app/utils/tenant_scope.py` — rol bazlı login inişi
- `ui/templates/platform/base.html` — Yönetim Özeti menü linki
- `app/__init__.py` — `card_visible`'a rol kapısı
- `services/k_radar_service.py` + `micro/modules/k_radar/routes_*.py` — lider scope
- `micro/modules/surec/permissions.py` + `micro/modules/proje/permissions.py` — liderlik EXISTS yardımcıları
- `translations/{tr,en}` — yeni UI metinleri

**Silinen:** `ui/templates/platform/k_radar/index.html` (ölü template)

---

## Bilinçli Sınırlar (hata değil)

- **Paket kısıtı role baskındır:** K-Radar/Analitik paketi olmayan kurumda üst yönetim bile o menüyü görmez.
- **Faz 3 görsel değişiklik yapmaz** — yalnız altyapı (harita boş).
- **Platform admin** login'de launcher'a iner (Yönetim Özeti tek kuruma özel, admin çok-kurumlu).
- Gelecekte ele alınabilecekler: kart-içi rol süzmenin fiilen doldurulması, route guard'ın diğer modüllere yayılması.
