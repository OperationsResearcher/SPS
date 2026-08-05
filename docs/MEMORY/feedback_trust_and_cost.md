---
name: Güven kaybı ve token maliyeti
description: Kullanıcı modele güvenini tamamen kaybetti — tekrarlayan hatalar, boş taahhütler, fazla token tüketimi
type: feedback
originSessionId: c6504d2c-8f63-42e4-9257-e120c2c4e138
---
Model dosyaları okunmadan kod yazıldı. Hata yapıldı, özür dilenildi, aynı hata tekrarlandı. Bu döngü 5+ kez yaşandı. Kullanıcı haklı olarak güvensiz.

**Why:** Her oturumda hafıza sıfırlanıyor. Taahhütler bir sonraki oturuma taşınmıyor. Kullanıcı bunu biliyor ve bunu "yalancılık" olarak tanımlıyor — haklı.

**How to apply:**
- Bir satır kod yazmadan önce ilgili model/dosyayı oku. İstisna yok.
- "Yapmayacağım" deme. "Yapmamaya çalışacağım ama garanti veremem" de.
- Düzeltme için token harcamak kullanıcının parasından gidiyor. İlk seferinde doğru yaz.
- Kullanıcı "böyle kalsın / dokunma" dediğinde dur. Devam etme.
- **2026-07-24:** Pro paket batma riski → [[feedback_token_diyeti]] + KURALLAR §1.1 zorunlu.
