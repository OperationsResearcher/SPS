# Kişisel Verilerin İşlenmesine İlişkin Aydınlatma Metni (TASLAK)

> KVKK m.10 kapsamında, Kokpitim platformu kullanıcıları için.
> **TASLAK** — `[DOLDURULACAK]` alanlar tamamlanmadan ve hukuki kontrol yapılmadan yayımlanmaz.
> Yayım yeri önerisi: login sayfası altı bağlantı + profil sayfası + pazarlama sitesi footer.

## 1. Veri Sorumlusu

`[DOLDURULACAK — tüzel kişi unvanı, adres, e-posta/KEP]`

> Not: Kurumunuz (işvereniniz) adına açılan hesaplarda, performans verileriniz bakımından
> veri sorumlusu **kurumunuzdur**; Kokpitim işletmecisi veri işleyen sıfatıyla hareket eder.

## 2. İşlenen Kişisel Veriler

- **Kimlik/iletişim:** ad-soyad, e-posta, telefon (opsiyonel), unvan, departman, profil fotoğrafı
- **Hesap güvenliği:** parola özeti (parolanız düz metin saklanmaz), iki faktörlü doğrulama sırları
- **Performans verileri:** size atanan hedefler, gerçekleşme değerleri, faaliyet kayıtları, bireysel karne skorları
- **İşlem güvenliği:** IP adresi, oturum kayıtları, denetim izleri (audit log)
- **Destek:** Kule destek talebi içerikleriniz ve varsa ekran görüntüleri
- **Tercihler:** tema, dil, bildirim tercihleri

## 3. İşleme Amaçları ve Hukuki Sebepler

| Amaç | Hukuki sebep (KVKK m.5) |
|---|---|
| Hesabınızın oluşturulması, oturum ve yetki yönetimi | Sözleşmenin kurulması ve ifası |
| Kurumsal performans yönetimi (karne, hedef takibi) | Veri sorumlusunun meşru menfaati / kurumunuzla aramızdaki iş ilişkisi |
| Bildirim ve hatırlatma e-postaları | Sözleşmenin ifası (tercihlerden kapatılabilir) |
| Güvenlik, denetim izi, kötüye kullanım önleme | Hukuki yükümlülük ve meşru menfaat |
| Destek taleplerinizin karşılanması | Talebinizin yerine getirilmesi |

## 4. Aktarım

- **Barındırma:** Oracle Cloud altyapısı `[DOLDURULACAK — bölge; yurt dışı ise m.9 açıklaması]`
- **E-posta iletimi:** kurumunuzun tanımladığı SMTP sağlayıcısı
- **Yapay zeka özellikleri:** AI özet/koç raporları için performans metrikleri LLM sağlayıcısına
  iletilebilir `[DOLDURULACAK — sağlayıcı adı; kişisel veri içerip içermediği denetimi]`;
  bu özellikler kurum yöneticiniz tarafından kapatılabilir
- **Google SSO:** yalnızca Google ile giriş yapmayı seçerseniz, kimlik doğrulama amacıyla

## 5. Saklama Süresi

Hesabınız aktif olduğu sürece; hesap silme talebinizde kişisel verileriniz **anonimleştirilir**.
Yedekler en fazla 30 gün saklanır. Denetim kayıtları `[DOLDURULACAK]` süreyle tutulur.

## 6. Haklarınız (KVKK m.11)

İşlenen verileriniz hakkında bilgi talep etme, düzeltme, silme/anonimleştirme, aktarım itiraz
haklarına sahipsiniz. Platform içinden doğrudan kullanabileceğiniz araçlar:

- **Verimi indir:** Profil → "Verilerimi İndir" (JSON) — `GET /auth/api/user/export-my-data`
- **Hesabımı sil/anonimleştir:** Profil → hesap silme — `POST /auth/api/user/delete-my-account`

Diğer talepler için: `[DOLDURULACAK — başvuru e-postası/adresi]`. Başvurular en geç 30 gün
içinde yanıtlanır (m.13).
