# -*- coding: utf-8 -*-
"""
Proje Yönetimi Modelleri
------------------------
Proje, Görev (Task), Dosya ve Proje Ekibi ile ilgili modelleri içerir.
"""
from extensions import db
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
import json

# Association Tables
task_predecessors = db.Table('task_predecessors',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('predecessor_id', db.Integer, db.ForeignKey('task.id'), primary_key=True)
)
project_members = db.Table('project_members',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

project_observers = db.Table('project_observers',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

project_related_processes = db.Table('project_related_processes',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('surec_id', db.Integer, db.ForeignKey('surec.id'), primary_key=True)
)

class Project(db.Model):
    """
    Proje Modeli
    
    Kurumsal projelerin takibi ve yönetimi için kullanılır.
    Proje sağlık skoru (V67) ve çoklu süreç ilişkisi desteklenir.
    """
    __tablename__ = 'project'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    
    # Temel Bilgiler
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    # Zamanlama
    start_date = db.Column(db.Date, nullable=True, index=True)
    end_date = db.Column(db.Date, nullable=True, index=True)
    
    # Durum
    priority = db.Column(db.String(50), default='Orta')  # Düşük, Orta, Yüksek
    is_archived = db.Column(db.Boolean, default=False, index=True)
    
    # Sağlık Skoru (V67)
    health_score = db.Column(db.Integer, default=100)
    health_status = db.Column(db.String(50), default='İyi')

    # Bildirim Ayarları (JSON)
    notification_settings = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('projeler', lazy=True))
    manager = db.relationship('User', foreign_keys=[manager_id], backref='yonettigi_projeler')
    
    # Many-to-Many
    members = db.relationship('User', secondary=project_members, backref='uye_oldugu_projeler')
    observers = db.relationship('User', secondary=project_observers, backref='gozlemci_oldugu_projeler')
    related_processes = db.relationship('Surec', secondary=project_related_processes, backref='bagli_projeler')
    
    def __repr__(self):
        return f'<Project {self.name}>'

    def get_notification_settings(self):
        """Proje bildirim ayarlarını dict olarak döndürür (yoksa default)."""
        default_settings = {
            'reminder_days': [7, 3, 1],
            'overdue_frequency': 'daily',
            'channels': {'in_app': True, 'email': False},
            'notify_manager': True,
            'notify_observers': False
        }
        if not self.notification_settings:
            return default_settings
        try:
            parsed = json.loads(self.notification_settings)
            if isinstance(parsed, dict):
                default_settings.update(parsed)
            return default_settings
        except Exception:
            return default_settings

class Task(db.Model):
    """
    Görev Modeli
    
    Proje altındaki iş paketlerini (görevleri) tanımlar.
    """
    __tablename__ = 'task'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False, index=True)
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Atamalar
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Dış kaynak / sistemde olmayan sorumlu (opsiyonel)
    external_assignee_name = db.Column(db.String(200), nullable=True)

    # Hiyerarşi / Planlama (API ve UI uyumu için opsiyonel alanlar)
    parent_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True, index=True)
    estimated_time = db.Column(db.Float, nullable=True)
    actual_time = db.Column(db.Float, nullable=True)
    progress = db.Column(db.Integer, default=0)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Otomasyon / ölçülebilirlik (mevcut endpointlerle uyum için)
    is_measurable = db.Column(db.Boolean, default=False)
    planned_output_value = db.Column(db.Float, nullable=True)
    related_indicator_id = db.Column(db.Integer, nullable=True)
    
    # Durum
    status = db.Column(db.String(50), default='To Do')
    priority = db.Column(db.String(50), default='Medium')
    is_archived = db.Column(db.Boolean, default=False)
    
    # Zamanlama
    due_date = db.Column(db.Date, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    reminder_date = db.Column(db.DateTime, nullable=True)  # Görev hatılatıcı tarihi/zamanı
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    project = db.relationship('Project', backref=db.backref('tasks', lazy=True, cascade='all, delete-orphan'))
    assignee = db.relationship('User', foreign_keys=[assignee_id], backref='assigned_tasks')
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='reported_tasks')
    parent = db.relationship('Task', remote_side=[id], backref=db.backref('children', lazy=True))

    # Bağımlılıklar: Öncel görevler (predecessors)
    predecessors = db.relationship(
        'Task', secondary=task_predecessors,
        primaryjoin=(task_predecessors.c.task_id == id),
        secondaryjoin=(task_predecessors.c.predecessor_id == id),
        backref=db.backref('successors', lazy='dynamic'), lazy='dynamic'
    )

    # Yeni bağımlılık modeli (tip ve lag destekli)
    dependencies_in = db.relationship(
        'TaskDependency', foreign_keys='TaskDependency.successor_id',
        backref=db.backref('successor', lazy=True), cascade='all, delete-orphan'
    )
    dependencies_out = db.relationship(
        'TaskDependency', foreign_keys='TaskDependency.predecessor_id',
        backref=db.backref('predecessor', lazy=True), cascade='all, delete-orphan'
    )

    # Legacy / UI uyumluluğu: assigned_to_id alanı ve bazı template'ler
    @hybrid_property
    def assigned_to_id(self):
        return self.assignee_id

    @assigned_to_id.setter
    def assigned_to_id(self, value):
        self.assignee_id = value

    @assigned_to_id.expression
    def assigned_to_id(cls):
        return cls.assignee_id

    @property
    def assigned_to(self):
        return self.assignee

    @assigned_to.setter
    def assigned_to(self, value):
        self.assignee = value
    
    def __repr__(self):
        return f'<Task {self.title}>'

class TaskImpact(db.Model):
    """
    Görev Etki Analizi Modeli
    
    Görevlerin stratejik hedefler veya PG'ler üzerindeki etkisini tanımlar.
    """
    __tablename__ = 'task_impact'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False, index=True)
    
    # Etkilenen Öğe
    impact_type = db.Column(db.String(50)) # 'Process', 'Strategy', 'KPI'
    impact_id = db.Column(db.Integer)
    description = db.Column(db.Text)
    
    # Etki Durumu (Eksik kolonlar eklendi)
    is_processed = db.Column(db.Boolean, default=False)
    processed_at = db.Column(db.DateTime, nullable=True)
    
    task = db.relationship('Task', backref=db.backref('impacts', lazy=True))

class TaskComment(db.Model):
    """Görev Yorumları"""
    __tablename__ = 'task_comment'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    task = db.relationship('Task', backref=db.backref('comments', lazy=True))
    user = db.relationship('User', backref='task_comments')

class TaskMention(db.Model):
    """Görev içi kullanıcı etiketleme"""
    __tablename__ = 'task_mention'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    mentioned_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('task_comment.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProjectFile(db.Model):
    """Proje Dosyaları"""
    __tablename__ = 'project_file'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProjectRisk(db.Model):
    """Proje Riskleri"""
    __tablename__ = 'project_risk'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    probability = db.Column(db.String(20)) # Low, Medium, High
    impact = db.Column(db.String(20)) # Low, Medium, High
    status = db.Column(db.String(20)) # Open, Mitigated, Closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Faz 2/3 Yeni Proje Modelleri
class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(20))

class TaskSubtask(db.Model):
    __tablename__ = 'task_subtask'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    
class TimeEntry(db.Model):
    __tablename__ = 'time_entry'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date)
    
class TaskActivity(db.Model):
    __tablename__ = 'task_activity'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TaskDependency(db.Model):
    """Görev bağımlılıkları (tip ve lag içeren)."""
    __tablename__ = 'task_dependency'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False, index=True)
    successor_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False, index=True)
    predecessor_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False, index=True)
    dependency_type = db.Column(db.String(4), default='FS')  # FS, SS, FF, SF
    lag_days = db.Column(db.Integer, default=0)

    project = db.relationship('Project', backref=db.backref('dependencies', lazy=True))


class IntegrationHook(db.Model):
    __tablename__ = 'integration_hook'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False, index=True)
    provider = db.Column(db.String(50), nullable=False)  # slack, teams, outlook
    url = db.Column(db.String(500), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    project = db.relationship('Project', backref=db.backref('integration_hooks', lazy=True))


class RuleDefinition(db.Model):
    __tablename__ = 'rule_definition'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True, index=True)
    name = db.Column(db.String(200), nullable=False)
    trigger = db.Column(db.String(100), nullable=False)  # status_change, due_date_passed, dependency_completed
    condition_json = db.Column(db.Text, nullable=True)
    actions_json = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    project = db.relationship('Project', backref=db.backref('rules', lazy=True))


class SLA(db.Model):
    __tablename__ = 'sla'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True, index=True)
    name = db.Column(db.String(200), nullable=False)
    target_hours = db.Column(db.Integer, nullable=False)
    breach_policy = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    project = db.relationship('Project', backref=db.backref('slas', lazy=True))


class RecurringTask(db.Model):
    __tablename__ = 'recurring_task'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    cron_expr = db.Column(db.String(100), nullable=False)  # örn: weekly, monthly, 0 9 * * 1
    template_task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    next_run_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    project = db.relationship('Project', backref=db.backref('recurring_tasks', lazy=True))
    template_task = db.relationship('Task', foreign_keys=[template_task_id])


class WorkingDay(db.Model):
    __tablename__ = 'working_day'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    is_working = db.Column(db.Boolean, default=True)

    project = db.relationship('Project', backref=db.backref('working_days', lazy=True))


class CapacityPlan(db.Model):
    __tablename__ = 'capacity_plan'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    weekly_hours = db.Column(db.Float, nullable=False, default=40.0)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)

    project = db.relationship('Project', backref=db.backref('capacity_plans', lazy=True))
    user = db.relationship('User', foreign_keys=[user_id])


class RaidItem(db.Model):
    __tablename__ = 'raid_item'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False, index=True)
    item_type = db.Column(db.String(20), nullable=False)  # Risk, Assumption, Issue, Dependency
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    status = db.Column(db.String(50), default='Open')
    
    # Risk alanları
    probability = db.Column(db.Integer, nullable=True)  # 1-5 arası
    impact = db.Column(db.Integer, nullable=True)  # 1-5 arası
    mitigation_plan = db.Column(db.Text, nullable=True)
    
    # Assumption alanları
    assumption_validation_date = db.Column(db.Date, nullable=True)  # Varsayımın doğrulama tarihi
    assumption_validated = db.Column(db.Boolean, default=False)
    assumption_notes = db.Column(db.Text, nullable=True)
    
    # Issue alanları
    issue_urgency = db.Column(db.String(50), nullable=True)  # Yüksek, Orta, Düşük
    issue_affected_work = db.Column(db.String(200), nullable=True)  # Etkilenen çalışma
    
    # Dependency alanları
    dependency_task_id = db.Column(db.Integer, nullable=True)  # Bağımlı görev
    dependency_type = db.Column(db.String(50), nullable=True)  # FS, SS, FF, SF (Critical Path tiplemeleri)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship('Project', backref=db.backref('raid_items', lazy=True))
    owner = db.relationship('User', foreign_keys=[owner_id])


class TaskBaseline(db.Model):
    __tablename__ = 'task_baseline'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False, index=True)
    planned_start = db.Column(db.Date, nullable=True)
    planned_end = db.Column(db.Date, nullable=True)
    planned_effort = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    task = db.relationship('Task', backref=db.backref('baseline', uselist=False))

class ProjectTemplate(db.Model):
    __tablename__ = 'project_template'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    structure = db.Column(db.Text) # JSON

class TaskTemplate(db.Model):
    __tablename__ = 'task_template'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
class Sprint(db.Model):
    __tablename__ = 'sprint'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20))

class TaskSprint(db.Model):
    __tablename__ = 'task_sprint'
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), primary_key=True)
    sprint_id = db.Column(db.Integer, db.ForeignKey('sprint.id'), primary_key=True)
