# 📋 TOMOFİL OTOMOTİV A.Ş. — DEMO TENANT (DOLDURULMUŞ ŞABLON)

> **Demo türü:** Müşteri showcase + 6 yıllık tarihçe (2021-2026)
> **Sektör:** Yerli otomotiv parça üreticisi — EV pivot hikayesi
> **Ölçek:** 100 çalışan (2026), 6 yıllık evrim, ~50 KPI, ~22 alt strateji
> **Hikaye:** 2021 kuruluş → pandemi → klasik motor parçaları → EV geçişi → sürdürülebilirlik → dijital dönüşüm
> **Doldurma tarihi:** 2026-05-23
> **Şablon kaynak:** [docs/sablon.md](../sablon.md)

---

## 🎬 ŞİRKET HİKAYESİ (DEMO NARRATIVE)

> **Tomofil Otomotiv A.Ş.** — Bursa Demirtaş OSB'de 2021 yılında 5 makine mühendisinin kurduğu girişim.
> İlk yıl içten yanmalı motor parçaları (krank mili, piston kolu, şanzıman dişli) tedariği ile Ford Otosan ve Tofaş'a girdi.
> 2022 pandemi/chip krizinde kadro daraldı, 2023'te toparlandı, 2024'te **EV pivot** kararı aldı.
> Bugün: e-motor stator/rotor parçaları + batarya hücre kasası üretiminde uzmanlaşıyor.
> **Kokpitim'i 2021 kuruluştan beri** kurumsal yönetim için kullanıyor — strateji ağacı, süreçler, KPI'lar yıllar içinde evrildi.

### 6 Yıllık Özet Tablo

| Yıl | Olay | Çalışan | Ana Strateji | Toplam KPI | Aktif Süreç |
|-----|------|---------|--------------|------------|-------------|
| 2021 | Kuruluş, OEM tedarik başlangıcı | 80 | 3 | 22 | 6 |
| 2022 | Chip krizi + pandemi etkisi | 60 | 3 | 24 | 6 |
| 2023 | İhracat açılımı (Avrupa) | 75 | 4 | 32 | 7 |
| 2024 | **EV PİVOT** — e-motor + batarya | 90 | 5 | 40 | 8 |
| 2025 | Sürdürülebilirlik + CBAM hazırlık | 96 | 6 | 46 | 9 |
| 2026 | Dijital dönüşüm + Industry 4.0 | 100 | 6 | 50 | 10 |

---

## ✅ Etkin Modüller

| Modül | Etkin? |
|-------|--------|
| ⭐ Tenant Kimliği | ✅ |
| ⭐ Plan Yılları (6 yıl) | ✅ |
| ⭐ Stratejik Plan (yıl bazlı evrim) | ✅ |
| ⭐ Süreçler + KPI'lar | ✅ (yıl bazlı evrim) |
| ⭐ Kullanıcılar (100, pandemi etkili kadro evrimi) | ✅ |
| 🔵 KPI Geçmiş Veri (karma sıklık) | ✅ |
| 🔵 Süreç Faaliyetleri | ✅ |
| 🔵 Proje Portföyü | ✅ |
| 🔵 Bireysel PG | ✅ |
| 🔵 SWOT / TOWS (her yıl) | ✅ |
| 🔵 PESTEL (her yıl) | ✅ |
| 🔵 Porter 5 Force (her yıl) | ✅ |
| 🔵 OKR (her yıl) | ✅ |
| 🔵 K-Vektor (2026 aktif) | ✅ |
| 🔵 K-Radar (tümü) | ✅ |
| 🔵 SMTP | ☐ (boş) |
| 🔵 Logo | ✅ (placeholder) |

---

# 1️⃣ TENANT KİMLİĞİ (2026 — bugün)

```yaml
name:              "Tomofil Otomotiv Sanayi ve Ticaret A.Ş."
short_name:        "Tomofil"
sector:            "Otomotiv / Yan Sanayi"
activity_area:     "Elektrikli araç parçaları (e-motor stator/rotor + batarya hücre kasası); klasik motor parçaları"
employee_count:    100
contact_email:     "info@tomofil.test"
phone_number:      "+90 224 555 0250"
website_url:       "https://tomofil.test"
tax_office:        "Bursa Osmangazi"
tax_number:        "8765432109"
max_user_count:    150
license_end_date:  "2027-12-31"

vision: |
  2030 yılında Türkiye ve Avrupa elektrikli araç ekosisteminin en güvenilen
  hassas parça tedarikçisi olmak; OEM'lerin "tier-1 tercih" listesinde yer almak.

purpose: |
  Türkiye'nin otomotiv sanayisinin elektrikli araç dönüşümüne hassas mühendislik,
  güvenilir kalite ve sürdürülebilir üretimle katkı sağlamak.

core_values: "Mühendislik Disiplini, Şeffaflık, Sürekli İyileştirme, Çevik Adaptasyon, Sürdürülebilirlik"

code_of_ethics: |
  IATF 16949 + ISO 9001 + ISO 14001 + ISO 45001 entegre yönetim sistemi.
  Tedarikçilerden çocuk işçi ve modern kölelik beyanı zorunlu. Konflikt mineralleri (3TG)
  raporlaması yıllık. Çalışan rüşvet/yolsuzluk eğitimi zorunlu.

quality_policy: |
  PPM hedefi <50, IATF 16949 sertifikası 2023'ten beri aktif. APQP/PPAP süreçleri
  her yeni parça için uygulanır. Müşteri reklamasyonu 24 saat içinde 8D başlatma.

plan_year_enabled: true
plan_year_start:   2021
k_vektor_enabled:  true
k_radar_enabled:   true

package_id:        1
```

---

# 2️⃣ TENANT ADMİN KULLANICISI

```yaml
admin_email:      "admin@tomofil.test"
admin_password:   "Tomofil2026!"
admin_first_name: "Tomofil"
admin_last_name:  "Yönetici"
admin_phone:      "+90 532 555 0001"
admin_job_title:  "Tenant Yöneticisi"
admin_department: "Yönetim / IT"
```

---

# 3️⃣ PLAN YILLARI (6 yıl — 2021 kuruluştan beri)

```yaml
plan_years:
  - { year: 2021, name: "2021 Kuruluş Yılı Planı",         status: "closed"  }
  - { year: 2022, name: "2022 Toparlanma Planı",            status: "closed"  }
  - { year: 2023, name: "2023 İhracat Açılım Planı",       status: "closed"  }
  - { year: 2024, name: "2024 EV Pivot Stratejik Planı",   status: "closed"  }
  - { year: 2025, name: "2025 Sürdürülebilirlik Planı",    status: "closed"  }
  - { year: 2026, name: "2026 Dijital Dönüşüm Planı",      status: "active"  }
  - { year: 2027, name: "2027 Stratejik Planı (taslak)",   status: "draft"   }
```

---

# 4️⃣ STRATEJİ EVRİMİ TARİHÇESİ (yıllar arası değişim özeti)

> **Önemli:** Her yıl için `strategies` + `sub_strategies` ayrı kayıt (plan_year_id ile bağlı).
> `source_strategy_id` ile önceki yıldaki ataya referans tutulur — devamlılık görselleştirilir.
> Toplam ~18 değişim → orta seviye evrim.

## 4.a Ana Strateji Yıllara Göre Tablosu

| Kod | Başlık | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|-----|--------|------|------|------|------|------|------|
| H1 | Yerli OEM'lere Hassas Parça Tedariki | ✅ | ✅ | ✅ | ⚠️ küçülme | ⚠️ | ⚠️ klasik motor azalan |
| H2 | Üretim Kapasitesi ve Kalite Temeli | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| H3 | İnsan ve Kurumsallaşma | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| H4 | İhracat Açılımı (Avrupa) | — | — | ➕ yeni | ✅ | ✅ | ✅ |
| H5 | Elektrikli Araç Geçişi | — | — | — | ➕ yeni | ✅ büyüme | ✅ |
| H6 | Sürdürülebilirlik ve ESG | — | — | — | — | ➕ yeni | ✅ |
| H7 | Dijital Operasyon ve Endüstri 4.0 | — | — | — | — | — | ➕ yeni |

Lejant: ✅ aktif · ➕ yeni eklendi · ⚠️ kapsam değişti / küçüldü · — yok

## 4.b Önemli Değişim Olayları (kronolojik)

| Yıl | Değişim | Etki |
|-----|---------|------|
| 2022 | Alt strateji 1.B (Avrupa Pazar Araştırması) **ertelendi** | Pandemi/finans |
| 2022 | Yeni alt strateji 3.C (Uzaktan İş ve Esnek Çalışma) eklendi | İK toparlanma |
| 2023 | **H4 (İhracat) ana strateji** eklendi | İlk Avrupa müşterisi (TIER-1 Almanya) |
| 2023 | Alt strateji 2.D (APQP/PPAP Olgunlaştırma) eklendi | IATF 16949 sertifika hazırlığı |
| 2024 | **H5 (EV Pivot) ana strateji** eklendi | Önemli stratejik kırılma |
| 2024 | Alt strateji 1.A.2 (İçten Yanmalı Motor Krank Mili) pasifleştirildi | Talep azalması |
| 2024 | 3 yeni alt strateji (e-motor stator, rotor, batarya kasası) | EV pivot başlangıç |
| 2025 | **H6 (Sürdürülebilirlik)** eklendi | CBAM riski + müşteri talebi |
| 2025 | Alt strateji 4.B (Asya Pazar Araştırması) **terkedildi** | Avrupa odak kararı |
| 2025 | Alt strateji 6.A.1 (Karbon Ayak İzi Ölçümü) eklendi | TCFD hazırlık |
| 2026 | **H7 (Dijital Dönüşüm)** eklendi | Industry 4.0 yatırım kararı |
| 2026 | Alt strateji 7.A.1 (Predictive Maintenance) eklendi | OEE %72→%88 hedefi |
| 2026 | Alt strateji 7.A.2 (Dijital İkiz Üretim Hattı) eklendi | Sanal devreye alma |
| 2026 | Alt strateji 5.A.4 (V2G/V2H teknoloji izleme) eklendi | Yeni nesil EV trendi |
| 2026 | Alt strateji 5.B.1 (e-motor stator) hedef revizyonu | %12→%25 üretim payı |
| 2026 | Alt strateji 1.A.1 (motor blok parça) için **kapsam küçültme** | Klasik motor payı azalan |

**Toplam değişim:** 16 (yumuşak-orta arası — gerçekçi kurumsal evrim)

---

# 5️⃣ STRATEJİK PLAN — 2026 (AKTİF YIL)

```yaml
strategies:
  # ── H1 — KLASİK MOTOR PARÇA TEDARİKİ (2021'den beri, kapsamı küçülüyor) ──
  - code: "H1"
    title: "Yerli OEM'lere Klasik Motor Parça Tedariki"
    description: "Geleneksel içten yanmalı motor parçaları; payı azalmakla birlikte istikrar getiren kaynak."
    sub_strategies:
      - { code: "1.A",   title: "Hassas Mekanik Parça Üretimi" }
      - { code: "1.A.1", title: "Motor Blok ve Silindir Parçaları (Ford Otosan)" }
      - { code: "1.A.2", title: "İçten Yanmalı Motor Krank Mili", status_note: "2024'te pasifleştirildi" }
      - { code: "1.A.3", title: "Şanzıman Dişli ve Mil Üretimi (Tofaş)" }

  # ── H2 — ÜRETİM KALİTE TEMELİ (kuruluştan beri, sürekli olgunlaşan) ──
  - code: "H2"
    title: "Üretim Kapasitesi ve Kalite Mükemmelliği"
    description: "IATF 16949 sertifikalı, sıfır hata felsefesi, OEE artışı."
    sub_strategies:
      - { code: "2.A",   title: "CNC + 5-Eksen İşleme Kapasitesi" }
      - { code: "2.A.1", title: "5-Eksen İşleme Merkezi (2 → 6 adet, 2030)" }
      - { code: "2.B",   title: "Kalite Yönetim Sistemi" }
      - { code: "2.B.1", title: "IATF 16949 + ISO 9001 Sertifika Bakımı" }
      - { code: "2.B.2", title: "PPM <50 — Sıfır Hata Hedefi" }
      - { code: "2.C",   title: "Üretim Verimliliği" }
      - { code: "2.C.1", title: "OEE %72 → %88 (2030)" }
      - { code: "2.D",   title: "APQP / PPAP Olgunlaştırma (2023'te eklendi)" }

  # ── H3 — İNSAN VE KURUMSALLAŞMA (kuruluştan beri) ──
  - code: "H3"
    title: "İnsan, Kültür ve Kurumsallaşma"
    description: "Bursa yetenek havzasında çekici işveren; ESOP + eğitim + iyi yönetişim."
    sub_strategies:
      - { code: "3.A",   title: "Yetenek Çekme ve Tutma" }
      - { code: "3.A.1", title: "Bursa Üniversite Stajı Programı (BUÜ, Uludağ)" }
      - { code: "3.B",   title: "Kurumsal Yönetişim" }
      - { code: "3.B.1", title: "ISO 9001 + IATF Entegre Yönetim Sistemi Olgunlaşması" }
      - { code: "3.C",   title: "Esnek ve Hibrit Çalışma (2022'de eklendi — pandemi mirası)" }

  # ── H4 — İHRACAT (2023'te eklendi) ──
  - code: "H4"
    title: "İhracat Açılımı ve Avrupa Pazarı"
    description: "İlk Avrupa müşterisi 2023'te kazanıldı; bugün ihracat payı %22."
    sub_strategies:
      - { code: "4.A",   title: "Avrupa Tier-1 Tedarikçi Sertifikasyonu" }
      - { code: "4.A.1", title: "Almanya VW Group Onboarding (devam)" }
      - { code: "4.A.2", title: "CBAM Uyum Hazırlığı (2027 yürürlük)" }

  # ── H5 — ELEKTRİKLİ ARAÇ GEÇİŞİ (2024'te eklendi — KRİTİK PİVOT) ──
  - code: "H5"
    title: "Elektrikli Araç Parça Üretimi (EV Pivot)"
    description: "2024'te başlayan stratejik pivot; bugün cironun %38'i. 2030 hedef %75."
    sub_strategies:
      - { code: "5.A",   title: "E-Motor Stator ve Rotor Üretimi" }
      - { code: "5.A.1", title: "Stator Lamination — Yıllık 25.000 → 80.000 adet" }
      - { code: "5.A.2", title: "Rotor Mil + Mıknatıs Montaj" }
      - { code: "5.A.3", title: "Hairpin Sargı Teknolojisi Lisansı (Bosch ortaklığı)" }
      - { code: "5.A.4", title: "V2G / V2H Teknoloji İzleme (2026'da eklendi)" }
      - { code: "5.B",   title: "Batarya Hücre Kasası Üretimi" }
      - { code: "5.B.1", title: "Alüminyum Pres + İşleme — TOGG Tedariki" }

  # ── H6 — SÜRDÜRÜLEBİLİRLİK (2025'te eklendi) ──
  - code: "H6"
    title: "Sürdürülebilirlik ve ESG Liderliği"
    description: "CBAM hazırlık + müşteri ESG talebi + B Corp yolculuğu."
    sub_strategies:
      - { code: "6.A",   title: "Karbon Ayak İzi Yönetimi" }
      - { code: "6.A.1", title: "Scope 1+2 Ölçümü ve Yıllık Raporlama (2025'te eklendi)" }
      - { code: "6.A.2", title: "Çatı GES — 250 kWp (2026)" }
      - { code: "6.B",   title: "Geri Dönüşümlü Hammadde" }
      - { code: "6.B.1", title: "Alüminyum Geri Dönüşüm %40 hedefi (batarya kasası)" }

  # ── H7 — DİJİTAL DÖNÜŞÜM (2026'da eklendi) ──
  - code: "H7"
    title: "Dijital Operasyon ve Endüstri 4.0"
    description: "Predictive maintenance + dijital ikiz + MES entegrasyonu."
    sub_strategies:
      - { code: "7.A",   title: "Industry 4.0 Altyapı" }
      - { code: "7.A.1", title: "Predictive Maintenance — IoT Sensör + ML Model" }
      - { code: "7.A.2", title: "Dijital İkiz — Hat 2 Sanal Devreye Alma" }
      - { code: "7.A.3", title: "MES + ERP Tam Entegrasyon" }
```

**2026 sayım:** 7 Ana + 14 L1 + ~22 L2 (1.A.2 pasif dahil) ≈ **toplam 36 strateji kaydı 2026 için**

## 5.b Geçmiş Yıllar İçin Strateji Snapshot (özet)

> Seed scripti her yıl için Strategy + SubStrategy kayıtlarını ayrı `plan_year_id` ile yaratacak.
> Yıllar arası `source_strategy_id` zinciri ile devamlılık görselleştirilir.

```yaml
strategies_by_year:
  2021: ["H1", "H2", "H3"]           # 3 ana
  2022: ["H1", "H2", "H3"]           # 3 ana
  2023: ["H1", "H2", "H3", "H4"]     # 4 ana
  2024: ["H1", "H2", "H3", "H4", "H5"]  # 5 ana
  2025: ["H1", "H2", "H3", "H4", "H5", "H6"]  # 6 ana
  2026: ["H1", "H2", "H3", "H4", "H5", "H6", "H7"]  # 7 ana
```

Detaylı 6 yıllık alt strateji kayıtları **seed script tarafından** kurallarla üretilecek (yukarıdaki "değişim olayları tablosu" + 2026 ağacı baz alınır, eskiye doğru sub_strategy'ler çıkarılır).

---

# 6️⃣ SÜREÇLER (2026 — 10 aktif süreç)

```yaml
processes:
  # ── KURULUŞ SÜREÇLERİ (2021'den beri tüm yıllarda) ──
  - { code: "P2M", name: "Planlama'dan Üretime",        english_name: "Plan-to-Manufacture",     weight: 18, owners: ["mehmet.aktas@tomofil.test"], description: "CNC + montaj + kalite kontrol", linked_sub_strategy_codes: ["2.A.1", "2.C.1", "5.A.1", "5.B.1", "7.A.1"] }
  - { code: "S2P", name: "Tedarik'ten Ödemeye",         english_name: "Source-to-Pay",           weight: 12, owners: ["ali.kaplan@tomofil.test"],   description: "Çelik + alüminyum + bakır tedarik", linked_sub_strategy_codes: ["6.B.1"] }
  - { code: "A2R", name: "Müşteri Edinme ve Tutma",     english_name: "Acquire-to-Retain",       weight: 12, owners: ["sibel.demir@tomofil.test"], description: "OEM ilişki yönetimi, RFQ", linked_sub_strategy_codes: ["1.A.1", "4.A.1", "5.A.1"] }
  - { code: "H2R", name: "İşe Alım'dan Emekliliğe",     english_name: "Hire-to-Retire",          weight: 8,  owners: ["pinar.aksoy@tomofil.test"], description: "İK yaşam döngüsü", linked_sub_strategy_codes: ["3.A.1", "3.C"] }
  - { code: "R2R", name: "Kayıt'tan Raporlamaya",       english_name: "Record-to-Report",        weight: 8,  owners: ["okan.celikkol@tomofil.test"], description: "Mali kayıt + IATF doküman", linked_sub_strategy_codes: ["2.B.1"] }
  - { code: "I2R", name: "Sorun'dan Çözüme",            english_name: "Issue-to-Resolution",     weight: 7,  owners: ["esra.sen@tomofil.test"], description: "8D + reklamasyon yönetimi", linked_sub_strategy_codes: ["2.B.2"] }

  # ── 2023'te eklenen: APQP / İhracat ──
  - { code: "C2L", name: "Konsept'ten Lansmana",        english_name: "Concept-to-Launch",       weight: 10, owners: ["taylan.koc@tomofil.test"], description: "Yeni parça APQP/PPAP süreci", linked_sub_strategy_codes: ["2.D", "4.A.1", "5.A.1", "5.B.1"] }

  # ── 2024'te eklenen: EV Pivot ile (özel süreç) ──
  - { code: "B2R", name: "Bataryadan Geri Dönüşüme",    english_name: "Battery-to-Recycle",      weight: 8,  owners: ["mehmet.aktas@tomofil.test"], description: "Batarya kasası geri kazanım + alüminyum döngü", linked_sub_strategy_codes: ["6.B.1"] }

  # ── 2025'te eklenen: Risk + Sürdürülebilirlik ──
  - { code: "R2M", name: "Risk'ten Azaltmaya",          english_name: "Risk-to-Mitigation",      weight: 7,  owners: ["okan.celikkol@tomofil.test"], description: "CBAM, döviz, OEM bağımlılık riskleri", linked_sub_strategy_codes: ["4.A.2", "6.A.1"] }

  # ── 2026'da eklenen: Dijital Dönüşüm ile ──
  - { code: "D2I", name: "Veri'den İçgörüye",           english_name: "Data-to-Insight",         weight: 5,  owners: ["fatih.demirel@tomofil.test"], description: "BI + IoT veri akışı + analitik", linked_sub_strategy_codes: ["7.A.1", "7.A.2", "7.A.3"] }

  - { code: "S2E", name: "Strateji'den İcraya",         english_name: "Strategy-to-Execution",   weight: 5,  owners: ["admin@tomofil.test"], description: "Stratejik plan yönetişimi + OKR", linked_sub_strategy_codes: [] }
```

**2026 sayım:** 10 süreç, weight toplamı=100 ✅

## 6.b Süreç Evrimi (yıllar arası)

| Süreç Kodu | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|------------|------|------|------|------|------|------|
| P2M | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| S2P | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| A2R | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| H2R | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R2R | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| I2R | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| C2L | — | — | ➕ | ✅ | ✅ | ✅ |
| B2R | — | — | — | ➕ | ✅ | ✅ |
| R2M | — | — | — | — | ➕ | ✅ |
| D2I | — | — | — | — | — | ➕ |

**Süreç sayısı:** 2021:6 → 2023:7 → 2024:8 → 2025:9 → 2026:10

---

# 7️⃣ PROCESS KPI'LAR (2026 — 50 KPI)

> 10 süreç × ortalama 5 KPI ≈ 50 KPI. Format Anadolu Yaşam ile aynı. Aşağıda **örnek satırlar** — generic seed scripti yıl bazlı tüm kayıtları üretecek.

```yaml
process_kpis:
  # ─── P2M (Üretim — kuruluştan beri en kritik süreç) ───
  - { process_code: "P2M", code: "P2M-01", name: "OEE (%)",                              unit: "%",     period: "Aylık",  target_value: "88", direction: "Increasing", weight: 25, is_important: true, linked_sub_strategy_code: "2.C.1", onceki_yil_ortalamasi: 72 }
  - { process_code: "P2M", code: "P2M-02", name: "FPY — First Pass Yield (%)",           unit: "%",     period: "Aylık",  target_value: "98", direction: "Increasing", weight: 20, is_important: true, onceki_yil_ortalamasi: 93 }
  - { process_code: "P2M", code: "P2M-03", name: "PPM Hata Oranı",                       unit: "ppm",   period: "Aylık",  target_value: "50", direction: "Decreasing", weight: 20, is_important: true, linked_sub_strategy_code: "2.B.2", onceki_yil_ortalamasi: 180 }
  - { process_code: "P2M", code: "P2M-04", name: "Birim Üretim Maliyeti (TL/parça)",     unit: "TL",    period: "Aylık",  target_value: "145", direction: "Decreasing", weight: 15, onceki_yil_ortalamasi: 195 }
  - { process_code: "P2M", code: "P2M-05", name: "Aylık Üretim Adedi (e-motor stator)", unit: "adet",  period: "Aylık",  target_value: "6500", direction: "Increasing", weight: 10, linked_sub_strategy_code: "5.A.1", onceki_yil_ortalamasi: 2100 }
  - { process_code: "P2M", code: "P2M-06", name: "Yenilenebilir Enerji Oranı (%)",       unit: "%",     period: "Aylık",  target_value: "45", direction: "Increasing", weight: 10, linked_sub_strategy_code: "6.A.2", onceki_yil_ortalamasi: 12 }

  # ─── S2P ───
  - { process_code: "S2P", code: "S2P-01", name: "Tedarikçi OTD (%)",                    unit: "%",     period: "Aylık",  target_value: "96", direction: "Increasing", weight: 30, is_important: true, onceki_yil_ortalamasi: 87 }
  - { process_code: "S2P", code: "S2P-02", name: "Çift-Kaynak Oranı (%)",                unit: "%",     period: "Çeyreklik", target_value: "100", direction: "Increasing", weight: 25, is_important: true, onceki_yil_ortalamasi: 78 }
  - { process_code: "S2P", code: "S2P-03", name: "Hammadde Maliyeti Sapması (%)",        unit: "%",     period: "Aylık",  target_value: "3", direction: "Decreasing", weight: 20, onceki_yil_ortalamasi: 12 }
  - { process_code: "S2P", code: "S2P-04", name: "Geri Dönüşmüş Alüminyum Oranı (%)",   unit: "%",     period: "Aylık",  target_value: "40", direction: "Increasing", weight: 15, linked_sub_strategy_code: "6.B.1", onceki_yil_ortalamasi: 8 }
  - { process_code: "S2P", code: "S2P-05", name: "Tedarikçi Kalite (PPM)",                unit: "ppm",   period: "Aylık",  target_value: "80", direction: "Decreasing", weight: 10, onceki_yil_ortalamasi: 220 }

  # ─── A2R ───
  - { process_code: "A2R", code: "A2R-01", name: "RFQ → Sipariş Dönüşümü (%)",          unit: "%",     period: "Aylık",  target_value: "32", direction: "Increasing", weight: 25, is_important: true, onceki_yil_ortalamasi: 22 }
  - { process_code: "A2R", code: "A2R-02", name: "Müşteri Sayısı (OEM + Tier-1)",       unit: "adet",  period: "Yıllık", target_value: "14", direction: "Increasing", weight: 15, onceki_yil_ortalamasi: 9 }
  - { process_code: "A2R", code: "A2R-03", name: "Müşteri NPS",                          unit: "skor",  period: "Yıllık", target_value: "62", direction: "Increasing", weight: 20, is_important: true, onceki_yil_ortalamasi: 38 }
  - { process_code: "A2R", code: "A2R-04", name: "İhracat Payı (%)",                     unit: "%",     period: "Çeyreklik", target_value: "32", direction: "Increasing", weight: 25, is_important: true, linked_sub_strategy_code: "4.A.1", onceki_yil_ortalamasi: 22 }
  - { process_code: "A2R", code: "A2R-05", name: "EV Cirosu Payı (%)",                   unit: "%",     period: "Çeyreklik", target_value: "48", direction: "Increasing", weight: 15, is_important: true, linked_sub_strategy_code: "5.A.1", onceki_yil_ortalamasi: 38 }

  # ─── C2L (2023'te eklendi) ───
  - { process_code: "C2L", code: "C2L-01", name: "APQP Aşama Tamamlama Süresi (gün)",   unit: "gün",   period: "Aylık",  target_value: "180", direction: "Decreasing", weight: 25, linked_sub_strategy_code: "2.D", onceki_yil_ortalamasi: 240 }
  - { process_code: "C2L", code: "C2L-02", name: "PPAP İlk Defa Onay (%)",               unit: "%",     period: "Çeyreklik", target_value: "85", direction: "Increasing", weight: 25, is_important: true, onceki_yil_ortalamasi: 62 }
  - { process_code: "C2L", code: "C2L-03", name: "Yıllık Yeni Parça Tesciliği",          unit: "adet",  period: "Yıllık", target_value: "18", direction: "Increasing", weight: 20, onceki_yil_ortalamasi: 9 }
  - { process_code: "C2L", code: "C2L-04", name: "Hairpin Sargı Teknolojisi Olgunluğu", unit: "skor",  period: "Çeyreklik", target_value: "4.5", direction: "Increasing", weight: 15, linked_sub_strategy_code: "5.A.3", onceki_yil_ortalamasi: 2.8 }
  - { process_code: "C2L", code: "C2L-05", name: "Tasarım → İlk Numune Süresi (gün)",   unit: "gün",   period: "Aylık",  target_value: "45", direction: "Decreasing", weight: 15, onceki_yil_ortalamasi: 75 }

  # ─── B2R (2024'te eklendi — EV ile) ───
  - { process_code: "B2R", code: "B2R-01", name: "Batarya Kasası Geri Kazanım Oranı (%)", unit: "%",   period: "Aylık",  target_value: "92", direction: "Increasing", weight: 35, is_important: true, linked_sub_strategy_code: "6.B.1", onceki_yil_ortalamasi: 68 }
  - { process_code: "B2R", code: "B2R-02", name: "Alüminyum Döngü Verimi (%)",            unit: "%",   period: "Aylık",  target_value: "97", direction: "Increasing", weight: 30, onceki_yil_ortalamasi: 82 }
  - { process_code: "B2R", code: "B2R-03", name: "Atık Aluminyum Hurda Geliri (TL/ay)",  unit: "TL",  period: "Aylık",  target_value: "180000", direction: "Increasing", weight: 20, onceki_yil_ortalamasi: 95000 }
  - { process_code: "B2R", code: "B2R-04", name: "Karbon Tasarrufu (ton CO2/yıl)",        unit: "ton", period: "Yıllık", target_value: "85", direction: "Increasing", weight: 15, onceki_yil_ortalamasi: 32 }

  # ─── H2R ───
  - { process_code: "H2R", code: "H2R-01", name: "İşe Alım Süresi (gün)",                  unit: "gün",  period: "Aylık",  target_value: "32", direction: "Decreasing", weight: 20, onceki_yil_ortalamasi: 48 }
  - { process_code: "H2R", code: "H2R-02", name: "eNPS",                                    unit: "skor", period: "Yıllık", target_value: "50", direction: "Increasing", weight: 25, is_important: true, onceki_yil_ortalamasi: 32 }
  - { process_code: "H2R", code: "H2R-03", name: "Yıllık Çıkış Oranı (%)",                  unit: "%",   period: "Yıllık", target_value: "6", direction: "Decreasing", weight: 20, is_important: true, onceki_yil_ortalamasi: 11 }
  - { process_code: "H2R", code: "H2R-04", name: "Eğitim Saati/Kişi (yıl)",                unit: "saat", period: "Yıllık", target_value: "48", direction: "Increasing", weight: 15, onceki_yil_ortalamasi: 26 }
  - { process_code: "H2R", code: "H2R-05", name: "Cinsiyet Çeşitliliği — Kadın Mühendis (%)", unit: "%", period: "Yıllık", target_value: "30", direction: "Increasing", weight: 10, onceki_yil_ortalamasi: 18 }
  - { process_code: "H2R", code: "H2R-06", name: "Onboarding Tamamlama (%)",                unit: "%",  period: "Aylık", target_value: "95", direction: "Increasing", weight: 10, onceki_yil_ortalamasi: 82 }

  # ─── R2R ───
  - { process_code: "R2R", code: "R2R-01", name: "Ay Kapanış Süresi (iş günü)",             unit: "gün",  period: "Aylık",  target_value: "5", direction: "Decreasing", weight: 25, onceki_yil_ortalamasi: 9 }
  - { process_code: "R2R", code: "R2R-02", name: "Mali Rapor Doğruluğu (%)",                 unit: "%",    period: "Aylık",  target_value: "99.7", direction: "Increasing", weight: 25, is_important: true, onceki_yil_ortalamasi: 98.4 }
  - { process_code: "R2R", code: "R2R-03", name: "IATF Doküman Doğruluğu (%)",                unit: "%",  period: "Çeyreklik", target_value: "100", direction: "Increasing", weight: 20, is_important: true, linked_sub_strategy_code: "2.B.1", onceki_yil_ortalamasi: 96 }
  - { process_code: "R2R", code: "R2R-04", name: "Denetim Bulgu Sayısı (IATF/ISO)",          unit: "adet", period: "Yıllık", target_value: "0", direction: "Decreasing", weight: 20, is_important: true, onceki_yil_ortalamasi: 2 }
  - { process_code: "R2R", code: "R2R-05", name: "EBITDA Marjı (%)",                          unit: "%",   period: "Yıllık", target_value: "18", direction: "Increasing", weight: 10, is_important: true, onceki_yil_ortalamasi: 11 }

  # ─── I2R ───
  - { process_code: "I2R", code: "I2R-01", name: "8D Açma Süresi (saat)",                    unit: "saat", period: "Aylık",  target_value: "24", direction: "Decreasing", weight: 25, is_important: true, onceki_yil_ortalamasi: 48 }
  - { process_code: "I2R", code: "I2R-02", name: "Reklamasyon Çözüm Süresi (gün)",            unit: "gün", period: "Aylık",  target_value: "14", direction: "Decreasing", weight: 25, onceki_yil_ortalamasi: 28 }
  - { process_code: "I2R", code: "I2R-03", name: "Garanti Maliyeti / Sevkiyat (TL/parça)",   unit: "TL",  period: "Aylık",  target_value: "8", direction: "Decreasing", weight: 20, onceki_yil_ortalamasi: 22 }
  - { process_code: "I2R", code: "I2R-04", name: "Kalıcı Çözüm Oranı (%)",                    unit: "%",   period: "Çeyreklik", target_value: "95", direction: "Increasing", weight: 20, is_important: true, onceki_yil_ortalamasi: 78 }
  - { process_code: "I2R", code: "I2R-05", name: "Müşteri Reklamasyon Sayısı / Ay",          unit: "adet", period: "Aylık", target_value: "2", direction: "Decreasing", weight: 10, onceki_yil_ortalamasi: 7 }

  # ─── R2M (2025'te eklendi) ───
  - { process_code: "R2M", code: "R2M-01", name: "CBAM Hazırlık Olgunluk Skoru",              unit: "skor", period: "Çeyreklik", target_value: "4.5", direction: "Increasing", weight: 30, is_important: true, linked_sub_strategy_code: "4.A.2", onceki_yil_ortalamasi: 2.8 }
  - { process_code: "R2M", code: "R2M-02", name: "OEM Müşteri Konsantrasyon Riski (%)",       unit: "%",   period: "Çeyreklik", target_value: "40", direction: "Decreasing", weight: 25, is_important: true, onceki_yil_ortalamasi: 58 }
  - { process_code: "R2M", code: "R2M-03", name: "Döviz Kuru Hedge Oranı (%)",                 unit: "%",  period: "Aylık",  target_value: "75", direction: "Increasing", weight: 25, onceki_yil_ortalamasi: 45 }
  - { process_code: "R2M", code: "R2M-04", name: "Aktif Risk Sayısı",                          unit: "adet", period: "Çeyreklik", target_value: "15", direction: "Decreasing", weight: 10, onceki_yil_ortalamasi: 22 }
  - { process_code: "R2M", code: "R2M-05", name: "Risk Azaltma Etkinliği (%)",                 unit: "%",   period: "Yıllık", target_value: "85", direction: "Increasing", weight: 10, onceki_yil_ortalamasi: 68 }

  # ─── D2I (2026'da eklendi) ───
  - { process_code: "D2I", code: "D2I-01", name: "Predictive Maintenance Yakalama (%)",       unit: "%",   period: "Aylık",  target_value: "75", direction: "Increasing", weight: 30, is_important: true, linked_sub_strategy_code: "7.A.1", onceki_yil_ortalamasi: 0 }
  - { process_code: "D2I", code: "D2I-02", name: "Dijital İkiz Doğruluk (%)",                  unit: "%",  period: "Çeyreklik", target_value: "92", direction: "Increasing", weight: 25, linked_sub_strategy_code: "7.A.2", onceki_yil_ortalamasi: 0 }
  - { process_code: "D2I", code: "D2I-03", name: "MES → ERP Veri Senkron Hata Oranı (%)",     unit: "%",   period: "Haftalık", target_value: "0.5", direction: "Decreasing", weight: 20, linked_sub_strategy_code: "7.A.3", onceki_yil_ortalamasi: 0 }
  - { process_code: "D2I", code: "D2I-04", name: "Self-Service Analitik Kullanıcı Sayısı",     unit: "kişi", period: "Aylık",  target_value: "45", direction: "Increasing", weight: 15, onceki_yil_ortalamasi: 8 }
  - { process_code: "D2I", code: "D2I-05", name: "Veri Kalite Skoru",                          unit: "skor", period: "Çeyreklik", target_value: "92", direction: "Increasing", weight: 10, onceki_yil_ortalamasi: 72 }

  # ─── S2E ───
  - { process_code: "S2E", code: "S2E-01", name: "OKR Hedef Gerçekleşme (%)",                  unit: "%",   period: "Çeyreklik", target_value: "78", direction: "Increasing", weight: 30, is_important: true, onceki_yil_ortalamasi: 58 }
  - { process_code: "S2E", code: "S2E-02", name: "Süreç Olgunluk Ortalaması (1-5)",            unit: "skor", period: "Yıllık", target_value: "4.0", direction: "Increasing", weight: 30, is_important: true, onceki_yil_ortalamasi: 2.8 }
  - { process_code: "S2E", code: "S2E-03", name: "Stratejik İnisiyatif Tamamlama (%)",          unit: "%",  period: "Yıllık", target_value: "85", direction: "Increasing", weight: 20, onceki_yil_ortalamasi: 65 }
  - { process_code: "S2E", code: "S2E-04", name: "Yönetim Raporu Yayın Doğruluğu (%)",          unit: "%",  period: "Aylık",  target_value: "99", direction: "Increasing", weight: 20, onceki_yil_ortalamasi: 92 }
```

**2026 sayım:** ~50 KPI ✅

## 7.b KPI Evrimi (yıllar arası)

| Olay | Yıl | Açıklama |
|------|-----|----------|
| OEE KPI eklendi | 2021 | Kuruluş, P2M temel KPI |
| PPM hata oranı KPI eklendi | 2022 | Kalite olgunlaştırma |
| APQP/PPAP KPI'ları (C2L) eklendi | 2023 | İhracat hazırlık |
| EV/EV gelir payı KPI'ları eklendi | 2024 | Pivot ile birlikte |
| Batarya kasası geri kazanım KPI'ları (B2R) eklendi | 2024 | EV süreci ile |
| CBAM olgunluk KPI'sı eklendi | 2025 | Risk modülü |
| Predictive maintenance KPI'ları (D2I) eklendi | 2026 | Industry 4.0 |
| **Hedef değişiklikleri** | | OEE: 2021=70%→ 2024=78%→ 2026=88%. NPS: 2022=25→ 2026=62. |
| **Terkedilen KPI** | 2024 | "İçten yanmalı motor parça sevkiyat adedi" — P2M'den çıkarıldı |
| **Birim değişimi** | 2025 | Bazı kalite KPI'ları %  → ppm dönüştürüldü |

Toplam KPI sayısı: 2021:22 → 2026:50

---

# 8️⃣ KULLANICILAR (100 — pandemi etkili kadro evrimi)

```yaml
users_bulk_file: "docs/tomofil-demo/calisanlar.json"
users_password_default: "Tomofil2026!"
```

## 8.a Kadro Evrimi (2021-2026)

| Yıl | Olay | Toplam | İşe alım | Çıkış |
|-----|------|--------|----------|-------|
| 2021 | Kuruluş + ilk OEM müşteri kazanımı | **80** | +80 | 0 |
| 2022 | Chip krizi + pandemi → kadro daraltma | **60** | +5 | -25 |
| 2023 | İhracat açılımı, ihracat ekibi büyütüldü | **75** | +18 | -3 |
| 2024 | EV pivot başlangıcı, e-motor ekibi kuruluyor | **90** | +18 | -3 |
| 2025 | Sürdürülebilirlik + R&D genişleme | **96** | +9 | -3 |
| 2026 | Industry 4.0 ekibi + dijital dönüşüm | **100** | +6 | -2 |

**6 yıl toplam:** ~136 işe alım, ~36 çıkış → net 100 çalışan

## 8.b 2026 Departman Dağılımı (her birim olsun isteğine uygun)

| Departman | Sayı | Açıklama |
|-----------|------|----------|
| Yönetim (CEO/COO/CFO/CTO/CHRO) | 5 | C-suite |
| Üretim — CNC + Montaj | 25 | Ana üretim hattı |
| Üretim — Kalite Güvence | 8 | IATF + saha kontrol |
| Üretim — Bakım + Maintenance | 6 | Predictive + reaktif |
| Ar-Ge ve Tasarım | 10 | APQP + EV teknoloji |
| Tedarik ve Lojistik | 7 | Çelik/Al/bakır + sevkiyat |
| Satış (OEM + İhracat) | 7 | Yerli + Avrupa |
| İK ve İdari İşler | 5 | İK + güvenlik + temizlik dış kaynak |
| Finans ve Muhasebe | 5 | Mali işler + bütçe |
| Bilgi Teknolojileri ve Veri | 4 | IT + BI + IoT |
| Sürdürülebilirlik ve ESG | 3 | Karbon + CBAM + raporlama |
| Müşteri Hizmetleri ve Garanti | 3 | 8D + reklamasyon |
| Strateji ve PMO | 3 | Strateji + proje yönetimi |
| Sağlık-Güvenlik-Çevre (HSE) | 3 | İSG + çevre |
| Pazarlama ve İletişim | 2 | Web + fuar + içerik |
| Hukuk ve Uyum | 2 | Sözleşme + uyum |
| Eğitim ve Akademi | 2 | İç eğitim + zanaatkar |
| **TOPLAM** | **100** | (admin hariç) |

## 8.c Manuel Tanımlı Yöneticiler (20 kişi — süreç sahipleri + C-suite)

```yaml
users:
  # ── C-Suite ──
  - { email: "deniz.tunc@tomofil.test",       first_name: "Deniz",     last_name: "Tunç",       role: "executive_manager", job_title: "CEO",                          department: "Yönetim",                    process_codes: ["S2E"],          raci_role: "A", hire_year: 2021 }
  - { email: "cansu.aydin@tomofil.test",      first_name: "Cansu",     last_name: "Aydın",      role: "executive_manager", job_title: "COO",                          department: "Yönetim",                    process_codes: ["P2M","S2P"],   raci_role: "A", hire_year: 2021 }
  - { email: "okan.celikkol@tomofil.test",    first_name: "Okan",      last_name: "Çelikkol",   role: "executive_manager", job_title: "CFO",                          department: "Finans",                     process_codes: ["R2R","R2M"],   raci_role: "A", hire_year: 2022 }
  - { email: "selim.korkmaz@tomofil.test",    first_name: "Selim",     last_name: "Korkmaz",    role: "executive_manager", job_title: "CTO",                          department: "Bilgi Teknolojileri",        process_codes: ["D2I"],          raci_role: "A", hire_year: 2024 }
  - { email: "esin.demir@tomofil.test",       first_name: "Esin",      last_name: "Demir",      role: "executive_manager", job_title: "CHRO",                         department: "İnsan Kaynakları",           process_codes: ["H2R"],          raci_role: "A", hire_year: 2023 }

  # ── Süreç Sahipleri ──
  - { email: "mehmet.aktas@tomofil.test",     first_name: "Mehmet",    last_name: "Aktaş",      role: "executive_manager", job_title: "Üretim Müdürü",                department: "Üretim — CNC + Montaj",      process_codes: ["P2M","B2R"],   raci_role: "R", hire_year: 2021 }
  - { email: "ali.kaplan@tomofil.test",       first_name: "Ali",       last_name: "Kaplan",     role: "executive_manager", job_title: "Tedarik Müdürü",                department: "Tedarik ve Lojistik",        process_codes: ["S2P"],          raci_role: "R", hire_year: 2021 }
  - { email: "sibel.demir@tomofil.test",      first_name: "Sibel",     last_name: "Demir",      role: "executive_manager", job_title: "Satış Direktörü",              department: "Satış (OEM + İhracat)",      process_codes: ["A2R"],          raci_role: "R", hire_year: 2023 }
  - { email: "pinar.aksoy@tomofil.test",      first_name: "Pınar",     last_name: "Aksoy",      role: "executive_manager", job_title: "İK Müdürü",                    department: "İnsan Kaynakları",           process_codes: ["H2R"],          raci_role: "R", hire_year: 2022 }
  - { email: "esra.sen@tomofil.test",         first_name: "Esra",      last_name: "Şen",        role: "executive_manager", job_title: "Müşteri Hizmetleri Müdürü",    department: "Müşteri Hizmetleri ve Garanti", process_codes: ["I2R"],       raci_role: "R", hire_year: 2022 }
  - { email: "taylan.koc@tomofil.test",       first_name: "Taylan",    last_name: "Koç",        role: "executive_manager", job_title: "Ar-Ge Müdürü",                  department: "Ar-Ge ve Tasarım",           process_codes: ["C2L"],          raci_role: "R", hire_year: 2023 }
  - { email: "fatih.demirel@tomofil.test",    first_name: "Fatih",     last_name: "Demirel",    role: "executive_manager", job_title: "Veri ve Analitik Yöneticisi",  department: "Bilgi Teknolojileri",        process_codes: ["D2I"],          raci_role: "R", hire_year: 2026 }

  # ── Departman / Birim Yöneticileri ──
  - { email: "ozge.kara@tomofil.test",        first_name: "Özge",      last_name: "Kara",       role: "executive_manager", job_title: "Kalite Güvence Müdürü",         department: "Üretim — Kalite Güvence",    process_codes: ["P2M","I2R"],   raci_role: "R", hire_year: 2021 }
  - { email: "burak.yilmaz@tomofil.test",     first_name: "Burak",     last_name: "Yılmaz",     role: "executive_manager", job_title: "Bakım Müdürü",                  department: "Üretim — Bakım",             process_codes: ["P2M","D2I"],   raci_role: "C", hire_year: 2021 }
  - { email: "ipek.gunes@tomofil.test",       first_name: "İpek",      last_name: "Güneş",      role: "executive_manager", job_title: "Sürdürülebilirlik Direktörü",   department: "Sürdürülebilirlik ve ESG",   process_codes: ["B2R","R2M"],   raci_role: "R", hire_year: 2025 }
  - { email: "mert.aslan@tomofil.test",       first_name: "Mert",      last_name: "Aslan",      role: "executive_manager", job_title: "İhracat Müdürü",                department: "Satış (OEM + İhracat)",      process_codes: ["A2R","R2M"],   raci_role: "R", hire_year: 2023 }
  - { email: "leyla.celik@tomofil.test",      first_name: "Leyla",     last_name: "Çelik",      role: "executive_manager", job_title: "EV Teknoloji Lideri",           department: "Ar-Ge ve Tasarım",           process_codes: ["C2L"],          raci_role: "R", hire_year: 2024 }
  - { email: "tuncay.ozdemir@tomofil.test",   first_name: "Tuncay",    last_name: "Özdemir",    role: "executive_manager", job_title: "HSE Müdürü",                    department: "Sağlık-Güvenlik-Çevre",      process_codes: ["R2M"],          raci_role: "C", hire_year: 2021 }
  - { email: "ferda.bulut@tomofil.test",      first_name: "Ferda",     last_name: "Bulut",      role: "executive_manager", job_title: "Strateji ve PMO Lideri",        department: "Strateji ve PMO",            process_codes: ["S2E"],          raci_role: "R", hire_year: 2023 }
  - { email: "selin.akar@tomofil.test",       first_name: "Selin",     last_name: "Akar",       role: "executive_manager", job_title: "Pazarlama Yöneticisi",          department: "Pazarlama ve İletişim",      process_codes: ["A2R"],          raci_role: "C", hire_year: 2024 }
```

> **`calisanlar.json` üretim kuralları (generic seed script tarafından):**
> - 100 toplam çalışan (admin hariç)
> - 20 manuel yukarıda → kalan 80 = generic ad havuzu + departman dağılımına göre rastgele
> - Her birim için `hire_year` dağılımı pandemi grafiğine uyumlu (60 dipte 2022)
> - %22 kadın oran (2026), %30 hedef (KPI ile uyumlu)

---

# 9️⃣ KPI GEÇMİŞ VERİ — KARMA SIKLIK

```yaml
kpi_data_bulk_file: "docs/tomofil-demo/kpi_data.json"

# ÜRETİM KURALLARI:
#   - 2026 (aktif): 50 KPI × 5 ay (Ocak-Mayıs) = 250 satır (aylık)
#                  + bazıları çeyreklik/yıllık → toplam ~300 satır
#   - 2025: ~46 KPI × 4 çeyrek = ~184 satır (çeyreklik)
#   - 2024: ~40 KPI × 4 çeyrek = ~160 satır (çeyreklik)
#   - 2023: ~32 KPI × 1 yıllık = ~32 satır
#   - 2022: ~24 KPI × 1 yıllık = ~24 satır
#   - 2021: ~22 KPI × 1 yıllık = ~22 satır
#   TOPLAM ≈ 720-1.150 satır
#
# TRAJECTORY (her KPI için):
#   - Başlangıç değeri = onceki_yil_ortalamasi'nin 1-2 yıl gerisi
#   - Bitiş değeri = 2026 target_value civarı (gerçekleşme genelde %85)
#   - Pandemi yıl (2022) sapma: P2M-01 OEE gibi üretim KPI'larında -%15 düşüş
#   - EV KPI'lar 2024 öncesi yok (NULL — KPI henüz aktif değildi)
#   - Trend gerçekçi: random walk + lineer iyileşme
```

> **Aksiyon:** `kpi_data.json` dosyası generic seed script yazılırken **kurala dayalı** olarak üretilecek.

---

# 🔟 SÜREÇ FAALİYETLERİ

```yaml
process_activities:
  # 2024 EV pivotu kapsamında
  - { process_code: "C2L", name: "E-motor Stator Lamination Hat Kurulumu", description: "İlk e-motor stator hattı devreye alma — TOGG ve Renault Türkiye için.", start_date: "2024-01-15", end_date: "2024-09-30", status: "Tamamlandı", progress: 100, assignees: ["leyla.celik@tomofil.test"], linked_kpi_code: "P2M-05" }
  - { process_code: "C2L", name: "Hairpin Sargı Teknolojisi Lisansı (Bosch)", description: "Bosch ile teknoloji transfer + ortak APQP süreci.", start_date: "2024-06-01", end_date: "2025-12-31", status: "Devam Ediyor", progress: 80, assignees: ["leyla.celik@tomofil.test","taylan.koc@tomofil.test"], linked_kpi_code: "C2L-04" }
  - { process_code: "P2M", name: "5-Eksen İşleme Merkezi #3 Yatırımı", description: "DMG Mori 5-eksen alımı + devreye alma.", start_date: "2025-03-01", end_date: "2025-12-31", status: "Tamamlandı", progress: 100, assignees: ["mehmet.aktas@tomofil.test"], linked_kpi_code: "P2M-01" }
  - { process_code: "B2R", name: "Alüminyum Hurda Geri Dönüşüm Hattı Kurulumu", description: "İçeride döküm yerine geri kazanım hattı.", start_date: "2024-09-01", end_date: "2025-06-30", status: "Tamamlandı", progress: 100, assignees: ["ipek.gunes@tomofil.test","mehmet.aktas@tomofil.test"], linked_kpi_code: "B2R-01" }
  - { process_code: "R2M", name: "CBAM Hazırlık Programı (Faz 1)", description: "Karbon ölçüm + raporlama altyapısı + tedarikçi yönlendirme.", start_date: "2025-04-01", end_date: "2026-12-31", status: "Devam Ediyor", progress: 65, assignees: ["ipek.gunes@tomofil.test","okan.celikkol@tomofil.test"], linked_kpi_code: "R2M-01" }
  - { process_code: "P2M", name: "Çatı GES Yatırımı 250 kWp", description: "Çatı güneş enerjisi devreye alma.", start_date: "2026-02-01", end_date: "2026-09-30", status: "Devam Ediyor", progress: 55, assignees: ["ipek.gunes@tomofil.test"], linked_kpi_code: "P2M-06" }
  - { process_code: "D2I", name: "Predictive Maintenance Pilot (Hat 2)", description: "5 CNC tezgah + ML model.", start_date: "2026-03-15", end_date: "2026-10-31", status: "Devam Ediyor", progress: 35, assignees: ["fatih.demirel@tomofil.test","burak.yilmaz@tomofil.test"], linked_kpi_code: "D2I-01" }
  - { process_code: "D2I", name: "Dijital İkiz — Hat 2 PoC", description: "Sanal devreye alma + senaryo testi.", start_date: "2026-04-01", end_date: "2026-12-31", status: "Devam Ediyor", progress: 20, assignees: ["fatih.demirel@tomofil.test"], linked_kpi_code: "D2I-02" }
  # Eski (2022-2023)
  - { process_code: "H2R", name: "Pandemi Sonrası Kadro Yapılandırma", description: "2022 daraltma sonrası 2023 toparlanma + yeni işe alım planı.", start_date: "2023-01-01", end_date: "2023-06-30", status: "Tamamlandı", progress: 100, assignees: ["pinar.aksoy@tomofil.test"], linked_kpi_code: "H2R-01" }
  - { process_code: "A2R", name: "İlk Avrupa Müşteri Kazanımı (Almanya)", description: "VW Group tier-2 onboarding süreci.", start_date: "2023-02-01", end_date: "2023-11-30", status: "Tamamlandı", progress: 100, assignees: ["mert.aslan@tomofil.test"], linked_kpi_code: "A2R-04" }
```

---

# 1️⃣1️⃣ PROJE PORTFÖYÜ

```yaml
projects:
  - name: "EV Pivot — e-Motor Stator Hattı"
    description: "Tomofil'in en kritik stratejik projesi. EV parça portföyünün omurgası."
    start_date: "2024-01-15"
    end_date: "2025-12-31"
    priority: "Yüksek"
    manager_email: "leyla.celik@tomofil.test"
    health_status: "İyi"
    linked_sub_strategy_codes: ["5.A.1", "5.A.3"]
    tasks:
      - { title: "Yatırım onayı + makine seçimi",  assignee_email: "cansu.aydin@tomofil.test", start_date: "2024-01-15", end_date: "2024-04-30", status: "Tamamlandı", priority: "High" }
      - { title: "Hat kurulumu (Schuler pres + Trumpf laser)", assignee_email: "mehmet.aktas@tomofil.test", start_date: "2024-05-01", end_date: "2024-08-31", status: "Tamamlandı", priority: "High" }
      - { title: "Hairpin sargı pilot lot (Bosch lisans)", assignee_email: "leyla.celik@tomofil.test", start_date: "2024-09-01", end_date: "2025-06-30", status: "Tamamlandı", priority: "High" }
      - { title: "PPAP — TOGG için ilk 50 örnek", assignee_email: "taylan.koc@tomofil.test", start_date: "2025-07-01", end_date: "2025-12-31", status: "Tamamlandı", priority: "High" }

  - name: "CBAM Uyum Programı"
    description: "Avrupa CBAM zorunluluğu öncesi karbon ayak izi hazırlığı."
    start_date: "2025-04-01"
    end_date: "2026-12-31"
    priority: "Yüksek"
    manager_email: "ipek.gunes@tomofil.test"
    health_status: "İyi"
    linked_sub_strategy_codes: ["4.A.2", "6.A.1"]
    tasks:
      - { title: "Scope 1+2 ölçüm metodolojisi", assignee_email: "ipek.gunes@tomofil.test", start_date: "2025-04-01", end_date: "2025-09-30", status: "Tamamlandı", priority: "High" }
      - { title: "Tedarikçi karbon beyanı toplama", assignee_email: "ali.kaplan@tomofil.test", start_date: "2025-08-01", end_date: "2026-06-30", status: "Devam Ediyor", priority: "High" }
      - { title: "Çatı GES devreye alma (250 kWp)", assignee_email: "ipek.gunes@tomofil.test", start_date: "2026-02-01", end_date: "2026-09-30", status: "Devam Ediyor", priority: "Medium" }
      - { title: "Karbon raporlama yazılımı entegrasyonu", assignee_email: "fatih.demirel@tomofil.test", start_date: "2026-05-01", end_date: "2026-11-30", status: "Yapılacak", priority: "Medium" }

  - name: "Industry 4.0 — Predictive Maintenance"
    description: "OEE %72→%88 hedefinin ana yatırımı."
    start_date: "2026-01-01"
    end_date: "2027-06-30"
    priority: "Yüksek"
    manager_email: "fatih.demirel@tomofil.test"
    health_status: "İyi"
    linked_sub_strategy_codes: ["7.A.1", "7.A.2"]
    tasks:
      - { title: "Hat 2'ye IoT sensör montajı (5 tezgah)", assignee_email: "burak.yilmaz@tomofil.test", start_date: "2026-03-15", end_date: "2026-06-30", status: "Devam Ediyor", priority: "High" }
      - { title: "ML model geliştirme + eğitim verisi",      assignee_email: "fatih.demirel@tomofil.test", start_date: "2026-04-01", end_date: "2026-10-31", status: "Devam Ediyor", priority: "High" }
      - { title: "Dijital ikiz simülasyon ortamı",            assignee_email: "fatih.demirel@tomofil.test", start_date: "2026-05-01", end_date: "2026-12-31", status: "Devam Ediyor", priority: "Medium" }

  - name: "Avrupa İhracat — VW Onboarding"
    description: "VW Group tier-1 sertifikasyon süreci."
    start_date: "2025-09-01"
    end_date: "2027-03-31"
    priority: "Yüksek"
    manager_email: "mert.aslan@tomofil.test"
    health_status: "Risk"
    linked_sub_strategy_codes: ["4.A.1"]
    tasks:
      - { title: "VW Formel Q denetim hazırlığı", assignee_email: "ozge.kara@tomofil.test", start_date: "2025-09-01", end_date: "2026-04-30", status: "Tamamlandı", priority: "High" }
      - { title: "Tier-1 onaylı sertifikasyon",   assignee_email: "mert.aslan@tomofil.test", start_date: "2026-05-01", end_date: "2027-03-31", status: "Devam Ediyor", priority: "High" }
```

---

# 1️⃣2️⃣ SWOT — 2026 (her yıl için ayrı, burada 2026 örnek)

```yaml
swot:
  plan_year: 2026
  strengths: |
    • IATF 16949 + ISO 9001 + ISO 14001 + ISO 45001 dörtlü sertifika
    • Bursa Demirtaş OSB'de stratejik konum (OEM müşterilerine 30 km)
    • Hairpin sargı teknolojisi lisansı (Türkiye'de sınırlı oyuncu)
    • TOGG ile aktif tedarik anlaşması (EV pazarındaki ilk yerli oyuncu)
    • Sıfır borç, %22 EBITDA marjı
    • 6 yıllık kurumsal yönetişim olgunluğu (kuruluştan kokpitim kullanımı)
  weaknesses: |
    • Müşteri konsantrasyonu yüksek: top 3 müşteri %58 ciro
    • Avrupa pazarına henüz tier-1 olarak doğrudan giremiyor (VW süreci devam)
    • Predictive maintenance / dijital ikiz henüz pilot aşamada
    • 100 çalışanlık ölçekte CAPEX yatırım gücü sınırlı
    • Ar-Ge yatırımı/ciro oranı %4 — global rakiplerin gerisinde
  opportunities: |
    • Türkiye EV pazarı 2030'a kadar 5x büyüyor (TOGG, Anadolu Isuzu vb.)
    • Avrupa otomotiv tedarik zincirinde Türkiye yükselen oyuncu (post-China+1+1)
    • CBAM hazırlığı tamamlanmışlık avantaja dönüşebilir
    • Yerli ve milli teşvikler (TÜBİTAK + KOSGEB)
    • V2G/V2H teknolojisi için erken pozisyonlanma
  threats: |
    • TL volatilitesi (hammadde %45 ithal)
    • Çin EV parça üreticilerinin Avrupa'ya dümdüz girmesi
    • Chip krizinin yeniden alevlenmesi (semi shortage)
    • Hammadde fiyat artışı (lityum, neodimyum)
    • Yetenekli mühendis havzasının Almanya'ya kaybedilmesi
```

(Seed script her yıl için ayrı SWOT üretecek — 2021'de "kuruluş heyecanı + sıfır müşteri", 2022 "pandemi+chip kriz" vs.)

---

# 1️⃣3️⃣ TOWS / 1️⃣4️⃣ PESTEL / 1️⃣5️⃣ PORTER — 2026

> Yapı SWOT ile aynı, her yıl için ayrı kayıt. **Seed script kuralları:**
> - SWOT/TOWS/PESTEL/Porter her yıl için 1 kayıt (toplam 6 yıl × 4 = 24 analiz)
> - 2026 detaylı yazılır (yukarıda örnek); 2021-2025 için kısaltılmış metinler
> - Yıl bazlı tema: 2021 "kuruluş", 2022 "pandemi", 2023 "ihracat", 2024 "EV pivot", 2025 "ESG", 2026 "dijital"

```yaml
# Detaylı içerik 2026 için yazılır, geri kalan yıllar için tema-bazlı kısa metinler.
# Yer sınırı nedeniyle bu dosyada genişletilmedi.
analyses_year_themes:
  2021: "Kuruluş, ilk OEM müşteri, sıfır geçmiş veri"
  2022: "Pandemi + chip krizi, kadro daraltma, finansal stres"
  2023: "Toparlanma + Avrupa açılım, ihracat başlangıcı"
  2024: "EV pivot kararı, stratejik kırılma"
  2025: "Sürdürülebilirlik dalgası, CBAM hazırlık"
  2026: "Dijital dönüşüm, Industry 4.0"
```

---

# 1️⃣6️⃣ OKR — 2026 (5 ana objective)

```yaml
okrs:
  - { plan_year: 2026, quarter: null, title: "EV cirosu payını %38'den %48'e çıkar", owner: "Deniz Tunç (CEO)", key_results: [
      { title: "EV ciro payı (%) %38 → %48", metric: "%",     start_value: 38,    target_value: 48,    current_value: 41 },
      { title: "Yeni EV müşteri sayısı 0 → 2", metric: "adet", start_value: 0,    target_value: 2,     current_value: 1 },
      { title: "EV parça yıllık adedi 78k → 145k", metric: "adet", start_value: 78000, target_value: 145000, current_value: 95000 }
    ]}
  - { plan_year: 2026, quarter: null, title: "OEE %72 → %85 (Industry 4.0)", owner: "Cansu Aydın (COO)", key_results: [
      { title: "OEE (%) 72 → 85",                  metric: "%",   start_value: 72, target_value: 85, current_value: 76 },
      { title: "Predictive maintenance yakalama %", metric: "%",   start_value: 0,  target_value: 75, current_value: 28 },
      { title: "PPM hata oranı 180 → 50",            metric: "ppm", start_value: 180, target_value: 50, current_value: 110 }
    ]}
  - { plan_year: 2026, quarter: null, title: "Avrupa tier-1 sertifikasyonu (VW)", owner: "Sibel Demir (CMO)", key_results: [
      { title: "VW Formel Q skoru 75 → 92",          metric: "skor", start_value: 75, target_value: 92, current_value: 84 },
      { title: "Avrupa müşteri sayısı 2 → 4",         metric: "adet", start_value: 2,  target_value: 4,  current_value: 3 },
      { title: "İhracat ciro payı %22 → %32",        metric: "%",     start_value: 22, target_value: 32, current_value: 26 }
    ]}
  - { plan_year: 2026, quarter: null, title: "CBAM hazırlığını tamamla (2027 yürürlük öncesi)", owner: "İpek Güneş (CSO)", key_results: [
      { title: "Tedarikçi karbon beyanı %15 → %95", metric: "%", start_value: 15,    target_value: 95, current_value: 58 },
      { title: "Scope 1+2 ölçümü tamamlandı (binary)", metric: "0/1", start_value: 0, target_value: 1, current_value: 1 },
      { title: "Yenilenebilir enerji oranı %12 → %45", metric: "%", start_value: 12, target_value: 45, current_value: 22 }
    ]}
  - { plan_year: 2026, quarter: null, title: "eNPS +32 → +55 (Kurum kültürü güçlendirme)", owner: "Esin Demir (CHRO)", key_results: [
      { title: "eNPS skoru +32 → +55",                metric: "skor", start_value: 32, target_value: 55, current_value: 38 },
      { title: "Eğitim saati/kişi 26 → 48",            metric: "saat", start_value: 26, target_value: 48, current_value: 31 },
      { title: "Kadın mühendis oranı %18 → %30",       metric: "%",    start_value: 18, target_value: 30, current_value: 22 }
    ]}
```

(Seed script geçmiş yıllar için de OKR'lar üretir — 2021'de 3 OKR, 2022'de 3, 2023'te 4, 2024'te 5, 2025'te 5, 2026'da 5 → toplam ~25 objective, ~75 key result)

---

# 1️⃣7️⃣ K-VEKTOR (2026)

```yaml
k_vektor_weights:
  strategies:
    - { code: "H1", weight: 12 }   # Klasik motor — küçülüyor
    - { code: "H2", weight: 18 }   # Üretim kalitesi
    - { code: "H3", weight: 8  }   # İnsan
    - { code: "H4", weight: 14 }   # İhracat
    - { code: "H5", weight: 25 }   # EV — en yüksek ağırlık
    - { code: "H6", weight: 12 }   # Sürdürülebilirlik
    - { code: "H7", weight: 11 }   # Dijital dönüşüm
  sub_strategies:
    - { code: "5.A.1", weight: 35 }   # Stator lamination
    - { code: "5.A.2", weight: 25 }   # Rotor
    - { code: "5.A.3", weight: 20 }   # Hairpin
    - { code: "5.A.4", weight: 5  }   # V2G/V2H izleme
    - { code: "5.B.1", weight: 15 }   # Batarya kasası
    # (diğer ana stratejiler için weight dağılımı ben gözden geçirdikten sonra)
```

---

# 1️⃣8️⃣ K-RADAR (2026)

## 18.a Süreç Olgunluk

```yaml
process_maturity:
  - { process_code: "P2M", maturity_level: 4, dimension: "Üretim", assessed_by: "mehmet.aktas@tomofil.test" }
  - { process_code: "S2P", maturity_level: 3, dimension: "Tedarik", assessed_by: "ali.kaplan@tomofil.test" }
  - { process_code: "A2R", maturity_level: 3, dimension: "Satış", assessed_by: "sibel.demir@tomofil.test" }
  - { process_code: "C2L", maturity_level: 3, dimension: "Ar-Ge", assessed_by: "taylan.koc@tomofil.test" }
  - { process_code: "H2R", maturity_level: 3, dimension: "İK", assessed_by: "pinar.aksoy@tomofil.test" }
  - { process_code: "R2R", maturity_level: 4, dimension: "Finans", assessed_by: "okan.celikkol@tomofil.test" }
  - { process_code: "I2R", maturity_level: 4, dimension: "Müşteri", assessed_by: "esra.sen@tomofil.test" }
  - { process_code: "B2R", maturity_level: 2, dimension: "Geri Dönüşüm", assessed_by: "ipek.gunes@tomofil.test" }
  - { process_code: "R2M", maturity_level: 2, dimension: "Risk", assessed_by: "okan.celikkol@tomofil.test" }
  - { process_code: "D2I", maturity_level: 2, dimension: "Veri", assessed_by: "fatih.demirel@tomofil.test" }
  - { process_code: "S2E", maturity_level: 3, dimension: "Strateji", assessed_by: "ferda.bulut@tomofil.test" }
```

Ortalama: 3.0/5 → 2030 hedef: 4.2/5

## 18.b Darboğaz Logu

```yaml
bottlenecks:
  - { process_code: "P2M", kpi_code: "P2M-01", severity: "Yüksek", note: "Hat 2 CNC tezgahında plansız duruşlar artıyor", triggered_at: "2026-03-15" }
  - { process_code: "S2P", kpi_code: "S2P-01", severity: "Kritik", note: "Neodimyum mıknatıs tedariğinde Çin lead-time 18 hafta", triggered_at: "2026-02-10" }
  - { process_code: "C2L", kpi_code: "C2L-02", severity: "Orta",   note: "PPAP ilk-onay oranı %62 — sektör %85", triggered_at: "2026-01-20" }
```

## 18.c Değer Zinciri (Porter)

```yaml
value_chain:
  - { category: "primary", title: "Hammadde Kabul",         linked_process_code: "S2P", muda_type: "Bekleme",    note: "Sertifika kontrolü 18 saat" }
  - { category: "primary", title: "CNC İşleme",              linked_process_code: "P2M", muda_type: "Hareket",    note: "Operatör tezgah arası 12 dk" }
  - { category: "primary", title: "Montaj + Test",           linked_process_code: "P2M", muda_type: "Hata",        note: "EV stator test fixture sayısı yetersiz" }
  - { category: "primary", title: "Sevkiyat",                linked_process_code: "S2P", muda_type: "Stok",        note: "Bursa→Avrupa konteyner bekleme 5 gün" }
  - { category: "primary", title: "Müşteri Hizmeti (8D)",     linked_process_code: "I2R", muda_type: null,          note: "—" }
  - { category: "support", title: "Yönetişim",                linked_process_code: "S2E", muda_type: null,          note: "—" }
  - { category: "support", title: "Ar-Ge",                    linked_process_code: "C2L", muda_type: "Beklenti",    note: "Yeni teknoloji izleme dağınık" }
  - { category: "support", title: "İK + Eğitim",              linked_process_code: "H2R", muda_type: null,          note: "—" }
```

## 18.d EVM (Projeler)

```yaml
evm_snapshots:
  - { project_name: "EV Pivot — e-Motor Stator Hattı",       snapshot_date: "2024-12-31", pv: 4500000, ev: 4200000, ac: 4380000, spi: 0.93, cpi: 0.96 }
  - { project_name: "EV Pivot — e-Motor Stator Hattı",       snapshot_date: "2025-12-31", pv: 8200000, ev: 8050000, ac: 8150000, spi: 0.98, cpi: 0.99 }
  - { project_name: "CBAM Uyum Programı",                    snapshot_date: "2026-03-31", pv: 850000,  ev: 720000,  ac: 780000,  spi: 0.85, cpi: 0.92 }
  - { project_name: "Industry 4.0 — Predictive Maintenance", snapshot_date: "2026-04-30", pv: 620000,  ev: 540000,  ac: 580000,  spi: 0.87, cpi: 0.93 }
  - { project_name: "Avrupa İhracat — VW Onboarding",        snapshot_date: "2026-03-31", pv: 380000,  ev: 290000,  ac: 350000,  spi: 0.76, cpi: 0.83 }
```

## 18.e Risk Isı Haritası (2026)

```yaml
risks:
  - { plan_year: 2026, title: "AB CBAM yürürlüğe girmesi (2027)",                 probability: 5, impact: 5, owner_email: "ipek.gunes@tomofil.test",     status: "Mitigating", source_type: "pestel" }
  - { plan_year: 2026, title: "Neodimyum mıknatıs tedarik krizi",                  probability: 4, impact: 5, owner_email: "ali.kaplan@tomofil.test",      status: "Open",       source_type: "process" }
  - { plan_year: 2026, title: "TL volatilitesi — ithal hammadde",                  probability: 5, impact: 4, owner_email: "okan.celikkol@tomofil.test",   status: "Mitigating", source_type: "pestel" }
  - { plan_year: 2026, title: "Müşteri konsantrasyonu — top 3 müşteri %58 ciro",   probability: 3, impact: 5, owner_email: "sibel.demir@tomofil.test",     status: "Mitigating", source_type: "swot" }
  - { plan_year: 2026, title: "Chip krizinin yeniden alevlenmesi",                  probability: 3, impact: 5, owner_email: "ali.kaplan@tomofil.test",      status: "Open",       source_type: "pestel" }
  - { plan_year: 2026, title: "VW onboarding gecikmesi",                            probability: 3, impact: 4, owner_email: "mert.aslan@tomofil.test",      status: "Open",       source_type: "project" }
  - { plan_year: 2026, title: "Yetenekli mühendis kaybı (Almanya rekabeti)",         probability: 4, impact: 3, owner_email: "esin.demir@tomofil.test",     status: "Mitigating", source_type: "swot" }
  - { plan_year: 2026, title: "Predictive maintenance pilot başarısızlık riski",     probability: 2, impact: 3, owner_email: "fatih.demirel@tomofil.test",   status: "Open",       source_type: "project" }
  - { plan_year: 2026, title: "TOGG üretim takvimi gecikmesi (müşteri etkisi)",      probability: 3, impact: 4, owner_email: "sibel.demir@tomofil.test",     status: "Open",       source_type: "porter" }
  - { plan_year: 2026, title: "İSG kazası — yeni hat eğitim aşaması",                probability: 2, impact: 5, owner_email: "tuncay.ozdemir@tomofil.test", status: "Mitigating", source_type: "process" }
```

## 18.f Paydaş Haritası

```yaml
stakeholders:
  - { plan_year: 2026, name: "TOGG",                     role: "müşteri (EV)",     influence: 5, interest: 5, strategy: "Manage Closely" }
  - { plan_year: 2026, name: "Ford Otosan",               role: "müşteri (OEM)",    influence: 5, interest: 4, strategy: "Manage Closely" }
  - { plan_year: 2026, name: "Tofaş",                     role: "müşteri (OEM)",    influence: 4, interest: 4, strategy: "Manage Closely" }
  - { plan_year: 2026, name: "VW Group (potansiyel)",     role: "müşteri (Avrupa)", influence: 5, interest: 4, strategy: "Manage Closely" }
  - { plan_year: 2026, name: "Renault Türkiye",           role: "müşteri (OEM)",    influence: 3, interest: 3, strategy: "Keep Satisfied" }
  - { plan_year: 2026, name: "Bosch (lisans ortağı)",      role: "teknoloji ortağı", influence: 4, interest: 4, strategy: "Manage Closely" }
  - { plan_year: 2026, name: "Çelik/Alüminyum Tedarikçileri", role: "tedarikçi",      influence: 4, interest: 3, strategy: "Keep Satisfied" }
  - { plan_year: 2026, name: "Çalışanlar (üretim)",        role: "iç paydaş",        influence: 4, interest: 5, strategy: "Manage Closely" }
  - { plan_year: 2026, name: "Yatırımcılar / Ortaklar",   role: "yatırımcı",        influence: 5, interest: 5, strategy: "Manage Closely" }
  - { plan_year: 2026, name: "TÜBİTAK + KOSGEB",          role: "regülatör/teşvik", influence: 3, interest: 2, strategy: "Keep Informed" }
  - { plan_year: 2026, name: "Bursa OSB Yönetimi",         role: "topluluk",         influence: 2, interest: 3, strategy: "Keep Informed" }
  - { plan_year: 2026, name: "Çevre Bakanlığı (CBAM)",     role: "regülatör",        influence: 5, interest: 3, strategy: "Keep Satisfied" }
```

## 18.g Paydaş Anketleri (yıllık trend)

```yaml
stakeholder_surveys:
  - { stakeholder_type: "OEM Müşteri",  period: "2021", score: 35, comment: "İlk yıl baseline", source: "Annual Customer NPS" }
  - { stakeholder_type: "OEM Müşteri",  period: "2022", score: 28, comment: "Pandemi etki", source: "Annual Customer NPS" }
  - { stakeholder_type: "OEM Müşteri",  period: "2023", score: 42, comment: "Toparlanma", source: "Annual Customer NPS" }
  - { stakeholder_type: "OEM Müşteri",  period: "2024", score: 48, comment: "EV güveni", source: "Annual Customer NPS" }
  - { stakeholder_type: "OEM Müşteri",  period: "2025", score: 55, comment: "Sürdürülebilirlik kazanım", source: "Annual Customer NPS" }
  - { stakeholder_type: "OEM Müşteri",  period: "2026 Q1", score: 58, comment: "Trend pozitif", source: "Pulse" }
  - { stakeholder_type: "Çalışan",      period: "2021", score: 18, comment: "eNPS baseline kuruluş", source: "eNPS" }
  - { stakeholder_type: "Çalışan",      period: "2022", score: 8,  comment: "Pandemi dipte", source: "eNPS" }
  - { stakeholder_type: "Çalışan",      period: "2023", score: 22, comment: "Toparlanma", source: "eNPS" }
  - { stakeholder_type: "Çalışan",      period: "2024", score: 28, comment: "EV heyecan", source: "eNPS" }
  - { stakeholder_type: "Çalışan",      period: "2025", score: 32, comment: "İstikrar", source: "eNPS" }
  - { stakeholder_type: "Çalışan",      period: "2026 Q1", score: 38, comment: "Hedef yolda", source: "Pulse" }
  - { stakeholder_type: "Tedarikçi",    period: "2025", score: 42, comment: "İlk tedarikçi memnuniyet anketi", source: "Annual Supplier Survey" }
```

## 18.h A3 Raporları (2 örnek)

```yaml
a3_reports:
  - source_type: "process"
    problem: "OEE Hat 2'de %68'e düştü (hedef %80)"
    root_cause_json: |
      {"5_neden": [
        "Plansız duruşlar arttı",
        "CNC tezgah yaşlanıyor (2021 alımı)",
        "Bakım reaktif, predictive değil",
        "Operatör eğitimi standardize değil",
        "Yedek parça stoku optimize değil"
      ]}
    countermeasures: |
      • Predictive Maintenance pilotu (Hat 2 başlangıç)
      • Operatör standart eğitim modülü
      • Kritik yedek parça min-max stok seviyeleri
  - source_type: "process"
    problem: "PPAP ilk-onay oranı %62 (sektör %85)"
    root_cause_json: |
      {"5_neden": [
        "Müşteri spec'leri tam anlaşılmıyor",
        "FMEA güncel değil",
        "Ar-Ge ve Üretim arası iletişim zayıf",
        "DOE çalışmaları yetersiz",
        "PPAP dokümanı manuel hazırlanıyor"
      ]}
    countermeasures: |
      • Müşteri spec inceleme kontrol listesi
      • FMEA quarterly review
      • PPAP doküman otomasyonu (template)
```

## 18.i Rakip Analizi

```yaml
competitors:
  - { plan_year: 2026, competitor_name: "Anadolu Otomotiv (yerli)",  dimension: "Fiyat",          our_score: 65, their_score: 72 }
  - { plan_year: 2026, competitor_name: "Anadolu Otomotiv (yerli)",  dimension: "EV Yetkinliği",  our_score: 80, their_score: 45 }
  - { plan_year: 2026, competitor_name: "TI Türkiye (Avrupa kökenli)", dimension: "Kalite (PPM)", our_score: 78, their_score: 92 }
  - { plan_year: 2026, competitor_name: "TI Türkiye (Avrupa kökenli)", dimension: "Marka",        our_score: 45, their_score: 88 }
  - { plan_year: 2026, competitor_name: "BorgWarner (uluslararası)",  dimension: "EV Teknolojisi", our_score: 70, their_score: 95 }
  - { plan_year: 2026, competitor_name: "BorgWarner (uluslararası)",  dimension: "Esneklik",      our_score: 85, their_score: 55 }
  - { plan_year: 2026, competitor_name: "Çin Tedarikçileri (Geely)",  dimension: "Fiyat",          our_score: 65, their_score: 95 }
  - { plan_year: 2026, competitor_name: "Çin Tedarikçileri (Geely)",  dimension: "Lead-time",      our_score: 80, their_score: 70 }
```

---

# 1️⃣9️⃣ E-POSTA / SMTP

```yaml
email_config: null   # Demo için bildirim yok
```

---

# 2️⃣0️⃣ LOGO

```yaml
logo:
  source_file: "docs/tomofil-demo/logo-placeholder.png"  # Placeholder
```

---

# 2️⃣1️⃣ KAYNAK DÖKÜMANLAR

```yaml
documents:
  strategy_md:        "docs/tomofil-demo/sablon-dolu.md"
  employees_json:     "docs/tomofil-demo/calisanlar.json"   # Generic seed script üretecek
  raw_data_json:      "docs/tomofil-demo/kpi_data.json"     # Generic seed script üretecek
  company_pdf:        null
  strategic_plan_pdf: null
  other_files: []
```

---

# 📐 SEED ÇIKTI ÖNGÖRÜSÜ

| Tablo | Beklenen kayıt | Açıklama |
|-------|----------------|----------|
| tenants | 1 | |
| plan_years | 7 (2021-2027) | |
| users | **101** (1 admin + 20 manuel + ~80 toplu) | |
| strategies | ~32 (6 yıl × 3-7 ana) | yıl bazlı |
| sub_strategies | ~110 (6 yıl × 14-22 alt) | yıl bazlı |
| processes | ~50 (6 yıl × 6-10 süreç) | yıl bazlı |
| process_kpis | ~210 (6 yıl × 22-50 KPI) | yıl bazlı |
| process_owners_table | ~50 | yıl bazlı |
| **kpi_data** | **~720-1.150** | karma sıklık |
| process_activities | ~15 | |
| individual_performance_indicators | ~40 | |
| project | 4 | |
| task | 14 | |
| swot/tows/pestel/porter | 6 × 4 = 24 | her yıl |
| okr_objectives | ~25 (6 yıl × 3-5 obj) | |
| okr_key_results | ~75 | |
| k_vektor_*_weights | ~25 (sadece 2026) | |
| process_maturity | 11 | 2026 |
| bottleneck_log | 3-8 | |
| value_chain_items | 8 | |
| evm_snapshots | 5 | |
| risk_heatmap_items | 10 | |
| stakeholder_maps | 12 | |
| stakeholder_surveys | 13 (yıllık trend) | |
| a3_reports | 2 | |
| competitor_analyses | 8 | |

**Tahmini toplam: ~1.500-1.900 DB satırı** (kullanıcılar dahil)

---

# 🚦 PRE-SEED KONTROL LİSTESİ

- ☐ Tenant adı + short_name benzersiz mi? (`Tomofil` mevcut DB'de yok ✅ — silindi)
- ☐ Admin e-postası unique mi? (`admin@tomofil.test` ✅)
- ☐ 7 plan yılı: 6 closed + 1 active (2026) + 1 draft (2027) ✅
- ☐ Strateji evrimi mantıklı mı? (her yıl + ana strateji baz alınarak)
- ☐ Süreç evrimi mantıklı mı? (6→10 büyüme)
- ☐ KPI hedef değerleri yıllar arasında tutarlı mı?
- ☐ Kullanıcı kadro evrimi (pandemi etkili) gerçekçi mi?
- ☐ K-Vektor 2026 ağırlıkları toplamı=100 (ana strateji için)
- ☐ Logo placeholder dosyası var mı?
- ☐ Generic seed script `calisanlar.json` ve `kpi_data.json`'ı kurallı üretecek mi?

---

> **Şablon versiyon:** v2.0 (Tomofil EV pivot — 6 yıllık tarihçe)
> **Kaynak:** docs/sablon.md v1.0
> **Sonraki adım:** Generic seed script (`scripts/seed_generic_tenant.py`) — bu dosyayı + üretilecek JSON'ları okur, DB'ye yazar.
