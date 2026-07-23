---
name: project_paketleme_segmentasyon
description: "Ürünü paketlere (tier) ayırma girişimi — segment/olgunluk modeli, demo overwhelm sorunu, strateji dosyası"
metadata: 
  node_type: memory
  type: project
  originSessionId: 0265ef0d-566e-4066-930c-3200531599d0
---

Ürün çok kapsamlı hale geldi → **paketleme/segmentasyon** girişimi başladı (2026-06-09). Strateji dosyası: **`docs/paketler/PAKETLEME-STRATEJISI.md`** (+ `docs/paketler/README.md`). Çalışma kuralı: önce burada mutabakat, sonra `subscription_packages` verisine/koda yansıt.

**Kullanıcının çekirdek gözlemi (bağlayıcı):** Demolar **full-set** (her özellik) yapıldığı için konu uzmanları "çok fazla şey var, %90'ı hakkında fikrim yok" refleksi veriyor. Teşhis: bu *özellik* değil **maruz kalma (yüzey)** sorunu — kısmen demo stratejisi sorunu.

**Kararlaşan çerçeve:**
- **Yetki (entitlement = paket) ≠ Maruz kalma (exposure = olgunluk+rol).** Overwhelm = exposure. Çözüm: kademeli açılma (progressive unlock) — her şeye lisanslı kurum bile yüzeyi L1'den başlatır.
- İki boyut: **ticari tier** (Başlangıç/Yönetim/Strateji/+Holding) × **olgunluk** (L1 başlat / L2 ölç / L3 optimize).
- Hedef segment vurgusu: olgunlaşmamış + veri personeli yok + yorum becerisi düşük kurumlar — rakiplerin kaçtığı segment; bizim **AI yorum + şablon(Tomofil) + sesli kılavuz** varlıklarımız farklılaşma. Başlangıç paketi "küçük yazılım" değil "yarı-kurulu + yorumlanmış deneyim".

**Yapısal bulgular (kod):**
- Yetki kapısı ZATEN çalışıyor: `micro/core/module_registry.py::get_accessible_modules` → paket→`package_modules`→modül→launcher. Eksik: paketleri tanımlamak (şu an tek `Master Package`). 14 launcher modülü tanımlı.
- "Normal vs İleri" ayrımı `system_modules`'te zaten var (İleri = Porter/BCG/Ansoff/VRIO/TOWS/Değer Zinciri/PESTEL). Taksonomi: 8 modül / 35 bileşen / 122 slug eşleme / 81 route. Ama K-Radar/Bireysel/OKR/BSC/ESG/`mock_*` bu 8 modülde YOK; Proje×2 ve CRM×2 placeholder (0 bileşen).

**Kritik çıkarımlar:** (1) PGV (PG verisi girişi) en yüksek veri-yükü = "veri personeli yok" segmentinin koptuğu yer → Başlangıç'ta minimuma indir. (2) K-Radar paradoksu: en ileri ama yorumu AI yapıyor → düşük-yetkinlik segmentine sadeleştirilmiş AI-görünüm olarak değer. (3) `mock_*` (~30+ deney tablosu: metaverse/DAO/doomsday/smart contract…) "%90 bilmiyorum"un büyük kısmı → kaldır ya da Lab; demoda gösterme.

**Açık kararlar (PAKETLEME-STRATEJISI.md §7):** segment ekseni, olgunluk doğrulaması, PGV stratejisi, mock_* kaderi, teslim modeli (self-servis mi danışmanlık mı), tier sayısı/isim, fiyat modeli, bileşen-içi gating enforcement doğrulaması.
