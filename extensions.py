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
# from flask_limiter import Limiter  # DEVRE DIŞI: Mock sınıf kullanılıyor
# from flask_limiter.util import get_remote_address  # DEVRE DIŞI
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

# --- RATE LIMITER IPTAL (Mock Sınıf) ---
# Flask-Limiter tamamen devre dışı, mock sınıf kullanılıyor
# Bu sayede @limiter.limit dekoratörleri hata vermeden çalışır ama hiçbir kısıtlama yapmaz
class FakeLimiter:
    def init_app(self, app):
        """init_app çağrısını boş geçir"""
        pass
    
    def limit(self, limit_value, *args, **kwargs):
        """limit dekoratörünü taklit et ama hiçbir şey yapma"""
        def decorator(f):
            return f
        return decorator

limiter = FakeLimiter()
# ----------------------------------------

# ESKİ KOD (YORUM SATIRI - İHTİYAÇ HALİNDE GERİ AÇILABİLİR):
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
# limiter = Limiter(
#     key_func=get_remote_address,
#     default_limits=["1000000 per second"],
#     storage_uri="memory://",
#     strategy="fixed-window",
#     enabled=False
# )

# Security Headers (Flask-Talisman)
# Note: Talisman will be initialized in __init__.py with app-specific config
talisman = Talisman()