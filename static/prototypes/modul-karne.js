/* Süreç Karnesi Modülü QA Soruları */

(function() {
    const questions = [
        { text: "Süreç karnesi sayfasına erişim doğru yetki kontrolü ile yapılıyor mu? (Kullanıcı sadece kendi süreçlerini görmeli)", answer: '', explanation: '' },
        { text: "Süreç seçimi dropdown/select listesi düzgün çalışıyor mu?", answer: '', explanation: '' },
        { text: "Süreç seçildiğinde PG listesi yükleniyor mu?", answer: '', explanation: '' },
        { text: "Yıl seçimi yapılabiliyor mu?", answer: '', explanation: '' },
        { text: "Periyot seçimi (Günlük, Haftalık, Aylık, Çeyreklik, Yıllık) yapılabiliyor mu?", answer: '', explanation: '' },
        { text: "PG veri girişi formu açılıyor mu? (Veri giriş butonu)", answer: '', explanation: '' },
        { text: "Veri girişi formunda tüm alanlar (tarih, değer, açıklama) doldurulabiliyor mu?", answer: '', explanation: '' },
        { text: "Veri girişi kaydetme işlemi başarıyla tamamlanıyor mu?", answer: '', explanation: '' },
        { text: "Kaydedilen veriler tabloda görüntüleniyor mu?", answer: '', explanation: '' },
        { text: "Veri düzenleme işlemi çalışıyor mu?", answer: '', explanation: '' },
        { text: "Veri silme işlemi çalışıyor ve onay mesajı gösteriliyor mu?", answer: '', explanation: '' },
        { text: "PG grafikleri doğru verilerle çiziliyor mu?", answer: '', explanation: '' },
        { text: "Hedef değer çizgisi grafikte görüntüleniyor mu?", answer: '', explanation: '' },
        { text: "Faaliyet ekleme butonu görünüyor ve çalışıyor mu?", answer: '', explanation: '' },
        { text: "Faaliyet ekleme formunda zorunlu alanlar belirtilmiş mi?", answer: '', explanation: '' },
        { text: "Faaliyet ekleme işlemi başarıyla tamamlanıyor mu?", answer: '', explanation: '' },
        { text: "Faaliyet listesi görüntüleniyor mu?", answer: '', explanation: '' },
        { text: "Faaliyet düzenleme işlemi çalışıyor mu?", answer: '', explanation: '' },
        { text: "Faaliyet silme işlemi çalışıyor ve onay mesajı gösteriliyor mu?", answer: '', explanation: '' },
        { text: "Excel export butonu görünüyor ve çalışıyor mu?", answer: '', explanation: '' },
        { text: "Excel export işlemi başarıyla tamamlanıyor ve dosya indiriliyor mu?", answer: '', explanation: '' },
        { text: "Export edilen Excel dosyasında tüm veriler doğru formatta mı?", answer: '', explanation: '' },
        { text: "Toplu veri girişi özelliği varsa çalışıyor mu?", answer: '', explanation: '' },
        { text: "Veri giriş sihirbazı (VGS) adım adım çalışıyor mu?", answer: '', explanation: '' },
        { text: "Hesaplama yöntemine göre (Ortalama, Toplam vb.) değerler doğru hesaplanıyor mu?", answer: '', explanation: '' },
        { text: "Form validasyonları çalışıyor mu? (Tarih kontrolü, sayısal değer kontrolü vb.)", answer: '', explanation: '' },
        { text: "Hata durumlarında anlaşılır hata mesajları gösteriliyor mu?", answer: '', explanation: '' },
        { text: "Süreç karnesi sayfası mobil cihazlarda düzgün çalışıyor mu?", answer: '', explanation: '' }
    ];

    setCurrentModule('karne', questions);
    initializeModule('karne', 'Süreç Karnesi', questions);
    setInterval(saveProgress, 30000);
})();
