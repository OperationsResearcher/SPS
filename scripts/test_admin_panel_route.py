"""
Admin panel route'unu test et
"""
from models import db, Kurum, User, Surec
from app import app
from flask_login import login_user

with app.app_context():
    # Admin kullanıcı
    admin_user = User.query.filter_by(username='admin').first()
    
    if not admin_user:
        print("❌ Admin kullanıcısı bulunamadı!")
        exit(1)
    
    # Route'u simüle et
    kurumlar = Kurum.query.all()
    kullanicilar = User.query.all()
    surecler = Surec.query.all()
    
    print(f"Admin Panel'e gönderilecek veri:")
    print(f"{'='*60}")
    print(f"Kurumlar: {len(kurumlar)}")
    for k in kurumlar:
        print(f"  - {k.kisa_ad}")
    
    print(f"\nKullanıcılar: {len(kullanicilar)}")
    print(f"Süreçler: {len(surecler)}")
    
    print(f"\nAdmin Kullanıcısı: {admin_user.username}")
    print(f"Admin Sistem Rol: {admin_user.sistem_rol}")
    
    # test client ile route'u çağır
    with app.test_client() as client:
        # Giriş yap
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_user.id)
        
        # Route'u çağır
        response = client.get('/admin-panel')
        
        print(f"\n\nRoute Çağrısı:")
        print(f"{'='*60}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # HTML'de kurumlar var mı kontrol et
            html = response.data.decode('utf-8')
            kurum_names = ['KalDer Eskisehir', 'Eskisehir Dikiz', 'Demo Teknoloji']
            
            print(f"\nHTML'de kurumların varlığı:")
            for name in kurum_names:
                if name in html:
                    print(f"  ✓ {name} var")
                else:
                    print(f"  ✗ {name} YOK")
            
            # Kullanıcılar var mı kontrol et
            user_names = ['burak', 'Ali', 'veli', 'ahmet']
            print(f"\nHTML'de kullanıcıların varlığı:")
            for name in user_names:
                if name in html:
                    print(f"  ✓ {name} var")
                else:
                    print(f"  ✗ {name} YOK")
        else:
            print(f"Hata! Response: {response.data.decode('utf-8')[:200]}")
