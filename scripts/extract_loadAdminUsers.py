"""
loadAdminUsers fonksiyonunun sonundaki kodu bul
"""

with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    content = f.read()

# loadAdminUsers fonksiyonunu bul
import re

# Fonksiyon başlaması
start_pattern = r'function loadAdminUsers\(\)'
start_match = re.search(start_pattern, content)

if start_match:
    start_pos = start_match.start()
    # Fonksiyon sonu (next function veya script kapanış)
    end_pattern = r'\n}\s*\n\s*function|\n}\s*\n\s*<script'
    end_match = re.search(end_pattern, content[start_pos:])
    
    if end_match:
        end_pos = start_pos + end_match.start() + end_match.group(0).find('}')
        func_content = content[start_pos:end_pos]
        
        # Son 500 karakteri göster
        print("loadAdminUsers fonksiyonunun sonu:")
        print("="*80)
        print(func_content[-1500:])
