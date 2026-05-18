# P5 — GÜVENLİK · UYUM · THREAT MODEL
> Tarih: 2026-05-16 · Durum: TASLAK · Bağımlılık: D2, D6, P4

---

## 1. Güvenlik İlkeleri

1. **Zero-trust by default** — her istek doğrulanır, hiçbir iç servis "güvenilir" değil
2. **Defense in depth** — RLS (DB) + OPA (app) + WAF (edge) + Network policy (K8s)
3. **Secrets never in code** — Vault tek kaynak, env var sadece bootstrap
4. **Least privilege** — IAM, K8s RBAC, DB role, API scope hepsi minimum
5. **Auditable** — her güvenlik-ilgili aksiyon audit log + WORM
6. **Encrypt everything** — transit (TLS 1.3) + rest (AES-256) + field-level (PII)

---

## 2. Threat Model (STRIDE özet)

### 2.1 Saldırı Yüzeyi
- Public web (sinaps.app, kokpitim.com)
- Public API (api.sinaps.app)
- Mobile app (RN/Expo)
- Webhook outbound (müşteri server'ı)
- AI proxy (LiteLLM)
- Keycloak SSO
- Bizim admin paneli (admin.kokpitgroup.com)
- 3rd party API key tüketicileri

### 2.2 STRIDE × Aktör
| Aktör | Spoofing | Tampering | Repudiation | Info Disclosure | DoS | Elevation |
|--|--|--|--|--|--|--|
| Anonymous attacker | Brute force, phishing | XSS, CSRF | — | Tenant probing | Volumetric, app-DDoS | RCE attempt |
| Authenticated user (kendi tenant'ı) | — | API param tamper | — | Cross-tenant probe | Rate abuse | Privilege escalation (RBAC bypass) |
| Authenticated user (başka tenant) | Session steal | RLS bypass deneme | — | **Veri sızıntısı (en kritik)** | — | Federation abuse |
| Insider (çalışan) | Account abuse | Audit silme | "yapmadım" | Müşteri verisi okuma | — | Prod erişim genişletme |
| Supply chain | Paket zehri (npm/PyPI) | CI poisoning | — | Build artifact leak | — | Container breakout |

### 2.3 Önlem Matrisi (Top 12)
| # | Tehdit | Kontrol |
|--|--|--|
| T1 | Cross-tenant veri okuma | RLS + OPA + Tenant Isolation Suite CI |
| T2 | JWT tampering | RS256 + Keycloak public key + clock skew |
| T3 | API key sızıntısı | Hashed at rest, rotate, scope, last-used UI |
| T4 | SQL injection | SQLAlchemy bound params zorunlu, raw SQL ban (lint) |
| T5 | XSS | React/Next default escape + CSP strict + DOMPurify (rich text) |
| T6 | CSRF | SameSite=Strict cookie + double-submit token |
| T7 | RCE (file upload) | Mime sniff + virus scan + execve disabled in S3 |
| T8 | DDoS | Cloudflare/Cloud Armor + rate limit (Redis) + autoscale cap |
| T9 | Insider abuse | 2-person rule (prod) + audit + just-in-time access (Vault) |
| T10 | Supply chain | SBOM (Syft) + signed images (cosign) + Renovate weekly |
| T11 | Container escape | Distroless image + non-root + seccomp + read-only fs |
| T12 | Secrets in logs | Log scrubber + pre-commit scan (gitleaks) + Vault audit |

---

## 3. Kimlik & Erişim

### 3.1 Müşteri Kullanıcı
- Keycloak SSO (OIDC, RS256)
- Password policy: min 12 char, blocklist (Pwned Passwords), no reuse 5
- MFA zorunlu: Sinaps Enterprise/Enterprise+ (TOTP + WebAuthn), Kokpitim opsiyonel
- Session: 12h, idle 30dk
- SSO federation: SAML/OIDC (Sinaps Enterprise — müşteri IdP)

### 3.2 Çalışan Erişimi
- Keycloak (ayrı realm: `staff`)
- MFA zorunlu (WebAuthn tercih)
- SSO-only (Google Workspace federation veya Okta)
- Prod erişim: **Just-in-Time** Vault üzerinden, max 2h, audit'li
- 2-person rule: DB direct query, vault unseal, KMS access

### 3.3 Service-to-Service
- mTLS K8s mesh (Linkerd veya Istio Ambient)
- Service account JWT (kısa ömür)
- Workload identity (no shared secret)

---

## 4. Veri Koruması

### 4.1 Sınıflandırma
| Sınıf | Örnek | Tedbir |
|--|--|--|
| **Public** | Marketing site, paket fiyat | TLS yeterli |
| **Internal** | Tenant adı, paket | Standart RLS |
| **Confidential** | OKR, KPI, strategy | RLS + audit |
| **Sensitive** | E-posta, telefon, IP | RLS + field encryption + scrub log |
| **Regulated** | Sağlık, finansal kişisel | RLS + customer-managed key (CMK) + DPA özel |

### 4.2 Şifreleme
- **In transit:** TLS 1.3, HSTS preload, certificate pinning (mobile)
- **At rest:** AES-256-GCM (Postgres, S3, NATS disk)
- **Key mgmt:** Vault (ADR-08) — auto-unseal cloud KMS
- **Field-level:** PII alanları Vault transit engine (e-posta, telefon, freetext freetext)
- **CMK (Customer-Managed Key):** Enterprise+ opsiyon — müşteri kendi KMS anahtarı

### 4.3 Veri Saklama
- Operasyonel: aktif data
- Audit: 90 gün hot (Postgres) + 7 yıl WORM (S3 Object Lock)
- Backup: 30 gün hot + 1 yıl cold
- Hard delete: GDPR/KVKK talebi → 30 gün, anonymize tercih

### 4.4 Veri Residency
- AB müşteri: AB bölgesi (Frankfurt veya Amsterdam)
- TR müşteri: TR + AB ikincil (KVKK uyumlu)
- ABD müşteri: us-east
- Sub-processor: aynı bölge zorunlu
- Cross-border transfer: SCC (Standard Contractual Clauses) imzalı

---

## 5. Uyum Yol Haritası (Compliance)

### 5.1 KVKK (Türkiye — birinci öncelik)
- VERBİS kayıt (kurum bilgisi)
- Aydınlatma metni (web + uygulama)
- Açık rıza formları (gerektiğinde)
- VERBİS sicil + Politikalar (saklama, imha, güvenlik)
- DPO (Veri Sorumlusu) atama — F1 sonu
- Hak başvuru süreci (30 gün)
- **Hedef:** F1 sonu uyum

### 5.2 GDPR (AB — Sinaps zorunlu)
- ROPA (Record of Processing Activities)
- DPIA (Data Protection Impact Assessment) — yüksek risk işlemler
- DPA + SCC (Standard Contractual Clauses)
- DPO (Avrupa Temsilcisi — gerektiğinde)
- Privacy by Design — kayıt
- Data breach notification: 72 saat
- **Hedef:** F2 sonu uyum dosyası, F4 sonu external review

### 5.3 SOC 2 Type I → Type II
- F1: Kontrol envanteri, policy yazımı (Trust Services Criteria)
- F2: Tooling (Vanta veya Drata) onboarding
- F3: Type I audit (point-in-time)
- F4+6 ay: Type II audit (6-12 ay observation window)
- **Hedef:** Type I report 12. ayın sonunda; Type II 18. ayın sonunda

### 5.4 ISO 27001
- Stage 1 audit hedefi: F4 sonu (sertifika ~6 ay sonra)
- ISMS dokümantasyonu Vanta ile paralel SOC2 ile sinerji

### 5.5 İleride (F5+)
- HIPAA (sağlık tenant'ları)
- ISO 27701 (privacy)
- C5 (Almanya cloud güvenliği)
- ENS (İspanya kamu)
- TX-RAMP (US Texas kamu)

### 5.6 Sertifikasyon Maliyeti
- KVKK: dahili çaba, ~€5K dış danışman
- SOC2 Type I: ~€15-25K (denetçi) + ~€10K platform (Vanta)
- ISO 27001: ~€20-30K
- Yıllık idame: ~€30K toplam

---

## 6. Güvenlik Operasyonu

### 6.1 Vulnerability Management
- Container scan: Trivy CI'da her build + nightly
- Dependency scan: Renovate weekly + Snyk free tier
- Patch SLA: Critical 7gün / High 30gün / Medium 90gün / Low 180gün
- SBOM (Syft) her release, kayıt

### 6.2 Penetration Test
- F2 sonu: internal pen test (mavi takım)
- F4 sonu: external pen test (3rd party)
- Yıllık tekrar
- Bug bounty: F4+6 ay, başlangıç scope sınırlı, HackerOne veya Intigriti

### 6.3 Security Logging & SIEM
- Loki tüm log
- Belirli pattern → güvenlik kanalı (auth fail, RLS bypass attempt, vault deny)
- F3+: dedicated SIEM (Wazuh self-host veya Panther)

### 6.4 Incident Response
**Plan:**
1. Detect (alarm/raporlama)
2. Triage (sev assign)
3. Contain (etkilenen kapsam izole)
4. Eradicate (kök neden temizle)
5. Recover (servis restore)
6. Postmortem + customer comm
7. Lessons learned → runbook update

**Customer breach notification:**
- 72 saat içinde (GDPR/KVKK)
- Şablon hazır: ne, ne zaman, etkilenen kapsam, alınan önlem, müşteri aksiyonu

### 6.5 Phishing/Awareness
- Çalışan training: aylık 15dk (KnowBe4 veya inhouse)
- Phishing simulation: çeyreklik
- Onboarding security training: F1'den itibaren zorunlu

---

## 7. Gizlilik (Privacy by Design)

### 7.1 Data Minimization
- Sadece gerekli alanlar toplanır
- Form alanları opsiyonel default
- 3rd party SDK denetimi (analytics, support widget) — minimum

### 7.2 Kullanıcı Hakları (DSAR)
- Sinaps admin panelinde: data export, data deletion, consent log
- 30 gün yanıt süresi (GDPR/KVKK)

### 7.3 Çerez / Tracking
- Strict opt-in (AB)
- Marketing cookie ayrı, default off
- AI Concierge: ayrı consent (LLM provider'a veri akar)

---

## 8. Güvenlik Header'ları & Web Hardening
P4'te uygulamada, burada özet referans:
```
Strict-Transport-Security · X-Content-Type-Options · X-Frame-Options · Referrer-Policy · CSP · Permissions-Policy
COOP / COEP / CORP (Spectre mitigation)
```

---

## 9. Compliance Documentation Set
F1-F4 boyunca üretilecek dokümanlar:
- Information Security Policy
- Acceptable Use Policy (çalışan)
- Access Control Policy
- Data Classification & Handling Policy
- Incident Response Plan
- Business Continuity Plan
- Vendor Risk Management Policy
- Vulnerability Management Policy
- Encryption Policy
- Logging & Monitoring Policy
- Change Management Policy
- HR Security Policy
- Asset Management Policy
- Backup Policy
- Privacy Policy (public)
- DPA template
- Sub-processor list (public)

Hepsi `docs/security/` altında, versiyonlu, yıllık review.

---

## 10. Açık Sorular
- OS-1: DPO inhouse mu dış mı? — Önerim: F1'de outsource (€600/ay), F4+ inhouse
- OS-2: Vanta vs Drata? — Önerim: Drata (daha modern UI, benzer fiyat)
- OS-3: Bug bounty F4 erken mi? — Daha güvenli: F5+, yeterli olgunluk
- OS-4: Sinaps Enterprise+ "BYO Encryption Key" (HYOK) ne zaman? — F5+
- OS-5: AB Cloud Code of Conduct adhere edelim mi? — Önerim: evet, F3
