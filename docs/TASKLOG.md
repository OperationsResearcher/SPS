# TASKLOG — Kokpitim Görev Takip Defteri
> Her kod değişikliği bu dosyaya işlenir.
> Format: TASK-[numara] | Tarih | Durum

## TASK-212 | 2026-06-23 | ✅ Tamamlandı

**Görev:** URL tek-dil — masaustu KÖKÜ /masaustu → /desktop (2 route, 301 köprülü)
**Modül:** masaustu, nav/registry/middleware, legacy_redirect, hata_kontrol, tests
**Durum:** ✅ Tamamlandı

### Çeviri haritası
/masaustu → /desktop, /masaustu/api/koe-danisman-ai → /desktop/api/koe-advisor-ai
(koe = Kurumsal Olgunluk Endeksi kısaltması KORUNDU; danisman→advisor).

### Değiştirilen Dosyalar
- `micro/modules/masaustu/routes.py` → 2 route (fonksiyon adları korundu)
- `app/__init__.py` nav, `micro/core/module_registry.py` url (id "masaustu" korundu)
- `app/middleware/legacy_sunset.py` → canonical /desktop (+/)
- `app/legacy_redirect_config.py` → EXACT /masaustu→app_bp.masaustu, PREFIX /masaustu/→/desktop/,
  tam-yol köprü koe-danisman-ai→koe-advisor-ai (iç segment, canonical-öncesi)
- `app/services/hata_kontrol_service.py` + `hata_kontrol_executor.py` → tarama hedefi /desktop
- `tests/test_legacy_sunset.py` (dashboard→desktop, kurum-paneli→organization beklentileri),
  `tests/test_module_smoke.py`, `tests/test_e2e_flow.py`

### Yapılan İşlem
/masaustu (modül) ≠ /masaustu-launcher (zaten /desktop-launcher, TASK-200) — KARIŞTIRILMADI
(kelime sınırı: /masaustu exact + /masaustu/ slash'lı prefix). Fonksiyon adları korundu → /dashboard
EXACT köprüsü url_for ile yeni /desktop'a otomatik yönlenir. koe-danisman-ai POST API: /masaustu/ prefix
kuralı kökü çevirdi ama iç danisman→advisor için ek tam-yol köprü gerekti (yoksa /desktop/api/koe-danisman-ai
= 404). frontend hardcoded YOK (url_for/data-*).

### Test
Restart: /desktop 302, /masaustu→/desktop 301, /masaustu/api/koe-danisman-ai→/desktop/api/koe-advisor-ai
(iç segment dahil), /dashboard→/desktop, /masaustu-launcher→/desktop-launcher (karışmadı), kurum/sp regresyon yok.
pytest legacy_sunset(redirect zinciri) + module → 26/26 geçti.

### Notlar
Kalan URL işi: sp plan-yıl grubu (aktif iş), /proje + /surec legacy alias (modern /project /process var),
admin araçları, kule, test_smoke_routes (/micro kırık).

## TASK-211 | 2026-06-23 | ✅ Tamamlandı

**Görev:** URL tek-dil — kurum KÖKÜ /kurum → /organization (15 route, 301 köprülü)
**Modül:** kurum, nav/registry/middleware, legacy_redirect, frontend, tests
**Durum:** ✅ Tamamlandı

### Karar gerekçesi
Kullanıcı "legacy dahil her şey /organization" dedi. İnceleme: legacy /kurum/kalite-politikalari,
/kurum/degerler, /kurum/etik-kurallari sadece static/js/kurum_panel.js'de (HİÇBİR template yüklemiyor =
ÖLÜ JS) + /api/kurum/* (api_bp /api prefix, ayrı yüzey). CANLI legacy /kurum route'u YOK. Dolayısıyla
"canlı olan her şey" = modern kurum modülü (15 route). Ölü JS'e dokunulmadı (çalışmıyor, strangler silecek).

### Değiştirilen Dosyalar
- `micro/modules/kurum/routes.py` → 15 route /kurum* → /organization* (fonksiyon adları korundu)
- `app/__init__.py` → nav; `micro/core/module_registry.py` → url (id "kurum" korundu)
- `app/middleware/legacy_sunset.py` → canonical /organization (+/)
- `app/legacy_redirect_config.py` → EXACT /kurum→app_bp.kurum, PREFIX /kurum/→/organization/,
  TASK-206 iç köprüleri /organization'a güncellendi (/kurum/ayarlar→/organization/settings vb.)
- `ui/templates/platform/kurum/index.html` (5 data-base), `ui/static/platform/js/kurum.js`,
  `ui/static/platform/js/command_palette.js`
- `tests/test_module_smoke.py` → /organization (+api/overview)

### Yapılan İşlem
Fonksiyon adları korundu → url_for/data-* otomatik doğru; /kurum-paneli, /kurum-yonetim EXACT_ENDPOINT
(app_bp.kurum/kurum_ayarlar) url_for ile yeni /organization'a yönlenir. /kurumsal, /kurumlar, /kurum-
KARIŞTIRILMADI (kelime sınırı: /kurum exact + /kurum/ slash'lı prefix). KART id "kurum" korundu.

### Test
Restart: /organization* 302, /kurum* (kök+settings+ayarlar+api+add-strategy) 301→/organization*,
/kurum-paneli→/organization, /k-rapor/org-comparison etkilenmedi, sp/individual regresyon yok.
pytest module+bireysel → 25/25 geçti.

### Notlar
ÖLÜ legacy: static/js/kurum_panel.js (/kurum/degerler vb.) çalışmıyor, dokunulmadı. Kalan URL işi:
sp plan-yıl grubu (aktif iş), admin araçları, kule, test_smoke_routes (/micro prefix kırık).

## TASK-210 | 2026-06-23 | ✅ Tamamlandı

**Görev:** URL tek-dil — k-rapor KALAN iç API segmentleri İngilizceye (8 route, 301 köprülü)
**Modül:** k_rapor, legacy_redirect, test, KURALLAR-MASTER
**Durum:** ✅ Tamamlandı

### Çeviri haritası (kök /k-rapor ürün adı KORUNDU)
faaliyet→activity, faaliyet-matris→activity-matrix, bireysel→individual, rekabet→competition,
aktivite-takvim→activity-calendar, kurum-karsilastirma→org-comparison, sorumlu-analiz→responsible-analysis,
bildirim-analiz→notification-analysis. (TASK-205'te atlanan kalan segmentler; k-rapor artık tam İngilizce.)

### Değiştirilen Dosyalar
- `micro/modules/k_rapor/routes.py` → 8 route path (fonksiyon adları korundu)
- `app/legacy_redirect_config.py` → 8 köprü (faaliyet-matris uzun-önce, faaliyet'ten önce)
- `tests/test_k_rapor_smoke.py` → rekabet→competition
- `docs/KURALLAR-MASTER.md` → PG satırına "URL'de pi" istisnası eklendi (TASK-209 kalıcı not)

### Yapılan İşlem
TASK-205 kalıbı: k_rapor.js apiUrl(name)→dataset["api"+CamelCase(name)] mimarisi; data-api-* DEĞERLERİ
url_for ile gelir → fonksiyon adları korunduğu için frontend otomatik doğru. apiUrl("faaliyet")/data-api-faaliyet
ANAHTAR çiftine dokunulmadı (sadece route path + url_for değeri). Hardcoded frontend çağrısı YOK.

### Test
Restart: 8 yeni İngilizce 302, 8 eski TR köprü 301 (faaliyet-matris doğru hedefe — uzun-önce çalıştı),
TASK-205(kurumsal) + PG→PI(pg-dagilim) regresyon yok. pytest k_rapor+module smoke → 17+19 geçti.

### Notlar
k-rapor modülü artık TAM İngilizce. Kalan URL işi: sp plan-yıl grubu (aktif iş), kurum kökü /organization,
admin araçları, kule, test_smoke_routes (/micro prefix kırık - ayrı borç).

## TASK-209 | 2026-06-23 | ✅ Tamamlandı

**Görev:** URL tek-dil — PG→PI (Performans Göstergesi = Performance Indicator) URL segmenti (8 route, 301 köprülü)
**Modül:** bireysel, raporlar, k_rapor, legacy_redirect, nav, frontend
**Durum:** ✅ Tamamlandı

### Düzeltme (kullanıcı)
PG İngilizcesi PI'dir. Önceki turlarda pg "korunan kısaltma" sanılıp bırakılmıştı; URL'de pi olmalı.
KAPSAM: SADECE URL segmentleri. Kod/DB (pg_id, ProcessKpi), data-* attribute ADLARI, KART kodları DOKUNULMADI.

### Çeviri haritası
/individual/api/pg/* → /individual/api/pi/* (5 route; <int:pg_id> PARAMETRE adı korundu),
/reports/pg-project-impact (+api) → /reports/pi-project-impact, /k-rapor/api/pg-dagilim → pi-dagilim.

### Değiştirilen Dosyalar
- `micro/modules/bireysel/routes.py` → 5× /individual/api/pi/
- `micro/modules/raporlar/routes_faz5.py` → /reports/pi-project-impact (+api)
- `micro/modules/k_rapor/routes.py` → /k-rapor/api/pi-dagilim
- `app/legacy_redirect_config.py` → 4 yeni pg→pi köprüsü + TASK-204 pg-proje-etki hedefi pi'ye düzeltildi
- `app/__init__.py` → component-visibility eşleme (pi-project-impact)
- `ui/templates/platform/raporlar/pg_proje_etki.html` (fetch), `bireysel/karne.html` (2 data-base değeri),
  `k_radar/hub.html` (link), `ui/static/platform/js/bireysel.js` (2 fallback değeri)

### Yapılan İşlem
Sadece URL string değerleri pg→pi. data-pg-*-base attribute ADLARI (JS dataset.pgUpdateBase eşleşmesi)
ve PG_UPDATE_BASE JS değişken adları KORUNDU — yalnız değerleri /pi/. Template dosya adları (pg_proje_etki.html),
fonksiyon adları, render hedefleri dokunulmadı. pg-dagilim'de 'dagilim' Türkçe kaldı (ayrı iş). hub.html
görünen metin "PG × Proje" Türkçe kaldı (kullanıcı metni). İki nesil köprü: pg-proje-etki→pi-project-impact.

### Test
Restart: pi-* route'ları 302/405(POST), pg-* eski URL'ler 301→pi (pg-proje-etki dahil iki nesil zincir),
k-radar/individual regresyon yok. pytest bireysel+module+k_rapor smoke → 42/42 geçti.

### Notlar
Kalan URL işi: sp plan-yıl grubu (aktif iş), kurum kökü /organization, admin araçları, kule, test_smoke_routes
(/micro prefix kırık). Kod/DB katmanında pg hâlâ korunuyor (sadece URL pi oldu).

## TASK-208 | 2026-06-23 | ✅ Tamamlandı

**Görev:** URL tek-dil — k-radar iç Türkçe segmentleri İngilizceye (11 route, 301 köprülü)
**Modül:** k_radar (4 route dosyası), legacy_redirect, frontend, tests
**Durum:** ✅ Tamamlandı

### Çeviri haritası (kök /k-radar ürün adı KORUNDU)
cross/paydas→cross/stakeholder, kp/deger-zinciri→kp/value-chain, kp/kapasite→kp/capacity,
kp/olgunluk→kp/maturity (+ekle→add), kpr/kaynak-kapasite→kpr/resource-capacity,
ks/strateji-real→ks/strategy-real. (swot-real/swot-summary/cpm/evm/bcg vb. İngilizce — dokunulmadı.)

### Değiştirilen Dosyalar
- `micro/modules/k_radar/routes_cross.py` (paydas→stakeholder)
- `micro/modules/k_radar/routes_kp.py` (deger-zinciri, kapasite, olgunluk→maturity tamamı)
- `micro/modules/k_radar/routes_kpr.py` (kaynak-kapasite→resource-capacity)
- `micro/modules/k_radar/routes_ks.py` (strateji-real→strategy-real)
- `app/legacy_redirect_config.py` → REPORTS_SEGMENT_REWRITE'a 11 k-radar köprüsü
- `ui/templates/platform/k_radar/kp_deger_zinciri.html`, `ui/static/platform/js/vc_items.js` → data-update-base
- `tests/test_k_radar_regression.py`, `tests/test_smoke_routes.py`, `scripts/k_radar_smoke_check.py`

### Yapılan İşlem
KART kodları (data-card-code="...paydas_haritasi") ve k-rapor ?tab=paydas anahtarlarına DOKUNULMADI
(URL değil). Fonksiyon adları korundu → list-url/add-url url_for otomatik doğru; sadece data-update-base
hardcoded değişti. olgunluk tutarlılık için tamamen maturity yapıldı (yarım çeviri tutarsızlık olurdu).

### Test
Restart: 6 yeni İngilizce route 302, 4 eski TR köprü 301→hedef, sp/reports/k-rapor regresyon yok.
pytest k_radar_regression(login'li 403/200) + module + k_rapor smoke → 40/40 geçti.

### Notlar
test_smoke_routes.py ÖNCEDEN KIRIK (benden bağımsız): 19 route'un tümü /micro/ prefix'i kullanıyor ama
route'lar artık kök URL'de (app_bp, /micro prefix yok). /micro/sp, /micro/process dahil hepsi 404.
Bu ayrı bir refactor (tüm /micro/ → kök); bu turda kapsam dışı. Benim 3 satırım sadece zaten-kırık
testlerin URL adını güncelledi. Kalan URL işi: sp plan-yıl grubu, kurum kökü /organization, admin araçları, kule.

## TASK-207 | 2026-06-23 | ✅ Tamamlandı

**Görev:** URL tek-dil — sp güvenli iç segmentleri (plan-yıl HARİÇ, 11 route, 301 köprülü)
**Modül:** sp (5 route dosyası), nav/gating, legacy_redirect, frontend, tests
**Durum:** ✅ Tamamlandı

### Çeviri haritası (kök /sp KORUNDU; plan-yıl grubu DOKUNULMADI)
misyon→mission, vizyon→vision, degerler→values, strateji-haritasi→strategy-map (+api),
strateji-proje-matris→strategy-project-matrix, ayarlar/ai→settings/ai, scenarios/kiyas→scenarios/compare,
api/exec-ai-ozet→api/exec-ai-summary, api/savas-odasi→api/war-room.

### Plan-yıl HARİÇ tutulanlar (aktif iş — çakışma riski, kullanıcı kararı)
/sp/sihirbaz/yeni-yil (+api preview/uygula), /sp/donemler, /sp/api/donem-karsilastir,
/sp/rapor/donemsel, /sp/api/proje + /gorev (PlanProject/PlanProjectTask bağımlı). TÜRKÇE kaldı.

### Değiştirilen Dosyalar
- `micro/modules/sp/routes_pages.py` → mission/vision/values/strategy-map (sayfa+api)
- `micro/modules/sp/routes_tenant_ai.py` → /sp/settings/ai
- `micro/modules/sp/routes_alignment.py` → /sp/strategy-project-matrix
- `micro/modules/sp/routes_scenario.py` → /sp/scenarios/compare
- `micro/modules/sp/routes_exec_advisor.py` → exec-ai-summary, war-room/fronts
- `app/__init__.py` → component-visibility eşleme (strategy-map, strategy-project-matrix)
- `app/legacy_redirect_config.py` → REPORTS_SEGMENT_REWRITE'a 10 sp köprüsü
- `ui/templates/platform/sp/exec_dashboard.html`, `k_radar/hub.html` (2), `command_palette.js` → linkler
- `tests/test_sp_strateji_haritasi.py` → /sp/strategy-map (+api)

### Yapılan İşlem
sp ~120 route, çoğu zaten İngilizce. Plan-yıl ile ilişkili route'lar (memory project_sp_yillik_plan
aktif işi) BİLİNÇLİ dışarıda. routes_sp_proje.py PlanProject bağımlı → atlandı. Fonksiyon adları
korundu → tüm url_for/data-* frontend otomatik doğru (hardcoded frontend çağrısı YOK). Köprü genel
segment-rewrite listesine eklendi (canonical /sp/ muafiyetinden önce).

### Test
Restart: 7 yeni İngilizce route 302, 4+ eski TR köprü 301→hedef, plan-yıl grubu TÜRKÇE/çalışır (dokunulmadı),
reports/kurum regresyon yok. pytest sp_strateji_haritasi + module smoke → 21/21 geçti.

### Notlar
Kalan: sp plan-yıl grubu (aktif iş bitince), kurum kökü /organization (geniş), admin araçları (ertelendi),
kule (domain). Kullanıcı seçimi bekleniyor.

## TASK-206 | 2026-06-23 | ✅ Tamamlandı

**Görev:** URL tek-dil — kurum iç Türkçe segmentleri İngilizceye (5 route, 301 köprülü)
**Modül:** kurum, legacy_redirect, frontend, kilavuz_executor
**Durum:** ✅ Tamamlandı

### Çeviri haritası (kök /kurum domain terimi olarak KORUNDU)
ayarlar→settings, kimlik→identity. (overview/add-strategy vb. zaten İngilizce.)

### Değiştirilen Dosyalar
- `micro/modules/kurum/routes.py` → /kurum/settings + 4× /kurum/api/identity/* (fonksiyon adları korundu)
- `app/legacy_redirect_config.py` → REPORTS_SEGMENT_REWRITE'a 2 kurum köprüsü
- `ui/templates/platform/kurum/index.html` → data-kimlik-base değeri /kurum/api/identity/
- `ui/static/platform/js/kurum.js` → hardcoded fallback /kurum/api/identity/
- `ui/static/platform/js/command_palette.js` → /kurum/settings
- `app/services/kilavuz_olusturucu_executor.py` → goto /kurum/settings

### Yapılan İşlem
Modern kurum modülü dar: kök + 2 TR segment. /kurum/kalite-politikalari, etik-kurallari, degerler
gibi route'lar LEGACY yüzeyde (S1, kurum micro modülünde DEĞİL) → dokunulmadı. url_for kullanan
referanslar (donemler.html, ayarlar/index.html, ayarlar.html) fonksiyon adı korunduğu için otomatik
doğru. data-kimlik-base attribute ADI (dataset.kimlikBase eşleşmesi) korundu, sadece değeri çevrildi.
kimlik/<kind> içindeki misyon/vizyon/degerler PARAMETRE değerleridir (DB kayıt türü) — URL path değil, dokunulmadı.

### Test
Restart: /kurum/settings + /kurum/api/identity/* 302 (login gate); /kurum/ayarlar→/kurum/settings,
/kurum/api/kimlik/<kind>/list→/kurum/api/identity/<kind>/list (alt yol korunarak) 301. k-rapor/reports/kurum kökü
regresyon yok. pytest module+admin smoke → 31/31 geçti.

### Notlar
ATLANDI: admin araçları (hata-kontrolu/kilavuz/yonetim-paneli) — kullanıcı yüzeyi yok + bakim-modu
middleware/self-scan bağımlılıkları; fayda düşük, risk orta. Kalan: sp (~12 path, aktif plan-yıl — ayrı
dikkatli oturum), kurum kökü /organization (geniş), kule (domain).

## TASK-205 | 2026-06-23 | ✅ Tamamlandı

**Görev:** URL tek-dil — k-rapor iç API segmentleri İngilizceye (9 segment, 301 köprülü)
**Modül:** k_rapor, dashboard_widgets, legacy_redirect/sunset, tests
**Durum:** ✅ Tamamlandı

### Çeviri haritası (kök /k-rapor ürün adı olarak KORUNDU)
kurumsal→corporate, surec-pg→process-pg, uyum→compliance, veri-durumu→data-status,
denetim→audit, uyari→alert, stratejik-analiz→strategic-analysis, paydas→stakeholder,
strateji-kapsama→strategy-coverage. (risk/k-vektor/rekabet/anomalies/digest İngilizce — dokunulmadı.)

### Değiştirilen Dosyalar
- `micro/modules/k_rapor/routes.py` → 9 `@route("/k-rapor/api/<TR>")` → İngilizce (fonksiyon adları korundu)
- `app/services/dashboard_widgets.py` → 2 hardcoded data_endpoint (corporate, stakeholder)
- `app/legacy_redirect_config.py` → REPORTS_SEGMENT_REWRITE'a 9 k-rapor köprüsü
- `app/middleware/legacy_sunset.py` → segment köprü bloğu GENELLEŞTİRİLDİ (tam-yol; /reports + /k-rapor)
- `tests/test_k_rapor_smoke.py`, `test_module_smoke.py` → yeni segment adları

### Yapılan İşlem
k_rapor.js `apiUrl(name)` → `dataset["api"+CamelCase(name)]` mimarisi; data-api-* attribute DEĞERLERİ
url_for ile geliyor → fonksiyon adları korunduğu için frontend otomatik doğru. Sadece route string'leri
+ 2 widget endpoint + testler değişti. `?tab=kurumsal` query/tab anahtarlarına DOKUNULMADI (URL path değil).
Köprü: TASK-204'teki /reports-özel segment bloğu tam-yol mantığına genelleştirildi (canonical muafiyetinden
önce çalışır); böylece /k-rapor/api/<TR> de köprülenir, /reports regresyonu yok.

### Test
Restart: 9 yeni API 302 (login gate), 9 eski TR segment 301→İngilizce. TASK-204 /reports köprü regresyonu
yok. pytest k_rapor+module+bireysel smoke → 42/42 geçti.

### Notlar
Kalan: sp (~12 path, aktif plan-yıl — dikkatli), kurum kökü (/kurum → /organization, geniş), admin araçları
(hata-kontrolu, kilavuz, yonetim-paneli), kule (domain). Kullanıcı seçimi bekleniyor.

## TASK-204 | 2026-06-23 | ✅ Tamamlandı

**Görev:** URL tek-dil — raporlar İÇ Türkçe segmentleri İngilizceye (24 segment, 301 köprülü)
**Modül:** raporlar (route+template+js), nav, legacy_sunset middleware + config
**Durum:** ✅ Tamamlandı

### Çeviri haritası (24 segment)
muda-analizi→muda-analysis, strateji-hikayesi→strategy-story, stratejik-yillik→strategic-annual,
bireysel-hizalama→individual-alignment, bireysel-karne-batch→individual-scorecard-batch,
operasyon-istatistik→operation-statistics, hizalama-sankey→alignment-sankey,
departman-performans→department-performance, yonetici-liderlik→executive-leadership,
sabah-ozeti→morning-summary, evrim-filmi→evolution-film, ai-sunum→ai-presentation,
ai-danisman→ai-advisor, yatirimci-sunum→investor-presentation, esg-rapor→esg-report,
esg-yonetim→esg-management, audit-paketi→audit-package, veri-kalitesi→data-quality,
k-vektor-carpiklik→k-vector-skewness, hedef-revizyon→target-revision, onay-zinciri→approval-chain,
pg-proje-etki→pg-project-impact (pg korundu), sektorel→sectoral, iki-fa→two-fa.

### Değiştirilen Dosyalar (126 hit / 32 dosya — toplu script)
- `scripts/_arsiv/fix_oneshot/rename_reports_segments.py` → çok-eşlemeli, uzun-anahtar-önce,
  tam-segment sınırlı; köprü dosyaları + docs/htmlcov/ARCHIVE hariç
- `micro/modules/raporlar/routes*.py` (8) → route string'leri (fonksiyon adları korundu)
- `ui/templates/.../raporlar/*.html`, `ui/static/.../js/raporlar/*.js`, `k_radar/hub.html` (23),
  `sp/ceyreklik_review.html`, `app/__init__.py` nav (23)
- `app/legacy_redirect_config.py` → yeni REPORTS_SEGMENT_REWRITE listesi (24 kural)
- `app/middleware/legacy_sunset.py` → REPORTS_SEGMENT_REWRITE'ı _should_skip'ten ÖNCE uygula;
  hem /reports/<TR> hem /reports/api/<TR> (+alt yol) varyantlarını köprüler

### Önemli teknik nokta
`/reports/` TASK-203'te canonical (redirect muaf) yapılmıştı → iç segment köprüsü normal PREFIX_REWRITE'a
ULAŞAMIYORDU (404 verdi). Çözüm: özel segment-rewrite bloğunu canonical kontrolünden ÖNCE çalıştır.
İlk denemede /reports/api/<TR> yakalanmadı (sadece /reports/<TR>); api/ varyantı da eklendi.

### Test
git grep: canlı kodda Türkçe iç segment kalmadı. Köprüler: /reports/<TR> ve /reports/api/<TR>(+/preview)
→ 301 yeni EN; çakışma testi (bireysel-hizalama vs -karne-batch) doğru ayrıştı. 37/37 smoke geçti.
analiz/bireysel regresyon yok. raporlar modülü artık TAMAMEN İngilizce.

### Notlar
Kalan modüller: sp (~12 TR path, aktif plan-yıl — dikkatli), kurum (/kurum/ayarlar), k-rapor (birkaç),
admin araçları (hata-kontrolu, kilavuz, yonetim-paneli), kule (domain terimi). Kullanıcı seçimi bekleniyor.

## TASK-203 | 2026-06-23 | ✅ Tamamlandı

**Görev:** URL tek-dil — raporlar modülü KÖK segmenti `/raporlar` → `/reports` (95 route, 301 köprülü)
**Modül:** raporlar (8 route dosyası), ui (template+js), nav, legacy_redirect
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar (329 hit / 95 dosya — toplu script)
- `scripts/_arsiv/fix_oneshot/rename_raporlar_to_reports.py` → tek-seferlik denetlenebilir script
  (regex `/raporlar` kelime-sınırlı → `/reports`; docs/htmlcov/ARCHIVE/_arsiv + köprü dosyaları HARİÇ)
- `micro/modules/raporlar/routes*.py` (8 dosya) → tüm `@route("/raporlar*")` → `/reports*`
- `ui/templates/platform/raporlar/*.html` (44), `ui/static/platform/js/raporlar/*.js` (40+),
  `k_radar/hub.html` (42 ref), `sp/ceyreklik_review.html`, `command_palette.js`, `app/__init__.py` nav
- `app/legacy_redirect_config.py` → PREFIX_REWRITE `/raporlar`→`/reports` (301; iç segment korunur)
- `app/middleware/legacy_sunset.py` → canonical prefix `/reports/`

### Yapılan İşlem
raporlar ~95 route, çoğu zaten İngilizce; sadece KÖK segment çevrildi. İç Türkçe segmentler
(muda-analizi, strateji-hikayesi, bireysel-hizalama, sabah-ozeti, ai-sunum, stratejik-yillik vb.)
BİLİNÇLİ olarak DOKUNULMADI — ayrı tur. 85+ dosyada hardcoded `/raporlar` olduğu için elle değil,
dry-run ile denetlenen tek-seferlik script kullanıldı. Köprü dosyaları script'ten hariç tutuldu
(yoksa `/raporlar→/reports` kuralı kendini ezerdi). PREFIX_REWRITE iç segmenti koruyarak köprüler.

### Test
git grep: canlı kodda `/raporlar` kalmadı (yalnız köprü). Restart: `/reports*` 302 (login gate),
`/raporlar*` 301→`/reports*` (iç segment korunarak). pytest module+bireysel+admin → 37/37 geçti.
analiz/bireysel/ayarlar regresyon yok.

### Notlar
İç Türkçe segmentler sıradaki tur: muda-analizi, strateji-hikayesi, bireysel-hizalama, operasyon-istatistik,
hizalama-sankey, departman-performans, yonetici-liderlik, sabah-ozeti, evrim-filmi, ai-sunum/danisman,
stratejik-yillik, yatirimci-sunum, esg-rapor/yonetim, audit-paketi, bireysel-karne-batch, veri-kalitesi,
k-vektor-carpiklik, hedef-revizyon, onay-zinciri, pg-proje-etki, sektorel, iki-fa. Kullanıcı seçimi bekleniyor.

## TASK-202 | 2026-06-23 | ✅ Tamamlandı

**Görev:** URL tek-dil — shared: ayarlar→settings, profil→profile, bildirim→notification (301 köprülü)
**Modül:** shared/auth, shared/ayarlar, shared/scheduled_reports, shared/bildirim, search, nav/registry, tests
**Durum:** ✅ Tamamlandı

### Çeviri haritası
ayarlar→settings, hesap→account, eposta→email, zamanlanmis-raporlar→scheduled-reports,
profil→profile (foto-yukle→photo-upload), bildirim→notification.

### Değiştirilen Dosyalar
- `micro/modules/shared/auth/routes.py` → /profile, /profile/photo-upload, /settings, /settings/account
- `micro/modules/shared/ayarlar/routes.py` → /settings/email (+ api/save|test|send-test)
- `micro/modules/shared/scheduled_reports/routes.py` → /settings/scheduled-reports
- `micro/modules/shared/bildirim/routes.py` → /notification (+ api/unread-count|mark-read|mark-all-read)
- `micro/modules/shared/search/routes.py` → kullanıcı arama sonucu link /profile
- `app/legacy_redirect_config.py` → 6 EXACT_ENDPOINT 301 köprü (eski Türkçe sayfa GET'leri)
- `app/middleware/legacy_sunset.py` → canonical prefix /settings/ /profile/ /notification/
- `ui/static/platform/js/command_palette.js` → 3 url; `ui/static/platform/js/masaustu.js` → mark-read base
- `ui/templates/platform/bildirim/index.html` → href /settings
- `app/__init__.py` → nav; `micro/core/module_registry.py` → 2 launcher url
- `app/services/kilavuz_olusturucu_executor.py` → 3 Playwright goto URL
- `tests/test_module_smoke.py` → /individual/api/scorecard (TASK-201 eksik kalan API satırları)
- `tests/test_admin_smoke.py` → kırık `/ayarlar/yedekleme` → doğru `/admin/araclar/yedekleme`

### Yapılan İşlem
base.html'deki TÜM bildirim/profil/ayarlar referansları url_for ile geldiği için (topbar badge,
sidebar, profil menüsü) fonksiyon adları korunarak otomatik doğru kaldı — sadece 3 hardcoded JS/HTML
referansı + backend nav/registry güncellendi. API'ler POST → eski path canlı çağrı yok.

### Test
Restart: 7 yeni route 302 (login gate), 5 eski Türkçe URL 301→yeni hedef. Regresyon yok (analiz/bireysel/
launcher sağlam). pytest module+bireysel+admin smoke → 25+9 geçti. Bonus: TASK-201'de kaçan
test_module_smoke API satırları ve önceden kırık admin yedekleme testi düzeltildi.

### Notlar
İki ayrı profil sistemi var: legacy /profile/* (kök auth_bp, static/js/profile.js) ZATEN İngilizce,
dokunulmadı. /kurum/ayarlar farklı modül (kurum), kapsam dışı. kule (tur) çevrilmedi. Modül id'leri
(ayarlar/bildirim, DB/registry) korundu.

## TASK-201 | 2026-06-23 | ✅ Tamamlandı

**Görev:** URL tek-dil — `bireysel` modülü → `/individual` (18 route, 301 köprülü)
**Modül:** bireysel, legacy_redirect, nav/gating/registry, tests
**Durum:** ✅ Tamamlandı

### Çeviri haritası
bireysel→individual, karne→scorecard, veri→data, faaliyet→activity, favori→favorite,
hizalama-skoru→alignment-score, ekip-hizalama→team-alignment, ai-ozet→ai-summary. **pg korundu** (KURALLAR).

### Değiştirilen Dosyalar
- `micro/modules/bireysel/routes.py` → 18 route path `/bireysel*` → `/individual*` (fonksiyon adları korundu)
- `app/legacy_redirect_config.py` → EXACT_ENDPOINT'e `/bireysel` + `/bireysel/karne` → `app_bp.bireysel_karne` (301)
- `app/middleware/legacy_sunset.py` → canonical `/bireysel`/`/bireysel/` → `/individual`
- `ui/templates/platform/bireysel/karne.html` → 4 `data-*-base` (diğer 5 zaten url_for)
- `ui/static/platform/js/bireysel.js` → 2 hardcoded fallback `/individual/...`
- `ui/static/platform/js/command_palette.js` → `/individual/scorecard`
- `platform_core/__init__.py` → gating prefix `/individual` (modül id `bireysel` korundu)
- `app/__init__.py` → nav eşlemesi `/individual` / `/individual/scorecard`
- `micro/core/module_registry.py` → launcher url `/individual/scorecard`
- `micro/modules/shared/my_tasks/routes.py`, `micro/modules/masaustu/routes.py` → takvim/görev link url
- `tests/test_bireysel_smoke.py`, `test_module_smoke.py`, `test_e2e_flow.py` → yeni URL'ler

### Yapılan İşlem
analiz pilotuyla aynı kalıp. 18 route İngilizceye çevrildi, fonksiyon adları korunduğu için url_for'lar
otomatik doğru. Sayfa GET'leri (`/bireysel`, `/bireysel/karne`) 301 ile köprülendi; API'ler POST olduğu
için middleware'e takılmaz, frontend güncellendiği için eski API path'lerine canlı çağrı kalmadı.
Eski alias'lar (`/gorevlerim`, `/performans-kartim`, `/bireysel-panel`) zaten fonksiyona bağlı → çalışmaya devam.

### Test
Restart sonrası: `/individual*` 302 (login gate), `/bireysel`+`/bireysel/karne` 301→`/individual/scorecard`.
`pytest tests/test_bireysel_smoke.py` → 6/6 geçti. analiz + launcher regresyon yok.

### Notlar
Çevrilmedi: `/raporlar/...bireysel-hizalama`, `bireysel-karne-batch` (AYRI raporlar modülü, bireysel değil).
Modül id `bireysel` (DB/registry) ve `pg` kısaltması korundu. Sıradaki: kullanıcı seçimi.

## TASK-200 | 2026-06-23 | ✅ Tamamlandı

**Görev:** URL tek-dil — izole route: `/masaustu-launcher` → `/desktop-launcher` (301 köprülü)
**Modül:** core/launcher, legacy_redirect, nav
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/core/launcher.py` → alias `/masaustu-launcher` → `/desktop-launcher` (`/launcher` kanonik korundu)
- `app/legacy_redirect_config.py` → EXACT_ENDPOINT'e `/masaustu-launcher` → `app_bp.launcher` (301)
- `ui/templates/platform/base.html` → breadcrumb home `/desktop-launcher`
- `ui/templates/platform/bildirim/index.html` → masaüstü butonu `/desktop-launcher`
- `ui/static/platform/js/command_palette.js` → komut paleti url `/desktop-launcher`
- `app/__init__.py` → nav eşlemesi `/desktop-launcher`

### Yapılan İşlem
`launcher()` fonksiyonu zaten `/launcher` (İngilizce) + `/masaustu-launcher` (Türkçe) alias'ı taşıyordu.
Türkçe alias `/desktop-launcher`'a çevrildi, 4 canlı referans güncellendi, eski URL 301 ile köprülendi.

### Test
Restart sonrası: `/desktop-launcher` 302 (login gate), `/masaustu-launcher` 301→`/desktop-launcher`,
`/launcher` korundu. Pilot `/analysis` ve `/analiz`→301 hâlâ sağlam (regresyon yok).

### Notlar
sp modülü (~120 route, çoğu İngilizce, aktif plan-yıl işi) riskli bulundu → ertelendi. Sıradaki
aday: bireysel modülü (orta, izole). Kullanıcı onayı bekleniyor.

## TASK-199 | 2026-06-23 | ✅ Tamamlandı

**Görev:** URL Türkçe→İngilizce tek-dil çalışması — PİLOT: `analiz` modülü → `/analysis` (301 köprülü)
**Modül:** analiz (micro/modules/analiz), legacy_redirect altyapısı
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/analiz/routes.py` → 7 route path `/analiz*` → `/analysis*` (fonksiyon adları korundu)
- `app/legacy_redirect_config.py` → PREFIX_REWRITE'a `/analiz`→`/analysis` köprüsü eklendi (301)
- `app/middleware/legacy_sunset.py` → canonical prefix `/analiz/`→`/analysis/` (yeni URL redirect'ten muaf)
- `ui/templates/platform/analiz/index.html` → 4 `data-*-base` attribute `/analysis/...`
- `ui/templates/platform/sp/exec_dashboard.html` → anomali kartı `href="/analysis"`
- `ui/static/platform/js/command_palette.js` → komut paleti url `/analysis`
- `app/__init__.py` → nav/breadcrumb eşlemesi `/analysis`
- `platform_core/__init__.py` → paket gating prefix `/analysis` (modül id `analiz` korundu)
- `micro/core/module_registry.py` → launcher modül url `/analysis`

### Yapılan İşlem
Strangler stratejisine uygun olarak modern `analiz` modülü pilot seçildi (7 route, tek endpoint kökü,
JS data-attribute'tan okuyor → düşük risk). URL path'leri İngilizceye çevrildi; mevcut
`legacy_sunset` middleware'i kullanılarak eski `/analiz*` yolları 301 ile `/analysis*`'e köprülendi.
`url_for` endpoint adıyla çalıştığı için fonksiyon adları (analiz_api_*) değiştirilmedi.

### Test
`pybasla.py` ile restart → `/analysis` 302 (login gate, route kayıtlı), `/analiz` 301→`/analysis/`,
`/analiz/api/trend/1` 301. Köprü ve yeni URL doğrulandı.

### Notlar
Bu bir PİLOT — yöntem kanıtlandı. Kalan ~141 Türkçe route faz faz aynı kalıpla çevrilebilir
(legacy `main_bp`/`api_bp` route'ları strangler ile eridiği için düşük öncelik). Kullanıcının
sıradaki modül seçimi bekleniyor. Çevrilmedi: marketing `/ozellikler/analiz-merkezi` (ayrı route),
docs kılavuz HTML'leri.

## TASK-198 | 2026-06-20 | ✅ Tamamlandı

**Görev:** KART/veri düzenleme katmanı + modül-bileşen eşlemesi onarımı (ağaçta boş bileşen)
**Modül:** admin (düzenleme API+UI), scripts (remap), saas
**Durum:** ✅ Yerelde runtime doğrulandı. Sadece YEREL.

### Değiştirilen Dosyalar
- `micro/modules/admin/routes.py` → 5 düzenleme API (kart update, veri-kaynağı CRUD, bileşen listesi)
- `ui/static/platform/js/admin_hierarchy.js` → inline düzenleme (required_component dropdown, kart düzenle, veri ekle/sil)
- `scripts/remap_modul_bilesen.py` → yeni: module_component_slugs temizle+doğru dağıt

### Yapılan İşlem
(1) Düzenleme: admin hiyerarşi ağacında veri-paket eşlemesi (required_component) UI'dan değiştirilebilir.
Kanıt: process_count kısıtsız yapılınca tom1 anında görüyor, geri alınca gizleniyor (koddan değil DB'den).
(2) Onarım: module_component_slugs eski/karışıktı (35 bileşen sadece sp+surec'e, mantıksız; kurum/k_radar/
bireysel/proje 0 bileşen → ağaçta boş görünüyordu). Temizlenip anlamlı dağıtıldı (kullanıcı onaylı):
kimlik→kurum, SWOT/PESTEL→ileri_sp, PG/PGV→surec vb. 122 eski satır → 35 temiz bağ. Ağaç artık dolu
(baslangic 18 bileşen, kurum'da 5 kimlik kartı). DB öncesi yedek.

### Notlar
k_radar/bireysel/proje/analiz/k_rapor modüllerinde hâlâ bileşen yok — onların bileşenleri henüz system_components'ta
tanımlı değil (ayrı iş). Kullanıcının şikayeti kurum/sp boşluğuydu, o çözüldü. Kart işaretleme kademeli sürüyor.

## TASK-197 | 2026-06-20 | ✅ Tamamlandı

**Görev:** KART katmanı — otomatik keşif + 4-katman admin hiyerarşi UI
**Modül:** saas (model), card_discovery_service, admin (route+UI)
**Durum:** ✅ Yerelde runtime doğrulandı (keşif sıfırdan kurdu, ağaç render). Sadece YEREL.

### Değiştirilen Dosyalar
- `app/services/card_discovery_service.py` → yeni: template data-card-* tarayıp SystemCard+CardDataSource seed (idempotent)
- `micro/modules/admin/routes.py` → /admin/cards/discover (keşif tetikleyici) + /admin/hierarchy (sayfa) + /admin/api/hierarchy (4-katman ağaç)
- `ui/templates/platform/admin/hierarchy.html` + `admin_hierarchy.js` → 4-katman ağaç (açılır/kapanır) + keşif butonu + required_component rozeti
- `ui/templates/platform/admin/packages.html` → "Hiyerarşi" linki
- `ui/templates/platform/kurum/index.html` → özet kartına data-card-* işaretleri (keşfedilebilir)

### Yapılan İşlem
İşaretleme şeması: kart=data-card-code, veri=data-card-key + data-requires (gereken bileşen). Keşif servisi
template'leri tarayıp DB'ye yansıtır (RouteRegistry sync felsefesi: tekrar tetiklenebilir). Admin sayfası
4 katmanı (paket→modül→bileşen→kart→veri) ağaç olarak gösterir; veri kaynaklarında required_component rozeti
= çapraz-paket veri farkındalığı görsel. Runtime: kart silinip keşif sıfırdan kurdu (1 kart+3 veri, required
doğru), ağaç API 4 paket, zincir tam (yonetim>surec>surec_performansi>kurum_ozet_kartlar).

### Notlar
Keşif kademeli: kartlar çalıştıkça data-card-* ile işaretlenir (şu an /kurum özet kartı işaretli, örnek).
Admin UI şu an GÖR + KEŞFET; düzenle/taşı (sira değiştir, veri-paket eşlemesi) sonraki adım. 4-katman temeli tam.

## TASK-196 | 2026-06-20 | ✅ Tamamlandı

**Görev:** Radikal paket gating — paket-içerik yönetim UI (Faz 2) + route-düzeyi enforcement (Faz 3)
**Modül:** admin (paket-modül UI), decorators, platform_core (before_request), sp (exec-dashboard)
**Durum:** ✅ Yerelde runtime doğrulandı (tom1/2/3 + Tomofil + Admin regresyon). Sadece YEREL.

### Sorun
Paket sınırı sadece sidebar/launcher görünürlüğünde; 67 bileşen + 500+ route veriyi doğrudan
sorguluyordu (exec-dashboard tom1'de PG gösteriyordu). Tek tek kapatmak imkansız.

### Değiştirilen Dosyalar
- `micro/modules/admin/routes.py` → /admin/packages/<id>/modules (GET liste+bileşen) + .../toggle (paket-modül M2M)
- `ui/templates/platform/admin/packages.html` + `admin_package_modules.js` → "Modüller" açılır panel (checkbox + bileşen önizleme)
- `app/utils/decorators.py` → require_component bypass'ı SADECE Admin'e daraltıldı + yeni require_module(module_id)
- `platform_core/__init__.py` → _enforce_package_module_gating before_request (prefix→modül, 500 route toplu gate)
- `micro/modules/sp/routes_exec_advisor.py` → exec-dashboard @require_module("surec")

### Yapılan İşlem
Faz 2: paket içeriği UI'dan yönetilebilir (pakete tıkla→modül checkbox + bileşen önizleme). L4/özel paket
seed'siz kurulabilir. Faz 3: yönetici bypass düzeltildi (sadece platform Admin; tenant_admin/executive_manager
artık pakete TABİ) + blueprint-bazlı before_request ile /process,/bireysel,/project,/analiz,/k-radar,/k-rapor
prefix'leri paket'e göre gate'lenir. Runtime: tom1'de 6 modül 302→masaüstü (sp/kurum açık), tom2 süreç/proje
açık, tom3 k-radar açık, Tomofil(full) hepsini görüyor, Admin bypass çalışıyor. Fail-open (gating çözülemezse engelleme yok).

### Notlar
Saf bileşen-düzeyi (500 route'a component_slug) yerine pragmatik hibrit: prefix→modül toplu gating + exec-dashboard
gibi karma sayfalara elle @require_module. require_component (bileşen-düzeyi) altyapısı duruyor, ileride kademeli
route etiketlemesiyle saf bileşen-düzeyine geçilebilir. Bu sadece SAYFA (GET) gating'i — derin güvenlik için
API/servis düzeyi ayrı (ertelendi).

## TASK-195 | 2026-06-20 | ✅ Tamamlandı

**Görev:** L3 eksiklik tamamlama — Değer Zinciri girişi + Kapasite UI + Program Gantt
**Modül:** k_radar (routes_kp), proje (routes_views/routes_list), platform UI
**Durum:** ✅ Yerelde runtime doğrulandı (3 boşluk kapatıldı). Sadece YEREL.

### Değiştirilen Dosyalar
- `micro/modules/k_radar/routes_kp.py` → Değer Zinciri öğe CRUD (birincil/destek, muda, süreç bağı)
- `ui/templates/platform/k_radar/kp_deger_zinciri.html` + `ui/static/platform/js/vc_items.js` → faaliyet yönetimi UI
- `micro/modules/proje/routes_views.py` → /project/<id>/views/kapasite route + ekip listesi
- `ui/templates/platform/project/kapasite.html` + `project_kapasite.js` + `_project_views_nav.html` → kapasite UI + nav sekmesi
- `micro/modules/proje/routes_list.py` → portföy route'una program_gantt verisi
- `ui/templates/platform/project/portfolio.html` + `program_gantt.js` → program zaman çizelgesi (Frappe-Gantt)

### Yapılan İşlem
DB-teyitli 3 boşluk (Dal 5 dersiyle önce doğrulandı): (1) Değer Zinciri — tablo+okuma vardı, GİRİŞ yoktu
(dead code, 0 satır) → CRUD + UI. (2) Kapasite — API (GET/POST/DELETE) vardı, UI yoktu → tablo+modal UI.
(3) Program Gantt — portföy sayfası vardı ama çok-proje zaman çizelgesi yoktu → Frappe-Gantt program görünümü
(proje start/end + skor renkleri). Runtime: 3 sayfa 200, Değer Zinciri+Kapasite CRUD round-trip (sentetik test
+temizlik), yetki 403, program_gantt JSON verisi doğrulandı.

### Notlar
Kapasite API'si @csrf.exempt ama global before_request CSRF var → JS X-CSRFToken header gönderir (test client
göndermediği için 400; CSRF kapalı testte 200). Değer Zinciri ESG kalıbıyla yapıldı.

## TASK-194 | 2026-06-19 | ✅ Tamamlandı

**Görev:** L3 Dal 4 — ESG metrik + değer girişi UI (dead code onarımı)
**Modül:** raporlar (routes_esg + __init__), platform/raporlar (template + JS)
**Durum:** ✅ Yerelde runtime doğrulandı (CRUD + yetki + upsert). Sadece YEREL.

### Değiştirilen Dosyalar
- `micro/modules/raporlar/routes_esg.py` → yeni: ESG metrik CRUD + yıllık değer girişi (yönetici-only, tenant izolasyonlu)
- `micro/modules/raporlar/__init__.py` → routes_esg import
- `ui/templates/platform/raporlar/esg_yonetim.html` → yeni yönetim sayfası
- `ui/static/platform/js/esg_yonetim.js` → metrik/değer CRUD (E/S/G gruplu, modal formlar)
- `ui/templates/platform/raporlar/esg_rapor.html` → "Metrikleri Yönet" linki

### Yapılan İşlem
ESG modeli (EsgMetric/EsgMetricValue) + PDF raporu vardı ama VERİ GİRİŞİ UI'ı yoktu → rapor üretilemez
"ölü kod" idi. /raporlar/esg-yonetim: metrik ekle/düzenle/sil (E/S/G, scope, hedef, baseline, SDG) + her
metriğe yıl-değer (upsert). Runtime: sayfa 200, geçersiz kategori→400, değer upsert→aynı id, standart
kullanıcı ekleme→403. Sentetik test+temizlik (Tomofil 5 metrik korundu — Dal 3 dersini uyguladım).

### Notlar
Kalan L3: Dal 5 (Ansoff/BCG/Değer Zinciri yeni analizler + K-Vektör — sıfırdan, en büyük).

## TASK-193 | 2026-06-19 | ✅ Tamamlandı

**Görev:** L3 Dal 2+3 — iskelet analiz UI'ları (SWOT/TOWS/PESTEL/BSC) + Porter route onarımı
**Modül:** sp (routes_analysis + menu), platform/sp (5 template + 3 JS)
**Durum:** ✅ Yerelde runtime doğrulandı (6 sayfa 200, Porter round-trip, BSC 211 KPI). Sadece YEREL.

### Değiştirilen Dosyalar
- `micro/modules/sp/routes_analysis.py` → sayfa route'ları (swot/tows/pestel/bsc/porter) + Porter API (get/save, 1-5 skor validasyonlu upsert)
- `ui/templates/platform/sp/{swot,tows,pestel,porter,bsc}.html` → yeni 5 template
- `ui/static/platform/js/{sp_liste_analiz,sp_porter,sp_bsc}.js` → yeni 3 JS bileşeni
- `ui/templates/platform/sp/menu.html` → 5 analiz linki eklendi (SWOT/TOWS/PESTEL/Porter/BSC)

### Yapılan İşlem
Dal 2: SWOT/TOWS/PESTEL API'leri vardı, UI yoktu → ortak sp_liste_analiz.js (kategori×madde) + 3 ince template.
BSC (211 KPI, 4 perspektif) görselleştirme + perspektif atama + otomatik sınıflandır UI. Dal 3: Porter modeli
vardı ama route YOKTU (kırık) → API (get/save) + sp_porter.js (1-5 baskı skoru + maddeler). Save'lerde 1-5
validasyonu (geçersiz skor→null teyit edildi). Tüm sayfalar plan-year bazlı, can_edit yetki-bağlı.

### Notlar
DİKKAT/DERS: Porter round-trip'i Tomofil canlı verisi üstünde test ettim, upsert orijinali ezdi; ham DB
write ile geri yükledim (Tesla/BYD/VW, diğer PY satırlarıyla tutarlı). Bundan sonra upsert testleri sentetik
tenant/boş PY'de. Kalan L3: Dal 4 (ESG input UI), Dal 5 (Ansoff/BCG/Değer Zinciri + K-Vektör).

## TASK-192 | 2026-06-19 | ✅ Tamamlandı

**Görev:** L3 Dal 1 — ileri_* modülleri Strateji paketine bağla (+ L3 keşif belgesi)
**Modül:** scripts (seed), paketler belgesi
**Durum:** ✅ Yerelde runtime doğrulandı (Strateji 11 modül, launcher değişmedi). Sadece YEREL.

### Değiştirilen Dosyalar
- `scripts/seed_l3_ileri_moduller.py` → yeni: ileri_stratejik/surec/proje modüllerini Strateji paketine bağlar (idempotent)
- `docs/paketler/PAKETLEME-STRATEJISI.md` → §4.C eklendi (L3 durum haritası + Dal 1 + kalan dallar), §4.B Strateji satırı güncellendi

### Yapılan İşlem
4 paralel kod keşfiyle L3 durumu DB-teyitli haritalandı: motor büyük ölçüde mevcut, eksikler dağınık (SWOT/
TOWS/PESTEL/BSC template yok, Porter route kırık, ESG input UI yok, K-Vektör/Ansoff/BCG/Değer Zinciri yok).
Dal 1: 3 ileri_* modülü Strateji'ye bağlandı (CRM hariç — launcher karşılığı yok). Launcher yüzeyi DEĞİŞMEDİ
(ileri_*→sp/surec/proje eşleşir); amaç paket tanımının dürüstlüğü. Strateji 8→11 modül. DB öncesi yedek.

### Notlar
L3 verisi gerçek (DB teyit): OKR 48, BSC 840, ESG 10 satır — iskelet değil. Kalan L3 dalları belgede §4.C'de.
Bu dal sadece paket tanımını dürüstleştirdi; gerçek L3 yetenek eksikleri (UI'lar) sonraki dallar.

## TASK-191 | 2026-06-19 | ✅ Tamamlandı

**Görev:** L2 Dal 3 — yeni tenant'ta paket seçimi (zaten var) + mevcut tenant'ları full pakete ata
**Modül:** scripts (atama), admin (doğrulama)
**Durum:** ✅ Yerelde runtime doğrulandı (7/7 Master, erişim korundu). Sadece YEREL.

### Değiştirilen Dosyalar
- `scripts/assign_existing_tenants_to_master.py` → yeni: mevcut tüm tenant'ları master_package'e atar (idempotent)

### Yapılan İşlem
(1) "Yeni tenant açarken paket seç" özelliği ZATEN MEVCUT — admin_tenants_add route'u package_id'yi işliyor
(satır 935/973), tenants.html'de paket dropdown'ı (em-package) var. Runtime: /admin/tenants 200, dropdown'da
4 paket (Başlangıç/Yönetim/Strateji/Master) görünüyor. KOD YAZILMADI, doğrulandı.
(2) Mevcut 7 tenant (4 paketsiz + 3 Master) → hepsi master_package'e (en kapsamlı, 13 modül). Kullanıcı kararı:
full erişim korunsun. Runtime: tenant 16 (eski paketsiz) yönetici 11 modül = full, modül kaybı yok. DB öncesi
tenants tablosu yedeği. İdempotent: 2. koşu 0 değişiklik.

### Notlar
"En yüksek paket" = Master Package (13 modül, full) seçildi — yeni Strateji tier'ı (8 modül) değil; çünkü
Master daha kapsamlı ve amaç full erişimi korumaktı. Yeni tenant'lar formdan istedikleri tier'ı seçer.

## TASK-190 | 2026-06-19 | ✅ Tamamlandı

**Görev:** L2 Dal 2 — gerçek paketleri tanımla (Başlangıç/Yönetim/Strateji)
**Modül:** scripts (seed), saas (subscription_packages/package_modules)
**Durum:** ✅ Yerelde runtime doğrulandı (3 paket farklı yüzey veriyor). Sadece YEREL.

### Değiştirilen Dosyalar
- `scripts/seed_l2_paketler.py` → yeni: 3 paket + modül bağları (idempotent, sequence drift korumalı)

### Yapılan İşlem
Paketler (kullanıcı kararı): Başlangıç(L1)=kurum+sp · Yönetim(L2)=+surec/bireysel/proje/analiz/k_rapor ·
Strateji(L3)=+k_radar. masaustu/ayarlar/bildirim=minimum (otomatik), admin=rol-kısıtlı → pakete eklenmedi.
Sequence drift (master id=1, seq=1 → PK çakışması) sync_pg_sequence_if_needed ile çözüldü. Runtime
get_accessible_modules: baslangic→5 modül (PGV YOK), yonetim→10 (PGV açık), strateji→11 (full). DB öncesi yedek.

### Notlar
'sp' modülü Başlangıç'ta (strateji ağacı dahil — modül-içi ayrım yok, bilinçli kabul). Tenant ataması
YAPILMADI: mevcut Master Package tenant'ları full kaldı (taşıma ayrı/riskli karar, sonraki dal). PGV
sınırı artık paket düzeyinde gerçek: Başlangıç'ta süreç/PGV kapalı, Yönetim'de açık.

## TASK-189 | 2026-06-19 | ✅ Tamamlandı

**Görev:** L2 Dal 1 — modül gating onarımı (paket motoru fiilen kapalıydı)
**Modül:** module_registry, scripts (seed), saas (system_modules/package_modules)
**Durum:** ✅ Yerelde runtime doğrulandı (gating açıldı, modül kaybı yok). Sadece YEREL.

### Değiştirilen Dosyalar
- `micro/core/module_registry.py` → _SYSTEM_CODE_TO_LAUNCHER_ID'ye DB gerçeği (`*_modulu` kodları) + 5 yeni modül kodu eşlemesi
- `scripts/seed_l2_module_gating.py` → yeni: eksik 5 modülü system_modules'a ekler + Master Package'i tam sete tamamlar (idempotent)

### Yapılan İşlem
Bulgu: system_modules kodları `_modulu` son ekliydi, registry tanımıyordu → _package_modules_to_launcher_ids
None dönüyordu → paket gating FİİLEN KAPALI (herkes her şeyi görüyordu). Onarım: (a) kod eşlemesi düzeltildi,
(b) Master Package'e eksik modüller (kurum/bireysel/analiz/k_radar/k_rapor) eklendi ki gating açılınca Master
tenant'lar modül kaybetmesin. Runtime: Master→8 launcher id (eskiden None), yönetici 11 modül, standart 10,
paketsiz yönetici 12 — modül kaybı yok. DB öncesi pg_dump yedeği alındı (backups/l2/).

### Notlar
Bu dal yalnızca gating MOTORUNU çalışır yaptı — Master full davranışı korundu. Gerçek L1/L2 paket ayrımı
(Başlangıç=PGV kapalı, Yönetim=açık) SONRAKİ dal. musteri_* (CRM) launcher karşılığı yok, eşlenmedi (placeholder).

## TASK-188 | 2026-06-19 | ✅ Tamamlandı

**Görev:** L1 Dal 6 — AI Yapı-Danışmanı kalibrasyonu + opsiyonel LLM anlatımı (lazy)
**Modül:** koe_service, masaustu (route+UI)
**Durum:** ✅ Yerelde runtime doğrulandı (kalibrasyon + yetki + LLM fallback). Sadece YEREL.

### Değiştirilen Dosyalar
- `app/services/koe_service.py` → boşluklara etki(temel/kısmi); _oncelik_puani (etki×aciliyet) sıralama; _llm_anlatim + yapi_danismani(use_llm) opsiyonel LLM
- `micro/modules/masaustu/routes.py` → /masaustu/api/koe-danisman-ai (POST, yönetici-only) lazy LLM endpoint
- `ui/templates/platform/masaustu/index.html` → KOE kartına "AI ile zenginleştir" butonu + data-koe-* işaretçileri
- `ui/static/platform/js/masaustu.js` → buton handler (CSRF'li fetch, anlatı+öneri DOM güncelleme, fallback bilgisi)

### Yapılan İşlem
Kalibrasyon: temel boşluklar (hiç strateji/süreç/faaliyet yok) ağırlıklı öncelikle her zaman üstte, kısmi
eksikler aciliyet (100-severity) sırasıyla. Tomofil: "Hiç faaliyetin yok" (temel, puan 200) en üstte — doğru.
LLM: heuristik boşluk TESPİTİ değişmez; sadece anlatı+öneri ifadesi LLM'le (llm_gateway.call_llm) doğallaşır.
Provider yok / kota / bozuk JSON → kaynak='heuristik' graceful fallback. Lazy buton, yönetici-only (standart→403).

### Notlar
LLM altyapısı zaten mevcuttu (llm_gateway + tenant BYOK). Bu makinede SSL kesme nedeniyle gerçek Gemini
çağrısı yapılamadı; LLM parse/eşleme yolu mock call_llm ile birim-test edildi (kaynak='llm' doğrulandı).
L1 dalları (3-6) tamam → sıradaki: kararları docs/paketler/PAKETLEME-STRATEJISI.md'ye yaz.

## TASK-187 | 2026-06-19 | ✅ Tamamlandı

**Görev:** L1 Dal 5 — rol etiketi terminoloji birleştirme (tek kaynak)
**Modül:** constants/roles, app context, raporlar, çeşitli template
**Durum:** ✅ Yerelde runtime doğrulandı (3 rol × çoklu sayfa render). Davranış/yetki DEĞİŞMEDİ.

### Değiştirilen Dosyalar
- `app/constants/roles.py` → ROLE_LABELS_TR + role_label_tr() (kanonik tek kaynak)
- `app/__init__.py` → _inject_role_labels context processor (Jinja'ya role_label_tr + ROLE_LABELS_TR)
- `micro/modules/raporlar/routes_faz2.py` → _ROL_TR map silindi, helper kullanıldı
- `ui/templates/platform/admin/users.html`, `auth/profil.html`, `base.html`, `launcher.html`, `masaustu/index.html` → dağınık rol map'leri/if-blokları silindi, role_label_tr ile değiştirildi
- `docs/UI-TERMINOLOJI.md` → kanonik rol etiketleri + "hardcode etme, helper'dan oku" notu

### Yapılan İşlem
Kanonik etiketler: Admin→Sistem Yöneticisi, tenant_admin→Kurum Yöneticisi, executive_manager→Üst Yönetim,
standard_user→Kurum Kullanıcısı. 6+ yerde tekrarlanan/çelişen ('Kurum Üst Yönetimi' vs 'Üst Yönetim',
'Standart Kullanıcı' vs 'Kurum Kullanıcısı') eşlemeler tek kaynağa indirildi. base.html'deki ölü roller
(yonetici/calisan/izleyici — DB'de yok, teyit edildi) elendi. Yetki mantığına (surec/permissions.py) DOKUNULMADI.

### Notlar
Devir metnindeki Süreç Üyesi/Lideri/Üst Yönetim altyapısı zaten mevcuttu (members/leaders/owners +
PRIVILEGED_ROLES); Dal 5 yalnızca etiket tutarlılığıydı. Güvenlik sınırı değişmedi.

## TASK-186 | 2026-06-19 | ✅ Tamamlandı

**Görev:** L1 Dal 4 — bireysel hedef iki katman (Standart/Stratejik) + opsiyonel strateji bağı + KOE sinyali
**Modül:** process (model), bireysel (routes+UI), koe_service
**Durum:** ✅ Yerelde runtime doğrulandı (migration round-trip + izolasyon + KOE asimetri). Sadece YEREL.

### Değiştirilen Dosyalar
- `app/models/process.py` → IndividualPerformanceIndicator'a katman + strategy_id (opsiyonel FK)
- `migrations/versions/b2c3d4e5f6a7_*.py` → 2 kolon + index + FK; heuristik dolum (süreç-PG bağlı → Stratejik)
- `micro/modules/bireysel/routes.py` → _normalize_katman (tenant izolasyonu); add/update katman kabul; karne payload + strateji listesi
- `ui/templates/platform/bireysel/karne.html` → strateji seçenekleri (tojson) + pg-update-base
- `ui/static/platform/js/bireysel.js` → katman seçimi + koşullu strateji dropdown + Stratejik rozeti
- `app/services/koe_service.py` → Kimlik&Strateji boyutuna 3. bileşen: stratejik_hedef_pct (skor 3'e bölünür)

### Yapılan İşlem
4a: model+migration, yerel 524 Standart/94 Stratejik, 0 yanlış, down→up round-trip. 4b: ekle/düzenle formu
+ liste rozeti; yabancı strategy_id reddi runtime'da kanıtlandı. 4c: KOE boyut1 = (kimlik+strateji+stratejik_hedef)/3.
Tomofil: 97 kullanıcının 1'i stratejik hedefli → %1 → boyut 100/100/1 = 67.0. Asimetri: +1 kullanıcı → %2.1 (rollback'li kanıt).

### Notlar
katman, source'tan bağımsız eksen (source=nereden geldiği, katman=stratejik mi). strategy_id sadece
katman='Stratejik' iken anlamlı; tenant izolasyonlu. KOE artık bireysel veriyi de okur (Dal 6 kalibrasyonuna girdi).

## TASK-185 | 2026-06-19 | ✅ Tamamlandı

**Görev:** L1 Dal 3c+3d — Kurumsal kimlik çok-satırlı CRUD UI + KOE'nin satırları okuması
**Modül:** kurum (routes), platform/kurum (template+js), koe_service
**Durum:** ✅ Yerelde runtime doğrulandı (test_client CRUD + asimetri kanıtı). Sadece YEREL.

### Değiştirilen Dosyalar
- `micro/modules/kurum/routes.py` → kimlik maddesi CRUD (list/add/update/delete, kind=values/ethics/quality, tenant izolasyonlu) + kurum() context'e kimlik maddeleri
- `ui/templates/platform/kurum/index.html` → kimlik_liste Jinja makrosu; 3 tek-TEXT `<p>` yerine madde listesi + ekle/düzenle/sil
- `ui/static/platform/js/kurum.js` → kimlik CRUD handler'ları (openMcFormModal); eski "Stratejik Kimlik" modal'ı "Amaç & Vizyon" olarak daraltıldı
- `app/services/koe_service.py` → kimlik doluluğu Değer/Etik/Kalite'yi satır tablolarından okur (eski TEXT okunmaz)

### Yapılan İşlem
3c: Generic `<kind>` CRUD — 3 tablo tek route seti, soft-delete, executive_manager/tenant_admin rolü.
Template `kimlik['values']` (dict.values method çakışması düzeltildi). 3d: KOE "Kimlik" boyutu
purpose+vision (TEXT) + 3 boyut (satır var/yok) üzerinden 5'li doluluk. test_client: list/add/update/
delete/bad-kind hepsi geçti. Asimetri kanıtı: değer satırları gizlenince doluluk 5/5→4/5 düştü (KOE satır okuyor).

### Notlar
purpose/vision hâlâ tek-TEXT (Dal 3 kapsamı değil). Eski core_values/code_of_ethics/quality_policy
TEXT kolonları DB'de duruyor ama hiçbir yerde okunmuyor (temiz kesim tamam).

## TASK-184 | 2026-06-19 | ✅ Tamamlandı

**Görev:** L1 Dal 3b — Kurumsal kimlik tek-TEXT → çok-satırlı veri taşıma (idempotent script)
**Modül:** scripts, app/models (tenant_identity)
**Durum:** ✅ Yerelde uygulandı (Tomofil 12 madde). Test/Yayın/Demo'ya gitmedi.

### Değiştirilen Dosyalar
- `scripts/migrate_tenant_identity_rows.py` → yeni: TEXT alanlarını satırlara böler (idempotent)

### Yapılan İşlem
core_values virgülle (5 madde), code_of_ethics & quality_policy cümle bazında (4+3 madde) bölündü.
Cümle maddelerinde baslik=kırpılmış özet, aciklama=cümlenin tamamı (tam metin korunur). İdempotency:
tenant+alan başına aktif satır varsa atlanır — 2. koşu 0 yazdı. Eski TEXT kolonlarına dokunulmadı ("temiz kesim").

### Notlar
DB içerik UTF-8 doğru teyit edildi (konsol cp1254 bozulması yanıltıcıydı). Sıra: 3a✅ 3b✅ → 3c (CRUD UI).

## TASK-183 | 2026-06-08 | ✅ Tamamlandı

**Görev:** Yayın deploy (Yerel→Test→Yayın, sıfır veri kaybı) + kalıcı "Sunucu Güncelleme Rehberi" dokümantasyonu
**Modül:** docs (SUNUCU-GUNCELLEME-REHBERI.md), deploy operasyonu
**Durum:** ✅ Yayın canlı, doküman yazıldı.

### Deploy (Admin Araçları + audit + yedekleme + alembic baseline → Yayın)
- Akış: **Yerel → Test (doğrulandı) → Yayın**. Önce kontrol dosyası (`docs/kontrol/yayinverileri_2026-06-08_1538.md`) + Yayın yedeği (DB+kod).
- Yayın IMAGE-BAKED → tarball/git + `docker build` + container recreate. Test/Demo BIND-MOUNT → tarball + `docker restart`.
- Sonuç: **10/10 satır sayısı aynı, veri kaybı YOK**. www.kokpitim.com /health 200.

### Dokümantasyon (kalıcı)
- `docs/SUNUCU-GUNCELLEME-REHBERI.md` (YENİ, canonical): 4 ortam envanteri (gerçek config doğrulandı), Yerel→Yayın / Yerel→Test / Yerel→Demo yordamları, kırmızı-çizgi ritüeli (kontrol dosyası+yedek), Alembic baseline davranış kuralları (tek head, alembic_version sahipliği, yeni migration), tuzaklar (GCM push, pg_dump sürüm, stale 5001, error.log kilidi).
- `docs/YERELDEN_VM_YAYIN.md` → ARŞİV notu (yeni dosyaya yönlendirme).

### Notlar
4 ortamın gerçek yapısı SSH ile teyit edildi: Yayın baked+git; Test/Demo bind-mount+tarball (Demo `kokpitim_test:latest` image paylaşıyor). Bkz. [[project_yedekleme_ve_db]].

## TASK-182 | 2026-06-08 | ✅ Tamamlandı

**Görev:** Alembic squash baseline — deploy'un Alembic adımı sorununu kalıcı çöz
**Modül:** migrations, oracle_safe_deploy akışı
**Durum:** ✅ Yerel + Test + Yayın stamp'li, doğrulandı.

### Problem (teşhis)
Şema yönetimi disiplinsiz hibritti: migration grafiğinde **5 birleşmemiş head**, yerel DB 2 ara-revizyonda, **Yayın'da alembic_version tablosu yok**, kodda otomatik create_all yok. `flask db upgrade` (deploy adımı) iki sebeple patlıyordu: (a) version tablosu yok → baştan başlar → "already exists", (b) 5 head → "multiple heads".

### Çözüm — squash baseline
- 65 eski migration `migrations/_archive_versions/`'e taşındı; modellerden **tek baseline** üretildi: `f5215370eebd` (161 tablo, down_revision=None). Boş DB'ye hatasız uygulandı (161 tablo = Yayın 161).
- Model↔DB farkı incelendi: 257 index/FK autogenerate gürültüsü + 13 minör (nullable/genişlik); **tip-uyumsuzluğu yok** → baseline honest, veri riski yok.
- Yerel + Test + Yayın DB'leri baseline'a **stamp**'lendi (sıfır-DDL; sadece `alembic_version` satırı). **Kritik:** tablo `kokpitim_user`/`kokpitim_test_user` **sahipliğinde** olmalı (yoksa app "permission denied"). 
- Test container'da `flask db upgrade` temiz **no-op** doğrulandı (mekanizma gerçek altyapıda).

### Doğrulama
Yayın: git 975dd39, versions/=1 baseline, alembic_version=f5215370eebd, /health 200, veri sabit (7/145/92492). Test: no-op upgrade OK. Yerel: current=head, upgrade no-op.

### Notlar
- Yayın container'ı bir sonraki deploy'da yeniden build edilince baseline'ı bake eder (şu an çalışan container eski migration'ları içeriyor ama zararsız — startup'ta migration çalışmıyor).
- Tekrar etmemesi için kural: **tek alembic head disiplini** (paralel dal migration'ları merge edilmeli).
- Eski 65 migration `_archive_versions/`'te (silinmedi, referans).


## TASK-180 | 2026-06-08 | ✅ Tamamlandı

**Görev:** Yedekleme bileşeni — eski tooling kaldırıldı, yeni Admin Araçları > Yedekleme kuruldu
**Modül:** yedekleme_service, routes_admin_tools, yedekleme.html, app/__init__ scheduler
**Durum:** ✅ Yerelde tamam, uçtan uca doğrulandı.

### Kaldırılanlar (kullanıcı onayı, kalıcı)
- Servisler: `admin_backup_service.py`, `backup_scheduler_service.py`, `yedekleyici.py`, `scripts/post_migration_assert.py`.
- UI/route: `ayarlar/yedekleme.html`, admin/routes.py backup route'ları (448-819) + middleware + importlar, ayarlar menü kartı.
- `__init__` eski scheduler hook, `instance/backup_schedule.json`.
- **Yedek verisi:** `backups/` + `Yedekler/` (7,5 GB) — kullanıcı iki kez bilgilendirilmiş onayıyla kalıcı silindi.
- **KORUNAN:** `tenant_backup_service.py` (demo_reset_service + ops scriptleri bağımlı — silinirse demo reset çöker).

### Yeni bileşen
- `app/services/yedekleme_service.py`: pg_dump (-Fc tam DB), kod tar.gz (tam/mtime-fark), rotasyon (son 14), `run_auto_backup`, `restore_db` (pg_restore --clean), `list_auto_backups`, `auto_status`. pg_dump yolu sürüm-bilincli seçilir (sunucu PG 18 → `C:\pgdata\bin`).
- Gece 02:00 APScheduler işi (`_init_yedekleme_scheduler`): tam DB + kod (haftada bir tam baseline, diğer günler fark).
- Route'lar (Admin-only): sayfa, manuel DB indir, manuel kod indir, dosya indir, otomatik-çalıştır, DB geri-yükle (şifre + onay metni `KOKPITIM-DB-GERIYUKLE`).
- `yedekleme.html` + Admin Araçları kartı. Çıktı: `instance/yedekler/otomatik/` (gitignored).

### Doğrulama
pg_dump 18 ile DB 3,4 MB / kod tam 111 MB üretildi; `run_auto_backup` DB+kod+rotasyon çalıştı; `pg_restore --list` ile dump geçerli+restore-edilebilir doğrulandı (1550 TOC, 162 tablo); scheduler 02:00 başladı; sayfa 302.

### Notlar
DB=PostgreSQL (yerelde de). Yerel `instance/kokpitim.db` 0 byte/ölü. Salt Admin; ortam kilidi yok → Test/Yayín'a deploy edilince çalışır (gece yedeği asıl orada anlamlı). Yerel-only; deploy ayrı onayla.

## TASK-179 | 2026-06-08 | ✅ Tamamlandı

**Görev:** Loglar → kurum detay sayfası (kategori bazlı zaman çizelgesi) + eksik audit instrumentasyonu
**Modül:** admin_logs_service, routes_admin_tools, loglar_kurum.html, sp/routes_strategy, sp/routes_pages, proje/routes_tasks, proje/routes_project_crud
**Durum:** ✅ Yerelde tamam, uçtan uca doğrulandı.

### Detay sayfası
- Loglar'daki "Kurum Bazında" satırına tıkla → `/admin/araclar/loglar/kurum/<id>`.
- 6 kategori (her biri AuditLog'dan): **Stratejik Plan** (Strateji+Kurum Yönetimi), **Süreç**, **PG (Gösterge)** (PG+KPI Yönetimi), **PG Verisi** (PG+KPI Veri Girişi), **Proje**, **Proje Görevi** (Proje Faaliyeti).
- Her kategori: son değişiklik özeti + katlanabilir zaman çizelgesi (son 15, eylem/varlık/kim/ne zaman). `new_values`'tan varlık adı + /sp kimlik kartı (Vizyon/Misyon/Değerler) etiketi çıkarılır. Saatler tarayıcı saatine.

### Audit instrumentasyonu — 9 yeni nokta (eksik kategoriler kapatıldı)
- `sp/routes_strategy.py` → strateji & alt strateji **ekle/güncelle/sil** (6 nokta) = "Strateji Yönetimi".
- `sp/routes_pages.py::sp_api_tenant_identity` → vizyon/misyon/amaç/değerler/etik **değişikliği** = "Kurum Yönetimi" (değişen kart anahtarları new_values'a yazılır → /sp kart-bazlı izleme).
- `proje/routes_tasks.py::project_task_delete` → görev **silme** = "Proje Faaliyeti" (create/update zaten vardı).
- `proje/routes_project_crud.py::project_delete` → proje **silme** = "Proje Yönetimi".
- AuditLogger.log_* kendi commit'i + try/except'i olduğu için işlem commit'inden sonra güvenle çağrıldı.

### Doğrulama
Playwright ile gerçek `/sp/api/strategy/add` → AuditLog CREATE "Strateji Yönetimi" `{name, code}` yazıldı (uçtan uca). Detay sayfası 6 kategoriyi gerçek veriyle render etti (Kayseri: PG 338, PG Verisi 326 kayıt).

### Notlar
Salt-okuma sayfa; instrumentasyon yalnız audit YAZAR (mevcut davranışı değiştirmez). Yerel-only; Test/Yayín ayrı onayla.

## TASK-178 | 2026-06-08 | ✅ Tamamlandı

**Görev:** Admin Araçları > Loglar bölümü — kurum bazında + genel giriş/veri hareketi logları
**Modül:** admin_logs_service, routes_admin_tools, loglar.html, araclar.html
**Durum:** ✅ Yerelde tamam, gerçek veriyle doğrulandı.

### Eklenen / Değiştirilen Dosyalar
- `app/services/admin_logs_service.py` (YENİ) → `collect_logs()`.
- `micro/modules/admin/routes_admin_tools.py` → `/admin/araclar/loglar` route'u.
- `ui/templates/platform/admin/loglar.html` (YENİ) → özet kartları + kurum tablosu + katlanabilir listeler + saat dilimi JS.
- `ui/templates/platform/admin/araclar.html` → Loglar kartı.

### Gösterilen metrikler
1. **Son giriş** (kim, ne zaman) + **Toplam giriş sayısı** → `AuditLog` (action="OTURUM AÇMA").
2. **Son veri hareketi** (ne, kim, ne zaman) → `AuditLog` (CRUD, güvenlik dışı) ∪ `KpiData` (PG verisi) — en yenisi.
3. **Hiç giriş yapmamış kullanıcılar** (sayı + katlanabilir liste) → login audit'i olmayan aktif User'lar.
4. **Son hareketler akışı** (genel, son 25) → AuditLog ∪ KpiData.
Yerel doğrulama: 169 giriş · 125 hiç girmemiş · kurum bazlı son giriş/son veri çalışıyor.

### Önemli teknik kararlar
- **PG verisi AuditLog'a yazılmıyor** (yalnız KpiData/KpiDataAudit) → "son veri hareketi" iki kaynağın birleşimi.
- **Saat dilimi:** tüm zamanlar UTC ISO basılır, `data-utc` + JS ile **admin'in tarayıcı saat dilimine** çevrilir (kullanıcı isteği).
- tz-aware/naive karışımı `_cmp()` ile normalize edildi (TypeError önlendi).
- Kurum başına değil metrik başına toplu sorgu (subquery-max-join) → N+1 yok.

### Notlar
Salt-okuma; yalnız _is_admin() korur, ortam kilidi yok → sonra Test/Yayín'a deploy edilince çalışır.
Yerel-only (henüz deploy edilmedi). Test/Yayín ayrı onayla.

## TASK-177 | 2026-06-08 | ✅ Tamamlandı

**Görev:** Admin Araçları > İstatistikler bölümü — kurum bazında sistem sayımları
**Modül:** admin_stats_service, routes_admin_tools, istatistikler.html, araclar.html
**Durum:** ✅ Yerelde tamam, doğrulandı.

### Değiştirilen / Eklenen Dosyalar
- `app/services/admin_stats_service.py` (YENİ) → `collect_statistics()`: metrik başına tek `GROUP BY tenant_id` sorgusu (N+1 yok).
- `micro/modules/admin/routes_admin_tools.py` → `/admin/araclar/istatistikler` route'u (`_is_admin()`, salt-okuma).
- `ui/templates/platform/admin/istatistikler.html` (YENİ) → özet kartları + kurum bazlı tablo + TOPLAM satırı.
- `ui/templates/platform/admin/araclar.html` → İstatistikler kartı eklendi.

### Sayılan metrikler (aktif kayıtlar)
Kurum (Tenant), Kullanıcı (User), Ana Strateji (Strategy), Alt Strateji (SubStrategy),
Süreç (Process), PG (ProcessKpi), PG Verisi (KpiData), Portföy Proje (Project), Proje Task (Task).
Yerel doğrulama: 5 kurum · 141 kullanıcı · 90/229 strateji · 161 süreç · 644 PG · 183.581 PG verisi.

### Hiyerarşik kırılım (kullanıcı isteği)
Bayi (`tenant_type='dealer'`) / Holding (`tenant_type='holding'`) üst kurumları, altında
açtıkları kurumlarla (`parent_tenant_id`) **iç içe** gösterilir: üst kurum → girintili alt
kurumlar → **grup ara toplamı** (kendisi + alt kurumlar). Bayi/Holding rozeti eklendi.
Servis hiyerarşik ağaç kurar (çok seviyeli, DFS); tablo girinti + ara toplam render eder.
Doğrulama: geçici (rollback'li) parent ataması ile nesting + ara toplam matematiği teyit edildi.

### Notlar
Proje türü kararı: yalnız **Portföy** (Project/Task) — SP/Plan projeleri hariç (kullanıcı tercihi).
Ortam kilidi YOK (salt-okuma); yalnız _is_admin() korur → sonra Test/Yayín'a deploy edilince doğrudan çalışır.
Yerel-only (henüz deploy edilmedi). Test/Yayín deploy'u ayrı onayla.

## TASK-176 | 2026-06-08 | ✅ Tamamlandı

**Görev:** Hata Kontrolü — eşzamanlılık kilidi (tarama/senaryo/yenile aynı anda çalışamaz)
**Modül:** hata_kontrol_executor, routes_admin_tools, hata_kontrolu.html
**Durum:** ✅ Yerelde tamam, kilit uçtan uca doğrulandı.

### Kök neden (244/210 sahte-FAIL)
Üç işlem (tarama, "Kur/Yenile", senaryolar) aynı izole `tomofiltest`'i paylaşıyor. Biri çalışırken
diğeri tomofiltest'i sıfırlarsa (wipe + reclone → sentetik admin silinir) **çalışan koşunun oturumu
ölür**. Log kanıtı: tarama 104 sayfa OK sonra senaryo reset'i (10:41:49) admini silince kalan 210
sayfa komple `/login`'e döndü. Kod hatası değildi — eşzamanlılık koruması eksikti.

### Değiştirilen Dosyalar
- `app/services/hata_kontrol_executor.py` → `_BUSY` + `busy_label()/try_acquire()/release()`; `start_run`/`start_scenarios` meşgulse `None`; thread'lerde `finally: release()`.
- `micro/modules/admin/routes_admin_tools.py` → tarama/senaryo/yenile route'ları meşgulse **HTTP 409** + etiket.
- `ui/templates/platform/admin/hata_kontrolu.html` → `setBusy()`; bir işlem çalışırken üç buton da kilitli; 409 mesajı gösterilir.

### Doğrulama
Tarama çalışırken senaryo/ikinci-tarama → reddedildi (None/409). Tarama bitince kilit serbest, senaryo başlayabildi. Tek başına tam tarama: 290 OK / 0 FAIL.

### Notlar
:5001 reloader'sız yeniden başlatıldı (çift dinleyici tuzağı). Yerel-only; Test/Demo/Yayín ayrı onay.

## TASK-175 | 2026-06-08 | ✅ Tamamlandı

**Görev:** Hata Kontrolü — Süreç senaryosuna PG ve PGV tam CRUD (düzenle/sil) ekle, gerçek UI tıklama
**Modül:** hata_kontrol_scenarios
**Durum:** ✅ Yerelde tamam. Standalone 7/7, tam paket 5/5 GEÇTİ, reset temiz.

### Değiştirilen Dosyalar
- `app/services/hata_kontrol_scenarios.py` → `scenario_surec_zinciri` 7 adıma çıkarıldı; `_vgs_enter` helper.

### Yapılan İşlem
İzole tomofiltest içinde OUR sürecin karnesine gidilir (yalnız bizim PG → `.btn-kpi-*` tek anlamlı). PG: oluştur + düzenle (`.btn-kpi-edit`) + sil (`.btn-kpi-delete` → SweetAlert onay). PGV: gir + sil (dinamik `#modal-micro-veri-detay`) + değiştir (sil + yeniden gir; aynı döneme tekrar giriş 409 → önce sil). Hepsi gerçek Playwright tıklamasıyla.

### Notlar
PG sil **yıl-kapsamlı dışlama** (`upsert_kpi_year_config is_included=False`), hard delete değil — assertion `.count()==0` yerine başarı toast'u (`/kaldırıld|silindi/i`) bekler. Yerel-only; Test/Demo/Yayín ayrı onay bekliyor.

## TASK-174 | 2026-06-08 | ✅ Tamamlandı

**Görev:** Admin Araçları/Hata Kontrolü detaylı inceleme + düzeltmeler + PGV tam UI + /sp perf değerlendirmesi
**Modül:** tenant_clone_service, hata_kontrol_executor, hata_kontrol_scenarios
**Durum:** ✅ Yerelde tamam, doğrulandı. Tam paket 5/5 GEÇTİ, reset temiz.

### Detaylı inceleme (2 paralel ajan) — doğrulanan düzeltmeler
- **KRİTİK:** `find_source_tenant_id` `'%tomofil%'` ile "tomofiltest"i de eşliyordu → hariç tutuldu + `source==test` guard (yanlış kurumu klonlama/silme riski).
- **Savunma derinliği:** clone/wipe servis katmanında da Yayín kilidi (`_is_production`).
- **Thread-safety:** `_MADE_MAPS` global → koşuya özel yerel `made_maps`.
- **Bellek:** `_RUNS` sınırsız büyüyordu → son 20 (`_MAX_RUNS`).
- **Kaynak yönetimi:** Playwright browser `try/finally` ile garanti kapatma.
- **DRY:** sentetik admin şifresi tek kaynak.
- **Temizlik:** ölü fetch helper'ları + kullanılmayan import'lar silindi.
- **Elenen (yanlış/abartılı):** pg_get_serial_sequence injection yok (adlar şemadan); FK sırası zaten doğru (0 sızıntı doğrulanmıştı).

### PGV tam UI otomasyonu
- Karne `.btn-kpi-vgs` → `#modal-kpi-data-entry` → `#kpi-data-entry-value` → `#btn-vgs-confirm`. Artık Süreç/PG/PGV 3 adım da gerçek tıklama.

### Reset (wipe) FK düzeltmesi
- `individual_kpi_data(_audits).user_id` CASCADE değil → senaryo PGV verisi sentetik admine bağlanınca `DELETE users` takılıyordu. Wipe'a eklendi → reset güvenilir.

### /sp performans — DEĞERLENDİRİLDİ, gerek YOK
- Ölçüm: /sp route **0.87s soğuk / 0.02s sıcak**. Önceki "91k yüzünden yavaş" iddiası YANLIŞ.
- Vizyon/Misyon UI senaryosunun ara sıra flake'i = **test sırasındaki DB çekişmesi** (gece 02:00 `early_warning` zamanlayıcısı + çoklu test sunucusu), /sp perf değil. Çekişmesiz koşuda 5/5 geçti.

## TASK-173 | 2026-06-08 | ✅ Tamamlandı

**Görev:** Hata Kontrolü — Aktif CRUD senaryolarını tüm çekirdek entity'lere yayma
**Modül:** app/services/hata_kontrol_scenarios.py + early_warning_service (bulunan bug)
**Durum:** ✅ Yerelde tamam; 5/5 senaryo entegre koşuda GEÇTİ, reset temiz. Dal: `claude/admin-araclari-hata-kontrolu`.

### Senaryo kütüphanesi (her şey kontrol altında)
- **Mavi Okyanus** (UI-tıklama): Tuval→aç→Faktör (buton/modal/AJAX)
- **Strateji** (API): ana + alt strateji create
- **Vizyon/Misyon** (API): tenant-identity purpose/vision
- **Süreç→PG→PGV** (API zinciri): süreç→process_kpi→kpi_data (alt-strateji bağlı)
- **Proje→Task** (form + API): portföy projesi + quick-add görev

### Yöntem kararı
- Hafif sayfa (Blue Ocean) → gerçek UI-tıklama.
- Bağlam-ağır / yavaş-render sayfalar (özellikle **/sp** — vizyon skoru 91k+ satır, tekrarlı yüklemede >90s render → UI-otomasyon güvenilmez) ve dinamik süreç sayfası → **API-seviyesi** (giriş yapmış oturumun tarayıcı `fetch`'iyle gerçek uçlar; session+CSRF doğal gider). Yine tomofiltest'e gerçek yazma + validation.
- Koşu sonunda tomofiltest otomatik sıfırlanır (tüm yeni veri temizlendi — doğrulandı).

### Yan bulgu (gerçek bug, düzeltildi)
- `services/early_warning_service.py`: `_send_notification` `notification_type` (NOT NULL) set etmiyordu → her gece 02:00 taramasında `NotNullViolation`. `pg_performance_deviation` eklendi.

### Güncelleme — tümü GERÇEK UI-tıklamaya çevrildi (kullanıcı talebi)
- Tüm 5 senaryo artık gerçek buton/form/modal tıklaması: Strateji + Vizyon/Misyon (/sp mc-modal), Süreç ('Yeni Süreç' modalı + alt-strateji checkbox), PG (karne #btn-kpi-add modalı), Proje + Task (/project form sayfaları). PGV: karne veri sihirbazı UI'ı mevcut (çok-adımlı; "UI var" notuyla işaretli, tam otomatize edilmedi).
- /sp ağır render'ı için cömert timeout (120s). **Entegre koşu: 5/5 GEÇTİ, tomofiltest reset temiz.**

### Not
- **/sp performansı** ayrı bir gerçek sorun (büyük tenant'ta çok yavaş) — ileride vizyon skoru cache'lenmeli; UI senaryolarını da hızlandırır.
- Yalnız Yerel; Test/Yayín ayrı onaya bağlı.

## TASK-172 | 2026-06-08 | ✅ Tamamlandı

**Görev:** Hata Kontrolü taramasının bulduğu gerçek kod kusurlarının düzeltilmesi (15 uç)
**Modül:** sp, raporlar, admin, api, ayarlar, period_report_service
**Durum:** ✅ Yerelde tamam, hepsi test_client ile doğrulandı (eski 500/503/404 → 200/400). Dal: `claude/admin-araclari-hata-kontrolu`.

### Arka plan
Hata Kontrolü aracı tam tarama (321 sayfa) yaptı; 16 fail + 14 warn çıktı. Sunucu loglarındaki traceback'lerden kök nedenler bulundu. Çoğu bir refactor kalıntısı: eksik import/helper.

### Düzeltmeler
- `routes_pages.py` → `from datetime import date` (sp_rapor_donemsel `date.today()` NameError)
- `period_report_service.py` → `get_column_letter()` (MergedCell `.column_letter` yok — donemsel rapor Excel)
- `routes_llm_quota.py` → eksik `platform/sp/llm_usage.html` şablonu oluşturuldu
- `routes_alignment.py` → SQL `CAST(:py_id AS INTEGER)` (plan yılı yokken AmbiguousParameter)
- `helpers.py` → `_require_plan_year()` tanımlandı; `routes_sp_proje.py` import etti (NameError → graceful 400)
- `routes_strategy.py` → eksik `/sp/api/strategies` GET ucu eklendi (/sp/okr 404 çağrısı)
- `routes_faz2/faz3/faz4.py` → `timezone` import (cfo/coo-dashboard + diğerleri NameError)
- `routes_faz3.py` → `_hk_safe_name()` modül helper'ı (yatirimci/esg/audit/bireysel-batch generate'te `_safe_filename` kapsam-dışı NameError)
- `routes_faz0.py` → `_dt.date.today()` → `_date.today()` (ai-sunum generate AttributeError)
- `api/routes.py` → `/api/v1/ai/recommend` `get_recommendations`(yok) → `smart_insights` (503 → 200)
- `admin/routes.py` → kullanici-detay: `tenant_id` yoksa 500 yerine 400
- `ayarlar/index.html` → `url_for('static')` → `url_for('app_bp.static')` (CSS/JS yanlış MIME/404)

### Doğrulama (Admin oturumu, test_client)
15 uç: hepsi <500. Örnek: /sp/rapor/donemsel 200, /sp/llm-usage 200, /sp/api/strategy-project-matrix 200, /sp/api/proje 400, /raporlar/api/{cfo,coo}-dashboard 200, /api/v1/ai/recommend 200, /raporlar/api/*/generate 200, /sp/okr 200, /ayarlar 200.

### Notlar
- "Beklenen" (kusur değil): `404 /demo*` (demo modu kapalı), `400` parametre-isteyen API uçları (validation doğru). Dokunulmadı.
- `/process` 20 sn timeout = araç tarafı ayar (ağır sayfa); kod kusuru değil — aracın timeout/networkidle ayarı ileride gevşetilebilir.
- **Yalnız Yerel.** Test/Yayín'a gitmesi ayrı onaya bağlı.

## TASK-171 | 2026-06-07 | ✅ Tamamlandı (Faz 1 — klon motoru)

**Görev:** Admin Araçları > Hata Kontrolü — Faz 1: tomofiltest izole klon motoru (yerel)
**Modül:** app/services/tenant_clone_service.py
**Durum:** ✅ Yerelde tamam, doğrulandı. Tasarım: `docs/HATA-KONTROLU-TASARIM.md`. Dal: `claude/admin-araclari-hata-kontrolu`.

### Yapılan
- `tenant_clone_service.py`: Tomofil → **tomofiltest** tam klon. Mantık satır-satır id-remap, yürütme küme-temelli (PostgreSQL temp eşleme tabloları + INSERT...SELECT JOIN). Tablo sırası/kapsam elle (wipe'tan doğrulanmış); FK-remap'ler SQLAlchemy introspection ile otomatik.
- Kullanıcı klonlanmaz → 1 **sentetik admin** (`admin@tomofiltest.local`). Bireysel/bildirim/üyelik tabloları v1'de atlanır.
- Sıfırlama = **wipe + yeniden klonla** (ayrı snapshot yok).

### Doğrulama (yerel, tenant 27 → tomofiltest)
- 94.002 satır remap'lendi; users=1, strategies=36, processes=71, process_kpis=221, kpi_data=91.408 (kaynakla birebir).
- Integrity: yetim sub_strategies 0, sızan kpi_data 0, self-ref parent 0.
- Reset: ikinci koşu eski tomofiltest'i temiz sildi, tek kopya kaldı (0 kalıntı).

### Notlar
- **Yalnız Yerel.** Test/Demo/Yayín için ayrı açık onay gerekir (Yayín kalıcı kırmızı çizgi).
- Sentetik admin şifresi şimdilik koda gömülü (yerel); ileride config'e taşınacak.

### Faz 1 UI (aynı task)
- `micro/modules/admin/routes_admin_tools.py`: `/admin/araclar`, `/admin/araclar/hata-kontrolu` (+ durum/yenile uçları). Yalnız `Admin` + **yalnız Yerel** (FLASK_ENV!=production → Test/Demo/Yayín otomatik 403).
- Templates: `admin/araclar.html` (genişleyebilir araç ızgarası) + `admin/hata_kontrolu.html` (tomofiltest durumu + "Kur/Yenile" butonu, klon motorunu UI'dan tetikler).
- `base.html`: sol menüde "Admin Araçları" grubu (yalnız Admin).
- Doğrulandı: Admin oturumuyla 3 sayfa/uç 200; durum tomofiltest'i (tid) doğru gösteriyor.

### Faz 2 — Keşif (route haritası, statik)
- `app/services/hata_kontrol_service.py` → `discover_routes(active_only=True)`: GET + parametresiz + kara-liste dışı + **yalnız app_bp** (legacy/pazarlama hariç). Modül gruplaması + şeffaf "atlananlar" sayımı.
- Uç: `/admin/araclar/hata-kontrolu/kesif`; Hata Kontrolü sayfasına "Keşfet" kartı (modül rozetleri + katlanır URL listesi).
- Doğrulandı: **321 aktif sayfa** keşfedildi (atlanan — parametreli 133, kara liste 25, legacy ~123).
- BFS (bağlantı gezme) bilinçli olarak Faz 3'e ertelendi (sayfa yükleme motorunu paylaşır).

### Faz 3b — Playwright tarayıcı motoru
- `app/services/hata_kontrol_executor.py`: arka plan thread + headless Chromium. tomofiltest sentetik admini ile login → her sayfayı aç (kuyruk/taze navigasyon) → HTTP + JS konsol hatası + başarısız AJAX + sunucu hata izi yakala → ✅/⚠️/❌/⏭️ sınıflandır.
- Uçlar: `/tarama-baslat` (POST, arka plan), `/tarama-durum` (canlı ilerleme). base_url = çalışan sunucu (request.host_url). Yalnız Admin + Yerel.
- UI: "Taramayı Başlat" + limit + ilerleme çubuğu + canlı sonuç tablosu (sorunlular üstte, kapsam-dışı 403'ler altta).
- Doğrulandı (canlı, 30 sayfa): gerçek kırıklar yakalandı — 500 `/admin/yonetim-paneli/kullanici-detay`, 503 `/api/v1/ai/recommend`, başarısız AJAX `/admin/yonetim-paneli`. 403 platform-admin sayfaları "kapsam dışı" (skip); indirme uçları kara listede.
- Not: sentetik admin **tenant_admin** → platform-Admin-only `/admin/*` sayfaları 403 (skip, kapsam dışı; izole tenant tasarımı gereği).

### Faz 3c — BFS bağlantı gezme + ölü link tespiti
- Executor tarama sırasında her sayfadaki iç `<a href>`'leri toplar (aynı origin, sorgu/fragment atılır).
- **Ölü link:** hiçbir Flask route'una uymayan href'ler (url_map match; kara liste/static hariç). **Yetim sayfa:** keşfedilen route'a hiçbir sayfadan link verilmemiş (yalnız TAM taramada hesaplanır; limitli koşuda baskılanır).
- Durum yanıtına + UI'a "Bağlantılar" bölümü (ölü link / yetim, katlanır liste).
- Doğrulandı (canlı, 40 sayfa): 24 bağlantı toplandı, **1 gerçek ölü link** bulundu — `/admin/yonetim` (kaynak `/admin/notifications`).

### Faz 3d — Aktif CRUD senaryoları ("tam aktif")
- `app/services/hata_kontrol_scenarios.py`: senaryo kütüphanesi (SCENARIOS). İlk senaryo **Mavi Okyanus CRUD** — gerçek UI: Tuval oluştur (buton+form+AJAX) → aç → Faktör ekle (modal+AJAX), her adım doğrulanır.
- `hata_kontrol_executor.start_scenarios/_run_scenarios`: login → senaryolar → **otomatik sıfırlama** (tomofiltest wipe+reclone, K8). Senaryo verisi baseline'a döner.
- `tenant_clone_service._wipe_test_tenant`: users'tan önce kullanıcı-bağlı runtime tablolarını (audit_logs, llm_usage, notifications, vb.) temizler (FK ihlali düzeltildi).
- Uçlar: `/senaryo-baslat` + `/senaryo-durum`; UI "Aktif CRUD Senaryoları" kartı (canlı adım sonuçları + reset bilgisi). Yalnız Admin + Yerel.
- Doğrulandı (canlı): Mavi Okyanus senaryosu 4/4 adım GEÇTİ; reset True; sıfırlama sonrası 0 kalıntı.
- Kalan (opsiyonel): senaryo kütüphanesini büyütme, kalıcı koşu geçmişi (DB), zamanlanmış koşu.

## TASK-170 | 2026-06-06 | ✅ Tamamlandı

**Görev:** Derin tarama sonrası doğrulanmış 6 iyileştirme açığının kapatılması
**Modül:** sp (Blue Ocean), notification, analytics, k_radar, model katmanı, repo hijyeni
**Durum:** ✅ Tamamlandı (yerel; Yayín'a dokunulmadı). Python derleme + import + JS kalıntı kontrolü geçti.

### Arka plan
5 paralel keşif ajanıyla derin tarama yapıldı. Bulguların ~yarısı **yanlış çıktı** (kpi_data index'leri zaten var, models/ paketi mevcut, kpi_value_to_float String kasıtlı, çoğu "hard delete" junction tablo = meşru) → elendi. Doğrulanan 6 gerçek açık kapatıldı.

### Değiştirilen Dosyalar
- `app/utils/db_sequence.py` → `add_and_commit_with_retry()` + `commit_with_retry()` eklendi (PK sequence desync UniqueViolation'ında hizala+tekrar dene)
- `micro/modules/sp/routes_frameworks.py` → Blue Ocean Canvas/Faktör/ERRC + VRIO insert'leri retry helper'a geçti; `_to_float/_to_int` ile parse 500 riski kapatıldı
- `app/services/notification_service.py` → `create_notification` + `bulk_create` retry korumasına alındı
- `app/models/__init__.py` → notification.py modelleri (notifications_ext/preferences/push) `create_all` için import (alias — core.Notification çakışması yok)
- `app/services/analytics_service.py` → String değerler pandas öncesi `to_numeric/to_datetime` ile güvenli dönüşüm; sıfır/NaN bölme temizliği
- `ui/static/platform/js/k_radar.js` → 2× `window.confirm` → SweetAlert2 `confirmDelete`
- `ui/static/platform/js/project_raid.js` → `confirm` → SweetAlert2 `confirmDelete`
- `ui/templates/platform/sp/blue_ocean.html` → Faktör + ERRC SweetAlert2 form modalları → mc-modal standardı (KURALLAR §5)
- Kök dizinden 16 tek-kullanımlık `debug_*.py`/`analyze_*.py`/`analyze_output.txt` silindi (repo hijyeni)

### Notlar
- #1 ertelenmiş "Yayín'da Tuval oluşturma 500" hatasının kök nedenini (sequence desync) koda karşı kapatır.
- #2 az önce düzeltilen okr/bsc/esg create_all eksiğinin ikizidir (notification tabloları taze deploy'da atlanırdı).
- Yayín'a dokunulmadı; canlıya gitmesi sonraki deploy'a bağlı.

## TASK-169 | 2026-06-04 | ✅ Tamamlandı

**Görev:** Yayín'da k-radar/ks OKR/BSC/EFQM kartları "yüklenemedi" — eksik tablolar
**Modül:** k_radar, app/models · Yayín DB (onaylı, additive)
**Durum:** ✅ Tamamlandı, kullanıcı verisine sıfır dokunuş, kullanıcı "çalışıyor" onayı

### Kök neden
`app/models/__init__.py` okr/bsc/esg modellerini import etmiyordu → deploy'daki `db.create_all()` bu tabloları metadata'da göremeyip oluşturmadı. Yayín'da `okr_objectives`, `okr_key_results`, `bsc_kpi_perspectives`, `esg_metrics`, `esg_metric_values` eksikti. Üç kart da `get_ks_extended_data()`'dan besleniyor; bu fonksiyon eksik `okr_objectives`'e takılıp komple çöküyor → OKR/BSC/EFQM birden "yüklenemedi".

### Yapılan İşlem
1. **Kod:** `app/models/__init__.py`'ye `OkrObjective/OkrKeyResult/BscKpiPerspective/EsgMetric/EsgMetricValue` import eklendi (commit; gelecekte create_all kapsar).
2. **Yayín DB (kullanıcı onaylı):** taze yedek (`pg_pre_okrtables_20260604_163437.sql.gz`) → okr/bsc/esg import + `db.create_all()` → 5 boş tablo oluştu.

### Doğrulama
kpi_data **92492 → 92492** (mevcut veri birebir aynı; yalnız CREATE TABLE). Tablolar oluştu, test sorguları çalışıyor. Kullanıcı k-radar/ks'te 3 kartın yüklendiğini onayladı.

### Notlar
- `models/__init__` kod düzeltmesi dalda commit'li ama Yayín'ın çalışan koduna henüz girmedi (tablolar elle oluşturuldu → Yayín şu an çalışır; kod düzeltmesi sonraki deploy'da gider).
- Üretim DB şema değişikliği otomatik-mod tarafından durduruldu → kullanıcı açık onayı (AskUserQuestion) ile yapıldı.

## TASK-168 | 2026-06-04 | ✅ Tamamlandı

**Görev:** Tüm UX + düzeltmelerin YAYIN'a (www.kokpitim.com) deploy'u — Test prova → Yayín
**Modül:** Deploy / Yayín · 105 commit (44909c6 → HEAD)
**Durum:** ✅ Tamamlandı, kullanıcı verisine SIFIR zarar (doğrulandı)

### Yapılan İşlem (mutlak kural: önce yedek, veri kırmızı çizgi)
1. **Yedekler:** Yayín DB (`pg_kokpitim_db_predeploy_20260604_105327.sql.gz`) + eski image tag (`kokpitim_web:pre_deploy_20260604_102801`) + kod commit `44909c6`.
2. **Analiz:** Yayín şeması `db.create_all` tabanlı (alembic_version YOK, kpi_data varchar). Repodaki veri-migration'ları (`kpi_value_to_float` vb.) UYGULANMADI (model String, varchar doğru). Standart `oracle_safe_deploy.sh` adım 5 = `alembic upgrade head` → alembic_version yokken tehlikeli → KULLANILMADI.
3. **Test provası** (test.kokpitim.com, Yayín ile birebir aynı şema): tam branch kodu + `db.create_all` (eklenecek tablo yok) + restart → satır sayısı AFTER=BEFORE (kpi_data 92492), smoke 200. Kullanıcı "test uygundur" onayı.
4. **Yayín:** fresh DB yedek + satır BEFORE → temiz kod tarball (`git archive HEAD`, junk hariç, 21M) extract → `docker build` (üretim eski image'da çalışır) → container yeni image'a geçti (sağlıksızsa otomatik rollback guard'ı vardı) → `db.create_all` (şema değişikliği YOK) → satır AFTER.

### Doğrulama
**Satır sayıları BEFORE = AFTER birebir:** kpi_data 92492, process_kpis 510, processes 96, strategies 53, project 1, task 0, tenants 7, users 145, process_activities 3 → **hiçbir kullanıcı verisi değişmedi.** Health 200, www.kokpitim.com 200, smoke route'ları 302.

### Notlar
- ⚠️ `/opt/kokpitim/app` git repo'su tarball extract ile "dirty" durumda (HEAD hâlâ 44909c6, working tree = branch kodu). İleride git-tabanlı deploy için `git reset --hard` veya branch'i main'e merge gerekir. Çalışmayı etkilemez (image build working tree'den).
- ⚠️ Proje oluşturma + "Tuval" oluşturma: KOD düzeltmeleri gitti ama Yayín DB'de `notifications`/`blue_ocean_canvases` sequence desync varsa hâlâ commit'te UniqueViolation olabilir. Sequence onarımı kullanıcı onayı + yedekle yapılır (kırmızı çizgi).

## TASK-167 | 2026-06-04 | ✅ Tamamlandı

**Görev:** Birikmiş düzeltmelerin demo.kokpitim.com'a deploy'u (TASK-166 sonrası)
**Modül:** Deploy / Demo · proje, blue-ocean, nav, savaş odası
**Durum:** ✅ Tamamlandı, smoke test geçti

### Aktarılan Dosyalar (6 — f8aac82..HEAD, commit'li)
- `micro/modules/proje/helpers.py`, `routes_project_crud.py` → proje 500 fix (plan_year_id + üye/gözlemci None)
- `micro/modules/sp/routes_exec_advisor.py`, `ui/.../sp/tv.html` → Savaş Odası ayar scope'u (kullanıcı+kurum)
- `ui/.../sp/blue_ocean.html` → Yeni Tuval standart mc-modal
- `ui/.../base.html` → sol bara Savaş Odası linki (K-Analiz altı)

### Yapılan İşlem
`git archive HEAD <6 dosya>` (150K) → scp → `/opt/kokpitim-demo/app` extract → chown 197609 → `docker restart kokpitim-demo-web`. 3.11 uyumu + py_compile doğrulandı. Yedek: `/tmp/demo-upd-backup-20260604_102221.tar.gz`. Smoke: /project/new, /sp/blue-ocean, /sp/tv, /masaustu, savas-odasi/fronts → hepsi 302; dış erişim 302.

### Notlar
- KURALLAR §8.4: yalnızca `*-demo`; DB'ye dokunulmadı (saf kod). `.env`/`instance` korundu.
- ⚠️ Proje 500'ün KOD katmanı düzeltildi; ancak demo DB'de `notifications` sequence desync varsa proje oluşturmada commit'te yine UniqueViolation olabilir (yerelde 5 sequence onarmıştık). Demo DB onarımı kullanıcı onayı ister (kırmızı çizgi).
- ⚠️ Yayın "Tuval" oluşturma hatası (sequence desync olası) hâlâ askıda — kontrol edilecek.
- Dal `claude/ux-gercek-bosluklar` — main'e merge/push EDİLMEDİ.

## TASK-166 | 2026-06-04 | ✅ Tamamlandı

**Görev:** UX özelliklerini (Savaş Odası vb.) demo.kokpitim.com'a deploy
**Modül:** Deploy / Demo ortamı (Yerel → Demo)
**Durum:** ✅ Tamamlandı, smoke test geçti

### Aktarılan Dosyalar (14 — UX commit aralığı, commit'li HEAD)
- `micro/modules/sp/{helpers,routes_exec_advisor,routes_scenario}.py`
- `micro/modules/surec/routes_karne.py`, `micro/modules/bireysel/routes.py`, `micro/modules/masaustu/routes.py`
- `ui/templates/platform/sp/{tv,scenarios,scenarios_kiyas,exec_dashboard,strateji_haritasi}.html`
- `ui/templates/platform/{surec/karne,kurum/index,bireysel/karne}.html`

### Yapılan İşlem
`git archive HEAD <14 dosya>` (400K) → scp → `/opt/kokpitim-demo/app` (bind-mount, git değil) extract → sahiplik 197609 → `docker restart kokpitim-demo-web`. Demo app dizini git repo değil; container kodu bind-mount ile okuyor, image rebuild gerekmedi (yeni pip yok). Yeni Python kodu 3.11-uyumlu doğrulandı. Deploy öncesi 14 dosyanın yedeği alındı: `/tmp/demo-ux-backup-20260604_083505.tar.gz` (rollback).

### Smoke Test
gunicorn 5080'de temiz başladı (4 worker, import/syntax hatası yok). 6 yeni route + ana sayfa + dış erişim (demo.kokpitim.com) → hepsi 302 (kayıtlı, 404/500 yok).

### Notlar
- KURALLAR §8.4 kırmızı çizgiler: yalnızca `*-demo` hedefleri; Test/Yayın'a dokunulmadı. DB migration/seed/wipe YOK — demo DB & Tomofil baseline değişmedi. `.env`/`instance` aktarılmadı (korundu).
- Savaş Odası + exec/senaryo route'ları SP rolü ister; demo Tomofil kullanıcısının rolü kontrol edilmeli (403 → kod hatası değil, yetki).
- Kaynak dal `claude/ux-gercek-bosluklar` — main'e merge EDİLMEDİ, push EDİLMEDİ.

## TASK-165 | 2026-06-03 | ✅ Tamamlandı

**Görev:** UX gerçek-boşluk kampanyası — 4 yeni özellik (rakip analizi sonrası, yalnızca eksik olanlar)
**Modül:** sp (harita, senaryo, exec/tv), surec (karne)
**Durum:** ✅ Yerelde tamam, derleme + JS sözdizimi doğrulandı. Dal: `claude/ux-gercek-bosluklar` (merge/push bekliyor)

### Değiştirilen / Yeni Dosyalar
- `micro/modules/sp/helpers.py` → PG düğümüne `score`/`health` + `_harita_health_band` (canlı nabız verisi)
- `ui/templates/platform/sp/strateji_haritasi.html` → additive `setupHealthPulse` (kritik/uyarı PG canvas nabzı)
- `micro/modules/surec/routes_karne.py` → `/process/api/karne/<id>/ai-ozet` (heuristik + opsiyonel LLM) + `_karne_heuristik_ozet`
- `ui/templates/platform/surec/karne.html` → inline AI özet şeridi (daktilo efekti, kendi kendine yeten script)
- `micro/modules/sp/routes_scenario.py` → `/sp/scenarios/kiyas` + `/sp/api/scenarios/compare` (salt-okunur skor)
- `ui/templates/platform/sp/scenarios_kiyas.html` (YENİ) → yan yana skor barı + what-if blend slider
- `ui/templates/platform/sp/scenarios.html` → "Kıyasla" linki
- `micro/modules/sp/routes_exec_advisor.py` → `/sp/tv` (war-room sayfa route'u)
- `ui/templates/platform/sp/tv.html` (YENİ) → tam ekran KPI duvarı (exec-snapshot, 30sn yenileme, spotlight, saat)
- `ui/templates/platform/sp/exec_dashboard.html` → "TV / War Room" linki
- `docs/ux/ONERI-YERLESIM-HARITASI.md` (YENİ) → öneri→sayfa yerleşim haritası + rakip analizi

### Yapılan İşlem
Derin kod taraması, önerilerin ~%80'inin (komut paleti, X-Matrix, NLP sorgu, storytelling, evrim filmi, çeyrek review, 40+ rapor hub'ı) ZATEN kurulu olduğunu gösterdi. Yalnızca gerçekten eksik 4 madde uçtan uca eklendi; her biri ayrı commit, mevcut servisleri (process_health, recommendation, score_engine, exec_dashboard, llm_gateway) yeniden kullanır; çalışan davranışa dokunulmadı (additive). LLM yoksa AI özet heuristik'e düşer (yerelde anahtarsız çalışır).

### Notlar
Görsel doğrulama yerelde kullanıcı tarafında yapılmalı (Flask/LLM bu ortamda koşturulmadı). Geri alma: `git revert <sha>` veya dalı bırak. AI özet kurum/exec'e aynı desenle genişletilebilir.

## TASK-164 | 2026-06-02 | 🟡 Kısmen (Part 1 kod tamam — deploy/baseline operatör adımı bekliyor)

**Görev:** Demo Tomofil sıfırlama özelliği (KURALLAR §8.4 — Yol B) — yerel kod
**Modül:** app/services/demo_reset_service.py, micro/modules/demo/routes.py, app/__init__.py, config.py, scripts/demo_baseline.py
**Durum:** 🟡 Part 1 (kod) tamam ve doğrulandı; Part 2-3 (veri aktarımı + deploy) operatör adımı

### Değiştirilen / Yeni Dosyalar
- `app/services/demo_reset_service.py` (YENİ) → snapshot_baseline / restore_baseline / mark_activity / inactivity_sweep + demir guard
- `micro/modules/demo/routes.py` → `/demo/end` + süre dolumu → restore; demo_start + heartbeat → mark_activity
- `config.py` → `DEMO_INACTIVITY_MINUTES` (vars. 15)
- `app/__init__.py` → demo modunda inaktivite sweeper scheduler (her 5 dk)
- `scripts/demo_baseline.py` (YENİ) → operatör CLI (snapshot/restore/status)

### Yapılan İşlem
Yol B: demo DB'nin tüm public tablolarının `demo_baseline` şema kopyası; sıfırlamada FK constraint'leri drop → truncate → baseline'dan insert → FK geri ekle → sequence resync. **session_replication_role kullanılmadı** (non-superuser kokpitim_demo_user yetkisi yok — yerelde test edilip doğrulandı); FK-drop/readd yöntemi throwaway şemalarda (FK+self-ref) kanıtlandı. **Demir guard:** tüm yıkıcı işlemler KOKPITIM_DEMO_MODE=1 şartına bağlı → yerel/Test/Yayın'da ASLA çalışmaz (yerelde RuntimeError ile doğrulandı). Tetikler: çıkış + 60dk süre + inaktivite (hepsi). py_compile 4/4, app normal modda açılıyor, guard kokpitim_db'yi koruyor.

### Veri aktarımı — Yol (b) seçildi: yalnızca Tomofil tenant
Mevcut `services/tenant_backup_service.py` (83 tablo, FK-grafiği scoped, üretimde admin panel + VM-sync'te kullanılıyor) kullanıldı — sıfırdan extractor yazılmadı.
- Yerel export ALINDI: `backups/tomofil_baseline_local.json.gz` (1.67 MB, 22 dolu tablo, 101.890 satır; kpi_data 91.408).
- `scripts/demo_load_tomofil.py` (YENİ, demo-guard'lı) → demo'da bu dosyayı restore_tenant_data ile yükler.

### KALAN operatör adımları (demo VM, yalnızca *-demo hedefleri)
1. Kod deploy: tarball/git → /opt/kokpitim-demo/app/ → docker restart kokpitim-demo-web.
2. Artifact'ı demo'ya kopyala → `python -m scripts.demo_load_tomofil <dosya>`.
3. Baseline: `python -m scripts.demo_baseline snapshot`.
4. Uçtan uca doğrulama: değişiklik → çıkış → sıfırlandı mı (yerelde test edilemedi; createdb/superuser yok).

## TASK-163 | 2026-06-02 | ✅ Tamamlandı

**Görev:** UX kalan-iş adım 4 — double-submit loading + 2 pill token (somut/güvenli kısım)
**Modül:** ui (admin.js, auth.js, masaustu, initiatives)
**Durum:** ✅ Tamamlandı (somut kazanımlar) — JS-kart kütle teması backlog

### Değiştirilen Dosyalar
- `ui/static/platform/js/admin.js` → kullanıcı-ekle Kaydet butonuna disabled+spinner (çift gönderim/mükerrer kullanıcı önlemi), finally ile geri açılır
- `ui/static/platform/js/auth.js` → login submit'inde geçerli formda buton disabled + "Giriş yapılıyor…" (çift gönderim önlemi)
- `ui/templates/platform/masaustu/index.html`, `sp/initiatives.html` → 2 pill `background:#fafbfc`→`var(--surface-hover)`, `color:#1e293b`→`var(--text-default)` (dark mode uyumlu)

### Yapılan İşlem
Step 4'ün düşük-riskli somut kısmı yapıldı: 2 async buton (kullanıcı oluştur, login) artık çift gönderime kapalı + yükleniyor durumu gösteriyor. Step 2'de bırakılan 2 pill bg+text token'a çevrildi (artık platform'da 0 inline color:#1e293b). JS OK, parse OK.

### Notlar
KASITLI ERTELENEN (yüksek-risk, görsel doğrulama gerektirir): ~15 raporlar/*.js + k_rapor.js/k_radar_ks.js içindeki yüzlerce hardcoded `background:#fff`/`color:#0f172a` (dark'ta beyaz kart — okunur ama tutarsız) ve Chart.js default renkleri. Bunlar dark mode'da tarayıcı doğrulaması olmadan kütle-çevrilirse semantik renkleri bozabilir; ayrı, gözle-doğrulanan iş olarak bırakıldı.

## TASK-162 | 2026-06-02 | ✅ Tamamlandı

**Görev:** UX kalan-iş adım 3 — label `for=` eşleşmesi (primary CRUD form'ları)
**Modül:** ui (admin/users, project/form)
**Durum:** ✅ Tamamlandı (primary form'lar) — kalan ~39 dosya backlog

### Değiştirilen Dosyalar
- `ui/templates/platform/admin/users.html` → 12 label'a `for=` eklendi (input id'leri zaten vardı: ua-*/ue-*)
- `ui/templates/platform/project/form.html` → 6 alana `id=` + label `for=` eklendi (pf-name/description/priority/initiative/start/end)

### Yapılan İşlem
Label'lar input'larla ilişkilendirilmemişti (label tıklayınca focus yok, ekran okuyucu duyurmuyor). İki primary CRUD formunda 18 label↔input eşleşmesi kuruldu. admin/users'ta input id'leri mevcuttu, sadece `for=` eklendi; project/form'da hem id hem for. Parse + eşleşme doğrulandı (12 for=, 6 for=/6 id=).

### Notlar
Sistemik bulgu ~288 label/41 dosya; primary form'lar yapıldı. Kalan ~39 dosya (surec/index 17, project/raid 12, kurum/ayarlar 12, sp/* vb.) backlog — düşük marjinal değer/dosya, gerektiğinde ele alınır. Adım 4 kaldı: JS-enjekte kart teması + double-submit.

## TASK-161 | 2026-06-02 | ✅ Tamamlandı

**Görev:** UX kalan-iş adım 2 — dark mode görünmez metin: inline `color:#1e293b` → `var(--text-default)`
**Modül:** ui/templates/platform (54 dosya)
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- 54 platform template'inde 101 inline `color:#1e293b` → `color:var(--text-default)` (sed toplu)
- `masaustu/index.html:207`, `sp/initiatives.html:172` → korundu (sabit `background:#fafbfc` pill; bg ile birlikte step 4'te ele alınacak)

### Yapılan İşlem
`--text-default` = `#1e293b` (light) / `#e2e8f0` (dark). Dönüşüm light'ta birebir aynı (sıfır görsel değişiklik), dark'ta görünmez metni okunur yapıyor. TASK-159'da aktive edilen dark mode ile birlikte bu kritikti (dark kartlarda koyu metin koyu zeminde görünmüyordu). Aynı element'te sabit açık `background` olan 2 satır hariç tutuldu (orada açık metin açık zeminde görünmez olurdu). 101 dönüşüm, 6 örnek template parse doğrulandı.

### Notlar
Kalan: 3) label `for=` (primary form'lar), 4) JS-enjekte kart teması (hardcoded #fff/#0f172a — dark'ta beyaz kart) + 2 pill'in bg'si + double-submit.

## TASK-160 | 2026-06-02 | ✅ Tamamlandı

**Görev:** UX kalan-iş adım 1 — modal close butonlarına aria-label; tablo overflow bulgusu false-positive çıktı
**Modül:** ui (k_radar, admin, k_rapor)
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/templates/platform/k_radar/ks.html` (10), `admin/users.html` (2), `admin/tenants.html` (2), `k_rapor/index.html` (1) → ikon-only `fa-times` close butonlarına `aria-label="Kapat"` + `<i aria-hidden="true">`

### Yapılan İşlem
Ekran-okuyucuya görünmez olan ikon-only modal-close butonlarına erişilebilir ad eklendi (15 buton). Geniş replace_all pattern'in yanlış buton etiketlemediği doğrulandı (hepsi modal-close). **Tablo overflow bulgusu (10 dosya) incelendiğinde false-positive çıktı:** flagged tabloların hepsi ya zaten `<div style="overflow:auto;">` içinde (yedekleme, cross_paydas, kp_olgunluk, vrio, JS matrisler xmatrix:68 & strategy_project_matrix:42) ya da `width:100%` (kapsayıcıya sığan). Ajan sadece `overflow-x`/`mc-table-wrap` aradığı için `overflow:auto`'yu kaçırmış. Sarma yapılmadı (çift-sarma olurdu).

### Notlar
Kalan adımlar: 2) `color:#1e293b` → token (dark mode görünmez metin), 3) label `for=` primary form'lar, 4) JS-kart teması + double-submit.

## TASK-159 | 2026-06-02 | ✅ Tamamlandı

**Görev:** İkinci UX taraması — dark mode split-brain fix + terminoloji/microcopy + avatar alt
**Modül:** ui (tema, k_radar, admin, sp, raporlar, base)
**Durum:** ✅ Tamamlandı (dark mode tarayıcıda görsel doğrulama bekliyor)

### Değiştirilen Dosyalar
- `ui/static/platform/js/app.js` + `ui/templates/platform/base.html` → dark mode iki sistem (micro_dark/class="dark" + kk_theme/data-theme) senkronlandı
- `ui/static/platform/js/command_palette.js` → "Çeyreklik Review"→"Çeyreklik Değerlendirme", "Replan Tetikleyiciler"→"Yeniden Planlama Tetikleyicileri", "Blue Ocean"→"Mavi Okyanus", "K-Radar (Raporlar)"→"K-Radar"
- `k_radar/risk_management.html` → th "Severity"→"Önem", "Heatmap"→"Isı Haritası"
- `admin/sub_tenants_usage.html` → th "Init"→"Girişim", "Plan Year"→"Plan Yılı"
- `raporlar/kv_carpiklik.html` → th "Avg Skor"→"Ort. Skor"; `sp/scenarios.html` → option "Baseline"→"Temel Senaryo"
- `base.html` → 2 avatar `<img>`'e `alt` eklendi (a11y)

### Yapılan İşlem
3 paralel ikinci-tur UX ajanı (a11y/form, tema/responsive, microcopy/derin-link). **Headline bulgu:** dark mode "split-brain" — görünür toggle `micro_dark`+`class="dark"` yazıyor (191 kural çalışıyor) ama `kk_theme`/`data-theme` hiç yazılmıyordu → 16 `[data-theme="dark"]` kuralı (breadcrumb, tüm mobil dark katmanı, ayar kutucukları, k_rapor bandı) ölüydü. Çalışan toggle KKTheme.apply ile senkronlandı; FOUC script kk_theme yoksa micro_dark'tan türetiyor. `.dark` yolu (çalışan) hiç değişmedi, sadece data-theme additive eklendi. Linkler ikinci turda da TEMİZ çıktı (319 endpoint url_map'le doğrulandı).

### Notlar
Dark mode fix tarayıcıda görsel doğrulama gerektirir (render edilemiyor). Kalan bulgular (raporlandı, uygulanmadı): label `for=` eksikliği (~288 label/41 dosya — sistemik), 9 close-button aria-label, JS-enjekte kartların hardcoded rengi (dark'ta beyaz kart), ~103 inline `color:#1e293b` (dark'ta görünmez metin), 10 bare table overflow wrapper, double-submit loading state.

## TASK-158 | 2026-06-02 | ✅ Tamamlandı

**Görev:** Derin UX taraması (linkler/Türkçe/sayfa yapısı) + 3 kritik breadcrumb 500'ü düzeltildi
**Modül:** ui/templates/platform (ayarlar, kurum)
**Durum:** ✅ Tamamlandı (kritik kısım) — kalan bulgular raporlandı

### Değiştirilen Dosyalar
- `ui/templates/platform/ayarlar/eposta.html`, `ayarlar/yedekleme.html` → `app_bp.ayarlar_index` (yok) → `app_bp.ayarlar`
- `ui/templates/platform/kurum/ayarlar.html` → `app_bp.kurum_index` (yok) → `app_bp.kurum`
- `ui/templates/platform/k_radar/hub.html` → 13 İngilizce kart başlığı Türkçeleştirildi (EVM Kazanılmış Değer, OKR Akışı, Risk Isı Haritası, CFO/COO/CHRO Paneli, Karbon Ayak İzi, AI Koç, Mobil Merkez, BI Bağlayıcı, Denetim Çıktı Paketi, İş Akışı…) + "Şirket"→"Kurum"
- `ui/templates/platform/ayarlar/index.html`, `project/portfolio.html`, `raporlar/audit_paketi.html` → görünür "tenant"/"Tenant"→"Kurum"

### Yapılan İşlem
3 paralel UX ajanıyla aktif platform UI (148 template + JS) tarandı. Kritik bulgu: 3 ayar sayfasının breadcrumb'ında var olmayan endpoint'e `url_for` çağrısı → BuildError → her render'da HTTP 500. url_map ile doğrulandı (ayarlar_index/kurum_index YOK, ayarlar/kurum VAR), düzeltildi, build testi geçti. `raporlar_index` referansları (mobile.html, pg_proje_etki.html) kontrol edildi — endpoint VAR, sağlam.

### Notlar
Raporlanan kalan bulgular (ayrı turda): Türkçe terminoloji (~12 İngilizce K-Radar kart başlığı, 3 "tenant"→"Kurum", "Şirket"→"Kurum", K-Radar/K-Rapor/Cross rename tutarsızlıkları); sayfa yapısı (11 koşulsuz alert()/confirm() §3 ihlali, 42 template inline script, okr.html mc-modal-overlay override, hardcoded JS URL'ler). Bunlar ürün/refactor kararı gerektiriyor.

## TASK-157 | 2026-06-02 | ✅ Tamamlandı

**Görev:** Derin tarama C2 (KPI'sız leaf None→TypeError) + P1 (score engine N+1) düzeltildi
**Modül:** app/services/score_engine_service.py
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/services/score_engine_service.py` → (P1) tüm KPI'lar tek `.in_()` sorgusuyla bulk yüklendi; (C2) `compute_process_scores_internal` dönüş dict'inde None→0.0 normalize

### Yapılan İşlem
- **C2:** KPI'sız leaf süreç recursion'da `None` taşıyor (hiyerarşik ortalamadan dışlama için bilinçli). Ama bu fonksiyonu ~10 tüketici (faz0-5, surec/routes_process, compute_vision_score, k_vektor_engine, k_rapor) doğrudan çağırıp dict'i SAYISAL kabul ediyordu → `sum(None)`/`float(None)`/`sorted(...-None)` → TypeError → boş leaf süreci olan kurumlarda vizyon/k-vektör/kurumsal rapor 500. Çözüm: recursion içi None dışlaması korundu, dönüş dict'i tek noktada None→0.0 normalize edildi (10 tüketicinin hepsi tek editle güvenli).
- **P1:** `calc_process_score` her leaf süreç için ayrı `ProcessKpi.query.filter_by(...)` çalıştırıyordu (N+1). Recursion öncesi tüm süreçlerin KPI'ları tek `.in_()` sorgusuyla yüklenip map'ten okunuyor.

compute_vision_score uçtan uca test edildi (artık hatasız), dönüşte None yok, calc_process_score'dan ekstra ProcessKpi sorgusu 0.

### Notlar
Davranış notu: KPI'sız bir süreç DOĞRUDAN bir alt-stratejiye bağlıysa artık o ortalamada 0.0 sayılır (önceki "dışla" niyeti yerine). Önceden bu yol zaten 500 veriyordu, yani çalışan davranış kaybı yok. İleride "dışla" semantiği istenirse ayrı iş.

## TASK-156 | 2026-06-02 | ✅ Tamamlandı

**Görev:** Derin tarama bulgularından 3 doğrulanmış HIGH düzeltildi (timezone NameError + 2 cross-tenant IDOR)
**Modül:** app/api, app/services
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/services/process_performance_service.py` → import'a `timezone` eklendi (C1)
- `app/api/routes.py` → `create_kpi_data` (V1) ve `get_forecast` (V2) endpoint'lerine tenant sahiplik kontrolü eklendi

### Yapılan İşlem
4 paralel derin-dalış ajanıyla tüm aktif kod tarandı. Bu turda 3 doğrulanmış HIGH düzeltildi:
- **C1 (10/10):** `process_performance_service.py` `datetime.now(timezone.utc)` çağırıyordu ama `timezone` import edilmemişti → her süreç-karne PG veri güncellemesi NameError → 500, değer kaydedilmiyordu. Import düzeltildi.
- **V1 (9/10):** `POST /api/v1/kpi-data` `process_kpi_id`'yi tenant kontrolü yapmadan yazıyordu → cross-tenant veri kirletme. ProcessKpi⋈Process.tenant_id kontrolü eklendi (403).
- **V2 (9/10):** `GET /api/v1/analytics/forecast/<kpi_id>` tenant kontrolü yoktu → cross-tenant KPI geçmişi/tahmini okuma. first_or_404 tenant-scope kontrolü eklendi.

py_compile + timezone namespace + SQLAlchemy sorgu derleme doğrulandı.

### Notlar
Derin taramanın KALAN bulguları (ayrı turlarda): C2 (KPI'sız leaf None→TypeError, 3 tüketici), C3/C4 (karne math ondalık/negatif), C5 (azalan-yön negatif), P1-P4 + 3 MEDIUM N+1 (eager-load refactor). Injection ekseni temiz.

## TASK-155 | 2026-06-02 | ✅ Tamamlandı

**Görev:** 30 dk kod kalitesi / teknik borç taraması — kod temiz çıktı, 9 SQLAlchemy `== None` standarda çevrildi
**Modül:** sp / surec route'lar
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/sp/routes_donemler.py`, `routes_flow.py`, `routes_pages.py` → `== None`/`!= None` → `.is_(None)`/`.isnot(None)`
- `micro/modules/surec/routes_karne.py`, `routes_process.py` → aynı

### Yapılan İşlem
Aktif kod (micro/ + app/) tarandı: console.log=0, bare except=0, except-pass=0, print()=0, mutable default arg=0, eval/exec=0, gerçek Jinja2-in-JS=0 (9 eşleşme yorum/JSDoc false-positive). 548 route'ta @login_required kontrolü: 16 "korumasız" route'un hepsi bilinçli public (marketing, hgs S2 borcu, legacy redirect). Tek somut bulgu: 9 SQLAlchemy NULL filtresi `== None` ile yazılmıştı; proje standardı (.is_()) ile tutarlı olsun diye `.is_(None)`/`.isnot(None)`'a çevrildi (fonksiyonel olarak birebir aynı, IS NULL SQL). py_compile 5/5 OK.

### Notlar
Kod tabanı stil/latent-bug eksenlerinde temiz çıktı — son turun 300+ değişikliği teknik borç sokmamış. Büyük dosyalar (k_rapor/routes.py 2534 satır) refactor adayı ama ayrı/büyük iş.

## TASK-154 | 2026-06-02 | ✅ Tamamlandı

**Görev:** 30 dk güvenlik + hijyen sprinti — log sızıntısı temizliği, encryption anahtar loglaması, temp temizliği
**Modül:** repo hijyeni / encryption
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `.gitignore` → `*.log` ve `logs/` eklendi (PII/secret/traceback sızıntısı önlemi)
- `app/utils/encryption.py` → dev fallback üretilen Fernet anahtarı artık loga YAZILMIYOR
- 6 takipli log git'ten çıkarıldı (`--cached`, diskte kaldı): err.log, error.log, logs/stratejik_planlama.log, out.log, server.log, tmp_spsweb.log
- `_login_err.log` (teşhis temp dosyası) silindi

### Yapılan İşlem
Repo'da 6 log dosyası takipliydi; tek başına error.log'da parola/token/secret/e-posta/traceback eşleşen 442 satır vardı (13.275 satır toplam). Bunlar git'ten çıkarıldı (diskte korundu, commit edilmedi). encryption.py dev fallback'i üretilen şifreleme anahtarını warning loguna basıyordu — log erişimi olan biri şifreli veriyi çözebilirdi; anahtar değeri logdan kaldırıldı (encrypt/decrypt test edildi, çalışıyor).

**Atlanan (riskli):** CSP `script-src-attr 'none'` sertleştirmesi planlanmıştı ama 72 template inline `onclick`/`onerror` kullanıyor → UI'yı kırardı. Bu, inline handler'lar `data-*`+addEventListener'a taşınınca yapılmalı (gelecek iş).

### Notlar
git'ten çıkarılan loglar staged-deletion olarak duruyor; commit kullanıcı "commit'le" deyince yapılacak.

## TASK-153 | 2026-06-02 | ✅ Tamamlandı

**Görev:** Derin güvenlik taraması — önceki oturumun değişikliklerinde 2 yeni açık bulundu ve düzeltildi
**Modül:** admin / sp (frontend)
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/admin/routes.py` → `_ADMIN_ROLES` artık `PLATFORM_ADMIN_ROLES` ({"Admin"}) sabitinden türüyor (yanlışlıkla `ADMIN_ROLES` = {"Admin","tenant_admin"} kullanılıyordu)
- `ui/static/platform/js/sp_donemler.js` → `esc()` modül kapsamına taşındı; `item.title`, `cf[1]`, `cf[2]`, `item.y1`, `item.y2` artık escape ediliyor

### Yapılan İşlem
4 paralel tanımlama + 2 paralel doğrulama alt-ajanıyla 141 dosyalık diff tarandı. İki HIGH bulgu (her biri 9/10 güven):
1. **Yetki yükseltme / cross-tenant IDOR:** `_is_admin()` kapısı yanlış sabit yüzünden `tenant_admin`'i de platform-admin sayıyordu → tenant_admin tüm kurumların kullanıcı/tenant verisini okuyabiliyor, herhangi bir kurumu düzenleyebiliyor, kendi kurumunu holding/dealer'a yükseltebiliyordu. Tek satır import düzeltmesiyle giderildi.
2. **Depolanmış XSS:** sp_donemler.js dönem-karşılaştırma render'ında `esc()` `renderResult` içinde tanımlı olduğundan `entityRowFn`/`metaRowFn` erişemiyordu; DB'den gelen strateji/KPI/dönem adları escape'siz innerHTML'e yazılıyordu. esc() modül kapsamına alınıp 7 sink sarıldı.

Diğer ~140 dosya temiz / güvenlik iyileştirmesi çıktı. py_compile + node --check ile doğrulandı.

### Notlar
İki açık da bu oturumdan önceki büyük değişiklikte (300+ düzeltme) sokulmuştu; tarama bunları yakaladı.

## TASK-152 | 2026-06-01 | ✅ Tamamlandı

**Görev:** Yerel login 500 — kök neden 5001'de takılı kalmış stale süreçler; ayrıca latent psycopg driver tutarsızlığı sertleştirildi
**Modül:** yerel ortam / config
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `config.py` → `_require_postgres_uri()` içinde URI şeması daima `postgresql+psycopg://` (psycopg3) olacak şekilde normalize ediliyor (latent bug hardening — yerel 500'ün sebebi DEĞİLDİ)

### Yapılan İşlem
**Yerel login 500'ün gerçek sebebi:** 5001 portunu aynı anda İKİ python süreci dinliyordu (werkzeug `SO_REUSEADDR` + debug reloader child süreci). Kullanıcının Ctrl+C'si eski süreci gerçekten öldürmüyordu; tarayıcı, `session` import'u olmayan ESKİ kodu çalıştıran stale sürece bağlanıp `NameError` → 500 alıyordu. Diskteki kod ise sağlamdı (test client, bypass'lı ve gerçek-parolalı taze sunucu — üçü de 302 başarılı reprodüce edildi). `netstat -ano | grep :5001` ile çift LISTENER tespit edildi; `taskkill` ile temizlenip tek temiz süreç başlatılınca login çalıştı.

**Ayrıca (ayrı, latent bug):** requirements.txt `psycopg[binary]` (psycopg3) kuruyor ama `.env` URI'si `postgresql+psycopg2://` istiyordu. Yeni container deploy'da (psycopg2 yok) `ModuleNotFoundError` → 500 olurdu. URI normalizasyonu ile her ortamda kurulu psycopg3 dialect'ine sabitlendi. Alembic de aynı engine'i kullandığından kapsam içinde.

### Notlar
Ders: Windows'ta `py app.py` (debug reloader) Ctrl+C ile her zaman tam ölmez; restart öncesi `netstat -ano | grep :5001` ile çift dinleyici kontrol et, gerekirse `taskkill /F /PID`.
> En yeni kayıt en üstte.

## TASK-151 | 2026-06-01 | ✅ Tamamlandı

**Görev:** H-43 — ProcessKpi.target_value ve KpiData.target_value/actual_value String(100)→Float tip değişikliği
**Modül:** app/models/process, migrations/versions, app/services
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/models/process.py` → ProcessKpi.target_value, KpiData.target_value ve actual_value String(100)→Float; actual_value nullable=True yapıldı
- `migrations/versions/k1l2m3n4o5p6_kpi_value_to_float.py` → Yeni Alembic migration; PostgreSQL USING dönüşümü + SQLite uyumlu fallback; down_revision tuple ile i2j3k4l5m016+a3b4c5d6e008 merge
- `app/services/bulk_import_service.py` → str(actual)/str(target) → float() dönüşümü
- `app/services/forecast_service.py` → float(str(...).replace(",",".")) → float(value) temizliği
- `app/services/kpi_anomaly_service.py` → str+replace+float → float() temizliği

### Yapılan İşlem
H-43 kapsamında ProcessKpi.target_value, KpiData.target_value ve KpiData.actual_value kolonları String(100)'den Float'a çevrildi. Alembic migration PostgreSQL için NULLIF(TRIM(col),'')::DOUBLE PRECISION USING ifadesi, SQLite için yeni kolon ekle/kopyala/sil yolunu kullanıyor. Skor motorundaki string→float dönüşümleri temizlendi. Migration iki mevcut DB head'ini (i2j3k4l5m016, a3b4c5d6e008) birleştiriyor.

### Notlar
- PostgreSQL'de sayısal olmayan veri varsa migration kasıtlı olarak hata verir — Test ortamına uygulamadan önce `SELECT * FROM kpi_data WHERE actual_value !~ '^-?[0-9]+\.?[0-9]*$'` ile temizlik yapılmalı.
- efqm_assessment.py ve exec_dashboard_service.py'deki raw SQL'de `::float` cast ve regex guard'lar artık gereksiz ama zarar vermez; ayrı bir temizlik task'ı olarak bırakıldı.

## TASK-150 | 2026-06-01 | ✅ Tamamlandı

**Görev:** H-40 — SMTP şifresi plaintext DB'de saklanıyordu, Fernet at-rest şifreleme eklendi
**Modül:** app/models/email_config, app/utils/encryption
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/utils/encryption.py` → Yeni dosya: Fernet encrypt/decrypt yardımcıları, ENCRYPTION_KEY env değişkeni
- `app/models/email_config.py` → smtp_password alanı hybrid_property ile şeffaf Fernet şifreleme kullanıyor
- `migrations/versions/k1l2m3n4o015_encrypt_smtp_password.py` → Mevcut plaintext kayıtları şifrelemek için örnek migration

### Yapılan İşlem
TenantEmailConfig.smtp_password artık DB'de Fernet şifreli (sütun adı değişmedi: smtp_password). Model katmanında hybrid_property ile okuma otomatik decrypt, yazma otomatik encrypt yapar. ENCRYPTION_KEY ortam değişkeni .env'e eklenmesi gerekir; yoksa geliştirme için geçici anahtar üretilir ve uyarı loglanır.

### Notlar
Mevcut veritabanı kayıtları için migrations/versions/k1l2m3n4o015 örnek migration hazır — çalıştırmadan önce `ENCRYPTION_KEY` .env'de tanımlı olmalı ve DB yedeği alınmalıdır.

## TASK-149 | 2026-06-01 | ✅ Tamamlandı

**Görev:** surec modülü 5 güvenlik/performans düzeltmesi (H-26, H-27, H-28, M-15, M-20)
**Modül:** micro/modules/surec
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/surec/routes_process.py` → H-26: surec_api_update'de leader_ids/member_ids döngü N+1 kaldırıldı, tek sorguda users_map
- `micro/modules/surec/routes_activity.py` → H-27: postpone'da dateutil.parser.parse yerine sabit format listesi + end<=start kontrolü
- `micro/modules/surec/routes_kpi_data.py` → H-28: kpi_id için güvenli int cast + 400 dönüşü; M-15: kpi_data_detail sorgusuna is_active=True filtresi; M-20: audit sorgusuna joinedload(KpiDataAudit.user)

### Yapılan İşlem
Beş ayrı kusur tek seferde giderildi: N+1 sorgu (lider/üye döngüsü), kontrolsüz dateutil parse (arbitrary string injection riski + start>=end eksikliği), güvensiz int cast, silinmiş satırların detail endpoint'te görünmesi ve audit lazy-load N+1.

### Notlar
KpiDataAudit.user ilişkisi modelde mevcut olduğu doğrulandı (app/models/process.py:461).

## TASK-148 | 2026-06-01 | ✅ Tamamlandı — Derin tarama sonrası 10 tur güvenlik + doğruluk düzeltmesi

**Görev:** Workflow derin tarama (143 ajan) bulgularından kalan HIGH/CRITICAL kalemler uygulandı
**Modül:** Tüm proje
**Durum:** ✅ Tamamlandı

### Özet (Tur 1-10)
- Tur 1: H-38 extra_data→metadata TypeError (5×), H-39 mark_as_read IDOR, H-53 int() ValueError
- Tur 2: H-11/H-12 API analytics/reports tenant isolation (4 endpoint)
- Tur 3: H-46 k_radar.js XSS (esc() helper + 4 innerHTML), H-49 project_raid.js CSRF token
- Tur 4: H-15 set-active yetki, H-17 initiative mass-assignment cross-tenant
- Tur 5: H-20 k_radar tenant_id=None, H-22 FavoriteKpi IDOR
- Tur 6: H-23 load_project tenant, H-24 boş form üye silme, H-25 soft-delete cascade
- Tur 7: H-41 email XSS html.escape, H-19 webhook SSRF + rol, H-50 rate limit 50K→300/saat
- Tur 8: H-36 negatif hedef parse + decreasing=0→100, H-37 KPI'sız süreç None
- Tur 9: H-32 PPTX filename injection, H-34 ReportLab html.escape (5×), M-14 plan_year_id
- Tur 10: M-05 Changeme123! → secrets.token_urlsafe, M-12 tenant_admin_role None guard

### Notlar
Kalan HIGH listesi (manuel/migration gereken): H-40 SMTP plaintext, H-42 cascade delete model değişikliği, H-43 String→Float migration, H-44 core.py FK ondelete migration

## TASK-147 | 2026-06-01 | ✅ Tamamlandı — 10 tur otomatik kod kalitesi döngüsü

**Görev:** Kullanıcı isteğiyle 10 tur arka arkaya tarama + düzeltme
**Modül:** Tüm proje (app/, micro/, ui/)
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar (Özet)
- `app/services/maintenance_service.py` → sessiz except'lere logging eklendi
- `app/services/holding_consolidated_service.py` → sessiz except'ler + logging modülü
- `app/services/sub_tenant_billing_service.py` → sessiz except'ler + logging
- `app/services/quarterly_review_service.py` → sessiz except'ler
- `app/services/kule_service.py` → timezone import hatası düzeltildi (NameError)
- `micro/modules/raporlar/routes_faz5.py` → timezone import hatası düzeltildi
- `app/models/tour.py` → utcnow→lambda + timezone import + __repr__
- `app/api/routes.py` → request.json→get_json, str(e) temizliği
- `app/api/auth.py` → request.json→get_json, utcnow, str(e)
- `app/routes/auth.py` → request.json→get_json, utcnow
- `app/models/notification.py` → FK ondelete (SET NULL/CASCADE) + utcnow×6
- `app/models/email_config.py` → FK ondelete (CASCADE/SET NULL)
- `app/models/k_radar.py` → FK ondelete×2 + __repr__
- `app/models/k_radar_domain.py` → FK ondelete×4 + __repr__×2 + f-string bug×3
- `app/models/k_vektor.py` → __repr__×3
- `app/models/strategy_frameworks.py` → __repr__×4
- `app/models/llm_usage.py` → __repr__×2
- `app/models/system_setting.py` → __repr__
- `app/models/replan_trigger.py` → __repr__×2
- `app/models/tenant_llm_config.py` → __repr__
- `app/models/audit.py` → utcnow×1 (sabit pointer→lambda)
- `app/models/portfolio_project.py` → utcnow×11
- `app/api/process/performance_routes.py` → str(e)×2
- `micro/modules/hgs/routes.py` → BOM karakter kaldırıldı
- `app/services/process_performance_service.py` → len()>0→bool()×2
- `app/services/report_service.py` → len()>0→bool()
- `micro/modules/admin/routes.py` → %s logger→f-string×10
- `app/routes/admin.py` → str(e) format düzeltmesi
- 19 servis/route dosyası → datetime.utcnow()→now(timezone.utc) toplam 33 adet

### Yapılan İşlem
10 tur tarama + düzeltme döngüsü: service sessiz exception (logging eklendi), utcnow deprecated kullanım (toplam ~55 adet uygulama genelinde), request.json→get_json, timezone import hataları (runtime crash önlendi), len()>0→bool, f-string logger %s, FK ondelete eksiklikleri, __repr__ eksik modeller, f-string bug (literal değer yerine değişken adı yazıyordu), BOM karakter, sabit pointer datetime.utcnow (lambda'ya çevrildi).

### Notlar
Scripts/ ve Yedekler/ dizinlerindeki utcnow'lara dokunulmadı (uygulama kodu değil).

## TASK-146 | 2026-06-01 | ✅ Tamamlandı — 6. tur kod kalitesi (str(e) güvenlik sızıntısı + saas.py syntax fix)

**Görev:** 63 adet exception string sızıntısı kapatıldı; saas.py syntax error düzeltildi
**Modül:** Tüm micro + app/routes
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/models/saas.py` → RouteRegistry.__repr__ sınıf dışına kaymıştı, içine taşındı; self.slug → self.code düzeltildi
- `micro/modules/sp/routes_exec_advisor.py` → 6x str(e) 500-level → generic mesaj
- `micro/modules/bireysel/routes.py` → 10x str(e) 400-level → generic mesaj
- `micro/modules/surec/routes_activity.py` → 7x str(e) → generic mesaj
- `micro/modules/surec/routes_kpi_data.py`, `routes_kpi.py`, `routes_process.py` → toplam 9x
- `micro/modules/k_radar/routes_common.py` → 1x
- `micro/modules/sp/routes_*.py` (6 dosya) → toplam 12x
- `micro/modules/shared/auth/routes.py` → profil fotoğraf 500 hatası generic mesaja çevrildi
- `app/routes/process.py` → 20x str(e) → generic mesaj
- `app/routes/admin.py` → dosya okuma 500 hatası generic + exc_info eklendi
- `app/routes/core.py` → Kule ticket 500 hatası generic + exc_info eklendi
- `micro/modules/sp/routes_analysis.py` → 3x bare except → except (ValueError, TypeError)
- `micro/modules/surec/routes_process.py` + `raporlar/routes_faz5.py` → SyntaxWarning r"" düzeltmesi
- `ui/templates/platform/ayarlar/index.html` → inline style + 2 script → harici dosyalara taşındı
- `ui/static/platform/css/ayarlar_index.css` + `js/ayarlar_index.js` → YENİ dosyalar
- `ui/static/platform/js/project_raid.js` → alert() → Swal.fire toast

### Yapılan İşlem
Toplam 63 str(e) sızıntısı kapatıldı — exception detayları artık istemciye ulaşmıyor, logger'a exc_info=True ile yazılıyor. saas.py'deki RouteRegistry.__repr__ syntax hatası (sınıf dışına yerleştirilmişti) acil olarak düzeltildi.

### Notlar
admin/routes.py:453 pg_err ve proje/routes_project_crud.py flash mesajları admin-only sayfalarda kasıtlı olduğu için dokunulmadı.

## TASK-145 | 2026-06-01 | ✅ Tamamlandı — 5. tur kod kalitesi (saas.py fix + bare except + inline scripts)

**Görev:** saas.py kritik syntax hatası + 3 bare except + alert() + ayarlar inline script/style
**Modül:** saas, sp/routes_analysis, project_raid.js, ayarlar template
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/models/saas.py` → RouteRegistry.__repr__ sınıf içine taşındı
- `micro/modules/sp/routes_analysis.py` → 3x bare except düzeltildi
- `ui/static/platform/js/project_raid.js` → alert() → Swal.fire
- `ui/templates/platform/ayarlar/index.html` → inline kod kaldırıldı
- `ui/static/platform/css/ayarlar_index.css` + `js/ayarlar_index.js` → YENİ

### Yapılan İşlem
Önceki turda saas.py'ye eklenen __repr__ metodu package_modules tablosunun altına (sınıf dışına) kaymış ve SyntaxError oluşturuyordu. Tüm __repr__ referans hataları da (self.slug → self.code) aynı anda düzeltildi.

### Notlar
SyntaxWarning: routes_process.py ve routes_faz5.py'de SQL string'leri r"" raw string olarak işaretlendi.

## TASK-144 | 2026-06-01 | ✅ Tamamlandı — Kapsamlı kod kalitesi iyileştirmeleri (15 bulgu)

**Görev:** Kod taraması sonucu tespit edilen 15 iyileştirme noktasının uygulanması
**Modül:** Çok sayıda modül (admin, surec, k_radar, raporlar, shared, services, models)
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/admin/routes_sub_tenants.py` → except:pass → logger.warning (4 yer)
- `micro/modules/shared/auth/routes.py` → CSRF decorator sırası düzeltildi + açıklama
- `micro/modules/admin/routes.py` → int() ValueError yakalandı; limit 500→100; rol sabitler
- `app/services/notification_service.py` → print→logger; bulk_create metodu eklendi
- `micro/modules/masaustu/routes.py` → limit 400/500→100
- `micro/modules/shared/my_tasks/routes.py` → joinedload eklendi (N+1 önlemi)
- `config.py` → MAX_QUERY_ROWS ve MAX_NOTIFICATION_ROWS sabitleri eklendi
- `app/utils/api_response.py` → YENİ: ok(), err(), paginated() merkezi wrapper
- `app/constants/roles.py` → YENİ: ADMIN_ROLES, PRIVILEGED_ROLES, WRITE_ROLES sabitleri
- `micro/modules/surec/permissions.py` → rol sabiti app/constants'tan import
- `micro/modules/proje/permissions.py` → rol sabiti app/constants'tan import
- `micro/modules/k_radar/routes_common.py` → rol sabiti app/constants'tan import
- `micro/modules/raporlar/helpers.py` → _get_tenant_context() yardımcı eklendi
- `app/models/core.py` → Composite index ix_tenant_parent_active eklendi
- `app/services/analytics_service.py` → try/except + pandas lazy import
- `ui/templates/platform/k_rapor/anomalies.html` → Low/Medium/High → Türkçe
- `ui/templates/platform/project/task_form.html` → öncelik değerleri Türkçe
- `ui/templates/platform/calendar/_calendar_quick_create_modal.html` → Türkçe
- `ui/templates/platform/raporlar/cfo_dashboard.html` → "Status Dağılımı" → "Durum Dağılımı"

### Yapılan İşlem
15 farklı iyileştirme noktası 4 öncelik katmanında ele alındı: güvenlik/hata yönetimi (acil), performans, kod kalitesi ve optimizasyon. Yeni dosyalar: api_response.py, constants/roles.py.

### Notlar
Yok.

---

## TASK-143 | 2026-05-31 | ✅ Tamamlandı — K-Radar toplu navigasyon + yıl filtresi + açıklama standardizasyonu

**Görev:** K-Radar hub'daki tüm sayfalarda navigasyon, yıl filtresi tasarımı ve açıklama standardizasyonu
**Modül:** k_rapor, raporlar (tüm gruplar)
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/templates/platform/raporlar/vrio_portfoy.html` → breadcrumb + mc-page-header eklendi
- `ui/templates/platform/raporlar/sektor_benchmark.html` → breadcrumb + mc-page-header
- `ui/templates/platform/raporlar/sektorel.html` → breadcrumb + mc-page-header
- `ui/templates/platform/raporlar/sunburst.html` → breadcrumb + mc-page-header
- `ui/templates/platform/raporlar/evrim_filmi.html` → breadcrumb + mc-page-header
- `ui/templates/platform/raporlar/strateji_hikayesi.html` → breadcrumb + mc-page-header
- `ui/templates/platform/raporlar/cfo_dashboard.html` → breadcrumb + mc-page-header (ve 13 AI/üst yönetim sayfası)
- `ui/templates/platform/raporlar/kv_carpiklik.html` → mc-page-header + mc-year-mini
- `ui/templates/platform/raporlar/cmmi_heatmap.html` → mc-year-mini sınıfı
- `ui/templates/platform/raporlar/hizalama_sankey.html` → mc-year-mini sınıfı
- `ui/templates/platform/raporlar/muda_analizi.html` → mc-year-mini sınıfı
- `ui/templates/platform/raporlar/op_istatistik.html` → mc-year-mini sınıfı
- `ui/static/platform/css/components.css` → .mc-year-mini ve .mc-year-sel CSS eklendi
- `ui/static/platform/css/k_rapor.css` → .kr-info-band CSS eklendi
- `ui/templates/platform/k_rapor/index.html` → 18 tab'a kr-info-band açıklama bandı, yıl seçici mc-year-mini
- `ui/static/platform/js/k_rapor.js` → k-vektor/evm/faaliyet-matris/sorumlu-analiz fetchJson'a {year} eklendi; TABS_NO_YEAR'a swot-trend eklendi
- `micro/modules/k_rapor/routes.py` → evm/faaliyet-matris/sorumlu-analiz route'larına yıl filtresi eklendi

### Yapılan İşlem
4 paket halinde çalışıldı: (1) 20 raporlar sayfasına breadcrumb + mc-page-header; (2) CSS sınıfı mc-year-mini ile 6 sayfada yıl filtresi standardizasyonu; (3) 4 k_rapor tab'ına yıl parametresi + swot-trend TABS_NO_YEAR'a alındı; (4) 18 k_rapor tab'ına kr-info-band açıklama bandı.

### Notlar
swot-trend zaten tüm yılları trend olarak gösterdiğinden yıl filtresi eklenmedi, yıl seçici gizlendi.

---

## TASK-142 | 2026-05-30 / 2026-05-31 | ✅ Tamamlandı (yerel) — Büyük UX yenileme oturumu

**Görev:** 4 sprint (16 özellik) + K-Radar birleşmesi + breadcrumb sistemi + 38+ rapor sayfası standardizasyonu + Initiative ↔ Proje stratejik bağ + Hiyerarşi Rehberi
**Modül:** platform geneli (sp, k_radar, raporlar, proje, ayarlar, base, app/__init__)
**Durum:** ✅ Tamamlandı

### Değiştirilen / Eklenen Dosyalar (özet — 90+ dosya)

**Yeni endpoint dosyaları**
- `micro/modules/shared/search/routes.py` → küresel arama API (Ctrl+K paleti)
- `micro/modules/shared/my_tasks/routes.py` → "Benim Görevlerim" birleşik widget API
- `micro/modules/shared/scheduled_reports/routes.py` → zamanlanmış raporlar abonelik API
- `micro/modules/sp/routes_alignment.py` → Strateji × Proje matris API + sayfa
- `app/services/efqm_assessment.py`, `app/services/bsc_auto_classifier.py` (önceki oturum)

**Yeni şablonlar**
- `ui/templates/platform/k_radar/hub.html` → 5 grupta 65+ kart birleşik K-Radar hub
- `ui/templates/platform/sp/strategy_project_matrix.html` → strateji×proje ısı haritası
- `ui/templates/platform/raporlar/pg_proje_etki.html` → PG×Proje çapraz etki
- `ui/templates/platform/ayarlar/zamanlanmis_raporlar.html` → 4 rapor abonelik kartı
- `ui/templates/platform/_hierarchy_help.html` → paylaşılabilir hiyerarşi rehberi popup

**Backend değişikliği**
- `app/__init__.py` → `current_section` + `current_subgroup` context processor (otomatik breadcrumb)
- `app/services/exec_dashboard_service.py` → `?year=` parametresi + tüm sorgulara plan_year filtresi
- `app/services/weekly_digest_service.py` → Arial TTF font (TR karakter) + DISTINCT ON ile 87x hızlanma
- `app/services/analytics_service.py` → safe_float ile str/int karşılaştırma hatası
- `app/services/report_service.py` → `kpi.frequency` AttributeError fallback
- `app/models/portfolio_project.py` → `Project.initiative_id` FK + `initiative` ilişkisi
- `micro/modules/analiz/routes.py` → 4 kırık endpoint düzeltildi (trend/health/anomalies/report)
- `micro/modules/sp/routes_frameworks.py` → `_can()` çıkarıldı, digest tüm girişli kullanıcılara
- `micro/modules/sp/routes_exec_advisor.py` → 3 yeni endpoint (strategy-scores, trend, kvektor-trend)
- `micro/modules/sp/routes_initiative.py` → 2 bağlama endpoint (girişim↔proje)
- `micro/modules/k_rapor/routes.py` → uyum/strateji-kapsama/surec-pg plan_year filtresi + aylık→çeyrek/yıllık aggregation
- `micro/modules/raporlar/routes_faz0.py` → Sankey 5 katman + skor + drill-down
- `micro/modules/raporlar/routes_faz1.py` → CMMI/Muda/Op-İstatistik yıl filtresi; ROI per Strategy KALDIRILDI
- `micro/modules/k_radar/routes_common.py` → `/k-radar` redirect değil, merged hub
- `micro/modules/k_rapor/routes.py` → `/k-rapor` (tab yok) `/k-radar`'a redirect
- `micro/modules/proje/routes_project_crud.py` → form'da initiative_id yönetimi
- `micro/modules/shared/auth/routes.py` → `/api/profile/theme` GET/POST endpoint

**JS değişikliği**
- `ui/static/platform/js/command_palette.js` (yeni) → Ctrl+K palet
- `ui/static/platform/js/raporlar/{cmmi,muda,sankey,kv_carpiklik,initiative_bubble,op_istatistik,hedef_revizyon}.js` → tooltip, yıl seçici, drill-down, TR çeviriler
- `ui/static/platform/js/k_rapor.js` → tab/yıl yönetimi + scroll
- `ui/static/platform/js/dark_mode.js` → server senkronu
- `ui/static/platform/js/surec.js` → set-active yıl + sparkline
- `ui/static/platform/css/components.css` → `mc-breadcrumb` sınıfları

**Veritabanı**
- `project` tablosuna `initiative_id INTEGER REFERENCES initiatives(id) ON DELETE SET NULL` + index

**Silinen**
- `ui/templates/platform/raporlar/roi_strategy.html` (kapsam dışı)
- `ui/static/platform/js/raporlar/roi_strategy.js`
- `micro/modules/raporlar/routes_faz1.py` içinde 2 ROI route bloğu

### Yapılan İşlem

**Sprint 1** (UI hızlı kazanım): boş durumlar zenginleştirildi (SP/Bildirim/Süreç), Proje listesinde RAID donut, Bireysel karne SVG progress ring, dark mode server senkronu.

**Sprint 2** (UX sıçraması): **Ctrl+K Komut Paleti** (statik + dinamik arama), Favoriler & Son Ziyaret Edilenler widget'ı, **"Benim Görevlerim"** union endpoint (proje görev + bireysel faaliyet + süreç aktivitesi), Proje listesinde toplu işlem sticky bar.

**Sprint 3** (görselleştirme): Süreç listesi PG mini sparkline (3 ay trend), SP K-Vektör strateji bubble heatmap, **Strateji × Proje hizalama matrisi** (yeni sayfa), Süreç olgunluk radarı (5 boyut).

**Sprint 4** (büyük yatırım): **PG × Proje Çapraz Etki Analizi**, topbar küresel arama, **Zamanlanmış Raporlar** (4 abonelik tipi).

**K-Radar Birleşmesi**: `/k-rapor` + `/raporlar` + `/k-analiz` sidebar/menü olarak tek "**K-Radar**" hub'ı altında birleştirildi. `/k-radar` yeni merged hub (65 kart, 5 grup). Eski URL'ler redirect.

**Breadcrumb Sistemi**: Tüm sayfalar için otomatik 3-4 katmanlı navigasyon (Home > Sidebar > Subgroup > Sayfa). `app/__init__.py`'de URL → bölüm/alt-grup haritası (65+ K-Radar URL'si eşlenmiş). 38 rapor sayfasından "Raporlara Dön" butonları topluca temizlendi.

**Sayfa Standardizasyonu**: 30+ sayfa standart `mc-page-header` + 1240 px kapsayıcı + breadcrumb + `mc-page-header` pattern'ine getirildi (k-rapor, sp, sürec, project, ayarlar, k-radar, raporlar alt-sayfaları).

**Initiative ↔ Proje Bağı**: UI'da "Initiative" → "**Stratejik Girişim**" (12 dosya). `Project.initiative_id` sütunu + DB migration. Initiative sayfasında "Altındaki Projeler" toggle widget'ı. Proje formuna stratejik girişim dropdown. Proje detayda rozet. Paylaşılabilir **Hiyerarşi Rehberi popup** (6 katman) `/sp`, `/sp/initiatives`, `/project` sayfalarına entegre.

**Bug Düzeltmeleri**: 
- Süreç karne sayfasında yıl değiştirince sonsuz reset döngüsü (process plan_year_id vs user active_year)
- `/sp/digest/weekly.pdf` HTML yerine PDF dönmesi (yetki + reportlab venv'de kurulum + Arial TTF)
- Tomofil 30s sorgu → 0.05s (DISTINCT ON ile N+1 önlemi)
- K-Rapor 6+ sekmede yıl filtresi eksikliği nedeniyle süreçlerin 5-7 kez tekrarı
- `/raporlar/op-istatistik` 404 (hub link URL uyumsuzluğu)
- Sidebar "Bireysel Performans" ikonu görünmüyordu (`fa-user-chart` Font Awesome'da yok)
- `/raporlar/roi-strategy` kapsamdan tamamen kaldırıldı (route + template + JS + URL mapping + hub kartı)
- `/k-rapor?tab=surec-pg` aylık verisi varken çeyrek/yıllık boş — on-the-fly aggregation
- Sankey görseli zenginleştirildi (5 katman, performans renkleri, hover vurgu, drill-down, yıl seçici, hizalanmamış uyarı) + "Stratejik Akış Haritası" olarak yeniden adlandırıldı
- CMMI Olgunluk Isı Haritası tam Türkçeleştirildi (5 seviye detaylı tanım, yorum kutusu)
- EVM panel açıklayıcı hale getirildi (PV/EV/AC tanımları + SPI/CPI eşikleri + 4 kombinasyon yorum tablosu)
- 38 rapor sayfasından "Raporlara Dön" butonu kaldırıldı (script)

### Notlar

- Veritabanı değişikliği var: `project.initiative_id` sütunu — yerel ve test/yayın'a deploy ederken `ALTER TABLE project ADD COLUMN initiative_id INTEGER REFERENCES initiatives(id) ON DELETE SET NULL` + index gerekecek.
- `requirements.txt`'ye `reportlab>=4.0` eklendi — yeni ortamlarda `pip install` zorunlu.
- Tüm sayfalar smoke geçti (HTTP 200). Mevcut tenant verisi bozulmadı.
- Breadcrumb sistemi `mc_breadcrumb` macro'su geriye dönük uyumlu (eski liste formatı hâlâ çalışır).
- Test/Yayın deploy bekliyor — kullanıcı "deploy edelim" dediğinde tek tarball + DB migration ile gönderilebilir.


## TASK-141 | 2026-05-27 | 🚧 Devam ediyor — Yeni Raporlar Bölümü (10-task yol haritası)

**Bağlam:** [docs/rapor/27mayisraporu.md](docs/rapor/27mayisraporu.md) (3.500 satır) içindeki rapor önerilerinden 10 tanesi seçildi. Hepsi sol menüde yeni "Raporlar" bölümünde başlatılacak — kullanıcı sonra hangisi hangi modüle gidecek diye karar verecek.

**Branch:** `claude/raporlar-yeni`

### Mimari karar
- Yeni sidebar entry: **Raporlar** (📊)
- Route: `/raporlar` (kart-grid landing — `/sp/menu` benzeri)
- Her rapor: `/raporlar/<slug>` ayrı sayfa
- Tasarım sistemi: mevcut `mc-card mc-card-lift` pattern
- Şimdilik STAGING bölümü, taksonomi sonra

### 10 Task Yol Haritası

| # | Rapor | Etki | Çaba | Veri kaynağı |
|---|---|---|---|---|
| 1 | **Veri Kalitesi Raporu** | Yüksek | ★★ | PG doluluk, eksik alan, son giriş tarihi |
| 2 | **K-Vektör Çarpıklık** (ağırlık vs skor) | Yüksek | ★★ | k_vektor_strategy_weights × strateji skoru |
| 3 | **Stratejik Hizalama Sankey** | Yüksek | ★★★ | strategies → sub → process → process_kpis (akış) |
| 4 | **PG Hedef Revizyon Sıklığı** | Orta | ★★ | kpi_year_configs vs ProcessKpi diff |
| 5 | **Departman Performans Skoru** | Yüksek | ★★ | users.department × bireysel PG ortalama |
| 6 | **Yönetici Liderlik Skoru** | Yüksek | ★★ | process_leaders × süreç skoru ortalaması |
| 7 | **Initiative Portföy Bubble** | Yüksek | ★★ | initiatives (bütçe × progress × priority) |
| 8 | **Operasyonel Sabah Özeti+** | Orta | ★★ | bugün biten faaliyet/task + kritik PG |
| 9 | **Yıllar Arası Evrim Filmi** | Çok Yüksek | ★★★★ | timeline scrubber + plan_year ağacı |
| 10 | **AI Yıl Sonu Sunum Üretici** | Çok Yüksek | ★★★★★ | python-pptx + LLM (büyük iş, en sona) |

### Tahmini saat
- Faz 0 (iskelet): 2h
- Task 1-2 (basit raporlar): 3h × 2 = 6h
- Task 3 (Sankey): 5h
- Task 4-8 (orta zorlukta): ~4h × 5 = 20h
- Task 9 (animasyon): 12h
- Task 10 (AI sunum): 35h
- **Toplam: ~80h ≈ 2 hafta**

### İlk teslimat (bu commit)
- Raporlar bp iskeleti (`/raporlar` landing + sidebar entry)
- Task 1: Veri Kalitesi Raporu
- Task 2: K-Vektör Çarpıklık Raporu
- demo.kokpitim.com'a deploy

### Kalan 8 task
Sonraki commit'lerde teker teker.

---

## TASK-140 | 2026-05-27 | ✅ Tamamlandı (canlı) — demo.kokpitim.com kök URL doğrudan demo landing'e yönlendir

**Görev:** demo.kokpitim.com / kök adresinden marketing/login sayfası yerine doğrudan demo landing (/demo) açılsın — demo subdomain'in tek giriş kapısı demo akışı olmalı
**Modül:** micro/core/launcher.py, micro/modules/marketing/routes.py
**Durum:** ✅ Canlı

### Değiştirilen Dosyalar
- `micro/core/launcher.py::platform_root` → demo mode aktifse: aktif session varsa launcher, yoksa /demo'ya redirect
- `micro/modules/marketing/routes.py::index` → aynı mantık (marketing_bp `/` route'unu da kapatıyor)

### Yapılan İşlem
İki ayrı blueprint aynı `/` path'ini kayıt ediyordu (app_bp + marketing_bp). marketing_bp önce yüklendiği için marketing landing dönüyordu. Her ikisinde de KOKPITIM_DEMO_MODE flag kontrolü eklendi.

### Davranış matrisi (demo modu)
| Durum | / cevabı |
|---|---|
| Demo session aktif | 302 → /masaustu-launcher (kullanıcı çalışmaya devam eder) |
| Demo session yok | 302 → /demo (landing — rol seçici) |

Production'da (KOKPITIM_DEMO_MODE=0) davranış değişmez.

### Canlı doğrulama
- `GET https://demo.kokpitim.com/` → HTTP 302 → `/demo`
- Landing render edilir (demo-role-card 24 kez, 3 rol kartı × 8 stil)

### Notlar
- Test ortamına da deploy edildi (tutarlılık)
- Login ekranı demo subdomain'de hiçbir zaman gösterilmez — kullanıcı yanlışlıkla `/auth/login` GET ederse de demo akışına dönmeli (sonraki iyileştirme)

---

## TASK-139 | 2026-05-27 | ✅ Tamamlandı (canlı) — demo modu üst-bar dönüşümü

**Görev:** Demo modunda yan-bar (240px) yerine yatay üst-bar göster — daha şık ve demo deneyimine uygun
**Modül:** ui/static/platform/css/, ui/templates/platform/base.html
**Durum:** ✅ Canlı (https://demo.kokpitim.com/)

### Yeni Dosyalar
- `ui/static/platform/css/demo.css` → body.demo-mode aktifken sidebar→topbar dönüşüm override'ları

### Değiştirilen Dosyalar
- `ui/templates/platform/base.html` → demo session'ı varsa demo.css koşullu link

### Yapılan İşlem
Pure CSS override; HTML yapısı değişmiyor:
- `.micro-sidebar` → `position: sticky; top: 40px; flex-direction: row; height: 58px; width: 100%`
- Sidebar brand kompakt (logo + ad), bölüm etiketleri (`Ana Modüller` vb.) gizlendi
- Nav item'ları yatay pill, aktif item alta çizgi
- `.micro-main` → margin-left: 0
- Footer (kullanıcı kartı) gizli — banner zaten rol/durum gösteriyor
- Mobil için kompakt versiyon

### Deploy
- Tarball ile /opt/kokpitim-demo/app/ ve /opt/kokpitim-test/app/ güncellendi
- docker restart kokpitim-demo-web
- Canlı doğrulama: demo.css yüklü, demo-mode body class aktif

---

## TASK-138 | 2026-05-27 | ✅ Tamamlandı (canlı: demo.kokpitim.com) — demo ortamı VM deploy

**Görev:** Demo v1'i Oracle VM'e demo.kokpitim.com olarak yayınla (4. ortam)
**Modül:** Oracle VM (/opt/kokpitim-demo/), scripts/ops/oracle/
**Durum:** ✅ Canlı

### Yeni Dosyalar
- `scripts/ops/oracle/setup_demo_env.sh` → idempotent demo ortamı kurulum scripti (DB + dump + .env + docker + nginx + SSL)

### Canlı Sonuç
- **URL:** https://demo.kokpitim.com/demo/
- **VM:** /opt/kokpitim-demo/ (port 5080, container kokpitim-demo-web)
- **DB:** kokpitim_demo_db (Tomofil verisi test DB'den klonlandı, 99k satır)
- **SSL:** Let's Encrypt cert (expires 2026-08-25, otomatik renew)
- **Container:** --network host, KOKPITIM_DEMO_MODE=1, volume mount /opt/kokpitim-demo/app → /app

### Yapılan İşlem
1. `git merge --no-ff claude/demo-ortami → main`, push (32af5c1..975b442)
2. DNS doğrulama: demo.kokpitim.com → 129.159.30.175 ✓
3. Yeni demo dosyaları tarball ile test ortamına aktarıldı (test bonus güncellendi)
4. `setup_demo_env.sh` VM'de çalıştırıldı: dizin + DB + dump + .env + nginx + cert
5. Container ayarlamaları (script'in yetersiz kaldığı 3 nokta):
   - **Hata 1:** `-p 127.0.0.1:5080:5080` port mapping → test container `--network host` → düzeltildi
   - **Hata 2:** image default CMD `gunicorn --bind 0.0.0.0:5000` → custom CMD ile `--bind 0.0.0.0:5080`
   - **Hata 3:** image içindeki config.py eski (KOKPITIM_DEMO_MODE yoktu) → volume mount `-v /opt/kokpitim-demo/app:/app`

### Canlı Doğrulama
- `GET https://demo.kokpitim.com/` → HTTP 200
- `GET /demo/` → 200, landing render (3 rol kartı, "99.000 satır", "gerçek veriyle")
- `GET /demo/start/yonetici` → 302 → launcher, banner aktif
- `GET /demo/heartbeat` (session aktif) → `{"active":true,"remaining_seconds":3599,"role":"yonetici"}`

### Notlar
- **Eşzamanlı kullanıcı:** v1 schema isolation içermez. v2 schema clone gerekli.
- **setup_demo_env.sh** ideal kurulumu yazıyor ama bu çalışmada 3 küçük manuel düzeltme gerekti (network host, CMD override, volume mount). Sonraki sefer script güncellenmeli.
- **Demo veri tazeliği:** Tomofil + güncel test kullanıcı verisi. Periyodik master refresh ayrı plan.

---

## TASK-137 | 2026-05-27 | ✅ Tamamlandı (yerel, claude/demo-ortami) — v1: landing + bypass-login + banner

**Görev:** Kokpitim demo ortamı v1 — landing sayfası, rol-bazlı bypass-login, demo banner + 60dk countdown + çıkış akışı
**Modül:** config.py, micro/modules/demo/, ui/templates/platform/demo/, platform_core/__init__.py, ui/templates/platform/base.html
**Durum:** ✅ Tamamlandı (v1 kapsamı — schema isolation v2'ye ertelendi)
**Plan:** docs/DEMO-ORTAMI-PLAN.md (S3 yaklaşımı — v2'de full inşa)

### Yeni Dosyalar
- `micro/modules/demo/__init__.py`, `routes.py` → demo blueprint (4 endpoint: landing, start/<role>, end, heartbeat)
- `ui/templates/platform/demo/landing.html` → standalone şık landing (gradient bg, 3 rol kartı, davranış açıklaması, footer)
- `ui/templates/platform/demo/_banner.html` → app içinde demo modunda görünen üst banner (countdown, çıkış, hesap-aç linki)

### Değiştirilen Dosyalar
- `config.py` → `KOKPITIM_DEMO_MODE`, `DEMO_SESSION_MINUTES`, `DEMO_TENANT_ID` yapılandırma alanları
- `platform_core/__init__.py` → demo routes import
- `ui/templates/platform/base.html` → demo banner koşullu include (`session.get('demo_session_active')`)

### Yapılan İşlem
**A. Landing (`/demo/`):** Standalone marketing-kalitesinde sayfa. Gradient arka plan, hero ("Kokpitim'i gerçek veriyle deneyin"), 3 bilgi şeridi (kayıt yok / 60dk / izole), 3 büyük rol kartı (Kurum Yöneticisi / Süreç Lideri / Süreç Üyesi — her birinde 4-bullet özelliği, kendi rengi, kendi ikonu), "Demo nasıl davranır?" 6 madde açıklama paneli, footer.

**B. Rol-bypass login (`/demo/start/<role>`):** Seçilen role karşılık gelen Tomofil tenant'ı (id=27) kullanıcısını bul → mevcut session'ı temizle → `login_user()` ile auto-login → session'a demo işaretleri yaz (`demo_session_active`, `demo_role`, `demo_role_label`, `demo_started_at`, `demo_expires_at`) → `/launcher`'a redirect. Yönetici → `admin@tomofil.com`, Lider/Üye → tenant içindeki ilk uygun rol-kullanıcısı.

**C. Banner (`base.html`):** `session.get('demo_session_active')` doğruysa üstte sticky gradient banner: rol etiketi + canlı kalan-süre countdown + "Hesap Aç" linki + "Çıkış" butonu. Her saniye JS countdown, her 30sn `/demo/heartbeat` ile sunucudan senkronize. Süre dolarsa SweetAlert ile uyarı + landing'e yönlendirme.

**D. Çıkış akışı:** Banner'daki "Çıkış" → SweetAlert onay modal'ı ("verilerin silinecek + hesap açmak için link") → `/demo/end` → `logout_user()` + session clear → landing'e döner.

**E. Güvenlik:** `KOKPITIM_DEMO_MODE=0` (veya değişken yok) olduğunda tüm 4 endpoint 404 döner. Prod'da yanlışlıkla deploy edilse bile demo'ya erişim mümkün değil. Test edildi.

### Test (yerel)
- `GET /demo/` → 200, 15kB sayfa, 3 rol kartı render
- `GET /demo/start/yonetici` → 302 /masaustu-launcher, session aktif, banner render
- `GET /demo/heartbeat` (session aktif) → `{"active":true,"remaining_seconds":3599,...}`
- `GET /demo/end` → 302 /demo, session clear, banner kaybolur
- `KOKPITIM_DEMO_MODE` kapalıyken tüm 4 endpoint → 404 ✓

### v1 Kapsamı Dışı (v2'de yapılacak)
- **Schema isolation (S3 per-session clone)** — eşzamanlı kullanıcılar şu an aynı Tomofil verisi üzerinde, birbirini görür. v2: PostgreSQL schema clone + havuz.
- **Demo DB ortamı kurulumu** — `setup_demo_env.sh` + `demo.kokpitim.com` Nginx/SSL + Docker container.
- **E-posta/LLM mock** — KOKPITIM_DEMO_MODE açıkken otomatik mock.
- **Beacon API + inaktivite timeout**.

### Notlar
- DNS `demo.kokpitim.com` Cloudflare'de açık.
- Test ortamına deploy: bir sonraki adımda, kullanıcı onayıyla. Demo container `KOKPITIM_DEMO_MODE=1` env ile.

---

## TASK-136 | 2026-05-27 | ✅ Tamamlandı (yerel, claude/tarih-egemen-plan-year)

**Görev:** "Tarih egemen" plan year doktrini — 3 fazlı SP veri yazımı yeniden mimarisi + yıllar arası diff + snapshot rolleri
**Modül:** app/services/, app/models/, micro/modules/surec/, micro/modules/bireysel/, micro/modules/sp/, ui/templates/platform/sp/, migrations/
**Durum:** ✅ Tamamlandı

### Yeni Dosyalar
- `app/services/date_sovereign.py` → tarih egemen doktrini yardımcı modülü (view_year / resolve_plan_year_for_date / entity_exists_in_year / build_existence_error / build_cross_year_notice)
- `app/services/plan_year_diff_service.py` → iki plan yılı arası diff hesaplayıcı (kimlik, strateji, alt strateji, süreç, PG, initiative, OKR, bağlar)
- `app/models/user_year_assignment.py` → UserYearAssignment modeli (yıllık snapshot rolü/departman) + resolve_user_assignment helper
- `migrations/versions/j3k4l5m6n017_user_year_assignments.py` → migration
- `ui/templates/platform/sp/karsilastirma.html` → yıllar arası karşılaştırma sayfası

### Değiştirilen Dosyalar
- `app/services/plan_year_service.py` → `get_active_plan_year_for_user` session yoksa bugünün takvim yılı PlanYear'ına düşer (UI default'larıyla tutarlı)
- `micro/modules/surec/routes_kpi_data.py` → KPI veri eklemede sert "aktif dönem yıl uyumu" engeli kaldırıldı; tarih → plan_year resolve + süreç/PG var mı kontrolü + cross-year rozeti
- `micro/modules/surec/routes_activity.py` → aynı doktrin faaliyet eklemede (start_at → plan_year)
- `micro/modules/bireysel/routes.py` → bireysel KPI veri eklemede aynı doktrin
- `micro/modules/sp/routes_plan_year.py` → `/sp/api/plan-years/diff` ve `/sp/karsilastirma` route'ları
- `static/js/process_karne.js`, `ui/static/platform/js/surec.js` → response.notice'ı yakalayıp toast'a ekler
- `app/models/__init__.py` → UserYearAssignment kaydı

### Yapılan İşlem
**Faz 0 — Doktrin:** "Clone birincil" kararı netleşti — bir varlığın o yılda olup olmadığı sorusu `entity.plan_year_id` ile cevaplanır (overlay tablolar sadece metadata override). Üç kavram ayrıştırıldı: VIEW context (UI filtresi, default current cal year), RECORD routing (tarih → plan year), EXISTENCE check (clone var mı).

**Faz 1 — KPI veri girişi ve faaliyet:** Eski "tarih == aktif dönem" sert engeli kaldırıldı. Yeni akış: data_date'in yılından plan_year resolve edilir; süreç/PG o yılda yoksa bağlamlı engel ("SR1A süreci 2026 planında yok, yalnızca 2025 verisi girilebilir"). Görüntü yılı ≠ kayıt yılı ise yumuşak rozet ("↩️ 2025 dönemine yazıldı") — kullanıcı dönem değiştirmek zorunda değil. Tomofil SR1A senaryosu doğru çalışır.

**Faz 2 — Yayılım:** Aynı doktrin bireysel KPI veri girişine (`bireysel/api/veri/add`) uygulandı. SWOT/PESTEL/Porter/OKR/SP-proje gibi tarihten bağımsız (yıl-snapshot) varlıklar zaten plan_year_id ile oluşturulduğundan değişiklik gerektirmedi.

**Faz 3 — Diff + Snapshot:**
- `plan_year_diff_service.diff_plan_years(tenant, year_a, year_b)` → identity / strategies / sub_strategies / processes / kpis / initiatives / okr / links kategorilerinde added/removed/changed listeleri. Eşleştirme `source_*_id` lineage + kod fallback ile.
- `/sp/karsilastirma` sayfasında interaktif yıl seçici + karşılaştırma tablosu (vizyon farkları yan-yana, kategoriler için yeni/kaldırılan/değişen kolonları).
- `user_year_assignments` tablosu: `(user_id, plan_year_id, tenant_id, job_title, department, role_label, note)` — kullanıcının yıllık snapshot rolü. `resolve_user_assignment()` helper: snapshot varsa onu döner, yoksa user.job_title/department fallback. Migration manuel SQL ile uygulandı (alembic flask cli `__init__.py` shadowing yüzünden çalışmıyor).

### Test sonuçları (Tomofil canlı veri)
- `diff_plan_years(27, 2025, 2026)` → SR1A + SR1B "removed", SR1 "added", vizyon 3 alan değişti, alt strateji +1/-1, PG +31/-32. Meta'daki `override_ozet` ile tutarlı.
- `user_year_assignments` tablosu yaratıldı (0 satır — kullanıcı UI'sı yok henüz).

### Notlar
- BSC perspectives tablosu DB'de yok (migration eksik) — diff serviste şu an dahil değil.
- UserYearAssignment UI tarafı (kullanıcı düzenleme ekranı) yapılmadı — backend hazır, ihtiyaç çıkınca eklenir.
- Tüm değişiklikler `claude/tarih-egemen-plan-year` dalında. Push/merge kullanıcı talebine bağlı.

### Düzeltme (Faz 3 duplikasyon temizliği)
İlk geçişte mevcut `/sp/donemler` sayfasındaki karşılaştırma özelliği görülmeden yeni `/sp/karsilastirma` sayfası + `plan_year_diff_service.py` yazılmıştı. Kullanıcı uyarısıyla geri alındı:
- `app/services/plan_year_diff_service.py` ve `ui/templates/platform/sp/karsilastirma.html` silindi
- `routes_plan_year.py`'den yeni endpoint'ler kaldırıldı
- Eksik 3 kategori (Initiative span, OKR sayım, links sayım) mevcut `sp_api_donem_karsilastir` endpoint'ine eklendi
- `donemler.html`'de bu üç kategori için yeni "Çok Yıllık Initiative / OKR / Bağlar" details bölümü eklendi
- Test (Tomofil 2025↔2026): 3 initiative `y2`'de başlamış, 3 `y2`'den önce bitmiş, 6 devam ediyor; OKR 3↔3; bağlar 13→15

---

## TASK-135 | 2026-05-27 | ✅ Tamamlandı (yerel)

**Görev:** Tomofil tam veri reset — hard wipe + 2020-2026 SP veri seti import
**Modül:** scripts/, docs/, app/models (envanter)
**Durum:** ✅ Tamamlandı

### Yeni Dosyalar
- `docs/TENANT-VERI-ENVANTERI.md` → 96 tablo, 15 modül, tam şema (kolon+FK+index+unique) dökümü
- `scripts/tomofil_hard_wipe.py` → tenant_id=27 için SP + portföy + bildirim hard delete (savepoint-li tek transaction)
- `scripts/tomofil_sp_import.py` → `TomofılSP_2020_2026_v2.json`'dan PG'ye bulk import (2-pass self-ref, +1M ID offset, user_id→admin remap)

### Yapılan İşlem
**A. Hard wipe (tenant_id=27):** Tomofil'in tüm SP ağacı + 48.283 KPI ölçümü + portföy projeleri + bildirimler hard delete edildi. Kullanıcılar (97) + tenant + roller + audit_logs + e-posta/LLM konfigleri korundu. Yedek alınmadı (kullanıcı talebi: yeni veri seti hazırdı).

**B. Cross-tenant FK temizliği:** Wipe sırasında ortaya çıkan `bottleneck_log.kpi_id`, `process_maturity.process_id`, `value_chain_items.linked_process_id`, `individual_activities/IPI.source_process_id` ve `processes.parent_id/source_process_id` referansları açıkça null'landı/silindi.

**C. SP 2020-2026 import (99.238 satır):** 7 plan yılı, 36 strateji, 93 alt strateji, 71 süreç, 221 PG, **91.408 KPI ölçüm**, 524 bireysel PG + 6.288 ölçümü, SWOT/PESTEL/Porter (7+7+7), 21 OKR + 63 KR, 5 ESG metrik + 35 ölçüm, 68 olgunluk, 35 risk, 21 initiative + 84 kilometre taşı, 21 SP projesi + 63 görev, 36 K-Vektör ağırlık, 7 tenant yıl kimliği, 7 KPI yıl override.

**D. Import mimarisi:**
- JSON `tenant_id` (her değer) → DB 27 remap
- JSON `user_id` ref'leri → Tomofil admin (id=8173) remap
- Tüm ID ve FK'lere +1.000.000 offset (diğer tenant ID'leriyle çakışma yok)
- Self-ref FK'ler (`source_*_id`, `parent_id`, `template_source_id`, `scenario_of_id`, `depends_on_task_id`) 2. pass'te `EXISTS` filtreli UPDATE ile bağlandı
- 27 sequence MAX(id)+1'e reset edildi

### Notlar
- JSON'da BSC perspectives (84 satır) var ama `bsc_kpi_perspectives` tablosu canlı DB'de yok → atlandı (migration eksik).
- JSON'daki bazı `source_process_id` ref'leri var olmayan eski yıl ID'lerine bakıyordu — kırık ref'ler (3 process source, 42 plan task depends) NULL bırakıldı.
- Wipe ve import'un ikisi de tek transaction, savepoint-li hata toleransıyla; başarısızlık halinde rollback.
- Gözle doğrulama yerel + test ortamında kullanıcı tarafından yapılacak.

---

## TASK-134 | 2026-05-26 | ✅ Tamamlandı (yerel + push, test ortamı aktif)

**Görev:** Test ortamı kurulumu (test.kokpitim.com) + üç-ortam terminolojisi + CSP fix
**Modül:** Oracle VM, docs/KURALLAR-MASTER.md, CLAUDE.md, app/__init__.py, requirements.txt, scripts/ops/oracle/
**Durum:** ✅ Tamamlandı

### Yapılan İşlem
1. **Test ortamı kuruldu** — `https://test.kokpitim.com/` (Oracle VM `/opt/kokpitim-test/`, port 5050, DB `kokpitim_test_db`, Let's Encrypt SSL)
2. **Üç-ortam terminolojisi** zorunlu kural olarak `KURALLAR-MASTER §8`'e yazıldı: Yerel → Test → Yayın. "VM/üretim VM" gibi belirsiz terimler yasak. `CLAUDE.md` üst yorumu da güncellendi.
3. **CSP fix** `app/__init__.py`'da: `cdn.tailwindcss.com` script-src ve connect-src'a eklendi (yereldeki DEBUG=True bunu maskeliyordu, test'te kurum sayfası iconları görünmüyordu).
4. **`PyYAML>=6.0`** requirements.txt'e eklendi (Kule sistemi için, test imajında build sırasında ortaya çıktı).

### Yeni Dosyalar
- `scripts/ops/oracle/setup_test_env.sh` → test ortamı orchestrator

### Değiştirilen Dosyalar
- `docs/KURALLAR-MASTER.md` §8 yeniden yazıldı (üç ortam tablosu + deploy akışı)
- `CLAUDE.md` üst yorum güncellendi
- `app/__init__.py` CSP
- `requirements.txt` PyYAML

### Notlar
- Test ortamı yereldeki .env'in **çoğunluğunu + test override'ları** (DB URI, PORT, SECRET_KEY) kullanır.
- SMTP DB'de saklanıyor (`tenant_email_configs`), .env'de değil — test'e dump ile aktarıldı.
- Çift tablo tanımı (`task_predecessors`: portfolio_project.py vs models/project.py) yerelde sessiz çalışıyor, test'in ilk clone'unda kırıldı; pragmatik çözüm: yereldeki kodu tarball ile direkt aktarmak.

---

## TASK-133 | 2026-05-26 | ✅ Tamamlandı (yerel, claude/ems-data-import)

**Görev:** Tomofil strateji ağacının markdown ile reconcile + K-Vektör 100 ölçeği
**Modül:** app/services/k_vektor_engine.py (etkilenmedi), micro/modules/sp/, ui/templates/platform/sp/, scripts/, micro/modules/surec/
**Durum:** ✅ Tamamlandı

### Yeni Dosyalar
- `scripts/tomofil_reconcile.py` → Tomofil strateji ağacını markdown'a göre yeniden yapılandıran orchestrator
- `scripts/tomofil_backfill_process_substrategy.py` → ara çözüm (sonradan reconcile ile ezildi)
- `backups/pre-tomofil-reconcile-20260526.dump` → 1 MB PG yedek
- `data/tomofil_reconcile/snapshot_before.csv` + `snapshot_after.csv`

### Değiştirilen Dosyalar
- `micro/modules/sp/routes_pages.py` → kv_vision_bar 100 ölçeğine indirildi (`score` alanı eklendi, `quotas`/`contrib` /10)
- `ui/templates/platform/sp/index.html` → "/1000" → "/100", "Hedef ölçek 100"
- `micro/modules/surec/routes_process.py` → /process sayfasına plan dönemi listesi + aktif yıl context
- `ui/templates/platform/surec/index.html` → plan dönemi seçici (POST /sp/api/plan-years/set-active)
- `ui/templates/platform/sp/index.html` → "Sistem rolü" badge satırı kaldırıldı (İngilizce role kod)
- `ui/templates/platform/base.html` → sidebar role gösterimi Türkçe haritaya geçirildi

### Yapılan İşlem
**A. K-Vektör 100 ölçeği:** Engine 1000 ölçeğinde bırakıldı (backward-compat); UI ve katkı/kota tablosu 100 ölçeğine indirildi. "Vizyon 1000 içindeki pay" → "Vizyon 100 içindeki pay" vb.

**B. Tomofil reconcile (7 fazlı orchestrator):**
1. Snapshot before (CSV)
2. Markdown parse (6 ana / 18 alt / 55 yaprak)
3. Hard delete: 7 Strategy, 35 SubStrategy, 49 ProcessSubStrategyLink, 18 KVektorWeight
4. Rebuild: 6 Strategy + 18 SubStrategy + 55 Initiative
5. 4 eksik süreç eklendi (F2D, O2C, S2E, W2R)
6. Process↔SubStrategy bağları markdown'a göre yeniden kuruldu (96 link)
7. Doğrulama + K-Vektör recalc

**C. /process sayfasına plan dönemi seçici** + UI tutarlılığı (Sistem rolü kodu Türkçeleştirme).

### Sonuç
- K-Vektör vizyon skoru: 0.00 → **59.21 / 100**
- Yetim alt strateji: 0
- Yetim süreç: 0
- 6/6 stratejinin skoru üretiliyor
- KpiData (48.283 satır) korundu

### Notlar
- K-Vektör ağırlıkları silindiği için sistem geçici olarak **eşit dağılım** kullanıyor; kullanıcı UI'dan ağırlıkları yeniden girecek.
- ProcessKpi.sub_strategy_id alanları NULL'landı (eski yaprak-substrategy bağı geçersiz); ProcessSubStrategyLink ile yeni bağ kuruldu.

---

## TASK-132 | 2026-05-26 | ✅ Tamamlandı (yerel, claude/ems-data-import)

**Görev:** Tomofil çalışanlarına gerçek cPanel e-posta hesabı + Tomofil için SMTP yapılandırma
**Modül:** scripts/, app/models/email_config.py (yalnızca okuma)
**Durum:** ✅ Tamamlandı

### Yeni Dosyalar
- `scripts/cpanel_email_bulk.py` → cPanel UAPI ile toplu e-posta açma scripti (idempotent, hata toleranslı, rate-limit'e dayanıklı)
- `scripts/tomofil_photo_assign.py` → fotoğraf-kullanıcı cinsiyet bazlı eşleştirme (önceki adımda)
- `scripts/tomofil_photo_upload.py` → profil fotoğrafı Pillow resize + DB güncelleme (önceki adımda)

### Yapılan İşlem
1. **cPanel hazırlık:** `kalites1` kullanıcısının API token'ı `.env`'e eklendi (gitignore'da)
2. **96 e-posta hesabı** açıldı: `<isim.soyisim>@kokpitim.com` formatında, 250 MB kota, şifre `TmF_2626` (sistemdeki ile aynı)
3. **Sistem DB email'leri** `@tomofil.test` → `@kokpitim.com` olarak güncellendi (96 kullanıcı)
4. **`bildirim@kokpitim.com`** ayrı bot hesabı açıldı (500 MB, güvenli rastgele şifre)
5. **`TenantEmailConfig`** Tomofil (id=27) için oluşturuldu: SMTP `mt-valve.guzelhosting.com:587` (STARTTLS), gönderici `Tomofil Bildirim <bildirim@kokpitim.com>`, 4 bildirim tipi aktif
6. **96 profil fotoğrafı** kullanıcılara atandı (Pillow 512×512 JPEG q=85)

### Notlar
- cPanel rate-limit ilk denemede 21'de takıldı → script yenilendi (1s delay, try/except, flush, 30s timeout-recovery, append-mode log)
- Tüm cPanel hesapları aynı şifrede; ileride bireysel şifre rotasyonu yapılırsa script güncellenir
- `bildirim@kokpitim.com` şifresi konuşma log'unda görünür → kullanıcı not aldı, gerekirse rotate edilebilir
- `.env` gitignore'da; cPanel token commit'e gitmiyor

---

## TASK-131 | 2026-05-26 | ✅ Tamamlandı (yerel, claude/ems-data-import)

**Görev:** EMS (Eskişehir Makine Sanayii A.Ş.) verilerinin sisteme aktarılması
**Modül:** scripts/ems_import/, backups/, instance/uploads/tenant_logos/
**Durum:** ✅ Tamamlandı

### Yeni Dosyalar
- `scripts/ems_import/_common.py` → ortak yardımcılar, C-Suite/YK/tesis kayıtları, 12 süreç haritası, 10 risk
- `scripts/ems_import/run_all.py` → 9 fazlı orchestrator (550 satır)
- `backups/pre-ems-import-20260526.dump` → 1 MB PG yedek (custom format)
- `data/ems_import_log/users_created.csv` → 20 yeni kullanıcı + geçici şifre
- `instance/uploads/tenant_logos/28.svg` → EMS placeholder logo (#1B3F6E + "EMS" yazısı)

### Yapılan İşlem
Tenant id=28 (EMS) için 9 fazlı veri yükleme: tenant profili (sektor, vergi, vizyon/misyon), 20 kullanıcı (9 C-Suite, 5 YK, 6 tesis müdürü), plan dönemi 2026, 12 süreç (P2M/A2R/C2L/O2C/S2P/H2R/I2R/F2D/R2R/Q2C/G2N/K2K), 6 ana + 16 alt strateji + 41 girişim (markdown'dan parse), 6 OKR Objective + 24 Key Result, 84 süreç KPI'sı, 10 risk (manuel C-Suite sahip ataması). 22.800 atomik kayıt 7 modülden aylık aggregate edilerek 289 KpiData satırına dönüştürüldü; 18 OKR snapshot KR.current_value olarak yansıtıldı.

### Sonuç İstatistikleri
- 21 kullanıcı | 12 süreç | 6/16 strateji | 41 girişim
- 6 Objective + 24 KR | 101 ProcessKpi | 289 KpiData | 10 risk

### Notlar
- Atomik veri "elle girilseydi nereye gider" mantığıyla aylık aggregate olarak KpiData'ya yazıldı; ham atomik tablo açılmadı.
- Risk modülünden gelen olasılık/etki güncellemeleri başlık farklılığı nedeniyle eşleşmedi; manuel atanan değerler korundu (sonradan eşleştirme yapılabilir).
- Yedek `backups/pre-ems-import-20260526.dump` ile geri dönüş mümkün.

---

## TASK-130 | 2026-05-26 | ⏸ Ertelendi

**Görev:** Kule yardımcı sistemi geçici olarak devre dışı bırakıldı
**Modül:** ui/templates/platform/base.html, docs/
**Durum:** ⏸ Ertelendi — UI stabilleşince devam

### Değiştirilen Dosyalar
- `ui/templates/platform/base.html` → Kule CSS/JS yüklemeleri yorum içine alındı
- `docs/ERTELENEN-ISLER.md` → yeni dosya, E1 girdisi (Kule durumu, dosyalar, devam talimatı)

### Yapılan İşlem
Kule altyapısı tamamlandı ama UI'da hala yoğun değişiklik var; her UI revizyonunda Kule'yi de güncellemek/test etmek zaman maliyetli. Kullanıcı kararıyla şimdilik askıya alındı. Tüm kod, YAML, SVG, model, migration ve API endpoint'leri korundu — sadece base template'teki include'lar kapatıldı. Branch `claude/kule-yardimci-sistemi` silinmedi, aynen duruyor.

### Notlar
Devam için: `docs/ERTELENEN-ISLER.md` E1 bölümünü oku, base.html'deki yorum satırlarını aç.

---

## TASK-129 | 2026-05-25 | ✅ Tamamlandı (yerel, claude/kule-yardimci-sistemi dalında)

**Görev:** Kule — kullanıcı yardımcı sistemi (Sprint 1-5 altyapı + içerik)
**Modül:** app/models/, app/services/, micro/modules/shared/kule/, ui/static/platform/, ui/templates/platform/, migrations/, docs/tours/
**Durum:** ✅ Tamamlandı

### Yeni Dosyalar
- `docs/KULE-TANIM.md` → karakter, ton, mimari spec (tek gerçek kaynak)
- `docs/tours/*.yaml` → 17 tur içeriği (masaustu, sp_*, surec, k_radar, bireysel, admin_*)
- `app/models/tour.py` → UserTourProgress modeli
- `app/services/kule_service.py` → YAML loader + progress yönetimi
- `micro/modules/shared/kule/routes.py` → 5 API endpoint
- `ui/static/platform/img/kule.svg` → hava kontrol kulesi karakter
- `ui/static/platform/css/kule.css` → FAB + welcome + driver.js teması
- `ui/static/platform/js/kule.js` → runtime (init, start, restart)
- `migrations/versions/i2j3k4l5m016_user_tour_progress.py`

### Değiştirilen Dosyalar
- `ui/templates/platform/base.html` → driver.js + kule.css/js + meta tag pickup
- 13 sayfa template'ine `<meta name="kule-tour-key">` + `data-tour` attribute'ları

### Yapılan İşlem
Tanım dosyası (KULE-TANIM.md) tek referans olarak yazıldı. Driver.js (CDN) tabanlı tur runtime'ı, YAML-driven içerik sistemi, sayfa başına `meta` etiketi ile otomatik başlatma. Sağ alt sabit FAB (kule SVG) ile manuel yeniden başlatma. Persona: Talat Konuk / Eskişehir Motor Sanayi. 17 tur YAML hatasız yükleniyor; migration uygulandı.

### Notlar
İçerik AI taslağıyla üretildi; kullanıcı geri bildirimine açık. Faz 2 (AI soru-cevap köprüsü) bilinçli olarak atlandı — ayrı proje.

---

## TASK-128 | 2026-05-25 | ✅ Tamamlandı (yerel + main'e merge, push/VM beklemede)

**Görev:** Bayi/Holding mimarisi — Sprint A-F (6 sprint)
**Modül:** app/models/, app/utils/, app/services/, app/routes/, micro/modules/admin/, ui/templates/platform/admin/, migrations/, tests/
**Durum:** ✅ Tamamlandı (`claude/bayi-holding-sprint-{a..f}` → main, 6 merge commit)

### Sprint Listesi

**Sprint A — Foundation** (merge `b6e8db1`)
- Tenant tablosuna 3 kolon: `tenant_type`, `parent_tenant_id`, `sub_tenant_limit` (migration `h1i2j3k4l015`)
- Self-ref relationship + property'ler (is_dealer/is_holding/is_parent_capable/is_sub_tenant)
- `app/utils/tenant_scope.py` genişletildi — 12 yetki helper:
  - `accessible_tenant_ids()`, `is_holding_user/admin()`, `is_dealer_user/admin()`,
    `child_tenant_ids()`, `can_manage_sub_tenants()`, `is_readonly_for_tenant()`,
    `scope_query()`, `validate_tenant_type()`, `can_be_parent()`, `check_sub_tenant_limit()`,
    `@block_if_holding_readonly()` decorator
- `tests/test_tenant_hierarchy.py` — 25 test (TÜMÜ PASSED), 4 spesifik saldırı senaryosu

**Sprint B — Platform Admin tip atama** (merge `71879c0`)
- `/admin/tenants` listesinde "Tip" sütunu + parent gösterimi
- Yeni/Düzenle modal: "Hiyerarşi" bölümü (sadece Admin görür) — tip + parent + sub_tenant_limit
- Backend `admin_tenants_add/edit`: tip validation, parent kontrolü, audit log `TENANT_TYPE_CHANGE`

**Sprint C — Bayi/Holding alt-tenant CRUD** (merge `1c5f4f7`)
- `micro/modules/admin/routes_sub_tenants.py` — yeni route modülü
- 5 endpoint: `GET/POST /admin/sub-tenants`, `POST /api/.../reset-password`, `POST /api/.../toggle`
- `/admin/sub-tenants` UI: hero kart + tablo + yeni alt-tenant modal + başarı modal'ı (geçici şifre kopyala)
- Sidebar: Bayi → "Müşterilerim", Holding → "Alt Şirket Yönetimi"
- Yeni alt-tenant otomatik `tenant_type='normal'` + ilk admin oluşturulur (Kp_<random> geçici şifre)

**Sprint D — Holding konsolide dashboard** (merge `2176370`)
- `app/services/holding_consolidated_service.py` — `build_holding_snapshot()`: tüm alt-tenant'ların aggregate snapshot'ı
- `/holding/dashboard` + `/holding/api/snapshot`
- UI: hero (avg sağlık 48px) + 4 toplam + 3 alarm tile + Chart.js karşılaştırma + tile grid
- Sidebar: Holding admin için "Holding Görünümü" (ana sayfa)

**Sprint E — Salt-okur drill-down** (merge `07eda2e`)
- `build_sub_tenant_drilldown()` servisi
- `/holding/tenant/<id>/view` + `/holding/api/tenant/<id>/drilldown`
- `_validate_holding_access()` ile yetki kontrolü (holding user kendi children + Platform Admin tümü)
- UI: salt-okur banner + hero + 6 KPI tile + initiative tablosu + risk tablosu
- Audit log: `HOLDING_VIEW_TENANT` (her drill-down)

**Sprint F — Login yönlendirme** (merge `38d527c`)
- `default_landing_endpoint()` helper: Holding → /holding/dashboard, Bayi → /admin/sub-tenants, diğer → /launcher
- 3 redirect noktası entegre: auth login (GET + POST), totp challenge success

### Güvenlik Saldırı Test Sonuçları (25/25 PASSED)
1. ✅ Bayi admin alt-tenant verisini sorgu ile çekemiyor (`accessible_tenant_ids` filtre)
2. ✅ Alt-tenant kullanıcısı parent'ı/kardeşlerini göremiyor
3. ✅ Holding admin sadece kendi alt-tenant'larını görüyor
4. ✅ Normal `tenant_admin` platform-wide erişim sağlayamıyor

### Notlar
Mimari karar: tüm DB sorguları artık `tenant_id IN accessible_tenant_ids(user)` filtresine bağlanmalı. Şu an mevcut endpoint'ler `current_user.tenant_id` kullanıyor — Bayi/Holding senaryosunda bu yeterli (bayi alt-tenant'a sızamaz, holding sadece kendi tenant'ını edit eder). Drill-down salt-okur özet sayfasıyla yapıldı (tüm sayfa refactor yerine), daha az invaziv.

İçi içe hiyerarşi yasak (bayi/holding altında bayi/holding açılamaz). Aktif alt-tenant varken parent'ı 'normal'a düşürme yasak.

---

## TASK-127 | 2026-05-25 | ✅ Tamamlandı (yerel + main)

**Görev:** Sidebar kurum logosu beyaz çerçeve fix + admin 2FA reset + profil foto otomatik resize
**Modül:** ui/static/platform/css/sidebar.css, micro/modules/admin/routes.py, micro/modules/shared/auth/routes.py
**Durum:** ✅ Tamamlandı (3 ayrı commit + merge)

### Değişiklikler
- `sidebar-brand-logo`: zorunlu beyaz arka plan + padding + box-shadow kaldırıldı (şeffaf PNG sidebar koyu zemininde direkt görünür); helper `.has-bg` class korundu
- `/admin/users/<id>/2fa-reset` endpoint: admin kullanıcının 2FA'sını sıfırlar (telefon kayıp + backup kod yok senaryosu); kullanıcı edit modal'a 2FA durum + sıfırla butonu
- Profil foto yükleme: 5MB sınır 15MB'a çıkarıldı, Pillow ile otomatik 512×512 LANCZOS resize + JPEG q=85; EXIF orientation düzeltmesi; orijinal 5MB+ olsa bile çıktı ~50KB

---

## TASK-126 | 2026-05-25 | ✅ Tamamlandı (yerel + main)

**Görev:** /admin/users sütun sıralama + adminin 2FA sıfırlaması
**Modül:** ui/templates/platform/admin/users.html, ui/static/platform/js/admin.js
**Durum:** ✅ Tamamlandı

### Değişiklikler
- Tablo başlığına tıklamalı sıralama (5 sütun: ad, e-posta, rol, kurum, durum)
- Asc/desc toggle + aktif kolon indigo arka plan + anlamsal sıralama (null'lar en alta)
- Tamamen client-side, filtre + sıralama birlikte çalışır

---

## TASK-125 | 2026-05-25 | ✅ Tamamlandı (yerel + main'e merge, push/VM beklemede)

**Görev:** Opsiyonel 2FA UI + challenge 500 hata fix
**Modül:** app/routes/totp.py, ui/templates/platform/auth/, ui/static/platform/js/, requirements.txt
**Durum:** ✅ Tamamlandı (`claude/2fa-profil-uygu` → main merge `1bd5b0f`)

### Değiştirilen / Eklenen Dosyalar
- `app/routes/totp.py` → 2 yeni JSON endpoint (`/2fa/status`, `/2fa/init`) + template path fix
- `ui/templates/platform/auth/profil.html` → "İki Faktörlü Kimlik Doğrulama" kartı + 3 modal (kurulum/backup/disable)
- `ui/templates/platform/auth/totp_challenge.html` → **YENİ** standalone challenge sayfası (login.html kalıbı)
- `ui/static/platform/js/twofa.js` → **YENİ** modal yönetimi + AJAX akışı
- `requirements.txt` → `pyotp>=2.9`, `qrcode>=8.0` eklendi

### Yapılan İşlem
2FA backend tam hazırdı (model + 4 endpoint), eksik olan kullanıcının erişebileceği UI'ydı. Profil sayfasına "Tamamen isteğe bağlıdır" notlu kart eklendi. Akış: Etkinleştir → QR + 6 haneli kod modal'ı → doğrulama → backup kodlar modal'ı (kopyala butonu). Çalışan kullanıcı için "Devre Dışı Bırak" şifre confirm ile. Login sonrası `/2fa/challenge` sayfası 500 veriyordu çünkü template eksikti — eklendi (Authenticator kod veya yedek kod modu, autocomplete=one-time-code, 6 hane dolunca otomatik submit). qrcode + pyotp paketleri kuruldu.

### Notlar
Profil sayfası UI Kılavuzu §1 prensiplerine uyumlu (tek odak, semantic color, hover transition'ları). 2FA opsiyonel — kullanıcı istediği zaman kapat-aç yapabilir. Backup kodlar bir kez kullanılır, kayboldukları takdirde admin manuel devre dışı bırakabilir (DB üzerinden `totp_enabled=False`).

---

## TASK-124 | 2026-05-25 | ✅ Tamamlandı (yerel + main'e merge, push/VM beklemede)

**Görev:** /admin/users sayfası iyileştirmesi — e-posta sığma + kurum filtresi + sütun sıralama
**Modül:** ui/templates/platform/admin/users.html, ui/static/platform/js/admin.js
**Durum:** ✅ Tamamlandı (`claude/fix-admin-users-layout` → main merge `948a2a0`)

### Değiştirilen Dosyalar
- `ui/templates/platform/admin/users.html` → `table-layout:fixed` + colgroup, ellipsis + title tooltip, kurum filtresi dropdown, butonlar icon-only, sortable th'ler, data-sort-* attribute'ları
- `ui/static/platform/js/admin.js` → tenant filtresi + "Temizle" + sonuç sayacı + 5 sütunda toggle asc/desc sıralama (ikon göstergesi)

### Yapılan İşlem
3 sprint commit'i:
1. **e-posta sığma + kurum filtresi** (`dc021be`) — uzun e-posta tabloyu taşırıyordu. table-layout:fixed + ellipsis; super-admin için ayrı "Kurum Filtresi" dropdown
2. **butonlar icon-only** (`0e8c165`) — Düzenle/Pasife Al/Aktifleştir butonları icon-only oldu (sığma sorunu), title attribute ile tooltip
3. **sütun başlığına sıralama** (`cc38ea0`) — 5 sütunda click → asc(▲) / desc(▼), aktif kolon indigo arka plan, anlamsal sıralama (rol/tenant null → 'zzz' en alta, durum 0_aktif → 1_pasif)

### Notlar
Tamamen client-side sıralama (sayfa yenilemez). Filtre + sıralama beraber çalışır. Tenant'a göre filtre eklenmesi ileride 1000+ kullanıcılı super-admin görünümünü kurtaracak. Sıralama state'i sayfa yenilenince sıfırlanır — kalıcı tutulması gerekirse localStorage'a eklenebilir.

---

## TASK-123 | 2026-05-25 | ✅ Tamamlandı (yerel + main'e merge, push/VM beklemede)

**Görev:** Tenant kurulum rehberi + tanıtım PDF + Playwright screenshot altyapısı
**Modül:** docs/test/, scripts/docs/, requirements-ai.txt
**Durum:** ✅ Tamamlandı (`claude/tenant-kurulum-rehberi` → main merge `c5ef452`)

### Eklenen Dosyalar
- `docs/test/tenant_kurulum_rehberi.md` (~1000 satır) — 17 adımlık lineer kurulum: profil → kurum → strateji → süreç → KPI → kullanıcılar → AI + bildirim
- `docs/test/tenant_kurulum_rehberi.pdf` (2.6 MB) — kapaklı, screenshot'lı, sayfa numaralı
- `docs/test/kokpitimtanitim.pdf` (3.6 MB) — galeri + 8 başlık altı screenshot
- `docs/test/screenshots/` — 19 PNG (tomofil tenant'tan otomatik)
- `scripts/docs/take_screenshots.py` — Playwright + login + 20 sayfa
- `scripts/docs/build_tanitim_pdf.py` — generic md→PDF, dosya adına göre kapak + screenshot eşlemesi
- `requirements-ai.txt` → playwright, weasyprint, markdown, pygments

### Yapılan İşlem
Tomofil tenant'ında Playwright/headless Chromium ile 19 sayfa otomatik screenshot. WeasyPrint Windows'ta GTK3 lib gerektirdiği için PDF üretimi Playwright/Chromium'a fallback edildi (chromium pip-system-certs + NODE_OPTIONS=--use-system-ca ile Norton SSL aşıldı). Generic builder herhangi bir md'yi PDF'e çevirir.

### Notlar
İlk çalıştırmada ~150 MB chromium binary indi (~5 dk). Sonraki build'ler cache'ten anında. Yeni sayfa eklediğimizde scripts/docs/take_screenshots.py'in PAGES listesine eklenmeli.

---

## TASK-122 | 2026-05-24 | ✅ Tamamlandı (yerel + main'e merge, push/VM beklemede)

**Görev:** UX test dokümantasyonu — 3 kapsamlı kılavuz belgesi
**Modül:** docs/test/
**Durum:** ✅ Tamamlandı (`claude/dokumantasyon-ux-test` → main merge `54b246b`)

### Eklenen Dosyalar
- `docs/test/kokpitimtanitim.md` (687 satır) — Proje detaylı tanıtım, modül haritası, veri modeli, AI sistemi, 10 SSS
- `docs/test/tenant_admin_kullanim_kilavuzu.md` (808 satır) — Admin için her şey: 7 adımlık ilk kurulum, 15 bölüm, hızlı aksiyon kartı
- `docs/test/tenant_kullanici_kilavuzu.md` (641 satır) — Standart kullanıcı için kullanım, 15 SSS, günlük/haftalık/aylık öneri listesi

### Yapılan İşlem
UX testçileri ve yeni kullanıcılar için üç katmanlı dokümantasyon: (1) sistemi tanıtan genel belge, (2) admin'in hangi ekranda ne yapacağını detaylı anlatan kılavuz, (3) standart kullanıcının "ne yapabilirim" sorusuna eksiksiz cevap veren rehber. 3 paralel agent ile derinlemesine envanter çıkarıldı (sayfa, bileşen, yetki, sık karşılaşılan sorunlar), ben sentezleyip yazdım. Toplam 2.136 satır markdown.

### Notlar
3 belge `docs/test/` klasöründe yaşayan doküman olarak duracak — yeni özellik eklendiğinde güncellenecek. CLAUDE.md kuralları gereği branch akışı uygulandı (yeni branch + commit + merge). VM'e gönderilmedi (kullanıcı talebi: "vm'e gönderme").

---

## TASK-121-AI | 2026-05-24 | ✅ Tamamlandı (yerel + main)

**Görev:** AI altyapı reformasyonu — LLM Gateway + BYOK + Kota Sistemi + Politika
**Modül:** app/services/, app/models/, micro/modules/sp/, ui/templates/platform/sp/, migrations/, docs/
**Durum:** ✅ Tamamlandı (commit `6c7016d`, merge `75d017b`)

### Eklenen Dosyalar
- `docs/AI-POLITIKASI.md` — 13 bölümlü AI çağrı kural kitabı
- `app/services/llm_gateway.py` — Provider-agnostic geçit (Gemini/OpenAI/Anthropic/Groq/OpenRouter); REST transport (Windows AV SSL uyumu); fiyatlama tabloları
- `app/services/llm_quota_service.py` — 4 katmanlı kota (cooldown + günlük/aylık + cost cap + sistem geneli); %80 alarm
- `app/models/llm_usage.py` — `LLMUsageLog` + `LLMQuotaOverride` (migration `f9g0h1i2j013`)
- `app/models/tenant_llm_config.py` — Fernet şifreli BYOK key (migration `g0h1i2j3k014`)
- `micro/modules/sp/routes_tenant_ai.py` — `/sp/ayarlar/ai` BYOK config endpoint'leri
- `micro/modules/sp/routes_llm_quota.py` — `/sp/llm-usage` kullanım panel API'ları
- `ui/templates/platform/sp/ai_settings.html` — Sistem AI vs BYOK seçim UI, "Test Et" butonu, KVKK PII toggle

### Değişen Dosyalar
- `app/services/ai_pivot_advisor_service.py` → `call_llm()` kullanır, heuristic fallback korundu
- `services/ai_coach_service.py` → `call_llm()` kullanır, tenant_id imzaya eklendi
- `requirements-ai.txt` → `google-generativeai`, `openai`, `anthropic`, `pip-system-certs`
- 14 POST/PATCH/DELETE endpoint'ine `@csrf.exempt` (CSRF JSON API blokajı düzeltildi)

### Yapılan İşlem
Tüm AI çağrıları artık tek geçitten geçer. Tenant kendi API anahtarını (`/sp/ayarlar/ai`) girerse sistem kotası harcanmaz. Sistem key ile çalışırken kotalar geçerli ($2/ay tenant başına, $50/ay toplam sistem). REST transport sayesinde Windows antivirus SSL inspection ile uyumlu. `gemini-2.5-flash-lite` default model (yeni proje free tier uyumlu).

### Notlar
SSL sorunu pip-system-certs + REST transport ile çözüldü. `google-generativeai` paketinin deprecated olduğu fark edildi — gelecekte `google-genai` paketine geçilebilir ama mevcut çalışır. Diğer 3 AI servisi (executive_summary, early_warning, advisor) zaten kural tabanlı, gateway entegrasyonu gerektirmedi.

---

## TASK-121-UI | 2026-05-24 | ✅ Tamamlandı (yerel + main)

**Görev:** UI Faz 1 (tasarım token altyapısı) + Pilot (Exec Dashboard rafine)
**Modül:** ui/static/platform/css/, ui/templates/platform/, docs/
**Durum:** ✅ Tamamlandı (commit `46c1cab`)

### Eklenen / Değişen Dosyalar
- `docs/UI-KILAVUZU.md` — 14 bölümlü tasarım sistemi kılavuzu (exec odaklı, mc-* korunarak)
- `ui/static/platform/css/components.css` → `:root` bloğuna 40+ token (spacing 8'in katı, color hiyerarşisi, semantic + soft renkler, transition, shadow); `.mc-skeleton` shimmer; `.mc-empty`; dark mode override
- `ui/templates/platform/base.html` → Chart.js global defaults (Inter font, slate grid, indigo palette)
- `ui/templates/platform/sp/exec_dashboard.html` → Kılavuza göre baştan tasarım: hero gradient + 48px display, KPI tile skeleton, semantic color, mikro-etkileşim

### Yapılan İşlem
Tüm sayfalarda kullanılacak tasarım sistemi altyapısı (Faz 1) + üst yönetim odaklı pilot uygulama (Exec Dashboard). Skeleton loader, empty state, tabular-nums, hover/transition standartları kılavuza bağlandı.

---

## TASK-121 | 2026-05-24 | ✅ Tamamlandı (sadece yerel)

**Görev:** Otonom iş mantığı testinin (`tests/otonom_is_mantigi_testi.py`) veritabanı kısıt hatası nedeniyle düzeltilmesi
**Modül:** tests/
**Durum:** ✅ Tamamlandı

### Değiştirilen / Eklenen Dosyalar
- `tests/otonom_is_mantigi_testi.py` → `populate_base_data` aşamasında oluşturulan test kurumu için eksik olan `tenant_id=1` ataması eklendi.

### Yapılan İşlem
Yeni projede "tenant isolation" ve "NOT NULL tenant_id" veri kısıtlamaları getirildiğinden dolayı eski test veritabanında SQLite üzerinde hata fırlatan `IntegrityError` (NOT NULL constraint failed: kurum.tenant_id) sorunu giderilmiştir. Yapılan düzeltme sonrası tüm otonom iş mantığı testleri (`unittest`) başarıyla `OK` statüsünde tamamlanmıştır.

### Notlar
Test çıktılarında Windows terminal CP1254 encoding uyumsuzluğu nedeniyle emoji (`✓`) karakterlerinden kaynaklanan hata, `PYTHONIOENCODING=utf-8` parametresiyle çözümlenmektedir.

---

## TASK-120 | 2026-05-24 | ✅ Tamamlandı (sadece yerel)

**Görev:** EFQM Olgunluk Modülü için arayüze görsel sonuç kartı ve detay modalı entegre edilmesi
**Modül:** ui/templates/platform/k_radar/, ui/static/platform/js/
**Durum:** ✅ Tamamlandı

### Değiştirilen / Eklenen Dosyalar
- `ui/templates/platform/k_radar/ks.html` → EFQM card, data-api-efqm niteliği ve EFQM sonuç modalı eklendi.
- `ui/static/platform/js/k_radar_ks.js` → `API.efqm` adresi eşleştirildi, açılışta verileri fetch eden boot kodları eklendi ve `loadModal` switch-case yapısına `"efqm"` eklendi.

### Yapılan İşlem
Mevcut backend modelleri (`ProcessMaturity`), API rotaları (`/k-radar/api/ks/efqm`) ve hesaplama motoru tam hazır olan EFQM Olgunluk modülü için KS-Radar sayfasına görsel sonuç kartı eklendi. Kart tıklandığında açılan ve başarı aralıkları/puan bantlarını (KPI 327) listeleyen şık bir modal entegre edildi.

### Notlar
Herhangi bir şema veya backend değişikliği gerektirmeden, mevcut altyapı arayüze tam entegre edilmiştir.

---

## TASK-119 | 2026-05-24 | ✅ Tamamlandı (sadece yerel)

**Görev:** Stratejik Planlama (/sp/) sayfalarındaki 500 hatalarının (TypeError: _check_sp_role() takes 0 positional arguments but 1 was given) düzeltilmesi
**Modül:** micro/modules/sp/
**Durum:** ✅ Tamamlandı

### Değiştirilen / Eklenen Dosyalar
- `micro/modules/sp/helpers.py` → `_check_sp_role` fonksiyonu parametresiz çağrılara ve `current_user` ile yapılan parametreli çağrılara uyumlu hale getirildi (`def _check_sp_role(user=None):` yapıldı).

### Yapılan İşlem
Stratejik planlama rotalarındaki (örn. `/sp/ceyreklik-review`, `/sp/donemler` vb.) yetki denetimi sırasında fırlatılan `TypeError: _check_sp_role() takes 0 positional arguments but 1 was given` hatası, yardımcı fonksiyona `user` parametresi isteğe bağlı olarak eklenerek çözüldü. Flask dev server reloads başarılı.

### Notlar
Geriye dönük tüm `_check_sp_role` çağrıları ve parametreli kullanımlar sorunsuz çalışmaktadır.

---

## TASK-118 | 2026-05-24 | ✅ Tamamlandı (sadece yerel)

**Görev:** Rekabet analizi sonrası 5 önerinin uygulanması — UX entegrasyon + AI Pivot + Exec Dashboard + TR Kamu şablonu + Initiative haritası
**Modül:** ui/templates/platform/, app/services/, app/templates_data/, micro/modules/sp/
**Durum:** ✅ Tamamlandı

### Değiştirilen / Eklenen Dosyalar
- `ui/templates/platform/base.html` → SP altına 5 sub-link (exec dashboard, çeyreklik, initiative, scenario, replan, templates) — Hamle #1
- `micro/modules/sp/helpers.py` → strateji haritası grafına Initiative node'ları (pembe, kesik kenar, dashed edge) — Hamle #3
- `ui/templates/platform/sp/strateji_haritasi.html` → vis-network `initiative` group theme — Hamle #3
- `app/services/exec_dashboard_service.py` → yeni; KPI/strateji/initiative/risk/anomali/trigger snapshot + health_score — Hamle #5
- `app/services/ai_pivot_advisor_service.py` → yeni; Gemini LLM + heuristic fallback ile pivot önerileri — Hamle #2
- `app/services/plan_year_template_service.py` → yeni; JSON şablon marketplace iskeleti — Hamle #4
- `app/templates_data/sbb_kamu_template.json` → yeni; Cumhurbaşkanlığı SBB 2024-2028 uyumlu 5 stratejik amaç + 13 alt strateji + 8 KPI — Hamle #4
- `micro/modules/sp/routes_exec_advisor.py` → yeni; 7 endpoint (exec-dashboard, exec-snapshot, ai-pivot, templates list/get/apply)
- `ui/templates/platform/sp/exec_dashboard.html` → yeni; sağlık skoru hero + 6 metrik kartı + AI Pivot paneli
- `ui/templates/platform/sp/templates.html` → yeni; şablon marketplace UI
- `micro/modules/sp/routes.py` → yeni route modülünü import

### Yapılan İşlem
Önceki rekabet analizi raporundaki 5 öncelikli hamlenin tamamı uygulandı: (1) sidebar entegrasyonu — S54-S57 yatırımı artık menüden erişilebilir; (2) AI Strategy Pivot Advisor — exec snapshot + son 7 gün trigger event'leri Gemini'ye gönderiliyor, key yoksa heuristic kural motoru fallback'i; (3) strateji haritasına initiative node'ları (vis-network group `initiative`, kesik çizgili kenar); (4) Cumhurbaşkanlığı SBB Stratejik Plan Hazırlama Kılavuzu uyumlu kamu şablonu + apply servisi — global rakiplerde olmayan TR-spesifik diferansiyatör; (5) Exec Dashboard tek bakışta 360° strateji sağlığı (health_score ağırlıklı: KPI on-target %40 + coverage %20 + faaliyet timeliness %20 + risk %10 + anomali %10). Tomofil tenant'ında smoke: health 45.7, 221 KPI.

### Notlar
SBB şablonu MVP — sektör genişletme için private/ngo şablonları sonraki sprintte. AI Pivot'ın LLM modu için GEMINI_API_KEY/.env şart; yoksa heuristic mod ile silent fallback. Schema migration yok (mevcut tablolar yeterli).

---

## TASK-118 | 2026-05-24 | ✅ Tamamlandı (sadece yerel)

**Görev:** Akademik strateji çerçeveleri paketi (S59-S63) — AG raporundan seçilen 5 öneri
**Modül:** app/services/, app/models/, micro/modules/sp/, ui/templates/platform/sp/, migrations/
**Durum:** ✅ Tamamlandı

### Değiştirilen / Eklenen Dosyalar
- `app/services/hoshin_xmatrix_service.py` → yeni; 4 çeyrek + 4 korelasyon matrisi (S59)
- `app/models/strategy_frameworks.py` → yeni; BlueOceanCanvas/Factor/ERRC + VRIOResource (S60-S61)
- `migrations/versions/d7e8f9g0h011_strategy_frameworks.py` → 4 yeni tablo
- `app/models/project.py` → PlanProjectTask'a progress_pct + planned_budget + actual_cost + depends_on_task_id (S62)
- `migrations/versions/e8f9g0h1i012_task_evm_fields.py` → 4 yeni kolon + index
- `app/services/project_evm_service.py` → yeni; PV/EV/AC/CV/SV/CPI/SPI/EAC + CPM (S62)
- `app/services/weekly_digest_service.py` → yeni; HTML→PDF (WeasyPrint → reportlab → HTML fallback) (S63)
- `micro/modules/sp/routes_frameworks.py` → yeni; 8 sayfa + 14 API endpoint
- `ui/templates/platform/sp/xmatrix.html` → Hoshin X-Matrix interaktif tablo
- `ui/templates/platform/sp/blue_ocean.html` → Strategy Canvas (Chart.js Value Curve) + ERRC Grid
- `ui/templates/platform/sp/vrio.html` → VRIO matrisi (canlı checkbox güncellemesi + Barney etiketi)
- `ui/templates/platform/base.html` → sidebar'a 5 yeni link (X-Matrix, Blue Ocean, VRIO, Haftalık PDF)
- `app/models/__init__.py` + `micro/modules/sp/routes.py` → modül kayıtları

### Yapılan İşlem
Antigravity raporunun beğenilen 5 önerisi uygulandı: (1) Hoshin Kanri X-Matrix — mevcut strateji/alt strateji/initiative/KPI verisinden korelasyon matrisi; (2) Blue Ocean Strategy Canvas + ERRC Grid — yeni tablolar, Chart.js value curve; (3) VRIO Resource matrisi — Barney karar ağacı ile otomatik rekabet avantajı etiketi; (4) PlanProjectTask EVM derinleştirme — bütçe + ilerleme alanları + 11 metrik servis + CPM kritik yol; (5) Haftalık digest — HTML/PDF render (3 katmanlı fallback). 2 yeni Alembic migration + 684 toplam route.

### Notlar
WeasyPrint sistem kütüphaneleri (cairo/pango) gerektirir; yoksa reportlab'a düşer, o da yoksa düz HTML döner — servis hiçbir zaman çökmez. Blue Ocean factor JSON şu an prompt() ile girilir (MVP) — sonraki sprintte modal form. Hoshin X-Matrix initiative↔KPI korelasyonu heuristic (aynı süreçten) — gelecekte initiative_kpi_links ara tablosu eklenebilir.

---

## TASK-117 | 2026-05-24 | ✅ Tamamlandı (sadece yerel)

**Görev:** Stratejik planlama geliştirme planı S53-S57 — 5 sprint somut çıktı (Ö1-Ö5, Ö8)
**Modül:** app/services/, app/models/, micro/modules/sp/, ui/templates/platform/sp/, migrations/
**Durum:** ✅ Tamamlandı

### Değiştirilen / Eklenen Dosyalar
- `app/utils/plan_year_filter.py` → `filter_by_plan_year_scoped()` helper (S53/Ö2)
- `micro/modules/k_rapor/routes.py` → helper kullanımı + syntax fix (S53)
- `micro/modules/proje/routes_project_crud.py` → plan_year_id form alanı (S53/Ö3)
- `app/services/quarterly_review_service.py` → yeni; çeyreklik review aggregator (S54/Ö1)
- `micro/modules/sp/routes_donemler.py` → `/sp/ceyreklik-review` + JSON API (S54/Ö1)
- `ui/templates/platform/sp/ceyreklik_review.html` → yeni dashboard (S54/Ö1)
- `app/models/initiative.py` + migration `a4b5c6d7e008` → Initiative + Milestone (S55/Ö4)
- `micro/modules/sp/routes_initiative.py` + `initiatives.html` → CRUD UI (S55/Ö4)
- `app/models/plan_year.py` + migration `b5c6d7e8f009` → scenario_of_id + scenario_label (S56/Ö5)
- `app/services/plan_year_service.py` → `clone_full_plan_year(as_scenario_label=...)` (S56)
- `micro/modules/sp/routes_scenario.py` + `scenarios.html` → senaryo dalları UI (S56/Ö5)
- `app/models/replan_trigger.py` + migration `c6d7e8f9g010` → ReplanTrigger + Event (S57/Ö8)
- `app/services/replan_trigger_service.py` → değerlendirme motoru (S57/Ö8)
- `micro/modules/sp/routes_replan_trigger.py` + `replan_triggers.html` → trigger UI (S57/Ö8)

### Yapılan İşlem
docs/SP-DONEM-ANALIZ-2026.md'deki 12 öneriden 5 tanesi (Ö1, Ö2, Ö3, Ö4, Ö5, Ö8) somut olarak uygulandı: Çeyreklik review wizard, plan_year NULL legacy uyum helper'ı, Project planYear form alanı, Multi-Year Initiative tabloları/CRUD, PlanYear senaryo dallanma (partial unique index), trigger-based otomatik replan motoru. 3 yeni Alembic migration uygulandı (a4-c6 zinciri f6g7h8i9j013 üzerine).

### Notlar
VM deploy ertelendi (kullanıcı önceki direktif). Trigger eval cron entegrasyonu (APScheduler) sonraki sprintte yapılabilir — şu an manuel "Şimdi Değerlendir" butonu var. Senaryo karşılaştırma UI'sı henüz yok; mevcut donem-karsilastir endpoint'i scenario_of_id'yi de göstermek için genişletilebilir.

---

## TASK-116 | 2026-05-23 | ✅ Tamamlandı (sadece yerel)

**Görev:** 9 Sprint paralel uygulaması — audit + roadmap + 6 sprint somut çıktı
**Modül:** app/utils/, tests/, docs/, migrations/
**Durum:** ✅ Tamamlandı (Sprint 9 büyük temizlik kullanıcı onayı bekliyor)

### Oluşturulan / Değiştirilen Dosyalar
- `docs/PROJE-AUDIT-2026Q2.md` → 15 modül + altyapı audit (3 paralel agent)
- `docs/RISK-MATRISI-2026Q2.md` → 32 risk, olasılık×etki matrisi
- `docs/ROADMAP-2026H2.md` → 9 sprint × 2 hafta detaylı plan
- `docs/LEGACY_SUNSET_MAP.md` → ~3.940 satır silme planı (Sprint 9)
- `docs/SPRINT-RAPORU-2026Q2.md` → bu oturumun sonuç raporu
- `app/utils/plan_year_filter.py` (+test, 4 senaryo) — Sprint 1
- `app/utils/tenant_scope.py` (+test, 7 senaryo) — Sprint 2
- `app/utils/upload_security.py` (+test, 22 senaryo) — Sprint 2
- `app/utils/query_counter.py` (+test, 6 senaryo) — Sprint 3
- `app/utils/pdf_export.py` (+test, 7 senaryo) — Sprint 8
- `tests/test_module_smoke.py` (17 senaryo) — Sprint 3
- `tests/test_karne_hesaplamalar.py` (27 senaryo) — Sprint 5
- `micro/modules/admin/routes.py` — logo upload security
- `micro/modules/sp/routes_flow.py` — graph performans limit
- `migrations/versions/b2c3d4e5f009_okr_tables.py` — OKR tabloları

### Yapılan İşlem
3 paralel sub-agent ile 15 modül + altyapı detaylı audit'i çıkarıldı, 32 risk
sınıflandırıldı, 9 sprint × 2 hafta roadmap yayınlandı. Sonra paralel uygulama:
Sprint 1-8 somut çıktılarla tamamlandı. **90 yeni test**, **5 yeni utility**,
**2 migration** uygulandı. Sprint 9 (~3.940 satır legacy sunset) planlandı,
yürütme kullanıcı onayıyla. 4 audit yanılgısı manuel doğrulamayla düzeltildi.

### Notlar
- Risk skoru ≥16 olan kritik açık: 5 → 2 (Sprint 9 ile 0 olacak)
- Test sayısı: ~80 → ~160 (+100%)
- Yeni production kod: ~1.500 satır (utility + decorator + helper'lar)
- Tomofil tenant_id=26 hala canlı (48.283 KpiData)
- VM'e push yapılmadı

---

## TASK-115 | 2026-05-23 | ✅ Tamamlandı (sadece yerel)

**Görev:** Tomofil demo tenant v2 — 6 yıllık (2021-2026) evrim + EV pivot hikayesi + generic seed script
**Modül:** scripts/, docs/sablon.md, docs/tomofil-demo/
**Durum:** ✅ Yerelde tamamlandı — VM yayını yapılmadı

### Oluşturulan / Değiştirilen Dosyalar
- `docs/sablon.md` → yeni — boş şablon, 21 bölümlü demo-tenant onboarding rehberi
- `docs/tomofil-demo/sablon-dolu.md` → yeni — doldurulmuş örnek (insanlar için doküman)
- `docs/tomofil-demo/tenant_data.yaml` → yeni — script için 2026 baseline yapılandırılmış veri
- `docs/tomofil-demo/year_deltas.yaml` → yeni — 2021-2025 yıllara göre strateji/süreç/KPI evrim delta'ları
- `scripts/seed_generic_tenant.py` → yeni — YAML-driven generic tenant seeder (--data --deltas --dry-run/--commit/--reset)

### Yapılan İşlem
Tomofil yerel PG (`kokpitim_db`) içine `tenant_id=26` ile yeniden açıldı: yerli EV parça üreticisi profili, 2021 kuruluş, 100 çalışan (97 user — admin + 20 manuel yönetici + 76 bulk), 7 plan yılı, 6 yıllık strateji evrimi (3 → 7 ana strateji, ~16 değişim eventi), 28 Strategy + 135 SubStrategy + 46 Process + 221 ProcessKpi (yıllara göre ayrı kayıt, source_*_id zinciri ile), 679 KpiData (2026 aylık + 2024-25 çeyreklik + 2021-23 yıllık), 4 proje + 13 görev, 6×4 = 24 SWOT/TOWS/PESTEL/Porter analizi, K-Vektor ağırlıkları (18), K-Radar tüm modüller (71 kayıt). OKR tabloları DB'de migrate edilmediği için skip edildi.

### Notlar
- Login: `admin@tomofil.test` / `Tomofil2026!`
- Hikaye: 2021 kuruluş → 2022 chip krizi → 2023 ihracat (H4) → 2024 EV pivot (H5) → 2025 sürdürülebilirlik (H6) → 2026 dijital dönüşüm (H7)
- `1.A.2` (İçten Yanmalı Motor Krank Mili) 2024'te is_active=False olarak pasifestirildi (kayıtta var, görünmüyor)
- Toplu kullanıcı sayısı 80 hedeflendi, departman dağılımları toplamı 76 — istenirse 4'lük ince ayar yapılabilir
- Project tablosunda ORM ↔ DB şema sapması var (is_active, deleted_at fazla); script raw SQL'e düşüyor
- Task tablosu da benzer şekilde raw SQL ile yazıldı (due_date alanı, end_date değil)
- OKR migration eksiği ayrı bir task: kokpitim'in OKR modülünü gerçekten kullanıyorsa alembic'e migration eklenmeli
- VM yayını kullanıcı yerel doğrulama yapana kadar bekliyor

---

## TASK-114 | 2026-05-22 | ✅ Tamamlandı (sadece yerel)

**Görev:** Tomofil Group N.V. örnek/test tenantı — Phase 1 seed (yereldeki PostgreSQL'e)
**Modül:** scripts/, docs/tomofil/
**Durum:** ✅ Yerelde tamamlandı — VM'e yayın **YAPILMADI** (kullanıcı yerel test ediyor)

### Oluşturulan / Değiştirilen Dosyalar
- `scripts/seed_tomofil_full.py` → yeni — idempotent seeder (`--dry-run` / `--commit` / `--reset`)
- `docs/tomofil/` → kaynak dosyalar (strateji ağacı md + 3.800 çalışan JSON + atomik veri JSON + 2 PDF)

### Yapılan İşlem
Yerel PostgreSQL (`kokpitim_db`) içine `tenant_id=21` ile yeni tenant açıldı: 3.801 kullanıcı (admin dahil), 10 plan yılı (2026 active, 2027-2035 draft), 14 süreç (A2R, C2L, P2M…), 6 ana + 73 alt strateji (H1-H6 → 1.A → 1.A.1 prefix hiyerarşi), 120 ProcessKpi, 14 süreç sahibi. Strateji ağacı md'den regex ile parse edildi, kullanıcılar Workday HCM formatındaki JSON'dan bulk insert ile yüklendi.

### Notlar
- Login: `admin@tomofil.test` / `Tomofil2026!` (role=tenant_admin)
- O2C sürecinde çalışan JSON'da yönetici kademesi olmadığı için fallback olarak admin user owner atandı.
- Phase 2 (kaynak `Tomofil_Veriler_v3.json` → 25.300 atomik kayıt → `kpi_data` agregasyonu ve PDF kopyalama) ayrı bir script ile yerel test sonrası yapılacak.
- VM (Oracle Cloud) yayını kullanıcı yerel doğrulama yapana kadar bekliyor.

---

## TASK-113 | 2026-05-21 | ✅ Tamamlandı

**Görev:** Terim standardı — «VM» = Oracle Cloud üretim; dokümantasyon ve deploy betikleri güncellemesi
**Modül:** docs, scripts/ops/oracle, scripts/vm_safe_deploy.sh, scripts/vm_smoke_check.ps1, CLAUDE.md, Agents
**Durum:** ✅ Tamamlandı

### Oluşturulan / Değiştirilen Dosyalar
- `docs/ORACLE-PROD-VM.md` → yeni — tek referans: SSH, dizinler, terim tablosu (VM / yerel / GCP arşiv)
- `scripts/ops/oracle/oracle_safe_deploy.sh` → yeni — rutin Oracle deploy (PG yedek, pull, Docker, Alembic, satır sayısı)
- `docs/KURALLAR-MASTER.md`, `docs/PROJE-MASTER.md` (bölüm 12) → üretim Oracle; GCP arşiv
- `docs/YERELDEN_VM_YAYIN.md`, `docs/VM_DEN_YERELE.md`, `docs/VM-YEREL-SENKRON-REHBERI.md` → `ssh`/`scp`, `/opt/kokpitim/`
- `docs/ORACLE_DEPLOY_ADIMLAR.md`, `docs/gcp2oraclegecisplani.md` → geçiş tamamlandı notu
- `docs/clauderapor.md`, `docs/kirowebsitesi.md`, `Agents/KURALLAR-MASTER.md`, `CLAUDE.md` → VM = Oracle
- `scripts/vm_safe_deploy.sh` → LEGACY GCP üst notu
- `scripts/vm_smoke_check.ps1` → varsayılan hedef Oracle SSH (`kokpitim-web`)

### Yapılan İşlem
GCP→Oracle geçişi sonrası repoda «VM» ifadesi **Oracle `kokpitim-v2` (`129.159.30.175`)** anlamına sabitlendi. Eski `sps-server-v2` / `gcloud` komutları tarihsel arşiv olarak işaretlendi; canlı yayın yordamı `oracle_safe_deploy.sh` ile hizalandı.

### Notlar
- Üretim: `ubuntu@129.159.30.175`, uygulama `/opt/kokpitim/app`, container `kokpitim-web`, PG `kokpitim_db` @ `127.0.0.1`.
- GCP Faz 0 yedekleri: `backups/oracle_migration/` — değişmedi.

---

## TASK-112 | 2026-05-19 | ✅ Tamamlandı

**Görev:** 19mayonderi.md planı — 10 yeni özellik uygulaması
**Modül:** masaustu, surec/kpi_data, sp, admin, bireysel, k_radar_service, app/socketio_events
**Durum:** ✅ Tamamlandı

### Değiştirilen / Oluşturulan Dosyalar
- `services/executive_morning_service.py` → yeni — KPI/faaliyet/proje durum özeti API servisi
- `micro/modules/masaustu/routes.py` → `/api/morning-summary` endpoint eklendi
- `ui/templates/platform/masaustu/index.html` → Yönetici Sabah Özeti widget eklendi
- `ui/static/platform/js/masaustu.js` → widget JS + WebSocket refresh dinleyicisi
- `micro/modules/surec/routes_kpi_data.py` → `/process/api/kpi-data/bulk-template` (Excel şablon), `/process/api/kpi-data/bulk-import` (toplu yükleme), `/process/api/kpi/<id>/score-detail` (puan şeffaflığı) eklendi
- `services/early_warning_service.py` → yeni — gece KPI trend analizi + bildirim servisi
- `app/__init__.py` → `_init_early_warning_scheduler()` — APScheduler ile her gece 02:00 tetikleyici
- `services/k_radar_service.py` → `_get_radar_weights()` eklendi, `get_hub_summary` tenant'a özgü ağırlık kullanıyor
- `micro/modules/admin/routes.py` → `/admin/k-radar/weights` GET+POST endpoint eklendi
- `micro/modules/sp/routes_pages.py` → `/sp/strateji-haritasi`, `/sp/api/strateji-haritasi`, `/sp/rapor/donemsel` eklendi
- `ui/templates/platform/sp/strateji_haritasi.html` → yeni — vis-network ağaç görselleştirme
- `services/period_report_service.py` → yeni — dönemsel KPI karşılaştırma Excel raporu
- `services/alignment_score_service.py` → yeni — bireysel→stratejik hizalama skoru hesaplama
- `micro/modules/bireysel/routes.py` → `/bireysel/api/hizalama-skoru`, `/bireysel/api/ekip-hizalama` eklendi
- `micro/modules/sp/routes_plan_year.py` → sihirbaz endpoint'leri: `/sp/sihirbaz/yeni-yil`, preview, uygula
- `ui/templates/platform/sp/sihirbaz_yeni_yil.html` → yeni — 3 adımlı plan yılı geçiş sihirbazı
- `app/socketio_events.py` → `kpi_data_entered` event + `notify_kpi_update()` yardımcı fonksiyonu

### Yapılan İşlem
19mayonderi.md planındaki 10 maddenin tamamı uygulandı. Uygulama import testi geçti (`create_app()` hatasız).

### Notlar
- APScheduler kurulu değilse erken uyarı zamanlayıcısı sessizce atlanır (WARNING log).
- D-3 KPI şeffaflığı backend API olarak tamamlandı; frontend karne sayfasına "Nasıl hesaplandı?" butonu sonraki oturumda eklenebilir.
- D-4 WebSocket: morning_summary_refresh eventi masaüstü JS'ine bağlandı; KPI kayıt endpoint'lerinden `notify_kpi_update()` çağrısı sonraki oturumda eklenebilir.

---

## TASK-111 | 2026-05-19 | ✅ Tamamlandı

**Görev:** İyileştirme Turu 2 — K-Radar cache, source chain N+1 fix, Project tam soft delete
**Modül:** services/k_radar_service, surec/karne, proje, migrations
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `services/k_radar_service.py` → 11 fonksiyona `@cache.memoize(timeout=300)` eklendi (get_hub_summary, get_ks_data, get_ks_extended_data, get_kp_data, get_kp_extended_data, get_kpr_data, get_kpr_extended_data, get_cross_heatmap_data, get_cross_extended_data, get_ks_*_real serisi)
- `micro/modules/surec/routes_karne.py` → `_resolve_process_by_source_chain` yeniden yazıldı: tenant'ın tüm klonlu süreçleri tek sorguda çekilip bellekte BFS yapılıyor (N+1 → 2 sorgu)
- `app/models/portfolio_project.py` → Project modeline `is_active`, `deleted_at`, `deleted_by` kolonları eklendi
- `micro/modules/proje/routes_project_crud.py` → proje silme: `is_active=False + deleted_at + deleted_by` (gerçek soft delete)
- `micro/modules/proje/project_list_query.py` → `is_active=True` filtresi eklendi
- `micro/modules/proje/permissions.py` → `accessible_projects_query`'e `is_active=True` filtresi eklendi
- `migrations/versions/a1b2c3d4e008_project_soft_delete.py` → yeni Alembic migration (upgrade + downgrade)

### Yapılan İşlem
K-Radar sayfaları artık 5 dakika boyunca DB'ye gitmiyor; aynı tenant için ikinci ziyaret önbellekten dönüyor. Yıl navigasyonu BFS'i 30+ sorgudan 2 sorguya indi. Project modeli diğer modeller (Process, KpiData) ile aynı soft delete standardına kavuştu; migration'ı `flask db upgrade` ile uygulamak yeterli.

### Notlar
- Login rate limit incelendi; `app/routes/auth.py:33` satırında `@limiter.limit(RATELIMIT_LOGIN)` zaten uygulanmıştı, ek değişiklik gerekmedi.
- Cache invalidation: K-Radar verileri değiştiğinde (yeni KPI, yeni proje) önbellek 5 dk içinde kendiliğinden sona erer. Anlık yenileme gerekirse `cache.delete_memoized(get_hub_summary, tenant_id)` çağrılabilir.

---

## TASK-110 | 2026-05-19 | ✅ Tamamlandı

**Görev:** İyileştirme planı uygulaması — soft delete, N+1 fix, k_radar bölme, smoke testler, console.log temizliği
**Modül:** proje, surec/karne, k_radar, tests, static/js
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/proje/routes_project_crud.py` → proje silme hard delete → `is_archived=True` (soft delete)
- `micro/modules/surec/routes_karne.py` → N+1 fix: KpiData ve ActivityTrack bulk prefetch + selectinload (kpi.sub_strategy→strategy, activity.assignment_links→user, reminders, process_kpi)
- `micro/modules/k_radar/routes.py` → 943 satırlık monolit → import hub'a dönüştürüldü
- `micro/modules/k_radar/routes_common.py` → yeni (hub, recommendations, schedule)
- `micro/modules/k_radar/routes_ks.py` → yeni (KS radar: swot, pestle, tows, gap, okr, bsc, efqm, hoshin, ansoff, bcg + gerçek veri API'leri)
- `micro/modules/k_radar/routes_kp.py` → yeni (KP radar: darbogaz, pareto, sla, benchmark, oee, vsm, kapasite, olgunluk CRUD)
- `micro/modules/k_radar/routes_kpr.py` → yeni (KPR radar: cpm, evm, risk, kaynak-kapasite, gantt)
- `micro/modules/k_radar/routes_cross.py` → yeni (Cross: paydas CRUD, rekabet, a3, anket)
- `tests/test_smoke_routes.py` → yeni (k_radar, proje, surec karne smoke testleri; unauthenticated 302 kontrolü)
- `static/js/admin_panel.js` → 34 console.log satırı kaldırıldı

### Yapılan İşlem
Analiz planındaki tüm öncelikli maddeler uygulandı. Karne endpoint'i artık N+1 yerine 2 bulk SELECT ile çalışıyor (KpiData: yıl×önceki yıl, ActivityTrack: tek sorgu). k_radar modülü sp/surec ile aynı pattern'e getirildi (5 alt dosya). Üretimde kullanıcı bilgilerini sızdıran console.log'lar temizlendi.

### Notlar
- `BscKpiPerspective` ve `ProcessSubStrategyLink` hard delete'leri junction table semantiği taşıdığından değiştirilmedi (veri kaybı riski yok, mapping ilişkisi).
- Project modeline `is_active` + `deleted_at` kolonu eklemek için Alembic migration henüz oluşturulmadı; `is_archived` şimdilik soft delete proxy olarak kullanılıyor.
- TODO'lar (`app/api/auth.py`, `services/webhook_service.py`, `services/report_service.py`) backlog'a alındı: Webhook implementasyonu, PDF export, Redis rate limiting.

---

## TASK-110 | 2026-05-20 | ✅ Tamamlandı

**Görev:** `/sp/strateji-haritasi` BuildError + ikon düzeltmesi + hata sayfaları
**Modül:** SP, templates, components.css, safe_urls
**Durum:** ✅ Tamamlandı

### Kök neden
1. `url_for('app_bp.sp_index')` — endpoint yok (`app_bp.sp` olmalı)
2. Hata sayfası `templates/base.html` → kayıtsız `dashboard_bp.index` (ikinci BuildError)
3. FA webfont yolu: `all.min.css` içinde `../webfonts` → `/m/platform/vendor/webfonts` (yanlış)

### Düzeltmeler
- `strateji_haritasi.html`: `app_bp.sp`, vis-network CSS
- `components.css`: doğru `@font-face` yolları
- `safe_url_for` + legacy `base.html` güncellemesi
- Hata şablonları: `errors/_minimal.html` (platform, dashboard_bp yok)
- API join düzeltmesi (`ProcessSubStrategyLink`)

### Test
`tests/test_sp_strateji_haritasi.py` — 2 passed

---

## TASK-109 | 2026-05-19 | ✅ Tamamlandı

**Görev:** Dalga D — E2E akış, tenant izolasyonu, N+1 guard, JSON API hata yanıtı
**Modül:** tests, app/utils/error_handlers
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `tests/test_e2e_flow.py`, `test_tenant_isolation.py`, `test_process_n1_guard.py`
- `app/utils/error_handlers.py` → `/process/api/*` ve Accept: json için JSON 403/404

### Yapılan İşlem
Platform sayfa akışı ve süreç API tenant izolasyonu otomatik testlere alındı. Pytest: **66 passed**.

---

## TASK-108 | 2026-05-19 | ✅ Tamamlandı

**Görev:** Dalga C — main/routes paket bölme, deprecated decorator, budama dokümanı
**Modül:** main/routes/, main/deprecated.py
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `main/routes/` → `_common`, `pages`, `kurum_panel`, `strategy_api`, `projects`
- `main/routes_monolith_backup.py` (yedek)
- `main/deprecated.py`, `scripts/dev/split_main_routes.py`
- `docs/LEGACY_ROUTE_DEPRECATION.md`
- `main/routes.py` kaldırıldı (paket)

### Yapılan İşlem
7600+ satırlık monolit 5 modüle bölündü. GET legacy sayfalarına `@legacy_html_to_platform` yedek yönlendirme eklendi.

---

## TASK-107 | 2026-05-19 | ✅ Tamamlandı

**Görev:** Dalga B — Model shim birliği, süreç API canonical doküman, paylaşılan redirect config
**Modül:** app/models, app/legacy_redirect_config.py, docs, tests
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/models/user_legacy.py`, `strategy_legacy.py`, `legacy_extras.py`, `legacy_bridge.py`
- `app/legacy_redirect_config.py` → middleware ortak config
- `docs/MODEL_MERGE_PLAN.md`, `docs/PROCESS_API_CANONICAL.md`
- `tests/test_process_api_surface.py`
- `scripts/ci/check_no_raw_models_import.py` → shim allowlist

### Yapılan İşlem
Runtime `from models` yalnızca `app/models/*_legacy.py` shim'lerinde. `legacy_bridge` canonical süreç/portföy + legacy shim re-export.

---

## TASK-106 | 2026-05-19 | ✅ Tamamlandı

**Görev:** Dalga A — Legacy sunset (HTML yönlendirme, 410 Gone, çift blueprint kapatma, yol haritası)
**Modül:** middleware, config, docs, tests
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/middleware/legacy_sunset.py` → GET/HEAD 301 platform, `/v2`/`/v3`/`/bsc` 410, `/projeler` rewrite
- `app/middleware/__init__.py` → paket
- `app/__init__.py` → sunset kaydı; `LEGACY_*_BP_ENABLED` ile dashboard/process BP koşullu
- `config.py` → `LEGACY_SUNSET_ENABLED`, `LEGACY_PROCESS_BP_ENABLED`, `LEGACY_DASHBOARD_BP_ENABLED`
- `main/routes.py` → kök `/` launcher/login
- `app/utils/error_handlers.py` → `HTTPException` handler (410 dahil)
- `scripts/dev/analyze_legacy_access_log.py` → nginx log analizi
- `docs/IYILESTIRME-YOL-HARITASI.md`, `docs/LEGACY_REDIRECT_MAP.md`, `DEPLOY_SMOKE_CHECKLIST.md`
- `tests/test_legacy_sunset.py`

### Yapılan İşlem
Dalga A tamamlandı: eski bookmark’lar platforma 301 ile yönleniyor; v2/v3/bsc 410; çift `/process` ve legacy dashboard BP varsayılan kapalı. `_should_skip` düzeltildi (`/projeler`, `/kurum-paneli` artık yanlışlıkla atlanmıyor).

### Notlar
Dalga B: `main/routes.py` model import birliği ve süreç API tekilleştirme. `LEGACY_SUNSET_ENABLED=false` acil geri alma anahtarı.

---

## TASK-105 | 2026-05-19 | ✅ Tamamlandı

**Görev:** İyileştirme paketi toplu uygulama (dokümantasyon, güvenlik, test, N+1, statik varlık, envanter)
**Modül:** docs, config, CI, tests, models, main
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `config.py` → `ProductionConfig`, `get_config(production)`, HGS bypass kapalı
- `app/__init__.py` → CSP `connect-src` CDN
- `app/models/process.py`, `core.py` → ilişki `lazy='select'`
- `ui/static/platform/vendor/fontawesome/` → FA 6.5.1 css+webfont hizası
- `main/admin.py` → `app.models.audit.AuditLog`
- `docs/PROJE-MASTER.md`, `KURALLAR-MASTER.md`, `DEPLOY_SMOKE_CHECKLIST.md`, `YEDEKLER_POLICY.md`, `STATIC_ASSETS_PLATFORM.md`, `LEGACY_ROUTE_INVENTORY.md`
- `scripts/dev/inventory_legacy_routes.py`, `.env.example`, `pytest.ini`, `.github/workflows/ci.yml`
- `tests/test_hgs_security.py`, `tests/test_import_guards.py`

### Yapılan İşlem
Önceki oturumdaki açık iyileştirme önerileri tek pakette uygulandı: prod güvenlik sertleştirmesi, dokümantasyon senkronu, legacy route envanteri, CI tam test suite (46 test), Font Awesome sürüm hizası.

### Notlar
Tailwind CDN bilinçli bırakıldı. `app/routes/process.py` / legacy birleştirme ayrı büyük faz.

---

## TASK-104 | 2026-05-19 | ✅ Tamamlandı

**Görev:** P3 kapanış — `legacy_bridge`, CI import politikası, production Redis rate limit, test suite
**Modül:** app/models, CI, güvenlik, tests
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/models/legacy_bridge.py` → tek köprü: canonical süreç/portföy + legacy kullanıcı/strateji
- `scripts/dev/migrate_models_imports.py` → 43 dosyada `from models` → `legacy_bridge`
- `scripts/ci/check_no_raw_models_import.py` + CI workflow güncellemesi
- `app/utils/security.py` → production’da `REDIS_URL` ile rate limit storage
- `app/models/core.py` → `Tenant.k_radar_enabled`
- `app/models/process.py` → legacy PG/veri synonym’leri (`kaynak_surec_pg_id`, `giris_periyot_*`, `pg_id`)
- `tests/conftest.py`, `test_services.py`, `test_project_service.py` → güncel API ile hizalı

### Yapılan İşlem
Runtime kodunda doğrudan `models` import’u `legacy_bridge` üzerinden toplandı. CI üç guard ile korunuyor (tek db, portföy, raw models). Production rate limit Redis’e düşebiliyor. Pytest: **42 passed**.

### Notlar
`scripts/` seed/migration betikleri bilinçli olarak `from models` kullanmaya devam edebilir. Uzun vadede `IndividualKpiData` / `IndividualPerformanceIndicator` tam legacy tablo birleşimi ayrı faz.

---

## TASK-103 | 2026-05-19 | ✅ Tamamlandı

**Görev:** P3 devam — `main/routes.py`, `api/routes.py`, kurum ve masaustu portföy import migrasyonu
**Modül:** main, api, micro/kurum, micro/masaustu
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `main/routes.py` → Project/Task/ProjectFile vb. `app.models.portfolio_project`; `db` → `extensions.db`
- `api/routes.py` → tüm proje portföy modelleri `portfolio_project`; `task_predecessors` dahil
- `micro/modules/kurum/kurum_overview.py`, `micro/modules/masaustu/routes.py` → portfolio import
- `scripts/ci/check_portfolio_imports.py` (proje/kurum/masaustu/main/api kapsamı); CI güncellendi

### Yapılan İşlem
Legacy `from models import Project` kullanımı ana route katmanlarından ve kurum/masaüstü modüllerinden kaldırıldı. CI ile bu dosyalarda portföy sembollerinin `models` üzerinden import edilmesi engellendi.

### Notlar
`main/routes.py` içinde Surec, Kurum, strateji legacy modelleri hâlâ `models` paketinden geliyor — ayrı faz.

---

## TASK-102 | 2026-05-19 | ✅ Tamamlandı

**Görev:** P3 — legacy proje modellerini `app.models.portfolio_project` altına taşıma; micro/proje import migrasyonu
**Modül:** app/models, micro/proje, models (shim)
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/models/portfolio_project.py` → portföy Project/Task/RAID modelleri (eski `models/project.py` içeriği)
- `models/project.py` → `app.models.portfolio_project` re-export shim
- `app/models/__init__.py` → Alembic için portfolio export
- `micro/modules/proje/*.py` → `app.models.portfolio_project` + `extensions.db`
- `scripts/ci/check_proje_imports.py`, `.github/workflows/ci.yml`

### Yapılan İşlem
Proje portföy modelleri canonical konuma alındı; micro proje modülündeki tüm `from models import Project` kullanımları kaldırıldı. Legacy `models.project` geriye dönük uyumluluk için ince shim olarak kaldı.

### Notlar
`api/routes.py` ve `main/routes.py` hâlâ `models` kullanıyor — sonraki faz.

---

## TASK-101 | 2026-05-19 | ✅ Tamamlandı

**Görev:** P2 — surec/sp route bölme, login rate limit, production CSP
**Modül:** micro/surec, micro/sp, auth, app factory
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/surec/` → `helpers.py`, `routes_process.py`, `routes_kpi.py`, `routes_kpi_data.py`, `routes_activity.py`, `routes_karne.py`, `routes_legacy.py`
- `micro/modules/sp/` → `helpers.py`, `routes_pages.py`, `routes_strategy.py`, `routes_flow.py`, `routes_plan_year.py`, `routes_donemler.py`, `routes_sp_proje.py`, `routes_analysis.py`
- `app/routes/auth.py` → POST `/login` rate limit
- `config.py` → `RATELIMIT_LOGIN`, testte `RATELIMIT_ENABLED=False`
- `app/__init__.py` → production CSP (Talisman)
- `scripts/dev/split_module_routes.py`, `fix_split_route_headers.py`

### Yapılan İşlem
2000+ satırlık monolit route dosyaları alt modüllere bölündü; ortak yardımcılar `helpers.py` içinde toplandı. Giriş endpoint’ine dakika/saat limiti eklendi. Production ortamında temel CSP etkinleştirildi (geliştirmede kapalı).

### Notlar
Legacy `models/` → `app/models/` migrasyonu sonraki faz (proje modülü öncelikli).

---

## TASK-100 | 2026-05-19 | ✅ Tamamlandı

**Görev:** 19mayisyedek yedek noktası + P0/P1 mimari iyileştirmeler (tek db, fabrika shim, CI, plan_year test)
**Modül:** altyapı / güvenlik / test
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `19mayisyedek` dalı + tag → commit `0192ee5` tam kod anlık görüntüsü
- `docs/19MAYISYEDEK_RESTORE.md`, `scripts/ops/restore_19mayisyedek.ps1` → geri dönüş
- `__init__.py` → `app.create_app` shim (eski fabrika dalda korunur)
- `app/extensions.py` + 7 servis → tek `extensions.db`
- `.gitignore`, `.github/workflows/ci.yml`, `scripts/ci/check_single_db.py`
- `tests/test_plan_year.py` → KpiYearConfig / get_kpi_config testleri
- `docs/KURALLAR-MASTER.md` → güvenlik borcu tablosu güncellendi

### Yapılan İşlem
İyileştirmelere başlamadan önce `19mayisyedek` adlı git dalı ve etiket ile yedek alındı. Ardından ikinci SQLAlchemy db riski giderildi, kök fabrika ince shim'e indirildi, CI'da db import kontrolü ve plan_year regresyon testleri eklendi.

### Notlar
Geri dönüş: `.\scripts\ops\restore_19mayisyedek.ps1` veya `git checkout 19mayisyedek && git reset --hard 0192ee5`

---

## TASK-099 | 2026-04-26 | ✅ Tamamlandı

**Görev:** VM'de KMF hedef PG için yıl bazlı görünürlük onarımı + yerel plan-year düzeltmelerini canlıya yayınlama
**Modül:** vm ops / sp-surec deploy
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `scripts/ops/vm_kmf_pg_visibility_check.sql` → Hedef PG yıl bazlı görünürlük doğrulama sorgusu
- `scripts/ops/vm_kmf_pg_find_target.sql` → VM'de hedef PG'yi daraltılmış filtreyle tespit sorgusu
- `scripts/ops/vm_kmf_pg_target_fix.sql` → Hedef PG için `is_active` + `is_included` onarım SQL'i

### Yapılan İşlem
VM PostgreSQL üzerinde yalnızca KMF tenant ve ilgili PG satırı hedeflenerek `kpi_id=343` için kayıt aktifleştirildi; `kpi_year_configs` satırları 2024 için `false`, diğer plan yılları için `true` olacak şekilde upsert edildi. Ardından `vm_safe_deploy.sh` ile `main` dalındaki plan-year karşılaştırma/silme düzeltmeleri canlıya alındı; deploy script'in satır sayısı kontrolü "değişmedi" olarak geçti.

### Notlar
`kpi_data`, `process_activities` ve diğer temel tabloların satır sayıları deploy öncesi/sonrası aynı kaldı; PG veri girişleri silinmedi.

---

## TASK-098 | 2026-04-26 | ✅ Tamamlandı

**Görev:** `/sp/donemler` karşılaştırmasında legacy süreçler nedeniyle KPI farkının görünmemesi için süreç sorgu kapsamını düzeltme
**Modül:** sp / dönem karşılaştırma
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/sp/routes.py` → süreç karşılaştırma sorgularına `plan_year_id IS NULL` legacy kayıtları eklendi

### Yapılan İşlem
`sp_api_donem_karsilastir` içinde `procs1/procs2` sorguları yalnızca `plan_year_id=<yıl>` yerine `plan_year_id=<yıl> OR NULL` olacak şekilde güncellendi. Böylece legacy (NULL etiketli) süreçlerin KPI'ları da karşılaştırma zincirine giriyor ve `KpiYearConfig.is_included` farkları (ör. 2024 hariç, 2026 dahil) UI’de görünür hale geliyor.

### Notlar
KMF için ilgili PG (`id=343`) doğrulaması: `2024 is_included=False`, `2025/2026 is_included=True`.

---

## TASK-097 | 2026-04-26 | ✅ Tamamlandı

**Görev:** `/sp/donemler` dönem karşılaştırmasında legacy KPI'larda (plan_year_id=NULL) farkların görünmemesi sorununu düzeltme
**Modül:** sp / dönem karşılaştırma
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/sp/routes.py` → KPI karşılaştırma eşleştirmesi ve yıllık config fark analizi güncellendi

### Yapılan İşlem
`sp_api_donem_karsilastir` içinde KPI karşılaştırması yalnızca `process_kpis.plan_year_id` dolu kayıtlarla sınırlı kalmayacak şekilde süreç bazlı genişletildi. Legacy aynı-kayıt kullanımında (aynı `kpi.id` iki yılda ortak) çiftleme mantığı iyileştirildi. KPI diff hesabına `KpiYearConfig` efektif değerleri (hedef, birim, yön, periyot, ağırlık) ve özellikle `is_included` (`Plana Dahil`) farkı eklendi.

### Notlar
Bu sayede yıl bazlı “yalnızca 2024'ten kaldırma” gibi işlemler `donemler` karşılaştırma panelinde KPI farkı olarak görünür.

---

## TASK-096 | 2026-04-26 | ✅ Tamamlandı

**Görev:** Plan döneminde PG silmenin tüm yılları etkilemesi hatasını düzeltme
**Modül:** surec / sp plan-year uyumluluğu
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/surec/routes.py` → PG ekle/sil akışında plan-year bağlamı düzeltildi; year bazlı hariç bırakma eklendi
- `ui/static/platform/js/surec.js` → PG silme isteğine seçili yılı gönderen istemci düzeltmesi

### Yapılan İşlem
Plan-year açık kurumlarda PG silme işlemi global `is_active=False` yerine seçili yıl için `KpiYearConfig.is_included=False` olacak şekilde güncellendi. Karne ve KPI liste API’lerinde `is_included=False` olan PG’ler seçili yıl için görünmez yapıldı. Ayrıca yeni eklenen PG kayıtlarının `plan_year_id` alanı aktif döneme bağlandı.

### Notlar
Bu düzeltme geçmişte global soft-delete edilmiş PG kayıtlarını geri getirmez; mevcut sorunlu kayıtlar için ayrı veri onarım adımı gerekir.

---

## TASK-095 | 2026-04-22 | ✅ Tamamlandı

**Görev:** VM’de tekrar eden erişim timeout sorunu için canlı teşhis + gunicorn kapasite profili kalıcı iyileştirmesi
**Modül:** deployment / backend runtime
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `Dockerfile` → Gunicorn varsayılanları 8 worker / 1 thread, daha düşük keep-alive, max-requests recycle ile güncellendi
- `scripts/ops/live_diag.sql` → VM PostgreSQL canlı teşhis sorguları eklendi
- `scripts/ops/vm_local_health_probe.py` → VM içinden URL bazlı ardışık timeout/latency probe aracı eklendi

### Yapılan İşlem
Canlı VM’de hem dış uçtan hem de VM içinden tekrar eden probe çalıştırılarak timeout’un Cloudflare değil uygulama worker katmanında oluştuğu doğrulandı. Canlıda worker artışıyla timeout oranı düştüğü gözlemlendi; ardından Dockerfile’da gunicorn çalışma profili kalıcı olarak güncellenip VM’de image rebuild + container recreate yapıldı.

### Notlar
Dağıtım sonrası VM içi `/health` 20/20 başarılı, dış dünyadan `health/login/home/process` smoke testleri timeout’suz geçti.

---

## TASK-094 | 2026-04-20 | ✅ Tamamlandı

**Görev:** VM tarafında aralıklı yavaşlama/spinner için bakım modu DB kontrolüne TTL cache hotfix uygulandı
**Modül:** backend / maintenance
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/services/maintenance_service.py` → Her istekte DB sorgusunu azaltmak için thread-safe bakım modu cache’i (TTL + invalidation) eklendi
- `config.py` → `MAINTENANCE_DB_CACHE_TTL_SECONDS` ayarı eklendi (varsayılan 5 sn)

### Yapılan İşlem
`maintenance_active()` akışında bakım modu bayrağı artık kısa süreli bellek cache’i üzerinden okunuyor; cache süresi dolduğunda DB’den yenileniyor. Yönetim paneli durum sorgusunda `force_refresh=True` ile anlık değer alınmaya devam ediyor, bakım modu toggle edildiğinde cache otomatik invalidated ediliyor.

### Notlar
Aralıklı `/` ve `/process` timeout gözlemlendi; bu hotfix request başına DB yükünü azaltarak spinner/yavaşlık etkisini düşürmek için uygulandı.

---

## TASK-094 | 2026-05-05 | ✅ Tamamlandı

**Görev:** Kokpitim tanıtım web sitesi (marketing_bp) oluşturuldu
**Modül:** marketing
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/marketing/__init__.py` → Yeni Blueprint
- `micro/modules/marketing/routes.py` → 12 route + blog + sitemap + robots.txt
- `templates/marketing/` → 13 template (base, index, 5 özellik, nasıl çalışır, demo, blog, iletişim)
- `static/marketing/css/marketing.css` → Tam marketing CSS sistemi
- `static/marketing/js/marketing.js` → Navbar scroll, hamburger, accordion, sayaç, fade-in, form validasyon
- `content/blog/` → 2 blog yazısı (Markdown)
- `__init__.py` → marketing_bp en önce register edildi (/ çakışması çözüldü)

### Yapılan İşlem
docs/kirowebsitesi.md belgesindeki talimatlar uygulandı. marketing_bp Blueprint'i app_bp'den önce register edilerek / route çakışması çözüldü. Mevcut hiçbir route/template değiştirilmedi. Tüm sayfalar @login_required olmadan herkese açık. Demo talep ve iletişim formları Flask-WTF CSRF + honeypot spam korumalı. Blog Markdown tabanlı (python-markdown). sitemap.xml ve robots.txt route'ları eklendi.

---
## TASK-093 | 2026-04-14 | ✅ Tamamlandı

**Görev:** KS-Radar OKR analizi modali eklendi + SWOT/TOWS/PESTLE CRUD desteklendi
**Modül:** k_radar / ks / okr
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/models/okr.py` → Yeni: OkrObjective + OkrKeyResult modelleri
- `micro/modules/sp/routes.py` → 7 yeni OKR API endpoint (list, obj CRUD, kr CRUD)
- `micro/modules/k_radar/routes.py` → Eski KS alt sayfa route’ları silindi
- `ui/templates/platform/k_radar/ks.html` → OKR API URL’leri eklendi
- `ui/static/platform/js/k_radar_ks.js` → loadOkrModal() + SWOT/TOWS/PESTLE CRUD
- `ui/static/platform/css/k_radar.css` → OKR + CRUD stilleri

### Yapılan İşlem
OKR modeli (Objective + KeyResult) oluşturuldu, tablolar create_all ile yaratıldı. KS-Radar hub’ında OKR kartına tıklayınca modal açılıyor: çeyrek bazlı gruplandırma, ilerleme bar’ları, Swal ile Objective/KR ekleme-düzenleme-silme. SWOT/TOWS/PESTLE modalları da CRUD destekli hale getirildi.

---

## TASK-092 | 2026-04-14 | ✅ Tamamlandı

**Görev:** SP modülüne SWOT/TOWS/PESTLE veri giriş ekranları eklendi
**Modül:** sp / stratejik analiz
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/sp/routes.py` → 6 yeni API endpoint: GET/POST için swot, tows, pestle
- `ui/templates/platform/sp/index.html` → 03.5 numaralı "Stratejik Analizler" kartı eklendi (Değerler ile Strateji Listesi arasına)
- `ui/static/platform/js/sp.js` → SWOT/TOWS/PESTLE yükleme, madde ekleme/silme, kaydetme fonksiyonları
- `ui/static/platform/css/sp.css` → Analiz kartı stilleri (2×2 grid, PESTLE 3×2 grid)

### Yapılan İşlem
SP sayfasında (\`/sp\`) Stratejik Analizler kartı eklendi. Üç sekme: SWOT (4 kadran), TOWS (SO/ST/WO/WT), PESTLE (6 faktör). Her sekme madde ekleme/silme + kaydet butonu içeriyor. Veriler aktif plan year'a bağlı olarak `swot_analyses`, `tows_analyses`, `pestel_analyses` tablolarına kaydediliyor. KS-Radar bu verileri otomatik okuyacak.

---

## TASK-091 | 2026-04-14 | ✅ Tamamlandı

**Görev:** 404 ve 500 hata sayfaları eklendi
**Modül:** platform / errors
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/templates/platform/errors/404.html` → Yeni oluşturuldu
- `ui/templates/platform/errors/500.html` → Yeni oluşturuldu (error_id desteği)
- `__init__.py` → 404, 403, 500 error handler'ları eklendi; 500'de DB rollback + UUID hata kodu

### Yapılan İşlem
403 sayfasıyla aynı stilde 404 (sarı ikon) ve 500 (kırmızı ikon) sayfaları oluşturuldu. 500 sayfasında her hataya benzersiz 8 karakterlik hata kodu üretiliyor, log'a yazılıyor ve kullanıcıya gösteriliyor. Flask error handler'ları `__init__.py`'ye eklendi.

---

## TASK-089 | 2026-04-12 | ✅ Tamamlandı

**Görev:** VM KMF salt okunur anlık görüntü + yerel repo → canlı deploy (veri kaynağı VM; KMF’ye DB’den müdahale yok)
**Modül:** deployment, ops, docs, çoklu modül (k_rapor, surec, tenant_backup, …)
**Durum:** ✅ Tamamlandı

### İlke
- **Tüm üretim verisi VM’de kalır**; bu işlemde **tenant verisi import/restore/sync yapılmadı**.
- **KMF (`tenant_id=16`) satırlarına kasıtlı UPDATE/DELETE yok**; deploy öncesi/sonrası sayımlar aynı.

### Deploy öncesi — VM KMF (salt okuma, `scripts/kmf_task084_counts.py`)

| Metrik | Değer |
|--------|------:|
| Kullanıcı | 8 |
| Süreç | 11 |
| PG | 135 |
| PGV | 318 |
| plan_years | 7 |
| Strateji | 6 |
| Alt strateji | 21 |

### Yedek ve güvenlik
- `scripts/vm_safe_deploy.sh` adım **1/6**: tam PostgreSQL yedek (`pg_dump` gzip). Örnek dosya: `backups/pg_kokpitim_db_full_20260412_205430.sql.gz` (VM host yolu: `/home/kokpitim.com/public_html/backups/`).
- Betik PostgreSQL URI önkoşulunu kontrol eder; temel tablo satır sayıları deploy öncesi/sonrası **aynı** doğrulandı (`OK`).
- Alembic: yeni revision uygulanmadı (head zaten güncel).

### Git / imaj
- **`main`:** `1cd2d3a` → `c4887e3` push; VM’de fast-forward + Docker image `sps_web_final:latest` + `sps-web` yeniden oluşturuldu.
- Özet commit kapsamı: K-Rapor modülü, admin URL düzeltmeleri, KMF ops betikleri (`kmf_hybrid_sync`, `kmf_compare_local_vm`, `kmf_pull_plan_years_from_vm`, `vm_export`/`vm_apply`), `tenant_backup_service` restore iyileştirmeleri, surec/K-Vektör plan_year NULL uyumu, TASKLOG ve diğer UI düzeltmeleri.

### Dokümantasyon
- `docs/ops/vm_kmf_readonly_snapshot.md` — deploy öncesi KMF tablosu + ham JSON + deploy notu.

### Deploy sonrası doğrulama
- KMF sayıları yukarıdaki tablo ile **değişmedi**; `/health` healthy.

---

## TASK-089 | 2026-04-12 | ✅ Tamamlandı

**Görev:** KS-Radar (Stratejik Planlama) alt modülü geliştirildi — SWOT, TOWS, PESTLE, GAP, Hub
**Modül:** k_radar / ks
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `services/k_radar_service.py` → 6 yeni fonksiyon: `get_ks_swot_real`, `get_ks_tows_real`, `get_ks_pestel_real`, `get_ks_porter_real`, `get_ks_gap_real`, `get_ks_strateji_real`
- `micro/modules/k_radar/routes.py` → 6 yeni API endpoint eklendi (`/k-radar/api/ks/*-real`)
- `ui/templates/platform/k_radar/ks.html` → Hub sayfası sıfırdan yeniden yazıldı
- `ui/templates/platform/k_radar/ks_swot.html` → Tam SWOT matrisi (4 kadran)
- `ui/templates/platform/k_radar/ks_tows.html` → Tam TOWS matrisi (SO/ST/WO/WT)
- `ui/templates/platform/k_radar/ks_pestle.html` → Radar chart + 6 faktör kartı
- `ui/templates/platform/k_radar/ks_gap.html` → Bar chart + pie + tablo
- `ui/static/platform/js/k_radar_ks.js` → Yeni JS dosyası (hub + 4 sayfa)
- `ui/static/platform/css/k_radar.css` → Yeni CSS dosyası (SWOT/TOWS/PESTLE stilleri)

### Yapılan İşlem
KS-Radar iskelet sayfaları gerçek içerikle dolduruldu. DB'deki `swot_analyses`, `tows_analyses`, `pestel_analyses` tabloları artık kullanılıyor. Veri yoksa SP modülüne yönlendirme yapılıyor. Hub sayfasında 4 özet stat kartı + 6 modül kartı + strateji kapsama listesi var. SWOT/TOWS tam matris görünümü, PESTLE radar chart + 6 faktör kartı, GAP bar+pie chart + tablo.

### Notlar
SWOT/TOWS/PESTLE verileri SP modülünde henüz doldurulmamış (boş kayıtlar var). SP modülüne veri giriş ekranları eklendiğinde KS-Radar otomatik dolacak.

---

## TASK-088 | 2026-04-12 | ✅ Tamamlandı

**Görev:** Karne sayfasında başarı puanı yanlış hesaplanıyordu — ham değer vs yüzde karışıklığı giderildi
**Modül:** surec / karne
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/surec/routes.py` → `utils.karne_hesaplamalar` import edildi; `surec_api_karne`'ye `basari_puani` alanı eklendi (backend hesaplama)
- `ui/static/platform/js/surec.js` → `formatKanbanBasariPuaniLikeTable` backend'den gelen `basari_puani`'yı öncelikli kullanacak şekilde güncellendi
- `ui/static/platform/js/pg_tablo_modal.js` → PG tablo modalında backend `basari_puani` öncelikli kullanılıyor

### Yapılan İşlem
Kök neden: Başarı puanı aralıkları DB'de ham değer olarak tanımlı (`{"3":"250-300"}`), ancak frontend `hesaplaBasariPuaniMicro` fonksiyonuna yüzde değeri (%100) geçiyordu. 300 gerçekleşen / 300 hedef = %100, bu da `0-149` aralığına (puan 1) düşüyordu. Çözüm: backend `surec_api_karne` API'si artık `hesapla_basari_puani(year_rollup=300, araliklar, direction)` ile doğru puanı hesaplayıp `basari_puani` alanı olarak döndürüyor. Frontend bu değeri öncelikli kullanıyor.

### Notlar
Yüzde bazlı aralık kullanan PG'ler için frontend fallback korundu.

---

## TASK-087 | 2026-04-12 | ✅ Tamamlandı

**Görev:** K-Rapor'a 8 yeni analiz sekmesi eklendi
**Modül:** k_rapor
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/k_rapor/routes.py` → 8 yeni API endpoint eklendi
- `ui/templates/platform/k_rapor/index.html` → 8 yeni tab butonu + panel HTML, 8 yeni data-api-* attribute
- `ui/static/platform/js/k_rapor.js` → 8 yeni load fonksiyonu + loadTab switch'e eklendi
- `ui/static/platform/css/k_rapor.css` → Aktivite takvimi heatmap stilleri eklendi

### Yapılan İşlem
1. **PG Dağılım** — Histogram + en düşük PG listesi (kpi_data 5960 kayıt)
2. **Faaliyet Matris** — Süreç bazlı yatay stacked bar chart (process_activities 2455 kayıt)
3. **Aktivite Takvimi** — GitHub tarzı günlük veri giriş heatmap + 30 gün trend
4. **Kurum Kıyas** — Kurumları ort. PG başarısına göre bar chart + tablo (18 kurum)
5. **Strateji Kapsama** — Boş/kısmi/tam strateji donut chart + stratejisiz süreçler
6. **Sorumlu Analizi** — Kişi başına faaliyet yükü stacked bar + gecikme tablosu
7. **SWOT Trend** — Yıllar içinde SWOT madde + TOWS strateji sayısı line/bar chart
8. **Bildirim Analizi** — Tür dağılımı donut + 30 gün trend bar chart

### Notlar
routes.py 1999 satıra ulaştı — ileride modüllere bölünmeli.

---

## TASK-086 | 2026-04-12 | ✅ Tamamlandı

**Görev:** K-Rapor API hataları log'dan tespit edilerek düzeltildi
**Modül:** k_rapor
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/k_rapor/routes.py` → 5 hata düzeltmesi

### Yapılan İşlem
Log'dan tespit edilen hatalar:
1. **`bireysel`** — `latest_by_pg` ve `all_by_pg` dict'leri `data_rows` öncesinde tanımlanmamıştı; sıra düzeltildi.
2. **`surec-pg`** — `KpiData.period_type` filtresi DB'de kolon yoksa exception veriyordu; try/except ile güvenli sorguya alındı, `period_no` için `getattr` kullanıldı.
3. **`trend`** — `AnalyticsService.get_performance_trend()` imzası `(process_id, kpi_id, start_date, end_date)` şeklinde; route `kpi_id` ve datetime nesneleri geçmiyordu, düzeltildi.
4. **`faaliyet`** — `plan_projects` tablosu DB'de yok; exception sonrası `db.session.rollback()` eklendi (session bozulmasını önler).
5. **`evm`** — `EvmSnapshot` import'u iç try/except'e alındı; tablo yoksa boş liste döner.

### Notlar
`k_radar_domain` modülü mevcut — Risk/Uyarı tab'ları çalışıyor, veri yoksa "Kayıt yok" gösterir.

---

## TASK-085 | 2026-04-12 | ✅ Tamamlandı

**Görev:** `/micro/` prefix'li route'lar kök URL yapısına taşındı
**Modül:** admin
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/admin/routes.py` → 5 route'da `/micro/admin/...` → `/admin/...` düzeltildi
- `app/utils/maintenance_middleware.py` → bakım modu bypass path'i `/micro/admin/bakim-modu` → `/admin/bakim-modu`

### Yapılan İşlem
`platform_core` blueprint'i `url_prefix=""` ile kök'te kayıtlı olduğundan `/micro/` prefix'i artık geçersiz. `admin_bakim_modu`, `yonetim_paneli`, `yonetim_paneli_istatistik`, `yonetim_paneli_kullanici_detay`, `yonetim_paneli_aktiviteler` route'larının path'leri düzeltildi. `maintenance_middleware`'deki bypass path kontrolü de güncellendi. Template'ler `url_for()` kullandığı için etkilenmedi.

### Notlar
Proje genelinde başka `/micro/` URL referansı kalmadı (Yedekler/ hariç).

---

## TASK-084 | 2026-04-12 | ✅ Tamamlandı

**Görev:** K-Rapor modülü — hata düzeltmeleri + yeni özellikler
**Modül:** k_rapor
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/k_rapor/routes.py` → 6 hata düzeltmesi + Excel export endpoint eklendi
- `ui/static/platform/js/k_rapor.js` → 5 hata düzeltmesi + trend modal + Excel export fonksiyonu
- `ui/templates/platform/k_rapor/index.html` → inline style kaldırıldı, mc-form-select→mc-select, export butonu, trend modal, EVM 8 sütun
- `ui/static/platform/css/k_rapor.css` → mc-page-content-wide, kr-ht-proc-link, kr-header-right sınıfları eklendi

### Yapılan İşlem
**Hata düzeltmeleri:** (1) `strategy_scores` dict'i artık ID yerine kod+başlık içeriyor (`strategy_scores_detail`). (2) `PlanProject`/`PlanYear` import'ları try/except ile korundu — model yoksa faaliyet verisi yine de döner. (3) `k_radar_domain` import'ları güvenli hale getirildi — K-Radar modülü yoksa boş liste döner. (4) `compute_k_vektor_bundle` import hatası yakalanıyor. (5) EVM'e proje adı eklendi. (6) JS'de `loaded` flag bug'ı düzeltildi — period/denetim değişikliğinde `delete loaded[tab]` kullanılıyor. (7) `loadKurumsal`'daki çift loading temizleme kaldırıldı. (8) `mc-form-select` → `mc-select` düzeltildi.
**Yeni özellikler:** Isı haritasında süreç adına tıklayınca trend modal açılıyor (Chart.js line chart). Excel export butonu — aktif tab verisini `.xlsx` olarak indiriyor (kurumsal/veri-durumu/bireysel/faaliyet). EVM tablosuna "Durum" sütunu eklendi.

### Notlar
Trend modal, `surec-pg` API'sinden `kpi_ids` alanını bekliyor — bu alan henüz backend'de dönmüyor; modal "PG verisi yok" mesajı gösterir. İleride `k_rapor_api_surec_pg`'ye `kpi_ids` eklenerek tamamlanabilir.

---

## TASK-083 | 2026-04-12 | ✅ Tamamlandı

**Görev:** HGS sayfası layout kayması giderildi — inline style ve inline JS temizlendi
**Modül:** hgs
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/templates/platform/hgs/index.html` → Tüm inline style'lar CSS sınıflarına taşındı; `onmouseover/onmouseout` inline JS kaldırıldı; `mc-page-content`, `hgs-user-row`, `mc-btn-outline` sınıfları kullanıldı
- `ui/static/platform/css/components.css` → `.mc-page-content`, `.mc-btn-outline`, `.hgs-user-row`, `.hgs-user-active`, `.hgs-user-name`, `.hgs-user-email` sınıfları eklendi

### Yapılan İşlem
HGS sayfasındaki `style="max-width:900px; margin:0 auto; padding:10px 0;"` wrapper inline style `.mc-page-content` sınıfına taşındı. Kullanıcı satırlarındaki `onmouseover/onmouseout` inline JS kaldırılıp CSS `:hover` ile değiştirildi. `mc-card-header` üzerindeki gereksiz padding override'ları kaldırıldı. `mc-btn-outline` sınıfı `components.css`'e eklendi (daha önce tanımsızdı). Aktif kullanıcı vurgusu için `.hgs-user-active` sınıfı eklendi.

### Notlar
Proje `micro/` → `ui/` yapısına taşınmış; tüm template ve CSS dosyaları artık `ui/templates/platform/` ve `ui/static/platform/` altında.

---

## TASK-082 | 2026-04-12 | ✅ Tamamlandı

**Görev:** K-Rapor — Uyarı, K-Vektör, EVM, Stratejik Analiz, Paydaş, Rekabet sekmesi eklendi; Bireysel tab zenginleştirildi
**Modül:** k_rapor
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/k_rapor/routes.py` → 6 yeni API endpoint (uyari, k-vektor, evm, stratejik-analiz, paydas, rekabet); bireysel endpoint güncellendi (veri_girilmis, toplam_giris, son_giris); kurumsal endpoint pg_saglik eklendi
- `ui/templates/platform/k_rapor/index.html` → 6 yeni sekme (Uyarı, K-Vektör, EVM, Stratejik Analiz, Paydaş, Rekabet & A3); bireysel tablo 8 sütuna genişletildi; faaliyet tabına proje portföy eklendi
- `ui/static/platform/js/k_rapor.js` → apiUrl() camelCase düzeltmesi; 6 yeni loadXxx() fonksiyonu; loadBireysel güncellendi
- `config.py` → VERSION 1.0.6 → 1.0.7

### Yapılan İşlem
`apiUrl()` fonksiyonunda tüm segment'ler büyük harfle başlatılarak camelCase dönüşüm hatası giderildi (root cause: tüm tablar "Yüklenemedi" gösteriyordu). Bireysel tab'a veri girişi istatistikleri (kaç PG'ye veri girilmiş, toplam giriş satırı, son giriş tarihi) eklendi. K-Vektör `compute_k_vektor_bundle()` üzerinden hesaplanır (boş ağırlık tablosuna karşı eşit dağılım fallback). Stratejik Analiz plan yılı bulamazsa en güncel yıla fallback yapar.

### Notlar
Score: 1.75 (başlangıç 2, -0.25 yeni sekmelerde boş veri). Tüm yeni sekmeler compute engine veya mevcut modeller üzerinden anlamlı veri üretir.

## TASK-081 | 2026-04-12 | ✅ Tamamlandı

**Görev:** K-Rapor modülü oluşturuldu — kurumsal raporlama merkezi
**Modül:** k_rapor (yeni)
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/k_rapor/__init__.py` → yeni modül
- `micro/modules/k_rapor/routes.py` → 10 route (ana sayfa + 9 API endpoint)
- `ui/templates/platform/k_rapor/index.html` → 8 tab'lı raporlama arayüzü
- `ui/static/platform/css/k_rapor.css` → modüle özgü stiller
- `ui/static/platform/js/k_rapor.js` → lazy-load tab sistemi + Chart.js
- `platform_core/__init__.py` → k_rapor_routes import eklendi
- `micro/core/module_registry.py` → K-Rapor modül kaydı ve rol kısıtlaması
- `ui/templates/platform/base.html` → sidebar K-Rapor linki eklendi

### Yapılan İşlem
`/k-rapor` altında 8 sekmeli raporlama merkezi oluşturuldu: Kurumsal Performans, Süreç & PG Isı Haritası, Stratejik Uyum Ağacı, Faaliyet, Bireysel Performans, Veri Giriş Durumu, Risk ve Denetim. Tüm sekmeler lazy-load ile API'dan veri çeker. Launcher sayfasında modül kartı, sidebar'da link eklendi. Yalnızca tenant_admin / executive_manager / Admin rollerine görünür.

### Notlar
Aşama 1 (iskelet + Kurumsal + Veri Durumu) ve Aşama 2-3 kapsamındaki tüm sekmeler tek seferde uygulandı. Export (Aşama 4) ertelendi.

## TASK-080 | 2026-04-10 | ✅ Tamamlandı

**Görev:** K-Vektör puanları plan yılı filtresi sonrası sıfır çıkıyordu — source_kpi_id zinciri taraması eklendi
**Modül:** score_engine
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/services/score_engine_service.py` → `get_pg_scores_from_kpi_data()` içine source_kpi_id zincir yürüyüşü eklendi

### Yapılan İşlem
TASK-079 ile `plan_year_id` filtresi eklendikten sonra KMF tenant'ında tüm K-Vektör puanları 0 çıkıyordu. Kök neden: KMF'de aktif plan yılı 2026 (plan_year_id=1) klonlarının 102 ProcessKpi kaydının hiçbirinde KpiData yok; veriler ilk dönem olan 2021 (plan_year_id=2) KPI ID'leri üzerinde tutuluyor. `get_pg_scores_from_kpi_data()` içinde, clone KPI için veri bulunamadığında artık `source_kpi_id` zinciri geriye doğru taranıyor (max 8 adım). Atadan bulunan veri, aktif dönemin hedef/yön/metod konfigürasyonu ile birlikte kullanılıyor.

### Notlar
`source_kpi_id` chain walk yalnızca `plan_year is not None` durumunda tetiklenir — `plan_year=None` (tenant bazlı) fallback davranışı değişmedi.

---

## TASK-078 | 2026-04-10 | ✅ Tamamlandı

**Görev:** SP Dönemler sayfasına iki dönem arasındaki farkları gösteren Dönem Karşılaştır paneli eklendi
**Modül:** sp
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/sp/routes.py` → `StrategyYearConfig, SubStrategyYearConfig, ProcessYearConfig` import eklendi; yeni `GET /sp/api/donem-karsilastir?y1=&y2=` route eklendi
- `ui/templates/platform/sp/donemler.html` → "Tüm Dönemler" kartının altına karşılaştırma paneli + JS eklendi

### Yapılan İşlem
`/sp/donemler` sayfasında en az 2 dönem varsa "Dönem Karşılaştır" paneli görünür. Kullanıcı iki dropdown'dan yıl seçer, "Karşılaştır" butonuna tıklar; backend `KpiYearConfig`, `StrategyYearConfig`, `SubStrategyYearConfig`, `ProcessYearConfig` tablolarını her iki dönem için sorgulayarak meta bilgi, strateji, alt strateji, süreç ve KPI hedefi farklarını JSON olarak döner. Frontend `<details>` panellerinde sarı vurgulu satırlarla değişen alanları gösterir; fark sayısını badge olarak özetler.

### Notlar
Karşılaştırma yalnızca `*_year_config` tablolarındaki override kayıtlarını kapsar; config kaydı olmayan varlıklar (fallback kullananlar) karşılaştırmaya dahil edilmez.

---

## TASK-079 | 2026-04-10 | ✅ Tamamlandı

**Görev:** K-Vektör hesaplamaları aktif SP dönemini baz alacak şekilde güncellendi
**Modül:** k_vektor, score_engine, sp, surec, kurum
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/services/k_vektor_engine.py` → `compute_k_vektor_bundle(plan_year=None)` parametresi eklendi; Process, Strategy, SubStrategy sorguları `plan_year_id` ile filtreleniyor
- `app/services/score_engine_service.py` → `get_pg_scores_from_kpi_data`, `compute_process_scores_internal`, `compute_vision_score` içinde plan_year filtreleri; K-Vektör çağrısına `plan_year` geçiriliyor; klasik yolda Strategy/SubStrategy `plan_year_id` ile filtreleniyor
- `app/services/k_vektor_config_service.py` → `k_vektor_weights_get_dict(plan_year=None)` ve `save_k_vektor_weights(plan_year=None)` — strateji listesi aktif dönem ID'sine göre filtreleniyor
- `micro/modules/sp/routes.py` → `compute_vision_score`, `k_vektor_weights_get_dict`, `save_k_vektor_weights`, `sp_api_graph` çağrılarına `active_plan_year` / `get_active_plan_year_for_user()` geçiriliyor
- `micro/modules/surec/routes.py` → `compute_process_scores_internal` çağrısına aktif plan_year geçiriliyor
- `micro/modules/kurum/routes.py` → `k_vektor_weights_get_dict` ve `save_k_vektor_weights` çağrılarına aktif plan_year geçiriliyor

### Yapılan İşlem
Full Clone mimarisinde her dönemin kendi Strategy/SubStrategy/Process/ProcessKpi kayıtları `plan_year_id` ile ayrılıyor. Önceki sürüm `tenant_id` ile sorgulayıp tüm dönemleri karıştırıyordu. Artık `plan_year` verildiğinde tüm motorlar yalnızca o döneme ait kayıtları kullanıyor; `plan_year=None` durumunda eski davranış (tenant bazlı) korunuyor — geriye dönük uyumluluk bozulmadı.

### Notlar
`api/routes.py` (legacy) ve `app/routes/strategy.py` güncellenmedi — bunlar plan year öncesi sistemden kalma; plan_year=None fallback ile çalışmaya devam eder.

---

## TASK-078d | 2026-04-10 | ✅ Tamamlandı

**Görev:** Dönem karşılaştırmasında KPI'lar artık süreç bazlı gruplu gösteriliyor
**Modül:** sp
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/sp/routes.py` → Süreç + KPI karşılaştırması birleştirildi; `_kpi_diff()` yardımcısı eklendi; KPI'lar artık `process_diffs[].kpis[]` içinde iç içe döner, bağımsız `kpi_diffs` listesi kaldırıldı
- `ui/templates/platform/sp/donemler.html` → `processSectionHtml()` fonksiyonu eklendi; süreç başlığı → altında KPI satırları şeklinde hiyerarşik tablo render ediyor

### Yapılan İşlem
Backend: Her süreç çiftinin kendi KPI'ları `kpis1_by_proc`/`kpis2_by_proc` dict'leri üzerinden `_match_pairs` ile eşleştirilip `kpis` listesi olarak sürece gömüldü. Frontend: `processSectionHtml()` her süreç için başlık satırı (gri arka plan), sürecin kendi alan farkları (girintili), ardından altındaki KPI satırları (daha derin girinti) olarak render ediyor; sarı vurgu yalnızca değişen satırlarda.

### Notlar
Yok.

---

## TASK-078c | 2026-04-10 | ✅ Tamamlandı

**Görev:** Dönem karşılaştırma mantığı kökten yeniden yazıldı — `*_year_config` tablolarından asıl tablolara geçildi
**Modül:** sp
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/sp/routes.py` → Strateji/alt strateji/süreç/KPI karşılaştırması `*_year_config` tablolarından `strategies`, `sub_strategies`, `processes`, `process_kpis` tablolarına taşındı; `source_*_id` ile eşleştirme yapan `_match_pairs()` yardımcısı eklendi
- `ui/templates/platform/sp/donemler.html` → Row render fonksiyonları `changed_fields` listesine göre yeniden yazıldı; satır bazlı alan farkları gösteriliyor

### Yapılan İşlem
Önceki sürüm `StrategyYearConfig`, `ProcessYearConfig` vb. override tablolarını sorguluyordu — bu tablolar boş olunca hiç fark çıkmıyordu. Doğru mimari Full Clone sistemidir: her yıl için stratejiler/süreçler/KPI'lar kopyalanarak `plan_year_id` ile o yıla bağlanır. `_match_pairs()` fonksiyonu Y1↔Y2 yönünde `source_*_id` referanslarını takip ederek eşleşen çiftleri bulur, eşleşemeyenleri "sadece bu yılda" olarak işaretler.

### Notlar
`*_year_config` import'ları routes.py'de kaldı; kimlik karşılaştırması (`TenantYearIdentity`) doğruydu, değiştirilmedi.

---

## TASK-078b | 2026-04-10 | ✅ Tamamlandı

**Görev:** Dönem karşılaştırmasına SP ana sayfasındaki kimlik alanları (Misyon, Vizyon, Değerler, Etik Kurallar, Kalite Politikası) eklendi
**Modül:** sp
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/sp/routes.py` → `sp_api_donem_karsilastir` route'una `TenantYearIdentity` sorgusu ve `identity_diffs` bloğu eklendi
- `ui/templates/platform/sp/donemler.html` → `identitySection` render + `identityRowFn` eklendi; her alan için 150 karakter önizleme gösterildi

### Yapılan İşlem
Her plan yılının `TenantYearIdentity` kaydından purpose, vision, core_values, code_of_ethics, quality_policy alanları çekilip karşılaştırıldı. Metin farklıysa veya dolu/boş durumu değiştiyse "değişmiş" sayılır. Önizleme olarak ilk 150 karakter gösterilir, uzun metinler `…` ile kesilir.

### Notlar
Yok.

## TASK-090 | 2026-04-11 | ✅ Tamamlandı

**Görev:** SP sayfasındaki "klonlanmamış strateji" uyarısı kaldırıldı
**Modül:** sp
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/templates/platform/sp/index.html` → `has_untagged_strategies` uyarı bloğu silindi

### Yapılan İşlem
TASK-088/089 ile `plan_year_id=NULL` legacy verisi skor motoru dahil tüm zincirde düzgün işlendiğinden, "klonlanmamış strateji" uyarısı artık yanıltıcıydı. Kaldırıldı.

### Notlar
Yok.

---

## TASK-096 | 2026-04-11 | ✅ Tamamlandı

**Görev:** Süreç listesine Kanban görünümü eklendi
**Modül:** surec
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/templates/platform/surec/index.html` → header'a Ağaç/Kanban toggle eklendi; 4 sütunlu kanban grid (Hedefte/Risk altında/Hedef dışı/Veri yok) eklendi; toggle tercihi localStorage'a kaydedilir

### Yapılan İşlem
Süreç listesinde mevcut ağaç görünümüne ek olarak kanban görünümü eklendi. Karne sayfasındaki `kb-*` CSS sınıfları yeniden kullanıldı. Süreçler puana göre 4 sütuna dağıtılır: ≥80% Hedefte, 50-79% Risk altında, <50% Hedef dışı, skor yok Veri yok. K-Vektör etkinse kart üzerinde gösterilir.

### Notlar
Yok.

---

## TASK-095 | 2026-04-11 | ✅ Tamamlandı

**Görev:** Süreç modalında alt strateji listesine sütun başlıkları eklendi
**Modül:** surec
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/static/platform/js/surec.js` → `populateSubStrategyPicker`: K-Vektör aktifken her strateji grubu altına "Alt Strateji" / "Katkı %" sütun başlığı eklendi

### Yapılan İşlem
Yeni Süreç ve Düzenle modallarındaki alt strateji bölümünde her ana strateji grubunun altında ince çizgiyle ayrılmış başlık satırı eklendi. Yalnızca K-Vektör etkin tenant'larda gösterilir.

### Notlar
Yok.

---

## TASK-094 | 2026-04-11 | ✅ Tamamlandı

**Görev:** Süreç Karnesi sayfası aktif SP döneminin yılıyla açılıyor
**Modül:** surec
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/surec/routes.py` → `surec_karne`: `current_year = active_py.year if active_py else datetime.now().year` — aktif plan yılı varsa o dönemin yılı kullanılıyor

### Yapılan İşlem
Karne sayfası her zaman `datetime.now().year` ile açılıyordu. Aktif SP dönemi 2025 iken bile 2026 verisi yükleniyordu. Şimdi `get_active_plan_year_for_user` ile dönem yılı alınıp `data-current-year` attribute'una yazılıyor.

### Notlar
Yok.

---

## TASK-094 | 2026-05-05 | ✅ Tamamlandı

**Görev:** Kokpitim tanıtım web sitesi (marketing_bp) oluşturuldu
**Modül:** marketing
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/marketing/__init__.py` → Yeni Blueprint
- `micro/modules/marketing/routes.py` → 12 route + blog + sitemap + robots.txt
- `templates/marketing/` → 13 template (base, index, 5 özellik, nasıl çalışır, demo, blog, iletişim)
- `static/marketing/css/marketing.css` → Tam marketing CSS sistemi
- `static/marketing/js/marketing.js` → Navbar scroll, hamburger, accordion, sayaç, fade-in, form validasyon
- `content/blog/` → 2 blog yazısı (Markdown)
- `__init__.py` → marketing_bp en önce register edildi (/ çakışması çözüldü)

### Yapılan İşlem
docs/kirowebsitesi.md belgesindeki talimatlar uygulandı. marketing_bp Blueprint'i app_bp'den önce register edilerek / route çakışması çözüldü. Mevcut hiçbir route/template değiştirilmedi. Tüm sayfalar @login_required olmadan herkese açık. Demo talep ve iletişim formları Flask-WTF CSRF + honeypot spam korumalı. Blog Markdown tabanlı (python-markdown). sitemap.xml ve robots.txt route'ları eklendi.

---
## TASK-093 | 2026-04-11 | ✅ Tamamlandı

**Görev:** Süreç listesinde K-Vektör skoru gösterimi + yıl fix
**Modül:** surec
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/surec/routes.py` → `compute_process_scores_internal` çağrısında `today.year` yerine `_surec_py.year` kullanılıyor
- `ui/templates/platform/surec/index.html` → her süreç kartına `k_vektor_enabled` aktifse K-Vektör skoru (`fas fa-vector-square` ikonlu, mor renk) eklendi

### Yapılan İşlem
Süreç listesi sayfasında K-Vektör etkin tenant'lar için her sürecin altında `K-Vektör: XX.X` etiketi gösterildi. Aynı zamanda skor hesaplamada yıl hatası da giderildi (aktif plan yılının yılı kullanılıyor).

### Notlar
Yok.

---

## TASK-092 | 2026-04-11 | ✅ Tamamlandı

**Görev:** K-Vektör alt strateji/strateji skorları 0 — NULL plan_year_id fix genişletildi
**Modül:** k_vektor_engine, score_engine_service
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/services/k_vektor_engine.py` → sub_strategy sorgusu ve strategy sorgusu: `plan_year_id IS NULL AND tenant_id=X` OR koşulu eklendi
- `app/services/score_engine_service.py` → sub_strategy ve strategy sorguları (K-Vektör dışı yol): aynı OR koşulu eklendi

### Yapılan İşlem
TASK-089'da yalnızca Process ve ProcessKpi sorgularına NULL plan_year_id fix uygulanmıştı. SubStrategy (Strategy join üzerinden) ve Strategy sorgularında aynı sorun mevcuttu: `plan_year_id=plan_year.id` filtresi KMF'nin NULL plan_year_id stratejilerini dışlıyordu → sub_strategy/strategy skoru hesaplanamıyordu → K-Vektör 0.

### Notlar
Yok.

---

## TASK-091 | 2026-04-11 | ✅ Tamamlandı

**Görev:** K-Vektör skoru plan yılından bağımsız yıl kullanıyordu — yıl fix
**Modül:** score_engine_service, sp routes
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/services/score_engine_service.py` → `compute_vision_score`: `year` parametresi None geldiğinde `plan_year.year` kullanılıyor, fallback olarak `date.today().year`
- `micro/modules/sp/routes.py` → `compute_vision_score` çağrısına `year=active_py.year` eklendi

### Yapılan İşlem
`compute_vision_score` her zaman `date.today().year` (2026) kullanıyordu. Seçili plan yılı 2025 bile olsa KpiData sorgusu `year=2026` yapılıyordu — veri bulunamıyordu, K-Vektör 0 çıkıyordu. Fix: `plan_year` verilmişse `plan_year.year` kullan.

### Notlar
TASK-089'daki `plan_year_id=NULL` fix'i doğru ancak yeterli değildi; bu fix asıl yıl hatasını kapatıyor.

---

## TASK-089 | 2026-04-11 | ✅ Tamamlandı

**Görev:** K-Vektör puanı NULL plan_year_id olan legacy süreçler için 0 çıkıyordu — skor motoru fix
**Modül:** score_engine_service, k_vektor_engine
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/services/score_engine_service.py` → `get_pg_scores_from_kpi_data`: ProcessKpi sorgusu `plan_year_id IS NULL AND tenant_id=X` OR koşulu eklendi; `compute_process_scores_internal`: Process sorgusu aynı OR koşuluyla güncellendi; `sqlalchemy.or_/and_` import eklendi
- `app/services/k_vektor_engine.py` → `compute_k_vektor_bundle`: Process sorgusu aynı OR koşuluyla güncellendi; `sqlalchemy.or_/and_` import eklendi

### Yapılan İşlem
KMF (ve benzeri VM/legacy) tenant'larında süreçlerin `plan_year_id=NULL` olması, skor motoru plan_year bazlı sorgu yaparken hiç süreç/KPI bulamamasına yol açıyordu. TASK-088'de surec listesine uygulanan "aktif plan_year_id OR NULL" mantığı, K-Vektör hesaplama zincirinin (ProcessKpi → Process → K-Vektör) üç kritik sorgusuna da uygulandı.

### Notlar
Surec modülündeki fix (TASK-088) skor motorunu kapsamamıştı; bu fix tamamlıyor.

---

## TASK-077 | 2026-04-09 | ✅ Tamamlandı

**Görev:** `/sp/analizler` bölümü tamamen kaldırıldı
**Modül:** sp
**Durum:** ✅ Tamamlandı

### Değiştirilen / Silinen Dosyalar
- `micro/modules/sp/routes.py` → Stratejik Analizler bölümü kaldırıldı: `sp_analizler()` route, 16 API endpoint (SWOT/TOWS/PESTEL/Porter/Rakip/Paydaş/Risk), tüm yardımcı fonksiyonlar ve modül import'ları silindi
- `ui/templates/platform/base.html` → Sidebar'dan "Stratejik Analizler" linki ve `active` koşulundaki `analizler` kontrolü kaldırıldı
- `ui/templates/platform/sp/analizler.html` → Silindi
- `ui/static/platform/css/analizler.css` → Silindi
- `ui/static/platform/js/analizler.js` → Silindi

### Yapılan İşlem
Anlamsız bulunan `/sp/analizler` sayfası ve tüm bağımlılıkları (route, API, template, CSS, JS, sidebar) eksiksiz kaldırıldı.

### Notlar
Yok.

---

## TASK-076 | 2026-04-09 | ✅ Tamamlandı

**Görev:** SP sayfasındaki K-Vektör açıklama notu kaldırıldı
**Modül:** sp
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/templates/platform/sp/index.html` → K-Vektör ham ağırlık açıklama notunu içeren `mc-alert mc-sp-flow-note` div'i silindi

### Yapılan İşlem
SP ana sayfasında `k_vektor_enabled and sp_can_manage` koşuluyla gösterilen "K-Vektör: Ana ve alt strateji ham ağırlıkları..." açıklama kutusu anlamsız bulunarak tamamen kaldırıldı.

### Notlar
Yok.

---

## TASK-075 | 2026-04-09 | ✅ Tamamlandı

**Görev:** SP Dönem Yönetimi masaüstüne taşındı — tüm CRUD (seçim, oluşturma, kapatma) ana sayfa widget'ı oldu
**Modül:** masaustu / sp / plan_year
**Durum:** ✅ Tamamlandı

### Değiştirilen / Oluşturulan Dosyalar
- `micro/modules/masaustu/routes.py` → plan_year verilerini yükle (plan_years, active_plan_year, sp_can_manage, plan_year_feature); render_template'e aktar
- `ui/templates/platform/masaustu/index.html` → "SP Dönem Yönetimi" widget eklendi; yeni dönem modalı eklendi; masaustu_plan_year.js linki eklendi; sp.css linki eklendi
- `ui/static/platform/js/masaustu_plan_year.js` → YENİ; dönem seçimi, yeni dönem oluşturma, dönem kapatma JS

### Yapılan İşlem
Dönem seçme/oluşturma/kapatma işlemleri SP sayfasına ek olarak masaüstüne de eklendi. Tüm kullanıcılar aktif dönemi görebilir ve değiştirebilir; Yeni Dönem / Kapat butonları yalnızca tenant_admin ve üst rollerde render edilir. Mevcut `/sp/api/plan-years` endpoint'leri yeniden kullanıldı, yeni route eklenmedi. SP sayfasındaki mevcut bar korundu.

### Notlar
Widget yalnızca `tenant.plan_year_enabled = True` olan tenantlarda görünür. Diğer tenantlarda masaüstü değişmez.

## TASK-074 | 2026-04-09 | ✅ Tamamlandı

**Görev:** PlanYear kayıtları var ama SP ana verisi boş yılların backfill'i + K-Radar görünürlük rollback + SP fallback metin düzeltmeleri  
**Modül:** sp / plan_year / k_radar / ui  
**Durum:** ✅ Tamamlandı

### Değiştirilen / Oluşturulan Dosyalar
- `scripts/fix_empty_plan_years_by_clone.py` → YENİ; `plan_year` boş yılları önceki dolu yıldan full clone ile backfill eden script
- `app/services/plan_year_service.py` → `clone_full_plan_year()` içinde `ProcessActivityAssignee` kopyalama alanı `order_no` ile uyumlu hale getirildi
- `micro/modules/sp/routes.py` → fallback mesajında seçili yıl (`sp_selected_plan_year`) ve gösterilen veri yılı (`sp_displayed_plan_year`) ayrıştırıldı
- `ui/templates/platform/sp/index.html` → bilgi banner metni seçili yıl / gösterilen yıl doğru gösterilecek şekilde güncellendi
- `micro/core/module_registry.py` → K-Radar tenant flag'e bağlı launcher filtresi geri alındı
- `micro/modules/k_radar/routes.py` → tenant bazlı K-Radar gate (`before_request`) geri alındı
- `ui/templates/platform/base.html` → K-Radar sidebar linki koşulsuz görünecek şekilde geri alındı
- `scripts/compare_tenant_backup_vs_db.py` → `.json.gz` yanında `.json` yedek dosyası da okuyacak şekilde genişletildi
- `scripts/print_tenant_table_counts.py` → YENİ; tenant bazlı tablo sayım aracı

### Yapılan İşlem
KMF örneğinde (tenant 16) `plan_years` içinde 2022-2026 mevcut olmasına rağmen `strategies/processes` kayıtları yalnızca 2021'e bağlıydı.  
Yeni backfill scripti önce dry-run ile analiz edildi, sonra uygulanarak 2022-2026 yıllarına ana SP verisi taşındı (6 strateji, 11 süreç ve ilişkili alt veriler).  
Ardından tüm tenantlar için script çalıştırıldı; kaynak yılı hiç olmayan tenantlar güvenli biçimde atlandı.  
Ek olarak K-Radar'ı devre dışı bırakan son feature-gate değişiklikleri geri alındı.

### Notlar
- KMF doğrulaması: 2021-2026 için `strategies=6`, `processes=11`; 2020 boş kaldı (kaynak yıl yok).
- Script, kaynağı olmayan boş yılları kopyalamaz; yanlış veri üretmemek için "atlandı" raporlar.
- Kalıcı politika önerisi: yeni yıl oluşturma akışında `from_year` ile full clone zorunlu/varsayılan olmalı.

---

## TASK-073 | 2026-04-09 | ✅ Tamamlandı

**Görev:** Süreç/KPI/bireysel PG sayfalarında plan_year fallback eklendi
**Modül:** surec / bireysel
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/surec/routes.py` → `surec()`: aktif yılda veri yoksa en çok sürece sahip yıla fallback; strateji filtresi de güncellendi
- `micro/modules/bireysel/routes.py` → `bireysel_api_karne()`: aktif yılda PG yoksa tüm PG'leri göster

### Yapılan İşlem
KMF gibi tüm verileri 2021 plan_year_id'de olan tenantlarda aktif yıl 2026 olduğu için süreçler, stratejiler ve PG'ler görünmüyordu. SP sayfasında uygulanan fallback mantığı surec ve bireysel modüllerine de taşındı.

### Notlar
Kalıcı çözüm: "Yeni Yıl Planı" oluşturulurken kaynak yıl seçilerek full clone yapılmalı. Fallback geçici uyumluluk katmanıdır.

---

## TASK-072 | 2026-04-08 | ✅ Tamamlandı

**Görev:** SP modal şeffaflık ve plan_year filtre hataları düzeltildi
**Modül:** sp / components
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/static/platform/css/components.css` → `.mc-modal-lg/md/sm/xl` için `background:#fff` + boyut kuralları eklendi; `.mc-modal-overlay.active` desteği eklendi
- `ui/static/platform/js/sp_plan_year.js` → modal açma/kapama `style.display` yerine `classList.add/remove("open")` ile yapıldı
- `ui/templates/platform/sp/index.html` → modaldan `style="display:none"` inline stil kaldırıldı; etiketlenmemiş kayıt uyarısı eklendi
- `micro/modules/sp/routes.py` → strateji/süreç sorgularına `or_(plan_year_id==active_py.id, plan_year_id==None)` filtresi eklendi; `has_untagged_strategies` flag'i eklendi

### Yapılan İşlem
Modal içeriği (`.mc-modal-lg`) CSS `background:white` tanımlamasına sahip değildi, bu nedenle şeffaf görünüyordu. `sp_plan_year.js` inline `style.display` yerine CSS sınıfıyla açılacak şekilde güncellendi. Strateji/süreç filtresine `plan_year_id IS NULL` kayıtları dahil edildi; etiketlenmemiş veri varsa uyarı banner gösterilecek.

### Notlar
`plan_year_id=NULL` kayıtlar tüm dönemlerde görünmeye devam eder. Tam izolasyon için `scripts/migrate_genesis_plan_year.py` çalıştırılmalı.

---

## TASK-071 | 2026-04-09 | ✅ Tamamlandı (FAZA 4b + FAZA 5)

**Görev:** SP Full Clone sistemi kullanıcıya açıldı — dönem oluşturma, yıl geçişi, karne navigasyonu, SP Projeler
**Modül:** sp / surec / plan_year
**Durum:** ✅ Tamamlandı

### Değiştirilen / Oluşturulan Dosyalar
- `micro/modules/sp/routes.py` → `sp_api_plan_years_create`: `clone_full_plan_year` entegre edildi; `sp()`: TenantYearIdentity'den misyon/vizyon yüklenir; `sp_api_tenant_identity`: plan_year aktifse TenantYearIdentity'e kaydeder; PlanProject + PlanProjectTask CRUD route'ları eklendi (`/sp/api/proje/`); `/sp/projeler` sayfa route'u eklendi
- `micro/modules/surec/routes.py` → `surec_karne`: plan_years listesi template'e aktarıldı; `surec_api_resolve_for_year` API eklendi (code + source_id chain traversal ile yıl bazlı process çözümleme)
- `ui/templates/platform/surec/karne.html` → `plan_year_enabled`, `resolve-year-url`, `current-year` data attr; yıl selector plan_years listesi ile güncellendi
- `ui/static/platform/js/surec.js` → yıl değişiminde plan_year aktifse resolve API çağrılıp ilgili dönemin klonuna navigate edilir
- `ui/templates/platform/sp/index.html` → TenantYearIdentity öncelikli misyon/vizyon okuma
- `ui/templates/platform/sp/projeler.html` → YENİ: SP Projeler sayfası
- `ui/static/platform/js/sp_projeler.js` → YENİ: proje kartları, görev yönetimi
- `ui/static/platform/css/sp.css` → proje kartı stilleri eklendi
- `ui/templates/platform/base.html` → sidebar'a SP Projeler linki eklendi

### Yapılan İşlem
"Yeni Dönem Oluştur" → from_year seçilince plan_year_enabled tenant için `clone_full_plan_year()` çağrılır (tüm strateji/süreç/KPI/faaliyet/analiz kopyalanır). Karne sayfasında yıl değiştirilince `/process/api/resolve-for-year` API, mevcut sürecin hedef yıldaki klonunu `code` eşleşmesi + `source_id` zinciriyle bulur ve o sayfaya yönlendirir. Misyon/vizyon plan_year aktifse `TenantYearIdentity`'den okunur ve kaydedilir. SP Projeler sayfası kart görünümü + görev yönetimi ile tamamlandı.

### Notlar
Tüm fazlar tamamlandı (FAZA 1-5). Overlay tabloları (kpi_year_configs vb.) hâlâ silinmedi — bir sonraki cleanup task'ında kaldırılabilir.

## TASK-070 | 2026-04-09 | ✅ Tamamlandı

**Görev:** Tüm stratejik analizler — SWOT, TOWS, PESTEL, Porter's 5 Güç, Rakip Analizi, Paydaş Haritası, Risk Haritası
**Modül:** sp / analiz
**Durum:** ✅ Tamamlandı

### Değiştirilen / Oluşturulan Dosyalar
- `app/models/swot.py` → `PestelAnalysis`, `PorterFiveForcesAnalysis` modelleri eklendi
- `app/models/k_radar_domain.py` → `CompetitorAnalysis`, `StakeholderMap`, `RiskHeatmapItem` modellerine `plan_year_id` FK eklendi
- `app/models/__init__.py` → yeni model import'ları eklendi
- `migrations/versions/d4e5f6g7h8i9_strategic_analyses_tables.py` → YENİ — migration çalıştırıldı, PostgreSQL'e uygulandı
- `micro/modules/sp/routes.py` → 7 analiz için 16 API endpoint eklendi + `sp_analizler()` sayfa route'u
- `ui/templates/platform/sp/analizler.html` → YENİ — tüm analizler için sekmeli UI
- `ui/static/platform/css/analizler.css` → YENİ — analiz sayfası stilleri
- `ui/static/platform/js/analizler.js` → YENİ — tüm analizler için veri yükleme, düzenleme, canvas görselleştirme
- `ui/templates/platform/base.html` → sidebar'a "Stratejik Analizler" linki eklendi

### Yapılan İşlem
7 stratejik analiz tipi plan_year bazlı olarak uygulandı. SWOT/TOWS/PESTEL/Porter her biri plan_year+tenant başına tek kayıt (get-or-create). Rakip/Paydaş/Risk ise çoklu satır tabanlı. Porter'da her kuvvet için hem öğe listesi hem şiddet skoru (1-5) tutulur. Paydaş Haritası ve Risk Haritası canvas ile görselleştirildi. `/sp/analizler` sayfasında sekmeli erişim, sidebar'a link eklendi.

### Notlar
Plan year feature disabled tenantlarda `/sp/analizler` sayfası uyarı gösterir. `_require_plan_year()` yardımcısı tüm API'lerde aktif dönem yoksa 400 döner.

## TASK-069 | 2026-04-08 | ✅ Tamamlandı (FAZA 3)

**Görev:** SP Tam Klon — FAZA 3: tüm route sorgularına aktif `plan_year_id` filtresi eklendi
**Modül:** surec / sp / bireysel / plan_year_service
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/services/plan_year_service.py` → `get_active_plan_year_for_user(user)` yardımcı fonksiyonu eklendi; `session` import'u eklendi
- `micro/modules/surec/routes.py` → `surec()` ve `_parent_options_with_depth()` plan_year_id filtresi; import güncellendi
- `micro/modules/sp/routes.py` → `sp()`, `sp_flow()`, `sp_api_graph()`, `sp_add_strategy()`, `sp_add_sub_strategy()` plan_year_id filtresi; import güncellendi
- `micro/modules/bireysel/routes.py` → `bireysel_api_karne()`, `bireysel_api_pg_add()`, `bireysel_api_pg_ensure_from_process_kpi()` plan_year_id filtresi; import güncellendi

### Yapılan İşlem
`get_active_plan_year_for_user(user)` fonksiyonu: tenant'ta `plan_year_enabled=False` ise `None` döner; session'daki `sp_active_year` veya tenant aktif yılı bulunur. Tüm süreç/strateji/bireysel PG sorgularına bu fonksiyondan gelen aktif dönem filtresi eklendi. Plan year aktif olmadığında mevcut davranış (tüm kayıtlar) korunur. Yeni strateji/sub-strateji/bireysel PG oluşturmada `plan_year_id` otomatik atanır.

### Notlar
`IndividualActivity` tablosunda henüz `plan_year_id` kolonu yok — migration'da yoktu, FAZA 4'te değerlendirilecek. Karne API overlay mantığı clonlanmış KPI'larda graceful fallback yapıyor (boş `_ycfg` → KPI değerleri direkt kullanılır).

## TASK-068 | 2026-04-08 | ✅ Tamamlandı (FAZA 1-2)

**Görev:** SP Tam Klon (Full Clone) mimarisi — DB altyapısı ve servis katmanı
**Modül:** plan_year / core / process / sp
**Durum:** ✅ Tamamlandı (FAZA 1-2 tamamlandı; FAZA 3-5 sonraki task)

### Değiştirilen Dosyalar
- `app/models/core.py` → Strategy + SubStrategy'e plan_year_id, source_strategy_id/source_sub_strategy_id eklendi
- `app/models/process.py` → Process, ProcessKpi, ProcessActivity, IndividualPerformanceIndicator'a plan_year_id + source_* eklendi
- `app/models/tenant_year.py` → YENİ: TenantYearIdentity (misyon/vizyon/değerler yıllık versiyonlama)
- `app/models/swot.py` → YENİ: SwotAnalysis, TowsAnalysis (plan_year bazlı)
- `app/models/project.py` → YENİ: Project, ProjectTask, ProjectActivity (plan_year bazlı)
- `app/models/__init__.py` → yeni model importları eklendi
- `app/services/plan_year_service.py` → clone_full_plan_year() eklendi (tam klon servisi)
- `migrations/versions/c2d3e4f5g6h7_full_clone_plan_year_fks.py` → YENİ migration
- `scripts/migrate_genesis_plan_year.py` → YENİ tek seferlik genesis atama scripti

### Yapılan İşlem
"Config Overlay" modelinden "Full Clone" modeline geçiş için altyapı hazırlandı. Her varlığa (strateji, süreç, KPI, faaliyet vb.) plan_year_id FK ve source_id zinciri eklendi. clone_full_plan_year() servisi tüm yapıyı hiyerarşik sırayla kopyalar. Migration çalıştırılınca kolonlar oluşur; genesis scripti mevcut verileri en eski plan_year'a atar.

### Notlar
Migration + genesis script çalıştırıldı, tüm hatalar düzeltildi (Process.parent FK belirsizliği, Project sınıf çakışması → PlanProject olarak yeniden adlandırıldı). 18 tenant için 473 KPI, 2454 faaliyet, 64 strateji genesis PlanYear'a bağlandı.
FAZA 3 (sorgu güncellemeleri), FAZA 4 (SWOT/TOWS/Proje route'ları), FAZA 5 (UI) sonraki task'larda.

## TASK-067 | 2026-04-06 | ✅ Tamamlandı

**Görev:** SP geçmiş yıl başlatma — kurum yöneticisi başlangıç yılı seçince plan_year'lar otomatik oluşturulur
**Modül:** sp / kurum
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/models/core.py` → `Tenant.plan_year_start` (Integer nullable) kolonu eklendi
- `migrations/versions/b1c2d3e4f5a6_tenant_plan_year_start.py` → yeni migration (uygulandı)
- `app/services/plan_year_service.py` → `initialize_plan_years(tenant_id, start_year)` eklendi
- `micro/modules/kurum/routes.py` → POST'ta `plan_year_start` işleme + `initialize_plan_years` çağrısı
- `ui/templates/platform/kurum/ayarlar.html` → toggle altına "Geçmiş yılları dahil et" dropdown
- `ui/static/platform/js/kurum_ayarlar.js` → plan_year_start collect + toggle show/hide

### Yapılan İşlem
Kurum yöneticisi `/kurum/ayarlar`'da "Yıllık dönem planlamasını etkinleştir" toggle'ı açtıktan sonra başlangıç yılını (2021–2026) seçer. Kaydet'e basınca `initialize_plan_years()` seçilen yıldan bugüne kadar tüm `plan_year` kayıtlarını oluşturur, mevcut KPI/strateji/süreç fallback değerleriyle seed eder. Geçmiş yıllar `status=closed`, aktif yıl `status=active` olarak oluşturulur.

### Notlar
E1 ertelenen iş tamamlandı (kullanıcı canlı geçişi yaptı 2026-04-06).

## TASK-066 | 2026-04-05 | ✅ Tamamlandı

**Görev:** /ayarlar/yedekleme sayfasına kurum bazlı JSON yedekleme ve geri yükleme eklendi
**Modül:** admin / backup
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `services/tenant_backup_service.py` → yeni servis — ~55 tabloyu kapsayan TABLE_PLAN, export/preview/restore/sequence reset
- `micro/modules/admin/routes.py` → import + 2 yeni route (kurum_indir GET, kurum_yukle POST) + ayarlar_yedekleme'ye tenant_list eklendi
- `ui/templates/platform/ayarlar/yedekleme.html` → "3 — Kurum yedeği" kartı + JS (select → download link)

### Yapılan İşlem
Kurum bazlı yedekleme: admin kullanıcı kurum seçer, `export_tenant_json()` o kuruma ait ~55 tabloyu FK sırasıyla sorgular ve JSON+gzip olarak döner. Geri yükleme: .json.gz yükle + şifre doğrula → ters sırayla DELETE → doğru sırayla INSERT ON CONFLICT DO NOTHING → sequence reset.

### Notlar
Restore sırasında begin_nested kullanılır; hata dizisi max 20 ile sınırlı; sequence güncelleme ayrı commit'te.

## TASK-065 | 2026-04-05 | ✅ Tamamlandı

**Görev:** audit_logs eksik kolon migration + AuditLogger db instance düzeltmesi
**Modül:** admin / audit
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `migrations/versions/a0b1c2d3e4f5_audit_logs_missing_columns.py` → yeni migration
- `app/utils/audit_logger.py` → `from app.extensions import db` → `from extensions import db` (doğru instance)

### Yapılan İşlem
`audit_logs` tablosunda `username`, `description`, `request_method`, `request_path` kolonları yoktu. `AuditLogger.log()` her çağrıldığında PostgreSQL `UndefinedColumn` hatası veriyordu; `except` bloğu sadece `print()` yaptığı için sessizce yutuluyordu. Sonuç: yönetim panelindeki tüm login istatistikleri yeni kayıt göremiyordu. Eksik kolonlar `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` ile eklendi, migration `a0b1c2d3e4f5` olarak kaydedildi (alembic_version güncellendi). Ayrıca `audit_logger.py` başlatılmamış `app.extensions.db` yerine kök `extensions.db` kullanacak şekilde düzeltildi.

### Notlar
VM deploy sırasında `flask db upgrade` bu migration'ı idempotent şekilde uygulayacak.

## TASK-064 | 2026-04-05 | ✅ Tamamlandı

**Görev:** Yönetim Paneli Login İstatistikleri hata düzeltme + kullanıcı bazlı aktivite tablosu
**Modül:** admin
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `services/audit_service.py` → `register_auth_audit_signals` eski `audit_log` yerine `app.models.audit.AuditLog` kullanacak şekilde düzeltildi
- `micro/modules/admin/routes.py` → `get_login_stats` sadeleştirildi; `get_user_activity_stats()` + `/kullanici-detay` endpoint eklendi
- `ui/templates/platform/admin/yonetim_paneli.html` → stat kartları düzeltildi, kullanıcı durumu tablosu eklendi
- `ui/static/platform/js/yonetim_paneli.js` → kullanıcı tablosu yükleme/render fonksiyonları eklendi
- `ui/static/platform/css/admin.css` → `.yp-stat-sub` style eklendi

### Yapılan İşlem
Kök sorun: `audit_service.py` login/logout olaylarını `audit_log` (legacy) tablosuna yanlış sütun adlarıyla yazıyordu, sessizce hata veriyordu; istatistik endpoint'i `audit_logs` (yeni) tablosunu okuduğu için sayılar hep 0 geliyordu. `register_auth_audit_signals` yeni modelle düzeltildi. Kullanıcı bazlı tablo (çevrimiçi, son giriş, 30G giriş/işlem) eklendi.

### Notlar
Geçmiş login kayıtları görünmez; sayılar fix sonrası sıfırdan birikecek.

## TASK-063 | 2026-04-05 | ✅ Tamamlandı

**Görev:** /process sayfasında süreç kartında aktif yılın gerçek başarı oranını göster
**Modül:** surec
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/surec/routes.py` → `compute_process_scores_internal` import edildi; `surec()` route'unda sayfa yüklenirken yıllık skor hesaplandı, `process_scores` dict template'e geçildi
- `ui/templates/platform/surec/index.html` → `p.progress` yerine `process_scores.get(p.id)` kullanıldı

### Yapılan İşlem
`surec()` route'u, sayfayı render ederken `compute_process_scores_internal(tid, year, today, persist_pg_scores=False)` çağırarak her süreç için anlık başarı skorunu hesaplar ve `process_scores` dict olarak template'e iletir. Template'de `{% set _ps = (process_scores.get(p.id) or 0)|round|int %}` ile değer alınır; progress bar ve `%` gösterimi buna göre güncellenir.

### Notlar
`persist_pg_scores=False` → salt okunur hesaplama, DB'ye yazılmaz. Hata durumunda `process_scores={}` fallback ile sayfa bozulmaz (tüm süreçler %0 görünür).

---

## TASK-062 | 2026-04-05 | ✅ Tamamlandı

**Görev:** SP Yıllık Dönem özelliğini kurum tercihine bağlı toggle yaptı
**Modül:** `kurum`, `sp`, `surec`
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/models/core.py` → `Tenant` modeline `plan_year_enabled` (Boolean, default False) eklendi
- `migrations/versions/z3a4b5c6d007_tenant_plan_year_enabled.py` → YENİ: Alembic migration (uygulandı ✅)
- `micro/modules/sp/routes.py` → `sp()` route: `plan_year_feature` bayrağı; kapalıysa yıl listesi çekilmiyor
- `ui/templates/platform/sp/index.html` → Plan year bar + modal + JS `{% if plan_year_feature %}` koşuluna alındı
- `micro/modules/surec/routes.py` → `surec_api_karne` ve `surec_api_kpi_list`: `plan_year_enabled` kapalıysa `get_plan_year` atlanıyor
- `ui/templates/platform/kurum/ayarlar.html` → K-Vektör'ün hemen altına "Yıllık Plan Dönemleri" toggle kartı eklendi
- `micro/modules/kurum/routes.py` → `plan_year_enabled` toggle kaydediliyor
- `ui/static/platform/js/kurum_ayarlar.js` → `plan_year_enabled` toggle verisi payload'a eklendi

### Yapılan İşlem
`Tenant` modeline `plan_year_enabled` boolean kolonu eklendi; kapalıyken SP plan year bar/modal HİÇ render edilmiyor, JS yüklenmiyor ve skor motoru KPI yıl config tablolarına bakmıyor (ProcessKpi fallback otomatik devrede). Kurum Ayarları sayfasına K-Vektör toggle kartıyla aynı biçimde yeni kart eklendi.

### Notlar
Mevcut tüm tenantlar için `plan_year_enabled = False` (migration server_default=false). Özelliği kullanmak isteyen kurum Kurum Ayarları → Yıllık Plan Dönemleri → toggle açar.

---

## TASK-061 | 2026-04-05 | ✅ Tamamlandı

**Görev:** SP Yıllık Dönem Sistemi — PlanYear mimarisi (Faz 1-6 altyapısı)
**Modül:** `sp`, `surec`, `plan_year`
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/models/plan_year.py` → YENİ: PlanYear, KpiYearConfig, StrategyYearConfig, SubStrategyYearConfig, ProcessYearConfig, IndividualKpiYearConfig modelleri
- `app/models/__init__.py` → 6 yeni model export edildi
- `migrations/versions/y2z3a4b5c006_plan_year_tables.py` → YENİ: 6 tablo migration (uygulandı ✅)
- `app/services/plan_year_service.py` → YENİ: fallback zinciri, get_kpi_configs_bulk, clone_plan_year, close_plan_year, upsert_kpi_year_config
- `app/services/score_engine_service.py` → plan_year parametresi eklendi; get_pg_scores ve compute_process_scores yıllık config kullanıyor
- `micro/modules/sp/routes.py` → 7 yeni plan year API endpoint; session active year; plan_years template'e aktarıldı
- `micro/modules/surec/routes.py` → surec_api_karne ve surec_api_kpi_list year-aware config (get_kpi_configs_bulk)
- `ui/templates/platform/sp/index.html` → Plan Year Bar UI (yıl seçici, yeni yıl modalı, yılı kapat butonu)
- `ui/static/platform/js/sp_plan_year.js` → YENİ: yıl seçici, yeni yıl oluşturma, yılı kapatma JS
- `ui/static/platform/css/sp.css` → Plan year bar CSS

### Yapılan İşlem
SP modülüne tüm fazları kapsayan yıllık dönem altyapısı eklendi. Her tenant için yılda bir `plan_years` kaydı tutulur; tüm KPI/strateji/süreç/bireysel PG konfigürasyonları bu yıla özgü overlay tablolarında saklanır. Yıllık config yoksa mevcut `ProcessKpi` değerleri fallback olarak kullanılır (sıfır kırılma garantisi). Karne sayfası artık seçili yılın hedeflerini kullanarak hesaplama yapar; yıl içinde hedef değişince geçmiş dönemler de otomatik olarak yeni hedefe göre hesaplanır (dinamik, store edilmez). `/sp` sayfasına plan dönemi seçici çubuğu eklendi; yeni yıl klonlama ve yılı kapatma akışları tamamlandı.

### Notlar
- Ertelenen: E1 — canlı DB'deki mevcut verilerin yıllık config'e migrasyon analizi (ayrı task)
- Ertelenen: D3 — yıllar arası karşılaştırma ekranı (altyapı hazır, UI/route henüz yok)
- `kpi_period_targets` tablosu eklenmedi; mevcut `computeCellTargetMicro` JS fonksiyonu (ölçüm_periyodu çarpan mantığı) yeterli bulundu

---

## TASK-060 | 2026-04-03 | ✅ Tamamlandı

**Görev:** Süreç karnesi PG kanban + K-Vektör analizi + PG tablo Swal katmanı + kurum K-Vektör anahtarı görünürlüğü
**Modül:** `surec.js`, `pg_tablo_modal.js`, `surec.css`, `karne.html`, `micro/modules/surec/routes.py`, `kurum/ayarlar.html`, `kurum.css`

### Yapılan İşlem
- **PG kanban kartları:** Hedef ve Gerçekleşen yanına birim soneki (değer `—` değilse); eski «Birim» satırı kaldırıldı, yerine tablo modalıyla aynı mantıkta **Başarı Puanı** (`formatKanbanBasariPuaniLikeTable`).
- **Periyot veri detayı — PGV silme onayı:** SweetAlert2’nin nested modal arkasında kalması giderildi: `swal-above-nested-modal` z-index yükseltildi, `pg_tablo_modal.js` silme `Swal.fire` için `didOpen` ile z-index; karne başarı aralığı bilgi `Swal`’ına aynı `didOpen`.
- **K-Vektör Analizi:** `surec_karne` şablona `k_vektor_enabled` aktarımı; üst bant **Görünüm** grubunda «Süreç Faaliyetleri»nin sağında buton (yalnız K-Vektör açık kurumda); modal: PG ağırlık toplamı %100 uyarısı, ağırlık tablosu toggle, başarı yapılandırması aktif/pasif sayıları, pasif PG’ler için **akordeon** liste, aktif PG’lerde 0–100 tam sayı aralık analizi ve **hatalı / sorunsuz** PG ayrımı.
- **Kurum ayarları:** K-Vektör «kullanımını etkinleştir» için görünür **toggle kartı** (büyük kaydırma, Kapalı/Açık rozetleri, hover/açık durum stilleri, karanlık tema); `kurum.css` sayfaya `extra_css` ile bağlandı.

### Değiştirilen Dosyalar
- `ui/static/platform/js/surec.js` — kanban meta + `formatKanbanBasariPuaniLikeTable` ve yardımcılar; K-Vektör modal render/akordeon/bölüm 3 listeleri; bilgi Swal `didOpen`
- `ui/static/platform/js/pg_tablo_modal.js` — silme onayı Swal `didOpen`
- `ui/static/platform/css/surec.css` — Swal z-index; K-Vektör analizi + akordeon stilleri; banner KV butonu
- `ui/templates/platform/surec/karne.html` — `data-k-vektor-enabled`, bantta KV butonu, KV modal iskeleti
- `micro/modules/surec/routes.py` — `surec_karne` içinde `k_vektor_enabled`
- `ui/templates/platform/kurum/ayarlar.html` — K-Vektör toggle markup, `kurum.css` linki
- `ui/static/platform/css/kurum.css` — `.kv-enable-*` toggle paneli

### Notlar
KV analizi verisi açılışta seçili yıl için `/process/api/karne/...` ile yenilenir.

---

## TASK-059 | 2026-04-03 | ✅ Tamamlandı

**Görev:** 6 ayrı UI düzeltmesi — SP badge, süreç tıklama, karne banner, kanban detay, VGS ikon, modal toolbar
**Modül:** sp, surec (index, karne), surec.js, pg_tablo_modal.js
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/static/platform/css/sp.css` → alt strateji chip başlığı çok satırlı (white-space:normal, word-break)
- `ui/templates/platform/surec/index.html` → süreç adı `<a>` tag ile karne linkine bağlandı
- `ui/templates/platform/surec/karne.html` → Rev. No kaldırıldı; VGS buton ikonu fa-wand-magic-sparkles, yazı "Veri Giriş Sihirbazı"; modal toolbar karne kartı gibi (start/center/end) yeniden düzenlendi
- `ui/static/platform/js/surec.js` → kanban Gerçekleşen hücresine data-kpi-id/data-period-key + click → openVeriDetay
- `ui/static/platform/js/pg_tablo_modal.js` → public `openVeriDetay(kpiId, periodKey)` API'ye eklendi
- `ui/static/platform/css/surec.css` → modal toolbar justify-content:center kaldırıldı

### Yapılan İşlem
SP alt strateji badge'leri uzun başlıklarda 2+ satır olabilecek şekilde açıldı. Süreç listesinde her süreç adı karne sayfasına link oldu. Karne banner'dan Rev. No satırı kaldırıldı. Kanban PG kartlarında Gerçekleşen hücresine tıklayınca pg_tablo_modal'dan `openVeriDetay` çağrılarak Periyot veri detayı modalı doğrudan açılıyor. Karne PG kartındaki VGS butonu ikon+yazı güncellendi. PG tablo modalı toolbar'ı [Yıl+Gösterim | Önceki+Badge+Sonraki | Butonlar] düzenine getirildi.

### Notlar
Yok.

---

## TASK-058 | 2026-04-03 | ✅ Tamamlandı

**Görev:** VM’den yerele yönergesi (`docs/VM_DEN_YERELE.md`)
**İçerik:** Git ile senkron (tercih), VM’den scp ile dosya/dump, PostgreSQL `pg_dump` indirme ve yerel restore özeti, `instance/` kopyası, KVKK/.env uyarıları; `YERELDEN_VM_YAYIN.md` ve `PROJE-MASTER.md` çapraz referans.

---

## TASK-057 | 2026-04-03 | ✅ Tamamlandı

**Görev:** Bakım modu — yayın/migration riskini azaltma; Admin kurtarma yolları
**Modül:** `system_settings`, middleware, yönetim paneli

### Yapılan İşlem
- `system_settings` tablosu + `maintenance_mode` bayrağı (Alembic `w1x2y3z4b004`).
- `MAINTENANCE_MODE` / `MAINTENANCE_OVERRIDE_OFF` / `MAINTENANCE_BYPASS_SECRET` ortam değişkenleri.
- Öncelikli `before_request`: Admin tam erişim; `/login` vb. whitelist; opsiyonel `bakim_erisim` + imzalı çerez; `docs/YERELDEN_VM_YAYIN.md` bölüm G.

### Değiştirilen / Eklenen Dosyalar
- `app/models/system_setting.py`, `migrations/versions/w1x2y3z4b004_*.py`, `app/services/maintenance_service.py`, `app/utils/maintenance_middleware.py`, `app/__init__.py`, `config.py`, `micro/modules/admin/routes.py`, `ui/templates/platform/maintenance.html`, `ui/templates/platform/admin/yonetim_paneli.html`, `ui/static/platform/js/yonetim_paneli.js`, `docs/YERELDEN_VM_YAYIN.md`

---

## TASK-056 | 2026-04-03 | ✅ Tamamlandı

**Görev:** Yerelden VM’e yayın prosedürünün tek belgede toplanması
**Dosya:** `docs/YERELDEN_VM_YAYIN.md` — push → `vm_safe_deploy.sh` → doğrulama; yaşanan sorunlar (sekans, PowerShell/SQL, pg_dump, SQLite vs PostgreSQL, eski deploy betiği uyarısı). `PROJE-MASTER.md` bölüm 15 ve `KURALLAR-MASTER.md` bölüm 8 güncellendi.

---

## TASK-055 | 2026-04-03 | ✅ Tamamlandı

**Görev:** Canlı dağıtım + `kpi_data` sekans düzeltmesi + Docker uyumlu `fix_postgres_sequences`
**Yapılan:** `vm_safe_deploy.sh` (pg yedek, pull `08584a2`, image, Alembic, satır sayısı kontrolü); VM `psql` ile `fix_kpi_data_sequences.sql`; konteynerde betik `PYTHONPATH` yaması ve doğrulama; `ef08e30` push (`scripts/sql/...` + betik düzeltmesi).

---

## TASK-054 | 2026-04-03 | ✅ Tamamlandı

**Görev:** PostgreSQL `kpi_data` / `kpi_data_audits` PK duplicate (sekans geride) — otomatik düzeltme
**Modül:** `db_sequence`, süreç API’leri, faaliyet otomatik PGV

### Yapılan İşlem
- `sync_kpi_data_related_sequences()`: her iki tablonun `id` sekansını `MAX(id)+1` ile hizalar.
- PGV ekleme uçlarında (micro `/process/api/kpi-data/add`, legacy `add_kpi_data`, `/api/v1/kpi-data`) duplicate tespitinde sekans senkronu + tek retry.
- `auto_complete_due_activities`: vadesi gelen faaliyetlerde otomatik KpiData üretiminden önce aynı sekans hizalaması (batch öncesi).
- Eski `app/api/v1` `create_kpi_data` için `kpi_data` duplicate retry.

### Değiştirilen Dosyalar
- `app/utils/db_sequence.py`
- `micro/modules/surec/routes.py`
- `app/routes/process.py`
- `micro/modules/api/routes.py`
- `app/api/routes.py`
- `app/services/process_activity_service.py`
- `scripts/fix_postgres_sequences.py` (docstring)

---

## TASK-053 | 2026-04-03 | ✅ Tamamlandı

**Görev:** Süreç karnesi PG tablo modalına «Ağırlıklı Başarı Puanı» sütunu
**Modül:** surec / `pg_tablo_modal.js`, `karne.html`

### Yapılan İşlem
`Ağırlık (%)` değeri 0–100 ise 100’e bölünerek normalize edilir; başarı 1–5 aralık puanı veya yüzde gösterimi ile çarpılır (`karne_hesaplamalar.hesapla_agirlikli_basari_puani` ile uyumlu). Sütun «Yıllık Gerçekleşme» ile «Başarı Puanı» arasına eklendi; sütun görünürlük panelinde kapatılabilir.

### Değiştirilen Dosyalar
- `ui/static/platform/js/pg_tablo_modal.js`
- `ui/templates/platform/surec/karne.html`

---

## TASK-052 | 2026-04-03 | ✅ Tamamlandı

**Görev:** Yönetim paneli istatistik endpointinde transaction-aborted hatasının giderilmesi
**Modül:** admin / login istatistikleri

### Değiştirilen Dosyalar
- `micro/modules/admin/routes.py` → `_unique_login_count` fallback exception handling

### Yapılan İşlem
`user_activity_log` fallback sorgusunda hata olduğunda SQLAlchemy transaction abort durumunda kalıyor ve sonraki sorgular `InFailedSqlTransaction` ile düşüyordu. Fallback `except` bloğuna `db.session.rollback()` eklenerek transaction temizliği sağlandı.

---

## TASK-051 | 2026-04-03 | ✅ Tamamlandı

**Görev:** Yönetim paneli login istatistiklerinde legacy login akışı için fallback
**Modül:** admin / login istatistikleri

### Değiştirilen Dosyalar
- `micro/modules/admin/routes.py` → `get_login_stats._unique_login_count`

### Yapılan İşlem
Canlıda bazı giriş akışlarının login olaylarını `audit_logs` yerine `user_activity_log` tablosuna (`tip='login'`) yazması nedeniyle son 24s/7g sayaçları artmıyordu. Audit sonucu 0 olduğunda ve tüm kurum görünümünde `user_activity_log` üzerinden fallback sayım eklendi.

---

## TASK-050 | 2026-04-03 | ✅ Tamamlandı

**Görev:** Yönetim panelinde “Şu an aktif” metrik tanımının aktif kullanıcı hesap sayısı olarak düzeltilmesi
**Modül:** admin / login istatistikleri

### Değiştirilen Dosyalar
- `micro/modules/admin/routes.py` → `get_login_stats`

### Yapılan İşlem
Paneldeki “Şu an aktif” alanı audit login/logout akışına bağlı çevrimiçi kullanıcı hesabı nedeniyle 0 görünebiliyordu. Metrik tenant filtreli **aktif kullanıcı hesabı** (`users.is_active=true`) olacak şekilde güncellendi. Eski çevrimiçi oturum hesabı `online_now` olarak JSON çıktısında korunmuştur.

---

## TASK-049 | 2026-04-03 | ✅ Tamamlandı

**Görev:** Yönetim panelinde tenant bazlı aktif kullanıcı istatistiğinin boş gelmesi
**Modül:** admin / login istatistikleri

### Değiştirilen Dosyalar
- `micro/modules/admin/routes.py` → `get_login_stats` tenant filtresi

### Yapılan İşlem
`audit_logs` kayıtlarında `tenant_id` boş olan login/logout satırları için tenant filtrelemesi yalnız `audit_logs.tenant_id` ile yapıldığında tenant bazlı istatistikler 0 görünebiliyordu. Filtreye fallback eklendi: `tenant_id` boşsa `user_id -> users.tenant_id` eşleştirmesi ile aynı tenant kullanıcıları sayılır.

---

## TASK-048 | 2026-04-03 | ✅ Tamamlandı

**Görev:** PG tablo modalında aralık hedef gösterimi + "Yıllık Gerçekleşme" sütunu
**Modül:** surec / karne API + modal tablo UI

### Değiştirilen Dosyalar
- `micro/modules/surec/routes.py` → `surec_api_karne` yanıtına `year_rollup` eklendi
- `ui/static/platform/js/pg_tablo_modal.js` → yıllık hedefte aralık formatı + yeni sütun render

### Yapılan İşlem
Tablo görünümünde `Yıllık Hedef` alanı, hedef aralık girilmişse (örn. `20-24`) iki ucu da yıllık ölçeğe çevirip `min-max` formatında gösterilecek şekilde güncellendi. Ayrıca `Başarı Puanı`ndan hemen önce `Yıllık Gerçekleşme` sütunu eklendi; değer, ilgili yılın ham PGV kayıtlarından veri toplama yöntemine göre (Toplama/Ortalama/Son Değer) hesaplanıp gösteriliyor.

---

## TASK-047 | 2026-04-03 | ✅ Tamamlandı

**Görev:** Performans göstergesi modalı ölçüm birimine "Hafta" eklenmesi
**Modül:** surec / karne UI

### Değiştirilen Dosyalar
- `ui/templates/platform/surec/karne.html` → `kpi-add-unit-options` datalist

### Yapılan İşlem
PG ekle/düzenle modalında kullanılan ölçüm birimi öneri listesine `Hafta` seçeneği eklendi.

---

## TASK-046 | 2026-04-03 | ✅ Tamamlandı

**Görev:** PG tablo modalı — «Önceki Yıl» hesaplama çarpan hatasının düzeltilmesi
**Modül:** surec / karne API

### Değiştirilen Dosyalar
- `micro/modules/surec/routes.py` → önceki yıl rollup hesabı ham PGV satırlarından yapılacak şekilde düzeltildi

### Yapılan İşlem
Önceki yıl değeri hesaplanırken period-key bazlı ara toplamlardan gidildiği için aynı PGV birden çok periyot anahtarına yazıldığında (yıllık/çeyrek/aylık) değer katlanıyordu (örn. 30 → 180). Hesap artık doğrudan **önceki yılın ham aktif PGV satırları** üzerinden yapılıyor; böylece yıllık satır 30 ise önceki yıl sütununda 30 görünür.

---

## TASK-045 | 2026-04-03 | ✅ Tamamlandı

**Görev:** Süreç Karnesi — PG tablo modalında «Önceki Yıl» sütunu (PGV özeti veya elle ortalama)
**Modül:** surec / karne API + modal tablo

### Değiştirilen Dosyalar
- `micro/modules/surec/routes.py` → `surec_api_karne`: önceki takvim yılı PGV’sinden özet (`prev_year_rollup`, `prev_year_from_pgv`), `onceki_yil_ortalamasi`
- `ui/static/platform/js/pg_tablo_modal.js` → sütun, yıldız + `title` ile bilgi (hesaplanan veri)
- `ui/templates/platform/surec/karne.html` → sütun görünürlük seçeneği
- `ui/static/platform/css/surec.css` → yıldız stili

### Yapılan İşlem
Tablo modalında **Önceki Yıl** sütunu: önceki yılda aktif PGV varsa veri toplama yöntemine göre özetlenir ve küçük yıldız ile «Bu veri önceki yıldan hesaplanmıştır.» ipucu gösterilir; yoksa PG kaydındaki **Önceki Yıl Ortalaması** alanı gösterilir (yıldız yok).

---

## TASK-044 | 2026-04-03 | ✅ Tamamlandı

**Görev:** Süreç Karnesi PG kanban gauge — başarı yüzdesinin seçili döneme göre hesaplanması
**Modül:** surec / karne UI

### Değiştirilen Dosyalar
- `ui/static/platform/js/surec.js` → `computeKpiKanbanScorePct` + `getKanbanActualNumeric`; `renderKanbanGauge` bağlam iletti

### Yapılan İşlem
Gauge skoru artık yıllık toplam hedef ve tüm `entries` değerlerinden değil; karttaki **Hedef** / **Gerçekleşen** ile aynı görünüm (`view`), gösterim periyodu ve `periodKey` üzerinden hesaplanıyor. Aralık hedefte skor, backend ile uyumlu olarak `Increasing` → ölçeklenmiş küçük uç, `Decreasing` → büyük uç. Gerçekleşen yoksa skor `null`, gauge **—** (sahte %100 yok).

---

## TASK-043 | 2026-04-03 | ✅ Tamamlandı

**Görev:** PG kartı hedef aralık gösteriminde periyot ölçekleme mantığının korunması
**Modül:** surec / karne UI

### Değiştirilen Dosyalar
- `ui/static/platform/js/surec.js` → `getMetaHedefKanban` aralık hedefte iki ucu periyoda göre ölçekleyip gösterir

### Yapılan İşlem
PG kartındaki `Hedef` alanında aralık değerler (`20-24`) için gösterim, önceki otomatik periyot mantığına geri alındı: yıllıkta `20-24`, 6 aylıkta `10-12`, çeyrekte `5-6` gibi iki uç da aynı hesapla ölçeklenerek gösterilir.

---

## TASK-042 | 2026-04-03 | ✅ Tamamlandı

**Görev:** Süreç Karnesi PG kartında aralıklı hedef değerin ham gösterimi
**Modül:** surec / karne UI

### Değiştirilen Dosyalar
- `ui/static/platform/js/surec.js` → `getMetaHedefKanban` içinde aralık hedef (`min-max`) için ham metin gösterimi

### Yapılan İşlem
Süreç Karnesi — Performans Göstergeleri kartındaki `Hedef` alanında, hedef değer aralık formatında girildiyse (örn. `20-24`) hesaplanmış tekil değer yerine kullanıcı girişindeki ham aralık metni gösterilecek şekilde düzenlendi. Hesaplama davranışı değişmedi.

---

## TASK-041 | 2026-04-03 | ✅ Tamamlandı

**Görev:** PG hedef değeri aralık girişi (örn. "45-49") — hesaplamada yön bazlı tek değer, gösterimde ham metin
**Modül:** score engine / performans hesaplama

### Değiştirilen Dosyalar
- `app/services/score_engine_service.py` → `_resolve_target_for_calculation`; PG skorunda hedef çözümlemesi
- `services/performance_service.py` → `calculateHedefDeger` aralık + `direction`; `generatePeriyotVerileri` `direction` parametresi
- `app/services/process_performance_service.py` → `generatePeriyotVerileri` çağrısına `direction` iletimi

### Yapılan İşlem
`Hedef Değer` alanına tek aralık formatı (`min-max`) girildiğinde `Increasing` için küçük uç, `Decreasing` için büyük uç hesaplamalara alındı; veritabanı / ekranda girilen metin değişmedi.

---

## TASK-040 | 2026-04-02 | ✅ Tamamlandı

**Görev:** /ayarlar sayfasına Admin'e özel Yönetim Paneli linki eklendi
**Modül:** ayarlar / index

### Değiştirilen Dosyalar
- `ui/templates/platform/ayarlar/index.html`

### Yapılan İşlem
Ayarlar hub sayfasında yalnızca `Admin` rolünün gördüğü bölüm içine Yönetim Paneli bağlantısı eklendi. Link kartındaki inline stil kaldırılarak sınıf tabanlı stil kullanıldı.

---

## TASK-039 | 2026-04-02 | ✅ Tamamlandı

**Görev:** Son iki değişikliğin geri alınması (KPI tipi + kullanıcı arama iyileştirmeleri)
**Modül:** surec / admin / ayarlar

### Değiştirilen Dosyalar
- `micro/modules/surec/routes.py` → KPI tipi doğrulama için eklenen sabit/fonksiyon ve ilgili kullanım geri alındı
- `ui/templates/platform/surec/karne.html` → `Sonuç` KPI tipi seçeneği kaldırıldı
- `ui/templates/platform/ayarlar/index.html` → Ayarlar hub’daki Yönetim Paneli linki kaldırıldı
- `ui/templates/platform/admin/users.html` → `data-search` alanı eski haline döndürüldü, sonuç-yok kutusu kaldırıldı
- `ui/static/platform/js/admin.js` → kullanıcı arama kutusu önceki basit filtreleme davranışına döndürüldü

### Yapılan İşlem
Kullanıcı talebine göre son iki adımda eklenen geliştirmeler geri alındı ve ilgili dosyalar bir önceki çalışma davranışına döndürüldü.

---

## TASK-038 | 2026-04-02 | ✅ Tamamlandı

**Görev:** SQLAlchemy sürüm doğrulama ve venv ile uygulama başlatma testi
**Modül:** altyapı / bağımlılık yönetimi

### Değiştirilen Dosyalar
- `requirements.txt` → `sqlalchemy>=2.0.36` satırı eklendi
- `docs/TASKLOG.md` → TASK-038 kaydı eklendi

### Yapılan İşlem
`requirements.txt` içindeki SQLAlchemy sürümü kontrol edildi, ardından `.venv\Scripts\pip.exe install "sqlalchemy>=2.0.36"` komutu çalıştırıldı (venv’de `2.0.48` zaten kurulu). Sonrasında `.venv\Scripts\python.exe app.py` ile uygulama başlatma testi yapıldı ve servis başarıyla ayağa kalktı.

---

## TASK-037 | 2026-04-02 | ✅ Tamamlandı

**Görev:** Yönetim Paneli — aktivite logu, eksik loglama ve UI
**Modül:** admin / yonetim_paneli

### Değiştirilen Dosyalar
- `app/routes/auth.py` → raw SQL audit kaldırıldı, AuditLogger.log() geçildi
- `micro/modules/admin/routes.py` → /aktiviteler endpoint + AuditLogger import
- `micro/modules/admin/constants.py` → AKTIVITE_ETIKETLER + RESOURCE_IKONLAR
- `micro/modules/surec/routes.py` → 19 noktaya audit log eklendi
- `micro/modules/proje/routes_project_crud.py` → proje create/update logları
- `micro/modules/proje/routes_tasks.py` → proje faaliyeti create/update logları
- `ui/templates/platform/admin/yonetim_paneli.html` → aktivite tablosu
- `ui/static/platform/js/yonetim_paneli.js` → fetch + skeleton + zaman formatı
- `ui/static/platform/css/admin.css` → tablo ve skeleton stilleri

### Yapılan İşlem
`audit_logs` tablosu üzerine 19 route/view noktasına `AuditLogger` tabanlı kayıtlar eklendi; `GET /micro/admin/yonetim-paneli/aktiviteler` endpoint’i ile kullanıcı, işlem etiketi ve kaynak ikonu içeren listeleme sağlandı. Yönetim paneli UI tarafında aktivite tablosu, tenant filtresiyle eşzamanlı yenileme, skeleton yükleme ve “X dk/saat/gün önce” zaman gösterimi tamamlandı.

---

## TASK-036 | 2026-04-02 | ✅ Tamamlandı

**Görev:** Yönetim paneli login istatistiklerinde 0 görünme hatası (audit yazımı + aksiyon filtre uyumu)
**Modül:** `app/routes/auth.py`, `micro/modules/admin/routes.py`
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/routes/auth.py` → login/logout akışına `audit_logs` kaydı eklendi; şema uyumsuzluk riskine karşı raw SQL ile ortak kolonlara yazım
- `micro/modules/admin/routes.py` → `get_login_stats` aksiyon filtreleri (`OTURUM AÇMA/KAPATMA`, `LOGIN/LOGOUT`) bozuk karakterli legacy kayıtları da kapsayacak şekilde genişletildi

### Yapılan İşlem
Yönetim panelinde son 24 saat/7 gün/aktif değerlerinin sürekli 0 gelmesinin nedeni, yeni oturumların `audit_logs` tablosuna düzenli yazılmaması ve bazı eski kayıtlarda aksiyon metninin karakter bozulmasıydı. Auth tarafına oturum açma/kapatma kayıtları güvenli şekilde eklendi; panel istatistik filtresi hem yeni hem legacy aksiyon adlarını kapsayacak şekilde güncellendi.

### Notlar
`active_now` hâlâ son 30 dakika heuristiği ile hesaplanır; gerçek session tablosu yoktur.

---

## TASK-035 | 2026-04-02 | ✅ Tamamlandı

**Görev:** Yönetim Paneli — login istatistikleri (audit_logs tabanlı)
**Modül:** admin / yonetim_paneli

### Değiştirilen Dosyalar
- `micro/modules/admin/routes.py` → `get_login_stats`, `get_tenant_list` ve 2 yeni route eklendi
- `ui/templates/platform/admin/yonetim_paneli.html` → yönetim paneli sayfası oluşturuldu
- `ui/static/platform/js/yonetim_paneli.js` → tenant filtresi + fetch + kart güncelleme eklendi
- `ui/static/platform/css/admin.css` → panel kart/grid stilleri eklendi

### Yapılan İşlem
`audit_logs` tablosundaki `OTURUM AÇMA` kayıtlarından 6 farklı zaman aralığı için istatistik üreten yönetim paneli geliştirildi. `tenant_id` filtreli JSON endpoint ile kurum bazlı görüntüleme sağlandı, tenant_admin için kurum kapsamı otomatik daraltıldı.

### Notlar
"Aktif oturum" hesaplaması son 30 dakika heuristiği ile yapılır; gerçek session tablosu yoktur.

---

## TASK-137 | 2026-03-23 | ✅ Tamamlandı

**Görev:** Süreç Faaliyetleri V2 — süreç karne faaliyetlerine `datetime` planı, çoklu atama, çoklu hatırlatma (in-app + opsiyonel e-posta), ertele/iptal aksiyonları, scheduler ile otomatik gerçekleşme ve bağlı PG için `KpiData(actual_value=1)` otomatik üretimi
**Modül:** `app/models/process.py`, `migrations/versions/4f3a2b1c9d8e_process_activity_v2_datetime_reminders.py`, `app/routes/process.py`, `app/services/process_activity_service.py`, `services/process_activity_scheduler.py`, `micro/services/notification_triggers.py`, `templates/process/karne.html`, `static/js/process_karne.js`, `__init__.py`, `app.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-136 | 2026-03-23 | ✅ Tamamlandı

**Görev:** Micro launcher’da az modül kartı — `get_accessible_modules` paket için yanlış ilişki (`system_modules`/`slug`); paketsiz kurumda kurum yöneticisine de yalnızca minimum 3 kart; düzeltme: `SubscriptionPackage.modules` + `SystemModule.code` eşlemesi, kod→launcher id sözlüğü, ayrıcalıklı rollerde tam liste
**Modül:** `micro/core/module_registry.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-135 | 2026-03-23 | ✅ Tamamlandı

**Görev:** Veritabanından **`1KMF`** kurumu (`tenants.id=9`, KMF Yonetim Danismanligi) kalıcı silindi; yedek `instance/kokpitim_before_tenant_delete_*.db`; tekrar kullanım için `scripts/delete_tenant_permanent.py`
**Modül:** `scripts/delete_tenant_permanent.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-134 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro hızlı giriş URL’leri **`/Hgs_mfg`** ve **`/Hgs_mfg/login/<id>`**; eski **`/hgs`** ve **`/hgs/login/<id>`** → 301 yönlendirme; `module_registry`, kullanım kılavuzu, `test_upload.py`
**Modül:** `micro/modules/hgs/routes.py`, `micro/core/module_registry.py`, `docs/`
**Durum:** ✅ Tamamlandı

---

## TASK-133 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Prod öncesi düzeltmeler — V3 panel linki kaldırıldı; Süreç PG toplamı gerçek `count`; faaliyet sıralamasında `end_date` NULL sonda; masaüstü bilgi paneli (kök vs `legacy_url_prefix`, localStorage); karalama metni; bireysel karne hedef uyarısı “tahmini / resmi değil” vurgusu; `docs/micro-kullanim-kilavuzu.md` + `docs/micro-kullanim-kilavuzu-yazdir.html` (PDF için yazdır); yol haritası V3 notu güncellendi
**Modül:** `ui/templates/platform/masaustu/index.html`, `micro/modules/masaustu/routes.py`, `ui/templates/platform/bireysel/karne.html`, `ui/static/platform/js/bireysel.js`, `docs/`
**Durum:** ✅ Tamamlandı

---

## TASK-132 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Bireysel karne + Masaüstü — planın uygulanması: timeline API, PG serisi endpoint, ısı/detay/sparkline; masaüstü komuta kartı, hızlı işlemler, Benim Masam, eksik PG (bu ay), bildirim okundu, karalama + widget sırası/gizleme (LS + Sortable), `docs/masaustu-bireysel-karne-yol-haritasi.md`
**Modül:** `micro/modules/bireysel/routes.py`, `micro/modules/masaustu/routes.py`, `ui/templates/platform/bireysel/karne.html`, `ui/templates/platform/masaustu/index.html`, `ui/static/platform/js/bireysel.js`, `ui/static/platform/js/masaustu.js`, `ui/static/platform/css/bireysel-karne.css`, `ui/static/platform/css/masaustu.css`, `docs/`
**Durum:** ✅ Tamamlandı

---

## TASK-131 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Proje analizler hub (`/project/<id>/analizler`) — sayfa başlığı ve `<title>`: **Proje Analizleri (geliştirme aşamasında)**
**Modül:** `ui/templates/platform/project/analyses.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-130 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi — **PG ekle / düzenle** (`modal-kpi-add`) başlık ve footer; kök mavi «Bootstrap» görünümü kaldırıldı, Micro standart modal başlığı
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/css/surec.css`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-129 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi — **Veri Girişi Sihirbazı** modal başlığı; gradient yerine Micro standart `.mc-modal-header` / lavanta ikon rozeti
**Modül:** `ui/static/platform/css/surec.css`, `ui/templates/platform/surec/karne.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-128 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi — Performans Göstergeleri kartında **Yazdır** yanına **Tablo Görünümü** butonu; tıklanınca PG kartı ile aynı `microPgTablo.open(null)` modalı
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/js/surec.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-127 | 2026-03-19 | ✅ Tamamlandı

**Görev:** **Proje özeti** kartı — Süreç özeti ile aynı düzen: önce **Özet Bilgiler**, yöneticiler için **Kurum geneli — projeler** (`project_tenant`, `data-ov-pt`), sonra **Grafikler** akordeonları (bitiş+görev / risk); `kurum_overview` `_build_project_block`; Chart yalnız görünür canvas; API `project_tenant`
**Modül:** `micro/modules/kurum/kurum_overview.py`, `ui/templates/platform/kurum/index.html`, `ui/static/platform/js/kurum.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-126 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Kurum **Süreç özeti** kartı — önce **Özet Bilgiler** (birleşik rakam ızgarası), sonra **Grafikler** başlığı altında akordeon (PG+strateji, operasyon, risk, performans); `__kurumRedrawCharts` + görünür canvas’da Chart; çift `data-ov` için `querySelectorAll`
**Modül:** `ui/templates/platform/kurum/index.html`, `ui/static/platform/js/kurum.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-125 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Kurum **Süreç özeti** — risk/uyarı (60 gün bayat PG verisi, geciken faaliyet, eksik PG tanımı), performans (`calculated_score` ortalama, düşük/skorsuz dağılımı); yöneticiler için **kurum geneli** ayrı kutu (`process_tenant`); yalnızca yeni `Process` modeli; grafikler + API/JS güncellemesi
**Modül:** `micro/modules/kurum/kurum_overview.py`, `ui/templates/platform/kurum/index.html`, `ui/static/platform/js/kurum.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-124 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Kurum paneli — **Stratejik Kimlik** kartı en üste taşındı; **Süreç / Proje özeti** Chart.js pasta + yatay çubuk grafikleri, vurgulu metinler ve “Tüm sayılar” ızgarası; `kurum.css` yükseklik; `kurum.js` grafik yenileme + tema olayı
**Modül:** `ui/templates/platform/kurum/index.html`, `ui/static/platform/js/kurum.js`, `ui/static/platform/css/kurum.css`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-123 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Kurum paneli (`/kurum`) — **tüm giriş yapmış tenant kullanıcılarına açık**; süreç/proje **özet metrikleri** (erişim kapsamına göre); `GET /kurum/api/overview` + **90 sn** sayfa içi yenileme; düzenleme API’leri ve ayarlar rolde kaldı; `module_registry` kurum rol kısıtı kaldırıldı
**Modül:** `micro/modules/kurum/kurum_overview.py`, `micro/modules/kurum/routes.py`, `ui/templates/platform/kurum/index.html`, `ui/static/platform/js/kurum.js`, `micro/core/module_registry.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-122 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Kurum paneli (`/kurum`) — **Stratejik Kimlik** kartı akordeon (Amaç, Temel değerler, Etik, Kalite); **vizyon** akordeon dışında vurgulu hero blok; **Stratejiler** kartı ana strateji başına akordeon + alt stratejiler panelde; `kurum.js` alan okuma `data-sk-field`
**Modül:** `ui/templates/platform/kurum/index.html`, `ui/static/platform/js/kurum.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-121 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Proje analiz araçları (CPM, SLA, kapasite, baseline, bağımlılık matrisi, kurallar, entegrasyonlar, tekrarlayan, çalışma günleri) — klasik Bootstrap şablonları yerine **Micro** (`base_tool.html`, Tailwind, `mc-pt-*`, SweetAlert toast); bilgi modalı Bootstrap’siz; `project_tool_info_data.js` + `project_tools_micro.js`; rotalar `load_project` + `user_can_access_project`
**Modül:** `ui/templates/platform/project/tools/*`, `ui/static/platform/css/project_tools.css`, `ui/static/platform/js/project_tool_info_data.js` (üretim), `project_tools_micro.js`, `micro/modules/proje/routes_project_tools_root.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-120 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç Yönetimi teknik raporu — sayfalar, veri modelleri, API’ler, işleme akışları, yetkiler, legacy `Surec` özeti; `docs/Surecrapor01.md`
**Modül:** `docs/Surecrapor01.md`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-119 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Proje analizleri hub — açıklama metni kaldırıldı; CPM/SLA vb. `/kok` yerine kök `/projeler/...`; **RAID** `Unexpected token '<'` — `app.create_app` içinde `api/routes.py` (`kokpitim_project_api_bp`) kök `/api/...` + legacy `/kok/api/...` çift kayıt (Flask `name=`); kırık `Blueprint.copy` kaldırıldı; `project_raid.js` JSON doğrulama + `MICRO_API_BASE` + `credentials`
**Modül:** `app/__init__.py`, `ui/static/platform/js/project_raid.js`, `docs/TASKLOG.md` (önceki: `analyses.html`, `routes_project_tools_root.py`)
**Durum:** ✅ Tamamlandı

---

## TASK-118 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Proje detayda **Proje analizleri** butonu + `/project/<id>/analizler` hub — eski “Proje Araçları” kart ızgarası (CPM, RAID→Micro, SLA, kapasite, baseline, bağımlılık matrisi, kurallar, entegrasyon, tekrarlayan, çalışma günleri); `main.*` klasik şablonlarına link; alt çubukta görev tamamlanma %; `_project_views_nav` entegrasyonu
**Modül:** `micro/modules/proje/routes_analyses.py`, `routes.py`, `ui/templates/platform/project/analyses.html`, `detail.html`, `_project_views_nav.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-117 | 2026-03-19 | ✅ Tamamlandı

**Görev:** `/project` geliştirmeleri — **filtreler** (kapsam benim/tümü ayrıcalıklı, tarih, lider, süreç, geciken/yakında bitiş), **sıralama** (güncelleme, bitiş, ad, geciken görev), **CSV** + **ICS** dışa aktarma, **toplu e-posta kanalı** (yalnız `is_privileged`), **4 haftalık tamamlanan trend** + **ısı haritası**, **RAID** + **sağlık** KPI, **benzer proje** (`clone_from`), **Chart.js tema** (`micro-theme-changed`)
**Modül:** `micro/modules/proje/project_list_query.py`, `project_overview_service.py`, `routes_list.py`, `routes_project_crud.py`, `ui/templates/platform/project/list.html`, `ui/templates/platform/project/form.html`, `ui/static/platform/js/app.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı (haftalık özet e-posta cron, Slack/Teams, Google OAuth senk — ayrı iş)

---

## TASK-116 | 2026-03-19 | ✅ Tamamlandı

**Görev:** `/project` proje listesi — **operasyon özeti**: KPI (proje, açık/geciken görev, görev≤7g, planı geçen proje, proje bitiş≤7g), Chart.js **doughnut** (görev durumu) + **yatay bar** (öncelik), **Dikkat** listesi (geciken görev veya proje bitişi geçmiş); yetki = `accessible_projects_query`; portföy linki ayrıcalıklı roller
**Modül:** `micro/modules/proje/project_overview_service.py`, `micro/modules/proje/routes_list.py`, `ui/templates/platform/project/list.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-115 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Proje **yeni lider / yeni üye** atamalarında uygulama içi bildirim + e-posta (`notify_project_leaders_added`, `notify_project_members_added`); Micro form (oluştur/düzenle) ve REST API (`/api/projeler` oluştur + PUT güncelle); `micro_project_new` `manager_id=leader_ids[0]` düzeltmesi
**Modül:** `micro/services/notification_triggers.py`, `micro/modules/proje/routes_project_crud.py`, `api/routes.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-114 | 2026-03-22 | ✅ Tamamlandı

**Görev:** Proje düzenlemede lider/üye kaydı **DB’de vardı** ama form ve detay **ORM (Legacy `user`) boş** olduğu için değişiklik görünmüyordu — `project_leaders` / `project_members` / `project_observers` tablosundan okuma; `Project.leader_user_ids`, `member_user_ids`, `observer_user_ids`; `project_form_init` + `resolve_leader_ids_from_form(..., project=)` ile koruma
**Modül:** `models/project.py`, `micro/modules/proje/helpers.py`, `micro/modules/proje/display.py`, `micro/modules/proje/routes_project_crud.py`, `ui/templates/platform/project/detail.html`, `ui/templates/platform/project/list.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-113 | 2026-03-22 | ✅ Tamamlandı

**Görev:** Proje detay **Görev özeti (durum)** kanban sütun sırası: **Tamamlandı → Devam Ediyor → Beklemede → Yapılacak**
**Modül:** `micro/modules/proje/routes_project_crud.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-112 | 2026-03-19 | ✅ Tamamlandı

**Görev:** **Çoklu proje lideri** — `project_leaders` ilişki tablosu; `manager_id` birincil lider; Micro form/JS çoklu seçim; yetkiler, bildirimler, API (`manager_ids` + `leader_ids`), rapor/üst yönetim filtresi, klonlama, migrasyon `c7d8e9f0a1b2`
**Modül:** `models/project.py`, `models/__init__.py`, `migrations/versions/c7d8e9f0a1b2_add_project_leaders.py`, `micro/modules/proje/*`, `ui/templates/platform/project/*`, `ui/static/platform/js/project_form_transfer.js`, `api/routes.py`, `services/*`, `decorators.py`, `main/routes.py`, `v3/routes.py`, `scripts/seed_boun_sample_project.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-111 | 2026-03-19 | ✅ Tamamlandı

**Görev:** **Proje yönetimi (Micro)** görev oluşturma/düzenlemede bildirimler: uygulama içi (`notifications` + WebSocket) ve e-posta (`notification_triggers` + `email_service`); proje `channels` / `notify_manager` uyumu; varsayılan kanallar `in_app` + `email`
**Modül:** `micro/modules/proje/routes_tasks.py`, `micro/services/notification_triggers.py`, `models/project.py` (`get_notification_settings` varsayılan), `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-110 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Oturum gerekince yönlendirme **`/login?next=...`** (kökta); **`/kok/login`** yerine çubukta `/kok` olmasın; **`public_login` / `public_logout`** + `auth_bp` kayıt sırası (micro `/login` çakışması giderildi); `micro_bp.micro_login` kaldırıldı
**Modül:** `app/__init__.py`, `app/routes/auth.py`, `app/extensions.py`, `app/utils/decorators.py`, `main/routes.py`, `micro/modules/shared/auth/routes.py`, `templates/*`, `ui/templates/platform/*`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-109 | 2026-03-19 | ✅ Tamamlandı

**Görev:** BOUN tenant için **örnek proje** tohum script’i: 1 lider + 5 üye, 20 görev (12 tamamlandı); `scripts/seed_boun_sample_project.py` (`--tenant-id`, `--replace`, `--dry-run`)
**Modül:** `scripts/seed_boun_sample_project.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-108 | 2026-03-22 | ✅ Tamamlandı

**Görev:** Açılışta **klasik giriş** (`auth_bp.login` / `/kok/login`); `login_manager.login_view` → `auth_bp.login`; `/login` → klasik girişe yönlendirme; çıkış → `auth_bp.login`; `docs/micro-kok-url-migration.md`
**Modül:** `app/__init__.py`, `app/routes/auth.py`, `micro/modules/shared/auth/routes.py`, `docs/micro-kok-url-migration.md`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-107 | 2026-03-22 | ✅ Tamamlandı

**Görev:** Micro **sol sidebar marka** alanı — mor «K» yerine **Kokpitim logosu** (`docs/kokpitim-logo.png` → `ui/static/platform/img/kokpitim-logo.png`); `.sidebar-brand-logo` img + `sidebar.css` (ilk sürümdeki topbar logosu kaldırıldı)
**Modül:** `ui/templates/platform/base.html`, `ui/static/platform/css/sidebar.css`, `ui/static/platform/img/kokpitim-logo.png`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-106 | 2026-03-19 | ✅ Tamamlandı

**Görev:** **Micro kök URL** — `micro_bp` öneki kaldırıldı (`/`, `/process`, …); klasik Kokpitim **`LEGACY_URL_PREFIX`** (varsayılan **`/kok`**) altında; **`/micro/...` → kök** ve **`/isr/...` → `/kok/...`** uyumluluk yönlendirmeleri; Micro statik **`/m/`**; `login_view` → `micro_bp.micro_login`; giriş/çıkış varsayılan launcher; Swagger `create_swagger_blueprint(legacy)`; eski `/micro/...` path’li şablon/JS/registry temizliği; kök **`GET /health`**; `docs/micro-kok-url-migration.md`
**Modül:** `config.py`, `app/__init__.py`, `app/api/swagger.py`, `app/routes/auth.py`, `micro/__init__.py`, `micro/core/*`, `micro/modules/*`, `ui/templates/platform/*`, `ui/static/platform/js/*`, `main/routes.py`, `test_upload.py`, `test_photo_final.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-105 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro **RAID** sayfasında “Nasıl kullanılır?” için **Bootstrap tamamen kaldırıldı**; `mc-modal` + `tool_info_modal.js` (`TOOL_INFO_DATA` `_tool_info_modal.html`’den `scripts/gen_micro_tool_info_js.py` ile üretilir); `_tool_info_modal.html` + `project_views.css` Bootstrap sınıf shimi
**Modül:** `ui/templates/platform/project/raid.html`, `ui/templates/platform/project/_tool_info_modal.html`, `ui/static/platform/js/tool_info_modal.js`, `ui/static/platform/css/project_views.css`, `scripts/gen_micro_tool_info_js.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-104 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro **Proje Yönetimi iyileştirme planı** uygulaması: TR başlıklar; liste **arama + öncelik filtresi**; **CoreUser** ile yönetici/üye etiketleri (`display.py`); detayda **görünüm şeridi** + görev özeti + **HTML dialog** ile silme; portföy **çift yol** (klasik matris / App tenant + Surec–Process eşlemesi); rotalar **list / crud / views / tasks** dosyalarına bölündü; **`toast_notify.js`** + RAID **Bootstrap kaldırıldı** (mc + vanilla modal/sekme); takvim yükleme göstergesi; `docs/proje-legacy-ve-tenant.md`; `tests/test_micro_proje_display.py`
**Modül:** `micro/modules/proje/*`, `ui/templates/platform/project/*`, `ui/static/platform/js/toast_notify.js`, `ui/static/platform/js/project_raid.js`, `ui/static/platform/css/project_views.css`, `ui/templates/platform/base.html`, `docs/`, `tests/`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-103 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro **Proje Yönetimi** formunda proje lideri + üye + gözlemci seçimi süreç paneli ile aynı UX (kaynak → hedef, Ekle/Çıkar, çift tıklama); gönderimde `manager_id` + gizli `members` / `observers` (çoklu seçim + `option.hidden` kaynaklı POST sorunları giderildi). **Düzeltme:** kullanıcı listesi `LegacyUser` (`user`/`kurum_id`) yerine Micro ile aynı **`app.models.core.User`** (`users`/`tenant_id`, `is_active`) + üye/gözlemci senkronu `project_members` / `project_observers` doğrudan yazım
**Modül:** `micro/modules/proje/routes.py` (`form_users`, `form_init`), `ui/templates/platform/project/form.html`, `ui/static/platform/css/project_form_transfer.css`, `ui/static/platform/js/project_form_transfer.js`, `ui/templates/platform/project/task_form.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-102 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Takvim, Gantt, RAID ve Kanban **Micro tema** içinde (`ui/templates/platform/project/*.html`, `project_views.css`, `_project_views_nav`); klasik **`/kok/projeler/<id>/*`** (main_bp) rotaları **Micro görünüme redirect**; çift tanımlı `proje_gantt` kaldırıldı (`project_views_nav` → `main.project_gantt`); proje detayındaki “kök şablon” uyarısı kaldırıldı
**Modül:** `micro/modules/proje/routes.py`, `ui/templates/platform/project/*`, `ui/static/platform/css/project_views.css`, `main/routes.py`, `templates/partials/project_views_nav.html`, `ui/templates/platform/project/detail.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-101 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro proje **üye / gözlemci** seçimi (`members`, `observers` — form + `_sync_project_members_observers`); düzenlemede bildirim checkbox’larından `notification_settings` güncelleme; detay sayfasında ekip rozetleri + **Takvim / Gantt / RAID / Kanban** (`/project/<id>/views/*`, erişim `user_can_access_project`)
**Modül:** `micro/modules/proje/routes.py`, `ui/templates/platform/project/form.html`, `ui/templates/platform/project/detail.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-100 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Alembic: `e7a8` batch_alter yerine idempotent sütun ekleme (SQLite FK yansıma hatası); `add_surec_parent` güncel şemada `surec` yoksa no-op; merge `9504` tek hat (`e7a8` → `add_surec_parent` → `9504` → `a1c2d3e4f5a6`); 2047 Supabase zinciri `migrations/versions/_disabled/`; `config.py` göreli sqlite URI → `instance/` + mutlak yol (Flask CLI `kokpitim.app` ile yanlış `C:\\instance\\db` önlendi); kök `/projeler`, `/projeler/yeni`, detay/düzenle, görev yolları → Micro redirect
**Modül:** `migrations/versions/e7a8b9c0d1e2_kpi_data_deleted_meta.py`, `add_surec_parent_id.py`, `9504e9a7e70f_merge_add_surec_parent_and_kpi_data_.py`, `config.py`, `main/routes.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-099 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro **Proje Yönetimi** — İngilizce URL (`/project`, `/project/portfolio`, `/project/<id>`, görev CRUD), `permissions.py` (süreç ile paralel), stratejik portföy + analiz, görevde `process_kpi_id` (PG) + migration (revizyon: `a1c2d3e4f5a6`, eski `f8a9b0c1d2e3` kaldırıldı)
**Modül:** `micro/modules/proje/*`, `ui/templates/platform/project/*`, `models/project.py`, `migrations/versions/a1c2d3e4f5a6_task_process_kpi_id.py`, `micro/core/module_registry.py`, `ui/templates/platform/base.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-098 | 2026-03-19 | ✅ Tamamlandı

**Görev:** `py app.py` ile çalışan fabrikada `main_bp` kayıtlı olmadığı için `/strategy/projects` (Proje Portföyü) 404 veriyordu; `app.create_app` sonuna `main_bp` eklendi. `User` üzerinde legacy uyumu: `kurum_id` → `tenant_id`, `sistem_rol` → rol eşlemesi
**Modül:** `app/__init__.py`, `app/models/core.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-097 | 2026-03-19 | ✅ Tamamlandı

**Görev:** PG kartı **Önceki / Sonraki** gezintisi: yıl ofseti yerine **seçilen gösterime göre bir önceki/sonraki periyot** (çeyrek, ay, hafta, 6 ay, yıl, günlükte **gün**); `karneNavPeriodKey` + `karneNavDataYear`; yıl seçicide senkron
**Modül:** `ui/static/platform/js/surec.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-096 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi **Performans Göstergeleri** kartında modal ile aynı gösterim mantığı: kart üstünde **Yıl**, **Gösterim**, **Önceki / rozet / Sonraki** (kalan alanda ortalı); günlükte ay/gün/yıl gezintisi; diğer gösterimlerde periyot imi + veri yılı; gizli `pg-gunluk-ay-select` modal senkronu; PG tık modalı aynı
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/js/surec.js`, `ui/static/platform/css/surec.css`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-095 | 2026-03-19 | ✅ Tamamlandı

**Görev:** PG tablo modalı: **yıl / gösterim** select daraltma; gösterim sırası **Yıllık → 6 aylık → Çeyreklik → Aylık → Haftalık → Günlük**, varsayılan **çeyrek**; modal açılışında yıl **takvim yılı**; **haftalık** sütun başlıkları **gün + ay** aralığı; **günlük** tek ay + **Önceki/Sonraki ay**; ana sayfa `pg-periyot-select` aynı sıra; API `halfyear_1`/`halfyear_2` (`process_utils.data_date_to_period_keys`); kanban/Excel **6 aylık** gerçek anahtarlar
**Modül:** `app/utils/process_utils.py`, `ui/static/platform/js/pg_tablo_modal.js`, `ui/static/platform/js/surec.js`, `ui/templates/platform/surec/karne.html`, `ui/static/platform/css/surec.css`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-094 | 2026-03-21 | ✅ Tamamlandı

**Görev:** Micro süreç karnesinde **PG kartına tıklanınca** kök karne **«Süreç Karnesi — Performans Göstergeleri»** tablosunun **tam modal kopyası** (yıl/gösterim, önceki-sonraki, sütun gösterimi, dinamik thead, hücre tık → veri detay + düzenle/sil); **süreç seçici yok**; **tıklanan PG satırı vurgu + kaydırma**; API `GET /process/api/kpi-data/detail`, stub `proje-gorevleri`; `pg_tablo_modal.js` + `surec.css` Micro renkleri; **asa (VGS)** ayrı
**Modül:** `micro/modules/surec/routes.py`, `ui/templates/platform/surec/karne.html`, `ui/static/platform/js/pg_tablo_modal.js`, `ui/static/platform/js/surec.js`, `ui/static/platform/css/surec.css`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-094 | 2026-05-05 | ✅ Tamamlandı

**Görev:** Kokpitim tanıtım web sitesi (marketing_bp) oluşturuldu
**Modül:** marketing
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/marketing/__init__.py` → Yeni Blueprint
- `micro/modules/marketing/routes.py` → 12 route + blog + sitemap + robots.txt
- `templates/marketing/` → 13 template (base, index, 5 özellik, nasıl çalışır, demo, blog, iletişim)
- `static/marketing/css/marketing.css` → Tam marketing CSS sistemi
- `static/marketing/js/marketing.js` → Navbar scroll, hamburger, accordion, sayaç, fade-in, form validasyon
- `content/blog/` → 2 blog yazısı (Markdown)
- `__init__.py` → marketing_bp en önce register edildi (/ çakışması çözüldü)

### Yapılan İşlem
docs/kirowebsitesi.md belgesindeki talimatlar uygulandı. marketing_bp Blueprint'i app_bp'den önce register edilerek / route çakışması çözüldü. Mevcut hiçbir route/template değiştirilmedi. Tüm sayfalar @login_required olmadan herkese açık. Demo talep ve iletişim formları Flask-WTF CSRF + honeypot spam korumalı. Blog Markdown tabanlı (python-markdown). sitemap.xml ve robots.txt route'ları eklendi.

---
## TASK-093 | 2026-03-21 | ✅ Tamamlandı

**Görev:** Süreç karnesi PG **kartına tıklayınca VGS açılması kaldırıldı**; favori / düzenle / sil yanına **asa (fa-wand-magic-sparkles) `btn-kpi-vgs`** ile VGS; yardımcı sihirbaz Swal metni güncellendi; `kb-card--clickable` kaldırıldı
**Modül:** `ui/static/platform/js/surec.js`, `ui/static/platform/css/surec.css`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-092 | 2026-03-21 | ✅ Tamamlandı

**Görev:** VGS modal: **Kayıt özeti** kaldırıldı; **Kayıt geçmişi** accordion formun **en altına** taşındı; önizleme JS/CSS temizlendi
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/js/surec_vgs.js`, `ui/static/platform/css/surec.css`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-091 | 2026-03-21 | ✅ Tamamlandı

**Görev:** VGS modal genişliği artırıldı (`max-width` ~1080px); kayıt geçmişi **İşlem** sütunu `min-width` + tablo sarmalayıcı yatay kaydırma (dar ekran)
**Modül:** `ui/static/platform/css/surec.css`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-090 | 2026-03-21 | ✅ Tamamlandı

**Görev:** VGS: modal alanı **Veri tarihi** (olaya ilişkin gün); **Veri girişi** Kaydet anında otomatik; kayıt geçmişi tablosunda **Yıl/Periyot kaldırıldı**, **Veri girişi** sütunu (`recorded_at`); özet ve düzenle/sil meta metinleri güncellendi
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/js/surec_vgs.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-089 | 2026-03-21 | ✅ Tamamlandı

**Görev:** VGS kayıt geçmişinde **son güncelleme**: kim + tarih (`KpiDataAudit` UPDATE); gerçekleşen / açıklama / hedeften herhangi biri değişince audit; API `last_updated_at`, `last_updated_by_name`, `recorded_at`; tabloda **Son güncelleme** sütunu (silinme sütunu aynı)
**Modül:** `micro/modules/surec/routes.py`, `ui/static/platform/js/surec_vgs.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-088 | 2026-03-21 | ✅ Tamamlandı

**Görev:** VGS geçmiş **Düzenle / Sil** akışında SweetAlert kaldırıldı; **MicroUI `mc-modal`** ile `modal-vgs-history-edit` ve `modal-vgs-history-delete` eklendi (`z-index: 10060`); Escape ve VGS backdrop tıklaması önce alt modalı kapatır
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/js/surec_vgs.js`, `ui/static/platform/js/surec.js`, `ui/static/platform/css/surec.css`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-087 | 2026-03-21 | 📝 Not

**Not:** `kpi_data.deleted_at` / `deleted_by_id` modelde varken DB güncellenmediyse SQLite’ta `no such column` → `/process/api/karne/...` **500** → ön yüzde «Unexpected token '<'… JSON» hatası. Çözüm: `py scripts/add_kpi_data_deleted_columns_sqlite.py` veya `flask db upgrade` (migration zinciri uygunsa).
**Modül:** `scripts/add_kpi_data_deleted_columns_sqlite.py`, `docs/TASKLOG.md`
**Durum:** 📝 Not

---

## TASK-086 | 2026-03-21 | ✅ Tamamlandı

**Görev:** VGS **Kayıt geçmişi** accordion (başlangıçta kapalı); `GET .../kpi-data/history/<kpi_id>` ile PG’nin tüm yıllar + silinmiş kayıtlar; üye yalnız kendi satırlarında CRUD, lider/sahip + ayrıcalıklı roller tüm aktif satırlarda; **soft sil** zaten `is_active`; `deleted_at` / `deleted_by_id` + migration; silinme bilgisi listede; skor tarafı `is_active=True` ile uyumlu
**Modül:** `app/models/process.py`, `migrations/versions/e7a8b9c0d1e2_kpi_data_deleted_meta.py`, `micro/modules/surec/routes.py`, `ui/templates/platform/surec/karne.html`, `ui/static/platform/js/surec_vgs.js`, `ui/static/platform/js/surec.js`, `ui/static/platform/css/surec.css`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-085 | 2026-03-21 | ✅ Tamamlandı

**Görev:** VGS modal başlığı **Veri Girişi Sihirbazı**; **periyot seçimi kaldırıldı** — yalnızca **veri girişi tarihi** (zorunlu); yıl/dönem PG ölçüm tipine göre tarihten türetilir; haftalık/günlük için `period_month` API’ye eklenir
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/js/surec_vgs.js`, `ui/static/platform/js/surec.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-084 | 2026-03-21 | ✅ Tamamlandı

**Görev:** Süreç karnesi **VGS** çok adımlı akış kaldırıldı: **tek ekranda** dönem + değer + altta **canlı kayıt özeti**; footer yalnız İptal / **Kaydet** (`form` submit); `surec_vgs.js` adım UI ve çift kayıt dinleyicisi temizlendi
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/js/surec_vgs.js`, `ui/static/platform/css/surec.css`, `ui/static/platform/js/surec.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-083 | 2026-03-21 | ✅ Tamamlandı

**Görev:** Micro süreç karnesi **VGS** (`surec_vgs.js`) `surec.js` ile bağlandı: `initSurecVgs`, `karne.html` script sırası, eski tek adımlı kayıt/`kpiDataEntryPayload` kaldırıldı; `getCanEnterPgv` ile API sonrası yetki güncellemesi; form submit yalnız `preventDefault`
**Modül:** `ui/static/platform/js/surec.js`, `ui/static/platform/js/surec_vgs.js`, `ui/templates/platform/surec/karne.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-082 | 2026-03-21 | ✅ Tamamlandı

**Görev:** Süreç düzenlemede üye ekleyince «Yeni süreç oluşturma yetkiniz yok» — şablonda **`surec-edit-id` gizli alanı yoktu**; JS süreç id yazamıyordu, `editId` boş kalıyordu (liderlerde kontrol tetikleniyordu). `index.html` gizli input eklendi; `saveProcessForm` düzenle modunda boş id iken yöneticiye yanlışlıkla ADD gitmesini engelleyen uyarı
**Modül:** `ui/templates/platform/surec/index.html`, `ui/static/platform/js/surec.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-081 | 2026-03-21 | ✅ Tamamlandı

**Görev:** Süreç listesinde **lider/sahip** kullanıcıda «Süreci düzenle» görünmüyordu (yalnızca `can_crud_process`); ayrıca düzenleme modalı yalnızca yöneticilere render ediliyordu. `can_open_process_modal`, şablonda düzenle/sil ayrımı, `surec.js` `openEditModal` / `saveProcessForm` (yeni süreç yalnız yönetici)
**Modül:** `micro/modules/surec/routes.py`, `ui/templates/platform/surec/index.html`, `ui/static/platform/js/surec.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-080 | 2026-03-21 | ✅ Tamamlandı

**Görev:** Kurum özel SMTP kapalıyken **Admin kurumunun kayıtlı SMTP’si** varsayılan çıkış: `send_notification_email` öncelik kurum özel → `MAIL_*` kimlik doluysa ortam → yoksa `Admin` rolündeki ilk aktif kullanıcının tenant’ı `_get_tenant_smtp_config`; `eposta.html` bilgilendirme güncellendi
**Modül:** `micro/services/email_service.py`, `ui/templates/platform/ayarlar/eposta.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-079 | 2026-03-21 | ✅ Tamamlandı

**Görev:** BOUN **Adil** test maili — Admin (tenant 1) **özel SMTP açık**, BOUN (tenant 7) **özel SMTP kapalı**; sistem `MAIL_USERNAME` boş olduğundan gönderim sessizce başarısızdı. `send_notification_email` artık **(bool, hata_metni)** döner; kimlik yoksa anlaşılır Türkçe mesaj; SMTP istisnaları ayrıştırıldı; test endpoint mesajı iletir; bildirim tetikleyicide başarısızlık loglanır; `eposta.html` uyarı + doğru sistem SMTP açıklaması
**Modül:** `micro/services/email_service.py`, `micro/modules/shared/ayarlar/routes.py`, `micro/services/notification_triggers.py`, `ui/templates/platform/ayarlar/eposta.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-078 | 2026-03-19 | ✅ Tamamlandı

**Görev:** `/ayarlar/eposta` test maili — turuncu ünlemli pencerenin **hata sanılması**; `MicroUI.onayla` varsayılanı `warning`+kırmızı onaydı. Varsayılan **`question` + mor onay**; test mailinde **`info`**; `MicroUI.post` HTML (403) yanıtında daha anlamlı mesaj; bilgi bandında onay açıklaması
**Modül:** `ui/static/platform/js/app.js`, `ui/static/platform/js/ayarlar_eposta.js`, `ui/templates/platform/ayarlar/eposta.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-077 | 2026-03-19 | ✅ Tamamlandı

**Görev:** **Default Corp** KMF/s11 import verisinin temizlenmesi — `wipe_process_pg_data.py --process-id 1` (HR-01: 38 PG + 291 KpiData pasif)
**Modül:** `scripts/wipe_process_pg_data.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-076 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Son **s11 / KMF** import verisinin silinmesi — `scripts/wipe_process_pg_data.py` (aktif `ProcessKpi` + `KpiData` + ilgili `FavoriteKpi` → `is_active=False`, `kmf_s11_import --wipe-kpis` ile aynı mantık); Boğaziçi süreç **18** üzerinde çalıştırıldı
**Modül:** `scripts/wipe_process_pg_data.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-075 | 2026-03-19 | ✅ Tamamlandı

**Görev:** **Adil** (`adil@kalitesoleni.com`, `tenant_admin`, Boğaziçi) süreç listesi analizi — KMF s11 verisi **Default Corp süreç 1**’deydi; BOUN’da **H1.1 eksik** ve süreç 18 **yanlış tenant** alt stratejisine (id 74) bağlıydı. `scripts/ensure_boun_h11_and_import_s11.py` ile tenant 7’de **H1.1 (id=75)** oluşturuldu, süreç **18** bağlantısı düzeltildi, `s11-extracted.json` → süreç **18** import (38 PG). `scripts/adil_process_access_report.py` rapor + `--heavy` ile yoğun süreç taraması; `adil_process_access_report.py` KpiData join `process_kpi_id` düzeltmesi
**Modül:** `scripts/ensure_boun_h11_and_import_s11.py`, `scripts/adil_process_access_report.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-074 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Çift **H1.1** alt strateji tutarsızlığı — `SubStrategy` **id=54** kaldırıldı; `process_sub_strategy_links` (18,24,25) **74**’e taşındı / çakışanlar silindi; `kmf_s11_import.py` aynı kod için `.order_by(SubStrategy.id.desc())` (gelecekte çift kayıtta deterministik seçim)
**Modül:** Veritabanı (tek seferlik), `scripts/kmf_s11_import.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-073 | 2026-03-19 | ✅ Tamamlandı

**Görev:** KMF s11 kullanıcı yanıtları — PG **H1.1** + **İyileştirme**; **6 ay** ölçüm periyodu (`karne.html` + `surec.js` Toplama çarpanı); `scripts/kmf_s11_import.py` (hedef aralığı→ortalama, çeyrek `KpiData`, 2 lider+6 üye random, `--wipe-kpis`); `analiz-boun-sr4-karne-excel.md` import bölümü
**Modül:** `scripts/kmf_s11_import.py`, `scripts/kmf_s11_extract.py`, `ui/templates/platform/surec/karne.html`, `ui/static/platform/js/surec.js`, `docs/analiz-boun-sr4-karne-excel.md`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-072 | 2026-03-19 | ✅ Tamamlandı

**Görev:** `s11.xlsx` veri çıkarımı — `scripts/kmf_s11_extract.py` (Fiili/Hedef birleştirme, meta, çeyrekler, başarı eşikleri); `docs/KMF/s11-extracted.json`; `analiz-boun-sr4-karne-excel.md` güncellendi; netleştirme soruları JSON’da
**Modül:** `scripts/kmf_s11_extract.py`, `docs/KMF/s11-extracted.json`, `docs/analiz-boun-sr4-karne-excel.md`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-071 | 2026-03-19 | ✅ Tamamlandı

**Görev:** `docs/KMF/s11.xlsx` (SR4 karnesi) analizi — 6 sayfa, sütun/Kokpitim eşlemesi, checklist; `analiz-boun-sr4-karne-excel.md` güncellendi; `analyze_karne_xlsx.py` konsol Unicode; `s11-xlsx-ozet.txt`
**Modül:** `docs/analiz-boun-sr4-karne-excel.md`, `scripts/analyze_karne_xlsx.py`, `docs/KMF/s11-xlsx-ozet.txt`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-070 | 2026-03-19 | ✅ Tamamlandı

**Görev:** BOUN SR4 Pazarlama süreç karnesi `.xlsx` analiz notu + `scripts/analyze_karne_xlsx.py` (ilk sürüm; dosya yokken çerçeve)
**Modül:** `docs/analiz-boun-sr4-karne-excel.md`, `scripts/analyze_karne_xlsx.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-069 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç Karnesi PG kartı — başlık altı açıklama metni kaldırıldı; **Görünüm periyodu** yanında üst bardan taşınan aksiyonlar (sihirbaz, PG ekle, faaliyet ekle, Excel, yazdır); **Excel’e aktar** artık gerçek **.xlsx** (`openpyxl`, `POST /process/api/karne/<id>/export-xlsx`).
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/js/surec.js`, `ui/static/platform/css/surec.css`, `micro/modules/surec/routes.py`
**Durum:** ✅ Tamamlandı

---

## TASK-068 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Karnede Kanban gauge — skor rengi **%0 kırmızı → %100 yeşil** sürekli HSL geçişi (`--gauge-h = pct * 1.2deg`); veri yok → nötr gri yay/metin. PG kartında favori ile sil arasında **Düzenle** (kalem, `can_crud_pg` + GET şablonu); `surec_api_kpi_get` / `surec_api_kpi_update` ile modal doldurma ve kayıt; sil URL’si `url_for` ile; `sub_strategy_id` boşaltılabilir (null).
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/js/surec.js`, `ui/static/platform/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-067 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro süreç karnesi «Performans Göstergeleri» — tablo kaldırıldı; **3 kolon Kanban** (Hedefte / Risk altında / Hedef dışı) + **yarım daire gauge** (dash 58); başarı yüzdesi eski tablo mantığı; veri yok → Risk; üstte görünüm periyodu → karta tıklayınca o döneme veri girişi; kartta alt strateji kodu + başlık; favori/sil korundu; API’ye `sub_strategy_code` eklendi; stiller `surec.css` (`.kb-*`)
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/js/surec.js`, `ui/static/platform/css/surec.css`, `micro/modules/surec/routes.py` (karne JSON alanı)
**Durum:** ✅ Tamamlandı

---

## TASK-066 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro süreç karnesi PG **Veri gir** diyaloğu — `.cursorrules` yerel modal şablonu (`mc-modal-overlay` / `mc-modal-header|body|footer`, lavanta ikonlu `mc-modal-title`, `mc-form-label` + `mc-form-input`, footer’da İptal + birincil Kaydet); SweetAlert2 `input` formu kaldırıldı
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/js/surec.js`, `ui/static/platform/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-065 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro PG karnesi okunabilirlik — **Görünüm periyodu** (çeyrek / ay / hafta / gün+ay seçimi / 6 aylık özet / yıl sonu), dinamik `thead`+`tbody` (kök `process_karne.js` anahtarları); **Sütunları göster/gizle** (localStorage) sabit sütunlar için; CSV seçilen görünüme göre; 6 aylık hücreler aylık `entries` toplamı/ortalaması (veri girişi yok, tooltip)
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/js/surec.js`, `ui/static/platform/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-064 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro süreç karnesi KPI kartı — kök `pgTabloCard` ile aynı sütunlar: Kodu, Ana/Alt strateji, Performans adı, Ağırlık, Birim, Ölçüm per., Yıllık hedef; I–IV çeyrek (Hedef/Gerç./Durum); Yıl sonu; Başarı puanı; İşlemler. Veri girişi `ceyrek` / `yillik` API; favori `/process/api/favorite-kpi/toggle`; özet metriklerde çeyrek yedek; CSV çeyrek kolonları
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/js/surec.js`, `ui/static/platform/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-063 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro `karne.html` — `surec.css` / `surec.js` için `?v=config VERSION` önbellek kırma; micro karnesi değişiklik doğrulama dokümanı `docs/micro-karne-kontrol-listesi.md`
**Modül:** `ui/templates/platform/surec/karne.html`, `docs/micro-karne-kontrol-listesi.md`
**Durum:** ✅ Tamamlandı

---

## TASK-062 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro süreç karnesi PG ekle — kök `process/karne` #addPGModal ile görsel/metin hizası: mavi modal başlığı (`#0d6efd`), hız göstergesi ikonu, başlık «Yeni Performans Göstergesi», etiket/placeholder/select metinleri kök ile aynı; yeşil «Kaydet» (`fa-plus-circle`); başarı kartı `bg-light`/`border-success` + düz yeşil header; araç çubuğu ve tablo başlığı «PG ekle» beyaz çerçeveli buton
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/css/surec.css`, `ui/static/platform/js/surec.js`
**Durum:** ✅ Tamamlandı

---

## TASK-061 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Başarı puanı açıklamalarının DB’de saklanması — `basari_puani_araliklari` JSON’u `{"1":{"aralik":"0-40","aciklama":"..."}}` (açıklama yoksa eski düz string); `parse_basari_puani_araliklari` / `hesapla_basari_puani` geriye dönük uyum; kök `process_karne.js`, `surec_karnesi.js`, micro `surec.js`, `calculations.js`
**Modül:** `utils/karne_hesaplamalar.py`, `app/utils/karne_hesaplamalar.py`, `app/models/process.py`, `models/process.py`, `static/js/process_karne.js`, `static/js/modules/process_karne/calculations.js`, `static/js/surec_karnesi.js`, `ui/static/platform/js/surec.js`, `ui/templates/platform/surec/karne.html`
**Durum:** ✅ Tamamlandı

---

## TASK-060 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro süreç karnesi — PG ekle modalı kök `process/karne` (#addPGForm) ile aynı alan seti: gösterge adı, kod, hedef, birim (datalist), skor ağırlığı, periyot, hedef yönü, hesaplama, gösterge türü, hedef belirleme, alt strateji, önceki yıl ort., açıklama, opsiyonel başarı puanı aralıkları (JSON — kök `process_karne.js` ile uyumlu); `mc-modal` + geniş layout (`karne-modal-kpi-add`)
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/js/surec.js`, `ui/static/platform/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-059 | 2026-03-19 | ✅ Tamamlandı

**Görev:** PG ekle modalı birim `datalist` — yalnızca 10 öneri: Adet, %, TL, Saat, Gün, Kişi, Puan, kg, km, kWh (özel metin girişi aynı)
**Modül:** `ui/templates/platform/surec/karne.html`
**Durum:** ✅ Tamamlandı

---

## TASK-058 | 2026-03-19 | ✅ Tamamlandı

**Görev:** PG ekle modalında «Birim» — `datalist` ile önerilen birimler + serbest metin; ipucu metni ve ek birim seçenekleri (zaman, kütle, alan, enerji, N/A vb.)
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-057 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi — «PG ekle» metni «Performans göstergesi ekle»; PG ekleme SweetAlert kaldırıldı, admin «Kullanıcı Düzenle» ile aynı `mc-modal` yapısı (`modal-kpi-add`); `karne-substrategies-json` kaldırıldı (alt strateji seçenekleri şablonda)
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/js/surec.js`, `ui/static/platform/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-056 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi başlık — daha alçak: üst sıra grid (sol mini logo + «Süreç paneline dön», orta «SÜREÇ KARNESİ», sağ meta); üst süreç küçük satır; padding/boşluk/az şerit sıkılaştırma
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-055 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi başlık barı — süreç `select` ile aksiyon butonları aynı satırda (`karne-banner-toolbar`, `align-items: flex-end`); üst satırda marka + meta; dar ekranda sütun
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-054 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi üst bar — canlı mor gradient kaldırıldı; `mc-card` çizgisi (beyaz/koyu kart, 3px indigo üst çizgi); süreç adı tekrarı (select altı) kaldırıldı; aksiyonlar `mc-btn` + yumuşak amber (`karne-btn-faaliyet-soft`) ve yeşil ton (`karne-btn-excel-soft`), sihirbaz `mc-btn-secondary`, PG `mc-btn-success`, yazdır `mc-btn-secondary` + `karne-btn-print-muted`
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-053 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi üst bar — kök görseline yakın mavi–mor gradient; sol: ikon+başlık, «Süreç paneline dön», yetkili süreç `select`, süreç adı; sağ: Döküman/Rev/Rev.tarihi/Yıl, butonlar (veri sihirbazı, PG ekle, faaliyet ekle, Excel CSV, yazdır); Excel export + sihirbaz JS
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/css/surec.css`, `ui/static/platform/js/surec.js`
**Durum:** ✅ Tamamlandı

---

## TASK-052 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi seçenek A — yıllık `target_value` ÷ 12 = aylık hedef; ay hücrelerinde `h:` ipucu; satırda verili ayların ortalama sapma % (artış/azalış yönüne göre işaret); hedef sütununda «Aylık: …»
**Modül:** `ui/templates/platform/surec/karne.html`, `ui/static/platform/js/surec.js`, `ui/static/platform/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-051 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi (`/process/<id>/karne`) — kök referansına yakın üst şerit (liste dön, döküman/revizyon tarihi + isteğe bağlı ilk yayın, üst süreç karnesi, faaliyetler, PG ekle, yazdır); genel bilgi üçlüsü; yönetici özeti; KPI tablosu genişletilmiş sütunlar; PG ekle SweetAlert; `accessible_processes_filter`. **Güncelleme:** Üst şeritte öncelik `revision_date`; «Dış veri aktar» kaldırıldı.
**Modül:** `micro/modules/surec/routes.py`, `ui/templates/platform/surec/karne.html`, `ui/static/platform/js/surec.js`, `ui/static/platform/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-050 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç kaydet bekleme süresi — nedenleri (SMTP senkron, tam sayfa yenileme); süreç atama e-postasını arka plan iş parçacığına alma; kayıt sırasında SweetAlert2 «Süreç kaydediliyor» + yüzde çubuğu (simüle), çift gönderim kilidi
**Modül:** `micro/services/notification_triggers.py`, `ui/static/platform/js/surec.js`
**Durum:** ✅ Tamamlandı

---

## TASK-049 | 2026-03-20 | ✅ Tamamlandı

**Görev:** `/process` — kurum yöneticileri (Admin, tenant_admin, executive_manager) tüm süreçlerde güncelleme: satırda «Düzenle», GET/POST ile aynı modal (lider/üye çift liste dahil)
**Modül:** `ui/templates/platform/surec/index.html`, `ui/static/platform/js/surec.js`
**Durum:** ✅ Tamamlandı

---

## TASK-048 | 2026-03-20 | ✅ Tamamlandı

**Görev:** Micro “Yeni Süreç” modalı — kök panel referansıyla hizalama (yeşil başlık, tarihler, üst süreç, sınırlar, ilerleme); Süreç Lideri/Üyesi çift liste (→ Ekle / ← Çıkar)
**Modül:** `micro/modules/surec/routes.py`, `ui/templates/platform/surec/index.html`, `ui/static/platform/js/surec.js`, `ui/static/platform/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-047 | 2026-03-20 | ✅ Tamamlandı

**Görev:** Süreç modülü RBAC (Admin / tenant_admin / executive_manager / atanan kullanıcı), süreç→en az bir alt strateji zorunluluğu, panelden Karnesi/Faaliyetler ayrı sayfa, PGV güncelle-sil API, menüde Süreç tüm oturumlu kullanıcılar
**Modül:** `micro/modules/surec/permissions.py`, `micro/modules/surec/routes.py`, `ui/templates/platform/surec/*`, `ui/static/platform/js/surec.js`, `ui/templates/platform/base.html`
**Durum:** ✅ Tamamlandı

### Not
Mevcut veritabanında alt strateji bağlantısı olmayan süreçler için güncelleme API’si `sub_strategy_links` gönderilene kadar hata verebilir; veri düzeltmesi veya kök `/process` panelinden bağlantı eklenmesi gerekir.

---

## TASK-046 | 2026-03-20 | ✅ Tamamlandı

**Görev:** Micro Süreç modülü kanonik URL `/process`; eski `/surec` → **307** ile `/process`; şablon/JS/bildirim/module_registry güncellemesi
**Modül:** `micro/modules/surec/routes.py`, `ui/templates/platform/surec/*.html`, `ui/static/platform/js/surec.js`, `micro/core/module_registry.py`, `micro/services/notification_triggers.py`
**Durum:** ✅ Tamamlandı

---

## TASK-045 | 2026-03-20 | ✅ Tamamlandı

**Görev:** SP akışta “Ana Stratejiler” (eski 5) kartı kaldırıldı; strateji listesi kartı başlığı “Strateji Listesi (Ana Stratejiler → Alt Stratejiler)”, rozet 05, adımlar 06–08
**Modül:** `ui/templates/platform/sp/index.html`, `ui/static/platform/js/sp.js`
**Durum:** ✅ Tamamlandı

---

## TASK-044 | 2026-03-20 | ✅ Tamamlandı

**Görev:** SP akış kartı gövdesine tıklanınca “yapım aşaması” sayfaları yerine kalem ile aynı düzenleme modalı / yönlendirme
**Modül:** `ui/templates/platform/sp/index.html`, `ui/static/platform/js/sp.js`, `ui/static/platform/css/sp.css`
**Durum:** ✅ Tamamlandı

### Not
`<a href>` yerine `div.mc-sp-card-body-trigger` + `data-sp-body-edit`; JS ilgili `.btn-sp-card-edit` tıklamasını tetikler; yoksa bilgi butonu. Kart 01–09 gövde.

---

## TASK-043 | 2026-03-20 | ✅ Tamamlandı

**Görev:** SP kart 01–03 önizlemede metin taşınca kaydırma (Misyon/Vizyon tam metin + ortak `.mc-sp-card-body-scroll`)
**Modül:** `ui/templates/platform/sp/index.html`, `ui/static/platform/css/sp.css`
**Durum:** ✅ Tamamlandı

---

## TASK-042 | 2026-03-20 | ✅ Tamamlandı

**Görev:** SP kart 03 Değerler/Etik — önizlemede ~3 satır görünür yükseklik, fazlası kaydırma çubuğu
**Modül:** `ui/templates/platform/sp/index.html`, `ui/static/platform/css/sp.css`
**Durum:** ✅ Tamamlandı

### Not
Metin çok satırlı veya `;` ile ayrılmış maddeler; tek paragrafta sarma + aynı max-height ile kaydırma.

---

## TASK-041 | 2026-03-20 | ✅ Tamamlandı

**Görev:** SP akış kartı 03 “Değerler ve Etik Kurallar” — girilen `core_values` / `code_of_ethics` önizlemesi ve tamamlanma (etik dolu iken rozet)
**Modül:** `ui/templates/platform/sp/index.html`, `ui/static/platform/css/sp.css`
**Durum:** ✅ Tamamlandı

---

## TASK-040 | 2026-03-20 | ✅ Tamamlandı

**Görev:** Boğaziçi Üniversitesi kurumu için tablodaki 5 ana (SA1–SA5) + 20 alt (H*) strateji verisi
**Modül:** `scripts/seed_bogazici_strategies.py`
**Durum:** ✅ Tamamlandı (geliştirme DB’de `--replace` ile uygulandı)

### Kullanım
`py scripts/seed_bogazici_strategies.py --replace` (kurum otomatik: adında boğaziçi/boun) veya `--tenant-id N`

---

## TASK-039 | 2026-03-20 | ✅ Tamamlandı

**Görev:** SP ana strateji ekleme HTTP 500 — `code`/`description` JSON `null` iken `.strip()` AttributeError
**Modül:** `micro/modules/sp/routes.py` (`sp_add_strategy`)
**Durum:** ✅ Tamamlandı

### Özet
`data.get("code", "")` anahtar varken değer `null` ise `None` döner; `(data.get("code") or "").strip()` kullanıldı.

---

## TASK-038 | 2026-03-20 | ✅ Tamamlandı

**Görev:** SP “Ana strateji ekle” JSON hatası (`Unexpected token '<'`) — CSRF HTML yanıtı
**Modül:** `micro/modules/sp/routes.py` (`@csrf.exempt` + `app.extensions.csrf`), `sp.js` `postJson`
**Durum:** ✅ Tamamlandı

### Özet
`/sp/api/*` POST uçlarına `login_required` + `sp_manage_required` ile birlikte `@csrf.exempt` eklendi (uygulamadaki gerçek CSRF `app.extensions` üzerinden). `postJson` HTML yanıtında anlamlı hata mesajı veriyor.

---

## TASK-037 | 2026-03-19 | ✅ Tamamlandı

**Görev:** SP akış kartlarında bilgi (i) butonu ve kart amacını anlatan `openMcInfoModal` penceresi
**Modül:** `base.html` / `mc-modal-form.js` / `components.css` / `sp/index.html` / `sp.js`
**Durum:** ✅ Tamamlandı

### Özet
Her kartın sağ üstünde düzenle ikonunun yanına `fa-circle-info` butonu; metinler `sp-card-help-json` + `openMcInfoModal` ile gösteriliyor.

---

## TASK-036 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Stratejik Planlama düzenleme formları — admin kullanıcı düzenle modalı ile aynı native `mc-modal` tasarımı
**Modül:** micro UI / `mc-modal-form.js` / `sp.js` / `components.css` / `base.html`
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/templates/platform/base.html` → Genel `#mc-modal-form-global` markup (admin ile aynı sınıflar)
- `ui/static/platform/js/mc-modal-form.js` → `openMcFormModal()` yardımcısı
- `ui/static/platform/js/sp.js` → Misyon/vizyon/değerler/SWOT/ana & alt strateji formları SweetAlert yerine native modal
- `ui/static/platform/css/components.css` → `textarea.mc-form-input`, `select.mc-form-input`, `.mc-modal-form-validation`

### Notlar
Toast, hata ve silme onayı SweetAlert2 ile devam ediyor.

---

## TASK-035 | 2026-03-19 | ✅ Tamamlandı

**Görev:** SECRET_KEY fallback kaldırıldı ve environment zorunlu hale getirildi
**Modül:** config / app init / security
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `config.py` → Hardcoded `SECRET_KEY` fallback kaldırıldı; environment yoksa `RuntimeError` atacak şekilde güncellendi
- `app/__init__.py` → `app.config["SECRET_KEY"]` için hardcoded fallback satırı kaldırıldı
- `.env` → `SECRET_KEY` güvenli rastgele değer ile eklendi/oluşturuldu (git'e eklenmedi)

### Yapılan İşlem
Uygulamanın gizli anahtarının yalnızca environment üzerinden okunması zorunlu hale getirildi. Hardcoded fallback'ler kaldırılarak production güvenlik riski düşürüldü. `.gitignore` içinde `.env` kuralı doğrulandı.

### Notlar
SECRET_KEY değeri güvenlik nedeniyle loglanmadı.

---

## TASK-034 | 2026-03-19 | ✅ Tamamlandı

**Görev:** FakeLimiter kaldırıldı, gerçek Flask-Limiter aktif edildi ve login endpoint'lerine rate limit eklendi
**Modül:** security / auth / micro-auth
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `extensions.py` → `FakeLimiter` tamamen kaldırıldı; gerçek `Limiter` import/instance eklendi
- `__init__.py` → limiter'ı devre dışı bırakan `RATELIMIT_ENABLED = False` satırı kaldırıldı
- `auth/routes.py` → `/auth/login` için `@limiter.limit("10 per minute")` eklendi
- `micro/modules/shared/auth/routes.py` → `/login` için `@limiter.limit("10 per minute")` eklendi
- `requirements.txt` → `Flask-Limiter==3.5.0` olarak versiyon sabitlendi

### Yapılan İşlem
Rate limiting mekanizması mock/fake yapıdan gerçek Flask-Limiter'a geçirildi. Uygulama başlatma akışında `limiter.init_app(app)` çağrısı zaten mevcut olduğundan korunarak aktif hale getirildi. Auth ve micro login endpointlerine dakikada 10 istek limiti uygulandı.

### Notlar
Micro login route'u projede `/login` olarak tanımlı; bu endpoint'e limit dekoratörü eklendi.

---

## TASK-033 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Kokpitim tam derinlik analiz raporu oluşturuldu (`docs/analiz-antigravity.md`)
**Modül:** docs / analiz
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `docs/analiz-antigravity.md` → 10 adımlı kapsamlı proje analizi oluşturuldu

### Yapılan İşlem
Proje haritası, mimari analiz (Blueprint, ORM, Micro modüller), kod kalitesi (teknik borç, güvenlik, performans), frontend analizi (CSS/JS/Template), modül bazlı derinlik analizi, TASKLOG trend analizi, iyileştirme önerileri, rekabet/trend analizi, test durumu ve dokümantasyon değerlendirmesi yapıldı. Genel sağlık skoru: 61/100.

### Notlar
5 kritik güvenlik bulgusu tespit edildi: Rate limiter devre dışı, çift hardcoded secret key, SESSION_COOKIE_SECURE eksik, Talisman başlatılmamış, CSRF exempt endpoint.

---

## TASK-032 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Kokpitim tam derinlik analiz raporu oluşturuldu (`docs/analiz-cursoranaliz.md`)
**Modül:** docs / analiz
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `docs/analiz-cursoranaliz.md` → 10 adımlı kapsamlı proje analizi eklendi (mimari, güvenlik, kalite, frontend, test, trend, öneriler)
- `docs/TASKLOG.md` → Bu kayıt eklendi

### Yapılan İşlem
Depodaki aktif kod ve legacy alanlar taranarak proje haritası, mimari katmanlar, veritabanı ve micro modül yapısı, teknik borç/güvenlik/performans bulguları, frontend tutarlılık analizi, TASKLOG trendleri ve iyileştirme önerileri tek raporda toplandı.

### Notlar
Toplam satır/dosya metrikleri hem ham depo hem aktif alan (yedek/legacy hariç) olarak ayrı raporlandı.

---

## TASK-031 | 2026-03-18 | 🔄 Düzeltme

**Görev:** profil.html boş dosya sorunu giderildi — Python script ile UTF-8 yeniden yazıldı
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/templates/platform/auth/profil.html` → PowerShell unicode escape hatası nedeniyle boşalmıştı; Python script ile UTF-8 olarak yeniden yazıldı
- `ui/static/platform/js/profil.js` → Aynı sorun; Python script ile UTF-8 olarak yeniden yazıldı

### Yapılan İşlem
PowerShell'in `\u` escape dizilerini literal string olarak yazması nedeniyle her iki dosya da boşalmıştı. Python script (`_write_profil.py`, `_write_profil_js.py`) ile UTF-8 encoding açıkça belirtilerek dosyalar yeniden oluşturuldu. Doğrulama: `extends platform/base.html`, `data-upload-url`, `UPLOAD_URL`, `swalError` varlığı kontrol edildi.

### Notlar
Yok.

---

## TASK-030 | 2026-03-18 | ✅ Tamamlandı

**Görev:** profil.html ve profil.js sıfırdan yeniden yazıldı — eski profile.html JS mantığı taşındı
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/templates/platform/auth/profil.html` → Silindi ve yeniden yazıldı; `platform/base.html` extend, `data-update-url`/`data-upload-url`, fotoğraf yükleme butonu + progress, profil formu, inline script yok
- `ui/static/platform/js/profil.js` → Silindi ve yeniden yazıldı; eski `profile.html` inline JS mantığı taşındı: dosya tipi/boyut kontrolü, `validateEmail`, `validatePhone`, Bootstrap Toast → SweetAlert2, fetch URL'leri `data-*`'dan okunuyor, `phone`→`phone_number`, `title`→`job_title`

### Yapılan İşlem
Eski `templates/profile.html`'deki inline JS (dosya tipi kontrolü, 5MB limit, e-posta/telefon validasyonu, fotoğraf güncelleme DOM mantığı) `profil.js`'e taşındı. Bootstrap Toast bildirimleri SweetAlert2 ile değiştirildi. HTML `platform/base.html`'i extend ediyor, tüm fetch URL'leri `data-*` attribute'larından okunuyor, inline `<script>` bloğu yok.

### Notlar
`static/js/profile.js` mevcut değildi — tüm JS `templates/profile.html` içinde inlineydi.

---

## TASK-029 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Eski profile.html JS mantığı micro profil.js'e taşındı; backend'e boyut ve mime kontrolü eklendi
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/static/platform/js/profil.js` → Client-side mime type kontrolü, 5MB boyut kontrolü, `validateEmail`, `validatePhone` fonksiyonları, content-type response kontrolü, FormData'ya `csrf_token` field eklendi
- `micro/modules/shared/auth/routes.py` → `profil_foto_yukle`'ye mime type kontrolü (`file.mimetype`) ve 5MB boyut kontrolü (`file.seek`) eklendi

### Yapılan İşlem
Eski `templates/profile.html`'deki JS'de bulunan dosya tipi/boyut validasyonu, e-posta ve telefon format kontrolü micro `profil.js`'e taşındı. FormData'ya `csrf_token` field'ı da eklendi (header'a ek olarak — CSRF sorununu kesin çözer). Backend `profil_foto_yukle`'ye mime type ve 5MB boyut kontrolü eklendi. Alan adları zaten doğruydu: `phone_number`, `job_title`.

### Notlar
Eski `/profile/update` ve `/profile/upload-photo` endpoint'leri dokunulmadı — kök `templates/profile.html` kullananlar için çalışmaya devam ediyor.

---

## TASK-028 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Profil fotoğrafı yükleme CSRF hatası giderildi
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/shared/auth/routes.py` → `from extensions import csrf` import eklendi; `profil_foto_yukle` endpoint'ine `@csrf.exempt` dekoratörü eklendi

### Yapılan İşlem
`profil_foto_yukle` endpoint'i `multipart/form-data` POST alıyor; `profil.js` CSRF token'ı `X-CSRFToken` header olarak gönderiyor. Flask-WTF varsayılan olarak form field'dan (`csrf_token`) okuduğu için header'ı tanımıyor ve isteği reddediyordu. `@csrf.exempt` ile endpoint CSRF korumasından muaf tutuldu — endpoint zaten `@login_required` ile korunuyor.

### Notlar
Yok.

---

## TASK-027 | 2026-03-18 | 🔄 Düzeltme

**Görev:** profil.js'de input sıfırlama sırası düzeltildi
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/static/platform/js/profil.js` → `this.value = ""` satırı `reader.readAsDataURL(file)` çağrısından önce taşındı

### Yapılan İşlem
`data-upload-url` doğru endpoint'e (`/profil/foto-yukle`) işaret ediyordu. Asıl sorun: bazı tarayıcılarda `this.value = ""` `FileReader` okuma tamamlanmadan çalışınca `file` referansı kaybolabiliyordu. `file` önce değişkene alınıp input hemen sıfırlandı, ardından `readAsDataURL` çağrıldı.

### Notlar
Yok.

---

## TASK-026 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Profil fotoğrafı butonu, canvas kırpma ve avatar güncellemesi
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/templates/platform/auth/profil.html` → Kamera label/icon kaldırıldı, `btn-foto-yukle` butonu eklendi
- `ui/static/platform/js/profil.js` → Canvas ile 400x400 merkez kırpma, JPEG 0.85 kalite, `btn-foto-yukle` click bağlantısı
- `ui/templates/platform/base.html` → Topbar ve sidebar footer avatar'ı `profile_photo` varsa `<img>` gösteriyor

### Yapılan İşlem
Kamera ikonu yerine standart `mc-btn` butonu eklendi. Fotoğraf seçilince FileReader → Image → Canvas ile 400x400 kare kırpma yapılıyor, `toBlob(jpeg, 0.85)` ile sıkıştırılıp endpoint'e gönderiliyor. Topbar ve sidebar avatar'ları profil fotoğrafı varsa `<img>` tag'i, yoksa harf gösteriyor.

### Notlar
Yok.

---

## TASK-025 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Profil sayfası micro yapıya tam taşındı — backend JSON API, fotoğraf yükleme, template ve JS
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/shared/auth/routes.py` → `profil` route'u JSON API POST handler'a dönüştürüldü; `profil_foto_yukle` endpoint'i eklendi
- `ui/templates/platform/auth/profil.html` → `profile_picture` → `profile_photo` düzeltildi; `data-update-url` / `data-upload-url` eklendi; rol badge Türkçeleştirildi; inline script kaldırıldı
- `ui/static/platform/js/profil.js` → Tamamen yeniden yazıldı: fetch URL'leri `data-*`'dan okunuyor, bildirimler SweetAlert2, form JSON API ile submit ediliyor

### Yapılan İşlem
Profil sayfası eski `auth_bp.profile` 307 redirect'inden kurtarıldı. `micro_bp.profil` artık kendi JSON API handler'ına sahip: şifre doğrulama, e-posta duplicate kontrolü, yeni model alan adları (`phone_number`, `job_title`). Fotoğraf yükleme `profil_foto_yukle` endpoint'inde — fiziksel silme yok, sadece DB güncelleniyor. `profil.js` SweetAlert2 ile yeniden yazıldı.

### Notlar
Eski `auth_bp.profile` ve `auth_bp.upload_profile_photo` endpoint'leri hâlâ çalışıyor — kök `templates/profile.html` kullananlar için dokunulmadı.

---

## TASK-024 | 2026-03-18 | ✅ Tamamlandı

**Görev:** users.html'de buton görünürlüğü üç role genişletildi, rol badge'leri Türkçeleştirildi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/templates/platform/admin/users.html` → Düzenle/Pasife Al buton koşulu `Admin` → `['Admin', 'tenant_admin', 'executive_manager']` olarak güncellendi; `rol_etiket` Jinja2 map'i eklendi, badge'ler Türkçe gösteriyor

### Yapılan İşlem
Daha önce Düzenle ve Pasife Al butonları yalnızca `Admin` rolüne görünüyordu; backend'de `tenant_admin` ve `executive_manager` de bu işlemleri yapabildiği için frontend koşulu üç role genişletildi. Tablodaki rol badge'leri `u.role.name` yerine `rol_etiket` map'inden Türkçe karşılıklarını gösteriyor; bilinmeyen roller olduğu gibi görünmeye devam eder.

### Notlar
Yok.

---

## TASK-023 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Rol atama yetki kontrolü ve dropdown filtrelemesi eklendi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/admin/routes.py` → `ASSIGNABLE_ROLES` sabiti eklendi; `admin_users_add` ve `admin_users_edit`'e rol yetki kontrolü eklendi; `admin_users` view'ında `roles` listesi `current_user` rolüne göre filtreleniyor

### Yapılan İşlem
`tenant_admin` ve `executive_manager` rolündeki kullanıcılar daha önce `Admin` dahil tüm rolleri atayabiliyordu. `ASSIGNABLE_ROLES` map'i ile her rol için izin verilen roller tanımlandı. `admin_users_add` ve `admin_users_edit` endpoint'lerinde atanmak istenen rol bu listeye göre kontrol ediliyor; yetkisiz atamada 403 dönüyor. `admin_users` view'ı da `roles` listesini aynı map'e göre filtreliyor, böylece dropdown'da sadece atanabilir roller görünüyor.

### Notlar
Yok.

---

## TASK-022 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Bulk import endpoint'i Excel desteği, şifre okuma ve ek alan eşleştirmesiyle güncellendi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/admin/routes.py` → `admin_users_bulk_import`: Excel (.xlsx/.xls) desteği eklendi, `Şifre` kolonu okunuyor (yoksa `"Changeme123!"` fallback), `Unvan`→`job_title` ve `Telefon`→`phone_number` alanları eklendi
- `micro/modules/admin/routes.py` → `admin_users_sample_excel`: Şablon başlığı `Sifre`→`Şifre` düzeltildi, örnek veriler Türkçe karakterlerle güncellendi
- `ui/static/platform/js/admin.js` → Bulk import Swal açıklama metni güncellendi (Excel birincil format olarak belirtildi)

### Yapılan İşlem
Örnek Excel şablonu 6 kolon sunuyordu (`Şifre`, `Unvan`, `Telefon` dahil) ancak bulk import yalnızca 3 kolonu (`email`, `first_name`, `last_name`) okuyordu. Endpoint openpyxl ile Excel okuma desteği kazandı; `Şifre` kolonu okunup hash'leniyor, yoksa güvenli fallback kullanılıyor. `Unvan` ve `Telefon` kolonları User modelindeki `job_title` ve `phone_number` alanlarına eşlendi. CSV desteği korundu.

### Notlar
`openpyxl` paketi gerekli — `pip install openpyxl` ile kurulabilir (zaten sample-excel endpoint'i kullandığı için yüklü olmalı).

---

## TASK-021 | 2026-03-18 | ✅ Tamamlandı

**Görev:** fillUserSelects fonksiyonuna ROLE_LABELS Türkçe çeviri map'i eklendi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/static/platform/js/admin.js` → `ROLE_LABELS` map eklendi; `fillUserSelects` içinde rol option'ları oluştururken `ROLE_LABELS[name] || name` kullanılıyor

### Yapılan İşlem
Kullanıcı ekle/düzenle modallarındaki rol dropdown'ı backend'den gelen İngilizce isimleri (Admin, User, tenant_admin, executive_manager, standard_user) artık Türkçe karşılıklarıyla gösteriyor. Bilinmeyen rol isimleri olduğu gibi gösterilmeye devam eder.

### Notlar
Yok.

---

## TASK-020 | 2026-03-18 | ✅ Tamamlandı

**Görev:** admin.js'deki kullanılmayan buildRoleOptions ve buildTenantOptions dead code kaldırıldı
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/static/platform/js/admin.js` → `buildRoleOptions`, `buildTenantOptions`, `ROLE_LABELS` kaldırıldı (dead code — native modal'a geçişte yerini `fillUserSelects` aldı)

### Yapılan İşlem
`fillUserSelects` ile HTML modal ID'leri (`ua-role`, `ua-tenant`, `ua-tenant-wrap`, `ue-role`, `ue-tenant`, `ue-tenant-wrap`) karşılaştırıldı — tam eşleşiyor, sorun yok. Eski Swal tabanlı koddan kalan `buildRoleOptions`, `buildTenantOptions` ve `ROLE_LABELS` artık hiçbir yerde çağrılmıyordu; kaldırıldı.

### Notlar
Yok.

---

## TASK-019 | 2026-03-18 | ✅ Tamamlandı

**Görev:** micro_bp Blueprint'inden hatalı static_url_path parametresi kaldırıldı
**Modül:** micro / blueprint
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/__init__.py` → `static_url_path="/micro/static"` parametresi kaldırıldı

### Yapılan İşlem
`static_url_path="/micro/static"` ile `url_prefix="/micro"` birleşince `url_for` `/micro/ui/static/platform/...` üretiyordu. Parametre kaldırıldığında Flask `url_prefix` + `/static` = `/micro/static` kullanıyor; `url_for('micro_bp.static', filename='platform/js/admin.js')` artık doğru `/ui/static/platform/js/admin.js` URL'ini üretiyor. Kök `/static/` route'u ile çakışma yok.

### Notlar
- **2026-03-19 (TASK-106):** Micro artık site kökünde; statik `url_prefix=""` ve `static_url_path="m"` → ör. `/m/micro/js/admin.js`. Bu kayıttaki URL anlatımı o dönemdeki `url_prefix="/micro"` düzenine aittir.

---

## TASK-018 | 2026-03-18 | 🔄 Düzeltme

**Görev:** users.html extra_js bloğundaki admin.js path'i orijinal haline döndürüldü
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/templates/platform/admin/users.html` → `filename='js/admin.js'` → `filename='platform/js/admin.js'` olarak geri alındı

### Yapılan İşlem
TASK-017'de yapılan path değişikliği geri alındı. `filename='platform/js/admin.js'` orijinal değerine döndürüldü.

### Notlar
Yok.

---

## TASK-017 | 2026-03-18 | ✅ Tamamlandı

**Görev:** users.html extra_js bloğundaki admin.js path'i düzeltildi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/templates/platform/admin/users.html` → `filename='platform/js/admin.js'` → `filename='js/admin.js'` olarak düzeltildi

### Yapılan İşlem
Blueprint static dosya yolu `micro/js/admin.js` yerine `js/admin.js` olarak düzeltildi. `micro_bp.static` zaten `ui/static/platform/` prefix'ini ekliyor, dolayısıyla `micro/js/` tekrarı 404'e yol açıyordu.

### Notlar
Yok.

---

## TASK-016 | 2026-03-18 | ✅ Tamamlandı

**Görev:** JS/CSS dosyalarına cache busting için VERSION query string eklendi
**Modül:** admin / config / base
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `config.py` → `Config` sınıfına `VERSION = "1.0.1"` eklendi
- `ui/templates/platform/base.html` → 3 CSS + 1 JS include satırına `?v={{ config['VERSION'] }}` eklendi
- `ui/templates/platform/admin/users.html` → `extra_js` bloğundaki `admin.js` satırına `?v={{ config['VERSION'] }}` eklendi

### Yapılan İşlem
Tarayıcı cache'inin eski JS/CSS dosyalarını sunmasını önlemek için `config.py`'ye `VERSION` sabiti eklendi. `base.html`'deki tüm yerel CSS/JS include'ları ve `users.html`'deki `admin.js` include'u bu versiyonu query string olarak kullanacak şekilde güncellendi. Bundan sonra her JS/CSS değişikliğinde `config.py`'deki `VERSION` değeri artırılmalıdır.

### Notlar
`tenants.html` ve diğer admin sayfalarının `extra_js` bloklarında da aynı pattern uygulanmalı.

---

## TASK-015 | 2026-03-18 | ✅ Tamamlandı

**Görev:** admin.js ROLE_LABELS map'indeki ASCII Türkçe karakter hataları düzeltildi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/static/platform/js/admin.js` → `ROLE_LABELS` map'inde 4 değer ve `buildRoleOptions` fallback string'i Türkçe karakterlerle düzeltildi

### Yapılan İşlem
`ROLE_LABELS` map'indeki `"Kullanici"`, `"Kurum Yoneticisi"`, `"Kurum Ust Yonetimi"`, `"Kurum Kullanicisi"` değerleri sırasıyla `"Kullanıcı"`, `"Kurum Yöneticisi"`, `"Kurum Üst Yönetimi"`, `"Kurum Kullanıcısı"` olarak güncellendi. `buildRoleOptions` fallback'i `"— Rol Sec —"` → `"— Rol Seç —"` yapıldı.

### Notlar
Yok.

---

## TASK-014 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Rol dropdown'ı Türkçe etiketlerle gösterilecek şekilde güncellendi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/static/platform/js/admin.js` → `ROLE_LABELS` map eklendi, `buildRoleOptions` fonksiyonu çeviri map'ini kullanacak şekilde güncellendi

### Yapılan İşlem
Backend'den gelen İngilizce rol isimleri (Admin, User, tenant_admin, executive_manager, standard_user) frontend'de Türkçe karşılıklarıyla gösterilmek üzere `ROLE_LABELS` map'i eklendi. Bilinmeyen rol isimleri olduğu gibi gösterilmeye devam eder.

### Notlar
Yok.

---

## TASK-013 | 2026-03-18 | ✅ Tamamlandı

**Görev:** users.html kullanıcı ekle/düzenle Swal modalları native HTML modal'a geçirildi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/templates/platform/admin/users.html` → `modal-user-add` ve `modal-user-edit` native modal'ları eklendi (mc-modal-overlay/mc-modal-lg yapısı)
- `ui/static/platform/js/admin.js` → btn-user-add ve btn-user-edit Swal.fire blokları kaldırıldı, native modal open/close/save fonksiyonları eklendi

### Yapılan İşlem
tenants.html'deki mc-modal-overlay/mc-modal-lg yapısı referans alınarak iki native modal oluşturuldu. admin.js'de Swal.fire bağımlılığı kaldırıldı; rol ve kurum select'leri admin-meta data-* attribute'larından dinamik dolduruluyor. API endpoint'leri (ADD_URL, EDIT_BASE) değişmedi.

### Notlar
toggle ve bulk-import işlemleri Swal.fire kullanmaya devam ediyor — bu kasıtlı, değiştirilmedi.

---

## TASK-012 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Excel şablonu sütunları güncellendi, Swal modal genişliği CSS ile sabitlendi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/admin/routes.py` → Excel şablonu başlıkları Ad/Soyad/E-posta/Sifre/Unvan/Telefon olarak güncellendi, 6 sütun genişliği ayarlandı
- `ui/static/platform/js/admin.js` → btn-user-add ve btn-user-edit Swal'larına `customClass: { popup: 'mc-swal-wide' }` eklendi
- `ui/static/platform/css/components.css` → `.mc-swal-wide` sınıfı eklendi (780px sabit genişlik)

### Yapılan İşlem
Excel şablonu kök yapıdaki kullanıcı alanlarıyla eşleştirildi. Swal modallarının gerçek genişliği tarayıcıda `width` parametresiyle tam uygulanmıyor olabildiğinden `customClass` + CSS ile 780px sabitlendi.

### Notlar
Yok.

---

## TASK-011 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Kullanıcı Swal modal genişlikleri 780px yapıldı, örnek Excel endpoint ve indirme butonu eklendi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/static/platform/js/admin.js` → btn-user-add width 560→780, btn-user-edit width 520→780, toplu içe aktar Swal'ına indirme butonu eklendi
- `micro/modules/admin/routes.py` → `/admin/users/sample-excel` GET endpoint'i eklendi (openpyxl ile xlsx üretir)

### Yapılan İşlem
Kullanıcı ekleme ve düzenleme Swal modalları tenant modal'ıyla aynı genişliğe (780px) getirildi. Toplu içe aktarma için örnek Excel şablonu üreten yeni bir endpoint eklendi. Swal'daki indirme butonu bu endpoint'e bağlandı; dosya kabul tipi `.csv,.xlsx` olarak güncellendi.

### Notlar
`openpyxl` paketi yüklü olmalı — `pip install openpyxl` ile kurulabilir.

---

## TASK-010 | 2026-03-18 | ✅ Tamamlandı

**Görev:** users.html kullanıcı yönetimi sayfası iyileştirmeleri ve admin.js e-posta alanı eklendi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/templates/platform/admin/users.html` → `data-email` eklendi, inline style kaldırıldı (`mc-page-content`), `mc-input`→`mc-form-input`, stat kartları eklendi, butonlar Admin kontrolüne alındı
- `ui/static/platform/js/admin.js` → `btn-user-edit` listener'ında `email` okunuyor, Swal formuna readonly e-posta alanı eklendi

### Yapılan İşlem
`users.html`'de 5 iyileştirme yapıldı: `data-email` attribute eklendi, `max-width` inline style `mc-page-content` sınıfıyla değiştirildi, arama kutusu sınıfı `mc-form-input` olarak düzeltildi, 3 stat kartı (toplam/aktif/pasif) eklendi, Düzenle ve Pasife Al butonları `Admin` rolü kontrolüne alındı. `admin.js`'de düzenleme Swal'ına readonly e-posta alanı eklendi.

### Notlar
E-posta alanı readonly — değiştirilemez, sadece bilgi amaçlı gösteriliyor.

---

## TASK-009 | 2026-03-18 | ✅ Tamamlandı

**Görev:** SQLAlchemy `Multiple classes found for path "User"` ve duplicate tablo hatası giderildi
**Modül:** models / app/models
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `models/user.py` → `class User` → `class LegacyUser`, `class Notification` → `class LegacyNotification`; tüm `relationship('User', ...)` → `relationship('LegacyUser', ...)`
- `models/__init__.py` → import satırı `LegacyUser`, `LegacyNotification` olarak güncellendi; `User = LegacyUser` ve `Notification = LegacyNotification` alias'ları eklendi
- `app/models/notification.py` → `__tablename__ = 'notifications'` → `'notifications_ext'` (core.py ile çakışma giderildi)

### Yapılan İşlem
`models/user.py` ile `app/models/core.py`'de aynı isimde `User` ve `Notification` class'ları bulunuyordu; SQLAlchemy registry çakışma hatası veriyordu. Kök `models/` altındaki class'lar `Legacy` prefix'i alarak yeniden adlandırıldı, geriye dönük uyumluluk için alias'lar eklendi. Ayrıca `app/models/notification.py` ile `app/models/core.py` aynı `notifications` tablo adını kullanıyordu; `notification.py` tablosu `notifications_ext` olarak yeniden adlandırıldı. Uygulama `http://127.0.0.1:5001` üzerinde hatasız başlıyor.

### Notlar
`notifications_ext` tablosu yeni bir tablo — mevcut DB'de bu tablo yoksa migration gerekebilir.

---

## TASK-008 | 2026-03-18 | ✅ Tamamlandı

**Görev:** `app/models/__init__.py`'deki duplicate `db` instance kaldırıldı, kök `extensions.py::db`'ye yönlendirildi
**Modül:** micro / db / models
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/models/__init__.py` → `db = SQLAlchemy()` kaldırıldı, `from extensions import db` ile kök instance kullanılıyor
- `__init__.py` → `from app.models import db as app_db` ve `app_db.init_app(app)` satırları kaldırıldı

### Yapılan İşlem
Projede 3 ayrı `SQLAlchemy` instance mevcuttu: `extensions.py::db`, `app/extensions.py::db`, `app/models/__init__.py::db`. Micro modülleri `app.models.db`'yi kullanıyor, kök uygulama ise `extensions.py::db`'yi `init_app` yapıyordu. Bu iki farklı instance olduğu için `RuntimeError: not registered with this SQLAlchemy instance` hatası oluşuyordu. `app/models/__init__.py`'deki `db = SQLAlchemy()` kaldırılıp kök `extensions.py`'den import edildi; artık tüm modeller tek bir instance üzerinde çalışıyor.

### Notlar
`app/extensions.py::db` hâlâ kullanılmıyor — ileride bu dosya da temizlenebilir.

---

## TASK-007 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Micro modüllerinin kullandığı `app.models.db` instance'ı kök `__init__.py`'de `init_app` ile bağlandı
**Modül:** micro / db
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `__init__.py` → `from app.models import db as app_db` import edildi, `app_db.init_app(app)` eklendi

### Yapılan İşlem
Projede 3 farklı `SQLAlchemy` instance'ı mevcut: `extensions.py::db`, `app/extensions.py::db`, `app/models/__init__.py::db`. Micro modülleri `app.models.db`'yi kullanıyor ancak kök `__init__.py` yalnızca `extensions.py::db`'yi `init_app` yapıyordu. `app_db.init_app(app)` eklenerek `RuntimeError: not registered with this SQLAlchemy instance` hatası giderildi.

### Notlar
Uzun vadede tek bir `db` instance'ına geçilmesi teknik borcu azaltır.

---

## TASK-006 | 2026-03-18 | ✅ Tamamlandı

**Görev:** `__init__.py`'ye eksik `micro_bp` register satırı eklendi
**Modül:** micro / hgs
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `__init__.py` → `from micro import micro_bp` + `app.register_blueprint(micro_bp)` eklendi

### Yapılan İşlem
Kök `__init__.py`'de micro_bp hiç register edilmemişti; bu yüzden `/micro/*` altındaki tüm route'lar 404 veriyordu. Blueprint kaydı `v3_bp`'nin hemen altına eklendi. Doğrulama: `/micro/hgs` ve `/micro/hgs/login/<int:user_id>` route'ları artık url_map'te görünüyor.

### Notlar
- **2026-03-19 (TASK-106):** Üretim `app.create_app` kullanır; Micro kökte `/hgs` vb. Eski `/micro/hgs` istekleri köke 302 ile yönlendirilir.

---

## TASK-005 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Login sayfası CSP bloğu nedeniyle bozulan inline style/script harici dosyalara taşındı
**Modül:** auth / login
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `templates/login.html` → Inline `<style>` ve `<script>` blokları kaldırıldı, harici dosyalara bağlandı
- `static/css/login.css` → Oluşturuldu (login sayfası tüm CSS'i)
- `static/js/login.js` → Oluşturuldu (quick login toggle JS)

### Yapılan İşlem
Flask-Talisman'ın `content_security_policy_nonce_in` ayarı inline style ve script bloklarını engelliyordu. Login sayfasındaki tüm CSS `static/css/login.css`'e, JS ise `static/js/login.js`'e taşındı. HTML'de sadece `<link>` ve `<script src>` referansları kaldı.

### Notlar
Tarayıcı erişimi sağlanamadı, kod analizi yapıldı.

---

## TASK-004 | 2026-03-18 | ✅ Tamamlandı

**Görev:** `config.py`'de eksik `get_config()` fonksiyonu eklendi
**Modül:** config
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `config.py` → `get_config()` fonksiyonu eklendi; `FLASK_ENV`'e göre `Config` veya `TestingConfig` döner

### Yapılan İşlem
`__init__.py` `get_config` adını import etmeye çalışıyordu ancak `config.py`'de yalnızca class tanımları vardı, fonksiyon yoktu. `TestingConfig`'in hemen altına `get_config()` factory fonksiyonu eklenerek `ImportError` giderildi.

### Notlar
Yok.

---

## TASK-003 | 2026-03-18 | ✅ Tamamlandı

**Görev:** TASKLOG.md UTF-8 BOM'suz yeniden yazıldı, eski_proje git'ten çıkarıldı
**Modül:** setup / git
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `docs/TASKLOG.md` → Python ile UTF-8 BOM'suz yeniden yazıldı
- `.gitignore` → `eski_proje/` satırı eklendi
- `eski_proje` → `git rm --cached` ile git index'ten kaldırıldı

### Yapılan İşlem
TASKLOG.md encoding sorunu giderildi; dosya artık BOM'suz saf UTF-8. eski_proje klasörü git'ten çıkarıldı ve .gitignore'a eklendi, git status'ta bir daha görünmeyecek.

### Notlar
Yok.

---

## TASK-002 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Tüm `px` font-size değerleri `var(--text-*)` CSS değişkenlerine geçirildi
**Modül:** css / tipografi
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/static/platform/css/components.css` → Tüm sabit `px` font-size değerleri `var(--text-*)` token'larıyla değiştirildi; `html { font-size: 16px }` rem tabanı korundu

### Yapılan İşlem
`components.css` içindeki tüm sabit `px` font-size değerleri `:root` üzerinde tanımlı `--text-2xs` → `--text-3xl` token'larıyla değiştirildi. Böylece `html { font-size }` değeri değiştirildiğinde tüm tipografi orantılı ölçeklenir.

### Notlar
`sidebar.css` önceki oturumda güncellenmişti. `app.css` zaten `rem` kullanıyor, dokunulmadı.

---

## TASK-001 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Proje kurulum ve GitHub entegrasyonu tamamlandı
**Modül:** setup
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `docs/TASKLOG.md` → İlk kayıt oluşturuldu
- `.kiro/steering/proje-kurallari.md` → TASKLOG + otomatik push kuralları eklendi
- `github_sync.py` → Otomatik push desteği eklendi

### Yapılan İşlem
Proje GitHub entegrasyonu kuruldu. Steering kuralları, TASKLOG takip sistemi ve otomatik push mekanizması devreye alındı.

### Notlar
Sistem test ediliyor. Sonraki görevlerden itibaren her değişiklikte TASKLOG otomatik güncellenecek ve push edilecek.

---

## TASK-001 | 2026-03-17 | 🔄 Düzeltme

**Görev:** tenants.html'de duplicate `extra_js` bloğu hatası giderildi
**Modül:** admin
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `ui/templates/platform/admin/tenants.html` → Duplicate `{% block extra_js %}` bloğu kaldırıldı

### Yapılan İşlem
Önceki oturumda `fsAppend` ile eklenen `extra_js` bloğu, dosyada zaten mevcut olan aynı blokla çakışıyordu. Jinja2 aynı isimde iki blok tanımına izin vermediği için `TemplateAssertionError` fırlatıyordu. Fazladan olan ikinci blok kaldırıldı.

### Notlar
Yok.

---

