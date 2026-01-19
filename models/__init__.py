# -*- coding: utf-8 -*-
"""
Veritabanı Modelleri Paketi
---------------------------
Uygulamanın tüm veritabanı modellerini tek bir noktadan sunar.
"""

# DB instance'ını dışarıya aç (geriye dönük uyumluluk için)
from extensions import db

from .user import (
    User, Kurum, YetkiMatrisi, OzelYetki, KullaniciYetki,
    DashboardLayout, Deger, EtikKural, KalitePolitikasi,
    Notification, UserActivityLog
)
from .strategy import AnaStrateji, AltStrateji, StrategyProcessMatrix
from .process import (
    Surec, SurecPerformansGostergesi, SurecFaaliyet, 
    SwotAnalizi, PestleAnalizi, TowsAnalizi,
    BireyselPerformansGostergesi, BireyselFaaliyet,
    PerformansGostergeVeri, PerformansGostergeVeriAudit,
    FaaliyetTakip, FavoriKPI,
    surec_uyeleri, surec_liderleri, surec_alt_stratejiler, process_owners
)
from .project import (
    Project, Task, TaskImpact, TaskComment, TaskMention,
    ProjectFile, ProjectRisk, Tag, TaskSubtask, TimeEntry,
    TaskActivity, ProjectTemplate, TaskTemplate, Sprint, TaskSprint,
    TaskDependency, IntegrationHook, RuleDefinition, SLA, RecurringTask, WorkingDay, CapacityPlan, RaidItem, TaskBaseline,
    project_members, project_observers, project_related_processes, task_predecessors
)

# V67 Activity Modeli
from datetime import datetime

class Activity(db.Model):
    """
    Genel Aktivite Modeli (V67)
    Tüm sistemdeki (Jira, Redmine, Dahili) aktivitelerin tek bir havuzda toplanması.
    """
    __tablename__ = 'activity'

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(50), nullable=False)  # Redmine, Jira, System
    external_id = db.Column(db.String(100))
    
    project_name = db.Column(db.String(200))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    
    subject = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    
    status = db.Column(db.String(50))
    priority = db.Column(db.String(50))
    
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=True)
    
    project = db.relationship('Project', backref=db.backref('activities', lazy=True))
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id])

# Faz 2/3/4 için Placeholder Moderller
class CorporateIdentity(db.Model):
    __tablename__ = 'corporate_identity'
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'))

# Aliases for English compatibility (Legacy Support)
Process = Surec
PerformanceIndicator = SurecPerformansGostergesi
MainStrategy = AnaStrateji
SubStrategy = AltStrateji

# __all__ listesi
__all__ = [
    'db', # Export db
    # User
    'User', 'Kurum', 'YetkiMatrisi', 'OzelYetki', 'KullaniciYetki',
    'DashboardLayout', 'Deger', 'EtikKural', 'KalitePolitikasi',
    'Notification', 'UserActivityLog',
    
    # Strategy
    'AnaStrateji', 'AltStrateji', 'StrategyProcessMatrix',
    'MainStrategy', 'SubStrategy', # Aliases
    
    # Process
    'Surec', 'SurecPerformansGostergesi', 'SurecFaaliyet', 
    'SwotAnalizi', 'PestleAnalizi', 'TowsAnalizi',
    'BireyselPerformansGostergesi', 'BireyselFaaliyet',
    'PerformansGostergeVeri', 'PerformansGostergeVeriAudit',
    'FaaliyetTakip', 'FavoriKPI',
    'surec_uyeleri', 'surec_liderleri', 'surec_alt_stratejiler', 'process_owners',
    'Process', 'PerformanceIndicator', # Aliases
    
    # Project
    'Project', 'Task', 'TaskImpact', 'TaskComment', 'TaskMention',
    'ProjectFile', 'ProjectRisk', 'Tag', 'TaskSubtask', 'TimeEntry',
    'TaskActivity', 'ProjectTemplate', 'TaskTemplate', 'Sprint', 'TaskSprint', 'TaskDependency',
    'IntegrationHook', 'RuleDefinition', 'SLA', 'RecurringTask', 'WorkingDay', 'CapacityPlan', 'RaidItem', 'TaskBaseline',
    'project_members', 'project_observers', 'project_related_processes', 'task_predecessors',
    
    # V67 & Others
    'Activity', 'CorporateIdentity'
]

# Eksik olan Faz 2/3 modellerini mock olarak ekle (Import hatalarını önlemek için)
models_to_mock = [
    'ObjectiveComment', 'StrategicPlan', 'PlanItem', 'GembaWalk',
    'Competency', 'UserCompetency', 'StrategicRisk', 'MudaFinding',
    'CrisisMode', 'SafetyCheck', 'SuccessionPlan', 'OrgScenario', 'OrgChange', 
    'InfluenceScore', 'MarketIntel', 'WellbeingScore', 'SimulationScenario', 
    'DeepWorkSession', 'Persona', 'ProductSimulation', 'SmartContract', 
    'DaoProposal', 'DaoVote', 'MetaverseDepartment', 'LegacyKnowledge',
    'Competitor', 'GameScenario', 'DoomsdayScenario', 'YearlyChronicle'
]

for model_name in models_to_mock:
    if model_name not in globals():
        # Geçici Mock Class OLUŞTUR VE GLOBALS'E ATA
        mock_class = type(model_name, (db.Model,), {
            '__tablename__': f'mock_{model_name.lower()}',
            'id': db.Column(db.Integer, primary_key=True),
            '__module__': __name__
        })
        globals()[model_name] = mock_class
        __all__.append(model_name)
