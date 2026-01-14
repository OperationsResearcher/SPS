with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fonksiyonu basit string replace ile bul
# confirmDelete kullanılan tüm deleteUser fonksiyonunu değiştir

# Önce fonksiyonun yaklaşık yerini bulalım
if 'async function deleteUser(userId, username) {' in content:
    print("✓ Fonksiyon bulundu")
    
    # confirmDelete ile başlayan eski versiyonu bul ve tamamını değiştir
    # Eski pattern - yaklaşık yapı
    start_marker = 'async function deleteUser(userId, username) {'
    
    # Start'ı bul
    idx = content.find(start_marker)
    if idx != -1:
        print(f"✓ Başlangıç index: {idx}")
        
        # İlk { ten sonra kapanan } u bul (brace matching)
        brace_count = 0
        start_idx = idx
        end_idx = idx
        
        i = idx
        while i < len(content):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
            i += 1
        
        if end_idx > start_idx:
            old_func = content[start_idx:end_idx]
            print(f"✓ Fonksiyon bulundu: {len(old_func)} karakter")
            print(f"İlk 100 karakter: {old_func[:100]}")
            
            # Yeni fonksiyon
            new_func = '''async function deleteUser(userId, username) {
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
            content_new = content[:start_idx] + new_func + content[end_idx:]
            
            # Kaydet
            with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
                f.write(content_new)
            
            print(f"✓ Fonksiyon değiştirildi")
            print(f"  Eski: {len(old_func)} karakter")
            print(f"  Yeni: {len(new_func)} karakter")
        else:
            print("✗ Fonksiyon sonu bulunamadı")
else:
    print("✗ Fonksiyon bulunamadı")
