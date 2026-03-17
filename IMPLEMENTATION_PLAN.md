
# 🚀 Stratejik Planlama ve Süreç Karnesi Uygulama Planı

Mevcut kod altyapısı ve **Yazılım.docx** ile **Excel Karneleri** analiz edilerek oluşturulan yol haritasıdır.

## 📅 Faz 1: Veritabanı ve Model Uyarlaması
**Hedef:** Veritabanını Excel'deki karne yapısına tam uyumlu hale getirmek.

1.  **KPI (Gösterge) Modelinin Güncellenmesi (`SurecPerformansGostergesi`):**
    *   `calculation_method` alanı güncellenecek: `Ortalama`, `Toplam`, `Son Değer`.
    *   `target_method` (Hedef Belirleme Yöntemi) için sabit seçenekler eklenecek:
        *   `RG` (Rakibe Göre)
        *   `HKY` (Hedef Katsayısı Yöntemi)
        *   `HK` (Hedef Konulamaz)
        *   `SH` (Sabit Hedef)
        *   `DH` (Dalgalı Hedef)
        *   `SGH` (Sektöre Göre Hedef)
    *   `gosterge_turu` alanı için seçenekler: `İyileştirme`, `Koruma`, `Bilgi Amaçlı`.
    *   Excel'deki `Doküman No`, `Revizyon Tarihi` gibi alanların `Surec` modelindeki varlığı teyit edilecek ve arayüzde gösterimi sağlanacak.

## 🖥️ Faz 2: Süreç Karnesi Arayüzü (Web UI)
**Hedef:** Süreç Liderlerinin Excel yerine sistem üzerinden karne oluşturmasını sağlamak.

1.  **Süreç Detay Sayfası Revizyonu:**
    *   "Süreç Özlük Bilgileri" paneli oluşturulacak.
    *   Alanlar: Süreç Adı, Doküman No, Rev. Tarihi, Rev. No, İlk Yayın Tarihi, Süreç Sınırları (Başlangıç/Bitiş).
    *   Yetki: Sadece **Süreç Lideri** ve **Üst Yönetim** düzenleyebilecek.

2.  **KPI Yönetim Modalı:**
    *   Yeni KPI eklerken yukarıdaki yeni dropdown seçenekleri (Yöntem, Tür, Hesaplama) sorulacak.
    *   Excel'deki sütun yapısına uygun bir tablo görünümü tasarlanacak.

## 🧮 Faz 3: Hesaplama ve Bireysel İndirgeme Motoru
**Hedef:** Stratejik hedeflerin otomatik hesaplanması ve kişilere dağıtılması.

1.  **Hesaplama Mantığı:**
    *   `Ortalama`: (Q1 + Q2 + Q3 + Q4) / 4
    *   `Toplam`: Q1 + Q2 + Q3 + Q4
    *   `Son Değer`: Q4 (veya en son girilen veri)
    *   Başarı Puanı Hesaplaması: (Gerçekleşen / Hedef) * 100

2.  **Bireysel Atama:**
    *   Süreç KPI'ları bireylere atandığında ("Süreçten Bireye"), seçilen hesaplama yöntemi bireysel hedefe de miras kalacak.

## 📊 Faz 4: Görselleştirme ve Raporlama
**Hedef:** Excel'deki "Grafik" ve "Yıl Sonu" görünümlerinin dijitalleştirilmesi.

1.  **Dijital Karne:**
    *   Süreç sayfasında Excel şablonuna çok benzeyen, renkli (HTML Table) bir "Karne Görünümü" oluşturulacak.
    *   Geçmiş yılların verileri (Önceki Yıl Ort.) sütun olarak gösterilecek.

---
**Teknik Not:** Veri girişi "Elle" olacağı için Excel Import özelliği **kapsam dışı** bırakılmıştır.
