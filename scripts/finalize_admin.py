import codecs
import shutil
import os

# Yollar
v3_path = r'c:\SPY_Cursor\SP_Code\templates\admin_v3.html'
target_path = r'c:\SPY_Cursor\SP_Code\templates\admin_panel.html'
routes_path = r'c:\SPY_Cursor\SP_Code\main\routes.py'

try:
    # 1. V3 Dosyasını Oku ve Temizle
    print("Reading V3...")
    with codecs.open(v3_path, 'r', 'utf-8', errors='ignore') as f:
        content = f.read()

    # Kırmızı bloğu temizle
    lines = content.splitlines()
    new_lines = []
    for line in lines:
        if 'V3 DOSYASI YÜKLENDİ' in line:
            continue
        if '<div style="background: red;' in line:
            continue
        # Sadece V3 div'ini hedef alıyoruz, başka divleri silmemeye dikkat.
        # En iyisi V3 metnini içeren div'i silmekti ama yukardaki yeterli.
        new_lines.append(line)

    content = '\n'.join(new_lines)

    # Title düzeltme
    content = content.replace('(V3 - DEBUG)', '')

    # 2. Dosyayı Hedefe Yaz
    print("Backing up old admin_panel.html...")
    if os.path.exists(target_path):
        shutil.copy(target_path, target_path.replace('.html', '_backup_broken.html'))

    print("Writing new admin_panel.html...")
    with codecs.open(target_path, 'w', 'utf-8') as f:
        f.write(content)

    # 3. Routes Güncelleme
    print("Updating routes.py...")
    with codecs.open(routes_path, 'r', 'utf-8', errors='ignore') as f:
        routes_content = f.read()

    if 'admin_v3.html' in routes_content:
        routes_content = routes_content.replace('admin_v3.html', 'admin_panel.html')
        print("Routes updated back to admin_panel.html")
    
    with codecs.open(routes_path, 'w', 'utf-8') as f:
        f.write(routes_content)

    print("Finalization complete.")

except Exception as e:
    print(f"Error: {e}")
