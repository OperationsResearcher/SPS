"""
deleteOrganization fonksiyonunu güncelle
"""

with open('templates/admin_panel.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Eski kod
old_code = '''function deleteOrganization(orgAd, orgId) {
    if (confirm(`"${orgAd}" kurumunu silmek istediİŸinizden emin misiniz?\\n\\nBu işlem geri alınamaz ve kurumdaki tüm kullanıcılar, süreçler ve veriler silinecektir!`)) {'''

# Yeni kod - Swal.fire ile
new_code = '''async function deleteOrganization(orgAd, orgId) {
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

if old_code in content:
    content = content.replace(old_code, new_code)
    print("✓ Fonksiyon güncellendi")
else:
    # Alternatif - sadece bozuk karakteri düzelt
    alt_old = 'kurumunu silmek istediİŸinizden'
    alt_new = 'kurumunu silmek istediğinizden'
    if alt_old in content:
        content = content.replace(alt_old, alt_new)
        print("✓ Türkçe karakter düzeltildi")
    
    # Şimdi confirm'i Swal.fire ile değiştir
    pattern1 = 'function deleteOrganization(orgAd, orgId) {'
    pattern2 = 'if (confirm('
    
    if pattern1 in content and pattern2 in content:
        # Fonksiyonu bul
        func_start = content.find(pattern1)
        # if (confirm(...)) bul
        if_start = content.find(pattern2, func_start, func_start + 500)
        
        if if_start > 0:
            # if (confirm(...)) { ifadesinin sonunu bul
            paren_count = 0
            in_backtick = False
            i = if_start + len('if (confirm(')
            
            for j in range(i, min(i + 500, len(content))):
                char = content[j]
                if char == '`':
                    in_backtick = not in_backtick
                if not in_backtick:
                    if char == '(':
                        paren_count += 1
                    elif char == ')':
                        if paren_count == 0:
                            # Bu closing paren
                            # )) { bulmalıyız
                            remaining = content[j:j+10]
                            if ')) {' in remaining:
                                close_brace_pos = j + remaining.find(')) {') + 4
                                
                                # Eski kodu al
                                old_section = content[func_start:close_brace_pos]
                                print(f"Eski kod bulundu ({len(old_section)} karakter)")
                                
                                # Yeni kod
                                new_section = new_code
                                
                                # Değiştir
                                content = content[:func_start] + new_section + content[close_brace_pos:]
                                print("✓ Kod değiştirildi!")
                                break
                        else:
                            paren_count -= 1

# Kaydet
with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Dosya kaydedildi!")
