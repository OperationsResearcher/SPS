#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script: Tüm kullanıcı şifrelerini 123456 olarak ayarla ve KMF kurumunu 1KMF yap
"""

from app import create_app
from extensions import db
from models.user import User, Kurum
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("=" * 60)
    print("KULLANICI ŞİFRE VE KMF KURUMU GÜNCELLEME")
    print("=" * 60)
    
    # 1. Tüm kullanıcıların şifrelerini 123456 yap
    print("\n[1] Tüm kullanıcıların şifresi 123456 olarak ayarlanıyor...")
    hashed_pwd = generate_password_hash('123456')
    kullanicilar = User.query.all()
    for k in kullanicilar:
        k.password_hash = hashed_pwd
        print(f"  ✓ {k.username} (ID: {k.id}) şifresi güncellendi")
    
    db.session.commit()
    print(f"✅ Toplam {len(kullanicilar)} kullanıcı güncellendi")
    
    # 2. KMF kurumunu 1KMF olarak değiştir
    print("\n[2] KMF kurumunu 1KMF olarak değiştiriliyor...")
    kmf_kurum = Kurum.query.filter_by(kisa_ad='KMF').first()
    if kmf_kurum:
        kmf_kurum.kisa_ad = '1KMF'
        db.session.commit()
        print(f"✅ Kurum adı değiştirildi: {kmf_kurum.kisa_ad}")
        
        # 3. Bu kurumun altındaki kullanıcıların adlarının başına 1 ekle
        print("\n[3] 1KMF kurumundaki kullanıcıların adlarına 1 ön eki ekleniyor...")
        kmf_users = User.query.filter_by(kurum_id=kmf_kurum.id).all()
        for user in kmf_users:
            eski_ad = user.first_name
            # Eğer zaten 1 ile başlıyorsa ekleme
            if user.first_name and not user.first_name.startswith('1'):
                user.first_name = '1' + user.first_name
                db.session.commit()
                print(f"  ✓ {eski_ad} → {user.first_name}")
            else:
                print(f"  - {user.first_name} (zaten 1 ile başlıyor veya boş)")
        
        print(f"✅ Toplam {len(kmf_users)} kullanıcı adı güncellendi")
    else:
        print("⚠️ KMF kurumu bulunamadı!")
    
    print("\n" + "=" * 60)
    print("GÜNCELLEME TAMAMLANDI")
    print("=" * 60)
