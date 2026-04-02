# KOKPİTİM PROJESİ: SIFIR HATA (ZERO DEFECT) VE KURUMSAL MÜKEMMELLİK ANALİZİ

**Tarih:** 26 Mart 2026  
**Hazırlayan:** Gemini Advanced Agent (Kıdemli Yazılım Mimarı ve Analist)  
**Sunulan Makam:** Kaptan (Proje Yöneticisi ve Ürün Sahibi)  
**Konu:** Kurumsal Ölçekte Sıfır Hata Hedefine Ulaşmak İçin Derinleştirilmiş Mimari İyileştirme ve Teknik Borç (Technical Debt) Analizi

---

## 1. GİRİŞ VE SIFIR HATA VİZYONU

Kurumsal (Enterprise) düzeyde bir SaaS (Software as a Service) platformu sunma iddiası; sistemin sadece "çalışıyor" olmasını değil, aynı zamanda **ölçeklenebilir, test edilebilir, güvenli ve sürdürülebilir** olmasını gerektirir. "Sıfır Hata" (Zero Defect) hedefi, hataların oluşmasını engellemek amacıyla kod yazım standartlarının, mimari tasarımın ve kalite güvence (QA) süreçlerinin en üst düzeye çıkarılması faaliyetidir.

Bu rapor, daha önceki yüzeysel "İyileştirmeye Açık Alanlar" tespitini alıp, adeta bir neşter yardımıyla projenin en alt katmanlarına kadar inerek detaylandırmaktadır. Projenin ciddi bir potansiyeli olmakla birlikte, aşağıdaki patalojik durumların acilen tedavi edilmesi elzemdir.

---

## 2. KÖK SORUN ODAĞI: TANRI NESNELER (GOD OBJECTS)

Projedeki en büyük teknik borç ve "spaghetti kod" üretim merkezi, boyutları sürdürülebilirlik sınırını çoktan aşmış iki temel yönlendirme dosyasıdır:

1.  **`main/routes.py` (7.624 Satır / 319 KB):** Neredeyse 45 farklı veritabanı modelinin içeriye dahil (import) edildiği, projelerin, süreçlerin, faaliyetlerin, yapay zekanın ve dashboard hesaplamalarının aynı kapta yoğrulduğu devasa bir yapıdır.
2.  **`api/routes.py` (6.119 Satır / 270 KB):** API isteklerini karşılayan bu dosya aynı hastalığa yakalanmıştır.

### ⚠️ Neden Bu Bir Sorundur? (Risk Analizi)
*   **Separation of Concerns (Sorumlulukların Ayrılığı) İhlali:** Controller (Route) katmanı sadece HTTP isteklerini almalı ve Business Logic'e (İş Mantığı Katmanına) devretmelidir. Oysa şu an API'nin içinde (`/surec/<surec_id>/karne/performans` rotasında) matematiksel ağırlıklandırma, başarı puanı hesaplama gibi derin algoritmalar işlenmektedir.
*   **Merge Conflict (Kod Çakışması) Kabusu:** Birden fazla geliştirici projeye dahil olduğunda, bu iki dosya üzerinde sürekli kod çakışmaları (conflict) yaşanacak ve geliştirme hızı (velocity) yerle bir olacaktır.

### 🎯 Kurumsal Çözüm (Domain-Driven Design)
Her iki klasör içindeki rotalar alanlarına (Domain) göre klasörlenmelidir.
`app/api/strategy/`, `app/api/activities/`, `app/api/processes/` gibi alt klasörler açılmalı; hesaplama mantıkları `services/` klasöründeki servislere aktarılmalı ve Controller'lar sadece şu kadar temiz olmalıdır:
```python
@api_bp.route('/karne/performans')
def get_performans():
    return StrategyService.calculate_performance(surec_id=1)
```

---

## 3. GÜVENLİK VE VERİ İZOLASYONU (IDOR VULNERABILITY RİSKİ)

Sistemin "Kurumlar Arası Veri İzolasyonunu (Tenant Isolation)" sağlama yöntemi son derece amatörce ve yüksek risk içerir formattadır.

### ⚠️ Mevcut Durum 
Şu anda rotalarda şu blok yüzlerce kez kopyalanıp yapıştırılmıştır:
```python
if current_user.sistem_rol != 'admin' and surec.kurum_id != current_user.kurum_id:
    return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403
```
Bir insanoğlu (yazılımcı) yeni bir rota eklerken bu 3 satırı unutursa veya yanlış yazarsa; B Kurumunun yöneticisi, A Kurumunun stratejik hedeflerini silebilir, güncelleyebilir veya okuyabilir. Bu, literatürde zafiyetlerin şahı olan **IDOR (Insecure Direct Object Reference)** açığını doğuracaktır. Siber güvenlik denetimlerinde sistem doğrudan sınıfta kalır.

### 🎯 Kurumsal Çözüm (Zorunlu)
Manual izolasyon kontrollerinden derhal vazgeçilmelidir. Bunun yerine:
1.  **Repository Patter / Query Filters:** SQLAlchemy sorguları, otomatik olarak mevcut kullanıcının kurumuna (ve rolüne) göre filtrelenmelidir. Base query override edilerek, bir kurum kullanıcısının başka kurumun objesini çekmesi ORM seviyesinde (SQL düzeyinde) engellenmelidir.
2.  **Dekoratörler:** Tüm kontroller `@require_tenant_access(model=Surec)` gibi merkezi güvenlik dekoratörleri (middleware proxy) ile yapılmalıdır.

---

## 4. MERKEZİ HATA YÖNETİMİ (CENTRALIZED EXCEPTION HANDLING)

Bir projeyi amatörden Enterprise (Kurumsal) seviyeye çıkaran en önemli pratiklerden biri Hata (Exception) yönetimidir.

### ⚠️ Mevcut Durum
Rotalardaki try-except bloklarına bakıldığında hata yakalama standardı şudur:
```python
except Exception as e:
    current_app.logger.error(f'Hata: {e}')
    return jsonify({'success': False, 'message': str(e)}), 500
```
Veritabanı bağlantısı da kopsa, parametre eksikliği de olsa (ValueError), validation error da olsa kullanıcıya sistemdeki Python Exception string'i (`str(e)`) dönülmektedir. Bu, hem güvenlik açığıdır (hata mesajları siber saldırganlara sistem altyapısını belli eder) hem de "Sıfır Hata" felsefesine aykırıdır.

### 🎯 Kurumsal Çözüm
1.  `try-except Exception as e` kullanımına son verilmelidir. Projeye özgü hata sınıfları tanımlanmalıdır:
    *   `class KokpitimValidationError(Exception): ...`
    *   `class AuthorizationError(Exception): ...`
    *   `class ResourceNotFoundError(Exception): ...`
2.  Flask'ın `@app.errorhandler()` yapısı ile merkezi bir hata yakalayıcı (Interceptor) yazılmalı, atılan hatalar merkezde formatlanarak API tarafına standart JSON (Örn: `code: 400`, `message: "Kullanıcı verisi eksik."`), UI tarafına da standart hata sayfaları olarak render edilmelidir.

---

## 5. ÖNYÜZ VE SUNUM KATMANI (FRONTEND DECOUPLING)

Sistem mimari kurallarımız olan "HTML içerisinde Inline Javascript/CSS olmayacak" ve "%100 İngilizce kod standartları" kuralları yeni sayfalarda çalışsa da genel ekosistemde tam oturmamıştır.

### ⚠️ Mevcut Durum
Jinja template'lerinden (Python Backend) Javascript'e veri aktarılırken hala direkt olarak `var myData = {{ data | tojson }};` blokları bulunmaktadır. Bu CSP (Content Security Policy) ihlallerine ve Cross-Site Scripting (XSS) zafiyetlerine davetiye çıkarır.

### 🎯 Kurumsal Çözüm (Sıfır Hata Front-End)
Tüm HTML yapısı tam bağımsız (Decoupled) hale gelmelidir. Backend verileri SADECE `data-xxx` öznitelikleri olarak HTML etiketlerine (tag) yazılmalı, saf `.js` dosyaları `element.dataset.xxx` diyerek bu değerleri okuyup kendi içinde aksiyon almalıdır. Hiçbir şablonda programatik yönlendirme/script entegrasyonu kalmamalıdır.

---

## 6. KALİTE GÜVENCESİ (QA) VE TEST OTOMASYONU

`tests/` dizininde yalnızca `otonom_is_mantigi_testi.py`, `test_services.py` gibi 11 dosya tespit edilmiştir. Neredeyse 15.000 satıra varan kritik business mantığının 11 genel dosya ile test ediliyor olması "Sıfır Hata" felsefesiyle tamamen çelişir.

### 🎯 Kurumsal Çözüm
1.  **Code Coverage (Kod Kapsamı):** `pytest-cov` ile raporlar çekilmeli ve test kapsamı (Coverage) %80'in üzerine çıkarılmalıdır.
2.  **Test Piramidi Kurulumu:** 
    *   *Unit (Birim) Testler:* Servis katmanlarındaki her bir matematiksel hesaplama (karne pıanlamaları vs.) için izole çalışmalıdır.
    *   *Integration (Entegrasyon) Testler:* API uçlarının veritabanıyla doğru konuşup konuşmadığını izlemelidir.
    *   *E2E (Uçtan Uca) Testler:* Playwright veya Selenium ile kritik kullanıcı senaryoları (HGS üzerinden rolden role atlama, süreç ekleme, strateji silme vs.) tarayıcı ortamında simüle edilmelidir.
3.  Geçilen bu zorlu mimariye CI/CD eklenerek, yukarıdaki testleri geçemeyen kodların "Merge" edilmesi git seviyesinde bloke edilmelidir.

---

## 7. SONUÇ VE YENİDEN YAPILANMA (REFACTORING) EYLEM PLANI

"Kurumsal ve Sıfır Hata" vizyonlu bir sistem için Kokpitim'in temelleri (Data modelleri, SaaS çoklu organizasyon altyapısı ve modül derinliği) muazzam derecede iyidir. Sorun veri mimarisinde değil, **iş mantığının (business logic'in) HTTP katmanları arasına güvensizce sıkıştırılmış** olmasındadır.

**Aksiyon Adımları Planı (Sprint Sırası):**
1.  **Mimari Cerahi Müdahale (1-2 Hafta):** `main/routes.py` ve `api/routes.py` parçalanarak `app/routes/` ve `services/` içine dağıtılacak. Controller blokları 50 satırı asla geçmeyecek hale getirilecek.
2.  **Güvenlik Kelepçesi (1 Hafta):** Tüm sorgulara SQLAlchemy tarafında Tenant-Aware (Kurum bazlı) zorunlu filtre enjekte edilecek. IDOR riski kökünden kazınacak.
3.  **Santralizasyon (1 Hafta):** Hatalar merkezde CustomException'lar ile yakalanıp, tarayıcıda tek düze ve zarif bir dille gösterilecek. Loglara tam metin Dökülecek.
4.  **Test Kalkanı:** Otonom test süreçleri ile eski özelliklerin (Regression) kırılmaması sağlanacak.

Kokpitim platformu işlevsel anlamda şampiyonluğa oynayan dev statüsündedir; geriye kalan tek dokunuş bu teknik borç zincirlerinden kurtulmak ve profesyonel mühendislik kalıbına bürünmektir.

*Saygılarımla,*  
**Gemini Advanced Agent**  
*Enterprise System Architect*
