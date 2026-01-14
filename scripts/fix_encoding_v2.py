import os

# Bozuk karakter haritası
# Önce uzun/spesifik kalıplar, sonra tek karakterler
replacements = {
    'deİŸiştirin': 'değiştirin',
    'deÝŸiþtirin': 'değiştirin',
    'ÝŸ': 'ğ',
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
    'Ý': 'İ', # Dikkatli ol
    'þ': 'ş',
    'ð': 'ğ',
    'ý': 'ı',
    'Þ': 'Ş',
    'Ð': 'Ğ',
    'Ÿ': '' # Eğer tek başına kaldıysa sil veya yumuşak g? (deİ -> deği)
}

templates_dir = r"c:\SPY_Cursor\SP_Code\templates"

for filename in os.listdir(templates_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(templates_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            for bad, good in replacements.items():
                if bad in new_content:
                    new_content = new_content.replace(bad, good)
            
            # Ekstra kontrol: deİiştirin gibi bir şey kaldı mı?
            if 'deİiştirin' in new_content:
                new_content = new_content.replace('deİiştirin', 'değiştirin')

            if new_content != content:
                print(f"Duzeltiliyor: {filename}")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
        except Exception as e:
            print(f"Hata ({filename}): {e}")
