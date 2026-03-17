/* Süreç Yönetimi Modülü QA Soruları */

(function() {
    const questions = [
        { text: "Süreç paneli sayfasına erişim doğru yetki kontrolü ile yapılıyor mu?", answer: '', explanation: '' },
        { text: "Yeni süreç ekleme butonu görünüyor ve çalışıyor mu?", answer: '', explanation: '' },
        { text: "Süreç ekleme formunda zorunlu alanlar (ad, kurum) belirtilmiş mi?", answer: '', explanation: '' },
        { text: "Süreç kodu (code) alanı doldurulabiliyor mu? (Örn: SR1, SR2)", answer: '', explanation: '' },
        { text: "Süreç adı (ad) alanı doldurulabiliyor mu?", answer: '', explanation: '' },
        { text: "Doküman numarası ve revizyon bilgileri girilebiliyor mu?", answer: '', explanation: '' },
        { text: "Süreç başlangıç ve bitiş tarihleri seçilebiliyor mu?", answer: '', explanation: '' },
        { text: "Süreç başlangıç ve bitiş sınırları (boundaries) açıklama alanları doldurulabiliyor mu?", answer: '', explanation: '' },
        { text: "Süreç durumu (Aktif/Pasif) seçilebiliyor mu?", answer: '', explanation: '' },
        { text: "Süreç lideri atama işlemi çalışıyor mu? (Çoklu lider seçimi)", answer: '', explanation: '' },
        { text: "Süreç üyesi atama işlemi çalışıyor mu? (Çoklu üye seçimi)", answer: '', explanation: '' },
        { text: "Süreç sahibi (process owner) atama işlemi çalışıyor mu?", answer: '', explanation: '' },
        { text: "Alt strateji ilişkilendirme işlemi çalışıyor mu? (Süreç-strateji bağlantısı)", answer: '', explanation: '' },
        { text: "Süreç ağırlığı (weight) ayarlanabiliyor mu?", answer: '', explanation: '' },
        { text: "Süreç ekleme işlemi başarıyla tamamlandığında onay mesajı gösteriliyor mu?", answer: '', explanation: '' },
        { text: "Süreç listesi düzgün görüntüleniyor mu? (Kod, ad, durum, lider bilgileri)", answer: '', explanation: '' },
        { text: "Süreç düzenleme butonu tıklanabilir ve form açılıyor mu?", answer: '', explanation: '' },
        { text: "Süreç düzenleme formunda mevcut süreç bilgileri doğru şekilde yükleniyor mu?", answer: '', explanation: '' },
        { text: "Süreç düzenleme işlemi başarıyla kaydediliyor ve liste güncelleniyor mu?", answer: '', explanation: '' },
        { text: "Süreç silme butonu görünüyor mu? (Yetki kontrolü ile)", answer: '', explanation: '' },
        { text: "Süreç silme işleminde onay mesajı gösteriliyor mu?", answer: '', explanation: '' },
        { text: "Süreç silme işlemi başarıyla tamamlanıyor ve listeden kaldırılıyor mu?", answer: '', explanation: '' },
        { text: "Süreç detay sayfasında tüm bilgiler görüntüleniyor mu?", answer: '', explanation: '' },
        { text: "Süreç listesinde filtreleme/arama özelliği varsa çalışıyor mu?", answer: '', explanation: '' },
        { text: "Süreç ilerleme durumu (progress) görüntülenebiliyor ve güncellenebiliyor mu?", answer: '', explanation: '' },
        { text: "Form validasyonları çalışıyor mu? (Boş alan kontrolü, tarih kontrolü vb.)", answer: '', explanation: '' },
        { text: "Hata durumlarında (örn: lider seçilmedi) anlaşılır hata mesajları gösteriliyor mu?", answer: '', explanation: '' },
        { text: "Süreç işlemleri mobil cihazlarda düzgün çalışıyor mu?", answer: '', explanation: '' }
    ];

    setCurrentModule('surec', questions);
    initializeModule('surec', 'Süreç Yönetimi', questions);
    setInterval(saveProgress, 30000);
})();
