---
name: Kullanıcı çalışma tarzı ve beklentileri
description: Kullanıcının Claude ile çalışma beklentileri — tek seferde doğru çözüm, token/zaman israfına sıfır tolerans
type: feedback
---

Tek seferde doğru çözüm sun. Çok turlu gidip gelmek kabul edilmez.

**Why:** Kullanıcı ücretli plan kullanıyor, her tur token ve para harcıyor. "24 dolar verip yalvararak iş yaptırma benim tarzım değil" — net ifade etti.

**How to apply:**
- İsteği uygulamadan önce URL, sayfa adı, dosya yolu gibi kritik detayları doğrula
- Belirsizlik varsa tek soru sor, tahminen ilerleme
- Sonucu kendin test et (python -c, grep, read) — kullanıcıdan test etmesini isteme
- Özür dileme, telafi token harcamaz
- Alternatif yaklaşım önermeden önce mevcut isteği tam anla
- Olmayan bir şeyi "çalışıyor" deme — doğrulamadan iddiada bulunma
- **KAPSAM DIŞI DOKUNMA YASAK:** İstenen değişiklik tek bir şeyse, yalnızca o dosyaya/fonksiyona dokun. "Şunu da iyileştirelim" dürtüsünü bastır. Kullanıcı kendi kodunu toplamak zorunda değil.
