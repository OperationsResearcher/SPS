# Kokpitim — Paketleme & Segmentasyon Stratejisi (Taslak v0.1)

> **Durum:** İlk-geçiş taslağı, tartışma ve düzeltme için. **L1 çekirdeği (KOE omurgası + Dal 3-6) inşa edildi** (§4.A); **L2 paket sistemi (gating onarımı + Başlangıç/Yönetim/Strateji tier'ları + tenant atama) inşa edildi** (§4.B). Hepsi yerelde — tüm L paketleri bitmeden Yayın'a çıkılmıyor.
> **Son güncelleme:** 2026-06-19

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

### 2.1 Yapısal bulgular (L2'de doğrulandı — bkz. §4.B)
1. ~~"Yetki kapısı ZATEN çalışıyor"~~ → **DÜZELTME (L2 Dal 1):** Yetki kapısı `get_accessible_modules` vardı ama **fiilen KAPALIYDI** — `system_modules` kodları (`*_modulu` son ekli) `module_registry` eşlemesinde tanınmıyordu → hep `None` → herkes her şeyi görüyordu. Onarıldı; paketler tanımlandı (§4.B).
2. **"Normal vs İleri" ayrımı zaten var** (`system_modules`): İleri katman = Porter/BCG/Ansoff/VRIO/TOWS/Değer Zinciri/PESTEL. Paket sınırı için hazır fay hattı.
3. **Açık soru CEVAPLANDI (L2):** Gating yalnızca **launcher/modül düzeyinde** zorlanıyor — bileşen/kart-içi (özellik düzeyi) enforcement YOK. Sonuç: PGV gibi modül-içi yetenekler tek başına gate'lenemez; paket sınırı **modül granülerliğinde** kuruldu (Süreç modülü = PGV ile birlikte L2'ye).

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
| 5 | Vizyon/Misyon/Amaç/Değer/Etik/Kalite kartları *(Değer/Etik/Kalite çok-satırlı — Dal 3)* | ÜY | L1 | Düşük | Kolay | Başlangıç+ | ✅ |
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
| 22 | Placeholder system_modules (Proje×2, ~~CRM/Müşteri×2~~) | — | — | — | — | Henüz ürün değil | — |

> **Güncelleme (2026-07-02):** CRM/Müşteri×2 (`musteri_iliskileri_yonetimi_modulu`, `ileri_iliskileri_yonetimi_modulu`) kullanıcı kararıyla **kalıcı olarak kaldırıldı** — hiçbir kod karşılığı (route/model/template/launcher) yoktu, DB'de yalnızca boş `system_modules` kaydı ve Master Package bağı olarak duruyordu (bkz. `scripts/remove_crm_placeholder_modules.py`). Proje×2 placeholder (§4 satır 21'deki `mock_*` ile karıştırılmasın — bu satır 22'deki ayrı, launcher karşılığı olmayan iskelet `system_modules` kayıtları) henüz gündemde değil.

\* "Düşük\*" = veri otomatik türetilir (kullanıcı girmez); ama **yorumu** zordur. Satır 13/17/19 tam olarak düşük-yetkinlik segmentinin ihtiyacı: veri girmeden, AI yorumuyla değer.

---

## 4.A. L1 "Başlangıç" paketi — İnşa edilen (2026-06-19)

> §3'teki "Başlangıç paketi = yarı-kurulu + yorumlanmış deneyim" vaadinin **kod tarafına yansıyan ilk somut katmanı**. KOE omurgası + 4 dal. Karar geçmişi: TASKLOG TASK-184…188. Tümü yerelde inşa+doğrulandı; Test/Yayın'a henüz çıkmadı.

### Omurga — KOE (Kurumsal Olgunluk Endeksi)
- **4 boyut, eşit %25:** Kimlik & Strateji Netliği · Süreç Mimarisi · Olgunluk · İcra Disiplini. `app/services/koe_service.py::compute_koe`.
- **PGV'siz:** yapıyı ölçer, performansı değil — "veri girecek personeli yok" segmenti için kritik (§5/1). Mevcut yapısal veriden hesaplanır, saf okuma.
- **Asimetri (bağlayıcı):** KOE'yi yalnızca **Üst Yönetim** görür (`sp_can_manage`). Standart kullanıcı görmez ama **besler** (girdiği yapı KOE'ye akar). Masaüstü kartı yönetici-only.

### Dal 3 — Kimlik çok-satırlı (Değer / Etik / Kalite)
- Tek-TEXT alanlar → çok-satırlı tablolar (`tenant_values` / `tenant_ethics_codes` / `tenant_quality_policies`). Her madde başlık+açıklama, soft-delete, tenant izolasyonlu.
- **"Temiz kesim" kararı:** yeni tablolar canonical; eski `tenants.core_values/code_of_ethics/quality_policy` TEXT kolonları DB'de **kalır ama okunmaz/yazılmaz** (geri-dönüş ağı).
- CRUD UI: Kurum Paneli'nde madde madde ekle/düzenle/sil (Üst Yönetim). KOE "Kimlik" boyutu artık satırları okur (eski TEXT'i değil). → §4 satır 5 bu dalla **çok-satırlıya** evrildi.

### Dal 4 — Bireysel hedef iki katman
- `IndividualPerformanceIndicator`'a **`katman`** (`Standart` / `Stratejik`) + opsiyonel `strategy_id` (kurum stratejisi bağı, tenant izolasyonlu).
- `katman`, mevcut `source` ekseninden **bağımsız** (source = nereden geldiği; katman = stratejik mi).
- KOE "Kimlik & Strateji" boyutuna sinyal: **stratejik hedefi olan çalışan oranı** (stratejinin bireye inmesi). → §4 satır 14'ün L1 sürümü: katman ayrımı L1'de var, tam bireysel performans L2.

### Dal 5 — Rol etiketi tek kaynak
- Kanonik rol etiketleri tek kaynakta: `app/constants/roles.py::ROLE_LABELS_TR` + `role_label_tr()` + Jinja helper. Dağınık/çelişen literal'lar elendi.
- Etiketler: Admin→Sistem Yöneticisi, tenant_admin→Kurum Yöneticisi, executive_manager→**Üst Yönetim**, standard_user→**Kurum Kullanıcısı**. Yetki mantığı (`surec/permissions.py`) değişmedi — yalnızca görünüm.

### Dal 6 — AI Yapı-Danışmanı (kalibrasyon + opsiyonel LLM)
- KOE boşluk raporundan **önceliklendirilmiş öneri + anlatı** (`yapi_danismani`). §3'teki "AI rapor yorumu" vaadinin L1 çekirdeği.
- **Kalibrasyon:** öncelik = etki × aciliyet — temel boşluklar (iskelet hiç yok) daima üstte.
- **Opsiyonel LLM:** boşluk *tespiti* heuristik kalır (deterministik); yalnızca *ifade* `llm_gateway` ile doğallaşır. Provider yok/bozuk çıktı → heuristik metne düşer. Lazy buton (yönetici-only).

### L1'in bilinçli sınırları (L2'ye ertelenen)
- PGV panelleri / performans verisi girişi → **L2** (KOE bilinçli PGV'siz).
- "L2'de açılır" etiketi **OLMAYACAK** — L2 ayrı paket, L1 yüzeyinde L2 sızıntısı yok.
- Bireysel hedefte tam performans ölçümü, süreç PG verisi, ileri analizler → L2/L3 (§4 tablosu).

---

## 4.B. L2 — Paket sistemi inşa edildi (2026-06-19)

> §3'teki tier modeli + §2.1'deki gating'in **koda yansıması**. PGV'nin paket düzeyinde gerçek sınırı. Karar geçmişi: TASKLOG TASK-189…191. Tümü yerelde inşa+doğrulandı; **deploy YOK** (tüm L paketleri bitmeden Yayın'a çıkılmaz — kullanıcı kararı).

### Dal 1 — Gating motoru onarımı
- **Bulgu:** Paket gating fiilen kapalıydı (§2.1/1 düzeltmesi). `module_registry._SYSTEM_CODE_TO_LAUNCHER_ID`'ye gerçek DB kodları (`*_modulu`) eklendi.
- Master Package eksik modüllerle (kurum/bireysel/analiz/k_radar/k_rapor) tamamlandı → gating açılınca mevcut tenant'lar modül kaybetmedi (`scripts/seed_l2_module_gating.py`).

### Dal 2 — Gerçek paketler (kümülatif tier)
| Paket (code) | Modüller (launcher) | Modül# | PGV? |
|---|---|---|---|
| **Başlangıç** (`baslangic`) | kurum, sp *(+ minimum: masaustu/ayarlar/bildirim)* | 5 | ✗ |
| **Yönetim** (`yonetim`) | + surec, bireysel, proje, analiz, k_rapor | 10 | ✓ |
| **Strateji** (`strateji`) | + k_radar *(+ ileri_* modülleri — L3 Dal 1)* | 11+3 | ✓ |
| Master Package | full (13 system_module) | — | ✓ |

- `scripts/seed_l2_paketler.py` (idempotent, sequence-drift korumalı). Runtime: her paket farklı launcher yüzeyi verdi (5/10/11).
- **`sp` Başlangıç'ta** (strateji ağacı dahil) — modül-içi ayrım olmadığı için (§2.1/3) ağaç gizlenemez; bilinçli kabul. Kimlik zaten `kurum` modülünde (Dal 3).

### Dal 3 — Tenant atama
- **Yeni tenant:** admin "Kurum Ekle" formunda paket dropdown'ı **zaten mevcuttu** (`admin_tenants_add` + `tenants.html`); runtime doğrulandı, kod yazılmadı.
- **Mevcut tenant'lar:** 7/7 **Master Package**'e (full, 13 modül) atandı (`scripts/assign_existing_tenants_to_master.py`). Kullanıcı kararı: full erişim korunsun, kimse modül kaybetmesin. "En yüksek" = en kapsamlı = Master (Strateji'nin 8'i değil).

### L2'nin durumu ve sınırları
- Paket sistemi **artık gerçekten çalışıyor**; PGV sınırı paket düzeyinde gerçek (Başlangıç PGV'siz, Yönetim PGV'li).
- **Özellik-düzeyi gating yok** (sadece modül/launcher). `sp`/`surec` gibi karma modüller bütün olarak gate'lenir. Daha ince ayrım gerekirse → ayrı altyapı (ertelendi).
- Tenant'lar şu an hepsi Master (full); gerçek tier dağılımı (kim Başlangıç, kim Yönetim) ticari karar — henüz uygulanmadı.

---

## 4.C. L3 "Strateji" paketi — keşif + ilk dal (2026-06-19)

> Keşif sonucu: **L3 motoru büyük ölçüde mevcut ve çalışıyor** (4 paralel kod keşfiyle DB-teyitli). Eksikler dağınık ve çoğu UI/yüzey düzeyinde. Karar geçmişi: TASKLOG TASK-192…

### L3 durum haritası (keşif özeti)
| Alan | Sağlam (çalışıyor) | İskelet (API/model var, UI yok) | Eksik/Kırık |
|---|---|---|---|
| **K-Radar** | KS/KP/KPR/Cross/Risk, Anomali, Sankey, AI Koçluk (LLM+fallback) | — | K-Vektör (belgede var, kodda yok) |
| **İleri strateji** | Blue Ocean, VRIO, OKR, Hoshin X-Matrix | SWOT/TOWS/PESTEL/BSC (template yok) | Porter (route yok), Ansoff/BCG/Değer Zinciri (yok) |
| **OKR/BSC/ESG** | OKR (tam, 48 kayıt) | BSC (API+840 kayıt, UI yok) | ESG (model+PDF var, **input UI yok**, 10 kayıt) |
| **Proje portföy** | Gantt, RAID, EVM, CPM, Portföy | Kapasite (DB/API var, UI yok) | Program/portföy Gantt (yok) |

### Dal 1 — ileri_* modülleri Strateji paketine bağlandı
- `ileri_stratejik_planlama` + `ileri_surec_yonetimi` + `ileri_proje_yonetimi` → Strateji paketine (`scripts/seed_l3_ileri_moduller.py`). Strateji artık 11 modül.
- `ileri_iliskileri` (CRM) eklenmedi — launcher karşılığı yok (placeholder).
- **Launcher yüzeyi değişmedi** (ileri_* → sp/surec/proje eşleşir): amaç paket *tanımının* dürüstlüğü, "Strateji ileri yetenekleri içerir" gerçeğini DB'ye yazmak.

### L3 dalları — yapılan / iptal
- **Dal 2 ✅:** SWOT/TOWS/PESTEL/BSC sayfa+template (ortak liste editörü). API'leri hazırdı, UI eklendi.
- **Dal 3 ✅:** Porter route'u bağlandı (model vardı, route yoktu — kırık onarıldı) + 1-5 skorlu editör.
- **Dal 4 ✅:** ESG metrik + değer girişi UI (`/raporlar/esg-yonetim`) — dead code onarıldı.
- **Dal 5 ❌ İPTAL (keşif çürüttü):** "Ansoff/BCG/Değer Zinciri sıfırdan + K-Vektör" varsayımı **YANLIŞTI** (DB teyidi). Gerçek: **K-Vektör tam mevcut** (`app/models/k_vektor.py` + route'lar); **Ansoff/BCG K-Radar'da** (`/k-radar/api/ks/ansoff`, `/bcg` — KS radar sayfasında); **Değer Zinciri K-Radar'da tam sayfa** (`/k-radar/kp/deger-zinciri` + `value_chain_items` tablo, 0 veri). Sıfırdan yazmak duplike/çakışma yaratırdı. Bu analizler L3'te (K-Radar/k_vektor modülleri) zaten erişilebilir. Ajan raporu yanıldı → **DB'de teyit kuralı** (memory) bir kez daha doğrulandı.

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
- [x] **Kaç tier + isimler:** ✅ L2 — 3 tier kuruldu: `baslangic` (Başlangıç) / `yonetim` (Yönetim) / `strateji` (Strateji). Holding eklenti ayrı. (§4.B)
- [ ] **Fiyat modeli:** kullanıcı başı / modül başı / sabit?
- [x] **Bileşen-içi gating:** ✅ L2 — CEVAP: kart düzeyi enforcement YOK; gating yalnızca modül/launcher düzeyinde. (§2.1/3, §4.B)
- [ ] **Tenant→tier dağılımı:** mevcut hepsi Master (full); gerçek tier ataması (kim Başlangıç/Yönetim) ticari karar — bekliyor.

---

## 8. Sonraki adımlar (mutabakat sonrası)
1. Tier'ları + modül eşlemesini kesinleştir → `subscription_packages` + `package_modules` seed.
2. Olgunluk/exposure katmanını tasarla (kademeli açılma mekaniği).
3. `mock_*` ayıklama kararını uygula.
4. Persona-bazlı demo akışı (full-set yerine).
