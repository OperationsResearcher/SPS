# -*- coding: utf-8 -*-
"""
Production Server - Waitress WSGI Server
Production ortamı için optimize edilmiş server konfigürasyonu
"""
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Logging konfigürasyonu
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'production.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def check_production_readiness():
    """Production hazırlık kontrolü"""
    logger.info("Production hazırlık kontrolü başlatılıyor...")
    
    errors = []
    warnings = []
    
    # Environment kontrolü
    flask_env = os.environ.get('FLASK_ENV', 'development')
    if flask_env != 'production':
        warnings.append(f"FLASK_ENV '{flask_env}' olarak ayarlanmış (production önerilir)")
    
    # Secret key kontrolü
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        errors.append("SECRET_KEY environment variable tanımlı değil!")
    elif len(secret_key) < 32:
        warnings.append(f"SECRET_KEY çok kısa ({len(secret_key)} karakter). Min 32 karakter önerilir.")
    
    # Debug mode kontrolü
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    if debug and flask_env == 'production':
        errors.append("PRODUCTION modunda DEBUG aktif! Bu güvenlik riski oluşturur.")
    
    # Rapor
    if errors:
        logger.error("❌ KRİTİK HATALAR:")
        for error in errors:
            logger.error(f"  - {error}")
        logger.error("\nProduction server başlatılamıyor!")
        return False
    
    if warnings:
        logger.warning("⚠️ UYARILAR:")
        for warning in warnings:
            logger.warning(f"  - {warning}")
    
    logger.info("✓ Production hazırlık kontrolü tamamlandı")
    return True


def create_app():
    """Flask uygulaması oluştur"""
    try:
        from __init__ import create_app as create_flask_app
        
        logger.info("Flask uygulaması oluşturuluyor...")
        app = create_flask_app()
        
        # Production ayarları
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        
        logger.info("✓ Flask uygulaması başarıyla oluşturuldu")
        return app
        
    except Exception as e:
        logger.error(f"❌ Flask uygulaması oluşturulamadı: {e}")
        raise


def start_server(app):
    """Waitress sunucusunu başlat"""
    try:
        from waitress import serve
        
        # Server konfigürasyonu
        host = os.environ.get('SERVER_HOST', '0.0.0.0')
        port = int(os.environ.get('SERVER_PORT', 8080))
        threads = int(os.environ.get('SERVER_THREADS', 4))
        
        logger.info("="*70)
        logger.info("STRATEJIK PLANLAMA SİSTEMİ - PRODUCTION SERVER")
        logger.info("="*70)
        logger.info(f"Server: Waitress WSGI")
        logger.info(f"Host: {host}")
        logger.info(f"Port: {port}")
        logger.info(f"Threads: {threads}")
        logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
        logger.info("="*70)
        logger.info("")
        logger.info(f"🚀 Server başlatılıyor: http://{host}:{port}")
        logger.info("")
        logger.info("Server'ı durdurmak için: Ctrl+C")
        logger.info("="*70)
        
        # Waitress server'ı başlat
        serve(
            app,
            host=host,
            port=port,
            threads=threads,
            url_scheme='http',
            # Connection pool
            channel_timeout=120,
            # İstek boyutu limitleri
            max_request_body_size=16 * 1024 * 1024,  # 16MB
            # Backlog
            backlog=1024,
            # Cleanup
            cleanup_interval=30,
            # Logging
            _quiet=False,
        )
        
    except ImportError:
        logger.error("❌ Waitress yüklü değil!")
        logger.error("Yüklemek için: pip install waitress")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\n\n⚠️ Server durduruldu (Keyboard Interrupt)")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Server başlatılamadı: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Ana fonksiyon"""
    try:
        # Production hazırlık kontrolü
        if not check_production_readiness():
            sys.exit(1)
        
        # Flask uygulamasını oluştur
        app = create_app()
        
        # Server'ı başlat
        start_server(app)
        
    except Exception as e:
        logger.error(f"❌ Beklenmeyen hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
