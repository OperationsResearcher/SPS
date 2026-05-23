"""Flask application factory."""

from datetime import datetime, timezone

from flask import Flask, jsonify
from sqlalchemy import text
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_talisman import Talisman

from app.extensions import csrf, cache, talisman
from app.models import db
from app.models.core import User

migrate = Migrate()
login_manager = LoginManager()


def create_app(config_class=None):
    """Create and configure the Flask application instance."""
    import os

    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask(
        __name__,
        template_folder=os.path.join(root_dir, "templates"),
        static_folder=os.path.join(root_dir, "static"),
    )

    if config_class is None:
        from config import get_config

        # Ortama göre doğru config'i seç (development/test/prod)
        config_class = get_config()

    app.config.from_object(config_class)

    # Tek yapı: legacy prefix kaldırıldı, kök URL kullanılır.
    app.config["LEGACY_URL_PREFIX"] = "/"

    # Cloudflare / ters vekil: X-Forwarded-Proto ve Host okunsun; aksi halde is_secure ve yönlendirmeler hatalı.
    _env = (os.environ.get("FLASK_ENV") or "").lower()
    _trust = (os.environ.get("TRUST_PROXY") or "").lower()
    if _env == "production" or _trust in ("1", "true", "yes"):
        from werkzeug.middleware.proxy_fix import ProxyFix

        app.wsgi_app = ProxyFix(
            app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1
        )

    csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from app.utils.maintenance_middleware import register_maintenance_middleware

    register_maintenance_middleware(app)

    # Initialize cache
    cache.init_app(app)

    # Initialize security utilities
    from app.utils.security import init_limiter, set_security_headers
    init_limiter(app)

    _flask_env = (os.environ.get("FLASK_ENV") or "").lower()
    if _flask_env == "production":
        talisman.init_app(
            app,
            force_https=False,
            content_security_policy={
                "default-src": "'self'",
                "script-src": (
                    "'self' 'unsafe-inline' 'unsafe-eval' "
                    "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com"
                ),
                "style-src": (
                    "'self' 'unsafe-inline' "
                    "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com"
                ),
                "font-src": (
                    "'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.gstatic.com"
                ),
                "img-src": "'self' data: https: blob:",
                "connect-src": (
                    "'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com"
                ),
                "frame-ancestors": "'none'",
                "base-uri": "'self'",
                "form-action": "'self'",
            },
            frame_options="DENY",
            referrer_policy="strict-origin-when-cross-origin",
        )
    else:
        talisman.init_app(
            app,
            force_https=False,
            content_security_policy=False,
        )

    # Initialize error tracking
    from app.utils.error_tracking import setup_logging, init_sentry
    setup_logging(app)
    init_sentry(app)

    # Add security headers to all responses
    @app.after_request
    def add_security_headers(response):
        return set_security_headers(response)

    # Register Centralized Error Handlers (Zero Defect Architecture)
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)

    login_manager.init_app(app)
    # Giriş URL'si kökte /login.
    login_manager.login_view = "public_login"
    login_manager.login_message = "Bu sayfayı görüntülemek için giriş yapmalısınız."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id)) if user_id else None

    from app.utils.safe_urls import safe_url_for

    @app.context_processor
    def _inject_safe_url_for():
        return {"safe_url_for": safe_url_for}

    @app.route("/health")
    def global_health():
        """Yük dengeleyici / izleme endpoint'i."""
        db_ok = True
        try:
            db.session.execute(text("SELECT 1"))
        except Exception:
            db_ok = False
        body = {
            "status": "healthy" if db_ok else "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": app.config.get("VERSION", "1.0.1"),
            "checks": {"database": "ok" if db_ok else "error"},
        }
        return jsonify(body), 200 if db_ok else 503

    # ── 1) Auth
    from app.routes.auth import auth_bp, login as auth_login_view, logout as auth_logout_view

    app.register_blueprint(auth_bp, url_prefix="")
    app.add_url_rule(
        "/login",
        endpoint="public_login",
        view_func=auth_login_view,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/logout",
        endpoint="public_logout",
        view_func=auth_logout_view,
        methods=["GET"],
    )

    # ── 1.5) Marketing (tanıtım sitesi) — app_bp'den önce register edilmeli
    from micro.modules.marketing import marketing_bp
    import micro.modules.marketing.routes  # noqa: F401
    app.register_blueprint(marketing_bp)

    # ── 2) Platform (kök "/")
    from platform_core import app_bp

    app.register_blueprint(app_bp)

    # ── 3) Uygulama blueprint'leri (tek yapı)
    from app.routes.admin import admin_bp
    # Sprint 9: app.routes.dashboard kaldırıldı — fonksiyonlar micro/masaustu + micro/kurum'a taşındı
    from app.routes.hgs import hgs_bp
    from app.routes.strategy import strategy_bp
    from app.routes.process import process_bp
    from app.routes.core import core_bp

    from app.api.routes import api_bp as app_api_v1_bp
    from app.api.swagger import create_swagger_blueprint
    from app.api.push import push_bp
    from app.api.ai import ai_bp

    app.register_blueprint(hgs_bp, url_prefix="")
    # Sprint 9: LEGACY_DASHBOARD_BP_ENABLED kaldırıldı (dashboard.py silindi)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(strategy_bp, url_prefix="")
    if app.config.get("LEGACY_PROCESS_BP_ENABLED"):
        app.register_blueprint(process_bp, url_prefix="")
    app.register_blueprint(core_bp, url_prefix="")

    app.register_blueprint(app_api_v1_bp, url_prefix="")

    # Kokpitim proje REST (RAID, görevler, SLA API vb.) — `api/routes.py`
    from api.routes import api_bp as kokpitim_project_api_bp
    
    # Process Modern API (Zero Defect Architecture)
    from app.api.process.performance_routes import process_performance_bp

    app.register_blueprint(kokpitim_project_api_bp, name="kokpitim_project_api")
    app.register_blueprint(process_performance_bp, name="process_performance_api")

    app.register_blueprint(create_swagger_blueprint(""))
    app.register_blueprint(push_bp, url_prefix="")
    app.register_blueprint(ai_bp, url_prefix="")

    # Admin backup scheduler (daily/weekly, persisted in instance/backup_schedule.json)
    if not app.testing:
        from services.backup_scheduler_service import init_backup_scheduler
        init_backup_scheduler(app)
        from services.k_radar_scheduler_service import init_k_radar_scheduler
        init_k_radar_scheduler(app)
        _init_early_warning_scheduler(app)

    # Legacy HTML sunset (GET yönlendirme / 410) — main_bp'den önce kayıt
    from app.middleware.legacy_sunset import init_legacy_sunset

    init_legacy_sunset(app)

    # Kök yollar: /projeler, süreç API vb. (HTML sayfaları middleware ile platforma gider)
    from main.routes import main_bp as kokpitim_main_bp

    app.register_blueprint(kokpitim_main_bp, url_prefix="")

    from app.extensions import init_socketio

    init_socketio(app)
    # "import app.socketio_events" kullanma: fonksiyon içinde `app` adı paket modülü ile gölgelenir;
    # return app yanlışlıkla WSGI yerine modül döner (AttributeError: module has no attribute run).
    import importlib

    importlib.import_module("app.socketio_events")

    return app


def _init_early_warning_scheduler(app) -> None:
    """Erken uyarı servisini her gece 02:00'de çalıştırır."""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        from services.early_warning_service import run_early_warning

        scheduler = BackgroundScheduler(daemon=True, timezone="Europe/Istanbul")
        scheduler.add_job(
            func=run_early_warning,
            args=[app],
            trigger=CronTrigger(hour=2, minute=0),
            id="early_warning_nightly",
            replace_existing=True,
        )
        scheduler.start()
        app.logger.info("[early_warning] Zamanlayıcı başlatıldı (her gece 02:00).")
    except ImportError:
        app.logger.warning("[early_warning] apscheduler kurulu değil, zamanlayıcı atlandı.")

    return app
