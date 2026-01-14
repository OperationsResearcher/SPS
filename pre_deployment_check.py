# -*- coding: utf-8 -*-
"""
Pre-Deployment Check Script
Deployment öncesi tüm gereksinimleri kontrol eder
"""
import sys
import os
import platform
import subprocess
import shutil
from pathlib import Path
import importlib.util


class Colors:
    """Terminal renk kodları"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    """Başlık yazdır"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")


def print_success(text):
    """Başarı mesajı"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_warning(text):
    """Uyarı mesajı"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_error(text):
    """Hata mesajı"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text):
    """Bilgi mesajı"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def check_python_version():
    """Python versiyonunu kontrol et"""
    print_header("Python Versiyonu Kontrolü")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print_info(f"Tespit edilen Python versiyonu: {version_str}")
    print_info(f"Platform: {platform.system()} {platform.release()}")
    print_info(f"Architecture: {platform.machine()}")
    
    if version.major >= 3 and version.minor >= 8:
        print_success("Python versiyonu uygun (3.8 veya üzeri)")
        return True
    else:
        print_error("Python 3.8 veya üzeri gerekli!")
        print_error(f"Mevcut versiyon: {version_str}")
        return False


def check_required_packages():
    """Gerekli paketleri kontrol et"""
    print_header("Gerekli Paketler Kontrolü")
    
    required_packages = {
        'flask': '2.3.0',
        'flask_sqlalchemy': '3.0.0',
        'flask_login': '0.6.0',
        'flask_migrate': '4.0.0',
        'werkzeug': '2.3.0',
        'waitress': '3.0.0',
        'dotenv': '1.0.0',  # python-dotenv paketi dotenv olarak import edilir
    }
    
    optional_packages = {
        'pyodbc': '5.0.0',
        'openpyxl': '3.1.0',
    }
    
    all_ok = True
    
    # Gerekli paketler
    print_info("Gerekli paketler kontrol ediliyor...")
    for package, min_version in required_packages.items():
        # Paket adı modül adından farklı olabilir
        module_name = package.replace('-', '_')
        
        try:
            # Paketi import etmeye çalış
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                try:
                    module = importlib.import_module(module_name)
                    version = getattr(module, '__version__', 'unknown')
                    print_success(f"{package} yüklü (versiyon: {version})")
                except Exception as e:
                    print_warning(f"{package} import edilemedi: {e}")
                    all_ok = False
            else:
                print_error(f"{package} yüklü değil!")
                all_ok = False
        except Exception as e:
            print_error(f"{package} kontrol edilemedi: {e}")
            all_ok = False
    
    # Opsiyonel paketler
    print_info("\nOpsiyonel paketler kontrol ediliyor...")
    for package, min_version in optional_packages.items():
        module_name = package.replace('-', '_')
        
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                module = importlib.import_module(module_name)
                version = getattr(module, '__version__', 'unknown')
                print_success(f"{package} yüklü (versiyon: {version})")
            else:
                print_warning(f"{package} yüklü değil (opsiyonel)")
        except Exception as e:
            print_warning(f"{package} kontrol edilemedi (opsiyonel): {e}")
    
    if not all_ok:
        print_error("\nEksik paketleri yüklemek için:")
        print_info("pip install -r requirements.txt")
    
    return all_ok


def check_directory_structure():
    """Dizin yapısını kontrol et"""
    print_header("Dizin Yapısı Kontrolü")
    
    required_dirs = [
        'static',
        'static/css',
        'static/js',
        'static/uploads',
        'static/uploads/logos',
        'templates',
    ]
    
    optional_dirs = [
        'logs',
        'backups',
        'tests',
    ]
    
    all_ok = True
    base_path = Path(os.getcwd())
    
    print_info("Gerekli dizinler kontrol ediliyor...")
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print_success(f"{dir_name}/ mevcut")
        else:
            print_error(f"{dir_name}/ bulunamadı!")
            all_ok = False
    
    print_info("\nOpsiyonel dizinler kontrol ediliyor...")
    for dir_name in optional_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print_success(f"{dir_name}/ mevcut")
        else:
            print_warning(f"{dir_name}/ bulunamadı (opsiyonel)")
            # Opsiyonel dizinleri oluştur
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print_success(f"{dir_name}/ oluşturuldu")
            except Exception as e:
                print_warning(f"{dir_name}/ oluşturulamadı: {e}")
    
    return all_ok


def check_required_files():
    """Gerekli dosyaları kontrol et"""
    print_header("Gerekli Dosyalar Kontrolü")
    
    required_files = [
        'app.py',
        '__init__.py',
        'config.py',
        'requirements.txt',
    ]
    
    optional_files = [
        '.env',
        'production_server.py',
        'init_db.py',
    ]
    
    all_ok = True
    base_path = Path(os.getcwd())
    
    print_info("Gerekli dosyalar kontrol ediliyor...")
    for file_name in required_files:
        file_path = base_path / file_name
        if file_path.exists() and file_path.is_file():
            size = file_path.stat().st_size
            print_success(f"{file_name} mevcut ({size} bytes)")
        else:
            print_error(f"{file_name} bulunamadı!")
            all_ok = False
    
    print_info("\nOpsiyonel dosyalar kontrol ediliyor...")
    for file_name in optional_files:
        file_path = base_path / file_name
        if file_path.exists() and file_path.is_file():
            size = file_path.stat().st_size
            print_success(f"{file_name} mevcut ({size} bytes)")
        else:
            print_warning(f"{file_name} bulunamadı (opsiyonel)")
    
    return all_ok


def check_environment_variables():
    """Environment variables kontrol et"""
    print_header("Environment Variables Kontrolü")
    
    # .env dosyasını yükle
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'SECRET_KEY': 'Security için kritik!',
    }
    
    recommended_vars = {
        'FLASK_ENV': 'development veya production',
        'SQL_SERVER': 'SQL Server bağlantısı için',
        'SQL_DATABASE': 'Veritabanı adı',
    }
    
    all_ok = True
    
    print_info("Kritik environment variables kontrol ediliyor...")
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            # Hassas bilgileri gösterme
            display_value = value[:5] + '...' if len(value) > 5 else '***'
            print_success(f"{var} = {display_value} ({description})")
            
            # SECRET_KEY uzunluğu kontrolü
            if var == 'SECRET_KEY' and len(value) < 32:
                print_warning(f"{var} çok kısa! Minimum 32 karakter önerilir.")
        else:
            print_error(f"{var} tanımlı değil! ({description})")
            all_ok = False
    
    print_info("\nÖnerilen environment variables kontrol ediliyor...")
    for var, description in recommended_vars.items():
        value = os.environ.get(var)
        if value:
            display_value = value[:20] + '...' if len(value) > 20 else value
            print_success(f"{var} = {display_value} ({description})")
        else:
            print_warning(f"{var} tanımlı değil ({description})")
    
    # FLASK_ENV production kontrolü
    flask_env = os.environ.get('FLASK_ENV', 'development')
    if flask_env == 'production':
        print_info("\n🚀 Production modu aktif")
        # Production için ekstra kontroller
        if not os.environ.get('SECRET_KEY'):
            print_error("PRODUCTION modunda SECRET_KEY zorunludur!")
            all_ok = False
    else:
        print_info(f"\n🔧 Environment: {flask_env}")
    
    return all_ok


def check_database_connection():
    """Veritabanı bağlantısını kontrol et"""
    print_header("Veritabanı Bağlantısı Kontrolü")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    sql_server = os.environ.get('SQL_SERVER')
    
    if sql_server:
        print_info(f"SQL Server bağlantısı test ediliyor: {sql_server}")
        try:
            import pyodbc
            
            sql_database = os.environ.get('SQL_DATABASE', 'stratejik_planlama')
            sql_username = os.environ.get('SQL_USERNAME')
            sql_password = os.environ.get('SQL_PASSWORD')
            sql_driver = os.environ.get('SQL_DRIVER', 'ODBC Driver 17 for SQL Server')
            
            # Connection string oluştur
            if sql_username and sql_password:
                conn_str = f'DRIVER={{{sql_driver}}};SERVER={sql_server};DATABASE={sql_database};UID={sql_username};PWD={sql_password}'
            else:
                conn_str = f'DRIVER={{{sql_driver}}};SERVER={sql_server};DATABASE={sql_database};Trusted_Connection=yes'
            
            # Bağlantı testi
            conn = pyodbc.connect(conn_str, timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            print_success("SQL Server bağlantısı başarılı!")
            print_info(f"SQL Server versiyonu: {version.split()[0]} {version.split()[3]}")
            conn.close()
            return True
            
        except ImportError:
            print_error("pyodbc modülü yüklü değil!")
            print_info("Yüklemek için: pip install pyodbc")
            return False
        except Exception as e:
            print_error(f"SQL Server bağlantı hatası: {e}")
            print_warning("SQLite fallback kullanılacak")
            return False
    else:
        print_info("SQL Server yapılandırılmamış, SQLite kullanılacak")
        
        # SQLite kontrolü
        db_path = Path(os.getcwd()) / 'spsv2.db'
        if db_path.exists():
            size = db_path.stat().st_size / 1024 / 1024  # MB
            print_success(f"SQLite veritabanı mevcut: spsv2.db ({size:.2f} MB)")
        else:
            print_warning("SQLite veritabanı henüz oluşturulmamış")
            print_info("Oluşturmak için: python init_db.py")
        
        return True


def check_disk_space():
    """Disk alanını kontrol et"""
    print_header("Disk Alanı Kontrolü")
    
    try:
        usage = shutil.disk_usage(os.getcwd())
        
        total_gb = usage.total / (1024**3)
        used_gb = usage.used / (1024**3)
        free_gb = usage.free / (1024**3)
        percent_used = (usage.used / usage.total) * 100
        
        print_info(f"Toplam Alan: {total_gb:.2f} GB")
        print_info(f"Kullanılan: {used_gb:.2f} GB ({percent_used:.1f}%)")
        print_info(f"Boş Alan: {free_gb:.2f} GB")
        
        if free_gb < 1:
            print_error("Yetersiz disk alanı! (Minimum 1GB gerekli)")
            return False
        elif free_gb < 5:
            print_warning("Disk alanı düşük! (5GB altı)")
            return True
        else:
            print_success("Yeterli disk alanı mevcut")
            return True
            
    except Exception as e:
        print_warning(f"Disk alanı kontrol edilemedi: {e}")
        return True


def check_port_availability():
    """Port kullanılabilirliğini kontrol et"""
    print_header("Port Kullanılabilirliği Kontrolü")
    
    import socket
    
    ports_to_check = [
        (5000, 'Flask Default'),
        (5001, 'Flask Alternative'),
        (8080, 'Production (Waitress)'),
    ]
    
    all_ok = True
    
    for port, description in ports_to_check:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                print_warning(f"Port {port} kullanımda ({description})")
                all_ok = False
            else:
                print_success(f"Port {port} kullanılabilir ({description})")
        except Exception as e:
            print_warning(f"Port {port} kontrol edilemedi: {e}")
    
    return all_ok


def check_permissions():
    """Dosya ve dizin izinlerini kontrol et"""
    print_header("İzin Kontrolü")
    
    base_path = Path(os.getcwd())
    
    # Yazma izni gereken dizinler
    writable_dirs = [
        'static/uploads/logos',
        'logs',
        'backups',
    ]
    
    all_ok = True
    
    for dir_name in writable_dirs:
        dir_path = base_path / dir_name
        
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print_success(f"{dir_name}/ oluşturuldu")
            except Exception as e:
                print_error(f"{dir_name}/ oluşturulamadı: {e}")
                all_ok = False
                continue
        
        # Yazma iznini test et
        test_file = dir_path / '.write_test'
        try:
            test_file.touch()
            test_file.unlink()
            print_success(f"{dir_name}/ yazılabilir")
        except Exception as e:
            print_error(f"{dir_name}/ yazma izni yok: {e}")
            all_ok = False
    
    return all_ok


def generate_summary(results):
    """Özet raporu oluştur"""
    print_header("DEPLOYMENT HAZIRLIK ÖZET RAPORU")
    
    total_checks = len(results)
    passed_checks = sum(1 for r in results.values() if r)
    failed_checks = total_checks - passed_checks
    
    print_info(f"Toplam Kontrol: {total_checks}")
    print_success(f"Başarılı: {passed_checks}")
    if failed_checks > 0:
        print_error(f"Başarısız: {failed_checks}")
    
    print("\n" + "="*70)
    
    all_passed = all(results.values())
    
    if all_passed:
        print_success("\n🎉 TÜM KONTROLLER BAŞARILI! Deployment için hazırsınız.\n")
        print_info("Deployment adımları için:")
        print_info("  1. DEPLOYMENT_GUIDE.md dosyasını inceleyin")
        print_info("  2. Veritabanını başlatın: python init_db.py")
        print_info("  3. Production server'ı çalıştırın: python production_server.py")
    else:
        print_error("\n⚠️ BAZI KONTROLLER BAŞARISIZ! Deployment öncesi düzeltmeler gerekli.\n")
        print_info("Başarısız kontroller:")
        for check_name, result in results.items():
            if not result:
                print_error(f"  - {check_name}")
        print_info("\nDetaylar için yukarıdaki bölümleri inceleyin.")
    
    print("="*70 + "\n")
    
    return all_passed


def main():
    """Ana kontrol fonksiyonu"""
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{'STRATEJIK PLANLAMA SİSTEMİ'.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{'Pre-Deployment Check Script'.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{'Versiyon: 2.2.0'.center(70)}{Colors.END}")
    print(f"{Colors.BLUE}{f'Tarih: 12 Ocak 2026'.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
    
    # Tüm kontrolleri çalıştır
    results = {
        'Python Versiyonu': check_python_version(),
        'Gerekli Paketler': check_required_packages(),
        'Dizin Yapısı': check_directory_structure(),
        'Gerekli Dosyalar': check_required_files(),
        'Environment Variables': check_environment_variables(),
        'Veritabanı Bağlantısı': check_database_connection(),
        'Disk Alanı': check_disk_space(),
        'Port Kullanılabilirliği': check_port_availability(),
        'Dosya İzinleri': check_permissions(),
    }
    
    # Özet raporu
    all_passed = generate_summary(results)
    
    # Exit code
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Kontrol iptal edildi.{Colors.END}\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Beklenmeyen hata: {e}{Colors.END}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
