#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Production Readiness Check Script
Bu script, uygulamanın production ortamına deploy edilmeye hazır olup olmadığını kontrol eder.
"""
import os
import sys
from pathlib import Path

# Proje kök dizinini bul
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_production_readiness():
    """Production hazırlık kontrolü"""
    errors = []
    warnings = []
    
    print("🔍 Production Readiness Check başlatılıyor...\n")
    
    # 1. Environment Kontrolü
    print("1. Environment Variables Kontrolü:")
    flask_env = os.environ.get('FLASK_ENV', 'development')
    if flask_env != 'production':
        warnings.append(f"FLASK_ENV='{flask_env}' (production olmalı)")
        print(f"  ⚠️  FLASK_ENV: {flask_env}")
    else:
        print(f"  ✅ FLASK_ENV: {flask_env}")
    
    # 2. SECRET_KEY Kontrolü
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        errors.append("SECRET_KEY environment variable must be set")
        print("  ❌ SECRET_KEY: Ayarlanmamış")
    elif secret_key == 'dev-secret-key-change-in-production':
        errors.append("SECRET_KEY is still using development default")
        print("  ❌ SECRET_KEY: Development default kullanılıyor")
    elif secret_key == 'your-secret-key-here-change-in-production':
        errors.append("SECRET_KEY is still using example value")
        print("  ❌ SECRET_KEY: Example değer kullanılıyor")
    elif len(secret_key) < 32:
        warnings.append("SECRET_KEY should be at least 32 characters long")
        print(f"  ⚠️  SECRET_KEY: Uzunluk yeterli değil ({len(secret_key)} karakter)")
    else:
        print(f"  ✅ SECRET_KEY: Ayarlanmış ({len(secret_key)} karakter)")
    
    # 3. Debug Mode Kontrolü
    print("\n2. Debug Mode Kontrolü:")
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    if debug_mode and flask_env == 'production':
        errors.append("DEBUG mode should be False in production")
        print("  ❌ DEBUG: Production'da aktif")
    else:
        print(f"  ✅ DEBUG: {'Aktif' if debug_mode else 'Pasif'}")
    
    # 4. Config Dosyası Kontrolü
    print("\n3. Configuration Kontrolü:")
    try:
        from config import ProductionConfig
        config = ProductionConfig()
        if config.DEBUG:
            errors.append("ProductionConfig.DEBUG should be False")
            print("  ❌ ProductionConfig.DEBUG: True")
        else:
            print("  ✅ ProductionConfig.DEBUG: False")
        
        if not config.SESSION_COOKIE_SECURE:
            warnings.append("SESSION_COOKIE_SECURE should be True in production")
            print("  ⚠️  SESSION_COOKIE_SECURE: False")
        else:
            print("  ✅ SESSION_COOKIE_SECURE: True")
            
    except Exception as e:
        warnings.append(f"Config kontrolü başarısız: {e}")
        print(f"  ⚠️  Config kontrolü: {e}")
    
    # 5. Database Bağlantısı
    print("\n4. Database Bağlantısı:")
    try:
        from __init__ import create_app
        app = create_app()
        with app.app_context():
            from extensions import db
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
        print("  ✅ Database: Bağlantı başarılı")
    except Exception as e:
        errors.append(f"Database connection failed: {e}")
        print(f"  ❌ Database: Bağlantı hatası - {e}")
    
    # 6. Kritik Dosyalar
    print("\n5. Kritik Dosyalar:")
    critical_files = [
        'requirements.txt',
        'README.md',
        '.env.example',
        '__init__.py',
        'config.py'
    ]
    for file in critical_files:
        if (project_root / file).exists():
            print(f"  ✅ {file}: Mevcut")
        else:
            warnings.append(f"Critical file missing: {file}")
            print(f"  ⚠️  {file}: Bulunamadı")
    
    # 7. Backup/Yedek Dosyalar (Uyarı)
    print("\n6. Backup Dosyaları Kontrolü:")
    backup_files = list(project_root.glob('**/*.backup')) + \
                   list(project_root.glob('**/*.yedek*')) + \
                   list(project_root.glob('**/*_backup.*'))
    if backup_files:
        for backup in backup_files[:5]:  # İlk 5'i göster
            warnings.append(f"Backup file found: {backup.relative_to(project_root)}")
            print(f"  ⚠️  {backup.relative_to(project_root)}: Backup dosyası")
        if len(backup_files) > 5:
            print(f"  ⚠️  ... ve {len(backup_files) - 5} dosya daha")
    else:
        print("  ✅ Backup dosyası yok")
    
    # Sonuç
    print("\n" + "="*60)
    print("SONUÇ:")
    print("="*60)
    
    if errors:
        print(f"\n❌ {len(errors)} KRİTİK HATA bulundu:")
        for error in errors:
            print(f"  - {error}")
        print("\n⚠️  Bu hatalar production deploy öncesi düzeltilmelidir!")
    
    if warnings:
        print(f"\n⚠️  {len(warnings)} UYARI:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if not errors and not warnings:
        print("\n✅ Tüm kontroller başarılı! Production'a deploy edilebilir.")
    elif not errors:
        print("\n⚠️  Uyarılar var ancak kritik hata yok. Production'a deploy edilebilir.")
    
    return len(errors) == 0

if __name__ == '__main__':
    success = check_production_readiness()
    sys.exit(0 if success else 1)



