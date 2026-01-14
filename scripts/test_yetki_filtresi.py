"""
Admin panel yetkilendirmesini test et
"""
from models import User, Kurum, Surec
from app import app

def test_admin_panel_data(username):
    """Belirli kullanıcı için admin panel verilerini simüle et"""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"❌ {username} bulunamadı!")
            return
        
        print(f"\n{'='*60}")
        print(f"Kullanıcı: {username}")
        print(f"Rol: {user.sistem_rol}")
        print(f"Kurum ID: {user.kurum_id}")
        print(f"Kurum: {user.kurum.kisa_ad}")
        print(f"{'='*60}")
        
        # Sistem admini mi kontrol et
        is_system_admin = user.sistem_rol == 'admin' and user.kurum_id == 1
        
        print(f"Sistem Admini: {is_system_admin}")
        
        # Verileri filtrele
        if is_system_admin:
            kurumlar = Kurum.query.all()
            kullanicilar = User.query.all()
            surecler = Surec.query.all()
        else:
            kurumlar = Kurum.query.filter_by(id=user.kurum_id).all()
            kullanicilar = User.query.filter_by(kurum_id=user.kurum_id).all()
            surecler = Surec.query.filter_by(kurum_id=user.kurum_id).all()
        
        print(f"\nGörünen Veriler:")
        print(f"  Kurumlar: {len(kurumlar)}")
        for k in kurumlar:
            print(f"    - {k.kisa_ad}")
        print(f"  Kullanıcılar: {len(kullanicilar)}")
        print(f"  Süreçler: {len(surecler)}")

# Test kullanıcıları
test_admin_panel_data('admin')
test_admin_panel_data('kmfadmin')
test_admin_panel_data('burak')  # KalDer Eskisehir kurum yoneticisi
