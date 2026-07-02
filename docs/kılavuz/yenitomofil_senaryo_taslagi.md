# YeniTomofil Otonom Çekim Senaryosu + Sesli Anlatı (v4.0 — Bölüm 1, birleşik)

Bu belge, **Kılavuz & Video Oluşturucu** paneli çalıştırıldığında Playwright'in sıfır veritabanlı `YeniTomofil` kurumu üzerinde otonom gerçekleştireceği adımların **ve** o adımlarda okunan **sesli anlatının** tek kaynağıdır.

> **v4.0 değişikliği:** Senaryo ile anlatı metni **tek dosyada** birleştirildi. Her alt-bölümün altında "ekranda ne oluyor" (adımlar) ve "ne anlatılıyor" (🎙️ beat) yan yana durur. Böylece bir adım değişince ikisi birlikte güncellenir.

> **Şu anki kapsam:** Yalnız **Bölüm 1**. Diğer bölümler (SP, Süreç/PG, Proje, K-Radar) en altta "Sonraki Bölümler" olarak saklı; sıraları gelince buraya eklenecek.
>
> **Çalışma kuralı (KURALLAR §9):** Önce bu dosyada mutabık kalınır, **sonra** koda yansıtılır.

> **Roller (terminoloji):** `tenant_admin` = **Kurum Yöneticisi** (YeniTomofil admini) · `executive_manager` = **Kurum Üst Yönetimi** · `standard_user` = **Kurum Kullanıcısı**.

> **Sesli anlatı (🎙️):** edge-tts, ses `tr-TR-AhmetNeural`. Her **beat** (B01…B15) bir çekim adımına bağlıdır; çekimde o adımdan sonraki bekleme, beat'in ses süresi kadardır → ekran ile anlatı kendiliğinden hizalanır. Beat metni kısaldıkça o adım kısalır. Kod karşılığı: `app/services/kilavuz_olusturucu_executor.py` içindeki `BEATS` sözlüğü (ID'ler birebir aynı).

---

## 📹 Bölüm 1: Giriş, Kurum ve Kullanıcı Yapılandırması

**Amaç:** Sisteme giriş, kurumun temel kimlik/ayarları, farklı tipte kullanıcıların oluşturulması ve rol bazlı yetki/ayar farklarının gösterilmesi.

**Çıktılar:** Video `1_giris_kurum_kullanici.mp4` (sesli) · Ekran görüntüleri `01`–`15`.

---

### 1.1 — Sistem Girişi ve Masaüstü (Launcher)

**Görseller:** `01_login.png`, `02_launcher.png`

1. `http://127.0.0.1:5001/login` açılır.
2. E-posta `admin@yenitomofil.local`, şifre `YeniTomofil!123` (bu hesap **Kurum Yöneticisi**).
3. [Görsel Odak]: **Giriş Yap** butonu kırmızı çerçevelenir (`01_login.png`), tıklanır.
4. **Masaüstü (Launcher)** yüklenir; modül kartları görünür (`02_launcher.png`).

> 🎙️ **B00** (açılış — `01_login` ekranında): Merhaba, Kokpitim'e hoş geldiniz. Veriye dayalı kararlar, geleceği şekillendiren stratejiler. Kurumsal performansınızı en üst seviyeye taşıyın.
> 🎙️ **B01** (`01_login`): Kokpitim'e giriş yaparak başlıyoruz. YeniTomofil kurumunun yöneticisi olarak e-posta ve şifremizi giriyor, Giriş Yap butonuna tıklıyoruz.
> 🎙️ **B02** (`02_launcher`): Karşımıza Masaüstü geliyor. Buradan kurumun tüm modüllerine; stratejik planlama, süreçler, projeler, K Raporlar ve K Analitik modüllerine tek noktadan erişiyoruz.

---

### 1.2 — Kurum Yönetimi (Kurum Bilgileri ve Ayarları)

**Sayfa:** `/kurum/ayarlar` · **Görseller:** `03_kurum_form.png`, `04_kurum_kaydedildi.png`

> Kullanıcılar eklenmeden önce kurumun **temel kimliği** tanımlanır. Bu sayfaya yalnız **Kurum Yöneticisi / Üst Yönetim** erişir.

1. **Kurum Paneli → Kurum Ayarları** (`/kurum/ayarlar`) açılır. **Kurum Bilgileri** formu doldurulur:
   - **Kurum Adı:** `YeniTomofil Otomotiv Sanayi ve Ticaret A.Ş.`
   - **Sektör:** `Otomotiv — Elektrikli Araç Üretimi` · **Vergi No:** `1234567890`
   - **Adres:** `Organize Sanayi Bölgesi 5. Cadde No:12, Bursa`
   - **Telefon:** `0224 555 12 34` · **E-posta:** `info@yenitomofil.com` · **Website:** `www.yenitomofil.com`
2. Alanlar dolunca sayfa **başa kaydırılır** (gezinme olmasın), doldurulmuş form gösterilir (`03_kurum_form.png`).
3. **K-Vektör** toggle'ı (görünür anahtar) etkinleştirilir; **Plan Yılı** kapalı bırakılır.
4. **Kaydet** (AJAX — sayfa yenilenmez) ile kurum bilgileri + K-Vektör kalıcı olarak yazılır.
5. **Logo:** `docs/kokpitim-logo.png` seçilip yüklenir (yükleme başarıda sayfa yenilenip kayıtlı bilgileri + logoyu gösterir). Kayıtlı hâl `04_kurum_kaydedildi.png`.

> **Not (teknik):** K-Vektör input'u CSS ile gizli toggle'dır; Playwright `check()` yerine **görünür label'a tıklanır** (aksi halde 30 sn actionability retry → üst↔toggle zıplaması). Logo yükleme sayfayı yenilediği için kayıt **logodan önce** yapılır.

> 🎙️ **B03** (`03_kurum_form`): İlk işimiz kurumun kimliğini tanımlamak. Kurum Ayarları sayfasından kurum adını, sektörünü, vergi numarasını ve iletişim bilgilerini giriyoruz.
> 🎙️ **B04** (`04_kurum_kaydedildi`): K-Vektör modülünü etkinleştiriyor, kurum bilgilerini kaydediyor ve logomuzu yüklüyoruz.

---

### 1.3 — Kullanıcı Yönetimi ve Yetkilendirme

**Sayfa:** `/admin/users` · **Görseller:** `05_users_page`, `06_user_form_fields`, `07_user_form_role`, `08_std_user_form`, `09_bulk_import`, `10_users_table_full`

1. **Yönetim → Kullanıcılar** (`/admin/users`) açılır; tablo, arama, **Kullanıcı Ekle**, **Toplu İçe Aktar**, **Örnek Excel İndir** tanıtılır (`05_users_page`).
2. **Kullanıcı Ekle** formu alan alan tanıtılır (`06_user_form_fields`): **Ad**, **Soyad**, **E-posta** (zorunlu, giriş kimliği), **Şifre** (boşsa otomatik), **Rol**.
3. **Rol** açılır listesi (`07_user_form_role`): **Kurum Üst Yönetimi** / **Kurum Kullanıcısı**.
4. **2 Kurum Üst Yönetimi** form ile eklenir: `Selin Demir`, `Mert Kaya`.
5. **10 Kurum Kullanıcısı** — ilk **2'si form ile** (`08_std_user_form`), kalan **8'i Toplu İçe Aktarma (Excel)** ile (`09_bulk_import`):

   | # | Ad Soyad | E-posta | Departman | Yöntem |
   |---|---|---|---|---|
   | 1 | Ahmet Yılmaz | ahmet.yilmaz@yenitomofil.local | Üretim Müh. | Form |
   | 2 | Ayşe Şahin | ayse.sahin@yenitomofil.local | Kalite Kontrol | Form |
   | 3 | Burak Çelik | burak.celik@yenitomofil.local | AR-GE | Excel |
   | 4 | Deniz Aydın | deniz.aydin@yenitomofil.local | Satış | Excel |
   | 5 | Elif Korkmaz | elif.korkmaz@yenitomofil.local | İnsan Kaynakları | Excel |
   | 6 | Furkan Arslan | furkan.arslan@yenitomofil.local | Lojistik | Excel |
   | 7 | Gizem Yıldız | gizem.yildiz@yenitomofil.local | Finans | Excel |
   | 8 | Hakan Doğan | hakan.dogan@yenitomofil.local | Bakım | Excel |
   | 9 | İrem Koç | irem.koc@yenitomofil.local | Pazarlama | Excel |
   | 10 | Kerem Öztürk | kerem.ozturk@yenitomofil.local | Satınalma | Excel |

6. [Görsel Odak]: Tüm kullanıcılar — **1 Yönetici + 2 Üst Yönetim + 10 Kullanıcı = 13 kayıt** (`10_users_table_full`).

**Rol yetkileri (özet):**

| Yetki | Yönetici | Üst Yönetim | Kullanıcı |
|---|:---:|:---:|:---:|
| Kullanıcı ekle/düzenle | ✅ | ✅ | ❌ |
| Strateji / Süreç / Proje | ✅ | ✅ | ❌ |
| Kurum ayarları (bilgi, SMTP) | ✅ | ✅ | ❌ |
| Atandığı işe veri girişi | ✅ | ✅ | ✅ *(lider/üye/atanan)* |
| Kişisel ayarlar (profil, tema, 2FA) | ✅ | ✅ | ✅ |
| Platform Yönetimi (Admin Araçları) | ❌ | ❌ | ❌ |

> 🎙️ **B05** (`05_users_page`): Sırada ekibi tanımlamak var. Yönetim menüsünden Kullanıcılar sayfasını açıyoruz. Burada kullanıcıları tek tek ekleyebilir, ya da Toplu İçe Aktar ile Excel'den onlarca kullanıcıyı bir anda oluşturabiliriz.
> 🎙️ **B06** (`06_user_form_fields`): Kullanıcı ekleme formu sade: Ad, Soyad, zorunlu olan ve giriş kimliği işlevi gören E-posta, isteğe bağlı Şifre ve Rol. Şifreyi boş bırakırsak sistem güvenli bir geçici şifre üretir.
> 🎙️ **B07** (`07_user_form_role`): Rol alanında iki seçenek var: stratejik kararlara ve yönetime katılan Kurum Üst Yönetimi, ve standart çalışan rolündeki Kurum Kullanıcısı.
> 🎙️ **B08** (form ekleme): İki üst yöneticiyi, Selin Demir ve Mert Kaya'yı; ardından ilk iki kurum kullanıcısını form üzerinden ekliyoruz.
> 🎙️ **B09** (`09_bulk_import`): Kalan sekiz kullanıcıyı ise Toplu İçe Aktarma ile ekliyoruz. Örnek Excel şablonunu doldurup yüklüyoruz; sistem her satırı otomatik olarak Kurum Kullanıcısı rolüyle oluşturuyor.
> 🎙️ **B10** (`10_users_table_full`): Sonuçta bir Kurum Yöneticisi, iki Üst Yönetim ve on Kurum Kullanıcısı; toplam on üç kişilik ekibimiz hazır. Kısaca yetkiler şöyle: Yönetici ve Üst Yönetim strateji, süreç, proje ve kurum ayarlarını yönetir; Kurum Kullanıcısı ise yalnızca kendine atanan işleri görür ve kişisel ayarlarını değiştirir.

---

### 1.4 — Farklı Rollerle Giriş ve Kullanıcı Ayarları

**Görseller:** `11_exec_menu`, `12_exec_eposta_ayarlari`, `13_user_menu`, `14_user_hesap_ayarlari`, `15_profil`

**A) Kurum Üst Yönetimi (Selin Demir):**
1. Çıkış, `selin.demir@yenitomofil.local` ile giriş.
2. [Görsel Odak]: Sol menü (`11_exec_menu`) — **görünür:** Stratejik Planlama, Kurum Paneli, Kullanıcılar, Kurumlar; **gizli:** SaaS Paketler, Admin Araçları.
3. **Ayarlar → E-posta (SMTP)** (`12_exec_eposta_ayarlari`): Sunucu, Port, Kullanıcı, Şifre, Gönderici, STARTTLS/SSL.

**B) Kurum Kullanıcısı (Ahmet Yılmaz):**
4. Çıkış, `ahmet.yilmaz@yenitomofil.local` ile giriş.
5. [Görsel Odak]: Sol menü (`13_user_menu`) — **kısıtlı**; Stratejik Planlama, Kullanıcılar, Kurumlar gizli.
6. **Ayarlar → Hesap Ayarları** (`14_user_hesap_ayarlari`): bildirim tercihleri, Dil, Saat Dilimi, Tarih Formatı, Tema.
7. **Profil** (`15_profil`): Ad/Soyad, Telefon, Ünvan, Departman, Profil Fotoğrafı, Şifre, 2FA.

> 🎙️ **B11** (`11_exec_menu`): Şimdi bu hesaplarla giriş yapıp farkları görelim. Önce Üst Yönetim, Selin Demir ile giriyoruz. Menüde Stratejik Planlama, Kurum Paneli ve Kullanıcılar görünüyor.
> 🎙️ **B12** (`12_exec_eposta_ayarlari`): Üst Yönetim, kurum ayarları kapsamında e-posta sunucusu, yani SMTP yapılandırmasına erişebilir. Sunucu, port, kullanıcı ve gönderici bilgileri buradan girilir.
> 🎙️ **B13** (`13_user_menu`): Şimdi standart bir Kurum Kullanıcısı, Ahmet Yılmaz ile giriyoruz. Menünün belirgin biçimde kısaldığını görüyoruz; stratejik planlama ve kullanıcı yönetimi artık gizli.
> 🎙️ **B14** (`14_user_hesap_ayarlari`): Kurum Kullanıcısı yalnızca kişisel ayarlarına erişir: bildirim tercihleri, dil, saat dilimi, tarih formatı ve açık-koyu tema.
> 🎙️ **B15** (`15_profil`): Profil sayfasından ad-soyad, telefon, ünvan, profil fotoğrafı, şifre değişikliği ve iki adımlı doğrulama yönetilir. Özetle: Üst Yönetim kurumu yönetirken, Kurum Kullanıcısı kendi profilini ve tercihlerini düzenler.

---

## 🔧 Teknik karşılık (mutabakat sonrası kodlanır)

1. **TTS:** Beat metinleri edge-tts (`tr-TR-AhmetNeural`) ile mp3'e çevrilir; süre ffprobe ile ölçülür. (Playwright loop'uyla çakışmaması için TTS ayrı thread'de `asyncio.run` ile çalışır.)
2. **Senkron:** Çekimde ilgili adımdan sonra `_beat("BXX")` çağrısı, sesin video offset'ini kaydeder ve ses süresi kadar bekler.
3. **Birleştirme:** ffmpeg `adelay`+`amix` ile her ses kendi offset'inde videoya bindirilir → H.264 + AAC mp4 (`+faststart`).
4. **Düşüş güvenliği:** edge-tts/ffmpeg/internet yoksa adım atlanır; sessiz mp4 üretilir (akış bozulmaz). Yalnız **Yerel**'de çalışır (`_is_local`).

---

## ⏳ Sonraki Bölümler (sırası gelince bu dosyaya eklenecek)

- **Bölüm 2: Sıfırdan Stratejik Planlama (SP)** — vizyon/misyon, ana/alt strateji.
- **Bölüm 3: Süreç Yönetimi ve Performans Göstergeleri (PG/KPI).**
- **Bölüm 4: Proje ve Görev (Task) Yönetimi.**
- **Bölüm 5: K-Radar ve İleri Düzey Analitik.**

*(Kod tarafında `_INCLUDE_DEFERRED = False` ile korunuyor; metinleri kesinleşince buraya alt-bölüm + 🎙️ beat olarak eklenecek.)*
