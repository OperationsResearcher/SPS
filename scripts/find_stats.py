"""
Başlık sayılarını gösteren alanları bul
"""

with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Toplam Kurum'dan sonra sayı gösterildiği kısmı bul
for i, line in enumerate(lines):
    if 'Toplam Kurum' in line:
        print(f"Toplam Kurum bulundu: Satır {i+1}")
        # Sonraki 20 satırı oku
        for j in range(i, min(i+25, len(lines))):
            if lines[j].strip():
                print(f"{j+1}: {lines[j].rstrip()}")
        break

print("\n" + "="*80)
print("Toplam Kullanıcı alanını bul:")
print("="*80)

for i, line in enumerate(lines):
    if 'Toplam Kullanici' in line or 'Toplam KULLANICI' in line:
        print(f"Toplam Kullanıcı bulundu: Satır {i+1}")
        # Sonraki 20 satırı oku
        for j in range(i, min(i+25, len(lines))):
            if lines[j].strip():
                print(f"{j+1}: {lines[j].rstrip()}")
        break
