"""
deleteOrganization fonksiyonuna response.ok kontrolü ekle
"""
import re

with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    content = f.read()

# async function deleteOrganization bulalım
pattern = r'(async function deleteOrganization\(orgAd, orgId\) \{.*?\.then\(response => )response\.json\(\)(.*?\.catch\(error =>)'

new_code = r'''\1{
            if (!response.ok) {
                return response.json().catch(() => {
                    throw new Error('Bir hata oluştu');
                }).then(err => {
                    throw new Error(err.message || 'Bir hata oluştu');
                });
            }
            return response.json();
        })\2'''

content_new = re.sub(pattern, new_code, content, flags=re.DOTALL)

if content_new != content:
    with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
        f.write(content_new)
    print("✓ Response handling düzeltildi")
else:
    print("✗ Pattern eşleşmedi")
