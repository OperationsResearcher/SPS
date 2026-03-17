"""
Tüm istatistik alanlarını bul
"""

with open('templates/admin_panel.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Tüm istatistikleri bul
search_terms = ['Toplam', 'TOPLAM']

for search in search_terms:
    for i, line in enumerate(lines):
        if search in line and ('Kurum' in line or 'Kullan' in line or 'Süreç' in line or 'Strateji' in line):
            # Sonraki 3 satırda sayı var mı kontrol et
            for j in range(i, min(i+8, len(lines))):
                if '|length' in lines[j] or 'innerHTML' in lines[j] or '<h3' in lines[j]:
                    print(f"{i+1}: {lines[i].strip()[:80]}")
                    print(f"    Sayı Satırı {j+1}: {lines[j].strip()[:80]}")
                    print()
                    break
