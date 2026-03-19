"""Application configuration loaded from .env via python-dotenv."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class."""

    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable is not set!")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///kokpitim.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # Oturum boyunca geçerli
    
    # Cache Configuration
    CACHE_TYPE = os.environ.get("CACHE_TYPE", "SimpleCache")  # SimpleCache, RedisCache, FileSystemCache
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    CACHE_REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CACHE_KEY_PREFIX = "kokpitim_"
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL", "memory://")
    RATELIMIT_ENABLED = True
    
    # Error Tracking (Sentry - optional)
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    
    # File Upload
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")

    # Cache Busting
    VERSION = "1.0.1"

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


def get_config():
    """Return the appropriate config object based on FLASK_ENV."""
    env = os.environ.get("FLASK_ENV", "development")
    if env == "testing":
        return TestingConfig()
    return Config()
