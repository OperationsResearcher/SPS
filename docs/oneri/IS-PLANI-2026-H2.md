# KOKPİTİM — İŞ PLANI (2026 H2)
> Kaynak: [`OZELLIK-ONERILERI-2026-07.md`](OZELLIK-ONERILERI-2026-07.md)
> Tarih: 2026-07-15 · Karar: **tüm öneriler sırayla yapılacak**
> Durum: `main` @ 493 test geçiyor, TASK-248…251 merge edildi

---

## 0. PLANI ŞEKİLLENDİREN KARARLAR (kullanıcı, 2026-07-15)

| Soru | Cevap | Plana etkisi |
|---|---|---|
| Yayın'da kaç gerçek müşteri? | **Henüz yok / pilot** | 🔴 **Planın en belirleyici cevabı.** Benchmark (§3.2) *kurulabilir ama açılamaz*; churn analitiği şu an anlamsız (churn edecek müşteri yok); **fiyat/paket kararı ve satışa hazırlık öne çıkıyor** |
| Öncelik? | **Hepsi, sırayla** | Faz yapısı korunur, hiçbiri atlanmaz |
| Redis? | **Ekleyebiliriz** | §1.3 blokesi kalkıyor → Faz 1'e girdi |
| Format? | **İkisi de** | Bu belge + türeyen TASK kayıtları (§Faz tablolarında TASK no'ları) |

### "Müşteri yok" gerçeğinin dürüst sonucu
Öneri belgesindeki bazı işler **bugün değer üretmez**:
- **Sektör benchmark** → k-anonimlik için sektör başına min. 5 gerçek kurum lazım. **Mimarisi kurulur, açılışı müşteriye bağlanır.**
- **Churn erken uyarısı** → churn edecek müşteri yok. `audit_logs` analitiği yine de yapılır ama amacı değişir: *churn tespiti* değil, **hangi ekran işe yaramıyor** (paketleme kararı için).
- **Buna karşılık öne çıkanlar:** teknik zemin (analitiğin ön koşulu), var olanı anlatma (§Faz 4), fiyat/paket kararı (§Faz 5).

---

## FAZ 1 — ZEMİN (Olmazsa olmaz)
> **Neden önce:** 366.716 sayısal ölçüm **metin olarak** duruyor. Faz 2-3'teki her analitik bunun üstüne kurulacak. Bu faz atlanırsa sonraki her şey `safe_float` parse'ına bağımlı, yavaş ve hataya açık kalır.

| # | TASK | İş | Bağımlılık | Kabul kriteri |
|---|---|---|---|---|
| 1.1 | TASK-252 | **`actual_value`/`target_value` → sayısal kolon**. `actual_numeric`, `target_numeric` (Numeric) ekle + backfill migration. Metin kolon **korunur** (girdi serbestliği), sayısal kolon analitiğin tek kaynağı olur. `safe_float` tek yerde toplanır. | — | 366k satır backfill edildi; parse edilemeyen satırlar raporlandı (sessizce 0 yazılmadı); DB'de `AVG()`/percentile çalışıyor; testler yeşil |
| 1.2 | TASK-253 | **`period_type` normalizasyonu.** `'Aylık'` (202) → `'aylik'` (365.925). Normalize + CHECK constraint. | — | Tek yazım kaldı; `GROUP BY period_type` doğru kova sayıyor |
| 1.3 | TASK-254 | **Redis + cache + rate limit.** Deploy `--network host` kullanıyor (`oracle_safe_deploy.sh:56`) → host'a `redis-server`, uygulama `redis://127.0.0.1:6379`. Compose'a gerek yok (PostgreSQL de böyle). `CACHE_TYPE=RedisCache`, `RATELIMIT_STORAGE_URL` (env'de zaten bekleniyor). `CacheService` çağrıları bağlanır. | Kullanıcı onayı ✅ | Redis ayakta; 8 worker **tek** cache görüyor; rate limit tutarlı; `CacheService.*` çağrılıyor; smoke test |
| 1.4 | TASK-255 | **CI'ı aç.** Faturalandırma kilidi çözülünce `.github/workflows/ci.yml` koşmalı. Çözülmezse `yerel_kontrol.py`'yi pre-commit hook'a bağla. | Hesap müdahalesi (kullanıcı) | CI yeşil koşuyor **veya** hook devrede |

**Faz 1 çıktısı:** Analitik için sağlam zemin. Yeni kullanıcı özelliği yok — bilinçli.

---

## FAZ 2 — VERİDEN DEĞER (Olsa güzel)
> Elimizdeki 7 yıllık × aylık × %99,9 dolu veriden ürün değeri çıkarma.

| # | TASK | İş | Bağımlılık | Kabul kriteri |
|---|---|---|---|---|
| 2.1 | TASK-256 | **Tahmin motorunu tekleştir + ürüne bağla.** `forecast_service` (k_rapor'dan çağrılıyor) + `ml_service` (api/ai.py'den) → tek motor. Karne/dashboard'a "yıl sonu tahmini + güven aralığı + hedef tutturma olasılığı". `calculate_achievement_probability` zaten yazılı. | **1.1** | Karnede tahmin bandı görünüyor; iki motor tek; gerçek tarayıcıda doğrulandı |
| 2.2 | TASK-257 | **Mevsimsellik.** `detect_seasonality` (yazılı, kullanılmıyor) → "Kasım'da her yıl düşersiniz, bu normal" vs "bu sefer anormal". Yanlış alarmı azaltır. | 2.1 | Anomali uyarısı mevsimselliği hesaba katıyor |
| 2.3 | TASK-258 | **`mock_*` ayıklaması.** 169 public tablonun **29'u** `mock_*` (DAO oylama, kıyamet senaryosu, oyun...). Paketleme belgesindeki "kaldır mı gizle mi" kararı kapatılır. | Kullanıcı kararı | Karar verildi + uygulandı; şema yüzeyi %17 azaldı (kaldırılırsa) |
| 2.4 | TASK-259 | **EVM projeksiyonu (EAC/ETC).** ⚠️ `evm_snapshots` **boş (0 kayıt)** → önce snapshot üretimi çalışmalı. Bu "veri var kullanılmıyor" değil, **"veri toplanmıyor"**. | Snapshot job | Snapshot üretiliyor; EAC/ETC hesaplanıyor |
| 2.5 | TASK-260 | **Kule'yi yeniden aç (E1).** Altyapı hazır (DB, 5 API, 17 tur YAML, Driver.js); `base.html`'de yorumda. UI stabilleşti → yeniden değerlendir. | UI stabil | Kule görünüyor; turlar çalışıyor |

---

## FAZ 3 — FARKLILAŞMA (Çığır açıcı)
> **Pazar kanıtı:** Microsoft, 66M kullanıcılı Viva paketinin içinde OKR ürününü tutturamadı ve *"adoption and usage hasn't grown"* diyerek 31.12.2025'te kapattı. Kategori shelf-ware'e düşüyor. Aşağıdakiler tam bu boşluğu vuruyor.

| # | TASK | İş | Bağımlılık | Kabul kriteri |
|---|---|---|---|---|
| 3.1 | TASK-261 | **Audit kapsamı denetimi.** `kpi_data_audits` **297 kayıt** (366k veriye karşı) → hangi yazma yolları audit yazıyor, hangileri atlıyor? Kapsam tamamlanır. | 1.1 | Her hedef/gerçekleşme değişikliği audit yazıyor; kapsam testli |
| 3.2 | TASK-262 | 🏆 **HEDEF MANİPÜLASYONU RADARI.** Ürünün en büyük farklılaştırıcısı. "Bu KPI'ın hedefi 3 kez aşağı çekildi, sonuncusu kapanışa 4 gün kala" · "X biriminde hedefler ort. %18 revize, Y'de %2" · "Yeşil görünüyor **çünkü** hedef düştü". **Rakip kanıtı: AI OKR kalite skorlama 16 üründe de yok** — herkes hedef *yazdırıyor*, kimse *not vermiyor*. | 3.1 + 1 dönem veri | Radar ekranı; yönetim "hedef dürüst mü" sorusunu cevaplayabiliyor |
| 3.3 | TASK-263 | **`audit_logs` ürün analitiği.** ⚠️ Amaç **churn değil** (müşteri yok) → **hangi ekran hiç açılmıyor**. `request_path` zaten toplanıyor. Paketleme kararlarını (hangi modül hangi tier) besler. | — | Ekran kullanım haritası; Faz 5'e girdi |
| 3.4 | TASK-264 | **Benchmark MİMARİSİ** (açılış değil). `TenantScopedMixin` bilinçli bypass + k-anonim eşik (sektör başına min. 5 kurum) + opt-in onayı. ⚠️ **Bugün açılamaz** (müşteri yok). **Mevcut durum düzeltmesi:** `routes_faz4.py:334` `_SEKTOR_BENCHMARKS` hardcoded (`{"otomotiv": {"OEE": 65...}}`). Sayfada uyarı **var** ama yanlış şeyi açıklıyor: *"kurumunuzun gerçek değerleri değildir"* diyor — yani "sizin değeriniz değil". Söylemediği: **bu rakamlar canlı veriden değil, elle yazılmış referans**. Metin netleştirilmeli. | 1.1 | Mimari hazır + eşik altında **kapalı**; uyarı metni verinin **kaynağını** söylüyor |
| 3.5 | TASK-265 | **KVKK-güvenli AI / veri ikametgahı.** BYOK + PII maskeleme + `base_url` zaten var (%90 hazır) → yerel LLM (Ollama/vLLM) + "veriniz çıkmadı" sertifikasyon ekranı. **Rakip kanıtı:** Spider Impact 5.8 metadata-only yapıyor ama **Türkiye'de barındırma yok**. KVKK hiçbir ülkeye yeterlilik kararı vermemiş. | — | Yerel LLM ile çalışıyor; ekran kanıt gösteriyor |

---

## FAZ 4 — VAR OLANI ANLAT (kod ~0, en ucuz kazanç)
> **Bulgu:** "Kimsede yok" listesinin **yarısı zaten çalışıyor ama anlatılmıyor.** Bu bir geliştirme değil, konumlandırma boşluğu. "Müşteri yok" cevabı bunu **öne** çekiyor.

| # | TASK | İş | Kabul kriteri |
|---|---|---|---|
| 4.1 | TASK-266 | **Özellik → değer haritası.** Zaten çalışan farklılaştırıcılar: **K-Vektör** (vizyon 1000 ölçeği — rakipler "vizyonun kaç puan" demez), **KOE** (PGV'siz olgunluk + AI yapı-danışmanı — **EFQM şablonu global vendor'larda yok**; AssessBase var ama *denetim* aracı, günlük KPI'ya bağlı değil), **otonom kılavuz/video üreteci**, **otonom hata kontrolü**. | Her biri için "hangi acıyı çözüyor" tek cümle |
| 4.2 | TASK-267 | **Konumlandırma metni.** Açılış: **Microsoft'un kendi itirafı** + **Sull (%28 yönetici üç önceliği sayabiliyor; kırık olan yatay koordinasyon, dikey kaskad değil)**. ⚠️ **KULLANMA:** "%90 strateji başarısız" (çarpıtılmış), "%82/%23 hizalama" (primary'yle uyuşmuyor) — Cândido & Santos (2015) bunları çürüttü; bilgili alıcı yıkar. | Metin hazır; çürük istatistik yok |
| 4.3 | TASK-268 | **Persona demo akışı.** Paketleme belgesinde açık karar. Full-set demo overwhelm ediyor. | Persona bazlı demo senaryosu |
| 4.4 | TASK-269 | ⚠️ **Türkçe'yi hendek olarak kullanma.** Spider Impact **zaten Türkçe destekliyor** (FAQ'den teyitli). Gerçek hendek: **mevzuat formatı (5018/5393) + veri yerleşikliği (KVKK)**. Kamu/belediye: **5393 md.41** → başkan 6 ayda plan sunmalı; ~1.389 belediye; 5 yıllık seçim döngüsü. **Yerli rakip: Vadi DIGIKENT** (5018/5393'e atıflı) — hafife alma. | Konumlandırma dil değil mevzuat üzerine kurulu |

---

## FAZ 5 — TİCARİ KARARLAR
> "Müşteri yok" cevabı bunları **kritik** yapıyor: ilk müşteriden önce verilmeli.

| # | TASK | İş | Kabul kriteri |
|---|---|---|---|
| 5.1 | TASK-270 | 🔴 **Fiyat modeli.** **Bulgu:** per-seat fiyatlama shelf-ware'i **kendisi üretiyor** — okuyucu koltuğu $8-16/ay ise alıcı koltukları *rapor verenlerle* sınırlar, *işi yapanlarla* değil → araç yönetici raporlama katmanına düşer = tam da çözmeye çalıştığımız hastalık. Bunu kabul eden iki ürün: **ESM ($1.000/ay sınırsız)**, **Perdoo (€1,50 izleyici koltuğu)**. | Fiyat modeli kararı verildi + gerekçesi yazılı |
| 5.2 | TASK-271 | **Tier/paket kararları.** Paketleme belgesindeki açıklar: tenant→tier dağılımı (7/7 hâlâ Master/full), progressive unlock mekaniği (en büyük boşluk), özellik-düzeyi gating. **Girdi: TASK-263 kullanım haritası.** | Kararlar kapatıldı |
| 5.3 | TASK-272 | **MCP server.** ⚠️ Rakipler 15 ayda ekledi: WorkBoard (**yazma yetkili, ~60 tool**), Perdoo (GA), Betterworks (beta), Planview. **Table stakes oluyor, bizde yok.** | MCP server çalışıyor |

---

## SIRA VE BAĞIMLILIK ÖZETİ

```
FAZ 1 (zemin)          1.1 actual_value ──┬─→ 2.1 tahmin ─→ 2.2 mevsimsellik
  1.2 period_type      1.3 Redis          ├─→ 3.1 audit kapsamı ─→ 3.2 HEDEF RADARI 🏆
  1.4 CI                                  └─→ 3.4 benchmark mimarisi (kapalı)

FAZ 4 (anlat)  ── bağımsız, paralel yürüyebilir ── kod ~0
FAZ 5 (ticari) ── 5.2 ← 3.3 (kullanım haritası)
```

**Kritik yol:** `1.1 → 3.1 → 3.2` (Hedef Radarı). Ürünün en büyük farklılaştırıcısı buradan geçiyor.

**Paralel yürütülebilir:** Faz 4 (kod gerektirmiyor) — Faz 1 sürerken başlanabilir.

---

## RİSKLER

| Risk | Etki | Azaltma |
|---|---|---|
| **1.1 backfill'de sessiz veri kaybı** | 🔴 366k satır — yanlış parse = yanlış karne | Metin kolon korunur; parse edilemeyenler **raporlanır**, sessizce 0 yazılmaz; migration downgrade test edilir |
| **3.2 için audit hacmi yetersiz** | 🟠 297 kayıt → radar boş çıkar | Önce 3.1 (kapsam), sonra **1 dönem veri birikimi**, sonra radar |
| **Benchmark müşterisiz açılırsa** | 🔴 k-anonimlik kırılır, kurum verisi sızar | Eşik altında **kapalı** kalır (kod seviyesinde) |
| **Redis eklenince env riski** | 🟠 Memory: "ENCRYPTION_KEY 3 ortamda sırayla patladı" | Deploy öncesi env kontrolü; `docker restart` env'i yeniden okumaz |
| **Hardcoded benchmark'ın kaynağı belirsiz** | 🟠 Sayfada uyarı **var** ama "sizin değeriniz değil" diyor; "canlı veriden gelmiyor" **demiyor** | TASK-264'te metni netleştir (küçük iş, mimariyi beklemez) |

---

## NOTLAR

- **Deploy yok:** L paketleri kuralı — tüm L paketleri bitmeden Yayın'a çıkılmıyor. Bu plan **yerelde** birikir.
- **Dal disiplini:** her faz kendi dalında (`claude/faz1-zemin` vb.), `main`'e merge kullanıcı onayıyla.
- **TASK numaraları** öneridir; uygulama sırasında TASKLOG'a gerçek numarayla yazılır.
- **Tahmini süre yazılmadı** — bilinçli. Süre tahmini için önce 1.1'in gerçek kapsamı (kaç yazma yolu `safe_float` kullanıyor) çıkarılmalı.
