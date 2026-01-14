"""
deleteOrganization fonksiyonunu tamamen yeniden yaz
"""
with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Yeni fonksiyon
new_function = '''async function deleteOrganization(orgAd, orgId) {
    const result = await Swal.fire({
        title: 'Kurum Silme',
        html: `<strong>"${orgAd}"</strong> kurumunu silmek istediğinizden emin misiniz?<br><br>` +
              '<div class="alert alert-warning mt-2"><i class="fas fa-exclamation-triangle"></i> Bu işlem geri alınamaz ve kurumdaki tüm kullanıcılar, süreçler ve veriler silinecektir!</div>',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Evet, Sil',
        cancelButtonText: 'İptal',
        focusCancel: true
    });

    if (result.isConfirmed) {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        fetch(`/admin/delete-organization/${orgId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.message || 'İşlem başarısız oldu');
                }).catch(err => {
                    if (err.message) {
                        throw err;
                    }
                    throw new Error('Sunucu hatası');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                showToast(data.message, 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showToast(data.message || 'İşlem başarısız', 'error');
            }
        })
        .catch(error => {
            console.error('Silme hatası:', error);
            showToast(error.message || 'Bir hata oluştu', 'error');
        });
    }
}'''

# Mevcut fonksiyonu bul
start = content.find('async function deleteOrganization(orgAd, orgId) {')
if start == -1:
    print("✗ Fonksiyon bulunamadı")
    exit(1)

# Curly brace matching ile fonksiyonun sonunu bul
brace_count = 0
in_function = False
end = start

for i in range(start, len(content)):
    char = content[i]
    if char == '{':
        in_function = True
        brace_count += 1
    elif char == '}':
        brace_count -= 1
        if in_function and brace_count == 0:
            end = i + 1
            break

old_func_len = end - start
print(f"✓ Fonksiyon bulundu: {old_func_len} karakter")

# Değiştir
content_new = content[:start] + new_function + content[end:]

# Kaydet
with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
    f.write(content_new)

print(f"✓ Fonksiyon değiştirildi")
print(f"  Eski: {old_func_len} karakter")
print(f"  Yeni: {len(new_function)} karakter")
print(f"  Fark: {len(new_function) - old_func_len:+d} karakter")
