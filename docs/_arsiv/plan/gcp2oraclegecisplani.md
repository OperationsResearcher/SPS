# GCP → Oracle Cloud Geçiş Planı — www.kokpitim.com

> **Tarih:** 2026-05-21  
> **Durum:** Geçiş uygulandı — **canlı VM = Oracle** (`docs/ORACLE-PROD-VM.md`)  
> **Kaynak (eski):** GCP `sps-server-v2` (Frankfurt) — arşiv / Faz 0 yedekleri  
> **Üretim:** Oracle `kokpitim-v2` — `129.159.30.175` (eu-frankfurt-1)  
> **Referans rapor:** `docs/Oraclecloudrapor.pdf`

---

## Onaylanan kararlar

| # | Karar |
|---|--------|
| 1 | `www.kokpitim.com` Oracle’a taşınacak (GCP sorunu sonrası karar) |
| 2 | **Paylaşımlı sunucu** — diğer uygulamalar (heom, certifiga, ai vb.) çalışmaya devam edecek |
| 3 | Ana Kokpitim uygulaması **`www.kokpitim.com`** üzerinden devam edecek |
| 4 | Host port: **8088** (Docker içi 5000) |
| 5 | **Cloudflare** devam edecek |
| 6 | GCP’den **her şey** çekilecek (DB, instance/uploads, .env, kod snapshot) |
| 7 | `.env` yerelde olmalı; yine de VM’den garanti kopya alınacak |
| 8 | Oracle SSH erişimi mevcut |
| 9 | Kesinti kabul edildi (30–60 dk DNS geçişi) |
| 10 | Disk temizliği plana dahil |

---

## Canlı veri referansı (19 Mayıs kapanış anı)

| Tablo | Kayıt |
|-------|-------|
| tenants | 18 |
| users | 78 |
| kpi_data | 6.133 |

**Yerel dump (2026-05-21):**  
`backups/vm_emergency/kokpitim_db_vm_20260521_211250.dump` (~714 KB, `pg_dump -Fc`)

---

## Port önerisi: 8088

| Port | Mevcut kullanım (Oracle) |
|------|--------------------------|
| 5001 | heom.kokpitim.com |
| 8003–8005 | nasreddin, can, certifiga |
| 8080 | open-webui (localhost) |
| 5432 | PostgreSQL 14 (localhost) |

**8088** boş, HEOM ile çakışmıyor. Docker içi port **5000** (mevcut Dockerfile ile uyumlu).

---

## Hedef mimari

```
Kullanıcı → Cloudflare (TLS) → 129.159.30.175:443
         → nginx (host, Let's Encrypt)
         → localhost:8088
         → Docker: kokpitim-web (Gunicorn :5000)
         → PostgreSQL 14 (host, 127.0.0.1:5432 / kokpitim_db)
         → volume: /opt/kokpitim/instance (uploads, logolar)
```

Diğer subdomain’ler (heom, certifiga, ai…) **nginx config’lerine dokunulmadan** aynı kalır.

---

## Faz 0 — GCP’den tam yedek (kesinti öncesi, ~1 saat)

**Amaç:** Oracle’a geçmeden önce GCP’deki her şeyi yerelde toplamak.

| # | İş | Kaynak (GCP VM) | Hedef (yerel) |
|---|-----|-----------------|---------------|
| 0.1 | PostgreSQL dump (taze) | `pg_dump -Fc kokpitim_db` | `backups/oracle_migration/` |
| 0.2 | `.env` + `.env.postgres` | `/home/kokpitim.com/public_html/` | aynı klasör (**Git’e konmaz**) |
| 0.3 | `instance/` tamamı | uploads, tenant_logos, vb. | `backups/oracle_migration/instance/` |
| 0.4 | Kod snapshot (opsiyonel güvenlik) | `public_html` tar (backups hariç) | `backups/oracle_migration/code_*.tar.gz` |
| 0.5 | Satır sayısı doğrulama | VM PostgreSQL | manifest: 18 / 78 / 6133 |

**Not:** Mevcut dump kullanılabilir; geçiş günü bir kez daha alınır.

**GCP VM bilgileri:**

- Instance: `sps-server-v2` / zone: `europe-west3-c`
- Güncel IP: `35.246.135.36` (eski: `34.89.231.89`)
- Kod dizini: `/home/kokpitim.com/public_html`
- Canlı DB: PostgreSQL `kokpitim_db` (host’ta, Docker dışında)

---

## Faz 1 — Oracle hazırlık (SSH, ~2 saat)

### 1.1 Disk temizliği (onaylı)

Sunucu %78 dolu; Kokpitim için en az **15 GB** boş hedef.

```bash
# Oracle SSH
docker builder prune -af          # ~26 GB build cache
docker image prune -af            # kullanılmayan imajlar
# Onaylıysa: /home/ubuntu/heom.zip (1.3 GB) vb. eski arşivler
df -h /
```

**Kural:** Sadece reclaimable Docker cache + açıkça onaylanmış dosyalar; **çalışan container’lara dokunulmaz.**

### 1.2 PostgreSQL (host PG14)

```bash
sudo -u postgres createdb kokpitim_db
sudo -u postgres createuser kokpitim_app -P   # güçlü şifre
sudo -u postgres psql -c "GRANT ALL ON DATABASE kokpitim_db TO kokpitim_app;"
```

### 1.3 Dizin yapısı

```bash
sudo mkdir -p /opt/kokpitim/{app,instance,backups,logs}
sudo chown -R ubuntu:ubuntu /opt/kokpitim
```

### 1.4 ARM64 Docker imajı

GCP amd64 imajı Oracle ARM’da çalışmaz → Oracle’da `docker build`:

```bash
cd /opt/kokpitim/app
# git clone veya scp ile kod
docker build -t kokpitim_web:latest .
```

**Oracle sunucu özeti (`Oraclecloudrapor.pdf`):**

| Alan | Değer |
|------|--------|
| Hostname | kokpitim-v2 |
| Public IP | 129.159.30.175 |
| Shape | VM.Standard.A1.Flex (ARM64), 4 OCPU / 24 GB |
| OS | Ubuntu 22.04 |
| nginx | host üzerinde TLS reverse proxy |
| Host PG | PostgreSQL 14 @ 127.0.0.1:5432 |

---

## Faz 2 — Veri taşıma (Oracle’a yükleme, ~1–2 saat)

| # | İş |
|---|-----|
| 2.1 | Dump’ı Oracle’a SCP |
| 2.2 | `pg_restore -d kokpitim_db --clean --if-exists ...` |
| 2.3 | Satır sayısı: tenants=18, users=78, kpi_data=6133 |
| 2.4 | `instance/` → `/opt/kokpitim/instance/` |
| 2.5 | `.env`: `SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://kokpitim_app:...@127.0.0.1:5432/kokpitim_db` |
| 2.6 | `TRUST_PROXY=1`, `FLASK_ENV=production`, `RATELIMIT_STORAGE_URL=memory://` (Redis yoksa) |
| 2.7 | Alembic: `docker exec kokpitim-web python3 scripts/run_db_upgrade.py` |

---

## Faz 3 — Uygulama ayağa kaldırma (~1 saat)

```bash
docker run -d --name kokpitim-web \
  --restart unless-stopped \
  -p 127.0.0.1:8088:5000 \
  -v /opt/kokpitim/instance:/app/instance \
  --env-file /opt/kokpitim/.env \
  -e FLASK_ENV=production \
  -e TRUST_PROXY=1 \
  kokpitim_web:latest
```

**Oracle içi test (Cloudflare öncesi):**

```bash
curl -sS http://127.0.0.1:8088/health
# database: ok beklenir
```

---

## Faz 4 — nginx + TLS (~1 saat)

Yeni vhost (mevcut subdomain config’lerine **dokunmadan**):

```nginx
# /etc/nginx/sites-available/www.kokpitim.com
server {
    listen 443 ssl http2;
    server_name www.kokpitim.com kokpitim.com;

    ssl_certificate     /etc/letsencrypt/live/www.kokpitim.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.kokpitim.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8088;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo certbot certonly --nginx -d www.kokpitim.com -d kokpitim.com
sudo ln -s /etc/nginx/sites-available/www.kokpitim.com /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

**Oracle IP ile doğrudan test:**

```bash
curl -k -H "Host: www.kokpitim.com" https://127.0.0.1/health
```

---

## Faz 5 — Cloudflare (manuel adımlar)

Cloudflare panel → **kokpitim.com** → DNS:

| Tip | Ad | İçerik | Proxy | Not |
|-----|-----|--------|-------|-----|
| **A** | `www` | `129.159.30.175` | Proxied | Ana uygulama |
| **A** | `@` | `129.159.30.175` | Proxied | veya `@` → `www` CNAME |

**SSL/TLS sekmesi:**

- Mod: **Full (strict)** (Oracle’da geçerli Let’s Encrypt sertifikası olunca)
- Geçiş anında sorun olursa geçici **Full**

**Eski kayıtları kaldır / güncelle:**

- `www` veya `@` → GCP IP (`34.89.231.89`, `35.246.135.36`) **silinmeli**

**Diğer subdomain’ler:** heom, certifiga, ai vb. **değiştirilmez**.

**Geçiş sonrası (opsiyonel):** Caching → Purge Everything.

---

## Faz 6 — Kesinti penceresi & DNS geçişi (~30–60 dk)

| Sıra | İş |
|------|-----|
| 6.1 | Oracle’da health OK |
| 6.2 | nginx + TLS OK |
| 6.3 | Cloudflare DNS güncelle |
| 6.4 | DNS propagasyon (5–30 dk) |
| 6.5 | Duman testi |

---

## Faz 7 — Duman testi

`docs/DEPLOY_SMOKE_CHECKLIST.md` maddeleri:

- [ ] `https://www.kokpitim.com/auth/login` → 200
- [ ] Login → masaüstü
- [ ] `/masaustu`, `/surec`, `/sp`
- [ ] Tenant logoları (`instance/uploads`)
- [ ] `/health` → `database: ok`
- [ ] `HGS_BYPASS_ENABLED` tanımsız veya `false`

---

## Faz 8 — GCP kapatma (Oracle 1 hafta stabil sonra)

| # | İş |
|---|-----|
| 8.1 | GCP VM **STOP** |
| 8.2 | 7 gün sorunsuz → son snapshot |
| 8.3 | VM + disk sil (isteğe bağlı) |
| 8.4 | GCP billing tekrar kapatılabilir |

---

## Riskler & önlemler

| Risk | Önlem |
|------|--------|
| ARM64 uyumsuzluk | Oracle’da yeniden `docker build` |
| Disk doluluğu | Faz 1.1 temizlik |
| HEOM/port çakışması | Port **8088** |
| Uploads eksik | Faz 0.3 tam `instance/` kopyası |
| Cloudflare eski IP | Faz 5 DNS güncelleme |
| Paylaşımlı sunucu yükü | restart policy + netdata izleme |

---

## Tahmini süre & maliyet

| | |
|---|---|
| Toplam iş | ~1 iş günü |
| Kesinti | 30–60 dk (DNS geçişi) |
| Oracle ek maliyet | Mevcut A1 instance — paylaşımlı, ek ücret yok |
| GCP | STOP sonrası compute ~0 |

---

## Uygulama sırası (onay sonrası)

1. **Faz 0** — GCP’den `.env`, `instance/`, taze dump
2. **Faz 1** — Oracle disk temizliği + PG + dizinler
3. **Faz 2–3** — restore + Docker + health
4. **Faz 4** — nginx + certbot
5. **Faz 5** — Cloudflare DNS cutover
6. **Faz 6–7** — duman testi
7. **Faz 8** — GCP stop (ayrı onay)

---

## İlgili dosyalar

| Dosya | Açıklama |
|-------|----------|
| `docs/Oraclecloudrapor.pdf` | Oracle mevcut altyapı raporu |
| `docs/YERELDEN_VM_YAYIN.md` | Eski GCP deploy yordamı |
| `docs/VM_DEN_YERELE.md` | VM → yerel veri çekme |
| `docs/DEPLOY_SMOKE_CHECKLIST.md` | Canlı doğrulama listesi |
| `scripts/ops/vm_emergency_pull_db.ps1` | Acil PG dump indirme betiği |

---

*Son güncelleme: 2026-05-21*
