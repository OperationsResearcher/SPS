"""
Flask Extensions
Tüm Flask extension'ları burada initialize edilir
"""


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

# KOD-01 (Faz 2.1): csrf / login_manager / migrate / limiter / talisman da TEK kaynaktan —
# kök extensions.py. Eskiden burada ve app/__init__.py'de ayrı kopyalar vardı; kökteki
# `@csrf.exempt` decorator'ları init edilmemiş nesneye yazıldığı için 75 uçta etkisizdi.
from extensions import csrf, login_manager, migrate, limiter, talisman  # noqa: F401

# WebSocket — flask_socketio ağır bağımlılık zinciri (requests/ssl) tetikler; yalnızca init_socketio(app) ile yüklenir.
socketio = None


def _socketio_cors_origins():
    import os
    raw = (os.environ.get("SOCKETIO_CORS_ORIGINS") or "").strip()
    if not raw:
        return None
    return "*" if raw == "*" else [o.strip() for o in raw.split(",") if o.strip()]


def init_socketio(app):
    """Flask-SocketIO'yu uygulamaya bağlar; socketio olayları bu çağrıdan sonra import edilmelidir."""
    global socketio
    if socketio is not None:
        return socketio
    from flask_socketio import SocketIO

    socketio = SocketIO(
        app,
        # GUV-16: "*" yerine varsayılan aynı-origin. Ayrı origin gerekirse
        # SOCKETIO_CORS_ORIGINS="https://a.example,https://b.example" ("*" da verilebilir).
        cors_allowed_origins=_socketio_cors_origins(),
        async_mode="threading",
        logger=True,
        engineio_logger=False,
    )
    return socketio
