# HEOM — Sunucu Bağlantı ve Erişim Kılavuzu

> **Amaç:** Bu dosya, **heom.kokpitim.com** yayınının çalıştığı Oracle Cloud sunucusuna ve
> HEOM uygulamasının kendisine doğrudan erişebilmen için gereken **tüm** bilgileri içerir.
> Bu kılavuz HEOM projesine verilince, başka hiçbir kaynağa ihtiyaç duymadan sunucuya
> bağlanıp uygulamayı yönetebilirsin.
>
> **Hazırlanma tarihi:** 2026-06-03 · Sunucudan **canlı keşifle** doğrulanmıştır (salt-okunur).
> **Niteliği:** Tek seferlik erişim kılavuzu.

---

## 0. TL;DR — En hızlı erişim

```bash
# 1) Sunucuya SSH
ssh -i <özel-anahtar-yolu> ubuntu@129.159.30.175

# 2) HEOM dizinine geç
cd /home/ubuntu/heom_project

# 3) Durumu gör
docker ps --filter "name=heom"
docker compose ps

# 4) Public erişim
#    https://heom.kokpitim.com   (login: .env içindeki ADMIN_USERNAME / ADMIN_PASSWORD)
```

---

## 1. Sunucu kimliği

| Alan | Değer |
|------|-------|
| Sağlayıcı | **Oracle Cloud** (paylaşımlı sunucu — birden çok proje barınıyor) |
| Public IP | **129.159.30.175** |
| SSH kullanıcısı | **ubuntu** |
| SSH özel anahtarı | `C:\crt\ssh-key-2026-04-18_v4.key` (Kokpitim ekibinin makinesindeki yol; senin makinende kendi kopyanın yolunu kullan) |
| İşletim sistemi | Ubuntu (ARM64) |
| Konteyner motoru | Docker + Docker Compose v2 |
| Reverse proxy | nginx + Certbot (Let's Encrypt SSL) |
| DNS / CDN | Cloudflare |

### SSH bağlantısı

```bash
# Linux/macOS/WSL veya Git-Bash
ssh -i /path/to/ssh-key-2026-04-18_v4.key ubuntu@129.159.30.175

# Windows PowerShell
ssh -i C:\crt\ssh-key-2026-04-18_v4.key ubuntu@129.159.30.175
```

> ⚠️ Anahtarın izinleri çok açıksa SSH reddeder. Linux/WSL'de: `chmod 600 <anahtar>`.
> Windows'ta dosyayı yalnızca kendi kullanıcına okutacak şekilde ayarla (icacls).

---

## 2. Public yayın zinciri (nasıl erişiliyor)

```
İnternet
  → Cloudflare (DNS + proxy, heom.kokpitim.com)
    → Oracle sunucu :443  (nginx, SSL — Let's Encrypt/Certbot)
      → proxy_pass http://127.0.0.1:5001
        → Docker konteyneri  heom-app  (Flask, port 5001)
```

- **Public URL:** https://heom.kokpitim.com
- **nginx config:** `/etc/nginx/sites-available/heom.conf` (sites-enabled'a sembolik bağlı)
- **SSL sertifikası:** `/etc/letsencrypt/live/heom.kokpitim.com/` (Certbot otomatik yeniler)
- HTTP (80) → HTTPS (443) **301 yönlendirme** zaten tanımlı.

nginx config'i görmek / test etmek / yeniden yüklemek:

```bash
sudo cat /etc/nginx/sites-available/heom.conf
sudo nginx -t                 # config sözdizimi testi
sudo systemctl reload nginx   # kesintisiz yeniden yükle
```

> 🚩 nginx **tüm projeler için ortak**. Yalnızca `heom.conf` dosyasına dokun; diğer
> `*.conf` dosyalarını (kokpitim, certifiga, nasreddin…) **değiştirme**.

---

## 3. Uygulama mimarisi (HEOM nedir, nasıl çalışıyor)

HEOM, **hukuki karar (içtihat) analiz paneli** — Flask tabanlı bir web uygulaması.
Playwright (Chromium) ile otomatik karar indirme botu ("BGE bot"), ChromaDB vektör
veritabanı (RAG) ve PostgreSQL içerir.

| Bileşen | Değer |
|---------|-------|
| Uygulama kök dizini | `/home/ubuntu/heom_project` |
| Giriş noktası | `HEOM_Dashboard/app.py` (tek dosya, ~131 KB Flask app) |
| Çalıştırma | `CMD ["python", "HEOM_Dashboard/app.py"]` (Dockerfile) |
| Python | 3.11-slim (+ Playwright Chromium, sistem GUI kütüphaneleri) |
| Dahili port | **5001** (host'a `5001:5001` map'li) |
| Orkestrasyon | `docker-compose.yml` (aynı dizinde) |

### Konteynerler

| Konteyner | Görev | Port |
|-----------|-------|------|
| **heom-app** | Flask web uygulaması | `0.0.0.0:5001 → 5001` |
| **heom-postgres** | PostgreSQL 16 veritabanı | `5432:5432` (host'ta açık) |

### Önemli route'lar (HEOM_Dashboard/app.py)

| Route | İşlev |
|-------|-------|
| `/` | Ana panel (login gerekli) |
| `/login`, `/logout` | Basic admin oturumu (ADMIN_USERNAME/PASSWORD) |
| `/indirme` | Karar indirme ekranı |
| `/api/get_stats` | İstatistik API |
| `/api/bge/start`, `/api/bge/stop` | İndirme botunu başlat/durdur |
| `/api/bge_status`, `/api/bge_logs` | Bot durumu / logları |
| `/api/bot_day_status` | Günlük bot durumu |

### Bağlı veri hacimleri (volumes)

| Host yolu | Konteyner içi | Amaç |
|-----------|---------------|------|
| `./data` | `/app/data` | Uygulama verisi |
| `/home/ubuntu/master_chroma_db` | `/home/ubuntu/master_chroma_db` | ChromaDB vektör DB (`MASTER_HUKUK_DB`, koleksiyon `master_hukuk_kulliyati`) |
| `/home/ubuntu/heom_data/kararlar_290k` | `/app/decision_texts` (salt-okunur) | ~290.000 karar metni |

---

## 4. Konteyner yönetimi (günlük operasyon)

Tüm komutlar **`/home/ubuntu/heom_project`** dizininden çalıştırılır:

```bash
cd /home/ubuntu/heom_project

docker compose ps                 # durum
docker compose logs -f heom-app   # canlı uygulama logu
docker compose logs --tail=200 heom-app

docker compose restart heom-app   # yalnızca uygulamayı yeniden başlat
docker compose restart            # uygulama + postgres

docker compose up -d              # ayakta değilse başlat
docker compose down               # durdur (postgres dahil) — DİKKAT
```

Tek konteyner komutları (compose'suz):

```bash
docker ps --filter "name=heom"
docker logs -f heom-app
docker restart heom-app
docker exec -it heom-app bash     # konteyner içine gir (debug)
```

### Kod güncelleyip yeniden derleme (deploy)

```bash
cd /home/ubuntu/heom_project
# (kodu güncelle: git pull / rsync / scp — projenin yöntemi neyse)
docker compose build heom-app     # imajı yeniden derle
docker compose up -d heom-app     # yeni imajla ayağa kaldır
docker compose logs -f heom-app   # doğrula
```

> Build, Playwright Chromium + sistem kütüphaneleri kurduğu için **birkaç dakika** sürebilir.

---

## 5. Veritabanı erişimi (PostgreSQL)

`docker-compose.yml`'den okunan bağlantı bilgileri:

| Alan | Değer |
|------|-------|
| Konteyner | `heom-postgres` |
| Sürüm | PostgreSQL **16** |
| Veritabanı | **karar_db** |
| Kullanıcı | **heom** |
| Parola | **heom_pass** |
| Port | host **5432** (`5432:5432`) |

### Konteyner içinden (en güvenli)

```bash
docker exec -it heom-postgres psql -U heom -d karar_db
# \dt   tablo listesi
# \q    çık
```

### Host'tan / uzaktan

```bash
# Sunucu üzerinden
psql "postgresql://heom:heom_pass@127.0.0.1:5432/karar_db"

# Yedek alma
docker exec heom-postgres pg_dump -U heom karar_db | gzip > heom_karar_db_$(date +%F).sql.gz
```

> 🔐 **Güvenlik notu:** `heom_pass` zayıf bir varsayılan paroladır ve postgres portu host'ta
> (`5432:5432`) açıktır. Üretim için parolayı güçlendirip portu yalnızca localhost'a
> (`127.0.0.1:5432:5432`) bağlamayı değerlendir. **certifiga-db** de postgres'tir ama yalnızca
> kendi ağı içinde; host 5432 = HEOM postgres.

---

## 6. Ortam değişkenleri (.env)

**Konum:** `/home/ubuntu/heom_project/.env`
**Yükleme:** `docker-compose.yml` → `heom-app.env_file: .env` (ayrıca app.py'de özel yükleyici).

Tanımlı anahtarlar (değerler **sunucudaki .env'de** — gizli, bu dokümana yazılmadı):

| Anahtar | Amaç |
|---------|------|
| `SECRET_KEY` | Flask oturum imzalama |
| `BASE_DIR` | Uygulama temel dizini (varsayılan `/app`) |
| `ADMIN_USERNAME` | Panel giriş kullanıcı adı |
| `ADMIN_PASSWORD` | Panel giriş parolası |

Değerleri görmek (yalnızca sunucuda, yetkin varsa):

```bash
cat /home/ubuntu/heom_project/.env
```

İsteğe bağlı/gelişmiş anahtarlar (app.py tarafından okunuyor, .env'de tanımlanabilir):
`PYTHON_EXECUTABLE`, `BGE_PYTHON`, `BGE_SCRIPT`, `BGE_TRACKER`,
`MASTER_CHROMA_DB_DIR`, `MASTER_CHROMA_COLLECTION`, `ESAS_IDX_DB`,
`MASTER_CHROMA_HOST_DIR`, `DECISION_TEXTS_HOST_DIR`.

> 🔐 `.env` gizli değerler içerir — **versiyon kontrolüne ekleme**, başkasıyla paylaşma.

---

## 7. Loglar ve tanılama

```bash
# Uygulama logu (canlı)
docker compose -f /home/ubuntu/heom_project/docker-compose.yml logs -f heom-app

# Konteyner içi debug logu (büyük olabilir — app_debug.log ~360 MB!)
ls -lh /home/ubuntu/heom_project/HEOM_Dashboard/app_debug.log
tail -f /home/ubuntu/heom_project/HEOM_Dashboard/app_debug.log

# Health smoke test
curl -I https://heom.kokpitim.com
curl -I http://127.0.0.1:5001         # sunucudan, nginx'i atlayarak
```

> ⚠️ `HEOM_Dashboard/app_debug.log` çok büyüyebiliyor (keşifte ~360 MB). Disk dolmasını
> önlemek için periyodik döndürme/temizleme düşün (`: > app_debug.log` ile sıfırla).

---

## 8. 🚩 Paylaşımlı sunucu — kırmızı çizgiler

Bu sunucuda **HEOM dışında** başka canlı projeler var. HEOM'a müdahale ederken
**yalnızca `heom-*` hedeflerine** dokun:

| Proje | Konteyner(ler) | Host portu |
|-------|----------------|------------|
| **HEOM** ← senin alanın | `heom-app`, `heom-postgres` | 5001, 5432 |
| Kokpitim (canlı/test/demo) | `kokpitim-web`, `kokpitim-test-web`, `kokpitim-demo-web` | 8088 / 5050 / 5080 |
| Certifiga | `certifiga-app`, `certifiga-db`, `certifiga-redis` | 8005 |
| Nasreddin | `merkez-nasreddin-app-1` | 8003 |
| Can (Jupyter) | `can-jupyter` | 8004 |
| Altyapı | `portainer`, `open-webui`, `qdrant`, `ollama` | 9000/8080/6333/11434 |

**Kurallar:**
- `docker compose down` / `docker system prune` gibi komutları **HEOM dizininde** ve
  **hedef belirterek** çalıştır. Global `docker stop $(docker ps -q)` gibi komutlar **YASAK** —
  diğer projeleri de düşürür.
- Diğer konteynerlere, nginx config'lerine, port atamalarına dokunma.
- Disk/temizlik işlemlerinde HEOM'a ait olmayan dosyaları (`/home/ubuntu/heom.zip` hariç —
  o eski bir arşiv) silme.

---

## 9. Hızlı referans kartı

```
PUBLIC      : https://heom.kokpitim.com        (login: .env ADMIN_USERNAME/PASSWORD)
SSH         : ssh -i <key> ubuntu@129.159.30.175
APP DİZİN   : /home/ubuntu/heom_project
GİRİŞ       : HEOM_Dashboard/app.py  (Flask, port 5001)
KONTEYNER   : heom-app (5001) · heom-postgres (5432)
COMPOSE     : /home/ubuntu/heom_project/docker-compose.yml
NGINX       : /etc/nginx/sites-available/heom.conf  → proxy 127.0.0.1:5001
SSL         : /etc/letsencrypt/live/heom.kokpitim.com/  (Certbot)
DB          : karar_db / heom / heom_pass  @ 127.0.0.1:5432  (postgres:16)
ENV         : /home/ubuntu/heom_project/.env
CHROMA      : /home/ubuntu/master_chroma_db  (koleksiyon: master_hukuk_kulliyati)
KARARLAR    : /home/ubuntu/heom_data/kararlar_290k  (~290k metin, read-only)

YENİDEN BAŞLAT : cd /home/ubuntu/heom_project && docker compose restart heom-app
LOG            : docker compose logs -f heom-app
DEPLOY         : docker compose build heom-app && docker compose up -d heom-app
DB SHELL       : docker exec -it heom-postgres psql -U heom -d karar_db
```

---

## 10. Sık karşılaşılan durumlar

| Belirti | Kontrol / Çözüm |
|---------|-----------------|
| Site açılmıyor (502/504) | `docker ps \| grep heom-app` ayakta mı? `docker compose restart heom-app` |
| 5001 cevap vermiyor | `curl -I http://127.0.0.1:5001` — uygulama logu: `docker compose logs --tail=100 heom-app` |
| SSL uyarısı / süresi dolmuş | `sudo certbot certificates`, gerekirse `sudo certbot renew` |
| nginx 404/yanlış yönlendirme | `sudo nginx -t && sudo systemctl reload nginx`; `heom.conf` doğru mu? |
| DB bağlanamıyor | `docker ps \| grep heom-postgres` (healthy mi?); `docker compose restart postgres` |
| Disk doluyor | `df -h /`; `app_debug.log` boyutu (`: > .../app_debug.log`); `docker image prune -af` (DİKKAT: paylaşımlı — yalnızca dangling imajlar) |
| Bot (BGE) çalışmıyor | `/api/bge_status`, `/api/bge_logs`; Playwright Chromium imaj içinde kurulu mu (`docker exec heom-app python -m playwright install --dry-run chromium`) |

---

*Bu kılavuz 2026-06-03'te `129.159.30.175` üzerinde canlı, salt-okunur keşifle (docker ps,*
*docker-compose.yml, nginx heom.conf, Dockerfile, .env anahtarları, app.py route'ları) doğrulandı.*
*Gizli değerler (SECRET_KEY, ADMIN_PASSWORD) bilinçli olarak bu dosyaya yazılmadı — sunucudaki*
*`.env`'den okunur.*
