# Statik Dosyaları Yerel Olarak Kullanma

## Sorun
Uygulama CDN'den (Content Delivery Network) Bootstrap, Bootstrap Icons, Font Awesome ve diğer kütüphaneleri yüklüyor. İnternet bağlantısı olmadığında bu dosyalar yüklenemiyor ve stiller/logolar gözükmüyor.

## Çözüm
CDN dosyalarını yerel olarak indirip `static` klasörüne kaydediyoruz. Böylece uygulama internet bağlantısı olmadan da çalışabilir.

## Kurulum Adımları

### 1. İndirme Scriptini Çalıştırın
İnternet bağlantınız varken aşağıdaki komutu çalıştırın:

```bash
python download_static_assets.py
```

Bu script şu dosyaları indirecek:
- Bootstrap CSS ve JS
- Bootstrap Icons CSS ve font dosyaları
- Font Awesome CSS ve font dosyaları
- jQuery
- Chart.js

### 2. Dosyaların Yerleşimi
İndirilen dosyalar şu yapıda olacak:

```
static/
├── vendor/
│   ├── bootstrap/
│   │   ├── bootstrap.min.css
│   │   └── bootstrap.bundle.min.js
│   ├── bootstrap-icons/
│   │   ├── bootstrap-icons.css
│   │   └── fonts/
│   │       └── bootstrap-icons.woff2
│   ├── fontawesome/
│   │   ├── all.min.css
│   │   └── webfonts/
│   │       ├── fa-solid-900.woff2
│   │       ├── fa-regular-400.woff2
│   │       └── fa-brands-400.woff2
│   ├── jquery/
│   │   └── jquery-3.7.1.min.js
│   └── chartjs/
│       └── chart.umd.js
```

### 3. Fallback Mekanizması
`base.html` dosyasında fallback mekanizması eklenmiştir. Eğer yerel dosya bulunamazsa, otomatik olarak CDN'den yüklenmeye çalışılır. Bu sayede:
- İnternet varsa: CDN'den hızlı yükleme
- İnternet yoksa: Yerel dosyalardan yükleme

## Notlar
- Scripti sadece bir kez çalıştırmanız yeterlidir.
- Dosyalar güncellendiğinde scripti tekrar çalıştırabilirsiniz.
- İnternet bağlantısı olmadan scripti çalıştıramazsınız (dosyaları indirmek için internet gerekir).

