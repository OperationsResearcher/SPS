"""
Flask Extensions
Tüm Flask extension'ları burada initialize edilir
"""

from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_caching import Cache

# Database — tek kaynak: kök extensions.py (db.init_app app/__init__.py içinde)
from extensions import db  # noqa: F401

# Cache — tek kaynak: kök extensions.py (init_app app/__init__.py içinde).
#
# 2026-07-21: Burada AYRI bir `Cache()` nesnesi vardı ve `init_app` YALNIZ
# ona uygulanıyordu. Kök `extensions.cache`'i import eden 3 dosya
# (api/routes_ai.py, services/cache_service.py, services/strategic_impact_service.py)
# init edilmemiş bir nesneyle çalışıyor, `cache.get()` çağrısında
# `KeyError: <flask_caching.Cache object>` alıyordu → /api/dashboard/executive 500.
#
# db için zaten bu desen kurulmuştu (yukarıdaki satır); cache atlanmıştı.
# İki Cache nesnesi tutmak B2'deki "kopya ayrışması" hatasının aynısıydı.
from extensions import cache  # noqa: F401

migrate = Migrate()

# Authentication
login_manager = LoginManager()
login_manager.login_view = "public_login"
login_manager.login_message = 'Lütfen giriş yapın.'

# CSRF Protection
csrf = CSRFProtect()

# Rate Limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Caching — yukarıda kök extensions.py'den import edildi (tek nesne).

# Security Headers
talisman = Talisman()

# WebSocket — flask_socketio ağır bağımlılık zinciri (requests/ssl) tetikler; yalnızca init_socketio(app) ile yüklenir.
socketio = None


def init_socketio(app):
    """Flask-SocketIO'yu uygulamaya bağlar; socketio olayları bu çağrıdan sonra import edilmelidir."""
    global socketio
    if socketio is not None:
        return socketio
    from flask_socketio import SocketIO

    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode="threading",
        logger=True,
        engineio_logger=False,
    )
    return socketio
