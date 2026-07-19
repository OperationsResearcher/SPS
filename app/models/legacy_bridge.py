# -*- coding: utf-8 -*-
"""
Uygulama kodu için tek import köprüsü (legacy `models` paketi yerine).

Yeni kod: doğrudan `app.models.process`, `app.models.portfolio_project`, `app.models.core`.
Bu modül geçiş dönemi için tüm Türkçe/İngilizce alias'ları toplar.
"""
from extensions import db

# ── Süreç / KPI (canonical) ───────────────────────────────────────────────────
from app.models.process import (
    Process,
    Process as Surec,
    ProcessKpi,
    ProcessKpi as SurecPerformansGostergesi,
    ProcessActivity,
    ProcessActivity as SurecFaaliyet,
    KpiData,
    KpiDataAudit,
    IndividualPerformanceIndicator,
    IndividualPerformanceIndicator as BireyselPerformansGostergesi,
    IndividualActivity,
    IndividualActivity as BireyselFaaliyet,
    IndividualKpiData,
    IndividualKpiData as PerformansGostergeVeri,
    IndividualKpiDataAudit,
    IndividualKpiDataAudit as PerformansGostergeVeriAudit,
    IndividualActivityTrack,
    IndividualActivityTrack as FaaliyetTakip,
    FavoriteKpi,
    FavoriteKpi as FavoriKPI,
    ProcessSubStrategyLink,
    process_members as surec_uyeleri,
    process_leaders as surec_liderleri,
    process_owners_table as process_owners,
)

surec_alt_stratejiler = ProcessSubStrategyLink.__table__

PerformanceIndicator = SurecPerformansGostergesi

# ── Portföy proje ─────────────────────────────────────────────────────────────
from app.models.portfolio_project import (
    Project,
    Task,
    TaskImpact,
    TaskComment,
    TaskMention,
    ProjectFile,
    ProjectRisk,
    Tag,
    TaskSubtask,
    TimeEntry,
    TaskActivity,
    ProjectTemplate,
    TaskTemplate,
    Sprint,
    TaskSprint,
    TaskDependency,
    IntegrationHook,
    RuleDefinition,
    SLA,
    RecurringTask,
    WorkingDay,
    CapacityPlan,
    RaidItem,
    TaskBaseline,
    project_members,
    project_observers,
    project_leaders,
    project_related_processes,
    task_predecessors,
)

# ── Kullanıcı / kurum / strateji (app.models.*_legacy shim) ───────────────────
from app.models.user_legacy import (
    User,
    Kurum,
    YetkiMatrisi,
    OzelYetki,
    KullaniciYetki,
    DashboardLayout,
    Deger,
    EtikKural,
    KalitePolitikasi,
    Notification,
    UserActivityLog,
    Note,
)
from app.models.strategy_legacy import (
    AnaStrateji,
    AltStrateji,
    StrategyProcessMatrix,
    StrategyMapLink,
    MainStrategy,
    SubStrategy,
)
from app.models.legacy_extras import (
    Activity,
    AuditLog,
    Feedback,
    UserDashboardSettings,
    CorporateIdentity,
    # NOT: 29 Faz 2/3/4 mock modeli (ObjectiveComment, StrategicRisk, GembaWalk,
    # MudaFinding, MetaverseDepartment, DoomsdayScenario...) KALDIRILDI (2026-07-19)
    # — onları kullanan legacy sayfalar silindi, mock üretici temizlendi.
)

