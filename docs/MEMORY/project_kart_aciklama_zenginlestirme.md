---
name: project_kart_aciklama_zenginlestirme
description: "Kart açıklama zenginleştirme — 501/501 BİTTİ (Yerel seed 2026-07-24). Otorite: docs/kontrol/KART-ACIKLAMA-DEVIR.md. Test/Demo/Yayın seed ayrı."
metadata: 
  node_type: memory
  type: project
  originSessionId: e77dc667-1e9b-4352-b2d9-78dfb468d0ba
  modified: 2026-07-24T00:36:00.000Z
---

Kullanıcı kart açıklamalarının "çok sığ" olduğunu söyledi (501 kart, ortalama 87
karakter, 65'i `"X — rapor kartı."` gibi sıfır bilgi şablon dolgu). Literatür
dayanaklı, doyurucu açıklamalar isteniyor.

**Durum (2026-07-24): 501/501 TAMAMLANDI (Yerel).**
Dal: `claude/kart-aciklama-bitir` (+ hesap paketi merge). Seed KONTROL: 501/501 aynı.
Katalog ort. **464 krk**, kısa/boş: 0. Son dilim: `card_descriptions_proje_ayarlar.py`
(60) → `--calistir`.

**"Kart işine devam" denildiğinde:** iş bitti — yalnızca ortam taşıma (Test/Demo/Yayın)
için `docs/kontrol/KART-ACIKLAMA-DEVIR.md` §6. İlerleme tablosu güncel.

**Kurulmuş altyapı (yeniden yapma):** `system_cards.description` Text
(migration `391945351814`); `base.html::renderInfoBody`;
`scripts/seed_card_descriptions.py` + `scripts/seed_data/card_descriptions_*.py` (9 dosya).

**Bağlayıcı — ŞEFFAFLIK:** İsim≠ölçüm ise `Sınır:` zorunlu.

**SWOT tuzağı:** "Albert Humphrey / SRI" KULLANMA. Güvenli: "1960'larda SRI'da SOFT".

**Yan ürün:** kod okurken bulunan hatalar → [[project_kart_veri_tutarsizliklari]]
(D1/D2/D3/T1/G1 hesap paketinde düzeltildi; SEM backfill / İ1 bilinçli açık).
