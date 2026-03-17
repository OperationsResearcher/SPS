/* Performans Göstergesi (PG) Modülü QA Soruları */

(function() {
    const questions = [
        { text: "Süreç karnesi sayfasında PG ekleme butonu görünüyor ve çalışıyor mu?", answer: '', explanation: '' },
        { text: "PG ekleme formunda zorunlu alanlar (ad, hedef değer, ölçüm birimi) belirtilmiş mi?", answer: '', explanation: '' },
        { text: "PG adı (ad) alanı doldurulabiliyor mu?", answer: '', explanation: '' },
        { text: "PG kodu (kodu) alanı doldurulabiliyor mu?", answer: '', explanation: '' },
        { text: "Hedef değer (hedef_deger) alanı doldurulabiliyor mu?", answer: '', explanation: '' },
        { text: "Ölçüm birimi (olcum_birimi) seçilebiliyor mu? (Adet, %, TL, Gün vb.)", answer: '', explanation: '' },
        { text: "Periyot seçimi yapılabiliyor mu? (Günlük, Haftalık, Aylık, Çeyreklik, Yıllık)", answer: '', explanation: '' },
        { text: "Ağırlık (agirlik) alanı doldurulabiliyor mu?", answer: '', explanation: '' },
        { text: "Önemli PG işaretleme (onemli checkbox) çalışıyor mu?", answer: '', explanation: '' },
        { text: "Veri toplama yöntemi (hesaplama yöntemi) seçilebiliyor mu? (Ortalama, Toplam vb.)", answer: '', explanation: '' },
        { text: "PG ekleme işlemi başarıyla tamamlandığında onay mesajı gösteriliyor mu?", answer: '', explanation: '' },
        { text: "PG listesi süreç karnesi sayfasında düzgün görüntüleniyor mu?", answer: '', explanation: '' },
        { text: "PG düzenleme butonu çalışıyor ve form/modal açılıyor mu?", answer: '', explanation: '' },
        { text: "PG düzenleme formunda mevcut PG bilgileri doğru şekilde yükleniyor mu?", answer: '', explanation: '' },
        { text: "PG düzenleme işlemi başarıyla kaydediliyor ve liste güncelleniyor mu?", answer: '', explanation: '' },
        { text: "PG silme butonu görünüyor mu?", answer: '', explanation: '' },
        { text: "PG silme işleminde onay mesajı gösteriliyor mu?", answer: '', explanation: '' },
        { text: "PG silme işlemi başarıyla tamamlanıyor ve listeden kaldırılıyor mu?", answer: '', explanation: '' },
        { text: "PG veri girişi yapılabiliyor mu? (Periyot bazlı)", answer: '', explanation: '' },
        { text: "PG grafikleri doğru görüntüleniyor mu?", answer: '', explanation: '' },
        { text: "Hedef değer ile gerçekleşen değer karşılaştırması görüntüleniyor mu?", answer: '', explanation: '' },
        { text: "Form validasyonları çalışıyor mu? (Boş alan kontrolü, sayısal değer kontrolü vb.)", answer: '', explanation: '' },
        { text: "Hata durumlarında anlaşılır hata mesajları gösteriliyor mu?", answer: '', explanation: '' },
        { text: "PG işlemleri mobil cihazlarda düzgün çalışıyor mu?", answer: '', explanation: '' }
    ];

    setCurrentModule('pg', questions);
    initializeModule('pg', 'Performans Göstergesi', questions);
    setInterval(saveProgress, 30000);
})();
