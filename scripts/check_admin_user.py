"""
Admin kullanıcısının ayrıntılarını kontrol et
"""
from models import User
from app import app

with app.app_context():
    # admin kullanıcısı
    admin = User.query.filter_by(username='admin').first()
    
    if admin:
        print(f"Admin Kullanıcı Bilgileri:")
        print(f"="*60)
        print(f"ID: {admin.id}")
        print(f"Username: {admin.username}")
        print(f"Email: {admin.email}")
        print(f"Sistem Rol: {admin.sistem_rol}")
        print(f"Kurum ID: {admin.kurum_id}")
        print(f"Kurum: {admin.kurum.kisa_ad if admin.kurum else 'YOK'}")
        print(f"\nHer İşlemi Kontrol Et:")
        print(f"sistem_rol == 'admin': {admin.sistem_rol == 'admin'}")
        print(f"sistem_rol != 'admin': {admin.sistem_rol != 'admin'}")
    else:
        print("❌ Admin kullanıcısı bulunamadı!")
        print("\nTüm admin kullanıcıları:")
        admins = User.query.filter_by(sistem_rol='admin').all()
        for adm in admins:
            print(f"  - {adm.username} (Kurum: {adm.kurum.kisa_ad})")
