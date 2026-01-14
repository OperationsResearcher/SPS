# -*- coding: utf-8 -*-
"""
Süreç Karnesi Tekil Test Scripti
Her kullanıcı için ayrı test
"""
import os
import sys
import requests
from dotenv import load_dotenv
import io
import time

# Windows console encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Environment variables yükle
load_dotenv()

BASE_URL = 'http://127.0.0.1:5000'

def test_user(username, password, role_name):
    """Tek bir kullanıcı için test"""
    print("=" * 60)
    print(f"{role_name} Testi - {username}")
    print("=" * 60)
    
    try:
        session = requests.Session()
        
        # Önce GET isteği yaparak CSRF token al
        time.sleep(1)  # Rate limit için bekle
        login_page = session.get(f'{BASE_URL}/login')
        
        if login_page.status_code != 200:
            print(f"  ❌ Login sayfası açılamadı: {login_page.status_code}")
            return False
        
        # CSRF token'ı parse et
        import re
        csrf_token_match = re.search(r'name="csrf_token" value="([^"]+)"', login_page.text)
        csrf_token = csrf_token_match.group(1) if csrf_token_match else None
        
        if not csrf_token:
            print("  ❌ CSRF token bulunamadı")
            return False
        
        # Login
        time.sleep(1)  # Rate limit için bekle
        login_response = session.post(
            f'{BASE_URL}/login',
            data={
                'username': username,
                'password': password,
                'csrf_token': csrf_token
            },
            allow_redirects=False
        )
        
        if login_response.status_code not in [200, 302]:
            print(f"  ❌ Login başarısız: {login_response.status_code}")
            print(f"  Response: {login_response.text[:200]}")
            return False
        
        print("  ✅ Login başarılı")
        
        # Süreç karnesi sayfasına eriş
        time.sleep(1)
        surec_karnesi_response = session.get(f'{BASE_URL}/surec-karnesi')
        
        if surec_karnesi_response.status_code == 200:
            print("  ✅ Süreç karnesi sayfası açıldı (200 OK)")
            
            # Sayfa içeriğinde hata kontrolü
            if 'Template render hatası' in surec_karnesi_response.text:
                print("  ❌ Template render hatası tespit edildi")
                error_match = re.search(r'Template render hatası: ([^<]+)', surec_karnesi_response.text)
                if error_match:
                    print(f"  Hata: {error_match.group(1)}")
                return False
            
            # Buton kontrolü (basit)
            if 'Veri Girişi' in surec_karnesi_response.text or 'PG Ekle' in surec_karnesi_response.text:
                print("  ✅ Veri girişi butonları mevcut")
            else:
                print("  ⚠️  Veri girişi butonları bulunamadı (sadece görüntüleme modu olabilir)")
            
            return True
        elif surec_karnesi_response.status_code == 403:
            print("  ❌ 403 Forbidden - Yetki hatası")
            return False
        elif surec_karnesi_response.status_code == 404:
            print("  ❌ 404 Not Found - Sayfa bulunamadı")
            return False
        elif surec_karnesi_response.status_code == 500:
            print("  ❌ 500 Internal Server Error")
            error_match = re.search(r'Template render hatası: ([^<]+)', surec_karnesi_response.text)
            if error_match:
                print(f"  Hata: {error_match.group(1)}")
            return False
        else:
            print(f"  ❌ Beklenmeyen status code: {surec_karnesi_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("  ❌ Flask uygulaması çalışmıyor!")
        return False
    except Exception as e:
        print(f"  ❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    results = {}
    
    # Test 1: Admin
    results['admin'] = test_user('admin', '123456', 'Admin')
    print()
    time.sleep(2)
    
    # Test 2: Kurum Yöneticisi
    results['kurum_yoneticisi'] = test_user('burak', '123456', 'Kurum Yöneticisi')
    print()
    time.sleep(2)
    
    # Test 3: Görüntüleyici
    results['görüntüleyici'] = test_user('Ali', '123456', 'Görüntüleyici (Normal Kullanıcı)')
    print()
    
    # Özet
    print("=" * 60)
    print("Test Sonuçları Özeti")
    print("=" * 60)
    for role, success in results.items():
        status = "✅ BAŞARILI" if success else "❌ BAŞARISIZ"
        print(f"{role.upper()}: {status}")

