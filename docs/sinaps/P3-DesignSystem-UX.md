# P3 — DESIGN SYSTEM · UX AKIŞLARI · BRAND BOOK
> Tarih: 2026-05-16 · Durum: TASLAK · Bağımlılık: D5, D8

---

## 1. Design System: "Cortex DS"

Sinaps + Kokpitim'in ortak design system'i. Kokpit Group umbrella'sı altında, iki ürünün **temaları** olur.

### 1.1 Temel Yapı
- **Foundation:** Shadcn/ui (Radix primitives) + Tailwind CSS
- **Token sistemi:** CSS variables, semantic naming (`--color-bg-primary`, değil `--color-blue-500`)
- **Tema:** `cortex-light`, `cortex-dark`, `cortex-sinaps-dark` (premium), `cortex-kokpitim`
- **Paket:** `@sinaps/ui` (D5'te tanımlı)

### 1.2 Token Katmanları
```
1. Primitive tokens  → --color-blue-500, --space-4, --font-size-md
2. Semantic tokens   → --color-bg-default, --color-text-muted
3. Component tokens  → --button-primary-bg, --card-shadow
```
Tema değişikliği yalnız katman 2'de yapılır.

### 1.3 Renk Sistemi
**Kokpitim teması (sıcak):**
- Brand primary: turuncu spektrum (#FF6B35)
- Brand secondary: lacivert (#1E3A8A)
- Tone: enerjik, dostane

**Sinaps teması (soğuk, premium):**
- Brand primary: derin lacivert (#0B1F3A)
- Brand accent: neon mavi-mor (#6366F1)
- Tone: kurumsal, güçlü, derin

**Ortak:**
- Success #16A34A · Warning #D97706 · Danger #DC2626 · Info #0284C7
- Yeşil/Sarı/Kırmızı KPI status (color blind safe, ek olarak ikon+desen)
- Karanlık tema **birinci sınıf** (Sinaps default)

### 1.4 Tipografi
- Latin: **Inter** (free, geniş weight)
- Arabic: **IBM Plex Sans Arabic**
- CJK: **Noto Sans CJK** (gerektiğinde)
- Scale: 12/14/16/18/20/24/30/36/48 px
- Line height: tight (1.2) / normal (1.5) / relaxed (1.75)

### 1.5 Spacing & Layout
- 4px taban grid: 4/8/12/16/24/32/48/64
- Container: 1280px max, sidebar 256px sabit, içerik responsive
- Breakpoint: sm 640 / md 768 / lg 1024 / xl 1280 / 2xl 1536

### 1.6 Bileşen Envanteri (MVP — 35 bileşen)

**Foundation (10):**
Button, IconButton, Input, Textarea, Select, Combobox, Checkbox, Radio, Switch, Slider

**Layout (5):**
Card, Sheet, Sidebar, AppShell, Splitter

**Feedback (5):**
Toast (SweetAlert2 yerine native), Banner, Alert, Skeleton, Spinner

**Disclosure (4):**
Dialog (modal), Drawer, Popover, Tooltip

**Data (6):**
DataTable (sortable, filterable, virtualized), Pagination, EmptyState, KPITile, ProgressBar, Stat

**Navigation (3):**
Tabs, Breadcrumbs, CommandPalette (Cmd+K)

**Domain-specific (2):**
HeatMatrix (5×5 risk matrisi), GanttRow (initiative roadmap)

> **Modal standardı:** D-KURALLAR §5'teki `mc-modal-*` yapısı Sinaps'a taşınmaz; Cortex Dialog/Drawer yenidir. Eski kural Kokpitim için geçerliliğini korur.

### 1.7 İkon Sistemi
- **Lucide React** — birincil
- Domain-specific (Hoshin matrix, EFQM wheel) inhouse SVG, `@sinaps/icons`
- 16/20/24 px standart; stroke 1.5

### 1.8 Motion & Etkileşim
- Süre: 150ms (micro) · 300ms (transition) · 500ms (page)
- Easing: `ease-out` (giriş), `ease-in` (çıkış)
- `prefers-reduced-motion` saygılı
- Loading: skeleton > spinner

### 1.9 Erişilebilirlik
- WCAG 2.2 AA minimum, AAA hedef (kontrast, klavye, ekran okuyucu)
- Tüm interactive en az 44×44 px hit area
- Focus ring görünür ve özelleştirilebilir
- Otomatik test: axe-core CI'da

### 1.10 RTL Desteği
- Tailwind `rtl:` variant + `dir="rtl"` HTML attr
- İkon yönü flip (chevron, arrow) otomatik
- Test: Arapça tenant'ta tüm sayfa snapshot

---

## 2. Kritik UX Akışları (MVP — 12 journey)

Her akış için: persona, giriş noktası, adım sayısı, başarı kriteri.

### J1. Organization Provisioning (bizim admin)
P10 SRE · 6 adım · 5 dakika
1. Bizim admin login → "New Organization" wizard
2. Org adı + brand seçimi (Kokpitim/Sinaps) + tier
3. Root tenant slug + locale + timezone
4. Initial admin user e-posta
5. Paket atama + modül seçimi
6. "Create" → Keycloak realm + DB seed + invite e-posta otomatik

### J2. First-time Tenant Admin Onboarding
P4 Tenant Admin · 8 adım · 15 dakika
1. Invite e-posta → set password (Keycloak)
2. MFA setup (zorunlu)
3. Welcome modal: "What brings you here?" (4 seçenek)
4. Locale + timezone confirm
5. Org logo upload
6. İlk 3 kullanıcı davet (toplu CSV opsiyonu)
7. Paket modülleri tour (her modül 1 ekran tanıtım)
8. Dashboard'a iniş — "Create your first plan" CTA

### J3. Strategic Plan Creation
P5 PMO · 7 adım · 20 dakika
1. Strategy → Plans → "+ New Plan"
2. Plan adı + dönem (2026-2035)
3. Vision/Mission/Values (multi-lang accordion)
4. Pillar (H1-Hn) ekle — drag-drop sıralama
5. Her pillar'a strateji ekle (main + sub)
6. SWOT/PESTEL/Porter5 analysis (opsiyonel, tab'lı)
7. Save → Plan status: draft

### J4. OKR Cascade Setup
P5 PMO · 6 adım · 30 dakika
1. Plan → OKR tab → "Cascade Builder"
2. Org level OKR yarat (objective + 3-5 KR)
3. "Cascade to BU" — alt tenant seç, otomatik child OKR taslak
4. Her BU sahibine atama
5. Bildirim gönder ("Sizden KR detaylandırma bekleniyor")
6. Çift onaylı (PMO + BU owner) → published

### J5. Hoshin X-Matrix Workshop
P5 PMO · 5 adım · 60-90 dk (workshop modu)
1. Plan → "Hoshin X-Matrix"
2. 4-quadrant editor (breakthrough / annual / improvements / metrics / owners)
3. Catchball channel başlat (workshop / digital form)
4. Round-trip onay (3 round default)
5. Lock → Initiative'lere otomatik dönüşüm önerisi

### J6. KPI Setup & Tracking
P5/P6 · 5 adım · 10 dk/KPI
1. KPI Master → "+ New KPI"
2. Code, ad, formula, unit, frequency, eşikler
3. Owner ata
4. Strategy/Process'e bağla
5. İlk ölçüm (manuel / import / API)

### J7. Stage-Gate Decision
P5 PMO · 4 adım · 15 dk
1. Initiative → "Gates" tab → G1
2. Criteria checklist (gate template)
3. Reviewer'lara onay isteği
4. Decision: pass / hold / kill / recycle + notlar

### J8. Risk Register Update
P7 Risk Yöneticisi · 6 adım · 10 dk/risk
1. Risk → Register seç
2. "+ New Risk" — kod, başlık, kategori
3. Inherent likelihood × impact → heatmap pozisyonu
4. Linked strategy/process/initiative
5. Control + KRI ekle
6. Save → KRI threshold breach'inde otomatik bildirim

### J9. TCFD Report Generation
P8 ESG Lideri · 4 adım · ~1 saat (veri toplama dışı)
1. ESG → TCFD → "New Report" (yıl seç)
2. 4 pillar form (governance / strategy / risk / metrics)
3. KPI/Risk auto-pull (var olanlardan)
4. Generate → PDF + JSON export

### J10. AI Concierge "Stratejik Soru"
Her persona · 2 adım · 1-3 dk
1. Cmd+K → "Ask Cortex" → soru yaz
2. AI yanıt (RAG ile kendi datasından) + kaynak referansları

### J11. Mobile OKR Check-in
P9 Bireysel · 3 adım · 30 saniye
1. Mobile app push notification → tap
2. KR slider güncelle + confidence
3. Optional 1-cümle yorum → kaydet

### J12. Tenant Switch (Federasyon)
P3 Holding Admin · 2 adım · 5 saniye
1. App header'da tenant picker → arama/seçim
2. Context değişir, dashboard yenilenir, breadcrumb güncellenir

---

## 3. UX İlkeleri (Cortex Pattern Library)

1. **Empty state her zaman aksiyon önerir** — "Henüz bir şey yok" değil, "İlk OKR'nızı oluşturun + nasıl yapılır"
2. **Optimistic UI** — kaydetme UI'ı block etmez; rollback ile geri al
3. **Inline edit > modal** — tablolarda hücre düzenleme, modal son çare
4. **Keyboard-first** — Cmd+K her yerde; Tab navigation tam
5. **Multi-lang content** — her translatable input'un dil sekmesi yan yana
6. **Tenant context her zaman görünür** — header'da kim/nerede olduğu net
7. **Audit trail bir tık ötede** — her kayıtta "history" drawer
8. **AI önerisi yardımcıdır, otoriter değildir** — AI çıktısı her zaman "kaynak" + "düzenle" düğmesi
9. **Heat / status renkleri ikon ile destekli** — daltonizm
10. **Yıkıcı aksiyon iki adım** — onay diyalog + yazarak tip ("DELETE")

---

## 4. Brand Book Outline (D8 ekstansiyonu)

### 4.1 Bölümler
1. Marka Mimarisi (D8 özet)
2. Logo varyantları — Kokpit Group, Kokpitim, Sinaps (yatay, dikey, ikonlu, mono)
3. Renk paleti (her marka)
4. Tipografi
5. Ton & dil rehberi (Kokpitim TR yakın, Sinaps EN kurumsal)
6. Görsel stil (fotoğraf, illüstrasyon, ikon)
7. Sunum şablonları (Google Slides + Keynote)
8. Sosyal medya şablonları (LinkedIn, X)
9. E-posta imza şablonu
10. Yasak kullanımlar (logo distorsiyon, yanlış renk)

### 4.2 Üretim Süreci
- F0 sonu: marka studio brief (in-house tasarım önerisi)
- F1 ortası: 3 yön sunumu → seçim
- F1 sonu: brand book v1 PDF + Figma library

---

## 5. Araç & Süreç

| Süreç | Araç |
|--|--|
| Design source | Figma (team plan) |
| Token sync | Figma Tokens → Style Dictionary → `@sinaps/ui` |
| İkon | Lucide + inhouse SVG → Figma library |
| Prototype | Figma + opsiyonel Framer (motion demo) |
| User research | Maze (unmoderated test) + Calendly (moderated 1:1) |
| Annotation/handoff | Figma Inspect |
| Visual regression | Chromatic veya Percy |

---

## 6. Önemli Eksikler (planlanmamış)
- 12 journey haricinde 30+ orta seviye akış var (admin, settings, billing, etc.) — F2 öncesi yazılmalı
- Empty state copy seti — tek tek yazılmalı, AI yardımı kabul (sonra revize)
- Onboarding email serisi (8-10 e-posta) — copywriter
- Help center makaleleri (~150 madde) — F3-F4 sürecinde

---

## 7. Açık Sorular
- OS-1: Figma team plan abonelik (≈€150/ay) F1'de gerekli mi yoksa Free ile başlanır mı?
- OS-2: Marka studio dış mı (~€20-40K) içeride mi?
- OS-3: SweetAlert2 Sinaps'ta yer alır mı? — Önerim: hayır, Cortex Toast yeterli
- OS-4: Dark theme default mı (Sinaps) yoksa user preference mı?
