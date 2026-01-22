from waitress import serve
from app import create_app
from werkzeug.middleware.proxy_fix import ProxyFix  # <--- EKLENDI: Gerekli kütüphane
import os

# Uygulamayi olustur
app = create_app()

# --- EKLENDI: ProxyFix Ayari (Caddy Uyumu) ---
# Caddy'nin ilettigi 'X-Forwarded-For' basligini okuyarak
# 127.0.0.1 yerine gercek kullanici IP'sini Flask'a tanitiyoruz.
# Bu sayede 'Too Many Requests' hatasi cozulur.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

if __name__ == '__main__':
    print("------------------------------------------------")
    print("SPS WAITRESS SUNUCUSU (HTTPS - CADDY ARKASI)")
    print(f"Calisma Dizini: {os.getcwd()}")
    print("Veritabani Yolu: C:\\SPY_Cursor\\SPS_DATA\\spsv2.db (Harici)")
    print("Erisim Adresi: http://0.0.0.0:8080 (Disaridan 443)")
    print("------------------------------------------------")
    
    # 8080 Portundan yayin yap (Caddy buraya yonlendirecek)
    serve(app, host='0.0.0.0', port=8080, threads=6)