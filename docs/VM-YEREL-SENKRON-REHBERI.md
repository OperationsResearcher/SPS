# VM - Yerel Senkron Rehberi

Son guncelleme: 2026-03-24

## 1) Mevcut Durum Ozeti

- Kod tabani su an hem yerelde hem VM'de ayni committe: `b3506d8`
- `/project` icin PostgreSQL uyumluluk fixleri her iki ortama da uygulandi:
  - `micro/modules/proje/routes_list.py`
  - `micro/modules/proje/project_list_query.py`
  - `micro/templates/micro/project/list.html`
- VM uygulama saglik durumu: `healthy` (database `ok`)

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
- VM container rebuild/restart yapildi ve health dogrulandi.

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

