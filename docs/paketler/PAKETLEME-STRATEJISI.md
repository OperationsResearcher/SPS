# Kokpitim — Paketleme & Segmentasyon Stratejisi (Taslak v0.1)

> **Durum:** İlk-geçiş taslağı, tartışma ve düzeltme için. Mutabakat sonrası `subscription_packages`/`package_modules` verisine + (gerekirse) gating koduna yansıtılır.
> **Son güncelleme:** 2026-06-09

---

## 0. Problem

Ürün çok kapsamlı hale geldi (SP, Süreç/PG, Bireysel, Proje, Analiz, K-Radar, K-Rapor + ileri analiz katmanları + `mock_*` deney modülleri). Demolarda tekrarlayan refleks:

> *"Çok fazla şey var, bu derinlikte ihtiyaç var mı? Bu ekranların %90'ı hakkında fikrim bile yok."*

**Teşhis:** Bu bir *özellik* sorunu değil, **yüzey alanı (maruz kalma) sorunu** — ve kısmen **full-set demo** stratejisinin sonucu. Çözüm iki katmanlı: (a) ürün yüzeyini olgunluğa göre yönet, (b) demoyu persona/yolculuk üzerinden kur.

**Hedef segment vurgusu (kullanıcı):** Giriş-seviye = yönetim sistemi oturmamış + veri girecek personeli yok + yorumlama becerisi düşük kurumlar. Bu segment, çoğu rakibin **kaçındığı** (insan maliyeti yüksek) segment; bizim **AI yorum + hazır şablon + sesli kılavuz** varlıklarımız burada farklılaşma sağlayabilir.

---

## 1. Temel ayrım: Yetki (entitlement) ≠ Maruz kalma (exposure)

| Kavram | Ne belirler | Neye bağlı |
|---|---|---|
| **Yetki / lisans** | Kuruma *neyi açtın* | Ticari paket (tier) |
| **Maruz kalma / yüzey** | Kullanıcı *neyi görüyor, ne zaman* | Olgunluk + rol (kademeli açılma) |

"%90 bilmiyorum" refleksi tamamen **maruz kalma** kutusundan. Bir kurum her şeye lisanslı olsa bile yüzeyi olgunluğuna uygun başlamalı; gerisi "daha fazlası" kapısının ardında, hazır oldukça açılır (**progressive unlock**).

---

## 2. Önerilen model: iki boyut

- **Ticari tier** (Başlangıç / Yönetim / Strateji / +Holding) → *entitlement*.
- **Olgunluk seviyesi** (L1 başlat → L2 ölç → L3 optimize) → *exposure*.

Olgunluk, tier'dan **bağımsız** ilerleyebilmeli (küçük ama olgun firma da var). Kurum tier satın alır; yüzeyi olgunlukla kademeli açar.

### 2.1 Yapısal bulgular (mevcut kod — işi kolaylaştırıyor)
1. **Yetki kapısı ZATEN çalışıyor:** `micro/core/module_registry.py::get_accessible_modules` → paket → `package_modules` → modül → launcher kartı. Eksik olan sadece **paketleri tanımlamak** (şu an tek `Master Package`, her şey açık).
2. **"Normal vs İleri" ayrımı zaten var** (`system_modules`): İleri katman = Porter/BCG/Ansoff/VRIO/TOWS/Değer Zinciri/PESTEL. Paket sınırı için hazır fay hattı.
3. **Açık soru:** Bileşen-içi (kart düzeyi) gating gerçekten zorlanıyor mu, yoksa yalnız katalog mu? (`module_component_slugs` 122 satır var; enforcement doğrulanacak.)

---

## 3. Paket önerisi (3 + 1)

| Paket | Olgunluk | Vaat | Çekirdek içerik | Varsayılan GİZLİ |
|---|---|---|---|---|
| **Başlangıç** ("Pusula"?) | L1 | *Başlat ve gör* | Kurum+kullanıcı, **basitleştirilmiş süreç + az sayıda kritik PG (şablon/Tomofil-benchmark ile hazır)**, basit dashboard, **AI rapor yorumu**, sesli onboarding. SP yalnız vizyon/misyon + tek seviye hedef. | Tüm ileri analiz, K-Radar (tam), OKR/BSC/ESG, proje portföy, strateji analiz araçları |
| **Yönetim** ("Kokpit"?) | L2 | *Yönet ve ölç* | Tam SP ağacı (ana/alt strateji, SWOT/TOWS), tam Süreç/PG, Bireysel performans, Proje (temel), Plan yılları, K-Radar temel kartları, K-Rapor | İleri strateji analizi (Porter/PESTEL/VRIO/BCG/Ansoff/Blue Ocean), gelişmiş K-Radar/AI koçluk, EVM/kapasite |
| **Strateji** ("Radar"?) | L3 | *Optimize et ve öngör* | Her şey: K-Radar tam (anomali, Sankey, K-Vektör, AI koçluk), ileri strateji analizleri, OKR/BSC/ESG, proje portföy (Gantt/RAID/EVM) | — |
| **Holding/Kurumsal** (eklenti) | — | *Konsolide et* | Çok-kurum/bayi-holding kırılımı, gelişmiş yetki, API/entegrasyon | — |

**Başlangıç paketi "küçük yazılım" DEĞİL, "yarı-kurulu + yorumlanmış deneyim".** Farkımız burada.

---

## 4. İlk-geçiş sınıflandırma haritası

Eksenler → **Kim:** Yön=Yönetici, ÜY=Üst Yönetim, Kul=Kullanıcı · **Olgunluk:** L1 Gün-1 / L2 ölçen / L3 ileri · **Yük:** veri-giriş yükü · **Yorum:** anlama zorluğu

| # | Alan / ekran | Kim | Olgunluk | Yük | Yorum | Tier | Gün-1? |
|---|---|---|---|---|---|---|---|
| **ÇEKİRDEK OMURGA** |
| 1 | Masaüstüm (kişisel özet) | Kul | L1 | Düşük | Kolay | Hepsi | ✅ |
| 2 | Kurum Paneli (kimlik/ayarlar) | Yön | L1 | Düşük | Kolay | Hepsi | ✅ |
| 3 | Ayarlar + Bildirim | Hepsi | L1 | Düşük | Kolay | Hepsi | ✅ |
| 4 | Yönetim Paneli (kullanıcı/kurum) | Yön | L1 | Düşük | Kolay | Hepsi | ✅ |
| **STRATEJİK PLANLAMA** |
| 5 | Vizyon/Misyon/Amaç/Değer/Etik/Kalite kartları | ÜY | L1 | Düşük | Kolay | Başlangıç+ | ✅ |
| 6 | Ana/Alt strateji ağacı | ÜY | L2 | Orta | Orta | Yönetim+ | ⛔ |
| 7 | SWOT | ÜY/Yön | L2 | Orta | Orta | Yönetim+ | ⛔ |
| 8 | TOWS/PESTEL/Porter/BCG/Ansoff/Değer Zinciri/VRIO/Blue Ocean | ÜY/uzman | L3 | Yüksek | **Uzman(AI)** | Strateji | ⛔ |
| 9 | Stratejik Asistan (AI) | Hepsi | L1 | Düşük | Kolay | Başlangıç+ | ✅ |
| **SÜREÇ YÖNETİMİ** |
| 10 | Süreç tanımı + karne | Yön/Kul | L2 | Orta | Orta | Yönetim+ | ⛔ |
| 11 | PG (gösterge) tanımı | Yön | L2 | **Yüksek** | Orta | Yönetim+ | ⛔ |
| 12 | PG Verisi girişi (PGV) | Kul | L2 | **EN YÜKSEK** | Kolay | Yönetim+ | ⛔ |
| 13 | Olgunluk / verimlilik / trend / başarı puanı | ÜY | L3 | Düşük* | Uzman | Strateji | ⛔ |
| **DİĞER ÇALIŞMA MODÜLLERİ** |
| 14 | Bireysel Performans (karne/PG) | Kul | L2 | Orta-Yük. | Orta | Yönetim+ | ⛔ |
| 15 | Proje — temel görev/Kanban | Kul/Yön | L2 | Orta | Kolay | Yönetim+ | ⛔ |
| 16 | Proje — Gantt/RAID/EVM/kapasite/portföy | Yön/uzman | L3 | Yüksek | Uzman | Strateji | ⛔ |
| **ANALİTİK & RAPOR** |
| 17 | Performans Analitiği (trend, sağlık skoru) | ÜY/Yön | L2-L3 | Düşük* | Orta-Uzman | Yönetim+ | ⛔ |
| 18 | K-Rapor (raporlama merkezi) | Yön/ÜY | L2 | Düşük | Orta | Yönetim+ | ⛔ |
| 19 | **K-Radar** (KS/KP/KPR/Cross, anomali, Sankey, K-Vektör, AI koçluk) | ÜY/uzman | L3 | Düşük* | **Uzman→AI yapar** | Strateji | ⛔ |
| 20 | OKR / BSC / ESG | ÜY | L3 | Orta-Yük. | Uzman | Strateji | ⛔ |
| **LAB / KESİLECEK** |
| 21 | `mock_*` (metaverse, DAO, doomsday, smart contract, gemba, persona… ~30+ tablo) | — | — | — | — | **Hiçbiri** | ⛔ (kaldır/Lab) |
| 22 | Placeholder system_modules (Proje×2, CRM/Müşteri×2 — 0 bileşen) | — | — | — | — | Henüz ürün değil | — |

\* "Düşük\*" = veri otomatik türetilir (kullanıcı girmez); ama **yorumu** zordur. Satır 13/17/19 tam olarak düşük-yetkinlik segmentinin ihtiyacı: veri girmeden, AI yorumuyla değer.

---

## 5. Üç kritik çıkarım

1. **PGV (satır 12) en kritik darboğaz.** En yüksek veri-giriş yükü; "veri girecek personeli yok" segmenti tam buradan kopuyor. Başlangıç paketinin kalbi: PGV'yi minimuma indir (az kritik gösterge + şablon/benchmark varsayılan).
2. **K-Radar paradoksu & fırsatı.** En "ileri" katman ama **yorumu AI yapan** katman. Düşük-yetkinlik segmentine *sadeleştirilmiş AI-yorum görünümü* olarak verilirse, rakiplerin kaçtığı segmentte farklılaşma.
3. **Demoda satır 8 ve 21'i gösterme.** "%90 bilmiyorum" refleksinin büyük kısmı ileri analizler (8) + `mock_*` lab (21). Sahnede olmamalı.

---

## 6. Rakip refleksi (özet)

- **Good-Better-Best (3 tier) + Enterprise** standart. Land-and-expand / PLG: tek takım-tek hedefle başlat, full platform gösterme (Quantive/Gtmhub, Workboard, Perdoo, Profit.co).
- Strateji-yürütme (Cascade, ClearPoint, Spider Impact, AchieveIt): ürünü **olgunluk yolculuğu** olarak satar; şablon galerisi + müşteri başarı ekibiyle boş-ekran panigini öldürür.
- Süreç/QMS (TR: QDMS, Bizagi, ELMA): modül-bazlı + kurulum/danışmanlık (insan dokunuşlu).
- Anti-pattern = "feature-catalog demo" (bizim yaşadığımız). Best practice: özelliği değil **sonucu/yolculuğu** sat.

---

## 7. Açık kararlar (mutabakat bekliyor)

- [ ] **Segmentasyon ekseni:** birincil = olgunluk mu, firma büyüklüğü mü? (öneri: olgunluk + rol → exposure; büyüklük ikincil)
- [ ] **Olgunluk kolonu doğrulaması:** L1/L2/L3 ve "Gün-1?" işaretleri sektör gözüyle doğru mu?
- [ ] **PGV stratejisi (Başlangıç):** gösterge sayısını sınırla mı, yoksa "tam şablon, kullanıcı hiç PG tanımlamaz" mı?
- [ ] **`mock_*` katmanı:** tamamen kaldır mı, "Lab/İnovasyon" olarak üst pakette gizli mi?
- [ ] **Teslim modeli (Başlangıç):** tam self-servis mi, insan dokunuşu (kurulum/danışmanlık) kabul mü?
- [ ] **Kaç tier + isimler:** 3 mü 4 mü; Başlangıç/Yönetim/Strateji/Holding isimleri kesin mi?
- [ ] **Fiyat modeli:** kullanıcı başı / modül başı / sabit?
- [ ] **Bileşen-içi gating:** kart düzeyi enforcement var mı (kod doğrulaması)?

---

## 8. Sonraki adımlar (mutabakat sonrası)
1. Tier'ları + modül eşlemesini kesinleştir → `subscription_packages` + `package_modules` seed.
2. Olgunluk/exposure katmanını tasarla (kademeli açılma mekaniği).
3. `mock_*` ayıklama kararını uygula.
4. Persona-bazlı demo akışı (full-set yerine).
