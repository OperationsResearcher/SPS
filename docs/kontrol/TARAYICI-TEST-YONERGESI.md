# Tarayıcı test yönergesi — KalDer öğrenme paketleri P1–P10

> Hazırlayan: Claude, 2026-10-24. Dal: `claude/kalder-ogrenme-p10-terminoloji` (P1–P10'un hepsini içerir).
> Otomatik testler geçti (1207 geçti, 0 başarısız). **Bu yönerge, otomatik testlerin göremediği şeyleri gözle doğrulamak içindir.**
> Tahmini süre: ~60–75 dk. Sıra önemli: önce §0 hazırlık, sonra en riskli olan §4 (güvenlik/CSRF).

## 0. Hazırlık (bir kez)

1. **Dalı kontrol et:** `git branch --show-current` → `claude/kalder-ogrenme-p10-terminoloji`.
2. **`.env` iki satır** (Yerel `.env` dosyana, değerleri kendin yaz; ben dokunmadım):
   - `KOKPITIM_ENV=local` → yoksa Admin > Yedekleme "DB yedeği indir" ve Hata Kontrolü araçları Yerel'de de **kilitli** görünür (P8 bilinçli davranış değişikliği).
   - `SSO_ALLOWED_DOMAINS=` (isteğe bağlı) → Google SSO ile ilk kez gelen kullanıcıyı otomatik açmak istiyorsan alan adlarını yaz; boşsa otomatik açılmaz.
3. **Uygulamayı yeniden başlat:** `python pybasla.py` (auto-reload güvenilmez). Önce eski süreç kalmadığından emin ol: `netstat -ano | findstr :5001` tek dinleyici olmalı.
4. **Tarayıcıda her sayfada sert yenile: `Ctrl+F5`** (CSS/JS önbelleği eski kalmasın).
5. **Giriş:** bir **Admin** ve mümkünse bir **sıradan kullanıcı** hesabıyla (iki ayrı sekme/gizli pencere).
6. **Geliştirici araçları (F12)** açık tut; **Console** sekmesinde kırmızı hata ve **Network** sekmesinde 400/500 var mı bakacaksın.

> **Genel kural:** Her adımda Console'da kırmızı hata veya Network'te 400/500 görürsen **durup not al** (sayfa + adım + hata metni).

---

## 1. P1 — Görsel: kontrast, mobil taşma, odak

| # | Ne yap | Doğru sonuç |
|---|---|---|
| 1.1 | F12 → cihaz moduna geç (Ctrl+Shift+M), genişlik **375px**. Şu sayfaları aç: Süreç listesi, bir **Süreç Karnesi**, K-Rapor, Masaüstüm. | Sayfa **yatay kaydırılmıyor** (alt kenarda yatay çubuk yok). Geniş tablolar kendi içinde kayar. |
| 1.2 | Aynı 375px'te üst çubuğa bak. | Başlık sığıyor/kesiliyor (…), plan dönemi etiketi gizli, taşma yok. |
| 1.3 | Normal genişlikte **Tab** tuşuyla sol menüde (sidebar) gez. | Odaktaki öğede **açık mor/mavi halka** görünüyor. |
| 1.4 | Koyu temaya geç (varsa), boş durum metinleri ve gri rozetleri incele. | Metinler **okunuyor** (soluk/silik değil). |
| 1.5 | Bir sayfada kırmızı/yeşil butonlara (Sil / Onayla) bak. | Metin rengi koyu ve net okunuyor. |

**Dikkat edilecek:** P1'in `min-width:0` değişikliği bazı sayfaların genişliğini değiştirebilir. Bir sayfa **eskisinden dar/sıkışık** görünüyorsa not al.

## 2. P2 — Modal metin istemleri (alert/confirm → SweetAlert2)

| # | Ne yap | Doğru sonuç |
|---|---|---|
| 2.1 | **Bireysel karne** → bir PG'de **Veri Gir**. Alanı **boş** bırakıp Kaydet. | Alanın **altında kırmızı** "Değer boş bırakılamaz." çıkar, pencere kapanmaz. |
| 2.2 | Aynı pencerede bir değer yazıp **Enter**'a bas. | Kaydedilir (Enter = Kaydet). **Esc** pencereyi kapatır. |
| 2.3 | **SP > Dönemler** → bir dönemde **Mührü Aç**: gerekçeyi **boş** bırak. | Alan altında "Mühür açma gerekçesi zorunludur." çıkar. |
| 2.4 | **Mühürle**'de gerekçeyi **boş** bırakıp onayla. | Hata **çıkmaz** (gerekçe burada isteğe bağlı), işlem ilerler. ⚠ Gerçek veriyi mühürleme; iptal et. |
| 2.5 | **K-Radar > Stratejik analiz** (SWOT/TOWS/PESTEL) → bir maddeyi **düzenle**. | Küçük modal açılır, yazıp Kaydet çalışır; boş bırakınca madde değişmez. |
| 2.6 | **SP > Porter** ve bir **liste analizi**'nde **Madde ekle**. Boş gönder. | "Boş olamaz." alan altında çıkar. |
| 2.7 | **Admin > Alt Kurumlar** → parola sıfırla ve pasifleştir/aktifleştir. | Tarayıcının çirkin `confirm` kutusu **değil**, SweetAlert2 onayı çıkar. |

## 3. P3 — Erişilebilirlik

| # | Ne yap | Doğru sonuç |
|---|---|---|
| 3.1 | Herhangi bir formda **Tab** ile alanlar arasında gez. | Her alanda klavye odak halkası görünür. |
| 3.2 | Etiket eklenen sayfalarda bir **etikete tıkla** (örn. Ayarlar > Dil, Zamanlanmış Raporlar > Gün). | İlgili alan **odaklanır** (label↔alan bağlantısı çalışıyor). |
| 3.3 | Eklenen **id**'ler JS'i bozmamış olmalı: Admin > Kullanıcılar'da arama kutusu, Bildirimler'de filtreler, Analiz'de süreç seçimi, K-Rapor'da dönem seçimleri. | Hepsi eskisi gibi çalışıyor (yazınca filtreliyor / seçince yüklüyor). |

## 4. P8 — GÜVENLİK ve CSRF (en önemli bölüm)

P8 tüm `@csrf.exempt` muafiyetlerini kaldırdı; artık her POST/PUT/DELETE bir token ister. Bir akışta token eksikse **400** döner. Aşağıdaki **tüm kaydet/sil/ekle** akışlarını bir kez dene ve Network'te **400** arama.

| # | Akış (gerçekten bir şey kaydet/ekle/sil) | Doğru sonuç |
|---|---|---|
| 4.1 | **SP > Strateji:** ana strateji ekle, düzenle, sil. | 200, kayıt oluşur. |
| 4.2 | **SP > Girişim (initiative)** ekle/düzenle/sil. | 200. |
| 4.3 | **SP > SP-Proje** bağla/çöz. | 200. |
| 4.4 | **SP > Yönetici danışmanı / Exec advisor** bir işlem tetikle. | 200. |
| 4.5 | **SP > Çerçeveler** (BSC, SWOT, PESTEL, OKR) bir kayıt ekle. | 200. |
| 4.6 | **SP > Plan yılı / Replan tetikleyici / Senaryo** bir kayıt işlemi. | 200. |
| 4.7 | **Süreç > PG veri girişi** (karne'den). | 200. |
| 4.8 | **Admin > Kurulum içe aktarma (Setup import)** şablon yükle. | 200 (400 ise token eksik). |
| 4.9 | **Admin > Yedekleme:** "DB Yedeği İndir". `KOKPITIM_ENV=local` varsa **iner**, yoksa kilitli mesajı görürsün. | Beklenen davranış. |
| 4.10 | **Admin > Hata kontrolü:** "Tarama başlat". | Çalışır. |
| 4.11 | **Zamanlanmış raporlar** ayarı kaydet. | 200. |
| 4.12 | **Kule (Kokpitim kule/telemetri)** sayfasında bir işlem. | 200. |
| 4.13 | **Çıkış yapıp tekrar giriş**; 2FA açık bir hesapla giriş. | Normal çalışır. |
| 4.14 | (Varsa) **Google ile giriş:** TOTP'li kullanıcıda giriş sonrası **2FA ekranı** gelmeli. | 2FA sorulur. |
| 4.15 | **Demo:** `/demo/start`'ı adres çubuğundan elle aç (GET). | **Demo başlamamalı** (bir hata/izin yok sayfası görürsün — artık yalnız CSRF'li POST ile başlar; tam kod değişebilir). Demo kendi host'unda (demo.kokpitim.com) çalışır; Yerel'de farklı davranış normal. |
| 4.16 | **XSS denemesi:** bir kayıt adına `<img src=x onerror=alert(1)>` yaz (örn. girişim adı), kaydet, listeye bak. | Metin **düz yazı** görünür, `alert` **çıkmaz**. Sonra kaydı sil. |

> Bir akışta **400** çıkarsa: sayfa adresini, hangi butona bastığını ve Network sekmesindeki isteğin URL'sini bana yaz. Büyük olasılıkla o çağıran `fetch` kullanmıyor ya da sayfa `base.html`'i miras almıyor.

## 5. P4 — Çeviri (EN) ve sabit metinler

| # | Ne yap | Doğru sonuç |
|---|---|---|
| 5.1 | Sağ üstten dili **English** yap (veya adrese `?lang=en` ekle). Masaüstüm, Süreç, SP, K-Rapor, Admin'i gez. | Menü, başlık, düğme ve kart metinleri **İngilizce**. Rastgele Türkçe kalan **sabit metin** yok. |
| 5.2 | Kart başlıklarındaki **(i)** düğmesine tıkla (EN'de). | Açıklama İngilizce açılır. |
| 5.3 | Dili **Türkçe**'ye döndür. | Her şey Türkçe, **"KPI" yerine "PG"** yazıyor (K-Radar, K-Rapor, Karne, Holding ekranları dahil). |

Kalan Türkçe bir metin bulursan **sayfa + metin** olarak not et (yeni msgid olarak eklenecek).

## 6. P5 — Masaüstüm (yeni kartlar)

| # | Ne yap | Doğru sonuç |
|---|---|---|
| 6.1 | **Masaüstüm**'ü aç (Admin ile). | Üstte **"Temel akış"** şeridi: Strateji → Süreç & PG → Veri girişi → Karne & Rapor. Bağlantılar çalışır (Strateji → SP sayfası). |
| 6.2 | Sorumlu olduğun süreçlerde eksik veri varsa. | **"Veri girişi bekleyen PG'lerim"** kartı listelenir; "Gir" → ilgili süreç karnesi. Eksik yoksa kart **görünmez**. |
| 6.3 | Tamamlanmamış bir kurum/yeni kurum için. | **"İlk kurulum"** kontrol listesi (Admin'e); **"Gizle"** ile kapanır ve geri gelmez. |
| 6.4 | Sıradan kullanıcıyla Masaüstüm. | İlk kurulum kartı **yok**; Temel akış yetkine göre adımları gösterir. |

**Kart ID'leri (şu an yok, bilinçli):** yeni 3 kartın ID'si (MA21, MA22, TA01) için **önce Admin > Kart Yönetimi'nden kart keşfini çalıştır**, sonra: `python scripts/seed_masaustu_yeni_kartlar.py`. Çıktıda 3 satır "MA21/MA22/TA01" görmelisin; "ATLANDI" yazıyorsa keşif eksik. (Bunu sen karar verip koş; ben koşmadım.)

## 7. P6 — Inline stil → sınıf (31 sayfa): görsel karşılaştırma

Bu, otomatik testin en az görebildiği alan. **31 sayfa** değişti; her biri etiket etiket eşit doğrulandı ama gözle bakmak şart. Her sayfayı **açık + koyu tema** ve **375px**'te aç; **eski haliyle (main dalıyla) yan yana** karşılaştırırsan en iyisi.

Sayfalar (öncelik sırasıyla): **K-Rapor ana sayfa**, **Masaüstüm**, **SP Yönetici paneli (exec dashboard)**, **Süreç listesi**, Admin > Loglar, Admin > Hata kontrolü, Admin > Holding drilldown, Admin > Alt kurumlar, Raporlar > Sektörel detay, SP > Blue Ocean, Raporlar > Girişim balonu, Admin > Holding dashboard, **Bireysel karne**, Alt kurum kullanımı, K-Radar KS, SP > VRIO, SP ana sayfa, **Profil**, Zamanlanmış raporlar, Raporlar > PG-proje etki, Proje listesi, Yönetim özeti, Admin > Kullanıcılar, Ayarlar ana, SP > Dönemler, Admin > Yedekleme, Kılavuz oluşturucu, SP > Çeyreklik review, Admin > İstatistikler, Risk ısı haritası, K-Radar KP.

Her sayfada bak: **boşluklar/aralıklar, renkler, yazı boyutu, kart gölgeleri, hizalama, taşma**. Eskisinden farklı görüneni not al (sayfa + hangi öğe).

⚠ Özel dikkat: **Masaüstüm takvimi** yüksekliği eskisi gibi (~420px) olmalı (bilerek inline bıraktım).

## 8. P7 — Bağımlılık (yalnız bilgi, tarayıcıda test yok)

- Yeni `requirements.lock` **Python 3.12+** ister; **Docker (3.11) bununla kurulamaz**, Docker `requirements.txt` kullanır. Yayın'dan önce **Test'te Docker build + test şart** (`docs/kontrol/BAGIMLILIK-TARAMASI.md`).
- Gerçek zamanlı özellikler (bildirimler/canlı işbirliği) `python-socketio` güncellemesinden etkilenebilir: bir bildirim akışını canlı dene (iki sekme: birinde görev ata, diğerinde bildirim gelsin).

## 9. P10 — Karne/sapma farkları (karar bekliyor, test yok)

`docs/kontrol/KALDER-KARNE-MOTORU-KIYAS.md` — iki farkı bilerek **taşımadım** (rakam değiştirir). İş kararı sende: istemcide hesaplanan yüzde ve sapma formülü KalDer gibi tek kaynağa taşınsın mı?

---

## Sonuç formu (bana ilet)

Sorun bulursan her biri için tek satır: **`[Bölüm.No] sayfa · ne yaptın · ne gördün`**
Örn: `[4.2] SP > Girişim · "Kaydet"e bastım · 400 (Network: /sp/api/initiative)`

Hepsi temizse: **"Tarayıcı testi temiz"** yaz; sonra birleştirme (merge) ve Test ortamına gönderme adımlarına geçeriz (yalnızca sen "merge edelim / push'la / deploy" dediğinde).
