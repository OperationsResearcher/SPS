import codecs
import re

path = r'c:\SPY_Cursor\SP_Code\templates\admin_v3.html'

try:
    with codecs.open(path, 'r', 'utf-8', errors='ignore') as f:
        content = f.read()

    # 1. Karakter Temizliği
    replacements = {
        'FotoİŸraf': 'Fotoğraf',
        'fotoİŸraf': 'fotoğraf',
        'DeİŸişmez': 'Değişmez',
        'deİŸişmez': 'değişmez',
        'Ç–nizleme': 'Önizleme',
        'BaİŸarılı': 'Başarılı',
        'baİŸarılı': 'başarılı',
        'Sistem rolu seçiniz...': 'Sistem Rolü Seçiniz...',
        'Boş bırakın deİŸişmez': 'Boş bırakın (değişmez)',
        'Modal\'lar─▒': 'Modalları',
        'fotoİŸraf': 'fotoğraf'
    }
    
    count = 0
    for old, new in replacements.items():
        if old in content:
            content = content.replace(old, new)
            count += 1
    
    print(f"{count} adet karakter düzeltmesi yapıldı.")

    # 2. Statik Dropdown Injection
    # Sistem Rolü
    static_roles = """<option value="">Sistem Rolü Seçiniz...</option>
<option value="admin">Sistem Yöneticisi</option>
<option value="kurum_yoneticisi">Kurum Yöneticisi</option>
<option value="ust_yonetim">Üst Yönetim</option>
<option value="kurum_kullanici">Standart Kullanıcı</option>
<option value="surec_lideri">Süreç Lideri</option>
<option value="surec_uyesi">Süreç Üyesi</option>"""

    target_string = '<option value="">Sistem Rolü Seçiniz...</option>'
    if target_string in content:
        content = content.replace(target_string, static_roles)
        print("Sistem Rolü dropdown seçenekleri statik olarak eklendi.")

    # Süreç Rolü
    static_process_roles = """<option value="">Süreç Rolü Seçiniz...</option>
<option value="surec_lideri">Süreç Lideri</option>
<option value="surec_uyesi">Süreç Üyesi</option>
<option value="yonetim_kurulu">Yönetim Kurulu</option>
<option value="genel_mudur">Genel Müdür</option>
<option value="direktor">Direktör</option>"""

    target_proc = '<option value="">Süreç rolü seçiniz...</option>'
    if target_proc in content:
        content = content.replace(target_proc, static_process_roles)
        print("Süreç Rolü dropdown seçenekleri statik olarak eklendi.")

    # 3. Dosyayı kaydet
    with codecs.open(path, 'w', 'utf-8') as f:
        f.write(content)
    
    print("Dosya başarıyla kaydedildi.")

except Exception as e:
    print(f"Hata: {e}")
