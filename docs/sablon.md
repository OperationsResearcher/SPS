# 📋 KOKPİTİM — DEMO TENANT OLUŞTURMA ŞABLONU

> **Amaç:** Yeni bir demo/örnek tenant açmak için gereken **tüm** bilgilerin doldurulabilir boş şablonu.
> **Doldurma kuralı:** `<DOLDUR>` alanlarına gerçek değer yaz. **Zorunlu** bölümler eksik kalamaz. **Opsiyonel** bölümlerde işin amacına göre satır ekle/sil.
> **Format:** Markdown — istersen JSON/CSV blokları olarak da doldurabilirsin.
> **Hedef DB:** PostgreSQL `kokpitim_db` (yerel) → onay sonrası Oracle VM.

---

## ✅ Hızlı Kapsam Kontrolü

Doldurmaya başlamadan önce **hangi modüllerin** etkin olacağına karar ver. ✓ işaretle:

| Modül | Açıklama | Etkin? |
|-------|----------|--------|
| ⭐ Tenant Kimliği | Şirket bilgileri, vizyon, değerler | ☐ (zorunlu) |
| ⭐ Plan Yılları | Çoklu yıl (2026-2035 vb.) | ☐ (zorunlu) |
| ⭐ Stratejik Plan | Ana + Alt Stratejiler | ☐ (zorunlu) |
| ⭐ Süreçler + KPI'lar | İş süreçleri ve performans göstergeleri | ☐ (zorunlu) |
| ⭐ Kullanıcılar | Yöneticiler, süreç sahipleri, çalışanlar | ☐ (zorunlu) |
| 🔵 KPI Geçmiş Veri | Aylık/çeyrek dönem ölçümleri | ☐ |
| 🔵 Süreç Faaliyetleri | Aksiyon planları | ☐ |
| 🔵 Proje Portföyü | Stratejik projeler + görevler | ☐ |
| 🔵 Bireysel PG | Çalışan performans göstergeleri | ☐ |
| 🔵 SWOT / TOWS | Stratejik analiz | ☐ |
| 🔵 PESTEL | Dış çevre analizi | ☐ |
| 🔵 Porter 5 Force | Rekabet analizi | ☐ |
| 🔵 OKR | Objectives + Key Results | ☐ |
| 🔵 K-Vektor | Stratejik ağırlık konfigürasyonu | ☐ |
| 🔵 K-Radar | Olgunluk, darboğaz, değer zinciri, risk haritası, paydaş, A3, rakip | ☐ |
| 🔵 SMTP / E-posta | Özel SMTP bildirim ayarları | ☐ |
| 🔵 Logo / Marka | Görsel kimlik dosyaları | ☐ |

⭐ = zorunlu · 🔵 = opsiyonel (boş bırakırsan seed atlanır)

---

# 1️⃣ TENANT KİMLİĞİ (⭐ ZORUNLU)

> Tabloya yazılır: `tenants`

```yaml
name:              "<DOLDUR — tam tüzel kişilik adı, ör: Tomofil Group N.V.>"
short_name:        "<DOLDUR — slug/kısa ad, 64 karakter, ör: Tomofil>"
sector:            "<DOLDUR — Otomotiv / Eğitim / Sağlık / Üretim / Hizmet vb.>"
activity_area:     "<DOLDUR — Faaliyet alanı, ör: Sürdürülebilir Elektrikli Araç Üretimi>"
employee_count:    <DOLDUR — toplam çalışan sayısı, integer>
contact_email:     "<DOLDUR — info@firma.com>"
phone_number:      "<DOLDUR — +90 ... veya boş>"
website_url:       "<DOLDUR — https://... veya boş>"
tax_office:        "<DOLDUR — vergi dairesi veya boş>"
tax_number:        "<DOLDUR — vergi no veya boş>"
max_user_count:    <DOLDUR — lisans tavanı, ör: 5000>
license_end_date:  "<DOLDUR — YYYY-MM-DD veya boş>"

# Stratejik kimlik (uzun metin / Markdown destekli)
vision:            "<DOLDUR — kurumun 5-10 yıllık vizyon cümlesi>"
purpose:           "<DOLDUR — kurumun varlık amacı / misyon>"
core_values:       "<DOLDUR — virgülle ayrılmış değerler veya kısa paragraf>"
code_of_ethics:    "<DOLDUR — etik kurallar paragrafı veya boş>"
quality_policy:    "<DOLDUR — kalite politikası veya boş>"

# Modül anahtarları (Boolean)
plan_year_enabled: true       # Yıllık plan sistemi
plan_year_start:   <DOLDUR — geçmiş yıl başlangıcı, ör: 2026>
k_vektor_enabled:  <true/false — stratejik ağırlık modülü>
k_radar_enabled:   <true/false — operasyonel risk/olgunluk modülü>

# Lisans paketi (id)
package_id:        1   # 1 = Master Package (varsayılan)
```

---

# 2️⃣ TENANT ADMİN KULLANICISI (⭐ ZORUNLU)

> Tabloya yazılır: `users` (role_id=3 → tenant_admin)

```yaml
admin_email:     "<DOLDUR — admin@firma.test>"
admin_password:  "<DOLDUR — Firma2026! gibi güçlü şifre>"
admin_first_name: "<DOLDUR — ör: Firma>"
admin_last_name:  "<DOLDUR — ör: Admin>"
admin_phone:      "<DOLDUR — telefon veya boş>"
admin_job_title:  "<DOLDUR — Tenant Yöneticisi>"
admin_department: "<DOLDUR — Yönetim>"
```

---

# 3️⃣ PLAN YILLARI (⭐ ZORUNLU)

> Tabloya yazılır: `plan_years` — her yıl için 1 kayıt

```yaml
plan_years:
  - year: <DOLDUR>     # ör: 2026
    name: "<DOLDUR>"   # ör: "2026 Stratejik Planı"
    status: "active"   # active | draft | closed | archived
  - year: 2027
    name: "2027 Stratejik Planı"
    status: "draft"
  # ... gerektiği kadar ekle
```

**Kural:** Aynı anda sadece **1 yıl** `active` olmalı, geri kalan `draft`.

---

# 4️⃣ STRATEJİK PLAN — ANA + ALT STRATEJİLER (⭐ ZORUNLU)

> Tablolar: `strategies` (Ana) + `sub_strategies` (Alt — kod prefiksiyle 2 seviye)

**Yapı:**
- Ana Strateji (Strategy) → kod: `H1`, `H2`, `ST1` gibi
- Alt Strateji L1 (SubStrategy) → kod: `1.A`, `1.B`, `H1.1` gibi
- Alt Strateji L2 (SubStrategy) → kod: `1.A.1`, `1.A.2` gibi (prefiks hiyerarşi)

```yaml
strategies:
  - code: "<DOLDUR — H1>"
    title: "<DOLDUR — Ana Strateji başlığı (max 200)>"
    description: "<DOLDUR — kısa açıklama veya boş>"
    sub_strategies:
      # L1 — birinci seviye alt strateji
      - code: "<DOLDUR — 1.A>"
        title: "<DOLDUR>"
        description: "<DOLDUR veya boş>"
      - code: "<DOLDUR — 1.A.1>"        # L2 — ikinci seviye (prefiks 1.A ile başlar)
        title: "<DOLDUR>"
        description: "<DOLDUR veya boş>"
      - code: "<DOLDUR — 1.A.2>"
        title: "<DOLDUR>"
        description: "<DOLDUR veya boş>"
      - code: "<DOLDUR — 1.B>"
        title: "<DOLDUR>"
        description: ""
      # ...
  - code: "<DOLDUR — H2>"
    title: "<DOLDUR>"
    description: ""
    sub_strategies: []
  # ...
```

**Öneri sayım:** 4-10 Ana Strateji, her birinin altında 2-5 L1, her L1 altında 0-5 L2.

---

# 5️⃣ SÜREÇLER (⭐ ZORUNLU)

> Tabloya yazılır: `processes`

```yaml
processes:
  - code: "<DOLDUR — A2R / SR1 / P01 gibi>"
    name: "<DOLDUR — Türkçe ad, ör: Müşteri Edinme ve Tutma>"
    english_name: "<DOLDUR — opsiyonel İngilizce ad>"
    description: "<DOLDUR — sürecin kısa açıklaması veya boş>"
    weight: <DOLDUR — 0-100 arası ağırlık, toplam=100 olmalı, opsiyonel>
    document_no: "<DOLDUR — opsiyonel doküman no>"
    revision_no: "<DOLDUR — opsiyonel revizyon no>"
    revision_date: "<DOLDUR — YYYY-MM-DD veya boş>"
    first_publish_date: "<DOLDUR — YYYY-MM-DD veya boş>"
    start_boundary: "<DOLDUR — sürecin başlangıç sınırı, opsiyonel>"
    end_boundary: "<DOLDUR — sürecin bitiş sınırı, opsiyonel>"
    # Hangi alt stratejilere katkı sağlıyor:
    linked_sub_strategy_codes: ["<DOLDUR — 1.A.1>", "<1.B.2>"]   # opsiyonel
    # Sahip / Lider / Üyeler (kullanıcı bölümündeki email'lerden seç):
    owners:  ["<DOLDUR — uzman.kisi@firma.test>"]
    leaders: ["<DOLDUR>"]
    members: ["<DOLDUR>", "<...>"]
  - code: "<DOLDUR>"
    name: "<DOLDUR>"
    # ...
```

---

# 6️⃣ PROCESS KPI'LAR (⭐ ZORUNLU)

> Tabloya yazılır: `process_kpis`

```yaml
process_kpis:
  - process_code: "<DOLDUR — yukarıdaki süreç kodu>"
    code: "<DOLDUR — PG-01>"
    name: "<DOLDUR — PG adı, ör: OEE (Overall Equipment Effectiveness)>"
    description: "<DOLDUR — ne ölçtüğü>"
    unit: "<DOLDUR — %, adet, gün, TL, vb.>"
    period: "<DOLDUR — Aylık / Çeyreklik / Yıllık>"
    target_value: "<DOLDUR — 92 / %15+ / 5500 gibi string olarak>"
    direction: "<Increasing / Decreasing>"
    weight: <DOLDUR — 0-100 ağırlık>
    is_important: <true/false>
    gosterge_turu: "<İyileştirme / Koruma / Bilgi Amaçlı>"
    target_method: "<RG / HKY / HK / SH / DH / SGH>"
    data_source: "<DOLDUR — veri kaynağı, ör: ERP/MES sistemi>"
    target_setting_method: "<DOLDUR — hedef belirleme yöntemi>"
    data_collection_method: "<Toplama / Ortalama / Son Değer>"
    calculation_method: "<AVG / SUM / LAST>"
    # Hangi alt strateji ile ilişkili:
    linked_sub_strategy_code: "<DOLDUR — 1.A.1 veya boş>"
    onceki_yil_ortalamasi: <DOLDUR — sayı veya boş>
    basari_puani_araliklari: |
      <DOLDUR — JSON formatında başarı puanı aralıkları veya boş>
      Örnek: {"1":"0-40","2":"41-60","3":"61-75","4":"76-90","5":"91-100"}
  # ... her süreç için 3-10 KPI önerilir
```

---

# 7️⃣ KULLANICILAR (⭐ ZORUNLU)

> Tabloya yazılır: `users`

**Format seçimi:** Az sayıda kullanıcı için aşağıdaki YAML'ı doldur. Büyük listeler (>50 kullanıcı) için ayrı JSON/CSV dosyası kullan ve aşağıya yolunu yaz.

```yaml
# Toplu dosya yolu (varsa)
users_bulk_file: "<DOLDUR — docs/<tenant>/calisanlar.json veya boş>"
users_password_default: "<DOLDUR — toplu yüklemede default şifre, ör: Firma2026!>"

# Tek tek kullanıcılar (manuel)
users:
  - email: "<DOLDUR — ad.soyad@firma.test>"
    password: "<DOLDUR — Firma2026!>"
    first_name: "<DOLDUR>"
    last_name: "<DOLDUR>"
    role: "<tenant_admin / executive_manager / standard_user>"
    job_title: "<DOLDUR — ör: Üretim Müdürü>"
    department: "<DOLDUR — ör: Üretim>"
    phone_number: "<DOLDUR veya boş>"
    # Süreç bağı (atanacağı süreç kodları)
    process_codes: ["<DOLDUR>", "<...>"]
    raci_role: "<R / A / C / I>"
  - email: "<DOLDUR>"
    # ...
```

**Toplu yükleme JSON formatı** (kullanıyorsan):
```json
{
  "calisanlar": [
    {
      "id": 1001,
      "ad_soyad": "Ahmet Yılmaz",
      "cinsiyet": "E",
      "milliyet": "TR",
      "unvan": "Üretim Müdürü",
      "kademe": "Yönetici",
      "departman": "Üretim",
      "lokasyon": "İstanbul",
      "surec_kodu": "P2M",
      "raci_rol": "R",
      "kpi": "OEE ≥ %92"
    }
  ]
}
```

---

# 8️⃣ KPI GEÇMİŞ VERİ — DÖNEMSEL ÖLÇÜMLER (🔵 OPSİYONEL)

> Tabloya yazılır: `kpi_data`

```yaml
kpi_data:
  - process_kpi_code: "<DOLDUR>"
    year: <DOLDUR — 2025>
    period_type: "<Monthly / Quarterly / Yearly>"
    period_no: <DOLDUR — 1-12 ay / 1-4 çeyrek / 1 yıl>
    target_value: <DOLDUR — sayı>
    actual_value: <DOLDUR — sayı>
    description: "<DOLDUR — opsiyonel açıklama>"
  # ...
```

**Toplu yükleme (atomik veri JSON):** Bursa örneğindeki gibi `tenant_veriler.json` formatı destekleniyor → modül başına agregasyon yapılır.

```yaml
kpi_data_bulk_file: "<DOLDUR — docs/<tenant>/veriler.json veya boş>"
```

---

# 9️⃣ SÜREÇ FAALİYETLERİ (🔵 OPSİYONEL)

> Tabloya yazılır: `process_activities`

```yaml
process_activities:
  - process_code: "<DOLDUR>"
    name: "<DOLDUR — faaliyet adı>"
    description: "<DOLDUR>"
    start_date: "<YYYY-MM-DD>"
    end_date: "<YYYY-MM-DD>"
    status: "<Planlandı / Devam Ediyor / Tamamlandı>"
    progress: <DOLDUR — 0-100>
    assignees: ["<email>", "<email>"]
    linked_kpi_code: "<DOLDUR veya boş>"
  # ...
```

---

# 🔟 BİREYSEL PERFORMANS GÖSTERGELERİ (🔵 OPSİYONEL)

> Tabloya yazılır: `individual_performance_indicators`

```yaml
individual_performance_indicators:
  - user_email: "<DOLDUR>"
    name: "<DOLDUR — bireysel PG adı>"
    target_value: "<DOLDUR>"
    unit: "<DOLDUR>"
    period: "<Aylık / Çeyreklik / Yıllık>"
    weight: <0-100>
    linked_process_kpi_code: "<DOLDUR veya boş>"
  # ...
```

---

# 1️⃣1️⃣ PROJE PORTFÖYÜ (🔵 OPSİYONEL)

> Tablolar: `project`, `task`

```yaml
projects:
  - name: "<DOLDUR — proje adı>"
    description: "<DOLDUR>"
    start_date: "<YYYY-MM-DD>"
    end_date: "<YYYY-MM-DD>"
    priority: "<Düşük / Orta / Yüksek>"
    manager_email: "<DOLDUR>"
    health_status: "<İyi / Risk / Kritik>"
    linked_sub_strategy_codes: ["<DOLDUR>"]
    tasks:
      - title: "<DOLDUR — görev başlığı>"
        description: "<DOLDUR>"
        assignee_email: "<DOLDUR>"
        start_date: "<YYYY-MM-DD>"
        end_date: "<YYYY-MM-DD>"
        status: "<Yapılacak / Devam Ediyor / Tamamlandı>"
        priority: "<Low / Medium / High>"
      # ...
  # ...
```

---

# 1️⃣2️⃣ SWOT ANALİZİ (🔵 OPSİYONEL)

> Tabloya yazılır: `swot_analyses` (her plan yılı için 1 kayıt)

```yaml
swot:
  plan_year: <DOLDUR — ör: 2026>
  strengths:      "<DOLDUR — Güçlü Yönler (S), satır satır veya paragraf>"
  weaknesses:     "<DOLDUR — Zayıf Yönler (W)>"
  opportunities:  "<DOLDUR — Fırsatlar (O)>"
  threats:        "<DOLDUR — Tehditler (T)>"
```

---

# 1️⃣3️⃣ TOWS ANALİZİ (🔵 OPSİYONEL)

> Tabloya yazılır: `tows_analyses`

```yaml
tows:
  plan_year: <DOLDUR>
  so_strategies: "<DOLDUR — Güçlü Yönler × Fırsatlar (saldırgan)>"
  st_strategies: "<DOLDUR — Güçlü Yönler × Tehditler (savunmacı)>"
  wo_strategies: "<DOLDUR — Zayıf Yönler × Fırsatlar (geliştirici)>"
  wt_strategies: "<DOLDUR — Zayıf Yönler × Tehditler (kaçınma)>"
```

---

# 1️⃣4️⃣ PESTEL ANALİZİ (🔵 OPSİYONEL)

> Tabloya yazılır: `pestel_analyses`

```yaml
pestel:
  plan_year: <DOLDUR>
  political:     "<DOLDUR — Siyasi faktörler>"
  economic:      "<DOLDUR — Ekonomik faktörler>"
  social:        "<DOLDUR — Sosyal faktörler>"
  technological: "<DOLDUR — Teknolojik faktörler>"
  environmental: "<DOLDUR — Çevresel faktörler>"
  legal:         "<DOLDUR — Yasal faktörler>"
```

---

# 1️⃣5️⃣ PORTER 5 GÜÇ ANALİZİ (🔵 OPSİYONEL)

> Tabloya yazılır: `porter_analyses`

```yaml
porter:
  plan_year: <DOLDUR>
  rivalry_intensity:  "<DOLDUR — Sektör Rekabet Yoğunluğu>"
  supplier_power:     "<DOLDUR — Tedarikçi Gücü>"
  buyer_power:        "<DOLDUR — Alıcı Gücü>"
  new_entrant_threat: "<DOLDUR — Yeni Giriş Tehdidi>"
  substitute_threat:  "<DOLDUR — İkame Ürün Tehdidi>"
```

---

# 1️⃣6️⃣ OKR — OBJECTIVES + KEY RESULTS (🔵 OPSİYONEL)

> Tablolar: `okr_objectives`, `okr_key_results`

```yaml
okrs:
  - plan_year: <DOLDUR — 2026>
    quarter: <DOLDUR — 1/2/3/4 veya null (yıllık)>
    title: "<DOLDUR — Objective başlığı>"
    description: "<DOLDUR>"
    owner: "<DOLDUR — sorumlu kişi veya ekip>"
    key_results:
      - title: "<DOLDUR — KR>"
        metric: "<DOLDUR — %, adet, TL, vb.>"
        start_value: <DOLDUR — sayı>
        target_value: <DOLDUR — sayı>
        current_value: <DOLDUR — sayı veya boş>
      # ...
  # ...
```

---

# 1️⃣7️⃣ K-VEKTOR — STRATEJİK AĞIRLIKLAR (🔵 OPSİYONEL)

> Tablolar: `k_vektor_strategy_weights`, `k_vektor_sub_strategy_weights`

```yaml
k_vektor_weights:
  strategies:
    - code: "<DOLDUR — H1>"
      weight: <DOLDUR — 0-100, toplam=100>
    # ...
  sub_strategies:
    - code: "<DOLDUR — 1.A.1>"
      weight: <DOLDUR — 0-100 (aynı parent içinde toplam=100)>
    # ...
```

---

# 1️⃣8️⃣ K-RADAR MODÜLLERİ (🔵 OPSİYONEL)

### 18.a Süreç Olgunluk (CMMI vb.) — `process_maturity`
```yaml
process_maturity:
  - process_code: "<DOLDUR>"
    maturity_level: <DOLDUR — 1-5>
    dimension: "<DOLDUR — opsiyonel boyut adı>"
    assessed_by: "<DOLDUR — email veya boş>"
```

### 18.b Darboğaz Logu — `bottleneck_log`
```yaml
bottlenecks:
  - process_code: "<DOLDUR>"
    kpi_code: "<DOLDUR veya boş>"
    severity: "<Düşük / Orta / Yüksek / Kritik>"
    note: "<DOLDUR>"
    triggered_at: "<YYYY-MM-DD>"
    resolved_at: "<YYYY-MM-DD veya boş>"
```

### 18.c Değer Zinciri — `value_chain_items`
```yaml
value_chain:
  - category: "<primary / support>"
    title: "<DOLDUR — ör: Operasyonlar, İK Yönetimi>"
    linked_process_code: "<DOLDUR veya boş>"
    muda_type: "<DOLDUR — 7 muda türünden biri veya boş>"
    note: "<DOLDUR veya boş>"
```

### 18.d EVM Snapshot — `evm_snapshots` (proje varsa)
```yaml
evm_snapshots:
  - project_name: "<DOLDUR — yukarıdaki proje adı>"
    snapshot_date: "<YYYY-MM-DD>"
    pv: <Planned Value>
    ev: <Earned Value>
    ac: <Actual Cost>
    spi: <Schedule Performance Index>
    cpi: <Cost Performance Index>
```

### 18.e Risk Isı Haritası — `risk_heatmap_items`
```yaml
risks:
  - plan_year: <DOLDUR>
    title: "<DOLDUR — risk başlığı>"
    probability: <1-5>
    impact: <1-5>
    owner_email: "<DOLDUR>"
    status: "<Open / Mitigating / Closed>"
    source_type: "<DOLDUR — pestel / process / project vb.>"
```

### 18.f Paydaş Haritası — `stakeholder_maps`
```yaml
stakeholders:
  - plan_year: <DOLDUR>
    name: "<DOLDUR — paydaş adı>"
    role: "<DOLDUR — müşteri / tedarikçi / regülatör vb.>"
    influence: <1-5>
    interest: <1-5>
    strategy: "<Manage Closely / Keep Satisfied / Keep Informed / Monitor>"
```

### 18.g Paydaş Anketleri — `stakeholder_surveys`
```yaml
stakeholder_surveys:
  - stakeholder_type: "<DOLDUR>"
    period: "<2026-Q1>"
    score: <0-100>
    comment: "<DOLDUR>"
    source: "<DOLDUR — NPS / CSAT vb.>"
```

### 18.h A3 Raporları — `a3_reports`
```yaml
a3_reports:
  - source_type: "<process / project / kpi>"
    problem: "<DOLDUR>"
    root_cause_json: "<DOLDUR — 5-Why JSON veya boş>"
    countermeasures: "<DOLDUR>"
```

### 18.i Rakip Analizi — `competitor_analyses`
```yaml
competitors:
  - plan_year: <DOLDUR>
    competitor_name: "<DOLDUR>"
    dimension: "<DOLDUR — fiyat / kalite / hizmet vb.>"
    our_score: <0-100>
    their_score: <0-100>
```

---

# 1️⃣9️⃣ E-POSTA / SMTP YAPILANDIRMASI (🔵 OPSİYONEL)

> Tabloya yazılır: `tenant_email_configs`

```yaml
email_config:
  use_custom_smtp: <true/false>
  smtp_host:    "<DOLDUR — smtp.gmail.com gibi>"
  smtp_port:    <587 / 465>
  smtp_use_tls: <true/false>
  smtp_use_ssl: <true/false>
  smtp_username: "<DOLDUR>"
  smtp_password: "<DOLDUR — düz, kod tarafında şifrelenecek>"
  sender_name:  "<DOLDUR — ör: Kokpitim - Firma Adı>"
  sender_email: "<DOLDUR — bildirim@firma.com>"
  notify_on_process_assign: <true/false>
  notify_on_kpi_change:     <true/false>
  notify_on_activity_add:   <true/false>
  notify_on_task_assign:    <true/false>
```

---

# 2️⃣0️⃣ LOGO / MARKA VARLIKLARI (🔵 OPSİYONEL)

```yaml
logo:
  source_file: "<DOLDUR — docs/<tenant>/logo.png veya boş>"
  # Seed sırasında instance/uploads/tenant_logos/<tenant_id>.png olarak kopyalanır
```

---

# 2️⃣1️⃣ KAYNAK DÖKÜMANLAR (referans)

Seed sırasında kullanılacak / arşivlenecek dosyalar:

```yaml
documents:
  strategy_md:       "<DOLDUR — strateji ağacı markdown yolu veya boş>"
  employees_json:    "<DOLDUR — çalışan listesi JSON yolu veya boş>"
  raw_data_json:     "<DOLDUR — atomik veri JSON yolu veya boş>"
  company_pdf:       "<DOLDUR — şirket dosyası PDF yolu veya boş>"
  strategic_plan_pdf:"<DOLDUR — stratejik plan PDF yolu veya boş>"
  other_files:       []
```

---

# 📐 SEED ÇIKTI ÖNGÖRÜSÜ

Şablon doldurulup script çalıştırıldığında oluşacak DB satırları:

| Tablo | Min | Max | Senin değerin |
|-------|-----|-----|----------------|
| tenants | 1 | 1 | 1 |
| plan_years | 1 | 20 | `<plan_years sayısı>` |
| users (admin dahil) | 2 | sınırsız | `<users sayısı + 1>` |
| roles | 0 (mevcut) | — | — |
| strategies | 1 | 30 | `<strategies sayısı>` |
| sub_strategies | 0 | 200 | `<sub_strategies toplam>` |
| processes | 1 | 50 | `<processes sayısı>` |
| process_kpis | 1 | 500 | `<kpis sayısı>` |
| process_owners_table | 1 | — | `<owners sayısı>` |
| kpi_data | 0 | binlerce | `<kpi_data sayısı>` |
| process_activities | 0 | yüzlerce | — |
| individual_performance_indicators | 0 | yüzlerce | — |
| project | 0 | onlarca | — |
| swot/tows/pestel/porter | 0 | plan_year×1 | — |
| okr_objectives + okr_key_results | 0 | onlarca | — |
| k_vektor_weights | 0 | strategies+sub_strategies | — |
| risk_heatmap_items, value_chain_items, ... | 0 | onlarca | — |
| tenant_email_configs | 0 | 1 | 0 veya 1 |

---

# 🚦 SEED ÖNCESİ KONTROL LİSTESİ

Şablonu doldurduktan sonra sıraya koy:

1. ☐ Tenant `name` ve `short_name` benzersiz mi? (mevcut 18 tenant ile çakışmıyor)
2. ☐ Admin e-postası `users.email` unique alanını ihlal etmiyor mu?
3. ☐ Plan yıllarından **sadece 1 tanesi** `active` mi?
4. ☐ Tüm Ana Strateji kodları benzersiz mi?
5. ☐ Tüm Alt Strateji kodları benzersiz mi? (kod prefix hiyerarşisi tutarlı mı?)
6. ☐ Tüm Süreç kodları benzersiz mi?
7. ☐ KPI'ların `process_code`'u tanımlı bir sürece işaret ediyor mu?
8. ☐ Kullanıcı email'leri `@<tenant>.test` formatında ve unique mi?
9. ☐ `process_codes` / `linked_kpi_code` / `assignee_email` çapraz referanslar geçerli mi?
10. ☐ Logo dosyası belirtildiyse gerçekten var mı?
11. ☐ JSON/CSV toplu dosyalar `docs/<tenant>/` klasörüne kopyalandı mı?

---

# 📞 SONRAKİ ADIM

Şablon doldurulduktan sonra:

```bash
# Önce dry-run (DB'ye yazmadan rapor)
python scripts/seed_generic_tenant.py --template docs/<tenant>/sablon-dolu.md --dry-run

# Sorun yoksa commit
python scripts/seed_generic_tenant.py --template docs/<tenant>/sablon-dolu.md --commit

# Hata olursa veya baştan başlamak için
python scripts/seed_generic_tenant.py --template docs/<tenant>/sablon-dolu.md --reset --commit
```

> **Not:** `scripts/seed_generic_tenant.py` henüz yazılmadı. Tomofil'de elle yapılan adımlar bu generic scripte dönüştürülecek (TASK sonraki). Şu anda her tenant için özel script gerekiyor.

---

> **Şablon versiyon:** v1.0 · 2026-05-23
> **Kaynak:** `app/models/*.py` ORM inceleme + `tenants` FK haritası
