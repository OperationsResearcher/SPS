# -*- coding: utf-8 -*-
"""
Demo Veri Oluşturma Scripti
Sistemi test edilebilir hale getirmek için demo veriler oluşturur.
Mevcut verileri silmeden, yoksa ekler.
"""
import sys
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash

# Uygulama ve modelleri import et
from __init__ import create_app
from models import (
    db, User, Kurum, Project, Task, ProjectRisk, Surec, SurecPerformansGostergesi,
    BireyselPerformansGostergesi, PerformansGostergeVeri
)

def create_demo_data():
    """Demo verileri oluştur"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🚀 Demo veriler oluşturuluyor...")
            
            # ============================================================
            # 1. KURUM OLUŞTUR
            # ============================================================
            print("1. Kurum kontrol ediliyor...")
            kurum = Kurum.query.filter_by(kisa_ad='Demo Teknoloji A.Ş.').first()
            if not kurum:
                kurum = Kurum(
                    kisa_ad='Demo Teknoloji A.Ş.',
                    ticari_unvan='Demo Teknoloji Anonim Şirketi',
                    faaliyet_alani='Yazılım Geliştirme ve Danışmanlık',
                    sektor='Teknoloji',
                    calisan_sayisi=150,
                    email='info@demoteknoloji.com',
                    telefon='+90 212 555 0100',
                    web_adresi='https://www.demoteknoloji.com'
                )
                db.session.add(kurum)
                db.session.commit()
                print("   ✅ Kurum oluşturuldu: Demo Teknoloji A.Ş.")
            else:
                print("   ℹ️  Kurum zaten mevcut: Demo Teknoloji A.Ş.")
            
            # ============================================================
            # 2. KULLANICILAR OLUŞTUR
            # ============================================================
            print("2. Kullanıcılar kontrol ediliyor...")
            users_data = [
                {
                    'username': 'demo_admin',
                    'email': 'admin@demoteknoloji.com',
                    'first_name': 'Demo',
                    'last_name': 'Admin',
                    'sistem_rol': 'admin',
                    'title': 'Sistem Yöneticisi'
                },
                {
                    'username': 'demo_yonetici',
                    'email': 'yonetici@demoteknoloji.com',
                    'first_name': 'Demo',
                    'last_name': 'Yönetici',
                    'sistem_rol': 'kurum_yoneticisi',
                    'title': 'Proje Yöneticisi'
                },
                {
                    'username': 'demo_uzman',
                    'email': 'uzman@demoteknoloji.com',
                    'first_name': 'Demo',
                    'last_name': 'Uzman',
                    'sistem_rol': 'kurum_kullanici',
                    'title': 'Yazılım Uzmanı'
                }
            ]
            
            created_users = {}
            for user_data in users_data:
                user = User.query.filter_by(username=user_data['username']).first()
                if not user:
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        password_hash=generate_password_hash('123456'),
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        sistem_rol=user_data['sistem_rol'],
                        title=user_data['title'],
                        kurum_id=kurum.id
                    )
                    db.session.add(user)
                    db.session.commit()
                    print(f"   ✅ Kullanıcı oluşturuldu: {user_data['username']} (Şifre: 123456)")
                else:
                    print(f"   ℹ️  Kullanıcı zaten mevcut: {user_data['username']}")
                created_users[user_data['username']] = user
            
            # ============================================================
            # 3. PROJE OLUŞTUR
            # ============================================================
            print("3. Proje kontrol ediliyor...")
            project = Project.query.filter_by(name='Dijital Dönüşüm 2025').first()
            if not project:
                start_date = date.today() - timedelta(days=30)  # 1 ay önce
                end_date = date.today() + timedelta(days=60)  # 2 ay sonra
                
                project = Project(
                    kurum_id=kurum.id,
                    name='Dijital Dönüşüm 2025',
                    manager_id=created_users['demo_yonetici'].id,
                    description='Kurumsal dijital dönüşüm sürecini yönetmek için kapsamlı bir proje. Tüm departmanların dijitalleşmesi ve süreç optimizasyonu hedeflenmektedir.',
                    start_date=start_date,
                    end_date=end_date,
                    priority='Yüksek'
                )
                db.session.add(project)
                db.session.flush()
                
                # Proje üyelerini ekle
                project.members.append(created_users['demo_uzman'])
                db.session.commit()
                print("   ✅ Proje oluşturuldu: Dijital Dönüşüm 2025")
            else:
                print("   ℹ️  Proje zaten mevcut: Dijital Dönüşüm 2025")
            
            # ============================================================
            # 4. GÖREVLER OLUŞTUR
            # ============================================================
            print("4. Görevler oluşturuluyor...")
            tasks_data = [
                {
                    'title': 'İhtiyaç Analizi',
                    'description': 'Mevcut sistemlerin analizi ve ihtiyaçların belirlenmesi',
                    'due_date': date.today() - timedelta(days=20),
                    'priority': 'Yüksek',
                    'status': 'Tamamlandı',
                    'order': 1
                },
                {
                    'title': 'Sistem Tasarımı',
                    'description': 'Yeni sistem mimarisinin tasarlanması ve dokümantasyonu',
                    'due_date': date.today() - timedelta(days=5),
                    'priority': 'Yüksek',
                    'status': 'Devam Ediyor',
                    'order': 2
                },
                {
                    'title': 'Geliştirme (Kodlama)',
                    'description': 'Backend ve frontend geliştirme işlemleri',
                    'due_date': date.today() + timedelta(days=20),
                    'priority': 'Orta',
                    'status': 'Yapılacak',
                    'order': 3
                },
                {
                    'title': 'Test ve Kalite Kontrolü',
                    'description': 'Birim testleri, entegrasyon testleri ve kullanıcı kabul testleri',
                    'due_date': date.today() + timedelta(days=40),
                    'priority': 'Yüksek',
                    'status': 'Yapılacak',
                    'order': 4
                },
                {
                    'title': 'Canlıya Alma ve Eğitim',
                    'description': 'Sistemin canlıya alınması ve kullanıcı eğitimleri',
                    'due_date': date.today() + timedelta(days=55),
                    'priority': 'Kritik',
                    'status': 'Yapılacak',
                    'order': 5
                }
            ]
            
            created_tasks = []
            for task_data in tasks_data:
                # Aynı isimde görev var mı kontrol et
                existing = Task.query.filter_by(
                    project_id=project.id,
                    title=task_data['title']
                ).first()
                
                if not existing:
                    task = Task(
                        project_id=project.id,
                        assigned_to_id=created_users['demo_uzman'].id,
                        title=task_data['title'],
                        description=task_data['description'],
                        due_date=task_data['due_date'],
                        priority=task_data['priority'],
                        status=task_data['status']
                    )
                    db.session.add(task)
                    db.session.commit()
                    created_tasks.append(task)
                    print(f"   ✅ Görev oluşturuldu: {task_data['title']}")
                else:
                    created_tasks.append(existing)
                    print(f"   ℹ️  Görev zaten mevcut: {task_data['title']}")
            
            # ============================================================
            # 5. RİSKLER OLUŞTUR
            # ============================================================
            print("5. Riskler oluşturuluyor...")
            risks_data = [
                {
                    'title': 'Teknoloji Uyumsuzluğu',
                    'description': 'Mevcut sistemlerle entegrasyon sırasında uyumsuzluk riski',
                    'impact': 5,
                    'probability': 3,
                    'mitigation_plan': 'Detaylı teknik analiz yapılacak ve pilot testler uygulanacak',
                    'status': 'Aktif'
                },
                {
                    'title': 'Kullanıcı Direnci',
                    'description': 'Yeni sisteme geçişte kullanıcıların adaptasyon sorunları',
                    'impact': 2,
                    'probability': 2,
                    'mitigation_plan': 'Kapsamlı eğitim programları ve destek ekibi oluşturulacak',
                    'status': 'Aktif'
                }
            ]
            
            for risk_data in risks_data:
                existing = ProjectRisk.query.filter_by(
                    project_id=project.id,
                    title=risk_data['title']
                ).first()
                
                if not existing:
                    risk = ProjectRisk(
                        project_id=project.id,
                        created_by_id=created_users['demo_yonetici'].id,
                        title=risk_data['title'],
                        description=risk_data['description'],
                        impact=risk_data['impact'],
                        probability=risk_data['probability'],
                        mitigation_plan=risk_data['mitigation_plan'],
                        status=risk_data['status']
                    )
                    db.session.add(risk)
                    db.session.commit()
                    print(f"   ✅ Risk oluşturuldu: {risk_data['title']} (Skor: {risk_data['impact'] * risk_data['probability']})")
                else:
                    print(f"   ℹ️  Risk zaten mevcut: {risk_data['title']}")
            
            # ============================================================
            # 6. SÜREÇ VE PERFORMANS GÖSTERGESİ (OPSİYONEL)
            # ============================================================
            print("6. Süreç ve performans göstergesi oluşturuluyor...")
            surec = Surec.query.filter_by(ad='Dijital Dönüşüm Süreci').first()
            if not surec:
                surec = Surec(
                    kurum_id=kurum.id,
                    ad='Dijital Dönüşüm Süreci',
                    durum='Aktif',
                    ilerleme=45,
                    aciklama='Dijital dönüşüm projesi için ana süreç'
                )
                db.session.add(surec)
                db.session.flush()
                
                # Süreç lideri ekle
                surec.liderler.append(created_users['demo_yonetici'])
                
                # Performans göstergesi ekle
                pg = SurecPerformansGostergesi(
                    surec_id=surec.id,
                    ad='Dijitalleşme Oranı',
                    aciklama='Kurumsal süreçlerin dijitalleşme yüzdesi',
                    hedef_deger='80',
                    olcum_birimi='Yüzde',
                    periyot='Aylik',
                    veri_toplama_yontemi='Ortalama'
                )
                db.session.add(pg)
                db.session.commit()
                print("   ✅ Süreç ve performans göstergesi oluşturuldu")
            else:
                print("   ℹ️  Süreç zaten mevcut: Dijital Dönüşüm Süreci")
            
            print("\n✅ Demo veriler başarıyla yüklendi.")
            print("\n📋 Giriş Bilgileri:")
            print("   - demo_admin / 123456 (Admin)")
            print("   - demo_yonetici / 123456 (Proje Yöneticisi)")
            print("   - demo_uzman / 123456 (Yazılım Uzmanı)")
            print("\n🎯 Oluşturulan Veriler:")
            print(f"   - Kurum: Demo Teknoloji A.Ş.")
            print(f"   - Proje: Dijital Dönüşüm 2025")
            print(f"   - Görevler: {len(created_tasks)} adet")
            print(f"   - Riskler: 2 adet (1 Kritik, 1 Düşük)")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Hata oluştu: {str(e)}")
            import traceback
            print(traceback.format_exc())
            sys.exit(1)


if __name__ == '__main__':
    create_demo_data()





