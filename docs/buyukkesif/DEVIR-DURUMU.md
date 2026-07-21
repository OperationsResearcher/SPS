# BÜYÜK KEŞİF DÜZELTMELERİ — DEVİR DURUMU

> **Son güncelleme:** 2026-07-21 · **Dal:** `claude/kesif-duzeltmeleri`
> **Kullanıcı kararı:** Bulgu S1 (Yayın DB parolası public GitHub'da) **KAPSAM DIŞI** —
> "tamamen dokunma". Ne rotasyon, ne dosya temizliği, ne git geçmişi. Kullanıcı ayrıca ele alacak.
> Diğer tüm bulgular onay beklemeden uygulanacak.

---

## Kaldığım yer

**3 commit atıldı, 756 test yeşil.** Sıradaki iş: aşağıdaki "9 kırık uç" listesi.

```
ea47a5e7  B1/M4 ölçülmedi != başarısız + kapsam göstergesi + rollback tuzağı
1bdfa0e7  F2/F10/F11/S5 + K1 geriye dönük doldurma
1fb86c93  K1/B2/B3/B4/B6/B7/B13/S3/K4/K5 — sessiz hesap hataları
```

---

## ✅ TAMAMLANAN (ölçümle doğrulandı)

| Kod | İş | Ölçülen sonuç |
|---|---|---|
| **K1** | `status_percentage` hiç yazılmıyordu | Merkezî servis + 5 yazma noktası. **515 satır** geriye dönük dolduruldu |
| **B2** | İki `karne_hesaplamalar`, üretim hatalı olanı kullanıyordu | `utils/` shim'e indirildi. `"4,5-9,5"` artık `(4.5, 9.5)` |
| **M1** | Başarı bantlarının %64,6'sı okunamıyordu | 1240 kayıtlık yeni format tanınıyor; parse boş dönerse **log'a düşüyor** |
| **B6** | Hedef sayıya çevrilemiyordu | **126 → 42**; kalan 42 bilinçli `'-'` |
| **B3** | `analytics_service` `direction` okumuyordu | `compute_pg_score`'a devredildi (604 azalan PG) |
| **B4** | `year` çözülüp kullanılmıyordu | Yıl filtresi + `data_date <= bugün` |
| **B7** | `lower_is_better` ölü koşulu | `k_radar_service` düzeltildi; kalan tek eşleşme yorum satırı |
| **B8** | Ham `float()` aralık hedeflerini atlıyordu | Aynı blokta düzeltildi |
| **B13** | `get_comparative_analysis` tenant filtresi yok | Filtre servise alındı + 4 çağırana `tenant_id` |
| **S3** | EVM kurumlar arası sızıntı | `compute_project_evm(pid, tenant_id=…)` |
| **K4** | Yeni müşterinin ilk sayfası 500 | `current_app.view_functions` koşulu kaldırıldı |
| **K5** | `NameError: today` | `date.today()` eklendi |
| **F2** | Saklı XSS (yetki yükseltme) | JS `_esc()` + sunucuda `sanitize_plain_text` |
| **F10/F11** | 36 kopya `esc()`, hiçbiri `'` kaçırmıyor | Merkezî `window.esc` (base.html) |
| **S5** | Sequence drift | **6/6 onarıldı**, `nextval` testiyle doğrulandı |
| **B1/M4** | "Ölçülmedi" 0 sayılıyordu (4 katman) | Tomofil `55.78→93.62`, KMF `6.48→85.60` + **kapsam** alanı |
| — | *(Rapor dışı)* Yutulan DB hatası rollback'siz | **7 uç 500→200** |

---

## 🔜 SIRADAKİ İŞ — 9 kırık uç

446 parametresiz GET ucu tarandı (KMF/t16 oturumu). Bu 9'u **hepsi düzeltmelerimden ÖNCE de
500 veriyordu** (`git stash` ile baseline karşılaştırması yapıldı — regresyon yok).

| Uç | Kök neden | Zorluk |
|---|---|---|
| `/admin/kule-iletisim` | `url_for('admin_bp.tenants')` — route yok, `tenants_archive` var | kolay |
| `/admin/strategy-management` | aynı | kolay |
| `/2fa/setup` | şablon yok: `auth/totp_setup.html` | orta |
| `/api/dashboard/executive` | `'<' not supported: NoneType and int` | orta |
| `/api/dokuman-merkezi` | `ProjectFile.scope` yok | orta |
| `/api/strategic-planning/graph` | `User.kurum` yok (legacy alan) | kolay |
| `/api/vision-score` | `expected ORM mapped attribute for loader strategy` | orta |
| `/debug/surec-data` | `User.username` yok | kolay |
| `/api/ai-coach/analyze` | GET'te JSON body bekliyor → 415 | kolay |

> **Not:** `admin_bp.tenants` 3 şablonda referanslı
> (`templates/admin/index.html:18,181`, `templates/layouts/admin_base.html:15`).
> Hafızadaki "route silme refleksi" dersi: Python + template ref'leri **aynı commit'te** taranmalı.

---

## 📋 KALAN PLAN (sırayla)

### P2
- **K2/K3/F4** — yıl seçicisine tepkisiz uçlar: `hub-summary` imzasında yıl yok,
  BI CSV'de yıl filtresi + `ORDER BY` yok, `micro/`'da 20 nokta hâlâ `date.today().year`
- **B11** — `get_anomaly_detection` ham metin üzerinde pandas `.mean()/.std()`
  (aynı dosyadaki `get_forecast`'ta belgelenip düzeltilmiş, burada atlanmış)
- **D2/D1/M2** — `calculation_method` tek kolonda iki dil (`Ortalama` 1050 / `AVG` 35)
- **F1/F3/F5** — karne yıl seçici standart kullanıcıda 403 alıyor; üç ayrı seçici
  aynı session anahtarını farklı uçlardan yazıyor; gizli seçici için 25 satır ölü kod
- **K6/K7/K9** — holding `_403()` çift tuple sarması; mühür açınca `active`→`draft` düşüyor
- **B5/B9/B10/B12/M3** — karışık ağırlıkta payda tutarsızlığı (64 süreç);
  azalan eşik `*1.20` yerine `/0.80` olmalı; `max(0.0, …)` eksik; üst 3 katmanda ağırlık yok

### P3
- **I2/I3/I4** — EN `.po`: 45 kaymış fuzzy (`'Tomofil' → 'Profile'`), placeholder kaybı,
  82 msgstr çelişkili paylaşım. **`--use-fuzzy` bir gün çalışırsa anında yayına çıkar**
- **S6/S10** — 121 noktada `str(e)` istemciye; 124 sessiz `except` (3'ü yetki kararı veriyor)
- **S4/S7** — data connector `@login_required`'sız; dosya yüklemede magic byte yok
- **S2** — `TENANT_GUARD_MODE=enforce` kademeli açılış
- **M11/M12** — "CMMI" ve "resmî EFQM seviyesi" ibareleri (türetilmiş gösterge, öyle denmeli)
- **D4/D6/D3** — `SwotAnalysis` iki dosyada aynı `__tablename__`, farklı şema;
  4 sarkan kolon modele yansıtılmamış (`is_included` ORM'den görünmüyor)
- **I6/F13** — JS i18n benimsenmesi 36/88 → en sık 50 dize

### Kapanış
- `docs/buyukkesif/00-YONETICI-OZETI.md` sonuç durumuyla güncellensin
- `docs/TASKLOG.md` girdisi
- Kullanıcıya merge/push sorulacak (**otomatik yapılmaz** — CLAUDE.md branch disiplini)

---

## ⚠️ YOL BOYUNCA ÇÜRÜTÜLEN RAPOR İDDİALARI

Ölçümle doğrulanmadan hiçbir bulgu düzeltilmedi; üçü yanlış çıktı:

| İddia | Ölçüm |
|---|---|
| **F15** — `pg_tablo_modal.js:306,317` kaçışsız | **YANLIŞ.** Zaten `escHtml()` kullanıyor. Değişiklik yapılmadı |
| **B7** — "iki dosyada" ölü koşul | **Biri zaten yoktu** (`analytics_service` farklı bir hataydı, B3 ile düzeldi) |
| **B1** — düzeltince Tomofil 80.02 olur | **93.62 çıktı** — rapor düz ortalama varsaymış, motor ağırlıklı kota kullanıyor |

---

## 🔍 RAPORDA HİÇ OLMAYAN, YOL BOYUNCA BULUNAN

1. **Yutulan DB hatası + rollback yokluğu** → 7 uç birden 500 (düzeltildi)
2. **`k_radar_kp_olgunluk` tablosu DB'de yok** — kodda 3 yerde geçiyor, migration'ı yazılmamış.
   Şu an `except` ile atlanıyor, olgunluk skoru performansa eşitleniyor. **Karar gerekiyor:**
   tablo mu oluşturulacak, kod mu kaldırılacak?
3. **`get_comparative_analysis` iki çağıranı zorunlu parametreyi geçirmiyordu** →
   `TypeError` → sessiz 500 (opsiyonel yapıldı)
4. **Eskişehir'in 289 PG'sinin hiçbirinde hedef tanımlı değil** → skor matematiksel olarak
   üretilemiyor. Hesap hatası değil, **veri kalitesi sorunu** — kullanıcıya söylenmeli
5. **`hesapla_onceki_yil_ortalamasi` iki kopyada farklı imzaya sahipti**
   (3 param vs 1 param). Shim ikisini de kabul ediyor

---

## Yeni araçlar (kalıcı)

```bash
python scripts/ops/sequence_drift_onar.py              # kontrol
python scripts/ops/sequence_drift_onar.py --calistir   # onar

python scripts/ops/kpi_data_skor_doldur.py             # kontrol
python scripts/ops/kpi_data_skor_doldur.py --calistir  # doldur
```

İkisi de varsayılan olarak **hiçbir şey yazmaz**; tablo listesi tutmaz (KURALLAR §8.6 ilkesi).
