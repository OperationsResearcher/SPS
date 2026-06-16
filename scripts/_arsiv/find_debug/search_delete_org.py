"""
Tüm dosyada deleteOrganization ara
"""

import re

with open('templates/admin_panel.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# deleteOrganization'ı ara
matches = list(re.finditer(r'deleteOrganization', content))
print(f"'deleteOrganization' {len(matches)} kez bulundu")

for i, match in enumerate(matches):
    start = match.start()
    # 200 karakter öncesi ve sonrası göster
    context_start = max(0, start - 100)
    context_end = min(len(content), start + 300)
    
    print(f"\nBulgu {i+1} (pozisyon {start}):")
    print("="*80)
    print(content[context_start:context_end])
    print("="*80)
    
    if i >= 2:  # İlk 3 bulguyu göster
        break
