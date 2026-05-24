# Tenant Kullanıcı Kılavuzu

> **Versiyon:** 1.0
> **Tarih:** 2026-05-24
> **Hedef:** Kurum içinde Kokpitim'i kullanan standart çalışan (yönetici değil)
> **Amaç:** "Ben Kokpitim'de ne yapabilirim, nereden başlarım?" sorusuna eksiksiz cevap

---

## İçindekiler

1. [Hoş Geldiniz](#1-hoş-geldiniz)
2. [İlk Giriş](#2-i̇lk-giriş)
3. [Masaüstüm](#3-masaüstüm)
4. [Bildirimler](#4-bildirimler)
5. [Bireysel Karnem](#5-bireysel-karnem)
6. [Süreç Karnesi](#6-süreç-karnesi)
7. [Faaliyetlerim](#7-faaliyetlerim)
8. [Projelerim](#8-projelerim)
9. [Stratejik Plan (Görüntüleme)](#9-stratejik-plan-görüntüleme)
10. [Profilim](#10-profilim)
11. [Kişisel Ayarlar](#11-kişisel-ayarlar)
12. [Yapamadığım Şeyler](#12-yapamadığım-şeyler)
13. [Sık Sorulan Sorular](#13-sık-sorulan-sorular)
14. [Hızlı Aksiyon Kartı](#14-hızlı-aksiyon-kartı)

---

## 1. Hoş Geldiniz

Kokpitim'e hoş geldiniz! Bu kılavuz **standart bir çalışan** için yazıldı. Eğer yöneticiyseniz, [Tenant Admin Kullanım Kılavuzu](tenant_admin_kullanim_kilavuzu.md) sizin için.

**Kokpitim'de neler yapabilirsiniz:**
- Kendi KPI'larınızın verilerini girer
- Bireysel performans karnenizi takip eder
- Atandığınız faaliyetleri günceller
- Atandığınız projelerde görevler yönetir
- Kurum stratejisini görüntüler (değiştiremezsiniz, sadece okursunuz)
- Bildirimlerinizi yönetir
- Profilinizi düzenler

**Yapamayacağınız şeyler (yönetici gerektiren):**
- Yeni strateji oluşturma
- KPI tanımlama (sadece veri girersiniz)
- Diğer kullanıcı yönetimi
- Kurum ayarlarını değiştirme

Detay için → [Bölüm 12](#12-yapamadığım-şeyler)

---

## 2. İlk Giriş

### 2.1 Sisteme nasıl giriş yapacağım?

Tarayıcınızda Kokpitim adresine gidin (örn: `https://kokpitim.com` veya kurumunuzun verdiği özel adres).

**Giriş ekranında:**
- E-posta: Kurum tarafından verilen iş e-postanız
- Şifre: Yöneticinin verdiği geçici şifre

⚠️ **İlk girişte:** Sistem sizi profil sayfasına yönlendirir → şifrenizi mutlaka değiştirin.

### 2.2 Şifremi unuttum, ne yapayım?

Giriş ekranında **"Şifremi Unuttum"** linkine tıklayın → e-posta adresinizi girin → sıfırlama maili gelir → maildeki linke tıklayın → yeni şifre belirleyin.

Mail gelmiyor mu? Yöneticinize başvurun.

### 2.3 İki faktörlü kimlik doğrulama (2FA) nedir, açmalı mıyım?

**Önerilen:** Evet, açın.

**Sayfa:** Profil → "2FA'yı Etkinleştir"

- QR kodu telefonunuzdaki Authenticator app (Google Authenticator, Microsoft Authenticator, Authy) ile tarayın
- 6 haneli kodu girin
- Yedek kodları **mutlaka kaydedin** (telefonunuzu kaybederseniz erişim için)

Sonraki girişlerde şifreden sonra 6 haneli kod istenir.

---

## 3. Masaüstüm

**Sayfa:** Sol menü → **Masaüstüm** (veya `/masaustu`)

İlk giriş yaptığınızda buraya düşersiniz. **Günlük çalışmanızın merkezi.**

### 3.1 Karşılama Alanı
"Merhaba, [Adınız] 👋" — sizi karşılar.

### 3.2 Bugünün Özeti (Command Panel)
Önemli sayılar:
- **Okunmamış bildirim:** Tıkla → `/bildirim` aç
- **Eksik PG verisi (bu ay):** Bu ay veri girmediğin KPI sayısı — Tıkla → `/bireysel/karne`
- **Geciken faaliyet:** Bitiş tarihi geçmiş faaliyetler
- **7 gün içinde biten:** Yakında bitmesi gereken faaliyetler

### 3.3 İstatistik Kartları
4 kutu:
- Bireysel PG (Performans Göstergesi) sayım
- Devam eden faaliyet sayım
- Süreç PG'lerim (üyesi/lideri olduğum süreçler)
- Okunmamış bildirim sayım

### 3.4 Hızlı İşlemler
6 büyük buton:
- Bireysel karne
- Bildirimler
- Süreçler
- Stratejik plan
- Projeler
- Kurum

### 3.5 Takvim
**FullCalendar** widget'ı:
- Yeşil = Süreç faaliyetlerim
- Mavi = Proje görevlerim
- Turuncu = Kişisel hatırlatıcılar

**Hızlı ekleme:** Takvimde bir günü tıkla → modal açılır → faaliyet veya görev hızlıca ekle.

### 3.6 Benim Masam (Inbox)
3 sekme:
- **Bugün:** Bugün biten faaliyetler
- **7 Gün:** Önümüzdeki haftada biten
- **Geciken:** Bitiş tarihi geçmiş, hala kapatılmamış

Her satıra tıkla → detay aç.

### 3.7 Dikkat: [Bu Ay] Verisi
Bu ay için veri girmediğin bireysel PG'ler listelenir.

**"Karnede veri gir"** butonu → doğrudan `/bireysel/karne`'ye götürür.

✅ Tüm verilerin girilmişse: Yeşil "Aferin!" mesajı.

### 3.8 Karalama Defteri
Sağda küçük not alma alanı.

⚠️ **Önemli:** Bu not **sadece tarayıcınızda** kalır (localStorage). Sunucuya yazılmaz, yedeklenmez, başka cihazda görünmez. Kendinize hatırlatma için iyidir, kritik bilgi için kullanmayın.

### 3.9 Özet Listeler
- **Bireysel PG'lerim:** Hedeflerimin kısa listesi
- **Devam Eden Faaliyetlerim:** İlerleme bar'ı ile

### 3.10 Bildirimler Özeti
Son 5-10 bildirim. "Tümünü Gör" → `/bildirim`.

### 3.11 Stratejik Hedefler Widget'ı
Kurumun ana stratejilerinin kısa listesi (sadece görüntü).

---

## 4. Bildirimler

**Sayfa:** Sol menü → **Bildirimler** (veya `/bildirim`)

Sistem size birkaç durumda otomatik bildirim gönderir:
- Yeni süreç atandı
- Yeni KPI eklendi/değişti
- Yeni faaliyet atandı
- Görev sorumluluğu size verildi
- Faaliyet bitiş tarihi yaklaşıyor
- Hatırlatıcı

### 4.1 Bildirim Listesi
Her bildirim için ikon, başlık, mesaj, tarih görürsünüz.

**Görsel:**
- Kalın yazı = okunmamış
- Açık yazı = okunmuş
- Yanında nokta = okunmamış işaretçisi

### 4.2 Bildirimi okumak
- Bildirim üzerine tıkla → varsa ilgili sayfaya gider (örn: faaliyet detayı)
- Yan tarafta "Okundu" butonu → sadece işaretler

### 4.3 Tümünü okundu işaretle
Üst köşede **"Tümünü Okundu İşaretle"** butonu. Toplu işaretler.

### 4.4 Bildirim ayarlarımı nasıl değiştiririm?
Profil → Ayarlar → "Bildirimler" sekmesi → açıp kapatabilirsiniz:
- E-posta bildirimleri
- Süreç bildirimleri
- Görev bildirimleri
- Deadline uyarıları

---

## 5. Bireysel Karnem

**Sayfa:** Sol menü → **Bireysel Karnem** (veya `/bireysel/karne`)

**Burası sizin kişisel performans tablonuz.** Kurum tarafından size atanmış hedeflerin (PG = Performans Göstergesi) aylık takibi.

### 5.1 Sayfanın Yapısı

**Üst bar:**
- "Bireysel Performans Karnem" başlığı
- Yıl seçici (geçmiş 5 yıl + gelecek 1 yıl)

**4 Özet Kart:**
- Toplam PG sayısı
- Veri girilen PG sayısı
- Faaliyet toplamı
- Tamamlanma yüzdesi

### 5.2 Yıl Özeti & Dikkat
Sistemin yıl boyunca veri girişinizden çıkardığı kısa özet + dikkat etmeniz gereken pill'ler.

### 5.3 "Bu Yıl Ne Yaptım?" Timeline
Veri girişlerinizin ve faaliyet etkinlikleriniz tarih sırasıyla — kronolojik akış.

### 5.4 Performans Göstergeleri Tablosu

| # | Gösterge Adı | Hedef | Birim | Oca | Şub | Mar | ... | İşlem |
|---|---|---|---|---|---|---|---|---|
| 1 | Müşteri memnuniyeti | 75 | % | 72 | 74 | — | ... | ✏️ |
| 2 | Yanıt süresi | 24 | saat | 26 | 22 | 20 | ... | ✏️ |

**Hücreye tıkla:** Veri girişi modal'ı açılır.
- Ay seç
- Aktual değeri gir (örn: 76)
- Notlar (opsiyonel)
- **Kaydet**

✅ Renk kodu:
- **Yeşil:** Hedef üstünde (%80+)
- **Sarı:** Yakın (%50-80)
- **Kırmızı:** Düşük (<50%)

### 5.5 PG Ekleme (Eğer izniniz varsa)

**Buton:** "PG Ekle" → modal:
- Ad (örn: "Aylık satış adedi")
- Birim (örn: "adet")
- Hedef değer (örn: 100)
- Ağırlık (toplam içinde)

⚠️ Bazı kurumlarda yöneticinin sizin için PG açması beklenir. "PG Ekle" butonu görünmüyorsa yöneticinize sorun.

### 5.6 Mini Grafik

Bir PG satırına tıkla → altında **12 aylık çizgi grafik** açılır. Hedef çizgisi + gerçekleşmeler. Trend hızlıca görünür.

### 5.7 Bireysel Faaliyetler

PG'lerden ayrı bir tablo: faaliyetlerin 12 aylık ay-bazlı takibi.

| Faaliyet | Durum | Oca | Şub | Mar | ... | İşlem |
|---|---|---|---|---|---|---|
| Aylık ekip toplantı | Devam | ✓ | ✓ | ✓ | ... | 🔄 |
| Yıllık eğitim katılım | Planlandı | — | — | — | ... | ▶️ |

Ay hücresine tıkla → o ay için faaliyeti **işaretlersiniz** (yaptığım/yapmadım).

### 5.8 PDF İndirme

**Buton:** "PDF Olarak İndir" → kişisel karneniz PDF olarak iner. Yöneticinizle paylaşmak için.

---

## 6. Süreç Karnesi

**Sayfa:** Sol menü → **Süreçler** → bir süreci seç → "Karne" sekmesi (veya `/process/<id>/karne`)

Burası sizin **üyesi veya lideri olduğunuz süreçlerin** KPI tablosu.

### 6.1 Hangi süreçlerin karnesini görürüm?
Sadece size atanmış süreçleri görürsünüz. Yönetici bir sürece üye eklerse, listede çıkar.

### 6.2 Karne Yapısı

Bireysel karne ile aynı mantık ama bu sefer **kurumsal süreç KPI'ları**:

| KPI | Hedef | Birim | Oca | Şub | ... |
|---|---|---|---|---|---|
| Sevkiyat zamanında yapma | 95 | % | 92 | 94 | ... |
| Hatalı ürün oranı | 2 | % | 3 | 2.5 | ... |

### 6.3 Veri Giriş

Hücreye tıkla → veri giriş modal'ı:
- Aktual değer
- (Hedef otomatik gösterilir)
- Not (opsiyonel)
- Kaydet

✅ Veriniz kaydedildikten sonra **audit log**'a yazılır — kim ne zaman ne girdi, kayıt altında.

### 6.4 Yetki

- **Üye (member):** Sadece veri girer
- **Lider (leader):** Veri girer + düzenler + siler

İcindeki rolünüzü süreç detay sayfasında görürsünüz.

### 6.5 Excel İndir / Toplu İmport

**Excel İndir:** Süreç KPI verisinin xlsx kopyasını indirir.
**Toplu İmport:** Doldurulmuş Excel'i yükleyip tek seferde çok veri girer.

⚠️ Bu butonları görmek için lider rolü gerekebilir.

---

## 7. Faaliyetlerim

Faaliyetler iki yerde görünür:
- **Bireysel karnemde** → kişisel faaliyetler
- **Süreç detayında** → kurumsal süreç faaliyetleri

### 7.1 Faaliyet Durumları
- **Planlandı** — başlamamış
- **Devam Ediyor** — çalışılıyor
- **Beklemede** — bloklanmış
- **Tamamlandı** ✅ — bitti
- **Ertelendi** — yeni tarihe atıldı
- **İptal** ❌ — yapılmayacak

### 7.2 Faaliyet Güncelleme

Faaliyet üzerine tıkla → modal:
- Durum değiştir
- Notlar ekle
- İlerleme yüzdesi
- Hızlı aksiyonlar: **Tamamla**, **Ertele**, **İptal**

### 7.3 Aylık Takip

Bireysel karne tablonuzdaki ay hücrelerine tıklayarak o ay için "yaptım" işaretlersiniz.

---

## 8. Projelerim

**Sayfa:** Sol menü → **Projeler** (veya `/project/list`)

Atandığınız projeler.

### 8.1 Proje Listesi

Tablo: ad, durum, proje yöneticisi, başlangıç/bitiş tarihi, ilerleme yüzdesi.

Sadece **dahil olduğunuz projeler** görünür.

### 8.2 Proje Detayı

Bir projeye tıkla → detay sayfası:

**Sekmeler:**
- **Özet:** Proje bilgileri, ilerleme, bütçe
- **Görevler:** Liste/Kanban/Gantt görünümü
- **Risk (RAID):** Risk listesi
- **Dosyalar:** Yüklenen dokümanlar
- **Takvim:** Tarihler kronolojik

### 8.3 Görev Yönetimi

Size atanmış görevleri görürsünüz. Görev satırı:
- **#** — sıra no
- **Başlık**
- **Durum** — açık/devam/bekleme/tamamlandı/iptal
- **Öncelik** — kritik/yüksek/orta/düşük
- **Sorumlu**
- **Tarih**
- **İlerleme %**

### 8.4 Görev Güncelleme

Göreve tıkla → detay:
- Durum değiştir (dropdown)
- İlerleme % gir
- Notlar ekle
- Yorum gönder
- Dosya ekle
- Zamanı kaydet (time entry)

### 8.5 Gantt Görünümü

**Sayfa:** `/project/<id>/views/gantt`

Zaman çizelgesinde görevlerin sırası. Bağımlılıkları (depends_on) çizgilerle gösterir. Kritik yol kırmızı renkli.

### 8.6 Kanban Görünümü

**Sayfa:** `/project/<id>/views/kanban`

Görevleri durum sütunlarında (Yapılacak / Yapılıyor / Tamamlandı). Drag-drop ile sürükleyerek durum değiştirebilirsiniz.

### 8.7 Yapamayacağınız Şeyler (proje)

- Yeni proje açma → yönetici hakkı
- Diğer kullanıcılara görev atama → proje yöneticisi yetkisi
- Proje silme → yönetici hakkı

---

## 9. Stratejik Plan (Görüntüleme)

**Sayfa:** Sol menü → **Stratejik Planlama** (veya `/sp`)

Kurumun stratejik planını **görüntüleyebilirsiniz** ama **düzenleyemezsiniz**.

### 9.1 Neler Görünür

- **Misyon:** Kurumun var olma sebebi
- **Vizyon:** Olmak istediğiniz yer
- **Değerler:** Kurum davranış ilkeleri
- **Ana Stratejiler:** Üst seviye stratejik hedefler
- **Alt Stratejiler:** Ana stratejilerin altındaki spesifik hedefler

### 9.2 Strateji Haritası

**Sayfa:** `/sp/strateji-haritasi`

İnteraktif grafik:
- Mor düğümler: Stratejiler
- Açık mor: Alt stratejiler
- Yeşil: Süreçler
- Turuncu: KPI'lar
- Pembe: Initiative'ler (çok yıllı girişimler)

Sürükleyip yakınlaştırabilirsiniz. Bir düğüme tıklayınca detay açılır.

### 9.3 Initiative'ler (Görüntüleme)

**Sayfa:** `/sp/initiatives`

Kurumun aktif stratejik girişimlerini görürsünüz (örn: "Dijital Dönüşüm 2026-2028"). Hangi stratejiye bağlı, ne zaman bitecek, hangi milestone'lar var.

⚠️ Initiative oluşturma yetkisi yöneticide.

### 9.4 Hoshin X-Matrix / Blue Ocean / VRIO

Bu sayfalar **yönetici araçları**. Size 403 sayfası gösterilebilir, normal.

---

## 10. Profilim

**Sayfa:** Sağ üst köşe → kullanıcı avatarı → **Profil**

### 10.1 Kişisel Bilgiler

- **E-posta** — değiştirilmez (yönetici değiştirir)
- **Ad / Soyad**
- **Telefon**
- **Unvan** (örn: "Pazarlama Uzmanı")
- **Bölüm**
- **Profil fotoğrafı** — drag-drop veya tıkla, yükle

### 10.2 Şifre Değiştirme

- Mevcut şifre (zorunlu)
- Yeni şifre (en az 6 karakter)
- **Karmaşıklık kuralları:**
  - En az 1 büyük harf
  - En az 1 küçük harf
  - En az 1 rakam
  - Tercihen 1 özel karakter

Şifreyi değiştirdiğinizde **denetim log'una** kaydedilir.

### 10.3 2FA (Two-Factor Authentication)

Yukarıda (Bölüm 2.3) anlatıldı. Çok önerilen.

### 10.4 Profil Fotoğrafı

**Desteklenen:** PNG, JPG, JPEG, GIF, SVG, WebP
**Max boyut:** Kurumun belirlediği (genelde 5MB)

Yüklediğinizde eski fotoğraf otomatik silinir.

---

## 11. Kişisel Ayarlar

**Sayfa:** Profil ekranında "Ayarlar" sekmesi veya doğrudan `/settings`

### 11.1 Bildirim Tercihleri

- E-posta bildirimleri: Aç / Kapa
- Süreç bildirimleri: Aç / Kapa
- Görev bildirimleri: Aç / Kapa
- Deadline uyarıları: Aç / Kapa

### 11.2 Dil ve Saat Dilimi

- Dil: Türkçe / English
- Saat dilimi: Default Europe/Istanbul
- Tarih formatı: dd.mm.yyyy / mm.dd.yyyy / yyyy-mm-dd

### 11.3 Tema

- **Light Mode** (varsayılan)
- **Dark Mode** (gece kullanımı)

Renk paleti seçeneği olabilir (Indigo varsayılan).

### 11.4 Sayfa Rehberi

- Aç / Kapa
- Rehber karakteri: Professional / Friendly / Minimal

---

## 12. Yapamadığım Şeyler

Standart kullanıcı olarak şunları **yapamazsınız** (yönetici hakkı gerekir):

| İşlem | Sebep | Kim yapabilir? |
|---|---|---|
| Yeni strateji ekleme | tenant_admin yetkisi | Yöneticiniz |
| Strateji düzenleme/silme | tenant_admin | Yöneticiniz |
| KPI tanımlama | tenant_admin / surec_lideri | Yöneticiniz / süreç lideri |
| Plan yılı oluşturma | tenant_admin | Yöneticiniz |
| Senaryo oluşturma | tenant_admin | Yöneticiniz |
| Initiative tanımlama | tenant_admin / executive_manager | Yöneticiniz |
| Diğer kullanıcı yönetimi | Admin | Sistem yöneticisi |
| Kurum ayarları değiştirme | tenant_admin | Yöneticiniz |
| AI yapılandırması | tenant_admin | Yöneticiniz |
| Süreç tanımlama | tenant_admin / executive_manager | Yöneticiniz |
| Replan trigger yapılandırma | tenant_admin | Yöneticiniz |
| Yedekleme | Admin | Sistem yöneticisi |
| Hoshin X-Matrix / Blue Ocean / VRIO yönetimi | tenant_admin | Yöneticiniz |

Yetkiniz olmayan bir sayfaya gitmeye çalıştığınızda **403 Forbidden** sayfası gösterilir.

---

## 13. Sık Sorulan Sorular

### S1: Şifremi unuttum, nasıl alırım?
Giriş sayfasında **"Şifremi Unuttum"** → e-posta adresinizi gir → sıfırlama linki mailinize gelir.

### S2: KPI verimi nereden giriyorum?
**Masaüstü** → "Eksik PG verisi" kartı → `/bireysel/karne` → tablodaki ay hücresine tıkla.

### S3: Karnemde neden kırmızı/yeşil var?
**Başarı oranı renkleri:**
- 🟢 **Yeşil:** Hedefe ulaştın (%80+)
- 🟡 **Sarı:** Yakın (%50-80)
- 🔴 **Kırmızı:** Düşük (<50%)

### S4: Bildirim ayarımı nasıl değiştiririm?
Profil → Ayarlar → **"Bildirimler"** sekmesi → istediğin türü kapat/aç.

### S5: Hangi süreçlerden sorumluyum?
**Masaüstü** → "Süreç PG'lerim" istatistik kartı veya **Süreçler** menüsü → liste filtresi "Üyesi olduklarım".

### S6: Yöneticim KPI eklemeden ben veri girebilir miyim?
**Hayır.** KPI tanımlanmadan veri girilmez. Yöneticinize "şu KPI'yı tanımlar mısın?" deyin.

### S7: Mobil cihazdan kullanabilir miyim?
**Evet.** Tarayıcıdan açın (Safari, Chrome, Edge mobil destekli). Tablet için optimize. Mobil özel app henüz yok.

### S8: Bireysel karne ne demek?
**Kişisel performans tablonuz.** Yöneticinin size atadığı hedefler (PG'ler) + sizin yapmanız beklenen aylık faaliyetler. Kurum karnesinden ayrıdır.

### S9: Veri girdim ama kaydetmedim — gitti mi?
Veri giriş modal'ında **"Kaydet"** butonuna basmadan kapattıysanız evet, kaybolur. Tarayıcıyı kapatmadan önce mutlaka kaydedin.

### S10: Karalama notum gitti?
Karalama defteri **tarayıcı cache'inde** saklanır. Tarayıcı önbelleğini temizlediyseniz veya başka cihazdan giriş yaptıysanız görünmez. Önemli not için **e-posta kendinize gönderin** veya bir Word dosyasına yazın.

### S11: Bir faaliyetim "geciken" olarak görünüyor ama tamamladım?
Faaliyete tıkla → modal aç → durumu **"Tamamlandı"** yap → Kaydet. Liste yenilenince geçer.

### S12: Yöneticim diyor ki "şu raporu indir" — nereden?
Yetkiniz varsa **K-Rapor** menüsü → Excel İndir veya PDF İndir. Yetkiniz yoksa yönetici kendisi alır.

### S13: Stratejik haritada bir kutucuğa tıklarsam ne olur?
İlgili stratejinin/sürecin/KPI'nın detayı açılır. Bilgi amaçlı — değişiklik yapamazsınız.

### S14: 2FA açtım ama telefonum yanımda yok, ne yapayım?
Aktivasyon sırasında verilen **yedek kodları** kullanın. Onları da kaybettiyseniz yöneticiye başvurun, 2FA sıfırlanır.

### S15: E-postam değişti, nasıl güncellerim?
Profil → e-posta alanı sizin tarafınızdan değiştirilemez. Yöneticinize "e-posta adresimi şu olarak güncelle" deyin.

---

## 14. Hızlı Aksiyon Kartı

Sık kullanılanlar:

| İhtiyacım | Sayfa |
|---|---|
| Günlük özet görmek | `/masaustu` |
| Bildirim okumak | `/bildirim` |
| Bireysel KPI verisi girmek | `/bireysel/karne` |
| Süreç KPI verisi girmek | `/process/<id>/karne` |
| Faaliyet durumu güncellemek | `/bireysel/karne` veya proje detayında |
| Atandığım projeler | `/project/list` |
| Görev güncellemek | Proje detayı → Görevler |
| Şifre değiştirmek | Profil sayfası |
| Tema değiştirmek (Dark Mode) | Ayarlar → Tema |
| Bildirim ayarı | Ayarlar → Bildirimler |
| Stratejiyi okumak | `/sp` |
| Profil fotoğrafı | Profil sayfası |

---

## Hatırlatma

✅ **Her gün yapmanız önerilen:**
1. Masaüstüne göz atın
2. Bildirimlerinizi kontrol edin
3. Eksik KPI verisi varsa girin (özellikle ay sonunda)
4. Geciken faaliyetlerinizi güncelleyin

✅ **Her hafta:**
1. Bireysel karnenizdeki ay özeti kontrol edin
2. Bu haftanın projelerinizdeki görevlerini güncelleyin

✅ **Her ay:**
1. Bireysel PG verilerinizi mutlaka girin
2. Tamamladığınız faaliyetleri işaretleyin
3. Karnenizden PDF alıp yöneticinize gönderin (eğer kurum istiyorsa)

---

## Bağlantılı Belgeler

- [`docs/test/kokpitimtanitim.md`](kokpitimtanitim.md) — Kokpitim'in genel tanıtımı
- [`docs/test/tenant_admin_kullanim_kilavuzu.md`](tenant_admin_kullanim_kilavuzu.md) — Yönetici kılavuzu (eğer admin iseniz)

---

## Yardım Gerek

- **Şifre/Erişim sorunu:** Yöneticinize başvurun
- **KPI/strateji sorunu:** Yöneticinize sorun
- **Sistem hatası (sayfa açılmıyor, hata mesajı):** Yöneticinize ekran görüntüsü + zaman bilgisi ile bildirin
- **Kullanım rehberi:** Bu belgeyi okuyun, sorunuz yoksa yöneticiye sorun

Kokpitim ile başarılar! 🚀
