---
name: project-github-actions-billing-kilidi
description: "GitHub Actions CI billing kilidi yüzünden Haziran 2026'dan beri hiç çalışmıyor — \"CI geçti\" varsayma"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9cf32375-5139-48c3-a16d-da6c06b83936
---

2026-07-08 keşfi: OperationsResearcher/SPS repo'sunda GitHub Actions koşuları
"account is locked due to a billing issue" ile runner başlamadan düşüyor.
Tüm koşular 3-8 saniye sürüyor (gerçek koşu imkânsız — pip install bile dakikalar alır);
bu durum en az Haziran 2026'dan (CI #8) beri böyle — CI o zamandan beri dekoratif.

**Why:** TASK-229'da eklenen ruff + coverage gate dahil hiçbir CI kontrolü fiilen
çalışmadı. "Push'landı, CI yeşil" varsayımı yanlış olur.

**KARAR (kullanıcı, 2026-07-08):** Billing düzeltilmeyecek — kart bilgisi girmek
istemiyor. CI bilinçli olarak devre dışı kalıyor. CI'ı düzeltmeyi ÖNERME.

**How to apply:**
- CI sonucuna güvenmeden önce koşu süresine bak: <10sn = çalışmamış demektir.
- Kilit kalkana kadar doğrulama YERELDE: her commit öncesi
  `ruff check .` + tam pytest (baseline: 19 failed yerel-ortam sorunu, gerisi geçmeli).
- Kullanıcı billing'i düzeltince ilk push'ta CI'ın gerçekten koştuğunu
  (süre dakikalar mertebesinde) teyit et; coverage gate %25 Ubuntu'da ilk kez
  ölçülecek — %25 altında kalırsa eşiği ölçülen değere indir.
İlgili: [[project-test-ortami-kurulum]]
