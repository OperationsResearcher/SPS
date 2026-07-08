# KVKK Uyum Dosyası — Kokpitim

> Oluşturma: 2026-07-08 (TASK-234, fablerapor Faz 3). Sistemdeki gerçek veri alanları
> ve mekanizmalar taranarak hazırlanmıştır — şablon metin değildir.
> `[DOLDURULACAK]` işaretli alanlar hukuki/idari bilgi gerektirir; yayımlamadan önce
> veri sorumlusu tarafından tamamlanmalı ve tercihen bir KVKK danışmanına kontrol ettirilmelidir.

## İçerik

| Dosya | Amaç | Muhatap |
|---|---|---|
| [aydinlatma-metni.md](aydinlatma-metni.md) | KVKK m.10 aydınlatma yükümlülüğü | Platform kullanıcıları (kurum personeli) |
| [veri-envanteri.md](veri-envanteri.md) | Kişisel veri işleme envanteri (VERBİS temeli) | Veri sorumlusu / denetim |
| [verbis-hazirlik.md](verbis-hazirlik.md) | VERBİS kayıt hazırlık kontrol listesi | Veri sorumlusu |

## Sistemde hazır olan teknik mekanizmalar (2026-07-08 doğrulaması)

- **Veri taşınabilirliği (m.11):** `GET /auth/api/user/export-my-data` — kullanıcı kendi verisini JSON alır (`app/routes/auth.py:194`)
- **Silme/anonimleştirme (m.7):** `POST /auth/api/user/delete-my-account` — hesap anonimleştirilir (`app/routes/auth.py:274`); platform genelinde **soft delete** politikası (hard delete yasak, KURALLAR §3)
- **Denetim izi:** `audit_logs` tablosu (KVKK_DATA_EXPORT / KVKK_USER_DELETE aksiyonları loglanır)
- **Erişim güvenliği:** parola hash (werkzeug), TOTP 2FA, Google SSO, oturum çerezleri Secure/HttpOnly/SameSite=Strict, rate limit, CSP
- **Şifreleme:** hassas yapılandırmalar `ENCRYPTION_KEY` ile; aktarımda TLS (https zorunlu, HSTS)
- **Tenant izolasyonu:** mantıksal `tenant_id` izolasyonu + merkezi tenant guard (TASK-230)
- **Yedekleme:** PostgreSQL gece yedekleri, 30 gün saklama (`scripts/ops/oracle/oracle_full_backup.sh`)

## Bilinen boşluklar (aksiyon gerekli)

1. **Pazarlama sitesinde gizlilik politikası / çerez aydınlatması sayfası YOK** (`micro/modules/marketing/` tarandı) — demo talep formu kişisel veri topluyor (ad/e-posta); yayımlanmadan önce sayfa eklenmeli.
2. **Çerez banner'ı yok** — oturum çerezleri "zorunlu çerez" kapsamında savunulabilir, ancak siteye analitik eklenirse banner şart olur.
3. VERBİS kayıt yükümlülüğü değerlendirmesi `[DOLDURULACAK]` — çalışan sayısı/ciro eşiklerine bağlı (bkz. verbis-hazirlik.md).
4. Yurt dışı aktarım: sunucular Oracle Cloud VM üzerinde — **veri merkezinin bulunduğu ülke/bölge teyit edilmeli** ve yurt dışıysa m.9 kapsamında açık rıza / Kurul izni değerlendirilmeli.
