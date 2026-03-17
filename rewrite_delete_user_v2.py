"""
Line 131154'teki deleteUser fonksiyonunu bul ve değiştir
"""
with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line 131154 (0-indexed olarak 131153)
start_line = 131153

# O satırdan başla ve async function deleteUser'ı bul
found = False
for i in range(start_line, min(start_line + 100, len(lines))):
    if 'async function deleteUser' in lines[i]:
        start_line = i
        found = True
        break

if not found:
    print(f"✗ Fonksiyon bulunamadı (line {start_line} civarı)")
    exit(1)

# Fonksiyonun bitişini bul
brace_count = 0
in_function = False
end_line = start_line

for i in range(start_line, len(lines)):
    for char in lines[i]:
        if char == '{':
            in_function = True
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if in_function and brace_count == 0:
                end_line = i + 1
                break
    if end_line > start_line:
        break

print(f"✓ Fonksiyon bulundu: lines {start_line + 1} - {end_line}")

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
}
'''

# Değiştir
new_lines = lines[:start_line] + [new_function] + lines[end_line:]

# Kaydet
with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"✓ Fonksiyon değiştirildi ({end_line - start_line} satır → 1 satır)")
