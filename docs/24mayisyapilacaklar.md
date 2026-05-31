# 📋 24 Mayıs 2026 — Yapılacaklar Listesi

> **Hazırlanış tarihi:** 2026-05-24
> **Bağlam:** Sprint 1-52 tamamlandı (~3 aylık yoğun çalışma). Bu doküman kalan açık işleri detaylandırır.
> **Kaynak dökümanlar:** [PROJE-AUDIT-2026Q2.md](PROJE-AUDIT-2026Q2.md) · [KALAN-EKSIKLER-2026Q2.md](KALAN-EKSIKLER-2026Q2.md) · [ROADMAP-2026H2.md](ROADMAP-2026H2.md) · [LEGACY_SUNSET_MAP.md](LEGACY_SUNSET_MAP.md) · [SOC2_ISO27001_HAZIRLIK.md](SOC2_ISO27001_HAZIRLIK.md)

---

## 🎯 ÖZET

| Kategori | İş sayısı | Toplam efor |
|---|:-:|:-:|
| 🔴 KRİTİK (kullanıcı/sistem eylemi) | 4 | ~6h |
| 🟠 YÜKSEK (legacy sunset + production hazırlık) | 8 | ~80h |
| 🟡 ORTA (yeni özellik + UI tamamlama) | 12 | ~180h |
| 🟢 DÜŞÜK (yeni modüller + compliance) | 10 | ~430h |
| **TOPLAM** | **34** | **~696h** |

---

# 🔴 KRİTİK (1-2 hafta içinde)

## K1. Production SECRET_KEY ve DB password rotasyonu
**Tip:** Kullanıcı/DevOps eylemi
**Tahmin:** 30 dk
**Bağımlılık:** Yok
**Detay:**
- `.env.production` dosyasında `SECRET_KEY=dev_key_123` HÂLÂ kullanılıyor olabilir
- DB password `kokpitim_dev_123` zayıf
- Rehber hazır: [GUVENLIK_REHBERI.md](GUVENLIK_REHBERI.md) §1.1-1.4
- **Adımlar:**
  1. `python -c "import secrets; print(secrets.token_hex(32))"` → SECRET_KEY üret
  2. PostgreSQL: `ALTER USER kokpitim_prod WITH PASSWORD '...'`
  3. `.env.production` güncelle (chmod 600)
  4. Restart → tüm session'lar invalidate
- **Kabul kriteri:** `.env.production` içinde "dev_key" geçmiyor, audit log'da SECRET_KEY_ROTATION kaydı var

## K2. KVKK Aydınlatma Metni sayfası
**Tip:** Hukuki + UI
**Tahmin:** 2h
**Bağımlılık:** Yok (KVKK altyapısı Sprint 12'de hazır)
**Detay:**
- Yeni route: `/kvkk-aydinlatma` (public, login-required değil)
- Template: `templates/auth/kvkk_aydinlatma.html`
- İçerik: hangi veriler toplanır, hangi amaçla, ne süre saklanır, hakları (Madde 11 referans)
- Profile sayfasından link verilir
- Login sayfasında footer'da link
- **Kabul kriteri:** Public erişim, tüm haklar listelenmiş, son güncelleme tarihi var

## K3. K-Vektor strateji + alt strateji weight update atomic transaction
**Tip:** Bug/risk
**Tahmin:** 2h
**Konum:** `micro/modules/sp/routes_strategy.py:125-144`
**Detay:**
- Strateji edit sırasında `KVektorStrategyWeight` + `KVektorSubStrategyWeight` aynı anda güncellenmesi gerek
- Hata durumunda partial update mümkün → veri tutarsızlığı
- **Çözüm:** Sprint 19'da `KpiData + KpiDataAudit` için yapılan `db.session.begin_nested()` (SAVEPOINT) pattern'ini uygula
- Test: K-Vektor weight FK violation → her ikisi de rollback olmalı

## K4. Audit log retention cron job
**Tip:** KVKK uyumluluk + DB performance
**Tahmin:** 1.5h
**Detay:**
- `audit_logs` tablosu sınırsız büyüyor — 6 ay sonra yüzbinlerce satır olabilir
- KVKK gereği: 90 gün sonra IP + user_agent anonimize
- **Adımlar:**
  1. APScheduler'a yeni job ekle: günlük 03:00
  2. Service: `app/services/audit_retention_service.py`
  3. Logic:
     - `UPDATE audit_logs SET ip_address=REGEXP_REPLACE(...) WHERE created_at < NOW() - 90 days`
     - 365 günden eski VIEW kayıtlarını sil (sadece CRITICAL action'ları tut)
- Manuel SQL [GUVENLIK_REHBERI.md](GUVENLIK_REHBERI.md) §4.3'te
- **Kabul kriteri:** Cron çalıştığını audit_logs'a kendisi kaydeder

---

# 🟠 YÜKSEK (3-6 hafta)

## Y1. `app/routes/process.py` SUNSET (1.805 satır legacy)
**Tahmin:** 8h
**Risk seviyesi:** YÜKSEK — gerçek üretim test'i gerek
**Hazırlık:** Sprint 29-30'da lazy import yapıldı (`LEGACY_PROCESS_BP_ENABLED=False`)
**Audit:** [PROCESS_BP_SUNSET_AUDIT.md](PROCESS_BP_SUNSET_AUDIT.md) — %95 parity onaylı
**Adımlar:**
1. **Pre-flight (1 saat):**
   - 39 endpoint'in micro/surec eşdeğerini smoke test ile doğrula
   - KpiDataAudit logic'i micro/surec'te birebir aynı mı kontrol et
   - Production logs: son 30 günde `LEGACY_PROCESS_BP_ENABLED=True` set edilmiş mi?
2. **Manuel API test (2 saat):**
   - 5 kritik endpoint: `/process/api/kpi-data/add`, `/process/api/activity/add`, `/process/api/kpi/delete/<id>`, `/process/<id>/karne`, `/process/api/update/<id>`
   - Tomofil tenant (id=27) ile bağlantılı test
3. **Migration logic taşıma (2 saat):**
   - Eğer process.py'da micro/surec'te olmayan logic varsa taşı
4. **Silme (1 saat):**
   - `app/__init__.py`'dan lazy import bloğunu kaldır
   - `app/routes/process.py` sil
   - CI guard zaten mevcut: `test_no_direct_process_bp_import_outside_init`
5. **Doğrulama (2 saat):**
   - Smoke test, e2e test
   - Üretim 1 hafta gözlem
**Kabul kriteri:** -1.805 satır, tüm testler yeşil, üretim 1 hafta sorunsuz

## Y2. `app/routes/admin.py` micro/admin merge (1.141 satır)
**Tahmin:** 12h
**Bağımlılık:** Y1 sonrası (process.py modeli)
**Detay:**
- micro/admin'de zaten 41 endpoint var (Sprint 1 sayım)
- `app/routes/admin.py` 24+ endpoint — bazıları duplicate, bazıları unique
- **Adımlar:**
  1. Endpoint diff (2 saat): hangi route legacy'de var, micro'da yok?
  2. Eksik route'ları micro/admin'e taşı (4 saat)
  3. Template'ler micro'ya yönlendir + safe_url_for fallback ekle (2 saat)
  4. CI guard ekle: `test_no_direct_admin_bp_import_outside_init` (1 saat)
  5. Lazy import → silme (1 saat)
  6. Test + doğrulama (2 saat)
**Kabul kriteri:** -1.141 satır, admin paneli tüm fonksiyonlar çalışır

## Y3. `app/routes/auth.py` + `auth/routes.py` auth merge (552 satır)
**Tahmin:** 10h
**Risk:** YÜKSEK — login flow değişikliği
**Detay:** [AUTH_MAIN_SUNSET_PLAN.md](AUTH_MAIN_SUNSET_PLAN.md) §Sprint 39-40
- `app/routes/auth.py` modern, aktif (302 satır)
- `auth/routes.py` legacy quick-login (250 satır), PROD'da disable
- **Hedef:** Her ikisini `micro/shared/auth/` altında birleştir
- **Adımlar:**
  1. micro/shared/auth/ mevcut yapı denetimi (1 saat)
  2. `auth/routes.py` referans sıfır mı? (1 saat) — sıfır ise sil
  3. `app/routes/auth.py` endpoint'lerini micro'ya taşı (4 saat):
     - `/login`, `/logout`, `/profile`, `/profile/upload-photo`, `/settings`
  4. KVKK + login throttle + 2FA flow'ları taşı (2 saat)
  5. Test (2 saat): manuel login flow + 2FA challenge + KVKK endpoint
**Kabul kriteri:** -552 satır, login flow + 2FA + KVKK çalışır

## Y4. `main/routes/` sunset (328 satır)
**Tahmin:** 6h
**Bağımlılık:** Y1, Y2, Y3 (önceki sunset'ler stabilize olmalı)
**Detay:** [AUTH_MAIN_SUNSET_PLAN.md](AUTH_MAIN_SUNSET_PLAN.md) §Sprint 41-42
- Çoğu endpoint `legacy_sunset` middleware ile zaten 410/301
- **Adımlar:**
  1. Endpoint usage analizi: hangileri hâlâ ulaşılabilir? (1 saat)
  2. Ulaşılabilen route'ları micro modüllere taşı veya 410 ekle (3 saat)
  3. `main_bp` blueprint'ini app/__init__.py'dan kaldır (1 saat)
  4. `main/routes/` klasörünü sil (1 saat)
  5. CI guard: `test_no_main_routes_import`
**Kabul kriteri:** -328 satır, `tests/test_legacy_sunset.py` 410 endpoint'leri doğruluyor

## Y5. KpiData atomicity xfail test fix
**Tahmin:** 3h
**Konum:** `tests/test_kpi_data_atomicity.py:120` (xfail)
**Detay:**
- Sprint 19.1'de SAVEPOINT pattern uygulandı (production'da çalışıyor)
- Test ortamı session davranışı production'dan farklı → xfail
- **Adımlar:**
  1. Test fixture'ı integration test olarak yeniden yapılandır
  2. Real Postgres connection ile test (in-memory değil)
  3. xfail mark'ını kaldır, test pass etmeli
**Kabul kriteri:** xfail kalkar, test yeşil

## Y6. Strategy clone FK orphan koruma
**Tahmin:** 4h
**Konum:** `micro/modules/sp/routes_plan_year.py:150+`
**Detay:**
- `clone_full_plan_year()` rollback'te FK orphan riski
- Audit'te tespit edildi (risk skoru 12)
- **Çözüm:**
  - Tüm clone işlemini `db.session.begin_nested()` savepoint içinde
  - Hata durumunda full rollback test
- Yeni test: `tests/test_plan_year_clone_atomicity.py`
**Kabul kriteri:** Clone hatası → 0 orphan record

## Y7. KVKK Aydınlatma metni Türkçe + İngilizce
**Tahmin:** 6h
**Bağımlılık:** K2 (sayfa altyapısı)
**Detay:**
- Hukuki incelemeden geçmiş metin gerek
- Türkçe ve İngilizce versiyon (i18n ile)
- KVK Kurumu standart şablonuna uyum
- 8 bölüm: amaç, kapsam, toplanan veriler, işleme amacı, aktarım, saklama süresi, haklar, iletişim
**Kabul kriteri:** Hukuk onayı + i18n switch (TR/EN)

## Y8. Pagination uygulama — 10 büyük endpoint
**Tahmin:** 6h
**Detay:**
- Sprint 19'da `paginate_query()` helper hazır
- Sprint 24'te `/admin/api/users` uyguladık
- Diğer büyük list endpoint'leri:
  1. `/process/api/list` (tenant'ta 100+ süreç)
  2. `/sp/api/strategies` (yıl × tenant)
  3. `/k-rapor/api/uyari` (anomali listesi)
  4. `/k-radar/api/risk/list` (riskler)
  5. `/bireysel/api/karne` (PG geçmiş)
  6. `/process/api/kpi-data/list/<id>` (KpiData geçmiş — Tomofil'de 5K+ satır)
  7. `/process/api/activity/list/<id>`
  8. `/sp/api/okr` (OKR listesi)
  9. `/k-rapor/api/faaliyet`
  10. `/process/api/kpi/list/<id>`
- Her birinde:
  - `paginate_query()` helper kullan
  - Default 50, max 200
  - Frontend'de "Daha fazla yükle" veya sayfa numarası
**Kabul kriteri:** Tüm 10 endpoint için page/page_size query params çalışıyor

---

# 🟡 ORTA (2-4 ay)

## O1. ESG modülü UI + endpoint'ler
**Tahmin:** 16h
**Bağımlılık:** Sprint 49 (model + migration) hazır
**Detay:**
- **Backend (6 saat):**
  - `micro/modules/sustainability/` (yeni modül)
  - CRUD endpoint'leri: metric CRUD + value entry + listing
  - Aggregate: Scope 1+2+3 toplam karbon hesabı
  - SDG bazlı raporlama
- **Frontend (8 saat):**
  - `/sustainability` ana sayfa (E/S/G kategori dashboard)
  - Metric ekleme/düzenleme formu (modal)
  - Aylık değer girişi
  - Grafikler: zaman serisi karbon, SDG ilerleme
- **Tests (2 saat):**
  - CRUD endpoint testleri
  - Aggregate hesabı snapshot test
**Kabul kriteri:** Tomofil için 10 ESG metric örnek + Q3 değerleri girilebilir

## O2. Dashboard builder UI (drag-drop)
**Tahmin:** 32h
**Bağımlılık:** Sprint 50 (widget registry hazır)
**Detay:**
- **Migration (1 saat):**
  - `user_dashboards` tablosu: user_id, name, widget_config_json, is_default
- **Backend (8 saat):**
  - CRUD: dashboard create/save/delete/list
  - Widget config validation (registry'deki config_schema'ya göre)
- **Frontend (20 saat):**
  - Vue/Vanilla JS grid layout (gridstack.js veya muuri)
  - Widget kütüphanesi side panel
  - Drag & drop layout
  - Widget config modal (kpi_id seç, period seç vb.)
  - "Varsayılan dashboard" + "Yeni dashboard" sekmeleri
- **Tests (3 saat):**
  - Widget config schema validation
  - Layout persist test
**Kabul kriteri:** Kullanıcı kendi dashboard'unu drag-drop ile inşa edip kaydedebilir

## O3. SOC 2 / ISO 27001 politika dokümanları
**Tahmin:** 32h
**Detay:** [SOC2_ISO27001_HAZIRLIK.md](SOC2_ISO27001_HAZIRLIK.md) §"Önceliklendirilmiş Liste"
**5 kritik politika dokümanı:**
1. **Bilgi Güvenliği Politikası (ISMS)** — 8h
   - Scope, sorumluluklar, taahhüt, gözden geçirme süreci
2. **İş Sürekliliği Planı (BCP)** — 8h
   - RTO/RPO hedefleri, backup test prosedürü, DR senaryoları
3. **Olay Müdahale Planı (IR)** — 6h
   - Severity sınıflandırma, escalation matrix, post-mortem template
4. **Tedarikçi Güvenlik Politikası** — 4h
   - 3rd party risk değerlendirme, sözleşme şablonu
5. **Çalışan Güvenlik Eğitimi içeriği** — 6h
   - Onboarding modülü, yıllık tazeleme, phishing simulation
**Format:** Her biri ayrı .md dosyası `docs/policies/` altında
**Kabul kriteri:** CTO + hukuk onayı, 5 doküman canlı

## O4. i18n çeviri kapsamı (33 → tüm UI)
**Tahmin:** 24h
**Bağımlılık:** Sprint 31 (33 mesaj zaten çevrildi)
**Detay:**
- **Extract (4 saat):** `pybabel extract -F babel.cfg -o messages.pot .`
- **Templates'de _() wrapper (10 saat):**
  - 20+ template'i gez, hardcoded TR string'leri `{{ _("...") }}` ile sar
  - JavaScript flash mesajları için ayrı dictionary
- **Python kodda gettext (6 saat):**
  - `flash("...", "success")` → `flash(_("..."), "success")`
  - audit description'lar gettext_lazy
- **TR + EN çeviri (4 saat):**
  - 200+ mesaj tahmini
  - .po dosyalarını güncelle, .mo derle
**Kabul kriteri:** UI'da `?lang=en` ile tam İngilizce arayüz

## O5. Mobile + PWA cilalama
**Tahmin:** 16h
**Bağımlılık:** Sprint 27 (mobile.css iskelet hazır)
**Detay:**
- **Service Worker (4h):** offline cache + install prompt
- **App manifest (2h):** name, icons, theme_color, display
- **Touch gesture'lar (4h):** swipe-to-delete, pull-to-refresh
- **Performance audit (3h):** Lighthouse 90+ score hedefi
- **Push notifications (3h):** FCM integration (Sprint 8'de push_subscriptions model var)
**Kabul kriteri:** Mobile Chrome'da "Ana ekrana ekle" → standalone app

## O6. Custom RBAC role oluşturma
**Tahmin:** 16h
**Detay:**
- Şu an 5 sabit role: Admin, User, tenant_admin, executive_manager, standard_user
- Tenant admin kendi tenant'ında custom role yaratabilmeli
- **Migration:** `tenant_roles` tablosu (mevcut roles tablosu sistemic, tenant_roles özelleştirilmiş)
- **UI:** Admin paneline "Role Yönetimi" sekmesi
- **Permission matrix:** Modül × Aksiyon (view/create/update/delete) tablo
**Kabul kriteri:** Tenant admin "Süreç Lideri" role'ünü yaratıp 5 kullanıcıya atayabilir

## O7. Sektör benchmark verisi (K-Radar)
**Tahmin:** 16h
**Detay:**
- "Sizin OEE %72, sektör ortalaması %78" karşılaştırması
- **Veri kaynağı (8h):**
  - Statik benchmark sözlüğü (sektör × KPI tipi → ortalama)
  - Veya anonymous aggregated user data (multi-tenant)
- **UI (6h):**
  - K-Radar olgunluk sayfasında "Benchmark" overlay
  - KPI kartlarında karşılaştırma rozeti
- **Test (2h)**
**Kabul kriteri:** Tomofil için 10 KPI'da benchmark görünür

## O8. KVKK uyumluluk genişletme
**Tahmin:** 12h
**Bağımlılık:** Sprint 12 (export/delete var) + K2 (aydınlatma metni)
**Detay:**
- **Consent management (4h):**
  - User kayıt olurken / ilk login'de aydınlatma onay kutucuğu
  - `users.consents_json` field (migration): {"kvkk":"2026-05-24","marketing":"2026-05-25"}
- **Veri taşınabilirliği genişletme (4h):**
  - PDF export (JSON yerine veya ek)
  - CSV export (tablo bazlı)
- **Veri silme delay (4h):**
  - "Hesabımı sil" → 7 gün cooling period
  - Email confirm
  - 7 gün sonra otomatik silme (APScheduler)
**Kabul kriteri:** KVKK Madde 11 + 7 tam uyum

## O9. Anomali detect cron job (otomatik bildirim)
**Tahmin:** 8h
**Bağımlılık:** Sprint 14 (anomali servisi) + Sprint 18 (digest scheduler) + Sprint 45 (Slack/Teams/Discord)
**Detay:**
- Şu an manuel: kullanıcı `/k-rapor/anomalies` sayfasında "Slack'e Gönder" butonu
- Otomatik:
  - Her gece 02:00 her tenant için anomali tara
  - severity ≥ high varsa configured webhook'a gönder
  - Tenant config: `notification_settings.anomaly_auto_dispatch_enabled`
- APScheduler hook
**Kabul kriteri:** Tomofil tenant'ında configure edilmiş webhook varsa, kritik anomali otomatik gönderilir

## O10. KPI versioning (şablon değişimi)
**Tahmin:** 16h
**Detay:**
- Sorun: KPI'nın `target_value` veya `unit` değişirse tarihsel `KpiData` inconsistent görünür
- **Çözüm:**
  - `ProcessKpi.version` field (migration)
  - Edit yapıldığında snapshot tut: `ProcessKpiSnapshot` tablosu
  - Karne hesabında "o zamanki target" kullan
- UI: "Şablon değişiklik history" göster
**Kabul kriteri:** KPI target'ı %85 → %90 değiştirilirse, geçmiş KpiData hâlâ %85'e göre değerlendirilir

## O11. AI Executive Summary genişletme
**Tahmin:** 12h
**Bağımlılık:** `services/ai_executive_summary.py` mevcut
**Detay:**
- Mevcut: temel özet yazımı
- **Genişletme:**
  - LLM prompt tuning (daha kurumsal Türkçe ton)
  - Multi-section: stratejik özet + operasyonel + risk + öneri
  - PDF olarak indir (Sprint 11 PDF altyapısı + )
  - Scheduled (haftalık/aylık) e-mail
- Provider: OpenAI / Anthropic / yerel LLM (Ollama)
**Kabul kriteri:** CEO bir butona basıp 2 dakikada 3 sayfalık yönetici özeti PDF alır

## O12. Bulk import genişletme (Process + Project)
**Tahmin:** 8h
**Bağımlılık:** Sprint 44 (KPI bulk import hazır)
**Detay:**
- **Process import (3h):**
  - Excel: code, name, parent_code, weight, description
  - Hiyerarşi: parent_code → parent_id resolve
- **Project import (3h):**
  - Excel: name, start_date, end_date, manager_email, priority
- **Tests (2h)**
**Kabul kriteri:** Toplu 50+ process veya proje Excel'den 30 saniyede yüklenir

---

# 🟢 DÜŞÜK (4-12 ay)

## D1. Yeni modül: Vendor / Tedarikçi Portali
**Tahmin:** 80h
**Detay:**
- **Use case:** Tomofil tedarikçilerine "Bu çeyrek OTD performansınız %87" gösterimi
- **Yapı:**
  - Yeni role: `vendor_user`
  - Vendor user tek bir tedarikçi entity'ye bağlanır
  - View-only erişim: kendi KPI'ları + iletişim
  - Feedback formu (memnuniyet anketi gibi)
- **Migration:** `vendors` tablosu + `vendor_users` (vendor_id → user_id)
- **UI:** Vendor-specific dashboard, brand restricted

## D2. Yeni modül: Müşteri Portali
**Tahmin:** 80h
**Detay:** Benzer Vendor, ama Customer side. Stakeholder engagement.

## D3. Yeni modül: Eğitim + Zanaatkar Gelişim Takibi
**Tahmin:** 80h
**Detay:**
- Tomofil senaryosundan ilham (çırak/usta sistemi)
- **Modüller:**
  - Eğitim kataloğu (CRUD)
  - Kullanıcı kayıt → tamamlama tracking
  - Sertifika expiration alert
  - Yetkinlik matrisi (employee × skill → seviye)
- **Migration:** `trainings`, `training_enrollments`, `certifications`, `competencies`

## D4. SOC 2 Type I başvurusu (Q1 2027)
**Tahmin:** 40h (hazırlık) + 6-8 hafta denetim
**Bağımlılık:** O3 (politika doc'lar tamamlanmalı)
**Detay:**
- CPA firma seç (Schellman, Aprio gibi US-based veya Türkiye'de partner)
- Pre-audit gap assessment
- Type I (point-in-time) → 3 ay
- Sertifika maliyeti: $30k-60k

## D5. ISO 27001 sertifikası (Q3 2027)
**Tahmin:** 60h (hazırlık) + 9-12 ay total
**Detay:**
- Türkiye'de TSE veya BSI Türkiye accredited body
- Stage 1 (doküman audit) → Stage 2 (operational audit)
- Kapsam: ISMS + Annex A 18 kontrol grubu
- Maliyet: $15k-30k

## D6. Veri rezidans (Data residency) — EU/TR seçimi
**Tahmin:** 24h
**Detay:**
- Tenant başına region seçimi: TR / EU / global
- Multi-region DB (Oracle Cloud Multi-Region)
- Backup'lar tenant region'unda kalır
- KVKK + GDPR uyum

## D7. Backup encryption AES-256
**Tahmin:** 16h
**Detay:**
- Mevcut backup paneli düz dosya
- AES-256 ile şifreleme (cryptography lib)
- Decrypt password tenant_admin tarafından girilir
- Cloud storage (S3-compatible) entegrasyonu

## D8. Public API + rate limiting per-tenant
**Tahmin:** 24h
**Bağımlılık:** Sprint 43 OpenAPI altyapısı + Sprint 48 data connector
**Detay:**
- API key management (tenant başına quota)
- Per-tenant rate limit (60 req/dakika/user)
- API analytics dashboard (kullanım grafiği)
- Webhook entegrasyon (3rd party app'ler için)

## D9. Anomali tespit AI advisor v2
**Tahmin:** 32h
**Bağımlılık:** Sprint 14 (Z-score) + LLM API
**Detay:**
- Mevcut Z-score basit
- AI v2:
  - LLM root cause öneri ("OEE düşüşü muhtemelen ... nedeniyle")
  - İlişkili KPI'lar cross-analyze
  - Trend prediction (Sprint 46 forecast genişletilmiş)
  - "Bir sonraki çeyrekte bu KPI'nın hedefi tutması için..."

## D10. Multi-language (FR + DE)
**Tahmin:** 40h
**Bağımlılık:** O4 (i18n EN tamamlanmış olmalı)
**Detay:**
- Babel için fr + de locale dosyaları
- Profesyonel çeviri (Türkçeden değil İngilizceden)
- Avrupa pazarı için satış kapısı

---

# 📅 ÖNERİLEN ZAMAN ÇİZELGESİ

## 2026 Haziran (Sprint 53-56) — Kritik + Yüksek
- Hafta 1: K1, K2, K3, K4 (KRİTİK 4 iş, 6h)
- Hafta 2-3: Y1 (process.py sunset 1.805 satır)
- Hafta 4: Y2 (admin.py merge başlangıç)

## 2026 Temmuz (Sprint 57-60) — Yüksek devam + Orta başlangıç
- Hafta 1-2: Y2 (admin.py) + Y3 (auth merge)
- Hafta 3: Y4 (main/routes) + Y5 + Y6 (atomicity test fix + clone)
- Hafta 4: O8 (pagination 10 endpoint) + Y7 (KVKK metin TR/EN)

## 2026 Ağustos-Eylül — Orta yoğun
- O1 (ESG UI), O2 (dashboard builder UI başlangıç)
- O3 (SOC 2 politika doc'ları — paralel iş)
- O4 (i18n tam kapsam)
- O9 (anomali cron) + O11 (AI summary) + O12 (bulk import genişletme)

## 2026 Ekim-Aralık — Diferansiyasyon
- O5 (Mobile + PWA), O6 (Custom RBAC), O7 (Sektör benchmark)
- O10 (KPI versioning)
- D8 (Public API), D9 (AI advisor v2)

## 2027 Q1-Q2 — Compliance + Sertifika
- D4 (SOC 2 Type I başvurusu)
- D5 (ISO 27001 Stage 1)
- D7 (Backup encryption)

## 2027 Q3-Q4 — Yeni modüller + uluslararasılaşma
- D1 (Vendor portal), D2 (Müşteri portali)
- D3 (Eğitim modülü)
- D6 (Data residency), D10 (Multi-language FR/DE)

---

# 🎯 BAŞARI METRIKLERI (2026 sonu hedef)

| Metrik | Şu an | 2026 sonu | Δ |
|---|:-:|:-:|:-:|
| Test sayısı | ~265 | 400+ | +50% |
| Test kapsamı | ~25% → %42 | %60 | +18pp |
| Legacy kod satırı | ~3.940 | <500 | -87% |
| Kritik risk ≥16 | 1 | 0 | -100% |
| Yeni özellik (Q3-Q4 hedef) | — | 8+ | (ESG UI, dashboard builder, AI v2, ...) |
| Compliance | — | SOC 2 Type I başlama | — |

---

# 🚦 PUSH ÖNCELİĞİ

Şu an Sprint 1-52 commit'leri yerel. Push için sıra:

1. ✅ Önce: gerçek Tomofil tenant tarayıcı testi (manuel sanity check)
2. ✅ Sonra: PG yedek al (`pg_dump > backups/`)
3. ✅ Sonra: `git push origin main`
4. ✅ Sonra: Oracle VM'e deploy (`scripts/ops/oracle/oracle_safe_deploy.sh`)
5. ✅ Sonra: VM smoke check (`scripts/vm_smoke_check.ps1`)

Detaylı VM deploy: [docs/YERELDEN_VM_YAYIN.md](YERELDEN_VM_YAYIN.md)

---

> **Doküman versiyon:** v1.0 · 2026-05-24
> **Önümüzdeki güncelleme:** Sprint 53 başında (Haziran 2026)
> **Sorumlu:** Kokpitim DevOps + CTO
