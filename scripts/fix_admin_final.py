import codecs

path = r'c:\SPY_Cursor\SP_Code\templates\admin_v3.html'
print(f"Reading {path}...")

try:
    with codecs.open(path, 'r', 'utf-8', errors='ignore') as f:
        content = f.read()

    # 1. populateRoleSelect fonksiyonunu iğdiş edelim
    # select.innerHTML = html; satırını bulup kapatalım.
    if 'select.innerHTML = html;' in content:
        content = content.replace('select.innerHTML = html;', '// select.innerHTML = html; // STATIC OPTIONS USED')
        print("Disabled innerHTML overwriting in populateRoleSelect")

    # 2. Sistem Rolü Injection
    static_roles = """<option value="">Sistem Rolü Seçiniz...</option>
<option value="admin">Sistem Yöneticisi</option>
<option value="kurum_yoneticisi">Kurum Yöneticisi</option>
<option value="ust_yonetim">Üst Yönetim</option>
<option value="kurum_kullanici">Standart Kullanıcı</option>
<option value="surec_lideri">Süreç Lideri</option>
<option value="surec_uyesi">Süreç Üyesi</option>"""

    # Varyasyonlar
    replace_targets = [
        '<option value="">Sistem rolü seçiniz...</option>',
        '<option value="">Sistem Rolü Seçiniz...</option>',
    ]

    replaced = False
    for target in replace_targets:
        if target in content:
            content = content.replace(target, static_roles)
            replaced = True
            print(f"Replaced system roles using '{target}'")
            # Break yapmıyoruz, hepsini değiştirsin (New User modalında da olabilir)
    
    if not replaced:
        print("WARNING: Could not find system role option to replace!")

    # 3. Dosyayı kaydet
    with codecs.open(path, 'w', 'utf-8') as f:
        f.write(content)
    
    print("File saved.")

except Exception as e:
    print(f"Error: {e}")
