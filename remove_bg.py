"""
Beyaz/gri arka planı tamamen kaldırır.
Yöntem: min(R,G,B) bazlı alpha kanalı hesaplama.
Koyu renkler opak kalır, açık renkler şeffaf olur.
"""
from PIL import Image
import numpy as np

src = r"c:\kokpitim\logok2.png"
dst = r"c:\kokpitim\static\img\kokpitim-logo.png"

img = Image.open(src).convert("RGBA")
data = np.array(img, dtype=np.float64)

R = data[:,:,0]
G = data[:,:,1]
B = data[:,:,2]

# Her pikselin "açıklık" değeri: min(R,G,B) / 255
# Beyaz (255) → açıklık=1.0 → alpha=0
# Koyu lacivert (min≈42) → açıklık≈0.16 → alpha=255
min_rgb = np.minimum(np.minimum(R, G), B)

# Alpha: ne kadar "açık olmayan" piksel → o kadar opak
# Doğrusal değil, 1.5 gamma ile koyu pikseller daha opak olsun
new_alpha = np.power(1.0 - (min_rgb / 255.0), 0.7) * 255.0
new_alpha = np.clip(new_alpha, 0, 255)

# Alpha'yı uygula
data[:,:,3] = new_alpha

result = Image.fromarray(data.astype(np.uint8), "RGBA")
result.save(dst, "PNG")
print(f"Tamamlandı: {dst}")
print(f"Ortalama alpha: {new_alpha.mean():.1f}")
