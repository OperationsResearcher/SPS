"""Fix Turkish character encoding and showToast parameter order issues in admin_panel.html"""
import re

file_path = r'c:\SPY_Cursor\SP_Code\templates\admin_panel.html'

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

original_content = content

# Fix Turkish character encoding issues - these are actually corrupted in the file
replacements = {
    'FotoÝraf': 'Fotoğraf',
    'Çnizleme': 'Önizleme',
    'Ýþlem': 'İşlem',
    'gerçekleþtirilemedi': 'gerçekleştirilemedi',
    'Lütfen': 'Lütfen',  # Already correct but include for consistency
    'baÝlan': 'bağlan',
    'oluþtu': 'oluştu',
    'Çrn': 'Örn',
    'Yükle': 'Yükle',  # Already correct
    'photoYükle': 'photoYukle',  # Fix variable names with Turkish chars
    'Baþarılı': 'Başarılı',
    'eriþilemiyor': 'erişilemiyor',
    'Oluþtur': 'Oluştur',
    'Oluþturuluyor': 'Oluşturuluyor',
    'yüklendiÝinde': 'yüklendiğinde',
}

for old, new in replacements.items():
    content = content.replace(old, new)

# Fix showToast parameter order issues
# Pattern: showToast(message, 'type') should be showToast('type', message)
# But be careful - showToast('type', message, title) is already correct

# Fix: showToast(data.message, 'success') -> showToast('success', data.message)
content = re.sub(
    r"showToast\(data\.message,\s*'success'\)",
    "showToast('success', data.message)",
    content
)

# Fix: showToast('message...', 'error') -> showToast('error', 'message...')
# Only when first param is a string literal (starts with quotes)
content = re.sub(
    r"showToast\((['\"])([^'\"]+)\1,\s*'(error|warning|info|success)'\)",
    r"showToast('\3', \1\2\1)",
    content
)

# Save the file
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Count changes
if content != original_content:
    print(f"✓ File updated successfully")
    print(f"  Total characters changed: {sum(1 for a, b in zip(original_content, content) if a != b)}")
    
    # Show some sample changes
    print("\nSample fixes applied:")
    for old, new in list(replacements.items())[:5]:
        count = original_content.count(old)
        if count > 0:
            print(f"  - '{old}' -> '{new}' ({count} occurrences)")
else:
    print("No changes needed")
