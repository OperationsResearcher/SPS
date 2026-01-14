"""
Template'den JavaScript kodu çıkar - /api/admin/users çağrısını bul
"""
import re

with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    content = f.read()

# /api/admin/users çağrısının etrafındaki 300 karakteri bul
pattern = r".{300}fetch\('/api/admin/users'\).{500}"
matches = re.finditer(pattern, content)

for i, match in enumerate(matches):
    print(f"\n{'='*80}")
    print(f"Match {i+1}:")
    print(f"{'='*80}")
    print(match.group(0)[:800])
    
    # İlk match'i bulup etrafında kod var mı kontrol et
    if i == 0:
        # Daha geniş bak
        start = max(0, match.start() - 500)
        end = min(len(content), match.end() + 1000)
        print(f"\n\nGENİŞ BAĞLAM:")
        print(content[start:end])
        break
