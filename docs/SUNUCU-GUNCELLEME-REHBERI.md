# SUNUCU GÜNCELLEME REHBERİ — Yerel → Test / Demo / Yayın

> **Tek canonical yordam.** Eski `docs/YERELDEN_VM_YAYIN.md` bunun yerine geçti (arşiv).
> Terminoloji bağlayıcı (KURALLAR-MASTER §8): **Yerel / Test / Demo / Yayın**. "VM" tek başına KULLANMA.
> Son güncelleme: 2026-06-08 (Alembic baseline + 4-ortam deploy mekaniği doğrulandı).

---

## 0. Altın kurallar

1. **Akış:** `Yerel → Test → Yayın` (Demo paralel hat: `Yerel → Demo`). Yereli doğrudan Yayın'a **atma**.
2. **Yayın = kırmızı çizgi.** Her Yayın güncellemesinden ÖNCE: **(a) kontrol dosyası** (veri sayımları) + **(b) yedek** (DB + kod). Kullanıcı verisi kaybolmaz.
3. Deploy **kullanıcı isteyince** yapılır ("yayına çıkalım" / "test'e gönderelim" / "demo'ya gönderelim"). Otomatik değil.
4. **SSH yalnız operatör.** Anahtar: `C:\crt\ssh-key-2026-04-18_v4.key` → `ubuntu@129.159.30.175`.

---

## 1. Ortam envanteri (2026-06-08 doğrulandı)

Üç sunucu ortamı aynı fiziksel makinede (`129.159.30.175`); izolasyon dizin/port/DB seviyesinde.

| | **Yayın (Canlı)** | **Test** | **Demo** | **Yerel** |
|--|---|---|---|---|
| URL | www.kokpitim.com | test.kokpitim.com | demo.kokpitim.com | 127.0.0.1:5001 |
| Dizin | `/opt/kokpitim/app` | `/opt/kokpitim-test/app` | `/opt/kokpitim-demo/app` | `C:\kokpitim` |
| Container | `kokpitim-web` | `kokpitim-test-web` | `kokpitim-demo-web` | — (gunicorn yok, dev server) |
| Port | 5000 | 5050 | 5080 | 5001 |
| DB | `kokpitim_db` / `kokpitim_user` | `kokpitim_test_db` / `kokpitim_test_user` | `kokpitim_demo_db` / `kokpitim_demo_user` | `kokpitim_db` / `kokpitim_user` |
| `.env` | `/opt/kokpitim/.env` | `…/app/.env` | `…/app/.env` (+ `KOKPITIM_DEMO_MODE=1`) | `C:\kokpitim\.env` |
| **Kod dağıtımı** | **IMAGE-BAKED** → `docker build` + container yeniden oluştur | **BIND-MOUNT** → kodu güncelle + `docker restart` | **BIND-MOUNT** → kodu güncelle + `docker restart` | dosya = çalışan kod |
| git checkout | **`.git` VAR** (origin/main) | `.git` YOK → **tarball/rsync** | `.git` YOK → **tarball/rsync** | `.git` VAR |
| Yedek dizini | `/opt/kokpitim/backups` | `/opt/kokpitim-test/backups` | `/opt/kokpitim-demo/backups` | `instance/yedekler` |

**Kritik fark:** Yayın kodu image'a **gömülü** (güncelleme = rebuild). Test/Demo kodu **bind-mount** (güncelleme = dosya değiştir + restart, rebuild yok — yeni Python bağımlılığı eklenmediyse).

---

## 2. Veritabanı & Şema gerçeği (önemli)

- **Tüm ortamlar PostgreSQL.** Yerel de PG (`kokpitim_db`, PG **18**). `instance/kokpitim.db` ölü (0 byte) — SQLite kullanılmıyor.
- **Sürücü:** kod psycopg2/psycopg3'ü `config.py` ile otomatik seçer (`find_spec`). `.env` `+psycopg2` yazsa bile kurulu olana normalize eder → her image çalışır.
- **`pg_dump` sürüm kuralı:** pg_dump ≥ sunucu sürümü olmalı. Yerelde **`C:\pgdata\bin`** (PG 18) kullan; `C:\Program Files\PostgreSQL\16\bin` (16) **kullanma** → "server version mismatch".
- **Otomatik `create_all` YOK.** Şema artık **Alembic baseline** ile yönetiliyor (bkz. §6). Yeni tablo/kolon = baseline üstüne yeni migration.

---

## 3. KIRMIZI ÇİZGİ — Yayın deploy öncesi ritüel (zorunlu)

```bash
KEY=/c/crt/ssh-key-2026-04-18_v4.key
# (a) KONTROL DOSYASI — veri sayımları
ssh -i $KEY ubuntu@129.159.30.175 '
for t in tenants users processes process_kpis kpi_data process_activities strategies sub_strategies project task; do
  echo "$t|$(sudo -u postgres psql -d kokpitim_db -At -c "SELECT count(*) FROM $t;")"
done'
# → docs/kontrol/yayinverileri_YYYY-MM-DD_HHMM.md olarak kaydet (deploy sonrası bununla doğrula)

# (b) YEDEK — DB (custom + sql.gz) + kod
ssh -i $KEY ubuntu@129.159.30.175 '
TS=$(date +%Y%m%d_%H%M%S); BK=/opt/kokpitim/backups
sudo -u postgres pg_dump -Fc kokpitim_db | sudo tee $BK/pre_deploy_pg_${TS}.dump >/dev/null
sudo -u postgres pg_dump     kokpitim_db | gzip -c | sudo tee $BK/pre_deploy_pg_${TS}.sql.gz >/dev/null
sudo tar czf $BK/pre_deploy_code_${TS}.tar.gz -C /opt/kokpitim/app --exclude=.git --exclude=__pycache__ --exclude=.venv .'
```

---

## 4. Yerel → Yayın (IMAGE-BAKED: build + recreate)

> Ön koşul: §3 ritüeli yapıldı. Branch main'e merge + push edilmeli (Yayın `origin/main` çeker).

```bash
# 0) Yerelde: branch→main merge + push  (DİKKAT: GIT_TERMINAL_PROMPT=0 KULLANMA → GCM'i bloklar)
git checkout main && git merge --no-ff <dal> && git push origin main

KEY=/c/crt/ssh-key-2026-04-18_v4.key
ssh -i $KEY ubuntu@129.159.30.175 '
set -e; APP=/opt/kokpitim/app; TS=$(date +%Y%m%d_%H%M%S)
# 1) rollback image etiketle (kesintisiz hazırlık)
sudo docker tag kokpitim_web:latest kokpitim_web:rollback_${TS}
# 2) kodu güncelle (git — Yayın bir git checkout)
sudo git -c safe.directory=$APP -C $APP fetch origin
sudo git -c safe.directory=$APP -C $APP reset --hard origin/main
# 3) BUILD (eski container çalışmaya devam — kesinti YOK; build patlarsa dururuz)
cd $APP && sudo docker build -t kokpitim_web:latest .
# 4) container yeniden oluştur (~1 dk kesinti)
sudo docker stop kokpitim-web; sudo docker rm kokpitim-web
sudo docker run -d --name kokpitim-web --restart unless-stopped --network host \
  -v /opt/kokpitim/instance:/app/instance --env-file /opt/kokpitim/.env \
  -e FLASK_ENV=production -e TRUST_PROXY=1 kokpitim_web:latest
# 5) Alembic upgrade (artık temiz no-op — bkz. §6)
sleep 6; sudo docker exec kokpitim-web bash -lc "cd /app && python3 scripts/run_db_upgrade.py"
'
# 6) Doğrula: /health 200 + satır sayıları kontrol dosyasıyla AYNI
curl -s -o /dev/null -w "%{http_code}\n" https://www.kokpitim.com/health
```

**`scripts/ops/oracle/oracle_safe_deploy.sh`** bu adımları (yedek + git pull + build + Alembic + satır-sayısı doğrulaması) tek scriptte yapar — Alembic baseline'dan sonra **çalışır**.

**Rollback:** `sudo docker stop/rm kokpitim-web && sudo docker run … kokpitim_web:rollback_<TS>` ; DB gerekirse `pg_restore -d kokpitim_db pre_deploy_pg_<TS>.dump`.

---

## 5. Yerel → Test / Demo (BIND-MOUNT: tarball + restart)

> Test/Demo kodu mount'lu → **rebuild gerekmez** (yeni pip bağımlılığı yoksa). `.env` ve `instance` tarball'dan **hariç** (korunur).

```bash
KEY=/c/crt/ssh-key-2026-04-18_v4.key
# 1) Yerelde tarball (.env/instance/.git/.venv hariç)
tar czf /tmp/kokpitim_kod.tar.gz --exclude=.git --exclude=.venv --exclude=node_modules \
  --exclude=__pycache__ --exclude='*.pyc' --exclude=.env --exclude=instance --exclude=docs/kontrol -C /c/kokpitim .
scp -i $KEY /tmp/kokpitim_kod.tar.gz ubuntu@129.159.30.175:/tmp/

# 2) Test için (Demo için: kokpitim-test → kokpitim-demo, -test → -demo)
ssh -i $KEY ubuntu@129.159.30.175 '
set -e; APP=/opt/kokpitim-test/app; TS=$(date +%Y%m%d_%H%M%S)
sudo cp $APP/.env /tmp/test_env_$TS 2>/dev/null || true                      # .env güvence
sudo tar czf /tmp/test_app_before_$TS.tar.gz -C $APP --exclude=__pycache__ .  # rollback
sudo tar xzf /tmp/kokpitim_kod.tar.gz -C $APP                                 # yeni kod (.env korunur)
sudo docker restart kokpitim-test-web
sleep 6; curl -s -o /dev/null -w "test /health -> %{http_code}\n" http://127.0.0.1:5050/health'
```

**Demo kırmızı çizgileri (KURALLAR §8.4):** Demo işlemleri YALNIZ `*-demo` hedeflerine dokunur. Saf kod deploy'u DB'ye dokunmaz; Tomofil baseline / demo DB'yi etkileyecek iş (seed/wipe/migration) **yalnız kullanıcı açıkça isteyince**.

---

## 6. ŞEMA / ALEMBIC — nasıl çalışıyor, bundan sonra nasıl davranılır

### Geçmişteki problem (2026-06-08'de çözüldü)
Şema yönetimi disiplinsiz hibrit hâldeydi: migration grafiğinde **5 birleşmemiş head**, yerel DB ara-revizyonlarda, **Yayın'da `alembic_version` tablosu hiç yoktu**, kodda otomatik `create_all` yoktu. Sonuç: `oracle_safe_deploy.sh`'in `flask db upgrade` adımı **patlıyordu** — (a) sürüm tablosu yok → baştan başlar → "already exists"; (b) 5 head → "multiple heads".

### Çözüm: squash baseline
65 eski migration `migrations/_archive_versions/`'e taşındı; modellerden **tek baseline** üretildi: **`f5215370eebd`** (`down_revision=None`, 161 tablo = Yayın'ın tablo sayısı). Yerel + Test + Yayın DB'leri buna **stamp**'lendi (sıfır-DDL; sadece `alembic_version` tek satırı). Doğrulandı: Test container'ında `flask db upgrade` temiz **no-op**; Yayın'da veri sabit.

### ⚠️ Bundan sonra ZORUNLU davranış
1. **Tek head disiplini.** Aynı anda iki dalda migration üretirsen 2 head olur → deploy patlar. Birleştir: `flask db merge -m "merge heads" <rev1> <rev2>` → tek head.
2. **Şema değişikliği = yeni migration.** Model değiştir → `flask db migrate -m "aciklama"` (baseline üstüne) → gözden geçir → commit. Elle `CREATE/ALTER` yapma; `db.create_all` yok.
3. **Yeni ortam/DB'yi baseline'a al.** Boş DB: `flask db upgrade` (baseline tüm şemayı kurar). Mevcut ama izlenmeyen DB: aşağıdaki stamp.
4. **alembic_version SAHİPLİĞİ (kritik tuzak).** Stamp'i `sudo -u postgres` ile yaparsan tablo `postgres`'in olur → app **"permission denied for table alembic_version"**. Sahibi app kullanıcısı olmalı:
   ```sql
   CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL,
       CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num));
   ALTER TABLE alembic_version OWNER TO kokpitim_user;   -- Test: kokpitim_test_user, Demo: kokpitim_demo_user
   DELETE FROM alembic_version;
   INSERT INTO alembic_version (version_num) VALUES ('f5215370eebd');
   ```
5. **Veri dönüştüren migration** (tip değişimi vb.) → ÖNCE yedek kopyada (scratch DB'ye prod dump'ı yükleyip) dene. Deploy'un satır-sayısı kontrolü tip-bozulmasını yakalamaz.

---

## 7. Tuzaklar (bu oturumda yaşandı, tekrar etmesin)

| Tuzak | Çözüm |
|---|---|
| `git push` takılıyor | **`GIT_TERMINAL_PROMPT=0` / `GCM_INTERACTIVE=never` KULLANMA** — GCM'i bloklar. Sade `git push origin main`. |
| `pg_dump: server version mismatch` | pg_dump ≥ sunucu sürümü. Yerelde `C:\pgdata\bin` (PG18). |
| `permission denied for table alembic_version` | `ALTER TABLE alembic_version OWNER TO <app_user>` (§6.4). |
| Yerel 5001 stale/çift dinleyici | `Get-CimInstance Win32_Process … create_app … Stop-Process`; port 0 olana kadar bekle, tek başlat. |
| Yayın `git pull` kodu geri alır | Önce branch→main **push** et; sonra Yayın `git reset --hard origin/main`. Aksi halde tarball deploy bir sonraki pull'da geri alınır. |
| `error.log` git checkout'u kilitliyor | Yerel sunucuyu durdur (dosya kilidi), sonra checkout/merge. |

---

## 8. Deploy sonrası doğrulama (her ortam)

1. `/health` → 200 (Yayın: https://www.kokpitim.com/health, Test: :5050, Demo: :5080).
2. **Satır sayıları** deploy ÖNCESİ kontrol dosyasıyla **birebir aynı** (Yayın kırmızı çizgi). Farklıysa → veri kaybı → yedekten dön.
3. Smoke: ana sayfalar + son değişen özellik.

---

## İlgili dosyalar
- `scripts/ops/oracle/oracle_safe_deploy.sh` — Yayın tek-script deploy (yedek+pull+build+alembic+doğrulama).
- `scripts/ops/oracle/setup_test_env.sh` / `setup_demo_env.sh` — ilk kurulum (DB reseed dahil — dikkat).
- `docs/kontrol/` — deploy öncesi/sonrası veri sayım kayıtları.
- `docs/KURALLAR-MASTER.md §8` — ortam terminolojisi + protokol.
- `docs/YERELDEN_VM_YAYIN.md` — **arşiv** (bu dosya yerine geçti).
