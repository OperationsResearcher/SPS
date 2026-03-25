# VM - Yerel Senkron Rehberi

Son guncelleme: 2026-03-24 (durum degerlendirmesi)

## 1) Mevcut Durum Ozeti

- **Kaynak dogruluk:** Uretim ve gelistirme hedefi **PostgreSQL**; SQLite artik ana DB degildir (yerel ve VM'deki `instance/*.db` yedek/artik dosya olabilir).
- **Git (origin/main):** Son deploy/script commitleri (orneğin `7d96be6`); yerel `main` ile `origin/main` esit tutulmali; VM `git pull` ile ayni committe olmali.
- `/project` PostgreSQL uyumluluk fixleri: `routes_list.py`, `project_list_query.py`, `list.html`.
- **RAID / kurum ozeti:** `raid_item` vb. tablolar icin Alembic migration eklendi (`eab1c2d3f4a5`); VM'de bu migration'in **PostgreSQL'e** uygulanmasi, bolum 10 (`.env` URI) ile baglidir.

### 2026-03-24 aksami — VM deploy denemesi ozeti

- VM'de `pg_dump` alindi; **PostgreSQL tarafindaki veri** bu islemle silinmedi.
- Container icinde `run_db_upgrade.py` calisirken log **SQLiteImpl** gosterdi: VM'deki `/home/kokpitim.com/public_html/.env` dosyasinda **`SQLALCHEMY_DATABASE_URI` yok** (yalnizca `SQL_*` MSSQL tarzi degiskenler var). Bu yuzden Flask varsayilan olarak **volume altindaki SQLite** dosyasina baglandi; Alembic de orada takildi (`tenants.purpose` duplicate). Bu, **PG verisini degil**, monte `instance` sqlite dosyasini etkiler.
- Cozum yolu: VM `.env` veya `docker run -e` ile **acik `SQLALCHEMY_DATABASE_URI=postgresql://.../kokpitim_db`** tanimlanmali; sonra migration yalnizca PG'ye karsı calistirilmali.

## 2) Bu Sorunlar Neden Cikti?

Ana sebepler:

- SQLite -> PostgreSQL gecisinde SQL davranis farklari (`DISTINCT + ORDER BY` gibi)
- Legacy model adlari (`user`, `surec`) ile yeni model adlari (`users`, `processes`) karisik kullanimi
- Canlida hizli hotfix, yerelde kod guncellemesi ve DB tasima adimlarinin ayri zamanlarda yapilmasi

Bu sorunlar "normal" gecis sorunlari; kalici surec kurulursa tekrar etmez.

## 3) Veri Senkron Politikasi (Kayipsiz)

Hedef:
- VM: gercek test verisi
- Yerel: gelistirme ortami
- Ikisi de kayipsiz birlesebilsin

Onereilen model:

1. **Tek dogru kaynak (source of truth) sec**
   - UAT/test doneminde genelde VM PostgreSQL kaynak olur.
2. **Sadece migration ile sema degistir**
   - Elle tablo/kolon ekleme minimum.
3. **Periyodik VM -> Yerel cek**
   - VM PostgreSQL dump al
   - Yerelde restore et
   - Son migration'lari uygula
4. **Yukari tasima (Yerel -> VM) yalniz kontrollu**
   - Feature release aninda:
     - VM backup
     - kod deploy
     - migration
     - smoke test

## 4) Standart Operasyon Akisi (Her Deploy)

1. VM DB backup (`pg_dump`)
2. Kod deploy (git pull/build/restart)
3. Migration calistir
4. Smoke test:
   - `/health`
   - `/project`
   - `/masaustu`
   - `/takvim`
5. Log kontrolu ve sayi kontrolu (kurum/kullanici/surec/PG/PGV/faaliyet/proje/task)

## 5) Bilinen Veri Istisnasi

- 1 adet PGV kaydi PostgreSQL FK kurali nedeniyle alinmiyor:
  - `kpi_data.id=4684`
  - `process_kpi_id=399` (karsilik KPI kaydi yok)
- Bu istisna bilincli olarak kabul edildi.

## 6) "Ayni Sorunlari Tekrar Yasar miyiz?" Kisa Cevap

- Bu rehberdeki akis uygulanirsa: **buyuk olasilikla hayir**.
- En kritik kural: **DB sema degisikligi = migration + backup + smoke test**.

## 7) Son Yapilan Isler (2026-03-24)

- VM/yerel proje listesi PostgreSQL uyumlu hale getirildi.
- `user` ve `surec` kaynakli patlamalar icin kod fallback/yumusatma uygulandi.
- VM DB, yerel referansla senkronlandi (bilinen 1 kayit istisnasi haric).
- RAID ozeti icin yumusatma + PG yardimci tablolar migration'i (kod) eklendi.
- `scripts/vm_safe_deploy.sh` (yedek + pull + build + `--env-file`) ve `scripts/run_db_upgrade.py` eklendi; VM `.env`'de PostgreSQL URI eksikligi tespit edildi (bkz. bolum 10).

## 8) Tek Komut Kontrol Scripti

Script dosyasi:

- `scripts/vm_smoke_check.ps1`

Ne yapar:

1. VM'de PostgreSQL backup alir
2. VM'deki `instance/*.db` (varsa) dosya artefact'ini yedekler (canli DB değil; bu dosya sadece fallback/volume içeriği olabilir)
3. `/health` kontrolu yapar
4. Temel metrik sayimlarini verir:
   - Kurum, Kullanici, Surec, PG, PGV, Surec Faaliyeti, Proje, Proje Faaliyeti
5. Docker ve port dinleme durumunu gosterir

Kullanim:

```powershell
.\scripts\vm_smoke_check.ps1
```

Opsiyonel (log da goster):

```powershell
.\scripts\vm_smoke_check.ps1 -ShowDockerLogs
```

## 9) Dosyalar / Git

- Repo icinde **bilerek silinen/bozulan kaynak dosya yok**; degisiklikler commit'li migration + micro/script yollarinda.
- **Takip disi (normal):** `Yedekler/*.zip`, `backups/` gibi dizinler cogu zaman `git status`'ta `??` kalir; commitlenmezse sorun degildir.

## 10) Kritik: VM `.env`, PostgreSQL URI ve Docker

Flask-Kokpitim **`SQLALCHEMY_DATABASE_URI`** okur. VM'deki `.env` icinde bu yoksa:

- Uygulama DB bağlantısını bulamazsa (geçici olarak) **SQLite** (`config.py` fallback + `instance` volume) kullanmaya düşebilir.
- `run_db_upgrade.py` de aynı env fallback’ı üzerinden çalışabilir; bu durumda **PostgreSQL’de şema/güncelleme yapılmaz**.

**Kalici cozum:**

1. `/home/kokpitim.com/public_html/.env.postgres` (git'e eklenmez) — ornek: `scripts/env.postgres.example`
2. Icerik ornegi: `SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://KULLANICI:SIFRE@host.docker.internal:5432/kokpitim_db`
3. `vm_safe_deploy.sh`: `--env-file .env` + varsa `.env.postgres`; Docker icin `--add-host=host.docker.internal:host-gateway`
4. **PostgreSQL dinleme adresi:** Varsayilan yalnizca `127.0.0.1` ise Docker koprusunden baglanti **reddedilir**. `/etc/postgresql/14/main/postgresql.conf` icinde `listen_addresses = '*'` yapildiktan sonra **`systemctl restart postgresql`** gerekir (`reload` yetmeyebilir). `pg_hba.conf` icinde `172.17.0.0/16` icin kural zaten varsa yeterlidir.

**2026-03-24:** VM'de yedek alindi, `.env.postgres` olusturuldu, PostgreSQL `listen_addresses` acildi, container + migration basariyla **PostgreSQL** uzerinde calisti; `tenants`/`users` sayilari onceki ile uyumlu kaldi.

## 11) Bu sorunlari bir daha yasamamak — ders ozeti

### Tek kaynak hakikati

- **Sema:** Sadece Alembic migration; “sunucuda bir komutla tablo ac” yaklasimi sayac ve ortamlari ayirir.
- **Ortam:** Yerel ve VM’de **aynı degisken adi** ile PostgreSQL URI (`SQLALCHEMY_DATABASE_URI`). MSSQL tarzi `SQL_*` degiskenleri uygulamayi **baglamaz**; kafa karisikligi yaratir — ya kaldirin ya da dokümante ayirin.

### Deploy sablonu (sirasyla)

1. **Yedek:** `pg_dump` (ve isterseniz SQLite volume).
2. **Kod:** `git pull`, image build.
3. **Container:** Uygulamanin **gercekte** hangi DB’ye baktigini dogrulayin (`docker exec … python3 -c "from run import app; print(app.config['SQLALCHEMY_DATABASE_URI'][:40])"` benzeri veya log’da `PostgreSQLImpl`).
4. **Migration:** `run_db_upgrade.py` (Flask CLI kok `__init__.py` cakismasindan kacinmak icin).
5. **Dogrulama:** `alembic current`, `/health`, kritik sayfalar + **bir onceki deploy’daki satir sayilari** ile karsilastirma (`vm_smoke_check.ps1` mantigi).

### PostgreSQL + Docker

- Docker icinden host PG’ye gidecekseniz: **URI host’u** (`host.docker.internal` + `host-gateway`) **ve** sunucuda PG’nin TCP’de dinlemesi (`listen_addresses`, `restart`) uyumlu olmali; sadece `pg_hba` yetmez.
- **Migration’i SQLite’a karsi calistirdiginizi** anlamak icin Alembic log’ta `SQLiteImpl` / `PostgreSQLImpl` ayrımına bakin.

### Semantik / miras kod

- ORM’de `user` / `surec` ile `users` / `processes` karisimi; tablo yoksa **fallback** veya migration ile doldurmak — “sessizce 0” veya patlama arasinda secim bilincli olsun.
- Iliiski tablolari (`project_leaders` vb.) modelde var ama migration atlanmissa production’da **UndefinedTable** — yeni tablolar icin her zaman **idempotent** migration ( `has_table` ) veya net zincir.

### Guvenlik ve operasyon

- `.env.postgres` **git’te olmamali**; sunucuda izinler sinirli.
- `listen_addresses = '*'` ile PG tum arayuzlere acilir; **firewall / sadece gerekli kaynak** kuralını gözden geçirin.
- Sunucuda **commitlenmemis `git stash` / yerel patch** birikirse `git pull` kilitlenir; deploy oncesi ya repoya alın ya da stash’i etiketleyip geri donus planı yazın.

## 12) Tam Teslim Protokolü (Yereldeki Her Şeyi, Veri Kaybı Olmadan)

Amaç:
- Yereldeki tum kod degisikliklerini atlamadan VM'ye almak
- VM PostgreSQL verisini korumak
- Deploy sonrasi VM DB'yi yerele cekip esit duruma getirmek

### 12.1 Yerelde on-hazirlik (kod + DB yedek)

1. Kaynak zip yedek:
```powershell
Set-Location c:\kokpitim
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
Compress-Archive -Path app,micro,models,migrations,scripts,config.py,requirements.txt,Dockerfile,run.py,wsgi.py `
  -DestinationPath "Yedekler\Kokpitim_Kaynak_$ts.zip" -Force
```

2. Yerel PostgreSQL yedek (zorunlu):
```powershell
pg_dump -h localhost -U kokpitim_user -d kokpitim_db -F c -f "backups\local_pg_before_deploy_$ts.dump"
```

3. Yerel calisan DB'nin PostgreSQL oldugunu dogrula:
```powershell
python -c "from app import create_app; app=create_app(); print(app.config['SQLALCHEMY_DATABASE_URI'])"
```
`postgresql://` ile baslamali.

### 12.2 Yerelde tum kodu commit/push (atlama riskini sifirla)

Not:
- `Yedekler/` ve `backups/` commitlenmez.
- `.env*`, gizli anahtar dosyalari commitlenmez.

```powershell
Set-Location c:\kokpitim
git add -A
git reset -- Yedekler/ backups/ .env .env.* *.pem *.key
git status
git commit -m "Tam teslim: yerel degisikliklerin tamami"
git push origin main
```

### 12.3 VM deploy (DB kayipsiz standart akis)

```powershell
gcloud compute ssh sps-server-v2 --zone europe-west3-c --command "cd /home/kokpitim.com/public_html && sudo git fetch origin main && sudo git reset --hard origin/main && sudo bash scripts/vm_safe_deploy.sh"
```

Bu script sunlari yapar:
1. VM PostgreSQL tam yedek (`pg_dump`)
2. Satir sayisi snapshot (once)
3. Kod guncelleme + container rebuild
4. Alembic upgrade (`PostgresqlImpl` beklenir)
5. Satir sayisi snapshot (sonra) + diff (degismemeli)
6. `/health` kontrolu

### 12.4 VM DB'yi yerele cekme (deploy sonrasi senkron)

1. VM'de yeni dump al:
```powershell
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
gcloud compute ssh sps-server-v2 --zone europe-west3-c --command "sudo -u postgres pg_dump -F c -d kokpitim_db -f /home/kokpitim.com/public_html/backups/vm_after_deploy_$ts.dump"
```

2. Dump'i yerel makineye kopyala:
```powershell
gcloud compute scp sps-server-v2:/home/kokpitim.com/public_html/backups/vm_after_deploy_$ts.dump "c:\kokpitim\backups\" --zone europe-west3-c
```

3. Yerel DB'yi yedekten geri donulebilir sekilde temizleyip restore et:
```powershell
dropdb   -h localhost -U kokpitim_user kokpitim_db
createdb -h localhost -U kokpitim_user kokpitim_db
pg_restore -h localhost -U kokpitim_user -d kokpitim_db --no-owner --no-privileges "backups\vm_after_deploy_$ts.dump"
```

4. Kontrol:
```powershell
python -c "from app import create_app; app=create_app(); print(app.config['SQLALCHEMY_DATABASE_URI'])"
```
ve uygulamada kritik sayfalar: `/`, `/masaustu`, `/project`, `/project/new`, `/takvim`, `/ayarlar/eposta`.

### 12.5 Kirmizi cizgiler

- `pg_restore --clean` veya tablo truncate islemleri canli VM DB'de uygulanmaz.
- VM'de dogrudan SQLite'a gecis yapilmaz; `SQLALCHEMY_DATABASE_URI` daima PostgreSQL olmalidir.
- Deploy adimlarinda hata varsa rollback icin en son VM dump dosyasi saklanir.

