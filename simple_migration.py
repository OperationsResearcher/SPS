# -*- coding: utf-8 -*-
"""
Basit Migration Scripti - SQL Server'dan SQLite'a
Tüm işlemleri tek seferde yapar
"""

import sys
import os
import json
from datetime import datetime, date
from decimal import Decimal

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask
from sqlalchemy import inspect

# SQLite dosya yolu
basedir = os.path.abspath(os.path.dirname(__file__))
SQLITE_DB_PATH = os.path.join(basedir, 'spsv2.db')
DUMP_FILE = os.path.join(basedir, 'data_dump.json')

# Mevcut Flask app ve db'yi kullan
from __init__ import create_app
from extensions import db

# Modelleri import et
from models import *

def main():
    print("=" * 60)
    print("BASIT MIGRATION - SQL Server -> SQLite")
    print("=" * 60)
    
    # 1. Mevcut SQLite DB'yi sil
    if os.path.exists(SQLITE_DB_PATH):
        os.remove(SQLITE_DB_PATH)
        print(f"[OK] Eski SQLite DB silindi")
    
    # 2. Flask app oluştur ve SQLite'a bağla
    app = create_app()
    original_uri = app.config['SQLALCHEMY_DATABASE_URI']
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{SQLITE_DB_PATH}'
    
    # Tabloları oluştur
    print("\n[1/3] SQLite veritabani ve tablolar olusturuluyor...")
    with app.app_context():
        # Engine'i yeniden başlat
        if hasattr(db, 'engine') and db.engine:
            db.engine.dispose()
        
        db.create_all()
        inspector = inspect(db.engine)
        table_count = len(inspector.get_table_names())
        print(f"[OK] {table_count} tablo olusturuldu")
    
    # 3. JSON'dan verileri yükle
    if not os.path.exists(DUMP_FILE):
        print(f"\n[HATA] {DUMP_FILE} bulunamadi!")
        print("Once migration_export.py calistirin")
        return
    
    print("\n[2/3] Veriler yukleniyor...")
    with open(DUMP_FILE, 'r', encoding='utf-8') as f:
        export_data = json.load(f)
    
    # Model mapping
    MODEL_MAP = {
        'Kurum': Kurum, 'User': User, 'DashboardLayout': DashboardLayout,
        'Deger': Deger, 'EtikKural': EtikKural, 'KalitePolitikasi': KalitePolitikasi,
        'AnaStrateji': AnaStrateji, 'AltStrateji': AltStrateji, 'Surec': Surec,
        'SwotAnalizi': SwotAnalizi, 'PestleAnalizi': PestleAnalizi,
        'SurecPerformansGostergesi': SurecPerformansGostergesi,
        'SurecFaaliyet': SurecFaaliyet,
        'BireyselPerformansGostergesi': BireyselPerformansGostergesi,
        'BireyselFaaliyet': BireyselFaaliyet, 'OzelYetki': OzelYetki,
        'Notification': Notification, 'UserActivityLog': UserActivityLog,
        'FavoriKPI': FavoriKPI, 'YetkiMatrisi': YetkiMatrisi,
        'KullaniciYetki': KullaniciYetki,
        'PerformansGostergeVeri': PerformansGostergeVeri,
        'PerformansGostergeVeriAudit': PerformansGostergeVeriAudit,
        'FaaliyetTakip': FaaliyetTakip,
        'Project': Project, 'Task': Task, 'TaskImpact': TaskImpact,
        'TaskComment': TaskComment, 'TaskMention': TaskMention,
        'ProjectFile': ProjectFile, 'Tag': Tag, 'TaskSubtask': TaskSubtask,
        'TimeEntry': TimeEntry, 'TaskActivity': TaskActivity,
        'ProjectTemplate': ProjectTemplate, 'TaskTemplate': TaskTemplate,
        'Sprint': Sprint, 'TaskSprint': TaskSprint, 'ProjectRisk': ProjectRisk,
    }
    
    ASSOCIATION_TABLE_MAP = {
        'surec_uyeleri': surec_uyeleri,
        'surec_liderleri': surec_liderleri,
        'surec_alt_stratejiler': surec_alt_stratejiler,
        'project_members': project_members,
        'project_observers': project_observers,
        'project_related_processes': project_related_processes,
        'task_predecessors': task_predecessors,
    }
    
    def parse_datetime(value):
        if value is None or isinstance(value, (datetime, date)):
            return value
        try:
            if 'T' in str(value):
                return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
            else:
                return date.fromisoformat(str(value))
        except:
            return value
    
    total_imported = 0
    
    with app.app_context():
        # Normal tablolar
        for table_name, model_class in MODEL_MAP.items():
            if table_name in export_data.get('tables', {}):
                data = export_data['tables'][table_name]
                if data:
                    for row in data:
                        try:
                            # Tarih dönüşümü
                            converted = {}
                            for k, v in row.items():
                                col = model_class.__table__.columns.get(k)
                                if col and ('DateTime' in str(col.type) or 'Date' in str(col.type)):
                                    converted[k] = parse_datetime(v)
                                else:
                                    converted[k] = v
                            
                            instance = model_class(**converted)
                            db.session.add(instance)
                        except Exception as e:
                            print(f"  [UYARI] {table_name}: {str(e)[:50]}")
                            continue
                    
                    db.session.commit()
                    print(f"[OK] {table_name}: {len(data)} kayit")
                    total_imported += len(data)
        
        # Association tablolar
        for table_name, table in ASSOCIATION_TABLE_MAP.items():
            if table_name in export_data.get('tables', {}):
                data = export_data['tables'][table_name]
                if data:
                    for row in data:
                        try:
                            stmt = table.insert().values(**row)
                            db.session.execute(stmt)
                        except:
                            continue
                    db.session.commit()
                    print(f"[OK] {table_name}: {len(data)} kayit")
                    total_imported += len(data)
    
    print("\n[3/3] Config ayarlaniyor...")
    
    # Config'i SQLite kullanacak şekilde ayarla
    config_content = """# -*- coding: utf-8 -*-
\"\"\"
Konfigürasyon Yönetimi
Environment variables kullanarak güvenli konfigürasyon yönetimi
\"\"\"
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    \"\"\"Temel konfigürasyon sınıfı\"\"\"
    
    # Flask ayarları
    _secret_key = os.environ.get('SECRET_KEY')
    if not _secret_key:
        env = os.environ.get('FLASK_ENV', 'development')
        if env == 'production':
            raise ValueError("SECRET_KEY environment variable must be set in production!")
        import warnings
        warnings.warn("SECRET_KEY not set. Using development fallback.", UserWarning)
        _secret_key = 'dev-secret-key-change-in-production'
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
    
    # Logging
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    LOG_FILE = os.path.join(basedir, 'logs', 'stratejik_planlama.log')
    LOG_MAX_BYTES = 10240000
    LOG_BACKUP_COUNT = 10


class DevelopmentConfig(Config):
    \"\"\"Development konfigürasyonu\"\"\"
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0


class ProductionConfig(Config):
    \"\"\"Production konfigürasyonu\"\"\"
    DEBUG = False
    TESTING = False
    TEMPLATES_AUTO_RELOAD = False
    SEND_FILE_MAX_AGE_DEFAULT = 31536000
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_ENABLED = True


class TestingConfig(Config):
    \"\"\"Testing konfigürasyonu\"\"\"
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
    \"\"\"Environment'a göre konfigürasyon döndür\"\"\"
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
"""
    
    # Config dosyasını yedekle ve yeni config'i yaz
    if os.path.exists('config.py'):
        import shutil
        shutil.copy('config.py', 'config.py.backup')
        print("[OK] Mevcut config.py yedeklendi (config.py.backup)")
    
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("[OK] Config.py SQLite kullanacak sekilde guncellendi")
    
    print("\n" + "=" * 60)
    print("[TAMAMLANDI] Migration basariyla tamamlandi!")
    print(f"[STAT] Toplam {total_imported} kayit aktarildi")
    print(f"[FILE] SQLite DB: {SQLITE_DB_PATH}")
    print("=" * 60)
    print("\nArtik proje SQLite uzerinden calisacak!")


if __name__ == '__main__':
    main()

