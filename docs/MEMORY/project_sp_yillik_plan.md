---
name: sp-y-ll-k-d-nem-sistemi-tasar-m-kararlar
description: Stratejik Planlamayı yıllık dönemlere bağlayan PlanYear mimarisi için tasarım ve kapsam kararları
metadata: 
  node_type: memory
  type: project
  originSessionId: 3b041b4f-9e7c-4993-9fe1-58d5bf43736a
---

SP modülüne yıllık dönem (PlanYear) sistemi EKLENDİ (2026-04-05). Tüm SP bileşenleri (Strateji, AltStrateji, Süreç, KPI, Faaliyet, Proje, Bireysel PG) bir yıla bağlandı.

**Why:** `ProcessKpi.target_value` zamansız tek bir alandı. Farklı yıllarda farklı hedeflere karşı değerlendirme yapılamıyordu.

**Uygulanan mimari:**
- 6 yeni tablo: plan_years, kpi_year_configs, strategy_year_configs, sub_strategy_year_configs, process_year_configs, individual_kpi_year_configs
- Migration: y2z3a4b5c006_plan_year_tables.py ✅ uygulandı
- Backward-compatible overlay: yıllık config yoksa ProcessKpi.target_value fallback
- `kpi_period_targets` tablosu YOK — mevcut JS computeCellTargetMicro fonksiyonu (ölçüm_periyodu × çarpan) yeterli
- Retroaktif hedef: kpi_year_configs.target_value değişince tüm o yılın hesapları otomatik güncellenir (dinamik, store edilmiyor)

**Değiştirilen dosyalar:**
- app/models/plan_year.py (YENİ)
- app/models/__init__.py (import eklendi)
- app/services/plan_year_service.py (YENİ — get_kpi_configs_bulk, clone_plan_year, close_plan_year vb.)
- app/services/score_engine_service.py (plan_year parametresi eklendi)
- micro/modules/sp/routes.py (plan year API endpointleri + session active year)
- micro/modules/surec/routes.py (karne API + kpi_list year-aware)
- ui/templates/platform/sp/index.html (plan year bar UI)
- ui/static/platform/js/sp_plan_year.js (YENİ — yıl seçici JS)
- ui/static/platform/css/sp.css (plan year bar CSS)

**Ertelenen işler:**
- E1: ✅ TAMAMLANDI — kullanıcı canlı geçişi yaptı (2026-04-06)
- D3: Yıllar arası karşılaştırma ekranı (altyapı hazır, UI/route henüz yok)

**Tenant Toggle (TASK-062):** `Tenant.plan_year_enabled` (Boolean, default=False). Migration: z3a4b5c6d007. Kapalıyken plan year bar/modal/JS render edilmez; skor motoru KPI yıl config tablolarına bakmaz. Kurum Ayarları sayfasında "Yıllık Plan Dönemleri" toggle kartı var.

**URL tek-dil (TASK-213, 2026-06-23):** Plan-yıl sayfa/API URL'leri İngilizceye çevrildi (eskiler 301 köprülü):
donemler→periods, sihirbaz/yeni-yil→wizard/new-year (uygula→apply), api/donem-karsilastir→api/period-compare,
rapor/donemsel→report/periodic, api/proje→api/project (gorev→task). Fonksiyon adları (sp_api_proje_*,
sp_donemler vb.) KORUNDU — url_for otomatik doğru. PlanProject/PlanProjectTask/plan_year_id modeli değişmedi.
URL'de `pi` (Performance Indicator), kod/DB'de `pg` (bkz [[project_kart_sistemi_mimari]] değil, KURALLAR-MASTER).

**SP API endpointleri:**
- GET/POST /sp/api/plan-years
- POST /sp/api/plan-years/set-active
- POST /sp/api/plan-years/{id}/close
- GET /sp/api/plan-years/{id}/kpi-configs
- POST /sp/api/plan-years/{id}/kpi-configs/{kpi_id}
- POST /sp/api/plan-years/{id}/kpi-configs/bulk
