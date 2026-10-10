# Derin Kod Analizi — ALAN B: Strateji ve Raporlama Modülleri

Tarih: 2026-10-10 · Kapsam: `micro/modules/sp/`, `micro/modules/k_radar/` (+ `services/k_radar_service.py`), `micro/modules/k_rapor/`, `micro/modules/raporlar/` (faz0-5 + esg), `micro/modules/analiz/`, PDF/PPTX/Excel/CSV export kodu.
Yöntem: Salt okunur. 372 route dekoratör, tenant filtresi, rol kontrolü, sorgu şekli ve istisna yönetimi açısından otomatik taranıp şüpheliler elle okunarak doğrulandı. `02-kod-kalitesi.md` tekrarlanmadı.

Etiketler: **Kesin** = kod okunarak doğrulandı; **Olası** = kodda zemin var, ortam/çalışma zamanı bağımlı.

## Özet

| Önem | Adet |
|---|---|
| Yüksek | 9 |
| Orta | 23 |
| Düşük | 8 |
| **Toplam** | **40** (35 Kesin, 5 Olası) |

| ID | Başlık | Önem | Etiket |
|---|---|---|---|
| B-001 | Yeniden-planlama tetikleyicisi başka kurumun PG verisini okur (IDOR) | Yüksek | Kesin |
| B-002 | Kişisel veri (PII) toplu rapor/export uçlarında rol kontrolü yok | Yüksek | Kesin |
| B-003 | Denetim izi, 2FA, finans ve premium dosya raporları herkese açık | Yüksek | Kesin |
| B-004 | Mühür (K8) SP yazma uçlarında uygulanmıyor | Yüksek | Kesin |
| B-005 | Yönetici/Savaş Odası SQL'leri "azalması iyi" yönünü yok sayıyor (D0 regresyonu) | Yüksek | Kesin |
| B-006 | K-Radar KS skoru ve "genişletilmiş" metrikler sayımlardan uydurulmuş | Yüksek | Kesin |
| B-007 | Yatırımcı sunumu/yıllık kitap: yer tutucu içerik, önizleme vaadi ≠ üretim | Yüksek | Kesin |
| B-008 | Öneri onayı: doğrulanmamış metinle, proje yetkisini aşarak görev yaratıyor | Yüksek | Kesin |
| B-009 | Yazma uçlarında kurum-FK doğrulaması yok (çapraz kurum sızıntısı) | Yüksek | Kesin |
| B-010 | Süreç kapsamı (RBAC) yalnız K-Radar hub'ında var, raporlarda yok | Orta | Kesin |
| B-011 | 39 SP/rapor yazma ucunda CSRF muafiyeti | Orta | Kesin |
| B-012 | `require_module` paket kapısı k_rapor/sp/k_radar'da yok; hata durumunda açık | Orta | Kesin |
| B-013 | Excel/CSV formül enjeksiyonu (kaçış yok) | Orta | Kesin |
| B-014 | ReportLab Paragraph işaretleme enjeksiyonu | Orta | Olası |
| B-015 | `get_kp_extended_data` yıl filtresini yalnız `base`'e uyguluyor | Orta | Kesin |
| B-016 | Çapraz ısı haritası yıl-sız memoize (K2 tuzağı tekrarı) | Orta | Kesin |
| B-017 | PG puanı için üç ayrı hedef kaynağı + kopya-yapıştır bloklar | Orta | Kesin |
| B-018 | Yıl/plan-yılı filtresi eksik veya tutarsız raporlar | Orta | Kesin |
| B-019 | EVM raporu: proje adları hep "Proje #id", yıl filtresi LIMIT sonrası | Orta | Kesin |
| B-020 | Süreç×PG ısı haritası farklı birimli değerlerin ortalamasını alıyor | Orta | Kesin |
| B-021 | Özet sayaçları yanlış (veri_yok, checked, on_time, kırpma) | Orta | Kesin |
| B-022 | Sahte CPM, keyfi kaynak yükü, öneri-pozisyon eşlemesi | Düşük | Kesin |
| B-023 | Senaryo dalları: etiket doğrulaması kırık, taban DB'de benzersizlik çakışması | Orta | Kesin |
| B-024 | Toplu KPI yıllık hedefi: "rollback" etkisiz (kısmi uygulama) | Orta | Kesin |
| B-025 | Doğrulanmamış girdi → 500 | Orta | Kesin |
| B-026 | Alan atama/değer doğrulaması yok (direction, progress, status, NaN, scope) | Orta | Kesin |
| B-027 | Sınırsız yıl ile PlanYear üretimi (set-active, sihirbaz) | Orta | Kesin |
| B-028 | N+1 ve istek-başı ağır hesap | Orta | Kesin |
| B-029 | Büyük tablolarda sınırsız `.all()` | Orta | Kesin |
| B-030 | Sessiz exception yutma (skorlar boş dönüyor, log yok) | Orta | Kesin |
| B-031 | K-Radar günlük özet takvimi tek global dosya | Orta | Kesin |
| B-032 | Digest gönderiminde alıcı doğrulaması yok | Orta | Kesin |
| B-033 | Hard delete ve eksik kaskad | Düşük | Kesin |
| B-034 | `_` değişkeni gettext'i gölgeliyor | Düşük | Kesin |
| B-035 | `date.today()` (37 yer) vs `today_tr` (0 yer) | Düşük | Olası |
| B-036 | Dosya adı / ZIP giriş adı kullanıcı girdisinden | Düşük | Olası |
| B-037 | LLM isteğine ham kurum verisi, sınırsız kullanıcı metni | Düşük | Olası |
| B-038 | Ölü/çift route, kopya rol listeleri, çift çeyrek raporu | Düşük | Kesin |
| B-039 | Küçük hesap ve etiket hataları | Düşük | Kesin |
| B-040 | Platform Admin (tenant_id=None) bağlamında 500/boş sonuç | Orta | Olası |

Olası etiketli 5: B-014, B-035, B-036, B-037, B-040.

---

## B-001 · Yeniden-planlama tetikleyicisi başka kurumun PG verisini okur (IDOR)
- **Dosya:satır:** `micro/modules/sp/routes_replan_trigger.py:39-60` (create), `app/services/replan_trigger_service.py:24-47` (`_eval_kpi_below_target`), `routes_replan_trigger.py:105-117` (events).
- **Kanıt:** `target_kpi_id=data.get("target_kpi_id") or None` doğrulanmadan kaydediliyor. Değerlendirme `SELECT ... FROM kpi_data WHERE process_kpi_id=:k` — `tenant_id`/`processes` join'i yok. Olay çıktısında `last_actual` ve `last_target` döner; `/api/replan-triggers/events` bunu tenant'a gösterir.
- **Etki:** SP yönetici rolündeki bir kullanıcı KPI id'sini sayarak başka kurumun son gerçekleşen/hedef değerini okur. Ayrıca `consecutive_periods` 0/negatifse `LIMIT :n` hatası; "hedef altı" yön gözetmiyor.
- **Önem:** Yüksek · **Etiket:** Kesin
- **Çözüm:** create'te `ProcessKpi.query.join(Process).filter(ProcessKpi.id==x, Process.tenant_id==tid)` doğrulaması; servis SQL'ine `JOIN processes p ... WHERE p.tenant_id=:t`; `consecutive_periods` 1-24; `direction` dikkate alınmalı.
- **Efor:** S (1-2 sa)
- **Doğrulama testi:** İki kurum; B kurumunun KPI id'si ile A kurumunda trigger oluştur → 400; mevcut kayıt için `evaluate` olay üretmemeli.

## B-002 · Kişisel veri (PII) toplu rapor/export uçlarında rol kontrolü yok
- **Dosya:satır:** `raporlar/routes_faz3.py:949-1057` (bireysel karne ZIP, `GET|POST`), `k_rapor/routes.py:587` (`/api/individual`), `k_rapor/routes.py:1419` (`export-excel?tab=bireysel`: e-posta dahil), `k_rapor/routes.py:2309` (`responsible-analysis`), `raporlar/routes_faz5.py:118` (BI CSV), `sp/routes_pages.py:340` (`report/periodic`).
- **Kanıt:** Dekoratörler yalnız `@login_required` (+ `require_module`). ZIP: her kullanıcının ad, e-posta, departman, PG listesi. `export-excel` bireysel sekmesi tüm kullanıcıların e-postasını ve başarı %'sini yazar.
- **Etki:** En düşük yetkili kurum kullanıcısı tüm çalışanların performans ve iletişim verisini indirebilir (KVKK / rol-görünüm ilkesi). K-Radar'daki `ROL-GORUNUM` kapsamı bu uçlarda yok.
- **Önem:** Yüksek · **Etiket:** Kesin
- **Çözüm:** `PRIVILEGED_ROLES` ile tek dekoratör (`@role_required`); düşük rol için yalnız kendi satırı. İndirme uçlarını yalnız `POST`+CSRF yap.
- **Efor:** M (3-4 sa)
- **Doğrulama testi:** `standard_user` ile ZIP / `export-excel?tab=bireysel` / `api/individual` → 403; `tenant_admin` → 200.

## B-003 · Denetim izi, 2FA, finans ve premium dosya raporları herkese açık
- **Dosya:satır:** `raporlar/routes_faz3.py:758-940` (Audit Paketi PDF: kullanıcı adı, aksiyon, 2FA oranı), `k_rapor/routes.py:888` (`/api/audit`), `raporlar/routes_faz1.py:663` (2FA'sız yöneticilerin e-posta listesi), `raporlar/routes_faz2.py:43` (CFO: bütçe, LLM maliyeti), `raporlar/routes_faz3.py:384` (yatırımcı PPTX), `k_rapor/routes.py:2454` (bildirim analizi: en çok bildirim alan kullanıcılar).
- **Kanıt:** Hiçbirinde rol kontrolü yok; yalnız `faz0:660` (`executive-leadership`) ve ESG yazma uçları kontrol ediyor.
- **Etki:** "2FA'sız yönetici listesi" saldırgana hedef listesi verir; audit/finans verisi sıradan kullanıcıya açık.
- **Önem:** Yüksek · **Etiket:** Kesin
- **Çözüm:** Rapor kataloğu için rol matrisi (`REPORT_ACL`) ve tek dekoratör; 2FA listesinde e-postayı yalnız ADMIN_ROLES'a ver.
- **Efor:** M (4 sa)
- **Doğrulama testi:** Standart kullanıcı ile `/k-report/api/audit-package/generate`, `/api/audit`, `/api/two-fa`, `/api/cfo-dashboard` → 403.

## B-004 · Mühür (K8) SP yazma uçlarında uygulanmıyor
- **Dosya:satır:** `app/services/date_sovereign.py:145` (`plan_year_writable`). Kullanım yalnız `bireysel`, `surec`; `sp/` içinde yalnız bir yorum. Etkilenenler: `sp/routes_strategy.py:100-285` (strateji/alt strateji ekle-güncelle-sil), `routes_analysis.py:138,215,279,343` (Porter/SWOT/TOWS/PESTEL), OKR, `routes_initiative.py`, `routes_sp_proje.py`, `routes_pages.py:290` (kurum kimliği), `routes_exec_advisor.py:488` (şablon uygula). `routes_plan_year.py:231,366,399` yalnız `status == "closed"` bakıyor (`archived` açık kalıyor).
- **Kanıt:** `date_sovereign.py` "K8 mutlaktır: kapanmış yıla asla veri"; SP rotalarında kontrol yok (grep).
- **Etki:** Mühürlü yıla strateji, SWOT, girişim yazılabilir.
- **Önem:** Yüksek · **Etiket:** Kesin
- **Çözüm:** `plan_year_writable_required` dekoratörü (S15 kararı) SP yazma uçlarına; `closed` yerine `KAPALI_DURUMLAR`.
- **Efor:** M (4-6 sa)
- **Doğrulama testi:** Yılı mühürle → `POST /api/swot`, `/api/strategy/add`, `/api/initiatives` → `plan_year_sealed`.

## B-005 · Yönetici/Savaş Odası SQL'leri "azalması iyi" yönünü yok sayıyor (D0 regresyonu)
- **Dosya:satır:** `sp/routes_exec_advisor.py:72-125` (`exec-strategy-scores`), `:251-290` (`exec-trend`), `:478-505` (`_SUBSTRAT_SQL`, `_PROCESS_SQL`); `raporlar/routes_faz5.py:430-445` (`pi-project-impact`).
- **Kanıt:** `kd.actual_value::float >= kd.target_value::float` yön bakmadan. Ek olarak: (a) birim "veri satırı" (aylık 12 satır = 12 oy), (b) `strategies ⨝ sub_strategies ⨝ links ⨝ processes ⨝ kpis ⨝ kpi_data` fan-out'u aynı satırı birden çok alt strateji için sayar, (c) `exec-trend` yıl/plan-yılı filtresiz, (d) `pi-project-impact` `EXISTS(herhangi bir satır hedefi geçmiş)` — tüm yıllar. `k_rapor/routes.py:22-38` D0 notu aynı hatanın "iyi performansı kötü raporladığını" yazıyor.
- **Etki:** Savaş Odası/Yönetici Paneli sıralamaları yanlış; azalan göstergeler tersine.
- **Önem:** Yüksek · **Etiket:** Kesin
- **Çözüm:** SQL yerine `compute_pg_score` (tek kural) kullanan servis; KPI başına son satır ve yıllık hedef.
- **Efor:** M-L (1 gün)
- **Doğrulama testi:** Tek "Decreasing" PG (hedef 5, gerçek 2) fixture'ı: `exec-strategy-scores` %100 dönmeli (şimdi %0).

## B-006 · K-Radar KS skoru ve "genişletilmiş" metrikler sayımlardan uydurulmuş
- **Dosya:satır:** `services/k_radar_service.py:287-299` (`_ks_component`), `:397-451` (`get_ks_extended_data`); `k_radar/routes_ks.py:12-36` (`_ks_swot_summary`).
- **Kanıt:** KS skoru = `min(süreç_sayısı/strateji_sayısı*100, 100)`. `pestle.coverage_score = strateji*8 + süreç*2`, `tows.candidate_actions = strateji*2`, `ansoff.risk_balance`, `bcg.balance_score` sayım formülü. `_ks_swot_summary` tüm yılların KpiData'sını çeker, `actual/target < 0.8` ile yön gözetmeden "düşük performans" der. `get_kp_extended_data` D3 notları "uydurma yok" ilkesini koyuyor; KS'ye uygulanmamış.
- **Etki:** Hub toplam skorunun KS payı (ağırlık 2/10) gerçek dışı.
- **Önem:** Yüksek · **Etiket:** Kesin
- **Çözüm:** KS'yi gerçek SWOT/PESTEL/hizalama doluluğundan türet; hesaplanamayanı `None` + "veri yok" göster.
- **Efor:** M (1 gün)
- **Doğrulama testi:** Strateji 1, süreç 5 → KS 100 (kanıt); düzeltmeden sonra analiz boşken KS `None`.

## B-007 · Yatırımcı sunumu/yıllık kitap: yer tutucu içerik, önizleme vaadi ≠ üretim
- **Dosya:satır:** `raporlar/routes_faz3.py:524-533` (sabit "Ar-Ge ~%40, Operasyon ~%30..." ve "İletişim: investor@example.com"), `:340-367` önizleme 18 slayt vs üretilen 13; `:76-110` yıllık kitap önizleme 14 bölüm/35 sayfa vs üretilen ~7 bölüm; ESG slaytı "Scope 1+2+3 takibi, bağımsız yatırımcı raporlaması" veri olmadan yazılıyor; `:402` strateji sorgusu `plan_year_id=` eşitliği (NULL legacy dışlanıyor; diğer raporlar `or_(.. is_(None))`).
- **Etki:** Müşteri uydurma yatırım dağılımı ve örnek e-posta içeren sunumu üçüncü kişiye gönderebilir.
- **Önem:** Yüksek · **Etiket:** Kesin
- **Çözüm:** Sabit metinleri kaldır veya kullanıcı girdili alan yap; önizlemeyi üretilen bölümlerden türet; ESG/risk slaytlarını gerçek veriyle koşullu yaz.
- **Efor:** M (4 sa)
- **Doğrulama testi:** PPTX'te "example.com" ve "~%40" bulunmamalı; önizleme slayt sayısı = üretilen.

## B-008 · Öneri onayı: doğrulanmamış metinle, proje yetkisini aşarak görev yaratıyor
- **Dosya:satır:** `k_radar/routes_common.py:117-137`, `services/k_radar_service.py:950-1015`.
- **Kanıt:** `item` istemciden gelen serbest metin (öneri listesinde olup olmadığı, uzunluk kontrol edilmiyor). `approved` olunca `_create_action_task_for_recommendation` kurumun **en son güncellenen** arşivlenmemiş projesine çağıran kullanıcıyı `assignee/reporter` yaparak görev ekler; kullanıcının o projede üye olup olmadığına bakmaz. Öneri anahtarı sha1(metin): metin değişince eski kararlar sahipsiz.
- **Etki:** Yönetici rolü rastgele metni projeye görev olarak enjekte eder; proje RBAC (`accessible_projects_query`) bypass'ı.
- **Önem:** Yüksek · **Etiket:** Kesin
- **Çözüm:** `item` ∈ `get_recommendations_from_summary(...)`; hedef proje kullanıcıya açık olmalı veya sabit "K-Radar Aksiyonları" projesi; 180 karakter üstü reddet.
- **Efor:** S-M (3 sa)
- **Doğrulama testi:** `item="x"*5000` ve listede olmayan metinle POST → 400.

## B-009 · Yazma uçlarında kurum-FK doğrulaması yok (çapraz kurum sızıntısı)
- **Dosya:satır:** `sp/routes_initiative.py:39-70` (create: `strategy_id`, `sub_strategy_id`, `owner_user_id`; PATCH doğruluyor, create doğrulamıyor), `k_radar/routes_risk.py:149-163` (`project_id`, `owner_id`, `plan_year_id`, `source_id`), `k_radar/routes_kp.py:138-160, 328-352` (`ProcessMaturity.process_id`; aynı dosyada değer zinciri `_vc_proc` doğruluyor, olgunluk doğrulamıyor), `sp/routes_sp_proje.py:171` (`assignee_id`).
- **Sızıntı zinciri:** `k_rapor/routes.py:860-865` `Process.query.filter(Process.id.in_(mat_proc_ids))` tenant süzmüyor → başka kurumun süreç adı raporda; `raporlar/routes_faz2.py:101` `db.session.get(Strategy, sid)` ve `routes_faz5.py:343` `db.session.get(User, owner_user_id)` tenant süzmüyor → başka kurumun strateji başlığı/kullanıcı adı CFO ve Onay Zinciri raporlarında.
- **Etki:** ID sayarak yazma + okuma yoluyla başka kurumun süreç/strateji/kullanıcı adı sızar.
- **Önem:** Yüksek · **Etiket:** Kesin
- **Çözüm:** Tüm FK girdilerini `filter_by(id=..., tenant_id=tid)` ile doğrula (ortak `assert_owned(model, id, tid)`); okuyan raporlarda da `tenant_id` filtresi ekle.
- **Efor:** M (4 sa)
- **Doğrulama testi:** A kullanıcısı B'nin `process_id`'si ile olgunluk ekler → 400; rapor yanıtında B'nin adı görünmemeli.

## B-010 · Süreç kapsamı (RBAC) yalnız K-Radar hub'ında var
- **Dosya:satır:** `k_radar/routes_common.py:33-43` (`_scope_tuples`); kapsamsız: `k_rapor/routes.py` (tüm `/api/*`), `analiz/routes.py:21-120`, `raporlar/*`.
- **Kanıt:** Lider için hub yalnız yetkili süreçleri sayıyor; aynı kullanıcı `/k-report/api/process-pg`, `/k-radar/analysis/api/health/<pid>` ile tüm süreçleri görüyor (`analiz` yalnız `tenant_id` süzüyor).
- **Önem:** Orta · **Etiket:** Kesin
- **Çözüm:** `accessible_processes_filter` ortak sorgu yardımcısına taşı; raporlarda uygula.
- **Efor:** L (1-2 gün)
- **Doğrulama testi:** Yalnız süreç X lideri `/analysis/api/health/Y` → 403/404.

## B-011 · 39 SP/rapor yazma ucunda CSRF muafiyeti
- **Dosya:** `sp/routes_*.py` içinde 38 `@csrf.exempt` (ör. `routes_strategy.py:112,152,190`, `routes_initiative.py`, `routes_plan_year.py:152,342,386`, `routes_frameworks.py`, `routes_tenant_ai.py` — AI anahtarı kaydet/sil), `raporlar/routes_faz4.py:468`.
- **Kanıt:** `CSRFProtect` global açık; `plan-years/close` için "S14: csrf.exempt KALDIRILDI" notu var, diğerleri bırakılmış. `SESSION_COOKIE_SAMESITE` env'den değişebilir (`config.py:100`, varsayılan Strict → şu an hafifletilmiş).
- **Önem:** Orta · **Etiket:** Kesin
- **Çözüm:** Muafiyeti kaldır; frontend `X-CSRFToken` göndermeli (diğer modüller gibi).
- **Efor:** M (3-4 sa)
- **Doğrulama testi:** Token'sız `POST /k-plan/strategy/api/strategy/delete/1` → 400.

## B-012 · `require_module` paket kapısı eksik
- **Dosya:** `k_rapor/routes.py` (35 route, hiçbirinde), `sp/*` (yalnız `exec-dashboard` sayfası), `k_radar/*`; `raporlar/*` ise `@require_module("k_rapor")` kullanıyor. `app/utils/decorators.py:78-83`: kapı çözülemezse `return f(...)` (fail-open).
- **Etki:** Paket dışı kurum `/k-report/api/*` (export-excel/pdf dahil) ve `sp/api/exec-snapshot` uçlarına doğrudan erişir; `exec-dashboard` sayfası kapılı ama API'si değil.
- **Önem:** Orta · **Etiket:** Kesin
- **Çözüm:** Blueprint düzeyi `before_request` modül kapısı; fail-open'ı logla ve kapat.
- **Efor:** S-M (2-3 sa)
- **Doğrulama testi:** `k_rapor` paketi olmayan kurumla `/k-report/api/export-excel` → 403.

## B-013 · Excel/CSV formül enjeksiyonu
- **Dosya:satır:** `k_rapor/routes.py:1419-1580` (openpyxl: `=` ile başlayan string hücre formül olur), `services/period_report_service.py` (tüm hücreler), `raporlar/routes_faz5.py:118-170` (BI CSV), `k_radar/routes_common.py:156-190` (history.csv). Depoda kaçış yardımcısı yok.
- **Kanıt:** `ws.append([k.code, k.name, ...])`, `writer.writerow([... kpi_name ...])`.
- **Etki:** Süreç/PG adına `=HYPERLINK(...)` yazan kullanıcı, raporu indiren yöneticide formül çalıştırır.
- **Önem:** Orta · **Etiket:** Kesin (kodda kaçış yok; sömürü Excel ayarına bağlı)
- **Çözüm:** `safe_cell(v)`: `str` ve `v[:1] in "=+-@\t\r"` ise başına `'`; tüm export'ta kullan.
- **Efor:** S (1-2 sa)
- **Doğrulama testi:** PG adı `=1+1` ile export; hücre metin olarak görünmeli.

## B-014 · ReportLab Paragraph işaretleme enjeksiyonu
- **Dosya:satır:** `raporlar/routes_faz3.py:799,1007,1011,1012` (`P(f"<b>{uname}</b>")`, e-posta), `app/services/weekly_digest_service.py:393,665` (kurum adı, yorum). Aynı dosyada `routes_faz3.py` yıllık kitap `html.escape` yapıyor ("markup injection koruması"), diğer PDF'ler yapmıyor.
- **Etki:** Ad `<`/`&` içeriyorsa tüm ZIP/PDF 500; `<img src=...>` ile dosya/URL çekme olasılığı (sürüm bağımlı).
- **Önem:** Orta · **Etiket:** Olası
- **Çözüm:** `xml.sax.saxutils.escape` ile tüm kullanıcı metni; tek yardımcı `_P(text)`.
- **Efor:** S
- **Doğrulama testi:** Kullanıcı soyadı `A<b` ile batch ZIP → 200.

## B-015 · `get_kp_extended_data` yıl filtresini yalnız `base`'e uyguluyor
- **Dosya:satır:** `services/k_radar_service.py:470-560` (`kpi_rows_all`, `kpi_rows`, `kpi_row_counts`).
- **Kanıt:** `year` yalnız `_process_component`'e geçiyor; SLA ihlal oranı, kıyaslanabilirlik, trend (son 30/60 gün) tüm yılların `KpiData`'sını alır, pencere `date.today()`'e göre. K2 düzeltmesi (hub) burada tamamlanmamış.
- **Etki:** Yıl seçici KP alt kartlarını değiştirmez; yıllar boyunca ≈90k satır bellekte.
- **Önem:** Orta · **Etiket:** Kesin
- **Çözüm:** Tüm KpiData sorgularına `KpiData.year == year`; trend penceresini seçili yıla bağla.
- **Efor:** S-M
- **Doğrulama testi:** 2020 ve 2026 için `/k-radar/api/kp/sla` farklı dönmeli.

## B-016 · Çapraz ısı haritası yıl-sız memoize
- **Dosya:satır:** `services/k_radar_service.py:820-825` (`get_hub_summary(tenant_id, scope_process_ids, scope_project_ids)` — `year` yok), `k_radar/routes_cross.py:107` (çağrı).
- **Kanıt:** `get_hub_summary` docstring'i (satır 336-346) bu hatayı açıkça uyarıyor: yıl içeride çözülürse cache anahtarına girmez. Isı haritası tam bunu yapıyor; 5 dk boyunca ilk isteğin yılı tüm yıllara servis edilir.
- **Önem:** Orta · **Etiket:** Kesin
- **Çözüm:** `get_cross_heatmap_data(..., year)` imzası; çağrıda `year=resolve_request_year()`.
- **Efor:** S
- **Doğrulama testi:** Yıl 2020 sonrası 2026 isteği farklı noktalar döndürmeli.

## B-017 · PG puanı için üç hedef kaynağı + kopya blok
- **Dosya:satır:** Skor motoru `score_engine_service.py:391-395` (`KpiYearConfig.target_value`), K-Radar `_process_component` (`latest.target_value or kpi.target_value`), `k_rapor/routes.py:975-1000 (alert), 1925 (pi-dagilim), 2170 (org-comparison)` (`kpi.target_value`; yıllık hedef yok sayılıyor). Aynı "son satır → compute_pg_score → yüzde" bloğu 4 kez kopyalanmış.
- **Etki:** Aynı PG aynı yılda Kurumsal, Dağılım, Uyarı ve K-Radar'da farklı yüzde; hedefi yıllık değişen göstergelerde geçmiş yıllar bugünün hedefiyle ölçülür.
- **Önem:** Orta · **Etiket:** Kesin
- **Çözüm:** `get_pg_year_score(kpi, year)` tek servis (yıllık hedef → satır hedefi → ana hedef), raporlar bunu çağırsın.
- **Efor:** M (4-6 sa)
- **Doğrulama testi:** Yıllık hedefi farklı PG için `alert`, `pi-dagilim`, `corporate` aynı yüzdeyi vermeli.

## B-018 · Yıl/plan-yılı filtresi eksik veya tutarsız raporlar
- **Dosya:satır:** `k_rapor/routes.py:472` (`/api/activity`: tüm yıllar), `:709` (`data-status` "cari dönem" diyor ama yıl içinde herhangi giriş = girildi), `:2454` (bildirim); `raporlar/routes_faz0.py:55-120` (veri kalitesi: son ölçüm tüm yıllardan), `routes_faz4.py:275` (`kpi_data_volume`), `routes_faz1.py:848` (early-warning), `routes_faz5.py:224` (ml-anomaly), `sp/routes_exec_advisor.py:251` (`exec-trend` yıl filtresiz), `routes_faz4.py:215-238` (`process_health` `?year` yok sayıyor). Plan-yılı NULL legacy davranışı karışık: bazı sorgular `or_(... is_(None))`, bazıları (`faz2:157`, `faz3:402`, `faz4:219`) eşitlik.
- **Önem:** Orta · **Etiket:** Kesin
- **Çözüm:** Ortak `year_scope(query, model, year)` yardımcısı; NULL legacy politikası tek yerde.
- **Efor:** L (1-2 gün)
- **Doğrulama testi:** Yıl 2020/2026 farkı olan her rapor için fixture karşılaştırma.

## B-019 · EVM raporu: proje adları ve yıl filtresi
- **Dosya:satır:** `k_rapor/routes.py:1185` (`from app.models.project import Project as ProjModel`), `:1177-1181` (`limit(120)` sonra yıl filtresi).
- **Kanıt:** `app/models/project.py` yalnız `PlanProject, PlanProjectTask, PlanProjectActivity` içeriyor; `Project` `portfolio_project.py`'de. İçe aktarma hatası `except Exception` ile loglanıp geçiliyor → adlar hep `"Proje #<id>"`. Yıl filtresi ilk 120 kaydı çekip Python'da süzüyor → eski yıl boş dönebilir.
- **Önem:** Orta · **Etiket:** Kesin
- **Çözüm:** `portfolio_project.Project` içe aktar, tenant süz; yıl filtresini SQL'e ve `LIMIT` öncesine al.
- **Efor:** S
- **Doğrulama testi:** EVM yanıtında `project_name` gerçek ad.

## B-020 · Süreç×PG ısı haritası birimleri karıştırıyor
- **Dosya:satır:** `k_rapor/routes.py:206-350`.
- **Kanıt:** Hücre `avg_val = ortalama(float(actual_value))` süreçteki tüm PG'ler için (yüzde, TL, adet karışık). `period` istemci string'i `KpiData.period_type == period` oluyor ama etiketler `else`'e düşüyor (geçersiz değerde sessizce çeyrek etiketi + boş veri). `data_index[(kpi, period_no)]` aynı anahtar için son satırı yazıyor (sıralama yok). `period_no` yoksa `or 1` ile hepsi 1. döneme yığılıyor.
- **Önem:** Orta · **Etiket:** Kesin
- **Çözüm:** Hücrede PG başarı yüzdesi ortalaması; `period` beyaz liste; satır birleştirmede deterministik kural.
- **Efor:** M
- **Doğrulama testi:** %5 ve 12000 TL değerli iki PG'li süreç hücresi 0-100 aralığında.

## B-021 · Özet sayaçları yanlış
- **Dosya:satır:** `k_rapor/routes.py:670,691` (`pgs[:200]` kırpılıyor, `veri_yok = len(pgs) - len(all_pcts)` kırpılanları "veri yok" sayar); `raporlar/routes_faz1.py:875,905` (`total_kpis_checked=len(all_kpis)` ama yalnız ilk 100 incelendi); `routes_faz5.py:247,298` (ilk 200, `kpis_skipped` kırpılanı atlanmış sayar); `raporlar/routes_faz3.py:979` (ZIP ilk 100 kullanıcı, önizleme tümünü söylüyor); `services/k_radar_service.py:795-801` (`on_time` tüm tamamlanan görevleri sayıyor, payda yalnız tarihli görevler → oran %100'ü aşabilir).
- **Önem:** Orta · **Etiket:** Kesin
- **Çözüm:** Kırpmayı sayımdan sonra yap, "gösterilen/toplam" bilgisini yanıta ekle; `on_time` = `completed_at <= due_date`.
- **Efor:** S-M
- **Doğrulama testi:** 250 PG fixture'ı ile `veri_yok` doğru; tamamlanan 5, tarihli 3 görev → oran ≤ 100.

## B-022 · Sahte CPM, keyfi kaynak yükü, öneri-pozisyon eşlemesi
- **Dosya:satır:** `k_radar/routes_kpr.py:23-46` ("critical_starts" = öncülü olmayan görevler; CPM yok), `services/k_radar_service.py:798` (`resource_load = aktif_görev/proje*10`), `:825-867` (`recommendations[0..3]` pozisyonla KS/KP/KPR/Bireysel'e bağlanıyor; liste değişken uzunlukta → yanlış öneri yanlış kartta).
- **Önem:** Düşük · **Etiket:** Kesin
- **Çözüm:** CPM'i "Başlangıç görevleri" diye etiketle veya gerçek ileri/geri geçiş uygula; öneriye `source` alanı ekle.
- **Efor:** M
- **Doğrulama testi:** `get_recommendations_from_summary` her öneri için kaynak etiketi döndürmeli.

## B-023 · Senaryo dalları
- **Dosya:satır:** `sp/routes_scenario.py:66` (`if label not in (...) and len(label) > 50` — mantık hatası, "veya" olmalı), `:117` (`db.session.delete(py)` PlanYear hard delete), `app/models/plan_year.py:63-65` + `migrations/versions/f5215370eebd_baseline_2026_06_squash.py:420` (tam `UniqueConstraint(tenant_id, year)`; senaryo aynı yılı kullandığı için ikinci kayıt `IntegrityError`; arşiv migration'daki kısmi indeks squash'ta kaybolmuş), `app/services/plan_year_service.py:49` (`get_plan_year` `scenario_of_id IS NULL` süzmüyor; 14+ çağrı).
- **Etki:** Sıfırdan kurulan DB'lerde (Test/Demo) senaryo oluşturma 500; kısmi indeksli DB'de rapor taban yerine senaryo planını bulabilir.
- **Önem:** Orta · **Etiket:** Kesin (mantık hatası); DB etkisi ortama bağlı
- **Çözüm:** Etiketi beyaz listeye sabitle; migration ile kısmi benzersiz indeks; `get_plan_year`'a `scenario_of_id.is_(None)`; silmeyi soft yap.
- **Efor:** M
- **Doğrulama testi:** Temiz DB'de senaryo oluştur → 201; `get_plan_year` her zaman taban yılı dönmeli.

## B-024 · Toplu KPI yıllık hedefi kısmi uygulanıyor
- **Dosya:satır:** `sp/routes_plan_year.py:386-445`, `app/services/plan_year_service.py:712-744` (`upsert_kpi_year_config` her çağrıda `db.session.commit()`).
- **Kanıt:** Döngüde hata olursa `db.session.rollback()` çağrılıyor ama önceki kayıtlar zaten commit edilmiş → "başarısız" cevabında yarısı yazılmış. `int(item["kpi_id"])` (satır 416) döngü dışı → ValueError 500.
- **Önem:** Orta · **Etiket:** Kesin
- **Çözüm:** `commit=False` parametresi, sonda tek commit; ön doğrulama.
- **Efor:** S
- **Doğrulama testi:** 3 kayıttan ortası geçersiz → hiçbiri yazılmamalı.

## B-025 · Doğrulanmamış girdi → 500
- **Dosya:satır:** `k_rapor/routes.py:1665,1711` (`int(payload["limit"])`, `.lower()` try dışı), `sp/routes_replan_trigger.py:59`, `sp/routes_frameworks.py:141` (`d.get("name","").strip()` JSON `null` → AttributeError), `sp/routes_sp_proje.py:109-112,183-186` (`strptime` hatası genel `except` → 500), `analiz/routes.py:47-51,178` (`fromisoformat` hatası 500; tz'li/tz'siz karışımı TypeError), `analiz/routes.py:110` (`process_ids` liste değilse), `sp/routes_initiative.py:53`, `sp/routes_plan_year.py:416`.
- **Önem:** Orta · **Etiket:** Kesin
- **Çözüm:** Ortak `parse_int/parse_date` yardımcıları + 400.
- **Efor:** M
- **Doğrulama testi:** `{"limit":"abc"}`, `{"name":null}`, `start_date=xx` → 400.

## B-026 · Alan atama/değer doğrulaması yok
- **Dosya:satır:** `app/services/plan_year_service.py:739-741` (`setattr(cfg, field, data[field])`: `direction`, `weight`, `target_value` doğrulamasız — "lower_is_better" gibi kayıt skor motorunu bozar), `sp/routes_initiative.py:99-103` (PATCH ham atama; `start>end` kontrolü yok), `sp/routes_frameworks.py:227-233` (VRIO), `sp/routes_sp_proje.py:104-107` (`progress` sınırsız), `sp/routes_pages.py:297-311` (kimlik alanları tip/uzunluk), `raporlar/routes_esg.py:104,164,237` (`scope` beyaz listede değil → karbon toplamından sessiz düşer; `year` aralığı yok; `_num("nan")` NaN kaydeder; geçersiz sayı sessizce `None` yazıp mevcut değeri siler), `k_radar/routes_risk.py:152,210` (`status` serbest metin).
- **Önem:** Orta · **Etiket:** Kesin
- **Çözüm:** Beyaz liste + aralık kontrolü; geçersizde 400.
- **Efor:** M
- **Doğrulama testi:** `direction="foo"` → 400; ESG değer `"abc"` → 400 ve mevcut değer korunur.

## B-027 · Sınırsız yıl ile PlanYear üretimi
- **Dosya:satır:** `sp/routes_plan_year.py:152-172` (`set-active`: `get_or_create_plan_year(tid, int(year))`, 1900-3000 kontrolü yok), `:482-528` (sihirbaz: `new_year` tipi/aralığı doğrulanmıyor). `routes_exec_advisor.py:455` şablon ucunda 2000-2100 kontrolü var — tutarsız.
- **Etki:** Yönetici yanlışlıkla `year=20260` ile yıl kaydı üretir; yıl seçici ve raporlar kirlenir.
- **Önem:** Orta · **Etiket:** Kesin
- **Çözüm:** `1900<year<3000` ve mevcut-yıl±N sınırı; ortak doğrulayıcı.
- **Efor:** S
- **Doğrulama testi:** `year=99999` → 400.

## B-028 · N+1 ve istek-başı ağır hesap
- **Dosya:satır:** `analiz/routes.py:218-246` (tüm kurum KPI'ları için döngüde `detect_anomalies`), `:48-75` (KPI başına `get_performance_trend`), `sp/routes_exec_advisor.py:160-245` (tek istekte 33 `compute_vision_score`; geçmiş cache 7 gün — geriye dönük veri girince bayat; anahtar veri değişimini içermiyor; hata `except Exception: return None` sessiz), `raporlar/routes_faz1.py:715` ve `faz3:632` (`for m in metrics: m.values` lazy N+1), `faz2:101,291`, `faz5:343` (döngüde `db.session.get`), `k_rapor/routes.py:2104` (Admin için tüm kurumlar).
- **Önem:** Orta · **Etiket:** Kesin
- **Çözüm:** Toplu SQL/`selectinload`, sonuç cache'i + arka plan iş.
- **Efor:** L
- **Doğrulama testi:** 200 KPI'lı kurumda `analysis/api/anomalies` sorgu sayısı sabit (<10).

## B-029 · Sınırsız `.all()`
- **Dosya:satır:** `services/k_radar_service.py:127-138` (yıl için tüm KpiData satırı yalnız "son"u almak için ORM'e yükleniyor), `:545` (`kpi_rows_all` tüm yıllar), `:786`; `k_radar/routes_ks.py:22` (`_ks_swot_summary` tüm yıllar); `k_rapor/routes.py:480` (tüm faaliyetler), `:1431` (export-excel `latest_data`), `:2459` (`Notification.filter_by(tenant_id).all()` — sonsuz büyür), `:860`; `raporlar/routes_faz5.py:253-263` (200 PG'nin tüm tarihçesi), `faz1:879`; `k_radar/routes_risk.py:75,112` (tüm riskler).
- **Önem:** Orta · **Etiket:** Kesin
- **Çözüm:** `DISTINCT ON`/pencere fonksiyonu veya `GROUP BY` ile veritabanında son kayıt; `LIMIT`/sayfalama.
- **Efor:** M-L
- **Doğrulama testi:** 500k KpiData ile hub yanıtı <1 sn ve bellek sabit.

## B-030 · Sessiz exception yutma
- **Dosya:satır:** `raporlar/routes_faz0.py:338,711`, `routes_faz1.py:786`, `routes_faz2.py:156`, `routes_faz4.py:238` (`except Exception: proc_scores = {}` — skor hesaplanamazsa tüm süreçler "—", log yok); `routes_faz2.py:83`; `sp/routes_exec_advisor.py:153` (`_kv_score_at`); `k_radar/routes_ks.py:35` (`low_perf = 0`); `raporlar/routes_faz3.py:714`. KURALLAR §3 "log zorunlu".
- **Etki:** Skor motoru hatası kullanıcıya "veri yok" gibi görünür, ekip hatayı görmez.
- **Önem:** Orta · **Etiket:** Kesin
- **Çözüm:** `current_app.logger.error(..., exc_info=True)` ve yanıtta `degraded=true` bayrağı.
- **Efor:** S
- **Doğrulama testi:** `compute_process_scores_internal` monkeypatch ile hata; log kaydı + `degraded`.

## B-031 · K-Radar günlük özet takvimi tek global dosya
- **Dosya:satır:** `k_radar/routes_common.py:69-77`, `services/k_radar_scheduler_service.py:28-64,125-144`.
- **Kanıt:** `instance/k_radar_schedule.json` tüm kurumlar için tek; herhangi bir kurumun `tenant_admin`/`executive_manager`'ı saati/aç-kapa'yı tüm sistem için değiştirir. `BackgroundScheduler` süreç içi: çok işçili sunucuda her worker ayrı zamanlayıcı kurar (`_already_sent_today` kısmi koruma).
- **Önem:** Orta · **Etiket:** Kesin
- **Çözüm:** Kurum bazlı ayar (DB), tek merkezli zamanlayıcı.
- **Efor:** M
- **Doğrulama testi:** A kurumu saati değiştirir; B kurumunun ayarı değişmemeli.

## B-032 · Digest gönderiminde alıcı doğrulaması yok
- **Dosya:satır:** `k_rapor/routes.py:1768-1792`, `app/services/email_digest_service.py:146-240`.
- **Kanıt:** `recipients` JSON'dan olduğu gibi; biçim/alan adı/sayı sınırı yok; `msg["To"] = to` doğrudan. Kurum SMTP'si üzerinden kurum özeti herhangi bir adrese gider (spam aktarıcısı / veri çıkarma). `digest/preview` (satır 1753) herkese açık HTML döner.
- **Önem:** Orta · **Etiket:** Kesin
- **Çözüm:** `parseaddr` + kurum kullanıcı e-posta beyaz listesi; en fazla N alıcı; preview'a rol kontrolü.
- **Efor:** S
- **Doğrulama testi:** `recipients=["x@evil.com\nBcc: y"]` → 400.

## B-033 · Hard delete ve eksik kaskad
- **Dosya:satır:** `sp/routes_frameworks.py:256` (VRIO hard delete), `sp/routes_scenario.py:117` (PlanYear), `raporlar/routes_esg.py:227` (ESG değeri), `sp/routes_strategy.py:147-160` (ana strateji soft delete'i alt stratejileri ve süreç bağlantılarını pasifleştirmiyor), `sp/routes_initiative.py:147-158` (girişim silinince bağlı projelerin `initiative_id`'si kalıyor). KURALLAR §3: hard delete yasak.
- **Önem:** Düşük · **Etiket:** Kesin
- **Çözüm:** `is_active=False` + bağımlıları pasifle.
- **Efor:** S-M
- **Doğrulama testi:** Strateji sil → alt stratejiler listede görünmemeli.

## B-034 · `_` değişkeni gettext'i gölgeliyor
- **Dosya:satır:** `sp/routes_exec_advisor.py:182,209` (`for _ in range(12)` / `range(8)`), kullanım `:244` (`_("İşlem tamamlanamadı.")` `except` içinde).
- **Etki:** Hata yolunda `TypeError: 'int' object is not callable` → JSON yerine HTML 500; erken hatada `UnboundLocalError`.
- **Önem:** Düşük · **Etiket:** Kesin
- **Çözüm:** `_i` kullan.
- **Efor:** XS
- **Doğrulama testi:** `get_plan_year` monkeypatch ile hata → 500 JSON.

## B-035 · `date.today()` vs `today_tr`
- **Dosya:** Kapsamda 37 `date.today()/datetime.now()` (ör. `k_rapor/routes.py:96,372,482`, `raporlar/routes_faz0.py:838`, `services/k_radar_service.py:786`), `today_tr` kullanımı 0 (`app/utils/tr_time.py` var, yalnız `date_sovereign` kullanıyor).
- **Etki:** Sunucu UTC ise 00:00-03:00 TR'de "bugün/gecikme/çeyrek/yıl" geride (yıl başında bir yıl).
- **Önem:** Düşük · **Etiket:** Olası (sunucu TZ'ye bağlı)
- **Çözüm:** Toplu `today_tr()`.
- **Efor:** S
- **Doğrulama testi:** `freezegun` ile 31 Aralık 22:30 UTC → rapor yılı yeni yıl.

## B-036 · Dosya adı / ZIP giriş adı kullanıcı girdisinden
- **Dosya:satır:** `raporlar/routes_faz3.py:1049` (`uname.replace(" ","_").replace("/","_")[:40]` — `\`, `..`, kontrol karakteri geçer; aynı isimler ZIP'te çakışır), `k_rapor/routes.py:1573` (`tab` ham dosya adında).
- **Önem:** Düşük · **Etiket:** Olası
- **Çözüm:** `werkzeug.utils.secure_filename` + `{id}_` öneki.
- **Efor:** XS
- **Doğrulama testi:** `last_name="..\\x"` ile ZIP giriş adı güvenli olmalı.

## B-037 · LLM isteğine ham kurum verisi, sınırsız kullanıcı metni
- **Dosya:satır:** `sp/routes_exec_advisor.py:430` (`str(snap)` tüm özet sözlüğü), `raporlar/routes_faz4.py:296-304` (`free_text` uzunluk sınırsız), `raporlar/routes_faz3.py:408` (kurum adı prompt'a).
- **Önem:** Düşük · **Etiket:** Olası (PII maskesi tenant ayarına bağlı)
- **Çözüm:** Girdi uzunluk sınırı (500), alanları beyaz listele, `pii_mask` uygula.
- **Efor:** S
- **Doğrulama testi:** 100k karakterlik `query` → 400.

## B-038 · Ölü/çift route, kopya rol listeleri, çift çeyrek raporu
- **Ölü route adayları** (ad ya da yol repoda başka hiçbir yerde anılmıyor; menü kaydı DB'de olabilir → doğrulanmalı): `sp_api_okr_sync_kpis` (`sp/routes_analysis.py:378`), `sp_llm_usage_page` (`routes_llm_quota.py:20`), `sp_api_k_vektor_weights` (`routes_pages.py:218`), `sp_digest_html` (`routes_frameworks.py:282`), `k_rapor_dashboard_widgets` (`k_rapor/routes.py:45`), `k_rapor_api_forecast` (`:60`), `k_rapor_anomalies_notify_webhook` (`:1643`), `raporlar_api_sektorel` (`routes_faz4.py:102`), `k_radar_api_ks_pestle/okr/bsc/porter_real` (`routes_ks.py:61,82,89,199`).
- **Çift kayıt:** `@app_bp.route("/k-radar/api/kp")` hem `routes_kp.py:165` hem `:299` → ikinci kural erişilemez ölü takma ad.
- **Kopya rol listeleri:** `_SP_ROLES` (`sp/helpers.py:50`, `routes_donemler.py:44`), `_ESG_ROLES`, `_is_manager` (`routes_risk.py:27`), `WRITE_ROLES`; `kurum_yoneticisi`, `ust_yonetim`, `admin` canonical rol listesinde yok (`app/constants/roles.py`).
- **Çift çeyrek raporu:** `sp/routes_donemler.py:520` (`quarterly_review_service`) ve `raporlar/routes_faz2.py:313` (ayrı, farklı mantık).
- **Önem:** Düşük · **Etiket:** Kesin (yinelenme); ölü route kısmı doğrulama ister
- **Çözüm:** Ölü adayları DB `system_pages` ile çapraz kontrol et, sonra sil; tek rol kaynağı.
- **Efor:** M
- **Doğrulama testi:** `flask routes` çıktısında çift kural kalmamalı.

## B-039 · Küçük hesap ve etiket hataları
- **Dosya:satır:** `k_rapor/routes.py:1944` (çift sayıda elemanda medyan yanlış), `:146-165` (`bottom5` artan değil azalan sırada, <10 süreçte top5 ile çakışır), `:1798-1830` PDF "Aktif kullanıcı sayısı" = `tenant.employee_count`, `strftime('%d %B %Y')` İngilizce ay adı; `raporlar/routes_faz0.py:78-90` boş durumda yanıt şekli (`iyi`) ≠ dolu şekil (`iyi_count_only`); `routes_faz3.py:870-890` "Aksiyon dağılımı (top 50)" yalnızca 50 kayıttan; `routes_faz2.py:313-364` rapor hep **bugünün** çeyreği (yıl seçici yok) ve yeni/biten girişim sayımlarında çeyrek üst sınırı yok (geçmiş çeyrek şişer, `updated_at` her düzenlemede değişir).
- **Önem:** Düşük · **Etiket:** Kesin
- **Çözüm:** Satır-satır düzeltme.
- **Efor:** S
- **Doğrulama testi:** `statistics.median` karşılaştırması; boş kurum JSON şeması testi.

## B-040 · Platform Admin (tenant_id=None) bağlamı
- **Dosya:satır:** Çoğu route doğrudan `current_user.tenant_id` kullanıyor (`k_rapor/routes.py`, `sp/*`): `filter_by(tenant_id=None)` → boş sonuç; `sp/routes_tenant_ai.py:42-44` `TenantLLMConfig(tenant_id=None)` kaydı → IntegrityError 500; `raporlar` ise 400 "Tenant yok" döndürüyor (tutarsız).
- **Önem:** Orta · **Etiket:** Olası
- **Çözüm:** Tek `require_tenant_context` dekoratörü ve net 400.
- **Efor:** S
- **Doğrulama testi:** `Admin` oturumu ile `/k-report/api/corporate` → 400, 500 değil.

---

## Doğrulama notları
- Taranan route: raporlar 101, k_rapor 41, sp ~138, k_radar ~91, analiz 9. Mutasyon yapan route'ların hepsi bir tür rol kontrolü içeriyor (SP: `sp_manage_required`/`_can`; K-Radar: `_can_manage_k_radar`/`_is_manager`; ESG: `_can_manage_esg`). Eksik olan **okuma/export** uçlarının rol kapısı (B-002/B-003).
- Doğrudan tenant filtresi atlayan basit IDOR bulunmadı (id'li sorguların çoğu `tenant_id` ile süzülü); sızıntılar FK doğrulaması yoluyla (B-001, B-009).
- İyi örnekler (referans alınabilir): `raporlar/routes_esg.py` (rol + modül + soft delete + tenant join), `sp/routes_plan_year.py::close` (denetim kaydı), `routes_faz4.py::_load_sektor` (path-traversal beyaz liste), `outbound_guard` (SSRF).
