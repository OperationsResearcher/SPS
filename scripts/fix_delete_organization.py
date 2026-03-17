"""
deleteOrganization fonksiyonunu bul ve düzelt
"""

with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Bozuk metni bul ve düzelt
old_text = 'kurumunu silmek istediðinizden emin misiniz?", "Bu iþlem geri alınamaz'
new_text = 'kurumunu silmek istediğinizden emin misiniz?", "Bu işlem geri alınamaz'

if old_text in content:
    content = content.replace(old_text, new_text)
    print("✓ Türkçe karakterler düzeltildi")

# deleteOrganization fonksiyonunu confirmDelete yerine Swal.fire ile değiştir
import re

# Fonksiyonun başını bul
pattern = r'async function deleteOrganization\(orgAd, orgId\) \{.*?const confirmed = await confirmDelete\([^)]+\);.*?if \(confirmed\) \{'
match = re.search(pattern, content, re.DOTALL)

if match:
    old_func = match.group(0)
    
    new_func = '''async function deleteOrganization(orgAd, orgId) {
    // Toaster ile onay iste
    const result = await Swal.fire({
        title: 'Kurum Silme',
        html: `<strong>"${orgAd}"</strong> kurumunu silmek istediğinizden emin misiniz?<br><br>` +
              '<div class="alert alert-warning mt-2"><i class="fas fa-exclamation-triangle"></i> Bu işlem geri alınamaz ve kurumdaki tüm kullanıcılar, süreçler ve veriler silinecektir!</div>',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Tamam',
        cancelButtonText: 'İptal',
        focusCancel: true
    });

    if (result.isConfirmed) {'''
    
    content = content.replace(old_func, new_func)
    print("✓ confirmDelete -> Swal.fire olarak değiştirildi")
else:
    print("✗ Fonksiyon bulunamadı")

# Kaydet
with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Dosya kaydedildi")
