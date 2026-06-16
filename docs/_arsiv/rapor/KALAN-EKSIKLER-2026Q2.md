# 📋 KALAN EKSİKLER — Sprint 18 Sonrası

> **Tarih:** 2026-05-23
> **Tamamlanan sprint:** 1-18
> **Bu doküman:** Audit + roadmap + güvenlik tarama sonrası HÂLÂ AÇIK olan tüm işlerin envanteri

---

## 🔴 KRİTİK (acil — yapılmazsa risk)

### Güvenlik (kullanıcı eylemi gerekiyor)
| # | İş | Yer | Tahmin |
|---|---|---|:-:|
| 1 | `.env` SECRET_KEY production'da değiştir | `.env:1` | 5 dk |
| 2 | DB password güçlendir + PROD'da uniq | `.env:3` | 10 dk |
| 3 | KVKK aydınlatma metni sayfası | yeni | 1h |

### Veri tutarlılığı
| # | İş | Yer | Tahmin |
|---|---|---|:-:|
| 4 | KpiData + KpiDataAudit atomicity (xfail test'i geçirmek) | `routes_kpi_data.py:150-200` | 3h |
| 5 | K-Vektor weight atomic update | `sp/routes_strategy.py:125-144` | 2h |

---

## 🟠 YÜKSEK (3-6 hafta)

### Legacy sunset (~3.940 satır kod silinecek)
| # | Dosya | Satır | Bağımlılık |
|---|---|:-:|---|
| 6 | `app/routes/process.py` | 1.805 | KpiDataAudit logic micro/surec'e taşı |
| 7 | `app/routes/admin.py` | 1.141 | micro/admin merge tamamla |
| 8 | `app/routes/strategy.py` | 195 | template'ler micro/sp'ye yönlendir |
| 9 | `app/routes/auth.py` legacy | 302 | micro/shared/auth merge |
| 10 | `auth/routes.py` (root) | 250+ | aynı |
| 11 | `decorators.py` (root) | 207 | `app/utils/project_rbac.py`'ye taşı |
| 12 | `main/routes/` | 328 | micro modüllere parça parça |

### Güvenlik (kod tarafı)
| # | İş | Tahmin |
|---|---|:-:|
| 13 | Login failure threshold + account lock | 4h |
| 14 | Password complexity rules (uzunluk+karmaşıklık) | 2h |
| 15 | Session SameSite=Strict (şu an Lax) | 30dk |
| 16 | Remember me token rotation | 4h |
| 17 | Rate limit storage memory→redis (S3) | 2h |
| 18 | Tüm `Query.all()` → pagination (DOS koruma) | 8h |
| 19 | Audit log retention policy (90 gün anonimize) | 4h |

### Test kapsamı (modül bazlı 0 test)
| # | Modül | Önerilen test sayısı |
|---|---|:-:|
| 20 | `k_rapor` | 10-15 |
| 21 | `bireysel` | 8-10 |
| 22 | `admin` | 12-15 |
| 23 | `marketing` | 3-5 |
| 24 | `kurum` | 5-8 |
| 25 | `masaustu` | 3-5 |

### Performans
| # | İş | Tahmin |
|---|---|:-:|
| 26 | k_rapor 16 endpoint N+1 fix (eager loading) | 6h |
| 27 | ProcessMaturity composite index | 30dk |
| 28 | N+1 regression test'leri her core modüle | 4h |

---

## 🟡 ORTA (2-3 ay)

### Yeni özellikler — diferansiasyon
| # | Özellik | Tahmin |
|---|---|:-:|
| 29 | **SSO Google OAuth** | 16h |
| 30 | **2FA TOTP** | 12h |
| 31 | **White-labeling** (logo, color, custom domain) | 16h |
| 32 | **Multi-language EN core** | 24h |
| 33 | **Mobile-first dashboard** + PWA | 32h |
| 34 | Dark mode toggle | 8h |
| 35 | Custom dashboard builder | 40h |
| 36 | Drilldown link'leri (chart → detail) | 8h |
| 37 | Trend forecasting (KPI projection) | 12h |
| 38 | Sektör benchmark verisi (K-Radar) | 16h |

### Entegrasyon
| # | Entegrasyon | Tahmin |
|---|---|:-:|
| 39 | Microsoft Azure AD SSO | 12h |
| 40 | SAML provider (enterprise) | 16h |
| 41 | Teams webhook (Slack benzeri) | 4h |
| 42 | Power BI REST API endpoint | 16h |
| 43 | Tableau Web Data Connector | 24h |
| 44 | Google Calendar sync | 12h |
| 45 | Bulk Excel import (KPI/Process/Project) | 12h |
| 46 | Discord webhook | 4h |

### AI / ML
| # | Özellik | Tahmin |
|---|---|:-:|
| 47 | KPI root cause LLM suggestion | 16h |
| 48 | Strateji pivot AI önerisi | 20h |
| 49 | Executive summary AI yazımı (`ai_executive_summary.py` extend) | 12h |
| 50 | What-If senaryo simülasyonu | 16h |

### Modül derinleşme
| # | İş | Tahmin |
|---|---|:-:|
| 51 | Strategy status (başlanmış/risk/tamamlandı) | 8h |
| 52 | Strategy edit history audit | 8h |
| 53 | Strategy bulk editor | 16h |
| 54 | KPI versioning (şablon değişimi) | 16h |
| 55 | Faaliyet gecikme push notification | 8h |
| 56 | Activity resource leveling | 16h |
| 57 | KPI correlation analysis (Pearson) | 12h |
| 58 | Gantt görev bağımlılığı + kritik yol | 32h |
| 59 | Project baseline tracking | 12h |
| 60 | Project EVM real-time | 16h |
| 61 | Bireysel peer comparison (departman) | 12h |
| 62 | Year-over-year trend | 12h |
| 63 | 360° feedback | 24h |
| 64 | Development plan tracking | 16h |

---

## 🟢 DÜŞÜK (4-6 ay sonra)

### Yeni modüller (büyük)
| # | Modül | Tahmin |
|---|---|:-:|
| 65 | Risk yönetim modülü (RAID + K-Radar birleşik) | 60h |
| 66 | Tedarikçi/Müşteri portali (vendor view) | 80h |
| 67 | Sürdürülebilirlik/ESG modülü (CBAM, Scope 1+2+3) | 100h |
| 68 | Eğitim + zanaatkar gelişim takip | 80h |

### Compliance & Enterprise
| # | İş | Tahmin |
|---|---|:-:|
| 69 | SOC 2 / ISO 27001 dokumentasyon hazırlık | 40h |
| 70 | Data residency (TR/EU seçimi) | 24h |
| 71 | Backup encryption AES-256 | 16h |
| 72 | Self-service backup restore | 16h |
| 73 | Custom RBAC role yaratma | 24h |
| 74 | License management (feature gating) | 32h |
| 75 | API gateway + rate limit per-tenant | 16h |
| 76 | API documentation (Swagger genişlet) | 12h |

---

## 📊 ÖZET SAYIM

| Bölge | İş sayısı | Toplam efor |
|---|:-:|:-:|
| 🔴 Kritik | 5 | ~6h |
| 🟠 Yüksek | 23 | ~80h |
| 🟡 Orta | 36 | ~400h |
| 🟢 Düşük | 12 | ~480h |
| **TOPLAM** | **76** | **~970h** |

---

## 🎯 SIRA ÖNERİSİ

### Sprint 19 (acil — bu hafta)
- Atomicity fix (KpiData transaction, K-Vektor)
- `.env` SECRET_KEY rotasyonu rehberi
- KVKK aydınlatma metni
- Session SameSite=Strict + login failure lock

### Sprint 20-21 (yüksek değer — 2-3 hafta)
- Legacy sunset: `dashboard.py` zaten silindi; sıra `process.py` ve `strategy.py`
- k_rapor + bireysel test kapsamı (~25 yeni test)
- Pagination zorunluluğu

### Sprint 22-23 (Q3 başı — enterprise hazırlık)
- SSO Google OAuth
- 2FA TOTP
- White-labeling
- Mobile-first dashboard başlangıcı

### Sprint 24+ (Q3-Q4)
- Multi-language EN
- AI advisor v2 (anomali genişlet)
- Yeni modüller (öncelik: ESG, sonra Risk yönetim, sonra Vendor portal)

---

## 🚀 EN HIZLI GETİRİSİ OLAN 5 İŞ (Quick Win)

1. **KpiData atomicity fix** (3h, kritik veri bütünlüğü)
2. **Pagination zorunluluğu** (8h, DOS koruması)
3. **`decorators.py` taşıma** (4h, ~207 satır legacy temizliği)
4. **k_rapor smoke test** (4h, %0 → %30 kapsam)
5. **Login failure lock** (4h, brute force koruması)

**Toplam:** 23 saat = ~1 sprint, etki büyük.
