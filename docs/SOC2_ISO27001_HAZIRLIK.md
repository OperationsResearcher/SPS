# 🛡️ SOC 2 + ISO 27001 Hazırlık Checklist

> **Tarih:** Sprint 51
> **Hedef kitle:** Compliance officer, CTO
> **Not:** Bu sertifika **değil**, sertifikasyon başvurusuna hazırlık dokümanıdır.
> Resmi sertifika için lisanslı denetçi (CPA / external auditor) gerekir.

---

## SOC 2 Trust Service Criteria — Kokpitim Durum

### 1. Security (CC — Common Criteria)

| Kontrol | Gereklilik | Kokpitim Durum | Kanıt |
|---|---|:-:|---|
| CC1.1 | Etik kod + COC | 🟡 Kısmi | `tenants.code_of_ethics` field |
| CC1.4 | Yetkinlik gereklilikleri | 🟡 Kısmi | Role tanımları |
| CC2.1 | Bilgi güvenliği politikası | 🔴 Eksik | Doküman yazılmalı |
| CC2.2 | İletişim güvenliği | 🟢 Var | TLS zorunlu, SAMESITE=Strict |
| CC2.3 | Çalışan güvenlik eğitimi | 🔴 Eksik | Doc yok |
| CC5.1 | Logical access — auth | 🟢 Var | Login + 2FA (Sprint 26) + SSO |
| CC5.2 | Logical access — yetki yönetimi | 🟢 Var | RBAC + tenant scope |
| CC5.3 | Yeni erişim onayı | 🟡 Kısmi | Admin user yarat — log var |
| CC6.1 | Logical access çıkış | 🟢 Var | KVKK delete (Sprint 12) |
| CC6.2 | Şifre yönetimi | 🟢 Var | Complexity policy (Sprint 22) |
| CC6.3 | Logical access kayıt | 🟢 Var | audit_logs + login throttle |
| CC6.6 | External access tracking | 🟢 Var | IP + user_agent log'lanır |
| CC6.7 | Veri transfer şifrelemesi | 🟢 Var | HTTPS only |
| CC6.8 | Anti-malware | 🟡 Kısmi | File upload validation (Sprint 22) |
| CC7.1 | Anomali tespit | 🟢 Var | KPI anomali (Sprint 14) + audit alert |
| CC7.2 | Sistem operasyon izleme | 🟡 Kısmi | Sentry opsiyonel |
| CC7.3 | Olay yönetimi | 🟡 Kısmi | Audit log + güvenlik rehberi (Sprint 47) |
| CC8.1 | Değişiklik yönetimi | 🟢 Var | Git + migration zinciri |
| CC9.1 | Risk yönetimi | 🟢 Var | Risk modülü (Sprint 34) + K-Radar |
| CC9.2 | Vendor management | 🔴 Eksik | Vendor portal modülü Sprint 53+ |

**Güvenlik kategori skoru: 🟢 65% · 🟡 25% · 🔴 10%**

### 2. Availability (A)

| Kontrol | Durum | Not |
|---|:-:|---|
| A1.1 SLA tanımı | 🔴 | Doc gerekli |
| A1.2 Capacity monitoring | 🟡 | Index var, otomasyon yok |
| A1.3 Backup + restore | 🟢 | `/ayarlar/yedekleme` paneli aktif |

### 3. Confidentiality (C)

| Kontrol | Durum |
|---|:-:|
| C1.1 Veri sınıflandırma | 🟡 |
| C1.2 Şifrelenmiş veri taşıma | 🟢 (TLS) |
| C1.3 Encrypted at rest | 🟡 (DB encryption opsiyonel) |

### 4. Processing Integrity (PI)

| Kontrol | Durum |
|---|:-:|
| PI1.1 Veri doğruluğu | 🟢 (transaction atomicity Sprint 19) |
| PI1.2 Input validation | 🟢 (Magic byte Sprint 22, password Sprint 22) |
| PI1.3 Processing complete | 🟡 |

### 5. Privacy (P)

| Kontrol | Durum |
|---|:-:|
| P1.1 Privacy notice | 🔴 (KVKK aydınlatma metni eksik) |
| P2.1 User consent | 🟡 |
| P3.1 Veri toplama sınırı | 🟡 |
| P4.1 Erişim hakkı | 🟢 (KVKK export Sprint 12) |
| P4.2 Düzeltme hakkı | 🟢 (Profile edit) |
| P4.3 Silme hakkı | 🟢 (KVKK delete Sprint 12) |
| P5.1 Veri kalitesi | 🟢 |
| P6.1 Saklama + imha | 🟡 (90 gün audit retention plan var) |

---

## ISO 27001 Annex A Kontroller — Durum

### A.5 Bilgi güvenliği politikaları
- 🔴 A.5.1 Politika dokümanı — **Yazılmalı**

### A.6 Bilgi güvenliği organizasyonu
- 🟢 A.6.1 Roller — Role model var
- 🟡 A.6.2 Mobile + uzaktan çalışma — Mobile-first CSS (Sprint 27)

### A.7 İnsan kaynakları güvenliği
- 🔴 A.7.1-7.3 Eğitim + employment lifecycle — Doc yok

### A.8 Varlık yönetimi
- 🟢 A.8.1 Asset inventory — DB modelleri = asset inventory
- 🟡 A.8.2 Bilgi sınıflandırma — Doc yok
- 🟢 A.8.3 Medya işleme — Upload security (Sprint 22)

### A.9 Erişim kontrolü
- 🟢 A.9.1 İş gereklilikleri — RBAC
- 🟢 A.9.2 User access mgmt — Admin paneli
- 🟢 A.9.3 User responsibility — KVKK + audit
- 🟢 A.9.4 System access — login + 2FA

### A.10 Kriptografi
- 🟢 A.10.1 Crypto controls — TLS + bcrypt
- 🟡 A.10.2 Key mgmt — SECRET_KEY rotasyon rehberi (Sprint 47)

### A.11 Fiziksel güvenlik
- ⚪ Cloud (Oracle VM) sorumluluğu

### A.12 Operasyon güvenliği
- 🟢 A.12.1 Operational procedures — Docker + scripts
- 🟢 A.12.3 Backup — Backup paneli + scheduler
- 🟢 A.12.4 Logging + monitoring — audit_logs
- 🟢 A.12.6 Vulnerability mgmt — Dependabot önerilir

### A.13 İletişim güvenliği
- 🟢 A.13.1 Network security — HTTPS, CSP, SameSite
- 🟢 A.13.2 Information transfer — Encrypted

### A.14 Sistem geliştirme
- 🟢 A.14.1 Security in dev — CI guards (Sprint 29-30)
- 🟢 A.14.2 Test environments — config layering

### A.15 Tedarikçi ilişkileri
- 🔴 A.15.1 Supplier policy — Doc yok

### A.16 Olay yönetimi
- 🟡 A.16.1 Incident mgmt — Güvenlik rehberi (Sprint 47)

### A.17 İş sürekliliği
- 🟡 A.17.1 BCP — Backup var, plan dokümante edilmedi

### A.18 Uyumluluk
- 🟢 A.18.1 Yasal uyum — KVKK alt yapısı (Sprint 12)
- 🟡 A.18.2 Bilgi güvenliği incelemesi — Audit log + yıllık review

---

## Eksiklerin Önceliklendirilmiş Listesi

### 🔴 KRİTİK (sertifika için zorunlu)

| # | Belge / Süreç | Tahmin |
|:-:|---|:-:|
| 1 | Bilgi Güvenliği Politikası (4-6 sayfa) | 8h |
| 2 | KVKK Aydınlatma Metni (web sayfa) | 2h |
| 3 | İncident Response Plan | 4h |
| 4 | Tedarikçi Güvenlik Politikası | 4h |
| 5 | İş Sürekliliği Planı (BCP) | 8h |

### 🟠 YÜKSEK (sertifika kapsamı genişletir)

| # | İş | Tahmin |
|:-:|---|:-:|
| 6 | Çalışan güvenlik eğitimi içeriği | 16h |
| 7 | Veri sınıflandırma (public/internal/confidential) | 4h |
| 8 | Yıllık risk değerlendirme dökümantasyonu | 4h |
| 9 | Vulnerability management process | 4h |
| 10 | Vendor management process + portal | 24h |

### 🟡 ORTA (preventive)

- Quarterly access review otomasyonu
- Encrypted-at-rest DB (pgcrypto column encryption)
- 3rd party pentest (yıllık)
- DR drill (felaket kurtarma testi)

---

## Önerilen Yol Haritası

### Q3 2026 — Politika dokümanları
- Sprint 53: ISMS politikası, KVKK aydınlatma metni
- Sprint 54: Incident response + BCP

### Q4 2026 — Process audit
- Sprint 55-56: Sertifika öncesi internal audit (preparation)
- 3rd party CPA seçimi

### 2027 — Sertifika
- Q1: SOC 2 Type I (point-in-time)
- Q2-Q3: SOC 2 Type II (6 ay süre — operating effectiveness)
- Q3: ISO 27001 Stage 1 + Stage 2 denetimleri

---

## Notlar

1. **SOC 2 vs ISO 27001 farkı:**
   - SOC 2: US-based, CPA firmaları denetler, "report" üretir
   - ISO 27001: Uluslararası, accredited body sertifika verir
   - Türkiye'de **ISO 27001** daha yaygın, kurumsal tender'larda istenir

2. **Maliyet tahmini (2026 fiyatlar):**
   - SOC 2 Type II: $30k-60k (CPA fee + 6 ay süre)
   - ISO 27001: $15k-30k (TSE/BSI/SGS gibi accredited body)

3. **Hazırlık süresi (mevcut kontrol seviyesinden):**
   - SOC 2 Type I: 3 ay (dökümantasyon + bazı eksik kontroller)
   - ISO 27001: 6-9 ay (ISMS yapı + Stage 1+2 audit)

4. **Bu doküman canlı tutulmalı**: Her güvenlik patch'i sonrası durum tablosu güncellenmelidir.

---

> Hazırlayan: Kokpitim DevOps  
> İnceleme: CTO + Bilgi Güvenliği Yöneticisi  
> Sonraki güncelleme: Q3 2026
