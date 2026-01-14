#!/usr/bin/env python
# -*- coding: utf-8 -*-

print("Kullanıcı yönetimi fonksiyonları tamamlanıyor...")

with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Dosya boyutu: {len(content)} karakter")

# İHTİYAÇ: Bu 3 fonksiyonu bul ve TAMAM olarak değiştir

# 1. setUserTableLoading - Bu zaten tamam olabilir, kontrol et
if 'function setUserTableLoading()' in content:
    print("✓ setUserTableLoading bulundu")

# 2. loadAdminUsers - TAMAMLANACAK
# Eski eksik kodu bul
old_loadAdminUsers = content[content.find('function loadAdminUsers()'):content.find('function loadAdminUsers()') + 1500]
close_brace_idx = old_loadAdminUsers.rfind('}')
if close_brace_idx > 0:
    old_loadAdminUsers = old_loadAdminUsers[:close_brace_idx + 1]

new_loadAdminUsers = '''function loadAdminUsers() {
    fetch('/api/admin/users', {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.adminUsersCache = data.data.users || [];
            window.allowedRoles = data.data.allowed_roles || [];
            renderUserTable();
        } else {
            showToast('Kullanıcılar yüklenemedi', 'error');
        }
    })
    .catch(error => {
        console.error('Hata:', error);
        showToast('Kullanıcılar yüklenemedi', 'error');
    });
}'''

content = content.replace(old_loadAdminUsers, new_loadAdminUsers)
print("✅ loadAdminUsers değiştirildi")

# 3. renderUserTable - TAMAMLANACAK
old_renderUserTable = content[content.find('function renderUserTable()'):content.find('function renderUserTable()') + 1500]
close_brace_idx = old_renderUserTable.rfind('}')
if close_brace_idx > 0:
    old_renderUserTable = old_renderUserTable[:close_brace_idx + 1]

new_renderUserTable = '''function renderUserTable() {
    const tbody = document.getElementById('userTableBody');
    if (!tbody) return;
    
    const users = window.adminUsersCache || [];
    
    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center">Kullanıcı bulunamadı</td></tr>';
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
                        <i class="fas fa-edit"></i> Düzenle
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id}, '${user.username}')">
                        <i class="fas fa-trash"></i> Sil
                    </button>
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}'''

content = content.replace(old_renderUserTable, new_renderUserTable)
print("✅ renderUserTable değiştirildi")

# Kaydet
with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Tamamlandı - Ctrl+F5 ile yenile!")
