import os

# Bozuk karakter haritası (Önce uzun stringler, sonra karakterler)
replacements = {
    'deÝŸiþtirin': 'değiştirin',
    'Ã§': 'ç',
    'Ã¼': 'ü',
    'Ã¶': 'ö',
    'Ä±': 'ı',
    'Ã°': 'ğ',
    'ÅŸ': 'ş',
    'Ä°': 'İ',
    'Ã—': 'Ö',
    'Ã‡': 'Ç',
    'ÄŸ': 'ğ',
    'Åž': 'Ş',
    'Ã–': 'Ö',
    'Ãœ': 'Ü',
    'Ý': 'İ',
    'þ': 'ş',
    'ð': 'ğ',
    'ý': 'ı',
    'Þ': 'Ş',
    'Ð': 'Ğ'
}

templates_dir = r"c:\SPY_Cursor\SP_Code\templates"

for filename in os.listdir(templates_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(templates_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            # Önce özel kelimeleri düzelt
            if 'deÝŸiþtirin' in new_content:
                new_content = new_content.replace('deÝŸiþtirin', 'değiştirin')
                
            # Genel karakterleri düzelt
            for bad, good in replacements.items():
                if bad in new_content:
                    new_content = new_content.replace(bad, good)
            
            if new_content != content:
                print(f"Duzeltiliyor: {filename}")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
        except Exception as e:
            print(f"Hata ({filename}): {e}")
