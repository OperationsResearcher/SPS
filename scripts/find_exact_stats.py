"""
Template'deki istatistik sayılarını gösteren satırları bul
"""

with open('templates/admin_panel.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# İstatistikleri gösteren alanları bul
import re

# Toplam Kurum alanı
match = re.search(r'Toplam Kurum.*?<h3[^>]*>.*?\{\{.*?\|length.*?\}\}', content, re.DOTALL)
if match:
    start = content.rfind('\n', 0, match.start())
    end = content.find('\n', match.end())
    line_num = content[:start].count('\n') + 1
    print(f"Toplam Kurum: Satır {line_num} civarı")
    print(f"Kod: {match.group(0)[:100]}...")

# Toplam Kullanıcı alanı  
match = re.search(r'Toplam.*?[Kk]ullan.*?<h3[^>]*>.*?\{\{.*?\|length.*?\}\}', content, re.DOTALL)
if match:
    start = content.rfind('\n', 0, match.start())
    end = content.find('\n', match.end())
    line_num = content[:start].count('\n') + 1
    print(f"Toplam Kullanıcı: Satır {line_num} civarı")
    print(f"Kod: {match.group(0)[:100]}...")

# Toplam Süreç alanı
match = re.search(r'Toplam.*?[Ss]üreç.*?<h3[^>]*>.*?\{\{.*?\|length.*?\}\}', content, re.DOTALL)
if match:
    start = content.rfind('\n', 0, match.start())
    end = content.find('\n', match.end())
    line_num = content[:start].count('\n') + 1
    print(f"Toplam Süreç: Satır {line_num} civarı")

# Alternatif: kurum|length ile başlayan satırları bul
matches = list(re.finditer(r'kurumlar\|length|kullanicilar\|length|surecler\|length', content))
print(f"\n\nBulunan istatistik gösterimleri:")
for match in matches:
    line_num = content[:match.start()].count('\n') + 1
    print(f"  Satır {line_num}: {match.group(0)}")
