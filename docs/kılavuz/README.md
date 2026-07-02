# Kılavuz & Video Dokümantasyonu

Bu klasör, **Kullanım Kılavuzu & Video Oluşturucu** girişimine ait **her türlü dokümantasyonu** tutar.
Uzun soluklu bir iştir; senaryo, çekim planları, bölüm metinleri, anlatım notları vb. buraya eklenir.

> **Sabit yönerge:** Kılavuz/video çekme işiyle ilgili **tüm dokümantasyon `docs/kılavuz/` altında** toplanır.
> (KURALLAR-MASTER §9'a işlendi.)

## İçindekiler
- [`yenitomofil_senaryo_taslagi.md`](yenitomofil_senaryo_taslagi.md) — **Tek kaynak (v4.0):** otonom çekim senaryosu **+ sesli anlatı** birleşik. Her alt-bölümde adımlar + 🎙️ beat (B01–B15) yan yana; edge-tts `tr-TR-AhmetNeural`, ses süresi ekran süresini sürer. **Önce mutabakat, sonra kodlama.** (Eski ayrı `yenitomofil_anlati_metni.md` buraya birleştirildi.)

## İlgili kod (referans — burada DEĞİL, kod tarafında)
Aşağıdakiler koddur ve path bağımlılıkları olduğu için yerlerinde durur; ileride kod düzenlemesi yapılırsa buraya taşıma değerlendirilebilir:
- `app/services/kilavuz_olusturucu_executor.py` — Playwright otonom çekim yürütücüsü
- `ui/templates/platform/admin/kilavuz_olusturucu.html` — admin paneli arayüzü
- `docs/compile_guide.py` — `user_guide_master.html` → PDF derleyici
- `docs/user_guide_master.html` — kılavuz PDF kaynağı (HTML)
- Üretilen çıktılar (gitignore'da): `docs/kokpitim_master_kullanim_kilavuzu.pdf`, `static/videos/kullanim_kilavuzu/`, `static/img/kullanim_kilavuzu/`

## Çalışma kuralı
1. Yeni bölüm/senaryo/metin → bu klasöre `.md` olarak eklenir.
2. Senaryo değişikliği önce burada yazılır, **mutabakat sağlanınca** koda yansıtılır.
3. Üretilen binary çıktılar (PDF/video/resim) commit edilmez (`.gitignore`).
