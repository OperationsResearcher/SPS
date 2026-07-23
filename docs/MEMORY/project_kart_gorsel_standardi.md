---
name: project_kart_gorsel_standardi
description: "Her kartın zorunlu görsel yapısı — ikon+başlık+(i) solda, kısa ID sağ üstte (admin)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 91906003-7dd8-45ad-a61f-27ad19461258
---

KART GÖRSEL STANDARDI (2026-06-21, kullanıcı mutabakatı, BAĞLAYICI). Yeni veya
değiştirilen HER kart bu yapıda olmalı:

Başlık satırı: **[mini FontAwesome ikon] Kart Başlığı (i)** solda → HERKESE görünür.
Sağ üst köşede **kısa Kart ID (short_id, 2 harf + numara, örn. MA01)** → yalnız
`role.name == 'Admin'`, salt gösterim (tıklanamaz, kopyalama YOK — kullanıcı
"tıkla kopyala" davranışını açıkça reddetti).

Mekanizma MERKEZÎ: `ui/templates/platform/base.html` (admin/route değil, base'de).
Kartı standarda sokmak: konteynere `data-card-code="<sayfa>.<kart>"` ekle + başlık
`mc-card-title`/`mc-stat-label` taşısın + sol mini ikon koy → admin'den keşfet
(`system_cards`'a yazılır) → `short_id` + `description` ata. (i) butonu description'ı
modalde gösterir.

short_id sayfa-harf öneki: MA=masaustu, SP=sp, PR=process(süreç), KU=kurum,
BR=bireysel, PJ=project(proje), KR=k-rapor, KD=k-radar, RP=raporlar.

**Why:** Kullanıcı kartlarda sorun bildirirken "şu kartta şu var" diyebilmek için
kısa görünür ID istedi; (i) ile her kullanıcı kartın amacını öğrenebilsin istedi.

**How to apply:** Tam yordam `docs/paketler/KART-KATMANI-TASARIM.md` §Kart Görsel
Standardı + `docs/KURALLAR-MASTER.md` §5.1. KRİTİK TUZAK: base.html/route değişince
`python pybasla.py` ile YENİDEN BAŞLAT — bu makinede Flask auto-reload güvenilmez,
yoksa eski JS servis edilir (5 prompt boşa gitti bu yüzden). Ayrıca toplu meta
endpoint'i GET olmalı; POST CSRF'e takılır. [[project_yerel_stale_surec_5001]]
[[project_kart_kimlik_csv]]
