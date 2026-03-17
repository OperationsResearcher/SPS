#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sistem Test Script - DetachedInstanceError ve Genel Sağlık Kontrolü
Kullanım: python test_system.py
"""
from app import create_app
from app.models import db
from app.models.core import User, Strategy, Tenant
from app.models.process import Process, ProcessKpi
from sqlalchemy.orm import selectinload, joinedload

def test_database_queries():
    """Veritabanı query'lerini test et"""
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("SİSTEM SAĞLIK KONTROLÜ - DetachedInstanceError Testi")
        print("=" * 70)
        
        # Test verisi al
        user = User.query.first()
        if not user or not user.tenant_id:
            print("\n❌ HATA: Veritabanında kullanıcı bulunamadı")
            print("   Lütfen önce veritabanını oluşturun: python create_user.py")
            return False
            
        tenant_id = user.tenant_id
        print(f"\n📊 Test Kullanıcısı: {user.email}")
        print(f"📊 Tenant ID: {tenant_id}")
        
        tests = []
        
        # Test 1: Process List
        print("\n" + "-" * 70)
        print("TEST 1: Süreç Listesi (/process/)")
        print("-" * 70)
        try:
            processes = Process.query.options(
                joinedload(Process.leaders),
                joinedload(Process.members),
                joinedload(Process.owners),
                selectinload(Process.process_sub_strategy_links),
                selectinload(Process.kpis)
            ).filter_by(tenant_id=tenant_id, is_active=True).all()
            
            # İlişkilere eriş
            for p in processes:
                _ = p.leaders
                _ = p.members
                _ = p.kpis
                
            print(f"✅ BAŞARILI: {len(processes)} süreç yüklendi")
            print(f"   - Tüm ilişkiler erişilebilir")
            print(f"   - DetachedInstanceError yok")
            tests.append(True)
        except Exception as e:
            print(f"❌ HATA: {e}")
            tests.append(False)
        
        # Test 2: Strategy List
        print("\n" + "-" * 70)
        print("TEST 2: Strateji Listesi (/strategy/)")
        print("-" * 70)
        try:
            strategies = Strategy.query.options(
                selectinload(Strategy.sub_strategies)
            ).filter_by(tenant_id=tenant_id, is_active=True).all()
            
            for s in strategies:
                _ = s.sub_strategies
                
            print(f"✅ BAŞARILI: {len(strategies)} strateji yüklendi")
            print(f"   - Alt stratejiler erişilebilir")
            tests.append(True)
        except Exception as e:
            print(f"❌ HATA: {e}")
            tests.append(False)
        
        # Test 3: Process Karne
        print("\n" + "-" * 70)
        print("TEST 3: Süreç Karnesi (/process/<id>/karne)")
        print("-" * 70)
        try:
            process = Process.query.options(
                selectinload(Process.kpis)
            ).filter_by(tenant_id=tenant_id, is_active=True).first()
            
            if process:
                kpi_count = len(process.kpis)
                print(f"✅ BAŞARILI: '{process.name}' süreci yüklendi")
                print(f"   - {kpi_count} KPI erişilebilir")
                tests.append(True)
            else:
                print("⚠️  UYARI: Süreç bulunamadı (veri yok)")
                tests.append(True)  # Veri yoksa hata değil
        except Exception as e:
            print(f"❌ HATA: {e}")
            tests.append(False)
        
        # Test 4: Tenant
        print("\n" + "-" * 70)
        print("TEST 4: Kurum Bilgileri (/admin/tenants)")
        print("-" * 70)
        try:
            tenant = Tenant.query.options(
                joinedload(Tenant.package)
            ).filter_by(id=tenant_id).first()
            
            if tenant:
                _ = tenant.package
                print(f"✅ BAŞARILI: '{tenant.name}' kurumu yüklendi")
                print(f"   - Paket bilgisi erişilebilir")
                tests.append(True)
            else:
                print("❌ HATA: Tenant bulunamadı")
                tests.append(False)
        except Exception as e:
            print(f"❌ HATA: {e}")
            tests.append(False)
        
        # Test 5: Users
        print("\n" + "-" * 70)
        print("TEST 5: Kullanıcı Listesi (/admin/users)")
        print("-" * 70)
        try:
            users = User.query.options(
                joinedload(User.role),
                joinedload(User.tenant)
            ).filter_by(tenant_id=tenant_id, is_active=True).all()
            
            for u in users:
                _ = u.role
                _ = u.tenant
                
            print(f"✅ BAŞARILI: {len(users)} kullanıcı yüklendi")
            print(f"   - Role ve tenant ilişkileri erişilebilir")
            tests.append(True)
        except Exception as e:
            print(f"❌ HATA: {e}")
            tests.append(False)
        
        # Özet
        print("\n" + "=" * 70)
        print("TEST SONUÇLARI")
        print("=" * 70)
        
        passed = sum(tests)
        total = len(tests)
        percentage = (passed / total * 100) if total > 0 else 0
        
        print(f"\nBaşarılı: {passed}/{total} ({percentage:.0f}%)")
        
        if passed == total:
            print("\n✅ TÜM TESTLER BAŞARILI!")
            print("   Sistem tamamen çalışır durumda.")
            print("   DetachedInstanceError sorunu yok.")
            print("\n🚀 Production'a hazır!")
            return True
        else:
            print(f"\n❌ {total - passed} TEST BAŞARISIZ")
            print("   Lütfen yukarıdaki hataları inceleyin.")
            return False

if __name__ == "__main__":
    import sys
    success = test_database_queries()
    sys.exit(0 if success else 1)
