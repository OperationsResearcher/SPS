# Kart Açıklama Zenginleştirme — DEVİR NOTU

> **Durdurma noktası: 2026-07-20.** Kullanıcı başka önemli sorunlara geçti.
> **"Kart işine devam" denildiğinde ÖNCE BU DOSYA OKUNUR**, sonra §"Devam
> Yordamı"ndaki adımlar uygulanır. Sıfırdan keşif yapmaya gerek yok.

---

## 1. Nerede kaldık — tek bakışta

| | |
|---|---|
| **Tamamlanan** | K-Radar 97 + **raporlar 94** = **191/501 kart** (güncelleme 2026-07-21) |
| **Kalan** | **310 kart** |
| **raporlar ortalaması** | 49 → **541 karakter** (2026-07-21) |
| **Tüm katalog ortalaması** | **277 karakter** (2026-07-21 ölçümü) |
| **Son durum** | K-Radar altyapısı main'de (`51c30bd4`); raporlar dilimi `claude/kart-aciklama-raporlar` dalında |

### Kalan iş — modül bazında (öncelik sırası)

| Modül | Kart | Mevcut ort. | Not |
|---|---|---|---|
| ~~`raporlar`~~ | ~~94~~ | ✅ 541 krk | **BİTTİ 2026-07-21** — `card_descriptions_raporlar.py` |
| `admin` | **83** | 74 krk | Yönetim ekranları |
| `sp` | **83** | 87 krk | Stratejik Planlama — literatür ağırlıklı (SWOT/TOWS/PESTEL burada da var) |
| `project` | 21 | 90 krk | Proje/portföy |
| `bireysel` | 14 | 68 krk | Bireysel performans |
| `process` | 13 | 135 krk | Süreç yönetimi |
| `yonetim` | 9 | 142 krk | |
| `ayarlar` / `kurum` / `auth` | 6+6+6 | ~90 krk | Küçük gruplar |
| `masaustu` + diğer tekil | ~70 | — | Dağınık kalanlar |

**Önerilen sıra (kalan):** `sp` → `admin` → `project` → `bireysel` → kalanlar.
(`sp` literatür bakımından K-Radar'a en yakın, hazır malzeme var — bkz. §4.)

**raporlar diliminde işleyen yöntem (2026-07-21, tekrar kullan):** 94 kart 4 paralel
Explore ajanına bölündü (sayfa grupları halinde), her ajan kart başına
Formül/Kaynak/Eşik/Fallback/Sınır çıkardı (dosya:satır kanıtlı) → açıklamalar tek
oturumda yazıldı → seed KONTROL 94/94 eşleşme → uygulandı. Ajan bulguları ayrıca
gerçek kod tutarsızlıkları yakaladı (ai_danisman action/pivot_type uyumsuzluğu,
audit PDF 4-vs-6 bölüm, ml_anomaly 6-vs-8 ölçüm metni) → KART-VERI-TUTARSIZLIKLARI.md'ye
işlenecek adaylar.

---

## 2. Kurulmuş altyapı — YENİDEN YAPMA

Bunların hepsi çalışıyor ve commit'li:

### 2.1 Şema
`system_cards.description` **`varchar(512)` → `Text`** (migration `391945351814`).
İlk deneme 512 sınırına takılıp `StringDataRightTruncation` vermişti.
**Test/Demo/Yayın'da bu migration KOŞULMADI** — oralarda uygulanmadan seed
çalıştırılırsa aynı hatayı verir.

### 2.2 Modal render
`ui/templates/platform/base.html` → **`renderInfoBody()`** fonksiyonu.
Önceden `bodyEl.textContent = j.description` idi (tek okunaksız duvar).
Şimdi düz metni yapılandırılmış basıyor:

| Girdi | Çıktı |
|---|---|
| `Başlık:` ile başlayan satır | kalın bölüm etiketi + gövde |
| boş satır | paragraf ayracı |
| `- ` ile başlayan satır | madde listesi |

XSS-güvenli: `innerHTML` yok, `createElement` + `textContent`.
`ui/static/platform/css/card_layer.css` → `.kk-b`'den `white-space: pre-wrap`
kaldırıldı (yapılandırılmış düğümlerle çakışıp çift boşluk yapıyordu).

### 2.3 Seed mekanizması
```bash
python scripts/seed_card_descriptions.py                    # KONTROL (varsayılan, yazmaz)
python scripts/seed_card_descriptions.py --calistir         # uygula
python scripts/seed_card_descriptions.py --calistir --sadece sp   # önek filtresi
```
- İdempotent (aynı metin varsa yazmaz), yalnız `description` alanına dokunur.
- DB'de olmayan `code` için kart **oluşturmaz**, atlar ve raporlar.
- İçerik kaynağı: `scripts/seed_data/card_descriptions_*.py` → `DESCRIPTIONS` dict.
- Yeni dosya eklemek yeterli; script `card_descriptions_*.py` kalıbındaki
  tüm dosyaları otomatik birleştirir.

**Mevcut içerik dosyaları:**
- `card_descriptions_k_radar.py` — 9 KP alt modülü
- `card_descriptions_k_radar_ks.py` — 16 KS + KP mini
- `card_descriptions_k_radar_kpr.py` — 14 KPR/Cross/Risk
- `card_descriptions_k_rapor.py` — 58 rapor kartı

---

## 3. Yazım sözleşmesi — BAĞLAYICI

Her açıklama şu bölüm sırasını izler (hepsi zorunlu değil, sırası zorunlu):

```
[tanım paragrafı — kavram nedir]

Hesap: [net aritmetik, koddan doğrulanmış]

Sınır: [gösterge adıyla gerçekte ölçülen ayrışıyorsa MUTLAKA]

Eşik: [kodda tanımlı bant varsa]

Yorum: [nasıl okunmalı, ne zaman yanıltır]

Kaynak: [doğrulanmış literatür — yazar, eser, yıl]
```

### Üç kural
1. **Uydurma yok.** Formül koddan, literatür web'den doğrulanır. Emin
   olunmayan yazılmaz.
2. **Şeffaflık zorunlu** (kullanıcı kararı, 2026-07-20). Gösterge adıyla
   gerçekte ölçülen şey ayrışıyorsa `Sınır:` bölümünde açıkça yazılır.
   Örnek: *"Bu oran 'zamanında tamamlanma' DEĞİL, yalnızca 'tamamlanma'
   oranıdır."*
3. **Düz metin.** DB'de markdown yok — biçimlendirmeyi modal yapar (§2.2).
   i18n zinciri bu sayede bozulmuyor.

### Doğrulanmış literatür — hazır malzeme
OEE/Nakajima 1988 (**dünya standardı %85** — listedeki tek sağlam sayısal eşik) ·
Muda/Ohno 1978 (7 israf) · VSM/Rother & Shook 1998 · Pareto/Juran ·
CMMI/SEI (5 seviye) · TOC/Goldratt 1984 (5 odaklanma adımı) · SLA/ITIL ·
Benchmarking/Camp 1989 · EVM/PMI (CPI, SPI; 1,0 referans) · CPM/Kelley &
Walker 1959 · Kingman kuyruk formülü 1961 · A3/Toyota · BSC/Kaplan & Norton
1992 (4 boyut) · Paydaş/Freeman 1984 · Güç-İlgi matrisi/Johnson & Scholes 1993 ·
Porter 5 Kuvvet 1979 · Porter değer zinciri 1985

### ⚠️ SWOT kökeni — dikkat
**"Albert Humphrey / Stanford Research Institute" atfını KULLANMA.**
Puyt, Lie & Wilderom, *"The origins of SWOT analysis"*, Long Range Planning
(2023) bu yaygın atfı çürütüyor. Güvenli ifade:
> *"1960'larda Stanford Research Institute'ta SOFT yöntemi olarak geliştirildi."*

### Diğer doğrulanamayan iddialar (kullanma)
- Akış verimliliğinde "%25 = yalın" eşiği → sektör teamülü, Rother & Shook'ta yok
- EVM'de "0,90 altı kritik" → uygulama teamülü, PMBOK'ta norm değil
- Ohno'nun 7 israfına eklenen 8. israf → sonraki dönem eklemesi
- SLA için evrensel eşik → yok, sözleşmeye özgü

---

## 4. Devam Yordamı — adım adım

### Adım 1: Kalan kartları çıkar
```bash
python -c "
from app import create_app; from extensions import db; from sqlalchemy import text
app=create_app()
with app.app_context():
    for r in db.session.execute(text(
      \"SELECT short_id, code, name, coalesce(description,'') FROM system_cards \"
      \"WHERE code LIKE 'sp=_%' ESCAPE '=' AND length(coalesce(description,''))<=350 ORDER BY code\"
    )).fetchall(): print(r[0], '|', r[1], '|', r[3][:60])
"
```
(`sp` yerine hedef modül öneki.)

### Adım 2: Kod bağlamını çıkar (ZORUNLU)
Explore ajanı ile ilgili modülün route/servis/template dosyalarını taratıp
her kart için **formül / kaynak tablo / eşik / fallback / sınır** çıkar.
**Bu adım atlanırsa açıklama uydurma olur.**

K-Radar'da kullanılan ajan istemi işe yaradı; aynı kalıbı kullan:
> "Her kart için: Ne gösteriyor / Formül / Kaynak (tablo+filtre) / Eşik /
> Fallback / Sınır (isim ile ölçülen ayrışıyorsa MUTLAKA). Emin olmadığın
> yeri 'KOD'DA BULUNAMADI' yaz — tahmin etme."

### Adım 3: Literatür (yalnız gerekiyorsa)
`sp` modülünde SWOT/TOWS/PESTEL/BSC tekrar geçecek — §3'teki hazır malzeme
yeterli. Yeni kavram çıkarsa (ör. Hoshin Kanri, Ansoff, BCG matrisi) web'den
doğrulat.

### Adım 4: İçerik dosyasını yaz
`scripts/seed_data/card_descriptions_<modul>.py` → `DESCRIPTIONS` dict.
§3 sözleşmesine uy.

### Adım 5: Uygula ve doğrula
```bash
python scripts/seed_card_descriptions.py                  # önce KONTROL
python scripts/seed_card_descriptions.py --calistir       # sonra uygula
```
`DB'de kart YOK` satırı sıfır olmalı; değilse kart kodu yanlış yazılmıştır.

### Adım 6: Ölç ve commit'le
Modül ortalamasının önce/sonra değerini raporla.

---

## 5. Bu iş sırasında BULUNAN HATALAR — ayrı iş

Açıklama yazmak için kodu okurken çıkan gerçek hatalar
**`docs/kontrol/KART-VERI-TUTARSIZLIKLARI.md`** dosyasında, öncelik sıralı.
Açıklamalarda dürüstçe kabul edildiler ama **düzeltilmediler.**

### En kritik: D0 — 438 gösterge ters hesaplanıyor
`micro/modules/k_rapor/routes.py` satır **991, 1901, 2161**:
```python
if kpi.direction == "lower_is_better":   # ← DB'de bu değer HİÇ YOK
```
Ölçüldü (2026-07-20): `Increasing`=956, `Decreasing`=**438**,
`lower_is_better`=**0**. Koşul hiçbir zaman doğru olmuyor →
**438 "azalması iyi" gösterge artması iyiymiş gibi hesaplanıyor.**

Somut etki: hedefi 5 olan hata oranı 2 ölçüldüğünde `%40` görünüyor;
doğrusu `%100`. **İyi performans kötü raporlanıyor.**

Skor motoru (`compute_pg_score`) doğru değeri kullandığı için **aynı gösterge
Kurumsal sekmesinde farklı, PG Dağılım sekmesinde farklı yüzde gösteriyor.**

**Düzeltme 3 satır** ama rapor rakamlarını değiştireceği için kullanıcı onayı
bekliyor. Düzeltmeden önce/sonra birkaç göstergenin yüzdesi elle doğrulanmalı.

### Diğerleri (belgede tam liste)
G1 KPR risk kartı yetki kapsamı uygulamıyor (yetki sızıntısı) · D1 değer
zinciri boşken maksimum gösteriyor · D2 trend yapay yön üretiyor · D3
veri yokken türetilmiş sayı (yaygın desen) · T1 risk eşiği iki ekranda
farklı (15 vs 16) · İ1 isim/ölçüm ayrışmaları (6 kalem)

---

## 6. Deploy durumu

- Yerel: **uygulandı** (97 kart + migration).
- Test / Demo / Yayın: **hiçbiri uygulanmadı.**
- Oralara taşınırken **sıra önemli**: önce `flask db upgrade` (Text migration),
  sonra `python scripts/seed_card_descriptions.py --calistir`.
  Migration koşmadan seed çalıştırılırsa 512 sınırına takılır.
- Seed, kod deploy'uyla otomatik çalışmaz (bilinen açık — `docs/kontrol/seed_calistirma_kaydi.md`).
