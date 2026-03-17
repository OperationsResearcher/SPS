#!/usr/bin/env python
# -*- coding: utf-8 -*-

print("Event listener düzeltiliyor...")

with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Boş event listener'ı bul ve düzelt
old_pattern = "usersTab.addEventListener('shown.bs.tab', function() {"
idx = content.find(old_pattern)

if idx != -1:
    # Event listener'ın kapanış parantezini bul
    start = idx
    brace_count = 0
    i = idx + len(old_pattern)
    found_open = False
    
    while i < len(content) and i < idx + 500:
        if content[i] == '{':
            brace_count += 1
            found_open = True
        elif content[i] == '}':
            brace_count -= 1
            if found_open and brace_count == -1:
                # Kapanış parantezini bulduk
                end = i + 1
                old_listener = content[start:end]
                
                new_listener = """usersTab.addEventListener('shown.bs.tab', function() {
            console.log('Users tab acildi - loadAdminUsers cagiriliyor');
            loadAdminUsers();
        })"""
                
                content = content.replace(old_listener, new_listener)
                print(f"✅ Event listener duzeltildi (satir ~{content[:start].count(chr(10))+1})")
                
                with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("✅ TAMAMLANDI - Ctrl+F5 ile yenile!")
                print("Users sekmesine tikla ve console'da 'Users tab acildi' mesajini gor")
                break
        i += 1
    else:
        print("❌ Event listener kapanisi bulunamadi")
else:
    print("❌ Event listener bulunamadi")
