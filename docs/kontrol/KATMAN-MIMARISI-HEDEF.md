# Katman Mimarisi — Hedef Tasarım

> Kullanıcıyla mutabık kalınan bölme. Analitik & rapor araçlarının 3 katmana
> ayrılması + URL yeniden yapılandırması.
> Tarih: 2026-07-17 · Durum: TASARIM (henüz uygulanmadı)
> Envanter: `ARAC-ENVANTERI-2026-07-17.md` · Keşif: `K-RADAR-vs-K-RAPOR-kesif.md`

---

## Temel ilke — kullanıcının kendi cümlesiyle

> "Bizim işimiz stratejik planı yönetmek. Girdilerimizi veriyoruz (ana/alt
> strateji, süreç, PG, proje, SWOT, PESTLE, OKR…), anlık yönetiyoruz. Sonra çeşitli
> araçlarla sonuçları görüyoruz. Ve karar destek sistemi olarak raporluyoruz."

Üç katman = bu üç cümle. Kural: **her veri tek katmanda (girdi) yazılır; teşhis
ve rapor katmanları SALT OKUR.**

---

## Üç katman + URL önekleri

| Katman | URL öneki | Rol | İçindeki modül(ler) |
|---|---|---|---|
| **1. Girdi** | `/k-plan/...` | Yaz + anlık yönet (tek sahip) | SP, Süreç, Proje, Bireysel |
| **2. Teşhis** | `/k-radar/...` | Gör (salt-oku) | K-Radar + Savaş Odası |
| **3. Rapor** | `/k-report/...` | Konsolide + dışa aktar | K-Rapor + raporlar |

**URL kuralı (KURALLAR-MASTER §2 ile uyumlu):**
- URL = backend/route → **İngilizce** (PG örneği: ekran "Performans Göstergesi",
  URL `/pi` — TASK-209 tek-dil kararı). Katman önekleri İngilizce: k-plan/k-radar/k-report.
- Ekran metni (sidebar, başlık) → **Türkçe** (Stratejik Planlama, Teşhis, Raporlar).
- "K-" öneki simetrik: **K-Plan / K-Radar / K-Report**.

**URL derinliği: katman/konu/araç (3 parça)** — kullanıcı kararı.
Katmanı DA konuyu DA URL'den okuruz; örtüşen araçlar (Gantt) katmana göre ayrı URL alır.

---

## URL şeması — katman/konu/araç

### Katman 1 — GİRDİ (`/k-plan/`)

> ⚠️ **DÜZELTİLDİ 2026-07-17 (ölçüm + kullanıcı kararı).** Bu bölüm önce Türkçe konu
> adlarıyla yazılmıştı (`/k-plan/surec/...`). Ölçüm gösterdi ki girdi modülleri
> **zaten İngilizce URL'ye taşınmış**: `/process` (37 route), `/individual` (18),
> `/project` (21) — `/surec`, `/proje` yalnızca legacy redirect olarak kalmış.
> Türkçe şema hem KURALLAR §2'yi ("URL = İngilizce") ihlal ederdi hem de mevcut
> kodu geriye döndürürdü. **Karar: İngilizce konu adı.** Ekran metni Türkçe kalır.

```
/k-plan/strategy/swot            SWOT, TOWS, PESTEL, Porter, VRIO, BSC, OKR,
/k-plan/strategy/pestel          Blue Ocean, X-Matrix, vizyon, misyon, değerler
/k-plan/strategy/okr
/k-plan/strategy/stakeholder     PAYDAŞ — girdi evi İNŞA EDİLİR (Faz 3)
/k-plan/process/list             süreç, PG
/k-plan/process/maturity         OLGUNLUK (K-Radar domain'inden TAŞINIR)
/k-plan/process/value-chain      DEĞER ZİNCİRİ — girdi evi İNŞA EDİLİR (Faz 3)
/k-plan/project/gantt            görev, Gantt, Kanban, Takvim, Kapasite
/k-plan/project/kanban           (anlık yönetim = girdi, kullanıcı kararı)
/k-plan/project/raid             PROJE RİSKİ (her risk bir kaynağa bağlı)
/k-plan/individual/scorecard     bireysel karne, hedef
```

### Katman 2 — TEŞHİS (`/k-radar/`) — SALT OKU
```
/k-radar/strateji/swot         aynı SWOT'u GÖSTERİR (yazamaz)
/k-radar/surec/olgunluk        olgunluk teşhisi (CMMI ısı haritası)
/k-radar/surec/pareto          darboğaz, Pareto, OEE, VSM, SLA, benchmark
/k-radar/proje/gantt           proje teşhisi (girdi Gantt'tan AYRI URL)
/k-radar/proje/evm             EVM, CPM
/k-radar/risk/heatmap          risk konsolidasyonu (tüm kaynaklardan okur)
/k-radar/cross/paydas          paydaş haritası görseli
/k-radar/savas-odasi           canlı KPI duvarı (SP'den TAŞINIR — saf teşhis)
```

### Katman 3 — RAPOR (`/k-report/`)
```
/k-report/kurumsal/ozet        kurumsal performans, K-Vektör
/k-report/panel/cfo            CFO, COO, CHRO panelleri
/k-report/esg/karbon           ESG, karbon
/k-report/ai/danisman          AI danışman, koç, sunum, NLP sorgu
/k-report/denetim/paket        denetim, 2FA, uyum
/k-report/export/pdf           PDF, Excel, Slack, BI connector, yatırımcı sunumu
```

---

## Bu bölmenin gerektirdiği TAŞIMALAR (borç)

Sadece isim/URL değil; kuralı uygulamak için 3 şey fiziksel taşınır:

| Ne | Nereden | Nereye | Neden |
|---|---|---|---|
| **Savaş Odası** | SP (`/sp/tv`) | Teşhis (`/k-radar/savas-odasi`) | Saf teşhis, sıfır girdi |
| **Olgunluk girişi** | K-Radar domain | Girdi (`/k-plan/surec/olgunluk`) | Süreç verisi, tek sahip girdi olmalı |
| **Yazma API çağrıları** | K-Radar/KS (`sp_api_swot_save`) | KALDIRILIR | Teşhis salt-oku olmalı |

---

## Karara bağlandı — açık karar noktası YOK

### Karar 1 — K-Rapor + raporlar BİRLEŞİR (`/k-report/` altında)
İkisi de rapor katmanı. k_rapor (35 route) + raporlar (101 route) → tek `/k-report/`.
**Dikkat — birleşme kör olmamalı, çakışma var (ölçüldü):**
- risk: raporlar'da 6 + k_rapor'da 1 → tek risk raporu
- bireysel: raporlar'da 5 + k_rapor'da 1
- anomali: raporlar'da 2 + k_rapor'da 1
Birleştirirken bu çift araçlar TEKİLLEŞTİRİLİR (en iyi olan kalır, diğeri redirect).

### Karar 2 — Proje teşhisi K-RADAR'a devredilir
Gantt/Kanban/Takvim = anlık yönetim → GİRDİ (`/k-plan/proje/`), Proje'de kalır.
Proje EVM/portföy/CPM = teşhis → `/k-radar/proje/`. Proje modülünün `views/gantt`
girdi tarafı; teşhis görselleri K-Radar'da toplanır. Örtüşme katman/konu URL'siyle
çözülür (`/k-plan/proje/gantt` ≠ `/k-radar/proje/gantt`).

### Karar 3 — Risk borcu TEMİZLENİR, kaynak = GENİŞ tanım
**İlke:** Her risk bir kaynağa bağlı. Kaynak = {SWOT, PESTEL, süreç, proje}.
Kurumsal-genel riskler zorla projeye değil, doğdukları stratejik analize bağlanır:
- "Kur Riski" → PESTEL (Ekonomik) · "Yetenek Kaybı" → SWOT (Zayıflık)
- "Tedarik Kesintisi" → süreç · proje riski → proje

**Gerçek boyut (ölçüldü):**
- Mevcut 70 "manual" risk = 35 gerçek × 2 (test kurumu ID kayması: tomofiltest+Tomofil).
  Gerçek kurumsal riskler (Hammadde, Kur, Tedarik…) — silinecek çöp değil, eşlenecek veri.
- `risk_heatmap_items` tablosunda `source_id` kolonu **YOK** (sadece `source_type`).
  → migration gerekir: `source_id` + FK ekle, sonra 35 riski kaynağa eşle.
- Bu ADIM ŞEMA + VERİ işidir; katman/URL bölmesinden AYRI koşar ama aynı hedefe hizmet eder.

---

## Uygulama gerçeği (küçümsenmemeli)

- **~412 route** yeni URL alır → her eski URL'den yeni URL'ye **301 redirect** şart
  (Yayın çalışıyor, bookmark'lar, dış linkler kırılmasın).
- **~64 template** `url_for` kullanıyor → endpoint ADLARI korunursa template'e
  dokunmadan sadece route yolu değişir (iş bu yüzden yönetilebilir).
- **Aşamalı yapılmalı**, tek seferde değil: önce redirect altyapısı, sonra katman
  katman. Her adım Test'te doğrulanır.
- Bu iş kullanıcının **paketleme/segmentasyon** stratejisinin parçası — tek başına
  değil, o bütünle ele alınmalı.
