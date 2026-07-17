# Katman Mimarisi — Uygulama Yol Haritası

> Hedef tasarım: `KATMAN-MIMARISI-HEDEF.md`. Bu belge NASIL uygulanacağını verir.
> İlke: Yayın çalışıyor — hiçbir adım eski URL'yi kırmaz, her adım Test'te doğrulanır.
> Tarih: 2026-07-17 · Durum: PLAN (uygulama başlamadı)

---

## Stratejinin kalbi — neden bu iş yönetilebilir

Üç ölçülmüş gerçek, işi 10× küçültüyor:

1. **Endpoint adları korunur, sadece route PATH'i değişir.**
   `@app_bp.route("/sp/swot")` → `@app_bp.route("/k-plan/strateji/swot")` ama
   `def sp_swot_page()` adı AYNI kalır. Template'teki `url_for('app_bp.sp_swot_page')`
   otomatik yeni path'i üretir → **~64 template'e dokunulmaz.**

2. **Redirect kalıbı zaten var** (`k_rapor/routes.py:88`). Her eski path'e
   `redirect(url_for(yeni_endpoint), code=301)` — sıfırdan altyapı yok.

3. **Tek gerçek elle-iş: 6 template'te hardcoded URL** (`href="/sp"` gibi,
   `url_for` kullanmayan). Bunlar tek tek düzeltilir.

**Sonuç:** İş "412 route + 64 template elle değiştir" değil; "route path'lerini
değiştir + endpoint adlarını dondur + 6 hardcoded düzelt + redirect ekle."

---

## Aşamalar — sırayla, her biri bağımsız test edilebilir

### FAZ 0 — Hazırlık (kod yok, güvenlik ağı)
- [ ] Bu 4 belgeyi commit et (tasarım donmuş olsun).
- [ ] **Endpoint adı envanteri:** her route'un `def` adını çıkar → değişMEYECEK
      olanların listesi. Bu liste "sözleşme" — path değişir, ad değişmez.
- [ ] Redirect helper yaz: `_eski_url_redirect(yeni_endpoint)` tek fonksiyon.
- [ ] Test ortamında baseline smoke test (tüm sayfa route'ları 200/302 mi).

### FAZ 1 — Redirect altyapısı (davranış değişmez, ağ kurulur)
- [ ] Her modül için eski path → yeni path eşleme tablosu (kod sabiti).
- [ ] Eski path'ler 301 ile yeniye yönlendirsin AMA yeni path'ler henüz eskiyle aynı.
- [ ] Bu fazda kullanıcı HİÇBİR fark görmez — sadece redirect katmanı hazırlanır.
- [ ] Test: eski URL'ler hâlâ çalışıyor mu (301 → 200).

### FAZ 2 — Katman 2 (Teşhis) — EN DÜŞÜK RİSK, önce bu
K-Radar zaten teşhis; sadece netleştirilir.
- [ ] `/k-radar/*` path'leri katman/konu şemasına geçir (`/k-radar/surec/pareto`).
- [ ] **Savaş Odası taşı:** `/sp/tv` → `/k-radar/savas-odasi` (endpoint adı korunur).
- [ ] **Yazma API'lerini KALDIR:** K-Radar/KS'teki `sp_api_swot_save` çağrıları
      → K-Radar salt-oku olur (kullanıcı düzeltmek için Girdi'ye yönlendirilir).
- [ ] "K-Analiz" ikinci sidebar girişini kaldır (K-Radar zaten var).
- [ ] Test: teşhis ekranları okuma yapıyor, yazma yok.

### FAZ 3 — Katman 1 (Girdi) ✅ UYGULANDI (2026-07-17, TASK-274)
- [x] SP → `/k-plan/strategy/*` · Süreç → `/k-plan/process/*` · Proje →
      `/k-plan/project/*` · Bireysel → `/k-plan/individual/*` (**202 route**)
      · URL dili: **İngilizce konu** (ölçüm: modüller zaten İngilizce'ydi; §2 kuralı)
- [x] **Olgunluk taşındı** → `/k-plan/process/maturity` (girdi evi, şablon paylaşımı)
- [x] **Paydaş + değer zinciri evleri inşa edildi** (kapsam genişlemesi, aşağıda)
- [x] **Hardcoded URL: 27'ymiş (6 değil)** → 26 düzeltildi, 3 bilerek bırakıldı
- [x] Eski adresler **307** redirect (301 değil — POST gövdesi korunmalı)
- [x] Test: 589 passed, sıfır regresyon · Faz 3 smoke 20/20 · Faz 2 smoke 16/16

🔴 **FAZ 4 İÇİN ZORUNLU DERS — path kapıları sessizce açılır**

Route path'i değişince **path önekine bakan güvenlik kapıları hata vermeden devre
dışı kalır**. Faz 3'te SP rol kapısı bu yüzden açıldı (test yakaladı). `/k-report/`
öneki eklenirken **bu 4 dosya AYNI commit'te** güncellenmeli:

1. `platform_core/__init__.py::_GATED_PREFIX_MODULE` — paket kapısı
2. `platform_core/__init__.py::_ROLE_GATED_PREFIX_MODULE` — rol/liderlik kapısı
3. `micro/core/module_registry.py` — modül `url` alanı (sidebar/launcher)
4. `app/middleware/legacy_sunset.py::_is_platform_canonical` — platform kanonik önek

Detay + kanıt: `ENDPOINT-SOZLESMESI.md` §Faz 3.

#### Faz 3 kapsam GENİŞLEMESİ — kullanıcı kararı 2026-07-17

Faz 2 ölçümü, Girdi katmanında **evi olmayan** 2 araç buldu (Faz 0 belgesine bak).
Olgunluk'tan farkları: onun evi hazırdı (süreç modülü), bunların yok — sadece
K-Radar'da yaşıyorlar. **Karar: Faz 3'te ev inşa edilir** (aynı dosyalara iki kez
girilmesin, ara dönemde katman kuralı delik kalmasın):

| Araç | Yazma route | Yeni girdi evi | Not |
|---|---:|---|---|
| **Paydaş** (`StakeholderMap`) | 4 | `/k-plan/strateji/paydas` | HEDEF belgede zaten listelenmiş |
| **Değer zinciri** (`ValueChainItem`) | 3 | `/k-plan/surec/deger-zinciri` | HEDEF belgede zaten listelenmiş |
| Olgunluk | 4 | `/k-plan/surec/olgunluk` | (zaten planlıydı) |

Her üçünde de K-Radar'da **salt-oku görünüm kalır** — veri orada görünmeye devam
eder, sadece yazma Girdi'ye taşınır (Faz 2'nin SWOT'ta yaptığının aynısı).

**Takvim (`k_radar_schedule_save`) kapsam DIŞI — ölçümle gerekçelendirildi:**
İş verisi yazmıyor; K-Radar'ın kendi rapor zamanlayıcı ayarını (açık/kapalı + saat)
kaydediyor. Katman kuralı iş verisi içindir; modülün kendi ayarı ihlal değildir.
→ K-Radar'da kalır, dokunulmaz.

### FAZ 4 — Katman 3 (Rapor) + BİRLEŞME — en büyük, en dağınık
- [ ] k_rapor + raporlar → `/k-report/*` altında birleştir.
- [ ] **Çakışan araçları tekilleştir** (risk 6+1, bireysel 5+1, anomali 2+1):
      en iyi olan kalır, diğeri redirect. Kör birleştirme YOK.
- [ ] `/reports` (İngilizce) → `/k-report` · dil kuralı uygulanır.
- [ ] Test: her rapor tek yerde, export/dağıtım çalışıyor.

### FAZ 5 — Risk borcu (ŞEMA + VERİ, ayrı koşabilir)
- [ ] Migration: `risk_heatmap_items`'a `source_id` + FK ekle.
- [ ] 35 gerçek riski geniş-kaynağa eşle (SWOT/PESTEL/süreç/proje):
      Kur→PESTEL, Yetenek→SWOT, Tedarik→süreç…
- [ ] `source=manual` seçeneğini kaldır (kaynaksız risk girişi engellenir).
- [ ] Test: her risk bir kaynağa bağlı, kaynaksız girilemiyor.

### FAZ 6 — Temizlik
- [ ] Eski redirect'leri koru (bookmark'lar için kalıcı) ama iç `url_for`'lar
      yeni endpoint'i kullansın.
- [ ] Sidebar ekran adları Türkçe + role göre ("Stratejik Planlama / K-Radar / Raporlar").
- [ ] Ölü "K-Analiz" izlerini temizle.

---

## Risk yönetimi

| Risk | Önlem |
|---|---|
| Yayın URL'leri kırılır | Her eski path → 301 redirect, kalıcı korunur |
| Template linkleri kopar | Endpoint ADLARI dondurulur → url_for otomatik uyum |
| Hardcoded URL 404 | Faz 3'te 6 dosya elle düzeltilir |
| Yarım kalırsa | Her faz bağımsız + Test'te doğrulanır; faz sınırında dururulabilir |
| Yayın'a erken çıkar | L paketleri kuralı: tüm iş yerelde birikir, Yayın deploy ayrı karar |

## Sıra mantığı — neden bu sıra
Faz 2 (Teşhis) önce çünkü **en düşük risk** (K-Radar zaten salt-teşhise yakın).
Faz 4 (Rapor birleşme) en sona çünkü **en dağınık + çakışma çözümü gerekiyor**.
Faz 5 (Risk) şema+veri olduğu için **paralel/ayrı** koşabilir — URL bölmesini beklemez.

## Kritik hatırlatma
Bu bütün iş kullanıcının **paketleme/segmentasyon** stratejisinin parçası. Her faz
sonunda "hangi paket hangi katmanı görür" gating kararıyla kesişir — izole yapılmaz.
Uygulama başlamadan önce kullanıcı onayı; her faz kendi dalında, Test'te doğrulanır.
