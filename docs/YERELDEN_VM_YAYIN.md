# Yerelden VM’e yayın (Kokpitim / kokpitim.com)

Bu dosya, **yerelde yapılan kod değişikliklerinin** üretim VM’ine güvenli şekilde alınması için **tek referans yordamdır**.  
VM adı, zone ve proje özeti: `docs/PROJE-MASTER.md` → bölüm 12.

---

## Özet akış

1. Yerelde değişiklikleri **commit** edip **GitHub `main`** dalına **push** et.
2. VM’de **`scripts/vm_safe_deploy.sh`** çalıştır (otomatik: PG yedek, `git pull`, Docker build, Alembic, satır sayısı kontrolü, health).
3. Gerekirse **sekans / bakım** adımlarını uygula (aşağıda).

Canlı veritabanı **PostgreSQL** (`kokpitim_db`). Uygulama **Docker** içinde (`sps-web`), kod dizini: `/home/kokpitim.com/public_html`.

---

## Ön koşullar

| Gereksinim | Açıklama |
|------------|----------|
| `gcloud` CLI | Giriş: `gcloud auth login` — VM SSH için yetkili hesap |
| Git remote | `origin` → GitHub; yayın **`main`** ile yapılır |
| VM’de `.env` | `SQLALCHEMY_DATABASE_URI=...postgresql...` (veya `.env.postgres`) — yoksa deploy betiği durur |
| Dal | `vm_safe_deploy.sh` içinde **`git pull origin main` sabit**; başka dal yayınlanacaksa önce betik/VM’de dal stratejisi netleştirilmeli |

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
cd /home/kokpitim.com/public_html && sudo bash scripts/vm_safe_deploy.sh
```

Betik sırasıyla:

1. **PostgreSQL tam yedek** — `backups/pg_kokpitim_db_full_<timestamp>.sql.gz`
2. **Temel tablolar satır sayısı** (önce)
3. **`git pull origin main`**
4. **`docker build`** → `sps_web_final:latest`
5. Konteyner **`sps-web`** yeniden oluşturulur: port **80→5000**, `--env-file .env` [+ `.env.postgres`], `--add-host=host.docker.internal:host-gateway`, `instance` volume
6. Konteyner içinde **`python3 scripts/run_db_upgrade.py`** (Alembic)
7. **Satır sayıları** (sonra) — öncekiyle aynı değilse betik **çıkar** (veri kaybı şüphesi)
8. **`curl http://127.0.0.1/health`**

Başarı çıktısında yedek dosya yolu yazdırılır; bunu not edin.

### Yerel Windows’tan tek seferde SSH ile çalıştırma

```powershell
gcloud compute ssh sps-server-v2 --zone=europe-west3-c --command="cd /home/kokpitim.com/public_html && sudo bash scripts/vm_safe_deploy.sh"
```

(Instance / zone farklıysa `docs/PROJE-MASTER.md` ile hizalayın.)

---

## C — Yayın sonrası doğrulama

| Kontrol | Komut / eylem |
|--------|----------------|
| Health | Tarayıcı veya VM’de: `curl -sS http://127.0.0.1/health` |
| Log | `sudo docker logs sps-web --tail=100` |
| Site | https://kokpitim.com — login, kritik modül (ör. süreç karnesi, PGV) |

---

## D — Bilinen sorunlar ve çözümler (deneyim özeti)

### 1) `kpi_data_pkey` duplicate key / sekans geride

**Belirti:** `INSERT INTO kpi_data` sırasında `duplicate key value violates unique constraint "kpi_data_pkey"`.

**Neden:** Import veya dump sonrası PostgreSQL **sequence** tablodaki `MAX(id)` ile uyumsuz.

**Çözüm (VM, Postgres kullanıcısı):**

- Tüm tablolar için (tercih): konteyner içinden  
  `sudo docker exec sps-web bash -lc 'cd /app && python3 scripts/fix_postgres_sequences.py'`  
  (Repo’da betik `PYTHONPATH=/app` ile uyumlu tutulmuştur.)
- Sadece PGV tabloları için SQL dosyası: `scripts/sql/fix_kpi_data_sequences.sql` — `psql -f` ile.

**Not:** Uygulama tarafında PGV ekleme uçlarında da sekans düzeltmesi + tek retry vardır; yine de sekansı bir kez hizalamak üretimde güvenlidir.

### 2) PowerShell + `gcloud --command` içinde SQL

`$(...)` veya karma `"` içinde `SELECT MAX(id)` yazmak PowerShell tarafından bozulabilir.  
**Çözüm:** SQL’i dosyaya yazıp `gcloud compute scp` ile VM’e atın, VM’de `psql -f /tmp/....sql` çalıştırın; veya doğrudan VM’de `psql` oturumu açın.

### 3) Yerelde `pg_dump` ile sunucu sürümü uyumsuzluğu

İstemci PostgreSQL sürümü sunucudan düşükse `pg_dump` bağlanamayabilir. **Tam yedek** için VM üzerinde `sudo -u postgres pg_dump ...` kullanın (`vm_safe_deploy.sh` bunu zaten yapar).

### 4) `docs/deploy_code_only.sh` ve eski PROJE-MASTER komutu

`deploy_code_only.sh` ve bazı eski tek satırlık `docker run` örnekleri **`.env` / `.env.postgres` ve `host.docker.internal`** kullanmıyor olabilir. Canlı ortamda **tercih her zaman `vm_safe_deploy.sh`** olmalı; aksi halde uygulama veritabanına bağlanamayabilir veya yanlış URI ile ayağa kalkabilir.

### 5) Canlı DB SQLite değildir

Geliştirmede `instance/kokpitim.db` (SQLite) kullanılıyor olabilir; **kokpitim.com üretimi PostgreSQL** üzerindedir. VM’ye **SQLite dosyası kopyalayarak** yayın beklenmez; şema/migration Alembic ile yönetilir.

---

## E — İsteğe bağlı: dal / acil yama

- Şu an `vm_safe_deploy.sh` **`main` sabit** çeker. Hotfix dalı yayınlanacaksa: VM’de geçici olarak ilgili dalı checkout + pull + aynı Docker adımları veya betiğe `BRANCH` desteği eklenmesi gerekir (arada prosedür sapması).
- **Öneri:** Acil düzeltmeyi `main`e merge edip standart akışı kullanın.

---

## F — Kontrol listesi (kopyala-yapıştır)

- [ ] Yerelde `git push origin main` başarılı
- [ ] VM’de `sudo bash scripts/vm_safe_deploy.sh` hatasız bitti
- [ ] `pg_*_full_*.sql.gz` yedek yolu kayıtlı
- [ ] `/health` `healthy`
- [ ] Sitede duman testi (login + kritik işlem)
- [ ] (Gerekirse) `fix_postgres_sequences.py` veya `fix_kpi_data_sequences.sql` çalıştırıldı

---

## Cursor / “şimdi yayınla” talimatı

Aşağıdakini aynen kullanabilirsiniz:

> `docs/YERELDEN_VM_YAYIN.md` yordamını uygula: yerelde commit+push `main`, sonra VM’de `vm_safe_deploy.sh`, ardından health ve kısa duman testi; PGV hatası görülürse sekans bölümüne göre düzelt.

---

## Sorular (netleştirme)

Bu yordam **varsayılan olarak `main` ve `vm_safe_deploy.sh`** ile yazar. İleride sık **hotfix dalı** veya **staging VM** kullanımı planlanıyorsa, bunlar için ayrı alt başlık veya betik parametresi (`BRANCH`, ikinci `APP_DIR`) eklenmesi iyi olur; ihtiyaç varsa bir sonraki revizyonda genişletilir.

---

*Son güncelleme: 2026-04-03*
