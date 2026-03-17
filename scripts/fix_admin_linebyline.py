#!/usr/bin/env python
# -*- coding: utf-8 -*-

print("Satır bazlı düzeltme başlıyor...")

# Dosyayı satır satır oku
with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Toplam {len(lines)} satır okundu")

# loadAdminUsers fonksiyonu için yeni kod (114930'dan başlayacak)
loadAdminUsers_code = '''function loadAdminUsers() {
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
}

'''

# renderUserTable fonksiyonu için yeni kod (117330'dan başlayacak)
renderUserTable_code = '''function renderUserTable() {
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
}

'''

# loadAdminUsers'ın kapanış parantezini bul (satır 114930'dan başla)
start_idx = 114929  # 0-based index
found_start = False
for i in range(start_idx, min(start_idx + 100, len(lines))):
    if 'function loadAdminUsers()' in lines[i]:
        found_start = True
        # Boş fonksiyonun kapanış süslü parantezini bul
        brace_count = 0
        start_line = i
        for j in range(i, min(i + 50, len(lines))):
            brace_count += lines[j].count('{') - lines[j].count('}')
            if brace_count == 0 and j > i:
                # Fonksiyonu değiştir
                end_line = j
                lines[start_line:end_line+1] = [loadAdminUsers_code]
                print(f"✅ loadAdminUsers değiştirildi (satır {start_line+1} - {end_line+1})")
                break
        break

if not found_start:
    print("⚠ loadAdminUsers bulunamadı")

# renderUserTable'ın kapanış parantezini bul (satır 117330'dan başla)
start_idx = 117329  # 0-based index
found_start = False
for i in range(start_idx, min(start_idx + 100, len(lines))):
    if 'function renderUserTable()' in lines[i]:
        found_start = True
        # Boş fonksiyonun kapanış süslü parantezini bul
        brace_count = 0
        start_line = i
        for j in range(i, min(i + 100, len(lines))):
            brace_count += lines[j].count('{') - lines[j].count('}')
            if brace_count == 0 and j > i:
                # Fonksiyonu değiştir
                end_line = j
                lines[start_line:end_line+1] = [renderUserTable_code]
                print(f"✅ renderUserTable değiştirildi (satır {start_line+1} - {end_line+1})")
                break
        break

if not found_start:
    print("⚠ renderUserTable bulunamadı")

# Dosyayı kaydet
with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Dosya kaydedildi - Ctrl+F5 ile yenile!")
