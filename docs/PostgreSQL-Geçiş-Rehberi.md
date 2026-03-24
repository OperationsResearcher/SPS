# PostgreSQL Geçiş Rehberi

> **Plan B:** Mevcut GCP VM'de PostgreSQL kurulumu — ek maliyet yok.
>
> Son güncelleme: 2026-03-23

---

## 1. Genel Bakış

Bu rehber, Kokpitim uygulamasının SQLite'dan PostgreSQL'e geçişini adım adım açıklar. İşlemler **yerel makine** ve **VM** olmak üzere iki aşamada yapılır.

| Önceki | Sonraki |
|--------|---------|
| SQLite (`instance/kokpitim.db`) | PostgreSQL (VM'de lokal) |
| Tek dosya, dosya kilidi | Eşzamanlı bağlantı, satır kilidi |
| ~20–50 kullanıcı sınırı | 30–40+ rahat kapasite |

---

## 2. Yerel Makinede Yapılacaklar

Tüm bu adımlar **geliştirme bilgisayarınızda** (örn. Windows + Cursor) yapılır. VM'ye bağlanmadan önce tamamlanmalıdır.

### 2.1 requirements.txt Güncellemesi

`requirements.txt` dosyasına PostgreSQL driver ekleyin:

```
psycopg2-binary>=2.9.0
```

Proje kökündeki `requirements.txt` dosyasının sonuna veya uygun bir yerine ekleyin.

### 2.2 Yerel DB Yedeği Al (önemli)

Yerelde geliştirme sırasında kullandığınız SQLite veritabanının yedeğini alın:

```powershell
# PowerShell (Windows)
Copy-Item -Path "instance\kokpitim.db" -Destination "instance\kokpitim_backup_$(Get-Date -Format 'yyyyMMdd_HHmm').db"
```

veya manuel olarak `instance\kokpitim.db` dosyasını güvenli bir yere kopyalayın.

### 2.3 .env Örneği (opsiyonel)

PostgreSQL geçişi sonrası kullanılacak ortam değişkenini not edin. Yerelde test etmeyecekseniz sadece referans için:

```
# VM'de container çalışırken kullanılacak
SQLALCHEMY_DATABASE_URI=postgresql://kokpitim_user:ŞİFRE@172.17.0.1/kokpitim_db
```

> Yerelde geliştirmeye SQLite ile devam edebilirsiniz. Sadece VM deploy'da PostgreSQL kullanılacak.

### 2.4 Değişiklikleri Git'e Gönder

Kod değişikliklerini (requirements.txt, varsa config değişiklikleri) commit edip push edin:

```bash
git add requirements.txt
git add -A
git commit -m "PostgreSQL geçişi: psycopg2-binary eklendi"
git push origin main
```

### 2.5 Yerel Özet Kontrol Listesi

- [ ] `requirements.txt`'e `psycopg2-binary>=2.9.0` eklendi
- [ ] Yerel `instance/kokpitim.db` yedeklendi
- [ ] Değişiklikler `git push` ile remote'a gönderildi

---

## 3. Ön Hazırlık (VM)

### 3.1 Yedek Al (zorunlu)

**VM'de:**
```bash
sudo docker cp sps-web:/app/instance/kokpitim.db /home/kokpitim.com/backups/kokpitim_sqlite_$(date +%Y%m%d_%H%M).db
```

**Yerelde (opsiyonel, yedek kopya):**
```bash
gcloud compute scp sps-server-v2:/home/kokpitim.com/backups/kokpitim_sqlite_*.db ./ --zone=europe-west3-c
```

### 3.2 Tahmini Süre

- PostgreSQL kurulum: ~5 dk  
- Veri taşıma: ~5–15 dk (veri boyutuna göre)  
- Config + test: ~10 dk  
- **Toplam:** ~30–45 dk  

---

## 4. VM'de PostgreSQL Kurulumu

### 4.1 VM'ye Bağlan

```bash
gcloud compute ssh sps-server-v2 --zone=europe-west3-c
```

### 4.2 PostgreSQL Kur ve Başlat

```bash
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 4.3 Kokpitim Veritabanı ve Kullanıcı Oluştur

```bash
sudo -u postgres psql << 'EOF'
CREATE USER kokpitim_user WITH PASSWORD 'GÜÇLÜ_ŞİFRE_BURAYA';
CREATE DATABASE kokpitim_db OWNER kokpitim_user;
GRANT ALL PRIVILEGES ON DATABASE kokpitim_db TO kokpitim_user;
\c kokpitim_db
GRANT ALL ON SCHEMA public TO kokpitim_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO kokpitim_user;
EOF
```

> **Güvenlik:** `GÜÇLÜ_ŞİFRE_BURAYA` yerine güçlü bir şifre koyun. Production'da `.env` veya Secret Manager kullanın.

### 4.4 Yerel Bağlantıyı Etkinleştir

PostgreSQL varsayılan olarak `localhost`'tan bağlantı kabul eder. Container ile aynı host'ta çalışacağı için ek ayar gerekmez. Güvenlik için sadece localhost:

```bash
# Kontrol (varsayılan genelde doğrudur)
sudo cat /etc/postgresql/*/main/pg_hba.conf | grep -v '^#' | grep -v '^$'
# local   all   all   peer veya md5 olmalı
```

---

## 5. Veri Taşıma (SQLite → PostgreSQL)

### 5.1 pgloader ile Otomatik Taşıma (önerilen)

```bash
sudo apt-get install -y pgloader
```

SQLite dosyasını container'dan veya host'tan alıp taşıyın:

```bash
SQLITE_PATH="/home/kokpitim.com/public_html/instance/kokpitim.db"
# veya container içindeki: önce kopyalayın
# sudo docker cp sps-web:/app/instance/kokpitim.db /tmp/kokpitim.db
# SQLITE_PATH="/tmp/kokpitim.db"

pgloader "${SQLITE_PATH}" \
  "postgresql://kokpitim_user:GÜÇLÜ_ŞİFRE_BURAYA@localhost/kokpitim_db"
```

### 5.2 pgloader Yoksa — Alembic + Manuel Script

1. Önce boş PostgreSQL schema oluştur:
   ```bash
   cd /home/kokpitim.com/public_html
   export SQLALCHEMY_DATABASE_URI="postgresql://kokpitim_user:GÜÇLÜ_ŞİFRE@localhost/kokpitim_db"
   flask db upgrade
   ```

2. SQLite verisini Python ile aktaran script kullanın (örnek: `scripts/sqlite_to_postgres.py` — projede yoksa ayrı oluşturulmalı).

---

## 6. Uygulama Konfigürasyonu

### 6.1 requirements.txt

`psycopg2-binary` yerel makinede `requirements.txt`'e eklenmiş olmalı (Bölüm 2.1). VM'de `git pull` ile alınır.

### 6.2 Ortam Değişkeni

VM'de veya Docker run ile `.env` / ortam değişkeni:

```bash
export SQLALCHEMY_DATABASE_URI="postgresql://kokpitim_user:GÜÇLÜ_ŞİFRE@host.docker.internal/kokpitim_db"
```

> **Not:** Container içinden host PostgreSQL'e erişim için:
> - Linux'ta `host.docker.internal` yerine host IP veya `172.17.0.1` (Docker bridge) kullanılabilir.
> - Alternatif: PostgreSQL'i container ile aynı Docker network'te çalıştırmak (ayrı PostgreSQL container).

### 6.3 Docker + Host PostgreSQL Bağlantısı

Container, host'taki PostgreSQL'e bağlanacaksa:

```bash
sudo docker run -d \
  --name sps-web \
  -p 80:5000 \
  -e SQLALCHEMY_DATABASE_URI="postgresql://kokpitim_user:ŞİFRE@172.17.0.1/kokpitim_db" \
  --add-host=host.docker.internal:host-gateway \
  sps_web_final:latest
```

Veya `172.17.0.1` yerine host IP:
```bash
ip addr show docker0 | grep inet
# Örn. 172.17.0.1
```

`pg_hba.conf` içinde Docker bridge IP aralığını kabul etmek gerekebilir:
```
# /etc/postgresql/*/main/pg_hba.conf
host    kokpitim_db    kokpitim_user    172.17.0.0/16    md5
```

Sonra:
```bash
sudo systemctl reload postgresql
```

---

## 7. config.py Uyumu

Mevcut `config.py` zaten `SQLALCHEMY_DATABASE_URI` ortam değişkenini kullanıyor. `sqlite:///` ile başlamıyorsa olduğu gibi kabul edilir. Ek kod değişikliği gerekmez — sadece env değerini güncelleyin.

---

## 8. Deploy Script Güncellemesi

PostgreSQL geçişi sonrası:

- `instance/` volume mount'u SQLite için kullanılıyordu. PostgreSQL'de bu mount opsiyonel (log/upload vb. için kalabilir).
- Container başlatırken `-e SQLALCHEMY_DATABASE_URI=...` mutlaka verilmeli.

**Güncellenmiş run örneği:**
```bash
sudo docker run -d \
  --name sps-web \
  -p 80:5000 \
  -v /home/kokpitim.com/public_html/instance:/app/instance \
  -e SQLALCHEMY_DATABASE_URI="postgresql://kokpitim_user:ŞİFRE@172.17.0.1/kokpitim_db" \
  sps_web_final:latest
```

---

## 9. Test ve Doğrulama

```bash
# Container log
sudo docker logs sps-web --tail=100

# Hata kontrolü
sudo docker logs sps-web 2>&1 | grep -i "error\|OperationalError\|connect"

# Sağlık kontrolü
curl -I http://127.0.0.1/
```

Tarayıcıda:
- https://kokpitim.com
- Giriş yap
- Süreç, karne, faaliyet sayfalarını kontrol et

---

## 10. Rollback (SQLite'a Dönüş)

Sorun çıkarsa:

1. Container'ı durdur/sil.
2. `SQLALCHEMY_DATABASE_URI` tekrar SQLite yap:
   ```bash
   -e SQLALCHEMY_DATABASE_URI="sqlite:////app/instance/kokpitim.db"
   ```
3. Yedek SQLite dosyasını `instance/kokpitim.db` olarak geri koy.
4. Container'ı eski parametrelerle yeniden başlat.

---

## 11. Kontrol Listesi

**Yerel (Bölüm 2):**
- [ ] `requirements.txt`'e `psycopg2-binary` eklendi
- [ ] Yerel DB yedeklendi
- [ ] `git push` yapıldı

**VM:**
- [ ] SQLite yedeği alındı
- [ ] PostgreSQL kuruldu ve çalışıyor
- [ ] `kokpitim_db` ve `kokpitim_user` oluşturuldu
- [ ] Veri taşıma tamamlandı (pgloader veya script)
- [ ] `requirements.txt`'e `psycopg2-binary` eklendi
- [ ] `SQLALCHEMY_DATABASE_URI` ortam değişkeni güncellendi
- [ ] `pg_hba.conf` Docker/host erişimine izin veriyor
- [ ] Container yeniden build edildi ve doğru env ile çalışıyor
- [ ] Login, süreç, karne, faaliyet test edildi

---

## 12. Faydalı Komutlar

```bash
# PostgreSQL durumu
sudo systemctl status postgresql

# Kokpitim DB'ye bağlan
sudo -u postgres psql -d kokpitim_db -c "\dt"

# Tablo satır sayıları
sudo -u postgres psql -d kokpitim_db -c "SELECT relname, n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC LIMIT 10;"
```
