# PG ve veri girişi raporu

*Oluşturulma: 2026-03-23 12:19:30*
*Kaynak: instance/kokpitim.db*

Bu rapor **aktif** (`is_active = 1`) kurum, süreç, PG ve veri satırlarını sayar. `kpi_data` için silinmemiş kayıtlar (`is_active = 1`) dikkate alınır.

## 1. Aktif kurumlar (`tenants`)

| ID | Kısa ad | Ad |
|---:|---|---|
| 3 | ASG | Anadolu Sağlık Grubu |
| 7 | BOUN | Boğaziçi Üniversitesi |
| 1 | default_corp | Default Corp |
| 6 | Deneme A.Ş. | Deneme |
| 10 | Deneme | Deneme Danışmanlık |
| 17 | Belediye | EBB |
| 13 | EcoDoga | EcoDoğa Geri Dönüşüm ve Enerji A.Ş. |
| 4 | EGE-TECH | Ege Teknoloji A.Ş. |
| 16 | KMF | Kayseri Model Fabrika |
| 9 | 1KMF | KMF Yonetim Danismanligi |
| 5 | MEV | Marmara Eğitim Vakfı |
| 12 | MegaYapi | Mega Yapı ve İnşaat Sanayi Tic. Ltd. |
| 8 | Sistem | Sistem Ynt |
| 11 | TechNova | TechNova Bilişim Çözümleri A.Ş. |
| 15 | TechNova Solutions | TechNova Bilişim Çözümleri A.Ş. |
| 14 | TestAS | Test A.Ş. |
| 2 | TK | Test Kurum |

## 2. Kurum başına süreç sayısı

| Kurum ID | Kurum | Süreç adedi |
|---:|---|---:|
| 3 | Anadolu Sağlık Grubu | 5 |
| 7 | Boğaziçi Üniversitesi | 1 |
| 1 | Default Corp | 2 |
| 6 | Deneme | 0 |
| 10 | Deneme Danışmanlık | 1 |
| 17 | EBB | 0 |
| 13 | EcoDoğa Geri Dönüşüm ve Enerji A.Ş. | 0 |
| 4 | Ege Teknoloji A.Ş. | 5 |
| 16 | Kayseri Model Fabrika | 11 |
| 9 | KMF Yonetim Danismanligi | 10 |
| 5 | Marmara Eğitim Vakfı | 5 |
| 12 | Mega Yapı ve İnşaat Sanayi Tic. Ltd. | 0 |
| 8 | Sistem Ynt | 0 |
| 11 | TechNova Bilişim Çözümleri A.Ş. | 12 |
| 15 | TechNova Bilişim Çözümleri A.Ş. | 3 |
| 14 | Test A.Ş. | 1 |
| 2 | Test Kurum | 0 |

## 3. Süreç başına PG sayısı (`process_kpis`)

### Anadolu Sağlık Grubu *(kurum id: 3)*

| Süreç ID | Kod | Süreç adı | PG sayısı |
|---:|---|---|---:|
| 3 | SR-01 | Hasta Kabul ve Kayıt Süreci | 1 |
| 4 | SR-02 | Tanı ve Tedavi Planlama | 4 |
| 5 | SR-03 | İlaç ve Malzeme Yönetimi | 3 |
| 6 | SR-04 | Hasta Güvenliği ve Kalite | 6 |
| 7 | SR-05 | Faturalandırma ve Tahsilat | 1 |

### Boğaziçi Üniversitesi *(kurum id: 7)*

| Süreç ID | Kod | Süreç adı | PG sayısı |
|---:|---|---|---:|
| 26 | SR1 | PAZARLAMA STRATEJİLERİ YÖNETİMİ SÜREÇ KARNESİ | 3 |

### Default Corp *(kurum id: 1)*

| Süreç ID | Kod | Süreç adı | PG sayısı |
|---:|---|---|---:|
| 1 | HR-01 | İnsan Kaynakları Yönetimi | 0 |
| 2 | IT-01 | Bilgi İşlem ve Altyapı | 0 |

### Deneme Danışmanlık *(kurum id: 10)*

| Süreç ID | Kod | Süreç adı | PG sayısı |
|---:|---|---|---:|
| 38 | — | Süreç1 | 1 |

### Ege Teknoloji A.Ş. *(kurum id: 4)*

| Süreç ID | Kod | Süreç adı | PG sayısı |
|---:|---|---|---:|
| 8 | SR-01 | Yazılım Geliştirme Yaşam Döngüsü | 7 |
| 9 | SR-02 | Müşteri Destek ve Servis | 3 |
| 10 | SR-03 | Altyapı ve Operasyon Yönetimi | 1 |
| 11 | SR-04 | Satış ve İş Geliştirme | 4 |
| 12 | SR-05 | Proje Yönetimi ve Teslimat | 7 |

### Kayseri Model Fabrika *(kurum id: 16)*

| Süreç ID | Kod | Süreç adı | PG sayısı |
|---:|---|---|---:|
| 54 | — | SR1 - ŞİRKET ORGANLARI YÖNETİMİ SÜRECİ | 5 |
| 63 | — | SR10 - TEDARİK YÖNETİMİ SÜREÇ KARNESİ | 4 |
| 64 | — | SR11 - MAKİNA, TEKNOLOJİ VE BİLGİ YÖNETİMİ SÜREÇ KARNESİ | 6 |
| 55 | — | SR2 - STRATEJİK PLANLAMA YÖNETİMİ SÜREÇ KARNESİ | 9 |
| 56 | — | SR3 - KURUM İMAJI VE KÜLTÜRÜ YÖNETİM SÜRECİ | 11 |
| 57 | — | SR4 - PAZARLAMA STRATEJİLERİ YÖNETİM SÜRECİ | 21 |
| 58 | — | SR5 - EĞİTİM HİZMETLERİ YÖNETİMİ SÜREÇ KARNESİ | 6 |
| 59 | — | SR6 - DANIŞMANLIK HİZMETLERİ YÖNETİMİ  SÜREÇ KARNESİ | 1 |
| 60 | — | SR7 - BAŞARILARI TANIMA VE ÖDÜLLENDİRME YÖNETİMİ SÜREÇ KARNESİ | 6 |
| 61 | — | SR8 - İNSAN KAYNAKLARI YÖNETİMİ SÜREÇ KARNESİ | 5 |
| 62 | — | SR9 - MALİ İŞLER YÖNETİMİ SÜREÇ KARNESİ | 9 |

### KMF Yonetim Danismanligi *(kurum id: 9)*

| Süreç ID | Kod | Süreç adı | PG sayısı |
|---:|---|---|---:|
| 36 | SR10 | Tedarik Yönetim Süreci | 0 |
| 37 | SR11 | Makine, Teknoloji ve Bilgi Yönetim Süreci | 0 |
| 28 | SR2 | Stratejik Planlama Süreci | 2 |
| 29 | SR3 | Kurum İmajı ve Kültürü Yönetme Süreci | 0 |
| 30 | SR4 | Pazarlama Stratejileri Yönetim Süreci | 35 |
| 31 | SR5 | Eğitim Hizmetleri Yönetim Süreci (Ücretli veya Gönüllü) | 0 |
| 32 | SR6 | Danışmanlık Hizmetleri Yönetim Süreci | 17 |
| 33 | SR7 | Başarıları Tanıma ve Ödüllendirme Süreci | 0 |
| 34 | SR8 | İnsan Kaynakları Yönetim Süreci | 0 |
| 35 | SR9 | Mali İşler Yönetim Süreci | 0 |

### Marmara Eğitim Vakfı *(kurum id: 5)*

| Süreç ID | Kod | Süreç adı | PG sayısı |
|---:|---|---|---:|
| 13 | SR-01 | Öğrenci Kayıt ve Kabul | 1 |
| 14 | SR-02 | Müfredat Planlama ve Uygulama | 5 |
| 15 | SR-03 | Öğretmen İşe Alım ve Gelişim | 8 |
| 16 | SR-04 | Veli İletişim ve Memnuniyet | 9 |
| 17 | SR-05 | Tesis ve Lojistik Yönetimi | 7 |

### TechNova Bilişim Çözümleri A.Ş. *(kurum id: 11)*

| Süreç ID | Kod | Süreç adı | PG sayısı |
|---:|---|---|---:|
| 44 | SR01 | Yazılım Geliştirme | 10 |
| 45 | SR02 | Müşteri Deneyimi | 10 |
| 46 | SR03 | İnsan Kaynakları | 10 |
| 47 | SR04 | Finans Yönetimi | 10 |
| 48 | SR05 | Satış & Pazarlama | 10 |
| 49 | SR06 | AR-GE | 10 |
| 50 | SR07 | BT Altyapı | 10 |
| 51 | SR08 | Kalite Yönetimi | 10 |
| 52 | SR09 | Lojistik | 10 |
| 53 | SR10 | Hukuk & Uyum | 10 |
| 40 | — | Müşteri Destek | 1 |
| 39 | — | Yazılım Geliştirme | 1 |

### TechNova Bilişim Çözümleri A.Ş. *(kurum id: 15)*

| Süreç ID | Kod | Süreç adı | PG sayısı |
|---:|---|---|---:|
| 41 | SR-01 | Yazılım Geliştirme | 2 |
| 42 | SR-02 | Müşteri Başarısı | 2 |
| 43 | SR-03 | İnsan Kaynakları | 2 |

### Test A.Ş. *(kurum id: 14)*

| Süreç ID | Kod | Süreç adı | PG sayısı |
|---:|---|---|---:|
| 27 | SR1 | Şirket Organları Yönetimi Süreci | 1 |

## 4. PG başına veri girişi sayısı (`kpi_data`)

### Anadolu Sağlık Grubu *(kurum id: 3)*
#### Süreç: Hasta Kabul ve Kayıt Süreci *(id 3, kod: SR-01)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 4 | PG-0101 | Ortalama Hasta Bekleme Süresi | 55 |

#### Süreç: Tanı ve Tedavi Planlama *(id 4, kod: SR-02)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 5 | PG-0201 | Sigorta Tahsilat Süresi | 42 |
| 6 | PG-0202 | Randevu İptal Edilme Oranı | 72 |
| 7 | PG-0203 | Ortalama Hasta Bekleme Süresi | 60 |
| 8 | PG-0204 | Taburcu Sonrası Readmisyon Oranı | 63 |

#### Süreç: İlaç ve Malzeme Yönetimi *(id 5, kod: SR-03)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 9 | PG-0301 | Hasta Memnuniyet Skoru | 81 |
| 10 | PG-0302 | Ameliyathane Doluluk Oranı | 65 |
| 11 | PG-0303 | Sağlık Personeli Devir Oranı | 50 |

#### Süreç: Hasta Güvenliği ve Kalite *(id 6, kod: SR-04)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 12 | PG-0401 | Tıbbi Hata Raporu Sayısı | 50 |
| 13 | PG-0402 | Hasta Memnuniyet Skoru | 56 |
| 14 | PG-0403 | Enfeksiyon Oranı (1000 Hasta/Gün) | 55 |
| 15 | PG-0404 | Sigorta Tahsilat Süresi | 79 |
| 16 | PG-0405 | Randevu İptal Edilme Oranı | 70 |
| 17 | PG-0406 | Ortalama Hasta Bekleme Süresi | 79 |

#### Süreç: Faturalandırma ve Tahsilat *(id 7, kod: SR-05)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 18 | PG-0501 | Tıbbi Hata Raporu Sayısı | 49 |

### Boğaziçi Üniversitesi *(kurum id: 7)*
#### Süreç: PAZARLAMA STRATEJİLERİ YÖNETİMİ SÜREÇ KARNESİ *(id 26, kod: SR1)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 149 | PG01 | Verilen Teklif Adeti | 4 |
| 150 | PG02 | Tekliflerin Sözleşmeye Dönüşme Oranı | 0 |
| 151 | PG03 | Hedef Pazardaki Müşteri Sayısı | 0 |

### Deneme Danışmanlık *(kurum id: 10)*
#### Süreç: Süreç1 *(id 38, kod: —)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 204 | — | Pg1 | 0 |

### Ege Teknoloji A.Ş. *(kurum id: 4)*
#### Süreç: Yazılım Geliştirme Yaşam Döngüsü *(id 8, kod: SR-01)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 19 | PG-0101 | Sprint Velocity | 68 |
| 20 | PG-0102 | Kod Kapsamı (Test Coverage) | 58 |
| 21 | PG-0103 | Dağıtım Sıklığı | 71 |
| 22 | PG-0104 | Çalışan Başına Gelir | 73 |
| 23 | PG-0105 | Müşteri Destek SLA Tutturma | 66 |
| 24 | PG-0106 | Hata Yoğunluğu (Bug/KLoC) | 77 |
| 25 | PG-0107 | Müşteri Memnuniyeti (NPS) | 57 |

#### Süreç: Müşteri Destek ve Servis *(id 9, kod: SR-02)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 26 | PG-0201 | Müşteri Destek SLA Tutturma | 68 |
| 27 | PG-0202 | Proje Teslimat Süresi | 41 |
| 28 | PG-0203 | Kod Kapsamı (Test Coverage) | 59 |

#### Süreç: Altyapı ve Operasyon Yönetimi *(id 10, kod: SR-03)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 29 | PG-0301 | Sistem Uptime Oranı | 68 |

#### Süreç: Satış ve İş Geliştirme *(id 11, kod: SR-04)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 30 | PG-0401 | Dağıtım Sıklığı | 70 |
| 31 | PG-0402 | Ortalama Çözüm Süresi | 67 |
| 32 | PG-0403 | Müşteri Destek SLA Tutturma | 50 |
| 33 | PG-0404 | Sistem Uptime Oranı | 57 |

#### Süreç: Proje Yönetimi ve Teslimat *(id 12, kod: SR-05)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 34 | PG-0501 | Kod Kapsamı (Test Coverage) | 47 |
| 35 | PG-0502 | Müşteri Memnuniyeti (NPS) | 58 |
| 36 | PG-0503 | Ortalama Çözüm Süresi | 51 |
| 37 | PG-0504 | Müşteri Destek SLA Tutturma | 50 |
| 38 | PG-0505 | Çalışan Başına Gelir | 62 |
| 39 | PG-0506 | Sprint Velocity | 59 |
| 40 | PG-0507 | Hata Yoğunluğu (Bug/KLoC) | 51 |

### Kayseri Model Fabrika *(kurum id: 16)*
#### Süreç: SR1 - ŞİRKET ORGANLARI YÖNETİMİ SÜRECİ *(id 54, kod: —)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 320 | — | Yönetim Kurulu Bilgilendirme Takvimine Uyum Oranı (Nakit Akış Tablosu Sunum ) | 0 |
| 318 | — | Yönetim Kurulu Karar Sayısı | 0 |
| 319 | — | Yönetim Kurulu Üyeleri İle Yapılan Görüşme Sayısı (Görüş Almak için Ziyaret Sayısı) | 0 |
| 316 | — | Şirket Genel Kurulları Zamanlamasına Uyum Oranı | 0 |
| 317 | — | Şirket Yönetim Kurulu Toplantıları Takvimine Uyum Oranı | 0 |

#### Süreç: SR10 - TEDARİK YÖNETİMİ SÜREÇ KARNESİ *(id 63, kod: —)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 375 | — | Baharat Değirmeni Sayısı | 0 |
| 384 | — | Gerçekleştirilen Sipariş Sayısı | 0 |
| 380 | — | Hediye Edilen Baharat Değirmeni Sayısı | 0 |
| 383 | — | Stok Doğruluk Oranı | 0 |

#### Süreç: SR11 - MAKİNA, TEKNOLOJİ VE BİLGİ YÖNETİMİ SÜREÇ KARNESİ *(id 64, kod: —)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 378 | — | Araçsız Kalınan Gün Sayısı | 0 |
| 386 | — | Makine Toplam Arıza Süresi | 0 |
| 372 | — | Su Tüketim Miktarı | 0 |
| 389 | — | Tamir Süresi(MTTR) | 0 |
| 397 | — | x | 0 |
| 398 | — | y | 0 |

#### Süreç: SR2 - STRATEJİK PLANLAMA YÖNETİMİ SÜREÇ KARNESİ *(id 55, kod: —)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 327 | — | EFQM Özdeğerlendirme Puanı | 0 |
| 324 | — | Hissedar Memnuniyet Oranı | 0 |
| 326 | — | Odak Grup Görüşme Sayısı (Hissedar ve Toplum) | 0 |
| 321 | — | SP Gözden Geçirme Planına Uyum Oranı | 0 |
| 325 | — | SP Veri Seti Kaynak Sayısı | 0 |
| 323 | — | Stratejik Hedeflere Ulaşma Oranı (SP Etkililiği) | 0 |
| 322 | — | Süreç Gözden Geçirme Planına Uyum Oranı | 0 |
| 329 | — | Yıllık Bütçe Gözden Geçirme | 0 |
| 328 | — | Yıllık Bütçe Hazırlama / Raporlama | 0 |

#### Süreç: SR3 - KURUM İMAJI VE KÜLTÜRÜ YÖNETİM SÜRECİ *(id 56, kod: —)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 330 | — | Faaliyetlerin (eğitim, danışmanlık, etkinlik, KSS) Basında Yer Alma Sayısı | 0 |
| 336 | — | Kurum Kimliği Unsurlarının Güncelliğini Kontrol Planına Uyum Oranı | 0 |
| 337 | — | Kurum İmaj Endeksi (Toplum) | 0 |
| 333 | — | Sosyal Medya İçerik Sayısı | 0 |
| 332 | — | Sosyal Medyadaki Takipçi Sayısı Artış Oranı (linkedin + İnstagram) | 0 |
| 338 | — | Sosyal Sorumluluk Faaliyet Sayısı | 0 |
| 340 | — | Sosyal Sorumluluk Faaliyetlerine Katılan Dış Paydaş Sayısı | 0 |
| 339 | — | STG'lere (BM 17 Kalkınma İlkesi) hizmet eden faaliyet sayısı | 0 |
| 331 | — | Tanınırlık Oranı | 0 |
| 334 | — | Yeşil Dönüşüme İlişkin Paylaşım Oranı | 0 |
| 335 | — | İçerik Başına Etkileşim Oranı | 0 |

#### Süreç: SR4 - PAZARLAMA STRATEJİLERİ YÖNETİM SÜRECİ *(id 57, kod: —)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 357 | — | Danışmanlık Hizmeti Verilen Yeni Firma Sayısı | 0 |
| 351 | — | Etkinliklere Katılımcı Sayısı | 0 |
| 344 | — | FVÖK/Net Satış Oranı | 0 |
| 345 | — | Gelir Bütçesine Uyum Oranı | 0 |
| 346 | — | Gider Bütçesine Uyum Oranı | 0 |
| 354 | — | Hedef Pazardaki Müşteri Sayısı | 0 |
| 348 | — | Kayseri İmalat Sanayisi Ortalama Dijital Farkındalık Artış Oranı | 0 |
| 347 | — | Kayseri İmalat Sanayisi Ortalama Yalın Farkındalık Artış Oranı | 0 |
| 349 | — | Kayseri İmalat Sanayisi Ortalama Yeşil/Sürdürlebilirlik Farkındalık Artış Oranı | 0 |
| 355 | — | KMF ile Aynı Bölgede Benzer Ürün ve Hizmetleri Sunan Kurum Sayısı | 0 |
| 353 | — | Mevcut Müşterileri Ziyaret Sayısı | 0 |
| 360 | — | Satışlarda Hibe/Teşvik Payı | 0 |
| 359 | — | Tavsiye Edilebilirlik Oranı | 0 |
| 343 | — | Tekliflerin Sözleşmeye Dönüşme Oranı - Sürdürülebilirlik | 0 |
| 342 | — | Verilen Teklif Sayısı - Sürdürülebilirlik | 0 |
| 341 | — | Verilen Teklif Sayısı - Yalın | 0 |
| 350 | — | Yapılan Etkinlik Sayısı (Panel, webinar, teknik gezi) | 0 |
| 358 | — | Yeşil Dönüşüm/Sürdürülebilirlik Çalışma(Eğitim-Proje-Etkinlik) Sayısı | 0 |
| 352 | — | Ziyaret Edilen Yeni Kurum Sayısı | 0 |
| 361 | — | Ödüle Başvuran Kurum ve Kuruluş Sayısı | 0 |
| 356 | — | Ürün/Hizmet Geliştirme Çalıştay Sayısı | 0 |

#### Süreç: SR5 - EĞİTİM HİZMETLERİ YÖNETİMİ SÜREÇ KARNESİ *(id 58, kod: —)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 392 | — | Eğitim Genel Memnuniyet Oranı | 0 |
| 370 | — | Eğitim Planına Uyum Oranı | 0 |
| 371 | — | Eğitimi Çalıştay Sayısı | 0 |
| 363 | — | Eğitimlere Katılan Sektör Çeşidi Sayısı | 0 |
| 387 | — | Sürdürülebilirlik konusunda verilen eğitim sayısı | 0 |
| 369 | — | Verilen Eğitim Sayısı (kaç farklı modül) | 0 |

#### Süreç: SR6 - DANIŞMANLIK HİZMETLERİ YÖNETİMİ  SÜREÇ KARNESİ *(id 59, kod: —)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 374 | — | Hizmet Verilen Kurumlardaki Getiri Miktarı | 0 |

#### Süreç: SR7 - BAŞARILARI TANIMA VE ÖDÜLLENDİRME YÖNETİMİ SÜREÇ KARNESİ *(id 60, kod: —)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 362 | — | Ödül Süreci Başlatma Takvimine Uyum Oranı | 0 |
| 367 | — | Ödül Süreci Değerlendirici Sayısı | 0 |
| 364 | — | Ödül Süreci Katılan Proje Sayısı | 0 |
| 365 | — | Ödül Süreci Katılımcı Memnuniyet Oranı | 0 |
| 368 | — | Ödül Töreni Genel Memnuniyet Oranı | 0 |
| 366 | — | Ödül Töreni Katılımcı Sayısı | 0 |

#### Süreç: SR8 - İNSAN KAYNAKLARI YÖNETİMİ SÜREÇ KARNESİ *(id 61, kod: —)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 382 | — | Yıllık İzin Tamamlama Oranı | 0 |
| 381 | — | Çalışan Memnuniyet Oranı | 0 |
| 376 | — | Çalışan Yetkinlik Geliştirme Planına Uyum Oranı | 0 |
| 377 | — | Çalışan Yetkinlik Seviyesi İyileşme Oranı | 0 |
| 373 | — | Özlük Haklarını Zamanında Sağlama Oranı | 0 |

#### Süreç: SR9 - MALİ İŞLER YÖNETİMİ SÜREÇ KARNESİ *(id 62, kod: —)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 391 | — | Fatura vb.nin Muhasebe Sistemine Zamanında Bildirilme Oranı | 0 |
| 393 | — | Finansal Raporlar Sunum Planına Uyum Oranı | 0 |
| 385 | — | Finansal İşlemler Maliyetinin Faaliyet Gelirine Oranı | 0 |
| 396 | — | Kesilen Fatura Sayısı | 0 |
| 394 | — | Mali denetim sayısı | 0 |
| 395 | — | Mali Denetimden Alınan Uyarı Sayısı | 0 |
| 379 | — | Tahsilatların Zamanında Yapılma Oranı | 0 |
| 388 | — | Tedarikçi Ödemelerinin Zamanında Yapılma Oranı | 0 |
| 390 | — | Vergi ve Yasal Yükümlülüklerin  Zamanında Yapılma Oranı | 0 |

### KMF Yonetim Danismanligi *(kurum id: 9)*
#### Süreç: Stratejik Planlama Süreci *(id 28, kod: SR2)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 209 | — | deneme | 0 |
| 208 | — | satış sayısı | 0 |

#### Süreç: Pazarlama Stratejileri Yönetim Süreci *(id 30, kod: SR4)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 176 | PG-SR4-NA-04871DF2 | Verilen Danışmanlık Süresi | 0 |
| 162 | PG-SR4-NA-096DFBCE | Ürün/Hizmet Geliştirme Çalıştay Sayısı | 0 |
| 174 | PG-SR4-NA-1481BFBC | Kurum İçi Eğitimlere Katılan Katılımcı Sayısı (Danışmanlık İçi) | 0 |
| 177 | PG-SR4-NA-16203942 | FVÖK/Net Satışlar | 0 |
| 180 | PG-SR4-NA-28185098 | Kurum İçi Eğitimlere Katılan Katılımcı Sayısı | 0 |
| 161 | PG-SR4-NA-2BC84605 | Ödül Süreci Gelirleri Bütçesine Uyum Oranı | 0 |
| 160 | PG-SR4-NA-2DBABA55 | Ziyaret Edilen Yeni Kurum Sayısı | 0 |
| 182 | PG-SR4-NA-369D9C11 | FVÖK/Net Satış Oranı | 0 |
| 163 | PG-SR4-NA-3F710884 | Ürün/Hizmet Geliştirme Çalıştaylarına Katılan Dış Paydaş  Sayısı | 0 |
| 156 | PG-SR4-NA-45ACA740 | Mevcut Müşterileri Ziyaret Sayısı | 0 |
| 153 | PG-SR4-NA-5734A314 | Etkinliklere Katılımcı Sayısı | 0 |
| 184 | PG-SR4-NA-5772BF1D | Kayseri İmalat Sanayisi Ortalama Yeşil/Sürdürlebilirlik Farkındalık Artış Oranı | 0 |
| 170 | PG-SR4-NA-5E7189C6 | Danışmanlık Hizmeti Verilen Yeni Firma Sayısı | 0 |
| 171 | PG-SR4-NA-682FCD90 | Genel Katılıma Açık Eğitimler Gerçekleştirilen Toplam Eğitim Süresi | 0 |
| 154 | PG-SR4-NA-6A3E282A | KMF ile Aynı Bölgede Benzer Ürün ve Hizmetleri Sunan Kurum Sayısı | 0 |
| 158 | PG-SR4-NA-88D0FEED | Tavsiye Edilebilirlik Oranı | 0 |
| 152 | PG-SR4-NA-90B7B808 | Danışmanlık Hizmeti Gelirleri Bütçesine Uyum Oranı | 0 |
| 183 | PG-SR4-NA-96D99A1B | Gider Bütçesine Uyum Oranı | 0 |
| 181 | PG-SR4-NA-A0C40819 | Yeşil Dönüşüm/Sürdürülebilirlik Çalışma(Eğitim-Proje-Etkinlik) Sayısı | 0 |
| 157 | PG-SR4-NA-A2EB9BF8 | Pazarlama Stratejileri Yönetimi 
Gider Bütçesine Uyum Oranı | 0 |
| 175 | PG-SR4-NA-AA91BB9A | VERİLEN EĞİTİMLERE KATILAN KURUM VE KURULUŞ SAYISI | 0 |
| 159 | PG-SR4-NA-BCA04923 | Tekliflerin Sözleşmeye Dönüşme Oranı | 0 |
| 178 | PG-SR4-NA-E1FFA9E0 | Genel Katılıma Açık Eğitimlere Katılımcı Sayısı | 0 |
| 155 | PG-SR4-NA-E741F3AF | Kayseri İmalat Sanayisi Ortalama Dijital Farkındalık Artış Oranı | 0 |
| 179 | PG-SR4-NA-F2480D47 | Kayseri İmalat Sanayisi Ortalama Yeşil Farkındalık Artış Oranı | 0 |
| 172 | PG-SR4-NA-FDDAB70C | Genel Katılıma Açık Eğitimlere Katılımcı Sayısı (Deneyimsel) | 0 |
| 173 | PG-SR4-NA-FFD69343 | Kurum İçi Eğitimler 
Gerçekleştirilen Toplam Eğitim Süresi | 0 |
| 164 | PG-SR4-ST2.1-9A80C2EC | Eğitim Gelirleri Bütçesine Uyum Oranı | 0 |
| 165 | PG-SR4-ST2.2-BAAC7C8A | Verilen Teklif Sayısı | 0 |
| 185 | PG-SR4-ST2.2-E9AECF15 | Gelir Bütçesine Uyum Oranı | 0 |
| 166 | PG-SR4-ST3.2-18EA4AAB | Kayseri İmalat Sanayisi Ortalama Yalın Farkındalık Artış Oranı | 0 |
| 167 | PG-SR4-ST3.3-08E4B43B | Yapılan Etkinlik Sayısı (Panel, webinar, teknik gezi) | 0 |
| 168 | PG-SR4-ST4.1-4D8212D3 | Hedef Pazardaki Müşteri Sayısı | 0 |
| 186 | PG-SR4-ST4.2-345C3E46 | Ödüle Başvuran Kurum ve Kuruluş Sayısı | 0 |
| 169 | PG-SR4-ST4.4-59165D14 | Satışlarda Hibe/Teşvik Payı | 0 |

#### Süreç: Danışmanlık Hizmetleri Yönetim Süreci *(id 32, kod: SR6)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 192 | PG-SR6-NA-140838EA | Tam Zamanlı Danışman Kapasite Kullanma Oranı | 0 |
| 189 | PG-SR6-NA-256EB5D6 | Danışmanlık Takvimine (Planına) Uyum Oranı | 0 |
| 201 | PG-SR6-NA-5DAEC51B | Mükerrer Hizmet Alan Firma Sayısı (Başladığı Yıl) | 0 |
| 202 | PG-SR6-NA-6034015B | Mükerrer Proje Sayısı (Başladığı Yıl) | 0 |
| 191 | PG-SR6-NA-75281698 | Proje Takviminden Sapma (Gün) | 0 |
| 190 | PG-SR6-NA-9DD528F6 | Ortalama Proje Tamamlanma Süresi | 0 |
| 187 | PG-SR6-NA-C5A13144 | Danışmanlık Gün Sayısı | 0 |
| 188 | PG-SR6-NA-D94A3EBF | Danışmanlık Süresi (Adam/Gün) | 0 |
| 193 | PG-SR6-NA-DC02F624 | Yarı Zamanlı Danışman Kullanma Oranı | 0 |
| 200 | PG-SR6-NA-F44B566D | Danışmanlık Süresi (İnsan/Gün) | 0 |
| 194 | PG-SR6-ST3.3-1711DDB9 | Hizmet Verilen Firma Sayısı (Başladığı Yıl) | 0 |
| 197 | PG-SR6-ST3.3-182876CD | Danışmanlık Süresi (İnsan/Gün) Stajyerli | 0 |
| 198 | PG-SR6-ST3.3-6CEE6852 | Sürdürülen Proje Sayısı | 0 |
| 195 | PG-SR6-ST3.3-8E684E08 | Hizmet Verilen Kurumlardaki Getiri Miktarı | 0 |
| 199 | PG-SR6-ST3.3-A20CF5C3 | Tamamlanan Proje Sayısı | 0 |
| 196 | PG-SR6-ST3.4-8CAA167D | Danışmanlık Projesi Memnuniyet Oranı | 0 |
| 203 | PG-SR6-ST6.1-A885A334 | Projelerde Görev Alan Stajyer Sayısı(Tamamlanan Proje) | 0 |

### Marmara Eğitim Vakfı *(kurum id: 5)*
#### Süreç: Öğrenci Kayıt ve Kabul *(id 13, kod: SR-01)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 41 | PG-0101 | Öğretmen Devir Oranı | 56 |

#### Süreç: Müfredat Planlama ve Uygulama *(id 14, kod: SR-02)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 42 | PG-0201 | Kayıt Yenileme Oranı | 66 |
| 43 | PG-0202 | Öğrenci Devamsızlık Oranı | 54 |
| 44 | PG-0203 | Öğretmen Memnuniyeti | 72 |
| 45 | PG-0204 | Öğretmen Devir Oranı | 51 |
| 46 | PG-0205 | Eğitim Materyali Yenileme Oranı | 60 |

#### Süreç: Öğretmen İşe Alım ve Gelişim *(id 15, kod: SR-03)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 47 | PG-0301 | Öğrenci Devamsızlık Oranı | 69 |
| 48 | PG-0302 | Başarı Ortalaması (Sınıf) | 57 |
| 49 | PG-0303 | Sınıf Başına Düşen Öğrenci | 73 |
| 50 | PG-0304 | Burs Alan Öğrenci Oranı | 54 |
| 51 | PG-0305 | Mezun İstihdam Oranı | 62 |
| 52 | PG-0306 | Öğretmen Memnuniyeti | 64 |
| 53 | PG-0307 | Kayıt Yenileme Oranı | 67 |
| 54 | PG-0308 | Veli Memnuniyet Skoru | 74 |

#### Süreç: Veli İletişim ve Memnuniyet *(id 16, kod: SR-04)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 55 | PG-0401 | Burs Alan Öğrenci Oranı | 53 |
| 56 | PG-0402 | Sınıf Başına Düşen Öğrenci | 62 |
| 57 | PG-0403 | Başarı Ortalaması (Sınıf) | 57 |
| 58 | PG-0404 | Öğretmen Devir Oranı | 57 |
| 59 | PG-0405 | Veli Memnuniyet Skoru | 75 |
| 60 | PG-0406 | Öğrenci Devamsızlık Oranı | 60 |
| 61 | PG-0407 | Kayıt Yenileme Oranı | 54 |
| 62 | PG-0408 | Eğitim Materyali Yenileme Oranı | 40 |
| 63 | PG-0409 | Mezun İstihdam Oranı | 60 |

#### Süreç: Tesis ve Lojistik Yönetimi *(id 17, kod: SR-05)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 64 | PG-0501 | Kayıt Yenileme Oranı | 74 |
| 65 | PG-0502 | Veli Memnuniyet Skoru | 45 |
| 66 | PG-0503 | Öğretmen Devir Oranı | 59 |
| 67 | PG-0504 | Başarı Ortalaması (Sınıf) | 53 |
| 68 | PG-0505 | Burs Alan Öğrenci Oranı | 77 |
| 69 | PG-0506 | Sınıf Başına Düşen Öğrenci | 55 |
| 70 | PG-0507 | Eğitim Materyali Yenileme Oranı | 66 |

### TechNova Bilişim Çözümleri A.Ş. *(kurum id: 11)*
#### Süreç: Yazılım Geliştirme *(id 44, kod: SR01)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 216 | SR01-PG01 | Yazılım Geliştirme - Tamamlama Oranı | 0 |
| 217 | SR01-PG02 | Yazılım Geliştirme - Ortalama Teslimat Süresi | 0 |
| 218 | SR01-PG03 | Yazılım Geliştirme - Hata Oranı | 0 |
| 219 | SR01-PG04 | Yazılım Geliştirme - Müşteri Memnuniyeti | 0 |
| 220 | SR01-PG05 | Yazılım Geliştirme - Süreç Verimliliği | 0 |
| 221 | SR01-PG06 | Yazılım Geliştirme - Maliyet Sapması | 0 |
| 222 | SR01-PG07 | Yazılım Geliştirme - Gelir Hedefi | 0 |
| 223 | SR01-PG08 | Yazılım Geliştirme - Eğitim Saati | 0 |
| 224 | SR01-PG09 | Yazılım Geliştirme - İşlem Adedi | 0 |
| 225 | SR01-PG10 | Yazılım Geliştirme - Uyum Skoru | 0 |

#### Süreç: Müşteri Deneyimi *(id 45, kod: SR02)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 226 | SR02-PG01 | Müşteri Deneyimi - Tamamlama Oranı | 0 |
| 227 | SR02-PG02 | Müşteri Deneyimi - Ortalama Teslimat Süresi | 0 |
| 228 | SR02-PG03 | Müşteri Deneyimi - Hata Oranı | 0 |
| 229 | SR02-PG04 | Müşteri Deneyimi - Müşteri Memnuniyeti | 0 |
| 230 | SR02-PG05 | Müşteri Deneyimi - Süreç Verimliliği | 0 |
| 231 | SR02-PG06 | Müşteri Deneyimi - Maliyet Sapması | 0 |
| 232 | SR02-PG07 | Müşteri Deneyimi - Gelir Hedefi | 0 |
| 233 | SR02-PG08 | Müşteri Deneyimi - Eğitim Saati | 0 |
| 234 | SR02-PG09 | Müşteri Deneyimi - İşlem Adedi | 0 |
| 235 | SR02-PG10 | Müşteri Deneyimi - Uyum Skoru | 0 |

#### Süreç: İnsan Kaynakları *(id 46, kod: SR03)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 236 | SR03-PG01 | İnsan Kaynakları - Tamamlama Oranı | 0 |
| 237 | SR03-PG02 | İnsan Kaynakları - Ortalama Teslimat Süresi | 0 |
| 238 | SR03-PG03 | İnsan Kaynakları - Hata Oranı | 0 |
| 239 | SR03-PG04 | İnsan Kaynakları - Müşteri Memnuniyeti | 0 |
| 240 | SR03-PG05 | İnsan Kaynakları - Süreç Verimliliği | 0 |
| 241 | SR03-PG06 | İnsan Kaynakları - Maliyet Sapması | 0 |
| 242 | SR03-PG07 | İnsan Kaynakları - Gelir Hedefi | 0 |
| 243 | SR03-PG08 | İnsan Kaynakları - Eğitim Saati | 0 |
| 244 | SR03-PG09 | İnsan Kaynakları - İşlem Adedi | 0 |
| 245 | SR03-PG10 | İnsan Kaynakları - Uyum Skoru | 0 |

#### Süreç: Finans Yönetimi *(id 47, kod: SR04)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 246 | SR04-PG01 | Finans Yönetimi - Tamamlama Oranı | 0 |
| 247 | SR04-PG02 | Finans Yönetimi - Ortalama Teslimat Süresi | 0 |
| 248 | SR04-PG03 | Finans Yönetimi - Hata Oranı | 0 |
| 249 | SR04-PG04 | Finans Yönetimi - Müşteri Memnuniyeti | 0 |
| 250 | SR04-PG05 | Finans Yönetimi - Süreç Verimliliği | 0 |
| 251 | SR04-PG06 | Finans Yönetimi - Maliyet Sapması | 0 |
| 252 | SR04-PG07 | Finans Yönetimi - Gelir Hedefi | 0 |
| 253 | SR04-PG08 | Finans Yönetimi - Eğitim Saati | 0 |
| 254 | SR04-PG09 | Finans Yönetimi - İşlem Adedi | 0 |
| 255 | SR04-PG10 | Finans Yönetimi - Uyum Skoru | 0 |

#### Süreç: Satış & Pazarlama *(id 48, kod: SR05)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 256 | SR05-PG01 | Satış & Pazarlama - Tamamlama Oranı | 0 |
| 257 | SR05-PG02 | Satış & Pazarlama - Ortalama Teslimat Süresi | 0 |
| 258 | SR05-PG03 | Satış & Pazarlama - Hata Oranı | 0 |
| 259 | SR05-PG04 | Satış & Pazarlama - Müşteri Memnuniyeti | 0 |
| 260 | SR05-PG05 | Satış & Pazarlama - Süreç Verimliliği | 0 |
| 261 | SR05-PG06 | Satış & Pazarlama - Maliyet Sapması | 0 |
| 262 | SR05-PG07 | Satış & Pazarlama - Gelir Hedefi | 0 |
| 263 | SR05-PG08 | Satış & Pazarlama - Eğitim Saati | 0 |
| 264 | SR05-PG09 | Satış & Pazarlama - İşlem Adedi | 0 |
| 265 | SR05-PG10 | Satış & Pazarlama - Uyum Skoru | 0 |

#### Süreç: AR-GE *(id 49, kod: SR06)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 266 | SR06-PG01 | AR-GE - Tamamlama Oranı | 0 |
| 267 | SR06-PG02 | AR-GE - Ortalama Teslimat Süresi | 0 |
| 268 | SR06-PG03 | AR-GE - Hata Oranı | 0 |
| 269 | SR06-PG04 | AR-GE - Müşteri Memnuniyeti | 0 |
| 270 | SR06-PG05 | AR-GE - Süreç Verimliliği | 0 |
| 271 | SR06-PG06 | AR-GE - Maliyet Sapması | 0 |
| 272 | SR06-PG07 | AR-GE - Gelir Hedefi | 0 |
| 273 | SR06-PG08 | AR-GE - Eğitim Saati | 0 |
| 274 | SR06-PG09 | AR-GE - İşlem Adedi | 0 |
| 275 | SR06-PG10 | AR-GE - Uyum Skoru | 0 |

#### Süreç: BT Altyapı *(id 50, kod: SR07)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 276 | SR07-PG01 | BT Altyapı - Tamamlama Oranı | 0 |
| 277 | SR07-PG02 | BT Altyapı - Ortalama Teslimat Süresi | 0 |
| 278 | SR07-PG03 | BT Altyapı - Hata Oranı | 0 |
| 279 | SR07-PG04 | BT Altyapı - Müşteri Memnuniyeti | 0 |
| 280 | SR07-PG05 | BT Altyapı - Süreç Verimliliği | 0 |
| 281 | SR07-PG06 | BT Altyapı - Maliyet Sapması | 0 |
| 282 | SR07-PG07 | BT Altyapı - Gelir Hedefi | 0 |
| 283 | SR07-PG08 | BT Altyapı - Eğitim Saati | 0 |
| 284 | SR07-PG09 | BT Altyapı - İşlem Adedi | 0 |
| 285 | SR07-PG10 | BT Altyapı - Uyum Skoru | 0 |

#### Süreç: Kalite Yönetimi *(id 51, kod: SR08)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 286 | SR08-PG01 | Kalite Yönetimi - Tamamlama Oranı | 0 |
| 287 | SR08-PG02 | Kalite Yönetimi - Ortalama Teslimat Süresi | 0 |
| 288 | SR08-PG03 | Kalite Yönetimi - Hata Oranı | 0 |
| 289 | SR08-PG04 | Kalite Yönetimi - Müşteri Memnuniyeti | 0 |
| 290 | SR08-PG05 | Kalite Yönetimi - Süreç Verimliliği | 0 |
| 291 | SR08-PG06 | Kalite Yönetimi - Maliyet Sapması | 0 |
| 292 | SR08-PG07 | Kalite Yönetimi - Gelir Hedefi | 0 |
| 293 | SR08-PG08 | Kalite Yönetimi - Eğitim Saati | 0 |
| 294 | SR08-PG09 | Kalite Yönetimi - İşlem Adedi | 0 |
| 295 | SR08-PG10 | Kalite Yönetimi - Uyum Skoru | 0 |

#### Süreç: Lojistik *(id 52, kod: SR09)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 296 | SR09-PG01 | Lojistik - Tamamlama Oranı | 0 |
| 297 | SR09-PG02 | Lojistik - Ortalama Teslimat Süresi | 0 |
| 298 | SR09-PG03 | Lojistik - Hata Oranı | 0 |
| 299 | SR09-PG04 | Lojistik - Müşteri Memnuniyeti | 0 |
| 300 | SR09-PG05 | Lojistik - Süreç Verimliliği | 0 |
| 301 | SR09-PG06 | Lojistik - Maliyet Sapması | 0 |
| 302 | SR09-PG07 | Lojistik - Gelir Hedefi | 0 |
| 303 | SR09-PG08 | Lojistik - Eğitim Saati | 0 |
| 304 | SR09-PG09 | Lojistik - İşlem Adedi | 0 |
| 305 | SR09-PG10 | Lojistik - Uyum Skoru | 0 |

#### Süreç: Hukuk & Uyum *(id 53, kod: SR10)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 306 | SR10-PG01 | Hukuk & Uyum - Tamamlama Oranı | 0 |
| 307 | SR10-PG02 | Hukuk & Uyum - Ortalama Teslimat Süresi | 0 |
| 308 | SR10-PG03 | Hukuk & Uyum - Hata Oranı | 0 |
| 309 | SR10-PG04 | Hukuk & Uyum - Müşteri Memnuniyeti | 0 |
| 310 | SR10-PG05 | Hukuk & Uyum - Süreç Verimliliği | 0 |
| 311 | SR10-PG06 | Hukuk & Uyum - Maliyet Sapması | 0 |
| 312 | SR10-PG07 | Hukuk & Uyum - Gelir Hedefi | 0 |
| 313 | SR10-PG08 | Hukuk & Uyum - Eğitim Saati | 0 |
| 314 | SR10-PG09 | Hukuk & Uyum - İşlem Adedi | 0 |
| 315 | SR10-PG10 | Hukuk & Uyum - Uyum Skoru | 0 |

#### Süreç: Müşteri Destek *(id 40, kod: —)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 206 | K-5190 | Ortalama Yanıt Süresi | 0 |

#### Süreç: Yazılım Geliştirme *(id 39, kod: —)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 205 | K-1258 | Sprint Tamamlama Oranı | 0 |

### TechNova Bilişim Çözümleri A.Ş. *(kurum id: 15)*
#### Süreç: Yazılım Geliştirme *(id 41, kod: SR-01)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 211 | — | Code Coverage | 0 |
| 210 | — | Sprint Velocity | 0 |

#### Süreç: Müşteri Başarısı *(id 42, kod: SR-02)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 212 | — | NPS Skoru | 0 |
| 213 | — | Ortalama Yanıt Süresi | 0 |

#### Süreç: İnsan Kaynakları *(id 43, kod: SR-03)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 215 | — | Eğitim Memnuniyeti | 0 |
| 214 | — | Çalışan Devir Hızı | 0 |

### Test A.Ş. *(kurum id: 14)*
#### Süreç: Şirket Organları Yönetimi Süreci *(id 27, kod: SR1)*

| PG id | Kod | PG adı | Veri girişi |
|---:|---|---|---:|
| 207 | — | satış sayısı | 0 |

## 5. Özet

| Kalem | Adet |
|---|---:|
| Aktif kurum | 17 |
| Aktif süreç | 56 |
| Aktif PG (`process_kpis`) | 318 |
| Aktif veri girişi (`kpi_data`) | 4086 |
