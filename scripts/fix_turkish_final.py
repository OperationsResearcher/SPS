"""
Türkçe karakter sorununu düzelt
"""

with open('templates/admin_panel.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Bozuk metin
old_text = 'DeİŸişiklikler'
new_text = 'Değişiklikler'

if old_text in content:
    new_content = content.replace(old_text, new_text)
    with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"✓ '{old_text}' -> '{new_text}' değiştirildi!")
else:
    print(f"✗ '{old_text}' bulunamadı!")
    
    # Alternatif karakterler dene
    alternatives = [
        'De\\u0130\\u015fişiklikler',
        'Deiþiklikler',
        'DeYişiklikler'
    ]
    
    for alt in alternatives:
        if alt in content:
            print(f"Alternatif bulundu: {alt}")
            break
