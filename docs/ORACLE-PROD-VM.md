# Üretim sunucusu (VM) — Oracle Cloud

> **Terim kuralı (2026-05-21):** Bu repoda ve sohbette **«VM»** = **Oracle Cloud üretim sunucusu**.  
> Eski **GCP** (`sps-server-v2`) artık canlı ortam değildir; yalnızca geçiş arşivi / yedek kaynağıdır.

---

## Özet tablo

| | **VM (üretim)** | **Yerel (geliştirme)** | **GCP (eski — arşiv)** |
|--|-----------------|------------------------|-------------------------|
| Anlam | Canlı `www.kokpitim.com` | `C:\kokpitim` | Kapatılmış kaynak; Faz 0 yedekleri |
| Sunucu | `kokpitim-v2` | Windows / WSL | `sps-server-v2` |
| IP | `129.159.30.175` | — | `35.246.135.36` (artık kullanılmaz) |
| SSH | `ubuntu@129.159.30.175` | — | `gcloud compute ssh` (tarihsel) |
| Uygulama dizini | `/opt/kokpitim/app` | `C:\kokpitim` | `/home/kokpitim.com/public_html` |
| Container | `kokpitim-web` | `py app.py` (5001) | `sps-web` |
| Veritabanı | PostgreSQL `kokpitim_db` @ `127.0.0.1:5432` | PG veya SQLite `instance/` | Aynı PG (taşındı) |
| Deploy betiği | `scripts/ops/oracle/oracle_safe_deploy.sh` | `git push` | `scripts/vm_safe_deploy.sh` (legacy) |

---

## Oracle VM — bağlantı

```powershell
# Yerel Windows (örnek anahtar yolu)
ssh -i C:\crt\ssh-key-2026-04-18_v4.key ubuntu@129.159.30.175
```

| Alan | Değer |
|------|--------|
| Bölge | `eu-frankfurt-1` |
| Shape | `VM.Standard.A1.Flex` (ARM64) |
| `.env` | `/opt/kokpitim/.env` |
| `instance/` | `/opt/kokpitim/instance` |
| Yedekler | `/opt/kokpitim/backups` |
| Nginx | `www.kokpitim.com` → `127.0.0.1:5000` |
| Health | `https://www.kokpitim.com/health` veya VM içi `curl -sS http://127.0.0.1/health` |

PostgreSQL yalnızca **localhost** dinler; dışarıdan `5432` açılmaz. Uygulama container’ı `--network host` ile aynı makinedeki PG’ye bağlanır.

---

## Yayın (yerel → VM)

1. Yerelde: `git push origin main`
2. VM’de (veya yerelden tek SSH):

```bash
cd /opt/kokpitim/app && sudo bash scripts/ops/oracle/oracle_safe_deploy.sh
```

Tek komut (PowerShell):

```powershell
ssh -i C:\crt\ssh-key-2026-04-18_v4.key ubuntu@129.159.30.175 `
  "cd /opt/kokpitim/app && sudo bash scripts/ops/oracle/oracle_safe_deploy.sh"
```

Tam yordam: `docs/YERELDEN_VM_YAYIN.md`  
İlk kurulum / restore: `docs/ORACLE_DEPLOY_ADIMLAR.md`, `docs/gcp2oraclegecisplani.md`

---

## VM → yerel (dump / dosya)

`docs/VM_DEN_YERELE.md` — `scp` hedefi artık `ubuntu@129.159.30.175`, yol `/opt/kokpitim/...`

Örnek dump indirme:

```powershell
scp -i C:\crt\ssh-key-2026-04-18_v4.key `
  ubuntu@129.159.30.175:/opt/kokpitim/backups/pg_kokpitim_db_full_*.sql.gz `
  C:\kokpitim\backups\
```

---

## GCP (eski ortam) — ne zaman adı geçer?

- **Geçiş planı ve Faz 0 yedekleri:** `docs/gcp2oraclegecisplani.md`, `backups/oracle_migration/`
- **Tarihsel komutlar:** `gcloud compute ssh sps-server-v2` — yeni iş için **kullanmayın**
- Agent / kullanıcı «VM’deki DB» dediğinde → **Oracle PostgreSQL** (`kokpitim_db`), yerel `instance/kokpitim.db` ile karıştırmayın

---

## İlgili dosyalar

| Dosya | Açıklama |
|-------|----------|
| `docs/YERELDEN_VM_YAYIN.md` | Kod yayını |
| `docs/VM_DEN_YERELE.md` | VM’den yerele çekme |
| `docs/VM-YEREL-SENKRON-REHBERI.md` | PG senkron notları |
| `scripts/ops/oracle/oracle_deploy.ps1` | İlk bootstrap paketi |
| `scripts/ops/oracle/oracle_safe_deploy.sh` | Rutin deploy |
