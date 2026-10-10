# ALAN A — Hesaplama Doğruluğu (derin analiz)

Tarih: 2026-10-10 · Salt okunur analiz (dosya değiştirilmedi, DB'ye bağlanılmadı).
Kanıt yöntemi: kod okuma + `.venv\Scripts\python.exe` ile saf fonksiyon denemeleri (denemeler `reports` dışında, geçici dizinde koştu).
Kapsam: `app/services/score_engine_service.py`, `process_health_service.py`, `process_performance_service.py`, `app/utils/karne_hesaplamalar.py`, `app/utils/process_utils.py`, `date_sovereign.py`, `kpi_data_score_service.py`, `plan_year_service.get_kpi_configs_bulk`, `micro/modules/surec/routes_karne.py` + `routes_kpi_data.py`, `k_rapor/routes.py`, `efqm_assessment.py`, `k_vektor_engine.py`, `ui/static/platform/js/surec.js`, legacy `services/score_engine_service.py`, `micro/modules/api/routes.py`.

## Özet

- Kesin hata: **14** · Olası risk: 6 · İyileştirme: 2
- "Aynı gösterge için 5 farklı hesap yolu" iddiası **DOĞRULANDI** (aslında 7 yol, bkz. bölüm 2). Aynı girdide yöntem etiketi, sayı biçimi, tarih kesimi, hedef kaynağı ve ağırlık kaynağı yüzünden **farklı sonuç üreten** yollar var.
- Önceki denetimde (`docs/ekim2026`) listelenen bazı hatalar (yön `lower_is_better`, `AVG` etiketi motorda, hedef 0 azalan) motor tarafında kapanmış; ama kapanış **yalnızca skor motoru + `health` için** geçerli. Karne API'si, JS, k_rapor, EFQM ve legacy yollar hâlâ eski kuralları kullanıyor.

---

## 1. Bulgular

### A-001 — Alt süreçleri hiç ölçülmemiş üst süreç 0.0 alıyor (B1/M4 düzeltmesi eksik kaldı)
- Dosya: `app/services/score_engine_service.py:461-470`
- Kanıt:
  ```python
  for cid, w in zip(child_ids, _agirliklar):
      child_score = calc_process_score(cid)
      if child_score is None:
          continue
      total += child_score * w; w_sum += w
  process_scores[process_id] = round(total / w_sum, 2) if (w_sum and w_sum > 0) else 0.0   # <- 469
  ```
  Yaprak süreçte aynı durum (`:499-501`) `None` dönüyor; **üst süreçte** ise tüm çocuklar `None` olunca `0.0` yazılıyor. Ek olarak çocuğu olan sürecin **kendi PG'leri** (`_kpis_by_proc`) hiç hesaba katılmıyor (`:455-471` çocuk varsa erken return).
- Etki: Süreç Karnesi / Süreç listesi (`routes_process.py:174`), Kurumsal rapor ve Vizyon puanı. Ölçülmemiş bir üst süreç "tamamen başarısız (0)" görünür, bağlı alt stratejiyi ve vizyonu aşağı çeker. Yani 07-21'de kapatılan "ölçülmedi ≠ 0" hatası bir seviyede geri geliyor. Çocuklu sürecin kendi PG'leri ise sessizce yok sayılıyor.
- Önem: Yüksek · Etiket: **kesin hata** (0.0 satırı) / olası risk (kendi PG'lerinin yok sayılması, tasarım kararı olabilir)
- Çözüm: `:469` → `None` dön (`if not w_sum: process_scores[pid]=None; return None`). Çocuklu sürecin kendi PG'leri de varsa karışık ağırlıkla birleştir veya en azından belgeye yaz.
- Efor: 0.5 saat · Test: Üst süreç + 2 çocuk, çocuklarda KpiData yok → `process_scores` içinde üst süreç anahtarı olmamalı; biri veri girince üst süreç = o çocuğun skoru.

### A-002 — Skor motoru yıllık config'in `is_included` ve `weight` alanlarını yok sayıyor, karne ise kullanıyor
- Dosya: `score_engine_service.py:443-447, 477` (motor) ↔ `routes_karne.py:268-270, 335` (karne) ↔ `plan_year_service.py:318-319`
- Kanıt: Motor `ProcessKpi.is_active` süzer, `_distribute_weights([k.weight for k in kpis])` ile **ProcessKpi.weight** kullanır. `get_kpi_configs_bulk` ise `weight` ve `is_included` döner; karne `if not _is_included: continue` ile PG'yi listeden çıkarır, ağırlığı `_ycfg["weight"]`dan gösterir. Motorda `kpi_cfg_map` yalnızca `target/direction/method` için okunuyor (`:389-397`).
- Etki: Bir yıl için "bu yıl dahil değil" işaretlenen veya yıllık ağırlığı değiştirilen PG; Karne ekranında yok/farklı ağırlıkta görünür, ama Süreç skorunda, Vizyon'da ve K-Vektör'de eski ağırlıkla ve dahil sayılır. Aynı süreç iki ekranda farklı yüzde gösterir.
- Önem: Yüksek · Etiket: **kesin hata** (kodla doğrulandı; veride kaç satır etkili ölçülmedi)
- Çözüm: `compute_process_scores_internal` içinde `get_kpi_configs_bulk` sonucundan `is_included=False` PG'leri ele, ağırlığı `cfg["weight"]`dan oku. Config haritasını `get_pg_scores_from_kpi_data` ile paylaş (çift sorgu olmasın).
- Efor: 2-3 saat · Test: PG B için `kpi_year_configs.is_included=False` → süreç skoru yalnız A'dan; ağırlık override'ı → skor değişir.

### A-003 — `_parse_float`: üç haneli ondalık sayı binlik sanılıyor (125 / 98750)
- Dosya: `score_engine_service.py:70-73`
- Kanıt (deneme çıktısı):
  ```
  '0.125'   -> 125.0      '98.750' -> 98750.0     '2.375' -> 2375.0
  '3.999'   -> 3999.0     '100.000'-> 100000.0    '1,234.5'-> 1.2345
  ```
  Kural "son grup 3 haneliyse binlik" ve `tam.lstrip('-').isdigit()`; `0.125` için `tam='0'` olduğundan da binlik sayılıyor. Hedef 0.9 iken gerçekleşen "0.125" → skor 100 (doğrusu 13.89).
- Etki: Oran/endeks tipi PG'ler (0,875 / 98,750 / 4,125 gibi 3 ondalıklı girişler) skor motorunda, `kpi_data_score_service` satır skorunda (`status_percentage`), `health` ve `score-detail`'de 1000 kat büyük okunur → skor 100'e yapışır veya hedef 1000 kat şişer → 0'a yakın çıkar. İngilizce biçim `1,234.5` ise 1.2345 olur.
- Önem: Yüksek · Etiket: **kesin hata**
- Çözüm: Belirsiz tek-noktalı değerde sol grup `0` ya da `-0` ise ondalık say; 3 haneli gruplu binlik yalnız sol grup 1-3 hane ve `0` ile başlamıyorsa. Tutarlı bir "sayı ayrıştırıcı" tek modülde (karne tarafındaki `_sayi_tr` ile birleştir). Veri tarafında kaç PG etkili olduğunu `~ '^-?[0-9]*\.[0-9]{3}$'` regex'iyle ölç.
- Efor: 2 saat · Test: yukarıdaki dizilerin tablosu (0.125→0.125, 1.234→1234 muğlak kabul ve belgele).

### A-004 — Başarı puanı bantları arasında boşluk varsa uydurma "3" dönüyor
- Dosya: `app/utils/karne_hesaplamalar.py:292-309` (`hesapla_basari_puani`)
- Kanıt (deneme):
  ```
  bantlar {1:'0-9',2:'10-49',3:'50-79',4:'80-99',5:'100-'}
  hesapla_basari_puani(99.5)  -> 3   (beklenen 4)
  hesapla_basari_puani(79.5)  -> 3
  hesapla_basari_puani(9.5)   -> 3   (beklenen 1)
  hesapla_basari_puani(11,{1:'1-10',5:'12-20'}) -> 3
  ```
  Uç değer kuralları sadece "tüm bantların dışı" için; arada kalan (tam sayı bantlarda ondalıklı gerçekleşen) için `return 3`. Bant biçimi (`hesapla_bant_puani`) aynı durumda doğru olarak `None` döner — iki biçim tutarsız.
- Etki: Yaygın eski tip `{"1":"%71-80",...}` (657 PG) bantlarında ondalıklı gerçekleşen (ör. 80.4) PG'ye 3 puan verilir; Karne PG satırındaki başarı puanı ve ağırlıklı puan yanlış.
- Önem: Orta-Yüksek · Etiket: **kesin hata**
- Çözüm: Boşlukta `None` dön (veya en yakın alt banda yuvarla ve log yaz); son `return 3` kaldırılsın.
- Efor: 1 saat · Test: Yukarıdaki dört vaka.

### A-005 — Ağırlıklı başarı puanı: ağırlık `1` ise çarpan 1.0, `2` ise 0.02 (monoton olmayan eşik)
- Dosya: `karne_hesaplamalar.py:348-351`, çağıranlar: `micro/modules/bireysel/routes.py:546`, `process_performance_service.py:117`
- Kanıt (deneme): `hesapla_agirlikli_basari_puani(4, 1)` → **4.0**, `(4, 2)` → **0.08**, `(4, 0.5)` → 2.0. `if agirlik > 1: /100 else float(agirlik)` — `%1` ağırlık 100% gibi hesaplanıyor.
- Etki: Bireysel performans ekranında %1 ağırlıklı PG, %2 ağırlıklıdan 50 kat daha fazla katkı verir; toplam bireysel puan şişer.
- Önem: Orta · Etiket: **kesin hata**
- Çözüm: Ağırlık birimini tek bir yerde sabitle (DB'de 0-100 yüzde, `weight` kolonu). Fonksiyon her zaman `/100` yapsın; 0-1 fraksiyon kabulü kaldırılsın veya çağıran dönüştürsün.
- Efor: 1 saat (+ çağıran kontrolü) · Test: ağırlık 1/2/100 için 0.04/0.08/4.0.

### A-006 — Karne API'si yöntem etiketini ve sayı biçimini motordan farklı çözüyor
- Dosya: `micro/modules/surec/routes_karne.py:294-330`
- Kanıt:
  ```python
  def _parse_float(v): return float(v) if v not in (None,"") else None     # '4,5' ve '%90' -> None
  ... if m in ("toplama","toplam") ... elif m == "ortalama" ... else: last   # 'AVG', 'SUM', 'Son Değer' -> son değer
  ```
  Motor ise `normalize_aggregation_method` (`AVG/SUM/LAST/Ortalama/Toplama/Son Değer`) ve Türkçe sayı ayrıştırıcı kullanıyor. Kod yorumundaki ölçüme göre `kpi_year_configs.calculation_method` içinde `AVG` 35 satır. Ayrıca toplama sonucu `str(sum(...))` → `0.30000000000000004` gibi float artıkları ekrana gidiyor.
- Etki: `AVG` etiketli PG için karne yıl özeti/dönem hücresi **ortalama yerine son değer** gösterir; `SUM` etiketi (varsa) toplam yerine son değer. `4,5` ya da `%90` gibi girişler karne hücresinde hesaba girmez, motorda girer. Aynı PG: Karne ≠ Süreç skoru ≠ Vizyon.
- Önem: Yüksek · Etiket: **kesin hata**
- Çözüm: `_aggregate` ve `_rollup_year_actual` içinde `score_engine_service.aggregate_actuals`/`_parse_float` kullan; toplamı `round(...,6)` ile yaz.
- Efor: 2 saat · Test: Aynı girdiyle (`AVG`, [4,"5,5",6]) `year_rollup` = motor `aggregate_actuals` sonucu.

### A-007 — Dönem sonu tarihli (gelecek) kayıtlar motorda dışlanıyor, karne/health/rapor'da dahil
- Dosya: `score_engine_service.py:367, 288` (`KpiData.data_date <= as_of`) ↔ `routes_karne.py:253-258`, `process_health_service.py:22-28`, `routes_kpi_data.py:690-694` (tarih süzgeci yok); yazan taraf `routes_kpi_data.py:117-124` + `process_utils.last_day_of_period`
- Kanıt: Veri sihirbazı `data_date`i **dönemin son günü** yapıyor (Yıllık → 31 Aralık, Çeyrek 3 → 30 Eylül, Aylık Eylül → 30 Eylül). 10 Eylül'de girilen Eylül verisi `data_date=2026-09-30` > bugün olduğundan motor onu **görmüyor**; Karne görüyor.
- Etki: Cari dönem verisini girmiş kullanıcı Karne'de değeri görür ama Süreç skoru/Vizyon/K-Vektör aynı gün değişmez (dönem bitince değişir). Yıllık girişler yıl sonuna kadar skora hiç yansımaz. "Veri girdim ama puan değişmedi" şikayetinin muhtemel kaynağı.
- Önem: Yüksek · Etiket: **kesin hata** (kodla; tasarım niyeti yoruma açık)
- Çözüm: Süzgeci `data_date <= as_of` yerine dönem başlangıcına göre yap (`period_type/period_no` ile dönem başlamışsa dahil) veya tek kural belirleyip bütün tüketicilere uygula (motor, karne, health, k_rapor). Yeni sihirbaz tarihi dönem sonu olarak kalabilir.
- Efor: 4 saat · Test: bugün 10 Eylül, `aylik/9` girişi → motor skorunda yer alır.

### A-008 — `process_health_service` yıllık config, tarih kesimi ve tutarlı yön kontrolü uygulamıyor
- Dosya: `process_health_service.py:33-37, 22-28, 60-66`
- Kanıt: `kpi.target_value`, `kpi.direction`, `kpi.data_collection_method` (ProcessKpi) kullanılıyor; `get_kpi_configs_bulk`/plan yılı yok. `as_of` süzgeci yok. `(kpi.direction or 'Increasing') != 'Decreasing'` büyük/küçük harfe duyarlı (`compute_pg_score` ise `.lower()`). Veri yoksa ve hedef çözülemezse **yıl-bağımsız** `kpi.calculated_score` (başka yılın son hesabı olabilir, bkz. A-016) skora katılıyor. PG verisi yokken `skor = surec_ilerleme` ama `durum='Veri yok'` — skor ve durum çelişir. Ağırlık kullanmadan düz ortalama.
- Etki: Süreç Karnesi üstündeki "Süreç sağlığı" (`routes_karne.py:599`), AI özeti ve uyarılar, aynı süreç için Süreç skorundan (motor) farklı yüzde gösterir. Yıllık hedefi değişen PG'de sağlık eski hedefle hesaplanır.
- Önem: Orta-Yüksek · Etiket: **kesin hata**
- Çözüm: Sağlık hesabı motorun `get_pg_scores_from_kpi_data` çıktısını kullanmalı; `0.7*PG + 0.3*ilerleme` bileşimi ayrı kalabilir.
- Efor: 3 saat · Test: Yıllık config'te hedef 200 (ProcessKpi'da 100) → sağlık skoru motorla aynı PG oranını kullanır.

### A-009 — K-Rapor uyarı/kritik PG uçları: tek son kayıt, ham `float()`, yöntem ve yıl hedefi yok
- Dosya: `micro/modules/k_rapor/routes.py:992-998, 1908-1916, 2170-2177` (ve `:288-300` matris)
- Kanıt: `float(kpi.target_value)`, `float(d.actual_value)`; hata `except (ValueError, TypeError)` ile yutuluyor (`:1015` civarı). Hedef "20-24", "%90", "1.200,5" ise PG listeden **sessizce düşer**. Gerçekleşen olarak yalnız **en son** satır kullanılıyor; `Toplama` yöntemli PG'de aylık değer yıllık hedefe bölünür (kritik sanılır). Yıllık config hedefi yerine `kpi.target_value`.
- Etki: "Kritik PG", "Uyarı", "Kurumsal vs PG dağılım" kartları motordan farklı PG listesi/yüzdesi gösterir. Biçimi bozuk PG'ler hiçbir uyarıda yer almaz (görünmez risk).
- Önem: Yüksek · Etiket: **kesin hata**
- Çözüm: Bu uçlar `get_pg_scores_from_kpi_data(...)` çıktısını kullansın.
- Efor: 3 saat · Test: SUM yöntemli PG, aylık [10,10,10], hedef 120 → kritik listesinde %25 (motor) görünmeli, %8 değil.

### A-010 — Kanban JS: azalan yönde gerçekleşen 0 → %0 (backend 100)
- Dosya: `ui/static/platform/js/surec.js:1789-1791`
- Kanıt: `pct = compareVal > 0 ? Math.round((skorTarget / compareVal) * 100) : 0;` Backend `compute_pg_score` Karar 5: azalan + gerçekleşen 0 → 100. Ayrıca `computeCellTargetMicro` (`:825-827`) `tv <= 0` hedefi `null` yapıyor (backend: azalan sıfır hedef geçerli) ve yalnız `Ortalama/Son Değer/Toplama/Toplam` etiketlerini tanıyor (`AVG` ve `SUM` Toplama gibi bölünmez → ay hedefi yıllık hedef kalır). `parseFloat("%90")` NaN.
- Etki: İş kazası, hata sayısı gibi "azalması iyi" PG'lerde gerçekleşen 0 iken Kanban kartı kırmızı/%0, Karne kartı yeşil/%100.
- Önem: Yüksek · Etiket: **kesin hata**
- Çözüm: API'ye hesaplanmış yüzdeyi gönder (tek kaynak), JS'te yeniden hesaplama yapma; kısa vadede bu iki koşulu backend ile hizala.
- Efor: 2 saat · Test: azalan PG hedef 5, gerçekleşen 0 → %100 yeşil.

### A-011 — Negatif hedefte artan yön tersine çalışıyor
- Dosya: `score_engine_service.py:206-212` (`compute_pg_score`)
- Kanıt (deneme): `compute_pg_score(-10,-5,'Increasing')` = 50.0, `(-10,-20)` = **100.0** (daha kötü sonuç tam puan); azalan: `(10,-3,'Decreasing')` = 0.0, `(-10,-5,'Decreasing')` = 100.0.
- Etki: Kâr/zarar, net nakit, sapma gibi negatif olabilen PG'ler ters puanlanır. (PG sayısı DB'de ölçülmedi.)
- Önem: Orta · Etiket: **kesin hata** (fonksiyon düzeyi; veride negatif hedef sayısı bilinmiyor)
- Çözüm: Hedef < 0 durumunda oran yerine fark tabanlı kural veya puanlanamaz (`None`) + kullanıcıya uyarı.
- Efor: 1-2 saat · Test: yukarıdaki dört girdi.

### A-012 — EFQM K7.1 "PG hedef başarısı" (kriterin %50'si): yön yok, yıl yok, satır bazlı
- Dosya: `app/services/efqm_assessment.py:274-283`
- Kanıt:
  ```sql
  kd.actual_value::float >= kd.target_value::float  ... FROM kpi_data kd JOIN process_kpis k ... WHERE p.tenant_id=:t AND kd.is_active=true
  ```
  (1) `Decreasing` PG'lerde başarı ters sayılıyor; (2) `kpi_data.year` / plan yılı süzgeci yok (tüm yılların tüm satırları); (3) PG değil **satır** sayılıyor, günlük/aylık giren PG baskın; (4) regex yalnız `^-?[0-9]+\.?[0-9]*$` → `4,5`, `%90`, aralıklı hedef dışarıda; (5) satırın kendi `target_value` boşsa satır hiç sayılmıyor (PG hedefi kullanılmıyor).
- Etki: EFQM puanı (Sonuçlar boyutu, 1000'lik toplamın büyük kısmı) yıl seçici ne olursa olsun aynı; azalan PG'ler başarısız görünür. Raporlarda gösterilen "Hazırlık/EFQM seviyesi" yanlış.
- Önem: Yüksek · Etiket: **kesin hata**
- Çözüm: Motorun `pg_scores`'u (yıl bazlı) üzerinden "skor >= 100" PG oranı kullan.
- Efor: 3 saat · Test: Biri azalan iki PG (iki yıl) → seçili yıl ve yön hesaba girer.

### A-013 — EFQM: faaliyet/risk/paydaş sayıları plan yılı süzgeçsiz, puanlar banker yuvarlama
- Dosya: `efqm_assessment.py:305-325` (faaliyet sorguları `processes p` ile join ama `p_py_clause` yok), `:725-739` (`pts = round(sc/100*weight)`)
- Kanıt: Süreçler yıl başına klonlanıyorsa (clone yaklaşımı) `process_activities` tüm yıl klonlarını sayar; `activity_overdue*5` ceza mutlak değer. `round()` Python'da yarıya en yakın çifte yuvarlar (2.5 → 2).
- Etki: Çok yıllı kurumda gecikmiş faaliyet cezası şişer (K5.4); kriter puanları 0.5 sapar. Alt bileşen toplamı ile kriter puanı farklı yuvarlandığı için ekranda toplamlar tutmayabilir.
- Önem: Düşük-Orta · Etiket: olası risk / iyileştirme
- Çözüm: `p_py_clause` ekle, yuvarlamayı `Decimal ROUND_HALF_UP` yap, toplamı alt bileşenlerden üret.
- Efor: 2 saat · Test: iki yıllı tenant, ikinci yıl klonunda gecikmiş faaliyet, yıl 1 seçili → ceza yalnız yıl 1.

### A-014 — Harici API `POST /api/v1/kpi-data`: `year` ile `data_date` ayrışabiliyor, sunucu tarihi kullanılıyor
- Dosya: `micro/modules/api/routes.py:82-88`; ayrıca `routes_kpi_data.py:128-129` (`date.today()`), `:664` (`date.today().year`), `routes_process.py:171`
- Kanıt: `year=int(data.get("year", date.today().year)), data_date=date.today()`. Kullanıcı `year=2025` yollarsa kayıt `year=2025`, `data_date=2026-xx`. Motor/Karne `KpiData.year == yıl` ile süzer; `data_date_to_period_keys` ise `d.year != year` için `[]` döner (`process_utils.py:68`). Sonuç: yıl toplamında var, dönem hücrelerinde yok. Ayrıca plan yılı/mühür (K8) `muhur_engeli(kpi)` ile **kayıt yılına göre değil KPI'ya göre** kontrol ediliyor ve `entity_exists_in_year` yok. `date.today()` sunucu saatidir (UTC konteyner); TR saatiyle 00:00-03:00 arası, özellikle 1 Ocak'ta kayıt bir önceki yıla düşer (`today_tr()` kullanılmıyor).
- Etki: Dönem tablosu ile yıl özeti uyuşmaz; yılbaşı gecesi girişler önceki (belki mühürlü) yıla gider.
- Önem: Orta · Etiket: **kesin hata** (year≠data_date) / olası risk (saat dilimi)
- Çözüm: `year = data_date.year` türet, `data_date` alanı kabul et, `today_tr()` kullan, `kpi-data/add`'deki plan yılı/mühür akışını paylaş.
- Efor: 2 saat · Test: `year=2025` gönder → 400 veya `year=data_date.year`.

### A-015 — Legacy skor motoru ve legacy karne servisi farklı formül kullanıyor (hâlâ kayıtlı)
- Dosya: `services/score_engine_service.py:30-75, 110-135` (API: `api/routes_ai.py:103, 196, 218`), `app/services/process_performance_service.py:79-89`
- Kanıt: Legacy `compute_pg_score`: azalan + gerçekleşen 0 → `None`, hedef 0 → `None`; yalnız **son** veri (`veri_tarihi desc` ilk satır), toplulaştırma yok; `_parse_float` yalnız `,`→`.`; hiyerarşide `_default_weight` karışık ağırlık toplamı ≠ 100 hatasını taşıyor. `process_performance_service.get_process_performance`: `['Toplama','SUM']` dışı (yani `Son Değer` de) **ortalama** alıyor; `parse_basari_puani_araliklari` yeni bant biçiminde `{}` döndürüp puansız kalıyor (1240 PG biçimi).
- Etki: `/api/vision-score`, `/api/ai-coach` ve `/api/.../performance` uçlarından beslenen ekran/AI özeti, modern motorla farklı vizyon/PG puanı verir. `current_user.kurum_id` modern kullanıcıda boş olabilir (400).
- Önem: Orta · Etiket: olası risk (kullanım sıklığı doğrulanmadı)
- Çözüm: Bu uçları modern `compute_vision_score` üzerine yönlendir veya kapat (strangler); legacy karne servisini `hesapla_basari_puani_ham` ile hizala.
- Efor: 4-6 saat · Test: Aynı veri iki uçta aynı vizyon puanı.

### A-016 — `calculated_score` yıl/tarih bağımsız, yan etkiyle üzerine yazılıyor; tüketiciler bayat değer okuyor
- Dosya: `score_engine_service.py:497-498`; `routes_kpi_data.py:219-222` (`recalc_on_pg_data_change(tenant, year_val)` → `persist=True`); tüketiciler `micro/modules/kurum/kurum_overview.py:188-221`, `process_health_service.py:38-44`, `sp/helpers.py:301`
- Kanıt: `recalc_on_pg_data_change` her veri ekleme/düzenlemede `persist_pg_scores=True` ile çalışıyor ve `year_val` kaydın yılı. 2025 verisi düzeltildiğinde `ProcessKpi.calculated_score` **2025** skoruyla yazılır. Skoru `None` olan (veri yok) PG'nin eski değeri silinmez (`if sc is None: continue`). Kolon yılsız.
- Etki: Kurum Genel Bakış'taki "ortalama PG skoru / düşük skorlu PG sayısı" hangi yılın verisi olduğu belirsiz ve bayat değer taşır; `health` fallback'i aynı şekilde.
- Önem: Orta · Etiket: **kesin hata** (mekanizma kodla doğrulandı)
- Çözüm: Persist'i yalnız cari plan yılı için yap ve ölçülemeyen PG'de `calculated_score=None` yaz; ya da kolonu kaldırıp tüketicilere motor çıktısı ver.
- Efor: 3 saat · Test: 2025 verisi düzenle → 2026 `calculated_score` değişmemeli.

### A-017 — Satır skoru (`status_percentage`) PG'nin ana hedefine ve tek satıra göre hesaplanıyor
- Dosya: `app/services/kpi_data_score_service.py:79-103`; tüketiciler `k_rapor/routes.py:650, 1510`, `raporlar/routes_faz1.py:859`, `faz4.py:192`
- Kanıt: Satırın `target_value`ı boşsa `kpi.target_value` (ProcessKpi) kullanılıyor; yıllık config hedefi yok. Toplama yöntemli PG'de her aylık satır **yıllık hedefe** karşı `Tutmadı` sonucu alır. KPI hedefi sonradan değişince eski satırların `status_percentage`si yeniden hesaplanmaz.
- Etki: "En iyi/en kötü PG", "trend skorları", BI dışa aktarımı ve masaüstü kartı, motorun yıllık özetinden bağımsız ve çoğu zaman düşük yüzde gösterir.
- Önem: Orta · Etiket: olası risk
- Çözüm: Raporlarda satır skoru yerine yıl özeti kullan veya satır skoru yalnızca "Ortalama/Son Değer" yöntemleri için anlamlı olsun; hedef değişiminde toplu yeniden hesap.
- Efor: 4 saat · Test: Toplama yöntemli PG, 3 satır, hedef yıllık → rapor yüzdesi = motor yüzdesi.

### A-018 — Toplama (SUM) yönteminde karışık periyot çift sayımı ve yıl-içi (YTD) toplam
- Dosya: `score_engine_service.py:362-370, 405`; `routes_karne.py:317-322`
- Kanıt: Yıl içindeki **tüm** kayıtlar (period_type'a bakmadan) toplanıyor. Aynı PG'de hem aylık girişler hem yıllık özet girişi (veya hem çeyreklik hem aylık) varsa SUM iki kez sayılır. Ayrıca yıl bitmeden SUM, tüm yılın hedefiyle kıyaslandığından Ekim'de skor ~%80'e sınırlı kalır.
- Etki: Satış/üretim gibi toplanan PG'lerde skor yıl boyunca düşük görünür; karışık periyotlu girişte abartılı.
- Önem: Orta · Etiket: olası risk (veri deseni ölçülmedi)
- Çözüm: Dönem tipi başına tek tip zorunlu veya hedefi geçen süreye orantıla (YTD hedef) ve karışık period_type uyarısı.
- Efor: 4+ saat (tasarım kararı gerekir) · Test: aylık 12 kayıt + yıllık özet kaydı → toplam bir kez.

### A-019 — Sınıf motoru alt strateji = basit ortalama; K-Vektör = bağlantı oranlı
- Dosya: `score_engine_service.py:610-623` ↔ `k_vektor_engine.py:96-107` (`_link_fractions_for_process`)
- Kanıt: Klasik motor bağlı süreçlerin ortalamasını alıyor, `ProcessSubStrategyLink` katkı yüzdesini yok sayıyor; K-Vektör tenant'ında aynı bağlantı yüzdeleri kullanılıyor.
- Etki: Tenant bayrağı (`k_vektor_enabled`) açılıp kapanınca aynı veriden farklı alt strateji skoru çıkar; "Katkı %" alanı klasik modda etkisiz.
- Önem: Düşük · Etiket: iyileştirme
- Çözüm: Klasik motorda da bağlantı oranlarını kullan veya arayüzde alanı klasik mod için gizle.
- Efor: 2 saat · Test: iki süreç %70/%30 bağlı → skor ağırlıklı.

### A-020 — Periyot eşlemesi: haftalık tanım iki farklı kuralla, geçersiz periyot sessizce kaydırılıyor
- Dosya: `process_utils.py:17-56, 59-82`; `process_activity_service.py:~25` (`_get_activity_period_fields`: ISO hafta)
- Kanıt (deneme): Şubat 2027'de `haftalik` hafta 4 ve 5 aynı tarihe (2027-02-28) gidiyor, anahtar `haftalik_4_2` (5. hafta verisi 4.nün üstüne yazılır). `last_day_of_period(2026,'ceyrek',5)` → 31 Aralık (Q4), `('aylik',13)` → Aralık (sessiz sıkıştırma), `halfyear` için `None`. Faaliyetten gelen otomatik PGV haftada **ISO hafta no (1-53)** kullanırken sihirbaz **ay içi hafta (1-5)** kullanır.
- Etki: Haftalık periyotlu PG'de 5. hafta girişi 4. haftanın hücresinde görünür; otomatik PGV'ler haftalık hücrede yanlış yerde.
- Önem: Düşük · Etiket: olası risk
- Çözüm: Geçersiz `period_no` için 400 dön; hafta tanımını tek fonksiyona topla (Pazartesi tabanlı ISO veya ay-içi).
- Efor: 2 saat · Test: Şubat hafta 5, `ceyrek/5`, `aylik/13`.

### A-021 — Yön (direction) karşılaştırmaları büyük/küçük harf ve eş anlamlı yazımlara dağınık
- Dosya: `process_health_service.py:37`, `k_rapor/routes.py:37`, `surec.js:1788`, `karne_hesaplamalar.py:213`
- Kanıt: Dört yerde dört kural (`!= 'Decreasing'`, `("Decreasing","decreasing","lower_is_better")`, `=== "Decreasing"`, `.lower() == 'decreasing'`). Deneme: `compute_pg_score(10,5,'Azalan')` = 50 (artan sayılıyor); `hesapla_basari_puani_ham(5, {"1":"50-","5":"-9"}, 'Azalan')` → puan 1 (en iyi değere en düşük puan).
- Etki: DB şu an yalnız `Increasing`/`Decreasing` taşıyor (belgede ölçülmüş); Excel içe aktarma/API ile başka yazım girerse sessizce artan sayılır. Şimdilik gizli risk.
- Önem: Düşük · Etiket: olası risk
- Çözüm: `normalize_direction()` + giriş doğrulaması (kaydederken), tüm karşılaştırmaları ona bağla.
- Efor: 1-2 saat · Test: `'azalan'`, `'DECREASING'`, `'Azalan'` aynı sonuç.

### A-022 — Karne PG hücrelerinde float gösterim hataları ve `year_rollup` yuvarlaması
- Dosya: `routes_karne.py:306-307` (`str(sum(...))`), `:323` (`round(...,6)`)
- Kanıt: `str(0.1+0.2)` = `0.30000000000000004`; ortalama için `round(...,2)` ama yıl özeti `round(...,6)` → hücre ve özet farklı hassasiyette.
- Etki: Görsel; yeniden hesaplanan başarı puanı banda sınırda farklı düşebilir.
- Önem: Düşük · Etiket: iyileştirme · Çözüm: tek yuvarlama kuralı (A-006 ile birlikte). Efor: 0.5 saat.

---

## 2. "Aynı gösterge için çok yol" doğrulaması

| # | Yol | Dosya | Hedef kaynağı | Yöntem etiketi | Sayı biçimi | Tarih kesimi | Çıktı |
|---|---|---|---|---|---|---|---|
| 1 | Motor | `score_engine_service.get_pg_scores_from_kpi_data` | yıllık config (+ aralık çözümü) | `AVG/SUM/LAST/TR` | TR + `%` `₺` | `data_date <= bugün (TR)` | oran 0-100 |
| 2 | Karne API | `routes_karne.surec_api_karne` | yıllık config | yalnız `ortalama`/`toplam(a)`, gerisi son | düz `float` | yok | rollup + bant puanı (1-5 veya 0-100) |
| 3 | Score detail | `routes_kpi_data.surec_api_kpi_score_detail` | `kpi.target_value` gösterimi; bant için config | `aggregate_actuals` (doğru) | düz `float` | yok | bant puanı |
| 4 | Health | `process_health_service` | ProcessKpi | `aggregate_actuals` | TR | yok | oran (düz ort.) |
| 5 | k_rapor uçları | `k_rapor/routes.py` (3 yer + matris) | ProcessKpi | yok (son değer) | düz `float` | yok | oran |
| 6 | Kanban JS | `surec.js:1738-1792` | ham | `Ortalama/Son Değer/Toplama` | `parseFloat` | yok | oran, azalan 0 → %0 |
| 7 | EFQM K7.1 | `efqm_assessment.py:274` | satır hedefi | yok | regex | yok | `>=`, yön yok |
| + | Satır skoru | `kpi_data_score_service` | satır/ProcessKpi | tek satır | TR | yok | `status_percentage` |
| + | Legacy | `services/score_engine_service.py` | legacy PG | son veri | `,`→`.` | `<= as_of` | oran |

Karşılaştırma sonucu: **Aynı girdi** (PG hedef 100, yöntem `AVG`, gerçekleşen "80", "90", "%100") için yol 1 ortalama (≈90) üzerinden skor üretir; yol 2 son değer; yol 5 yalnızca son satır; yol 7 "satır >= hedef" ölçütü. Hedef `20-24` ise yol 1 ve 4 çözer, yol 5 PG'yi atar. Azalan + gerçekleşen 0 için yol 1 = %100, yol 6 = %0. Önerilen çözüm (belgedeki `pg_yillik_ozet`) yerinde: tek "yıllık özet" fonksiyonu yazılıp 2, 3, 4, 5, 6, 7 numaralı yollar ona bağlanmalı. A-002, A-006, A-008, A-009, A-010, A-012 bu birleşmenin gerekçesini oluşturur.

## 3. Kontrol edilip sorun bulunmayanlar
- Hedef 0 + azalan (Karar 4) ve `gerçekleşen 0` azalan (Karar 5) motorda doğru; `_distribute_weights` karışık ağırlıkta 60/20/20 üretiyor (denendi).
- `_resolve_target_for_calculation`: `20-24` artanda 20, azalanda 24 (denendi).
- Plan yılı süzgeci motorda `plan_year_id IS NULL` legacy kayıtları tenant koşuluyla dahil ediyor (doğru); `plan_year_id == py.id` kolunda tenant koşulu yok ama plan yılı kuruma özgü (düşük risk).
- Bant biçimi `max: null` üst sınırsız, çakışmada en yüksek puan (tutarlı).
- `D0` (`lower_is_better`) k_rapor'da `_azalmasi_iyi` ile kapanmış.
