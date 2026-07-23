---
name: feedback-token-diyeti
description: "BAĞLAYICI 2026-07-24: Pro paket batmasın. Deploy/git script; kısa bağlam; deneme-yanılma yok; pahalı Agent işini sohbete taşıma."
metadata:
  node_type: memory
  type: feedback
  modified: 2026-07-24T02:20:00.000Z
---

Kullanıcı Pro paketi aldı; ~4 saatte included kredinin büyük kısmı yandı.
Risk: **batmak** (paket bir günde erir). Token israfı = para israfı.

**How to apply — BAĞLAYICI:**

1. **Orchestrator önce:** Yayın/Test → `yayina_ver.ps1`; commit/push → `commit_push.ps1`.
   Sohbette SSH/SCP/dump adım adım YASAK (script FALLBACK basmadıkça).
2. **Küçük iş = kısa yol:** Tek dosya / soru → Ask veya tek tur; tüm repoyu Agent’a açma.
3. **Bağlam diyeti:** `@` ile az dosya; uzun transcript / tüm MEMORY dump etme.
   Yeni büyük iş → **yeni sohbet**.
4. **Tek seferde doğru:** Kök neden → uygula. Aynı hatayı 3+ kez deneme;
   2. başarısızlıktan sonra FALLBACK / kullanıcıya net durum.
5. **Keşif sınırlı:** Explore/subagent yalnız gerektiğinde; “her şeyi tara” yok.
6. **Yazmadan önce:** Yönlendirme + onay (mevcut kural). Onaysız büyük refactor yok.
7. **Cevap kısa:** Kullanıcıya roman yazma; özet + gerekli komut/kanıt.
8. **Model:** Kullanıcı tercih etmedikçe gereksiz yere en pahalı modeli zorlama.

Detay: `docs/KURALLAR-MASTER.md` §1.1 · Cursor `token-diyeti.mdc`.
Related: [[feedback_trust_and_cost]], [[feedback_user_style]],
[[feedback_deploy_4_katman_ve_test_demo_sifirla]], [[feedback_git_commit_push_orchestrator]].
