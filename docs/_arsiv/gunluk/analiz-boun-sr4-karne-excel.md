# Boğaziçi Üniversitesi SR4 — Süreç Karnesi Excel Analizi

**Kaynak dosya:** `docs/KMF/s11.xlsx` (önceki ad: SR4 Pazarlama Stratejileri Yönetimi Süreç Karnesi)  
**Çıkarım:** `scripts/analyze_karne_xlsx.py` + `docs/KMF/s11-xlsx-ozet.txt` (ham çıktı)

---

## 1. Çalışma kitabı yapısı

| Sayfa | Amaç |
|--------|------|
| **Veriler** | Şablon / ana veri: süreç üst bilgisi + tüm PG satırları, başarı puanı aralıkları, çeyreklik ve yıl sonu sütunları (fiili + hedef çiftleri). |
| **2021** … **2025** | Yıllık “rapor” görünümü: aynı tablo iskeleti, ilgili yıla ait değerler ve o yılın revizyon/yayın tarihleri; PG listesi yıllara göre değişebiliyor (ör. 2024’te yapı farklı). |

**Sütun sayısı:** ~23 (veri + 5 sütunluk başarı puanı bandı açıklamaları).

---

## 2. Üst bilgi (yıllık sayfalarda ~satır 1–4)

- **Başlık:** SR4 — PAZARLAMA STRATEJİLERİ YÖNETİMİ SÜREÇ KARNESİ  
- **Revizyon tarihi**, **Yayın tarihi**, **Doküman no** (hücreler yatay birleşik yapıda)  
- **Süreç lideri** (ör. Salih YALÇIN, Tuğba Sorkulu)  
- **Süreç ekibi** (isim listesi; yıllara göre güncellenmiş)

Bunlar Kokpitim’de kısmen **`Process`** (ad, doküman no, revizyon) ve **`Process.leaders` / üyeler** ile karşılanır; Excel’deki serbest metin alanları için ek alan veya not şablonu gerekebilir.

---

## 3. Başarı puanı bandı (~satır 5)

Beş sütunda metinsel aralıklar (1–5 puan):

1. Beklentinin çok altında  
2. İyileştirmeye açık  
3. Hedefe ulaşmış  
4. Hedefin üzerinde  
5. Mükemmel  

**Veriler** sayfasında bu aralıklar PG satırının sağında hücrelerde de tekrarlanıyor (ör. `400.000-449.000`, `%80-89` gibi göstergeye özel eşikler).

Kokpitim PG formunda **`basari_puani_araliklari`** (JSON) bu yapıya denk gelir.

---

## 4. Tablo başlığı (~satır 6) — sütun sözlüğü

| Excel sütunu (mantık) | İçerik | Kokpitim eşlemesi |
|------------------------|--------|-------------------|
| Ana Strateji | ST2, ST3… kod | Strateji başlığı (API’de `strategy_title`) |
| Alt Strateji | ST2.1, ST2.2… | Alt strateji kodu + başlık (`sub_strategy_*`) |
| Gösterge | PG adı | `ProcessKpi.name` |
| Göst. Türü | Kısaltma (ör. İyileştirme) | `gosterge_turu` |
| Hedef Belirl. Yön. | DH, HKY, SH… | `target_method` |
| Göst. Ağırlığı (%) | 0.05–0.11 vb. | `weight` (yüzde) |
| Birim | TL, %, adet… | `unit` |
| Ölçüm Per. | 3 ay, 1 Yıl, 6 ay… | `period` (metin eşlemesi gerek: “Çeyreklik” / özel) |
| Önceki Yıl Ort. | Sayı veya boş | `onceki_yil_ortalamasi` |
| Fiili / Hedef | Satır etiketi | İki ayrı veri satırı (aşağıda) |
| 1.Ç, 2.Ç, 3.Ç, 4.Ç | Çeyrek değerleri | `entries.ceyrek_1` … `ceyrek_4` |
| Yıl Sonu | Yıllık özet hücresi | `entries.yillik_1` veya yıla göre tek değer |
| Başarı Puanı | 0–5 | Hesaplanan / şablonda saklanan |
| Ağırlıklı Başarı Puanı | Ağırlık × puan | Raporlama (sistemde ayrı hesap veya export) |

**Not:** Excel’de her **gösterge** için genelde **iki satır**: biri **Fiili**, biri **Hedef** (aynı PG, farklı satır). Kokpitim’de hedef çoğu zaman hücre bazında `computeCellTargetMicro` ile türetilir; doğrudan “hedef satırı” importu için veri modeli veya import kuralı netleştirilmeli.

---

## 5. Veri modeli farkları (dikkat)

1. **Çift satır (Fiili / Hedef):** Excel görsel olarak iki satır; Kokpitim’de tek PG + `entries` anahtarları. İçe aktarımda birleştirme kuralı yazılmalı.  
2. **Ölçüm periyodu metni:** “3 ay”, “1 Yıl”, “6 ay” → uygulamadaki `Aylık` / `Çeyreklik` / `Yıllık` ile eşleme tablosu gerekir.  
3. **Yıllık sayfa = yıl snapshot:** Her yıl ayrı sayfa; Kokpitim’de tek süreç karnesi + **yıl seçici**. Veri `KpiData` + `year` ile tutuluyor — mantık uyumlu.  
4. **PG seti yıllara göre değişiyor:** Aynı süreçte gösterge ekleme/çıkarma var; `is_active` ve tarihçe ile uyumlu tutulmalı.  
5. **“Veriler” sayfası:** Hem şablon hem güncel parametreler (2020 parametre başarı puanları gibi notlar) içeriyor; hangi hücrelerin “canlı veri” olduğu importta ayrıştırılmalı.

---

## 6. s11.xlsx’ten veri alma (uygulandı)

### Tam çıkarım: `scripts/kmf_s11_extract.py`

Üretir: `docs/KMF/s11-extracted.json` (UTF-8)

```bash
py scripts/kmf_s11_extract.py docs/KMF/s11.xlsx -o docs/KMF/s11-extracted.json --no-raw-rows
```

- **Sayfalar:** `Veriler` + dört haneli yıl sayfaları.
- Her sayfa için: `meta` (başlık, tarihler, lider, ekip, 1–5 puan bandı başlıkları), `gostergeler[]` (Fiili + Hedef birleşik).
- JSON içinde **`sizden_beklenen_netlestirmeler`**: Kokpitim’e yazmadan önce yanıtlanması gereken sorular (varsayımsız ilerleme).

### Yapısal özet betiği (ham satır dökümü)

`py scripts/analyze_karne_xlsx.py "docs/KMF/s11.xlsx" --rows 40`

### Manuel CSV

Excel’den sayfa bazında CSV; UTF-8 kaydedin.

Windows konsolunda Türkçe çıktı için:

`PYTHONIOENCODING=utf-8 py scripts/... > docs/KMF/ozet.txt`

---

## 7. Özet: Süreç karnesi oluşturmak için gereken bilgiler (checklist)

- [ ] Süreç kimliği: kod (SR4), ad, doküman no, revizyon / yayın tarihi  
- [ ] Süreç lideri ve ekip üyeleri (sistem kullanıcılarına bağlama)  
- [ ] Her PG için: ana/alt strateji, ad, gösterge türü, hedef belirleme yöntemi, ağırlık, birim, ölçüm periyodu, önceki yıl ortalaması  
- [ ] Başarı puanı 1–5 için aralık tanımları (metin veya sayısal eşik)  
- [ ] Çeyrek bazında **fiili** değerler (ve Excel’de ayrı yazılmışsa **hedef** değerleri)  
- [ ] Yıl sonu sütunu değeri  
- [ ] İsteğe bağlı: hesaplanmış başarı puanı ve ağırlıklı skor (içe aktarımda doğrulama veya yeniden hesap)

---

## 8. Kokpitim’e aktarım (uygulandı)

**Kararlar:** Alt strateji **H1.1**; gösterge türü **İyileştirme**; ölçüm **3 ay→Çeyreklik**, **1 Yıl→Yıllık**, **6 ay→`6 ay`** (PG formuna eklendi); hedef metin aralığı → **sayıların ortalaması**; süreç **2 lider + 6 üye** tenant kullanıcılarından rastgele (`--seed` ile tekrarlanabilir).

```bash
py scripts/kmf_s11_import.py --process-id <SÜREÇ_ID> --actor-user-id <KULLANICI_ID> ^
  --xlsx docs/KMF/s11.xlsx --dry-run

py scripts/kmf_s11_import.py --process-id <SÜREÇ_ID> --actor-user-id <KULLANICI_ID> ^
  --xlsx docs/KMF/s11.xlsx --wipe-kpis --seed 42
```

- **Önkoşul:** Tenant’ta **H1.1** kodlu `SubStrategy` ve aktif kullanıcı **≥ 8**. Tanım repoda `scripts/seed_bogazici_strategies.py` içinde (SA1 altında, tam başlık metniyle); veritabanında yoksa: `py scripts/seed_bogazici_strategies.py --tenant-id <ID>` (veya `--tenant-name`).
- **`--wipe-kpis`:** İlgili süreçteki mevcut aktif PG ve KPI verilerini pasifleştirir.
- Veri satırları **yıl sayfalarından** (2021–2025); **Veriler** sayfası yalnızca şablonda olmayan göstergeler için tamamlayıcıdır.

*Son güncelleme: `s11.xlsx` okunarak dolduruldu; import TASK-073.*
