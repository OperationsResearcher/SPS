"""
Flask Extensions
Tüm Flask extension'ları burada initialize edilir
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_caching import Cache

# Database
db = SQLAlchemy()
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

# Caching
cache = Cache()

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
