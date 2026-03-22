"""
Profile photo upload + DB persistence test.
Runs against the live server at http://127.0.0.1:5001
"""
import requests
import re

s = requests.Session()

# 1) HGS sayfasını aç, Adil kullanıcısını bul ve login ol
resp_hgs = s.get("http://127.0.0.1:5001/hgs")
match = re.search(r'href=["\'].*?/login/(\d+)["\'].*?adil@kalitesoleni\.com', resp_hgs.text, re.IGNORECASE | re.DOTALL)
if not match:
    print("HATA: HGS sayfasında adil@kalitesoleni.com bulunamadı!")
    exit(1)

uid = match.group(1)
print(f"[1] Adil kullanıcısı bulundu (ID={uid}), giriş yapılıyor...")
resp_login = s.get(f"http://127.0.0.1:5001/hgs/login/{uid}")
print(f"    Login redirect sonucu: {resp_login.url}")

# 2) Profil sayfasını aç, CSRF token al
resp_profil = s.get("http://127.0.0.1:5001/profil")
csrf_match = re.search(r'<meta name="csrf-token" content="(.*?)"', resp_profil.text)
csrf = csrf_match.group(1) if csrf_match else ""
has_photo_before = "profilePhotoImg" in resp_profil.text
print(f"[2] Profil sayfası alındı  | CSRF: {'OK' if csrf else 'BULUNAMADI'} | Fotoğraf öncesi: {has_photo_before}")

# 3) Gerçek bir resim dosyası yükle (Kokpitlogo.png)
with open(r"c:\kokpitim\static\img\Kokpitlogo.png", "rb") as f:
    img_bytes = f.read()

print(f"[3] Resim okundu: {len(img_bytes)} byte, yükleniyor...")
resp_upload = s.post(
    "http://127.0.0.1:5001/profil/foto-yukle",
    files={"file": ("Kokpitlogo.png", img_bytes, "image/png")},
    headers={"X-CSRFToken": csrf},
)
print(f"    Upload response: HTTP {resp_upload.status_code}")
try:
    data = resp_upload.json()
    print(f"    JSON: {data}")
    photo_url = data.get("photo_url", "")
except Exception as e:
    print(f"    JSON parse hatası: {e}")
    print(f"    Ham metin: {resp_upload.text[:300]}")
    exit(1)

# 4) Sayfayı yenile ve fotoğrafın gelip gelmediğini kontrol et
resp_profil2 = s.get("http://127.0.0.1:5001/profil")
has_photo_after = "profilePhotoImg" in resp_profil2.text
photo_src_ok = photo_url and photo_url in resp_profil2.text if photo_url else False

print(f"\n[4] Sayfa yenileme sonucu:")
print(f"    profilePhotoImg var mı : {has_photo_after}")
print(f"    photo_url HTML'de var mı: {photo_src_ok}")
print(f"    photo_url              : {photo_url}")

# 5) Fotoğrafın URL'si gerçekten servis ediliyor mu?
if photo_url:
    resp_img = s.get(f"http://127.0.0.1:5001{photo_url}")
    print(f"    Fotoğraf HTTP isteği   : {resp_img.status_code} ({resp_img.headers.get('content-type','')})")

if has_photo_after and photo_src_ok:
    print("\n✅ BAŞARILI: Fotoğraf veritabanına kaydedildi ve sayfa yenilemesinde doğru görünüyor!")
else:
    print("\n❌ HATA: Fotoğraf sayfa yenilemesinde görünmüyor. DB'ye kaydedilmemiş olabilir.")
