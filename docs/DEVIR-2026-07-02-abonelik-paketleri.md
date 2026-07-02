# DEVİR BELGESİ — Abonelik Paketleri (2026-07-02)

> Yeni sohbete devir için. Bir önceki oturumda konu **i18n/kart görsel standardı** ve
> birkaç bug fix'ti (bu belgeyle karıştırılmasın) — abonelik paketleme işine kaldığı
> yerden devam etmek için gereken TÜM bağlam burada toplandı.
> **Bağlayıcı kurallar:** CLAUDE.md + docs/KURALLAR-MASTER.md. Yerel→Test→Yayın.
> **Tüm L paketleri bitmeden Yayın'a ÇIKMA YOK** (memory: project_l_paketleri_deploy_kurali).

---

## 1. NEREDEYİZ — Tek cümle

Abonelik paketleme (Başlangıç/Yönetim/Strateji + Master) **tasarım + L1/L2/L3 inşası
tamamlanmış durumda, ama iki paralel/tamamlanmamış iş var**: (a) `main`'deki çalışan
gating sistemi (modül/sidebar/route düzeyi — üretimde çalışıyor gibi görünüyor), (b)
`claude/kart-katmani` dalı (henüz merge edilmemiş, kart+veri düzeyinde ince gating
ekliyor). **Bu ikisinin ilişkisi netleştirilmeden devam edilmemeli.**

## 2. ÖNCELİKLE OKUNMASI GEREKEN BELGELER (sırayla)

1. **`docs/paketler/PAKETLEME-STRATEJISI.md`** — ana strateji belgesi. §3 paket tanımları,
   §4.A/B/C L1/L2/L3 inşa kayıtları, **§7 açık kararlar (mutabakat bekliyor) — en kritik
   bölüm, oradan başla.**
2. **`docs/DEVIR-2026-06-21-paket-hiyerarsi.md`** — bir önceki oturumun devir notu.
   4-katman mimari (Paket→Modül→Bileşen→Kart→Veri), `claude/kart-katmani` dalının durumu,
   test ortamı (tom1/tom2/tom3), sıradaki adımlar (a/b/c seçenekleri, kullanıcıya
   soruldu ama seçilmedi — hâlâ açık olabilir).
3. **`docs/paketler/KART-KATMANI-TASARIM.md`** — kart+veri gating tasarımı (mutabakat).
4. **`docs/paketler/BILESEN-GORUNURLUK-KALIBI.md`** — `component_visible()` kalıbı.
5. **`docs/paketler/KART-SISTEMI-MIMARI.md`**, **`KART-STANDART-ILERLEME.md`** — bunlar
   **BAŞKA bir iştir** (aşağıda §4'te açıklandı), paketlemeyle karıştırma.

## 3. ŞU ANKİ DB DURUMU (bugün 2026-07-02 teyit edildi)

```
subscription_packages: master_package, baslangic (Başlangıç), yonetim (Yönetim), strateji (Strateji)
tenant→package dağılımı: package_id=1 → 7 tenant, package_id=2/3/4 → 1'er tenant
```
Yani **"tüm tenant'lar Master'da" durumu artık TAM doğru değil** — en az 3 tenant farklı
paketlere atanmış görünüyor (id=2,3,4). Bunun tom1/tom2/tom3 test tenant'ları mı yoksa
gerçek atamalar mı olduğunu **yeni oturum DB'den teyit etmeli** (id'leri sorgula, isimlere
bak) — varsayımla ilerleme.

## 4. KRİTİK UYARI — İKİ AYRI "KART" İŞİYLE KARIŞTIRMA

Bu oturumdan (2026-07-02, bugün) önceki konuşmada, **paketlemeyle ilgisiz** başka bir iş
yapıldı: **UI kart görsel standardı** — her sayfadaki kartlara `data-card-code` +
`mc-card-title` ekleyip, (i) bilgi butonu ve admin-only short_id rozeti göstermek
(bkz. `docs/paketler/KART-KATMANI-TASARIM.md` §Kart Görsel Standardı, ve
`docs/KURALLAR-MASTER.md` §5.1). Bu iş kapsamında:

- **`system_pages`** tablosu (main'de, `app/models/saas.py`'de tanımlı) **165 kayda** çıkarıldı
- **`system_cards`** tablosu **699 kayda** çıkarıldı (i18n çevirili açıklamalarla)
- Bu, **paket-gating için değil** — yalnızca (i) butonu + admin rozeti için.

**ÇAKIŞMA RİSKİ:** `claude/kart-katmani` dalına bakıldığında, o daldaki `app/models/saas.py`
**`SystemPage` modelini hiç içermiyor** (main'de var, o dalda yok — dallar ıraksamış).
O dal `SystemCard`'ı **paket/bileşen gating** amacıyla kullanıyor (`CardDataSource` ile
birlikte, "kartın bu veri parçası hangi pakette görünür" mantığı). Main'deki
`system_cards` ise şu an **yalnızca görsel/i18n** amaçlı, `component_id` alanı hemen
hemen tüm yeni kayıtlarda `NULL` bırakıldı (gating'e bağlanmadı).

**Yeni oturum ilk iş olarak şunu netleştirmeli:**
- `claude/kart-katmani` dalını merge etmeden önce, o daldaki `SystemCard` şeması ile
  main'deki (i18n işinden sonraki) `SystemCard` şemasını satır satır karşılaştır
  (`git diff main claude/kart-katmani -- app/models/saas.py`).
  Muhtemelen migration çakışması + veri kaybı riski var (699 main kaydı, dalda yok).
- Kullanıcıya sor: iki amacı (görsel-standart + paket-gating) **aynı tabloda birleştirmek**
  mi istiyor, yoksa ayrıştırmak mı (örn. `component_id` alanını gating için doldurmak,
  görsel-standart kayıtlarını olduğu gibi bırakmak)?

## 5. AÇIK KARARLAR (PAKETLEME-STRATEJISI.md §7'den, hâlâ güncel olabilir — teyit et)

- [ ] Segmentasyon ekseni: olgunluk mu, firma büyüklüğü mü birincil?
- [ ] PGV stratejisi (Başlangıç paketi): gösterge sayısı sınırlı mı, yoksa şablon zorunlu mu?
- [ ] `mock_*` tabloları (~30+, metaverse/DAO/doomsday vb. deney modülleri): tamamen kaldır
      mı, "Lab" olarak üst pakette gizli mi bırak?
- [ ] Teslim modeli (Başlangıç): tam self-servis mi, insan dokunuşlu (danışmanlık) mı?
- [ ] Fiyat modeli: kullanıcı başı / modül başı / sabit?
- [ ] **Tenant→tier gerçek dağıtımı:** §3'te bahsedildiği gibi hepsi Master'dı ama §3'te
      gördüğüm DB sorgusu artık 3 tenant'ın farklı pakette olduğunu gösteriyor — bu
      değişikliğin nasıl/ne zaman yapıldığını (script mi, elle mi) TASKLOG'dan doğrula.

Zaten kapanmış kararlar (§7'de işaretli, tekrar açma):
- [x] Kaç tier + isimler: baslangic/yonetim/strateji + Master eklenti — kapalı.
- [x] Bileşen-içi gating var mı: YOK, yalnızca modül/launcher düzeyinde — kapalı (ama
      `claude/kart-katmani` dalı bunu **değiştirmeye** çalışıyor, §4'e bak).

## 6. SIRADAKİ ADIMLAR (önceki devir notundan, muhtemelen hâlâ geçerli)

`docs/DEVIR-2026-06-21-paket-hiyerarsi.md`'de kullanıcıya sorulmuş ama seçilmemiş 3 seçenek:
- **(a)** Eksik modüllerin (k_radar/bireysel/proje/analiz/k_rapor) bileşenlerini tanımla.
- **(b)** Daha çok kartı `data-card-*` ile işaretle → keşfet (kademeli kapsam).
  **NOT:** (b) kısmen bugünkü i18n oturumunda YAPILDI ama gating amacıyla değil — bu
  yüzden §4'teki çakışma riskini önce çöz.
- **(c)** `claude/kart-katmani` dalını main'e merge et.

Yeni oturum muhtemelen önce bu üçünü kullanıcıyla teyit etmeli — "hâlâ bunlardan biri mi,
yoksa öncelik değişti mi" diye sormak doğru olur, varsayılmamalı.

## 7. TEST ORTAMI (önceki devirden, doğrulanmadı — kontrol et)

tom1/tom2/tom3 tenant'ları (Tomofil'den kademeli klon, baslangic/yonetim/strateji
paketleriyle) kurulmuş olabilir. Ortak şifre `Test1234!` deniyordu. **Bu oturumda
doğrulanmadı** — hâlâ var mı, DB'de tenant adı/id ile kontrol et.

## 8. ÇALIŞMA TARZI (bağlayıcı, tekrar hatırlatma)

- Ajan/keşif raporlarına güvenme → DB query / runtime test ile teyit et.
- Tek seferde doğru çözüm; deneme-yanılma yasak; dosyayı okumadan kod yazma.
- main'e doğrudan commit yok; her iş kendi dalında → kullanıcı onayıyla merge.
- Push/deploy yalnızca kullanıcı "yayına çıkalım" dediğinde.
- **Tüm L paketleri bitmeden Yayın'a çıkma yok** (bu kural hâlâ bağlayıcı).
