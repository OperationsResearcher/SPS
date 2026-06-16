# -*- coding: utf-8 -*-
"""
Güvenli Veritabanı Güncelleme Scripti
-------------------------------------
Mevcut verileri silmeden sadece yeni eklenen Feedback tablosunu veritabanına ekler.
"""
import os
import sys

# Proje kök dizinini Python path'ine ekle
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Flask uygulamasını import et
from __init__ import create_app
from extensions import db
from models import Feedback  # Feedback modelini import et

def update_database():
    """
    Veritabanını günceller - Sadece yeni tabloları ekler, mevcut verileri silmez.
    """
    app = create_app()
    
    with app.app_context():
        print("🔄 Veritabanı güncelleme başlatılıyor...")
        print("-" * 50)
        
        try:
            # Sadece yeni tabloları oluştur (mevcut tablolara dokunmaz)
            db.create_all()
            print("✅ Feedback tablosu başarıyla oluşturuldu/doğrulandı.")
            print("-" * 50)
            print("✅ Veritabanı güncelleme tamamlandı!")
            print("\n📝 Not: Mevcut veriler korundu, sadece yeni tablo eklendi.")
            
        except Exception as e:
            print(f"❌ Hata oluştu: {e}")
            print("-" * 50)
            print("⚠️  Lütfen hata mesajını kontrol edin ve gerekirse manuel müdahale yapın.")
            sys.exit(1)

if __name__ == '__main__':
    update_database()
