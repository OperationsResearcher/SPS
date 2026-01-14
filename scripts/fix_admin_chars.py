import os

# Bozuklukları düzelt
file_path = r"c:\SPY_Cursor\SP_Code\templates\admin_panel.html"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Spesifik kelimeler (Ekran görüntüsünden)
content = content.replace('FotoİŸraf', 'Fotoğraf')
content = content.replace('deİŸiş', 'değiş')
content = content.replace('deİŸiþ', 'değiş')
content = content.replace('baİŸlan', 'bağlan')
content = content.replace('beİŸen', 'beğen')
content = content.replace('İçeriİŸi', 'İçeriği')

# Genel karakterler (Kalanlar için)
content = content.replace('İŸ', 'ğ') # En yaygın bozukluk
content = content.replace('Ç–', 'Ö') # Ö yerine Ç-
content = content.replace('İşlem', 'İşlem') # Doğru
content = content.replace('Ã§', 'ç')
content = content.replace('Ã¼', 'ü')
content = content.replace('Ã¶', 'ö')
content = content.replace('Ã–', 'Ö')
content = content.replace('Ã‡', 'Ç')
content = content.replace('ÄŸ', 'ğ')
content = content.replace('Ä°', 'İ')
content = content.replace('ÅŸ', 'ş')
content = content.replace('Åž', 'Ş')

# Kaydet
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Düzeltme tamamlandı.")
