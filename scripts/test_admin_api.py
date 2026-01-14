"""
Admin API'yi test et - Hangi kullanıcı hangi sonucu alıyor?
"""
from models import db, User, Kurum
from app import app
from flask import session
from flask_login import login_user
import json

def test_with_user(username):
    """Belirli bir kullanıcı ile API test et"""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"❌ {username} kullanıcısı bulunamadı!")
            return
        
        print(f"\n{'='*60}")
        print(f"Kullanıcı: {username}")
        print(f"Rol: {user.sistem_rol}")
        print(f"Kurum ID: {user.kurum_id}")
        print(f"Kurum: {user.kurum.kisa_ad if user.kurum else 'YOK'}")
        print(f"{'='*60}")
        
        # Test client oluştur
        with app.test_client() as client:
            # Login ol
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
            
            # API'yi çağır
            response = client.get('/api/admin/users')
            
            print(f"\nAPI Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = json.loads(response.data)
                if data.get('success'):
                    users = data.get('data', {}).get('users', [])
                    print(f"✅ Görünen kullanıcı sayısı: {len(users)}")
                    print(f"\nKullanıcılar:")
                    for u in users[:10]:  # İlk 10'unu göster
                        print(f"  - {u['username']} ({u['sistem_rol']}) - Kurum: {u.get('kurum_adi', 'YOK')}")
                    if len(users) > 10:
                        print(f"  ... ve {len(users)-10} kullanıcı daha")
                else:
                    print(f"❌ API Hatası: {data.get('message')}")
            else:
                print(f"❌ HTTP Hatası: {response.status_code}")
                print(response.data.decode('utf-8'))

if __name__ == '__main__':
    # Admin kullanıcısını test et
    test_with_user('admin')
    
    # Diğer kullanıcıları test et
    test_with_user('burak')  # kurum_yoneticisi
    test_with_user('Ali')    # kurum_kullanici
