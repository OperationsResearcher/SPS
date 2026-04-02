"""Application configuration loaded from .env via python-dotenv."""

import os
from dotenv import load_dotenv

load_dotenv()


def _require_postgres_uri() -> str:
    """Geliştirme ve üretim için yalnızca PostgreSQL URI kabul edilir."""
    raw = (os.environ.get("SQLALCHEMY_DATABASE_URI") or "").strip()
    if not raw:
        raise RuntimeError(
            "SQLALCHEMY_DATABASE_URI ortam değişkeni zorunludur (PostgreSQL). "
            "Örnek: postgresql+psycopg2://kullanici:sifre@host:5432/veritabani"
        )
    if raw.lower().lstrip().startswith("sqlite:"):
        raise RuntimeError(
            "SQLite artık geliştirme ve üretim için desteklenmiyor. "
            "SQLALCHEMY_DATABASE_URI değerini PostgreSQL olarak ayarlayın."
        )
    return raw


def _apply_runtime_db_uri(config_obj) -> None:
    """Development / production config nesnesine geçerli PostgreSQL URI ata."""
    config_obj.SQLALCHEMY_DATABASE_URI = _require_postgres_uri()


class Config:
    """Base configuration class."""

    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable is not set!")

    # Araç/script geriye dönük uyumu: asıl uygulama get_config() ile doldurur.
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI") or ""

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

    # PostgreSQL: kopuk bağlantı / sonsuz bekleme riskini azaltır (Cloudflare 524)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "connect_args": {"connect_timeout": 15},
    }

    # Rate Limiting (yüksek trafik/çoklu modal istekleri için geniş limitler)
    # REDIS_URL ile otomatik bağlama yok: konteynerde Redis yoksa limiter her istekte kilitlenir.
    RATELIMIT_STORAGE_URL = os.environ.get("RATELIMIT_STORAGE_URL", "memory://")
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = os.environ.get("RATELIMIT_DEFAULT", "50000 per hour; 1000000 per day")
    HGS_BYPASS_ENABLED = os.environ.get('HGS_BYPASS_ENABLED', 'false').lower() == 'true'

    # Error Tracking (Sentry - optional)
    SENTRY_DSN = os.environ.get("SENTRY_DSN")

    # File Upload
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
    # Admin yedek geri yükleme (zip/sql) — before_request ile sınırlı rotalarda uygulanır
    ADMIN_BACKUP_MAX_UPLOAD = int(os.environ.get("ADMIN_BACKUP_MAX_UPLOAD_MB", "512")) * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")

    # Cache Busting
    VERSION = "1.0.1"

    # Tek yapı: legacy URL öneki kaldırıldı.
    LEGACY_URL_PREFIX = "/"

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
    SQLALCHEMY_ENGINE_OPTIONS = {}
    WTF_CSRF_ENABLED = False


class DevelopmentConfig(Config):
    """Development configuration."""
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Üretim profili (hazırlık scriptleri ve doğrudan kullanım için)."""
    DEBUG = False

    def __init__(self):
        _apply_runtime_db_uri(self)


def get_config():
    """Return the appropriate config object based on FLASK_ENV."""
    env = (os.environ.get("FLASK_ENV") or "development").lower()
    if env == "testing":
        return TestingConfig()
    if env == "development":
        cfg = DevelopmentConfig()
        _apply_runtime_db_uri(cfg)
        return cfg
    cfg = Config()
    _apply_runtime_db_uri(cfg)
    return cfg
