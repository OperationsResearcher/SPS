with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    content = f.read()

# deleteUser fonksiyonunu bul
marker = 'async function deleteUser(userId, username) {'
start = content.find(marker)

if start == -1:
    print("NOT FOUND")
    exit(1)

# Fonksiyonun sonunu bul
brace_count = 0
end = start
for i in range(start, len(content)):
    if content[i] == '{':
        brace_count += 1
    elif content[i] == '}':
        brace_count -= 1
        if brace_count == 0:
            end = i + 1
            break

print(f"Found: {start} to {end}, length: {end-start}")

# Yeni fonksiyon
new_func = """async function deleteUser(userId, username) {
    const result = await Swal.fire({
        title: 'Kullanıcı Silme',
        html: `<strong>"${username}"</strong> kullanıcısını silmek istediğinizden emin misiniz?<br><br>` +
              '<div class="alert alert-warning mt-2"><i class="fas fa-exclamation-triangle"></i> Bu işlem geri alınamaz ve kullanıcının tüm verileri arşivlenecektir.</div>',
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
        
        try {
            const response = await fetch(`/api/admin/users/delete/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            });
            
            if (!response.ok) {
                const data = await response.json().catch(() => ({ message: 'Sunucu hatası' }));
                throw new Error(data.message || 'İşlem başarısız');
            }
            
            const data = await response.json();
            
            if (data.success) {
                showToast(data.message, 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showToast(data.message || 'İşlem başarısız', 'error');
            }
        } catch (error) {
            console.error('Kullanıcı silme hatası:', error);
            showToast(error.message || 'Bir hata oluştu', 'error');
        }
    }
}"""

# Değiştir
content = content[:start] + new_func + content[end:]

with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("REPLACED")
