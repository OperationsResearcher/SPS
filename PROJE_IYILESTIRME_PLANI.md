# 🚀 Proje İyileştirme Planı (Project Improvement Plan)

Bu belge, mevcut Stratejik Planlama Sistemi projesinin Backend, Frontend ve Veritabanı yapısının detaylı analizini ve tespit edilen sorunların çözümüne yönelik kapsamlı iyileştirme planını içerir.

## 📋 1. Yönetici Özeti
Proje genel olarak modern bir teknoloji yığını (Python/Flask, SQLAIchemy) üzerine kurulmuş ve "production-ready" (üretime hazır) olma yolunda ilerlemektedir. Ancak, **kritik güvenlik açıkları**, **yönetilemez dosya boyutları** ve **standart dışı veritabanı yönetimi** gibi acil müdahale gerektiren alanlar tespit edilmiştir.

**Genel Sağlık Puanı:** 6/10

---

## 🔍 2. Detaylı Analiz Raporu

### 2.1 🛡️ Güvenlik Analizi (Kritik)
*   **Debug Modu Açık:** `app.py` dosyasında `app.run(debug=True)` satırı hardcoded olarak bırakılmış. Bu, canlı ortamda (production) sistemin kaynak kodlarını ve hata detaylarını dışarıya açarak büyük bir güvenlik riski oluşturur.
*   **Hassas Veriler:** `.env` dosyası kullanılıyor olması olumlu, ancak kod içinde bazı noktalarda geliştirme ortamına yönelik "bypass" kodları olabilir.
*   **CSP (Content Security Policy):** `__init__.py` içinde CSP ayarları var ancak `unsafe-inline` kullanımı XSS saldırılarına kapı aralayabilir.

### 2.2 🏗️ Mimari ve Kod Kalitesi Analizi
*   **Monolitik Dosyalar (God Object Anti-pattern):**
    *   `models.py`: Yaklaşık **2000 satır**. Tüm veritabanı modelleri tek bir dosyada. Bu durum bakımı zorlaştırır, ekip çalışmasını engeller ve Git çakışmalarına yol açar.
    *   `api/routes.py`: Yaklaşık **4000 satır**. Tüm API uç noktaları tek dosyada. Okunabilirlik çok düşük.
    *   `main/routes.py`: **4000+ satır**.
*   **Kod Tekrarı:** Benzer yetki kontrolleri ve veri doğrulama işlemleri farklı yerlerde tekrar edilmiş.
*   **Tip Güvenliği:** Python 3.8+ kullanılmasına rağmen "Type Hinting" (Tip ipuçları) kullanımı çok az.

### 2.3 🗄️ Veritabanı Yapısı Analizi
*   **Manuel Migrasyonlar:** `__init__.py` dosyası içinde uygulamanın başlangıcında çalışan `ALTER TABLE` komutları tespit edildi. Bu, profesyonel bir yaklaşım değildir. Veritabanı şema değişiklikleri **Flask-Migrate (Alembic)** ile yönetilmeli ve versiyonlanmalıdır.
*   **İlişkisel Bütünlük:** Modellerde soft-delete (silindi) bayrağı var ancak tüm sorgularda bu bayrağın kontrol edildiğinden emin olunmalı.

### 2.4 🎨 Frontend Analizi
*   **Karışık Yapı:** HTML şablonları (`templates/`) içinde yoğun miktarda inline JavaScript ve CSS bulunuyor. Bu, frontend kodunun yeniden kullanılabilirliğini ve test edilebilirliğini düşürüyor.
*   **Kök Dizin Kirliliği:** Kök dizinde çok sayıda geçici test betiği (`test_*.py`, `fix_*.py`) ve prototip HTML dosyası (`modul-*.html`) bulunuyor.

---

## 🛠️ 3. İyileştirme Yol Haritası (Uygulama Adımları)

Aşağıdaki adımlar, projenin otonom olarak iyileştirilmesi için öncelik sırasına göre planlanmıştır.

### 🚨 Faz 1: Kritik Güvenlik ve Altyapı Düzeltmeleri (Acil)
1.  **Debug Modu Kapatma:** `app.py` düzenlenerek `FLASK_DEBUG` ortam değişkenine bağlı hale getirilecek.
2.  **Güvenli Başlatma:** `__init__.py` içindeki güvenlik başlıkları (Security Headers) ve CSRF ayarları gözden geçirilecek.
3.  **Manuel DB Kodlarını Temizleme:** `__init__.py` içindeki riskli `ALTER TABLE` blokları temizlenecek ve bu değişiklikler düzgün bir migrasyon dosyasına dönüştürülecek.

### 🏗️ Faz 2: Mimari Refactoring (Yapısal Düzenleme)
1.  **Modelleri Parçalama:** `models.py` dosyası `models/` paketi altına taşınacak ve modüllere ayrılacak:
    *   `models/user.py` (Kullanıcı, Yetki)
    *   `models/process.py` (Süreç, Faaliyet)
    *   `models/strategy.py` (Strateji)
    *   `models/project.py` (Proje Yönetimi)
2.  **Route'ları Parçalama:** `api/routes.py` ve `main/routes.py` dosyaları `blueprints/` yapısına dönüştürülecek. Her modül kendi route dosyasına sahip olacak.

### 🧹 Faz 3: Kod Temizliği ve Organizasyon
1.  **Kök Dizin Temizliği:** `.py` uzantılı test ve fix scriptleri `scripts/` veya `tests/` klasörüne, `.html` prototipleri `prototypes/` klasörüne taşınacak.
2.  **Kod Standartları:** Türkçe yorum satırları ve Type Hinting (Tip İpuçları) eklenecek.

---

## ✅ Sonuç
Bu plan uygulandığında, proje; güvenliği sağlanmış, modüler, geliştirilmesi kolay ve modern standartlara uygun bir yapıya kavuşacaktır.
