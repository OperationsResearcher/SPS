#!/usr/bin/env python3
"""Buttons rendering'ini düzelt"""
import re

# Dosyayı oku
with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Buttons tanımının iç içe template literals'ı düzelt
# Basit buttons tanımı yapmak
old_pattern = r'const buttons = `\n(.*?)\n    `;'
new_buttons = '''const buttons = `
        <div class="btn-group btn-group-sm" role="group">
            <button class="btn btn-outline-primary" onclick="viewUser(${user.id})" title="Görüntüle">
                <i class="fas fa-eye"></i>
            </button>
            <button class="btn btn-outline-warning" onclick="editUser(${user.id})" title="Düzenle">
                <i class="fas fa-edit"></i>
            </button>
            <button class="btn btn-outline-danger" onclick="deleteUser(${user.id}, '${escapeHtml(user.username)}');" title="Sil">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;'''

# Boş satırları kaldıran bir regex
# renderUserRow fonksiyonunda buttons değişkeni bul
start_idx = content.find('const buttons = `')
if start_idx > -1:
    # const buttons başlangıcından sonra `; bulana kadar
    end_idx = content.find('`;', start_idx)
    if end_idx > -1:
        end_idx += 2
        old_section = content[start_idx:end_idx]
        print(f"Bulundu: {len(old_section)} karakter")
        print(f"İlk 500 karakter:\n{old_section[:500]}")
        
        # Basitleştirilmiş buttons
        new_section = '''const buttons = `<div class="btn-group btn-group-sm" role="group"><button class="btn btn-outline-primary" onclick="viewUser(${user.id})" title="Görüntüle"><i class="fas fa-eye"></i></button><button class="btn btn-outline-warning" onclick="editUser(${user.id})" title="Düzenle"><i class="fas fa-edit"></i></button><button class="btn btn-outline-danger" onclick="deleteUser(${user.id}, '${escapeHtml(user.username)}');" title="Sil"><i class="fas fa-trash"></i></button></div>`;'''
        
        content = content[:start_idx] + new_section + content[end_idx:]
        
        # Dosyaya yaz
        with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ Buttons tanımı düzeltildi")
    else:
        print("✗ Kapanış `; bulunamadı")
else:
    print("✗ const buttons = ` bulunamadı")
