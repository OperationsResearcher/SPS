"""SaaS hierarchy models: Package -> Module -> Component, RouteRegistry."""

from extensions import db


class RouteRegistry(db.Model):
    """Dinamik rota kaydı - Auto-Discovery bileşen eşleştirmesi."""

    __tablename__ = "route_registry"

    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(255), unique=True, nullable=False)
    url_rule = db.Column(db.String(512), nullable=False)
    methods = db.Column(db.String(128), nullable=True)  # Örn: GET, POST
    component_slug = db.Column(db.String(128), nullable=True)  # Kullanıcının atadığı bileşen ismi

    def __repr__(self):
        return f'<RouteRegistry {self.id} {(self.endpoint or "")[:30]}>'


# Ara tablolar (Many-to-Many)
package_modules = db.Table(
    "package_modules",
    db.Column("package_id", db.Integer, db.ForeignKey("subscription_packages.id"), primary_key=True),
    db.Column("module_id", db.Integer, db.ForeignKey("system_modules.id"), primary_key=True),
)


class SystemComponent(db.Model):
    """Sistem bileşeni — tenant paketinde yetkilendirme için slug (code)."""

    __tablename__ = "system_components"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(512), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f'<SystemComponent {self.id} {(self.code or "")[:20]}>'


class SystemPage(db.Model):
    """SAYFA — kartların bulunduğu ekran/sayfa (kart code prefix'i ile eşleşir).

    Örn: code='raporlar_cfo_dashboard', kartların code'u 'raporlar_cfo_dashboard.*'.
    short_id = modül-kısa kimlik (RP-CFO, MA, PR...). Admin sayfa başında görür;
    "hangi sayfada hangi kart var" envanteri + sorun bildiriminde sayfa referansı.
    """
    __tablename__ = "system_pages"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80), unique=True, nullable=False, index=True)  # kart code prefix
    name = db.Column(db.String(160), nullable=False)
    url = db.Column(db.String(255), nullable=True)
    short_id = db.Column(db.String(16), unique=True, nullable=True, index=True)
    description = db.Column(db.String(512), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f'<SystemPage {self.id} {(self.short_id or self.code or "")[:16]}>'


class SystemCard(db.Model):
    """KART — hiyerarşinin en alt katmanı (bileşen altındaki kart).

    Örn: 'KPI kartı', 'Performans Trend Analizi kartı'. Bir bileşene bağlı.
    Otomatik keşifle doldurulur, admin'den yer değiştirilir/düzenlenir.
    """
    __tablename__ = "system_cards"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(80), unique=True, nullable=False)
    # Kısa görünen kimlik (2 harf sayfa kısaltması + numara, örn. MA01).
    # Uzun `code` iç anahtardır; short_id kullanıcıya/admin'e gösterilen etikettir.
    short_id = db.Column(db.String(12), unique=True, nullable=True, index=True)
    component_id = db.Column(
        db.Integer, db.ForeignKey("system_components.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    sira = db.Column(db.Integer, default=0)  # yer değiştirme (gösterim sırası)
    # Text: zenginleştirilmiş kart açıklamaları 512 karaktere sığmıyor (hesap
    # yöntemi + yorum + sınır + literatür dayanağı bölümleri). PostgreSQL'de
    # Text ile varchar arasında performans farkı yoktur.
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    data_sources = db.relationship(
        "CardDataSource", backref="card", lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f'<SystemCard {self.id} {(self.code or "")[:24]}>'


class CardDataSource(db.Model):
    """KART-İÇİ VERİ → PAKET eşlemesi (çapraz-paket veri farkındalığı).

    Bir kartın içindeki her veri parçası (data_key), hangi bileşene/pakete tabi
    olduğunu (required_component_code) taşır. Kullanıcının paketinde o bileşen
    yoksa o veri parçası karttan DÜŞER (kart kalır, kısmi gösterilir).
    """
    __tablename__ = "card_data_sources"

    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(
        db.Integer, db.ForeignKey("system_cards.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    data_key = db.Column(db.String(120), nullable=False)   # örn "pgv_kapsami"
    # Bu verinin gerektirdiği bileşen kodu (system_components.code).
    # NULL = kartın kendi bileşenine tabi (ek kısıt yok).
    required_component_code = db.Column(db.String(80), nullable=True, index=True)
    label = db.Column(db.String(200), nullable=True)        # UI'da görünen ad
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("card_id", "data_key", name="uq_card_data_key"),
    )

    def __repr__(self):
        return f'<CardDataSource card={self.card_id} {self.data_key[:20]}>'


class SystemModule(db.Model):
    """System module - bileşenler = RouteRegistry.component_slug (Bileşenler sekmesindeki Bileşen İsmi)."""

    __tablename__ = "system_modules"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(512), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Bileşen = Bileşen İsmi (component_slug) - Bileşenler sekmesinden
    component_slugs = db.relationship(
        "ModuleComponentSlug",
        backref="module",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f'<SystemModule {self.id} {(self.code or "")[:20]}>'


class ModuleComponentSlug(db.Model):
    """Modül-Bileşen ilişkisi - bileşen = RouteRegistry.component_slug."""

    __tablename__ = "module_component_slugs"

    module_id = db.Column(db.Integer, db.ForeignKey("system_modules.id"), primary_key=True)
    component_slug = db.Column(db.String(128), primary_key=True)

    def __repr__(self):
        return f'<ModuleComponentSlug module={self.module_id} slug={self.component_slug[:20]}>'


class SubscriptionPackage(db.Model):
    """Subscription package containing modules."""

    __tablename__ = "subscription_packages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(512), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    modules = db.relationship(
        "SystemModule",
        secondary=package_modules,
        backref=db.backref("packages", lazy="dynamic"),
        lazy="dynamic",
    )
    tenants = db.relationship("Tenant", back_populates="package")

    def __repr__(self):
        return f'<SubscriptionPackage {self.id} {(self.name or "")[:20]}>'
