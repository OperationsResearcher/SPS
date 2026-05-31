# Oracle Deploy — Hızlı Adımlar

> **VM** = bu sunucu (Oracle). GCP `sps-server-v2` artık canlı değil. Özet: `docs/ORACLE-PROD-VM.md`

## Önkoşul

- GCP yedekleri: `backups/oracle_migration/` ✅
- Oracle SSH anahtarı (`.ssh` altında, `ubuntu@129.159.30.175`)

## Tek komut (yerel PowerShell)

```powershell
cd C:\kokpitim
.\scripts\ops\oracle\oracle_deploy.ps1 -IdentityFile C:\Users\SIZ\.ssh\ORACLE_ANAHTARINIZ
```

Varsayılan git commit (geçiş anı GCP/Oracle ilk deploy): `53334f44`

## Manuel (Oracle SSH içinde)

Dosyalar `/tmp/kokpitim_deploy/` altına yüklendikten sonra:

```bash
export GIT_REF=53334f44fb8216fc5398e977cf073146ac93c8a6
bash /tmp/kokpitim_deploy/oracle_server_bootstrap.sh
```

## DNS (Cloudflare)

| Tip | Ad | İçerik |
|-----|-----|--------|
| A | www | 129.159.30.175 |
| A | @ | 129.159.30.175 |

SSL: `sudo certbot --nginx -d www.kokpitim.com -d kokpitim.com`

## Doğrulama

```bash
curl -sS http://127.0.0.1:8088/health
curl -sS -H "Host: www.kokpitim.com" http://127.0.0.1/health
```

Smoke: `docs/DEPLOY_SMOKE_CHECKLIST.md`
