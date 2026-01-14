# -*- coding: utf-8 -*-
"""
Konfigürasyon Yönetimi
Environment variables kullanarak güvenli konfigürasyon yönetimi
"""
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Temel konfigürasyon sınıfı"""
    
    # Flask ayarları
    _secret_key = os.environ.get('SECRET_KEY')
    if not _secret_key:
        env = os.environ.get('FLASK_ENV', 'development')
        if env == 'production':
            raise ValueError("❌ PRODUCTION ERROR: SECRET_KEY environment variable MUST be set!")
        import warnings
        warnings.warn("⚠️ WARNING: SECRET_KEY not set. Using development fallback - NOT SAFE FOR PRODUCTION!", UserWarning)
        _secret_key = 'dev-secret-key-change-in-production-' + str(os.urandom(16).hex())
    SECRET_KEY = _secret_key
    
    # Veritabanı - SQLite (Migration sonrası)
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "spsv2.db")}'
    
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'echo': False
    }
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session ayarları
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Dosya yükleme
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads', 'logos')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}
    
    # Cache ayarları
    SEND_FILE_MAX_AGE_DEFAULT = 0
    TEMPLATES_AUTO_RELOAD = True
    
    # Flask-Caching configuration
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL', 'redis://localhost:6379/0')
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'True').lower() == 'true'
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    
    # Logging
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    LOG_FILE = os.path.join(basedir, 'logs', 'stratejik_planlama.log')
    LOG_MAX_BYTES = 10240000
    LOG_BACKUP_COUNT = 10


class DevelopmentConfig(Config):
    """Development konfigürasyonu"""
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0


class ProductionConfig(Config):
    """Production konfigürasyonu"""
    DEBUG = False
    TESTING = False
    TEMPLATES_AUTO_RELOAD = False
    SEND_FILE_MAX_AGE_DEFAULT = 31536000
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_ENABLED = True


class TestingConfig(Config):
    """Testing konfigürasyonu"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Environment'a göre konfigürasyon döndür"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
