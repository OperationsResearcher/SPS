"""
kmfadmin kullanıcısının bilgilerini kontrol et
"""
from models import User
from app import app

with app.app_context():
    kmfadmin = User.query.filter_by(username='kmfadmin').first()
    admin = User.query.filter_by(username='admin').first()
    
    print("Kullanıcı Karşılaştırması:")
    print("="*60)
    
    if admin:
        print(f"admin:")
        print(f"  - ID: {admin.id}")
        print(f"  - Sistem Rol: {admin.sistem_rol}")
        print(f"  - Kurum ID: {admin.kurum_id}")
        print(f"  - Kurum: {admin.kurum.kisa_ad}")
    
    if kmfadmin:
        print(f"\nkmfadmin:")
        print(f"  - ID: {kmfadmin.id}")
        print(f"  - Sistem Rol: {kmfadmin.sistem_rol}")
        print(f"  - Kurum ID: {kmfadmin.kurum_id}")
        print(f"  - Kurum: {kmfadmin.kurum.kisa_ad}")
        
        print(f"\n{'='*60}")
        print("Sonuç:")
        print(f"  kmfadmin sistem admini mi? {kmfadmin.sistem_rol == 'admin' and kmfadmin.kurum_id == 1}")
        print(f"  kmfadmin kurum admini mi? {kmfadmin.sistem_rol == 'admin' and kmfadmin.kurum_id != 1}")
