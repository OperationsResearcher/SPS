"""SP Proje modulleri — plan year bazlı (yeni sistem)."""
from datetime import datetime, timezone
from extensions import db
from app.utils.tenant_guard import TenantScopedMixin


class PlanProject(TenantScopedMixin, db.Model):
    """SP Proje. Her PlanYear kapsaminda olusturulur/klonlanir."""
    __tablename__ = "plan_projects"

    id = db.Column(db.Integer, primary_key=True)
    plan_year_id = db.Column(
        db.Integer, db.ForeignKey("plan_years.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    source_project_id = db.Column(
        db.Integer, db.ForeignKey("plan_projects.id", ondelete="SET NULL"),
        nullable=True
    )

    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="Planlandı", nullable=False)
    progress = db.Column(db.Integer, default=0, nullable=False)

    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)

    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    plan_year = db.relationship(
        "PlanYear",
        backref=db.backref("plan_projects", lazy="dynamic", cascade="all, delete-orphan")
    )
    tenant = db.relationship(
        "Tenant",
        backref=db.backref("plan_projects", lazy="dynamic")
    )
    source_project = db.relationship(
        "PlanProject", remote_side=[id], foreign_keys=[source_project_id]
    )

    def __repr__(self):
        return f"<PlanProject {self.name} plan_year={self.plan_year_id}>"


class PlanProjectTask(db.Model):
    """SP Proje Gorevi."""
    __tablename__ = "plan_project_tasks"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer, db.ForeignKey("plan_projects.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    plan_year_id = db.Column(
        db.Integer, db.ForeignKey("plan_years.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    assignee_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True, index=True
    )

    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="Planlandı", nullable=False)

    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)

    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)

    # S62: EVM alanları
    progress_pct = db.Column(db.Float, nullable=False, default=0.0)
    planned_budget = db.Column(db.Numeric(18, 2), nullable=True)
    actual_cost = db.Column(db.Numeric(18, 2), nullable=True, default=0)
    depends_on_task_id = db.Column(
        db.Integer, db.ForeignKey("plan_project_tasks.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    project = db.relationship(
        "PlanProject",
        backref=db.backref("tasks", lazy="dynamic", cascade="all, delete-orphan")
    )
    plan_year = db.relationship("PlanYear", backref=db.backref("plan_project_tasks", lazy="dynamic"))
    assignee = db.relationship("User", backref=db.backref("plan_project_tasks", lazy="dynamic"))

    def __repr__(self):
        return f"<PlanProjectTask {self.name} project={self.project_id}>"


class PlanProjectActivity(db.Model):
    """SP Proje Faaliyeti."""
    __tablename__ = "plan_project_activities"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer, db.ForeignKey("plan_projects.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    plan_year_id = db.Column(
        db.Integer, db.ForeignKey("plan_years.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="Planlandı", nullable=False)

    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    project = db.relationship(
        "PlanProject",
        backref=db.backref("activities", lazy="dynamic", cascade="all, delete-orphan")
    )
    plan_year = db.relationship("PlanYear", backref=db.backref("plan_project_activities", lazy="dynamic"))

    def __repr__(self):
        return f"<PlanProjectActivity {self.name} project={self.project_id}>"
