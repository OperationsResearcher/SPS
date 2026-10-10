# 04 — Performans ve Altyapı Denetimi (salt okunur)

Tarih: 2026-10-10. Kapsam: statik kod ve script incelemesi; sunucuya erişim yok.
Etiketler: [KANIT] = kodda görüldü, [ÇIKARIM] = koşula bağlı, canlıda doğrulanmadı.
Not: Süre kısıtı nedeniyle karne/rapor servisleri örneklemeyle incelendi; micro/modules/raporlar taranmadı.

## Bulgular

### PA-001 — Her gunicorn worker'ı kendi scheduler'ını başlatır (işler çoklanır)
- Dosya: app/__init__.py:675-747, Dockerfile:44 (`--workers 8`)
- Kanıt: her create_app() içinde `BackgroundScheduler(...).start()` (digest, yedekleme ve bir diğeri); lider seçimi/kilit yok. Yedekleme yalnız `YEDEKLEME_SCHEDULER_ENABLED` env ile kapanır.
- Açıklama: 8 süreç = 8 scheduler. Gece 02:00 yedeği 8 kez, digest (açıksa) 8 kez tetiklenir; max-requests ile worker yenilenince scheduler da yeniden doğar.
- Koşul: Yayın'da scheduler bayrakları açık. Etki: 8x pg_dump (CPU/disk), mükerrer e-posta, rotasyonun (14 adet) yedekleri çok kısa sürede ezmesi. Önem: Yüksek. Etiket: [KANIT]/[ÇIKARIM-koşul]
- Çözüm: Scheduler'ı tek süreçte (ayrı container/cron) çalıştır veya Redis/PG advisory lock ile tek lider. Efor: S-M.
- Doğrulama: Yayın'da gece 02:00 log'unda kaç tetik var; backups dizinindeki dosya sayısı/zamanları.

### PA-002 — SocketIO `threading` modu + çok worker sync gunicorn
- Dosya: app/extensions.py:46-52, Dockerfile:44
- Kanıt: `async_mode="threading"`, `--threads 1`, 8 worker, `message_queue` yok.
- Açıklama: Worker'lar arası emit paylaşılmaz; websocket upgrade sync worker'da çalışmaz, long-polling sticky session olmadan oturum bulamaz ("Invalid session" 400). Gerçek zamanlı özellikler kısmen çalışmayabilir.
- Etki: Orta-Yüksek. Etiket: [ÇIKARIM] (canlı davranış test edilmedi).
- Çözüm: Redis message_queue + sticky session/tek worker, ya da özelliği SSE/polling'e çevir. Efor: M.
- Doğrulama: İki tarayıcıyla event testi; nginx log'unda socket.io 400.

### PA-003 — Tek sunucu SPOF: yedekler aynı VM'de, off-site kopya yok
- Dosya: scripts/ops/oracle/oracle_safe_deploy.sh:10,19; app/services/yedekleme_service.py:39,293
- Kanıt: BACKUP_DIR=/opt/kokpitim/backups; off-site (rclone/scp/bucket) adımı yok. Test/Demo/Yayın/PG/Redis aynı host.
- Açıklama: Disk/VM kaybında veri ve yedek birlikte gider.
- Etki: Kritik. Önem: P0. Etiket: [KANIT]
- Çözüm: Gece dump'ını şifreli olarak Oracle Object Storage/başka bölgeye kopyala; aylık restore tatbikatı. Efor: S-M.
- Doğrulama: Harici depoda dump var mı; temiz bir VM'de pg_restore denemesi.

### PA-004 — Yayın deploy'unda sağlık kapısı ve otomatik geri alma yok
- Dosya: scripts/ops/oracle/oracle_safe_deploy.sh:55-94
- Kanıt: Eski container silinip yenisi `docker run` ile başlatılır; health sonucu yalnız "UYARI" basar (satır 94). Migration yeni container içinde (satır 65), başarısızlıkta eski imaj geri getirilmez. Alembic downgrade stratejisi yok.
- Açıklama: Hatalı imaj/migration'da kesinti ve manuel müdahale.
- Etki: Yüksek. Etiket: [KANIT]
- Çözüm: Önceki imajı `:prev` etiketle; health başarısızsa otomatik geri başlat; geri yükleme komutunu script'e bağla. Efor: M.
- Doğrulama: Test'te bilerek bozuk imaj deploy edip geri dönüş süresini ölç.

### PA-005 — Yedek rotasyonu 14 adet; geri yükleme tek-transaction değil
- Dosya: app/services/yedekleme_service.py:39,167-182
- Kanıt: `_KEEP_LAST=14`; `pg_restore --clean --if-exists`, "errors ignored" tolere ediliyor.
- Açıklama: PA-001 ile çoklanırsa 14 yedek ~2 güne iner; geç fark edilen bozulmada sağlam eski yedek kalmaz. Yarım restore DB'yi tutarsız bırakabilir.
- Etki: Orta-Yüksek. Etiket: [KANIT]/[ÇIKARIM]
- Çözüm: GFS (7 günlük + 4 haftalık + 6 aylık); restore'u önce geçici DB'de doğrula; `--single-transaction`. Efor: S-M.
- Doğrulama: Restore tatbikatı; rotasyon birim testi.

### PA-006 — Gunicorn: 8 sync worker, threads=1, timeout 60
- Dosya: Dockerfile:41-44
- Kanıt: `--workers 8 --threads 1 --timeout 60`. Yorum, "aralıklı takılan worker" sorununu kök neden yerine worker artırarak çözdüğünü gösteriyor. Ayrıca hata-kontrol/kılavuz executor thread'leri (app/services/hata_kontrol_executor.py:183, kilavuz_olusturucu_executor.py:347) web worker içinde çalışır.
- Açıklama: 8 eşzamanlı yavaş rapor/karne isteği siteyi tıkar; arka plan thread'leri max-requests recycle'ında kesilebilir. Celery tanımlı (app/tasks.py) ama bağlı olup olmadığı doğrulanmadı.
- Etki: Orta-Yüksek. Etiket: [KANIT]/[ÇIKARIM]
- Çözüm: gthread (örn. 4 worker x 4 thread), ağır işleri ayrı worker/kuyruğa taşı, çekirdek sayısına göre ayarla. Efor: M.
- Doğrulama: Karne endpoint'iyle yük testi; worker timeout log sayısı.

### PA-007 — Süreç performans servisinde döngü içi sorgular (N+1)
- Dosya: app/services/process_performance_service.py:61-93, 317-333
- Kanıt: `for pg in surec_pgler:` içinde her PG için `generatePeriyotVerileri(...)` (DB'ye gider) ve `pg.alt_strateji.ana_strateji` lazy erişimi; kaydetme döngüsünde `User.query.get` / `SurecPerformansGostergesi.query.get` her veri satırında.
- Açıklama: Sorgu sayısı PG sayısı x periyoda doğrusal artar. Karşı örnek: score_engine_service.py:353-440 toplu yükleme yapmış (P1 N+1 önlemi), yani doğru desen kod tabanında mevcut.
- Etki: Orta. Etiket: [KANIT] (sorgu sayısı ölçülmedi).
- Çözüm: `pg_id IN (...)` ile tek sorgu, dict'ten oku; kaydetmede önyükleme. Efor: M.
- Doğrulama: SQLAlchemy sorgu sayacı ile istek başına sorgu sayısı (hedef <20).

### PA-008 — Skor motorunda O(n²) `next(...)` aramaları
- Dosya: app/services/score_engine_service.py:449,456
- Kanıt: her süreç/çocuk için `next((p for p in processes if p.id == ...))`.
- Açıklama: Büyük tenant'ta CPU maliyeti ikinci dereceden; DB'yi yormaz.
- Önem: Düşük. Etiket: [KANIT]
- Çözüm: `proc_by_id = {p.id: p for p in processes}`. Efor: XS.
- Doğrulama: Büyük tenant üzerinde cProfile.

### PA-009 — Bileşik indeksler seyrek
- Dosya: app/models/process.py (Index yalnız :452,531,534,675,676), app/models/core.py:17,216
- Kanıt: 211 tekil `index=True` var; `Process(tenant_id,is_active)` ve `ProcessKpi(process_id,is_active)` için bileşik indeks yok, oysa score_engine bu filtrelerle çalışıyor (satır 419-441).
- Açıklama: Veri küçükken sorun yok; tenant sayısı artınca seq scan riski. EXPLAIN yapılmadı.
- Önem: Orta-Düşük. Etiket: [ÇIKARIM]
- Çözüm: `pg_stat_statements` aç, EXPLAIN ANALYZE ile doğrula, sonra Alembic ile indeks ekle. Efor: S.
- Doğrulama: pg_stat_statements'ta en yavaş 10 sorgu.

### PA-010 — Redis erişilemezse sessizce SimpleCache/memory limiter'a düşüş
- Dosya: app/__init__.py:72-80, config.py:112-135, docker-compose.yml:14-17
- Kanıt: RedisCache istenip erişilemezse SimpleCache'e fallback (yalnız log uyarısı). 8 worker = 8 ayrı cache; limiter memory:// ise limit x8 gevşer. Yayın `--network host` ile compose dışında, Redis host servisi.
- Etki: Orta (tutarsız veri + login throttle gevşemesi). Etiket: [KANIT]/[ÇIKARIM-koşul]
- Çözüm: Yayın'da Redis yoksa alarm/başlatmayı reddet; /health'e Redis ekle. Efor: S.
- Doğrulama: Test'te Redis'i durdurup /health ve rate-limit davranışı.

### PA-011 — /health yalnız DB'ye bakar; derin kontrol ve dış izleme kanıtı yok
- Dosya: app/__init__.py:531-546
- Kanıt: tek `SELECT 1`. Sentry koşullu (init_sentry); uptime/alarm kanıtı yok. Kökte err.log, error.log, hata_logu*.txt gibi dosya tabanlı log izleri var.
- Etki: Orta (geç tespit). Etiket: [KANIT]
- Çözüm: Derin health (db, redis, son yedek yaşı); dış uptime izleme; yedek hatasında e-posta. Efor: S.
- Doğrulama: Yedeği kapatınca alarm geliyor mu.

### PA-012 — Migration disiplini belirsiz: 22 aktif + 8 `_disabled` revizyon
- Dosya: migrations/versions/ (22), migrations/versions/_disabled (8); kökte add_*_sql.sql, add_performance_indexes.sql
- Kanıt: Model sayısına göre az revizyon; şema kısmen elle SQL/seed ile kuruluyor. Test/Demo "sıfırdan kurulur" olduğundan sapma gizlenebilir.
- Açıklama: `alembic heads` birden fazla ise upgrade kırılır; model-şema farkı doğrulanmadı.
- Etki: Orta. Etiket: [ÇIKARIM]
- Çözüm: Deploy öncesi `alembic heads` tek mi + `alembic check`; kök SQL'leri arşivle. Efor: S-M.
- Doğrulama: `alembic heads`, `alembic check` (yerel ve Test).

### PA-013 — İmaj hijyeni: root kullanıcı, `COPY . .`, Python sürüm sapması
- Dosya: Dockerfile:9-30
- Kanıt: USER tanımı yok; `COPY . .` kökte backups/, htmlcov/, *.dump, data_dump.json, xlsx gibi büyük/hassas dosyalar varken .dockerignore içeriği bu denetimde doğrulanmadı; 3.11 (imaj) vs 3.13 (yerel).
- Etki: Orta-Düşük (imaj şişmesi, veri sızıntısı, ortam sapması). Etiket: [ÇIKARIM]
- Çözüm: .dockerignore'u doğrula, non-root USER, requirements kilidi. Efor: S.
- Doğrulama: `docker history`/imaj boyutu; imajda `ls /app/backups`.

### PA-014 — Test/Demo/Yayın aynı VM'de kaynak yarışı
- Dosya: docs/KURALLAR-MASTER.md §8.1; Dockerfile (her ortam 8 worker)
- Kanıt: üç container x 8 worker + PG + Redis tek host.
- Açıklama: Test'teki sıfırdan kurulum/restore Yayın'ı yavaşlatabilir; OOM-killer riski.
- Önem: Orta. Etiket: [ÇIKARIM]
- Çözüm: Test/Demo için worker=2 ve container bellek limiti. Efor: XS.
- Doğrulama: `docker stats`, `dmesg | grep -i oom`.

## Öncelik özeti
- P0: PA-003
- P1: PA-001, PA-004, PA-006, PA-002
- P2: PA-005, PA-007, PA-010, PA-011, PA-012
- P3: PA-008, PA-009, PA-013, PA-014
