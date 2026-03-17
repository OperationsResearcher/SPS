# Kokpitim Projesi (Greenfield) – Proje Anayasası ve Çalışma Standartları

## ⚠️ PORT 5001 (KRİTİK)
**Kokpitim uygulaması her zaman port 5001 üzerinden çalışır.** `run.py` port=5001 kullanır. Sunucu başlatırken, test ederken veya URL örneği verirken MUTLAKA `http://127.0.0.1:5001` veya `localhost:5001` kullanılacaktır. Port 5000 YANLIŞTIR.

## 0. 🚨 GÖRSEL DOĞRULAMA VE RAPORLAMA (P0 - EN YÜKSEK ÖNCELİK)
Cursor (Agent), bir görevi bitirdiğinde sadece terminal loglarına bakma. Chrome Uzantısı ile sayfayı aç, F12 konsolunu kontrol et. Kırmızı bir hata (`Uncaught SyntaxError` veya `500 Error`) varsa kendin düzelt.
Raporlarını daima şu cümleyle bitir: **"✅ Sayfa tarayıcıda açıldı, konsol hatası taranmadı ve görsel olarak doğrulandı."**

## 1. DİL VE İSİMLENDİRME STANDARTLARI (YENİ MİMARİ KURAL)
- **Kodlar %100 İngilizce:** Veritabanı tabloları, sütunları, değişkenler, fonksiyon isimleri, dosya isimleri ve rotalar KESİNLİKLE İngilizce olacaktır.
- **Standartlar:**
  - Değişken, Fonksiyon, Dosya ve Rota isimleri: `snake_case` (Örn: `strategic_goals`, `get_user_data()`, `/api/strategy/swot`)
  - Veritabanı Sınıfları (Modeller): `PascalCase` (Örn: `SystemComponent`, `SubscriptionPackage`)
- **Arayüz (UI) %100 Türkçe:** Sadece kullanıcının ekranda gördüğü HTML metinleri, SweetAlert mesajları ve Flash mesajları Türkçe, kurumsal ve profesyonel bir dille yazılacaktır.

## 2. 🏗️ KATI KATMAN AYRIMI (NO INLINE JS/CSS)
- **HTML dosyaları (.html) içinde KESİNLİKLE `<script>` veya `<style>` etiketleri (blokları) bulunamaz.**
- Tüm JavaScript (`static/js/`) ve CSS (`static/css/`) dosyaları harici olmalıdır.
- Backend'den JavaScript'e veri aktarımı SADECE HTML elementlerinin `data-*` öznitelikleri üzerinden veya zorunlu hallerde HTML içindeki 10 satırı geçmeyen `window.CONFIG` objesi ile yapılacaktır.
- Harici `.js` dosyalarında Jinja2 sözdizimi (`{{ }}`) KESİNLİKLE kullanılamaz.

## 3. MİMARİ VE GÖÇ (MIGRATION) KURALLARI
- **Eski Proje İzolasyonu:** `eski_proje_referans` klasöründeki kodlar SADECE referans amaçlıdır. Oradan yeni projeye doğrudan Python `import` işlemi YAPILAMAZ. Kodlar İngilizce standartlara çevrilerek yeni klasörlere (`app/routes/`, `app/models/`) adapte edilmelidir.
- **SaaS Hiyerarşisi:** Sistem mimarisi "Paket -> Modül -> Bileşen" (Package -> Module -> Component) hiyerarşisine dayanır. Yetkilendirme kontrolleri daima bu zincire göre yapılmalıdır.
- **Blueprint Disiplini:** `app.py` asla şişirilemez. Her yeni özellik kendi modülünün Blueprint'i altına yazılmalı ve `app/routes/__init__.py` üzerinden merkezi olarak kaydedilmelidir.

## 4. UI/UX VE GÜVENLİK STANDARTLARI
- **SweetAlert2:** Tüm bildirimler ve onay pencereleri için tarayıcı varsayılanları (`alert`, `confirm`) yasaktır; sadece SweetAlert2 kullanılacaktır.
- **Hard Delete Yasak:** Veritabanından hiçbir veri kalıcı olarak silinemez. Daima `is_active=False` veya `is_deleted=True` mantığı kullanılmalıdır.
- **Yetkilendirme:** Sisteme giriş yapmadan erişilmemesi gereken tüm rotalar `@login_required` ile korunmalıdır. Modül yetkisi gerektiren rotalarda `@require_component` kullanılmalıdır.