#!/usr/bin/env python
# -*- coding: utf-8 -*-

print("Admin panel UTF-8 düzeltme ve fonksiyon tamamlama...")

# Binary modda oku, encoding hatalarını ignore et
with open('templates/admin_panel.html', 'rb') as f:
    content_bytes = f.read()

# UTF-8'e çevir, hatalı karakterleri ignore et
content = content_bytes.decode('utf-8', errors='ignore')
print(f"Dosya okundu: {len(content)} karakter")

# loadAdminUsers - TAMAMLANACAK
old_loadAdminUsers = content[content.find('function loadAdminUsers()'):content.find('function loadAdminUsers()') + 1500]
close_brace_idx = old_loadAdminUsers.rfind('}')
if close_brace_idx > 0:
    old_loadAdminUsers = old_loadAdminUsers[:close_brace_idx + 1]

new_loadAdminUsers = '''function loadAdminUsers() {
    console.log('loadAdminUsers cagrildi');
    fetch('/api/admin/users', {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        }
    })
    .then(response => {
        console.log('API yanit:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Data:', data);
        if (data.success) {
            window.adminUsersCache = data.data.users || [];
            window.allowedRoles = data.data.allowed_roles || [];
            console.log('Kullanici sayisi:', window.adminUsersCache.length);
            renderUserTable();
        } else {
            showToast('Kullanicilar yuklenemedi', 'error');
        }
    })
    .catch(error => {
        console.error('Hata:', error);
        showToast('Kullanicilar yuklenemedi', 'error');
    });
}'''

content = content.replace(old_loadAdminUsers, new_loadAdminUsers)
print("✅ loadAdminUsers tamamlandi")

# renderUserTable - TAMAMLANACAK
old_renderUserTable = content[content.find('function renderUserTable()'):content.find('function renderUserTable()') + 1500]
close_brace_idx = old_renderUserTable.rfind('}')
if close_brace_idx > 0:
    old_renderUserTable = old_renderUserTable[:close_brace_idx + 1]

new_renderUserTable = '''function renderUserTable() {
    console.log('renderUserTable cagrildi, kullanici sayisi:', window.adminUsersCache?.length);
    const tbody = document.getElementById('userTableBody');
    if (!tbody) {
        console.error('userTableBody elementi bulunamadi!');
        return;
    }
    
    const users = window.adminUsersCache || [];
    
    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center">Kullanici bulunamadi</td></tr>';
        return;
    }
    
    let html = '';
    users.forEach(user => {
        const profileImg = user.profile_photo ? 
            `/static/uploads/profile_photos/${user.profile_photo}` : 
            '/static/images/default-avatar.png';
        
        html += `
            <tr>
                <td>${user.id}</td>
                <td>
                    <img src="${profileImg}" alt="${user.username}" 
                         style="width:30px;height:30px;border-radius:50%;margin-right:8px;" 
                         onerror="this.src='/static/images/default-avatar.png'">
                    ${user.username}
                </td>
                <td>${user.full_name || ''}</td>
                <td>${user.email || ''}</td>
                <td>${user.sistem_rol || ''}</td>
                <td>${user.kurum_adi || ''}</td>
                <td>${user.process_summary || ''}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="editUser(${user.id})">
                        <i class="fas fa-edit"></i> Duzenle
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id}, '${user.username}')">
                        <i class="fas fa-trash"></i> Sil
                    </button>
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
    console.log('Tablo guncellendi');
}'''

content = content.replace(old_renderUserTable, new_renderUserTable)
print("✅ renderUserTable tamamlandi")

# UTF-8 ile kaydet
with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ TAMAMLANDI!")
print("Ctrl+F5 ile yenile ve F12 ile Console'u ac")
