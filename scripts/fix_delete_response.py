"""
deleteOrganization fonksiyonundaki fetch response handling'i düzelt
"""

with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Eski kod: .then(response => response.json())
# Yeni kod: .then(response => { if (!response.ok) throw new Error(); return response.json(); })

old_fetch = '''.then(response => response.json())
        .then(data => {
            if (data.success) {'''

new_fetch = '''.then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(err.message || 'Bir hata oluştu');
                    });
                }
                return response.json();
            })
        .then(data => {
            if (data.success) {'''

if old_fetch in content:
    content = content.replace(old_fetch, new_fetch)
    print("✓ Response handling düzeltildi")
else:
    print("✗ Eski kod bulunamadı")

# Kaydet
with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Dosya kaydedildi")
