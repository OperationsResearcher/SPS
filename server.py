import os
import subprocess
from waitress import serve
from app import create_app

def kill_port_8080():
    """
    8080 portunu kullanan eski süreçleri bulur ve sonlandırır.
    Windows için taskkill kullanır.
    """
    try:
        # netstat ile 8080 portunu kullanan PID'leri bul
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True,
            shell=True
        )
        
        pids_to_kill = []
        for line in result.stdout.split('\n'):
            if ':8080' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) > 4:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids_to_kill.append(pid)
        
        # Bulunan PID'leri öldür
        if pids_to_kill:
            print(f"⚠️  8080 portunu kullanan {len(pids_to_kill)} süreç bulundu. Temizleniyor...")
            for pid in pids_to_kill:
                try:
                    subprocess.run(
                        ['taskkill', '/F', '/PID', pid],
                        capture_output=True,
                        shell=True
                    )
                    print(f"   ✓ PID {pid} sonlandırıldı")
                except Exception as e:
                    print(f"   ✗ PID {pid} sonlandırılamadı: {e}")
            print("✅ Port temizliği tamamlandı.\n")
        else:
            print("✅ 8080 portu temiz.\n")
    except Exception as e:
        print(f"⚠️  Port kontrolü sırasında hata: {e}\n")


# Port temizliğini yap
kill_port_8080()

# Uygulamayı oluştur
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = create_app()

# Template ve static folder yollarını garanti altına al
if not hasattr(app, 'template_folder') or app.template_folder is None:
    app.template_folder = os.path.join(BASE_DIR, 'templates')
if not hasattr(app, 'static_folder') or app.static_folder is None:
    app.static_folder = os.path.join(BASE_DIR, 'static')

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 WAITRESS PROD SUNUCUSU BAŞLATILIYOR (PORT 8080)...")
    print("=" * 60)
    print(f"📁 Çalışma Dizini: {BASE_DIR}")
    print(f"📂 Template Klasörü: {app.template_folder}")
    print(f"📂 Static Klasörü: {app.static_folder}")
    print(f"🌐 Erişim Adresi: http://0.0.0.0:8080")
    print(f"⚙️  Thread Sayısı: 6")
    print(f"🏭 Mod: PRODUCTION (Waitress)")
    print("=" * 60)
    print()
    
    # Waitress Production Sunucusu
    serve(app, host='0.0.0.0', port=8080, threads=6)
