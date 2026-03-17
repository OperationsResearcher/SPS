"""
Türkçe karakter sorunlu metni bul ve düzelt
"""

with open('templates/admin_panel.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Bozuk metni bul
import re

# "DeÝiþiklikler" veya benzeri karakterler
pattern = r'De[^\s]*i[^\s]*iklikler'
matches = list(re.finditer(pattern, content))

if matches:
    for match in matches:
        line_num = content[:match.start()].count('\n') + 1
        # 100 karakter öncesi ve sonrası
        start = max(0, match.start() - 100)
        end = min(len(content), match.end() + 100)
        
        print(f"Bulundu: Satır {line_num}")
        print(f"Metin: '{match.group(0)}'")
        print(f"\nBağlam:")
        print(content[start:end])
        print("\n" + "="*80)

# Dosyayı düzelt
old_text = 'DeÝiþiklikler'
new_text = 'Değişiklikler'

if old_text in content:
    new_content = content.replace(old_text, new_text)
    with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"\n✓ '{old_text}' -> '{new_text}' değiştirildi!")
else:
    print(f"\n✗ '{old_text}' bulunamadı!")
