# -*- coding: utf-8 -*-
"""
Uygulama genelinde kullanılan Flask eklentilerini (extensions) merkezi olarak tanımlar.
Bu, dairesel bağımlılıkları (circular dependencies) önler ve uygulama fabrikası (app factory)
modelini destekler.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_caching import Cache

# Veritabanı ve migrasyon
db = SQLAlchemy()
migrate = Migrate()

# Cache
cache = Cache()

# Kullanıcı oturum yönetimi
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Bu sayfaya erişmek için giriş yapmalısınız.'
login_manager.login_message_category = 'info'
login_manager.session_protection = 'strong'

# CSRF koruması
csrf = CSRFProtect()

# Rate Limiting - Relaxed for development/testing
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10000/hour", "1000/minute"],  # Very high limits for development
    storage_uri="memory://",
    strategy="fixed-window"
)

# Security Headers (Flask-Talisman)
# Note: Talisman will be initialized in __init__.py with app-specific config
talisman = Talisman()