"""Fix all encoding issues in admin_panel.html"""
import re
import sys

file_path = r'c:\SPY_Cursor\SP_Code\templates\admin_panel.html'

# Read file as bytes first to see what we're dealing with
with open(file_path, 'rb') as f:
    raw_bytes = f.read()

# Try to determine encoding - should be UTF-8
content_str = raw_bytes.decode('utf-8')

# Create replacements dictionary
# These are the actual corrupted byte sequences we need to fix
replacements = {
    # Turkish character corruptions found in the file
    'FotoÝraf': 'Fotoğraf',
    'Çnizleme': 'Önizleme',
    'Ýþlem': 'İşlem',
    'gerçekleþtirilemedi': 'gerçekleştirilemedi',
    'baÝlan': 'bağlan',
    'oluþtu': 'oluştu',
    'Çrn': 'Örn',
    'Baþarılı': 'Başarılı',
    'eriþilemiyor': 'erişilemiyor',
    'Oluþtur': 'Oluştur',
    'Oluþturuluyor': 'Oluşturuluyor',
    'yüklendiÝinde': 'yüklendiğinde',
}

print("Applying character fixes...")
changed_count = 0
for old, new in replacements.items():
    count = content_str.count(old)
    if count > 0:
        content_str = content_str.replace(old, new)
        changed_count += count
        print(f"  {old} -> {new}: {count} times")

# Fix showToast parameter order
print("\nFixing showToast parameter orders...")
# showToast(message, 'type') -> showToast('type', message)
content_str = re.sub(
    r"showToast\((['\"])([^'\"]+)\1,\s*'(error|warning|success|info)'\)",
    r"showToast('\3', \1\2\1)",
    content_str
)

# Save fixed content
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content_str)

print(f"\nDone! Fixed {changed_count} character encoding issues.")
print("File saved successfully.")
