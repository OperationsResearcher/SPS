# Admin Araçları → Hata Kontrolü — Tasarım Belgesi

> Durum: **TASARIM / mutabakat** (henüz kod yok). 2026-06-07.
> Kullanıcı ile soru-cevap ile karara bağlandı. Kod yazımı bu belgenin onayından sonra.
> İlgili kurallar: `docs/KURALLAR-MASTER.md` (§1 Altın Kural, §8 Ortamlar).

---

## 1. Amaç

Genel admin'in, **bir IDE açmadan / Claude olmadan**, admin panelindeki bir butona basarak
uygulamanın sayfalarını ve özelliklerini otomatik gezip **çalışmayanları raporlamasını** sağlamak.

Bu, "Admin Araçları" adlı **genişleyebilir** bir bölümün ilk aracıdır. İleride aynı başlık
altına başka admin araçları eklenecek.

---

## 2. Karar Günlüğü (kullanıcı ile mutabık)

| # | Konu | Karar |
|---|------|-------|
| K1 | Erişim | **Yalnız genel admin** (platform `Admin` rolü). tenant_admin dahil kimse giremez. |
| K2 | Konteyner | Sol menüde yeni **"Admin Araçları"** grubu; genişleyebilir; ilk araç **Hata Kontrolü**. |
| K3 | Tespit derinliği | Sayfa erişimi **+ özellik (buton/form/AJAX) gerçekten çalışıyor mu** (tam aktif). |
| K4 | Keşif | **Hibrit**: route haritası (474 parametresiz GET) ⊕ ana ekrandan BFS link gezme. |
| K5 | Parametreli sayfalar | v1'de **atla** (135 adet `/<id>`). Sonra eklenebilir. |
| K6 | Çalışma biçimi | **Arka planda + canlı ilerleme** (uzun sürer). |
| K7 | Aktif test verisi | **tomofiltest** adlı izole kurum (Tomofil'den **tam klon**, **satır-satır id-remap** tekniğiyle). |
| K8 | tomofiltest sıfırlama | **Wipe + yeniden klonla** (ayrı snapshot yok; her sıfırlamada tomofiltest silinip Tomofil'den taze kopyalanır). |
| K9 | Ortam kapsamı | **v1 yalnız Yerel.** Test/Demo/Yayín için **her biri ayrı açık onay** gerekir (kullanıcı tek tek onaylar). Hedef mimari her non-prod ortamda kendi tomofiltest'i; ama kurulum **Yerel'den başlar**, diğerlerine ancak ayrı onayla genişler. |
| K10 | Giriş/kullanıcı | tomofiltest'e **sentetik tek admin** yaratılır; gerçek kullanıcı klonlanmaz. |
| K11 | İnşa sırası | **Önce tomofiltest klonu**, sonra tarayıcı/crawler. |

---

## 3. KIRMIZI ÇİZGİLER (tartışmasız)

0. **Kurulum kapsamı: v1 YALNIZCA Yerel.** Test, Demo ve Yayín'a hiçbir şey kurulmaz/açılmaz —
   her ortam için **ayrı, açık kullanıcı onayı** şart. Onay olmadan o ortama deploy/etkinleştirme yapılmaz.
1. **Yayín'da ASLA çalışmaz.** Onay olsa bile otomatik değil; hem menü gizli hem her route ortam kilidi (`ENV == production` → 403).
2. **Aktif CRUD yalnız tomofiltest kurumunda.** Gerçek/demo Tomofil ve başka hiçbir kurum verisine dokunulmaz.
3. **Kara liste her zaman dışarıda:** `/logout`, `delete-my-account`, `export`, e-posta gönderimi,
   demo/end, deploy/apply gibi yıkıcı/oturum-bozan uçlar — pasif taramada bile çağrılmaz.
4. **Çift kapı:** menüyü gizlemek yetmez; her endpoint `Admin` değilse 403 döner.

---

## 4. Mimari — Genel Bakış

```
[Admin Araçları]  (sol menü, yalnız Admin)
   └─ [Hata Kontrolü]  (Yayín'da gizli/kilitli)
          │  "Taramayı Başlat"
          ▼
   [Arka plan işi] ──canlı ilerleme──▶ [Rapor: modül × ✅/⚠️/❌ × HTTP × hata özeti × link]
          │
   1) KEŞİF      : route haritası (474) ⊕ ana ekrandan BFS  → benzersiz URL listesi
   2) YÜRÜTME    : Playwright (headless Chrome), tomofiltest sentetik admini ile login
                   • her sayfa: JS hatası + başarısız XHR + hata bandı + HTTP kodu
                   • güvenli etkileşim: sekme/filtre/modal aç
                   • kayıtlı CRUD senaryoları → tomofiltest'te
   3) GÜVENLİK   : ortam kilidi (Yayín yok) · kara liste · tomofiltest izolasyonu · timeout
   4) SIFIRLAMA  : aktif koşu sonrası tomofiltest snapshot'tan geri yüklenir
```

---

## 5. Faz 1 (İLK İŞ) — tomofiltest izole kurumu

### 5.1 Klon mekanizması
- Kaynak: bulunulan ortamın Tomofil tenant'ı. Hedef: yeni `tenant_id` (tomofiltest).
- **FK graf sırası**: ebeveyn→çocuk; her tablo için `eski_id → yeni_id` haritası.
- Kapsam: tenant'a bağlı **tüm** tablolar (strateji, alt strateji, süreç, PG, kpi_data,
  faaliyet, proje, OKR/BSC/ESG, SWOT/TOWS, risk, initiative, plan_year…).
- **Klon sonrası**: tüm PG sequence'leri hizala (desync önlemi); eksik tablo kalmadığını doğrula.
- **Mevcut araçları yeniden kullan**: demo snapshot/restore mantığı (`demo_reset_service`) ve
  varsa tenant kopyalama yardımcıları incelenip temel alınacak (build aşamasında doğrulanır).

### 5.2 Sentetik admin (K10)
- tomofiltest içinde **tek bir tenant_admin** kullanıcı: ör. `tomofiltest-admin`,
  şifresi config/env'den (yalnız crawler bilir). Gerçek e-posta/şifre **kopyalanmaz**.

### 5.3 Kimlik & bulunabilirlik
- tomofiltest, `Tenant` üzerinde bir işaretle ayırt edilir (ör. `is_test = True` veya config
  `TEST_TENANT_SLUG = "tomofiltest"`). Sistem bu kurumu buradan bulur.

### 5.4 Sıfırlama (K8)
- Klon bir kez kurulur → tomofiltest **baseline snapshot**'ı alınır.
- Her aktif koşudan sonra: tomofiltest satırları temizlenip snapshot'tan geri yüklenir (hızlı).
- Tam yeniden klon (yavaş) yalnız elle "Kur/Yenile" ile.

### 5.5 Ortam (K9)
- Klon mekanizması ortamdan bağımsız; Yerel/Test/Demo'da kendi Tomofil'inden kendi tomofiltest'ini kurar.
- Yayín'da klon **çalışmaz** (kilit).

---

## 6. Faz 2 — Keşif (discovery)

- **Route haritası**: 474 parametresiz GET sayfa (kara liste çıkarılır).
- **BFS link gezme**: ana ekrandan başlayıp aynı-origin `<a href>` takip; menüye bağlı olmayan
  yetim sayfalar da yakalanır.
- **Hijyen**: sorgu parametreleri atılır; `/proje/1`,`/proje/2` → `/proje/<id>` desenine indirgenir
  (v1'de parametreliler atlanır); maks. derinlik ~4; toplam sayfa tavanı (~600).

---

## 7. Faz 3 — Yürütme (Playwright, pasif + güvenli)

- Headless Chrome; tomofiltest sentetik admini ile login.
- Her URL'e **taze navigasyon** (`page.goto`). **Kuyruk tabanlı**: hata olan sayfa kuyruğu
  bloklamaz; kaydedilir, sıradakine geçilir — "geri tuşu" gerekmez.
- Toplanan sinyaller: HTTP kodu, JS konsol hataları, **başarısız XHR/fetch**, hata bandı/boş-durum.
- Güvenli etkileşimler (yalnız okuyan): sekme değiştir, filtre, modal aç.
- Dayanıklılık: her sayfaya timeout; bağlam çökerse yeniden yaratılır; her URL `try/except` izole.

### 7.1 "Hata" yorumlama kuralları
| Durum | Sonuç |
|------|------|
| HTTP 200, hata izi yok | ✅ çalışıyor |
| HTTP 500 / 404 | ❌ kırık |
| HTTP 403 | ⚠️ yetki (çoğu zaman beklenen) |
| HTTP 302 → login | ❌ oturum/erişim sorunu |
| 200 + "İşlem tamamlanamadı" / Flask hata izi / JS hatası / başarısız AJAX | ⚠️/❌ |

---

## 8. Faz 4 — Aktif CRUD senaryoları (yalnız tomofiltest)

- "Her butonu tıkla" sihirli değildir; **kayıtlı senaryolar** kütüphanesi:
  ör. "Proje oluştur → düzenle → sil", "PG veri gir → kaydet".
- Her senaryo **sıfırdan** başlar (taze navigasyon); bir adım patlarsa senaryo iptal, hata kaydı,
  güvenli noktaya dön, sonraki senaryo.
- Koşu sonunda tomofiltest snapshot'tan geri yüklenir (§5.4).
- Senaryo kütüphanesi zamanla büyür (332 yazma ucu için kademeli).

---

## 9. Faz 5 — Rapor & cila

- Sonuç tabloları: `hata_kontrol_run` (koşu başlığı, ortam, başlangıç/bitiş, özet sayılar) +
  `hata_kontrol_sonuc` (url, modül, durum, http, hata özeti). Geçmiş koşular bedava gelir.
- Rapor ekranı: modüle göre gruplu, ✅/⚠️/❌ filtreli, sayfaya tıklanır link, koşu geçmişi.
- İleride: zamanlanmış otomatik koşu (gece), e-posta/özet.

---

## 10. Yol Haritası (özet)

| Faz | İçerik | Çıktı |
|-----|--------|-------|
| **1** | Admin Araçları menüsü + tomofiltest tam klon + sentetik admin + snapshot/restore | Test zemini hazır |
| **2** | Keşif (route ⊕ BFS) | URL listesi |
| **3** | Playwright pasif + güvenli tarama + yorumlama + arka plan/ilerleme | İlk gerçek rapor |
| **4** | Aktif CRUD senaryoları (tomofiltest) | Derin doğrulama |
| **5** | Rapor cilası, geçmiş, zamanlama | Olgun araç |

---

## 11. Açık / build-aşamasında netleşecek noktalar

- Mevcut tenant-klon/snapshot araçlarının ne kadarı yeniden kullanılabilir (demo_reset_service vb.).
- Ortam tespiti için kesin bayrak (config `ENV`/özel flag) — Yayín kilidi buna bağlanacak.
- Playwright + Chromium'un Docker imajlarına eklenmesi (Test/Demo) ve Yerel (Windows) kurulumu.
- tomofiltest kimliği: `Tenant.is_test` kolonu mu, config slug mu.
