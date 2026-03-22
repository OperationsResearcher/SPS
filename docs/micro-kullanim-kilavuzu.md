# Kokpitim — Micro arayüz kullanım kılavuzu

**Sürüm notu:** Test / pilot kullanım için hazırlanmıştır.  
**PDF oluşturma:** `micro-kullanim-kilavuzu-yazdir.html` dosyasını tarayıcıda açıp **Ctrl+P → PDF olarak kaydet** kullanın; veya bu `.md` dosyasını VS Code “Markdown PDF” eklentisi / Pandoc ile PDF’e dönüştürün.

---

## 1. Genel: İki arayüz, adresler

| Ne | Nerede |
|----|--------|
| **Yeni (Micro) platform** | Kök URL — örn. `https://sunucunuz/masaustu`, `https://sunucunuz/bireysel/karne` |
| **Klasik (eski) Kokpitim** | `LEGACY_URL_PREFIX` altında — kurulumda genelde **`/kok`** (örn. `/kok/login`) |

- Giriş sonrası yan menü ve adres çubuğu **Micro**’da mı **/kok**’ta mı olduğunuzu gösterir.  
- Test kullanıcılarına: günlük iş için **Micro kök adresi** önerilir; eski ekranlar ihtiyaç halinde `/kok` üzerinden açılır.

---

## 2. Masaüstüm (`/masaustu`)

**Amaç:** Günlük komuta merkezi — bildirimler, eksik veriler, yaklaşan faaliyetler, kısayollar.

### 2.1 Üst bilgi paneli
- **Yeni Kokpitim** kök adrestedir; klasik arayüz **`/kok`** (veya kurumunuzdaki legacy önek) altındadır.
- **Karalama defteri** ve **widget sırası / gizlenen kartlar** yalnızca **tarayıcıda** (`localStorage`) saklanır: sunucuya gitmez, başka cihazda görünmez, yedeklenmez.

### 2.2 Bugünün özeti
Tıklanabilir kutular: okunmamış bildirim sayısı, bu ay eksik bireysel PG verisi, geciken faaliyet, önümüzdeki 7 günde biten faaliyet. İlgili sayfaya yönlendirir.

### 2.3 İstatistik kartları
- **Bireysel PG / Faaliyet / Bildirim:** toplam veya bekleyen sayılar.  
- **Süreç PG:** Üye veya **lider** olduğunuz süreçlerdeki **toplam aktif PG** sayısı (gerçek toplam). Alttaki listede yalnızca **son güncellenen 5** örnek gösterilir.

### 2.4 Hızlı işlemler
Bireysel karne, bildirimler, süreçler, stratejik plan, projeler, kurum — tek tık.

### 2.5 Benim Masam
Sekmeler: **Bugün** (bitiş tarihi bugün), **7 gün**, **Geciken** (bitiş tarihi geçmiş, tamamlanmamış). Faaliyetlerde bitiş tarihi yoksa liste sıralamasında sonda yer alır.

### 2.6 Dikkat: bu ay verisi
Bulunduğunuz takvim ayı için henüz veri girilmemiş **bireysel** PG’ler. “Karnede veri gir” ile bireysel karneye gidersiniz.

### 2.7 Karalama defteri
Kısa notlar; sadece bu tarayıcıda kalır (bkz. üst bilgi).

### 2.8 Bildirimler
Satırda **Okundu** ile tek bildirimi kapatır (sunucuda işaretlenir). **Tümünü Gör** ile bildirim merkezine gidersiniz.

### 2.9 Widget yönetimi ve sürükleme
- **Widget yönetimi:** Hangi kartların görüneceğini seçer; kaydet sonrası sayfa yenilenir.  
- Kart **başlığından** tutup sürükleyerek sırayı değiştirirsiniz; sıra tarayıcıda saklanır.

### 2.10 Süreç PG listesi (varsa)
Örnek 5 kayıt; tam liste için Süreçler modülüne gidin.

---

## 3. Bireysel performans karnesi (`/bireysel/karne`)

**Amaç:** Kişisel PG’ler ve faaliyetler; aylık veri; geçmiş özeti.

### 3.1 Yıl seçimi
Üstteki yıl listesinden takvim yılı seçilir; tablolar ve API bu yıla göre yüklenir.

### 3.2 Özet istatistikler
Toplam PG, veri girilmiş PG sayısı, faaliyet sayısı, faaliyet tamamlanma oranı (yaklaşık).

### 3.3 Yıl özeti & dikkat (pill’ler)
- Kaç ayda en az bir PG verisi olduğu, bu yıl hiç veri almamış PG sayısı.  
- **Sarı “hedefe göre zayıf” uyarısı:** Son girilen aylık değer ile hedefi karşılaştıran **tahmini, bilgi amaçlı** göstergedir; **resmi performans veya İK değerlendirmesi değildir.**

### 3.4 Bu yıl ne yaptım? (zaman çizgisi)
PG veri girişleri ve tamamlanan faaliyet ayları kronolojik listede gösterilir.

### 3.5 Performans göstergeleri tablosu
- **Yeşil / kırmızı ısı:** Geçmiş veya içinde bulunulan ay için veri var/yok vurgusu.  
- Hücredeki değere tıklayınca **veri girişi** (SweetAlert).  
- **Satıra** (sil ve hücre düğmesi dışına) tıklayınca **yıllık detay**: kayıt listesi ve mini aylık grafik.  
- Çöp kutusu: PG’yi pasifleştirir.

### 3.6 Faaliyetler tablosu
Aylık kutucuklar işaretlenebilir; faaliyet ekle/sil.

---

## 4. Bildirim merkezi (`/bildirim`)

Okunmamış ve okunmuş bildirimler; tür ve tarih. Masaüstünden tek tek okundu işaretlenebilir; burada toplu işlemler (varsa) kullanım kılavuzuna eklenir.

---

## 5. Modül başlatıcı (launcher / ana sayfa)

Rol ve pakete göre modül kutuları. Tıklanınca ilgili Micro yoluna gider. Erişilemeyen modüller listede olmayabilir.

---

## 6. Stratejik planlama (`/sp`)

Kurum stratejileri, alt stratejiler, hedefler (rolünüze göre düzenleme veya salt okunur). Detay: ekran üstü başlıklar ve formlar üzerinden ilerleyin; kayıt sonrası listeler güncellenir.

---

## 7. Süreç yönetimi (`/process`)

Süreç listesi; süreç detayında üyeler, liderler, PG ve faaliyetler. Yetkinize göre ekleme/düzenleme. Süreç **karnesi** genelde `/process/<id>/karne` altında; PG veri girişi, tablo görünümü, VGS (veri giriş sihirbazı) bu ekranlarda kullanılır.

**VGS:** Seçilen PG ve tarih ile süreç + bireysel karneye (eşleşen PG varsa) veri yazımı. İzin yoksa hata mesajı döner.

---

## 8. Kurum paneli (`/kurum`)

Kurum özeti, stratejik kimlik, yöneticiler için ek özetler (rol bağımlı). Sayfa içi akordeonlar ve linklerle gezinin.

---

## 9. Proje yönetimi (`/project`)

Proje listesi, filtreler, proje detayına giriş; görevler, Kanban, takvim vb. (projeye göre). Yetkisiz kullanıcı boş liste veya erişim kısıtı görebilir.

---

## 10. Analiz merkezi (`/analiz`)

Raporlama ve analiz sayfaları (kurulumunuza göre menü öğeleri değişebilir).

---

## 11. Ayarlar (`/ayarlar`)

Profil, kurum ve kullanıcı ayarları (rolünüze göre sekmeler).

---

## 12. Yönetim paneli (`/admin/users` vb.)

**tenant_admin / executive_manager / Admin** rolleri için kullanıcı, kurum, paket yönetimi. Yetkisiz erişimde yönlendirme veya hata alırsınız.

---

## 13. API dokümantasyonu (`/api/docs`)

REST API referansı; geliştirici ve entegrasyon kullanımı.

---

## 14. Hızlı giriş (`/Hgs_mfg`)

Yalnızca geliştirme/demo; üretimde çoğu kurulumda kapatılır veya kısıtlanır. Eski adres **`/hgs`** otomatik olarak **`/Hgs_mfg`** adresine yönlendirilir (301).

---

## 15. Sık sorunlar

| Durum | Ne yapmalı? |
|-------|-------------|
| Sayfa 404, “eski” menü | Adresin `/kok` ile mi yoksa kök ile mi olduğunu kontrol edin. |
| Masaüstü widget’ları kayboldu | Widget yönetiminden tekrar açın; gizlilik tarayıcı verisine bağlıdır. |
| Karalama notu yok | Farklı tarayıcı/cihaz kullanıyorsanız normaldir (yerel saklama). |
| Bildirim okundu olmuyo | Oturum ve CSRF; sayfayı yenileyip tekrar deneyin. |
| Süreç PG sayısı ile liste uyumsuz | Kartta **toplam**, altta **5 örnek** — tasarım gereği. |

---

## 16. Destek ve geri bildirim

Test sırasında karşılaşılan ekran görüntüsü, kullanıcı rolü, URL ve yaklaşık saat bilgisi ile destek ekibine iletin.

---

*Bu belge depodaki `docs/micro-kullanim-kilavuzu.md` dosyasıdır; güncellemeler için git geçmişine bakın.*
