# Excel Süreç Karnesi vs Mevcut Sistem Analizi

## Excel Dosyası Yapısı (SR4 Pazarlama Stratejileri Yönetimi Süreç Karnesi.xlsx)

### 1. Başlık Bilgileri
- **Süreç Adı**: SR4 - PAZARLAMA STRATEJİLERİ YÖNETİMİ SÜREÇ KARNESİ
- **REV. TARİHİ**: Revizyon tarihi (örn: 2021-04-15)
- **YAYIN TARİHİ**: İlk yayın tarihi (örn: 2020-02-01)
- **DOKÜMAN NO**: Doküman numarası
- **SÜREÇ LİDERİ**: Tek lider (örn: Salih YALIN)
- **SÜREÇ EKİBİ**: Ekip üyeleri (virgülle ayrılmış)

### 2. Performans Göstergeleri Tablosu Yapısı

#### Kolonlar:
1. **Ana Strateji** (ST2, ST3, ST4 gibi)
2. **Alt Strateji** (ST2.1, ST2.2, ST3.1 gibi)
3. **Gösterge** (Performans göstergesi adı)
4. **Göst. Türü** (iyileştirme, istatistik)
5. **Hedef Belirl. Yön.** (DH, HKY, SH, RG, HK, SGH)
6. **Göst. Ağırlığı (%)** (0.05, 0.1, 0.11 gibi)
7. **Birim** (TL, %, adet)
8. **Ölçüm Per.** (3 ay, 6 ay, 1 Yıl)
9. **Önceki Yıl Ort.** (Önceki yılın ortalaması)
10. **Fiili/Hedef** (Fiili veya Hedef satırı)
11. **1.Ç** (1. Çeyrek değeri)
12. **2.Ç** (2. Çeyrek değeri)
13. **3.Ç** (3. Çeyrek değeri)
14. **4.Ç** (4. Çeyrek değeri)
15. **Yıl Sonu** (Yıl sonu toplam/hedef)
16. **Başarı Puanı** (1-5 arası)
17. **Ağırlıklı Başarı Puanı** (Ağırlık × Başarı Puanı)
18. **Başarı Puanı Aralıkları** (Kolon 19-23):
    - Beklentinin Çok Altında (1 puan)
    - İyileştirmeye Açık (2 puan)
    - Hedefe Ulaşmış (3 puan)
    - Hedefin Üzerinde (4 puan)
    - Mükemmel (5 puan)

### 3. Veri Yapısı
- Her performans göstergesi için **2 satır**:
  - **Fiili satır**: Gerçekleşen değerler
  - **Hedef satır**: Hedef değerler
- Çeyrek bazlı veri girişi
- Başarı puanı hesaplama (1-5 arası)
- Ağırlıklı başarı puanı hesaplama

### 4. Yıllık Sheet'ler
- Her yıl için ayrı sheet (2021, 2022, 2023, 2025)
- Aynı yapı, farklı veriler

## Mevcut Sistem Yapısı

### 1. Süreç Bilgileri
- Süreç adı, doküman no, rev no, yıl bilgisi
- Çoklu lider desteği (liderler listesi)
- Çoklu üye desteği (üyeler listesi)

### 2. Performans Göstergeleri Tablosu
- Kodu, Performans Adı, Hedef, Periyot, Ağırlık (%), Hesaplama Yöntemi
- Çeyrek bazlı kolonlar: Hedef, Gerç., Durum (her çeyrek için)
- İşlemler kolonu (Düzenle, Sil)

### 3. Veri Yapısı
- Tek satırda hem hedef hem gerçekleşen değerler
- Çeyrek bazlı veri girişi
- Durum göstergesi (renk kodlu)

## Farklar ve Eksikler

### Eksik Özellikler:
1. **Ana Strateji ve Alt Strateji kolonları** - Excel'de var, mevcut sistemde yok
2. **Göst. Türü** (iyileştirme/istatistik) - Excel'de var, mevcut sistemde yok
3. **Hedef Belirl. Yön.** (DH, HKY, SH, RG, HK, SGH) - Excel'de var, mevcut sistemde yok
4. **Önceki Yıl Ort.** - Excel'de var, mevcut sistemde yok
5. **Başarı Puanı** (1-5 arası) - Excel'de var, mevcut sistemde yok
6. **Ağırlıklı Başarı Puanı** - Excel'de var, mevcut sistemde yok
7. **Başarı Puanı Aralıkları** (5 seviye) - Excel'de var, mevcut sistemde yok
8. **Fiili/Hedef satır ayrımı** - Excel'de 2 satır, mevcut sistemde tek satır
9. **Yıl Sonu toplam/hedef** - Excel'de var, mevcut sistemde yok
10. **Yıllık sheet'ler** - Excel'de var, mevcut sistemde yok

### Farklılıklar:
1. **Süreç Lideri**: Excel'de tek lider, mevcut sistemde çoklu lider
2. **Süreç Ekibi**: Excel'de virgülle ayrılmış metin, mevcut sistemde liste
3. **Veri Görünümü**: Excel'de 2 satır (Fiili/Hedef), mevcut sistemde tek satır

## Önerilen Değişiklikler

### 1. Veritabanı Değişiklikleri
- `SurecPerformansGostergesi` modeline yeni alanlar:
  - `ana_strateji_kodu` (ST2, ST3, ST4)
  - `alt_strateji_kodu` (ST2.1, ST2.2)
  - `gosterge_turu` (iyileştirme, istatistik)
  - `hedef_belirleme_yontemi` (DH, HKY, SH, RG, HK, SGH) - Zaten var: `target_method`
  - `onceki_yil_ortalamasi`
  - `basari_puani` (1-5 arası)
  - `agirlikli_basari_puani`
  - `basari_puani_araliklari` (JSON: {1: "...", 2: "...", 3: "...", 4: "...", 5: "..."})

### 2. Frontend Değişiklikleri
- Tablo yapısını Excel formatına uygun hale getir:
  - Ana Strateji ve Alt Strateji kolonları ekle
  - Göst. Türü kolonu ekle
  - Hedef Belirl. Yön. kolonu ekle
  - Önceki Yıl Ort. kolonu ekle
  - Başarı Puanı kolonu ekle
  - Ağırlıklı Başarı Puanı kolonu ekle
  - Fiili/Hedef satır ayrımı (2 satır gösterimi)
  - Başarı puanı aralıkları gösterimi

### 3. Hesaplama Mantığı
- Başarı puanı hesaplama algoritması:
  - Gerçekleşen değeri başarı puanı aralıklarına göre 1-5 arası puana çevir
  - Ağırlıklı başarı puanı = Ağırlık × Başarı Puanı
  - Süreç toplam ağırlıklı başarı puanı = Tüm PG'lerin ağırlıklı başarı puanları toplamı

### 4. Yıllık Veri Yönetimi
- Her yıl için ayrı veri saklama
- Yıl bazlı filtreleme ve görüntüleme
- Önceki yıl ortalaması hesaplama ve saklama



