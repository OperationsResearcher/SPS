"""Application configuration loaded from .env via python-dotenv."""

import os
from datetime import timedelta
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
    # Driver normalizasyonu: URI'deki `+psycopg2` / çıplak `postgresql://` şeması,
    # o sürücünün kurulu OLMADIĞI ortamda ModuleNotFoundError → her DB sorgusu 500.
    # Sürücüyü sabitlemek yerine ortamda KURULU olanı tespit edip ona normalize et
    # (psycopg3 tercih; yoksa psycopg2). Yerel, demo (psycopg2), yeni container hepsi çalışır.
    import importlib.util
    if importlib.util.find_spec("psycopg") is not None:
        _driver = "psycopg"        # psycopg3
    elif importlib.util.find_spec("psycopg2") is not None:
        _driver = "psycopg2"
    else:
        _driver = "psycopg"        # hiçbiri yoksa psycopg3 varsay (anlamlı hata mesajı için)
    for _scheme in ("postgresql+psycopg2://", "postgresql+psycopg://", "postgresql://", "postgres://"):
        if raw.startswith(_scheme):
            raw = f"postgresql+{_driver}://" + raw[len(_scheme):]
            break
    return raw


def _apply_runtime_db_uri(config_obj) -> None:
    """Development / production config nesnesine geçerli PostgreSQL URI ata."""
    config_obj.SQLALCHEMY_DATABASE_URI = _require_postgres_uri()


class Config:
    """Base configuration class."""

    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable is not set!")

    # ── Demo Ortamı ─────────────────────────────────────────────────────────
    # KOKPITIM_DEMO_MODE=1 ise demo akışı (landing, rol-bazlı auto-login, banner)
    # aktiftir. PRODUCTION'da kapalı tutulmalıdır.
    KOKPITIM_DEMO_MODE = os.environ.get("KOKPITIM_DEMO_MODE", "0") == "1"
    # Demo session süresi (dk)
    DEMO_SESSION_MINUTES = int(os.environ.get("DEMO_SESSION_MINUTES", "60"))
    # Demo verisinin bulunduğu tenant adı (Tomofil)
    DEMO_TENANT_ID = int(os.environ.get("DEMO_TENANT_ID", "27"))
    # Demo inaktivite sıfırlama eşiği (dk) — bu süre boyunca heartbeat gelmezse
    # ve veri değişmişse Tomofil baseline'a geri yüklenir (KURALLAR §8.4)
    DEMO_INACTIVITY_MINUTES = int(os.environ.get("DEMO_INACTIVITY_MINUTES", "15"))

    # Araç/script geriye dönük uyumu: asıl uygulama get_config() ile doldurur.
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI") or ""

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── İş Kuralı Sabitleri ─────────────────────────────────────────────────────
    # Analitik ve raporlama geri bakış pencereleri (gün cinsinden)
    ANALYTICS_SHORT_LOOKBACK_DAYS  = int(os.environ.get("ANALYTICS_SHORT_LOOKBACK_DAYS",  "30"))
    ANALYTICS_MID_LOOKBACK_DAYS    = int(os.environ.get("ANALYTICS_MID_LOOKBACK_DAYS",    "90"))
    ANALYTICS_LONG_LOOKBACK_DAYS   = int(os.environ.get("ANALYTICS_LONG_LOOKBACK_DAYS",   "365"))
    # Performans eşikleri (0-100 skor skalaı)
    KPI_SCORE_CRITICAL_THRESHOLD   = int(os.environ.get("KPI_SCORE_CRITICAL_THRESHOLD",   "70"))
    KPI_SCORE_WARNING_THRESHOLD    = int(os.environ.get("KPI_SCORE_WARNING_THRESHOLD",    "90"))
    # Dışa aktarma limitleri
    MAX_EXPORT_RECORDS             = int(os.environ.get("MAX_EXPORT_RECORDS",            "1000"))

    # ── Sorgu Limitleri ─────────────────────────────────────────────────────────
    # Tek sorguda döndürülen maksimum satır sayısı (pagination olmayan listelerde)
    MAX_QUERY_ROWS = int(os.environ.get("MAX_QUERY_ROWS", "100"))
    # Bildirim listesi maksimum sayısı
    MAX_NOTIFICATION_ROWS = int(os.environ.get("MAX_NOTIFICATION_ROWS", "100"))
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    # Sprint 22: SameSite=Strict (CSRF güvenliği — payment-style strict)
    # Lax → Strict geçişi: cross-site form post engellenir, top-level GET izin verir
    SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "Strict")
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Strict"  # Sprint 22

    # Session süresi (varsayılan 24 saat)
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=int(os.environ.get("SESSION_LIFETIME_HOURS", "24")) * 3600
    )

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
    # Üretimde REDIS_URL tanımlıysa init_limiter otomatik Redis kullanır (memory:// yerine)
    RATELIMIT_STORAGE_URL = os.environ.get("RATELIMIT_STORAGE_URL", "memory://")
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = os.environ.get("RATELIMIT_DEFAULT", "300 per hour; 3000 per day")
    RATELIMIT_LOGIN = os.environ.get("RATELIMIT_LOGIN", "15 per minute; 100 per hour")
    HGS_BYPASS_ENABLED = os.environ.get('HGS_BYPASS_ENABLED', 'false').lower() == 'true'

    # Dalga A: legacy HTML yönlendirme middleware (GET → platform)
    LEGACY_SUNSET_ENABLED = os.environ.get("LEGACY_SUNSET_ENABLED", "true").lower() == "true"
    # Çift /process yüzeyi — micro/surec canonical; legacy process_bp kapalı
    LEGACY_PROCESS_BP_ENABLED = os.environ.get("LEGACY_PROCESS_BP_ENABLED", "false").lower() == "true"
    LEGACY_DASHBOARD_BP_ENABLED = os.environ.get("LEGACY_DASHBOARD_BP_ENABLED", "false").lower() == "true"

    # Error Tracking (Sentry - optional)
    SENTRY_DSN = os.environ.get("SENTRY_DSN")

    # File Upload
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
    # Admin yedek geri yükleme (zip/sql) — before_request ile sınırlı rotalarda uygulanır
    ADMIN_BACKUP_MAX_UPLOAD = int(os.environ.get("ADMIN_BACKUP_MAX_UPLOAD_MB", "512")) * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")

    # Cache Busting
    VERSION = "1.0.7"

    # Bakım modu — bakım: docs/YERELDEN_VM_YAYIN.md veya kod icinde maintenance_service
    MAINTENANCE_OVERRIDE_OFF = os.environ.get("MAINTENANCE_OVERRIDE_OFF", "").lower() in (
        "1",
        "true",
        "yes",
    )
    MAINTENANCE_ENV_FORCE = os.environ.get("MAINTENANCE_MODE", "").lower() in (
        "1",
        "true",
        "yes",
    )
    MAINTENANCE_BYPASS_SECRET = (os.environ.get("MAINTENANCE_BYPASS_SECRET") or "").strip() or None
    MAINTENANCE_DB_CACHE_TTL_SECONDS = float(
        os.environ.get("MAINTENANCE_DB_CACHE_TTL_SECONDS", "5")
    )

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
    RATELIMIT_ENABLED = False


class DevelopmentConfig(Config):
    """Development configuration."""
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Üretim profili (hazırlık scriptleri ve doğrudan kullanım için)."""
    DEBUG = False
    # Üretimde HGS bypass asla açılmaz (.env yanlış set edilse bile)
    HGS_BYPASS_ENABLED = False
    # CSP üretimde varsayılan olarak açık; CSP_ENABLED=false ile kapatılabilir
    CSP_ENABLED = os.environ.get("CSP_ENABLED", "true").lower() != "false"

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
    if env == "production":
        return ProductionConfig()
    cfg = Config()
    _apply_runtime_db_uri(cfg)
    return cfg
