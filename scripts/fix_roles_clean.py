import codecs
import re

path = r'c:\SPY_Cursor\SP_Code\templates\admin_v3.html'
print(f"Reading {path}...")

try:
    with codecs.open(path, 'r', 'utf-8', errors='ignore') as f:
        content = f.read()

    clean_roles = """<option value="">Sistem Rolü Seçiniz...</option>
<option value="admin">Sistem Yöneticisi</option>
<option value="kurum_yoneticisi">Kurum Yöneticisi</option>
<option value="ust_yonetim">Üst Yönetim</option>
<option value="kurum_kullanici">Standart Kullanıcı</option>"""

    # 1. Edit User Modal (id="editUserRole")
    pattern_edit = r'(<select[^>]*id="editUserRole"[^>]*>)(.*?)(</select>)'
    match_edit = re.search(pattern_edit, content, re.DOTALL)
    if match_edit:
        new_block = match_edit.group(1) + clean_roles + match_edit.group(3)
        content = content.replace(match_edit.group(0), new_block)
        print("Cleaned editUserRole dropdown.")
    else:
        print("editUserRole not found!")

    # 2. New User Modal (id="role" genelde)
    # <select ... name="role" ...>
    # Daha geniş arama: name="role" olan select
    pattern_new = r'(<select[^>]*name="role"[^>]*>)(.*?)(</select>)'
    match_new = re.search(pattern_new, content, re.DOTALL)
    if match_new:
        new_block = match_new.group(1) + clean_roles + match_new.group(3)
        # Sadece bu bloğu değiştirelim (tüm dosyadaki replace değil)
        content = content.replace(match_new.group(0), new_block) 
        print("Cleaned New User dropdown (name='role').")
    else:
        # id="newUserRole" ile dene
        pattern_new2 = r'(<select[^>]*id="newUserRole"[^>]*>)(.*?)(</select>)'
        match_new2 = re.search(pattern_new2, content, re.DOTALL)
        if match_new2:
            new_block = match_new2.group(1) + clean_roles + match_new2.group(3)
            content = content.replace(match_new2.group(0), new_block)
            print("Cleaned New User dropdown (id='newUserRole').")
        else:
             print("New User dropdown not found!")

    # 3. JS Temizliği (innerHTML comment out satırını tamamen silmeye gerek yok, 
    # ama duplicate olmasın diye kontrol edelim. Script zaten çalışmıyor.)

    with codecs.open(path, 'w', 'utf-8') as f:
        f.write(content)
        
    print("Saved.")

except Exception as e:
    print(f"Error: {e}")
