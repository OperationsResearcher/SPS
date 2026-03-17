"""
Satır bazlı replace işlemi
"""

with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Satır 101152'den itibaren deleteOrganization fonksiyonunu bul
target_line = 101152 - 1  # 0-indexed

# Fonksiyon başlangıcını kontrol et
if 'deleteOrganization' in lines[target_line]:
    print(f"✓ Satır {target_line + 1}: {lines[target_line].strip()}")
    
    # Yeni fonksiyon başlangıcı
    new_function_lines = [
        'async function deleteOrganization(orgAd, orgId) {\n',
        '    // Toaster ile onay iste\n',
        '    const result = await Swal.fire({\n',
        '        title: \'Kurum Silme\',\n',
        '        html: `<strong>"${orgAd}"</strong> kurumunu silmek istediğinizden emin misiniz?<br><br>` +\n',
        '              \'<div class="alert alert-warning mt-2"><i class="fas fa-exclamation-triangle"></i> Bu işlem geri alınamaz ve kurumdaki tüm kullanıcılar, süreçler ve veriler silinecektir!</div>\',\n',
        '        icon: \'warning\',\n',
        '        showCancelButton: true,\n',
        '        confirmButtonColor: \'#dc3545\',\n',
        '        cancelButtonColor: \'#6c757d\',\n',
        '        confirmButtonText: \'Tamam\',\n',
        '        cancelButtonText: \'İptal\',\n',
        '        focusCancel: true\n',
        '    });\n',
        '\n',
        '    if (result.isConfirmed) {\n'
    ]
    
    # Satır 101152'den başla, "if (confirmed)" satırını bul
    skip_until_line = target_line + 1
    for i in range(target_line + 1, min(target_line + 50, len(lines))):
        if 'if (confirmed)' in lines[i] or 'if(confirmed)' in lines[i]:
            skip_until_line = i + 1
            print(f"✓ 'if (confirmed)' bulundu satır {i + 1}")
            break
    
    # Yeni satırları oluştur
    new_lines = lines[:target_line] + new_function_lines + lines[skip_until_line:]
    
    # Kaydet
    with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✓ {len(new_function_lines)} yeni satır eklendi")
    print(f"✓ {skip_until_line - target_line} eski satır silindi")
    print("✓ Dosya kaydedildi!")
else:
    print("❌ deleteOrganization fonksiyonu bulunamadı!")
