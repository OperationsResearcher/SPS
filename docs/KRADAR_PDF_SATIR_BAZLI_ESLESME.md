# K-Radar PDF Satır Bazlı Eşleşme

Kaynak: `docs/KRadar.pdf`  
Tarih: 2026-03-26

Durum kodları:
- **Tamamlandı**: Uygulamada var ve çalışır doğrulandı
- **Kısmi**: Temel/operasyonel ilk seviye var, ileri derinlik sonraki iterasyon
- **Faz-2**: Bilinçli olarak sonraki fazda

## 1) Vizyon / 3 Radar Katmanı

| PDF Maddesi | Durum | Not |
|---|---|---|
| KS-Radar + KP-Radar + KPR-Radar ana omurga | Tamamlandı | Hub ve alt radar sayfaları mevcut |
| Cross-Modül araç kutusu | Tamamlandı | Cross ana ekran + alt modüller var |

## 2) Mimari Yapı ve Route’lar

| PDF Route Hedefi | Durum | Uygulama Karşılığı |
|---|---|---|
| `/k-radar` | Tamamlandı | Hub + öneri + history + trigger kartı |
| `/k-radar/ks` | Tamamlandı | KS ana ekran |
| `/k-radar/ks/swot` altında KS analizleri | Tamamlandı | SWOT/PESTLE/TOWS/Gap/OKR/Hoshin/Ansoff/BCG/BSC/EFQM açıldı |
| `/k-radar/kp` | Tamamlandı | KP ana ekran |
| `/k-radar/kp/olgunluk` altında KP analizleri | Tamamlandı | Olgunluk + Darboğaz + Değer Zinciri + Pareto + SLA + Kapasite + Benchmark + OEE + VSM |
| `/k-radar/kpr` | Tamamlandı | KPR ana ekran |
| `/k-radar/kpr/cpm` altında KPR analizleri | Tamamlandı | CPM + EVM + Risk + Kaynak Kapasite + Gantt |
| `/k-radar/cross` | Tamamlandı | Isı haritası + Rekabet + Paydaş + A3/5Neden + Anket |

## 2.2 KS→KP→KPR FK Zinciri

| PDF Beklentisi | Durum | Not |
|---|---|---|
| `tows_matrix.linked_strategy_id` zinciri | Kısmi | Tasarım ve hizalama var; veri kalitesi/migration doğrulaması ayrı turda derinleştirilmeli |
| `processes.strategy_id` | Tamamlandı | Süreç-strateji ilişkisi çalışır |
| `projects.linked_strategy_id` | Kısmi | Route/analiz akışı var; tüm projelerde alan kullanım yoğunluğu veriye bağlı |
| `analysis_item.process_id` | Kısmi | Legacy/canonical geçiş kaynaklı bazı alanlar ortam verisine göre değişebilir |

## 3) Analiz Envanteri

### 3.1 KS-Radar (10 analiz)

| Analiz | Durum | Not |
|---|---|---|
| SWOT | Tamamlandı | Ekran + API |
| PESTLE | Tamamlandı | Ekran + API |
| TOWS | Tamamlandı | Ekran + API |
| Gap | Tamamlandı | Ekran + API |
| OKR | Tamamlandı | Ekran + API |
| Hoshin Kanri | Tamamlandı | Ekran + API |
| Ansoff | Tamamlandı | Ekran + API |
| BCG | Tamamlandı | Ekran + API |
| Balanced Scorecard | Kısmi | Özet metrik seviyesi; perspektif bazlı detay rapor ileri iterasyon |
| EFQM | Kısmi | Özet metrik seviyesi; tam RADAR detayları ileri iterasyon |

### 3.2 KP-Radar (9 analiz)

| Analiz | Durum | Not |
|---|---|---|
| Süreç Olgunluk | Tamamlandı | CRUD + API-first |
| Darboğaz | Tamamlandı | Domain tablosu + metrik |
| Değer Zinciri | Tamamlandı | Domain tablosu + metrik |
| Pareto | Tamamlandı | Hesaplanan etki dilimi |
| SLA Histogramı | Kısmi | SLA riski/ihlal oranı var; histogram görselleştirme ileri tur |
| Kapasite Kullanım | Kısmi | Kullanım tahmini var; `resource_capacity` tam entegrasyonu ileri tur |
| Dönem Bazlı Benchmark | Tamamlandı | Dönem satırı + karşılaştırılabilirlik |
| OEE | Tamamlandı | Availability/Performance/Quality + OEE |
| VSM/Muda | Tamamlandı | `value_chain_item.muda_type` tabanlı metrikler |

### 3.3 KPR-Radar (5 analiz + Faz2)

| Analiz | Durum | Not |
|---|---|---|
| CPM | Tamamlandı | Ekran + API |
| EVM | Tamamlandı | `evm_snapshots` tabanlı metrik |
| Kaynak Kapasite | Kısmi | Metrik var; `resource_capacity` tam tablo entegrasyonu ileri tur |
| Risk Radarı | Tamamlandı | `risk_heatmap_items` + proje risk metrikleri |
| Gantt Görünümü | Kısmi | Gantt özet metrik var; tam çizelge UI mevcut proje modülüne bağlı |
| Monte Carlo Simülasyonu | Faz-2 | PDF’de Faz-2 olarak işaretli |

### 3.4 Cross-Modül (6 analiz)

| Analiz | Durum | Not |
|---|---|---|
| Risk Isı Haritası | Tamamlandı | Etkileşimli grid + detay panel |
| Rekabet Radarı | Tamamlandı | Ekran + API |
| Paydaş Analizi | Tamamlandı | CRUD + filtre/sıralama |
| A3 Raporu | Tamamlandı | Ekran + API özet |
| 5 Neden / Kök Neden | Tamamlandı | `a3_report.root_cause_json` kapsaması |
| Paydaş Algı Anketi | Tamamlandı | Ekran + API |

## 4) Veritabanı Şema Değişiklikleri

### 4.1 Mevcut tablolara alan ekleri

| PDF Alanı | Durum | Not |
|---|---|---|
| `analysis_item.scope/process_id/is_suggested` | Kısmi | Ortam ve legacy/canonical dönüşüme bağlı doğrulama gerekli |
| `tows_matrix.linked_strategy_id/converted_at` | Kısmi | Yapısal hedef karşılandı, veri migrasyon denetimi gerekebilir |
| `process_kpis.bsc_perspective/bcg_category/tolerance_*` | Kısmi | Tüm alanların prod veride aktif kullanımı doğrulanmalı |
| `processes.dmaic_phase` | Kısmi | Alan standardizasyonu legacy dönüşümlerle ilişkili |
| `users.potential_score` | Kısmi | 9-box senaryosu için kullanım derinliği ayrı tur |

### 4.2 Yeni tablo paketi

| PDF Tablo Grubu | Durum | Not |
|---|---|---|
| `process_maturity`, `bottleneck_log`, `value_chain_items`, `evm_snapshots`, `risk_heatmap_items`, `competitor_analyses`, `stakeholder_maps`, `stakeholder_surveys`, `a3_reports` | Tamamlandı | Model + migration + API kullanımında aktif |
| `resource_capacity`, `fmea_items`, `skill_matrix`, `gap_analysis`, `strategic_assessment`, `kano_items`, `blue_ocean_canvas`, `scenario_plan`, `financial_metrics`, `change_initiative` vb. | Kısmi | PDF hedefinde var; bu turda tamamı operasyonelleştirilmedi |

## 5) Kural Tabanlı Öneri Motoru

| PDF Beklentisi | Durum | Not |
|---|---|---|
| Radar bazlı tetikleyici | Tamamlandı | `get_recommendation_triggers` aktif |
| Günlük scheduler | Tamamlandı | Scheduler servisi mevcut |
| Kullanıcı onayı zorunlu | Tamamlandı | Onay/red akışı mevcut |
| Onay sonrası aksiyon görevi | Tamamlandı | Task üretimi + dedup + öncelik |
| Tam audit izlenebilirliği | Kısmi | Geçmiş/CSV var; ileri audit ekranı geliştirilebilir |

## 6) Erişim / Rol

| PDF Beklentisi | Durum | Not |
|---|---|---|
| `@login_required` + tenant izolasyonu | Tamamlandı | Route korumaları aktif |
| Admin/tenant_admin/executive_manager yazma yetkisi | Tamamlandı | Write policy sertleştirildi |
| User sadece okuma | Tamamlandı | Regresyon testi ile doğrulandı |

## 7) Faz Planı

| Faz | Durum |
|---|---|
| Faz 1 adımları (ana kurulum) | Tamamlandı (bu tur kapsamı) |
| Faz 2: Monte Carlo + AI-Pilot + Senaryo Simülatörü | Faz-2 |

## Sonuç

`KRadar.pdf` içeriği için:
- **Çekirdek mimari ve modül kapsamı: Tamamlandı**
- **İleri analitik derinlik / bazı tablo aileleri: Kısmi**
- **Faz-2 bileşenleri: Bilinçli olarak beklemede**

Bu nedenle nihai değerlendirme: **%100 çekirdek kapsam tamam, %100 nihai olgunluk değil (kısmi ileri maddeler + Faz-2 bekleyenler var).**
