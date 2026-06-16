# -*- coding: utf-8 -*-
"""
CDN'den statik dosyaları indirip yerel static klasörüne kopyalar.
İnternet bağlantısı olmadığında uygulamanın çalışması için gereklidir.
"""
import os
import urllib.request
import shutil
from pathlib import Path

# Static klasör yolu
STATIC_DIR = Path('static')
VENDOR_DIR = STATIC_DIR / 'vendor'

# İndirilecek dosyalar
FILES_TO_DOWNLOAD = {
    # Bootstrap CSS
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css': 
        STATIC_DIR / 'vendor' / 'bootstrap' / 'bootstrap.min.css',
    
    # Bootstrap JS Bundle
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js': 
        STATIC_DIR / 'vendor' / 'bootstrap' / 'bootstrap.bundle.min.js',
    
    # Bootstrap Icons CSS
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css': 
        STATIC_DIR / 'vendor' / 'bootstrap-icons' / 'bootstrap-icons.css',
    
    # Bootstrap Icons Font Files (WOFF2)
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/fonts/bootstrap-icons.woff2': 
        STATIC_DIR / 'vendor' / 'bootstrap-icons' / 'fonts' / 'bootstrap-icons.woff2',
    
    # Font Awesome CSS
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css': 
        STATIC_DIR / 'vendor' / 'fontawesome' / 'all.min.css',
    
    # Font Awesome Font Files (WOFF2 - ana font dosyası)
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-solid-900.woff2': 
        STATIC_DIR / 'vendor' / 'fontawesome' / 'webfonts' / 'fa-solid-900.woff2',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-regular-400.woff2': 
        STATIC_DIR / 'vendor' / 'fontawesome' / 'webfonts' / 'fa-regular-400.woff2',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-brands-400.woff2': 
        STATIC_DIR / 'vendor' / 'fontawesome' / 'webfonts' / 'fa-brands-400.woff2',
    
    # jQuery
    'https://code.jquery.com/jquery-3.7.1.min.js': 
        STATIC_DIR / 'vendor' / 'jquery' / 'jquery-3.7.1.min.js',
    
    # Chart.js
    'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js': 
        STATIC_DIR / 'vendor' / 'chartjs' / 'chart.umd.js',

    # vis-network (graph visualization)
    'https://cdn.jsdelivr.net/npm/vis-network@9.1.9/styles/vis-network.min.css':
        STATIC_DIR / 'vendor' / 'vis-network' / 'vis-network.min.css',
    'https://cdn.jsdelivr.net/npm/vis-network@9.1.9/standalone/umd/vis-network.min.js':
        STATIC_DIR / 'vendor' / 'vis-network' / 'vis-network.min.js',
}

def download_file(url, dest_path):
    """Bir dosyayı URL'den indirir ve belirtilen yola kaydeder."""
    try:
        # Klasörü oluştur
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"İndiriliyor: {url}")
        print(f"Kaydediliyor: {dest_path}")
        
        # Dosyayı indir
        urllib.request.urlretrieve(url, dest_path)
        print(f"✓ Başarıyla indirildi: {dest_path.name}\n")
        return True
    except Exception as e:
        print(f"✗ Hata: {url} - {str(e)}\n")
        return False

def fix_bootstrap_icons_css(css_path):
    """Bootstrap Icons CSS dosyasındaki font yollarını düzeltir."""
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Font yollarını düzelt (göreceli yolları mutlak yollara çevir)
        # Bootstrap Icons CSS'inde genellikle '../fonts/' veya './fonts/' kullanılır
        content = content.replace('../fonts/', 'fonts/')
        content = content.replace('./fonts/', 'fonts/')
        
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Bootstrap Icons CSS font yolları düzeltildi\n")
        return True
    except Exception as e:
        print(f"⚠ Bootstrap Icons CSS düzeltilemedi: {str(e)}\n")
        return False

def fix_fontawesome_css(css_path):
    """Font Awesome CSS dosyasındaki font yollarını düzeltir."""
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Font yollarını düzelt (CDN yollarını yerel yollara çevir)
        # Font Awesome CSS'inde genellikle '../webfonts/' veya './webfonts/' kullanılır
        content = content.replace('../webfonts/', 'webfonts/')
        content = content.replace('./webfonts/', 'webfonts/')
        # CDN yollarını da yerel yollara çevir
        content = content.replace('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/', 'webfonts/')
        
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Font Awesome CSS font yolları düzeltildi\n")
        return True
    except Exception as e:
        print(f"⚠ Font Awesome CSS düzeltilemedi: {str(e)}\n")
        return False

def main():
    print("=" * 60)
    print("Statik Dosyaları İndirme Scripti")
    print("=" * 60)
    print()
    
    # Static klasörünü oluştur
    STATIC_DIR.mkdir(exist_ok=True)
    
    success_count = 0
    fail_count = 0
    
    for url, dest_path in FILES_TO_DOWNLOAD.items():
        if download_file(url, dest_path):
            success_count += 1
        else:
            fail_count += 1
    
    # Bootstrap Icons CSS dosyasını düzelt
    bootstrap_icons_css = STATIC_DIR / 'vendor' / 'bootstrap-icons' / 'bootstrap-icons.css'
    if bootstrap_icons_css.exists():
        fix_bootstrap_icons_css(bootstrap_icons_css)
    
    # Font Awesome CSS dosyasını düzelt
    fontawesome_css = STATIC_DIR / 'vendor' / 'fontawesome' / 'all.min.css'
    if fontawesome_css.exists():
        fix_fontawesome_css(fontawesome_css)
    
    print("=" * 60)
    print(f"İndirme Tamamlandı!")
    print(f"Başarılı: {success_count}")
    print(f"Başarısız: {fail_count}")
    print("=" * 60)
    
    if fail_count == 0:
        print("\n✓ Tüm dosyalar başarıyla indirildi!")
        print("Artık uygulama internet bağlantısı olmadan da çalışacak.")
    else:
        print(f"\n⚠ {fail_count} dosya indirilemedi. Lütfen internet bağlantınızı kontrol edin.")
        print("İnternet bağlantısı olduğunda bu scripti tekrar çalıştırın.")

if __name__ == '__main__':
    main()

