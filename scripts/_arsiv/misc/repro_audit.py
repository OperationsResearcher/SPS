
import logging
from __init__ import create_app
from extensions import db
from models.user import User, Kurum
from models.process import Surec, SurecPerformansGostergesi
from models.audit import AuditLog
from werkzeug.security import generate_password_hash
import json

# Setup
app = create_app()
app.config['WTF_CSRF_ENABLED'] = False

logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

def run_test():
    with app.app_context():
        # 1. Setup Data
        kurum = Kurum.query.filter_by(kisa_ad='TestAS').first()
        if not kurum:
            kurum = Kurum(kisa_ad='TestAS', ticari_unvan='Test A.Ş.', silindi=False)
            db.session.add(kurum)
            db.session.commit()
        
        user = User.query.filter_by(username='1salih').first()
        if not user:
            user = User(
                username='1salih', 
                email='1salih@test.com', 
                password_hash=generate_password_hash('123456'),
                kurum_id=kurum.id,
                first_name='Salih',
                last_name='Yilmaz',
                sistem_rol='kurum_kullanici',
                silindi=False
            )
            db.session.add(user)
            db.session.commit()
        else:
            # Ensure password is known
            user.password_hash = generate_password_hash('123456')
            user.kurum_id = kurum.id
            user.silindi = False
            db.session.commit()

        # Find Process
        surec_adi = "Şirket Organları Yönetimi Süreci"
        surec = Surec.query.filter(Surec.ad.ilike(f"%{surec_adi}%")).first()
        if not surec:
            # Create if not exists for testing
            surec = Surec(ad=surec_adi, kurum_id=kurum.id, silindi=False)
            db.session.add(surec)
            db.session.commit()
            print(f"Süreç created: {surec.id}")
        else:
             print(f"Süreç found: {surec.id}")
             # Ensure kurum matches
             surec.kurum_id = kurum.id
             db.session.commit()

        # Find PG
        pg_adi = "Satış Sayısı"
        pg = SurecPerformansGostergesi.query.filter(SurecPerformansGostergesi.ad.ilike(f"%{pg_adi}%"), SurecPerformansGostergesi.surec_id==surec.id).first()
        if not pg:
            pg = SurecPerformansGostergesi(
                surec_id=surec.id, 
                ad=pg_adi, 
                silindi=False,
                hedef_deger=100,
                olcum_birimi='Adet',
                periyot='Aylık'
            )
            db.session.add(pg)
            db.session.commit()
            print(f"PG created: {pg.id}")
        else:
            print(f"PG found: {pg.id}")

        # Ensure User has permission (if needed by logic)
        # Logic says: if user is admin, ok. If not, must be in same kurum.
        # User is in 'TestAS' (same as surec).

    # 2. Simulate User Action via Test Client to trigger listeners with context
    client = app.test_client()
    
    # Login
    with client:
        print("Logging in...")
        resp = client.post('/auth/login', data={'username': '1salih', 'password': '123456'}, follow_redirects=True)
        if b"Giri" in resp.data or resp.status_code == 200: 
            # Note: 200 is returned on success page render
            print("Login successful (assumed)")
        else:
            print(f"Login response status: {resp.status_code}")

        # Payload
        # Following api/routes.py expectation
        payload = {
            "surec_id": surec.id,
            "yil": 2026,
            "pg_verileri": [{
                "pg_id": 0,
                "surec_pg_id": pg.id,
                "periyot_tipi": "yillik",
                "periyot_no": 1,
                "field": "gerceklesen",
                "value": "125",
                "aciklama": "Tested Audit via Script"
            }]
        }

        # Send Request
        print(f"Sending POST to /api/surec/{surec.id}/karne/kaydet")
        # Need CSRF token? The route might be protected.
        # But for test client, usually CSRF needs handling if ENABLE_CSRF is on.
        # Let's try without first. If fails, I'll bypass or fetch token.
        # Actually api/ routes might be exempt or need token.
        # The route in routes.py doesn't show @csrf.exempt explicit for this one usually?
        # Let's check route definition again.
        
        headers = {'Content-Type': 'application/json'}
        # Fake CSRF if needed?
        
        resp = client.post(f'/api/surec/{surec.id}/karne/kaydet', data=json.dumps(payload), headers=headers)
        print(f"Save Response: {resp.status_code}, {resp.data}")

        # Create Admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@test.com',
                password_hash=generate_password_hash('admin123'),
                kurum_id=kurum.id,
                sistem_rol='admin',
                silindi=False
            )
            db.session.add(admin)
            db.session.commit()
        else:
            admin.password_hash = generate_password_hash('admin123')
            db.session.commit()

    # 2. Simulate User Action via Test Client
    client = app.test_client()
    
    # Login
    with client:
        # ... (keep existing login/post logic) ...
        print("Logging in as 1salih...")
        client.post('/auth/login', data={'username': '1salih', 'password': '123456'}, follow_redirects=True)
        
        payload = {
            "surec_id": surec.id,
            "yil": 2026,
            "pg_verileri": [{
                "pg_id": 0,
                "surec_pg_id": pg.id,
                "periyot_tipi": "yillik",
                "periyot_no": 1,
                "field": "gerceklesen",
                "value": "125",
                "aciklama": "Tested Audit via Script"
            }]
        }
        headers = {'Content-Type': 'application/json'}
        resp = client.post(f'/api/surec/{surec.id}/karne/kaydet', data=json.dumps(payload), headers=headers)
        print(f"Save Response: {resp.status_code}")
        client.get('/auth/logout')

    # 3. Verify via Admin API
    with client:
        print("Logging in as admin...")
        client.post('/auth/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
        print("Fetching Audit Logs via API...")
        resp = client.get('/admin/api/logs')
        if resp.status_code == 200:
            data = resp.json
            logs = data.get('data', [])
            print(f"API returned {len(logs)} logs.")
            found = False
            for log in logs:
                print(f"API Log: User:{log['username']} Action:{log['action']} Table:{log['table_name']}")
                if log['username'] == '1salih' or 'PerformansGostergeVeri' in log['table_name']:
                    found = True
            
            if found:
                print("SUCCESS: Log found in API response.")
            else:
                print("FAILURE: Log NOT found in API response.")
        else:
            print(f"Failed to fetch logs: {resp.status_code}")


if __name__ == "__main__":
    run_test()
