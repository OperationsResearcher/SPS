"""Models package - db instance and all models for Alembic discovery."""

# Tek bir db instance kullan — kök extensions.py'den import et
from extensions import db  # noqa: F401

# Import all models after db is defined (Alembic needs them)
from app.models.core import Role, Tenant, User, Notification  # noqa: E402
from app.models.saas import (  # noqa: E402
    ModuleComponentSlug,
    RouteRegistry,
    SystemComponent,
    SystemModule,
    SubscriptionPackage,
)
from app.models.audit import AuditLog  # noqa: E402
from app.models.process import (  # noqa: E402
    Process,
    ProcessKpi,
    ProcessActivity,
    ProcessActivityAssignee,
    ProcessActivityReminder,
    KpiData,
    KpiDataAudit,
    IndividualPerformanceIndicator,
    IndividualActivity,
    IndividualKpiData,
    IndividualKpiDataAudit,
    IndividualActivityTrack,
    FavoriteKpi,
)
from app.models.email_config import TenantEmailConfig  # noqa: E402
from app.models.system_setting import SystemSetting  # noqa: E402
from app.models.k_radar import KRadarRecommendationAction  # noqa: E402
from app.models.k_vektor import (  # noqa: E402
    KVektorConfigSnapshot,
    KVektorStrategyWeight,
    KVektorSubStrategyWeight,
)
from app.models.k_radar_domain import (  # noqa: E402
    ProcessMaturity,
    BottleneckLog,
    ValueChainItem,
    EvmSnapshot,
    RiskHeatmapItem,
    StakeholderMap,
    StakeholderSurvey,
    A3Report,
    CompetitorAnalysis,
)
from app.models.plan_year import (  # noqa: E402
    PlanYear,
    KpiYearConfig,
    StrategyYearConfig,
    SubStrategyYearConfig,
    ProcessYearConfig,
    IndividualKpiYearConfig,
)
from app.models.tenant_year import TenantYearIdentity  # noqa: E402
from app.models.tenant_identity import (  # noqa: E402
    TenantValue, TenantEthicsCode, TenantQualityPolicy,
)
from app.models.user_year_assignment import UserYearAssignment  # noqa: E402
from app.models.initiative import Initiative, InitiativeMilestone  # noqa: E402
from app.models.replan_trigger import ReplanTrigger, ReplanTriggerEvent  # noqa: E402
from app.models.strategy_frameworks import (  # noqa: E402
    BlueOceanCanvas, BlueOceanFactor, BlueOceanERRC, VRIOResource,
)
from app.models.llm_usage import LLMUsageLog, LLMQuotaOverride  # noqa: E402
from app.models.tenant_llm_config import TenantLLMConfig  # noqa: E402
from app.models.tour import UserTourProgress  # noqa: E402
# notifications_ext / notification_preferences / push_subscriptions —
# create_all'ın bu tabloları görebilmesi için kayıt (okr/bsc/esg ile aynı
# eksik). core.Notification ile isim çakışmasın diye alias.
from app.models.notification import (  # noqa: E402,F401
    Notification as NotificationExt,
    NotificationPreference,
    PushSubscription,
)
from app.models.swot import SwotAnalysis, TowsAnalysis, PestelAnalysis, PorterFiveForcesAnalysis  # noqa: E402
from app.models.okr import OkrObjective, OkrKeyResult  # noqa: E402
from app.models.bsc import BscKpiPerspective  # noqa: E402
from app.models.esg import EsgMetric, EsgMetricValue  # noqa: E402
from app.models.project import PlanProject, PlanProjectTask, PlanProjectActivity  # noqa: E402
from app.models.marketing import DemoRequest  # noqa: E402
from app.models.portfolio_project import (  # noqa: E402
    Project,
    Task,
    RaidItem,
    TaskImpact,
    TaskComment,
    ProjectFile,
    project_members,
    project_observers,
    project_leaders,
    project_related_processes,
    task_predecessors,
)
