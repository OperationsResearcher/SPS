from datetime import datetime, timezone
from sqlalchemy.ext.associationproxy import association_proxy
from extensions import db
from app.models.core import SubStrategy

# Association Tables (Many-to-Many Relationships)

# Process Sub-Strategy Links (with contribution percentage)
class ProcessSubStrategyLink(db.Model):
    """Süreç–Alt Strateji bağlantısı; her bağlantıya katkı yüzdesi atanabilir."""
    __tablename__ = 'process_sub_strategy_links'

    process_id = db.Column(db.Integer, db.ForeignKey('processes.id', ondelete='CASCADE'), primary_key=True)
    sub_strategy_id = db.Column(db.Integer, db.ForeignKey('sub_strategies.id', ondelete='CASCADE'), primary_key=True)
    contribution_pct = db.Column(db.Float, nullable=True)  # 0–100

    process = db.relationship('Process', backref=db.backref('process_sub_strategy_links', cascade='all, delete-orphan', lazy=True))
    sub_strategy = db.relationship('SubStrategy', backref=db.backref('process_sub_strategy_links', lazy=True))

    def __repr__(self):
        return f'<ProcessSubStrategyLink p={self.process_id} ss={self.sub_strategy_id} %{self.contribution_pct}>'


# Process members (Süreç Üyeleri)
process_members = db.Table('process_members',
    db.Column('process_id', db.Integer, db.ForeignKey('processes.id', ondelete='CASCADE'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
)

# Process leaders (Süreç Liderleri)
process_leaders = db.Table('process_leaders',
    db.Column('process_id', db.Integer, db.ForeignKey('processes.id', ondelete='CASCADE'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
)

# Process owners (Süreç Sahipleri)
process_owners_table = db.Table('process_owners_table',
    db.Column('process_id', db.Integer, db.ForeignKey('processes.id', ondelete='CASCADE'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
)

class Process(db.Model):
    """
    Process Model (Süreç)
    
    Defines the organization's business processes.
    Hierarchical structure using parent_id.
    """
    __tablename__ = 'processes'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('processes.id', ondelete='SET NULL'), nullable=True, index=True)

    # Core details
    code = db.Column(db.String(20), nullable=True, index=True)  # e.g.: SR1
    name = db.Column(db.String(200), nullable=False, index=True) # Turkish Name
    english_name = db.Column(db.String(200), nullable=True) # Optional English Translation
    
    # KYS/Quality Details
    weight = db.Column(db.Float, nullable=True) # 0-100 score engine
    document_no = db.Column(db.String(50), nullable=True)
    revision_no = db.Column(db.String(20), nullable=True)
    revision_date = db.Column(db.Date, nullable=True)
    first_publish_date = db.Column(db.Date, nullable=True)
    
    # Status and Progress
    status = db.Column(db.String(50), default='Aktif') # Aktif, Pasif vs.
    progress = db.Column(db.Integer, default=0)
    
    # Scope
    start_boundary = db.Column(db.Text, nullable=True)
    end_boundary = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Auditing / Soft Delete
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    tenant = db.relationship('Tenant', backref=db.backref('processes', lazy=True, cascade="all, delete-orphan"))
    parent = db.relationship('Process', remote_side=[id], backref=db.backref('sub_processes', lazy='dynamic'))
    
    # Many-to-Many
    leaders = db.relationship('User', secondary=process_leaders, backref='led_processes')
    members = db.relationship('User', secondary=process_members, backref='member_processes')
    owners = db.relationship('User', secondary=process_owners_table, backref='owned_processes')

    # Sub-strategies (via association object for contribution_pct)
    sub_strategies = association_proxy('process_sub_strategy_links', 'sub_strategy',
        creator=lambda ss: ProcessSubStrategyLink(sub_strategy=ss))
    
    def __repr__(self):
        return f'<Process {self.code} - {self.name}>'


# SubStrategy.processes (reverse) — process.py'de tanımlandığı için burada ekliyoruz
SubStrategy.processes = association_proxy('process_sub_strategy_links', 'process')


class ProcessKpi(db.Model):
    """
    Process Key Performance Indicator Model (Süreç PG)
    """
    __tablename__ = 'process_kpis'
    
    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('processes.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Basic info
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    code = db.Column(db.String(50), nullable=True)  # e.g.: PG-01
    
    # Targets
    target_value = db.Column(db.String(100), nullable=True)
    unit = db.Column(db.String(50), nullable=True)
    period = db.Column(db.String(50), nullable=True)  # Aylık, Çeyreklik, Yıllık
    
    # Methods
    data_source = db.Column(db.String(200), nullable=True)
    target_setting_method = db.Column(db.String(200), nullable=True)
    data_collection_method = db.Column(db.String(50), default='Ortalama')  # Toplama, Ortalama, Son Değer
    calculation_method = db.Column(db.String(20), default='AVG')

    # Eski proje uyumluluğu — Yeni alanlar
    gosterge_turu = db.Column(db.String(50), nullable=True)       # İyileştirme, Koruma, Bilgi Amaçlı
    target_method = db.Column(db.String(10), nullable=True)       # RG, HKY, HK, SH, DH, SGH
    basari_puani_araliklari = db.Column(db.Text, nullable=True)   # JSON: {"1":"0-40"} veya {"1":{"aralik":"0-40","aciklama":"..."}}
    onceki_yil_ortalamasi = db.Column(db.Float, nullable=True)    # Önceki yıl performans bazı

    # Configuration
    weight = db.Column(db.Float, default=0, nullable=True)
    is_important = db.Column(db.Boolean, default=False)
    direction = db.Column(db.String(20), default='Increasing')  # Increasing/Decreasing
    
    calculated_score = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    
    # Linking
    sub_strategy_id = db.Column(db.Integer, db.ForeignKey('sub_strategies.id', ondelete='SET NULL'), nullable=True, index=True)
    
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    process = db.relationship('Process', backref=db.backref('kpis', lazy=True, cascade='all, delete-orphan'))
    sub_strategy = db.relationship('SubStrategy', backref=db.backref('process_kpis', lazy=True))
    
    def __repr__(self):
        return f'<ProcessKpi {self.name}>'


class ProcessActivity(db.Model):
    """
    Process Activity Model (Süreç Faaliyeti/Aksiyon).
    """
    __tablename__ = 'process_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('processes.id', ondelete='CASCADE'), nullable=False, index=True)
    process_kpi_id = db.Column(db.Integer, db.ForeignKey('process_kpis.id', ondelete='SET NULL'), nullable=True, index=True)
    
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Legacy date-only alanları (geriye dönük uyumluluk)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)

    # V2 zaman planı (asıl işleyen alanlar)
    start_at = db.Column(db.DateTime, nullable=True, index=True)
    end_at = db.Column(db.DateTime, nullable=True, index=True)
    
    status = db.Column(db.String(50), default='Planlandı')
    progress = db.Column(db.Integer, default=0)
    notify_email = db.Column(db.Boolean, default=False, nullable=False)
    auto_complete_enabled = db.Column(db.Boolean, default=True, nullable=False)
    auto_pgv_created = db.Column(db.Boolean, default=False, nullable=False, index=True)
    auto_pgv_kpi_data_id = db.Column(db.Integer, db.ForeignKey('kpi_data.id', ondelete='SET NULL'), nullable=True, index=True)

    completed_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    postponed_at = db.Column(db.DateTime, nullable=True)

    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    process = db.relationship('Process', backref=db.backref('activities', lazy=True, cascade='all, delete-orphan'))
    process_kpi = db.relationship('ProcessKpi', backref=db.backref('activities', lazy=True))
    auto_pgv_kpi_data = db.relationship('KpiData', foreign_keys=[auto_pgv_kpi_data_id], uselist=False)
    assignees = db.relationship(
        'User',
        secondary='process_activity_assignees',
        primaryjoin='ProcessActivity.id == ProcessActivityAssignee.activity_id',
        secondaryjoin='User.id == ProcessActivityAssignee.user_id',
        foreign_keys='[ProcessActivityAssignee.activity_id, ProcessActivityAssignee.user_id]',
        backref=db.backref('assigned_process_activities', lazy=True),
        overlaps='assignment_links,process_activity_assignments,activity,user',
        lazy=True,
    )
    
    def __repr__(self):
        return f'<ProcessActivity {self.name}>'

    @property
    def first_assignee_id(self):
        links = sorted(self.assignment_links, key=lambda x: (x.order_no or 0, x.created_at or datetime.min))
        return links[0].user_id if links else None


class ProcessActivityAssignee(db.Model):
    """V2: Süreç faaliyeti çoklu atama ilişkisi."""
    __tablename__ = 'process_activity_assignees'

    activity_id = db.Column(db.Integer, db.ForeignKey('process_activities.id', ondelete='CASCADE'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    order_no = db.Column(db.Integer, nullable=False, default=1)
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    assigned_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    activity = db.relationship(
        'ProcessActivity',
        backref=db.backref('assignment_links', lazy=True, cascade='all, delete-orphan', overlaps='assignees,assigned_process_activities'),
        overlaps='assignees,assigned_process_activities',
    )
    user = db.relationship(
        'User',
        foreign_keys=[user_id],
        backref=db.backref('process_activity_assignments', lazy=True, overlaps='assignees,assigned_process_activities'),
        overlaps='assignees,assigned_process_activities',
    )
    assigner = db.relationship('User', foreign_keys=[assigned_by], backref=db.backref('assigned_process_activities_links', lazy=True))

    def __repr__(self):
        return f'<ProcessActivityAssignee a={self.activity_id} u={self.user_id} o={self.order_no}>'


class ProcessActivityReminder(db.Model):
    """V2: Süreç faaliyeti için çoklu hatırlatma satırları."""
    __tablename__ = 'process_activity_reminders'

    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('process_activities.id', ondelete='CASCADE'), nullable=False, index=True)
    minutes_before = db.Column(db.Integer, nullable=False)
    remind_at = db.Column(db.DateTime, nullable=False, index=True)
    channel_email = db.Column(db.Boolean, default=False, nullable=False)
    sent_at = db.Column(db.DateTime, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    activity = db.relationship('ProcessActivity', backref=db.backref('reminders', lazy=True, cascade='all, delete-orphan'))

    __table_args__ = (
        db.UniqueConstraint('activity_id', 'minutes_before', name='uq_activity_reminder_offset'),
    )

    def __repr__(self):
        return f'<ProcessActivityReminder a={self.activity_id} m={self.minutes_before}>'


class ActivityTrack(db.Model):
    """
    Monthly tracking for process activities (Aylık Faaliyet Takibi).
    Checkbox: did this activity happen in this month?
    """
    __tablename__ = 'activity_tracks'

    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('process_activities.id', ondelete='CASCADE'), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    completed = db.Column(db.Boolean, default=False, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    activity = db.relationship('ProcessActivity', backref=db.backref('tracks', lazy=True, cascade='all, delete-orphan'))

    __table_args__ = (
        db.UniqueConstraint('activity_id', 'year', 'month', name='uq_activity_track'),
    )

    def __repr__(self):
        return f'<ActivityTrack activity={self.activity_id} {self.year}/{self.month} done={self.completed}>'


class KpiData(db.Model):
    """
    KPI Data Model (Performans Gösterge Veri)
    Stores the factual data entered for KPIs mapped over time.
    """
    __tablename__ = 'kpi_data'
    
    id = db.Column(db.Integer, primary_key=True)
    process_kpi_id = db.Column(db.Integer, db.ForeignKey('process_kpis.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Timing
    year = db.Column(db.Integer, nullable=False, index=True)
    data_date = db.Column(db.Date, nullable=False, index=True)
    
    period_type = db.Column(db.String(20), nullable=True)  # yillik, ceyrek, aylik
    period_no = db.Column(db.Integer, nullable=True)
    period_month = db.Column(db.Integer, nullable=True)
    
    # Values
    target_value = db.Column(db.String(100), nullable=True)
    actual_value = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=True)
    status_percentage = db.Column(db.Float, nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Auditing
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Veriyi giren
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)  # Soft delete: is_active=False
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)
    deleted_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)

    # Relationships
    process_kpi = db.relationship('ProcessKpi', backref=db.backref('data_entries', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('entered_kpi_data', lazy=True))
    deleted_by = db.relationship('User', foreign_keys=[deleted_by_id], backref=db.backref('deleted_kpi_data_rows', lazy=True))
    
    __table_args__ = (
        db.Index('idx_kpi_data_lookup', 'process_kpi_id', 'year', 'data_date'),
    )


class KpiDataAudit(db.Model):
    """KPI Data Audit Log"""
    __tablename__ = 'kpi_data_audits'
    
    id = db.Column(db.Integer, primary_key=True)
    kpi_data_id = db.Column(db.Integer, db.ForeignKey('kpi_data.id', ondelete='CASCADE'), nullable=False, index=True)
    
    action_type = db.Column(db.String(20), nullable=False) # CREATE, UPDATE, DELETE
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    action_detail = db.Column(db.Text, nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    kpi_data = db.relationship('KpiData', backref=db.backref('audits', lazy=True, passive_deletes=True))
    user = db.relationship('User', backref=db.backref('kpi_audits', lazy=True))


# ─────────────────────────────────────────────────────────────
# Bireysel Performans Göstergeleri ve Faaliyetler (Eski Proje Uyumu)
# ─────────────────────────────────────────────────────────────

class IndividualPerformanceIndicator(db.Model):
    """
    Bireysel Performans Göstergesi (Bireysel PG).
    Kullanıcının bireysel hedeflerini veya süreçten atanan hedefleri tutar.
    """
    __tablename__ = 'individual_performance_indicators'
    
    __table_args__ = (
        db.Index('idx_indiv_pg_user_source', 'user_id', 'source'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    code = db.Column(db.String(50), nullable=True)
    
    target_value = db.Column(db.String(100), nullable=True)
    actual_value = db.Column(db.String(100), nullable=True)
    unit = db.Column(db.String(50), nullable=True)
    
    period = db.Column(db.String(50), nullable=True)
    weight = db.Column(db.Float, default=0, nullable=True)
    is_important = db.Column(db.Boolean, default=False)
    
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default='Devam Ediyor')
    
    source = db.Column(db.String(50), default='Bireysel')
    source_process_id = db.Column(db.Integer, db.ForeignKey('processes.id', ondelete='SET NULL'), nullable=True, index=True)
    source_process_kpi_id = db.Column(db.Integer, db.ForeignKey('process_kpis.id', ondelete='SET NULL'), nullable=True, index=True)
    
    direction = db.Column(db.String(20), default='Increasing')
    basari_puani_araliklari = db.Column(db.Text, nullable=True)
    
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', backref=db.backref('individual_performance_indicators', lazy=True))
    source_process = db.relationship('Process', foreign_keys=[source_process_id])
    source_process_kpi = db.relationship('ProcessKpi', foreign_keys=[source_process_kpi_id])
    
    def __repr__(self):
        return f'<IndividualPerformanceIndicator {self.name}>'


class IndividualActivity(db.Model):
    """
    Bireysel Faaliyet.
    Kullanıcının kendine atadığı veya süreçten gelen aksiyonlar.
    """
    __tablename__ = 'individual_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    
    status = db.Column(db.String(50), default='Planlandı')
    progress = db.Column(db.Integer, default=0)
    
    source = db.Column(db.String(50), default='Bireysel')
    source_process_id = db.Column(db.Integer, db.ForeignKey('processes.id', ondelete='SET NULL'), nullable=True, index=True)
    source_process_activity_id = db.Column(db.Integer, db.ForeignKey('process_activities.id', ondelete='SET NULL'), nullable=True, index=True)
    
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', backref=db.backref('individual_activities', lazy=True))
    source_process = db.relationship('Process', foreign_keys=[source_process_id])
    source_process_activity = db.relationship('ProcessActivity', foreign_keys=[source_process_activity_id])
    
    def __repr__(self):
        return f'<IndividualActivity {self.name}>'


class IndividualKpiData(db.Model):
    """
    Bireysel PG'ye bağlı performans verisi (PerformansGostergeVeri).
    Periyodik veri girişi için kullanılır.
    """
    __tablename__ = 'individual_kpi_data'
    
    __table_args__ = (
        db.Index('idx_indiv_kpi_data_lookup', 'individual_pg_id', 'year', 'data_date'),
        db.Index('idx_indiv_kpi_data_user', 'user_id', 'year'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    individual_pg_id = db.Column(db.Integer, db.ForeignKey('individual_performance_indicators.id', ondelete='CASCADE'), nullable=False, index=True)
    
    year = db.Column(db.Integer, nullable=False, index=True)
    data_date = db.Column(db.Date, nullable=False, index=True)
    
    period_type = db.Column(db.String(20), nullable=True)
    period_no = db.Column(db.Integer, nullable=True)
    period_month = db.Column(db.Integer, nullable=True)
    
    target_value = db.Column(db.String(100), nullable=True)
    actual_value = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=True)
    status_percentage = db.Column(db.Float, nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    individual_pg = db.relationship('IndividualPerformanceIndicator', backref=db.backref('data_entries', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User', foreign_keys=[user_id])
    
    def __repr__(self):
        return f'<IndividualKpiData pg={self.individual_pg_id} {self.year} {self.data_date}>'


class IndividualKpiDataAudit(db.Model):
    """Bireysel PG Veri Değişiklik Geçmişi (Audit Log)"""
    __tablename__ = 'individual_kpi_data_audits'
    
    id = db.Column(db.Integer, primary_key=True)
    individual_kpi_data_id = db.Column(db.Integer, db.ForeignKey('individual_kpi_data.id', ondelete='CASCADE'), nullable=False, index=True)
    
    action_type = db.Column(db.String(20), nullable=False)
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    action_detail = db.Column(db.Text, nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    individual_kpi_data = db.relationship('IndividualKpiData', backref=db.backref('audits', lazy=True, passive_deletes=True))
    user = db.relationship('User', backref=db.backref('individual_kpi_audits', lazy=True))


class IndividualActivityTrack(db.Model):
    """Bireysel faaliyet aylık takibi (FaaliyetTakip)"""
    __tablename__ = 'individual_activity_tracks'
    
    id = db.Column(db.Integer, primary_key=True)
    individual_activity_id = db.Column(db.Integer, db.ForeignKey('individual_activities.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    note = db.Column(db.Text, nullable=True)
    completed_date = db.Column(db.Date, nullable=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    individual_activity = db.relationship('IndividualActivity', backref=db.backref('tracks', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('individual_activity_tracks', lazy=True))
    
    __table_args__ = (
        db.UniqueConstraint('individual_activity_id', 'year', 'month', name='uq_indiv_activity_track'),
    )
    
    def __repr__(self):
        return f'<IndividualActivityTrack activity={self.individual_activity_id} {self.year}/{self.month}>'


class FavoriteKpi(db.Model):
    """Favori Performans Göstergesi"""
    __tablename__ = 'favorite_kpis'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    process_kpi_id = db.Column(db.Integer, db.ForeignKey('process_kpis.id', ondelete='CASCADE'), nullable=False, index=True)
    sort_order = db.Column(db.Integer, default=0)
    # Kural 4: Hard delete yasağı — soft delete desteği
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', backref=db.backref('favorite_kpis', lazy=True))
    process_kpi = db.relationship('ProcessKpi', backref=db.backref('favorited_by', lazy=True))
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'process_kpi_id', name='uq_favorite_kpi'),
    )

