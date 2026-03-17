"""
deleteOrganization fonksiyonunu bul ve syntax kontrolü yap
"""
with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fonksiyonu bul
start = content.find('async function deleteOrganization')
if start == -1:
    print("✗ Fonksiyon bulunamadı")
    exit(1)

# Fonksiyonun bitişini bul (matching curly braces)
brace_count = 0
in_function = False
end = start

for i in range(start, len(content)):
    char = content[i]
    if char == '{':
        in_function = True
        brace_count += 1
    elif char == '}':
        brace_count -= 1
        if in_function and brace_count == 0:
            end = i + 1
            break

function_code = content[start:end]
print(f"✓ Fonksiyon bulundu: {len(function_code)} karakter")
print(f"✓ Başlangıç: {start}, Bitiş: {end}")

# Syntax kontrolü
if 'response => response.json()' in function_code:
    print("✗ Hala eski kod var (response => response.json())")
elif 'if (!response.ok)' in function_code:
    print("✓ Yeni kod var (response.ok kontrolü)")
else:
    print("? Response handling bulunamadı")

# Fonksiyonu kaydet
with open('deleteOrganization_extracted.js', 'w', encoding='utf-8') as f:
    f.write(function_code)
print("✓ Fonksiyon deleteOrganization_extracted.js'e kaydedildi")
