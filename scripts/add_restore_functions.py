"""
Admin panele silinmiş kurumlar için JavaScript fonksiyonları ekle
"""
with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    content = f.read()

# deleteOrganization fonksiyonundan sonra yeni fonksiyonları ekle
marker = 'async function deleteOrganization(orgAd, orgId) {'

if marker in content:
    # deleteOrganization fonksiyonunun sonunu bul
    start = content.find(marker)
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
    
    # Yeni fonksiyonlar
    new_functions = '''

// Silinmiş kurumları yükle
async function loadDeletedOrganizations() {
    const loading = document.getElementById('deleted-organizations-loading');
    const content = document.getElementById('deleted-organizations-content');
    const empty = document.getElementById('deleted-organizations-empty');
    const tableBody = document.getElementById('deleted-organizations-table-body');
    
    loading.style.display = 'block';
    content.style.display = 'none';
    
    try {
        const response = await fetch('/admin/deleted-organizations');
        const result = await response.json();
        
        if (result.success && result.data.length > 0) {
            tableBody.innerHTML = '';
            
            result.data.forEach(kurum => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><strong>${kurum.kisa_ad}</strong></td>
                    <td>${kurum.ticari_unvan}</td>
                    <td>${kurum.deleted_at || '-'}</td>
                    <td>${kurum.deleted_by_name || '-'}</td>
                    <td><span class="badge bg-secondary">${kurum.user_count} kullanıcı</span></td>
                    <td><span class="badge bg-info">${kurum.surec_count} süreç</span></td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-success" onclick="restoreOrganization('${kurum.kisa_ad}', ${kurum.id})">
                            <i class="fas fa-undo me-1"></i>Geri Getir
                        </button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
            
            empty.style.display = 'none';
            content.style.display = 'block';
        } else {
            empty.style.display = 'block';
            content.style.display = 'block';
        }
    } catch (error) {
        console.error('Silinmiş kurumlar yükleme hatası:', error);
        showToast('Silinmiş kurumlar yüklenirken hata oluştu', 'error');
    } finally {
        loading.style.display = 'none';
    }
}

// Kurum geri getir
async function restoreOrganization(orgName, orgId) {
    const result = await Swal.fire({
        title: 'Kurum Geri Getirme',
        html: `
            <p><strong>"${orgName}"</strong> kurumunu geri getirmek istediğinizden emin misiniz?</p>
            <div class="form-check text-start mt-3">
                <input class="form-check-input" type="checkbox" id="restore-users" checked>
                <label class="form-check-label" for="restore-users">
                    Kullanıcıları da geri getir
                </label>
            </div>
            <div class="form-check text-start mt-2">
                <input class="form-check-input" type="checkbox" id="restore-processes" checked>
                <label class="form-check-label" for="restore-processes">
                    Süreçleri de geri getir
                </label>
            </div>
        `,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#28a745',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Geri Getir',
        cancelButtonText: 'İptal',
        preConfirm: () => {
            return {
                restore_users: document.getElementById('restore-users').checked,
                restore_processes: document.getElementById('restore-processes').checked
            };
        }
    });
    
    if (result.isConfirmed) {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        
        try {
            const response = await fetch(`/admin/restore-organization/${orgId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(result.value)
            });
            
            const data = await response.json();
            
            if (data.success) {
                showToast(data.message, 'success');
                // Hem silinmiş listesini hem aktif listesini yenile
                loadDeletedOrganizations();
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showToast(data.message || 'Geri getirme başarısız', 'error');
            }
        } catch (error) {
            console.error('Geri getirme hatası:', error);
            showToast('Bir hata oluştu', 'error');
        }
    }
}

// Silinmiş Kurumlar tab'ı açıldığında veri yükle
document.addEventListener('DOMContentLoaded', function() {
    const deletedTab = document.getElementById('deleted-organizations-tab');
    if (deletedTab) {
        deletedTab.addEventListener('shown.bs.tab', function() {
            loadDeletedOrganizations();
        });
    }
});
'''
    
    # Fonksiyonu ekle
    content = content[:end] + new_functions + content[end:]
    print("✓ JavaScript fonksiyonları eklendi")
    
    # Kaydet
    with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Dosya kaydedildi")
else:
    print("✗ deleteOrganization fonksiyonu bulunamadı")
