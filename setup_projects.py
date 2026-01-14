# -*- coding: utf-8 -*-
"""
Proje Seed Scripti
Stratejik Proje Portföyü için test verileri oluşturur.
"""
import sys
from datetime import datetime, date, timedelta
from __init__ import create_app
from models import db, Project, Process, User, Kurum

def setup_projects():
    """Kurum ID 87 için dummy projeler oluştur"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=" * 60)
            print("PROJE SEED VERILERI OLUSTURMA")
            print("=" * 60)
            
            # Kurum kontrolü
            kurum = Kurum.query.get(87)
            if not kurum:
                print("[HATA] Kurum ID 87 bulunamadi!")
                return False
            
            # Mevcut proje sayısını kontrol et
            existing_count = Project.query.filter_by(kurum_id=87).count()
            print(f"\n[Mevcut proje sayisi: {existing_count}]")
            
            if existing_count >= 3:
                print("[BILGI] Yeterli proje mevcut, seed atlaniyor.")
                return True
            
            # Süreçleri çek
            processes = Process.query.filter_by(kurum_id=87).limit(5).all()
            if len(processes) < 2:
                print("[HATA] Yeterli surec bulunamadi (en az 2 surec gerekli)")
                return False
            
            # Admin kullanıcısını bul
            admin_user = User.query.filter_by(username='kmfadmin', kurum_id=87).first()
            if not admin_user:
                admin_user = User.query.filter_by(kurum_id=87).first()
            
            if not admin_user:
                print("[HATA] Kullanici bulunamadi!")
                return False
            
            # Dummy projeler
            projects_data = [
                {
                    'name': 'Dijital Dönüşüm Projesi',
                    'description': 'Kurumsal dijital dönüşüm sürecini hızlandıracak kapsamlı proje',
                    'start_date': date.today() - timedelta(days=30),
                    'end_date': date.today() + timedelta(days=90),
                    'priority': 'Yüksek',
                    'processes': processes[:2]  # İlk 2 süreç
                },
                {
                    'name': 'Müşteri Memnuniyeti Artırma',
                    'description': 'Müşteri deneyimini iyileştirmek için stratejik proje',
                    'start_date': date.today() - timedelta(days=15),
                    'end_date': date.today() + timedelta(days=60),
                    'priority': 'Orta',
                    'processes': processes[1:3] if len(processes) >= 3 else processes[:1]
                },
                {
                    'name': 'Operasyonel Verimlilik',
                    'description': 'İş süreçlerini optimize ederek maliyetleri düşürme projesi',
                    'start_date': date.today(),
                    'end_date': date.today() + timedelta(days=120),
                    'priority': 'Kritik',
                    'processes': processes[2:4] if len(processes) >= 4 else processes[:2]
                },
                {
                    'name': 'Yenilikçi Ürün Geliştirme',
                    'description': 'Pazar ihtiyaçlarına yönelik yeni ürün tasarımı',
                    'start_date': date.today() + timedelta(days=7),
                    'end_date': date.today() + timedelta(days=150),
                    'priority': 'Orta',
                    'processes': processes[3:5] if len(processes) >= 5 else processes[:2]
                },
                {
                    'name': 'Sürdürülebilirlik İnisiyatifi',
                    'description': 'Çevresel etkiyi azaltmak için yeşil proje',
                    'start_date': date.today() - timedelta(days=10),
                    'end_date': date.today() + timedelta(days=180),
                    'priority': 'Yüksek',
                    'processes': processes[:3] if len(processes) >= 3 else processes
                }
            ]
            
            created = 0
            for proj_data in projects_data:
                # Proje zaten var mı kontrol et
                existing = Project.query.filter_by(name=proj_data['name'], kurum_id=87).first()
                if existing:
                    print(f"  [ATLANDI] {proj_data['name']} zaten mevcut")
                    continue
                
                project = Project(
                    name=proj_data['name'],
                    description=proj_data['description'],
                    start_date=proj_data['start_date'],
                    end_date=proj_data['end_date'],
                    priority=proj_data['priority'],
                    kurum_id=87,
                    manager_id=admin_user.id
                )
                db.session.add(project)
                db.session.flush()  # ID'yi almak için
                
                # Süreçleri ilişkilendir
                for process in proj_data['processes']:
                    if process not in project.related_processes:
                        project.related_processes.append(process)
                
                created += 1
                print(f"  [OK] {proj_data['name']} olusturuldu ({len(proj_data['processes'])} surec ile)")
            
            db.session.commit()
            print(f"\n[BASARILI] {created} proje olusturuldu!")
            return True
            
        except Exception as e:
            import traceback
            print(f"\n[HATA] {str(e)}")
            print(traceback.format_exc())
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = setup_projects()
    sys.exit(0 if success else 1)

