"""Flask application factory."""

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate

from app.extensions import csrf, cache
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
        from config import Config

        config_class = Config

    app.config.from_object(config_class)

    csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize cache
    cache.init_app(app)
    
    # Initialize security utilities
    from app.utils.security import init_limiter, set_security_headers
    init_limiter(app)
    
    # Initialize error tracking
    from app.utils.error_tracking import setup_logging, init_sentry
    setup_logging(app)
    init_sentry(app)
    
    # Add security headers to all responses
    @app.after_request
    def add_security_headers(response):
        return set_security_headers(response)



    login_manager.init_app(app)
    login_manager.login_view = "auth_bp.login"
    login_manager.login_message = "Bu sayfayı görüntülemek için giriş yapmalısınız."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id)) if user_id else None

    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.hgs import hgs_bp
    from app.routes.strategy import strategy_bp
    from app.routes.process import process_bp
    from app.routes.core import core_bp
    
    # API Blueprints
    from app.api.routes import api_bp
    from app.api.swagger import swaggerui_blueprint
    from app.api.push import push_bp
    from app.api.ai import ai_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(hgs_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(strategy_bp)
    app.register_blueprint(process_bp)
    app.register_blueprint(core_bp)
    
    # Register API blueprints (Sprint 13-21)
    app.register_blueprint(api_bp)
    app.register_blueprint(swaggerui_blueprint)
    app.register_blueprint(push_bp)
    app.register_blueprint(ai_bp)

    # Micro platform (yeni modüler arayüz — /micro)
    from micro import micro_bp
    app.register_blueprint(micro_bp)

    return app
