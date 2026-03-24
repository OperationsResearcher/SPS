# PostgreSQL Geçiş Rehberi

> **Amaç:** Yerel ve yayın ortamını aynı yapıya getirmek — her ikisinde de PostgreSQL.
> Yerelde geliştirip test ediyoruz, VM'de yayınlıyoruz.
>
> Son güncelleme: 2026-03-24

---

## 1. Genel Bakış

| Ortam   | Veritabanı   | Kullanım                         |
|---------|--------------|-----------------------------------|
| Yerel   | PostgreSQL   | Geliştirme, test                  |
| VM      | PostgreSQL   | Yayın (kokpitim.com)              |

**Akış:** Yerelde PostgreSQL ile geliştir → Test et → VM'ye deploy et.

| Önceki           | Sonraki        |
|------------------|----------------|
| SQLite (tek dosya)| PostgreSQL (yerel + VM) |
| ~20–50 kullanıcı sınırı | 30–40+ rahat kapasite |

---

## 2. Yerel Makinede Yapılacaklar

Tüm adımlar **geliştirme bilgisayarınızda** (Windows + Cursor) yapılır.

### 2.1 requirements.txt

`psycopg2-binary>=2.9.0` eklendi. (`requirements.txt`)

### 2.2 PostgreSQL Kurulumu (Windows)

1. İndir: https://www.postgresql.org/download/windows/
2. **EDB Installer** ile kurun; kurulum sırasında:
   - Port: `5432` (varsayılan)
   - postgres kullanıcısı için şifre belirleyin
3. Kurulum sonrası **pgAdmin** veya **psql** ile bağlantıyı test edin.

Alternatif (Chocolatey):
```powershell
choco install postgresql
```

**Yerel PostgreSQL dizinleri (bu proje):**
| Amaç | Yol |
|------|-----|
| Veri dizini (PGDATA) | `C:\pgdata2` |
| Bin (pg_dump, psql) | Kuruluma göre `C:\Program Files\PostgreSQL\<versiyon>\bin` — yedekleyici için PATH'e eklenmeli |

### 2.3 Yerel Veritabanı ve Kullanıcı Oluşturma

**pgAdmin** veya **psql** ile:

```sql
CREATE USER kokpitim_user WITH PASSWORD 'kokpitim_dev_123';
CREATE DATABASE kokpitim_db OWNER kokpitim_user;
GRANT ALL PRIVILEGES ON DATABASE kokpitim_db TO kokpitim_user;
\c kokpitim_db
GRANT ALL ON SCHEMA public TO kokpitim_user;
```

> Yerelde basit şifre kullanılabilir; VM'de güçlü şifre kullanın.

### 2.4 SQLite → PostgreSQL Veri Taşıma (Yerelde)

**Seçenek A — pgloader (Windows):**

- pgloader: https://github.com/dimitri/pgloader/releases
- Çalıştır:
```cmd
pgloader instance/kokpitim.db postgresql://kokpitim_user:kokpitim_dev_123@localhost/kokpitim_db
```

**Seçenek B — Alembic + Python script:**

1. Boş schema oluştur:
```powershell
$env:SQLALCHEMY_DATABASE_URI="postgresql://kokpitim_user:kokpitim_dev_123@localhost/kokpitim_db"
flask db upgrade
```

2. Veri taşıma scripti çalıştır (projede `scripts/sqlite_to_postgres.py` varsa).

### 2.5 .env Ayarları (Yerel)

Proje kökündeki `.env` dosyasına ekleyin veya güncelleyin:

```
SQLALCHEMY_DATABASE_URI=postgresql://kokpitim_user:kokpitim_dev_123@localhost/kokpitim_db
```

> SQLite URI satırını yorum satırı yapın veya silin.

### 2.6 Yerel Çalıştırma ve Test

```powershell
pip install -r requirements.txt
python app.py
# veya: flask run
```

Tarayıcıda `http://127.0.0.1:5001` — giriş, süreç, karne, faaliyet sayfalarını test edin.

### 2.7 Yerel Kontrol Listesi

- [ ] PostgreSQL kuruldu
- [ ] `kokpitim_db` ve `kokpitim_user` oluşturuldu
- [ ] SQLite verisi PostgreSQL'e taşındı
- [ ] `.env` içinde `SQLALCHEMY_DATABASE_URI` PostgreSQL'e ayarlandı
- [ ] Uygulama yerelde çalışıyor ve test edildi

---

## 3. VM'de Yapılacaklar (Yayın)

Yerelde her şey çalıştıktan sonra VM tarafına geçin.

### 3.0 Tek Komutla Geçiş (Önerilen)

Önce kodu VM'ye alın, sonra:

```bash
gcloud compute ssh sps-server-v2 --zone=europe-west3-c
cd /home/kokpitim.com/public_html
sudo git pull origin main
export PG_PASSWORD='GÜÇLÜ_ŞİFRE_BURAYA'
chmod +x scripts/vm_postgres_migration.sh
./scripts/vm_postgres_migration.sh
```

Bu script: SQLite yedeği → PostgreSQL kurulum → DB oluşturma → `flask db upgrade` → veri taşıma → container'ı PostgreSQL ile başlatma adımlarını otomatik yapar.

### 3.1 VM'ye Bağlan

```bash
gcloud compute ssh sps-server-v2 --zone=europe-west3-c
```

### 3.2 SQLite Yedeği Al (geçiş öncesi zorunlu)

```bash
mkdir -p /home/kokpitim.com/backups
sudo docker cp sps-web:/app/instance/kokpitim.db /home/kokpitim.com/backups/kokpitim_sqlite_$(date +%Y%m%d_%H%M).db
```

### 3.3 PostgreSQL Kur ve Başlat

```bash
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 3.4 VM'de Veritabanı ve Kullanıcı

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

### 3.5 Veri Taşıma (VM'de)

**Not:** 3.0 Tek Komutla Geçiş kullanıyorsanız bu adım otomatik yapılır (Python script ile).

**Alternatif — pgloader (manuel adımlar için):**
```bash
sudo apt-get install -y pgloader
SQLITE_PATH="/home/kokpitim.com/public_html/instance/kokpitim.db"
pgloader "${SQLITE_PATH}" "postgresql://kokpitim_user:GÜÇLÜ_ŞİFRE@localhost/kokpitim_db"
```
> Uyarı: pgloader schema uyumsuzluklarında hata verebilir. Önerilen: 3.0 script.

### 3.6 pg_hba.conf — Docker Erişimi

Container, host PostgreSQL'e bağlanacak. `pg_hba.conf`'a ekleyin:

```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

Ek satır:
```
host    kokpitim_db    kokpitim_user    172.17.0.0/16    md5
host    kokpitim_db    kokpitim_user    127.0.0.1/32     md5
```

```bash
sudo systemctl reload postgresql
```

### 3.7 Kod Güncelle ve Container Başlat

```bash
cd /home/kokpitim.com/public_html
sudo git pull origin main
sudo docker build -t sps_web_final:latest .
sudo docker stop sps-web 2>/dev/null; sudo docker rm sps-web 2>/dev/null
sudo docker run -d \
  --name sps-web \
  -p 80:5000 \
  -v /home/kokpitim.com/public_html/instance:/app/instance \
  -e SQLALCHEMY_DATABASE_URI="postgresql://kokpitim_user:GÜÇLÜ_ŞİFRE@172.17.0.1/kokpitim_db" \
  sps_web_final:latest
```

> `172.17.0.1` — Docker bridge; `ip addr show docker0` ile doğrulayın.

### 3.8 VM Kontrol Listesi

- [ ] SQLite yedeği alındı
- [ ] PostgreSQL kuruldu
- [ ] `kokpitim_db` ve `kokpitim_user` oluşturuldu
- [ ] Veri taşındı
- [ ] `pg_hba.conf` güncellendi
- [ ] Container doğru env ile başlatıldı
- [ ] https://kokpitim.com test edildi

---

## 4. Günlük Akış (Özet)

| Adım | Yerel | VM |
|------|-------|-----|
| Geliştirme | Kod yaz, `app.py` ile çalıştır, PostgreSQL'e bağlan | — |
| Test | http://127.0.0.1:5001 üzerinden test et | — |
| Deploy | `git add`, `git commit`, `git push` | `git pull`, `docker build`, container restart |

---

## 5. Rollback (Acil)

**Yerel:** `.env` içinde `SQLALCHEMY_DATABASE_URI` tekrar SQLite yap; yedek `kokpitim.db` geri koy.

**VM:** Container'ı `SQLALCHEMY_DATABASE_URI=sqlite:////app/instance/kokpitim.db` ile başlat; yedek SQLite dosyasını geri koy.

---

## 6. Faydalı Komutlar

**Yerel (PowerShell):**
```powershell
# PostgreSQL servis durumu
Get-Service postgresql*

# Bağlantı testi
psql -U kokpitim_user -d kokpitim_db -h localhost -c "\dt"

# pg_dump/psql icin PATH (yedekleyici kullanacaksaniz)
$env:PATH = "C:\Program Files\PostgreSQL\16\bin;" + $env:PATH
# veya kalici: Sistem Ozellikleri > Ortam Degiskenleri > Path'e ekleyin
```

**VM:**
```bash
sudo systemctl status postgresql
sudo -u postgres psql -d kokpitim_db -c "\dt"
sudo docker logs sps-web --tail=50
```
