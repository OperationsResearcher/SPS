"""
Admin panel template'deki başlık/dashboard istatistik alanını bul
"""

with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Satır 2449'daki "Toplam Kurum" civarında kodu oku
start = 2449 - 50  # 50 satır öncesinden
end = 2449 + 100   # 100 satır sonrasına kadar

print("Başlık/Dashboard İstatistik Alanı:")
print("="*80)

for i in range(start-1, min(end, len(lines))):
    line = lines[i].rstrip()
    # Boş olmayan satırları göster
    if line.strip() or i == 2449-1:
        print(f"{i+1}: {line[:120]}")
