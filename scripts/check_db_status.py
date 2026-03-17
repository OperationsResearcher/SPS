from models import db, Kurum, User
from app import app

with app.app_context():
    print(f'Toplam Kurum: {Kurum.query.count()}')
    print(f'Toplam Kullanıcı: {User.query.count()}')
    
    print('\n=== KURUMLAR ===')
    kurumlar = Kurum.query.all()
    for kurum in kurumlar:
        print(f'  - {kurum.kisa_ad} / {kurum.ticari_unvan} (ID: {kurum.id})')
    
    print('\n=== KULLANICILAR ===')
    users = User.query.all()
    for user in users:
        kurum_name = user.kurum.kisa_ad if user.kurum else 'YOK'
        print(f'  - {user.username} | Rol: {user.sistem_rol} | Kurum: {kurum_name} (ID: {user.kurum_id})')
