---
name: project-uc-ortam
description: "Kokpitim'de üç-ortam mimarisi; \"VM/üretim VM\" terim YASAK"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7e3b87f3-74ac-46ae-ac39-25ec42733a89
---

Kokpitim'de **üç ortam** vardır ve isimleri bağlayıcıdır:

| # | İsim | URL | Lokasyon |
|---|---|---|---|
| 1 | **Yerel** | `http://127.0.0.1:5001` | Geliştirici (Windows) |
| 2 | **Test** | `https://test.kokpitim.com` | Oracle VM `/opt/kokpitim-test/` port 5050 DB `kokpitim_test_db` |
| 3 | **Yayın** | `https://www.kokpitim.com` | Oracle VM `/opt/kokpitim/` port 5000 DB `kokpitim_db` |

Test ve Yayın aynı Oracle VM'de (129.159.30.175), izolasyon dizin/port/DB seviyesinde.

**Why:** Kullanıcı "VM"/"üretim VM"/"production VM" gibi belirsiz terim kullanılınca hangi ortamdan bahsedildiği belli olmuyor; karışıklığı 2026-05-26'da fark etti ve "kesinlikle ekle" diyerek kuralı dayattı.

**How to apply:** Sohbette her zaman **Yerel / Test / Yayın** üçlüsünü kullan. "VM" tek başına yetmiyor — "test VM" / "yayın VM" gibi belirt.

İlgili dosyalar: [[project-test-ortami-kurulum]] (test ortamı kurulum detayları)

Bkz. `docs/KURALLAR-MASTER.md` §8 (tek gerçek kaynak).
