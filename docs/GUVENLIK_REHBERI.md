# 🔐 KOKPITIM — Güvenlik Operasyon Rehberi

> **Hedef kitle:** DevOps / sistem yöneticisi
> **Son güncelleme:** Sprint 47

## 1. Production'a İlk Çıkış Checklist

### 1.1 Secrets üretimi (5 dakika)

```bash
# SECRET_KEY üret
python -c "import secrets; print(secrets.token_hex(32))"
# Çıktıyı .env.production'da SECRET_KEY= satırına yapıştır

# DB password üret (en az 24 karakter)
python -c "import secrets; print(secrets.token_urlsafe(24))"

# Postgres user yarat:
sudo -u postgres psql -c "CREATE USER kokpitim_prod WITH PASSWORD 'YUKARIDAKI_SIFRE';"
sudo -u postgres psql -c "CREATE DATABASE kokpitim_prod OWNER kokpitim_prod;"
```

### 1.2 .env.production konum + izin

```bash
# Sadece app user okuyabilsin
chown www-data:www-data .env.production
chmod 600 .env.production

# .gitignore kontrol:
grep -E "^\.env\.production$" .gitignore || echo ".env.production" >> .gitignore
```

### 1.3 SECRET_KEY rotasyon (planlı 90 günde bir)

⚠️ **UYARI:** SECRET_KEY değişince tüm aktif session'lar geçersizleşir.
Kullanıcılar tekrar giriş yapmak zorunda kalır. Düşük trafik saatinde yap.

```bash
# 1. Yeni key üret
NEW_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# 2. .env.production'da güncelle (manuel)
# 3. Uygulamayı restart et:
docker compose restart web   # Docker ise
systemctl restart kokpitim   # systemd ise

# 4. Audit log'a kaydet (manuel):
sudo -u postgres psql kokpitim_prod -c "
  INSERT INTO audit_logs (action, resource_type, description, created_at)
  VALUES ('SECRET_KEY_ROTATION', 'SECURITY', 'Manuel rotasyon', NOW());
"
```

### 1.4 DB password rotasyon (yıllık)

```bash
# 1. Yeni şifre üret
NEW_PW=$(python -c "import secrets; print(secrets.token_urlsafe(24))")

# 2. Postgres'te değiştir:
sudo -u postgres psql -c "ALTER USER kokpitim_prod WITH PASSWORD '$NEW_PW';"

# 3. .env.production'da SQLALCHEMY_DATABASE_URI'yi güncelle

# 4. Uygulamayı restart et
```

---

## 2. Düzenli Güvenlik İşlemleri

### 2.1 Audit log incelemesi (haftalık)

```sql
-- Şüpheli aktiviteler
SELECT action, count(*) FROM audit_logs
WHERE created_at > NOW() - INTERVAL '7 days'
  AND action IN ('LOGIN_FAILED', 'LOGIN_BLOCKED_LOCKED', 'ACCOUNT_LOCKED',
                 'CROSS_TENANT_BLOCKED', 'PASSWORD_CHANGED', 'KVKK_USER_DELETE',
                 '2FA_DISABLED')
GROUP BY action ORDER BY count(*) DESC;

-- Tek IP'den çok başarısız login
SELECT ip_address, count(*) FROM audit_logs
WHERE action = 'LOGIN_FAILED' AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY ip_address HAVING count(*) > 20
ORDER BY count(*) DESC;
```

### 2.2 Backup şifre rotasyonu (3 ayda bir)

`/ayarlar/yedekleme` panelindeki backup şifresini düzenli değiştir.

### 2.3 SSL/TLS sertifikası

Cloudflare/Let's Encrypt otomatik yenileme aktif olduğundan emin ol.
Sertifika 30 günden az kalmışsa uyarı sistemi:

```bash
# /etc/cron.daily/cert-check.sh
echo | openssl s_client -servername kokpitim.kurum.com -connect kokpitim.kurum.com:443 2>/dev/null | \
  openssl x509 -noout -dates | grep notAfter
```

---

## 3. Acil Müdahale Senaryoları

### 3.1 SECRET_KEY sızdırıldı şüphesi

1. **Hemen yeni key üret + restart** (yukarıdaki 1.3 adımları)
2. Tüm aktif session'lar geçersizleşir
3. 2FA aktif kullanıcılar yine 2FA gerektirir → güvenli
4. Audit log incele: son 48 saat anormallik var mı?

### 3.2 Toplu hesap ele geçirme şüphesi

```sql
-- Son 24 saatte yeni IP'den login olan tüm kullanıcılar
SELECT DISTINCT u.email, l.ip_address, l.created_at
FROM audit_logs l JOIN users u ON l.user_id = u.id
WHERE l.action LIKE '%OTURUM%' AND l.created_at > NOW() - INTERVAL '24 hours'
  AND l.ip_address NOT IN (
    SELECT DISTINCT ip_address FROM audit_logs
    WHERE user_id = u.id AND created_at < NOW() - INTERVAL '1 day'
    AND ip_address IS NOT NULL
  );
```

Şüpheli kullanıcıları zorla logout (session invalidate):
```bash
# Tüm session'ları geçersizleştir (nuclear option)
# = SECRET_KEY rotasyonu
```

### 3.3 Cross-tenant data leakage tespit

```sql
SELECT user_id, description, ip_address, created_at FROM audit_logs
WHERE action = 'CROSS_TENANT_BLOCKED'
ORDER BY created_at DESC LIMIT 100;
```

Sıkça blocking olan user'ları araştır → kötü niyet veya bug?

---

## 4. KVKK Uyumluluk

### 4.1 Veri silme talebi

Kullanıcı kendisi: Profile → "Hesabımı Sil" butonu (Sprint 16)
Manuel: SQL ile anonimleştirme:
```sql
UPDATE users SET
  email = CONCAT('deleted_', SUBSTRING(md5(id::text), 1, 8), '@anonim.local'),
  first_name = 'Silindi', last_name = 'Kullanıcı',
  phone_number = NULL, profile_picture = NULL,
  password_hash = '!', is_active = false
WHERE id = :user_id;

INSERT INTO audit_logs (action, resource_type, resource_id, description, created_at)
VALUES ('KVKK_USER_DELETE_MANUAL', 'SECURITY', :user_id, 'Admin tarafından KVKK silme', NOW());
```

### 4.2 Veri export talebi

Kullanıcı kendisi: Profile → "Verilerimi İndir"
Manuel: `/api/user/export-my-data` admin-tarafından user impersonate ile

### 4.3 Audit log retention (90 gün)

```sql
-- Aylık cron job — 90 günden eski audit log'ları anonimleştir
UPDATE audit_logs
SET ip_address = REGEXP_REPLACE(ip_address, '\.\d+$', '.0'),  -- son octet 0
    user_agent = '[anonimize]'
WHERE created_at < NOW() - INTERVAL '90 days'
  AND ip_address IS NOT NULL;
```

---

## 5. Pentestler ve Düzenli Audit'ler

### Yıllık
- 3rd-party penetration test
- SOC 2 / ISO 27001 dökümantasyon güncellemesi (`docs/SOC2_ISO27001_HAZIRLIK.md`)
- Dependency audit: `pip list --outdated`, GitHub Dependabot

### Aylık
- Audit log analizi
- SSL sertifika expiration
- Backup test (restore deneme)
- DB sequence senkron check

### Haftalık
- Failed login pattern analizi
- Active 2FA kullanım oranı
- Cross-tenant blocked event count
- Disk + memory monitoring

---

## 6. İletişim ve Bildirim

- Güvenlik açığı bildirimi: security@kurum.com
- KVKK Veri Sahibi Hakları talepleri: kvkk@kurum.com
- Acil müdahale: 7/24 nöbetçi numara

---

> Bu doküman canlı tutulmalı; her güvenlik patch'i sonrası güncellenir.
