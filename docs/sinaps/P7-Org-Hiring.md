# P7 — ORGANİZASYON · HIRING PLANI
> Tarih: 2026-05-16 · Durum: TASLAK · Bağımlılık: P1, P4

---

## 1. Felsefe

- **Küçük ekip, derin sahiplik.** Y1 sonu max 20 kişi.
- **Full-stack tercihi.** F1-F2'de role katı değil; üretkenlik öncelikli.
- **Remote-first.** TR + AB zaman dilimi (2-saat fark içinde).
- **Asenkron iş kültürü.** Yazılı kararlar, az toplantı.
- **Dogfooding.** Sinaps'ı kendi şirketimizi yönetmek için kullanırız (OKR, süreç, risk).

---

## 2. Y1 Org Şeması (Hedef: 18 kişi, ay 12 sonu)

```
                          CEO (kurucu)
                        ╱      |       ╲
                    CTO       CRO       COO
                  (kurucu)  (~Ay 6)   (~Ay 9)
                  ╱  |  ╲     |          |
              Eng  Prod  SRE  Sales+CSM  Ops+Finance
            (8-10) (1)   (1)   (3-4)      (1-2)
```

**Çekirdek (F0-F1, ay 0-3):** 6 kişi
- CEO + CTO (kurucular)
- 2 Backend Eng (Python/Postgres uzmanı)
- 2 Frontend Eng (Next.js/TS)

**Genişleme 1 (F1 sonu, ay 3):** +3 = 9
- 1 SRE / Platform Eng
- 1 Product Designer
- 1 Product Manager

**Genişleme 2 (F2, ay 4-6):** +4 = 13
- 1 Senior Backend (event/AI alanı)
- 1 Senior Frontend
- 1 Sales/BD lead (CRO öncesi)
- 1 Founding CSM

**Genişleme 3 (F3, ay 7-9):** +3 = 16
- 1 QA / Quality Eng
- 1 Mobile Eng (RN/Expo)
- 1 SDR / Marketing ops

**Genişleme 4 (F4, ay 10-12):** +2 = 18
- 1 Security Eng / DPO (yarı zamanlı dış olabilir)
- 1 Finance / Operations Manager

---

## 3. Rol Tanımları (özet)

### 3.1 Mühendislik
- **Senior Backend Eng** — Python, FastAPI, PostgreSQL (ltree/RLS deneyimi tercih), domain modeling. Y1'de domain context sahipliği.
- **Senior Frontend Eng** — Next.js 15 App Router, TS, Tailwind, design system. Cortex DS sahibi.
- **SRE / Platform Eng** — K8s, Helm, ArgoCD, observability, çok-bulut. Runbook + on-call başlatır.
- **Mobile Eng** — RN/Expo, OTA update, store delivery (Apple/Google).
- **Quality Eng** — Test stratejisi, otomasyon, CI sahibi. Kalite kültürü taşıyıcı.
- **Security Eng** — Compliance + threat model + pen test koordinasyon. Yarı zamanlı F4 başlangıç.

### 3.2 Ürün
- **Product Manager** — Roadmap, müşteri görüşme, PRD, stage-gate koordinatör.
- **Product Designer** — UX research, Figma, Cortex DS tasarım, brand book.

### 3.3 Go-to-Market
- **CRO / Head of Revenue (Ay 6+)** — Sinaps Enterprise satış lideri.
- **Sales/BD Lead** — Kuruculardan devralır pipeline.
- **SDR** — outbound, lead qual.
- **Founding CSM** — Y1'de tek CSM, "her şey"i yapar (onboarding, support, expansion).
- **Marketing Ops** — content, demand gen, paid ops.

### 3.4 Operasyon
- **COO (Ay 9+)** — finans, hukuk, İK koordinasyonu.
- **Finance/Ops Manager** — fatura, muhasebe arabirim, vendor.

---

## 4. Hiring Takvimi & Maliyet

### 4.1 Aylık Maliyet Tahmini (TR market + AB karışık)
| Rol | Y1 maaş (€/yıl, all-in) |
|--|--:|
| CTO (founder) | 0 (equity) |
| Senior Backend Eng | 70-90K |
| Senior Frontend Eng | 65-85K |
| SRE | 75-95K |
| Mobile Eng | 60-80K |
| Quality Eng | 55-75K |
| Security Eng (yarı zamanlı) | 35-50K |
| Product Manager | 65-85K |
| Product Designer | 55-75K |
| CRO | 100-140K + komisyon |
| Sales Lead | 50-70K + komisyon |
| SDR | 30-45K + komisyon |
| CSM | 45-65K |
| Marketing | 45-65K |
| COO | 90-120K |
| Finance/Ops | 40-55K |

### 4.2 Toplam Y1 Tahmini Burn (Personel)
- Çekirdek 6 (3 ay): ~€85K
- 9 kişi (3 ay): ~€140K
- 13 kişi (3 ay): ~€220K
- 16 kişi (3 ay): ~€280K
- **Yıllık personel:** ~€700-800K

### 4.3 Genel Burn (Personel + Cloud + Araç + Hukuk + Marketing)
- Y1 toplam: **~€1.0-1.2M**
- Y2 hedef: **~€2.0-2.5M** (~30 kişi)

---

## 5. Hiring Süreci

### 5.1 Adım
1. **JD + scorecard** (ürün/eng/satış için ayrı şablon)
2. **Sourcing:** LinkedIn + Wellfound + ağ referansı + TR teknik topluluklar
3. **Recruiter screen** (30dk)
4. **Hiring manager interview** (45dk)
5. **Take-home / case study** (eng için 4-6 saat opsiyonel)
6. **Onsite/remote panel** (3-4 görüşme: teknik, sistem tasarımı, takım uyumu, kurucu sohbet)
7. **Referans (2-3)**
8. **Teklif** + 14 gün düşünme

### 5.2 İlkeler
- **Strong hire veya no hire** — "ortalama" yok
- **Anti-bias:** structured scorecard, en az 1 paneliste underrepresented hire için
- **48 saatte feedback** her aşamada
- **Compensation transparent:** range JD'de

---

## 6. Onboarding (Yeni Çalışan)

### 6.1 Hafta 0
- Donanım gönderim (laptop, monitör opsiyonel)
- Hesap provisioning (Google, Slack, GitHub, Linear, Notion)
- Welcome paketi (Kokpit Group merch — sonra)

### 6.2 Hafta 1
- Şirket + ürün + mimari oryantasyon (4 oturum)
- Buddy ataması (mentor)
- 30-60-90 plan oluşturma
- Security training (zorunlu)
- 1:1 her gün (yöneticiyle)

### 6.3 30 gün
- İlk PR merged (eng) veya ilk demo (non-eng)
- Tüm modül sahipleriyle tanışma
- Müşteri çağrısı dinleme (en az 3)

### 6.4 90 gün
- Bağımsız ownership başlar
- Performans değerlendirme (light touch)

---

## 7. Performans & Gelişim

### 7.1 Yapı
- Çeyreklik OKR (kendi ürünümüzü kullanıyoruz)
- 1:1 haftalık (yöneticiyle 30dk)
- 6 aylık 360° feedback (light)
- Yıllık ücret/eşitleme görüşmesi

### 7.2 Equity & Hisse
- Pre-seed / seed sonrası ESOP havuzu %10-15
- Founding ekip için preferential
- 4 yıl vesting + 1 yıl cliff (standart)

---

## 8. Kültür Sözleşmesi

1. **Aşırı şeffaflık** — açık metrik, açık karar
2. **Yazılı düşünme** — "Konuşmaya çıkmadan önce dokümana yaz"
3. **Müşteri her şeyden önce** — herkes ayda 1 müşteri çağrısı
4. **Kendi ürünümüzü kullan** — Sinaps OKR/strateji şirket içi
5. **Hızlı iter, geç optimize et** — F1-F2 hız önemli, F3+ kalite
6. **Saygılı çatışma** — fikirde sert, insanda yumuşak
7. **Maaş + ödenek + saygı** — taban koşullar; perks değil

---

## 9. Remote-First İşletim

- **Çekirdek saat:** 11:00-15:00 İstanbul (overlap zorunlu)
- **Toplantı kuralı:** ajandasız toplantı yok; karar yazılır
- **Quarterly in-person:** 3 ayda 1 hafta İstanbul/Berlin/Lizbon (rotasyon)
- **Yıllık offsite:** 1 hafta (takım bonding)
- **Async default:** 24h yanıt makul, "şimdi" istisnai

---

## 10. Araçlar (Stack)

| İhtiyaç | Araç |
|--|--|
| İletişim | Slack |
| Doküman | Notion (wiki) + Linear (ticket) veya tek araçta Linear Docs |
| Repo | GitHub |
| Tasarım | Figma |
| Toplantı | Google Meet + Loom (async video) |
| HR/Payroll | Deel (multi-country) |
| Equity | Carta veya Pulley |
| Expense | Brex / Pleo / Wallester |
| Customer comms | Plain (support) + Slack Connect |
| Recruiting | Workable veya Ashby |
| Performance | Lattice (sonra) |
| Pulse | Officevibe veya Lattice |

---

## 11. Risk

| Risk | Önlem |
|--|--|
| Yetenek savaşı (Berlin, Amsterdam) | Erken hire, TR + AB karışık ekip, equity güçlü |
| Kurucu burnout | İlk SRE + PM erken alınır |
| Yanlış hire | 90 gün kararlı değerlendirme + mutual exit |
| Remote izolasyon | Çeyreklik in-person + buddy |
| Kültür sulanma | Onboarding kültür modülü + new-hire interview rubric |

---

## 12. Açık Sorular
- OS-1: Y1'de TR-only mı, AB hire açar mıyız? — Önerim: AB hire ay 4'ten itibaren, ama TR çoğunluk
- OS-2: ESOP havuzu yüzdesi? — Bağlı: yatırımcı VC sözleşmesi
- OS-3: Maaş bandı kamuya açık mı? — Önerim: dahili açık, dışarıya JD'de range
- OS-4: Founding CSM yerine kurucu CTO/CEO ay 6'ya kadar CS yapar mı? — Önerim: evet, customer empathy
