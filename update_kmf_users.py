#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script: 1KMF kurumundaki kullanıcıların adlarının başına 1 ekle
"""

from app import create_app
from extensions import db
from models.user import User, Kurum

app = create_app()

with app.app_context():
    print("=" * 60)
    print("1KMF KULLANICI ADLARI GÜNCELLEME")
    print("=" * 60)
    
    kmf_kurum = Kurum.query.filter_by(kisa_ad='1KMF').first()
    if kmf_kurum:
        print(f"\n🔍 Kurum: {kmf_kurum.kisa_ad} (ID: {kmf_kurum.id})")
        
        kmf_users = User.query.filter_by(kurum_id=kmf_kurum.id).all()
        print(f"📊 Toplam {len(kmf_users)} kullanıcı bulundu\n")
        
        for user in kmf_users:
            if user.first_name:
                eski_ad = user.first_name
                # Eğer zaten 1 ile başlıyorsa ekleme
                if not user.first_name.startswith('1'):
                    user.first_name = '1' + user.first_name
                    db.session.commit()
                    print(f"  ✓ '{eski_ad}' → '{user.first_name}'")
                else:
                    print(f"  - '{user.first_name}' (zaten 1 ile başlıyor)")
            else:
                print(f"  - {user.username} (ad boş)")
        
        print(f"\n✅ Güncelleme tamamlandı")
    else:
        print("❌ 1KMF kurumu bulunamadı!")
    
    print("\n" + "=" * 60)
