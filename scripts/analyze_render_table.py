"""
renderUserTable ve renderUserPagination fonksiyonlarını bul ve analiz et
"""

with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# renderUserTable fonksiyonunu bul
match = re.search(r'function renderUserTable\(\)\s*{(.*?)(\n\s*function|\n\s*</script>)', content, re.DOTALL)
if match:
    func_body = match.group(1)
    # Paketleme kaldır
    lines = func_body.split('\n')
    cleaned = [l.strip() for l in lines if l.strip() and not l.strip().startswith('//')]
    
    print("renderUserTable Mantığı:")
    print("="*80)
    print('\n'.join(cleaned[:40]))  # İlk 40 satır
    
    print("\n\n... (ortası atlandı) ...\n")
    print('\n'.join(cleaned[-20:]))  # Son 20 satır
