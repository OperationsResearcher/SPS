# -*- coding: utf-8 -*-
"""
V67 Migration Script: Mock Data'dan Activity Tablosuna Geçiş
Bu script, get_mock_data() fonksiyonundaki mock verileri Activity tablosuna aktarır.
"""

from app import create_app, db
from models import Activity, Project
from datetime import datetime


def get_mock_data():
    """Orijinal mock data fonksiyonu (migration için)"""
    return [
        {'source': 'Redmine', 'project_name': 'Omega V66', 'subject': 'Login Güvenlik Yaması', 'status': 'Açık', 'priority': 'High', 'date': datetime(2025, 12, 29)},
        {'source': 'Jira', 'project_name': 'Mobil App', 'subject': 'Bildirim Hatası', 'status': 'Beklemede', 'priority': 'Normal', 'date': datetime(2025, 12, 29)},
        {'source': 'Dahili', 'project_name': 'Sunucu', 'subject': 'Disk Temizliği', 'status': 'Tamamlandı', 'priority': 'Low', 'date': datetime(2025, 12, 28)},
        {'source': 'Redmine', 'project_name': 'Omega V66', 'subject': 'DB Migrasyonu', 'status': 'Açık', 'priority': 'High', 'date': datetime(2025, 12, 30)},
        {'source': 'CRM', 'project_name': 'Satış', 'subject': 'Müşteri Listesi', 'status': 'Devam', 'priority': 'Normal', 'date': datetime(2025, 12, 30)}
    ]


def migrate_mock_data():
    """Mock verileri Activity tablosuna aktar"""
    app = create_app()
    
    with app.app_context():
        try:
            # Mevcut Activity kayıtlarını kontrol et (tekrar eklememek için)
            existing_count = Activity.query.count()
            if existing_count > 0:
                print(f"⚠️  Zaten {existing_count} adet Activity kaydı mevcut. Migration atlanıyor.")
                return
            
            # Mock verileri al
            mock_activities = get_mock_data()
            
            # Proje adlarını Project ID'ye çevirmeye çalış
            for activity_data in mock_activities:
                project_name = activity_data.pop('project_name', None)
                
                # Proje adına göre Project bulmaya çalış
                if project_name:
                    project = Project.query.filter_by(name=project_name).first()
                    if project:
                        activity_data['project_id'] = project.id
                    else:
                        # Proje bulunamazsa project_name alanını kullan
                        activity_data['project_name'] = project_name
                
                # Activity oluştur
                activity = Activity(**activity_data)
                db.session.add(activity)
            
            # Kaydet
            db.session.commit()
            print(f"✅ {len(mock_activities)} adet Activity kaydı başarıyla eklendi.")
            
            # Projelerin sağlık skorlarını güncelle
            projects = Project.query.all()
            for project in projects:
                project.update_health()
            db.session.commit()
            print("✅ Proje sağlık skorları güncellendi.")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration hatası: {str(e)}")
            raise


if __name__ == '__main__':
    migrate_mock_data()



