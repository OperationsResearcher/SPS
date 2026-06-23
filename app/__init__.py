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

    @app.context_processor
    def _inject_component_visibility():
        """Bileşen-düzeyi görünürlük: {% if component_visible('performans_gostergesi') %}.

        Modül açık olsa bile İÇİNDEKİ bileşeni paket'e göre gizlemek için.
        Kaynak: paket → modül → component_slug (require_component ile aynı zincir).
        Yalnız platform Admin bypass; kurum rolleri pakete tabi. Bir kez hesaplanır.
        """
        from flask_login import current_user

        slugs = None  # None = kısıtlama yok (Admin / hata / paketsiz fail-open)
        try:
            if current_user.is_authenticated:
                if current_user.role and current_user.role.name == "Admin":
                    slugs = None  # platform admin: her bileşen görünür
                else:
                    pkg = getattr(current_user.tenant, "package", None) if current_user.tenant else None
                    if pkg is not None:
                        s = set()
                        for mod in pkg.modules:
                            for comp in mod.component_slugs:
                                s.add(comp.component_slug)
                        slugs = s
                    # pkg None → slugs None (paketsiz: kısıtlama yok, mevcut davranış)
        except Exception:
            slugs = None  # fail-open

        def component_visible(slug):
            if slugs is None:
                return True
            return slug in slugs

        def card_data_visible(card_code, data_key):
            """Kart-içi veri parçası paket'e göre görünür mü? (KART katmanı).

            CardDataSource.required_component_code → component_visible ile kontrol.
            Eşleme yoksa görünür (fail-open). slugs None ise (Admin/paketsiz) görünür.
            """
            if slugs is None:
                return True
            try:
                from app.models.saas import SystemCard, CardDataSource
                row = (CardDataSource.query
                       .join(SystemCard, CardDataSource.card_id == SystemCard.id)
                       .filter(SystemCard.code == card_code,
                               CardDataSource.data_key == data_key,
                               CardDataSource.is_active.is_(True))
                       .first())
            except Exception:
                return True
            if not row or not row.required_component_code:
                return True  # eşleme/kısıt yok → göster
            return row.required_component_code in slugs

        return {"component_visible": component_visible,
                "card_data_visible": card_data_visible}

    @app.context_processor
    def _inject_sidebar_modules():
        """Sidebar paket-gating: kullanıcının erişebileceği launcher modül id'leri.

        Sidebar (base.html) bu kümeyle modül linklerini koşullar — launcher
        kartlarıyla aynı paket kapısı (get_accessible_modules). Giriş yoksa boş.
        Template: {% if 'surec' in sidebar_module_ids %}
        """
        from flask_login import current_user
        try:
            if not current_user.is_authenticated:
                return {"sidebar_module_ids": set()}
            from app_platform.core.module_registry import get_accessible_modules
            ids = {m["id"] for m in get_accessible_modules(current_user)}
        except Exception:
            # Hata durumunda sidebar'ı kısıtlama (mevcut davranışa düş)
            return {"sidebar_module_ids": None}
        return {"sidebar_module_ids": ids}

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
        ("/reports/k-vector-skewness", None): "performans",
        ("/reports/alignment-sankey", None): "performans",
        ("/sp/strategy-project-matrix", None): "performans",
        ("/reports/pg-project-impact", None): "performans",
        ("/reports/department-performance", None): "performans",
        ("/reports/executive-leadership", None): "performans",
        ("/reports/cmmi-heatmap", None): "performans",
        ("/reports/target-revision", None): "performans",
        ("/k-radar/ks", None): "performans",
        # Yürütme
        ("/k-rapor", "faaliyet"): "yurutme",
        ("/k-rapor", "faaliyet-matris"): "yurutme",
        ("/k-rapor", "aktivite-takvim"): "yurutme",
        ("/k-rapor", "sorumlu-analiz"): "yurutme",
        ("/k-rapor", "bireysel"): "yurutme",
        ("/k-rapor", "evm"): "yurutme",
        ("/reports/individual-alignment", None): "yurutme",
        ("/reports/initiative-bubble", None): "yurutme",
        ("/reports/initiative-roadmap", None): "yurutme",
        ("/reports/quarterly-review", None): "yurutme",
        ("/reports/okr-cascade", None): "yurutme",
        ("/reports/morning-summary", None): "yurutme",
        ("/reports/operation-statistics", None): "yurutme",
        ("/reports/muda-analysis", None): "yurutme",
        # Risk & Veri
        ("/k-rapor", "risk"): "risk",
        ("/k-rapor", "uyari"): "risk",
        ("/k-rapor", "veri-durumu"): "risk",
        ("/k-rapor", "denetim"): "risk",
        ("/k-rapor", "bildirim-analiz"): "risk",
        ("/reports/risk-heatmap", None): "risk",
        ("/reports/early-warning", None): "risk",
        ("/reports/ml-anomaly", None): "risk",
        ("/reports/data-quality", None): "risk",
        ("/reports/two-fa", None): "risk",
        ("/reports/audit-package", None): "risk",
        ("/reports/approval-chain", None): "risk",
        # Strateji
        ("/k-rapor", "stratejik-analiz"): "strateji",
        ("/k-rapor", "swot-trend"): "strateji",
        ("/k-rapor", "paydas"): "strateji",
        ("/k-rapor", "rekabet"): "strateji",
        ("/k-rapor", "kurum-karsilastirma"): "strateji",
        ("/reports/vrio-portfoy", None): "strateji",
        ("/reports/sektor-benchmark", None): "ai",
        ("/reports/sectoral", None): "strateji",
        ("/reports/sunburst", None): "strateji",
        ("/sp/strategy-map", None): "strateji",
        ("/reports/evolution-film", None): "strateji",
        ("/reports/strategy-story", None): "strateji",
        # AI & Üst Yönetim
        ("/reports/cfo-dashboard", None): "ai",
        ("/reports/coo-dashboard", None): "ai",
        ("/reports/chro-dashboard", None): "ai",
        ("/reports/investor-presentation", None): "ai",
        ("/reports/strategic-annual", None): "ai",
        ("/reports/esg-report", None): "ai",
        ("/reports/carbon-trend", None): "ai",
        ("/reports/ai-advisor", None): "ai",
        ("/reports/ai-coach", None): "ai",
        ("/reports/ai-presentation", None): "ai",
        ("/reports/nlp-query", None): "ai",
        ("/reports/individual-scorecard-batch", None): "ai",
        ("/reports/mobile", None): "ai",
        ("/reports/bi-connector", None): "ai",
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
            ("/desktop-launcher",  "Masaüstü", "/desktop-launcher"),
            ("/masaustu",          "Masaüstü", "/desktop-launcher"),
            ("/sp",                "Stratejik Planlama", "/sp"),
            ("/process",           "Süreç Yönetimi", "/process"),
            ("/proje",             "Proje Yönetimi", "/project"),
            ("/project",           "Proje Yönetimi", "/project"),
            ("/k-radar",           "K-Radar", "/k-radar"),
            ("/k-analiz",          "K-Radar", "/k-radar"),
            ("/k-rapor",           "K-Radar", "/k-radar"),
            ("/reports",          "K-Radar", "/k-radar"),
            ("/individual",        "Bireysel Performans", "/individual/scorecard"),
            ("/analysis",          "Performans Analitiği", "/analysis"),
            ("/notification",      "Bildirimler", "/notification"),
            ("/settings",          "Ayarlar", "/settings"),
            ("/kurum",             "Kurum", "/kurum"),
            ("/admin",             "Yönetim Paneli", "/admin/yonetim-paneli"),
            ("/yonetim",           "Yönetim Paneli", "/admin/yonetim-paneli"),
            ("/profile",           "Profil", "/profile"),
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
