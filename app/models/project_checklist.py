# -*- coding: utf-8 -*-
"""
Proje Kontrol Listesi (Danışmanlık Süreci Kontrol Listesi).

Kurum başına, plan yılı başına bir şablon (ChecklistTemplate) tutulur. Proje
oluşunca şablon projeye KOPYALANIR (ProjectChecklistItem); sonradan şablon
değişse de mevcut projeler bozulmaz. Her madde çift onaylıdır:
Bekliyor → Yapıldı (sorumlu) → Onaylandı (lider/yönetici, yapandan farklı kişi).
Tüm aktif maddeler Onaylandı olmadan proje tamamlanamaz.
"""
from datetime import datetime, timezone

from extensions import db


def _now():
    return datetime.now(timezone.utc)


# Madde durumları (tek kaynak — route/servis/şablon bunu kullanır)
STATUS_PENDING = "Bekliyor"
STATUS_DONE = "Yapıldı"
STATUS_APPROVED = "Onaylandı"
ITEM_STATUSES = (STATUS_PENDING, STATUS_DONE, STATUS_APPROVED)


class ChecklistTemplate(db.Model):
    """Kurumun yıl bazlı kontrol listesi şablonu."""
    __tablename__ = "checklist_template"
    __table_args__ = (
        db.UniqueConstraint("tenant_id", "year", name="uq_checklist_template_tenant_year"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False, default="Kontrol Listesi")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=_now)
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)

    items = db.relationship(
        "ChecklistTemplateItem", backref="template", lazy="select",
        order_by="ChecklistTemplateItem.sort_order", cascade="all, delete-orphan",
    )


class ChecklistTemplateItem(db.Model):
    __tablename__ = "checklist_template_item"

    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey("checklist_template.id", ondelete="CASCADE"), nullable=False, index=True)
    stage = db.Column(db.String(100), nullable=False)          # Genel Aksiyonlar, Teşhis…
    item_group = db.Column(db.String(60), nullable=True)       # Uygulama / Çıktı
    text = db.Column(db.Text, nullable=False)
    period_days = db.Column(db.Integer, nullable=True)         # periyodik hatırlatma (gün)
    evidence_required = db.Column(db.Boolean, default=False, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)


class ProjectChecklistItem(db.Model):
    """Projeye kopyalanmış kontrol listesi maddesi."""
    __tablename__ = "project_checklist_item"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id", ondelete="CASCADE"), nullable=False, index=True)
    source_item_id = db.Column(db.Integer, db.ForeignKey("checklist_template_item.id", ondelete="SET NULL"), nullable=True)

    stage = db.Column(db.String(100), nullable=False)
    item_group = db.Column(db.String(60), nullable=True)
    text = db.Column(db.Text, nullable=False)
    period_days = db.Column(db.Integer, nullable=True)
    evidence_required = db.Column(db.Boolean, default=False, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)

    status = db.Column(db.String(20), default=STATUS_PENDING, nullable=False, index=True)
    done_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    done_at = db.Column(db.DateTime, nullable=True)
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    note = db.Column(db.Text, nullable=True)

    next_reminder_at = db.Column(db.DateTime, nullable=True, index=True)
    last_reminded_at = db.Column(db.DateTime, nullable=True)

    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=_now)
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)

    project = db.relationship("Project", backref=db.backref("checklist_items", lazy="select"))
    done_user = db.relationship("User", foreign_keys=[done_by])
    approved_user = db.relationship("User", foreign_keys=[approved_by])
    evidences = db.relationship(
        "ProjectChecklistEvidence", backref="item", lazy="select",
        order_by="ProjectChecklistEvidence.created_at", cascade="all, delete-orphan",
    )
    assignments = db.relationship(
        "ProjectChecklistAssignment", backref="item", lazy="select",
        order_by="ProjectChecklistAssignment.id", cascade="all, delete-orphan",
    )


class ProjectChecklistEvidence(db.Model):
    """Madde kanıtı: dosya veya bağlantı."""
    __tablename__ = "project_checklist_evidence"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("project_checklist_item.id", ondelete="CASCADE"), nullable=False, index=True)
    uploader_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    kind = db.Column(db.String(10), nullable=False, default="file")  # file | link
    title = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=True)
    url = db.Column(db.String(1000), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=_now)

    uploader = db.relationship("User", foreign_keys=[uploader_id])


# Atama hedef türleri: kullanıcı / süreç (sürecin tüm üyeleri) / proje (proje ekibi)
TARGET_USER = "user"
TARGET_PROCESS = "process"
TARGET_PROJECT = "project"
TARGET_TYPES = (TARGET_USER, TARGET_PROCESS, TARGET_PROJECT)


class ProjectChecklistAssignment(db.Model):
    """Maddenin sorumluları: tek tek kullanıcılar, bir sürecin tüm üyeleri ve/veya proje ekibi."""
    __tablename__ = "project_checklist_assignment"
    __table_args__ = (
        db.UniqueConstraint("item_id", "target_type", "target_id", name="uq_checklist_assignment_target"),
    )

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("project_checklist_item.id", ondelete="CASCADE"), nullable=False, index=True)
    target_type = db.Column(db.String(10), nullable=False)
    # user → users.id · process → processes.id · project → projenin kendisi (0)
    target_id = db.Column(db.Integer, nullable=False, default=0)
    assigned_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = db.Column(db.DateTime, default=_now)
