#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Logo Optimizasyon Scripti
static/kokpitlogo.png dosyasını web için optimize eder.
"""

import os
import sys
from PIL import Image

# Windows terminal encoding sorununu çöz
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def optimize_logo():
    logo_path = 'static/kokpitlogo.png'
    
    # Dosya var mı kontrol et
    if not os.path.exists(logo_path):
        print(f"❌ HATA: {logo_path} dosyası bulunamadı!")
        return
    
    # Orijinal dosya boyutunu al
    original_size = os.path.getsize(logo_path)
    print(f"📁 Orijinal dosya boyutu: {original_size / 1024:.2f} KB")
    
    try:
        # Resmi aç
        print(f"🖼️  Resim açılıyor: {logo_path}")
        img = Image.open(logo_path)
        
        # Orijinal boyutları göster
        original_width, original_height = img.size
        print(f"📐 Orijinal boyutlar: {original_width}x{original_height} px")
        
        # Yeni genişlik
        new_width = 400
        # Yüksekliği orantılı hesapla
        aspect_ratio = original_height / original_width
        new_height = int(new_width * aspect_ratio)
        
        print(f"📐 Yeni boyutlar: {new_width}x{new_height} px")
        
        # Resmi yeniden boyutlandır (Lanczos filtresi - yüksek kalite)
        print("🔄 Resim yeniden boyutlandırılıyor...")
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Optimize ederek kaydet
        print("💾 Optimize edilmiş resim kaydediliyor...")
        img_resized.save(
            logo_path,
            'PNG',
            optimize=True,
            compress_level=9  # Maksimum sıkıştırma
        )
        
        # Yeni dosya boyutunu al
        new_size = os.path.getsize(logo_path)
        print(f"📁 Yeni dosya boyutu: {new_size / 1024:.2f} KB")
        
        # Karşılaştırma
        size_reduction = original_size - new_size
        reduction_percent = (size_reduction / original_size) * 100
        
        print("\n" + "="*50)
        print("✅ OPTİMİZASYON TAMAMLANDI!")
        print("="*50)
        print(f"📉 Boyut azalması: {size_reduction / 1024:.2f} KB")
        print(f"📊 Yüzde azalma: {reduction_percent:.1f}%")
        print(f"🎯 Hedef genişlik: {new_width}px (başarılı)")
        print("="*50)
        
    except Exception as e:
        print(f"❌ HATA: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("🚀 Logo Optimizasyon Başlatılıyor...\n")
    optimize_logo()
