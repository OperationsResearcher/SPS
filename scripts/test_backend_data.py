"""
Admin panel route test - backend verilerini kontrol et
"""
from models import db, User, Kurum, Surec
from app import app
from flask import render_template

with app.app_context():
    # Admin kullanıcısı kontrol et
    admin_user = User.query.filter_by(username='admin').first()
    
    if not admin_user:
        print("❌ Admin kullanıcısı bulunamadı!")
        exit(1)
    
    print(f"Admin Kullanıcı: {admin_user.username}")
    print(f"Sistem Rol: {admin_user.sistem_rol}")
    print(f"Kurum ID: {admin_user.kurum_id}")
    
    # Route'deki verileri simüle et
    kurumlar = Kurum.query.all()
    kullanicilar = User.query.all()
    surecler = Surec.query.all()
    
    print(f"\n{'='*60}")
    print(f"Route'tan döndürülecek veriler:")
    print(f"{'='*60}")
    print(f"Kurumlar: {len(kurumlar)}")
    print(f"Kullanıcılar: {len(kullanicilar)}")
    print(f"Süreçler: {len(surecler)}")
    
    # Template render edilirse ne gösterilecek
    print(f"\n{'='*60}")
    print(f"Template'de gösterilen sayılar:")
    print(f"  {{ kurumlar|length }} = {len(kurumlar)}")
    print(f"  {{ kullanicilar|length }} = {len(kullanicilar)}")
    print(f"  {{ surecler|length }} = {len(surecler)}")
