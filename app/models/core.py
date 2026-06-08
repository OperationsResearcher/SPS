"""Core models: Tenant, Role, User."""

from datetime import datetime, timezone

from flask_login import UserMixin

from app.models import db


class Tenant(db.Model):
    """Tenant (organization) model."""

    __tablename__ = "tenants"
    __table_args__ = (
        # Alt-tenant listelerinde (parent_tenant_id + is_active) sık filtreleniyor
        db.Index("ix_tenant_parent_active", "parent_tenant_id", "is_active"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    short_name = db.Column(db.String(64), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey("subscription_packages.id"), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Eski kurum formu alanları (snake_case, İngilizce)
    activity_area = db.Column(db.String(200), nullable=True)  # Faaliyet Alanı
    sector = db.Column(db.String(100), nullable=True)  # Sektör
    employee_count = db.Column(db.Integer, nullable=True)  # Çalışan Sayısı
    contact_email = db.Column(db.String(120), nullable=True)  # Kurum E-posta
    phone_number = db.Column(db.String(20), nullable=True)  # Telefon
    website_url = db.Column(db.String(200), nullable=True)  # Web Adresi
    tax_office = db.Column(db.String(100), nullable=True)  # Vergi Dairesi
    tax_number = db.Column(db.String(20), nullable=True)  # Vergi Numarası
    max_user_count = db.Column(db.Integer, default=5, nullable=True)  # Maks. Kullanıcı Sayısı
    license_end_date = db.Column(db.Date, nullable=True)  # Lisans Bitiş Tarihi

    # Yeni Stratejik Kimlik Alanları
    purpose = db.Column(db.Text, nullable=True)  # Amaç
    vision = db.Column(db.Text, nullable=True)  # Vizyon
    core_values = db.Column(db.Text, nullable=True)  # Değerler
    code_of_ethics = db.Column(db.Text, nullable=True)  # Etik Kurallar
    quality_policy = db.Column(db.Text, nullable=True)  # Kalite Politikası

    # Kurum logosu (instance/uploads/tenant_logos/ altında saklanır; dosya adı örn. "5.png")
    logo_path = db.Column(db.String(500), nullable=True)
    logo_updated_at = db.Column(db.DateTime, nullable=True)

    k_vektor_enabled = db.Column(db.Boolean, default=False, nullable=False)
    k_radar_enabled = db.Column(db.Boolean, default=False, nullable=False)
    plan_year_enabled = db.Column(db.Boolean, default=False, nullable=False)
    plan_year_start = db.Column(db.Integer, nullable=True)  # Geçmiş yıl başlangıcı (ör. 2021)

    # ─── Bayi/Holding Hiyerarşisi (Sprint A) ──────────────────────────────────
    # tenant_type: 'normal' (bağımsız) / 'dealer' (bayi) / 'holding' (grup şirketi)
    # Sadece Platform Admin atayabilir. Karar: docs/AI-POLITIKASI değil — yeni bir kural seti.
    tenant_type = db.Column(db.String(20), default="normal", nullable=False)

    # Alt tenant ise parent buraya yazılır. NULL = bağımsız tenant.
    parent_tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )

    # Bayi/Holding kaç alt tenant açabilir? NULL = sınırsız (paket bazlı override edilir)
    sub_tenant_limit = db.Column(db.Integer, nullable=True)

    package = db.relationship("SubscriptionPackage", back_populates="tenants", lazy="select")
    users = db.relationship("User", back_populates="tenant", lazy="select")

    # Self-referencing: parent + children
    parent_tenant = db.relationship(
        "Tenant", remote_side="Tenant.id",
        foreign_keys=[parent_tenant_id],
        backref=db.backref("sub_tenants", lazy="dynamic"),
    )

    # Helper'lar
    @property
    def is_dealer(self) -> bool:
        return self.tenant_type == "dealer"

    @property
    def is_holding(self) -> bool:
        return self.tenant_type == "holding"

    @property
    def is_parent_capable(self) -> bool:
        """Bu tenant alt-tenant açabilir mi?"""
        return self.tenant_type in ("dealer", "holding")

    @property
    def is_sub_tenant(self) -> bool:
        return self.parent_tenant_id is not None


class Role(db.Model):
    """Role model for user authorization."""

    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    users = db.relationship("User", back_populates="role")


class User(UserMixin, db.Model):
    """User model with Flask-Login support."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    # Soft delete: is_active=False (deleted_at kolonu KASITLI olarak yok —
    # sil tarihi/kim sildi gerekirse audit_logs'tan alınabilir)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Eski kullanıcı formu alanları (snake_case, İngilizce)
    phone_number = db.Column(db.String(20), nullable=True)  # Telefon
    job_title = db.Column(db.String(100), nullable=True)  # Unvan
    department = db.Column(db.String(100), nullable=True)  # Departman
    profile_picture = db.Column(db.String(500), nullable=True)  # Profil fotoğrafı URL

    # Ayarlar (settings) - JSON veya basit alanlar
    theme_preferences = db.Column(db.Text, nullable=True)  # JSON: {theme, color}
    layout_preference = db.Column(db.String(20), default="classic", nullable=False)  # classic, sidebar
    notification_preferences = db.Column(db.Text, nullable=True)  # JSON: {email, process, task, deadline}
    locale_preferences = db.Column(db.Text, nullable=True)  # JSON: {language, timezone, date_format}
    show_page_guides = db.Column(db.Boolean, default=True, nullable=False)
    guide_character_style = db.Column(db.String(50), default="professional", nullable=False)  # professional, friendly, minimal

    # Sprint 26: TOTP 2FA alanları
    totp_secret = db.Column(db.String(64), nullable=True)  # base32 secret
    totp_enabled = db.Column(db.Boolean, default=False, nullable=False)
    totp_backup_codes_json = db.Column(db.Text, nullable=True)  # JSON list

    tenant = db.relationship("Tenant", back_populates="users", lazy="select")
    role = db.relationship("Role", back_populates="users")

    @property
    def kurum_id(self):
        """Legacy `main` rotaları (proje portföyü, matris) ile uyum.

        Veritabanında `tenants.id` ile eski `kurum.id` aynı değerleri kullanmalıdır.
        """
        return self.tenant_id

    @property
    def sistem_rol(self):
        """Legacy `decorators.role_required` ve strateji şablonları için rol kodu."""
        if not self.role or not self.role.name:
            return "kurum_kullanici"
        r = self.role.name.strip()
        aliases = {
            "Admin": "admin",
            "tenant_admin": "kurum_yoneticisi",
            "executive_manager": "ust_yonetim",
            "yonetici": "surec_lideri",
            "calisan": "kurum_kullanici",
            "kurum_kullanici": "kurum_kullanici",
            "izleyici": "kurum_kullanici",
        }
        return aliases.get(r, r.lower().replace(" ", "_"))


class Ticket(db.Model):
    """Kule İletişim (Ticket) Modeli."""

    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=True, index=True)
    page_url = db.Column(db.String(500), nullable=True)
    subject = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    screenshot_path = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(50), default="Bekliyor", nullable=False)
    admin_note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = db.relationship("User", backref=db.backref("tickets", lazy=True))
    tenant = db.relationship("Tenant", backref=db.backref("tickets", lazy=True))

    def __repr__(self):
        return f"<Ticket {self.id} - {self.subject} - {self.status}>"


class Strategy(db.Model):
    """
    Main Strategy Model (Ana Strateji).
    Defines the top-level strategic goals of the institution.
    """
    __tablename__ = "strategies"
    __table_args__ = (
        # Sık kullanılan birleşik filtre: tenant + plan_year bazlı listeleme
        db.Index("idx_strategy_tenant_plan_year", "tenant_id", "plan_year_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    # Code and Title
    code = db.Column(db.String(20), nullable=True, index=True)  # e.g., ST1
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Meta Data
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Plan Year FK (Full Clone sistemi)
    plan_year_id = db.Column(db.Integer, db.ForeignKey("plan_years.id", ondelete="CASCADE"), nullable=True, index=True)
    source_strategy_id = db.Column(db.Integer, db.ForeignKey("strategies.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    tenant = db.relationship("Tenant", backref=db.backref("strategies", lazy=True, cascade="all, delete-orphan", order_by="Strategy.code"))
    source_strategy = db.relationship("Strategy", remote_side="Strategy.id", foreign_keys="Strategy.source_strategy_id")

    def __repr__(self):
        return f"<Strategy {self.code or ''} - {self.title}>"


class SubStrategy(db.Model):
    """
    Sub Strategy Model (Alt Strateji).
    Breakdown of main strategies.
    """
    __tablename__ = "sub_strategies"

    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Code and Title
    code = db.Column(db.String(20), nullable=True, index=True)  # e.g., ST1.1
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Meta Data
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Plan Year FK (Full Clone sistemi)
    plan_year_id = db.Column(db.Integer, db.ForeignKey("plan_years.id", ondelete="CASCADE"), nullable=True, index=True)
    source_sub_strategy_id = db.Column(db.Integer, db.ForeignKey("sub_strategies.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    strategy = db.relationship("Strategy", backref=db.backref("sub_strategies", lazy=True, cascade="all, delete-orphan", order_by="SubStrategy.code"))
    source_sub_strategy = db.relationship("SubStrategy", remote_side="SubStrategy.id", foreign_keys="SubStrategy.source_sub_strategy_id")

    def __repr__(self):
        return f"<SubStrategy {self.code or ''} - {self.title}>"


class Notification(db.Model):
    """Sistem Bildirimleri (PG sapma, görev vb.)."""

    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=True, index=True)

    # Kural 3: Alan adları İngilizce snake_case olmalı
    notification_type = db.Column(db.String(50), nullable=False)   # pg_performance_deviation, task_assigned vb.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=True)
    link = db.Column(db.String(500), nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False)

    process_id = db.Column(db.Integer, nullable=True)
    related_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", foreign_keys=[user_id], backref=db.backref("notifications", lazy=True))

