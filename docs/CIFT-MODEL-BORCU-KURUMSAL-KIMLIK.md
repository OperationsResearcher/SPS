# Çift-Model Borcu — Kurumsal Kimlik & Strateji Tek-Kaynak Konsolidasyonu

> **Durum:** Teşhis tamamlandı, taşıma (migration) YAPILMADI.
> **Tarih:** 2026-06-16
> **İlgili borç:** KURALLAR-MASTER §7 · S1 (Legacy route çift yüzey)
> **Üst envanter:** [`LEGACY_ROUTE_INVENTORY.md`](LEGACY_ROUTE_INVENTORY.md)
> **Neden önemli (iş bağlamı):** L1 "Başlangıç" paketinin ölçüm omurgası **KOE (Kurumsal Olgunluk Endeksi)**;
> 1. boyutu "Kimlik & Strateji Netliği", 2. boyutu "Süreç Mimarisi". Bu boyutlar tam da aşağıdaki
> çakışan kavramların üstüne kurulu. **İki kaynak varsa KOE ölçülemez** → bu konsolidasyon L1'in ön koşuludur.
> Strateji bağlamı: [`paketler/PAKETLEME-STRATEJISI.md`](paketler/PAKETLEME-STRATEJISI.md)

---

## 1. Kök neden (tek cümle)

Model katmanı ikiye bölünmüş ve **ikisi de aktif**: **legacy `models/`** (Türkçe: `Kurum`, `Deger`,
`AnaStrateji`, `Surec`…) ile **modern `app/models/`** (`Tenant`, `Strategy`, `Process`…). Aynı kavram
**iki ayrı tabloda** tutuluyor; aralarında **senkron yok**. Bir route legacy'ye, başka bir route modern'e
yazıyor → kullanıcı sayfaya göre **farklı veri** görüyor.

Kullanıcının ilk fark ettiği semptom: `http://127.0.0.1:5001/kurum` ile `http://127.0.0.1:5001/sp`
**farklı Vizyon/Misyon** gösteriyor.

## 2. Aktiflik teyidi (ölü kod değil)

- Legacy route'lar `main/routes/strategy_api.py` içinde `@main_bp.route` ile tanımlı.
- `main_bp`, [`app/__init__.py`](../app/__init__.py) **satır 391-393**'te `url_prefix=""` ile **koşulsuz register** ediliyor.
- Modern kurum API'ları `micro/modules/kurum/routes.py` → `app_bp`; URL'leri `/kurum/api/**` ve `/kurum/ayarlar`.
- **URL çakışması YOK** (legacy `/kurum/ana-stratejiler/...` vs modern `/kurum/api/...`) → ikisi de sessizce çalışıyor.

## 3. Çakışan kavramlar haritası

| # | Kavram | Legacy tablo / route | Modern tablo / route | Yapı farkı | Risk |
|---|--------|----------------------|----------------------|-----------|------|
| 1 | **Vizyon / Amaç(Misyon)** | `kurum.vizyon`, `kurum.amac` · `POST /kurum/update-amac-vizyon` ([strategy_api.py:208](../main/routes/strategy_api.py#L208)) | `tenants.vision`, `tenants.purpose` (+ `tenant_year_identities`) · `/kurum/api/update-strategy` ([kurum/routes.py:243](../micro/modules/kurum/routes.py#L243)) | Aynı alan, iki yer; modern yıl-bazlı | 🔴 |
| 2 | **Ana Strateji** | `ana_strateji` (`ad`,`weight`,`perspective`) · `/kurum/ana-stratejiler/*` ([strategy_api.py:7+](../main/routes/strategy_api.py)) | `strategies` (`title`,`code`,`description`) · `/kurum/api/add-strategy` ([kurum/routes.py:267](../micro/modules/kurum/routes.py#L267)) + `sp/routes_strategy.py` | İki ayrı tablo; legacy'de `perspective`/`weight` fazladan | 🔴 |
| 3 | **Alt Strateji** | `alt_strateji` · `/kurum/alt-stratejiler/*` ([strategy_api.py:135+](../main/routes/strategy_api.py)) | `sub_strategies` · `/kurum/api/add-sub-strategy` ([kurum/routes.py:342](../micro/modules/kurum/routes.py#L342)) | İki ayrı tablo, iki ayrı parent | 🔴 |
| 4 | **Değerler** | `deger` (ayrı tablo, **çok satır**) · `/kurum/degerler/*` ([strategy_api.py:232+](../main/routes/strategy_api.py#L232)) | `tenants.core_values` (**tek TEXT**) | **Yapı dönüşümü gerekir** (satır↔metin) | 🟠 |
| 5 | **Etik Kurallar** | `etik_kural` (ayrı tablo) · `/kurum/etik-kurallari/*` ([strategy_api.py:309+](../main/routes/strategy_api.py#L309)) | `tenants.code_of_ethics` (tek TEXT) | **Yapı dönüşümü gerekir** | 🟠 |
| 6 | **Kalite Politikası** | `kalite_politikasi` · `/kurum/kalite-politikalari/*` ([strategy_api.py:385+](../main/routes/strategy_api.py#L385)) | `tenants.quality_policy` (tek TEXT) | Yapı dönüşümü gerekir | 🟡 |
| 7 | **Süreç / PG / Bireysel PG** | `surec`, `surec_performans_gostergesi`, `bireysel_performans_gostergesi` (legacy ORM) | `processes`, `process_kpis`, `individual_performance_indicators` | Çoğunlukla **aynı tablo, farklı ORM sınıfı** | 🟡 |

## 4. Bonus bug (bu işle birlikte düzeltilecek)

[`ui/templates/platform/sp/index.html`](../ui/templates/platform/sp/index.html) **satır 24** `tenant.mission`
okuyor ama `Tenant` modelinde **`mission` alanı yok** (doğrusu `purpose`). SP sayfasında misyon hep boş düşüyor.

## 5. Karar: yön ve sıra

**Tek gerçek kaynak = MODERN** (`app/models/`, `tenants` + `tenant_year_identities` + `strategies`/`sub_strategies`).
Gerekçe: yıl-bazlı versiyonlamayı ve "canlı/çevik plan" vaadini zaten modern taraf taşıyor. Legacy emekliye ayrılır.

**Faz sırası (önce-onay; her faz kendi dalında, KURALLAR §branch):**

- **Faz 1 — Kimlik (🔴):** Vizyon/Amaç tek kaynağa indir. `/kurum/update-amac-vizyon` legacy yazma yolu kapatılır;
  veri `kurum.*` → `tenants.*` taşınır. `tenant.mission` bug'ı düzeltilir.
- **Faz 2 — Strateji (🔴):** `ana_strateji`/`alt_strateji` → `strategies`/`sub_strategies` taşıması.
  Dikkat: legacy `perspective` (BSC) ve `weight` alanlarının modern karşılığı **yok** — taşımadan önce
  bu alanların korunup korunmayacağına karar verilmeli (modern modeli zenginleştir veya bilinçli düş).
- **Faz 3 — Değerler/Etik/Kalite (🟠/🟡):** **KARAR (2026-06-16): çok-satırlı yapı kazanır.**
  Bu, "modern kazanır" kuralının **bilinçli istisnasıdır** — burada legacy'nin çok-satırlı yapısı (her değer/etik/kalite
  maddesi = ayrı kayıt: başlık + açıklama) doğru olandır; modern tek-TEXT (`tenants.core_values/code_of_ethics/quality_policy`)
  emekliye ayrılır. Legacy tablolar (`deger`/`etik_kural`/`kalite_politikasi`) **modern isimlendirmeyle yeniden kurulur**
  (ör. `tenant_values`, `tenant_ethics_codes`, `tenant_quality_policies` — `app/models/` altında, modern ORM).
  **Gerekçe (L1 üç bloğu da bunu şart koşuyor):**
  - **KOE:** "Kimlik & Strateji Netliği" boyutu tek-TEXT'ten anlamlı sinyal üretemez; çok-satırlı yapı
    "kaç madde tanımlı, kaçı açıklamalı → % olgun" verir.
  - **Onboarding wizard:** "sektör şablonundan değerleri **satır satır işaretle/çıkar**" deneyimi yalnızca satır-bazlı yapıyla olur.
  - **AI Yapı-Danışmanı:** "Değer X'in açıklaması boş" gibi boşluk tespiti satır-bazlı yapı gerektirir.
  - Bonus: ileride bir değeri/etik maddesini bir stratejiye **bağlamak** mümkün olur (tek-TEXT'te imkânsız).
- **Faz 4 — Süreç/PG/Bireysel ORM tekilleştirme (🟡):** legacy ORM sınıflarını modern'e alias'la / legacy route'ları emekliye al.

**Her fazda kırmızı çizgi:** veri taşıması = DB değişikliği → önce yedek (KURALLAR §8). Tomofil (tenant 27)
demo baseline'ı bu kavramları içerir; taşıma demo/yayın verisini etkilemeden önce yerelde doğrulanır.

## 6. Açık kararlar (taşımadan önce netleşmeli)

1. ~~Değerler/Etik/Kalite: tek-TEXT mi, çok-satırlı modele yükseltme mi?~~ **KARARLAŞTI (2026-06-16): çok-satırlı (bkz. Faz 3).**
2. `ana_strateji.perspective` / `weight` korunacak mı (modern Strategy'e alan eklensin mi)?
3. Legacy route'lar: hemen kaldır mı, yoksa "deprecated → 410/redirect" geçiş dönemi mi?
4. Taşıma tek seferlik script mi, Alembic migration mı (squash baseline `f5215370eebd` üstüne)?
