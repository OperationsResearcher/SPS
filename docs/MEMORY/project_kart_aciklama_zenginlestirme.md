---
name: project_kart_aciklama_zenginlestirme
description: "Kart açıklamalarını zenginleştirme işi — 2026-07-20'de K-Radar 97/97 bitti, 405 kart kaldı; devam notu docs/kontrol/KART-ACIKLAMA-DEVIR.md"
metadata: 
  node_type: memory
  type: project
  originSessionId: e77dc667-1e9b-4352-b2d9-78dfb468d0ba
  modified: 2026-07-20T09:06:29.747Z
---

Kullanıcı kart açıklamalarının "çok sığ" olduğunu söyledi (501 kart, ortalama 87
karakter, 65'i `"X — rapor kartı."` gibi sıfır bilgi şablon dolgu). Literatür
dayanaklı, doyurucu açıklamalar isteniyor.

**2026-07-20'de durduruldu** (başka işlere geçildi). Sonra dilimler devam etti.

**"Kart işine devam" denildiğinde ÖNCE ŞUNU OKU:**
`docs/kontrol/KART-ACIKLAMA-DEVIR.md` — ama ilerleme tablosu geride kalabilir;
güncel sayı için `git log --oneline --grep=kart` + seed dosyalarına bak.

**Durum (2026-07-23 güncelleme):** git'te **441/501** tamam
(`masaustu+karneler+analiz+YO`, `admin`, `sp`, `raporlar`, K-Radar). Kalan ~60;
`scripts/seed_data/card_descriptions_proje_ayarlar.py` yerelde untracked görüldü.
Dal örneği: `claude/kart-aciklama-raporlar`. DEVİR notundaki "191/501" eskimiş.

**Kurulmuş altyapı (yeniden yapma):** `system_cards.description` Text'e çevrildi
(migration `391945351814`); `base.html::renderInfoBody` modalı yapılandırılmış
basıyor; `scripts/seed_card_descriptions.py` idempotent seed (KONTROL modu
varsayılan), içerik `scripts/seed_data/card_descriptions_*.py`.

**Bağlayıcı kullanıcı kararı — ŞEFFAFLIK:** Gösterge adıyla gerçekte ölçülen şey
ayrışıyorsa açıklamada `Sınır:` bölümünde açıkça yazılır. Kullanıcı bunu seçti.

**SWOT tuzağı:** "Albert Humphrey / SRI" atfı 2023 tarihli akademik araştırmayla
çürütülmüş — KULLANMA. Güvenli: "1960'larda SRI'da SOFT olarak geliştirildi".

**Bu iş 405 kartlık içerik üretiminden fazlasını doğurdu:** kod okurken gerçek
hatalar bulundu → [[project_kart_veri_tutarsizliklari]].
