# KULE — Kokpitim Yardımcı Sistemi Tanım Dosyası

> **Sürüm:** 1.0
> **Yürürlük:** 2026-05-25
> **Kimlik:** Kule, Kokpitim'in kullanıcı yardımcısıdır. Tur sihirbazı, bağlam yardımı ve (faz 2'de) yapay zekâ destekli soru-cevap sağlar.
> **Bu dosya tek gerçek kaynaktır.** "Kulenin X'ini düzelt" denildiğinde buraya bakılır.

---

## 1. Kimlik ve Metafor

| | |
|---|---|
| **İsim** | Kule |
| **Rol** | Kullanıcının yanındaki sakin, mantıklı, yol gösteren yardımcı |
| **Metafor** | Hava trafik kulesi — pilot (kullanıcı) ile yer kontrolü arasındaki kanal. Kokpitim'in *kokpit* metaforuyla doğal eşleşir. |
| **Hitap şekli** | "Kule" tek başına özne olarak kullanılır. Cinsiyet yok. "O" zamiri. |
| **Kullanıcıya seslenme** | Sen-dili. İsmiyle: "Talat, …" |
| **Yetki** | Kule **önerir**, kullanıcı **karar verir**. Asla buyurgan değildir. |

---

## 2. Görsel Karakter

### 2.1 Form
- Minik, 3-4 katlı stilize bir hava trafik kulesi
- Üst katta cam kabin (yarı şeffaf), kabinde tek bir ışık noktası
- Kabinin üstünde yavaşça dönen iki ince anten
- Gövde silindirik, alt taban hafif geniş
- Soft drop-shadow, hafif yuvarlatılmış köşeler

### 2.2 Renk Paleti
| Eleman | Renk | Token |
|---|---|---|
| Gövde | Beyaz / açık gri | `#f8fafc` / `#e2e8f0` |
| Cam kabin | Cam mavisi | `#dbeafe` |
| Anten | Lacivert | `#1e293b` |
| Aksan / ana renk | Kokpitim primary | `var(--color-primary)` = `#4f46e5` |
| **Işık — sakin (varsayılan)** | Yeşil | `#10b981` |
| **Işık — öneri var** | Sarı | `#f59e0b` |
| **Işık — uyarı / dikkat** | Kırmızı | `#dc2626` |
| **Işık — konuşurken** | Yanıp söner (animasyon) | — |

### 2.3 Boyut ve Yerleşim
| Bağlam | Boyut | Konum |
|---|---|---|
| Sağ alt köşede sürekli simge | 56×56 px | `position:fixed; right:24px; bottom:24px` |
| Tur açıkken yanında küçük simge | 32×32 px | Driver.js popover'ının yanında |
| İlk karşılama baloncuğu | 80×80 px | Sayfa ortasında / kart başında |
| Mobil | 44×44 px | `right:16px; bottom:16px` |

### 2.4 Animasyonlar (zorunlu olanlar)
- **Antenin dönüşü:** `8s linear infinite` (çok yavaş; "düşünüyorum" hissi yaratmaz)
- **Konuşurken kabin ışığı:** `1s ease-in-out infinite` yanıp sönme
- **Yükleniyor durumu:** Anten dönüşü hızlanır (`2s`)
- **Yeni bildirim:** Kabin ışığı sarıya döner + bir kez hafif zıplar (`bounce 0.6s`)

### 2.5 SVG Asset Konumu
- Master SVG: `ui/static/platform/img/kule.svg`
- İnline kullanım için Jinja2 makro: `ui/templates/platform/_macros/kule.html`
- Durum varyantları renk override ile (CSS değişkeni)

---

## 3. Konuşma Tonu

### 3.1 Genel İlke
- **Sen-dili**, samimi ama mesafeli (laubali değil)
- Cümleler kısa: 1-2 cümle, gerekiyorsa madde madde
- Jargon kullanıldığında **parantez içinde** açıklanır
- "Sanırım", "belki" yerine **net** ifade: "Önce bunu yapalım."
- **Buyurgan değil**, davet edici: "X'i deneyelim mi?" / "Bir sonraki adımda Y görelim mi?"

### 3.2 İlk hitap kalıbı
> 📡 **Kule'den Talat'a:** [mesaj]

Tur içi adımlarda **prefix gerekmez**, doğrudan mesaj verilir.

### 3.3 Onay/seçenek kalıbı
İki butonlu sunum tercih edilir:
- `[Devam]` / `[Şimdi değil]`
- `[Başlayalım]` / `[Atla]`
- `[Anladım]` / `[Tekrar göster]`

### 3.4 Yasaklar
- ❌ "Üzgünüm…", "Maalesef…" — Kule pasif değildir
- ❌ "Sistem hatası" — kullanıcıya teknik dil yok
- ❌ Emoji bombardımanı — adım başına en fazla 1 emoji
- ❌ "Ben yapay zekayım" itirafı — Kule bir karakterdir
- ❌ Korku dili: "yanlış yaparsanız…", "dikkat etmezseniz…"

### 3.5 Örnek mikro-kopya

**Karşılama (ilk giriş):**
> Hoş geldin Talat. Eskişehir Motor Sanayi için planlama yolculuğuna birlikte başlayalım mı?
> [Rotayı çiz] [Sonra]

**Adım açıklaması:**
> Buradan kurumunuzun vizyonunu tanımlıyoruz. Vizyon = 3-5 yıl sonra olmak istediğiniz yer.

**Boş durum:**
> Henüz girişimin yok. Bir girişim, vizyona ulaşmak için yapacağın büyük iş paketidir.
> [İlk girişimi oluştur]

**Hatırlatma:**
> Plan dönemini henüz aktifleştirmedin. Hazır olunca buradan başlayabilirsin.

---

## 4. Teknik Mimari

### 4.1 Veri Modeli
```
user_tour_progress
├── id           (PK)
├── user_id      (FK → users.id)
├── tour_key     (str, ör: "masaustu", "sp_menu")
├── status       (enum: 'pending' | 'completed' | 'dismissed')
├── completed_at (datetime, nullable)
├── dismissed_at (datetime, nullable)
├── seen_count   (int, default 0)
└── updated_at   (datetime)

UNIQUE(user_id, tour_key)
```

### 4.2 İçerik Formatı
- Konum: `docs/tours/<tour_key>.yaml`
- Şema:
```yaml
key: masaustu
title: "Masaüstü turu"
audience: ["tenant_admin", "executive_manager", "Admin"]  # boş ise herkes
auto_show: true            # ilk açılışta otomatik
welcome:
  title: "Hoş geldin Talat"
  body: "Eskişehir Motor Sanayi için rotayı birlikte çizelim."
  cta_primary: "Başlayalım"
  cta_secondary: "Sonra"
steps:
  - target: '[data-tour="masaustu-launcher-sp"]'
    title: "Stratejik Planlama"
    body: "Buradan kurumunuzun vizyonunu, stratejilerini ve girişimlerini yöneteceksin."
    placement: "bottom"
  - target: '[data-tour="masaustu-launcher-surec"]'
    title: "Süreç Yönetimi"
    body: "Stratejileri günlük süreç ve KPI'lara bağladığımız yer."
finale:
  title: "Hazırsın"
  body: "Turu istediğin zaman sağ alttaki Kule'den tekrar başlatabilirsin."
```

### 4.3 Selektör Kuralı
- Adım hedefleri için **CSS class değil, `data-tour` attribute** kullanılır
- Format: `data-tour="<modul>-<eleman>"` (kebab-case)
- Örnek: `data-tour="sp-card-girisimler"`, `data-tour="masaustu-launcher-sp"`
- Bu, UI refaktörlerinde tur kırılmasını önler

### 4.4 Backend Endpoint'ler
| Method | URL | Amaç |
|---|---|---|
| GET | `/api/kule/tour/<key>` | Tur YAML'ını JSON olarak döner + kullanıcı progress |
| POST | `/api/kule/tour/<key>/complete` | Tur tamamlandı işaretle |
| POST | `/api/kule/tour/<key>/dismiss` | Tur atlandı işaretle (auto_show kapanır) |
| POST | `/api/kule/tour/<key>/restart` | Progress sıfırla, tekrar göster |
| GET | `/api/kule/state` | Kullanıcı için tüm tur durumları (header'da Kule rozeti için) |

### 4.5 Frontend Bileşen
- Konum: `ui/static/platform/js/kule.js` + `ui/static/platform/css/kule.css`
- Bağımlılık: Driver.js (CDN veya `static/vendor/driver.js/`)
- Global API:
  ```js
  Kule.init({ tourKey: "masaustu" })   // Sayfa açılışta çağrılır
  Kule.start(tourKey)                   // Manuel başlatma
  Kule.toggle()                         // Sağ alt simgeye tıklayınca
  Kule.help()                           // Faz 2: AI soru-cevap kutusu
  ```

### 4.6 Otomatik Açılış Mantığı
1. Sayfa yüklenir → `Kule.init({tourKey})` çalışır
2. `GET /api/kule/tour/<key>` ile kullanıcı progress alınır
3. `status == 'pending'` ve `auto_show == true` ise karşılama baloncuğu açılır
4. Kullanıcı "Başlayalım" derse Driver.js turu başlar
5. Tur sonunda `POST /api/kule/tour/<key>/complete` çağrılır
6. "Şimdi değil" derse `dismiss` çağrılır → bir daha otomatik açılmaz
7. Sağ alttaki Kule her zaman yeniden başlatma için orada

---

## 5. Kapsam ve Sıralama

### 5.1 Faz 1 — Sihirbaz Turları (mevcut sprint serisi)
**Persona: Talat Konuk — Eskişehir Motor Sanayi, kurum yöneticisi**

| Sprint | Sayfa | Tur key | Durum |
|---|---|---|---|
| S1 | Altyapı (DB, Driver.js, Kule SVG, global ? butonu) | — | — |
| S1 | Masaüstü | `masaustu` | İlk tur |
| S2 | Stratejik Planlama hub | `sp_menu` | |
| S2 | SP Genel Bakış | `sp_overview` | |
| S2 | Plan Dönemleri | `sp_plan_years` | |
| S2 | Girişimler | `sp_initiatives` | |
| S3 | Çeyreklik Değerlendirme | `sp_quarterly` | |
| S3 | Hoshin X-Matrisi | `sp_xmatrix` | |
| S3 | VRIO Analizi | `sp_vrio` | |
| S3 | Mavi Okyanus | `sp_blue_ocean` | |
| S3 | Senaryolar | `sp_scenarios` | |
| S3 | Yeniden Planlama Tetikleyicileri | `sp_replan` | |
| S3 | Yönetici Paneli | `sp_exec_dashboard` | |
| S4 | Süreç Yönetimi | `surec` | |
| S4 | K-Radar | `k_radar` | |
| S4 | Bireysel Performans | `bireysel` | |
| S4 | Analiz | `analiz` | |
| S5 | Kullanıcı Yönetimi | `admin_users` | |
| S5 | Kurum Yönetimi | `admin_tenants` | |
| S5 | Alt Kurum Yönetimi | `admin_sub_tenants` | Bayi/Holding |
| S5 | Holding Dashboard | `holding_dashboard` | |

### 5.2 Faz 2 — Akıllı Yardım (sonraki proje)
- Sağ alttaki Kule'ye tıklayınca soru-cevap kutusu açılır
- Backend: sayfa key + soru → LLM (mevcut AI Gateway) → cevap
- RAG kaynağı: aynı YAML dosyaları + DB durumu (kullanıcının verisi)
- Konuşma geçmişi `kule_conversations` tablosunda

### 5.3 Persona Kapsamı
- **Şu an:** Sadece kurum yöneticisi (tenant_admin, executive_manager, Admin) turları
- **Sonra:** Aynı YAML kalıbıyla `audience: ["user", "team_lead", "process_owner"]` için ayrı kısa turlar

---

## 6. Bakım ve Geliştirme Kuralları

### 6.1 Yeni tur ekleme
1. `docs/tours/<key>.yaml` oluştur
2. Hedef sayfa template'ine `data-tour="..."` attribute'ları ekle
3. Page template'in `{% block scripts %}` içinde `Kule.init({tourKey: "<key>"})` çağır
4. UI Terminoloji ve dil kurallarına uy (`docs/UI-TERMINOLOJI.md`)

### 6.2 İçerik dili
- Tüm tur içerikleri Türkçedir
- Kod örnekleri, jargon → parantez içi gloss
- Persona ismi `welcome.body` içinde **dinamik:** `{{ user.first_name }}` ile değiştirilir

### 6.3 Tur kırıldığında
- UI değişikliği `data-tour` attribute'unu kaldırırsa tur kırılır
- Hata Driver.js console'a düşer + Kule sessizce kapanır (kullanıcıya hata göstermez)
- Logger: `app.logger.warning("[kule] target missing: <selector>")`

### 6.4 İçerik üretim süreci
1. **AI taslak:** Sayfa amacı + Talat persona verilir, AI YAML taslağı üretir
2. **İnsan onayı:** Kullanıcı (kod sahibi) okur, tonu düzeltir, gerekirse adım atar/ekler
3. **Yayınlama:** YAML dosyası `docs/tours/`'a eklenir, commit

---

## 7. Hızlı Referans — "Kule'nin X'ini düzelt" demek için

| Demek istediğin | Buraya bak |
|---|---|
| "Kulenin yüzünü değiştir" | §2 Görsel Karakter |
| "Kule farklı konuşsun" | §3 Konuşma Tonu |
| "Kule şu sayfada da çıksın" | §5.1 Kapsam tablosu |
| "Kulenin rengi farklı olsun" | §2.2 Renk Paleti |
| "Kule otomatik açılmasın" | §4.6 Otomatik Açılış Mantığı |
| "Bu turu yeniden yazalım" | `docs/tours/<key>.yaml` |
| "Kule'ye yeni özellik ekle" | §5.2 Faz 2 |
| "Telif riski var mı?" | İsim mitolojik/jenerik — `volkan` ile karışmaz çünkü `Kule` jenerik Türkçe |

---

## 8. Açık Sorular / İlerideki Kararlar

- [ ] Mobil tasarımda Kule'nin yeri tablet/küçük ekranda nasıl davranacak?
- [ ] Çoklu dil — `body_tr` / `body_en` ayrımı ne zaman?
- [ ] AI köprüsü için sayfa bağlamı nasıl serileştirilecek (mevcut veri + sayfa key)?
- [ ] Kule sesli mi konuşacak (TTS) — uzun vadede?
- [ ] "Kule'yi tamamen kapat" tercihi profil sayfasına eklenmeli mi?

---

**İlk içerik üretimi Talat Konuk persona'sı üzerinden yapılır. Bu dosyada referans verilen örnekler ve mikro-kopya, ilk turların temel taslaklarıdır.**
