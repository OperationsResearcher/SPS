# Yerelden VM’e yayın (Kokpitim / kokpitim.com)

Bu dosya, **yerelde yapılan kod değişikliklerinin** üretim **VM**’ine güvenli şekilde alınması için **tek referans yordamdır**.

> **VM = Oracle Cloud** (`kokpitim-v2`, `129.159.30.175`). Eski GCP (`sps-server-v2`) kullanılmaz.  
> Özet tablo: `docs/ORACLE-PROD-VM.md`

**Ters yön (VM → yerel):** `docs/VM_DEN_YERELE.md`  
Altyapı özeti: `docs/PROJE-MASTER.md` → bölüm 12.

---

## Özet akış

1. Yerelde değişiklikleri **commit** edip **GitHub `main`** dalına **push** et.
2. **Oracle VM**’de **`scripts/ops/oracle/oracle_safe_deploy.sh`** çalıştır (PG yedek, `git pull`, Docker build, Alembic, satır sayısı, health).
3. Gerekirse **sekans / bakım** adımlarını uygula (aşağıda).

Canlı veritabanı **PostgreSQL** (`kokpitim_db`). Uygulama **Docker** (`kokpitim-web`, `--network host`), kod: `/opt/kokpitim/app`, `.env`: `/opt/kokpitim/.env`.

---

## Ön koşullar

| Gereksinim | Açıklama |
|------------|----------|
| Oracle SSH anahtarı | `ubuntu@129.159.30.175` (ör. `C:\crt\ssh-key-2026-04-18_v4.key`) |
| Git remote | `origin` → GitHub; yayın **`main`** ile yapılır |
| VM’de `.env` | `/opt/kokpitim/.env` — `SQLALCHEMY_DATABASE_URI=...postgresql...127.0.0.1...` |
| Dal | `oracle_safe_deploy.sh` içinde **`git pull origin main` sabit** |

---

## A — Yerelde (Windows / PowerShell)

### 1) Yalnız kod + dokümantasyon commit

Yedek zip’leri, `Yedekler/`, `backups/` gibi klasörleri **istemeden eklemeyin**.

```powershell
cd C:\kokpitim
git status
git add <dosyalar>   # veya seçili modüller
```

### 2) Commit mesajı (PowerShell)

Bash `heredoc` kullanmayın; çok satırlı mesaj için:

```powershell
$msg = @"
fix(surec): kısa açıklama

TASK-0XX
"@
git commit -m $msg.Trim()
```

### 3) Push

```powershell
git push origin main
```

Push tamamlanmadan VM tarafında `git pull` anlamlı güncelleme getirmez.

---

## B — VM’de güvenli yayın (tercih edilen)

**Tek komut** (SSH oturumu açıp veya tek satırda):

```bash
cd /opt/kokpitim/app && sudo bash scripts/ops/oracle/oracle_safe_deploy.sh
```

Betik sırasıyla:

1. **PostgreSQL tam yedek** — `/opt/kokpitim/backups/pg_kokpitim_db_full_<timestamp>.sql.gz`
2. **Temel tablolar satır sayısı** (önce)
3. **`git pull origin main`**
4. **`docker build`** → `kokpitim_web:latest`
5. Konteyner **`kokpitim-web`**: `--network host`, `--env-file /opt/kokpitim/.env`, `instance` → `/opt/kokpitim/instance`
6. Konteyner içinde **`python3 scripts/run_db_upgrade.py`** (Alembic)
7. **Satır sayıları** (sonra) — öncekiyle aynı değilse betik **çıkar**
8. **`curl http://127.0.0.1/health`** (nginx üzerinden)

### Yerel Windows’tan tek seferde SSH

```powershell
ssh -i C:\crt\ssh-key-2026-04-18_v4.key ubuntu@129.159.30.175 `
  "cd /opt/kokpitim/app && sudo bash scripts/ops/oracle/oracle_safe_deploy.sh"
```

> **Legacy:** GCP için `scripts/vm_safe_deploy.sh` ve `gcloud compute ssh sps-server-v2` — yalnızca arşiv.

---

## C — Yayın sonrası doğrulama

| Kontrol | Komut / eylem |
|--------|----------------|
| Health | Tarayıcı veya VM’de: `curl -sS http://127.0.0.1/health` |
| Log | `docker logs kokpitim-web --tail=100` |
| Site | https://kokpitim.com — login, kritik modül (ör. süreç karnesi, PGV) |

---

## D — Bilinen sorunlar ve çözümler (deneyim özeti)

### 1) `kpi_data_pkey` duplicate key / sekans geride

**Belirti:** `INSERT INTO kpi_data` sırasında `duplicate key value violates unique constraint "kpi_data_pkey"`.

**Neden:** Import veya dump sonrası PostgreSQL **sequence** tablodaki `MAX(id)` ile uyumsuz.

**Çözüm (VM, Postgres kullanıcısı):**

- Tüm tablolar için (tercih): konteyner içinden  
  `docker exec kokpitim-web bash -lc 'cd /app && python3 scripts/fix_postgres_sequences.py'`  
  (Repo’da betik `PYTHONPATH=/app` ile uyumlu tutulmuştur.)
- Sadece PGV tabloları için SQL dosyası: `scripts/sql/fix_kpi_data_sequences.sql` — `psql -f` ile.

**Not:** Uygulama tarafında PGV ekleme uçlarında da sekans düzeltmesi + tek retry vardır; yine de sekansı bir kez hizalamak üretimde güvenlidir.

### 2) PowerShell + uzak SQL

`$(...)` veya karma `"` içinde SQL yazmak PowerShell tarafından bozulabilir.  
**Çözüm:** SQL’i dosyaya yazıp `scp` ile Oracle VM’e atın, VM’de `psql -f /tmp/....sql` çalıştırın; veya SSH oturumunda doğrudan `psql`.

### 3) Yerelde `pg_dump` ile sunucu sürümü uyumsuzluğu

İstemci PostgreSQL sürümü sunucudan düşükse `pg_dump` bağlanamayabilir. **Tam yedek** için Oracle VM üzerinde `sudo -u postgres pg_dump ...` kullanın (`oracle_safe_deploy.sh` bunu yapar).

### 4) Eski GCP deploy betikleri

`scripts/vm_safe_deploy.sh`, `deploy_code_only.sh` ve GCP yolları **legacy**. Canlı Oracle’da **`oracle_safe_deploy.sh`** kullanın.

### 5) Canlı DB SQLite değildir

Geliştirmede `instance/kokpitim.db` (SQLite) kullanılıyor olabilir; **kokpitim.com üretimi PostgreSQL** üzerindedir. VM’ye **SQLite dosyası kopyalayarak** yayın beklenmez; şema/migration Alembic ile yönetilir.

---

## E — İsteğe bağlı: dal / acil yama

- Şu an `oracle_safe_deploy.sh` **`main` sabit** çeker. Hotfix dalı yayınlanacaksa: VM’de geçici olarak ilgili dalı checkout + pull + aynı Docker adımları veya betiğe `BRANCH` desteği eklenmesi gerekir (arada prosedür sapması).
- **Öneri:** Acil düzeltmeyi `main`e merge edip standart akışı kullanın.

---

## G — Bakım modu (yayın / migration öncesi kilitlenmeyi azaltma)

| Ne | Açıklama |
|----|----------|
| **Panel** | **Yönetim Paneli** — yalnız rolü **`Admin`** olan kullanıcıda «Bakım modu» kartı görünür; `system_settings.maintenance_mode` güncellenir. |
| **Davranış** | Bakım **açıkken**: `/health`, `/login`, `/logout`, platform statikleri (`/m/...`), bakım API’si çalışır; **Admin** oturumu tüm siteye erişir; diğer tüm istekler **503** bakım sayfası. |
| **`MAINTENANCE_MODE`** | Ortamda `true` ise bakım **zorunlu** (panelden kapatılamaz). Kısa süreli tam kilitleme için deploy/migration öncesi kullanılabilir. |
| **`MAINTENANCE_OVERRIDE_OFF`** | `true` ise bakım **kapalı** sayılır (DB ne derse desin). Sunucuda felaket / kilitlenme sonrası açmak için. |
| **`MAINTENANCE_BYPASS_SECRET`** | Opsiyonel, uzun rastgele gizli anahtar. Yetkili, **tek sefer** tarayıcıda `?bakim_erisim=GİZLİ` ile (herhangi bir yol) sınırlı süreli çerez alır; bakım ekranını **Admin olmadan** aşmak için (operasyon dokümanında tutulur, herkese açık yazılmaz). |
| **SSH / psql** | `UPDATE system_settings SET value = 'false' WHERE key = 'maintenance_mode';` ile panel erişilemese bile bayrak kapatılabilir. |

> Matematiksel “sıfır risk” yoktur; bu katman **kilit kaldırmak** ve **yazmayı sınırlamak** için ek güvenlik ağıdır.

---

## F — Kontrol listesi (kopyala-yapıştır)

- [ ] Yerelde `git push origin main` başarılı
- [ ] Oracle VM’de `sudo bash scripts/ops/oracle/oracle_safe_deploy.sh` hatasız bitti
- [ ] `pg_*_full_*.sql.gz` yedek yolu kayıtlı
- [ ] `/health` `healthy`
- [ ] Sitede duman testi (login + kritik işlem)
- [ ] (Gerekirse) `fix_postgres_sequences.py` veya `fix_kpi_data_sequences.sql` çalıştırıldı

---

## Cursor / “şimdi yayınla” talimatı

Aşağıdakini aynen kullanabilirsiniz:

> `docs/YERELDEN_VM_YAYIN.md` yordamını uygula: yerelde commit+push `main`, sonra **Oracle VM**’de `oracle_safe_deploy.sh`, ardından health ve duman testi. VM = Oracle (`docs/ORACLE-PROD-VM.md`).

---

## Sorular (netleştirme)

Bu yordam **varsayılan olarak `main` ve `oracle_safe_deploy.sh`** ile yazar. İleride sık **hotfix dalı** veya **staging VM** kullanımı planlanıyorsa, bunlar için ayrı alt başlık veya betik parametresi (`BRANCH`, ikinci `APP_DIR`) eklenmesi iyi olur; ihtiyaç varsa bir sonraki revizyonda genişletilir.

---

*Son güncelleme: 2026-05-21 — VM = Oracle Cloud*
