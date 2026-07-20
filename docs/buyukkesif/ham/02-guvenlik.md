# HAM BULGU — Güvenlik ve Veri Bütünlüğü

> Kaynak: paralel güvenlik/sistem uzmanı taraması · 858 route, 170 tablo, 259 FK
> Tarih: 2026-07-21 · **Kritik bulgular ana oturumda yeniden doğrulandı**

---

## S1 — Canlı Yayın DB parolası public GitHub deposunda ✅ DOĞRULANDI · **EN ACİL**

**Ciddiyet: KRİTİK**

Yayın PostgreSQL parolası **4 dosyada düz metin**, `origin/main`'e push edilmiş:

| Dosya | Satır |
|---|---|
| `scripts/ops/compare_db_counts.py` | 57 |
| `scripts/ops/oracle/oracle_deploy.ps1` | 60, 68 |
| `scripts/ops/oracle/oracle_fix_db.sh` | 3 |
| `scripts/restore_vm_original_data.py` | 13 |

### Ana oturumda yapılan doğrulama

| Kontrol | Sonuç |
|---|---|
| Parola dosyalarda mı? | ✅ 5 satırda, düz metin |
| `origin/main`'de mi? | ✅ `git cat-file -e` ile teyit |
| Depo public mi? | ✅ **`"private": false, "visibility": "public"`** |
| Ne zamandır açıkta? | ✅ **2026-04-03** — commit `91a23e00`, ~3,5 ay |

### Aciliyeti düşüren tek şey — ama güvenmeyin

| Kontrol | Sonuç |
|---|---|
| 5432 dışarıdan erişilebilir mi? | ❌ **kapalı/filtreli** |
| PostgreSQL `listen_addresses` | **`localhost`** |

Yani parola herkesin elinde ama **şu an doğrudan bağlanılamıyor**. Bu, açığı
"sömürülüyor"dan **"gecikmeli bomba"ya** indiriyor:

- Firewall kuralı bir gün gevşerse → anında tam DB erişimi
- Aynı parola başka bir yerde kullanılıyorsa (SSH, panel, başka servis) → şimdi bile risk
- GitHub'da parola arayan otomatik tarayıcılar bu depoyu çoktan taramış olabilir

### Öneri (sırayla)

1. **Parolayı HEMEN döndür** — geçmişi temizlemek tek başına yetmez, parola zaten kopyalanmış olabilir
2. 4 dosyayı env değişkeni okumaya çevir
3. Aynı parolanın başka yerde kullanılıp kullanılmadığını kontrol et
4. Deponun public kalması gerekip gerekmediğine karar ver

---

## S2 — Merkezî tenant koruması KAPALI · KRİTİK (yapısal)

`config.py:143` → `TENANT_GUARD_MODE = os.environ.get("TENANT_GUARD_MODE", "off")`

Hiçbir `.env`'de `enforce` yok (yalnızca `tests/test_tenant_guard.py` set ediyor).
`_guard_enabled()` `"off"` dönünce ORM dinleyicisi **hiçbir kriter eklemiyor** —
`TenantScopedMixin` taşıyan modeller fiilen korumasız.

> Ayrıca `verify_tenant_resource` ve `scope_query` yazılmış ama **0 route'ta kullanılıyor**
> — ölü kod, "koruma var" yanılsaması yaratıyor.

**Sonuç:** 858 route'un her biri `tenant_id` filtresini **elle** hatırlamak zorunda.
Tek unutulan yer = kurumlar arası veri sızıntısı, arkada ağ yok. S3 bunun canlı örneği.

---

## S3 — Kurumlar arası finansal veri sızıntısı (EVM ucu) · KRİTİK

`micro/modules/sp/routes_frameworks.py:263-269` + `app/services/project_evm_service.py:45`

`<int:pid>` alan route **hiçbir sahiplik doğrulaması yapmıyor**. Tek koruma `_check_sp_role`
— yani **rol** kontrolü, sahiplik değil. `pid` doğrudan servise gidiyor:
`PlanProject.query.get(project_id)` — tenant filtresi yok. S2 nedeniyle mixin de devrede değil.

**Sömürü:** Herhangi bir kurumda SP rolü olan kullanıcı `pid`'yi 1'den deneyerek başka
kurumların **proje bütçesini** okur: `bac` (toplam bütçe), `ac` (fiili maliyet), `eac`,
görev bazında ad/tarih/bütçe.

> Aynı dosyadaki VRIO/Blue Ocean kardeş uçları **doğru kalıbı kullanıyor** — bu tek uç sapmış.
> İkinci bir filtresiz kopya: `services/evm_service.py:13`

---

## S4 — Kimlik doğrulamasız veri konnektörü API'si · YÜKSEK

`app/api/data_connector.py:30-75`

`/kpi-data`, `/processes`, `/kpis`, `/metadata` uçlarında **`@login_required` yok**.
Tek koruma türetilmiş token: `sha256(f"{user_id}:{secret}:dataconn")` — kullanıcı başına
**sabit**, DB'de saklanmıyor, **iptal edilemez, süresi dolmaz**.

Token query string'den de kabul ediliyor (`?token=` / `?apikey=`) → proxy loglarına,
tarayıcı geçmişine, `Referer` başlığına düşer.

> Kodun kendi yorumu itiraf ediyor:
> `# Production'da: ayrı api_tokens tablosu + expiration + scope`

**Sömürü:** `SECRET_KEY` sızarsa saldırgan **her tenant'taki her kullanıcı** için geçerli
token üretir. Ayrıca `_user_from_token` her istekte 2000 kullanıcıyı tarıyor → DoS çarpanı.

---

## S5 — Sequence drift: 5 tabloda sonraki INSERT kesin çakışacak · YÜKSEK

| Tablo | last_value | max_id | id=1 dolu mu? |
|---|---|---|---|
| `route_registry` | 1 | 81 | **evet** |
| `system_components` | 1 | 35 | **evet** |
| `roles` | 1 | 5 | **evet** |
| `user_tour_progress` | 1 | 4 | **evet** |
| `process_activity_reminders` | 1 | 17 | hayır |

`is_called=f` → sonraki `nextval` **1 döndürür**, 4 tabloda id=1 zaten dolu.

**Sömürü değil, operasyonel kaza:** Bir sonraki rol/bileşen ekleme denemesi
`duplicate key value violates unique constraint` ile patlar.

Muhtemel kaynak: Yayın→Yerel veri çekiminde `setval` adımının atlanması
(CLAUDE.md'de "sequence drift" zaten bilinen tuzak olarak kayıtlı).

---

## S6 — 121 noktada istisna metni istemciye dönüyor · YÜKSEK

`main/routes/pages.py` (23) · `main/routes/projects.py` (11) · `main/routes/strategy_api.py` (6)
· `micro/modules/admin/routes_admin_tools.py:231,259`

Kalıp: `return jsonify({'success': False, 'message': str(e)}), 500`

SQLAlchemy hatalarında `str(e)` **çalışan SQL cümlesini, tablo/kolon adlarını, constraint
adlarını ve parametre değerlerini** içerir. `routes_admin_tools.py:259`'da `pg_restore`
hatası döndüğü için mesaj **bağlantı dizesini/host/user** taşıyabilir.

> **Kritik ayrıntı:** `app/utils/error_handlers.py:89-104` **doğru yazılmış** — traceback
> yalnız log'a gidiyor. Sorun bu güvenlik ağının **atlanması**: yerel `except` blokları
> kontrolü merkezî handler'a hiç bırakmıyor.

---

## S7 — Doğrulamasız dosya yüklemeleri (webroot'a yazan) · YÜKSEK

`app/routes/core.py:41-52` · `main/routes/projects.py:587-609` · `routes_admin_tools.py:247-256`

Yalnızca uzantı-son-eki kontrolü, sihirli bayt doğrulaması yok, dosya `static/` altına yazılıyor.
DB geri yüklemede tek kapı `f.filename.endswith(".dump")` — **saldırganın seçtiği metin
üzerinde string kontrolü** — sonra baytlar doğrudan `pg_restore`'a gidiyor.

> `app/utils/upload_security.py` **iyi yazılmış** (magic byte, SVG script taraması,
> path traversal koruması) ve iki yerde doğru kullanılıyor. Sorun: bu iyi kütüphane
> yukarıdaki uçlarda **çağrılmıyor**. Ayrıca `upload_security`'de boyut sınırı parametresi yok.

---

## S8 — `SESSION_COOKIE_SAMESITE` env ile gevşetilebilir; 132 CSRF muafiyeti buna bağlı · ORTA-YÜKSEK

`config.py:97` → `os.environ.get("SESSION_COOKIE_SAMESITE", "Strict")`

Kapsamda **132 `@csrf.exempt`** var; tek koruma bu ayar. Muafiyet yorumları **yanlış
gerekçe** yazıyor (`shared/auth/routes.py:74`: *"SameSite=Lax cookie yeterli"* — gerçekte config `Strict`).

Muaf ve veri değiştiren uçlar: DB geri yükleme, rol atama, kullanıcı oluşturma.

**Risk:** Biri env'de `SAMESITE=Lax/None` yaparsa **132 uç aynı anda** sessizce CSRF'e açılır.

---

## S9 — `.env` içinde çakışan DB tanımı · ORTA

```
SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://.../kokpitim_db   ← uygulama bunu okuyor
DATABASE_URL=sqlite:///instance/kokpitim.db                     ← ÖLÜ, yanıltıcı
```

Uygulama doğru DB'yi kullanıyor (`config.py:12` yalnız `SQLALCHEMY_DATABASE_URI` okuyor),
ama `scripts/ops/yayin_yerele_cek.py:60-63` yorumu bu tuzağın **daha önce gerçekten
ısırdığını** belgeliyor: *"shell'de takılı kalan eski DATABASE_URL=sqlite yüzünden script
yanlış DB'yi görüyordu"*.

> Aynı çakışma **Test ortamının `.env`'inde de var** (bu oturumda deploy sırasında görüldü).

---

## S10 — Yetki kontrolünde sessizce yutulan istisnalar · ORTA

KURALLAR §3 `except: pass`'i yasaklıyor; kapsamda **124 ihlal** (6 çıplak `except:`).

En tehlikeli üçü:

| Dosya:satır | Neden tehlikeli |
|---|---|
| `app/utils/tenant_scope.py:250` | Rol çözümlemesi yutuluyor → hata olursa **sessizce düşük yetkiye** düşüyor, iz yok |
| `app/routes/auth.py:35` | DB denetim kaydı başarısız olunca **yedek dosya log'u da** yutuluyor → kimlik doğrulama olayı **tamamen kayboluyor** |
| `utils/file_validation.py:23` | Çıplak `except: pass` — `python-magic` yoksa tüm yüklemeler sessizce **uzantı tahminine** düşüyor (S7'yi büyütür) |

---

# DOĞRULANAN OLUMLU BULGULAR

Bunlar rapora dahil edildi çünkü aksi varsayılırdı — sistem sanılandan iyi:

| Konu | Sonuç |
|---|---|
| **SQL injection** | ❌ **YOK.** ~1318 ham SQL noktası tarandı; kullanıcı girdisi taşıyan her değer `:param` ile bağlanmış. Dinamik `ORDER BY` enterpolasyonu **sıfır** (yaygın kör nokta — burada yok) |
| **Yetim kayıt** | ❌ **YOK.** 259 FK kısıtının tamamı sorgulandı, ebeveynsiz satır yok |
| **`debug=True` Yayın'a sızıyor mu** | ❌ Hayır. Dockerfile `gunicorn run:app` ile çalışıyor → blok hiç yürümüyor |
| **`yayin_yerele_cek.py` güvenli mi** | ✅ Evet. `DROP SCHEMA` yalnız yerel URL'de koşuyor, Yayın'da tek işlem salt-okunur `pg_dump` |
| **`.env` git'te mi** | ❌ Hayır (`.gitignore:2-3`). SSH anahtarı da repoda değil |
| **Admin uçları korumasız mı** | ❌ Hayır. Yıkıcı uçlar gövde-içi kontrol taşıyor; DB geri yükleme ayrıca parola tekrarı + yazılı onay istiyor |

**Tek dekoratör tutarsızlığı:** `app/api/process/performance_routes.py:80,182,195` —
kardeşlerindeki `@require_process_access` yok.

**Küçük veri notları:** `users`'ta `tenant_id` NULL 1 kayıt (id=12); pasif tenant 30'a bağlı
1 aktif kullanıcı; `notifications` 7488 ve `audit_logs` 36 satırda NULL `tenant_id`
(bu tablolar tasarım gereği tenant'sız olabilir — doğrulanmalı).

---

## En acil üç iş

1. **S1** — Parola rotasyonu (public'te 3,5 aydır)
2. **S3** — EVM sahiplik kontrolü (tek satır)
3. **S5** — Sequence `setval` (bir sonraki kayıt eklemede patlayacak)
