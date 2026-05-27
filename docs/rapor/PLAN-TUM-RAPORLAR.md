# Tüm Raporlar — Kapsamlı Uygulama Planı

> **Tarih:** 2026-05-27 · **Versiyon:** 1.0
> **Bağlam:** [27mayisraporu.md](27mayisraporu.md) içindeki 100+ rapor başlığı için kapsam, veri kaynağı, tahmini iş, MVP/Full ayrımı ve risk.
> **Mevcut durum:** 10 rapor (8+9+10) yerelde **HAZIR**, kalan ~131 başlık burada planlanmıştır.
> **Kullanım:** Kullanıcı bu plandan istediği ürünü seçer → ayrıca TASK olarak açılır.

---

## 📊 Hızlı Özet

| Kategori | Toplam | Hazır | Kalan | Tahmini Toplam Saat |
|---|---|---|---|---|
| Stratejik | 24 | 6 | 18 | ~95h |
| Operasyonel & Süreç | 22 | 2 | 20 | ~80h |
| Finansal & EVM | 12 | 1 | 11 | ~55h |
| İK & Bireysel | 14 | 1 | 13 | ~50h |
| Risk, Uyum & Denetim | 16 | 0 | 16 | ~75h |
| ESG | 10 | 0 | 10 | ~45h |
| AI Ürünleri | 18 | 1 | 17 | ~280h |
| Yıllar Arası | 12 | 2 | 10 | ~55h |
| Persona Dashboard | 7 | 1 | 6 | ~120h |
| Sektörel Paket | 8 | 0 | 8 | ~280h |
| Altyapı (büyük) | 10 | 0 | 10 | ~600h |
| **TOPLAM** | **153** | **14** | **139** | **~1.735h** |

**~1.735 saat ≈ 1 kişi × 10 ay** ya da **3-4 kişi × 3-4 ay**.

---

## 🔑 Kullanılan Notasyon

| Kısaltma | Anlam |
|---|---|
| **S** | Small — 2-4 saat |
| **M** | Medium — 4-12 saat |
| **L** | Large — 12-30 saat |
| **XL** | Extra Large — 30-80 saat |
| **XXL** | Very Large — 80h+ |
| **MVP** | Minimum kullanılabilir versiyon (genelde 1/3 effort) |
| **Full** | Tam özellikli versiyon |
| 🟢 | Veri zaten var, doğrudan rapor edilir |
| 🟡 | Veri var ama hesaplama/agregasyon gerekli |
| 🔴 | Eksik veri var, yeni alanlar/tablolar gerekli |
| ⚡ | Hızlı kazanç (yüksek etki, düşük çaba) |

---

## 1. STRATEJİK RAPORLAR (18 kaldı)

| # | Ad | Veri kaynağı | Saat | MVP | Risk | Etiket |
|---|---|---|---|---|---|---|
| ST-01 | Stratejik Hiyerarşi **Sunburst** | strategies + sub_strategies + processes + K-Vektör | S(4h) | Tek sayfa SVG sunburst, hover tooltip | D3 öğrenme | 🟢 ⚡ |
| ST-02 | **SWOT Animasyonlu Diff** | swot_analyses 7 yıl | M(6h) | 2 yıl yan yana karşılaştırma | Semantic matching zor | 🟡 |
| ST-03 | PESTEL Trend | pestel_analyses 7 yıl | S(4h) | 6 kategori × 7 yıl mini-bar | — | 🟢 |
| ST-04 | Porter 5 Forces Spider Yıllık | porter_analyses | S(4h) | 7 yıl tek spider üst üste | — | 🟢 |
| ST-05 | Blue Ocean Value Curve Anim | blue_ocean_factors yıllık | M(8h) | Tek yıl statik, sonra anim | Veri sınırlı | 🟡 |
| ST-06 | **VRIO Portföy 4-Köşe Matrisi** | vrio_resources | S(4h) | 4 kuadrant tek görsel | — | 🟢 ⚡ |
| ST-07 | **BCG Matrix** | strategies × bağlı PG sayısı (proxy) | M(6h) | 4 kuadrant balon | "Pazar payı" verisi eksik | 🟡 |
| ST-08 | Ansoff Matrix | strategies + initiative kategorisi (manual etiket) | M(6h) | 4 kuadrant + manuel etiketleme UI | Kategori eksik | 🔴 |
| ST-09 | OKR Cascade Görseli | okr_objectives + okr_key_results + linked_strategy | M(8h) | Hiyerarşik tree (üst→alt→bireysel) | — | 🟢 ⚡ |
| ST-10 | BSC Dengelilik Skorboardu | bsc_kpi_perspectives | S(4h) | 4 perspektif × KPI sayısı + skor | — | 🟢 |
| ST-11 | **Initiative Roadmap Gantt** | initiatives + milestones | M(8h) | Tek Gantt vis.js timeline | — | 🟢 ⚡ |
| ST-12 | Stratejik Karar Geçmişi Timeline | audit_log + replan_trigger_events | M(8h) | "kim ne zaman ne değiştirdi" feed | Audit log filtreleme | 🟡 |
| ST-13 | Stratejik Risk Korelasyonu | risk_heatmap × strategy linkage | M(8h) | Manuel risk-strateji bağlantısı + heatmap | Bağ verisi eksik | 🔴 |
| ST-14 | Rakip Pozisyon Spider | competitor_analyses | S(4h) | 6 boyutlu radar, biz vs rakipler | — | 🟢 |
| ST-15 | Stratejik Maliyet Atıfı | initiative.budget × bağlı strategy | M(6h) | "ST3'e 7 yılda 4.3M harcandı" | — | 🟢 |
| ST-16 | **7-Yıllık Stratejik Yıllık Kitap** (250 sayfa PDF) | tüm SP veri | XL(80h) | 50 sayfa MVP | LLM 200 sayfa tutarsız, weasyprint render | 🟢 ⭐ |
| ST-17 | Stratejik Hizalama Kompozit Skor | hiyerarşi + skor + bağlantı | M(8h) | "Hizalama %72" tek skor + detay | Formül kararı | 🟡 |
| ST-18 | Stratejik Karar Destek Hub | yukarıdaki 17'sinin master sayfası | S(3h) | Kart-grid landing | — | 🟢 |

**Bu kategori toplam: ~177h, ortalama 10h/rapor. ⭐ Stratejik Yıllık 80h tek başına.**

---

## 2. OPERASYONEL & SÜREÇ RAPORLARI (20 kaldı)

| # | Ad | Veri kaynağı | Saat | MVP | Risk | Etiket |
|---|---|---|---|---|---|---|
| OP-01 | KPI Trend + Tahmin Detay Sayfası | kpi_data + forecast_service | M(6h) | Tek PG için 24ay + 6ay forecast | — | 🟢 ⚡ |
| OP-02 | OEE Operasyonel Detay | PG-UP01 (mevcut PG) | S(4h) | Availability×Performance×Quality breakdown | OEE bileşen verisi yok | 🔴 |
| OP-03 | Value Stream Mapping | processes hiyerarşi + activity süreleri | L(16h) | Statik VSM tek süreç | Akış tasarımı zor | 🟡 |
| OP-04 | 7 Muda Waste Analizi | muda_analyzer servisi var | M(6h) | Mevcut servisi sayfaya bağla | — | 🟢 ⚡ |
| OP-05 | Pareto 80/20 | kpi_data sapma frekansı | M(6h) | "%80 sorun şu 5 süreçte" | — | 🟢 |
| OP-06 | Darboğaz Frekans Raporu | bottleneck_log | S(4h) | Top 5 süreç, severity dağılımı | Veri ince | 🟡 |
| OP-07 | SLA Compliance Raporu | sla + actual completion | M(6h) | % uyum + breach sayısı + maliyet | — | 🟢 |
| OP-08 | Süreç-PG Katkı Hücreleri | process_sub_strategy_links + contribution_pct | M(6h) | 71×16 matris ısı haritası | — | 🟢 |
| OP-09 | Auto-PGV Etki Raporu | activity.auto_pgv_created flag | S(3h) | "X faaliyet otomatik PG verisi üretti" | — | 🟢 ⚡ |
| OP-10 | KPI Anomali Detay Sayfası | anomaly_service mevcut | S(4h) | Mevcut anomali listesi + detay | — | 🟢 ⚡ |
| OP-11 | Süreç Lideri/Üye Yük Dağılımı | process_members/leaders M:N + activity yükü | M(6h) | "kim aşırı yüklü" listesi | M:N veri eksik (Tomofil'de) | 🟡 |
| OP-12 | Süreç-Süreç Bağımlılık Haritası | processes.parent_id self-ref | S(4h) | Network graph tree | — | 🟢 |
| OP-13 | **Aylık Performans Bülteni** (otomatik PDF) | ayın özet verisi | L(12h) | Tek süreç için 5 sayfa, sonra batch | — | 🟢 ⭐ |
| OP-14 | Süreç Ekibi 360° Geri Bildirim | process_members + bireysel PG | L(20h) | Anket akışı + UI | Yeni süreç tasarımı | 🔴 |
| OP-15 | CMMI Olgunluk Heatmap | process_maturity | S(3h) | 71 süreç × 1-5 seviye heatmap | — | 🟢 ⚡ |
| OP-16 | Faaliyet Matrisi Detay | process_activities × ay/süreç | M(6h) | "K-Rapor"daki var ama geniş versiyon | — | 🟢 |
| OP-17 | Operasyonel İstatistik Sayfası | activity + task + KPI bugün | S(3h) | Tek sayfa "bugün ne oldu" | — | 🟢 ⚡ |
| OP-18 | Süreç Sağlık Karnesi Master | tüm süreçler tek heatmap | S(4h) | 71 süreç renkli grid | — | 🟢 ⚡ |
| OP-19 | KPI Manipülasyon Tespiti | kpi_data_audit pattern analizi | M(8h) | "sürekli güncellenen" PG flag | False positive | 🟡 |
| OP-20 | Veri Girişi Tamlığı Sayfa | kpi_data son giriş × PG | S(3h) | Veri Kalitesi'nde var ama detay | — | 🟢 |

**Toplam: ~133h.**

---

## 3. FİNANSAL & EVM RAPORLARI (11 kaldı)

| # | Ad | Veri kaynağı | Saat | MVP | Risk | Etiket |
|---|---|---|---|---|---|---|
| FN-01 | Plan-Proje EVM Detay Grafiği | plan_project_tasks (PV/EV/AC) | M(8h) | Tek proje SPI/CPI trend | EVM verisi eksik olabilir | 🟡 |
| FN-02 | CPM Kritik Yol Detay | plan_project_tasks + depends_on | M(8h) | vis.js network + kritik renk | — | 🟢 |
| FN-03 | Time Entry → Maliyet | time_entry × user.hourly_rate (eklenmeli) | M(8h) | hourly_rate alanı + maliyet hesap | Yeni veri alanı | 🔴 |
| FN-04 | Kapasite vs Talep Heatmap | capacity_plan × task atama | M(8h) | 97 user × 52 hafta grid | — | 🟢 |
| FN-05 | **ROI per Strategy** | initiative bütçe + strategy bağ × skor | M(6h) | "ST3'e 1₺ → 0.045 puan" | Formül kararı | 🟡 ⚡ |
| FN-06 | Initiative Geri Dönüş Yıllık | initiatives × success/fail × bütçe | M(6h) | Sınıflandırma + bütçe sapması | — | 🟢 |
| FN-07 | Sprint Velocity | sprint + task_sprint | S(4h) | Velocity trend grafiği | Story point veri eksik | 🟡 |
| FN-08 | Estimation Accuracy | task.estimated_time vs actual | S(4h) | Sapma histogram | — | 🟢 |
| FN-09 | Recurring Cost Analizi | recurring_task | S(4h) | Yıllık tahmini maliyet | — | 🟢 |
| FN-10 | SLA Breach Maliyet Tahmini | sla.breach_policy + sayım | S(3h) | Tahmini kayıp ₺ | — | 🟢 |
| FN-11 | **CFO Yıllık Finansal Konsolide** | tüm bütçe agregasyonu | L(12h) | Tek sayfa CFO dashboard | — | 🟢 ⭐ |

**Toplam: ~71h.**

---

## 4. İNSAN KAYNAKLARI & BİREYSEL (13 kaldı)

| # | Ad | Veri kaynağı | Saat | MVP | Risk | Etiket |
|---|---|---|---|---|---|---|
| HR-01 | **Bireysel Karne PDF Batch** | tüm aktif user × bireysel PG | M(8h) | Tek user PDF, sonra batch worker | weasyprint Türkçe font | 🟢 ⭐ |
| HR-02 | Çalışan Aktivite Yoğunluk Heatmap | audit_log × kullanıcı × hafta | M(6h) | 97×52 grid | — | 🟢 |
| HR-03 | Çalışan Bağlılık Skoru Kompozit | login + bildirim + PG doluluk | M(8h) | 5 kriterli formül + skor | Formül kararı | 🟡 |
| HR-04 | 360° Geri Bildirim Akışı | process_members × bireysel PG | XL(24h) | Anket akışı + agregasyon | Tam yeni süreç | 🔴 |
| HR-05 | **Eğitim İhtiyaç Analizi** (CMMI bazlı) | process_maturity + user × süreç | M(8h) | "L2 süreç üyesi şu eğitimi alsın" | — | 🟢 ⭐ |
| HR-06 | Liderlik Yedekleme Planı | process_leaders + user.successor (eklenmeli) | M(6h) | Successor alanı + risk matrisi | Yeni alan | 🔴 |
| HR-07 | Bireysel Hedef Hizalama | alignment_score servisi mevcut | S(4h) | Mevcut servisi sayfaya bağla | — | 🟢 ⚡ |
| HR-08 | Tenure-based Performans Heatmap | user.created_at + bireysel PG | S(4h) | 0-2, 2-5, 5-10, 10+ kohort | — | 🟢 |
| HR-09 | **Workforce Analytics Dashboard** | tüm İK metrikleri tek sayfa | L(12h) | Multi-widget İK ekranı | — | 🟢 ⭐ |
| HR-10 | Kullanıcı Yetki Matrisi | role × system_component | S(4h) | Matris görseli | — | 🟢 |
| HR-11 | Çalışan Hareket Geçmişi | audit_log üzerinden | M(6h) | Timeline view | — | 🟢 |
| HR-12 | İK Doğum Günü Bülteni | user + doğum_tarihi (eklenmeli) | S(3h) | Otomatik takvim | Yeni alan | 🔴 |
| HR-13 | CHRO Dashboard | yukarıdakileri 1 sayfada toparlar | L(12h) | Master İK ekranı | — | 🟢 ⭐ |

**Toplam: ~105h.**

---

## 5. RİSK, UYUM & DENETİM (16 başlık)

| # | Ad | Veri kaynağı | Saat | MVP | Risk | Etiket |
|---|---|---|---|---|---|---|
| RK-01 | **Risk Heat Map Detay** | risk_heatmap_items | S(4h) | 5×5 grid + balonlar | — | 🟢 ⚡ |
| RK-02 | Risk Trend Yıllık | risks × yıl | M(6h) | 7 yıllık trend grafiği | — | 🟢 |
| RK-03 | Risk-Strateji Çapraz Matrisi | risks × manual strategy etiket | M(8h) | Manuel etiketleme UI + matris | Bağ verisi eksik | 🔴 |
| RK-04 | Risk Sahip Performansı | risk.owner_id × mitigated/open | S(4h) | Sahip bazlı tablo | — | 🟢 |
| RK-05 | RAID Item Lifecycle | raid_item × tip × durum | M(6h) | 4 kategori timeline | — | 🟢 |
| RK-06 | **Compliance Audit Log (GDPR/KVKK)** | audit_logs filtered | M(8h) | Kişisel veri erişim raporu | KVKK kategorize zor | 🟡 ⭐ |
| RK-07 | Kullanıcı Hesap Anomali Tespiti | audit_log pattern | M(8h) | Olağandışı saat/IP/sıklık | False positive | 🟡 |
| RK-08 | 2FA Kullanım Raporu | users.totp_enabled | S(3h) | Tenant başına % oran | — | 🟢 ⚡ |
| RK-09 | **KPI Manipülasyon Tespiti** | kpi_data_audit pattern | M(8h) | Sürekli update / yuvarlama / geriye dönük | False positive | 🟡 ⭐ |
| RK-10 | ISO 9001 Süreç Uyum Raporu | processes KYS metadata | M(6h) | document_no + revision yaş + uyum | — | 🟢 |
| RK-11 | Quarterly Review Cycle Raporu | quarterly_review servisi | S(4h) | Mevcut servisi sayfa | — | 🟢 |
| RK-12 | Replan Trigger Yıllık Özet | replan_triggers × events | S(4h) | Tetik bazlı sayım + last_fired | — | 🟢 |
| RK-13 | Risk Mitigation Effectiveness | risk mitigated sonrası strateji skor | L(12h) | Korelasyon analizi | İstatistiksel test | 🟡 |
| RK-14 | **Üçüncü Parti Audit Çıktı Paketi** | tüm SP + audit log | L(16h) | Denetçi için 50 sayfalık PDF | weasyprint büyük PDF | 🟢 ⭐ |
| RK-15 | Çevresel Uyum (ESG-E) | esg_metric_values scope1+2+3 | S(4h) | CDP/GRI şablon | — | 🟢 |
| RK-16 | İncident Post-Mortem AI Şablonu | a3_reports + AI | M(8h) | Boş A3 form + AI doldur önerisi | LLM prompt | 🟡 |

**Toplam: ~109h.**

---

## 6. ESG & SÜRDÜRÜLEBİLİRLİK (10 başlık)

| # | Ad | Veri kaynağı | Saat | MVP | Risk | Etiket |
|---|---|---|---|---|---|---|
| ES-01 | **Carbon Footprint Toplam Trend** | esg_metric_values scope1+2+3 | S(4h) | 7 yıllık çizgi grafiği + Net Zero hedef | Veri sınırlı | 🟢 ⚡ |
| ES-02 | Carbon Intensity | scope × gelir veya çalışan sayısı | S(3h) | Normalize karbon | Gelir verisi eksik | 🟡 |
| ES-03 | **SDG Katkı Haritası** | esg_metrics.sdg_codes | M(6h) | BM 17 SDG renk haritası | — | 🟢 ⭐ |
| ES-04 | ESG Kompozit Skor | E+S+G × ağırlık | M(6h) | Tek skor + alt breakdown | Ağırlık kararı | 🟡 |
| ES-05 | Su/Enerji/Atık Trio Çizelgesi | esg_metric_values (eksik) | M(6h) | 3 metrik trend | Veri yok (Tomofil sadece 5 metrik) | 🔴 |
| ES-06 | Sosyal Etki (S) Raporu | LTIFR + çeşitlilik metrikleri | M(6h) | Çoklu sosyal metrik panel | Veri eksik | 🔴 |
| ES-07 | Yönetişim (G) Skoru | Bağımsız üye, etik şikayet (eksik) | M(6h) | Manuel girilen G metrikleri | Veri yok | 🔴 |
| ES-08 | **GRI/CDP/TCFD Yıllık Rapor** | tüm ESG | L(16h) | GRI standart formatında PDF | Şablon kompleks | 🟡 ⭐ |
| ES-09 | Tedarikçi Sürdürülebilirlik Skoru | stakeholder_survey tedarikçi tipi | M(6h) | Tedarikçi havuz puanı | Veri yok | 🔴 |
| ES-10 | İklim Risk Senaryo Modellemesi | Monte Carlo × ESG | L(16h) | 2°C / 4°C senaryo simülasyonu | Karmaşık model | 🔴 |

**Toplam: ~75h. Çoğunluğu veri eksikliği — Tomofil'in ESG metrikleri sınırlı.**

---

## 7. AI ÜRÜNLERİ (17 kaldı)

| # | Ad | Veri kaynağı | Saat | MVP | Risk | Etiket |
|---|---|---|---|---|---|---|
| AI-01 | **AI Doğal Dil Sorgu (NLP→SQL)** | tüm tablolar + LLM | XL(60h) | 10 pre-defined pattern, sonra free-form | SQL injection, hatalı SQL | 🟢 ⭐⭐ |
| AI-02 | AI Strateji Danışmanı | strategies + kpi_data + LLM | M(12h) | ai_pivot_advisor servisi mevcut + sayfa | LLM tutarsız | 🟢 ⚡ |
| AI-03 | AI Sabah Özeti (artırılmış) | mevcut + LLM tonlama | S(4h) | Mevcut "executive_morning" + AI rewrite | — | 🟢 ⚡ |
| AI-04 | AI Coach | her PG sayfasında "Bu PG için 3 öneri" | M(8h) | ai_coach_service var, UI'a bağla | — | 🟢 ⚡ |
| AI-05 | AI Early Warning Dashboard | early_warning_service var | S(4h) | Mevcut servisi sayfaya | — | 🟢 ⚡ |
| AI-06 | AI Toplantı Tutanağı Üretici | quarterly_review + LLM | M(12h) | Q sonu agenda + alınan kararlar | — | 🟢 |
| AI-07 | AI SWOT Otomatik Üretimi | tüm sistem + LLM | M(12h) | 6 ay veri → AI SWOT taslağı | LLM accuracy | 🟡 |
| AI-08 | AI Strateji Çelişki Tespiti | strategies + kpi × LLM | L(16h) | "ST3 ve ST5 çelişiyor mu?" | Karmaşık prompt | 🟡 |
| AI-09 | AI PDF Rapor Özetleyici | yüklenen PDF + LLM | M(12h) | 50 sayfa → 3 sayfa özet | PDF parse hatası | 🟡 |
| AI-10 | **AI Sektör Benchmark** | tenant + sektör public data + LLM | XL(40h) | Otomotiv için manuel benchmark + AI yorum | Public data toplama | 🔴 ⭐ |
| AI-11 | AI Quarterly Review Hazırlayıcısı | plan_year_diff + LLM | M(12h) | Toplantı öncesi agenda + ön soru | — | 🟢 ⭐ |
| AI-12 | **AI Strateji Hikayeleştirici (7 yıl)** | tüm yıl verisi + LLM | L(20h) | 5 sayfa narrative | LLM uzun anlatım tutarsız | 🟢 ⭐ |
| AI-13 | AI Personel Geri Bildirim Asistanı | bireysel PG + faaliyet + LLM | M(12h) | 6 aylık değerlendirme taslağı | Bias riski | 🟡 |
| AI-14 | AI Risk Senaryosu Üretici | tenant.sector + LLM | M(8h) | "10 olası risk listele" | Sektör bilgisi | 🟢 |
| AI-15 | AI A3 Problem Çözme Yardımcısı | a3_reports + LLM | M(8h) | A3 form üzerinde "Önerilen kök neden" | — | 🟢 |
| AI-16 | AI Initiative Bağımsız Değerlendirme | initiative + benchmark + LLM | M(12h) | "Bu ROI mantıklı mı?" | — | 🟡 |
| AI-17 | **AI Yatırımcı Sunum Üretici** | tüm yıl verisi + python-pptx + LLM | XL(30h) | 30-40 slayt PPTX (AI Yıl Sonu Sunum'un genişletilmiş hali) | python-pptx grafik | 🟢 ⭐ |

**Toplam: ~282h. AI Doğal Dil Sorgu tek başına ~60h.**

---

## 8. YILLAR ARASI KARŞILAŞTIRMA (10 kaldı)

| # | Ad | Veri kaynağı | Saat | MVP | Risk | Etiket |
|---|---|---|---|---|---|---|
| YA-01 | **Vizyon Evrim Sankey** | tenant_year_identities + AI semantic | M(8h) | Sade benzerlik karşılaştırma | Semantic similarity model | 🟡 ⭐ |
| YA-02 | Strateji Yaşam Çizgisi | strategies × plan_year_id | M(6h) | Her stratejinin yıl aralığı timeline | — | 🟢 |
| YA-03 | **Hedef Tutturma Yıllık** | kpi_data × hedef başarı oranı | M(8h) | Yıllık % başarı + trend | — | 🟢 ⭐ |
| YA-04 | K-Vektör Ağırlık Evrim | k_vektor_strategy_weights × yıl | S(4h) | Stacked area chart | Yıllık snapshot eksik (mevcut tek versiyon) | 🟡 |
| YA-05 | SWOT Maddesi Yolculuğu | swot 7 yıl + semantic | L(16h) | "Bu zayıf yön güçlü oldu mu" semantic | NLP model | 🔴 |
| YA-06 | Risk Devrimi Yıllık | risk × yıl × P/I değişim | M(6h) | Aynı risk yıl yıl trend | Risk ID stabilitesi | 🟡 |
| YA-07 | Initiative Başarı Atlas | initiatives × completed/cancelled × bütçe | M(6h) | Sınıflandırma + görsel atlas | — | 🟢 |
| YA-08 | OKR Cycle Karşılaştırma | okr_objectives × yıl | S(4h) | Önceki yıl vs bu yıl tablo | — | 🟢 |
| YA-09 | Çalışan Hareket Heatmap | user.created_at + soft delete | M(6h) | Yıl içinde giren/çıkan | Soft delete tarihleri eksik | 🟡 |
| YA-10 | **Yıllık Şirket Sağlık Kompozit Skoru** | 6-7 boyut × ağırlık | L(12h) | Tek skor + alt detay | Formül + ağırlık kararı | 🟡 ⭐ |

**Toplam: ~76h.**

---

## 9. PERSONA DASHBOARD'LARI (6 kaldı)

> Her dashboard ~12-20h. Mevcut "Executive Dashboard" var, bunlar onun kardeşleri.

| # | Persona | Veri | Saat | İçerik |
|---|---|---|---|---|
| PD-01 | **CFO Dashboard** | initiative + EVM + recurring cost + maliyet | L(16h) | Bütçe sapma + EVM kompozit + ROI + LLM cost |
| PD-02 | **COO Dashboard** | süreç sağlık + OEE + SLA + darboğaz | L(16h) | Süreç heatmap + 7 muda + Pareto |
| PD-03 | **CHRO Dashboard** | İK metrikleri | L(16h) | Workforce + departman + bağlılık + eğitim |
| PD-04 | CMO Dashboard | NPS + CSAT + müşteri perspektifi BSC | L(16h) | Müşteri yolculuk + rakip + brand |
| PD-05 | CSO (Sürdürülebilirlik) Dashboard | ESG | L(16h) | Carbon + SDG + sosyal etki |
| PD-06 | Sales Manager Dashboard | satış süreçleri PG | L(16h) | Bölgesel + segment + funnel |

**Toplam: ~96h. Tek dashboard ortalama 16h.**

**Tasarım kararı:** Hepsi aynı widget framework (`dashboard_widgets.py` var) üzerinde, JSON config ile.

---

## 10. SEKTÖREL PAKETLER (8 sektör)

> Her paket: 50-100 sayfa strateji + süreç + PG + risk şablonu, JSON formatında, tek tıkla tenant'a yüklenebilir.

| # | Sektör | KPI öncelik | Saat | Notlar |
|---|---|---|---|---|
| SP-01 | **Otomotiv / Üretim** | OEE, PPM, OTIF, lead time, capacity | L(30h) | Tomofil zaten örnek, derinleştir |
| SP-02 | Sağlık / Hastane | Bekleme süresi, doluluk, mortalite, infection | XL(40h) | JCI/HIMSS uyum |
| SP-03 | Eğitim / Üniversite | Mezun memnuniyet, kontenjan, başarı, yayın | L(30h) | YÖK/ABET/AACSB |
| SP-04 | Finans / Banka | NPL, capital adequacy, ROE, customer LTV | XL(40h) | BDDK + Basel III |
| SP-05 | Belediye / Kamu | Vatandaş memnuniyeti, hizmet süresi, şikayet | L(30h) | Şeffaflık dashboard |
| SP-06 | Perakende / Zincir | Stok devir, sepet, satış/m², sıklık | L(30h) | Omnichannel |
| SP-07 | İnşaat / Müteahhitlik | Proje karlılık, plan-gerçek, LTIR | L(30h) | İş güvenliği ağır |
| SP-08 | Hizmet / Danışmanlık | Utilization, billable %, customer sat, margin | M(20h) | Daha basit |

**Toplam: ~250h. Bir sektör paketi ~30h.**

**Strateji:** Önce Otomotiv'i mükemmelleştir (Tomofil), sonra 2 sektör daha pilot, sonra otomatik şablon üretimi.

---

## 11. BÜYÜK ALTYAPI YATIRIMLARI (10 büyük başlık)

| # | Ad | Açıklama | Saat | Kategori |
|---|---|---|---|---|
| IF-01 | **Mobile Native App** (iOS + Android) | React Native, 4 ana ekran, push notification | XXL(220h) | Yeni stack |
| IF-02 | **PowerPoint Export Geneli** | Her dashboard'dan PPT, template marketplace | L(50h) | python-pptx |
| IF-03 | **BI Connector (Tableau/Power BI)** | OData v4 endpoint | L(60h) | Spec öğrenme |
| IF-04 | **NLP → SQL Doğal Dil Sorgu** | LLM destekli güvenli SQL | XL(70h) | AI-01 ile aynı |
| IF-05 | **ML Anomali (Isolation Forest, LSTM)** | scikit-learn / PyTorch | XL(60h) | Mevcut z-score'un üstüne |
| IF-06 | **Workflow Engine (BPMN)** | Görsel akış + approval chains | XXL(150h) | Camunda alternatifi |
| IF-07 | **External Data Ingestion (SAP/Oracle adapter)** | ERP'den otomatik KPI akışı | XL(80h) | Adapter framework |
| IF-08 | **Document Management + Versioning** | Süreç dokümanları için | L(40h) | MinIO/S3 storage |
| IF-09 | **Form Builder** | KPI veri girişi için dinamik form | L(50h) | JSON schema |
| IF-10 | **Approval Chains** | Initiative onay zinciri | M(30h) | Workflow küçük versiyon |

**Toplam: ~810h. Bunlar 1+ kişi-yıl yatırımları.**

---

## ⚡ HIZLI KAZANÇ MATRİSİ — sol-üst yapılmalı

Effort (X) × Etki (Y) düşük→yüksek:

```
Y EKSEN: ETKİ (1-5)
5 ┤        AI-12     │ IF-04 NLP  │ SP-01-08
  │      Hikaye     │           │   Sektör
4 ┤ ⚡AI-02-05      │ HR-09       │ IF-01 Mobile
  │   AI Coach v.s. │ Workforce   │
3 ┤ ⚡ST-01 Sunburst│ PD-01-03    │ IF-02 PPT Export
  │ ⚡ST-09 OKR     │ CFO/COO/CHRO│
  │ ⚡OP-04 Muda    │             │
2 ┤ ⚡FN-05 ROI     │ AI-11 QR    │ ES-08 GRI/CDP
  │ ⚡HR-07 Hizal.  │ Quarterly   │
1 ┤ ⚡RK-08 2FA     │             │ IF-06 BPMN
  └─────────────────┼─────────────┼──────────────
   DÜŞÜK ÇABA     ORTA           BÜYÜK
   (X EKSEN: ÇABA)
```

**Hızlı kazançlar (sol-üst):** ~30 başlık × ortalama 4h = ~120h (3 hafta) → çok wow etki.

---

## 🎯 ÖNCELİKLENDİRME ÖNERİLERİ

### Faz 1 — "Wow lansman" (1 ay)
Mevcut 10 raporun üstüne hızlı kazançlar:
- ST-01 Sunburst (4h)
- ST-06 VRIO (4h)
- ST-09 OKR Cascade (8h)
- ST-11 Initiative Gantt (8h)
- OP-04 7 Muda (6h)
- OP-15 CMMI Heatmap (3h)
- OP-17 Op. İstatistik (3h)
- FN-05 ROI per Strategy (6h)
- HR-07 Bireysel Hizalama (4h)
- RK-01 Risk Heatmap (4h)
- RK-08 2FA Raporu (3h)
- ES-01 Carbon Trend (4h)
- AI-02 AI Strateji Danışman (12h)
- AI-04 AI Coach (8h)
- AI-05 AI Early Warning Dashboard (4h)

**Toplam:** 15 hızlı rapor × ~5h = **~80h** (yaklaşık 2 hafta tek kişi).

### Faz 2 — "Persona deneyimi" (2 ay)
- PD-01 CFO Dashboard (16h)
- PD-02 COO Dashboard (16h)
- PD-03 CHRO Dashboard (16h)
- HR-09 Workforce Analytics (12h)
- HR-13 CHRO Dashboard (12h)
- AI-11 Quarterly Review Hazırlayıcısı (12h)
- AI-12 Strateji Hikayeleştirici (20h)

**Toplam:** **~104h** (3 hafta).

### Faz 3 — "Premium ürünler" (3 ay)
- ST-16 Stratejik Yıllık Kitap (80h)
- AI-17 Yatırımcı Sunum (30h) — AI-10'un genişlemesi
- ES-08 GRI/CDP/TCFD (16h)
- RK-14 Audit Çıktı Paketi (16h)
- HR-01 Bireysel Karne PDF batch (8h)

**Toplam:** **~150h** (~1 ay).

### Faz 4 — "Sektörel + AI derinleşme" (3-4 ay)
- SP-01 Otomotiv (30h)
- SP-02 Sağlık (40h)
- SP-04 Finans (40h)
- AI-01 NLP Sorgu (60h)
- AI-10 Sektör Benchmark (40h)

**Toplam:** **~210h** (~5-6 hafta).

### Faz 5 — "Büyük altyapı" (6+ ay)
- IF-01 Mobile App (220h)
- IF-03 BI Connector (60h)
- IF-05 ML Anomali (60h)
- IF-06 Workflow Engine (150h)

**Toplam:** **~490h** (3+ ay).

---

## 📋 KARAR MATRİSİ

Kullanıcı için tartışma odakları:

### A. Şimdi başlanması en mantıklı 5 başlık (ROI bazlı)
1. **AI Coach** (8h) — her PG sayfasında çıkar, sürekli wow
2. **CFO Dashboard** (16h) — yöneticiler için somut
3. **Stratejik Yıllık Kitap** (80h) — premium ürün, yıllık fatura
4. **Otomotiv sektörel paket** (30h) — pazarlama altın madeni
5. **AI Doğal Dil Sorgu MVP** (20h) — basit pattern → wow demosu

**Toplam:** ~154h (~4 hafta tek kişi). En yüksek ROI.

### B. Veri eksiklikleri sebebiyle ERTELENMESİ önerilenler
- ES-05/06/07 (Tomofil ESG veri ince)
- ST-08 Ansoff Matrix (kategori veri eksik)
- ST-13 Risk-Strateji çapraz (bağlantı yok)
- FN-03 Time→maliyet (hourly_rate yok)
- HR-06 Yedekleme Planı (successor yok)
- HR-12 Doğum günü (doğum tarihi yok)

**Çözüm:** önce veri modeli zenginleşmeli, sonra rapor.

### C. Çok büyük yatırım — ROI tartışması
- IF-01 Mobile (220h) — değer büyük ama yatırım da büyük
- IF-06 Workflow Engine (150h) — sadece enterprise için
- AI-01 NLP Sorgu (60-70h) — büyük etki ama SQL injection riski

---

## 💼 İŞ MODELİ ETKİSİ

Her başlığın **gelir potansiyeli**:

| Başlık | Standart paket | Premium ek-ödeme | Pazar değeri |
|---|---|---|---|
| Hızlı kazançlar (Faz 1) | ✓ dahil | — | Müşteri tutma |
| Persona dashboard (Faz 2) | Pro paket | — | Pro upsell |
| Stratejik Yıllık Kitap | — | ₺30K/yıl | Premium ürün |
| Yatırımcı Sunum | — | ₺20K/sunum | Per-use |
| Sektörel paket | — | ₺80K kurulum | Bir-kerelik |
| AI premium (NLP, Hikaye, Coach) | Enterprise | LLM kotası ek ücret | AI Add-on |
| Mobile App | Enterprise | — | Enterprise upsell |
| BI Connector | Enterprise | — | Enterprise upsell |

**Yıllık tek müşteri için (orta ölçek) potansiyel:**
- Standart Pro paketi: ₺120K
- + Stratejik Yıllık Kitap: ₺30K
- + Yatırımcı Sunum (4×): ₺80K
- + AI Premium: ₺60K
- + Sektörel paket (1. yıl): ₺80K
- **Toplam: ₺370K/yıl/müşteri**

10 müşteri = **₺3.7M yıllık tekrarlayan gelir**.

---

## 🚦 SONRAKİ ADIM

Kullanıcı bu plandan ne istiyor?

1. **"Faz 1 hızlı kazançları başla"** → 15 başlık, ~80h, 2 hafta
2. **"3 persona dashboard önce"** → CFO+COO+CHRO, ~48h
3. **"Yatırımcı için premium ürünler"** → Stratejik Yıllık + Yatırımcı Sunum, ~110h
4. **"Belirli bir başlığı detaylandır"** → o başlık için ayrı task açılır
5. **"Bekle, ekipte tartışacağız"** → bu plan referans olarak kalır

Plan yaşayan bir dokümandır — yeni başlık eklenir, mevcut başlıklar yapıldıkça `[HAZIR ✓]` etiketlenir, öncelikler revize edilir.

---

**Hazırlayan:** Claude · 2026-05-27
**Kaynak:** [docs/rapor/27mayisraporu.md](27mayisraporu.md) · [docs/TENANT-VERI-ENVANTERI.md](../TENANT-VERI-ENVANTERI.md)
