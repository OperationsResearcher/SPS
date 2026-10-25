
## Dashboard Veri Kaynağı Analizi

### 1. Backend Analizi (`main/routes.py`)
- **Fonksiyon:** `@main_bp.route('/dashboard')`
- **Veri Kaynağı:** `Activity` modeli kullanılıyor.
    - `Task` (Proje Görevi) modeli **kullanılmıyor**.
    - Veriler `db_activities = Activity.query...` ile çekiliyor.
- **Hesaplama Mantığı:**
    - **Kritik İşler:** `Activity` tablosunda `priority='High'` ve statüsü Tamamlandı/Kapalı olmayanlar.
    - **Toplam Yük:** `Activity` tablosundaki toplam kayıt sayısı.
    - **Tamamlanan:** `Activity` tablosunda `status='Tamamlandı'` olanlar.
    - **Değişken:** Template'e `stats` sözlüğü içinde `critical_tasks`, `total_tasks` vb. gönderiliyor.

### 2. Frontend Analizi (`templates/dashboard_v2.html`)
- **Durum:** Veriler dinamik olarak bağlanmış, hardcoded (elle yazılmış) değil.
- **Kullanılan Değişkenler:**
    - `{{ stats.critical_tasks or 0 }}`
    - `{{ stats.total_tasks or 0 }}`
    - `{{ stats.completed_tasks or 0 }}`
- **Görsel:** "Özet Kartları" bölümünde bu değişkenler gösteriliyor.

### 3. Veri Modeli Analizi
- **Kullanılan Model:** `Activity` (models/__init__.py içinde tanımlı)
    - Alanlar: `priority`, `status`, `subject`, `project_id`.
    - Amaç: Redmine, Jira ve Dahili sistemlerden gelen aktivitelerin toplandığı havuz.
- **Mevcut Diğer Model:** `Task` (models/project.py içinde tanımlı)
    - Bu model aslında projenin gerçek görevlerini tutuyor ancak şu an dashboard bu tabloyu **sorgulamıyor**.

### Sonuç ve Öneri
Dashboard şu anda sadece `Activity` tablosuna bakıyor. Eğer Proje Yönetimi modülündeki (`Task` tablosu) gerçek görevlerin burada görünmesini istiyorsanız, ya `Task` kayıtları `Activity` tablosuna otomatik kopyalanmalı ya da Dashboard sorgusu hem `Task` hem `Activity` tablolarını kapsayacak şekilde güncellenmelidir.


## Karar Destek Kartı Analizi

### 1. Frontend Tespiti (`templates/dashboard_v2.html`)
- **Konum:** "Karar Destek Özeti" başlıklı kart (Satır ~124).
- **Durum:** Yarı-Dinamik. Sabit metinler içine yerleştirilmiş `stats` değişkenlerini kullanıyor.
- **İçerik:**
  - **Yöneticiler için:** Kritik iş sayısı, Açık toplam iş sayısı, Performans skoru.
  - **Çalışanlar için:** "Bugünkü öncelik: Kritik işleri tamamla" (Statik metin), Devam eden görevler, Tamamlanan görevler.
- **Eksik:** Gerçek bir "öneri" veya "analiz" metni yok. Sadece sayısal özet sunuluyor.

### 2. Backend Tespiti (`main/routes.py`)
- **Veri Kaynağı:** Kartın içeriği, genel dashboard istatistikleri (`stats` sözlüğü) üzerinden besleniyor.
- **Mantık:**
  - Özel bir "Karar Destek" algoritması bulunmuyor.
  - Veriler, `Activity` ve (yeni eklenen) `Task` tablolarından gelen sayısal toplamların basit işlemlerle (çıkarma, vb.) gösterilmesinden ibaret.
  - Örn: `Açık İş = Toplam - Tamamlanan`.

### 3. Tespit Edilen Eksiklikler
- **Basitlik:** Kartın adı "Karar Destek" olsa da, şu an sadece bir "Durum Özeti" işlevi görüyor.
- **Statik Öneriler:** Kullanıcıya "Şu projeye odaklanın", "Gecikme riski var" gibi duruma özel dinamik metinler üretilmiyor.
- **Veri Tekrarı:** Üstteki renkli kartlarda (Kritik İşler, Toplam Yük) zaten var olan sayılar burada liste halinde tekrar ediliyor.

### Öneri
Bu alanın gerçek bir "Karar Destek" modülüne dönüşmesi için, backend tarafında verileri analiz edip *string* formatında öneriler üreten bir servis (örn: `DecisionSupportService`) entegre edilmelidir.


## Dashboard Veri Kapsamı Analizi

### 1. Filtre Kontrolü
- **Mevcut Durum:**
    - `db_activities = Activity.query.options(joinedload(Activity.project)).all()`
    - `db_tasks = Task.query.filter(Task.is_archived == False).all()`
    - **Sonuç:** Hiçbir kullanıcı veya kurum filtresi **YOK**.

### 2. Risk Analizi
- **Risk Seviyesi:** 🔴 **YÜKSEK (CRITICAL)**
- **Açıklama:**
    - Şu an sisteme giren HERHANGİ bir kullanıcı, sadece kendi görevlerini değil, **TÜM KURUMLARIN** ve **TÜM KULLANICILARIN** görevlerini/aktivitelerini dashboard'da görmektedir.
    - Özellikle `Activity` ve `Task` modelleri, çoklu kiracı (multi-tenant) yapısına göre filtrelenmemiştir.
    - Örneğin A Kurumu çalışanı, B Kurumunun kritik stratejik planlarını ve görevlerini sayısal olarak görebilir (toplam sayıları).
    - Kodda açıkça `# TODO: İlerde kullanıcı bazlı filtreleme eklenebilir` şeklinde bir not düşülmüş, ancak bu güvenlik açığı oluşturuyor.

### 3. Kod Kanıtı
`main/routes.py` (227. ve 232. satırlar):
```python
# 1. Activity tablosundan veriler
db_activities = Activity.query.options(joinedload(Activity.project)).all() # FİLTRE YOK

# 2. Task (Proje Görevleri) tablosundan veriler
db_tasks = Task.query.filter(Task.is_archived == False).all() # SADECE ARŞİV KONTROLÜ VAR
```

### Öneri
Acilen şu filtrelerin eklenmesi gerekmektedir:
1. **Kurum Filtresi:** `User.kurum_id`'ye göre sadece o kuruma ait proje/task/aktiviteler çekilmeli.
2. **Kişisel Filtre (Opsiyonel):** Rol tabanlı olarak, normal kullanıcılar sadece kendilerine atananları görmeli.
