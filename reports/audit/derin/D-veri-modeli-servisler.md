# ALAN D — Veri modeli, migration, arka plan işleri, servis katmanı (derin analiz)

Tarih: 2026-10-10 | Yöntem: salt-okunur. AST ile "modelde olmayan alan" taraması (model sınıfı özellikleri × tüm `Model.alan`, `Model(alan=...)`, `filter_by(alan=...)` kullanımları), `create_app()` + SQLAlchemy `inspect` ile model↔yerel DB kıyası, `SELECT`/`pg_*` sayımları (yazma yok), manuel kod okuma. `reports/audit/04-performans-altyapi.md` tekrarlanmadı.
Etiketler: [KOD] kodda doğrulandı · [DB] yerel DB ölçümü · [DEĞER] tasarım/risk.
Not: Kök altındaki `Kalder/` dizini git'te izlenmeyen (0 izlenen dosya) tam bir repo kopyasıdır; tüm bulgular kök koddur, `Kalder/` taramadan çıkarıldı.

Kesin sayı: **28 bulgu** (1 Kritik, 5 Yüksek, 13 Orta, 9 Düşük).

---

## D-001 — `log_task_activity` her çağrıda patlıyor ve `rollback()` ile görev güncellemesini siliyor
- Yer: `services/task_activity_service.py:25-38` (TaskActivity(action=, field_name=, old_value=, new_value=, description=)) ↔ `app/models/portfolio_project.py:406-413` (modelde yalnız `activity_type`, `details`); tetikleyici `api/routes_projects.py:639-642, 687-693, 765-766`, tek commit `:729`.
- Kanıt: Modelde `action/field_name/old_value/new_value/description` yok → ctor `TypeError: 'action' is an invalid keyword argument`. `except` içinde `db.session.rollback()`. `api_gorev_guncelle` (PUT) tüm alan değişikliklerini oturumda biriktirir, commit en sonda (729); `log_task_updated/assigned/status_changed` commit'ten ÖNCE çağrılır → bekleyen tüm değişiklikler geri alınır, uç yine `success: true` döner. Silme ucunda (`:765`) önceki `TaskImpact...delete()` da geri alınır.
- Etki: Görev başlığı/durum/atama değişikliği kalıcı olmuyor, kullanıcı başarı mesajı görüyor (sessiz veri kaybı). Aktivite günlüğü hiç yazılmıyor.
- Önem: **Kritik** | Etiket: [KOD]
- Çözüm: Servisi gerçek alanlara (`activity_type`, `details` JSON) bağla; `rollback()`'i kaldır (log yazımı çağıranın transaction'ına dokunmasın, gerekirse `begin_nested()`); çağrıları commit'ten sonra yap.
- Efor: S (2-3 sa) | Doğrulama: PUT ile başlık+durum değiştir → DB'de kalıcılık ve `task_activity` satırı; birim test.

## D-002 — `ProjectFile` modeli ile kod arasında 9 alanlık uyumsuzluk (dosya yükleme/listeleme/klonlama çalışmıyor)
- Yer: `api/routes_files.py:84-88, 190-215, 290-296, 370`; `services/project_cloning.py:180-195`; model `app/models/portfolio_project.py:360-369` (id, project_id, uploader_id, filename, file_path, file_type, created_at).
- Kanıt: Kod `file_name, user_id, file_size, description, version, parent_file_id, is_active, scope, category` kullanıyor; hiçbiri modelde/DB'de yok (DB tablosu modelle birebir). GET `/projeler/<id>/dosyalar` `filter_by(is_active=True)` → `InvalidRequestError` → 500; POST dosyayı diske yazıyor (`file.save`) sonra `ProjectFile(...)` ctor'unda patlıyor → sahipsiz dosya. `api_dokuman_merkezi` yalnız 501'e çevrilmiş (çalışma ağacında); `api_proje_dosyalar` ve `clone_project` düzeltilmemiş.
- Etki: Proje dosya modülü tamamen kırık; disk şişmesi (orphan upload).
- Önem: **Yüksek** | Etiket: [KOD][DB]
- Çözüm: Ya modeli+migration ile genişlet (version/parent/is_active/scope...), ya uçları mevcut alanlara (`filename`, `uploader_id`) bağla; önce DB kaydı sonra dosya yaz (hata olursa sil).
- Efor: M (1 gün) | Doğrulama: yükle/listele/klonla e2e; `static/uploads` orphan taraması.

## D-003 — `ProjectRisk`: olmayan alanlar + String kolonlarda sayısal çarpma
- Yer: `api/routes_projects.py:899, 904-913, 999-1006`; `services/project_cloning.py:166-175`; `services/executive_dashboard.py:233-234`; model `portfolio_project.py:371-381`.
- Kanıt: Kod `created_by_id`, `created_by` (ilişki), `mitigation_plan`, `ProjectRisk.project` kullanıyor — modelde yok. Ayrıca `impact`/`probability` `String(20)` ('Low/Medium/High') iken kod `int(...)` yazıyor ve `r.impact * r.probability` ile sıralıyor (str×str → TypeError).
- Etki: Risk listesi/ekleme/klonlama/yönetici panosundaki risk skoru 500 veya boş. (`project_risk` yerel DB'de 0 satır — özellik hiç kullanılmamış.)
- Önem: **Yüksek** | Etiket: [KOD]
- Çözüm: Modeli Integer 1-5 + `created_by_id` FK + `mitigation_plan` ile yeniden tanımla, migration yaz; veya uçları kaldır.
- Efor: M | Doğrulama: risk CRUD + yönetici panosu testi.

## D-004 — `Project(template_id=...)` olmayan alan: proje klonlama çalışmaz
- Yer: `services/project_cloning.py:49` (+ D-002/D-003 alanları); çağrı `api/routes_projects.py:1231`.
- Kanıt: `Project` modelinde `template_id` yok (AST taraması).
- Etki: "Projeyi kopyala" her çağrıda hata.
- Önem: Orta | Etiket: [KOD]
- Çözüm: `template_id` argümanını kaldır; D-002/003 ile birlikte düzelt.
- Efor: S | Doğrulama: klon ucu testi.

## D-005 — Görev bildirim servisi ölü tabloya yazıyor (`notification` → boş `"user"` tablosu)
- Yer: `services/notification_service.py:3` (`from app.models.legacy_bridge import Notification, User`), `:40-62, 123-150`; `app/models/user_legacy.py` (`User = LegacyUser`, `Notification = LegacyNotification`); `models/user.py:243-258`.
- Kanıt [DB]: `"user"` 0 satır, `notification` 0 satır; `notification.user_id` FK → `"user"(id)`; gerçek kullanıcılar `users` (461), bildirimler `notifications` (71.520). Servis `User.query.get(core_user_id)` → None ("if not task or not assigned_by: return None") ya da FK ihlali; hepsi `except`→`rollback`→None ile sessiz.
- Etki: Görev atama/yorum/durum/gecikme/kritik risk bildirimleri ve e-postaları hiç üretilmiyor; ayrıca `rollback()` çağıran isteğin bekleyen değişikliklerini siler (D-001 ile aynı sınıf).
- Önem: **Yüksek** | Etiket: [KOD][DB]
- Çözüm: Servisi `app.models.core.Notification` (title/message/notification_type/tenant_id) ve `core.User`'a taşı; `rollback()` çağırma. Legacy `user`/`notification` tablolarını kaldırma planına al.
- Efor: M | Doğrulama: görev ata → `notifications`'ta satır + e-posta.

## D-006 — Görev hatırlatma, faaliyet hatırlatma ve bildirim zamanlayıcıları hiç başlatılmıyor
- Yer: `services/task_reminder_scheduler.py:78 (init_scheduler)`, `services/process_activity_scheduler.py:116 (init_process_activity_scheduler)`, `services/background_tasks.py:108,189 (init_notification_scheduler / init_background_executor)`; yalnız `app.py:48-51` kapatma (shutdown) çağırıyor.
- Kanıt: Repo genelinde grep: bu `init_*` fonksiyonlarının tanım dışında çağrısı yok. `app/__init__.py:638-647` yalnız k_radar, early_warning, digest, yedekleme, demo sweeper'ı başlatıyor.
- Etki: `Task.reminder_date` hatırlatmaları, faaliyet hatırlatma/otomatik tamamlama bildirimleri, deadline/overdue kontrolleri hiç çalışmıyor (UI hatırlatma kaydetmeyi kabul ediyor). Çalıştırılsalar bile: `task_reminder_scheduler.py:44` `datetime.utcnow()` ile karşılaştırıyor ama `reminder_date` istemciden yerel (İstanbul) duvar saati olarak geliyor (`routes_projects.py:491,606`) → 3 saat kayma.
- Önem: **Yüksek** | Etiket: [KOD]
- Çözüm: `_start_schedulers()` içine ekle (lider kilidi altında), saat dilimini `Europe/Istanbul` yap; D-005 düzeltilmeden açma.
- Efor: S-M | Doğrulama: lider logunda job listesi; hatırlatma e2e.

## D-007 — `RouteRegistry(url_pattern=...)`: bileşen senkronizasyonu her seferinde 500
- Yer: `micro/modules/admin/routes.py:1466`; model `app/models/saas.py:12-15` (alan adı `url_rule`, NOT NULL).
- Kanıt [DB]: `route_registry` tablosu boş (0 satır) → senkronizasyon her zaman "yeni endpoint" bulur ve ctor `TypeError` verir.
- Etki: Admin > Bileşen senkronizasyonu hiç çalışmıyor; route_registry boş kalıyor.
- Önem: Orta | Etiket: [KOD][DB]
- Çözüm: `url_pattern=` → `url_rule=`.
- Efor: XS | Doğrulama: POST `/admin/components/sync` → N satır.

## D-008 — K-Radar zamanlama ucu: proxy nesnesi, lider olmayan worker'da ikinci zamanlayıcı, TZ'siz
- Yer: `micro/modules/k_radar/routes_common.py:76-77`; `services/k_radar_scheduler_service.py:120-142`.
- Kanıt: `apply_schedule(current_app)` — `current_app` bir `LocalProxy`; job iş parçacığında `app.app_context()` çağrılınca istek bağlamı dışında `RuntimeError`. İstek hangi worker'a düşerse onun global `_scheduler`'ı oluşturulur → lider olmayan süreçte ikinci scheduler; lider eski ayarla sürer. `BackgroundScheduler()` timezone verilmemiş (diğerleri `Europe/Istanbul`): UTC sunucuda "08:30" = 11:30 TR. Ayar dosyası `instance/k_radar_schedule.json` container içinde (deploy'da kaybolur).
- Etki: UI'dan saat değiştirince özet ya hiç çalışmaz ya çift çalışır; ayar yeniden deploy'da kaybolur.
- Önem: Orta | Etiket: [KOD]
- Çözüm: `current_app._get_current_object()`; ayarı DB'ye (system_setting) taşı ve lider süreç periyodik okusun; timezone ver.
- Efor: M | Doğrulama: UI'da saat değiştir, lider logunda job tetiklenmesi.

## D-009 — Erken uyarı işi: tek commit, yutulan DB hatası, tekrar bildirim, tenant_id yok
- Yer: `app/services/early_warning_service.py:42-216` (özellikle `:77, :175, :198-206`, `_send_notification :22-37`); zamanlayıcı `app/__init__.py:738-757`.
- Kanıt: (1) `db.session.commit()` tüm tenantlar bittikten sonra tek sefer; dış `try`'a düşen herhangi bir hata → `rollback` tüm tenant bildirimlerini siler. (2) KPI döngüsü içi `except Exception` DB hatasını yutuyor (rollback yok) → PostgreSQL işlemi "aborted" kalır, sonraki sorgular `InFailedSqlTransaction` (memory: tenant clone dersi). (3) Aynı gün tekrar-üretim koruması yok (k_radar'daki `_already_sent_today` benzeri yok); lider her PG için ayrı bildirim alır. (4) `Notification(...)` `tenant_id` set edilmiyor. (5) `downtrend` hedefin üstünde bile tek düşüşte "kritik" sayıyor. (6) Job'da `misfire_grace_time/coalesce` yok.
- Etki [DB]: `pg_performance_deviation` 11.584 bildirim (07-08→09-07), hepsi `tenant_id IS NULL`; aynı kullanıcı+başlık+mesaj+gün tekrar grubu 9.345 (tüm tipler).
- Önem: Orta | Etiket: [KOD][DB]
- Çözüm: Tenant başına `try/commit/rollback` (veya `begin_nested`); gün-bazlı tekilleştirme; `tenant_id` yaz; trend mantığını netleştir.
- Efor: M | Doğrulama: iki kez çalıştır → bildirim sayısı artmamalı; bozuk tenant diğerlerini etkilememeli.

## D-010 — Bildirim tablosu sınırsız büyüyor, okunmamış %98,6, bileşik indeks yok
- Yer: `app/models/core.py:284-306`; üreticiler `services/k_radar_scheduler_service.py:84-100`, D-009.
- Kanıt [DB]: `notifications` 71.520 satır; 70.548 okunmamış; `k_radar_daily_digest` tek başına 58.340 satır (2026-04-02→10-05); indeksler yalnız `tenant_id`, `user_id`. `get_unread_count` her WebSocket bağlantısında çalışır.
- Etki: Rozet sayısı anlamsız; zamanla sorgu yavaşlaması ve disk.
- Önem: Orta | Etiket: [DB]
- Çözüm: Retention işi (örn. 90 gün), `(user_id, is_read, created_at)` bileşik indeks, özet tipi bildirimleri tek satıra upsert.
- Efor: S | Doğrulama: EXPLAIN; satır sayısı.

## D-011 — Socket.IO: `tenant_<id>` odasına kimse katılmıyor, yayınlar boşa gidiyor
- Yer: `app/socketio_events.py:42-60` (connect yalnız `user_<id>` odası), `:181 (broadcast_to_tenant)`, `:197-221 (handle_kpi_data_entered, notify_kpi_update)`.
- Kanıt: Kod tabanında `join_room(f"tenant_...")` yok (grep). `morning_summary_refresh` yayınları hiç alıcıya ulaşmıyor.
- Etki: Masaüstü canlı güncelleme özelliği çalışmıyor.
- Önem: Orta | Etiket: [KOD]
- Çözüm: `handle_connect` içinde `join_room(f"tenant_{current_user.tenant_id}")`.
- Efor: XS | Doğrulama: iki tarayıcı oturumu ile KPI girişi.

## D-012 — Socket.IO `leave_process`: üyelik/tenant kontrolü yok, başka kurum odasına sahte olay + e-posta yayını
- Yer: `app/socketio_events.py:96-112`; ayrıca `:115-131`, `:70-92`.
- Kanıt: `leave_process` `_can_access_process`/`_in_process_room` kontrolü olmadan `emit('user_left', {email,...}, room=f'process_{id}')` yapıyor; oturumlu herhangi bir kullanıcı keyfî `process_id` ile başka kurumun odasına olay gönderebilir. `user_joined/user_left/user_typing` yayınları `current_user.email` içeriyor. `data.get(...)` — `data` None/liste gelirse `AttributeError`. `kpi_data_update` istemcinin verdiği `field/value` değerini doğrulamadan yayınlıyor (rol kontrolü yok; salt-okur kullanıcı sahte KPI değeri gösterebilir).
- Etki: Cross-tenant olay enjeksiyonu (düşük şiddetli), UI sahteciliği, e-posta yayını.
- Önem: Orta | Etiket: [KOD]
- Çözüm: `leave_process`'te `_in_process_room` zorunlu; yayında e-posta yerine ad/ID; `kpi_data_update` için yazma yetkisi + tip doğrulaması; `data` şema kontrolü.
- Efor: S | Doğrulama: ikinci kurum kullanıcısıyla event testi.

## D-013 — Socket.IO çok-worker uyumsuzluğu
- Yer: `app/extensions.py:39-54` (`async_mode="threading"`, `message_queue` yok), `app/socketio_events.py:19 (active_users)`.
- Kanıt: Gunicorn N worker + kuyruk yok → odalar süreç-içi; `socketio.emit` başka worker'daki istemcilere ulaşmaz; `active_users` süreç-yerel sözlük.
- Etki: Bildirim/canlı güncelleme tutarsız; `get_active_users` eksik.
- Önem: Düşük | Etiket: [DEĞER]
- Çözüm: Redis `message_queue` veya tek worker + sticky; ya da özelliği kaldır.
- Efor: M | Doğrulama: 2 worker ile çapraz yayın testi.

## D-014 — `restore_tenant_data`: savepoint içinde tam `rollback()`, hata olsa da commit, yanıltıcı sayaç
- Yer: `services/tenant_backup_service.py:309-395` (özellikle `:343-352, :369-385`).
- Kanıt: `with db.session.begin_nested():` içinde silme hatasında `db.session.rollback()` (tüm oturumu + savepoint'i geri alır; sonraki `begin_nested` çıkışı hata verir/kısmi durum). INSERT `ON CONFLICT DO NOTHING`; silme başarısızsa eski satırlar kalır ama `count += 1` sayılır. `errors` dolsa bile `db.session.commit()` (kısmi geri yükleme kalıcı). INSERT sütun adları yedek dosyasından (`row.keys()`) SQL'e enterpolasyon yapılıyor (güvenilmeyen yedekte SQL enjeksiyonu); `tenant_id` yedeğin `meta`'sından alınıyor, çağıranın kurumuyla doğrulanmıyor. Şu an yalnız demo script'lerinden çağrılıyor (route yok).
- Etki: Kısmi/yanlış geri yükleme sessiz; ileride route'a bağlanırsa kritik.
- Önem: Orta | Etiket: [KOD]
- Çözüm: Tek dış transaction + satır başına `begin_nested`; `errors` doluysa rollback; kolon adlarını `information_schema` ile beyaz listele; tenant doğrulaması.
- Efor: M | Doğrulama: bozuk yedek ile test.

## D-015 — Yerel DB alembic sürümü repoda yok (`bi01c4e5f6a7`)
- Yer: yerel `alembic_version`; `migrations/versions/` (tek baş: `ux01a2b3c4d5`).
- Kanıt [DB]: yerelde `bi01c4e5f6a7`; bu revizyon yalnız izlenmeyen `Kalder/migrations/versions/bi01c4e5f6a7_*.py` (+ `kd01a2b3c4d5_kalder_is_core.py`) içinde. Kök zincir doğrusal ve tek baş.
- Etki: Yerelde `flask db upgrade/current` "Can't locate revision" ile kırılır; Kalder'deki `is_core/holding_source_id` kolonları kök modellerde yok (Kalder kodu kök DB'ye yazarsa uyumsuz).
- Önem: Orta | Etiket: [DB][DEĞER]
- Çözüm: Yerel DB'yi kök zincire `alembic stamp ux01a2b3c4d5` ile hizala (şema doğrulandıktan sonra), `Kalder/`'i repo dışına al.
- Efor: S | Doğrulama: `flask db current/heads`.

## D-016 — `Tag.name` global unique (tenant yok)
- Yer: `app/models/portfolio_project.py:384-388`.
- Kanıt: `Tag` tablosunda `tenant_id` yok, `name unique=True`. İki kurum aynı etiketi açamaz; etiketler kurumlar arası ortak havuz.
- Etki: Kurumlar arası çakışma/bilgi sızıntısı (etiket adları görünür).
- Önem: Orta | Etiket: [KOD]
- Çözüm: `tenant_id` + `UniqueConstraint(tenant_id, name)`; migration ile mevcut etiketleri kuruma dağıt.
- Efor: M | Doğrulama: iki kurumda aynı etiket oluşturma.

## D-017 — Sert silme + ORM `delete-orphan` / DB `ON DELETE CASCADE` ile soft-delete kuralı çakışıyor
- Yer: `app/models/process.py:205 (Process.kpis cascade all, delete-orphan), 447 (ProcessKpi.data_entries), 400 (kpi_data.process_kpi_id ondelete CASCADE), 488 (kpi_data_audits.kpi_data_id ondelete CASCADE), 274, 382`; hard delete çağrıları `main/routes/pages.py:511 (db.session.delete(pg), pg=ProcessKpi), :907 (faaliyet)`, `micro/modules/sp/routes_scenario.py:117 (PlanYear)`.
- Kanıt: `ProcessKpi` silinince ORM tüm `kpi_data` satırlarını, onlarla birlikte `kpi_data_audits` denetim izini de siler (DB CASCADE ile). Legacy `main_bp` uçları kayıtlı (legacy_sunset yalnız GET HTML'i yönlendiriyor).
- Etki: Tek istekle geri dönüşsüz KPI geçmişi + denetim izi kaybı; KURALLAR §3 "hard delete yasak" ihlali.
- Önem: **Yüksek** | Etiket: [KOD][DEĞER]
- Çözüm: Bu uçları `is_active=False`'a çevir; `kpi_data_audits` FK'sini `RESTRICT`/`SET NULL` yap; modellerde `delete-orphan`'ı `save-update, merge`'e indir.
- Efor: M | Doğrulama: DELETE çağrısı sonrası `kpi_data` sayısı değişmemeli.

## D-018 — 47 FK kolonunda indeks yok (PostgreSQL FK'yı otomatik indekslemez)
- Yer: örnekler: `task.assignee_id/reporter_id`, `task_comment.task_id/user_id`, `task_mention.*`, `task_subtask.task_id`, `time_entry.task_id/user_id`, `task_activity.task_id/user_id`, `project_file.project_id/uploader_id`, `project_risk.project_id`, `sprint.project_id`, `processes.source_process_id`, `process_kpis.source_kpi_id`, `process_activities.source_activity_id`, `kpi_data_audits.user_id`, `initiatives.sub_strategy_id/owner_user_id`, `esg_metric_values.metric_id`, `notifications.related_user_id`, `llm_usage_logs.user_id`.
- Kanıt [DB]: `pg_indexes` `task` için yalnız `parent_id, process_kpi_id, project_id`; `project_file` yalnız PK. Tam liste AST ile üretildi (47 kolon).
- Etki: Üst kayıt silme/cascade ve ilişki yüklemeleri büyük tabloda tam tarama.
- Önem: Orta | Etiket: [KOD][DB]
- Çözüm: Tek migration'da `index=True` + `CREATE INDEX CONCURRENTLY`; öncelik: `task`, `task_comment`, `kpi_data_audits.user_id`.
- Efor: S-M | Doğrulama: EXPLAIN, `pg_stat_user_indexes`.

## D-019 — İki tabloda `tenant_id` FK'sız; kod alanlarında tenant kapsamlı unique yok
- Yer: `app/models/plan_year.py:338 (plan_year_seal_audits.tenant_id)`, `app/models/replan_trigger.py:87 (replan_trigger_events.tenant_id)` — `nullable=False, index=True` ama `ForeignKey` yok. Kod alanları: `strategies.code`, `sub_strategies.code`, `processes.code`, `process_kpis.code`, `individual_performance_indicators.code`, `initiatives.code`, `esg_metrics.code` için unique/UniqueConstraint yok.
- Kanıt [DB]: `processes` içinde 113 `(tenant_id, code)` tekrar grubu (örn. tenant 27 `SR1`×7 — plan yılı klonları nedeniyle beklenir, ancak `(tenant, plan_year, code)` koruması da yok); `strategies` 70 grup.
- Etki: Kurum silindiğinde yetim denetim kayıtları; aynı yılda mükerrer kod girilebilir.
- Önem: Düşük | Etiket: [KOD][DB]
- Çözüm: FK ekle; `UniqueConstraint(tenant_id, plan_year_id, code)` (önce veri temizliği).
- Efor: M | Doğrulama: duplicate sorgusu 0.

## D-020 — Zaman dilimi karışımı: aware varsayılanlar naive `DateTime` kolonlarında; 25 `utcnow()` + 43 `datetime.now()`
- Yer: modellerde `default=lambda: datetime.now(timezone.utc)` (207 kullanım) ama sütunlar `db.DateTime` (timezone=True yalnız 1 yerde); karşılaştırmalar `services/k_radar_scheduler_service.py:73-85` (`date.today()` yerel × `created_at` UTC kaynaklı), `services/task_reminder_scheduler.py:44` (D-006), `services/timesheet_service.py`, `services/digest_service.py`, `app/services/llm_quota_service.py:66,233` (`datetime.now()` bilinçli yerel), `app/services/automated_reporting_service.py`.
- Kanıt: "bugün" kontrolleri sunucu TZ'sine (container UTC) bağlı; İstanbul gün sınırında (00:00-03:00) tekrar/kaçırma.
- Etki: Gün sınırı kaymaları, 3 saatlik hatalar.
- Önem: Düşük | Etiket: [KOD][DEĞER]
- Çözüm: Tek kural: DB'de UTC naive, iş günü `Europe/Istanbul` helper'ı; zamanlayıcıları aynı TZ'ye bağla.
- Efor: M-L | Doğrulama: TZ=UTC ile gün-sınırı testi.

## D-021 — `TimeEntry` servisi modelde olmayan alanları kullanıyor (ölü modül)
- Yer: `services/timesheet_service.py:25-40, 70, 137-139`; model `portfolio_project.py:397-404` (`duration_minutes`, `date`; `start_time/end_time` yok).
- Kanıt: AST taraması: `TimeEntry.start_time`, `filter_by(end_time=...)`, ctor `start_time=`. Servisin dışarıdan çağrısı yok.
- Etki: Zaman takibi çalışmaz; ileride bağlanırsa 500.
- Önem: Düşük | Etiket: [KOD]
- Çözüm: Modele `started_at/ended_at` ekle ya da servisi sil.
- Efor: S | Doğrulama: birim test / dosya silme.

## D-022 — `PlanYear.filter_by(is_active=True)`: modelde `is_active` yok (durum `status`)
- Yer: `micro/modules/sp/helpers.py:210`.
- Kanıt: `PlanYear` alanları `status` (draft/active/...); `is_active` yok → `InvalidRequestError`, `except` yutuyor, vizyon metni her zaman varsayılan "Vizyon".
- Etki: SP akış/ağaç görünümünde kurum vizyonu hiç gösterilmez.
- Önem: Düşük | Etiket: [KOD]
- Çözüm: `status="active"` kullan (ya da `plan_year_service` aktif-yıl yardımcısı).
- Efor: XS | Doğrulama: vizyon dolu tenant ile sayfa.

## D-023 — Yutulan DB hataları sonrası oturum "aborted" (transaction dersi)
- Yer: `app/services/early_warning_service.py:77,175` (D-009); `services/notification_service.py:296,521`; `services/project_service.py:224`; `app/services/process_performance_service.py:147`; `services/ai_advisor_service.py:252`; `app/services/plan_year_service.py:453`; `app/services/kilavuz_olusturucu_executor.py:921,930`.
- Kanıt: AST taraması: `try` gövdesinde sorgu/commit var, `except` blokta `rollback()` ve `raise` yok. PostgreSQL'de hata sonrası aynı transaction'da sonraki sorgular `InFailedSqlTransaction` verir; sonraki `commit()` sessiz rollback'e döner (memory: tenant clone dersi). Özellikle `project_service.py:224` PG-veri yazımında `continue` ile devam ediyor.
- Etki: Kısmen işlenmiş toplu işler, kaybolan bildirim/veri.
- Önem: Orta | Etiket: [KOD]
- Çözüm: Döngü içi iş birimini `with db.session.begin_nested():` ile sar; hata dalında `rollback()`.
- Efor: M | Doğrulama: kasıtlı kısıt ihlali ile test.

## D-024 — Bozuk Celery modülü (`app/tasks.py`): uygulama bağlamı yok, hiçbir yerde kullanılmıyor
- Yer: `app/tasks.py:1-106`; `requirements.txt:47` (celery).
- Kanıt: `User.query...` görevleri `app_context` olmadan; `celery.conf` Flask'a bağlı değil; `app.tasks` içe aktaran/worker başlatan kod, compose/servis dosyası yok (grep). `User.query...distinct()` pasif kurumları da kapsıyor; `monitor_anomalies` KPI başına lider sayısı kadar uyarı.
- Etki: Ölü kod; etkinleştirilirse `RuntimeError: Working outside of application context`.
- Önem: Düşük | Etiket: [KOD]
- Çözüm: Sil veya `ContextTask` ile bağla; bağımlılığı kaldır.
- Efor: S | Doğrulama: grep + import testi.

## D-025 — Zamanlayıcı mimarisi: işler ayrı `BackgroundScheduler`'larda, misfire/coalesce tutarsız
- Yer: `app/__init__.py:681-757`; `services/k_radar_scheduler_service.py:122`, `services/task_reminder_scheduler.py:81`, `services/process_activity_scheduler.py`.
- Kanıt: 4+ ayrı scheduler örneği; `early_warning_nightly` ve `yedekleme_nightly` aynı 02:00; yalnız yedekte `misfire_grace_time/coalesce`; ikisi timezone'suz. Lider kilidi (`scheduler_leader.py`) doğru uygulanmış.
- Etki: Restart anında kaçan işler, 02:00 DB yük çakışması.
- Önem: Düşük | Etiket: [KOD]
- Çözüm: Tek `BackgroundScheduler(timezone=...)`, ortak `job_defaults` (`misfire_grace_time=3600, coalesce=True`), early_warning 02:30'a kaydır.
- Efor: S | Doğrulama: job listesi.

## D-026 — `KpiData` için dönem-yuvası unique kısıtı yok
- Yer: `app/models/process.py:397-460` (yalnız `idx_kpi_data_lookup` indeksi).
- Kanıt [DB]: 366.668 aktif satırda `(process_kpi_id, data_date, period_type, period_no)` için 103.198 tekrar grubu (159.007 fazla satır; 1000000+ id'li sentetik/yük verisi, farklı `actual_value`). Çift tıklama/yarışta aynı dönem için ikinci kayıt oluşabilir.
- Etki: Skor motoru hangi satırı okuyacağını belirsiz seçer; çift sayım riski.
- Önem: Orta | Etiket: [DB][DEĞER]
- Çözüm: Kısmi unique indeks `WHERE is_active` (veri temizliği sonrası) veya upsert.
- Efor: M | Doğrulama: duplicate sorgusu 0, çift POST testi.

## D-027 — `users.email` global unique + soft delete; `tenant_id` boş kullanıcı
- Yer: `app/models/core.py:120`; [DB] `users.tenant_id IS NULL` 1 satır; `Notification.tenant_id` nullable.
- Kanıt: Soft-delete (`is_active=False`) edilen kullanıcının e-postası yeniden kullanılamaz; tenant'sız kullanıcı `TenantScopedMixin` süzgecini (enforce modunda) atlar.
- Etki: Yeniden davet/kayıt çakışması; izolasyon boşluğu (küçük).
- Önem: Düşük | Etiket: [KOD][DB]
- Çözüm: Kısmi unique `(lower(email)) WHERE is_active`; tenant'sız kullanıcıyı platform-admin olarak doğrula.
- Efor: S | Doğrulama: pasif kullanıcı e-postasıyla yeni kayıt.

## D-028 — Webhook servisi taslak; etkinleştirilirse SSRF/senkron risk
- Yer: `app/services/webhook_service.py:44-96, 135-160, 180`; `services/webhook_service.py:48`.
- Kanıt: `get_active_webhooks` `[]` döner, `log_delivery` içindeki commit yorum satırı; teslim kaydı yok. Etkinleştirildiğinde `requests.post(url)` URL doğrulaması (özel IP/metadata) olmadan ve istek içinde senkron (10 sn).
- Etki: Bugün sıfır (ölü); özelliği açarken SSRF.
- Önem: Düşük | Etiket: [KOD]
- Çözüm: Açmadan önce URL allow/deny listesi, kuyruk, teslim logu.
- Efor: M | Doğrulama: özel IP hedefi reddedilmeli.

---

### Doğrulanan temiz alanlar (kapsam içi, bulgu çıkmadı)
- Alembic zinciri: tek baş (`ux01a2b3c4d5`), kopuk/çift baş yok; `_disabled` zincire girmiyor.
- Model ↔ yerel DB şeması (`inspect`, `metadata.sorted_tables`): eksik tablo/kolon, DB-only kolon veya NULL-ability sapması **yok**.
- `scheduler_leader`: PG advisory lock ile tek-lider mantığı doğru.
- `tenant_clone_service`: tek transaction + hata dalında rollback doğru.
- Socket.IO: `join_process`, `get_active_users`, `typing`, `mark_notification_read` yetki kontrolü yapıyor (GUV-16); `kpi_data_entered` tenant'ı istemciden değil oturumdan alıyor.
- Tarama sınırı: AST taraması `Model.alan` ve ctor/`filter_by` anahtarlarını kapsar; `User` adı hem `core.User` hem legacy `LegacyUser` olarak kullanıldığı için `User.*` sonuçları (api/routes_admin.py, main/routes/projects.py) yanlış-pozitif sayılıp elendi.
