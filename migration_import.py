# -*- coding: utf-8 -*-
"""
SQLite'a Veri İçer Alma Scripti (migration_import.py)

Bu script, `data_dump.json` dosyasını okur ve verileri SQLite veritabanına yükler.

KULLANIM:
1. Önce migration_init.py'yi çalıştırdığınızdan emin olun.
2. data_dump.json dosyasının mevcut olduğundan emin olun.
3. Bu scripti çalıştırın: python migration_import.py
4. Veriler SQLite veritabanına yüklenecektir.
"""

import sys
import json
import os
from datetime import datetime, date

# Flask uygulama context'i için
sys.path.insert(0, os.path.dirname(__file__))

from __init__ import create_app
from models import (
    # Ana modeller
    Kurum,
    User,
    DashboardLayout,
    Deger,
    EtikKural,
    KalitePolitikasi,
    AnaStrateji,
    AltStrateji,
    Surec,
    SwotAnalizi,
    PestleAnalizi,
    SurecPerformansGostergesi,
    SurecFaaliyet,
    BireyselPerformansGostergesi,
    BireyselFaaliyet,
    OzelYetki,
    Notification,
    UserActivityLog,
    FavoriKPI,
    YetkiMatrisi,
    KullaniciYetki,
    PerformansGostergeVeri,
    PerformansGostergeVeriAudit,
    FaaliyetTakip,
    Project,
    Task,
    TaskImpact,
    TaskComment,
    TaskMention,
    ProjectFile,
    Tag,
    TaskSubtask,
    TimeEntry,
    TaskActivity,
    ProjectTemplate,
    TaskTemplate,
    Sprint,
    TaskSprint,
    ProjectRisk,
    
    # Association Tables
    surec_uyeleri,
    surec_liderleri,
    surec_alt_stratejiler,
    project_members,
    project_observers,
    project_related_processes,
    task_predecessors,
    
    db
)

# SQLite veritabanı dosya yolu
basedir = os.path.abspath(os.path.dirname(__file__))
SQLITE_DB_PATH = os.path.join(basedir, 'spsv2.db')
DUMP_FILE = os.path.join(basedir, 'data_dump.json')

# Model mapping (tablo adı -> model class)
MODEL_MAP = {
    'Kurum': Kurum,
    'User': User,
    'DashboardLayout': DashboardLayout,
    'Deger': Deger,
    'EtikKural': EtikKural,
    'KalitePolitikasi': KalitePolitikasi,
    'AnaStrateji': AnaStrateji,
    'AltStrateji': AltStrateji,
    'Surec': Surec,
    'SwotAnalizi': SwotAnalizi,
    'PestleAnalizi': PestleAnalizi,
    'SurecPerformansGostergesi': SurecPerformansGostergesi,
    'SurecFaaliyet': SurecFaaliyet,
    'BireyselPerformansGostergesi': BireyselPerformansGostergesi,
    'BireyselFaaliyet': BireyselFaaliyet,
    'OzelYetki': OzelYetki,
    'Notification': Notification,
    'UserActivityLog': UserActivityLog,
    'FavoriKPI': FavoriKPI,
    'YetkiMatrisi': YetkiMatrisi,
    'KullaniciYetki': KullaniciYetki,
    'PerformansGostergeVeri': PerformansGostergeVeri,
    'PerformansGostergeVeriAudit': PerformansGostergeVeriAudit,
    'FaaliyetTakip': FaaliyetTakip,
    'Project': Project,
    'Task': Task,
    'TaskImpact': TaskImpact,
    'TaskComment': TaskComment,
    'TaskMention': TaskMention,
    'ProjectFile': ProjectFile,
    'Tag': Tag,
    'TaskSubtask': TaskSubtask,
    'TimeEntry': TimeEntry,
    'TaskActivity': TaskActivity,
    'ProjectTemplate': ProjectTemplate,
    'TaskTemplate': TaskTemplate,
    'Sprint': Sprint,
    'TaskSprint': TaskSprint,
    'ProjectRisk': ProjectRisk,
}

# Association table mapping
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
    """ISO 8601 string'i Python datetime/date objesine çevirir"""
    if value is None:
        return None
    
    if isinstance(value, (datetime, date)):
        return value
    
    try:
        # ISO format: "2024-01-15T10:30:00" veya "2024-01-15"
        if 'T' in value:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        else:
            return date.fromisoformat(value)
    except (ValueError, AttributeError):
        # Eğer parse edilemezse olduğu gibi döndür
        return value


def convert_data_types(row, model_class):
    """JSON'dan gelen verileri model'in beklediği tiplere çevirir"""
    converted = {}
    for key, value in row.items():
        if value is None:
            converted[key] = None
            continue
        
        # Kolon tipini kontrol et
        column = model_class.__table__.columns.get(key)
        if column is None:
            converted[key] = value
            continue
        
        column_type = str(column.type)
        
        # DateTime/Date dönüşümü
        if 'DateTime' in column_type or 'Date' in column_type:
            converted[key] = parse_datetime(value)
        # Boolean dönüşümü
        elif 'Boolean' in column_type or 'BIT' in column_type:
            converted[key] = bool(value) if value is not None else None
        # Integer dönüşümü
        elif 'Integer' in column_type:
            converted[key] = int(value) if value is not None else None
        # Float dönüşümü
        elif 'Float' in column_type or 'Numeric' in column_type:
            converted[key] = float(value) if value is not None else None
        # Diğerleri olduğu gibi
        else:
            converted[key] = value
    
    return converted


def import_table_data(table_name, data, app_context):
    """Bir tablonun verilerini SQLite'a yükler"""
    if table_name not in MODEL_MAP:
        print(f"[WARNING] {table_name} icin model bulunamadi, atlaniyor...")
        return 0
    
    model_class = MODEL_MAP[table_name]
    
    if not data:
        print(f"[INFO] {table_name}: Veri yok, atlaniyor")
        return 0
    
    try:
        with app_context:
            imported_count = 0
            for row in data:
                try:
                    # Veri tiplerini dönüştür
                    converted_row = convert_data_types(row, model_class)
                    
                    # Model instance oluştur
                    instance = model_class(**converted_row)
                    
                    # Veritabanına ekle
                    db.session.add(instance)
                    imported_count += 1
                except Exception as e:
                    print(f"  [WARNING] Kayit import edilemedi: {str(e)}")
                    continue
            
            # Commit
            db.session.commit()
            print(f"[OK] {table_name}: {imported_count} kayit yuklendi")
            return imported_count
            
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] {table_name} yuklenirken hata: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0


def import_association_table(table_name, data, app_context):
    """Association table verilerini yükler"""
    if table_name not in ASSOCIATION_TABLE_MAP:
        print(f"[WARNING] {table_name} icin association table bulunamadi, atlaniyor...")
        return 0
    
    table = ASSOCIATION_TABLE_MAP[table_name]
    
    if not data:
        print(f"[INFO] {table_name}: Veri yok, atlaniyor")
        return 0
    
    try:
        with app_context:
            imported_count = 0
            for row in data:
                try:
                    # Association table'a INSERT yap
                    stmt = table.insert().values(**row)
                    db.session.execute(stmt)
                    imported_count += 1
                except Exception as e:
                    print(f"  [WARNING] Kayit import edilemedi: {str(e)}")
                    continue
            
            # Commit
            db.session.commit()
            print(f"[OK] {table_name}: {imported_count} kayit yuklendi")
            return imported_count
            
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] {table_name} yuklenirken hata: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0


def main():
    """Ana import fonksiyonu"""
    print("=" * 60)
    print("SQLite'a Veri İçer Alma İşlemi Başlatılıyor...")
    print("=" * 60)
    
    # Dosya kontrolü
    if not os.path.exists(DUMP_FILE):
        print(f"[ERROR] {DUMP_FILE} dosyasi bulunamadi!")
        print("Önce migration_export.py'yi çalıştırın.")
        sys.exit(1)
    
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"[ERROR] {SQLITE_DB_PATH} dosyasi bulunamadi!")
        print("Önce migration_init.py'yi çalıştırın.")
        sys.exit(1)
    
    # JSON dosyasını yükle
    try:
        with open(DUMP_FILE, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
    except Exception as e:
        print(f"❌ JSON dosyası okunurken hata: {str(e)}")
        sys.exit(1)
    
    # Metadata'yı göster
    metadata = export_data.get('metadata', {})
    print(f"\n[INFO] Export Bilgileri:")
    print(f"   Tarih: {metadata.get('export_date', 'Bilinmiyor')}")
    print(f"   Kaynak: {metadata.get('source_db', 'Bilinmiyor')}")
    print(f"   Hedef: {metadata.get('target_db', 'Bilinmiyor')}")
    
    # Flask uygulama oluştur
    app = create_app()
    
    # Config'i SQLite kullanacak şekilde değiştir
    original_uri = app.config['SQLALCHEMY_DATABASE_URI']
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{SQLITE_DB_PATH}'
    
    # Import sırası (Foreign key bağımlılığına göre)
    import_order = [
        'Kurum',
        'User',
        'DashboardLayout',
        'Deger',
        'EtikKural',
        'KalitePolitikasi',
        'AnaStrateji',
        'AltStrateji',
        'Surec',
        'SwotAnalizi',
        'PestleAnalizi',
        'SurecPerformansGostergesi',
        'SurecFaaliyet',
        'BireyselPerformansGostergesi',
        'BireyselFaaliyet',
        'OzelYetki',
        'Notification',
        'UserActivityLog',
        'FavoriKPI',
        'YetkiMatrisi',
        'KullaniciYetki',
        'PerformansGostergeVeri',
        'PerformansGostergeVeriAudit',
        'FaaliyetTakip',
        'Project',
        'Tag',
        'ProjectTemplate',
        'TaskTemplate',
        'Sprint',
        'Task',
        'ProjectFile',
        'ProjectRisk',
        'TaskImpact',
        'TaskComment',
        'TaskMention',
        'TaskSubtask',
        'TimeEntry',
        'TaskActivity',
        'TaskSprint',
    ]
    
    # Association table'lar
    association_tables = [
        'surec_uyeleri',
        'surec_liderleri',
        'surec_alt_stratejiler',
        'project_members',
        'project_observers',
        'project_related_processes',
        'task_predecessors',
    ]
    
    total_imported = 0
    
    try:
        with app.app_context():
            # Normal tabloları import et
            print("\n[INFO] Normal tablolar yukleniyor...")
            for table_name in import_order:
                if table_name in export_data.get('tables', {}):
                    count = import_table_data(table_name, export_data['tables'][table_name], app.app_context())
                    total_imported += count
            
            # Association table'ları import et
            print("\n[INFO] Iliski tablolari yukleniyor...")
            for table_name in association_tables:
                if table_name in export_data.get('tables', {}):
                    count = import_association_table(table_name, export_data['tables'][table_name], app.app_context())
                    total_imported += count
            
            print("\n" + "=" * 60)
            print("[OK] Import islemi tamamlandi!")
            print(f"[STAT] Toplam yuklenen kayit: {total_imported}")
            print(f"[FILE] Veritabani: {SQLITE_DB_PATH}")
            print("=" * 60)
            print("\nSon adım: config.py'yi SQLite kullanacak şekilde güncelleyin")
            
    except Exception as e:
        print(f"\n[ERROR] Import islemi sirasinda hata: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Original URI'yi geri yükle
        app.config['SQLALCHEMY_DATABASE_URI'] = original_uri


if __name__ == '__main__':
    main()

