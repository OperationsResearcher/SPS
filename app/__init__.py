"""Flask application factory."""

from datetime import datetime, timezone

from flask import Flask, jsonify, redirect, request
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

    # Klasik Kokpitim arayüzü öneki (varsayılan /kok). Micro kök "/".
    raw_legacy = (app.config.get("LEGACY_URL_PREFIX") or "/kok").strip() or "/kok"
    if not raw_legacy.startswith("/"):
        raw_legacy = "/" + raw_legacy
    legacy = raw_legacy.rstrip("/") or "/kok"
    app.config["LEGACY_URL_PREFIX"] = legacy

    csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize cache
    cache.init_app(app)

    # Initialize security utilities
    from app.utils.security import init_limiter, set_security_headers
    init_limiter(app)
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

    login_manager.init_app(app)
    # Giriş URL’si kökte /login (çubukta /kok yok); legacy /kok/login aynı view ile çalışmaya devam eder.
    login_manager.login_view = "public_login"
    login_manager.login_message = "Bu sayfayı görüntülemek için giriş yapmalısınız."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id)) if user_id else None

    @app.context_processor
    def inject_legacy_url_prefix():
        return {"legacy_url_prefix": app.config["LEGACY_URL_PREFIX"]}

    @app.route("/health")
    def global_health():
        """Yük dengeleyici / izleme — klasik /kok önekinin dışında kökte kalır."""
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

    # ── 1) Klasik auth (/kok/login vb.) + kök /login, /logout — micro'dan önce (micro'da /login yok)
    from app.routes.auth import auth_bp, login as auth_login_view, logout as auth_logout_view

    app.register_blueprint(auth_bp, url_prefix=legacy)
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

    # ── 2) Micro platform (kök "/")
    from micro import micro_bp

    app.register_blueprint(micro_bp)

    # Eski /micro/... yer imleri → yeni kök yollar
    @app.route("/micro", strict_slashes=False)
    @app.route("/micro/", strict_slashes=False)
    def _redirect_old_micro_root():
        dest = "/"
        if request.query_string:
            dest = dest + "?" + request.query_string.decode()
        return redirect(dest, code=302)

    @app.route("/micro/<path:subpath>")
    def _redirect_old_micro_subpath(subpath):
        dest = "/" + subpath.lstrip("/")
        if request.query_string:
            dest = dest + "?" + request.query_string.decode()
        return redirect(dest, code=302)

    # /isr → klasik arayüz (LEGACY_URL_PREFIX) alias
    @app.route("/isr", strict_slashes=False)
    @app.route("/isr/", strict_slashes=False)
    def _isr_to_legacy_root():
        dest = legacy + "/"
        if request.query_string:
            dest = dest + "?" + request.query_string.decode()
        return redirect(dest, code=302)

    @app.route("/isr/<path:subpath>")
    def _isr_to_legacy_path(subpath):
        dest = legacy + "/" + subpath.lstrip("/")
        if request.query_string:
            dest = dest + "?" + request.query_string.decode()
        return redirect(dest, code=302)

    # ── 3) Diğer klasik (legacy) blueprint'ler — LEGACY_URL_PREFIX altında
    from app.routes.admin import admin_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.hgs import hgs_bp
    from app.routes.strategy import strategy_bp
    from app.routes.process import process_bp
    from app.routes.core import core_bp

    from app.api.routes import api_bp as app_api_v1_bp
    from app.api.swagger import create_swagger_blueprint
    from app.api.push import push_bp
    from app.api.ai import ai_bp

    app.register_blueprint(hgs_bp, url_prefix=legacy)
    app.register_blueprint(dashboard_bp, url_prefix=legacy)
    app.register_blueprint(admin_bp, url_prefix=legacy + "/admin")
    app.register_blueprint(strategy_bp, url_prefix=legacy)
    app.register_blueprint(process_bp, url_prefix=legacy)
    app.register_blueprint(core_bp, url_prefix=legacy)

    app.register_blueprint(app_api_v1_bp, url_prefix=legacy)

    # Kokpitim proje REST (RAID, görevler, SLA API vb.) — `api/routes.py`; kök /api/... + legacy /kok/api/...
    from api.routes import api_bp as kokpitim_project_api_bp

    app.register_blueprint(kokpitim_project_api_bp, name="kokpitim_project_api")
    app.register_blueprint(
        kokpitim_project_api_bp,
        url_prefix=legacy + "/api",
        name="kokpitim_project_api_legacy",
    )

    app.register_blueprint(create_swagger_blueprint(legacy))
    app.register_blueprint(push_bp, url_prefix=legacy)
    app.register_blueprint(ai_bp, url_prefix=legacy)

    # Kök legacy: /projeler, süreç, strateji projeleri vb.
    from main.routes import main_bp as kokpitim_main_bp

    app.register_blueprint(kokpitim_main_bp, url_prefix=legacy)

    return app
