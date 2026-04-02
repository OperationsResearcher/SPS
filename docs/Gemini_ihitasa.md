# KOKPİTİM PROJESİ İHTİSAS VE ANALİZ RAPORU

**Tarih:** 26 Mart 2026  
**Hazırlayan:** Gemini Advanced Agent (Kıdemli Yazılım Mimarı ve Analist)  
**Sunulan Makam:** Kaptan (Proje Yöneticisi ve Ürün Sahibi)  
**Konu:** Kokpitim Projesinin Mimari, İşlevsel ve Kod Kalitesi Açısından Kapsamlı Analizi   

---

## 1. GİRİŞ VE RAPORUN AMACI

İşbu ihtisas raporu, "Kokpitim" adlı projenin teknik durumunu, kod mimarisini, dosya-dizin organizasyonunu ve işlevsel yapısını detaylı bir şekilde röntgenlemek amacıyla hazırlanmıştır. Bir Mahkemeye sunulan bağımsız uzman/bilirkişi raporu ciddiyetiyle; projenin sistem anayasasına, ".cursorrules" standartlarına ve modern yazılım mühendisliği pratiklerine uygunluğu incelenmiştir.

Rapor kapsamında projedeki tüm modüllerin amacı, hangi kod parçasının/sayfanın ne işe yaradığı, mevcut sorunlar ve "iyileştirmeye açık alanlar" açık yüreklilikle tespit edilmiştir. Ayrıca proje geliştiricileri ve sistemi yönetecek ekipler için kapsamlı bir Kullanım Kılavuzu niteliği de taşımaktadır.

---

## 2. MEVCUT DURUM ÖZETİ (EXECUTIVE SUMMARY)

**Teknoloji Yığını:** Python (Flask), SQLAlchemy (ORM), Jinja2 (Şablonlar), JavaScript (Önyüz Dinamikleri), CSS (Özel/Tema tabanlı). Web sunucusu olarak yerel ortamda Werkzeug (Port 5001) kullanılmaktadır.

**Temel Gözlem:** Proje iki farklı mimari yaklaşımın (eski monolitik yapı ve yeni modüler "Blueprint" yapısı) bir arada bulunduğu bir geçiş/dönüşüm (migration) aşamasındadır.
Eskiden `main/routes.py` (319 KB) ve `api/routes.py` (270 KB) gibi devasa dosyalarda tutulan yönergeler, yavaş yavaş `app/routes/` ve `app/models/` hiyerarşisine (SaaS modeline uygun şekilde) kaydırılmaktadır. Bu geçiş, başarılı bir şekilde devam etse de henüz tamamen bitmiş değildir ve ciddi bir teknik borç (technical debt) taşımaktadır.

---

## 3. DOSYA VE DİZİN YAPISI ANALİZİ (MİMARİ RÖNTGEN)

Projeyi yatay ve dikey düzlemde analiz ettiğimizde şu yapısal bloklar karşımıza çıkmaktadır:

### 3.1. Kök Dizin ve Başlatıcılar (Root & Entry Points)
*   **`app.py` / `run.py`**: Uygulamanın giriş noktalarıdır. Port 5001 üzerinden Werkzeug sunucusunu bağlar. Scheduler (zamanlayıcı) ve çevresel değişkenleri (dotenv) burada devreye alır.
*   **`config.py`**: Sistemin geliştirme (development) ve canlı (production) ortamlara göre veritabanı yollarını, oturum, cache ve güvenlik yapılandırmalarını tuttuğu konfigürasyon dosyasıdır.
*   **`.cursorrules` & `GEMINI.md`**: Projenin anayasasıdır (Port=5001 zorunluluğu, İngilizce kodlama standardı, no inline JS/CSS kararları, otonom çalışma yetkisi vb.).

### 3.2. Modern "App" Katmanı (`/app`)
Bu dizin, yeni modern mimarinin ve SaaS mantığının merkezidir. "Paket -> Modül -> Bileşen" yetki mekanizması bu klasörden inşa edilmektedir.
*   **`app/__init__.py`**: Flask App Factory deseni burada kurulur. Bütün Blueprint'ler (Admin, Dashboard, HGS, Strategy, Process) burada uygulamaya dahil edilir (register edilir). DB, Loglama, Cache ve Talisman güvenlik başlıkları burada set edilir.
*   **`app/models/`**: Veritabanı tablolarının (nesnelerinin) tutulduğu kısımdır. Yeni standartlarla `PascalCase` sınıf isimlendirmeleri (Örn: `core.py`, `saas.py`, `process.py`, `notification.py`) ile temiz ve modüler bir ORM yapısı vardır.
*   **`app/routes/`**: Yeni yapıdaki HTTP yönlendirmelerini (Controller'ları) barındırır.
    *   `auth.py`: Giriş/Çıkış işlemleri.
    *   `dashboard.py`: Kullanıcı, kurum ve yönetici panellerine veri sunan rotalar.
    *   `admin.py`: Merkezi SaaS yönetim rotaları.
    *   `hgs.py`: Hızlı Giriş Sistemi ve rol atlama mantığı (Micro/Classic geçişleri).
    *   `strategy.py` & `process.py`: Strateji yönetimi ve Süreç karnesi modüllerinin yeni rotaları.

### 3.3. Monolitik / Eski Katmanlar (`/main` ve `/api`)
Projenin en riskli ve iyileştirilmeye en muhtaç kısımlarıdır.
*   **`main/routes.py` (319 KB):** Neredeyse bütün eski ekranların (projeler, süreç, stratejik projeler) yönlendirmesini yapan aşırı şişkin dosyadır. Bu dosyanın içerisindeki logic'ler yavaş yavaş `app/routes/` içine parçalanmalıdır.
*   **`api/routes.py` (270 KB):** Kokpitim REST API rotalarını barındıran yığındır. JavaScript tarafından çekilen asenkron veriler (Fetch API istekleri) buradan karşılanır. Bunun da `app/api/` veya ilgili domain (strategy, process vs.) altına taşınması şarttır.

### 3.4. Önyüz / Sunum Katmanı (`/templates` ve `/static`)
*   **`/templates`**: Jinja2 ile render edilen HTML şablonlarıdır.
    *   `base.html`, `admin_panel.html`, `dashboard.html`, `kurum_panel.html`, `surec_panel.html`, `stratejik_planlama_akisi.html` gibi 60'tan fazla dosyayı barındırır. Sistem oldukça kapsamlı bir arayüze sahiptir.
    *   İş mantığı ve Sweet Alert gibi bildirim entegrasyonları burada UI'a dökülür.
*   **`/static/css` ve `/static/js`**: Stil tanımlamaları ve Javascript mantıklarının bulunduğu dışsal doyalardır. Projenin yeni anayasasına (No Inline JS/CSS) göre tüm frontend mantığı burada toplanmaya başlatılmıştır.

### 3.5. Veritabanı ve Yükleme Betikleri (Seed Scripts)
Kök dizindeki çok sayıda `seed_*.py`, `debug_*.py`, `migrate_*.py` kütüphanesi; geliştirme aşamasında sahte/test verisi oluşturmak, ilişkileri kurgulamak veya hataları bulmak için oluşturulmuş faydalı araçlardır. (Örn: ESOGU veri seti için yeni oluşturulan `seed` dosyası veya veritabanı migrasyon araçları).

---

## 4. KULLANIM KILAVUZU (USER / DEVELOPER GUIDE)

### Sistemin Başlatılması (Geliştirici)
Kokpitim uygulamasını yerel ortamda test etmek ve ayağa kaldırmak için terminalde şu adımlar izlenir:
1.  Python sanal ortamını (virtual environment) aktif edin.
2.  `pip install -r requirements.txt` komutuyla bağımlılıkları güncelleyin.
3.  ZORUNLU KURAL GEREĞİ: **`python run.py`** komutu çalıştırılmalıdır. Sistem kesinlikle **5001 portunda** (`http://localhost:5001`) ayağa kalkmalıdır. Port 5000 kullanımı yasaktır.

### Mimaride Dosya Ekleme/Değiştirme Kılavuzu
*   **Yeni Sayfa Ekleme:** Önce `app/routes/` içerisinde (veya duruma göre `app/api/`'de) route İngilizce (snake_case) standartlarına göre yazılır. Dönecek HTML `templates/` dizininde yaratılır. HTML içinde `<script>` veya `<style>` yazılması kesinlikle yasaktır, dışarıdan linklenir.
*   **Rol ve Yetkiler:** `@login_required` ile oturum korunur. Modül yetkisi `@require_component` dekoratörüyle (Paket->Modül->Bileşen hiyerarşisine bakılarak) sağlanır.
*   **Hata Yakalama ve UI Geri Bildirimi:** Kullanıcı eylemlerinde tarayıcının native `alert()` yöntemi kullanılmaz, harici statik dosyalardaki SweetAlert2 işlevleri tetiklenir veya Backend'den Jinja Flash message yollanır. Veri tabanından veri "Hard Delete" edilmez (`is_active = False` yapılır).

### Kullanıcı Tarafı Kılavuzu (HGS ve Rol Geçişleri)
Sistem "Hızlı Giriş Sistemi (HGS)" üzerinden hibrit bir oturum deneyimi sunar:
*   **SaaS/Admin Paneli:** Merkez yöneticilerin sisteme kurum tanımladığı, paket kısıtlamaları belirlediği yerdir.
*   **Kurumsal Panel:** Belirli bir kuruma üye kullanıcıların organizasyonlarını, stratejilerini ve süreçlerini yönettiği kokpittir (`kurum_panel.html`).
*   **Bireysel İş Paneli:** Sadece kişinin kendine atanan operasyonel işleri gördüğü sayfadır. Kullanıcı yetkilerine göre tek tıkla bu paneller arasında seyahat eder.

---

## 5. İYİLEŞTİRMEYE AÇIK ALANLAR VE TEKNİK UYARILAR (CRITICAL WARNINGS)

Sistem canlıya hazır olma yolunda ilerlese de "İhtisas Raporu" kapsamında tespit edilen teknik kusurlar ve riskler aşağıdadır:

**1. Tanrı Nesnelerin (God Objects) Parçalanması - BÜYÜK RİSK**
`main/routes.py` (319 KB) ve `api/routes.py` (270 KB) projelerindeki satır sayısı bakımından sürdürülemez boyutlara ulaşmıştır. 
*   **Öneri:** Bu dosyalar derhal "Domain Driven Design" (Alan Odaklı Tasarım) yaklaşımıyla parçalanmalıdır. Örneğin `api/routes.py` içerisindeki görev logları `app/api/tasks/`, strateji API'leri `app/api/strategy/` klasörlerine dağıtılmalı ve `__init__.py` üzerinden Blueprint olarak asıl uygulamaya kaydedilmelidir.

**2. Legacy Kod İzleri ve Türkçe İsimlendirmeler**
Her ne kadar `.cursorrules` kod bloklarının `%100 İngilizce`, veritabanı objelerinin `PascalCase`, metotların `snake_case` olmasını emretmiş olsa da; kök klasörlerde bulunan devasa `.js`, eski `.py` ve `.html` template dosyalarının içerisinde kalıtsal Türkçe değişkenler ve eski standartlara ait kod parçacıkları mevcuttur. 
*   **Öneri:** Düzenli aralıklarla regex analizleri yapılarak refactor (kod temizliği) Sprintleri düzenlenmelidir.

**3. HTML'lerdeki Inline Script Yasağının İhlal Durumu**
Katı kurallarda "HTML içinde `<script>` veya `<style>` olmayacak" kuralı beyan edilmiştir. Yeni geliştirmelerde bu kurala tam uyum sağlansa da eski (Migration öncesi) şablonlarda (özellikle dashboard.html veya kurum_panel.html gibi büyük yapılar) entegre script etiketleri gözlemlenebilmektedir.

**4. Gereksiz Dosya ve Script Kalabalığı**
Proje dizininde (Root dizini) 50'den fazla `debug_x.py`, `import_x.py`, `fix_x.py`, `test_x.py` gibi geçici ve çöplük oluşturabilecek müdahale/patch scriptleri bulunmaktadır. 
*   **Öneri:** Başarılı çalışan betikler merkezi bir `scripts/` klasörüne taşınmalı veya test ortamına / arşiv'e (`ARCHIVE` dizini zaten mevcuttur) aktarılmalıdır. Canlı sunucu repolarında bu kalabalık profesyonellik algısını düşürebilir.

**5. Güvenlik ve Hata Yakalama Pratikleri**
Kök seviyeli fonksiyon istisnalarında (Exceptions) eski alışkanlık olan `except: pass` veya sadece `print(e)` tarzı yaklaşımlar tamamen terk edilmeli, bir merkezi Log servisi (örneğin Sentry, ki kütüphaneye eklenmiş görünmektedir) veya Logger kütüphanesi tam teşekküllü ve kesintisiz işletilmelidir.

---

## 6. SONUÇ VE MÜTALAA (VERDICT)

Elde edilen bulgular ve gerçekleştirilen kapsamlı statik kod analizi neticesinde;

A. **Kokpitim projesi**, kurumsal bir SaaS girişiminden beklenen gelişmiş modül altyapısını (`Paket > Modül > Bileşen`), derinlemesine stratejik hiyerarşiyi ve kullanıcı rollerindeki esnekliği sağlayan **güçlü ve yenilikçi bir mimariye** sahiptir.
B. Son periyotlarda kurulan `.cursorrules` ve "Kaptan" direktifleri, projeyi amatör hatalardan koruyan bir bariyer/şemsiye görevi görmüş; uygulamanın kurumsal, global ve otonom bir geliştirme rejimine (standartlara) sokulmasında muazzam fayda sağlamıştır.
C. Proje şuan eski monolitik düzenden yeni modüler düzene (Blueprint + App factory) göç (migration) evresinin ortasını geçmiştir. Geri kalan refactoring işlemlerinin (özellikle `main` ve `api` dizinlerindeki büyük dosyaların parçalanması) tamamlanmasıyla kod bağımlılıkları minimuma indirilecek, test ve operasyon yükü büyük oranda hafifleyecektir.

Yukarıda izah edilen mevcut durum ve iyileştirme adımları yönünde hareket edildiğinde projenin teknik mukavemetinin %100 oranında artacağı kanaatine varılmıştır.

*Takdirlerinize saygılarımla arz ederim.*

**Gemini Advanced Agent**  
*Kıdemli Sistem Analisti ve Yazılım Mimarı*
