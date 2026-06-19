"""Flask application factory."""

from datetime import datetime, timezone

from flask import Flask, jsonify
from sqlalchemy import text
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_talisman import Talisman

from app.extensions import csrf, cache, talisman
from app.models import db
from app.models.core import User

migrate = Migrate()
login_manager = LoginManager()


def create_app(config_class=None):
    """Create and configure the Flask application instance."""
    import os

    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask(
        __name__,
        template_folder=os.path.join(root_dir, "templates"),
        static_folder=os.path.join(root_dir, "static"),
    )

    if config_class is None:
        from config import get_config

        # Ortama göre doğru config'i seç (development/test/prod)
        config_class = get_config()

    app.config.from_object(config_class)

    # Tek yapı: legacy prefix kaldırıldı, kök URL kullanılır.
    app.config["LEGACY_URL_PREFIX"] = "/"

    # Cloudflare / ters vekil: X-Forwarded-Proto ve Host okunsun; aksi halde is_secure ve yönlendirmeler hatalı.
    _env = (os.environ.get("FLASK_ENV") or "").lower()
    _trust = (os.environ.get("TRUST_PROXY") or "").lower()
    if _env == "production" and _trust not in ("0", "false", "no"):
        from werkzeug.middleware.proxy_fix import ProxyFix

        app.wsgi_app = ProxyFix(
            app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1
        )

    csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from app.utils.maintenance_middleware import register_maintenance_middleware

    register_maintenance_middleware(app)

    # Initialize cache
    cache.init_app(app)

    # Initialize security utilities
    from app.utils.security import init_limiter, set_security_headers
    init_limiter(app)

    _flask_env = (os.environ.get("FLASK_ENV") or "").lower()
    _csp_enabled = app.config.get(
        "CSP_ENABLED", os.environ.get("CSP_ENABLED", str(_flask_env == "production")).lower() == "true"
    )
    if _csp_enabled:
        talisman.init_app(
            app,
            force_https=False,
            content_security_policy={
                "default-src": "'self'",
                "script-src": (
                    "'self' 'unsafe-inline' 'unsafe-eval' "
                    "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com "
                    "https://cdn.tailwindcss.com"
                ),
                "style-src": (
                    "'self' 'unsafe-inline' "
                    "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com"
                ),
                "font-src": (
                    "'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.gstatic.com"
                ),
                "img-src": "'self' data: https: blob:",
                "connect-src": (
                    "'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com "
                    "https://cdn.tailwindcss.com"
                ),
                "frame-ancestors": "'none'",
                "base-uri": "'self'",
                "form-action": "'self'",
            },
            frame_options="DENY",
            referrer_policy="strict-origin-when-cross-origin",
        )
    else:
        talisman.init_app(
            app,
            force_https=False,
            content_security_policy=False,
        )

    # Initialize error tracking
    from app.utils.error_tracking import setup_logging, init_sentry
    setup_logging(app)
    init_sentry(app)

    # Add security headers to all responses
    @app.after_request
    def add_security_headers(response):
        return set_security_headers(response)

    # Register Centralized Error Handlers (Zero Defect Architecture)
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)

    login_manager.init_app(app)
    # Giriş URL'si kökte /login.
    login_manager.login_view = "public_login"
    login_manager.login_message = "Bu sayfayı görüntülemek için giriş yapmalısınız."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id)) if user_id else None

    from app.utils.safe_urls import safe_url_for

    @app.context_processor
    def _inject_safe_url_for():
        return {"safe_url_for": safe_url_for}

    @app.context_processor
    def _inject_role_labels():
        """Kanonik rol etiketleri — tek kaynak (app.constants.roles).

        Template: {{ role_label_tr(user.role.name) }}
        JS gömme: {{ ROLE_LABELS_TR | tojson }}
        """
        from app.constants.roles import role_label_tr, ROLE_LABELS_TR
        return {"role_label_tr": role_label_tr, "ROLE_LABELS_TR": ROLE_LABELS_TR}

    # K-Radar hub'ındaki kart URL'lerinin grup eşlemesi (breadcrumb için)
    _KRADAR_GROUPS = {
        "performans": "📊 Performans",
        "yurutme": "🚀 Yürütme",
        "risk": "🛡 Risk & Veri",
        "strateji": "🎯 Strateji",
        "ai": "🤖 AI & Üst Yönetim",
    }
    # (path, tab) → group_key
    _KRADAR_URL_TO_GROUP = {
        # Performans
        ("/k-rapor", "kurumsal"): "performans",
        ("/k-rapor", "surec-pg"): "performans",
        ("/k-rapor", "pg-dagilim"): "performans",
        ("/k-rapor", "k-vektor"): "performans",
        ("/k-rapor", "uyum"): "performans",
        ("/k-rapor", "strateji-kapsama"): "performans",
        ("/raporlar/k-vektor-carpiklik", None): "performans",
        ("/raporlar/hizalama-sankey", None): "performans",
        ("/sp/strateji-proje-matris", None): "performans",
        ("/raporlar/pg-proje-etki", None): "performans",
        ("/raporlar/departman-performans", None): "performans",
        ("/raporlar/yonetici-liderlik", None): "performans",
        ("/raporlar/cmmi-heatmap", None): "performans",
        ("/raporlar/hedef-revizyon", None): "performans",
        ("/k-radar/ks", None): "performans",
        # Yürütme
        ("/k-rapor", "faaliyet"): "yurutme",
        ("/k-rapor", "faaliyet-matris"): "yurutme",
        ("/k-rapor", "aktivite-takvim"): "yurutme",
        ("/k-rapor", "sorumlu-analiz"): "yurutme",
        ("/k-rapor", "bireysel"): "yurutme",
        ("/k-rapor", "evm"): "yurutme",
        ("/raporlar/bireysel-hizalama", None): "yurutme",
        ("/raporlar/initiative-bubble", None): "yurutme",
        ("/raporlar/initiative-roadmap", None): "yurutme",
        ("/raporlar/quarterly-review", None): "yurutme",
        ("/raporlar/okr-cascade", None): "yurutme",
        ("/raporlar/sabah-ozeti", None): "yurutme",
        ("/raporlar/operasyon-istatistik", None): "yurutme",
        ("/raporlar/muda-analizi", None): "yurutme",
        # Risk & Veri
        ("/k-rapor", "risk"): "risk",
        ("/k-rapor", "uyari"): "risk",
        ("/k-rapor", "veri-durumu"): "risk",
        ("/k-rapor", "denetim"): "risk",
        ("/k-rapor", "bildirim-analiz"): "risk",
        ("/raporlar/risk-heatmap", None): "risk",
        ("/raporlar/early-warning", None): "risk",
        ("/raporlar/ml-anomaly", None): "risk",
        ("/raporlar/veri-kalitesi", None): "risk",
        ("/raporlar/iki-fa", None): "risk",
        ("/raporlar/audit-paketi", None): "risk",
        ("/raporlar/onay-zinciri", None): "risk",
        # Strateji
        ("/k-rapor", "stratejik-analiz"): "strateji",
        ("/k-rapor", "swot-trend"): "strateji",
        ("/k-rapor", "paydas"): "strateji",
        ("/k-rapor", "rekabet"): "strateji",
        ("/k-rapor", "kurum-karsilastirma"): "strateji",
        ("/raporlar/vrio-portfoy", None): "strateji",
        ("/raporlar/sektor-benchmark", None): "ai",
        ("/raporlar/sektorel", None): "strateji",
        ("/raporlar/sunburst", None): "strateji",
        ("/sp/strateji-haritasi", None): "strateji",
        ("/raporlar/evrim-filmi", None): "strateji",
        ("/raporlar/strateji-hikayesi", None): "strateji",
        # AI & Üst Yönetim
        ("/raporlar/cfo-dashboard", None): "ai",
        ("/raporlar/coo-dashboard", None): "ai",
        ("/raporlar/chro-dashboard", None): "ai",
        ("/raporlar/yatirimci-sunum", None): "ai",
        ("/raporlar/stratejik-yillik", None): "ai",
        ("/raporlar/esg-rapor", None): "ai",
        ("/raporlar/carbon-trend", None): "ai",
        ("/raporlar/ai-danisman", None): "ai",
        ("/raporlar/ai-coach", None): "ai",
        ("/raporlar/ai-sunum", None): "ai",
        ("/raporlar/nlp-query", None): "ai",
        ("/raporlar/bireysel-karne-batch", None): "ai",
        ("/raporlar/mobile", None): "ai",
        ("/raporlar/bi-connector", None): "ai",
    }

    @app.context_processor
    def _inject_kradar_subgroup():
        """K-Radar alt sayfalarında bağlı oldukları grubu döner (breadcrumb için)."""
        from flask import request
        try:
            path = request.path
            tab = request.args.get("tab")
        except Exception:
            return {"current_subgroup": None}
        key = (path, tab) if tab else (path, None)
        group_key = _KRADAR_URL_TO_GROUP.get(key)
        if not group_key:
            return {"current_subgroup": None}
        return {"current_subgroup": {
            "label": _KRADAR_GROUPS.get(group_key, group_key),
            "url": "/k-radar?g=" + group_key,
            "key": group_key,
        }}

    @app.context_processor
    def _inject_current_section():
        """Geçerli URL'den sidebar bölümünü çöz — breadcrumb için."""
        from flask import request
        # Path → (etiket, url) eşlemesi. Önek eşleşmesi sıralı; ilk eşleşen kazanır.
        # Sıra: daha uzun/spesifik önek önce.
        sections = [
            ("/masaustu-launcher", "Masaüstü", "/masaustu-launcher"),
            ("/masaustu",          "Masaüstü", "/masaustu-launcher"),
            ("/sp",                "Stratejik Planlama", "/sp"),
            ("/process",           "Süreç Yönetimi", "/process"),
            ("/proje",             "Proje Yönetimi", "/project"),
            ("/project",           "Proje Yönetimi", "/project"),
            ("/k-radar",           "K-Radar", "/k-radar"),
            ("/k-analiz",          "K-Radar", "/k-radar"),
            ("/k-rapor",           "K-Radar", "/k-radar"),
            ("/raporlar",          "K-Radar", "/k-radar"),
            ("/bireysel",          "Bireysel Performans", "/bireysel/karne"),
            ("/analiz",            "Performans Analitiği", "/analiz"),
            ("/bildirim",          "Bildirimler", "/bildirim"),
            ("/ayarlar",           "Ayarlar", "/ayarlar"),
            ("/kurum",             "Kurum", "/kurum"),
            ("/admin",             "Yönetim Paneli", "/admin/yonetim-paneli"),
            ("/yonetim",           "Yönetim Paneli", "/admin/yonetim-paneli"),
            ("/profil",            "Profil", "/profil"),
        ]
        try:
            path = request.path
        except Exception:
            return {"current_section": None}
        for prefix, label, url in sections:
            if path == prefix or path.startswith(prefix + "/") or path.startswith(prefix + "?"):
                return {"current_section": {"label": label, "url": url, "prefix": prefix, "is_root": (path == prefix or path == url)}}
        return {"current_section": None}

    @app.route("/health")
    def global_health():
        """Yük dengeleyici / izleme endpoint'i."""
        db_ok = True
        try:
            db.session.execute(text("SELECT 1"))
        except Exception:
            db_ok = False
        body = {
            "status": "healthy" if db_ok else "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": app.config.get("VERSION", "1.0.1"),
            "checks": {"database": "ok" if db_ok else "error"},
        }
        return jsonify(body), 200 if db_ok else 503

    # ── 1) Auth
    from app.routes.auth import auth_bp, login as auth_login_view, logout as auth_logout_view

    app.register_blueprint(auth_bp, url_prefix="")
    app.add_url_rule(
        "/login",
        endpoint="public_login",
        view_func=auth_login_view,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/logout",
        endpoint="public_logout",
        view_func=auth_logout_view,
        methods=["GET"],
    )

    # ── 1.5) Marketing (tanıtım sitesi) — app_bp'den önce register edilmeli
    from micro.modules.marketing import marketing_bp
    import micro.modules.marketing.routes  # noqa: F401
    app.register_blueprint(marketing_bp)

    # ── 2) Platform (kök "/")
    from platform_core import app_bp

    app.register_blueprint(app_bp)

    # ── 3) Uygulama blueprint'leri (tek yapı)
    from app.routes.admin import admin_bp
    # Sprint 9: app.routes.dashboard kaldırıldı — fonksiyonlar micro/masaustu + micro/kurum'a taşındı
    # HGS (Hızlı Giriş) tamamen kaldırıldı (2026-06-16)
    # Sprint 25: SSO blueprint
    from app.routes.sso import sso_bp
    # Sprint 26: 2FA TOTP blueprint
    from app.routes.totp import totp_bp
    # Sprint 52: strategy_bp silindi — micro/sp canonical (safe_urls.py mapping mevcut)
    # Sprint 29-30: process_bp lazy import — sadece LEGACY_PROCESS_BP_ENABLED ise yüklenir
    # (1.805 satır legacy kod; mikro/surec canonical)
    from app.routes.core import core_bp

    from app.api.routes import api_bp as app_api_v1_bp
    from app.api.swagger import create_swagger_blueprint
    from app.api.push import push_bp
    from app.api.ai import ai_bp

    # Sprint 9: LEGACY_DASHBOARD_BP_ENABLED kaldırıldı (dashboard.py silindi)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    # Sprint 25: SSO blueprint kaydı
    app.register_blueprint(sso_bp)
    # Sprint 26: 2FA TOTP blueprint kaydı
    app.register_blueprint(totp_bp)
    # Sprint 48: Data connector (Power BI / Tableau JSON API)
    from app.api.data_connector import dataconn_bp, register_token_endpoint
    app.register_blueprint(dataconn_bp)
    register_token_endpoint(app)

    # Sprint 28: i18n (Flask-Babel) — opsiyonel, kurulu değilse atlar
    try:
        from app.i18n import init_babel
        init_babel(app)
    except Exception as _i18n_err:
        app.logger.warning(f"[i18n] Atlandı: {_i18n_err}")
    # Sprint 52: strategy_bp register kaldırıldı (safe_url_for ile micro/sp'ye yönlendir)
    if app.config.get("LEGACY_PROCESS_BP_ENABLED"):
        # Sprint 29-30: legacy bp lazy load — sadece flag açıksa import edilir
        from app.routes.process import process_bp
        app.register_blueprint(process_bp, url_prefix="")
    app.register_blueprint(core_bp, url_prefix="")

    app.register_blueprint(app_api_v1_bp, url_prefix="")

    # Kokpitim proje REST (RAID, görevler, SLA API vb.) — `api/routes.py`
    from api.routes import api_bp as kokpitim_project_api_bp
    
    # Process Modern API (Zero Defect Architecture)
    from app.api.process.performance_routes import process_performance_bp

    app.register_blueprint(kokpitim_project_api_bp, name="kokpitim_project_api")
    app.register_blueprint(process_performance_bp, name="process_performance_api")

    app.register_blueprint(create_swagger_blueprint(""))
    app.register_blueprint(push_bp, url_prefix="")
    app.register_blueprint(ai_bp, url_prefix="")

    if not app.testing:
        from services.k_radar_scheduler_service import init_k_radar_scheduler
        init_k_radar_scheduler(app)
        _init_early_warning_scheduler(app)
        _init_weekly_digest_scheduler(app)  # Sprint 18
        _init_yedekleme_scheduler(app)
        if app.config.get("KOKPITIM_DEMO_MODE"):
            _init_demo_inactivity_sweeper(app)  # KURALLAR §8.4 — demo Tomofil sıfırlama

    # Legacy HTML sunset (GET yönlendirme / 410) — main_bp'den önce kayıt
    from app.middleware.legacy_sunset import init_legacy_sunset

    init_legacy_sunset(app)

    # Kök yollar: /projeler, süreç API vb. (HTML sayfaları middleware ile platforma gider)
    from main.routes import main_bp as kokpitim_main_bp

    app.register_blueprint(kokpitim_main_bp, url_prefix="")

    from app.extensions import init_socketio

    init_socketio(app)
    # "import app.socketio_events" kullanma: fonksiyon içinde `app` adı paket modülü ile gölgelenir;
    # return app yanlışlıkla WSGI yerine modül döner (AttributeError: module has no attribute run).
    import importlib

    importlib.import_module("app.socketio_events")

    return app


def _init_weekly_digest_scheduler(app) -> None:
    """Haftalık digest mail — her Pazartesi 09:00 (Europe/Istanbul)."""
    if not app.config.get("DIGEST_SCHEDULER_ENABLED", False):
        app.logger.info("[digest_scheduler] DIGEST_SCHEDULER_ENABLED=False — atlandı")
        return
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger

        def _run():
            with app.app_context():
                from app.services.email_digest_service import schedule_digest_for_all_tenants
                schedule_digest_for_all_tenants()

        scheduler = BackgroundScheduler(daemon=True, timezone="Europe/Istanbul")
        scheduler.add_job(
            func=_run,
            trigger=CronTrigger(day_of_week="mon", hour=9, minute=0),
            id="weekly_digest_monday",
            replace_existing=True,
        )
        scheduler.start()
        app.logger.info("[digest_scheduler] Haftalık digest — her Pazartesi 09:00 başlatıldı.")
    except ImportError:
        app.logger.warning("[digest_scheduler] apscheduler kurulu değil.")
    except Exception as e:
        app.logger.error(f"[digest_scheduler] Başlatma hatası: {e}")


def _init_yedekleme_scheduler(app) -> None:
    """Otomatik yedek (tam DB + kod fark) her gece 02:00'de çalışır."""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        from app.services.yedekleme_service import run_auto_backup

        scheduler = BackgroundScheduler(daemon=True, timezone="Europe/Istanbul")
        scheduler.add_job(
            func=run_auto_backup,
            args=[app],
            trigger=CronTrigger(hour=2, minute=0),
            id="yedekleme_nightly",
            replace_existing=True,
            misfire_grace_time=3600,
            coalesce=True,
        )
        scheduler.start()
        app.logger.info("[yedekleme] Otomatik yedek zamanlayıcı başlatıldı (her gece 02:00).")
    except ImportError:
        app.logger.warning("[yedekleme] apscheduler yok, otomatik yedek atlandı.")
    return app


def _init_early_warning_scheduler(app) -> None:
    """Erken uyarı servisini her gece 02:00'de çalıştırır."""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        from services.early_warning_service import run_early_warning

        scheduler = BackgroundScheduler(daemon=True, timezone="Europe/Istanbul")
        scheduler.add_job(
            func=run_early_warning,
            args=[app],
            trigger=CronTrigger(hour=2, minute=0),
            id="early_warning_nightly",
            replace_existing=True,
        )
        scheduler.start()
        app.logger.info("[early_warning] Zamanlayıcı başlatıldı (her gece 02:00).")
    except ImportError:
        app.logger.warning("[early_warning] apscheduler kurulu değil, zamanlayıcı atlandı.")

    return app


def _init_demo_inactivity_sweeper(app) -> None:
    """Demo inaktivite sıfırlayıcı (KURALLAR §8.4) — her 5 dk Tomofil'i baseline'a
    döndürme kontrolü. Yalnızca KOKPITIM_DEMO_MODE=1 ortamında çağrılır."""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.interval import IntervalTrigger

        inactivity = app.config.get("DEMO_INACTIVITY_MINUTES", 15)

        def _run():
            with app.app_context():
                from app.services.demo_reset_service import inactivity_sweep
                inactivity_sweep(inactivity)

        scheduler = BackgroundScheduler(daemon=True, timezone="Europe/Istanbul")
        scheduler.add_job(
            func=_run,
            trigger=IntervalTrigger(minutes=5),
            id="demo_inactivity_sweep",
            replace_existing=True,
        )
        scheduler.start()
        app.logger.info("[demo_reset] inaktivite sweeper başlatıldı (her 5 dk, eşik=%s dk).", inactivity)
    except ImportError:
        app.logger.warning("[demo_reset] apscheduler kurulu değil, sweeper atlandı.")
    except Exception as e:
        app.logger.error("[demo_reset] sweeper başlatma hatası: %s", e)
