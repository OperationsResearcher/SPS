import os

file_path = r"c:\SPY_Cursor\SP_Code\templates\admin_panel_v2.html"

try:
    # Dosyayı oku (encoding hatası varsa ignore)
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Karakter düzeltmeleri
    replacements = {
        'FotoİŸraf': 'Fotoğraf',
        'fotoİŸraf': 'fotoğraf',
        'DeİŸişmez': 'Değişmez',
        'deİŸişmez': 'değişmez',
        'Ç–nizleme': 'Önizleme',
        'BaİŸarılı': 'Başarılı',
        'baİŸarılı': 'başarılı',
        'onchange="handleDüzenleProfilPhotoYükle(this)"': 'onchange="handleDüzenleProfilPhotoYükle(this)"', # Teyit
        'margin-right: 15px;': 'margin-right: 15px;'
    }
    
    # Karakterleri düzelt
    count = 0
    for old, new in replacements.items():
        if old in content:
            content = content.replace(old, new)
            count += 1
    
    print(f"{count} adet karakter/text replace işlemi yapıldı.")

    # Başlık değişikliği - DEBUG için
    mark = " (V3 - DEBUG)"
    if 'Stratejik Planlama' in content and mark not in content:
        # İlk bulduğu başlığı değiştir
        content = content.replace('Stratejik Planlama', 'Stratejik Planlama' + mark, 1)
        print("Başlık güncellendi.")

    # Dosyayı UTF-8 olarak kaydet
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("İşlem tamam. Dosya UTF-8 olarak kaydedildi.")

except Exception as e:
    print(f"Hata: {e}")
