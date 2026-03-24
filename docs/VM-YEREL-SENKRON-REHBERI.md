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
2. VM'deki SQLite dosyasini (varsa) backup alir
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

## 10) Kritik: VM `.env` ve PostgreSQL URI

Flask-Kokpitim **`SQLALCHEMY_DATABASE_URI`** okur. VM'deki `.env` icinde bu yoksa:

- Uygulama **SQLite** (`config.py` varsayilan + `instance` volume) kullanir.
- `flask db upgrade` / `run_db_upgrade.py` de ayni sebeple SQLite'a gider; **PostgreSQL semasi guncellenmez**.

**Yapilacak (tek seferlik / kalici):** Sunucu `.env` dosyasina ornek:

`SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://KULLANICI:SIFRE@172.17.0.1:5432/kokpitim_db`

(Host adresi kurulumunuza gore `127.0.0.1` veya Docker bridge IP degisebilir.) Ardindan container `--env-file` ile kaldirilmali ve `python3 scripts/run_db_upgrade.py` tekrar denenmeli.

