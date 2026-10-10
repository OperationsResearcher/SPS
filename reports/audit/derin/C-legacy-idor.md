# ALAN C — Legacy yüzeyde kiracı izolasyonu (IDOR) taraması

Tarih: 2026-10-10 · Kip: SALT OKUNUR (kod okuma; sunucu/DB erişimi yok) · Dal: `claude/duzeltme-faz1-dogruluk` (çalışma ağacı, commit edilmemiş değişiklikler dahil)
Kapsam: `api/*.py` (6 route dosyası + helpers), `main/routes/*.py`, `app/routes/*.py`, `app/api/**`. Tarama ~200 route.

## 1. Özet

| Metrik | Sayı |
|---|---|
| Taranan route | ~200 (api 88, main 48, app/routes 29, app/api 37) |
| `@login_required`'sız route | 12 (login/sso/reset/offline/index — kasıtlı genel) |
| Doğrulanmış IDOR (kod yolu izlendi, kiracı sınırı aşılıyor) | **4** (C-001 … C-004) |
| Doğrulanmış yan bulgu (IDOR değil, kiracı/yetki sınırı) | **3** (C-005 … C-007) |
| IDOR adayı (düşük etki / dolaylı / DB doğrulaması gerek) | 10 (bölüm 5) |
| Mass-assignment (request.json → setattr / `**data`) | **0** — yalnız `app/routes/admin.py:403,473` sabit beyaz listeli döngü |
| Kod yolu izlenip TEMİZ çıkan uç | 24+ (bölüm 4) |

Genel hüküm: Legacy yüzeyin büyük kısmı önceki turlarda sertleştirilmiş (`kurum_id != current_user.kurum_id` + `project_id` eşleşmesi desenleri yaygın; `dokuman-merkezi` uçları 501 ile kapalı; `app/api/routes.py` KPI uçları tenant JOIN filtreli). Kalan açıkların ortak deseni: **gövdedeki ikincil ID'ler** (atanan kullanıcı, PG id, alt strateji id) doğrulanmıyor; URL'deki ana nesne (`project_id`) doğrulanıyor. Guard bu ikincil nesne türlerini kapsamıyor (bölüm 3), bu yüzden bulgular guard "enforce" iken de sömürülebilir.

## 2. Doğrulanmış IDOR listesi

### C-001 — Görev "etki" (TaskImpact) ile başka kiracının bireysel PG'sine veri yazma — YÜKSEK
- Dosya:satır: `api/routes_projects.py:647-657` (impacts yazımı) → `services/project_service.py:79,136-170` (tüketim)
- Kanıt: `PUT /api/projeler/<pid>/gorevler/<tid>` gövdesindeki `impacts[].related_pg_id` doğrulanmadan `TaskImpact`'e yazılır. Görev "Tamamlandı"ya çekilince `handle_task_completion`, `BireyselPerformansGostergesi.query.get(impact.related_pg_id)` ile PG'yi (kiracı filtresi YOK) yükler ve `PerformansGostergeVeri(bireysel_pg_id=…, user_id=bireysel_pg.user_id, gerceklesen_deger=impact_value)` ekler. Model→kiracı: `IndividualPerformanceIndicator.user_id → users.tenant_id`; modelde `tenant_id` yok, `TenantScopedMixin` taşımıyor (guard dışı).
- Etki: Herhangi bir kiracının üyesi, ardışık PG id'leriyle başka kurumun bireysel KPI verisini bozar/üretir; skor motoru ve karne yanlış hesaplanır. Yazma kör (yanıt sızıntısı yok) ama bütünlük kaybı.
- Önem: Yüksek (cross-tenant yazma).
- Çözüm: Impact kaydederken `related_pg_id` ve `related_faaliyet_id`'yi, PG sahibinin `tenant_id == project.tenant_id` olduğunu doğrulayarak kabul et; `handle_task_completion` içinde `bireysel_pg.user.tenant_id == task.project.tenant_id` şartı ekle (savunma derinliği).
- Efor: S (1-2 saat + test).
- Doğrulama testi: A kiracısı kullanıcısı, B kiracısına ait bir `individual_performance_indicators.id` ile `impacts:[{related_pg_id:<B_pg>, impact_value:"99"}]` gönderip görevi "Tamamlandı"ya çeker. Beklenen: 400/403 ve B tarafında yeni `PerformansGostergeVeri` satırı YOK.

### C-002 — Görev atamasında yabancı kiracı kullanıcısı: ad sızıntısı + görev başlığı sızıntısı + bildirim/e-posta enjeksiyonu — YÜKSEK
- Dosya:satır: oluşturma `api/routes_projects.py:472-515`; güncelleme `api/routes_projects.py:626-642`; sızıntı yolları `api/routes_projects.py:339-372` (görev listesi), `api/routes_projects.py:1253-1272` + `services/resource_planning.py:178-214`; bildirim `services/notification_service.py:33-64`.
- Kanıt: `assigned_to_id` (POST/PUT) yalnız `int()`'e çevrilir; atananın kurumu kontrol edilmez.
  1. `GET …/gorevler` yanıtı `assigned_to.first_name/last_name` döndürür → herhangi bir `users.id` için ad-soyad numaralandırma.
  2. `GET …/gorevler/<tid>/asiri-yukleme-kontrol`, `check_task_overload(task_id, task.assigned_to_id, due_date)` çağırır; `Task.query.filter(assigned_to_id==X, status!='Tamamlandı', due_date aralığı)` proje/kiracı filtresi OLMADAN çalışır ve yanıtta `conflicting_tasks:[{id,title,due_date}]` döner. Saldırgan yabancı kullanıcıya görev atayıp `due_date`'i kaydırarak o kullanıcının başka kurumdaki görev başlıklarını okur. `Task` guard dışı (tenant_id yok).
  3. `create_task_assigned_notification` yabancı kullanıcıya bildirim + `send_task_assigned_email` e-postası üretir; içerik saldırgan kontrollü görev başlığı (kimlik avı/spam).
- Etki: Cross-tenant okuma (ad, görev başlıkları) + yabancı kullanıcıya e-posta gönderimi. Kullanıcı id'leri ardışık, toplu tarama mümkün.
- Önem: Yüksek.
- Çözüm: Atama (POST/PUT) sırasında `CoreUser` için `tenant_id == project.tenant_id` zorunlu; `check_task_overload` içinde `Task` ⨝ `Project` kiracı süzgeci; aynı doğrulama `routes_pm.py:324,380` (`owner_id`) ve `:568,749` (`user_id`) için.
- Efor: S-M.
- Doğrulama testi: A kullanıcısı kendi görevine `assigned_to_id=<B kullanıcı id>` yazar. Beklenen: 400. Mevcut davranışta `GET gorevler` yanıtında B kullanıcısının adı görünür.

### C-003 — Süreç PG güncellemede `alt_strateji_id` doğrulanmıyor → yabancı kiracının strateji adı okuma — ORTA
- Dosya:satır: yazma `main/routes/pages.py:451-455` (add yolunda `:218-229` doğrulama VAR, update yolunda YOK); okuma `main/routes/pages.py:311,344-347`.
- Kanıt: `surec_performans_gostergesi_update`, `pg.alt_strateji_id = int(data[...])` doğrudan atar. `surec_performans_gostergesi_get`, `joinedload(SurecPerformansGostergesi.alt_strateji).joinedload(AltStrateji.ana_strateji)` ile `pg.alt_strateji.ad` ve `…ana_strateji.ad` döndürür. `AltStrateji`/`AnaStrateji` legacy modeller, `TenantScopedMixin` yok; ilişki yüklemeleri (`is_relationship_load`) guard'dan zaten muaf.
- Etki: Yazma yetkili rol (kurum_yoneticisi/ust_yonetim/admin), başka kurumun alt/ana strateji adlarını id taramasıyla okur.
- Önem: Orta (okuma, yönetici rol şartı, yalnız strateji başlıkları).
- Çözüm: Update yolunda da `alt_strateji ∈ surec.alt_stratejiler` (add'deki gibi) veya `AltStrateji.ana_strateji.has(kurum_id=surec.kurum_id)`.
- Efor: XS.
- Doğrulama testi: A kurum yöneticisi, kendi sürecinin PG'sine `alt_strateji_id=<B alt strateji>` yollar. Beklenen: 400; ardından GET yanıtında B adı görünmemeli.

### C-004 — `GET /api/kurum/<kurum_id>/alt-stratejiler?surec_id=` yabancı sürecin alt stratejilerini döndürür (guard'a bağımlı) — ORTA (guard açıkken DÜŞÜK)
- Dosya:satır: `api/routes_admin.py:171-214` (özellikle `:187-210`)
- Kanıt: `kurum_id != current_user.tenant_id` kontrolü yalnız yol parametresini doğrular; `surec_id` sorgu parametresiyle `Surec.query.filter_by(id=surec_id, silindi=False).first()` kurum eşleşmesi olmadan yüklenir ve `surec.alt_stratejiler` döndürülür.
- Etki: `Surec`=`Process` `TenantScopedMixin` taşıdığı için `TENANT_GUARD_MODE=enforce` iken sorgu otomatik süzülür (sonuç boş döner). Guard `off`, bypass, `sistem_rol=='admin'` veya fail-open durumunda açık sızıntı. Elle kontrol eksik olduğundan "guard'a muhtaç" sınıfında.
- Önem: Orta (savunma tek katmana bağlı).
- Çözüm: `filter_by(id=surec_id, kurum_id=kurum_id, silindi=False)`.
- Efor: XS.
- Doğrulama testi: `TENANT_GUARD_MODE=off` ile A kullanıcısı B'nin `surec_id`'sini verir. Mevcut: 200 + B stratejileri; düzeltmeden sonra boş.

### Yan bulgular (IDOR sınıfında değil; kiracı/yetki sınırı)

#### C-005 — `kurum/update-logo` + `kurum/upload-logo` ile rastgele dosya silme (path traversal) — YÜKSEK
- Dosya:satır: `api/routes_admin.py:250-265` (update-logo), `:105-163` (upload-logo, özellikle `:139-148`).
- Kanıt: Rol kontrolü yok (her giriş yapmış kullanıcı). `update-logo`, `logo_url`'i doğrulamadan `kurum.logo_url`'e yazar. `upload-logo`, eski logo `startswith('static/')` ise `os.path.exists(old_path)` → `os.remove(old_path)` yapar. `logo_url="static/../.env"` yazılıp ardından logo yüklenirse çalışma dizinine göre `static/../.env` silinir (`..` normalize edilmiyor, `startswith` yetersiz).
- Etki: Sunucuda uygulama sürecinin yazabildiği rastgele dosyayı silme (config, DB dosyası vb.); ayrıca kurum logosu dış URL'ye yönlendirilebilir.
- Çözüm: Rol kontrolü (kurum_yoneticisi/admin); `logo_url` yalnız sunucunun ürettiği `/static/uploads/logos/<uuid>_*` kalıbını kabul etsin; silmeden önce `os.path.realpath` ile `static/uploads/logos` altında olduğunu doğrula. Efor: S.
- Test: Düşük yetkili kullanıcıyla `update-logo {"logo_url":"static/../instance/x"}` → 400/403; ardından upload → hedef dosya yerinde kalmalı.

#### C-006 — Kullanıcı yönetiminde rol hiyerarşisi yok (kiracı içi dikey yetki yükseltme) — ORTA
- Dosya:satır: `api/routes_admin.py:913-1000` (update), `:569-607` (delete), `:860-900` (yetki matrisi)
- Kanıt: İzinli roller `admin/kurum_yoneticisi/ust_yonetim`; hedef yalnız "aynı kurum" olmalı. `ust_yonetim` kullanıcısı aynı kurumdaki `kurum_yoneticisi`nin parolasını ve rolünü değiştirebilir veya hesabı silebilir; `admin` rolü atanamıyor ama başka hiyerarşi kontrolü yok. Not: `sistem_rol` modern `User`'da salt-okunur property (`app/models/core.py:166`); bu uçlar ise `LegacyUser` (`user` tablosu) üzerinde çalışıyor — canlıda fiilen çalışıyorsa hesap devralma mümkün (bölüm 3 ek not).
- Çözüm: Hedefin rol seviyesi ≤ çağıranın seviyesi şartı; parola/rol değişimini yalnız `kurum_yoneticisi`'ne ver. Efor: S.

#### C-007 — Proje yazma uçlarında yalnız kurum kontrolü var (kiracı içi BOLA / fonksiyon yetkisi) — ORTA
- Dosya:satır: `api/routes_projects.py:218-336` (PUT proje: lider/üye/gözlemci listeleri), `:986-1122` (risk ekle/güncelle/sil), `:1197-1250` (klonla), `api/routes_files.py:70-245, 441-498` (dosya)
- Kanıt: Bu uçlar `@project_*_required` kullanmıyor; `project.kurum_id == current_user.kurum_id` yeterli. Aynı kurumdaki sıradan `kurum_kullanici`, projeye bağı olmadan başka ekibin projesinin liderini/üyelerini değiştirebilir, risk silebilir, projeyi klonlayabilir. Kiracılar arası değil (kiracı sınırı korunuyor).
- Çözüm: Aynı uçlara `@project_manager_required` / `@project_member_required`. Efor: S.

## 3. Guard (TENANT_GUARD_MODE) kapsam analizi

Mekanizma (`app/utils/tenant_guard.py`): SQLAlchemy `do_orm_execute` + `with_loader_criteria(TenantScopedMixin, tenant_id IN allowed)`; `config.py:159` varsayılan `enforce` (TestingConfig `off`, `config.py:235`). `app/utils/tenant_scope.py`: `verify_tenant_resource` / `scope_query` **hiçbir yerde kullanılmıyor** (0 çağrı) — ölü yardımcılar; gerçek koruma yalnız guard + elle filtreler.

Guard kapsamındaki 39 model (mixin): AuditLog, BscKpiPerspective, Ticket, Strategy, Notification (modern), TenantEmailConfig, EsgMetric, Initiative, KRadarRecommendationAction, ProcessMaturity, BottleneckLog, ValueChainItem, EvmSnapshot, RiskHeatmapItem, StakeholderMap, StakeholderSurvey, A3Report, CompetitorAnalysis, KVektor×3, LLMUsageLog, LLMQuotaOverride, OkrObjective, PlanYear, **Project**, **Process**, PlanProject, ReplanTrigger(+Event), BlueOceanCanvas, VRIOResource, Swot/Tows/Pestel/Porter, TenantLLMConfig, TenantYearIdentity, UserYearAssignment.

Kapsam DIŞI (bu rapordaki bulguları belirleyen):
- `tenant_id` taşıyıp mixin'siz: `User`, `Tenant`, `PlanYearSealAudit`, `SystemSetting`; legacy `LegacyUser` (`user`), `Kurum`, `Deger/EtikKural/KalitePolitikasi`.
- Kiracıyı yalnız ebeveyn üzerinden bağlayan alt modeller (hiçbiri guard'lı değil): `Task`, `TaskImpact/Comment/Dependency`, `ProjectFile`, `ProjectRisk`, `RaidItem`, `SLA`, `CapacityPlan`, `IntegrationHook`, `RuleDefinition`, `RecurringTask`, `ProcessKpi`, `KpiData`, `ProcessActivity`, `IndividualPerformanceIndicator`, `IndividualActivity`, `IndividualKpiData`, `FavoriteKpi`, `SubStrategy`, `AnaStrateji/AltStrateji`, `Feedback`, `KullaniciYetki`. Bunlara id ile doğrudan erişen her uç (C-001, C-002, C-003) elle kontrole bağımlı.
- Mekanizma muafiyetleri: yalnız `SELECT` süzülür (UPDATE/DELETE/INSERT değil); `is_relationship_load` / `is_column_load` atlanır (joinedload zincirleriyle ebeveynden sızıntı mümkün, bkz. C-003); Core tablolar (`db.session.query(table)`, `text()`, ilişki tabloları `project_members`, `surec_liderleri`…) süzülmez; kimlik haritası (identity map) isabetinde SQL çalışmaz; `sistem_rol=='admin'` ve `tenant_id=None` kullanıcı tümüyle muaf; çözümleme hatasında **fail-open** (`except → ids=None`); request-dışı bağlam (scheduler, CLI) muaf; açık bypass (`tenant_guard_bypass`) kod tabanında yalnız `tenant_guard.py` tanımı + `raporlar/routes_faz4` notunda geçiyor.
- Tutarsızlık: legacy yüzey "sistem admini"ni bazı yerde `sistem_rol=='admin' and tenant_id==1` (`api_admin_*`, feedback), bazı yerde yalnız `sistem_rol=='admin'` (`api_surec_*`, `update-organization`, `rol-matrisi2/update`, guard) ile tanımlıyor; `tenant_scope.is_platform_admin` ise `role.name=="Admin"` kullanıyor. Roller global ve kiracı oluşturamıyor (`roles.name` unique) → şimdilik sömürülemez; ancak `sistem_rol` fallback'i (`r.lower().replace(" ","_")`) yeni bir "ADMIN" rol adının otomatik platform admini sayılmasına yol açar.
- Test boşluğu: TestingConfig'te guard `off`; pytest regresyonları guard'sız koşar (`test_tenant_guard.py` 6 test ayrı).
- Sonuç: Guard `Project`/`Process` kök nesneleri için gerçek ikinci katman; bu raporun IDOR'larının hepsi alt/ikincil nesnelerde (Task, PG, AltStrateji, User) → guard "enforce" iken de açık. Guard `off`'a düşerse C-004 ve `Surec.query.get(...)` kullanan, elle kontrolü atlanabilir uçlar da açılır.

Ek not (kimlik tablosu karışıklığı — DB'de doğrulanamadı): `api/*` ve `main/routes/pages.py` içindeki `User` / `Kurum` / `Notification` isimleri `app.models.legacy_bridge` üzerinden **legacy** `user` / `kurum` / `notification` tablolarına gider (`app/models/user_legacy.py:20`), oysa oturum ve `project_members` modern `users` tablosunu kullanır. `User.query.get(uid).kurum_id == current_user.kurum_id` kontrolleri legacy satırı ölçer; id'ler modern tabloyla örtüşmüyorsa ya fail-closed (uç çalışmaz) ya da yanlış kişiyi doğrular. Etki legacy `user` tablosunun canlıda dolu/senkron olup olmadığına bağlı: Test/Yayın'da salt-okunur `SELECT count(*) FROM "user"` ve id eşleşmesi kontrol edilmeli.

## 4. Route envanteri (özet; "OK" = kod yolu izlenip kontrol doğrulandı)

LR = `@login_required`. Guard sütunu: nesnenin modelinin mixin taşıyıp taşımadığı.

### api/routes_admin.py (19)
| Route | Metod | Dec. | ID | Yükleme | Kontrol | Guard | Hüküm |
|---|---|---|---|---|---|---|---|
| /activities | GET | LR | — | kullanıcı filtreli | evet | — | OK |
| /kurum/upload-logo | POST | LR | — | current_user.tenant | rol YOK | — | **C-005** |
| /kurum/update-logo | POST | LR | — | current_user.tenant | rol YOK, URL doğrulama YOK | — | **C-005** |
| /kurum/toggle-guide-system | POST | LR | — | current_user.tenant | rol var | — | OK |
| /kurum/<kurum_id>/alt-stratejiler | GET | LR | kurum_id, ?surec_id | Surec filter_by(id) | kurum_id var; surec_id YOK | Process ✔ | **C-004** |
| /user/layout, /user/theme | POST | LR | — | current_user | — | — | OK |
| /notifications, /count, /mark-all-read | GET/POST | LR | — | user_id filtreli | evet | ✔ | OK |
| /notifications/<id>/mark-read | POST | LR | id | get_or_404 | user_id eşleşmesi | ✔ | OK |
| /admin/users | GET | LR | — | kurum filtreli | rol+kurum | ✘ | OK |
| /admin/users/delete/<uid> | DELETE/POST | LR | uid | LegacyUser.get | kurum+rol (hiyerarşi yok) | ✘ | C-006 |
| /admin/users/<uid> | GET | LR | uid | LegacyUser.get | kurum+rol | ✘ | OK |
| /rol-matrisi, /rol-matrisi2 | GET | LR | — | kurum filtreli (admin: tümü) | rol | ✘ | OK |
| /rol-matrisi2/update | POST | LR | kullanici_id | LegacyUser.get | kurum (admin: tümü) | ✘ | OK (C-006 notu) |
| /admin/users/update/<uid> | POST | LR | uid | LegacyUser.get | kurum+rol (hiyerarşi yok) | ✘ | C-006 |
| /admin/users/add | POST | LR | — | — | kurum+rol | — | OK |

### api/routes_ai.py (13)
| Route | Kontrol | Hüküm |
|---|---|---|
| /ai/insights, /vision-score (+/recalc), /ai-coach/analyze, /dashboard/ai-advisor, /dashboard/executive, /simulation/what-if | hepsi `current_user.kurum_id` ile servis çağırıyor | OK |
| /dashboard/ai-advisor/notify | `notify_recommendation` yalnız log (no-op) | OK |
| /kurum/<kurum_id>/stratejik-profil | role_required + kurum eşleşmesi (admin hariç); cache anahtarı kurum | OK |
| /ai/stratejik-oneri, /ai/yeni-oneri, /ai/kabul-et | mock, ID yok | OK |
| /project/<pid>/simulate | get_or_404 + kurum | OK |

### api/routes_files.py (6)
| Route | Kontrol | Hüküm |
|---|---|---|
| /projeler/<pid>/dosyalar GET/POST | kurum var, proje rolü yok | C-007; `ProjectFile`'da `file_name`/`is_active`/`version` alanları yok → uç fiilen hata verir |
| /projeler/<pid>/dosyalar/<fid>/indir | kurum + `project_id` eşleşmesi | OK (A9) |
| /projeler/<pid>/dosyalar/<fid> DELETE | kurum + eşleşme + yönetici/yükleyen | OK |
| /dokuman-merkezi, /<fid>/indir, /<fid> DELETE | 501 ile kapalı | OK |

### api/routes_pm.py (27)
Tamamı `@project_observer_allowed` / `@project_member_required` (project_rbac: kurum eşleşmesi + rol). Alt kaynaklar (`raid/<id>`, `kapasite/<id>`, `integrations/<id>`, `kurallar/<id>`, `sla/<id>`, `tekrarlayan/<id>`) `filter_by(id=…, project_id=project.id)` ile yükleniyor — OK. `baseline` görevi `task.project_id != project.id` ile eliyor — OK. `portfoy/ozet` kurum filtreli — OK. Düşük: `owner_id`, `user_id`, `template_task_id`, `dependency_task_id` doğrulanmıyor (A3, A5); `sla` GET `project_id IS NULL` satırlarını da döndürür (A6).

### api/routes_process.py (4)
`uyeler`, `dagit`, `saglik-skoru`: `Surec.query.get` sonrası rol + `surec.kurum_id` kontrolü (admin hariç); `dagit` hedef kullanıcı kurumu ve `surec_pg.surec_id` eşleşmesi doğrulanıyor — OK. `/pg-veri/proje-gorevleri` mock — OK.

### api/routes_projects.py (19)
| Route | Hüküm |
|---|---|
| /projeler GET/POST | kurum filtreli; üye/lider/süreç kurum doğrulamalı — OK |
| /projeler/<pid> GET/PUT | kurum var; rol yok — C-007 |
| gorevler GET (observer), POST (member), gorevler/<tid> PUT (member), DELETE (manager) | proje rolü + `task.project_id` eşleşmesi; ancak `assigned_to_id`, `impacts`, `parent_id` doğrulanmıyor — **C-001, C-002**, A1-A2 |
| gorevler/<tid>/yorumlar GET/POST | rol + `task.project_id` eşleşmesi — OK |
| gorevler/<tid>/bagimliliklar GET/POST | rol + öncüller `project_id` filtreli — OK |
| riskler GET/POST/PUT/DELETE | kurum + `risk.project_id` eşleşmesi; rol yok — C-007 |
| ai-tahmin, kaynak-isi-haritasi, asiri-yukleme-kontrol | kurum (+`task.project_id`) var — OK; asiri-yukleme-kontrol servisi sızdırır (C-002) |
| klonla | kurum var; yeni proje kaynakla aynı kiracı — OK (rol yok, C-007) |
| /task/<tid>/complete | task→project→kurum kontrolü; `related_indicator_id` kod tabanında hiçbir yerde atanmıyor — OK/latent (A8) |

### main/routes (48) — LR; çoğu `Surec.query.get` + `sistem_rol != 'admin' and surec.kurum_id != kurum` + rol
`pages.py` süreç/PG/faaliyet uçları (`/surec/<sid>/performans-gostergesi/*`, `/surec/<sid>/faaliyet/*`, `/surec/update|get|delete/<sid>`, `/surec/add-simple`): alt nesneler `filter_by(id, surec_id)` ile yükleniyor, lider/üye/alt strateji listeleri `kurum_id` süzgeçli, `parent_id` `_validate_surec_parent_id` ile — OK. İstisna: PG update `alt_strateji_id` (**C-003**), faaliyet update `surec_pg_id` (A4). `kurum_panel.py`: `strategic-planning/graph` kurum filtreli; `/admin/seed_db`, `/admin/fix-bsc-schema` yalnız admin ama GET ile durum değiştiriyor (A7). `projects.py`: muda-hunter süreç kurum filtreli, organization uçları rol+kurum (`update-organization` admin tüm kurum — tasarım), feedback uçları kurum (kurum_id==1 admin istisnası). `strategy_api.py`: `update_cell` strateji ve süreç `kurum_id` ile süzülü, proje uçları `kurum_id` filtreli + `role_required`, `kpi/add` 410. `_common.py`: genel.

### app/routes (29)
`admin.py`: tüm uçlar `_require_admin*` / `_require_process_admin` + `tenant_id == current_user.tenant_id` (Admin hariç); `create/update-process` ebeveyn/lider/üye/alt strateji `validate_same_tenant_*` ile kiracıya bağlanıyor; ticket uçları kiracı kontrollü — OK. `auth.py` KVKK uçları yalnız `current_user` verisi — OK. `core.py kule_send` tenant=current_user — OK. `password_reset.py`, `sso.py`, `totp.py` kimlik doğrulama akışları (IDOR alanı dışı; `totp_challenge` oturumdaki pending id kullanıyor).

### app/api (37)
`routes.py` (14): süreç/KPI/KpiData uçları `Process.tenant_id == current_user.tenant_id` JOIN filtreli, `create_kpi_data` sahiplik kontrollü, `comparison` id listesi tenant süzgeçli — OK. `ai.py` (9): `_check_kpi_tenant/_check_process_tenant` — OK. `data_connector.py` (5): `tid = user.tenant_id` ile filtre — OK. `push.py` (4): kullanıcıya bağlı abonelik — OK. `process/performance_routes.py` (5): `require_process_access` + servis katmanı kurum/lider/üye kontrolü; `karne/performans` servis içinde `surec.kurum_id != user.kurum_id`; `faaliyet/<id>/takip` `faaliyet.user_id != user.id` — OK. `save_performance_data` standart kullanıcının aynı kurumdaki başka kullanıcı adına veri girmesine izin veriyor (kiracı içi, A10).

## 5. IDOR adayları (düşük etki / dolaylı / ek doğrulama gerek)

| ID | Yer | Açıklama | Önem |
|---|---|---|---|
| A1 | `api/routes_projects.py:616` | Görev `parent_id` başka proje/kiracı görevine bağlanabiliyor; ağaç sorguları `project_id` süzgeçli, okuma sızıntısı doğrulanmadı | Düşük |
| A2 | `api/routes_projects.py:652-655` | `related_faaliyet_id` aynı desen (C-001 ile birlikte düzeltilmeli) | Orta (C-001 kapsamı) |
| A3 | `api/routes_pm.py:324,380,568,749` | RAID `owner_id`, kapasite `user_id` yabancı kullanıcı id'si; yanıtlar yalnız id döndürüyor | Düşük |
| A4 | `main/routes/pages.py:868` | faaliyet `surec_pg_id` yabancı PG; `recalc_on_faaliyet_change` kurum eşleşmesiyle durduruyor, görüntüleme yolu bulunmadı | Düşük |
| A5 | `api/routes_pm.py:212,845` | `template_task_id` yabancı görev; tüketen kod bulunamadı (latent) | Düşük/Latent |
| A6 | `api/routes_pm.py:149-156` | SLA GET `project_id IS NULL` "genel" satırlar tüm kiracılara görünür; bunları oluşturan API yok | Düşük/Latent |
| A7 | `main/routes/kurum_panel.py:10,41` | `seed_db` / `fix-bsc-schema` GET ile durum değiştirir (CSRF; yalnız admin); `fix-bsc-schema` SQLite `PRAGMA` kullanıyor, PostgreSQL'de çalışmaz | Düşük |
| A8 | `api/routes_projects.py:1278-1340` | `task.related_indicator_id` ile PG verisi üretimi; atayan kod yok ama alan yazılabilir hale gelirse C-001 sınıfı | Latent |
| A9 | `api/routes_files.py:151,203`, `api/routes_admin.py:155` | Yüklenen dosyalar `/static/uploads/...` altında kimlik doğrulamasız servis ediliyor; uuid tahmin edilemez ama indirme uçlarının yetki kontrolünü baypas eder (URL liste yanıtında ifşa) | Düşük-Orta |
| A10 | `app/services/process_performance_service.py:323-334` | Standart kullanıcı kiracı içi başka kullanıcı adına PG verisi yazabilir | Düşük |

## 6. Mass-assignment

`setattr(`, `**data`, `**request.json`, `update(data)` kalıpları kapsamdaki dosyalarda yalnız `app/routes/admin.py:403,473` (tarih alanları için sabit liste) — risk yok. Alan alan elle atama yapılan uçlarda riskli alan: `api_admin_update_user` `user.sistem_rol = incoming_role` (doğrulanmamış rol dizgesi; `admin` hariç sınırsız, bkz. C-006) ve `kurum_id` (yalnız sistem admini). Şema doğrulayıcı kullanan tek uç `create_kpi_data` (`KpiDataSchema`).

## 7. Öncelikli aksiyon sırası
1. C-005 (rastgele dosya silme) — XS/S, hemen.
2. C-002 + C-001 — ortak "ikincil ID doğrulama" yardımcısı (`assert_same_tenant_user/pg`) ile birlikte kapat.
3. C-003, C-004 — tek satırlık filtre.
4. C-006 / C-007 — rol hiyerarşisi ve proje-rolü dekoratörleri.
5. Test: TestingConfig'te guard `off`; her C-0xx için guard açık ve kapalı çapraz-kiracı regresyon testi yaz. `tenant_scope.verify_tenant_resource` ölü; ya kullan ya sil.
6. DB doğrulaması (Test/Yayın, salt-okunur): legacy `user`/`kurum` tabloları dolu mu, id'ler `users`/`tenants` ile örtüşüyor mu.
