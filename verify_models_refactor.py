import sys
import os

# Proje kök dizinini path'e ekle
sys.path.append(os.getcwd())

try:
    print("--- Test 1: models import ---")
    from models import (
        User, Kurum, Process, PerformanceIndicator, 
        MainStrategy, SubStrategy, Project, Task
    )
    print("✅ Temel modeller ve Aliaslar (Process, MainStrategy) başarıyla import edildi.")
    
    print("\n--- Test 2: App Factory ---")
    from app import create_app
    app = create_app()
    print("✅ App Factory (create_app) başarıyla oluşturuldu.")
    
    print("\n--- Test 3: DB Context ---")
    with app.app_context():
        from extensions import db
        # Basit bir sorgu denemesi (tablo oluşmuş mu diye değil, SQLA context hatası var mı diye)
        print("DB Engine:", db.engine)
    print("✅ DB Context erişimi başarılı.")

    print("\n🎉 BAŞARILI: Uygulama başlatılabilir durumda.")

except ImportError as e:
    print(f"\n❌ IMPORT HATASI: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"\n❌ GENEL HATA: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
