#!/usr/bin/env python
# -*- coding: utf-8 -*-

print("usersTab debug ekleniyor...")

with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    content = f.read()

# usersTab tanımını bul ve debug ekle
old_code = """const usersTab = document.getElementById('users-tab');"""

new_code = """const usersTab = document.getElementById('users-tab');
    console.log('usersTab elementi:', usersTab);"""

if old_code in content:
    content = content.replace(old_code, new_code, 1)
    print("✅ usersTab debug eklendi")
else:
    print("❌ usersTab bulunamadi")

# Event listener'a da debug ekle
old_listener = """usersTab.addEventListener('shown.bs.tab', function() {
            loadAdminUsers();"""

new_listener = """usersTab.addEventListener('shown.bs.tab', function() {
            console.log('>>> Users TAB ACILDI - loadAdminUsers cagiriliyor...');
            loadAdminUsers();"""

if old_listener in content:
    content = content.replace(old_listener, new_listener, 1)
    print("✅ Event listener debug eklendi")
else:
    print("❌ Event listener bulunamadi")

with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ TAMAMLANDI!")
print("Simdi:")
print("1. Ctrl+F5 ile yenile")
print("2. F12 ile console ac")
print("3. Console'da 'usersTab elementi: <button>' gormeli")
print("4. Users sekmesine tikla")
print("5. Console'da '>>> Users TAB ACILDI' gormeli")
