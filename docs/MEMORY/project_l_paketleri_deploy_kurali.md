---
name: project_l_paketleri_deploy_kurali
description: "L paketleri (L1, L2, ...) tümü bitmeden canlı Yayın VM'e deploy YOK; iş yerelde birikir"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3a8493cf-9065-4a0e-a046-8aaec833dd90
---

Kullanıcı kararı (2026-06-19, bağlayıcı): **Tüm L paketleri (L1, L2, … tamamı) bitmeden Yayın'a (canlı VM, www.kokpitim.com) ASLA çıkılmaz.** L paketleri kademeli inşa ediliyor; her L paketi bitince Yayın'a gitmez — hepsi tamamlanana kadar iş yerelde (ve gerekirse Test'te) birikir.

**Why:** Ürün L1→L2→L3 olgunluk katmanları olarak paketleniyor ([[project_paketleme_segmentasyon]]). Yarım bir L-seti canlıya çıkarsa müşteri eksik/tutarsız paket görür. Yayın = kırmızı çizgi (kullanıcı verisi); tam set hazır olmadan risk alınmaz.

**How to apply:** L paketi (L1 dalları gibi) bitince **"yayına çıkalım mı"** diye SORMA, deploy ÖNERME. Sadece bir sonraki L paketine/dala geç. Push bile yalnızca kullanıcı açıkça "push'la" derse. L1 bitti (Dal 3-6 main'de + paketleme belgesi [[project_sp_yillik_plan]] bağlamında); şimdi L2 (PGV panelleri). Deploy protokolü kuralları ([[project_uc_ortam]], KURALLAR §8) hâlâ geçerli ama tetik "tüm L'ler bitti" koşuluna bağlı.
