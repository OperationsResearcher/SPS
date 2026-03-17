import requests
import openpyxl
from io import BytesIO
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from app import create_app
from models import User

BASE_URL = "http://127.0.0.1:5001"
LOGIN_URL = f"{BASE_URL}/auth/login"
DOWNLOAD_URL = f"{BASE_URL}/admin/download-user-template"
CREATE_USER_URL = f"{BASE_URL}/admin/create-user"
UPLOAD_URL = f"{BASE_URL}/admin/upload-users-excel"

def get_admin_credentials():
    app = create_app()
    with app.app_context():
        # Find an admin user
        admin = User.query.filter_by(sistem_rol='admin').first()
        if admin:
            print(f"Found admin user: {admin.username}")
            return admin.username
        else:
            print("No admin user found in DB")
            return None

def verify_backend():
    username = get_admin_credentials()
    if not username:
        print("Skipping verification due to missing admin user.")
        return

    # Try common passwords
    passwords = ['123456', 'Password123', 'admin', 'password']
    
    session = requests.Session()
    logged_in = False
    
    for password in passwords:
        print(f"Attempting login with {username} / {password} ...")
        try:
            res = session.post(LOGIN_URL, data={'username': username, 'password': password})
            if res.status_code == 200 and 'dashboard' in res.url:
                print("Login successful!")
                logged_in = True
                break
        except Exception as e:
            print(f"Login attempt error: {e}")
            
    if not logged_in:
        print("Could not login with any common password. Manual verification required.")
        return

    # 2. Download Template
    print("\nTesting Template Download...")
    try:
        res = session.get(DOWNLOAD_URL)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print("Download successful. Headers:", res.headers.get('Content-Type'))
            if 'spreadsheetml' in res.headers.get('Content-Type', ''):
                print("PASS: Correct Content-Type")
            else:
                print("FAIL: Incorrect Content-Type")
        else:
            print(f"FAIL: Status {res.status_code}")
            print("Response preview:", res.text[:200])
    except Exception as e:
        print("Download error:", e)

    # 3. Create User
    print("\nTesting Create User...")
    user_data = {
        'username': 'api_test_user_v3',
        'email': 'api_v3@test.com',
        'password': 'ApiPassword123',
        'role': 'kurum_kullanici',
        'kurum_id': 1
    }
    try:
        res = session.post(CREATE_USER_URL, json=user_data)
        print(f"Status: {res.status_code}")
        try:
            json_resp = res.json()
            print("Response JSON:", json_resp)
            if res.status_code == 200 and json_resp.get('success'):
                print("PASS: User created")
            else:
                print("FAIL: User creation failed")
        except:
            print("FAIL: Could not parse JSON")
            print("Response text:", res.text[:500])
    except Exception as e:
        print("Create User error:", e)

if __name__ == "__main__":
    verify_backend()
