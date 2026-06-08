# KOKPİTİM — Öneri Yerleşim Haritası + Rakip Analizi

> **Soru:** Bu önerileri mevcut yapımızda nereye konumlandırabiliriz? Hangi sayfada?
> **Tarih:** 2026-06-03 · Kaynak: kod taraması (route + template) + kaynaklı rakip araştırması.

---

## 0. ÖNEMLİ DÜZELTME — Önerilerin çoğunun ZATEN bir sayfası var

İlk analizde bazı özellikleri "yok ❌" diye işaretlemiştim. Kod taraması bunu düzeltiyor:
**`/raporlar/` modülü altında 40+ gelişmiş rapor sayfası halihazırda mevcut** (ince HTML kabuğu + adanmış `js/raporlar/*.js` ile API'den veri çekip render eden, **işleyen** sayfalar).

Mevcut `/raporlar/*` sayfaları (route → template):
`ai-sunum, ai-coach, ai-danisman, nlp-query, ml-anomaly, quarterly-review, strateji-hikayesi, evrim-filmi, hizalama-sankey, sunburst, initiative-bubble, initiative-roadmap, muda-analizi, cmmi-heatmap, vrio-portfoy, sektor-benchmark, sektorel, yatirimci-sunum, audit-paketi, mobile, sabah-ozeti, early-warning, risk-heatmap, esg-rapor, carbon-trend, okr-cascade, onay-zinciri, pg-proje-etki, departman-performans, yonetici-liderlik, hedef-revizyon, k-vektor-carpiklik, veri-kalitesi, operasyon-istatistik, cfo-dashboard, coo-dashboard, chro-dashboard, stratejik-yillik, bireysel-hizalama, bi-connector, nlp-query ...`

**Asıl boşluk üç başlıkta:**
1. **Keşfedilebilirlik (discoverability):** Bu sayfalar ana launcher menüsünde modül olarak görünmüyor; sidebar'da K-Radar aktif-durumu `'raporlar' in ep` ile bunları K-Radar bağlamına gizliyor + bir `/raporlar` hub'ı (index.html, 102 satır) var. Kullanıcı çoğunu hiç bulamıyor.
2. **Derinlik:** Bazı sayfalar ince (35-60 satır) — erken/iskelet; içerik zenginleştirilmeli.
3. **Çekirdeğe entegrasyon:** AI Türkçe naratif, komut paleti, canlı harita nabzı, tek-tık board PDF, real-time — bunların ayrı rapor sayfasında değil, **çekirdek ekranların (karne, kurum, exec, harita) üstünde** olması gerekiyor.

---

## 1. Mevcut sayfa yapısı (sidebar / ana modüller)

| Modül | Route | Template | Rol |
|-------|-------|----------|-----|
| Masaüstü | `/masaustu` | `launcher.html` | Açılış / modül kartları + takvim |
| Stratejik Planlama | `/sp/menu`, `/sp` | `sp/menu.html`, `sp/flow.html` | Strateji menüsü + akış |
| ↳ Strateji Haritası | `/sp/strateji-haritasi` | `sp/strateji_haritasi.html` | vis-network ağ haritası |
| ↳ Exec Dashboard | `/sp/exec-dashboard` | `sp/exec_dashboard.html` | Yönetici 360° |
| ↳ OKR | `/sp/okr` | `sp/okr.html` | OKR / KR |
| Kurum | `/kurum` | `kurum/index.html` | Kimlik + süreç/proje özeti + grafikler |
| Süreç (Karne) | `/surec`, `/process/api/karne/<id>` | `surec/index.html`, `surec/karne.html` | Süreç karnesi |
| K-Radar | `/k-radar` | `k_radar/hub.html` | Skor radarı + öneriler/tetikleyiciler |
| Bireysel | `/bireysel/karne` | `bireysel/karne.html` | Bireysel karne |
| Analiz | `/analiz` | `analiz/index.html` | Trend + **forecast + anomali API'leri zaten var** |
| **Raporlar (hub)** | `/raporlar` | `raporlar/index.html` | **40+ rapor — ana menüde yüzeye çıkmamış** |

---

## 2. YERLEŞİM HARİTASI — her öneri hangi sayfaya oturur

`Durum: ✅ sayfa var · 🟡 yarım/iskelet · ⊕ çekirdeğe widget · 🆕 yeni`

| # | Öneri / Wow | Konum (route → template) | Durum | Yapılacak |
|---|-------------|--------------------------|-------|-----------|
| 1 | **Oto Türkçe yönetici özeti** | `surec/karne.html` üstü + `/kurum` + `/sp/exec-dashboard` (ayrıca `/raporlar/ai-danisman` var) | ⊕ | Çekirdek ekranların başına AI özet şeridi |
| 2 | **Doğal dilde sorgu (chat-with-data)** | `/raporlar/nlp-query` **zaten var** | 🟡 | Güçlendir + Cmd+K ile global çağır |
| 3 | **AI ile OKR/strateji taslağı** | `/sp/okr`, `/sp` (+ `/raporlar/ai-coach`) | ⊕ | OKR/SP formuna "AI taslakla" butonu |
| 4 | **Strateji-sapması / erken uyarı** | `/raporlar/early-warning` + `/k-radar` (triggers API var) | ✅🟡 | İkisini "Stratejik Erken Uyarı"da birleştir |
| 5 | **Tahmin + anomali** | `/analiz` (forecast/anomaly API **var**) + `/raporlar/ml-anomaly` | ✅ | Yelpaze grafiği + olasılık rozeti ekle |
| 6 | **Strateji haritası (görsel)** | `/sp/strateji-haritasi` **zaten var** | ✅ | Koz — canlı nabız ekle (#15) |
| 7 | **Süreç sağlık skoru** | `/analiz` (health API var) + `/kurum` + `/k-radar/kp` | ✅🟡 | Süreç sağlık ızgarası widget'ı |
| 8 | **Çeyrek inceleme (QBR)** | `/raporlar/quarterly-review` **zaten var** | ✅🟡 | İş akışı (güncelle→onayla→hatırlat) ekle |
| 9 | **Sabah özeti / "bugün dikkat et"** | `/raporlar/sabah-ozeti` + `/api/morning-summary` **var** | ✅ | **Masaüstü `/masaustu` açılışına taşı** |
| 10 | **Storytelling / sunum modu** | `/raporlar/strateji-hikayesi` + `/raporlar/ai-sunum` + `/raporlar/yatirimci-sunum` **var** | ✅🟡 | Tam ekran sunum modunu parlat |
| 11 | **Zaman makinesi (time-travel)** | `/raporlar/evrim-filmi` **zaten var** | ✅🟡 | Çekirdek dashboard'lara yıl slider'ı |
| 12 | **Markalı "Yönetim Kurulu Raporu" PDF** | `/raporlar/yatirimci-sunum` + `audit-paketi` + `pdf_export` | 🟡 | Tek-tık markalı board PDF + zamanla |
| 13 | **Hizalama Sankey / Sunburst** | `/raporlar/hizalama-sankey`, `/raporlar/sunburst` **var** | ✅ | Yüzeye çıkar |
| 14 | **Muda / israf** | `/raporlar/muda-analizi` **var** | ✅ | Yüzeye çıkar |
| 15 | **CFO/COO/CHRO panoları** | `/raporlar/cfo-dashboard` vb. **var** | ✅🟡 | Persona menüsüne koy |
| 16 | **ESG / karbon** | `/raporlar/esg-rapor`, `carbon-trend` **var** | ✅ | Yüzeye çıkar |
| 17 | **Hoshin X-Matrix** | (sayfa yok) — `/sp/` altına yeni | 🆕 | `hoshin_xmatrix_service` hazır, UI yok |
| 18 | **Senaryo / what-if kıyas** | `/sp` plan years (veri var) — yeni kıyas | 🆕 | Baseline⟷iyimser slider sayfası |
| 19 | **Komut paleti (Cmd+K)** | `base.html` — **global** | 🆕 | Tüm sayfalarda klavye navigasyon |
| 20 | **Canlı harita nabzı** | `/sp/strateji-haritasi` (mevcut) | ⊕ | vis-network node nabız/renk |
| 21 | **TV / war-room modu** | yeni mod (`/sp/exec-dashboard` türevi) | 🆕 | socketio ile büyük ekran döngüsü |
| 22 | **Gerçek zamanlı canlılık** | `socketio_events.py` **var** — global | 🟡 | Veri girince anlık güncelle |
| 23 | **Kutlama/konfeti, sparkline** | `surec/karne.html`, `bireysel/karne.html` | ⊕ | Mikro-keyif efektleri |

**Özet:** 23 maddenin **~13'ü zaten bir sayfada mevcut** (çoğu `/raporlar/`), 4'ü çekirdeğe widget, 5'i gerçekten yeni, 1'i global.

---

## 3. Sonuç — yerleşim stratejisi

1. **Önce keşfedilebilirlik:** `/raporlar` hub'ını ana launcher'a **"Raporlar & İçgörüler"** modülü olarak çıkar; içini **persona/amaç** ile grupla (Yönetici · Strateji · Süreç · Finans · Risk/ESG · AI). Mevcut 40+ sayfanın çoğu zaten orada — sadece görünmüyor.
2. **Çekirdeğe AI katmanı:** Oto Türkçe özet (1), komut paleti (19), canlı harita nabzı (20), real-time (22) — bunlar rapor sayfasına değil, **karne/kurum/exec/harita** üstüne gelmeli. En yüksek "wow".
3. **İnce sayfaları zenginleştir:** nlp-query, quarterly-review, strateji-hikayesi, evrim-filmi, sabah-ozeti (35-60 satır) → tam deneyim.
4. **Gerçekten yeni 5:** Hoshin X-Matrix, senaryo kıyas, TV/war-room modu, tek-tık board PDF, AI OKR taslak.

> Tek cümle: **Çoğu öneri "yeni sayfa" değil, "var olan sayfayı görünür + derin yapmak" + çekirdeğe ince bir AI/wow katmanı eklemek.**

---

## 4. Rakip dayanağı (kaynaklı özet)

- **AI oto-naratif:** ClearPoint her rapora yönetici özeti yazıyor ([clearpointstrategy.com](https://www.clearpointstrategy.com/platform/automation)); Power BI Smart Narrative DAX'sız dinamik özet + cross-filter güncelleme ([microsoft](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-smart-narrative)). → **Madde 1**
- **Doğal dil sorgu:** WorkBoard Chief-of-Staff + Power BI Copilot ([microsoft](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-reports-overview)). → **Madde 2/19**
- **AI OKR taslağı:** WorkBoard Co-Author ([workboard](https://learn.workboard.com/co-author-okrs-with-generative-ai)); Cascade Tapestry ([cascade](https://www.cascade.app/strategy-ai)). → **Madde 3**
- **Drift/risk zekâsı:** Cascade strategy-drift + risk tespiti ([cascade](https://www.cascade.app/solutions/ai-strategy-insights)). → **Madde 4**
- **Board raporu / QBR:** ClearPoint Briefing Books + QBR akışı ([clearpoint](https://www.clearpointstrategy.com/platform/reporting)); Envisio roll-up ([envisio](https://envisio.com/solutions/strategy-execution-software/)). → **Madde 8/12**
- **Storytelling:** Tableau Stories ([tableau](https://help.tableau.com/current/pro/desktop/en-us/story_create.htm)); Power BI narrative ([microsoft](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-create-narrative)). → **Madde 10**
- **Trend:** Gartner — 2027'de analitik içeriğin %75'i GenAI, AI ajanları kararların yarısını sürükler ([gartner](https://www.gartner.com/en/newsroom/press-releases/2025-06-18-gartner-predicts-75-percent-of-analytics-content-to-use-genai-for-enhanced-contextual-intelligence-by-2027)).

> *Rakip yetenekleri büyük ölçüde satıcı pazarlama/doküman içeriğidir (3-0 doğrulandı, ama bağımsız performans testi değil).*
