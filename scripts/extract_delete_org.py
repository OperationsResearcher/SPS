"""
deleteOrganization fonksiyonunun tam içeriğini çıkar
"""

with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Satır 101152'den başla
start = 101152 - 1
in_function = False
func_lines = []
brace_count = 0

for i in range(start, min(start + 200, len(lines))):
    line = lines[i]
    
    if 'async function deleteOrganization' in line:
        in_function = True
    
    if in_function:
        func_lines.append(f"{i+1}: {line.rstrip()}")
        
        # Parantez sayısını takip et
        brace_count += line.count('{') - line.count('}')
        
        # Fonksiyon bittiğinde dur
        if brace_count == 0 and len(func_lines) > 5:
            break

print("deleteOrganization fonksiyonu:")
print("="*80)
for line in func_lines[:50]:  # İlk 50 satır
    print(line)
