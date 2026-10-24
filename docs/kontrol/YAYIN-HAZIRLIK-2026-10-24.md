# Yayın hazırlık raporu — 2026-10-24

> Kapsam: yerel `main` (KalDer P1–P10 merge'ü sonrası) → Test → Yayın. Bu belge **deploy etmez**; deploy yalnız
> kullanıcı "test'e gönderelim" / "yayına çıkalım" dediğinde (KURALLAR §8, REHBER §0). Kural 7 gereği 4 katman tek listede.

## 0. Durum özeti
| | |
|---|---|
| Yerel `main` | `397371e4` + `claude/yayin-hazirlik` dalındaki düzeltmeler (aşağıda) |
| `origin/main` | `925bb5a4` → **yerelden 21 commit geride; push YAPILMADI** (orchestrator ön koşulu: `origin/main = yerel HEAD`) |
| Yayın'ın GERÇEK konumu (2026-10-24, sunucudan okundu) | **kod `4cb738bb` (2026-09-08), alembic `bi01c4e5f6a7`**, PostgreSQL 14.24, aarch64 (ARM), DB 328 MB, kök disk %84 dolu (32 GB boş). Etiket `deploy-2026-07-08` yanıltıcıydı. |
| Yayın'a göre bekleyen | **3 migration** (`gs01 → ux01 → mg01`; önceki "15" sayısı etiketten hesaplandığı için YANLIŞTI), 8 yeni ortam değişkeni ve **KMF veri geçişi (aşağıda 2.4, ZORUNLU)** |
| Otomatik test | Py 3.11: 1227 geçti, 0 başarısız (KalDer P1–P10 + Docker kilidi); Test'te Docker build henüz yapılmadı |

## 1. 🔴 Bulunan ve düzeltilen deploy engeli: iki Alembic head
`hd01a2b3c4d5` iki dala ayrılmıştı (`bi01c4e5f6a7` ve `gs01a2b3c4d5 → ux01a2b3c4d5`). `alembic upgrade head` **"Multiple head revisions"** ile durur ve deploy script'i (`oracle_safe_deploy.sh`, REHBER §4 adım 5) takılırdı.
- **Düzeltme:** `migrations/versions/mg01a2b3c4d5_merge_bi01_ux01.py` (boş birleştirme, şemayı değiştirmez). Tek head: `mg01a2b3c4d5`.
- **Koruma:** `tests/test_alembic_tek_head.py` (tek head + yetim migration yok).
- ⚠ **Yerel geliştirme DB'si grafikten sapmış:** `alembic_version = bi01c4e5f6a7` ama `users.session_version` (gs01 etkisi) VAR, `ux01` indeksi YOK. Yerelde `flask db upgrade` `gs01`'de "kolon zaten var" diyebilir; Yayın/Test'te zincir baştan sıralı çalışır, sorun beklenmez. Yerel için gerekirse: `flask db stamp mg01a2b3c4d5` (indeks eksik kalır; ux01'in SQL'i elle koşulabilir).

## 2. Dört katman listesi (REHBER §0 madde 7)
### 2.1 Kod
- 187 commit / 800 dosya (etiketten bu yana). Sunucudaki gerçek commit `dort_katman_kontrol.sh` ile okunur (push sonrası).
- Dockerfile artık `requirements.lock` kuruyor (x86_64 + aarch64 cp311 wheel doğrulandı, `http-ece` sdist derlenir). **İlk gerçek Docker build Test'te olacak** (gcc / libpq-dev burada doğrulanmadı).
- Python 3.11 imajı ile kod uyumlu (tam test 3.11'de geçti).

### 2.2 Şema — Yayın `bi01c4e5f6a7`'de; bekleyen: `gs01a2b3c4d5` (users.session_version), `ux01a2b3c4d5` (bireysel PG benzersiz indeks), `mg01a2b3c4d5` (birleştirme). Aşağıdaki liste etiketten (Temmuz) bu yana TÜM migration'lardır; Yayın'da çoğu zaten uygulanmış
Veri DEĞİŞTİRENLER (hepsi UPDATE: NULL → değer; iki temizlik adımı **kalın**):
| Migration | Etki |
|---|---|
| `a1f2c3d4e5b6` yılbazlı faz 1.1 | 8 tabloya `plan_year_id` + FK + index; kurumun **en eski** plan yılıyla backfill |
| `yb14a7c2e9f1` / `yb16b3d8f4a2` | `is_included`; `project`/`task` plan yılı (kurumun aktif/son yılı) |
| `bi01c4e5f6a7` | bireysel PG yılı kaynak süreç PG'sine hizalanır |
| `f0aa4591b689` | `kpi_data.actual_numeric/target_numeric` + metinden sayıya backfill (**en büyük tablo**: yerelde 367 bin satır / 91 MB) |
| **`e9669efe440c`** | **yetim `kpi_data.user_id` → NULL** (ölçüm korunur), FK yeniden kurulur, `period_type` normalize |
| **`ux01a2b3c4d5`** | **mükerrer aktif bireysel PG: en eskisi kalır, kalanlar `is_active=false`** + benzersiz kısmi indeks |
| `hd01a2b3c4d5` / `b7d3e1f4a920` | risk ısı haritası: `project_id`, elle girilmiş satırların kaynak eşlemesi |
| `c927a97a2fef` | `kpi_data_audits` eski/yeni hedef kolonları |

Yapısal / zararsız: `391945351814` (varchar→text), `da9b27f1a650` (index), `gs01a2b3c4d5` (`users.session_version`), `f6a7b8c9d0e1` (`demo_requests`), `yb20c5e1a8d3` (mühür denetim tablosu).

**Yayın'da deploy ÖNCESİ çalıştırılacak salt-okunur ön kontrol:** `scripts/ops/yayin_onkontrol.sql` (yazmaz; 11 bölüm: mevcut revizyon, tablo boyutları, ux01'de pasifleşecek satır sayısı, yetim user_id, period_type dağılımı, backfill kapsamı, plan yılı olmayan kurum, risk kaynakları, veri sayıları). Çıktıyı kontrol dosyasıyla birlikte `docs/kontrol/` altına kaydet:
```bash
psql "$DATABASE_URL" -f scripts/ops/yayin_onkontrol.sql > docs/kontrol/yayin_onkontrol_$(date +%F_%H%M).txt
```
Yerelde aynı betik çalıştı (referans): kpi_data 367.219 satır; ux01 mükerrer 0; yetim user_id 0; planı olmayan aktif kurum 5.

### 2.3 Veri
Kırmızı çizgi ritüeli değişmez: **kontrol dosyası + DB yedeği (custom + sql.gz) + kod yedeği** (REHBER §3). Deploy sonrası satır sayıları kontrol dosyasıyla birebir aynı olmalı (`oracle_safe_deploy.sh` satır kilidi). Yukarıdaki ux01 / e9669 sayıları > 0 ise kullanıcıya bildirilir.

### 2.4 Tek seferlik işlemler (migration ile GELMEZ)
0. **🔴 KMF yıl bazlı veri geçişi (ZORUNLU, Yayın'da henüz uygulanmadı):** `yilbazli_faz1_2_clone_zinciri.py --tenant 16 --calistir` → `yilbazli_faz1_5_kpi_data_remap.py --calistir` → `yilbazli_faz1_4_override_goc.py --tenant 16 --calistir` (6 Ekim TASK-311'deki yerel sıra). Yayın'da yapı farkı yalnız KMF'dir (11 süreç/187 PG yılsız; yerelde 77/973); diğer tüm kurumlar Yayın ile yerelde birebir aynı. **Yayın kopyası üzerinde prova edildi, KMF'de kayıp yok** (ayrıntı, 28 görünmez ölçüm bulgusu ve kontrol prosedürü: [KMF-VERI-ENVANTERI-2026-10-24.md](KMF-VERI-ENVANTERI-2026-10-24.md)). Bu işlemden önce DB yedeği şart; yedek aracı `scripts/ops/yayin_kopya_al.py`.
1. **Kart keşfi** (`/admin/hierarchy` → kart keşfi): yeni kartlar (ör. `masaustu.bekleyen_pg`, `masaustu.ilk_kurulum`, `temel_akis.serit`) `system_cards`'a girer. Seed'den ÖNCE.
2. `seed_card_descriptions.py --calistir` (orchestrator: `yayin_seed_kart.sh`): ön koşul `description` tipi `text` (391945351814 sonrası).
3. **`scripts/seed_masaustu_yeni_kartlar.py`** (MA21, MA22, TA01): orchestrator'a `EXTRA_SEEDS="scripts/seed_masaustu_yeni_kartlar.py"` ile eklenir. EN karşılığı `.po`'da hazır.
4. `docs/kontrol/seed_calistirma_kaydi.md` güncellenir (yeni satır eklendi).

## 3. Ortam değişkenleri (sunucu `.env`: operatör kontrol eder; değerleri bu belgeye YAZMA)
| Değişken | Varsayılan / davranış | Yayın / Test için |
|---|---|---|
| `KOKPITIM_ENV` | `local` ise admin yedek / hata-kontrol araçları açık | **Sunucuda ASLA `local` olmamalı** (tanımsız bırak) |
| `SSO_ALLOWED_DOMAINS` | boşsa Google SSO ile **yeni kullanıcı otomatik açılmaz** (eskiden açılıyordu) | Google SSO kullanılıyorsa alan adlarını ekle |
| `YEDEKLEME_SCHEDULER_ENABLED` | **varsayılan `true`**: her gece 02:00 uygulama içi tam DB dökümü + **~250–580 MB kod arşivi**, `kokpitim-instance` volume'una (son 14 tutulur); yalnız Demo'da kapalı. **Yayın'da zaten çalışıyor: `/app/instance/yedekler` şu an 2,5 GB, kök disk %84 dolu** (eski kodda da vardı; bu değişken onu kapatabilmeyi sağlıyor) | ⚠ **KARAR:** VM'in kendi yedeği (`oracle_full_backup.sh`) var, sunucuda kod git'te → önerim Yayın/Test'te `false` (disk dolması riski, Demo'da yaşandı: TASK-239) |
| `DEMO_ALLOWED_HOSTS` | varsayılan demo + yerel; Yayın / Test'te `/demo/start` 404 | Demo'da varsayılan yeterli |
| `SOCKETIO_CORS_ORIGINS` | tanımsız = yalnız aynı kaynak | nginx arkasında aynı alan adı → dokunma |
| `REMINDER_SCHEDULERS_ENABLED` | varsayılan kapalı | değişiklik yok |
| `LLM_TIMEOUT_SECONDS` (40), `LLM_ALLOW_PRIVATE_BASE_URL` (kapalı) | varsayılanlar güvenli | değişiklik yok |
| `ENCRYPTION_KEY`, `SECRET_KEY` | **3 ortamda sırayla patlamış risk** (hafıza notu); `docker restart` env'i yeniden okumaz | deploy öncesi varlığını doğrula |

## 4. Davranış değişiklikleri (kullanıcılara / operatöre görünür)
- **CSRF:** tüm POST/PUT/DELETE token ister (sayfa JS'i `csrf_fetch.js` ile otomatik ekler). **Tarayıcı dışı çağıran** (betik, webhook, mobil) varsa 400 alır. Envanter: muafiyeti kaldırılan 53 uç tarayıcı arayüzünden çağrılıyor; harici çağıran bilinmiyor → Test'te doğrula.
- **Karne:** başarı yüzdesi ve sapma uyarıları tek motordan; bazı PG'lerde rakam değişebilir (`docs/kontrol/KALDER-KARNE-MOTORU-KIYAS.md`). **Test'te gerçek kurum verisiyle önce/sonra kıyası** al.
- Terminoloji: "KPI" → "PG"; EN çevirisi tamamlandı; logo yükleme (legacy uç) düzeltildi.

## 5. Önerilen sıra (hepsi kullanıcı komutuyla)
1. **"push'la"** → `git push origin main` (+ bu dalın merge'ü).
2. `.\scripts\ops\oracle\yayina_ver.ps1 -Mod kontrol` → yalnız 4 katman raporu (yazmaz).
3. **"test'e gönderelim"** → `-Mod test -Onay` (Test **sıfırdan** kurulur). Test'te: Docker build başarılı mı, migration'lar sorunsuz mu (`alembic current` = `mg01a2b3c4d5`), `/health`, tarayıcı testi (artifact: https://claude.ai/artifact/YNoaBojR69dsiy19gEZDmU), karne rakam kıyası.
4. Yayın'da `yayin_onkontrol.sql` + kontrol dosyası + yedek. **KMF için ayrıca:** `python scripts/ops/yayin_kopya_al.py --db kokpitim_yayin_oncesi_<tarih>` (deploy'dan hemen önce referans kopya; 2026-10-24 yedeği `backups/yayin/yayin_2026-10-24_1028.dump` zaten alındı).
5. **"yayına çıkalım"** → `-Mod yayin -Onay` (yedek + pull + build + alembic + satır kilidi) → **KMF veri geçişi (§2.4 madde 0)** → seed (§2.4) → `https://www.kokpitim.com/health` → **KMF kontrolü** (`yayin_kopya_al.py --db kokpitim_yayin_sonrasi` + `kurum_veri_kiyas.py kiyas ...`; KMF-VERI-ENVANTERI §5).
6. Geri dönüş: rollback image etiketi (REHBER §4 adım 1) + DB yedeği; şema geri dönüşü için migration `downgrade`'leri veri değiştirenlerde güvenilir DEĞİL → **yedekten dön**.

## 6. Açık kararlar / engeller
1. 🔴 **"Tüm L paketleri bitmeden Yayın yok" (2026-06-19, bağlayıcı):** bu kuralın koşulu sağlandı mı? Sağlandıysa onay ver; sağlanmadıysa Yayın bekler (Test'e gönderme serbest).
2. `YEDEKLEME_SCHEDULER_ENABLED` Yayın / Test'te kapatılsın mı? (öneri: evet)
3. Google SSO kullanılıyor mu → `SSO_ALLOWED_DOMAINS`.
4. Push + bu dalın `main`'e merge'ü (migration birleştirme olmadan deploy engelli).
5. **KMF veri geçişi ve karışık yapılı 31 PG kopyası** (28 ölçüm yıl bazlı karnede görünmez): karar/plan [KMF-VERI-ENVANTERI-2026-10-24.md](KMF-VERI-ENVANTERI-2026-10-24.md) §4 ve §6.
