"""
deleteUser fonksiyonunu SweetAlert2 ile güncelle ve CSRF token ekle
"""
with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    content = f.read()

# deleteUser fonksiyonunu bul
marker = 'async function deleteUser(userId, username) {'

if marker in content:
    start = content.find(marker)
    
    # Fonksiyonun sonunu bul
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
    
    # Yeni fonksiyon
    new_function = '''async function deleteUser(userId, username) {
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
}'''
    
    # Değiştir
    content = content[:start] + new_function + content[end:]
    
    with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ deleteUser fonksiyonu güncellendi")
    print(f"  Eski: {end - start} karakter")
    print(f"  Yeni: {len(new_function)} karakter")
else:
    print("✗ deleteUser fonksiyonu bulunamadı")
