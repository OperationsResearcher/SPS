"""Application configuration loaded from .env via python-dotenv."""

import os
from dotenv import load_dotenv

load_dotenv()

# Flask CLI `app.py` → `kokpitim.app` importu göreli sqlite yolunu C:\\instance\\... yapabiliyor.
# Tek DB: proje köküne sabit mutlak yol (Flask import yolundan bağımsız).
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_SQLITE_FILE = os.path.join(_BASE_DIR, "instance", "kokpitim.db")
_DEFAULT_SQLITE_URI = "sqlite:///" + _DEFAULT_SQLITE_FILE.replace("\\", "/")


def _resolve_sqlalchemy_uri() -> str:
    """Göreli sqlite URI'yi proje köküne göre çözer; yalnızca dosya adı ise instance/ altına koyar."""
    raw = os.environ.get("SQLALCHEMY_DATABASE_URI", _DEFAULT_SQLITE_URI)
    if not raw.startswith("sqlite:///"):
        return raw
    rest = raw[len("sqlite:///") :]
    if rest.startswith(":memory:"):
        return raw
    if os.path.isabs(rest):
        return raw
    base_norm = os.path.normpath(_BASE_DIR)
    # sqlite:///kokpitim.db → instance/kokpitim.db
    if "/" not in rest and "\\" not in rest:
        abs_path = os.path.normpath(os.path.join(_BASE_DIR, "instance", rest))
    else:
        abs_path = os.path.normpath(os.path.join(_BASE_DIR, rest))
    if not abs_path.startswith(base_norm):
        return _DEFAULT_SQLITE_URI
    return "sqlite:///" + abs_path.replace("\\", "/")


class Config:
    """Base configuration class."""

    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable is not set!")
    SQLALCHEMY_DATABASE_URI = _resolve_sqlalchemy_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # Oturum boyunca geçerli
    
    # Cache Configuration
    CACHE_TYPE = os.environ.get("CACHE_TYPE", "SimpleCache")  # SimpleCache, RedisCache, FileSystemCache
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    CACHE_REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CACHE_KEY_PREFIX = "kokpitim_"
    
    # Rate Limiting (yüksek trafik/çoklu modal istekleri için geniş limitler)
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL", "memory://")
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = os.environ.get("RATELIMIT_DEFAULT", "50000 per hour; 1000000 per day")
    HGS_BYPASS_ENABLED = os.environ.get('HGS_BYPASS_ENABLED', 'false').lower() == 'true'
    
    # Error Tracking (Sentry - optional)
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    
    # File Upload
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")

    # Cache Busting
    VERSION = "1.0.1"

    # Klasik (kök) Kokpitim arayüzü — Micro artık "/" kökünde. Örn. /kok/dashboard
    LEGACY_URL_PREFIX = os.environ.get("LEGACY_URL_PREFIX", "/kok").strip() or "/kok"

    # E-posta (sistem varsayılan SMTP — kokpitim.com)
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "false").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_SENDER_NAME = os.environ.get("MAIL_SENDER_NAME", "Kokpitim")
    MAIL_SENDER_EMAIL = os.environ.get("MAIL_SENDER_EMAIL", "bildirim@kokpitim.com")


class TestingConfig(Config):
    """Test configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URI", "sqlite:///:memory:")
    WTF_CSRF_ENABLED = False


class DevelopmentConfig(Config):
    """Development configuration."""
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False


def get_config():
    """Return the appropriate config object based on FLASK_ENV."""
    env = os.environ.get("FLASK_ENV", "development")
    if env == "development":
        return DevelopmentConfig()
    if env == "testing":
        return TestingConfig()
    return Config()
