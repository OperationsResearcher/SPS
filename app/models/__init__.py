"""Models package - db instance and all models for Alembic discovery."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
from app.models.strategy import SwotAnalysis  # noqa: E402
from app.models.process import (  # noqa: E402
    Process,
    ProcessKpi,
    ProcessActivity,
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
