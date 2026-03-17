---
description: Projenin iş mantığını ve veri bütünlüğünü doğrulayan otonom testleri çalıştırır.
---

Bu workflow, sistemin temel iş mantığını (Süreç, PG, Kullanıcı Yetkileri) doğrulamak için hazırlanan otonom test senaryosunu çalıştırır.

#### 1. Test Ortamını Hazırla ve Testi Çalıştır
// turbo
```bash
.venv\Scripts\python.exe tests/otonom_is_mantigi_testi.py
```

#### 2. Sonuçları Değerlendir
- ✅ **OK**: Tüm senaryolar (Süreç ekleme, PG atama, Veri izole etme) başarılıdır.
- ❌ **FAIL**: Hata mesajını analiz et ve ilgili modülü (models/process.py veya models/user.py) kontrol et.
