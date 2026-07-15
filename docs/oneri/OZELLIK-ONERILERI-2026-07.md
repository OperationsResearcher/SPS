# KOKPİTİM — ÖZELLİK ÖNERİLERİ
> Tarih: 2026-07-15 · Yöntem: kod + **canlı yerel DB** taraması (spekülasyon değil)
> Kapsam: **şu an kullanmadığımız** özellikler. Var olanlar bilinçli olarak listelenmedi.

---

## 0. ÖNCE: ELİMİZDE NE VAR? (ölçüldü, tahmin değil)

Öneriler bu tabloya dayanıyor. Rakamlar yerel PostgreSQL'den çekildi (2026-07-15).

| Varlık | Ölçüm | Anlamı |
|---|---|---|
| **KPI veri noktası** | **366.716** | Ciddi bir veri varlığı |
| Hedef+gerçekleşme dolu | **366.326 (%99,9)** | Veri kalitesi yüksek — analitik için hazır |
| Zaman serisi derinliği | **7 yıl (2020–2026)** | Trend/mevsimsellik için yeterli |
| Granülarite | **%99,8 aylık** | Aylık = tahmin için ideal |
| KPI tanımı | 1.395 | — |
| Süreç / Strateji | 380 / 198 | — |
| Kullanıcı | 447 | — |
| LLM çağrısı (gerçek) | **279 log kaydı, 10 çağrı noktası, 9 dosya** | AI altyapısı ölü değil, **çalışıyor** |
| Bildirim | 4.354 | Sistem canlı kullanılıyor |
| Initiative / OKR | 104 / 69 | — |

**Zaten var (öneri değil):** AI danışman/koç/sunum, NLP sorgu, anomali tespiti, forecast servisi, BI/Power BI connector, Slack/webhook/push/e-posta, SSO+2FA, EVM/CPM/Gantt/RAID, OKR/BSC/ESG/EFQM/Hoshin, holding/bayi konsolidasyon+faturalama, zamanlanmış rapor, i18n TR/EN, çok-sağlayıcılı LLM gateway (BYOK+PII maskeleme+kota+maliyet takibi).

> **Not:** Bu belge hazırlanırken bir keşif ajanı "forecast_service ölü, LLM sadece 2 yerde kullanılıyor" dedi. **Doğrulandım: yanlıştı.** `forecast_service` `k_rapor/routes.py:57`'den çağrılıyor, `call_llm` 10 yerde kullanılıyor. Aşağıdaki her iddia bizzat DB/kod ile teyit edildi.

---

# 1. OLMAZSA OLMAZ

> Bunlar özellik değil, **ürünün güvenilirliği**. Yokluğu bir gün müşteri kaybettirir.

## 1.1 `actual_value` String(100) → sayısal kolon 🔴

**Durum:** [`app/models/process.py:395`](../../app/models/process.py#L395) — 366.716 sayısal ölçüm **metin olarak** saklanıyor.

**Neden olmazsa olmaz:**
- Her analitik `safe_float` parse'ından geçiyor → yavaş, hatalı veriye açık
- DB tarafında `AVG()`, `SUM()`, percentile **yapılamıyor** → benchmark/tahmin hep Python'da, tüm satırı çekerek
- `"12,5"` vs `"12.5"` vs `"%12"` sessizce farklı parse edilir → **yanlış karne**

**Ne yapılmalı:** `actual_numeric`/`target_numeric` (Numeric) yardımcı kolonları + backfill migration. Metin kolon korunur (girdi serbestliği), sayısal kolon analitik için tek kaynak olur.

**Maliyet:** 1 migration + backfill + `safe_float`'ın tek yerde toplanması. **Bu yapılmadan aşağıdaki hiçbir analitik öneri sağlıklı çalışmaz.**

## 1.2 `period_type` veri kalitesi 🔴

**Ölçüm:** `'aylik'` → 365.925 kayıt · **`'Aylık'` → 202 kayıt** (aynı şey, farklı yazım)

Sessiz bir tutarsızlık. `GROUP BY period_type` yapan her rapor 202 kaydı ayrı kova sayıyor. Normalize + CHECK constraint gerekiyor.

## 1.3 Redis — cache ve rate limit için ⛔ BLOKE

**Ölçüm:** Redis **hiçbir ortamda yok** — yerelde ping timeout, `docker-compose.yml`'de tek servis (`kokpitim-web`), Yayın deploy script'inde geçmiyor.

**Sonuçları:**
- `CacheService` yazılı ama **0 çağrı** — Redis'siz açılamaz
- `CACHE_TYPE=SimpleCache` + Dockerfile `GUNICORN_WORKERS:-8` → **8 worker = 8 tutarsız cache** → kullanıcıya yanlış rakam
- Rate limit `memory://` → 8 worker'da limit fiilen **8× gevşek** (brute-force koruması zayıf)
- [`config.py:125`](../../config.py#L125) zaten uyarıyor: *"Redis yoksa limiter her istekte kilitlenir"*

**Bu bir kod işi değil, altyapı kararı.** Yayın'a Redis eklenirse cache+limit tek task'ta bağlanır.

## 1.4 CI'ın açılması 🔴

GitHub Actions faturalandırma kilidi yüzünden Haziran'dan beri koşmuyor. Bu sürede **21 test sessizce kırıldı** (TASK-248'de onarıldı). `scripts/ci/yerel_kontrol.py` köprü olarak eklendi ama kalıcı çözüm değil.

---

# 2. OLSA GÜZEL OLUR

> Elimizdeki veriden değer çıkaran, orta maliyetli işler.

## 2.1 Tahmin motorunu ürüne bağla

**Durum:** İki tahmin implementasyonu var — `forecast_service.py` (lineer regresyon + güven aralığı) ve `ml_service.py` (sklearn). `forecast_service` yalnız `k_rapor`'dan, `ml_service` yalnız `app/api/ai.py`'den çağrılıyor.

**Fırsat:** 7 yıllık × aylık × %99,9 dolu veri, tahmin için **ideal**. Ama kullanıcı bunu karnesinde görmüyor.

**Öneri:** İki motoru tekleştir → karne/dashboard'a "yıl sonu tahmini + güven aralığı + hedefi tutturma olasılığı" bandı. `ml_service.calculate_achievement_probability` zaten yazılmış.

**Ön koşul:** §1.1 (sayısal kolon).

## 2.2 Mevsimsellik farkındalığı

`detect_seasonality` `ml_service`'te var, kullanılmıyor. 7 yıl aylık veri ile mevsimsellik çıkarılabilir → "Kasım'da her yıl düşüyorsunuz, bu normal" vs "bu sefer anormal" ayrımı. Yanlış alarmı azaltır.

## 2.3 EVM projeksiyonu (EAC/ETC)

`evm_snapshots` modeli PV/EV/AC/SPI/CPI + tarih tutuyor. **Ama tablo boş (0 kayıt)** — yani önce snapshot üretimi çalışmalı. Sonrasında EAC/ETC klasik formülle bedavaya gelir.

**Dürüst not:** Bu "veri var, kullanılmıyor" değil, "**veri henüz toplanmıyor**" kategorisinde.

## 2.4 `mock_*` tablo ayıklaması

**Ölçüm:** 169 public tablonun **29'u `mock_*`** — `mock_daoproposal`, `mock_doomsdayscenario`, `mock_gamescenario`, `mock_metaverse`… Paketleme belgesinde "ayıkla mı, gizle mi" kararı **hâlâ açık**.

Şema yüzeyinin %17'si laboratuvar artığı. Yeni geliştiriciyi yanıltır, yedek/migration süresini uzatır.

## 2.5 Kule'yi yeniden aç (E1)

Tüm altyapı hazır (DB, servis, 5 API, 17 tur YAML'i, Driver.js runtime) ama `base.html`'de **yorumda** → kullanıcı görmüyor. UI stabilleştiğine göre yeniden değerlendirilebilir.

---

# 3. ÇIĞIR AÇICI

> Oyunun kuralını değiştirir. Hepsi **elimizdeki veriye** dayanıyor — yeni veri toplamadan.

## 3.1 🏆 Hedef Manipülasyonu Tespiti ("Target Gaming Radar")

**Bu, bildiğim kadarıyla hiçbir strateji yazılımında yok** — ve tam da bu pazarın en büyük açığını vuruyor.

**Sorun:** Strateji yazılımlarının en bilinen eleştirisi *"shelf-ware oluyor, kimse ciddiye almıyor"*. Sebebi basit: **hedefler tutmayınca hedef değiştirilir**, sistem yeşil gösterir, kimse fark etmez. Yazılım bir tiyatro aracına dönüşür.

**Elimizdeki koz:** `kpi_data_audits` tablosu **her hedef değişikliğinin** `old_value` → `new_value` + `user_id` + `created_at` izini tutuyor.

**Ürün:** Yönetime tek ekran:
- "Bu KPI'ın hedefi yıl içinde **3 kez aşağı** çekildi — son değişiklik dönem kapanışına **4 gün** kala"
- "X biriminde hedefler ortalama %18 aşağı revize edildi, Y biriminde %2"
- "Bu kurum yeşil görünüyor **çünkü** hedefler düştü, performans değil"

**Neden çığır açıcı:** Rakipler "hedefe ulaştın mı?" diye soruyor. Kokpitim **"hedefin kendisi dürüst mü?"** diye soracak. Bu, yönetim danışmanlığının en değerli sorusu ve hiçbir dashboard sormuyor.

**Dürüst kısıt:** `kpi_data_audits` şu an **297 kayıt** (366k veriye karşı). Yani audit yazımı ya yeni açılmış ya eksik. **Önce audit kapsamı tam olmalı** — hangi yolların audit yazdığı denetlenmeli. Şema doğru, hacim yetersiz.

**Yol:** (1) audit kapsamını tamamla → (2) 1 dönem veri biriksin → (3) radar ekranı. Ön koşul: §1.1.

## 3.2 🏆 Gerçek Sektör Benchmark (k-anonim)

**Kritik keşif:** Mevcut "sektör benchmark" raporu ([`routes_faz4.py:334`](../../micro/modules/raporlar/routes_faz4.py#L334)) **tamamen hardcoded**:

```python
_SEKTOR_BENCHMARKS = {
    "otomotiv": {"OEE": 65, "PPM Defect": 80, "OTIF": 88, ...}   # elle yazılmış sabitler
}
```

Yani müşteriye "sektör ortalaması 65" diyoruz — bu rakam **hiçbir gerçek veriden gelmiyor**.

**Elimizdeki koz (ölçüldü):** Aynı KPI adları **5 ayrı kurumda** geçiyor — "Ar-Ge Etkinlik Skoru", "Aylık Satış Adedi", "Birim Üretim Maliyeti", "Dijital Kanal Büyüme Oranı"… `Tenant.sector` + `employee_count` segmentasyon için hazır.

**Ürün:** "Sektörünüzde medyan OEE %71, siz %64'tesiniz — üst çeyrek %83" — **gerçek, canlı, anonim** veriden.

**Neden çığır açıcı:** Bu bir **veri ağı etkisi**. Her yeni kurum benchmark'ı zenginleştirir → ürün her müşteriyle daha değerli olur → rakip kopyalayamaz (verisi yok). Klasik savunma hendeği.

**Dürüst kısıt (önemli):** Şu an 10 kurumun çoğu test/klon (`tom1`, `tom2`, `tom3`, `tomofiltest`) — **gerçek kurum ~4**, ve `sector` çoğunda **boş**. k-anonimlik için sektör başına min. 5 gerçek kurum gerekir. Yani bu özellik **bugün açılamaz**; müşteri sayısı arttıkça açılır. Ama mimarisi şimdi kurulmalı (`TenantScopedMixin` bilinçli bypass + k-anonim eşik + opt-in onayı).

## 3.3 🏆 KVKK-Güvenli Kurumsal AI — "Veriniz yurt dışına çıkmıyor"

**Elimizdeki koz:** LLM gateway zaten **BYOK + PII maskeleme + tenant başına şifreli anahtar (Fernet) + kota + maliyet takibi** ile kurulu. `docs/AI-POLITIKASI.md` "yanıtlar log'da saklanmaz — KVKK" diyor. SOC2/ISO27001 hazırlık belgesi var.

**Fırsat:** Bu altyapı bir **teknik detay** olarak duruyor; oysa Türkiye kurumsal/kamu pazarında **satış argümanının kendisi**. Global rakipler (Quantive, Cascade, ClearPoint) AI'ı kendi bulutlarında çalıştırır — KVKK'ya duyarlı kamu/savunma/finans müşterisi için bu **kırmızı çizgi**.

**Ürün:** Yerel LLM (Ollama/vLLM) desteği + "veri ikametgahı" sertifikasyon ekranı: *"AI analiziniz kurumunuzun sunucusundan çıkmadı"*. Gateway `base_url` alanı zaten var — self-hosted için tasarlanmış.

**Neden çığır açıcı:** Global rakiplerin **yapısal olarak** veremeyeceği bir söz. Onların iş modeli merkezi buluta bağlı. KVKK + kamu ihalesi + Türkçe = savunulabilir niş.

**Dürüst not:** Rakip taraması tamamlanamadı (zaman). "Hiçbirinde yok" iddiası **kod tarafında doğrulandı** (bizde var), pazar tarafında **doğrulanmadı**. Yatırım kararı öncesi rakip AI mimarileri teyit edilmeli.

## 3.4 Ürün Kullanım Analitiği (`audit_logs`)

`audit_logs` `request_path` + `user_agent` + `user_id` + `created_at` topluyor — **ama okuyan yok** (sadece kullanıcının kendi giriş geçmişi).

Bugünkü veriyle çıkarılabilir: hangi ekran hiç açılmıyor, kim 30 gündür girmiyor (**churn erken uyarısı**), onboarding nerede terk ediliyor. Kendi ürününüzü ölçmüyorsunuz — paketleme kararları (hangi modül hangi tier'a) bu veriyle verilir.

**Ölçüm:** 1.135 audit kaydı var; hacim düşük ama şema doğru.

---

# 4. BU ÖZELLİKLER KİMSEDE YOK

> Kullanıcının ek isteği. **Dürüstlük notu:** rakip pazar taraması zaman kısıtı nedeniyle tamamlanamadı.
> Aşağıdaki "kimsede yok" iddiaları **kendi kod tabanımızda doğrulandı** (bizde var/yok kesin),
> **rakiplerde yokluğu ise sektör bilgisine dayanıyor, kaynakla teyit edilmedi.**
> Yatırım kararı öncesi rakip teyidi şart.

| # | Özellik | Bizde durum | Neden benzersiz olabilir |
|---|---|---|---|
| 1 | **Hedef Manipülasyonu Radarı** (§3.1) | Şema hazır (`kpi_data_audits`), hacim yetersiz | Rakipler "hedefe ulaştın mı" sorar; "hedef dürüst mü" sorusu **ürünün kendi müşterisini denetlemesi** demek — ticari olarak cesaret ister, bu yüzden kimse yapmaz |
| 2 | **Gerçek k-anonim sektör benchmark** (§3.2) | Veri yapısı hazır, kurum sayısı yetersiz | Rakiplerde benchmark ya yok ya danışmanlık raporundan gelen sabit tablo (bizimki de şu an öyle). Canlı+anonim+otomatik olanı görmedim |
| 3 | **KVKK-güvenli / veri-ikametgahlı AI** (§3.3) | **Altyapı %90 hazır** (BYOK, PII maskeleme, `base_url`) | Global SaaS'ın iş modeli merkezi buluta bağlı — yapısal olarak veremezler |
| 4 | **K-Vektör (vizyon 1000 ölçeği)** | ✅ Çalışıyor | PG→Süreç→Alt→Ana→Vizyon tek sayıya indirgeme. Rakipler BSC/OKR skoru verir; "vizyonun kaç puan" demez |
| 5 | **KOE — Kurumsal Olgunluk Endeksi (PGV'siz)** | ✅ Çalışıyor | Veri girmeden olgunluk ölçen 4 boyutlu endeks + AI yapı-danışmanı. Rakiplerde olgunluk ölçümü genelde anket bazlı |
| 6 | **Otonom kılavuz/video üreteci** | ✅ Çalışıyor (`kilavuz_olusturucu_executor`) | Ürünün kendi kullanım videosunu ekran görüntüsü alarak üretmesi — hiçbir SPM ürününde görmedim |
| 7 | **Otonom hata kontrol senaryoları** | ✅ Çalışıyor (`hata_kontrol_executor`) | Ürünün kendi kendini gezip hata araması |

**Dikkat:** 4–7 **zaten var** — yani "kimsede yok" listesinin yarısı bizde **çalışıyor ama anlatılmıyor**. Bu bir geliştirme değil, **pazarlama/konumlandırma** boşluğu. Belki de en ucuz kazanç: var olanı anlatmak.

---

# ÖNERİLEN SIRA

| Sıra | İş | Gerekçe |
|---|---|---|
| 1 | §1.1 sayısal kolon + §1.2 period_type | **Her analitiğin ön koşulu.** Bunsuz §2.1/§3.1/§3.2 sağlıksız |
| 2 | §1.4 CI + §1.3 Redis kararı | Güvenlik ağı + altyapı (sizin kararınız) |
| 3 | §3.4 audit analitiği | Ucuz, veri hazır, paketleme kararlarını besler |
| 4 | §3.1 Hedef Radarı — audit kapsamını tamamla | En yüksek farklılaşma, ön koşulu var |
| 5 | §2.1 tahmin motorunu bağla | Veri ideal, kod yazılı, sadece bağlanmamış |
| 6 | §3.2 benchmark **mimarisi** | Bugün açılamaz (kurum sayısı) ama şimdi tasarlanmalı |

---

## KAYNAK / YÖNTEM NOTU

- Tüm rakamlar 2026-07-15'te yerel PostgreSQL'den ölçüldü.
- Kod iddiaları `grep`/dosya okuma ile teyit edildi; ajan raporlarındaki **iki hata düzeltildi** (`forecast_service` ölü değil; `call_llm` 2 değil 10 yerde).
- **Doğrulanmayan tek alan:** rakip pazar analizi (§4 uyarısına bakın).
- Karşılaştırma tabanı: `docs/paketler/PAKETLEME-STRATEJISI.md`, `docs/AI-POLITIKASI.md`, `docs/_arsiv/rapor/ERTELENEN-ISLER.md`.
