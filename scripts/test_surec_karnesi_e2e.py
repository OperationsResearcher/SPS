# -*- coding: utf-8 -*-
"""
Süreç Karnesi E2E Test Scripti
3 farklı kullanıcı rolü ile test yapar
"""
import os
import sys
import requests
from dotenv import load_dotenv
import io
import sys

# Windows console encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Environment variables yükle
load_dotenv()

BASE_URL = 'http://127.0.0.1:5000'

def test_surec_karnesi_access():
    """Süreç Karnesi sayfasına erişimi test et"""
    print("=" * 60)
    print("Süreç Karnesi E2E Test")
    print("=" * 60)
    print()
    
    results = {
        'admin': {'success': False, 'errors': []},
        'kurum_yoneticisi': {'success': False, 'errors': []},
        'görüntüleyici': {'success': False, 'errors': []}
    }
    
    # Test 1: Admin kullanıcı
    print("1. Admin Kullanıcı Testi")
    print("-" * 60)
    try:
        # Login (varsayılan admin kullanıcısı)
        session = requests.Session()
        
        # Önce GET isteği yaparak CSRF token al
        login_page = session.get(f'{BASE_URL}/login')
        if login_page.status_code != 200:
            print(f"  ❌ Login sayfası açılamadı: {login_page.status_code}")
            results['admin']['errors'].append(f'Login page failed: {login_page.status_code}')
            print()
            # Diğer testlere devam et
        else:
            # CSRF token'ı parse et (basit regex ile)
            import re
            csrf_token_match = re.search(r'name="csrf_token" value="([^"]+)"', login_page.text)
            csrf_token = csrf_token_match.group(1) if csrf_token_match else None
            
            login_response = session.post(
                f'{BASE_URL}/login',
                data={
                    'username': 'admin',
                    'password': '123456',  # Test şifresi
                    'csrf_token': csrf_token
                },
                allow_redirects=False
            )
        
        if login_response.status_code in [200, 302]:
            print("  ✅ Admin login başarılı")
            
            # Süreç karnesi sayfasına eriş
            surec_karnesi_response = session.get(f'{BASE_URL}/surec-karnesi')
            
            if surec_karnesi_response.status_code == 200:
                print("  ✅ Süreç karnesi sayfası açıldı (200 OK)")
                results['admin']['success'] = True
            elif surec_karnesi_response.status_code == 403:
                print("  ❌ 403 Forbidden - Yetki hatası")
                results['admin']['errors'].append('403 Forbidden')
            elif surec_karnesi_response.status_code == 404:
                print("  ❌ 404 Not Found - Sayfa bulunamadı")
                results['admin']['errors'].append('404 Not Found')
            elif surec_karnesi_response.status_code == 500:
                print("  ❌ 500 Internal Server Error")
                results['admin']['errors'].append('500 Internal Server Error')
            else:
                print(f"  ❌ Beklenmeyen status code: {surec_karnesi_response.status_code}")
                results['admin']['errors'].append(f'Status {surec_karnesi_response.status_code}')
        else:
            print(f"  ❌ Admin login başarısız: {login_response.status_code}")
            results['admin']['errors'].append(f'Login failed: {login_response.status_code}')
    except requests.exceptions.ConnectionError:
        print("  ❌ Flask uygulaması çalışmıyor! Lütfen uygulamayı başlatın.")
        results['admin']['errors'].append('Connection Error - Flask app not running')
    except Exception as e:
        print(f"  ❌ Hata: {e}")
        results['admin']['errors'].append(str(e))
    
    print()
    
    # Test 2: Kurum Yöneticisi
    print("2. Kurum Yöneticisi Testi")
    print("-" * 60)
    try:
        session = requests.Session()
        
        # Önce GET isteği yaparak CSRF token al
        login_page = session.get(f'{BASE_URL}/login')
        if login_page.status_code != 200:
            print(f"  ❌ Login sayfası açılamadı: {login_page.status_code}")
            results['kurum_yoneticisi']['errors'].append(f'Login page failed: {login_page.status_code}')
            print()
        else:
            import re
            csrf_token_match = re.search(r'name="csrf_token" value="([^"]+)"', login_page.text)
            csrf_token = csrf_token_match.group(1) if csrf_token_match else None
            
            # Kurum yöneticisi kullanıcısı bul (sistem_rol='kurum_yoneticisi')
            login_response = session.post(
                f'{BASE_URL}/login',
                data={
                    'username': 'burak',  # Gerçek kullanıcı: kurum_yoneticisi
                    'password': '123456',  # Test şifresi
                    'csrf_token': csrf_token
                },
                allow_redirects=False
            )
        
        if login_response.status_code in [200, 302]:
            print("  ✅ Kurum yöneticisi login başarılı")
            
            surec_karnesi_response = session.get(f'{BASE_URL}/surec-karnesi')
            
            if surec_karnesi_response.status_code == 200:
                print("  ✅ Süreç karnesi sayfası açıldı (200 OK)")
                results['kurum_yoneticisi']['success'] = True
            else:
                print(f"  ❌ Status code: {surec_karnesi_response.status_code}")
                print(f"  Response: {surec_karnesi_response.text[:500]}")
                results['kurum_yoneticisi']['errors'].append(f'Status {surec_karnesi_response.status_code}')
        else:
            print(f"  ❌ Kurum yöneticisi login başarısız: {login_response.status_code}")
            results['kurum_yoneticisi']['errors'].append(f'Login failed: {login_response.status_code}')
    except requests.exceptions.ConnectionError:
        print("  ❌ Flask uygulaması çalışmıyor!")
        results['kurum_yoneticisi']['errors'].append('Connection Error')
    except Exception as e:
        print(f"  ❌ Hata: {e}")
        results['kurum_yoneticisi']['errors'].append(str(e))
    
    print()
    
    # Test 3: Görüntüleyici (Normal kullanıcı)
    print("3. Görüntüleyici (Normal Kullanıcı) Testi")
    print("-" * 60)
    try:
        session = requests.Session()
        
        # Önce GET isteği yaparak CSRF token al
        login_page = session.get(f'{BASE_URL}/login')
        if login_page.status_code != 200:
            print(f"  ❌ Login sayfası açılamadı: {login_page.status_code}")
            results['görüntüleyici']['errors'].append(f'Login page failed: {login_page.status_code}')
            print()
        else:
            import re
            csrf_token_match = re.search(r'name="csrf_token" value="([^"]+)"', login_page.text)
            csrf_token = csrf_token_match.group(1) if csrf_token_match else None
            
            login_response = session.post(
                f'{BASE_URL}/login',
                data={
                    'username': 'Ali',  # Gerçek kullanıcı: kurum_kullanici
                    'password': '123456',  # Test şifresi
                    'csrf_token': csrf_token
                },
                allow_redirects=False
            )
        
        if login_response.status_code in [200, 302]:
            print("  ✅ Görüntüleyici login başarılı")
            
            surec_karnesi_response = session.get(f'{BASE_URL}/surec-karnesi')
            
            if surec_karnesi_response.status_code == 200:
                print("  ✅ Süreç karnesi sayfası açıldı (200 OK)")
                results['görüntüleyici']['success'] = True
            else:
                print(f"  ❌ Status code: {surec_karnesi_response.status_code}")
                print(f"  Response: {surec_karnesi_response.text[:500]}")
                results['görüntüleyici']['errors'].append(f'Status {surec_karnesi_response.status_code}')
        else:
            print(f"  ❌ Görüntüleyici login başarısız: {login_response.status_code}")
            results['görüntüleyici']['errors'].append(f'Login failed: {login_response.status_code}')
    except requests.exceptions.ConnectionError:
        print("  ❌ Flask uygulaması çalışmıyor!")
        results['görüntüleyici']['errors'].append('Connection Error')
    except Exception as e:
        print(f"  ❌ Hata: {e}")
        results['görüntüleyici']['errors'].append(str(e))
    
    print()
    print("=" * 60)
    print("Test Sonuçları Özeti")
    print("=" * 60)
    for role, result in results.items():
        status = "✅ BAŞARILI" if result['success'] else "❌ BAŞARISIZ"
        print(f"{role.upper()}: {status}")
        if result['errors']:
            for error in result['errors']:
                print(f"  - {error}")
    
    return results

if __name__ == '__main__':
    test_surec_karnesi_access()

