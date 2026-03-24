# Yetki Smoke Test Checklist

Bu dokuman, su moduller icin yetki davranisini hizli dogrulamak amaciyla hazirlanmistir:

- Surecler
- PG'ler
- PGV'ler
- Surec Faaliyetleri
- Projeler / Task'lar

## 1) Test Oncesi Hazirlik

Ayni tenant icinde asagidaki kullanicilar hazir olmalidir:

- `tenant_admin`
- `executive_manager`
- `standard_user` (atanmamis)
- `process_leader`
- `process_member`
- `project_leader` (manager)
- `project_member`

Gerekli veri seti:

- 2 surec:
  - `Surec-A`: leader=`process_leader`, member=`process_member`
  - `Surec-B`: test kullanicilari atanmis degil
- 1 proje:
  - leader/manager=`project_leader`
  - member=`project_member`
- `Surec-A` icinde:
  - En az 1 PG
  - En az 2 PGV satiri:
    - biri `process_member` tarafindan girilmis
    - biri `process_leader` tarafindan girilmis
  - En az 2 faaliyet:
    - biri `process_member`a atanmis
    - biri baska bir kullaniciya atanmis
- Projede en az 2 task:
  - biri `project_member`a atanmis
  - biri baska bir kullaniciya atanmis

## 2) Rol Bazli Beklenen Sonuclar

## A) tenant_admin / executive_manager

- [ ] Surec olusturabilir.
- [ ] Proje olusturabilir.
- [ ] Surec, PG, PGV ve faaliyet uzerinde CRUD yapabilir.
- [ ] Proje bilgilerini duzenleyebilir.
- [ ] Task olusturabilir ve duzenleyebilir.
- [ ] Task silebilir (`/project/<id>/task/<id>/delete`).

## B) process_leader

- [ ] Atandigi surecte surec bilgisi guncelleyebilir.
- [ ] Atanmadigi surecte surec bilgisi guncelleyemez (403).
- [ ] Atandigi surecte PG CRUD yapabilir.
- [ ] Atandigi surecte kendi ve baskasinin PGV kaydini duzenleyebilir/silebilir.
- [ ] Faaliyet ekleyebilir.
- [ ] Faaliyette RUD/complete/track yapabilir.

## C) process_member

- [ ] Atandigi sureci goruntuleyebilir.
- [ ] Surec bilgisi/PG CRUD yapamaz (403).
- [ ] PGV: sadece kendi girdigi kayitlarda update/delete yapabilir.
- [ ] PGV: baskasinin kaydinda update/delete yapamaz (403).
- [ ] Faaliyet ekleyebilir.
- [ ] Sadece kendisine atanmis faaliyette RUD/complete/track yapabilir.
- [ ] Kendisine atanmamis faaliyette RUD/complete/track yapamaz (403).

## D) project_leader (manager)

- [ ] Proje bilgilerini duzenleyebilir.
- [ ] Task olusturabilir.
- [ ] Tum tasklari duzenleyebilir.
- [ ] Task silemez (yalniz ust yonetim silebilir).

## E) project_member

- [ ] Projeyi goruntuleyebilir.
- [ ] Proje bilgilerini duzenleyemez.
- [ ] Task olusturamaz.
- [ ] Sadece kendisine atanmis taski duzenleyebilir.
- [ ] Baskasina atanmis taski duzenleyemez (403).
- [ ] Task silemez.

## F) Atanmamis standard_user

- [ ] Atanmadigi surecleri goremez.
- [ ] Surec/PG/PGV/faaliyet API cagrilarinda 403 alir.
- [ ] Atanmadigi projeleri goremez.
- [ ] Proje/task islemlerinde yetkisiz olur.

## 3) API Seviyesi Hizli Kontrol

UI testine ek olarak Network veya API araci ile asagidaki endpoint'ler kontrol edilmelidir.

Surec:

- `/process/api/add`
- `/process/api/update/<id>`
- `/process/api/kpi/*`
- `/process/api/kpi-data/*`
- `/process/api/activity/add`
- `/process/api/activity/update|delete|complete|track`

Proje:

- `/project/new`
- `/project/<id>/task/new`
- `/project/<id>/task/<id>/edit`
- `/project/<id>/task/<id>/delete`

Beklenen davranis:

- Yetkili senaryolarda `2xx` + basarili mesaj
- Yetkisiz senaryolarda `403` + anlasilir hata mesaji

## 4) Test Sonucu Kayit Formati

Her satir icin asagidaki format kullanilsin:

- Kullanici:
- Islem:
- Beklenen:
- Gerceklesen:
- Sonuc: `PASS` / `FAIL`
- Not:

