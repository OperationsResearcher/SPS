---
name: project_strangler_karari
description: Sıfırdan yazma REDDEDİLDİ; strangler ile modernizasyon kararı (2026-06-16) — büyük rewrite riski
metadata: 
  node_type: memory
  type: project
  originSessionId: 0265ef0d-566e-4066-930c-3200531599d0
---

**2026-06-16 mimari karar (bağlayıcı):** "Projeyi sıfırdan mikro-modüler SaaS olarak yeniden yaz" önerisi
**değerlendirildi ve REDDEDİLDİ.** Yerine **strangler fig (kademeli kuşatma)** seçildi: mevcut sistem çalışır
kalır, legacy yüzey (`main/`, eski `templates/`, `models/`) dalga dalga emekliye alınır, yeni özellikler
yalnızca `micro/`'ya yazılır.

**Neden sıfırdan REDDEDİLDİ:**
- Kullanıcı daha önce sıfırdan-yazma denedi, **yarıda kaldı, iptal etti** (en güçlü veri — aynı duvar tekrar gelir).
- DB-doğrulanmış gerçek: korkulan çift-model borcu **yoktu** — legacy tablolar boş/yok, veri katmanı zaten modern
  tek-kaynakta (bkz. [[project_teknik_borc_haritasi]]). Tenant izolasyonu sağlam. `micro/` zaten kısmen mikro-modüler
  (13 launcher, blueprint, paket kapısı `get_accessible_modules`).
- Big-rewrite sektörün en pahalı/en sık başarısız kararı (görünmeyen bug-bilgisi kaybı, hareketli hedef, "%90 bitti"
  tuzağı = tam kullanıcının iptal ettiği nokta).

**Kanıt:** 2026-06-16'da ~1600 satır ölü legacy kod strangler ile silindi, sistem hiç kırılmadan (HGS + Dalga
0/1/1.5/1.6/3/4). Her dalga: kendi dalı → teyit → smoke test → commit → merge. Yarıda kalsa bile kazanım kalıcı.

**Bundan sonra "sıfırdan yazalım mı" tekrar gündeme gelirse:** bu kararı + kanıtı hatırlat; strangler'ın neden
yettiğini göster. Hedef temiz mimari = mevcut `micro/` + `app/models/` çekirdeğini BÜYÜTMEK, legacy'yi ERİTMEK.
[[feedback_user_style]] (tek seferde doğru, israfa tolerans yok) ile uyumlu: rewrite israf riski yüksek.
