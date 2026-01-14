"""
Admin panel template'inde kullanıcı filtreleme kodunu bul
"""

with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Satır 114834 civarında usersPerPage buldum
# Şimdi ondan sonraki kodları oku
start_idx = 114834 - 1  # 0-indexed
end_idx = min(start_idx + 500, len(lines))

print("usersPerPage tanımından sonraki 500 satır:")
print("="*80)
for i in range(start_idx, end_idx):
    if i < len(lines):
        line = lines[i].rstrip()
        if line.strip():  # Boş olmayan satırlar
            print(f"{i+1}: {line[:150]}")

print("\n\n" + "="*80)
print("API çağrısını ara (57553):")
print("="*80)
api_idx = 57553 - 1
start_api = max(0, api_idx - 50)
end_api = min(api_idx + 200, len(lines))

for i in range(start_api, end_api):
    if i < len(lines):
        line = lines[i].rstrip()
        print(f"{i+1}: {line[:120]}")
