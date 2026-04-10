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
from app.models.swot import SwotAnalysis, TowsAnalysis, PestelAnalysis, PorterFiveForcesAnalysis  # noqa: E402
from app.models.project import PlanProject, PlanProjectTask, PlanProjectActivity  # noqa: E402
