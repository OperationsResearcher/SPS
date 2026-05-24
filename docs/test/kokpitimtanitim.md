# Kokpitim — Kapsamlı Proje Tanıtım Belgesi

> **Versiyon:** 1.0
> **Tarih:** 2026-05-24
> **Hedef Kitle:** Projeye yeni katılan geliştirici, yatırımcı, müşteri demosu, UX testçisi
> **Amaç:** "Kokpitim nedir, ne yapar, hangi bileşenleri var, nasıl çalışır" sorularına eksiksiz cevap

---

## İçindekiler

1. [Kokpitim Nedir?](#1-kokpitim-nedir)
2. [Kim İçin?](#2-kim-için)
3. [Hangi Sorunları Çözer?](#3-hangi-sorunları-çözer)
4. [Mimari Tasarım](#4-mimari-tasarım)
5. [Modül Haritası](#5-modül-haritası)
6. [Veri Modeli](#6-veri-modeli)
7. [Kullanıcı Tipleri ve Yetkiler](#7-kullanıcı-tipleri-ve-yetkiler)
8. [Sayfa ve Bileşen Envanteri](#8-sayfa-ve-bileşen-envanteri)
9. [AI/LLM Sistemi](#9-aillm-sistemi)
10. [Plan Year Sistemi](#10-plan-year-sistemi)
11. [Sık Sorulan Sorular](#11-sık-sorulan-sorular)
12. [Teknik Mimari](#12-teknik-mimari)

---

## 1. Kokpitim Nedir?

**Kokpitim**, kurumların stratejik planlama, KPI takibi ve performans yönetimi süreçlerini tek bir platformda birleştiren **çok kiracılı (multi-tenant) B2B SaaS** uygulamasıdır.

Akademik standartlar (BSC, OKR, Hoshin Kanri, Blue Ocean, VRIO, EFQM) ile pratik operasyonel ihtiyaçları (KPI veri girişi, faaliyet takibi, proje yönetimi) tek arayüzde birleştirir. Türkçe-first tasarımı, KVKK uyumu ve Türk pazarına özel düzenlemelere (5018, TSRS, SBB) yerel desteği ile global rakiplerden (Cascade, Quantive, ClearPoint) ayrışır.

**Bir cümlede:** "Stratejik vizyonu operasyonel KPI'lara, KPI'ları bireysel hedeflere bağlayan, kurumsal performans işletim sistemi."

---

## 2. Kim İçin?

| Hedef Kitle | Tipik Kurum | Asıl Faydası |
|---|---|---|
| **Orta-büyük özel sektör** | 100-500 kişilik üretim, hizmet, finans şirketleri | BSC + OKR birarada, ESG raporlama hazır |
| **Kamu kurumları** | Belediyeler (50K+ nüfus), bakanlık genel müdürlükleri | 5018 sayılı Kanun + SBB Stratejik Plan Hazırlama Kılavuzu uyumlu şablon |
| **BIST sürdürülebilirlik şirketleri** | ~100 BIST 25 + diğer ESG raporlayanları | TSRS uyumlu native ESG modülü |
| **KOBİ** | 25-100 kişilik dijitalleşen şirketler | KOSGEB Dijital Dönüşüm Desteği uyumlu |

---

## 3. Hangi Sorunları Çözer?

### 3.1 Strateji Yürütme Açığı (Strategy Execution Gap)
**Sorun:** Stratejik plan kâğıt üstünde kalır, günlük iş ona göre yürümez.
**Kokpitim çözümü:** Strateji → Alt Strateji → Süreç → KPI → Bireysel Hedef otomatik bağlantısı. Her gün veri girişinde stratejik etki anlık ölçülür.

### 3.2 Çok Çerçeveli Yönetim (BSC + OKR + Hoshin)
**Sorun:** Bir kurum hem BSC perspektifleri hem OKR çeyrek hedefleri tutmak istiyorsa, ikisini Excel'de elle bağlamak zorunda.
**Kokpitim çözümü:** Üçü de native, aynı veri kaynağından beslenir. Tek tıkla aynı KPI hem BSC "Finansal Perspektif"e hem OKR Key Result'a hem Strategy Cascade'e bağlanır.

### 3.3 ESG/TSRS Raporlama Yükü
**Sorun:** TSRS (Türkiye Sürdürülebilirlik Raporlama Standartları) 2026'da zorunlu hale geldi. KAP'a açıklama yapmayan şirketlere 70.920 TL/yıl ceza.
**Kokpitim çözümü:** Native ESG modülü (E/S/G kategorileri + Scope 1/2/3) + KAP uyumlu PDF çıktısı.

### 3.4 Multi-Year Initiative Takibi
**Sorun:** "Dijital Dönüşüm 2026-2028" gibi 3 yıllık programlar yıllık plan yıllarına sığmaz.
**Kokpitim çözümü:** Initiative modeli — start_year/end_year ile yıllık plandan bağımsız yaşam döngüsü.

### 3.5 Scenario Planning (What-if Analizi)
**Sorun:** "Optimist senaryoda bu yatırımı yaparsak; kötümser senaryoda bu pivot'a hazır mıyız?" sorusu için ayrı Excel'ler.
**Kokpitim çözümü:** PlanYear'dan dallandırılan scenario_of_id sistemi — baseline + optimistic + pessimistic paralel dallar.

### 3.6 Erken Uyarı ve Otomatik Replan
**Sorun:** KPI'lar düşmeye başladığı an müdahale gecikir.
**Kokpitim çözümü:** ReplanTrigger motoru — "2 ardışık dönem hedef altı" gibi kurallar otomatik tetiklenir, AI Pivot Advisor öneri üretir.

---

## 4. Mimari Tasarım

### 4.1 Multi-Tenant Mantığı

Her şirket bir **tenant**. Veri izolasyonu **tüm tablolarda `tenant_id`** kolonu ile sağlanır. Her sorguya otomatik tenant filtresi uygulanır (decorator'lar + helper'lar).

```
tenants
  ├── users (tenant_id)
  ├── plan_years (tenant_id)
  │   ├── strategies (tenant_id, plan_year_id)
  │   ├── processes (tenant_id, plan_year_id)
  │   ├── plan_projects (plan_year_id)
  │   └── initiative_milestones (initiative_id → tenants)
  ├── initiatives (tenant_id)
  ├── replan_triggers (tenant_id)
  ├── blue_ocean_canvases (tenant_id)
  ├── vrio_resources (tenant_id)
  ├── llm_usage_logs (tenant_id)
  └── tenant_llm_configs (tenant_id, BYOK key)
```

**Sonuç:** Tenant A'nın verisi Tenant B'ye **hiçbir koşulda** sızmaz. Veri izolasyonu DB seviyesinde garanti altında.

### 4.2 Plan Year Sistemi (Full Clone + Scenario Branching)

Stratejik planlama doğası gereği yıllıktır. Her yıl yeni bir **PlanYear** açılır. İki klonlama modeli:

- **Full Clone:** Önceki yılın tüm stratejilerini, süreçlerini, KPI'larını yeni yıla kopyalar. `source_*_id` zinciri orjini takip eder.
- **Scenario Branching:** Aynı yıl içinde paralel senaryolar (baseline/optimistic/pessimistic). Partial unique index sayesinde aynı yıla birden fazla scenario PlanYear yer alabilir.

### 4.3 Blueprint Mimarisi (Flask)

Tüm rotalar **tek bir blueprint** altında: `app_bp` (`/micro` prefix).
Modüller (`micro/modules/`) bu blueprint'e import edilerek registered olur.

```
micro_bp (app_bp)
  ├── /sp/*              (Stratejik Planlama)
  ├── /surec/*           (Süreç Yönetimi)
  ├── /process/*         (Süreç — modern URL)
  ├── /k_radar/*         (KPI Radar)
  ├── /k_rapor/*         (KPI Rapor)
  ├── /project/*         (Proje Yönetimi)
  ├── /bireysel/*        (Bireysel Karne)
  ├── /kurum/*           (Kurum Ayarları)
  ├── /admin/*           (Sistem Yönetimi)
  ├── /masaustu          (Dashboard)
  ├── /bildirim/*        (Bildirimler)
  ├── /ayarlar/*         (Kişisel Ayarlar)
  └── /auth/*            (Login/Profil)
```

---

## 5. Modül Haritası

### 5.1 Stratejik Planlama (`/sp`)

**Sorumluluğu:** Stratejik plan oluşturma, takip, senaryo yönetimi, akademik çerçeveler.

**Alt sayfalar (kullanıcı için görünür):**
| URL | Sayfa | İşlev |
|---|---|---|
| `/sp` | Ana sayfa | Vizyon/Misyon/Değerler + strateji ağacı (akış olgunluk göstergesi) |
| `/sp/donemler` | Plan Yılları | Yıl oluşturma, klonlama, kapatma, aktifleştirme |
| `/sp/sihirbaz/yeni-yil` | Yeni Yıl Sihirbazı | Önceki yıldan klon önizleme + uygulama |
| `/sp/templates` | Şablon Marketplace | SBB Kamu, OKR vb. hazır şablonlar |
| `/sp/strateji-haritasi` | Strateji Haritası | vis-network grafik (Strategy↔SubStrategy↔Process↔KPI↔Initiative) |
| `/sp/xmatrix` | Hoshin X-Matrix | 4 çeyrek korelasyon matrisi |
| `/sp/blue-ocean` | Blue Ocean Canvas | Strategy Canvas (Chart.js) + ERRC Grid |
| `/sp/vrio` | VRIO Analizi | Kaynak/yetenek matrisi + Barney etiketi |
| `/sp/initiatives` | Initiative'ler | Çok yıllı stratejik girişimler |
| `/sp/scenarios` | Senaryolar | What-if dalları (baseline/optimistic/pessimistic) |
| `/sp/replan-triggers` | Replan Trigger | Otomatik replan kuralları |
| `/sp/ceyreklik-review` | Çeyreklik Review | Strateji sağlık skoru + AI özet |
| `/sp/exec-dashboard` | Exec Dashboard | Hero + 6 KPI tile + AI Pivot |
| `/sp/ayarlar/ai` | AI Ayarları | BYOK key + provider seçimi |
| `/sp/llm-usage` | LLM Kullanım | Token tüketim + maliyet özeti |
| `/sp/digest/weekly.pdf` | Haftalık Rapor | PDF özet |
| `/sp/okr` | OKR | Objective + Key Result yönetimi |
| `/sp/misyon`, `/sp/vizyon`, `/sp/degerler` | Kurumsal Kimlik | Yıla özgü metinler |

**Veri modeli:**
- `Strategy`, `SubStrategy`, `PlanYear`, `KpiYearConfig`, `StrategyYearConfig`
- `Initiative`, `InitiativeMilestone`
- `ReplanTrigger`, `ReplanTriggerEvent`
- `BlueOceanCanvas`, `BlueOceanFactor`, `BlueOceanERRC`
- `VRIOResource`
- `OkrObjective`, `OkrKeyResult`

### 5.2 Süreç Yönetimi (`/surec`, `/process`)

**Sorumluluğu:** Süreç tanımlama, KPI yönetimi, periyodik veri girişi, faaliyet takibi.

| URL | Sayfa | İşlev |
|---|---|---|
| `/process` | Süreç listesi | Tüm süreçler + filtreleme |
| `/process/<id>/karne` | Süreç Karnesi | KPI veri girişi (12 aylık matris) |
| `/process/<id>/faaliyetler` | Faaliyetler | Operasyonel görev takibi |

**Veri modeli:**
- `Process`, `ProcessKpi`, `KpiData`, `KpiDataAudit`
- `ProcessActivity`, `ProcessActivityAssignee`
- `ProcessSubStrategyLink` (contribution_pct ile)

### 5.3 K-Radar (`/k_radar`)

**Sorumluluğu:** KPI sağlık göstergeleri, risk, anomali, kalite parametreleri.

| URL | İşlev |
|---|---|
| `/k_radar` | Hub — özet kartlar |
| `/k_radar/risk` | Risk register + heat map |
| `/k_radar/cross/paydas` | Paydaş analizi |
| `/k_radar/cross/a3` | A3 problem solving |
| `/k_radar/cross/rekabet` | Rekabet analizi |
| `/k_radar/kp/darbogaz`, `/k_radar/kp/oee`, `/k_radar/kp/vsm`, vb. | KP modülleri |
| `/k_radar/kpr/cpm`, `/k_radar/kpr/evm` | Proje radar |
| `/k_radar/ks/swot-summary`, `/ks/bsc`, `/ks/hoshin` | Strateji analiz |

### 5.4 K-Rapor (`/k_rapor`)

**Sorumluluğu:** Raporlama, trend analizi, Excel/PDF export, anomali tespiti.

30+ API endpoint: trend, forecast, kurumsal, uyum, faaliyet, risk, denetim, k-vektor, EVM, paydaş analizi, rekabet, PG dağılımı, vb.

### 5.5 Proje Yönetimi (`/project`)

**Sorumluluğu:** Proje portföyü, görev takibi, Gantt/Kanban, EVM.

| URL | İşlev |
|---|---|
| `/project/list` | Proje listesi |
| `/project/<id>` | Proje detay |
| `/project/<id>/views/gantt` | Gantt görünümü |
| `/project/<id>/views/kanban` | Kanban board |
| `/project/<id>/views/raid` | RAID log (Risks/Assumptions/Issues/Dependencies) |
| `/project/<id>/views/calendar` | Takvim |
| `/sp/api/projects/<id>/evm` | EVM metrikleri (PV/EV/AC/CPI/SPI/EAC) + CPM kritik yol |

**Veri modeli:**
- `PlanProject`, `PlanProjectTask`, `PlanProjectActivity`
- `Project`, `Task`, `RaidItem` (modern portföy modeli)

### 5.6 Bireysel Performans (`/bireysel`)

**Sorumluluğu:** Kişisel KPI karnesi, bireysel hedefler, faaliyet takibi.

| URL | İşlev |
|---|---|
| `/bireysel` | Ana sayfa |
| `/bireysel/karne` | 12 aylık kişisel KPI tablosu |

**Veri modeli:**
- `IndividualPerformanceIndicator`
- `IndividualActivity`, `IndividualActivityTrack`
- `IndividualKpiData`, `FavoriteKpi`

### 5.7 Kurum (`/kurum`)

**Sorumluluğu:** Kurum profili, logo, vizyon/misyon/değerler.

### 5.8 Admin (`/admin`)

**Sorumluluğu:** Kullanıcı yönetimi, tenant yönetimi, paket, yedekleme, bakım modu.

### 5.9 Masaüstü (`/masaustu`)

**Sorumluluğu:** Kişisel dashboard — bildirim, eksik veri, takvim, hızlı linkler.

### 5.10 Diğerleri
- **`/bildirim`** — Bildirim merkezi
- **`/ayarlar/eposta`, `/ayarlar/yedekleme`** — Kişisel ayarlar
- **`/auth/login`, `/auth/profil`** — Kimlik
- **`/api/v1/*`** — REST API (Swagger)
- **`/api/v1/dataconn/*`** — Power BI / Tableau JSON connector

---

## 6. Veri Modeli

### 6.1 Çekirdek Tablolar

```
Tenant ─┬── User (n)
        ├── PlanYear (n)
        │   ├── Strategy (n)
        │   │   └── SubStrategy (n)
        │   │       └── ProcessSubStrategyLink (m:n with Process)
        │   ├── Process (n)
        │   │   ├── ProcessKpi (n)
        │   │   │   └── KpiData (n) [aylık/dönemsel]
        │   │   ├── ProcessActivity (n)
        │   │   └── members/leaders/owners (m:n)
        │   ├── PlanProject (n)
        │   │   ├── PlanProjectTask (progress + budget)
        │   │   └── PlanProjectActivity
        │   └── TenantYearIdentity (1, mission/vision/values)
        ├── Initiative (n) — start_year/end_year
        │   └── InitiativeMilestone (n)
        ├── ReplanTrigger (n)
        │   └── ReplanTriggerEvent (n)
        ├── BlueOceanCanvas (n)
        │   ├── BlueOceanFactor (n)
        │   └── BlueOceanERRC (n)
        ├── VRIOResource (n)
        ├── LLMUsageLog (n) [her AI çağrısı]
        ├── LLMQuotaOverride (1)
        ├── TenantLLMConfig (1, BYOK key)
        └── SubscriptionPackage
```

### 6.2 Önemli İlişkiler

- **`source_*_id` zinciri:** PlanYear klonlandığında her kayıt önceki yıldaki aslına işaret eder. Lineage takibi için kritik.
- **`scenario_of_id`:** PlanYear başka bir PlanYear'ın senaryosu mu? NULL ise ana plan, dolu ise scenario branch.
- **`plan_year_id` her veri tablosunda:** Yıllar arasında veri karışmasın diye.
- **`tenant_id` her temel tabloda:** Multi-tenant izolasyon garantisi.

### 6.3 Migration Geçmişi

Sprint bazlı önemli migration'lar:
- `y2z3a4b5c006` — Plan year tabloları
- `a4b5c6d7e008` — Initiative + Milestone
- `b5c6d7e8f009` — Scenario branching (partial unique index)
- `c6d7e8f9g010` — Replan triggers
- `d7e8f9g0h011` — Blue Ocean + VRIO
- `e8f9g0h1i012` — Task EVM alanları
- `f9g0h1i2j013` — LLM usage + quota
- `g0h1i2j3k014` — Tenant LLM config (BYOK)

---

## 7. Kullanıcı Tipleri ve Yetkiler

### 7.1 Rol Hiyerarşisi

| Rol | Kapsam | Yetki |
|---|---|---|
| **Admin** (platform sahibi) | Tüm tenant'lar | Sistem yönetimi, bakım modu, paket yönetimi |
| **tenant_admin** | Tek tenant | Tüm SP işlemleri, kullanıcı yönetimi, kurum ayarları |
| **executive_manager** | Tek tenant | tenant_admin ile aynı SP yetkileri + üst yönetim raporları |
| **ust_yonetim** | Tek tenant | SP modülüne yönetim erişimi |
| **kurum_yoneticisi** | Tek tenant | Kurum ayarları |
| **surec_lideri** | Atandığı süreçler | Süreç KPI yönetimi, veri giriş |
| **kalite** | Atandığı süreçler | Süreç yönetimi |
| **manager** | Atandığı kullanıcılar | Bireysel raporlama |
| **kurum_kullanici** | Kendi verileri | Bireysel karne, atandığı süreç KPI veri girişi |
| **izleyici** | Görüntüleme | Sadece read-only |

### 7.2 Yetki Kontrol Mekanizmaları

- `@login_required` — Her korunan rotada zorunlu
- `_check_sp_role()` — SP modülü erişimi (`helpers.py:41-48`)
- `@sp_manage_required` decorator — SP yazma yetkisi
- `_admin_backup_guard()` — Admin-only yedekleme
- `_is_admin_or_tenant_admin()` — Admin paneli erişimi
- `PRIVILEGED_ROLES` — Proje modülü ({"Admin", "tenant_admin", "executive_manager"})

---

## 8. Sayfa ve Bileşen Envanteri

Toplam **76 aktif sayfa**, **684 rota**. Sayfa tipleri:

### 8.1 Dashboard Sayfaları
- `/masaustu` — Kişisel dashboard (FullCalendar widget + 4 stat kartı + 13 alt bölüm)
- `/sp/exec-dashboard` — Üst yönetim hero kart + 6 KPI tile + AI Pivot panel
- `/k_radar` — KPI radar hub
- `/k_rapor` — Raporlama dashboard

### 8.2 Veri Giriş Sayfaları
- `/bireysel/karne` — 12 aylık matris (kişisel)
- `/process/<id>/karne` — 12 aylık matris (süreç)
- `/sp/sihirbaz/yeni-yil` — Multi-step wizard

### 8.3 Analiz Sayfaları
- `/sp/xmatrix` — 4 çeyrek HTML tablosu (Strategy↔SubStrategy↔Initiative↔KPI)
- `/sp/blue-ocean` — Chart.js Value Curve + ERRC 4-kadran grid
- `/sp/vrio` — Canlı checkbox tablosu + Barney etiketi
- `/sp/strateji-haritasi` — vis-network interaktif grafik

### 8.4 CRUD Sayfaları
- `/sp/initiatives` — Liste + modal form
- `/sp/scenarios` — Liste + dallandırma form
- `/sp/replan-triggers` — CRUD + "Şimdi Değerlendir" butonu
- `/project/list`, `/project/new`, `/project/<id>/edit` — Proje yaşam döngüsü
- `/admin/yonetim-paneli/kullanici-detay` — Kullanıcı CRUD

### 8.5 Görselleştirme Bileşenleri

| Bileşen | Kütüphane | Nerede |
|---|---|---|
| Çizgi/Bar grafik | Chart.js 4.4 | Exec dashboard, Blue Ocean, k_rapor trend |
| Network/Graph | vis-network | Strateji haritası, dynamic flow |
| Gantt | Custom | Proje gantt view |
| Kanban | Custom | Proje kanban view |
| FullCalendar | FullCalendar.js | Masaüstü takvim |
| Modal | mc-modal CSS | Tüm CRUD işlemleri (KURALLAR §5) |
| Toast | SweetAlert2 | Bildirim, başarı/hata mesajı |
| Skeleton loader | CSS `@keyframes mc-shimmer` | Exec dashboard tile'lar |

### 8.6 Tasarım Sistemi

- **Renk paleti:** Indigo (#4f46e5) + Slate gri + semantic (success/warning/danger)
- **Tipografi:** Inter font, 10 boyut tokeni (text-2xs→text-display)
- **Spacing:** 8'in katları (4/8/12/16/20/24/32/40)
- **Tema:** Light + Dark (`html.dark` override)
- **CSS framework:** Tailwind CDN + custom `mc-*` component library (components.css 1.3K satır)
- **Sayfa rehberi:** Sidebar (240px sabit, koyu indigo) + topbar (beyaz)

Detaylı kural seti: [`docs/UI-KILAVUZU.md`](../UI-KILAVUZU.md)

---

## 9. AI/LLM Sistemi

### 9.1 LLM Gateway (Provider-Agnostic)

Tüm AI çağrıları tek geçitten geçer: `app/services/llm_gateway.py`

```python
from app.services.llm_gateway import call_llm

result = call_llm(
    tenant_id=current_user.tenant_id,
    endpoint="ai_pivot",
    prompt=user_prompt,
    system_prompt="Sen kıdemli strateji danışmanısın...",
)
# result = {text, source, provider, model, usage, quota_summary, ...}
```

### 9.2 Desteklenen Sağlayıcılar

| Provider | Default Model | Maliyet (1M token) |
|---|---|---|
| **Gemini** | `gemini-2.5-flash-lite` | $0.10/$0.40 (giriş/çıkış) |
| **OpenAI** | `gpt-4o-mini` | $0.15/$0.60 |
| **Anthropic** | `claude-haiku-4-5` | $1.00/$5.00 |
| **Groq** | `llama-3.3-70b-versatile` | $0.59/$0.79 |
| **OpenRouter** | `google/gemini-2.0-flash-exp:free` | 0 (ücretsiz katman) |

### 9.3 Anahtar Çözüm Sırası

```
1. Tenant BYOK key var mı + aktif mi?  → Tenant key kullan (kendi faturası)
2. Sistem default key var mı (env)?    → Sistem key (kotalı)
3. Hiçbiri yok                          → text=None, caller heuristic'e düşer
```

### 9.4 Kota Sistemi (4 Katmanlı)

| Katman | Varsayılan | Override |
|---|---|---|
| Cooldown (aynı tenant + endpoint) | 30 sn | Tenant override tablosu |
| Tenant günlük çağrı | 50 | Aynı |
| Tenant aylık çağrı | 500 | Aynı |
| Tenant aylık maliyet USD | $2 | Aynı |
| Sistem geneli günlük | 1.000 | env: `LLM_QUOTA_LIMITS` |
| Sistem aylık maliyet | $50 | env |
| Alarm eşiği | %80 | env |

### 9.5 Endpoint Kategorileri

| Kod | Hangi Servis | Tipik Token |
|---|---|---|
| `ai_pivot` | Strategy Pivot Advisor | ~2.000 |
| `ai_coach` | Bireysel performans koçluğu | ~1.500 |
| `ai_summary` | Yönetici özet | ~3.000 |
| `ai_early_warning` | Erken uyarı | ~1.000 |
| `ai_advisor` | Strateji danışmanı | ~2.500 |

### 9.6 BYOK (Bring Your Own Key)

Tenant kendi API anahtarını `/sp/ayarlar/ai` sayfasından girer. Fernet ile şifreli saklanır. Kullandığında **sistem kotası harcanmaz**, kendi sağlayıcı faturasından düşer.

### 9.7 Politika Belgesi

Tüm detay: [`docs/AI-POLITIKASI.md`](../AI-POLITIKASI.md) (13 bölüm, sözleşme niteliğinde).

---

## 10. Plan Year Sistemi

### 10.1 Yaşam Döngüsü

```
draft → active → closed → archived
```

### 10.2 Klonlama Modları

**A) Overlay Clone (`clone_plan_year`)**: Sadece YearConfig kayıtları açar, ana entity'ler yeniden kullanılır.

**B) Full Clone (`clone_full_plan_year`)**: Tüm strateji, alt strateji, süreç, KPI, faaliyet, proje yeniden yaratılır. `source_*_id` zinciri ile orijini takip eder.

### 10.3 Scenario Branching

Aynı yıla birden fazla PlanYear (baseline + optimistic + pessimistic). Partial unique index: `WHERE scenario_of_id IS NULL`.

```sql
CREATE UNIQUE INDEX uq_plan_year_tenant_year_main
ON plan_years (tenant_id, year)
WHERE scenario_of_id IS NULL;
```

Senaryolar bu kısıtın dışında — istediğiniz kadar açılabilir.

### 10.4 Year Config Override

Klonlanmış kayıtlar üstüne yıllık config tabloları (KpiYearConfig, StrategyYearConfig, ProcessYearConfig) override edilebilir. Örnek: bir KPI'nın 2026 hedefi 100, 2027'de 120 olabilir — KPI'nın kendisi değişmez, sadece YearConfig.

---

## 11. Sık Sorulan Sorular

### S1: "Bir KPI nasıl izlenir?"
1. Yönetici **ProcessKpi** tanımlar (hedef, ölçüm birimi, dönem)
2. Atanan kullanıcı periyodik veri girer → `kpi_data` tablosu
3. K-Radar/K-Rapor grafik + trend + uyarı gösterir
4. Anomali (z-score ≥ 2.0) tespit edilirse Replan Trigger devreye girebilir

### S2: "Yıllık plan nasıl yenilenir?"
1. Yönetici `/sp/sihirbaz/yeni-yil` açar
2. Kaynak yılı seçer
3. Önizleme: Hangi stratejiler/süreçler klonlanacak
4. Uygula → tüm yapı yeni `PlanYear`'a kopyalanır (`source_*_id` zinciri ile)
5. Yeni yıl `draft` status'ta açılır, üzerinde değişiklik yapılır
6. Hazır olunca `active` yapılır, önceki yıl `closed` olur

### S3: "Senaryo planlama ne demek?"
Tek bir plan yılından alternatif gelecek varyasyonları üretmek. Örnek: "2027 baseline" + "2027 optimistic (yatırım büyütülürse)" + "2027 pessimistic (kriz olursa)". Her senaryo bağımsız KPI hedefi, Initiative listesi, kaynak dağılımı tutar. Exec dashboard'da karşılaştırılır.

### S4: "Initiative nedir, strateji ile farkı ne?"
- **Strategy:** Uzun vadeli kurumsal yön (3-5 yıl), göreceli sabit
- **Initiative:** Belirli bir değişimi gerçekleştirmek için açılan, bütçeli, dönemli, sorumluluğa atanmış proje-benzeri girişim. `start_year` ve `end_year` olur, milestone'lara bölünür. Plan year'dan bağımsız yaşam döngüsü.

### S5: "Çeyreklik review niye var?"
Modern strateji cadence pattern'ı:
- **Yıllık:** Vizyon ve ana strateji (sabit)
- **Çeyreklik:** Strateji ayarlama, pivot kararı
- **Aylık:** Roadmap iyileştirme, operasyonel düzeltme

`/sp/ceyreklik-review` çeyrek özet üretir: KPI sağlığı, Initiative ilerleme, Risk değişimi, Anomali listesi, Trigger event'leri → karar tablosu.

### S6: "Replan trigger nasıl çalışır?"
Admin trigger tanımlar (`/sp/replan-triggers`):
- Tip: `kpi_below_target`, `overdue_activity_pct`, `risk_score`, `anomaly_high`
- Koşul: KPI ID + threshold + consecutive_periods
- Aksiyon: `notify` / `suggest_pivot` / `create_review`

"Şimdi Değerlendir" butonu (veya cron) çalışınca koşullar kontrol edilir, tetiklenen trigger'lar için `ReplanTriggerEvent` kaydı açılır, AI Pivot Advisor çağrılır.

### S7: "Stratejik sağlık skoru nasıl hesaplanır?"

`build_exec_snapshot()` içinde ağırlıklı 4 boyut:

| Boyut | Ağırlık | Formül |
|---|---:|---|
| KPI hedef üstü | %40 | `on_target_pct × 0.4` |
| KPI veri kapsama | %20 | `(with_data/total) × 100 × 0.2` |
| Faaliyet vaktinde | %20 | `(100 - overdue%) × 0.2` |
| Sıfır kritik risk | %10 | varsa +10 |
| Sıfır yüksek anomali | %10 | varsa +10 |

**Sonuç:** 0-100 arası composite skor.

**Bu basit bir heuristic.** Sektör spesifik benchmark, geçmiş trend, vizyon ağırlığı yok. Olgunlaşma için: docs'taki ileri model önerileri.

### S8: "AI önerileri güvenilir mi?"
- **Sistem garantisi:** LLM yoksa heuristic motor çalışır, sistem hiçbir zaman çökmez
- **Bağlam:** Şu an sadece tenant'ın güncel snapshot'ı gönderiliyor — sektör/tarihçe/vizyon yok. Bu yüzden öneriler "genelci"
- **Karar mekanizması:** Öneri ekrana basılıyor — otomatik aksiyon almıyor. Insan yöneticisi karar verir
- **Şeffaflık:** Hangi LLM kullanıldı, kaç token harcandı, maliyet ne — UI'da görünür

**Doğru kullanım:** Öneriyi "akıllı görünen 1. seviye danışman" gibi alın. Stratejik kararı uygulamadan önce kendiniz değerlendirin.

### S9: "Veri güvenliği nasıl sağlanıyor?"
- **Multi-tenant izolasyon:** Tüm sorgularda `tenant_id` filtresi zorunlu
- **CSRF koruması:** Flask-WTF, JSON API'lerde `@csrf.exempt` ile bypass (login_required + tenant_id ile yeterli)
- **HTTPS:** Production'da Talisman ile zorunlu
- **CSP:** Content Security Policy headers
- **Şifre hash:** Werkzeug PBKDF2
- **2FA:** TOTP destekli
- **Audit log:** AuditLog tablosu (login, kritik aksiyon)
- **LLM key:** Fernet şifreli (`SECRET_KEY` türevi)

### S10: "Mobil cihazdan kullanılabilir mi?"
- Responsive design (Tailwind breakpoint'leri)
- Sidebar mobile'da hamburger menüye dönüşür
- Tabletler için optimal (CEO/CFO iPad senaryosu)
- Mobil özel app yok — web responsive

---

## 12. Teknik Mimari

### 12.1 Teknoloji Stack

| Katman | Teknoloji |
|---|---|
| **Backend** | Python 3.13, Flask 3.1, SQLAlchemy 2.0 |
| **Database** | PostgreSQL (production), SQLite (geliştirme yedek) |
| **Migration** | Alembic |
| **Cache** | Flask-Caching (Redis production) |
| **Rate Limit** | Flask-Limiter (Redis production) |
| **Auth** | Flask-Login + pyotp (TOTP) + Authlib (Google OAuth) |
| **Frontend** | Jinja2 templates + Tailwind CDN + Alpine.js |
| **Chart** | Chart.js 4.4, vis-network |
| **Modal/Toast** | SweetAlert2 11 + custom `mc-modal` |
| **PDF** | WeasyPrint → reportlab fallback |
| **WSGI Server** | Waitress (production), Werkzeug (dev) |
| **AI** | google-generativeai, openai, anthropic SDKs |
| **Container** | Docker (Oracle VM production) |
| **SSL** | pip-system-certs (Windows uyumu için) |

### 12.2 Dosya Yapısı

```
kokpitim/
├── app/
│   ├── models/              # Tüm SQLAlchemy modelleri
│   ├── services/            # İş mantığı katmanı
│   │   ├── llm_gateway.py
│   │   ├── llm_quota_service.py
│   │   ├── ai_pivot_advisor_service.py
│   │   ├── exec_dashboard_service.py
│   │   ├── hoshin_xmatrix_service.py
│   │   ├── project_evm_service.py
│   │   ├── weekly_digest_service.py
│   │   ├── plan_year_service.py
│   │   ├── plan_year_template_service.py
│   │   └── ...
│   ├── templates_data/      # JSON şablonlar (SBB Kamu vb.)
│   └── utils/               # Yardımcılar (security, plan_year_filter, vb.)
├── micro/modules/           # Blueprint modülleri
│   ├── sp/                  # Stratejik Planlama
│   ├── surec/               # Süreç Yönetimi
│   ├── k_radar/             # KPI Radar
│   ├── k_rapor/             # Raporlama
│   ├── proje/               # Proje Yönetimi
│   ├── bireysel/            # Bireysel Karne
│   ├── kurum/               # Kurum Ayarları
│   ├── admin/               # Sistem Yönetimi
│   ├── shared/              # Auth, ayarlar, bildirim
│   └── ...
├── ui/templates/platform/   # Jinja2 templateler
│   ├── base.html
│   ├── sp/                  # 18 sayfa
│   ├── surec/               # 3 sayfa
│   ├── k_radar/             # 16 sayfa
│   ├── proje/               # 9 sayfa
│   └── ...
├── ui/static/platform/      # CSS, JS, vendor
│   ├── css/
│   │   ├── components.css   # Tasarım sistemi (1.3K satır)
│   │   ├── sidebar.css
│   │   └── ...
│   └── js/
├── platform_core/           # Blueprint registry
├── extensions.py            # Flask extensions
├── config.py                # Konfigürasyon
├── app.py                   # Entry point (port 5001)
├── migrations/versions/     # Alembic
├── docs/                    # Dokümantasyon
│   ├── AI-POLITIKASI.md
│   ├── UI-KILAVUZU.md
│   ├── KURALLAR-MASTER.md
│   └── test/                # Bu dosya + kılavuzlar
├── scripts/ops/oracle/      # VM deploy script'leri
└── requirements*.txt        # Bağımlılıklar
```

### 12.3 Geliştirme Akışı

- **Branch disiplini:** `claude/<konu>` veya `feature/<konu>` → main'e `--no-ff` merge
- **Commit kalıbı:** Conventional Commits (`feat(sp): ...`, `fix(...)`, `docs(...)`)
- **Co-author:** Claude tarafından yapılan değişikliklerde `Co-Authored-By: Claude Opus 4.7`
- **Tag stratejisi:** `baseline-YYYY-MM-DD` (stabil nokta), `deploy-YYYY-MM-DD` (VM'e gönderim)
- **TASKLOG:** Her görev sonunda `docs/TASKLOG.md`'ye kayıt

### 12.4 Deploy Akışı

1. Yerelde test edilmiş kod main'e merge edilir
2. `git push origin main`
3. VM'de `ssh ubuntu@129.159.30.175`
4. `cd /opt/kokpitim/app && sudo bash scripts/ops/oracle/oracle_safe_deploy.sh`
5. Script: PostgreSQL yedeği + git pull + Docker rebuild + Alembic upgrade + satır sayısı doğrulama

### 12.5 Performans

- **N+1 koruması:** selectinload, joinedload her query'de
- **Index'ler:** tenant_id, plan_year_id, process_id, created_at sık filtre kolonlarında
- **Cache:** KPI trend (1 saat), tenant config (30 dk)
- **Connection pool:** SQLAlchemy pool_size=20, max_overflow=40

---

## Belge Hakkında

Bu belge yaşayan bir doküman. Yeni özellik eklendiğinde, yeni sayfa açıldığında bu belge güncellenir.

**Bağlantılı belgeler:**
- [`docs/UI-KILAVUZU.md`](../UI-KILAVUZU.md) — Tasarım sistemi
- [`docs/AI-POLITIKASI.md`](../AI-POLITIKASI.md) — AI çağrı kuralları
- [`docs/KURALLAR-MASTER.md`](../KURALLAR-MASTER.md) — Kodlama disiplini
- [`docs/test/tenant_admin_kullanim_kilavuzu.md`](tenant_admin_kullanim_kilavuzu.md) — Admin kılavuzu
- [`docs/test/tenant_kullanici_kilavuzu.md`](tenant_kullanici_kilavuzu.md) — Standart kullanıcı kılavuzu

**Sorular için:** Bu belgede cevap bulamıyorsanız `docs/` klasörünü inceleyin veya proje ekibine sorun.
