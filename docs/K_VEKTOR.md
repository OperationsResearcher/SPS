# K-Vektör — Spesifikasyon (taslak)

Bu belge, stratejik planlama ↔ süreç ↔ PG hiyerarşisinde **matematiksel vizyon skoru** (hedef ölçek **1000**) üreten **K-Vektör** özelliğinin ürün ve teknik kararlarını bir arada tutar. Uygulama bu belgeye göre ilerler; değişiklikler versiyon notu ile işlenir.

---

## 1. Amaç ve kapsam

- **Vizyon skoru:** Kurum **1000 puana** ulaştığında “vizyona ulaşıldı” yorumuna temel oluşturan, hiyerarşik ve ağırlıklı bir skor.
- **Geriye dönük uyumluluk:** Özellik **kapalıyken** mevcut davranış ve ekranlar **değişmez**.
- **Açıkken:** Aynı veri modeli üzerinde ek ağırlık girişleri, hesaplama motoru ve (gerektiğinde) ek UI.

---

## 2. Özellik anahtarı (tenant)

- **Aç/kapa:** Kurum ayarları (`/kurum/ayarlar`) — **K-Vektör kullanımı**.
- **Ana ve alt strateji ham ağırlıkları:** Stratejik Planlama (`/sp`) — **Strateji listesi** kartında her ana strateji / alt strateji **Düzenle** modalı; toplu düzenleme için `GET/POST /sp/api/k-vektor/weights` (API) kullanılabilir.
- **Süreç–alt strateji katkı %:** Süreç Yönetimi (`/process`) — süreç oluşturma/düzenleme modalı.
- `k_vektor_enabled = false` → K-Vektör hesapları ve süreç formundaki **% dağılımı alanları** gösterilmez; mevcut akış.
- `k_vektor_enabled = true` → Aşağıdaki kurallar devreye girer.

---

## 3. Hiyerarşi ve veri akışı (özet)

```
Vizyon (1000 hedef)
  ← Ana stratejiler (ağırlık → 1000 içinde kota)
      ← Alt stratejiler (ebeveyn kotası içinde oransal bölüşüm)
          ← Süreçler (süreç skoru; alt stratejilere % ile dağıtım)
              ← PG’ler (mevcut PG ağırlıkları ile süreç skoru)
```

- **PG:** Mevcut PG ağırlıkları ve PGV ile üretilen başarı mantığı **aynı kalır** (K-Vektör sadece üst katmanları birleştirir).
- **Eksik PG / skor yok:** İlgili dalın katkısı **0**.

---

## 4. Matematik — genel kural

Her ebeveynin altında, kullanıcı **ham ağırlıklar** \(w_i\) girebilir; girilmezse **eşit dağıtım** uygulanır.

- Alt öğelerin ham ağırlık toplamı \(S = \sum w_i\) (eşit dağıtımda \(w_i = 1\) varsayımı ile uyumlu tanım).
- **Ebeveyn kotası** \(K\) içinde \(i\). çocuğun payı:

\[
\text{pay}_i = K \cdot \frac{w_i}{S}
\]

- **En üst (vizyon):** Hedef toplam kota **\(K = 1000\)**. Ana stratejiler için kullanıcı ham değerleri girer; örnek: 50 + 150 + 50 + 100 + 150 = **500** → ölçek **1000/500 = 2** → kotlar **100, 300, 100, 200, 300** (yani \(1000 \cdot w_i / S\)).
- **“2 ile çarp”** sabit bir kural değildir; çarpan **\(1000/S\)** (ebeveyn kotası ve seviyeye göre genel olarak \(K/S\)).

Alt seviyelerde (alt strateji, süreç bağlamı vb.) aynı **oransal bölüşüm** ilkesi uygulanır; ebeveynin kotası \(K\) bir üstten gelir.

---

## 5. Süreç ↔ alt strateji yüzdeleri

- Süreç oluşturma / düzenleme ekranında, K-Vektör **açıkken:** seçilen her alt strateji için **%** girişi (ör. 60).
- Bu %, **o sürecin (hesaplanmış) süreç skorunun** ilgili alt stratejiye nasıl yansıyacağını belirler; **birden fazla** alt strateji bağlantısında her biri için ayrı %.
- **Toplam % 100’ü aşamaz**; aşımda kullanıcı **bilgilendirilir** (kayıt engeli veya onay politikası uygulama aşamasında netleştirilir — varsayılan: engelleme).
- **Tek** alt strateji seçildiğinde bile kullanıcı **% girmek zorundadır** (otomatik 100 yok); ileride süreç değişikliklerinde yönetilebilirlik için.
- Tüm bağlar için % **girişi yok / toplam 0** senaryosu: **eşit dağıtım** (bağlı alt strateji sayısına göre).

---

## 6. Yuvarlama (A)

- Ara hesaplarda yeterli hassasiyet (ör. ondalık) kullanılır.
- **Küçük yuvarlama farkları** için **son adımda düzeltme** uygulanır; gösterilen **vizyon toplamı** ile **1000** hedefi tutarlı olacak şekilde (ör. son kademede kalan fark en küçük birimlere dağıtım veya tek kaleme düzeltme — uygulama notunda net formül seçilecek).

---

## 7. Boş ağırlık / sıfır toplam (B)

- Ana (ve uygun alt) seviyelerde ham ağırlıklar **hiç girilmemiş veya anlamsız sıfır toplamı** → **eşit dağıtım**.
- Süreç–alt strateji % tarafında: **Bölüm 5** ile uyumlu (toplam 0 → eşit).

---

## 8. Zaman (C)

- Skor **güncel ve anlık**: PG / süreç verisi ne ise hesap o anki duruma göre (ilk fazda dönem/ay bazlı raporlama **zorunlu değil**).

---

## 9. Denetim ve geçmiş (D)

- Ağırlık veya % **değişikliklerinde** **değişiklik anına snapshot** saklanır (denetim izi).
- Sadece “yeniden hesapla ve geçmişi sil” modeli **kullanılmaz**; en azından yapılandırma değişiklikleri kayıt altına alınır.

---

## 10. Uygulama notları (teknik)

- Hesaplama motoru: saf fonksiyon + test edilebilir girdi/çıktı.
- Tenant bayrağı + ağırlık / süreç-% tabloları + snapshot tabloları (şema ayrı migration ile).
- API: özet skor ve kırılım (UI ve rapor).
- Performans: gerektiğinde önbellek; PG/süreç verisi veya ağırlık değişiminde invalidasyon.

---

## 11. Revizyon

| Tarih | Değişiklik |
|-------|-------------|
| 2026-03-29 | İlk sürüm: ürün kararları A–D dahil konsolide edildi. |

---

## 12. Uygulama günlüğü (ilerleme)

Bu bölüm, kod ve operasyonel adımların kısa kaydıdır; ayrıntılı spesifikasyon yukarıdaki maddelerdedir.

| Tarih | Not |
|-------|-----|
| 2026-03-29 | Alembic `v8w9x0y1z002`: `tenants.k_vektor_enabled`, `k_vektor_strategy_weights`, `k_vektor_sub_strategy_weights`, `k_vektor_config_snapshots`. |
| 2026-03-29 | Skor motoru: `k_vektor_enabled` ise `k_vektor_engine.compute_k_vektor_bundle`, değilse mevcut ortalama tabanlı vizyon akışı. |
| 2026-03-29 | Kurum ayarları: K-Vektör yalnızca aç/kapa (snapshot `k_vektor_toggle`). |
| 2026-03-29 | Ana/alt ham ağırlıklar: `/sp` **Strateji listesi** içinde ana/alt **Düzenle** modalları (`k_vektor_weight_raw`); snapshot `k_vektor_weight_strategy` / `k_vektor_weight_sub_strategy`. Toplu API: `GET/POST /sp/api/k-vektor/weights`. |
| 2026-03-29 | Süreç API/UI (`/process`): K-Vektör açıkken süreç modalında alt strateji katkı %; toplam ≤ 100; `_apply_sub_strategy_links` doğrulaması. |
| 2026-03-29 | `k_vektor_engine`: süreç bağları için `sqlalchemy.orm.joinedload` ile yükleme düzeltmesi. |
