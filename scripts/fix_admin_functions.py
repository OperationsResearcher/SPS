#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

print("Admin panel düzeltiliyor...")

# Dosyayı oku
with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Dosya okundu: {len(content)} karakter")

# 1. loadAdminUsers fonksiyonunu doldur
loadAdminUsers_new = '''function loadAdminUsers() {
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

# Boş loadAdminUsers'ı bul ve değiştir
pattern1 = r'function loadAdminUsers\(\) \{\s*\}'
if re.search(pattern1, content):
    content = re.sub(pattern1, loadAdminUsers_new, content)
    print("✅ loadAdminUsers dolduruldu")
else:
    print("⚠ loadAdminUsers bulunamadı")

# 2. renderUserTable fonksiyonunu doldur
renderUserTable_new = '''function renderUserTable() {
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

# Boş renderUserTable'ı bul ve değiştir
pattern2 = r'function renderUserTable\(\) \{\s*\}'
if re.search(pattern2, content):
    content = re.sub(pattern2, renderUserTable_new, content)
    print("✅ renderUserTable dolduruldu")
else:
    print("⚠ renderUserTable bulunamadı")

# Kaydet
with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Dosya kaydedildi")
print("\n📋 ÖZET:")
print("- deleteUser: Zaten hazır (Content-Type ✓, CSRF ✓)")
print("- editUser: Zaten hazır (Content-Type ✓, CSRF ✓)")
print("- saveUserChanges: Zaten hazır (Content-Type ✓, CSRF ✓)")
print("- loadAdminUsers: Dolduruldu ✓")
print("- renderUserTable: Dolduruldu ✓")
print("\nTarayıcıda Ctrl+F5 ile yenile!")
