# 📊 STRATEJİK PLAN DÖNEMİ MANTIĞI — DURUM ANALİZİ VE ÖNERİLER

> **Tarih:** 2026-05-24
> **Hazırlama yöntemi:** Mevcut kod incelemesi + uluslararası literatür taraması (10+ kaynak)
> **Kapsam:** PlanYear modeli, clone sistemi, modül entegrasyonu, kullanıcı deneyimi
> **Önemli:** Bu doküman teknik karar destekleyici. Karar yetkisi CTO + Ürün'de.

---

## 🎯 YÖNETİCİ ÖZETİ

Kokpitim'in mevcut **yıllık plan + tam klon** (Full Clone) mimarisi **2010'ların standardı**. Literatür ve sektör lideri SaaS'lar son 3 yılda **sürekli planlama (continuous planning) + yuvarlanır ufuk (rolling horizon) + senaryo-tetikli güncelleme** modeline geçti.

**3 büyük gözlem:**

1. ✅ **Sağlam temel:** PlanYear + Full Clone mimarisi gerçek bir ihtiyaca cevap veriyor (yıl bazlı snapshot, source_*_id zinciri). Tomofil 6-yıllık demo'da çalıştığı doğrulandı.

2. ⚠️ **Yıllık döngü kısıtlı:** "Bir yıl açıldı → 12 ay aynı stratejiyi koru → kapat" döngüsü modern enterprise için yetersiz. Sektör %43 daha fazla revenue growth'u rolling forecast ile elde ediyor ([Aberdeen Group](https://www.cubesoftware.com/blog/rolling-forecast)).

3. 🚀 **Diferansiasyon fırsatı:** Senaryo planlama (what-if) + AI tahminleme + tetikli yeniden planlama Kokpitim'i ClearPoint/Cascade/Quantive seviyesine taşır.

**Önerilen yol:** Mevcut yıllık altyapıyı koruyup üzerine **3 katman** ekle:
- **Çeyreklik review cadence** (built-in workflow, otomatik bildirim)
- **Senaryo planlama** (mevcut yıldan branch'leyip ne-olur-eğer testleri)
- **Tetik-tabanlı revizyon** (anomali → strateji revize teklifi)

---

# 1. MEVCUT YAPI — Durum Tespiti

## 1.1 PlanYear modeli

**Konum:** [app/models/plan_year.py](../app/models/plan_year.py)

```python
PlanYear:
    id, tenant_id, year, name, status, template_source_id, closed_at
    # status: draft | active | closed | archived

KpiYearConfig:        # KPI'nın yıla özgü override
StrategyYearConfig:   # Strategy yıla özgü override
SubStrategyYearConfig
ProcessYearConfig
IndividualKpiYearConfig
```

**Güçlü yön:**
- Her ana entity (Strategy/SubStrategy/Process/ProcessKpi) `plan_year_id` taşır
- `source_*_id` ile önceki yıldaki "ata" kayıt referans alınır → değişim takibi mümkün
- `template_source_id` ile yeni yıl açılırken klonlama desteği
- 5 ayrı `YearConfig` tablosu → hedef/birim/ağırlık yıla özel revize edilebilir

**Zayıf yön:**
- Status sadece 4 değer; modern yaklaşımlarda `forecast`, `revised`, `rolling` da olabilir
- Tek "yıl" birimi var — çeyreklik/altı-aylık alt dönemler model'de yok
- "Bu yılı çatallandır" (branch) gibi senaryo özelliği yok

## 1.2 İki ayrı Clone Sistemi — ÖNEMLİ BULGU

Detaylı kod incelemesi sırasında tespit edildi: aslında **2 farklı klon fonksiyonu** var:

| Fonksiyon | Konum | Klonladığı |
|---|---|---|
| `clone_plan_year` (overlay) | `plan_year_service.py:316-426` | Sadece **YearConfig** tabloları (override değerler) |
| `clone_full_plan_year` (full) | `plan_year_service.py:584-855` | **TÜM entity'ler** + zincir (Strategy/SubStrategy/Process/Kpi/Activity/IndividualKpi/SwotAnalysis/TowsAnalysis/TenantYearIdentity) |

**Seçim:** `plan_year_feature=True` ise full clone, False ise overlay clone (`routes_plan_year.py:123`).

**Sorun:** İki mod arasında **legacy uyumsuzluk** — bazı sorgular `include_null=True` ile overlay'i destekler, bazıları `include_null=False` ile full-clone bekler. Audit'te tespit edilen filter inconsistency (Pattern #1 vs #3) bu iki mod karışımından doğuyor.

**Mantık:** Yeni yıl açıldığında **önceki yılın tüm Strategy/SubStrategy/Process/ProcessKpi kayıtları kopyalanır** (`clone_full_plan_year` fonksiyonu). Her klon `source_*_id` ile orijinaline bağlıdır.

**Tomofil örneği (gerçek veri):**

| Yıl | Strategy | SubStrategy | Process | ProcessKpi |
|:-:|:-:|:-:|:-:|:-:|
| 2021 | 3 | 14 | 6 | 22 |
| 2022 | 3 | 15 | 6 | 24 |
| 2023 | 4 | 17 | 7 | 32 |
| 2024 | 5 | 21 | 8 | 40 |
| 2025 | 6 | 22 | 9 | 46 |
| 2026 | 7 | 23 | 10 | 50 |
| **TOPLAM** | **28** | **112** | **46** | **214** |

**Güçlü yön:**
- Yıl bazlı **bağımsız** veri → tarihsel raporlama kolay
- Strategy değişti diye geçmiş veri bozulmaz
- `source_strategy_id` ile "1.A → 1.A (önceki yıl)" zinciri görselleştirilebilir

**Zayıf yön:**
- **Veri duplikasyonu**: aynı strateji 6 yıl × yıl başına klon = 6x veri
- **Hedef güncellemeleri yıllar arası senkron değil**: 2024'te bir KPI hedefini değiştirsen, 2025 klonunda otomatik yansımaz
- **FK orphan riski**: Klon işleminde hata olursa yarı dolu yıl kalır (Sprint 19 audit'inde tespit)
- **Devam eden inisiyatifler** (multi-year) için "bu strateji 2023'te başladı, 2026'da bitecek" görselleştirmesi yok

## 1.3 plan_year_filter helper (Sprint 1)

**Konum:** [app/utils/plan_year_filter.py](../app/utils/plan_year_filter.py)

```python
filter_by_plan_year(query, model, active_py_id, include_null=True)
```

**Durum:**
- 3 yerde kullanılıyor (sp/routes_pages, sp/routes_flow, surec/routes_process)
- Diğer modüller (k_rapor, bireysel, k_radar) hâlâ kendi `or_(...IS NULL)` pattern'ini kullanıyor → inconsistency

## 1.4 Modüllerde plan_year farkındalığı

| Modül | Farkındalık | Notlar |
|---|:-:|---|
| **sp** | 🟢 Tam | Plan year switcher, klon, karşılaştırma sayfası mevcut |
| **surec** | 🟢 Tam | ProcessKpi.plan_year_id zorunlu; karne yıl-aware |
| **k_radar** | 🟡 Kısmi | RiskHeatmapItem, StakeholderMap, CompetitorAnalysis'de var; ProcessMaturity'de yok |
| **k_rapor** | 🟡 Kısmi | `get_active_plan_year_for_user` çağrılıyor ama bazı yerlerde `year` parametresi hardcoded |
| **bireysel** | 🟢 Tam | IndividualPerformanceIndicator yıl-aware |
| **proje** | 🔴 Eksik | Project.plan_year_id model'de var, UI formda yok (audit bulgusu) |
| **admin** | ⚪ N/A | Plan year değil — sistem yönetimi |

---

# 2. LİTERATÜR — Modern Stratejik Planlama Trendleri

## 2.1 Geleneksel Yıllık vs Sürekli Planlama

| Boyut | Geleneksel (Yıllık) | Modern (Sürekli/Rolling) |
|---|---|---|
| Periyot | 12 ay sabit | 12-18 ay yuvarlanır ufuk |
| Revizyon sıklığı | Yıl sonu | Çeyreklik veya tetik-bazlı |
| Tamamlanma oranı | %12-22 inisiyatif | %43 daha hızlı büyüme |
| Senaryo | Tek "base case" | Multi-scenario (best/worst/likely) |
| Yönetişim | Top-down annual cycle | OODA loop (Observe-Orient-Decide-Act) |

**Kaynak:** [Achieveit — 2024 Strategic Planning Trends](https://www.achieveit.com/resources/blog/the-latest-strategic-planning-and-execution-trends-and-statistics/), [Cube Software — Rolling Forecasts](https://www.cubesoftware.com/blog/rolling-forecast)

> "Organizations are stopping treatment of strategy as an annual document and starting to run it as a **live operating system**." — modern enterprise paradigması

## 2.2 Cadence: 18 aylık döngü trendi

[ClearPoint Strategy](https://www.clearpointstrategy.com/blog/18-month-strategic-planning-cycle) raporu:
- "Annual planning" yerleşik ama geçiş **18-24 aylık rolling**'e doğru
- Kuruluşlar **annual refresh + quarterly rebalance** ikili modeli benimsiyor
- Atlassian, Triskell, Dragonboat platformları **yıl + çeyrek + aylık** üç katmanlı

[Atlassian — Quarterly Planning Guide](https://www.atlassian.com/work-management/strategic-planning/quarterly-planning):
- "Annual = vision, quarterly = strategy, monthly = roadmap review"
- 90 günlük döngü adapte olabilen ekipler için "tatlı nokta"

## 2.3 Framework Entegrasyonu — OKR + BSC + Hoshin Kanri

Modern enterprise tek bir framework değil **hibrit** kullanıyor:

| Framework | Güçlü yönü | Eksiği | Optimal kullanım |
|---|---|---|---|
| **BSC** | Holistic perspektif (finansal/müşteri/süreç/öğrenme) | Yavaş, statik | Yıllık stratejik temel |
| **Hoshin Kanri** | 3-5 yıllık vizyon → yıllık dökm | Karmaşık X-matrix | Multi-year hizalama |
| **OKR** | Çeyreklik agile | Stratejik bağlam eksik | Operasyonel uygulama |

**Entegrasyon önerisi** ([Profit.co](https://www.profit.co/blog/strategy/hoshin-kanri-integration), [I-nexus](https://blog.i-nexus.com/hoshin-kanri-balanced-scorecard)):

```
┌─────────────────────────────────────┐
│  Hoshin Kanri (3-5 yıl)            │  ← Long-term vision
│  Vizyon + Stratejik Çıkış (X-mtx)  │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  Balanced Scorecard (Annual)        │  ← Yıllık denge
│  4 perspektif × KPI                 │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  OKR (Quarterly)                    │  ← Çeyreklik agile
│  Objective + 3-5 KR                 │
└─────────────────────────────────────┘
```

**Kokpitim'in durumu:** Üçü de mevcut (sp + BSC perspektifi + OKR modülü). Sprint 33'te OKR↔KPI bağı kuruldu. **Eksik:** Üçünü tek bir "stratejik ağaç" görsele birleştirmek (cascade).

## 2.4 Senaryo Planlama (Scenario Planning)

[Cascade — Best AI Strategy Platforms](https://www.cascade.app/blog/best-ai-strategy-platforms), [Quantive StrategyAI](https://quantive.com/resources/articles/quantive-strategyai-vs-ai-strategy-platforms):

Modern platformlar 3 tip senaryo sunuyor:

1. **What-if analiz**: "Tedarikçi fiyatları %20 artarsa OEE hedefi nasıl etkilenir?"
2. **Best/Worst/Likely case**: Aynı strateji 3 farklı projeksiyon
3. **Trigger-based replanning**: KPI sapması eşiği aşınca otomatik plan revizyon teklifi

**Kokpitim'de yok.** En yakın özellikler:
- Sprint 46 KPI forecasting (linear regression) — single scenario
- Sprint 14 anomaly detection — alert var ama plan revize akışı yok

## 2.5 AI ile Strateji Pivot

[Cascade — AI Strategy](https://www.cascade.app/blog/best-ai-strategy-platforms):

> "AI-powered strategy platforms identify patterns in historical data, flag unusual changes, and **suggest forecast adjustments**."

**Örnek:** Quantive StrategyAI — kurumsal strateji ağacında AI önerisi: "Bu KPI hedefiniz son 3 çeyrekte %85 sapıyor. Hedefi revize etmeyi mi yoksa stratejik girişim eklemeyi mi öneriyorsunuz?"

**Kokpitim'de:** Sprint 14 (Z-score anomaly), Sprint 46 (forecasting), `ai_advisor_service.py` var ama henüz "strateji önerisi" seviyesinde değil.

---

# 2.6 Kod İnceleme — Olgunluk Skoru

Agent ile yapılan derinlemesine inceleme sonucu (`plan_year_service.py` 883 satır, 11 dosya):

| Boyut | Derece | Notlar |
|---|:-:|---|
| **Model Tasarımı** | 9/10 | 5 YearConfig + full-clone chain kapsamlı |
| **Service Layer** | 8/10 | Fallback iyi, `_compute_prev_year_actuals` yavaş |
| **Filter Tutarlılığı** | 5/10 | 3 farklı pattern, helper %50 entegre |
| **API Tamamlanmışlığı** | 7/10 | CRUD ✅, onay workflow ❌, raporlama ❌ |
| **UI/UX** | 6/10 | Sihirbaz var, dönem seçici unclear |
| **Modül Farkındalığı** | 6/10 | sp/surec ✅, k_rapor/k_radar/bireysel/proje zayıf |
| **Performance** | 6/10 | `get_kpi_configs_bulk()` N+1 fix, clone'da ortalama compute slow |
| **Legacy Uyum** | 7/10 | Overlay + full-clone mix yönetilebilir |

**Genel olgunluk:** %70-75 production-ready.

---

# 3. TESPİT EDİLEN SORUNLAR

| # | Sorun | Etki | Konum |
|:-:|---|:-:|---|
| 1 | Yılı kapatmadan revize akışı yok | 🟠 Y | sp/routes_plan_year |
| 2 | "Bu strateji 2023'te başladı, 2026'da bitecek" multi-year görseli yok | 🟠 Y | UI eksiği |
| 3 | Senaryo planlama (what-if) yok | 🟠 Y | Yeni özellik |
| 4 | Çeyreklik review cadence built-in değil | 🟡 O | Workflow eksiği |
| 5 | plan_year_filter helper %50 entegre | 🟡 O | k_rapor, k_radar, bireysel |
| 6 | Yıl klonlamada hedef güncellemeleri yıllar arası senkron değil | 🟡 O | clone_full_plan_year |
| 7 | Project.plan_year_id UI'da yok | 🟡 O | proje/routes_project_crud |
| 8 | Hoshin Kanri X-Matrix benzeri cascade görseli yok | 🟡 O | sp/routes_flow |
| 9 | Clone atomicity (FK orphan riski) | 🟡 O | Sprint 19 audit |
| 10 | "Bu yıl içinde hedef revize" log+audit eksik | 🟡 O | YearConfig'lere audit |

---

# 4. ÖNERİLER — Önceliklendirilmiş Liste

## 🔴 Sprint 53-55 (1-2 ay) — Akut iyileştirmeler

### Ö1. Çeyreklik review wizard
- `/sp/donemler/ceyreklik-review` yeni sayfa
- Kullanıcı yılı seçer → çeyrek (Q1-Q4) → review checklist
- Sonuç: PDF özet + audit log + tenant_admin'e mail digest
- **Efor:** 12 saat
- **Faydası:** Atlassian/ClearPoint cadence pattern'ı, kurumsal review zorunluluğu

### Ö2. plan_year_filter helper'ı 4 modüle daha entegre
- k_rapor, k_radar (ProcessMaturity hariç), bireysel, proje
- Inconsistency'i sıfırla
- **Efor:** 6 saat (Sprint 1 hazır altyapı, sadece çağırma)

### Ö3. Project.plan_year_id formda göster
- Audit bulgusu (Sprint 1)
- 1-2 dropdown + filtreleme
- **Efor:** 3 saat

## 🟠 Sprint 56-58 (2-3 ay) — Yapısal genişleme

### Ö4. Multi-year Initiative (Cross-Year Strategy)
**Sorun:** "Bu strateji 2023'te başladı, 2026'da bitecek" gösterilemiyor.
**Çözüm:**
- Yeni model: `StrategicInitiative` (cross-year)
  - `start_year`, `target_year`, `progress_pct`
  - 1 → N ilişki: bir initiative → birden fazla yıl içinde stratejilerle bağlı
- UI: Gantt benzeri **multi-year initiative timeline**
- **Efor:** 24 saat

### Ö5. Senaryo Planlama (Scenario Branching)
**Sorun:** "Tedarikçi fiyatları %20 artarsa..." what-if testi yok.
**Çözüm:**
- PlanYear'a `scenario_of_id` field (yeni migration)
- "Mevcut 2026 planından branch yarat" → `Scenario` versiyonu
- Karşılaştırma sayfası: Base vs Scenario A vs Scenario B
- KPI hedef override per scenario
- **Efor:** 32 saat
- **Differentiator:** Quantive/Cascade seviyesinde özellik

### Ö6. Hoshin Kanri X-Matrix görseli
**Sorun:** Cascade hierarchy (vizyon → 3-5 yıllık → yıllık → çeyreklik) tek tabloda görünmüyor.
**Çözüm:**
- `/sp/x-matrix` yeni sayfa
- 4 kadran: Long-term breakthrough × Annual goals × Improvement priorities × Metrics
- Mevcut Strategy + SubStrategy + ProcessKpi + OKR'u birleştir
- **Efor:** 20 saat
- **Faydası:** Hoshin Kanri tabanlı kurumlar için tek görsel

## 🟡 Sprint 59-62 (3-4 ay) — Diferansiasyon

### Ö7. AI-powered Strategy Pivot Önerileri
**Sorun:** Anomali alert var, ama "strateji revize et" akışı yok.
**Çözüm:**
- Sprint 14 anomaly + Sprint 46 forecast + LLM (OpenAI/Anthropic)
- Algoritma:
  1. KPI'da süregelen sapma tespit (Z-score 3+ çeyrek)
  2. İlişkili strategy/sub_strategy bul (linked_sub_strategy_id)
  3. LLM prompt: "Bu KPI'nın trendi şöyle, hangi strateji revizyonu öneriyorsun?"
  4. UI: "AI Önerisi" kartı + onay/reddet
- **Efor:** 40 saat
- **Differentiator:** Quantive StrategyAI seviyesi

### Ö8. Trigger-based Replanning
**Sorun:** Plan revize sadece manuel (kullanıcı çeyrek review'unda).
**Çözüm:**
- Trigger kuralları (admin tanımlar):
  - "Eğer KPI X 3 çeyrek üst üste sapıyorsa → plan revizyon önerisi mail at"
  - "Eğer ESG metric eşik aşıyorsa → sürdürülebilirlik stratejisi gözden geçir"
- APScheduler nightly cron
- **Efor:** 16 saat

### Ö9. Rolling Horizon View
**Sorun:** Kullanıcı sadece tek bir yıla bakıyor; modern yaklaşım yuvarlanır 18 ay.
**Çözüm:**
- `/sp/rolling-view`: bugün ± 18 ay grid
- Geçmiş 6 ay (closed yıl verisi) + mevcut 12 ay (active) + gelecek 6 ay (draft scenario)
- Bir görsel grafikte
- **Efor:** 16 saat

## 🟢 Sprint 63+ (4-6 ay) — Olgunlaşma

### Ö10. Cross-Year Comparison Dashboard
- "2023 OEE vs 2026 OEE — değişim grafiği"
- Mevcut donemler sayfasını genişlet
- **Efor:** 12 saat

### Ö11. Plan Year Templates Marketplace
- "Otomotiv sektörü 5 yıllık şablon" gibi hazır templates
- Tenant yeni yıl açarken seçer
- **Efor:** 24 saat

### Ö12. Strategy DNA (lineage)
- "Bu KPI'nın atası 2021'de hangi stratejiden doğdu?"
- `source_*_id` zincirini visual olarak göster
- **Efor:** 16 saat

---

# 5. MIMARİ ÖNERİLER

## 5.1 Status Enum Genişletmesi

Şu an: `draft | active | closed | archived`

Önerilen:
```python
class PlanYearStatus:
    DRAFT       = "draft"        # Henüz yayınlanmamış
    ACTIVE      = "active"       # Mevcut yıl
    REVISED     = "revised"      # Yıl içinde revize edildi (Ö1)
    SCENARIO    = "scenario"     # Branch'lanmış senaryo (Ö5)
    FORECAST    = "forecast"     # AI tahminli gelecek (Ö7)
    CLOSED      = "closed"       # Tamamlandı
    ARCHIVED    = "archived"     # Soğuk arşiv
```

## 5.2 Yeni Modeller

```python
class StrategicInitiative:  # Ö4
    id, tenant_id, name, description
    start_year, target_year
    health_status  # iyi/risk/kritik

class InitiativeYear:  # Initiative-Year join
    initiative_id, plan_year_id
    progress_pct, notes

class ReplanTrigger:  # Ö8
    id, tenant_id, name
    condition_json  # {"kpi_id": 100, "consecutive_quarters": 3, "z_score_threshold": 2}
    action          # "email" | "ai_suggest" | "auto_revise"
    is_active

class ScenarioBranch:  # Ö5 — PlanYear extension
    # Aslında PlanYear'a scenario_of_id field eklenir, ayrı tablo gerekmez
```

## 5.3 plan_year_filter helper'ı genişletme

```python
# Sprint 1'de yazılan helper'a ek:
def get_rolling_window(user, months_back=6, months_ahead=6):
    """Yuvarlanır ufuk için aktif + komşu yılları döndür."""
    # Ö9 için altyapı
```

---

# 6. UYGULAMA YOL HARİTASI

## Q3 2026 (Ağustos-Ekim)
- Ö1 (Çeyreklik review wizard) — kurumsal cadence için zorunlu
- Ö2 (helper yayılımı) — inconsistency'i sıfırla
- Ö3 (Project plan_year UI) — quick win

## Q4 2026 (Kasım-Ocak)
- Ö4 (Multi-year initiative) — Tomofil senaryosuna katma değer
- Ö9 (Rolling horizon view) — Modern cadence

## Q1 2027 (Şubat-Nisan)
- Ö5 (Scenario branching) — Quantive parity
- Ö6 (X-Matrix) — Hoshin Kanri'li müşteriler için

## Q2 2027 (Mayıs-Temmuz)
- Ö7 (AI strategy pivot) — DIFFERENTIATOR
- Ö8 (Trigger-based replan) — Otomatik

## Q3-Q4 2027
- Ö10-12 (cross-year, templates, DNA) — olgunlaşma

---

# 7. RAKIP KARŞILAŞTIRMA

| Özellik | Kokpitim (mevcut) | Kokpitim (+öneriler) | ClearPoint | Cascade | Quantive |
|---|:-:|:-:|:-:|:-:|:-:|
| Plan year + clone | ✅ | ✅ | ✅ | ✅ | ✅ |
| BSC + OKR + Hoshin | ✅ (kısmi) | ✅ (Ö6) | ⚪ BSC ağırlık | ⚪ OKR ağırlık | ⚪ OKR ağırlık |
| Çeyreklik cadence | ⚠️ | ✅ (Ö1) | ✅ | ✅ | ✅ |
| Multi-year initiative | ❌ | ✅ (Ö4) | ✅ | ✅ | ⚪ |
| Senaryo planlama | ❌ | ✅ (Ö5) | ✅ | ✅ | ✅ |
| AI strategy pivot | ❌ | ✅ (Ö7) | ⚪ | ✅ | ✅ (StrategyAI) |
| Trigger-based replan | ❌ | ✅ (Ö8) | ⚠️ | ⚠️ | ✅ |
| Rolling horizon view | ❌ | ✅ (Ö9) | ✅ | ⚪ | ✅ |
| Multi-tenant + KVKK | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ |
| Türkçe native + sektör benchmark | ✅ | ✅ | ❌ | ❌ | ❌ |

**Sonuç:** Önerilen 9 iş yapılırsa Kokpitim, dünya çapında ilk 5 enterprise platform paritesine ulaşır + Türkçe pazarda **lider konumda kalır**.

---

# 8. SONUÇ

Mevcut PlanYear mantığı **mühendislik olarak sağlam** ama **ürün stratejisi olarak zamanın gerisinde**. Yıllık döngü 2010'larda standartken, 2024-2026'da sektör **çeyreklik agile + senaryo + AI** üçlüsüne geçti.

**3 anahtar öneri:**

1. **Hemen (Q3 2026):** Çeyreklik review cadence (Ö1) + helper yayılımı (Ö2)
2. **Orta vade (Q4 2026 - Q1 2027):** Multi-year initiative (Ö4) + Scenario branching (Ö5)
3. **Uzun vade (Q2-Q4 2027):** AI strategy pivot (Ö7) + Trigger-based replan (Ö8)

**Toplam efor:** ~228 saat (28 iş günü = 6 sprint × 2 hafta + buffer)

**Beklenen sonuç:** Pazar konumu **fast-follower → kategori lideri** (Türkçe enterprise SaaS pazarında).

---

## Kaynaklar

### Literatür
- [The Rise of the 18-Month Strategic Planning Cycle — ClearPoint Strategy](https://www.clearpointstrategy.com/blog/18-month-strategic-planning-cycle)
- [Strategic Planning Trends 2024 — Achieveit](https://www.achieveit.com/resources/blog/the-latest-strategic-planning-and-execution-trends-and-statistics/)
- [Rolling Forecast Best Practices — Cube Software](https://www.cubesoftware.com/blog/rolling-forecast)
- [Quarterly Planning Guide — Atlassian](https://www.atlassian.com/work-management/strategic-planning/quarterly-planning)

### Framework Entegrasyonu
- [Integrating Hoshin Kanri with OKRs, BSC, and Lean — Profit.co](https://www.profit.co/blog/strategy/hoshin-kanri-integration)
- [Hoshin Kanri + Balanced Scorecard — I-Nexus](https://blog.i-nexus.com/hoshin-kanri-balanced-scorecard)
- [Hoshin Kanri, BSC, OKR comparison — Amplon](https://amplon.io/hoshin-kanri-okr-and-bsc-compared/)

### Senaryo Planlama & AI
- [Best AI Strategy Platforms 2026 — Cascade](https://www.cascade.app/blog/best-ai-strategy-platforms)
- [Quantive StrategyAI vs Other Platforms](https://quantive.com/resources/articles/quantive-strategyai-vs-ai-strategy-platforms)
- [Top 10 Scenario Planning Tools 2026 — Epicflow](https://www.epicflow.com/blog/scenario-planning-tools/)

### Cadence & Trigger-Based
- [Strategic Planning Rhythm Explained — Umbrex](https://umbrex.com/resources/frameworks/strategy-frameworks/strategic-planning-rhythm/)
- [Quarterly Planning Cadence — Dragonboat](https://dragonboat.io/blog/quarterly-planning-cadence-aligns-agile-teams/)

### Software Karşılaştırma
- [Best Strategy Execution Software 2026 — GWork.io](https://gwork.io/blog/best-strategy-execution-software/)
- [7 Best Strategic Planning Software 2025 — Quantive](https://quantive.com/resources/articles/best-strategic-planning-software)
- [Best Strategic Planning Software 2024 — OnStrategy](https://onstrategyhq.com/strategic-planning-software/best-strategic-planning-software/)

### Mevcut Sistem Kaynakları (Kokpitim iç)
- [PROJE-AUDIT-2026Q2.md](PROJE-AUDIT-2026Q2.md) — Sprint 1 ardından audit
- [SPRINT-RAPORU-2026Q2.md](SPRINT-RAPORU-2026Q2.md) — Sprint 1-9 sonuç
- [KALAN-EKSIKLER-2026Q2.md](KALAN-EKSIKLER-2026Q2.md) — Mevcut açık iş listesi

---

> **Doküman versiyon:** v1.0 · 2026-05-24
> **Önerilen güncelleme:** Q4 2026 — uygulama sonuçları sonrası revize
> **İlgili kişiler:** CTO, Ürün Yöneticisi, Stratejik Planlama Uzmanı
