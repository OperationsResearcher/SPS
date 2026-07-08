# Kişisel Veri İşleme Envanteri — Kokpitim

> 2026-07-08 — kod tabanı ve DB şeması taranarak çıkarılmıştır (TASK-234).
> Veri sorumlusu: `[DOLDURULACAK — tüzel kişi unvanı]`

## 1. Veri kategorileri ve kaynakları

### 1.1 Kullanıcı kimlik/iletişim verileri (`users` tablosu)
| Alan | Veri | Zorunlu? | Amaç |
|---|---|---|---|
| `email` | E-posta | ✅ | Kimlik doğrulama, bildirim |
| `first_name`, `last_name` | Ad-soyad | ○ | Kullanıcı tanımlama, karne/rapor gösterimi |
| `phone_number` | Telefon | ○ | İletişim (opsiyonel profil alanı) |
| `job_title`, `department` | Unvan, departman | ○ | Organizasyon/performans yönetimi |
| `profile_picture` | Profil fotoğrafı URL | ○ | Kullanıcı arayüzü |
| `password_hash` | Parola özeti (düz parola SAKLANMAZ) | ✅ | Kimlik doğrulama |
| `totp_secret`, `totp_backup_codes_json` | 2FA sırları | ○ | Hesap güvenliği |
| `theme/layout/notification/locale_preferences` | Tercihler | ○ | Kişiselleştirme |

### 1.2 Performans verileri (özel önem — çalışan izleme boyutu)
| Kaynak | Veri | Not |
|---|---|---|
| `individual_performance_indicators`, `individual_kpi_data`, `individual_activities` | Bireysel hedef, gerçekleşme, faaliyet kayıtları | Çalışanın iş performansı — işveren meşru menfaati; aydınlatma metninde AÇIKÇA belirtilmeli |
| `kpi_data.user_id` | Veriyi giren kullanıcı | İzlenebilirlik |
| Bireysel karne PDF'leri | Ad-soyad + performans skorları | Talep üzerine üretilir, sistemde saklanmaz |

### 1.3 İşlem/log verileri
| Kaynak | Veri | Saklama |
|---|---|---|
| `audit_logs` | user_id, aksiyon, IP adresi, zaman | Denetim izi; süre politikası `[DOLDURULACAK — öneri: 2 yıl]` |
| `error.log` (uygulama) | Hata bağlamında IP/user-agent olabilir | Rotasyonlu 10MB×5 (TASK-229) |
| Nginx erişim logları (Yayın VM) | IP, user-agent | `[DOLDURULACAK — sunucu log rotasyon süresi]` |

### 1.4 Destek/iletişim verileri
| Kaynak | Veri |
|---|---|
| `tickets` (Kule) | Konu, mesaj, ekran görüntüsü yolu, sayfa URL |
| Demo talep formu (pazarlama sitesi) | Ad, e-posta, kurum — **gizlilik politikası sayfası henüz yok (boşluk #1)** |
| `notifications` | Kullanıcıya gönderilen bildirim içerikleri |

### 1.5 Çerezler
| Çerez | Tür | Amaç |
|---|---|---|
| Flask session | Zorunlu | Oturum yönetimi (Secure, HttpOnly, SameSite=Strict) |
| remember token | Zorunlu (opsiyonlu) | "Beni hatırla" |
| Üçüncü taraf analitik | — | YOK (2026-07-08 itibarıyla) |

## 2. İşleme amaçları ve hukuki sebepler (m.5)

| Amaç | Hukuki sebep |
|---|---|
| Hizmetin sunulması (hesap, oturum, yetki) | Sözleşmenin kurulması/ifası (m.5/2-c) |
| Performans yönetimi (karne, PG takibi) | Veri sorumlusunun meşru menfaati (m.5/2-f) — müşteri kurumun İK süreci; Kokpitim burada **veri işleyen** konumundadır |
| Güvenlik logları, denetim izi | Hukuki yükümlülük + meşru menfaat |
| Bildirim e-postaları | Sözleşmenin ifası; tercihle kapatılabilir |
| Demo talebi ile iletişim | İlgili kişinin talebi (m.5/2-c) |

> **Rol ayrımı (kritik):** Kokpitim çok-kiracılı SaaS'tır. Kurum (tenant) kendi personelinin verisi için **veri sorumlusu**, Kokpitim işletmecisi **veri işleyen**dir. Müşteri sözleşmelerine veri işleme ek protokolü (DPA benzeri) eklenmesi önerilir — `[DOLDURULACAK]`.

## 3. Aktarımlar

| Alıcı | Veri | Dayanak |
|---|---|---|
| SMTP sağlayıcı (tenant'ın kendi SMTP'si veya platform SMTP) | E-posta adresi, bildirim içeriği | Hizmetin ifası |
| LLM sağlayıcı (Gemini — AI özet/koç özellikleri) | Performans metrikleri (AD-SOYAD gönderimi kontrol edilmeli `[DOLDURULACAK — prompt içerik denetimi]`) | Meşru menfaat + sözleşme; tenant AI ayarlarından kapatılabilir |
| Oracle Cloud (barındırma) | Tüm veriler (barındırma) | Veri merkezi bölgesi teyidi `[DOLDURULACAK]`; yurt dışıysa m.9 değerlendirmesi ŞART |
| Google (SSO kullanan kullanıcılar) | E-posta (kimlik doğrulama) | İlgili kişinin talebi |

## 4. Saklama ve imha

- Hesap silme: **anonimleştirme** (m.7 endpoint'i) — kişisel alanlar silinir, istatistiksel bütünlük korunur
- Platform politikası: hard delete yok, `is_active=False` soft delete; anonimleştirme kişisel veri bağını koparır
- DB yedekleri: 30 gün otomatik imha (`oracle_full_backup.sh` retention)
- Audit log saklama süresi: `[DOLDURULACAK]`
- Kişisel Veri Saklama ve İmha Politikası belgesi: `[DOLDURULACAK — VERBİS kaydı zorunluysa şart]`

## 5. Teknik ve idari tedbirler (mevcut — kod doğrulamalı)

- Parola hash, TOTP 2FA, SSO, brute-force kilidi, rate limit (Redis)
- TLS/HSTS, CSP, Secure/HttpOnly/SameSite=Strict çerezler, X-Frame-Options DENY
- Tenant izolasyonu: route-düzeyi kontroller + merkezi ORM guard (TASK-230)
- `ENCRYPTION_KEY` ile hassas yapılandırma şifreleme; `.env` sırları repo dışında
- Denetim izi (audit_logs), erişim loglama, günlük yedek + restore prosedürü
- İdari: `[DOLDURULACAK — personel gizlilik taahhütleri, erişim yetki matrisi onayı]`
