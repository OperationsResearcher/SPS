# -*- coding: utf-8 -*-
"""
KMF Admin Kullanıcısı Oluşturma Scripti
ID 87'ye bağlı özel admin kullanıcısı oluşturur veya günceller.
"""
import sys
from werkzeug.security import generate_password_hash

# Uygulama ve modelleri import et
from __init__ import create_app
from models import db, User, Process

def create_kmf_admin():
    """KMF Admin kullanıcısı oluştur veya güncelle"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=" * 60)
            print("KMF ADMIN KULLANICISI OLUSTURMA")
            print("=" * 60)
            
            # ============================================================
            # 1. KULLANICI KONTROLÜ
            # ============================================================
            print("\n1. Kullanici kontrolu yapiliyor...")
            kmf_admin = User.query.filter_by(username='kmfadmin').first()
            
            if kmf_admin:
                # Kullanıcı varsa güncelle
                print("   [BILGI] 'kmfadmin' kullanici adiyla bir kullanici bulundu.")
                print("   [ISLEM] kurum_id 87 olarak guncelleniyor ve sifre resetleniyor...")
                kmf_admin.kurum_id = 87
                kmf_admin.password_hash = generate_password_hash('123456')
                kmf_admin.email = 'kmfadmin@kmf.org.tr'
                kmf_admin.first_name = 'KMF'
                kmf_admin.last_name = 'Admin'
                kmf_admin.sistem_rol = 'admin'
                kmf_admin.title = 'KMF Sistem Yoneticisi'
                db.session.commit()
                print("   [OK] Kullanici guncellendi!")
            else:
                # Kullanıcı yoksa oluştur
                print("   [ISLEM] Yeni 'kmfadmin' kullanici olusturuluyor...")
                kmf_admin = User(
                    username='kmfadmin',
                    email='kmfadmin@kmf.org.tr',
                    password_hash=generate_password_hash('123456'),
                    first_name='KMF',
                    last_name='Admin',
                    sistem_rol='admin',
                    kurum_id=87,
                    title='KMF Sistem Yoneticisi'
                )
                db.session.add(kmf_admin)
                db.session.commit()
                print("   [OK] Kullanici olusturuldu!")
            
            # ============================================================
            # 2. VERIFICATION (Süreç Sayısı Kontrolü)
            # ============================================================
            print("\n2. Verification yapiliyor...")
            process_count = Process.query.filter_by(kurum_id=87).count()
            
            # ============================================================
            # 3. SONUÇ
            # ============================================================
            print("\n" + "=" * 60)
            print("BASARILI!")
            print("=" * 60)
            print("\nKULLANICI HAZIR: kmfadmin / 123456")
            print("BAGLI KURUM ID: 87")
            print("GOREBILECEGI SUREC SAYISI: {}".format(process_count))
            print("\n" + "=" * 60)
            print("Sisteme giris yapabilirsiniz!")
            print("=" * 60 + "\n")
            
            return True
            
        except Exception as e:
            import traceback
            print("\n" + "=" * 60)
            print("HATA!")
            print("=" * 60)
            print("Hata mesaji: {}".format(str(e)))
            print("\nDetayli hata:")
            print(traceback.format_exc())
            print("=" * 60 + "\n")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = create_kmf_admin()
    sys.exit(0 if success else 1)


