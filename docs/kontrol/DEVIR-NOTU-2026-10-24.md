# DEVİR NOTU — 2026-10-24 (Yayın deploy + KMF geçişi sonrası)

> Yeni sohbet bu dosyayı okuyarak başlasın. Ayrıntı: `docs/kontrol/YAYIN-HAZIRLIK-2026-10-24.md`, `docs/kontrol/KMF-VERI-ENVANTERI-2026-10-24.md`, TASKLOG TASK-317…333.

## 1. Şu an nerede
| | |
|---|---|
| **Yayın** | kod `875e6fd9`, alembic `mg01a2b3c4d5`, sağlık 200, `YEDEKLEME_SCHEDULER_ENABLED=false` |
| **KMF (tenant 16)** | yıl bazlı geçiş UYGULANDI; karışık PG 0; kıyas ✅ KAYIP YOK (22227 → 23608) |
| **Test** | yeni kodla sıfırdan kuruldu; alembic hâlâ `bi01c4e5f6a7` (yerel dump'tan geldi, 3 migration uygulanmadı) |
| **Demo** | dokunulmadı |
| **Git** | `main` = `1a60a7db` (yerel). `origin/main` = `875e6fd9`. **1 commit push'lanmadı** (TASK-333) |

## 2. Bu oturumda yapılanlar (özet)
- KalDer öğrenme paketleri P1–P8, P10 main'de (P9 şema/veri bilerek yapılmadı; Yayın'ı bloklamıyor).
- Alembic çift head birleştirildi (`mg01a2b3c4d5`) + test.
- KMF araçları: `kurum_veri_kiyas.py`, `yayin_kopya_al.py`, `yilbazli_faz1_2b_karisik_pg_duzelt.py`, `kurum_yilbazli_gecis.py` (sıra 1.2 → 1.2b → 1.5 → 1.4 → doğrulama; `--calistir` için `--yedek-onay` zorunlu).
- 31 karışık yıllı PG / 28 görünmez ölçüm düzeltildi.
- `yayina_ver.ps1` iki hatası düzeltildi: çıkış kodu dizi olması (sahte FALLBACK) ve uzak komutta CR.
- HATA-04 kodda zaten doğruydu (kapandı); kart açıklamaları 501/501 (Yayın'da zaten Text + 501 kart).

## 3. Yedekler ve geri alma
- Yerel: `backups/yayin/yayin_2026-10-24_1028.dump` (ilk), `_1512.dump` (deploy öncesi), `_1531.dump` (sonrası) + instance tar'ları. Gitignored. Dosyayı ayrı diske de kopyalayın.
- Sunucu: `/opt/kokpitim/backups/pg_kokpitim_db_full_20261024_122507.sql.gz`.
- Geri alma CSV (1.2b): Yayın container `instance/yilbazli/karisik_pg_geri_alma_20261024_123039.csv`.
- Yayın `.env` yedeği: `/opt/kokpitim/.env.bak_20261024`.
- Yerel DB'ler: `kokpitim_yayin_oncesi` (dokunma), `_oncesi2`, `_sonrasi`, `_prova`, `_prova2` (silinebilir).

## 4. Açık işler
1. **Tarayıcı testi (kullanıcıda, canlıda):** KMF SR5/SR8/SR11 karneleri, 2024–2026 yılları, daha önce görünmeyen 28 ölçüm.
2. **Push:** `git push origin main` (1 commit). Kullanıcı "push'la" demeden yapılmaz.
3. **Test'i yeniden kurma** (isteğe bağlı): alembic Test'te eski; Test sıfırdan kurulurken `run_db_upgrade` çalışmıyor.
4. `SSO_ALLOWED_DOMAINS`: Google SSO kullanılıyorsa Yayın `.env`'e alan adı eklenmeli (boşsa yeni kullanıcı otomatik açılmaz).
5. Birleştirilmiş `claude/kalder-ogrenme-*` dalları ve `claude/yayin-hazirlik` silinebilir (`git branch -d`, kullanıcı onayıyla).
6. Yayın'da yedek disk: `/app/instance/yedekler` ~2,5 GB, kök disk ~%84 — eski yedekleri temizleme kararı bekliyor.
7. P5 kart seed'i kart keşfi sonrası (kullanıcı adımı), yerelde `.env` `KOKPITIM_ENV=local`.

## 5. Bu makinede / bu projede tuzaklar
- **İzinler:** Yayın'a yazan işler (ssh yazma, deploy script, container içi python) otomatik mod sınıflandırıcısına takılabilir. Kullanıcı Bash için ssh kuralı verdi; canlı veri değiştiren komutları kullanıcı kendi PowerShell'inden çalıştırır (Windows'ta `sudo` yok — önce ssh ile sunucuya girilir).
- `yayina_ver.ps1` push kontrolü git stderr'de düşüyor → `-AtlaPushKontrol` (push'un tamam olduğunu elle doğrula).
- Yıkıcı git yok (`checkout -f`, `reset --hard`); `scripts/ops/oracle/*.sh` üzerinde kullanıcının uncommitted değişiklikleri var, dokunma.
- `taskkill /IM` yok; yalnız kendi PID'ini port üzerinden öldür.
- Yerel DB'ye başka DB'yi `SQLALCHEMY_DATABASE_URI` env ile yönlendir; Türkçe SQL'i UTF-8 dosyayla ver (`PGCLIENTENCODING=UTF8`).
- Faz 1.5 uyarısı "kalan yanlış yıl 343" beklenen: 204 Tenant 28 (Yayın'da zaten var) + 139 KMF pasif 2020 PG.
- Kurallar: Yayın = Yerel → Test → Yayın; "yayına çıkalım" demeden deploy yok; Yayın'a yazma yalnızca kullanıcı isteğiyle.
