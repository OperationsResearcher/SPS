# -*- coding: utf-8 -*-
"""
SQL Server'dan Veri Aktarma Scripti (migration_export.py)

Bu script, mevcut SQL Server veritabanından TÜM verileri çıkarır ve
JSON formatında `data_dump.json` dosyasına kaydeder.

KULLANIM:
1. Mevcut SQL Server bağlantı ayarlarınızın config.py'de doğru olduğundan emin olun.
2. Bu scripti çalıştırın: python migration_export.py
3. `data_dump.json` dosyası oluşturulacaktır.
"""

import sys
import json
import os
from datetime import datetime, date
from decimal import Decimal

# Flask uygulama context'i için
sys.path.insert(0, os.path.dirname(__file__))

from __init__ import create_app
from models import (
    # Ana modeller (Foreign key bağımlılığı yok)
    Kurum,
    
    # User ve ilişkili modeller
    User,
    DashboardLayout,
    
    # Kurum'a bağlı modeller
    Deger,
    EtikKural,
    KalitePolitikasi,
    AnaStrateji,
    AltStrateji,
    Surec,
    SwotAnalizi,
    PestleAnalizi,
    
    # Association Tables (ilişki tabloları)
    surec_uyeleri,
    surec_liderleri,
    surec_alt_stratejiler,
    
    # Surec'e bağlı modeller
    SurecPerformansGostergesi,
    SurecFaaliyet,
    
    # User'a bağlı modeller
    BireyselPerformansGostergesi,
    BireyselFaaliyet,
    OzelYetki,
    Notification,
    UserActivityLog,
    FavoriKPI,
    
    # Yetkilendirme modelleri
    YetkiMatrisi,
    KullaniciYetki,
    
    # Performans göstergesi verileri
    PerformansGostergeVeri,
    PerformansGostergeVeriAudit,
    
    # Faaliyet takip
    FaaliyetTakip,
    
    # Proje Yönetimi modelleri
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
    
    # Association Tables (Proje Yönetimi)
    project_members,
    project_observers,
    project_related_processes,
    task_predecessors,
    
    db
)

# JSON serialization için helper
class DateTimeEncoder(json.JSONEncoder):
    """Datetime, date ve Decimal objelerini JSON uyumlu string'e çevirir"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def serialize_model(obj):
    """SQLAlchemy model objesini dictionary'ye çevirir"""
    if obj is None:
        return None
    
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        # None değerleri de dahil et
        result[column.name] = value
    return result


def export_table_data(model_class, app_context):
    """Bir tablodaki tüm verileri çıkarır"""
    try:
        with app_context:
            records = model_class.query.all()
            data = [serialize_model(record) for record in records]
            print(f"[OK] {model_class.__tablename__}: {len(data)} kayit cikarildi")
            return data
    except Exception as e:
        print(f"[ERROR] {model_class.__tablename__} cikarilirken hata: {str(e)}")
        return []


def export_association_table(table_name, table, app_context):
    """Association table (ilişki tablosu) verilerini çıkarır"""
    try:
        with app_context:
            # Association table'ları doğrudan sorgulayamayız, SQL ile çekmeliyiz
            from sqlalchemy import select
            result = db.session.execute(select(*table.columns).select_from(table))
            data = [dict(row._mapping) for row in result]
            print(f"[OK] {table_name}: {len(data)} kayit cikarildi")
            return data
    except Exception as e:
        print(f"[ERROR] {table_name} cikarilirken hata: {str(e)}")
        return []


def test_connection(app):
    """SQL Server bağlantısını test et"""
    try:
        with app.app_context():
            # Basit bir sorgu çalıştır
            result = db.session.execute(db.text("SELECT 1"))
            result.fetchone()
            return True
    except Exception as e:
        print(f"\n[HATA] Baglanti testi basarisiz: {str(e)}")
        return False


def main():
    """Ana export fonksiyonu"""
    print("=" * 60)
    print("SQL Server'dan Veri Aktarma İşlemi Başlatılıyor...")
    print("=" * 60)
    
    # Flask uygulama oluştur
    app = create_app()
    
    # SQL Server'dan veri çekmek için geçici olarak SQL Server bağlantısını aktif et
    # Önce environment variable'ları kontrol et
    original_uri = app.config['SQLALCHEMY_DATABASE_URI']
    sql_server_configured = False
    
    if os.environ.get('SQL_SERVER') or os.environ.get('DATABASE_URL'):
        # SQL Server bağlantısı var, config'deki ayarları kullan
        from config import build_sqlserver_uri
        if os.environ.get('DATABASE_URL'):
            app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
            print("[INFO] DATABASE_URL kullanılıyor")
        elif os.environ.get('SQL_SERVER'):
            app.config['SQLALCHEMY_DATABASE_URI'] = build_sqlserver_uri()
            print("[INFO] SQL Server baglantisi environment variable'lardan oluşturuldu")
        
        # Bağlantıyı test et
        print("[INFO] Bağlantı test ediliyor...")
        if test_connection(app):
            print("[OK] SQL Server baglantisi basarili!")
            sql_server_configured = True
        else:
            print("\n[HATA] SQL Server baglantisi basarisiz!")
            print("\nÇözüm önerileri:")
            print("1. test_sqlserver_connection.py scriptini çalıştırarak bağlantıyı test edin")
            print("2. Environment variable'ları kontrol edin:")
            print("   - SQL_SERVER")
            print("   - SQL_DATABASE")
            print("   - SQL_USERNAME")
            print("   - SQL_PASSWORD")
            print("   - SQL_DRIVER")
            print("3. SQL Server'ın çalıştığından emin olun")
            print("4. Firewall ayarlarını kontrol edin")
            sys.exit(1)
    else:
        print("\n[HATA] SQL Server baglanti bilgileri bulunamadi!")
        print("\nGerekli environment variable'lar:")
        print("  - SQL_SERVER (örn: localhost veya (localdb)\\MSSQLLocalDB)")
        print("  - SQL_DATABASE (örn: stratejik_planlama)")
        print("  - SQL_USERNAME (örn: sa)")
        print("  - SQL_PASSWORD (şifreniz)")
        print("  - SQL_DRIVER (örn: ODBC Driver 17 for SQL Server)")
        print("\nVeya DATABASE_URL direkt olarak set edilebilir:")
        print("  DATABASE_URL=mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17+for+SQL+Server")
        print("\n[INFO] Mevcut veritabani URI: " + app.config['SQLALCHEMY_DATABASE_URI'])
        print("\n💡 İpucu: Önce 'python test_sqlserver_connection.py' çalıştırarak bağlantıyı test edin")
        sys.exit(1)
    
    # Foreign key bağımlılık sırasına göre modeller
    # (Önce ana tablolar, sonra çocuk tablolar)
    export_order = [
        # 1. Kurum (hiçbir bağımlılığı yok)
        ('Kurum', Kurum),
        
        # 2. User (Kurum'a bağlı)
        ('User', User),
        
        # 3. User'a bağlı modeller
        ('DashboardLayout', DashboardLayout),
        ('BireyselPerformansGostergesi', BireyselPerformansGostergesi),
        ('BireyselFaaliyet', BireyselFaaliyet),
        ('OzelYetki', OzelYetki),
        ('Notification', Notification),
        ('UserActivityLog', UserActivityLog),
        ('FavoriKPI', FavoriKPI),
        
        # 4. Kurum'a bağlı modeller
        ('Deger', Deger),
        ('EtikKural', EtikKural),
        ('KalitePolitikasi', KalitePolitikasi),
        ('AnaStrateji', AnaStrateji),
        ('AltStrateji', AltStrateji),
        ('Surec', Surec),
        ('SwotAnalizi', SwotAnalizi),
        ('PestleAnalizi', PestleAnalizi),
        
        # 5. Surec'e bağlı modeller
        ('SurecPerformansGostergesi', SurecPerformansGostergesi),
        ('SurecFaaliyet', SurecFaaliyet),
        
        # 6. Yetkilendirme
        ('YetkiMatrisi', YetkiMatrisi),
        ('KullaniciYetki', KullaniciYetki),
        
        # 7. Performans göstergesi verileri
        ('PerformansGostergeVeri', PerformansGostergeVeri),
        ('PerformansGostergeVeriAudit', PerformansGostergeVeriAudit),
        
        # 8. Faaliyet takip
        ('FaaliyetTakip', FaaliyetTakip),
        
        # 9. Proje Yönetimi - Ana modeller
        ('Project', Project),
        ('Tag', Tag),
        ('ProjectTemplate', ProjectTemplate),
        ('TaskTemplate', TaskTemplate),
        ('Sprint', Sprint),
        
        # 10. Proje'ye bağlı modeller
        ('Task', Task),
        ('ProjectFile', ProjectFile),
        ('ProjectRisk', ProjectRisk),
        
        # 11. Task'e bağlı modeller
        ('TaskImpact', TaskImpact),
        ('TaskComment', TaskComment),
        ('TaskMention', TaskMention),
        ('TaskSubtask', TaskSubtask),
        ('TimeEntry', TimeEntry),
        ('TaskActivity', TaskActivity),
        ('TaskSprint', TaskSprint),
    ]
    
    # Association table'lar (ilişki tabloları)
    association_tables = [
        ('surec_uyeleri', surec_uyeleri),
        ('surec_liderleri', surec_liderleri),
        ('surec_alt_stratejiler', surec_alt_stratejiler),
        ('project_members', project_members),
        ('project_observers', project_observers),
        ('project_related_processes', project_related_processes),
        ('task_predecessors', task_predecessors),
    ]
    
    # Export verilerini saklamak için dictionary
    export_data = {
        'metadata': {
            'export_date': datetime.utcnow().isoformat(),
            'source_db': 'SQL Server',
            'target_db': 'SQLite',
            'version': '1.0'
        },
        'tables': {}
    }
    
    # Normal tabloları export et
    with app.app_context():
        for table_name, model_class in export_order:
            export_data['tables'][table_name] = export_table_data(model_class, app.app_context())
        
        # Association table'ları export et
        for table_name, table in association_tables:
            export_data['tables'][table_name] = export_association_table(table_name, table, app.app_context())
    
    # JSON dosyasına kaydet
    output_file = 'data_dump.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
        
        # İstatistikler
        total_records = sum(len(data) for data in export_data['tables'].values())
        print("\n" + "=" * 60)
        print("[OK] Export islemi tamamlandi!")
        print(f"[FILE] Dosya: {output_file}")
        print(f"[STAT] Toplam tablo sayisi: {len(export_data['tables'])}")
        print(f"[STAT] Toplam kayit sayisi: {total_records}")
        print("=" * 60)
        print("\nBir sonraki adım: python migration_init.py çalıştırın")
        
    except Exception as e:
        print(f"\n[ERROR] JSON dosyasina yazilirken hata: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Original URI'yi geri yükle
        app.config['SQLALCHEMY_DATABASE_URI'] = original_uri


if __name__ == '__main__':
    main()

