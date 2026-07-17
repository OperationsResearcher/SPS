# Analitik & Rapor Araçları — Tam Envanter

> Amaç: Rapor + analitik araçlarının SIRALI TAM listesi. Sonra "nasıl bölmeliyiz" tartışması.
> Yöntem: 6 modülün hub tanımları + route'ları + template'leri tarandı (elle değil, ölçümle).
> Tarih: 2026-07-17

---

## Ölçek — 6 modül, ~120 kullanıcı-görünür araç, 358 route

| Modül | Route | Kullanıcının gördüğü ad | Rolü |
|---|---:|---|---|
| **sp** | 127 | "Stratejik Planlama" | Strateji araçlarını ÜRETİR + yönetir |
| **raporlar** | 101 | (K-Radar hub'dan linkli) | Zengin rapor/panel/AI araçları |
| **k_radar** | 88 | "K-Radar" + "K-Analiz" | TEŞHİS — canlı skorlar, hub |
| **k_rapor** | 35 | (K-Radar hub'dan linkli) | Kurum-geneli konsolidasyon + export |
| **analiz** | 7 | "Performans Analitiği" | Süreç bazlı health/trend/forecast/anomali |

**Kritik:** Bu modüller ayrı DEĞİL — K-Radar hub'ı hepsinin araçlarını tek sayfada
linkliyor. Kullanıcı 5 menü girişi görüyor ama araçlar 6 modüle dağılmış ve
bazıları birden çok yerde beliriyor.

---

## TAM LİSTE — kategoriye göre (araç · nerede yaşıyor · örtüşme)

### A. Strateji Formülasyon Araçları (SP'nin sahibi olduğu)
Bunlar SP'de ÜRETİLİR; K-Radar/KS'de gösterilir; K-Rapor'da raporlanır. **3 katman.**

| Araç | Sahip | Ayrıca görünür |
|---|---|---|
| SWOT Analizi | sp | K-Radar/KS, K-Rapor, raporlar/swot-trend |
| TOWS Matrisi | sp | K-Radar/KS, K-Rapor |
| PESTEL Analizi | sp | K-Radar/KS, K-Rapor |
| Porter 5 Güç | sp | K-Radar/KS, K-Rapor |
| VRIO Analizi | sp | K-Radar (VRIO Portföy), raporlar/vrio_portfoy |
| GAP Analizi | sp | K-Radar/KS |
| BSC (Dengeli Karne) | sp | K-Radar/KS |
| OKR | sp | K-Radar (OKR Akışı), raporlar/okr_cascade |
| Blue Ocean (Mavi Okyanus) | sp | — |
| Hoshin X-Matrisi | sp | — |
| Ansoff / BCG | sp/k_radar_ks | — |
| Strateji Haritası | sp | K-Radar |
| Strateji × Proje Matrisi | sp | K-Radar |
| Senaryolar | sp | — |
| Girişimler (Initiatives) | sp | K-Radar (balon grafiği, yol haritası), raporlar |
| Vizyon / Misyon / Değerler | sp | — |

### B. Süreç & Performans Analitiği (KP katmanı)
| Araç | Sahip | Ayrıca |
|---|---|---|
| Süreç & PG Tablosu | k_radar/kp | k_rapor |
| CMMI/Süreç Olgunluk Isı Haritası | k_radar/kp | raporlar/cmmi_heatmap |
| Darboğaz Analizi | k_radar/kp | — |
| Değer Zinciri | k_radar/kp | — |
| Pareto | k_radar/kp | — |
| SLA | k_radar/kp | — |
| Benchmark | k_radar/kp | raporlar/sektor_benchmark |
| OEE | k_radar/kp | — |
| VSM (Değer Akış Haritası) | k_radar/kp | — |
| Kapasite | k_radar/kp | — |
| 7 Muda (İsraf) | k_radar/kp | raporlar/muda_analizi |
| **Performans Analitiği (health/trend/forecast/anomali)** | **analiz** | k_rapor, k_radar örtüşür |

### C. Proje / Portföy Analitiği (KPR katmanı)
| Araç | Sahip | Ayrıca |
|---|---|---|
| CPM (Kritik Yol) | k_radar/kpr | — |
| EVM (Kazanılmış Değer) | k_radar/kpr | k_rapor, raporlar/pg_proje_etki |
| Proje Riski | k_radar/kpr | — |
| Kaynak Kapasitesi | k_radar/kpr | — |
| Gantt | k_radar/kpr | — |
| Girişim Balon Grafiği | k_radar/raporlar | initiative_bubble |
| Girişim Yol Haritası | k_radar/raporlar | initiative_roadmap |

### D. Risk & Uyarı
| Araç | Sahip | Ayrıca |
|---|---|---|
| Risk Isı Haritası (5×5) | k_radar/risk | raporlar/risk_heatmap |
| RAID Risk Yönetimi | k_radar/risk | — |
| Aktif Uyarılar | k_radar | k_rapor |
| AI Erken Uyarı | k_radar/raporlar | early_warning |
| ML Anomali (İzolasyon Ormanı) | raporlar/ml_anomaly | analiz (z-score), k_rapor |

### E. Kurumsal / Yönetici Panelleri
| Araç | Sahip |
|---|---|
| Kurumsal Performans | k_rapor |
| K-Vektör Skoru / Çarpıklık | k_radar/raporlar (kv_carpiklik) |
| CFO Paneli | raporlar/cfo_dashboard |
| COO Paneli | raporlar/coo_dashboard |
| CHRO Paneli | raporlar/chro_dashboard |
| Departman Performans | raporlar/departman_performans |
| Yönetici Liderlik Skoru | raporlar/yonetici_liderlik |
| Çeyreklik Değerlendirme | raporlar/quarterly_review |
| Sabah Operasyonel Özeti | raporlar/sabah_ozeti |

### F. Paydaş / Rekabet / Dış Analiz
| Araç | Sahip |
|---|---|
| Paydaş Haritası | k_radar/cross |
| Rekabet & A3 | k_radar/cross |
| Kurum Kıyas | k_rapor |
| Sektörel Plan Paketleri | raporlar/sektorel |
| AI Sektör Benchmark | raporlar/sektor_benchmark |

### G. Bireysel / İK
| Araç | Sahip |
|---|---|
| Bireysel Performans/Karne | k_radar/raporlar (bireysel_karne_batch) |
| Bireysel Hedef Hizalama | k_radar/raporlar (bireysel_hizalama) |
| Sorumlu Analizi | k_radar/raporlar |
| Departman Performans | raporlar |

### H. ESG / Sürdürülebilirlik
| Araç | Sahip |
|---|---|
| ESG Yıllık Rapor | raporlar/esg_rapor |
| ESG Yönetim | raporlar/esg_yonetim |
| Karbon Ayak İzi Trendi | raporlar/carbon_trend |

### I. Denetim / Uyum / Veri Kalitesi
| Araç | Sahip |
|---|---|
| Denetim Kayıtları | k_rapor |
| Denetim Çıktı Paketi | raporlar/audit_paketi |
| 2FA Kullanım Raporu | raporlar/iki_fa |
| Veri Durumu / Veri Kalitesi | k_radar/k_rapor/raporlar |
| Onay Zinciri | raporlar/onay_zinciri |
| Uyum (Katkı Ağacı) | k_rapor |

### J. AI Araçları
| Araç | Sahip |
|---|---|
| AI Strateji Danışmanı | raporlar/ai_danisman |
| AI Koç | raporlar/ai_coach |
| AI Strateji Hikayeleştirici | raporlar/strateji_hikayesi |
| AI Sunum Üretici | raporlar/ai_sunum |
| AI Doğal Dil Sorgu | raporlar/nlp_query |

### K. Görselleştirme / Anlatı
| Araç | Sahip |
|---|---|
| Stratejik Akış Haritası | k_radar/sp (flow) |
| Sunburst (Hiyerarşi) | raporlar/sunburst |
| Yıllar Arası Evrim Filmi | raporlar/evrim_filmi |
| Hizalama Sankey | raporlar/hizalama_sankey |

### L. Çıktı / Dağıtım (araç değil, kanal)
| Kanal | Sahip |
|---|---|
| Excel Export | k_rapor |
| PDF Export (executive summary) | k_rapor |
| Slack/Teams/Discord bildirim | k_rapor |
| E-posta Digest | k_rapor |
| Yatırımcı Sunumu (PPTX) | raporlar/yatirimci_sunum |
| Stratejik Yıllık Kitap | raporlar/stratejik_yillik |
| BI Connector (Power BI/Tableau) | raporlar/bi_connector |
| Mobil | raporlar/mobile |

---

## KAPSAM KANITI — hiçbir araç dışarıda kalmadı (çapraz kontrol)

> Kullanıcı uyarısı: "Dışarıda bıraktığımız hiçbir araç kalmamalı." Bu tablo, TÜM
> modüllerin TÜM kullanıcı-görünür sayfalarını (api/yazma hariç) sayar ve katmana atar.

| Modül | Sayfa route | Katman | Envanterde | Not |
|---|---:|---|---|---|
| sp | 33 | GİRDİ (+ Savaş Odası/exec teşhis) | ✅ A | SP içinde teşhis de var (war-room, exec-dashboard) |
| surec | 6 | GİRDİ | ✅ B | süreç, PG, olgunluk (taşınacak) |
| proje | 19 | GİRDİ + TEŞHİS | ✅ C | Gantt/Kanban/Takvim/RAID/Portföy görünümleri (K-Radar KPR ile örtüşür) |
| bireysel | 2 | GİRDİ + görüntüleme | ✅ G | bireysel karne |
| k_radar | 26 | TEŞHİS | ✅ B/C/D/F | hub tüm modülleri linkler |
| k_rapor | 2 | RAPOR | ✅ E/I/L | + 33 api ekran |
| raporlar | 45 | RAPOR + AI + ESG | ✅ E/H/J/K/L | en dağınık |
| analiz | 1 | TEŞHİS | ✅ B | Performans Analitiği |
| masaustu | 3 | TEŞHİS | ✅ + | Masaüstüm, **Yönetim Özeti** (bugün düzeltildi) |
| marketing | — | ALTYAPI | — | tanıtım, araç değil |
| demo | — | ALTYAPI | — | demo oturum, araç değil |

**Sidebar'da geç fark edilip eklenenler** (ilk envanterde eksikti, şimdi kapsandı):
- **Savaş Odası** (`/sp/tv`) — tam ekran KPI duvarı (war-room). Teşhis. → SP'de yaşıyor.
- **Yönetim Özeti** (`/yonetim-ozeti`) — bugün kartları düzeltilen ekran. Teşhis.
- **Masaüstüm** (`/masaustu`) — kişisel dashboard. Teşhis.
- **Holding Görünümü** — çok-kurum paneli. Teşhis (üst seviye).
- **Bireysel Performans** (`/bireysel/karne`) — bireysel karne. Girdi + görüntüleme.

**Toplam ~137 kullanıcı-görünür sayfa route.** marketing/demo altyapı olduğu için
araç envanterine girmez. Geri kalan HER sayfa bir katmana atandı — dışarıda araç yok.

⚠️ **Çözülmemiş örtüşme:** `proje/views/gantt` ↔ `k_radar/kpr/gantt`, `proje/views/raid`
↔ `k_radar/risk` — proje modülü kendi teşhisini yapıyor AMA K-Radar da aynısını
yapıyor. Bölmede karar: proje teşhisi Proje'de mi kalsın, K-Radar'a mı devredilsin?

---

## İlk gözlemler (tartışma için)

1. **Araçlar 6 modüle dağılmış ama K-Radar hub hepsini tek sayfada topluyor** →
   kullanıcı 60+ kutu görüyor, boğuluyor. (memory: "demo overwhelm" riski.)

2. **Aynı araç 2-3 yerde beliriyor** (SWOT 4 yerde, EVM 3, VRIO 2, OKR 2). Örtüşme
   kod düzeyinde katmanlı (üretici→teşhis→rapor) ama KULLANICI için tekrar gibi.

3. **`raporlar` (101 route) en büyük ve en dağınık** — CFO paneli, ESG, AI koç,
   sunburst, bireysel karne… ortak teması yok, "kalanların çöplüğü" gibi büyümüş.

4. **Katmanlar isimde görünmüyor:** formülasyon (SP) / teşhis (K-Radar) /
   raporlama (K-Rapor/raporlar) / dağıtım — hepsi karışık sunuluyor.

5. **AI araçları dağınık** (5 araç, hepsi raporlar'da ama K-Radar hub'dan linkli) —
   tek "AI" başlığı altında toplanabilir.
