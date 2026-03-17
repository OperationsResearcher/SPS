# SQL Server'dan SQLite'a Veri Göçü (Migration) Kılavuzu

Bu kılavuz, mevcut SQL Server veritabanındaki TÜM verileri SQLite'a aktarmak için hazırlanmıştır.

## 📋 Gereksinimler

- Python 3.7+
- Flask uygulaması ve tüm bağımlılıkları yüklü olmalı
- SQL Server'a bağlantı erişimi (mevcut ayarlarla)
- Yeterli disk alanı (veri dump dosyası için)

## 🚀 Kullanım Adımları

### ADIM 0: SQL Server Bağlantı Testi (ÖNEMLİ!)

**Migration işleminden ÖNCE SQL Server bağlantısını test edin:**

```bash
python test_sqlserver_connection.py
```

**Ne yapar:**
- Environment variable'ları kontrol eder
- PyODBC kütüphanesinin yüklü olup olmadığını kontrol eder
- ODBC driver'larını listeler
- SQL Server bağlantısını test eder
- Detaylı hata mesajları gösterir

**Çıktı:**
- Bağlantı başarılı ise: Migration işlemine devam edebilirsiniz
- Bağlantı başarısız ise: Hata nedenleri ve çözüm önerileri gösterilir

**Not:** Bu adımı atlamayın! Bağlantı sorunlarını önceden tespit etmek migration işlemini çok daha sorunsuz hale getirir.

---

### ADIM 1: Veri Dışa Aktarma (Export)

**SQL Server'dan verileri JSON formatında dışa aktarır:**

```bash
python migration_export.py
```

**Ne yapar:**
- Mevcut SQL Server veritabanına bağlanır
- TÜM tablolardaki verileri okur
- Foreign key bağımlılık sırasına göre işler
- `data_dump.json` dosyasına kaydeder
- Tarih alanlarını ISO 8601 formatına çevirir

**Çıktı:**
- `data_dump.json` dosyası oluşturulur
- Konsolda hangi tablodan kaç kayıt çıkarıldığı gösterilir

**Not:** 
- Bu adım sırasında SQL Server bağlantısının çalışır durumda olması gerekir
- Eğer bağlantı hatası alırsanız, önce `test_sqlserver_connection.py` scriptini çalıştırın

---

### ADIM 2: SQLite Veritabanı Oluşturma

**Boş SQLite veritabanı ve tabloları oluşturur:**

```bash
python migration_init.py
```

**Ne yapar:**
- `spsv2.db` adında yeni bir SQLite dosyası oluşturur
- Mevcut `spsv2.db` varsa siler (DİKKAT: Veri kaybı olur!)
- Tüm tabloları oluşturur (schema'yı kurar)
- Tablo listesini konsolda gösterir

**Çıktı:**
- `spsv2.db` dosyası oluşturulur
- Konsolda oluşturulan tablo listesi gösterilir

---

### ADIM 3: Veri İçe Aktarma (Import)

**JSON dosyasındaki verileri SQLite'a yükler:**

```bash
python migration_import.py
```

**Ne yapar:**
- `data_dump.json` dosyasını okur
- Foreign key bağımlılık sırasına göre verileri yükler
- JSON'daki tarih stringlerini Python datetime objesine çevirir
- ID'leri koruyarak verileri ekler
- Her tablo için kaç kayıt yüklendiğini gösterir

**Çıktı:**
- `spsv2.db` dosyasına veriler yüklenir
- Konsolda her tablo için yüklenen kayıt sayısı gösterilir

---

### ADIM 4: Config.py Güncelleme (Otomatik)

**Config.py dosyası zaten güncellenmiştir.** Artık varsayılan olarak SQLite kullanılacaktır.

Eğer manuel kontrol etmek isterseniz:
- `config.py` dosyasında `SQLALCHEMY_DATABASE_URI` ayarını kontrol edin
- SQL Server satırları yorum satırına alınmış olmalı
- SQLite URI aktif olmalı: `sqlite:///spsv2.db`

---

## ⚠️ ÖNEMLİ NOTLAR

1. **Yedekleme:** Migration işleminden ÖNCE mevcut SQL Server veritabanını yedekleyin!

2. **Veri Bütünlüğü:** 
   - Foreign key constraint'leri kontrol edilir
   - ID'ler korunur (çakışma olmaz)
   - Tarih formatları dönüştürülür

3. **Hata Durumu:**
   - Her script hata yönetimi içerir
   - Hata durumunda konsolda detaylı bilgi gösterilir
   - Veritabanı transaction'ları güvenli şekilde yönetilir

4. **Dosya Konumları:**
   - `data_dump.json` → Proje kök dizininde
   - `spsv2.db` → Proje kök dizininde
   - Scriptler → Proje kök dizininde

5. **Test:**
   - Migration sonrası uygulamayı başlatın
   - Verilerin doğru yüklendiğini kontrol edin
   - Kritik işlemleri test edin

---

## 🔍 Sorun Giderme

### "SQL Server bağlantı hatası"

**İlk adım:** `test_sqlserver_connection.py` scriptini çalıştırın:
```bash
python test_sqlserver_connection.py
```

**Olası nedenler ve çözümler:**

1. **Environment variable'lar set edilmemiş:**
   ```bash
   # Windows PowerShell
   $env:SQL_SERVER="localhost"
   $env:SQL_DATABASE="stratejik_planlama"
   $env:SQL_USERNAME="sa"
   $env:SQL_PASSWORD="your_password"
   $env:SQL_DRIVER="ODBC Driver 17 for SQL Server"
   
   # Windows CMD
   set SQL_SERVER=localhost
   set SQL_DATABASE=stratejik_planlama
   set SQL_USERNAME=sa
   set SQL_PASSWORD=your_password
   set SQL_DRIVER=ODBC Driver 17 for SQL Server
   ```

2. **PyODBC yüklü değil:**
   ```bash
   pip install pyodbc>=5.0.0
   ```

3. **ODBC Driver yüklü değil:**
   - ODBC Driver 17 for SQL Server indirin ve yükleyin
   - https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

4. **SQL Server çalışmıyor:**
   - SQL Server servisinin çalıştığından emin olun
   - Windows'ta: Services.msc'den SQL Server servisini kontrol edin

5. **Firewall/Network sorunu:**
   - SQL Server portunun (varsayılan 1433) açık olduğundan emin olun
   - Firewall ayarlarını kontrol edin

6. **Yanlış sunucu adı/port:**
   - LocalDB kullanıyorsanız: `(localdb)\MSSQLLocalDB`
   - Named instance kullanıyorsanız: `server\instance`
   - Port belirtmek için: `server,port` (örn: `localhost,1433`)

### "JSON dosyası bulunamadı"
- Önce `migration_export.py`'yi çalıştırdığınızdan emin olun
- `data_dump.json` dosyasının proje kök dizininde olduğunu kontrol edin

### "SQLite DB bulunamadı"
- Önce `migration_init.py`'yi çalıştırdığınızdan emin olun
- `spsv2.db` dosyasının proje kök dizininde olduğunu kontrol edin

### "Foreign key constraint hatası"
- Veriler doğru sırada yüklenmeli (export_order'a göre)
- Eğer hata devam ederse, ilgili tablodaki foreign key'leri kontrol edin

### "Import sırasında veri kaybı"
- Her tablo için konsolda yüklenen kayıt sayısını kontrol edin
- Export sırasındaki kayıt sayısıyla import sırasındaki sayıyı karşılaştırın

---

## 📊 Migration Sonrası Kontrol Listesi

- [ ] `spsv2.db` dosyası oluşturuldu
- [ ] `data_dump.json` dosyası mevcut
- [ ] Uygulama SQLite'a bağlanıyor
- [ ] Kullanıcılar giriş yapabiliyor
- [ ] Projeler görüntülenebiliyor
- [ ] Görevler listelenebiliyor
- [ ] Süreçler ve performans göstergeleri çalışıyor
- [ ] İlişkiler (foreign key'ler) doğru çalışıyor

---

## 🔄 Geri Dönüş (Rollback)

Eğer migration'dan sonra SQL Server'a geri dönmek isterseniz:

1. `config.py` dosyasında SQL Server satırlarının yorumunu kaldırın
2. SQLite satırını yorum satırına alın
3. Uygulamayı yeniden başlatın

**Not:** Bu işlem sadece config değişikliği yapar, veriler SQL Server'da kalır (eğer silmediyseniz).

---

## 📞 Destek

Sorun yaşarsanız:
1. Konsol çıktısını kontrol edin
2. `data_dump.json` dosyasının boyutunu kontrol edin (boş olmamalı)
3. `spsv2.db` dosyasının boyutunu kontrol edin (0 byte olmamalı)
4. Hata mesajlarını not edin ve log dosyalarını kontrol edin

---

**Son Güncelleme:** 2025-01-XX  
**Versiyon:** 1.0


