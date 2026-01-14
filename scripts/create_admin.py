# -*- coding: utf-8 -*-
"""
Admin Kullanıcısı Oluşturma Scripti
Sisteme giriş yapabilmek için master admin kullanıcısı oluşturur veya şifresini resetler.
"""
import sys
from werkzeug.security import generate_password_hash

# Uygulama ve modelleri import et
from __init__ import create_app
from models import db, User, Kurum

def create_admin_user():
    """Admin kullanıcısı oluştur veya şifresini resetle"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=" * 60)
            print("ADMIN KULLANICISI OLUSTURMA SCRIPTI")
            print("=" * 60)
            
            # ============================================================
            # 1. KURUM KONTROLÜ VE OLUŞTURMA (İlk kurum veya varsayılan)
            # ============================================================
            print("\n1. Kurum kontrolu yapiliyor...")
            kurum = Kurum.query.first()  # İlk kurumu kullan (tüm sisteme erişim için)
            if not kurum:
                # Hiç kurum yoksa varsayılan bir kurum oluştur
                kurum = Kurum(
                    kisa_ad='Sistem',
                    ticari_unvan='Sistem Yonetimi',
                    faaliyet_alani='Sistem Yonetimi',
                    sektor='Teknoloji',
                    calisan_sayisi=1,
                    email='admin@system.local',
                    telefon='+90 000 000 0000',
                    web_adresi='https://system.local'
                )
                db.session.add(kurum)
                db.session.commit()
                print("   [OK] Varsayilan kurum olusturuldu (ID: {})".format(kurum.id))
            else:
                print("   [OK] Kurum mevcut (ID: {}, Ad: {})".format(kurum.id, kurum.kisa_ad))
            
            # ============================================================
            # 2. ADMIN KULLANICISI KONTROLÜ
            # ============================================================
            print("\n2. Admin kullanici kontrolu yapiliyor...")
            admin_user = User.query.filter_by(username='admin').first()
            
            if admin_user:
                # Kullanıcı varsa şifresini resetle
                print("   [BILGI] 'admin' kullanici adiyla bir kullanici bulundu.")
                print("   [ISLEM] Sifre '123456' olarak resetleniyor...")
                admin_user.password_hash = generate_password_hash('123456')
                admin_user.email = 'admin@system.local'
                admin_user.first_name = 'Sistem'
                admin_user.last_name = 'Yoneticisi'
                admin_user.sistem_rol = 'admin'  # Tüm sisteme erişim için admin rolü
                admin_user.kurum_id = kurum.id  # Kurum bağlantısı zorunlu (ama admin rolü ile tüm kurumlara erişebilir)
                admin_user.title = 'Sistem Yoneticisi'
                db.session.commit()
                print("   [OK] Sifre resetlendi!")
            else:
                # Kullanıcı yoksa oluştur
                print("   [ISLEM] Yeni admin kullanici olusturuluyor...")
                admin_user = User(
                    username='admin',
                    email='admin@system.local',
                    password_hash=generate_password_hash('123456'),
                    first_name='Sistem',
                    last_name='Yoneticisi',
                    sistem_rol='admin',  # Tüm sisteme erişim için admin rolü
                    kurum_id=kurum.id,  # Kurum bağlantısı zorunlu (ama admin rolü ile tüm kurumlara erişebilir)
                    title='Sistem Yoneticisi'
                )
                db.session.add(admin_user)
                db.session.commit()
                print("   [OK] Admin kullanici olusturuldu!")
            
            # ============================================================
            # 3. SONUÇ
            # ============================================================
            print("\n" + "=" * 60)
            print("Basarili!")
            print("=" * 60)
            print("\nAdmin Kullanici Bilgileri:")
            print("  Kullanici Adi: admin")
            print("  Sifre: 123456")
            print("  Email: admin@system.local")
            print("  Kurum: {} (Tum sistemlere erisim hakki var)".format(kurum.kisa_ad))
            print("  Rol: admin (Tum sisteme erisim yetkisi)")
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
    success = create_admin_user()
    sys.exit(0 if success else 1)


