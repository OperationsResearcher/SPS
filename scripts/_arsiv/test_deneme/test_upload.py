import requests
import re
import json

s = requests.Session()
resp = s.get('http://127.0.0.1:5001/MfG_hgs')
match = re.search(r'href=[\"\'].*?/login/(\d+)[\"\'].*?adil@kalitesoleni\.com', resp.text, re.IGNORECASE | re.DOTALL)
if match:
    uid = match.group(1)
    s.get(f'http://127.0.0.1:5001/MfG_hgs/login/{uid}')
    
    r_profil = s.get('http://127.0.0.1:5001/profil')
    csrf_match = re.search(r'meta name=\"csrf-token\" content=\"(.*?)\"', r_profil.text)
    csrf = csrf_match.group(1) if csrf_match else ''
        
    print('Logged in via HGS. CSRF:', csrf)
    files = {'file': ('test.png', b'test', 'image/png')}
    headers = {'X-CSRFToken': csrf}
    res = s.post('http://127.0.0.1:5001/profil/foto-yukle', files=files, headers=headers)
    print("STATUS:", res.status_code)
    try:
        print("JSON:", res.json())
    except:
        print("TEXT:", res.text[:200])
else:
    print('HGS user not found')
