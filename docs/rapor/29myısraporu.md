# KOKPİTİM — Kullanıcı Deneyimi & Yeni Özellik Raporu
**Tarih:** 2026-05-29  
**Kapsam:** Kullanıcı tarafı / görsel iyileştirmeler ve yeni özellik fikirleri (backend refactor hariç)

---

## 1. UI Tutarsızlıkları (Hızlı Kazanımlar)

| # | Konu | Konum | Effort | Etki |
|---|------|-------|--------|------|
| A1 | Inline `onmouseover` / `onmouseout` handler temizliği | `ui/templates/platform/base.html:309-325`, `388-391` | S | M |
| A2 | "Proje Yönetimi" sidebar linki eski iskelet sayfaya gidiyor; `project/list.html`'e yönlendir | `base.html` sidebar | S | H |
| A3 | K-Radar KP sayfası `mc-page-header` standardı dışı; inline `style="..."` | `ui/templates/platform/k_radar/kp.html:1-31` | M | L |
| A4 | Analiz modülünde hardcoded renk (#fef3c7, #ecfeff) ve inline flex | `ui/templates/platform/analiz/index.html:13-100` | M | M |
| A5 | Bazı modallar hâlâ SweetAlert (modal olarak) — `mc-modal-overlay`'e çevrilmeli | Süreç & Bildirim formları | M | M |

---

## 2. Eksik Etkileşimler

### B1. Komut Paleti — `Ctrl+K`
Topbar arama + 15+ modül arası hızlı geçiş. Strateji / KPI / proje / süreç adıyla atla.  
**Konum:** `base.html` topbar + yeni `ui/static/platform/js/command-palette.js`  
**Effort:** M · **Etki:** H

### B2. Favoriler & Son Ziyaret Edilenler
Masaüstüne pin'lenebilir widget. Tekrarlı iş akışlarında ~40% hızlanma.  
**Konum:** `masaustu/index.html` + localStorage/profile API  
**Effort:** M · **Etki:** H

### B3. Tablo Sütun Yönetimi
Admin kullanıcı tablosunda sütun gizle/göster, sıra değiştir, kaydedilmiş görünüm.  
**Konum:** `admin/users.html:75-100`  
**Effort:** M · **Etki:** M

### B4. Toplu İşlemler (Bulk Action Toolbar)
`project/list.html`'de checkbox başlangıcı var; sticky toolbar yok (Sil / Atama / Dışa aktar).  
**Effort:** M · **Etki:** H

### B5. Form Inline Validasyon
HTML5 Constraint API + `aria-invalid` + alan altı hata span'i. Şu an hatalar modal'la dönüyor.  
**Effort:** M · **Etki:** M

### B6. Zenginleştirilmiş Boş Durumlar
"Başlamak için" yönlendirme + örnek şablon linki. SP `sp-card-help-json` yaklaşımı diğer modüllere yayılmalı.  
**Konum:** `sp/index.html:422-431`, `bildirim/index.html:73-77`, `surec/index.html`  
**Effort:** S · **Etki:** H

---

## 3. Görselleştirme Fırsatları

### C1. Strateji Ağırlık Heatmap'i
K-Vektör ağırlığı sadece sayı; bubble/heatmap eklenmeli (boyut=ağırlık, renk=olgunluk).  
**Konum:** `sp/index.html:316-420` · **Effort:** M

### C2. KPI Mini Sparkline
Süreç listesinde "{{ p.kpis|length }} PG" yanına son 3 ay trend mini-çizgisi.  
**Konum:** `surec/index.html:86-100` · **Effort:** M

### C3. Proje Risk Donut
RAID açık sayısının yanında Risk/Varsayım/Sorun dağılım donut'u.  
**Konum:** `project/list.html:62-71` · **Effort:** S

### C4. Süreç Olgunluk Radarı
KP/KPR boyutlarında (Olgunluk, Baskı, Kapasite, SLA, Benchmark) radar.  
**Konum:** `k_radar/kp.html` · **Effort:** M

### C5. Bireysel Karne Progress Ring
Sayfa üstüne PG başarı % ve faaliyet tamamlanma % SVG halkaları.  
**Konum:** `bireysel/karne.html` · **Effort:** S

---

## 4. Çapraz Modül Entegrasyonu (Yeni Özellikler)

### D1. Strateji ↔ Proje Hizalama Matrisi
Heatmap: satır=ana strateji, sütun=proje, hücre=alignment %.  
**Konum:** `sp/strateji_proje_matrix.html` (yeni) · **Effort:** M · **Etki:** H

### D2. KPI ↔ Proje Çapraz Analiz
Sunburst/alluvial diagram: hangi proje hangi KPI'yi nasıl etkiliyor.  
**Konum:** `k_rapor/` yeni rapor · **Effort:** L · **Etki:** H

### D3. Bildirim Merkezi Filtre & Gruplama
Tip / Kaynak / Okunma durumu sidebar filtre.  
**Konum:** `bildirim/index.html` · **Effort:** M

### D4. "Benim Görevlerim" Birleşik Widget
Proje görevleri + bireysel faaliyetler + süreç aktiviteleri tek union sorgu.  
**Konum:** `masaustu/index.html` · **Effort:** M · **Etki:** H

### D5. Küresel Arama
Topbar dropdown: strateji + KPI + proje + süreç + kullanıcı.  
**Effort:** L · **Etki:** H

---

## 5. Kullanıcı Verimliliği

### E1. Klavye Kısayolları
`?` yardım, `Ctrl+K` palet, `j/k` liste gezinme, `s` favori, `g s` → strateji vb.  
**Effort:** M

### E2. Sunucuya Kaydedilen Tema Tercihi
Dark mode şu an sadece localStorage. Profil tablosuna `theme` sütunu → çoklu cihazda konsistans.  
**Effort:** S

### E3. Inline Düzenleme
Strateji/KPI/proje başlıkları için click-to-edit. Modal açmadan rename.  
**Effort:** M

---

## 6. Onboarding & Yardım

### F1. Bağlamsal Yardım Popover'ları
`sp-card-help-json` yaklaşımı tüm `mc-card-header`'lara yayılmalı. Kule sistemi (ERTELENDİ E1) aktif edilebilir.  
**Effort:** L

### F2. Örnek Veri Üreteci
Yeni kurum için "Demo veri oluştur" butonu → otomatik strateji + KPI + proje fikstürü.  
**Effort:** M · **Etki:** H

### F3. Modül Bazlı Rehberli Tur
Kule reactivation + `data-kule-tour-key`.  
**Effort:** L

---

## 7. Mobil & Responsive

### G1. Mobil Fallback Görünümler
Gantt → liste, Network grafik → ağaç görünümü. Şu an horizontal scroll bile zor.  
**Konum:** `project/gantt.html`, `k_radar/strateji_haritasi` · **Effort:** M

---

## 8. Dışa Aktarma & Raporlama

### H1. Eksik PDF/Excel Export
Strateji listesi, süreç ağacı, KPI tabloları, bireysel faaliyetler.  
**Effort:** M · **Etki:** H

### H2. Zamanlanmış Raporlar
Haftalık özet / sabah özeti / risk raporu e-posta abonelikleri.  
**Konum:** Ayarlar → "Zamanlanmış Raporlar" · **Effort:** L

---

## Öncelik Tavsiyesi

**Sprint 1 (hızlı kazanım):** A1, A2, B6, C3, C5, E2  
**Sprint 2 (UX sıçraması):** B1 (Ctrl+K), B2 (favoriler), D4 (benim görevlerim), B4 (toplu işlem)  
**Sprint 3 (görselleştirme):** C1, C2, C4, D1  
**Sprint 4 (büyük yatırım):** D2, D5, F3, H2

---

*Tarama kapsamı: 90+ Jinja şablon, 50+ JS dosyası, 7 ana modül.*
