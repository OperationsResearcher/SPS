#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

# Dosyayı binary modda okuyup encoding sorununu çöz
try:
    with open('templates/admin_panel.html', 'rb') as f:
        content_bytes = f.read()
    
    # UTF-8 ile decode et, hatalı karakterleri replace et
    content = content_bytes.decode('utf-8', errors='ignore')
    print(f"Dosya okundu: {len(content)} karakter")
    
    # loadAdminUsers fonksiyonunu bul ve doldur
    loadAdminUsers_pattern = r'function loadAdminUsers\(\) \{[^}]*\}'
    loadAdminUsers_replacement = '''function loadAdminUsers() {
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
            showToast('Kullanıcılar yüklenemedi: ' + (data.message || ''), 'error');
        }
    })
    .catch(error => {
        console.error('Kullanıcılar yüklenirken hata:', error);
        showToast('Kullanıcılar yüklenemedi', 'error');
    });
}'''
    
    content = re.sub(loadAdminUsers_pattern, loadAdminUsers_replacement, content, flags=re.DOTALL)
    print("loadAdminUsers güncellendi")
    
    # renderUserTable fonksiyonunu bul ve doldur
    renderUserTable_pattern = r'function renderUserTable\(\) \{[^}]*\}'
    renderUserTable_replacement = '''function renderUserTable() {
    const tbody = document.querySelector('#userTableBody');
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
                         style="width: 30px; height: 30px; border-radius: 50%; margin-right: 8px;" 
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
    
    content = re.sub(renderUserTable_pattern, renderUserTable_replacement, content, flags=re.DOTALL)
    print("renderUserTable güncellendi")
    
    # UTF-8 ile kaydet
    with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Dosya başarıyla güncellendi ve UTF-8 olarak kaydedildi")
    
except Exception as e:
    print(f"❌ Hata: {e}")
    import traceback
    traceback.print_exc()
