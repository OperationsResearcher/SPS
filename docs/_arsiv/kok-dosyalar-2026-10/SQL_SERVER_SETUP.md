# SQL Server Bağlantı Kurulumu

## 1. .env Dosyası Oluşturma

Proje kök klasöründe (SP_Code) `.env` dosyası oluşturun ve aşağıdaki bilgileri doldurun:

```env
# SQL Server Bağlantı Bilgileri
SQL_SERVER=localhost
SQL_DATABASE=stratejik_planlama
SQL_USERNAME=sa
SQL_PASSWORD=your_password_here
SQL_DRIVER=ODBC Driver 17 for SQL Server

# Alternatif: Windows Authentication kullanmak için
# SQL_SERVER=localhost
# SQL_DATABASE=stratejik_planlama
# SQL_USERNAME=
# SQL_PASSWORD=
# SQL_DRIVER=ODBC Driver 17 for SQL Server

# Flask Environment
FLASK_ENV=development

# Secret Key
SECRET_KEY=your-secret-key-here-change-in-production
```

## 2. SQL Server Bağlantı Seçenekleri

### Seçenek A: SQL Server Authentication
```env
SQL_SERVER=localhost
SQL_DATABASE=stratejik_planlama
SQL_USERNAME=sa
SQL_PASSWORD=your_password
SQL_DRIVER=ODBC Driver 17 for SQL Server
```

### Seçenek B: Windows Authentication (Trusted Connection)
```env
SQL_SERVER=localhost
SQL_DATABASE=stratejik_planlama
SQL_USERNAME=
SQL_PASSWORD=
SQL_DRIVER=ODBC Driver 17 for SQL Server
```

### Seçenek C: Direkt Connection String
```env
DATABASE_URL=mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server
```

## 3. Veritabanı Oluşturma

SQL Server Management Studio (SSMS) veya SQL Server komut satırı ile veritabanını oluşturun:

```sql
CREATE DATABASE stratejik_planlama;
```

## 4. Bağlantıyı Test Etme

`.env` dosyasını oluşturduktan sonra:

```bash
.venv\Scripts\python.exe test_sqlserver_connection.py
```

Bu script:
- Environment variable'ları kontrol eder
- SQL Server bağlantısını test eder
- Tabloların varlığını kontrol eder
- Veri sayılarını gösterir

## 5. Şema Oluşturma

Eğer SQL Server'da tablolar yoksa:

```bash
.venv\Scripts\python.exe init_database.py
```

Bu script tüm tabloları SQL Server'da oluşturur.

## 6. Veri Transferi

Eğer veriler yoksa:

```bash
.venv\Scripts\python.exe transfer_v2_data.py
```

Bu script V2 SQLite veritabanından SQL Server'a veri aktarır.

## Notlar

- `.env` dosyası `.gitignore` içinde olmalıdır (güvenlik için)
- SQL Server'ın çalıştığından emin olun
- ODBC Driver 17 for SQL Server'ın yüklü olduğundan emin olun
- Windows Authentication kullanıyorsanız, SQL Server'ın Windows Authentication'ı desteklediğinden emin olun

