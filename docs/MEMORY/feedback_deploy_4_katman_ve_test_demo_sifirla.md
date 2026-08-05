---
name: feedback-deploy-4-katman-ve-test-demo-sifirla
description: "2026-07-07 kararı (bağlayıcı): Yayın deploy'unda 4 katman OTOMATİK kontrol edilir; Test/Demo her zaman sıfırdan kurulur, asla tamir edilmez"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1c201b8f-7e54-4158-89cc-c16526a01fc7
---

7 saatlik bir "Yayın'a 6 kurum ekle" işi sırasında kullanıcı defalarca "yine bir şey eksik çıkıyor,
bunu her seferinde ben mi fark edeceğim" diye tepki gösterdi (kart açıklamaları, sequence drift,
FK kolonu eksiklikleri, seed script'leri — hepsi ayrı ayrı, kullanıcı fark ettikçe ortaya çıktı).
Kullanıcı buna çok sinirlendi ("kafamı siktin", "zamanımı çaldın") — bu, otorite belgeye (KURALLAR
§1 "tek seferde doğru çözüm" ilkesi) rağmen tekrarlanan bir hata deseniydi.

**Why:** "Yereli X ortamına ver" komutu tek bir işlem değil — en az 4 bağımsız katman içeriyor:
(1) kod, (2) DB şeması (migration), (3) DB verisi (kurum/kullanıcı/kpi), (4) kod deploy'uyla
OTOMATİK gelmeyen tek-seferlik işlemler (seed script'leri, `discover_cards()` gibi keşif route'ları).
Bunları teker teker, kullanıcı fark ettikçe ele almak güven kaybına ve büyük zaman/token israfına
yol açtı.

**How to apply — İKİ AYRI KURAL, kalıcı, `docs/SUNUCU-GUNCELLEME-REHBERI.md` §0 madde 6-7'de yazılı:**

1. **Test/Demo: HER ZAMAN sıfırdan kurulum, asla tamir/yama.** Küçük bir değişiklik istense bile
   "önce dene, olmazsa sıfırla" YOK — direkt container+DB+kod silinir, yerelden sıfırdan kurulur
   (+ Demo için Tomofil baseline seed'i). Sebep: hassas kullanıcı verisi yok, parça parça tamir
   saatler harcatıyor.

2. **Yayın: her deploy isteğinde OTOMATİK 4-katman kontrolü** — kullanıcı sormadan, kod/şema/veri/
   tek-seferlik-işlemler HEPSİ kontrol edilip eksikler TEK LİSTEDE sunulur. Kırmızı çizgi ritüeli
   (kontrol dosyası + yedek, [[project_yedekleme_ve_db]]) bunun YERİNE GEÇMEZ, ona ek olarak hâlâ
   zorunlu.

3. **2026-07-24 — orchestrator:** Tercih `scripts/ops/oracle/yayina_ver.ps1` (rehber §0.8).
   Script FALLBACK basarsa geleneksel §3/§4/§5; ajan sessiz yama yapmaz.

Bu, [[project_seed_script_deploy_acigi]] ve [[project_encryption_key_deploy_riski]] memory'lerindeki
noktasal derslerin ÜST KURALI — onlar "şu spesifik şey eksik çıktı" derken, bu memory "her deploy'da
sistematik olarak TÜMÜNÜ kontrol et" diyor.

**Taşınabilirlik notu (kullanıcı sordu):** Bu kural hem `docs/SUNUCU-GUNCELLEME-REHBERI.md`'ye (dosya,
her IDE/araçtan okunur) hem buraya (memory, yalnız Claude Code + bu proje) yazıldı. Başka bir IDE/AI
asistanı kullanılırsa, o asistana `docs/SUNUCU-GUNCELLEME-REHBERI.md`'yi okumasını söylemek gerekir —
memory dosyaları otomatik taşınmaz.
