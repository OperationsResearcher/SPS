# -*- coding: utf-8 -*-
"""
Uygulama Fabrikası (Application Factory) ve ana başlangıç noktası.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask

# Yerel importlar
from config import get_config
from extensions import db, migrate, login_manager, csrf, limiter, talisman, cache

def create_app(config_name=None):
    """
    Flask uygulama örneğini (app instance) oluşturan ve yapılandıran fabrika fonksiyonu.
    """
    app = Flask(__name__)

    # 1. Konfigürasyonu yükle
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(get_config())

    # 2. Eklentileri (extensions) ilklendir
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    # Rate Limiter - Sadece aktifse başlat
    if app.config.get('RATELIMIT_ENABLED', False):
        limiter.init_app(app)
    else:
        # Devre dışı modda bile init et ama enabled=False olarak ayarlanmış durumda
        limiter.init_app(app)
    cache.init_app(app)
    
    # Security Headers (Flask-Talisman)
    # Production'da strict CSP, development'ta daha esnek
    if not app.debug:
        talisman.init_app(
            app,
            force_https=True,
            strict_transport_security=True,
            strict_transport_security_max_age=31536000,  # 1 yıl
            content_security_policy={
                'default-src': "'self'",
                'script-src': "'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
                'style-src': "'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com",
                'font-src': "'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.gstatic.com",
                'img-src': "'self' data: https: blob:",
                'connect-src': "'self'",
                'frame-ancestors': "'none'",
                'base-uri': "'self'",
                'form-action': "'self'"
            },
            content_security_policy_nonce_in=['script-src', 'style-src'],
            frame_options='DENY',
            referrer_policy='strict-origin-when-cross-origin'
        )
    else:
        # Development: Daha esnek CSP (debug için)
        talisman.init_app(
            app,
            force_https=False,
            strict_transport_security=False,
            content_security_policy={
                'default-src': "'self'",
                'script-src': "'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://code.jquery.com",
                'style-src': "'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com",
                'font-src': "'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.gstatic.com",
                'img-src': "'self' data: https: blob:",
                'connect-src': "'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://code.jquery.com"
            },
            frame_options='SAMEORIGIN'
        )
    
    # LoginManager user_loader callback
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    # 2.5. Background task executor'ı başlat
    from services.background_tasks import init_background_executor
    init_background_executor(app)
    
    # 2.6. Görev Hatırlatma Scheduler'ı başlat
    from services.task_reminder_scheduler import init_scheduler
    with app.app_context():
        init_scheduler(app)
        app.logger.info('Görev hatırlatma scheduler başlatıldı')
    
    # 3. Logging'i yapılandır
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/stratejik_planlama.log', maxBytes=10240, backupCount=10, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Stratejik Planlama sistemi başlatılıyor')
    
    # 3.5. Audit Logging Başlat
    from services.audit_service import register_audit_listeners, register_auth_audit_signals
    register_audit_listeners(app)
    register_auth_audit_signals(app)

    # 3.6. DB tablolarını oluştur (eksik tabloları garantiye alır)
    with app.app_context():
        db.create_all()
    
    # 4. Custom Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        app.logger.error(f'Server Error: {error}')
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('errors/403.html'), 403
    
    # Additional Security Headers
    @app.after_request
    def set_additional_security_headers(response):
        """Ekstra güvenlik header'ları ekle"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # HSTS header (production için)
        if not app.debug:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()  # Hata durumunda transaction'ı rollback et
        app.logger.error(f'500 Hatası: {error}', exc_info=True)
        return render_template('errors/500.html'), 500

    # 4.5 Blueprints Kaydı
    from main.routes import main_bp
    from auth.routes import auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from api.routes import api_bp
    app.register_blueprint(api_bp)

    from main.admin import admin_bp
    app.register_blueprint(admin_bp)

    from analysis.routes import analysis_bp
    app.register_blueprint(analysis_bp)

    from bsc.routes import bsc_bp
    app.register_blueprint(bsc_bp)

    # 4.7 V2 Modülü (Deneysel)
    from v2 import v2_bp
    app.register_blueprint(v2_bp)

    # 4.8 V3 Modülü (Dashboard)
    from v3 import v3_bp
    app.register_blueprint(v3_bp)

    # 4.6 Custom Filters
    @app.template_filter('role_name')
    def role_name_filter(role):
        roles = {
            'admin': 'Sistem Yöneticisi',
            'kurum_yoneticisi': 'Kurum Yöneticisi',
            'ust_yonetim': 'Üst Yönetim',
            'yonetici': 'Yönetici',
            'calisan': 'Çalışan',
            'kurum_kullanici': 'Kurum Kullanıcısı',
            'izleyici': 'İzleyici'
        }
        return roles.get(role, role)

    # 5. Modelleri import et (veritabanı şeması için)
    with app.app_context():
        # Tüm modelleri import et
        from models import (
            User, Kurum, Surec, AnaStrateji, AltStrateji,
            StrategyMapLink,
            SurecPerformansGostergesi, SurecFaaliyet,
            BireyselPerformansGostergesi, BireyselFaaliyet,
            PerformansGostergeVeri, PerformansGostergeVeriAudit,
            FaaliyetTakip,
            AnalysisItem, TowsMatrix,
            Notification, UserActivityLog, FavoriKPI,
            YetkiMatrisi, KullaniciYetki, OzelYetki,
            DashboardLayout, Deger, EtikKural, KalitePolitikasi,
            Project, Task, TaskImpact, TaskComment, TaskMention, ProjectFile,  # Proje Yönetimi modelleri
            Tag, TaskSubtask, TimeEntry, TaskActivity, ProjectTemplate, TaskTemplate, Sprint, TaskSprint, ProjectRisk  # Yeni modeller
        )
        # Proje Yönetimi servisini import et (event listener'lar için)
        from services import project_service
        
        # -------------------------------------------------------------------------
        # ÖNEMLİ: MIGRATION İŞLEMİ İÇİN OTOMATİK TABLO OLUŞTURMA KAPATILDI
        # Supabase geçişi tamamlanana kadar bu bloğu kapalı tutuyoruz.
        # -------------------------------------------------------------------------
        # Development ortamında tabloları otomatik oluştur (sadece eksik tablolar için)
        # if app.debug or app.config.get('ENV') == 'development':
        #     try:
        #         # Sadece eksik tabloları oluştur (mevcut tabloları silmez)
        #         db.create_all()
        #         app.logger.info('Veritabanı tabloları kontrol edildi ve güncellendi.')
                
        #         # Project tablosuna eksik kolonları ekle (eğer yoksa)
        #         try:
        #             from sqlalchemy import text, inspect
        #             inspector = inspect(db.engine)
        #             columns = [col['name'] for col in inspector.get_columns('project')]

        #             db_url = str(db.engine.url)
        #             is_sqlite = 'sqlite' in db_url.lower()
                    
        #             if 'start_date' not in columns:
        #                 db.session.execute(text("ALTER TABLE project ADD start_date DATE NULL"))
        #                 app.logger.info('start_date kolonu eklendi.')
                    
        #             if 'end_date' not in columns:
        #                 db.session.execute(text("ALTER TABLE project ADD end_date DATE NULL"))
        #                 app.logger.info('end_date kolonu eklendi.')
                    
        #             if 'priority' not in columns:
        #                 db.session.execute(text("ALTER TABLE project ADD priority NVARCHAR(50) DEFAULT 'Orta'"))
        #                 app.logger.info('priority kolonu eklendi.')

        #             if 'notification_settings' not in columns:
        #                 # JSON olarak saklanır
        #                 if is_sqlite:
        #                     db.session.execute(text("ALTER TABLE project ADD COLUMN notification_settings TEXT NULL"))
        #                 else:
        #                     db.session.execute(text("ALTER TABLE project ADD notification_settings NVARCHAR(MAX) NULL"))
        #                 app.logger.info('project.notification_settings kolonu eklendi.')
                    
        #             db.session.commit()
        #         except Exception as col_error:
        #             db.session.rollback()
        #             app.logger.warning(f'Kolon ekleme hatası (normal olabilir): {str(col_error)}')
                
        #         # TaskImpact tablosuna eksik kolonları ekle (eğer yoksa)
        #         try:
        #             from sqlalchemy import text, inspect
        #             inspector = inspect(db.engine)
        #             task_impact_columns = [col['name'] for col in inspector.get_columns('task_impact')]
                    
        #             if 'is_processed' not in task_impact_columns:
        #                 db.session.execute(text("ALTER TABLE task_impact ADD is_processed BIT DEFAULT 0"))
        #                 db.session.execute(text("CREATE INDEX idx_task_impact_is_processed ON task_impact(is_processed)"))
        #                 app.logger.info('task_impact.is_processed kolonu eklendi.')
                    
        #             if 'processed_at' not in task_impact_columns:
        #                 db.session.execute(text("ALTER TABLE task_impact ADD processed_at DATETIME NULL"))
        #                 app.logger.info('task_impact.processed_at kolonu eklendi.')
                    
        #             # Project tablosuna is_archived, health_score, health_status kolonlarını ekle (eğer yoksa)
        #             try:
        #                 project_columns = [col['name'] for col in inspector.get_columns('project')]
        #                 if 'is_archived' not in project_columns:
        #                     db.session.execute(text("ALTER TABLE project ADD is_archived BIT DEFAULT 0"))
        #                     db.session.execute(text("CREATE INDEX idx_project_is_archived ON project(is_archived)"))
        #                     app.logger.info('project.is_archived kolonu eklendi.')
                        
        #                 # V67: Proje Sağlık Skoru kolonları
        #                 db_url = str(db.engine.url)
        #                 is_sqlite = 'sqlite' in db_url.lower()
                        
        #                 if 'health_score' not in project_columns:
        #                     if is_sqlite:
        #                         db.session.execute(text("ALTER TABLE project ADD COLUMN health_score INTEGER DEFAULT 100"))
        #                     else:
        #                         db.session.execute(text("ALTER TABLE project ADD health_score INT DEFAULT 100"))
        #                     app.logger.info('project.health_score kolonu eklendi.')
                        
        #                 if 'health_status' not in project_columns:
        #                     if is_sqlite:
        #                         db.session.execute(text("ALTER TABLE project ADD COLUMN health_status VARCHAR(50) DEFAULT 'İyi'"))
        #                     else:
        #                         db.session.execute(text("ALTER TABLE project ADD health_status NVARCHAR(50) DEFAULT 'İyi'"))
        #                     app.logger.info('project.health_status kolonu eklendi.')
                        
        #                 db.session.commit()
        #             except Exception as col_error:
        #                 db.session.rollback()
        #                 app.logger.warning(f'Project kolon ekleme hatası (normal olabilir): {str(col_error)}')
                    
        #             # Task tablosuna is_archived kolonu ekle (eğer yoksa)
        #             try:
        #                 task_columns = [col['name'] for col in inspector.get_columns('task')]

        #                 db_url = str(db.engine.url)
        #                 is_sqlite = 'sqlite' in db_url.lower()
        #                 if 'is_archived' not in task_columns:
        #                     db.session.execute(text("ALTER TABLE task ADD is_archived BIT DEFAULT 0"))
        #                     db.session.execute(text("CREATE INDEX idx_task_is_archived ON task(is_archived)"))
        #                     app.logger.info('task.is_archived kolonu eklendi.')

        #                 # Task planlama kolonları (UI/API uyumu)
        #                 # Not: SQLite'da ADD COLUMN ile eklenir
        #                 if 'parent_id' not in task_columns:
        #                     if is_sqlite:
        #                         db.session.execute(text("ALTER TABLE task ADD COLUMN parent_id INTEGER NULL"))
        #                     else:
        #                         db.session.execute(text("ALTER TABLE task ADD parent_id INT NULL"))
        #                     try:
        #                         db.session.execute(text("CREATE INDEX idx_task_parent_id ON task(parent_id)"))
        #                     except Exception:
        #                         pass
        #                     app.logger.info('task.parent_id kolonu eklendi.')

        #                 if 'estimated_time' not in task_columns:
        #                     if is_sqlite:
        #                         db.session.execute(text("ALTER TABLE task ADD COLUMN estimated

    return app