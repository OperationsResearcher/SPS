# VM’den yerele (Kokpitim / kokpitim.com)

Bu dosya, **üretim VM’indeki** (Oracle Cloud) kod veya verinin geliştirme makinesine **kontrollü şekilde** alınması için referans yordamdır.

> **VM = Oracle** (`ubuntu@129.159.30.175`, `/opt/kokpitim/...`). Eski GCP komutları arşiv.  
> `docs/ORACLE-PROD-VM.md`

Ters yön (yerel → VM): `docs/YERELDEN_VM_YAYIN.md`.  
Altyapı: `docs/PROJE-MASTER.md` → bölüm 12.

---

## Ne zaman gerekir?

| Durum | Tipik çözüm |
|-------|-------------|
| Yerel `main` geride kaldı | Önce **GitHub `git pull`** — VM genelde `main` ile aynı commit’te olmalıdır. |
| VM’de commitlenmemiş / deneysel kod var | VM’de `git status`, diff veya seçili dosyaları **`scp`** / yama olarak alın (aşağıda). |
| Canlı veriyle hata ayıklama | **PostgreSQL dump** indirip yerelde restore (Kişisel veri / KVKK — anonimleştirme düşünün). |
| `instance/` yüklemeleri, logo vb. | VM `public_html/instance` veya konteyner volume’dan **dosya kopyası**. |

---

## Ön koşullar

- Oracle VM’e **SSH** / **SCP** (ör. `ssh -i ... ubuntu@129.159.30.175`).
- Yerelde: proje kökü (`C:\kokpitim`), PostgreSQL client (dump restore için).
- **Üretim `.env`, şifreler, API anahtarları** Git’e ve paylaşılan repoya **konmaz**.

---

## A — Kod: tercih edilen yol (Git)

Üretimde yayın akışı `git pull origin main` ile gidiyorsa, yerel makinede:

```powershell
cd C:\kokpitim
git fetch origin
git status
git pull origin main
```

VM’de hangi commit’in çalıştığını görmek için (SSH oturumunda):

```bash
cd /opt/kokpitim/app && git rev-parse HEAD && git log -1 --oneline
```

Yerelde aynı commit’i kullanmak:

```powershell
git fetch origin
git checkout main
git pull origin main
# İsteğe bağlı: VM'deki SHA ile hizala
# git checkout <VM'deki_commit_sha>
```

Bu yöntem **VM dosya sisteminden kopyalamadan** en güvenli senkron yoldur.

---

## B — Kod: VM’de yerel GitHub’da olmayan değişiklikler

1. SSH ile VM’ye bağlanın.
2. `cd /opt/kokpitim/app && git status`
3. Gerekirse yama veya tek dosya çıkarın:

```bash
# Örnek: tek dosyayı /tmp altına
sudo cp yol/dosya.py /tmp/dosya.py
sudo chmod a+r /tmp/dosya.py
```

Yerel PowerShell:

```powershell
scp -i C:\crt\ssh-key-2026-04-18_v4.key ubuntu@129.159.30.175:/tmp/dosya.py C:\kokpitim\yol\dosya.py
```

**Uyarı:** Sunucudaki tüm ağacı başka bir branch’e commit etmeden yerel ile ezme, iz sürülemez merge’lere yol açar. Mümkünse önce VM’de veya makinede branch + commit.

---

## C — Veritabanı: VM PostgreSQL → yerel

Canlı veri **PostgreSQL** (`kokpitim_db`, VM host’ta). Yerel geliştirme de projede PostgreSQL beklenir (`config`/`.env`).

### 1) Dump’ı VM’de üretme

SSH:

```bash
TS=$(date +%Y%m%d_%H%M%S)
sudo -u postgres pg_dump -Fc kokpitim_db > /tmp/kokpitim_db_${TS}.dump
# veya düz SQL:
# sudo -u postgres pg_dump kokpitim_db | gzip -c > /tmp/kokpitim_db_${TS}.sql.gz
sudo chmod a+r /tmp/kokpitim_db_${TS}.dump
```

### 2) Yerel bilgisayara indirme

```powershell
scp -i C:\crt\ssh-key-2026-04-18_v4.key ubuntu@129.159.30.175:/tmp/kokpitim_db_YYYYMMDD_HHMMSS.dump C:\kokpitim\backups\
```

### 3) Yerelde restore (özet)

- **Yerel veritabanı adı** ve kullanıcı `.env` içindeki `SQLALCHEMY_DATABASE_URI` ile uyumlu olmalı.
- **Özel format** (`-Fc`): `pg_restore -d hedef_veritabani ...`
- **Düz SQL** (`*.sql.gz`): `gunzip -c ... | psql ...` veya sıkıştırılmamış `psql -f ...`

**Sürüm uyarısı:** `pg_restore` / `psql` sürümü sunucudan çok eskiyse hata verebilir. Sorun çıkarsa dump’ı VM’de (sunucu ile aynı major) üretin veya uyumlu client kurun.

### KVKK / güvenlik

Canlı veri içerir: e-posta, kişisel içerik. Mümkünse **anonimleştirilmiş** kopya kullanın; dosyayı şifreli diskte tutun, paylaşmayın.

---

## D — `instance/` ve yüklemeler

VM yolu: `/opt/kokpitim/instance/` (logolar, `uploads` vb.).

```powershell
scp -i C:\crt\ssh-key-2026-04-18_v4.key -r ubuntu@129.159.30.175:/opt/kokpitim/instance/uploads/tenant_logos C:\kokpitim\instance\uploads\
```

Doğrulama (SSH): `ls -la /opt/kokpitim/instance`

---

## E — Bilerek yapılmayanlar

- Üretim **`.env`** dosyasının tamamını repoya koymak.
- **`SECRET_KEY`**, SMTP, üçüncü parti anahtarlarını yerel `.env`’e birebir taşımak (gerekirse ayrı dev anahtarlar).
- Üzerinde çalışılacak canlı DB’nin **yazma** amaçlı paylaşımı (tercihen salt okunur / kopya).

---

## F — Kontrol listesi

- [ ] Kod için önce `git pull origin main` (veya VM SHA ile hizalama) denendi.
- [ ] VM’de `git status` temiz veya farklar bilinçli olarak alındı.
- [ ] DB indirildiyse restore yerelde başarılı; `SQLALCHEMY_DATABASE_URI` güncellendi.
- [ ] Gizli anahtarlar / tam üretim `.env` repoya girmedi.
- [ ] Hassas dump dosyası güvenli konumda, gereksiz kopyalar silindi.

---

## Cursor / “VM’den yerele çek” talimatı

> `docs/VM_DEN_YERELE.md` yönergesine göre ilerle: önce Git senkronu; gerekirse VM `pg_dump` + `gcloud compute scp` ve yerel restore; `.env`/gizlilik kurallarına uy.

---

*Son güncelleme: 2026-04-03*
