# -*- coding: utf-8 -*-
"""UserYearAssignment — Kullanıcının yıllık snapshot rolü.

Tarih egemen plan year doktrininin (Faz 3) parçası.

User kalıcı kimliktir, ama unvanı/departmanı yıldan yıla değişebilir.
Bu model o yıla ait snapshot tutar. Yoksa User.job_title/department fallback.
"""
from datetime import datetime, timezone

from extensions import db
from app.utils.tenant_guard import TenantScopedMixin


class UserYearAssignment(TenantScopedMixin, db.Model):
    __tablename__ = "user_year_assignments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    plan_year_id = db.Column(
        db.Integer, db.ForeignKey("plan_years.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    job_title = db.Column(db.String(150), nullable=True)
    department = db.Column(db.String(150), nullable=True)
    role_label = db.Column(db.String(80), nullable=True)
    note = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc), nullable=False,
    )

    user = db.relationship("User", backref=db.backref("year_assignments", lazy="dynamic"))
    plan_year = db.relationship("PlanYear", backref=db.backref("user_assignments", lazy="dynamic"))
    tenant = db.relationship("Tenant", backref=db.backref("user_year_assignments", lazy="dynamic"))

    __table_args__ = (
        db.UniqueConstraint("user_id", "plan_year_id", name="uq_user_year_assignment"),
    )

    def __repr__(self):
        return f"<UserYearAssignment u={self.user_id} py={self.plan_year_id}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plan_year_id": self.plan_year_id,
            "job_title": self.job_title,
            "department": self.department,
            "role_label": self.role_label,
            "note": self.note,
        }


def resolve_user_assignment(user, plan_year_id: int) -> dict:
    """Kullanıcının o yılki snapshot bilgisini getirir.

    Önce UserYearAssignment'a bakar; yoksa user.job_title/department fallback.
    """
    if user is None:
        return {}
    if plan_year_id:
        a = UserYearAssignment.query.filter_by(
            user_id=user.id, plan_year_id=plan_year_id
        ).first()
        if a:
            return {
                "job_title": a.job_title or getattr(user, "job_title", None),
                "department": a.department or getattr(user, "department", None),
                "role_label": a.role_label,
                "source": "year_snapshot",
            }
    return {
        "job_title": getattr(user, "job_title", None),
        "department": getattr(user, "department", None),
        "role_label": None,
        "source": "user_default",
    }
