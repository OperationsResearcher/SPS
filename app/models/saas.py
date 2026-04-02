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


class ModuleComponentSlug(db.Model):
    """Modül-Bileşen ilişkisi - bileşen = RouteRegistry.component_slug."""

    __tablename__ = "module_component_slugs"

    module_id = db.Column(db.Integer, db.ForeignKey("system_modules.id"), primary_key=True)
    component_slug = db.Column(db.String(128), primary_key=True)


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
