# Katman Mimarisi — Yerel Test Yönergesi

> Kullanıcı için elle test rehberi. Kod tarafı doğrulandı (602 test + 70 smoke),
> bu belge **senin gözünle** kontrol içindir: ekranlar açılıyor mu, linkler doğru mu,
> kural çalışıyor mu.
> Tarih: 2026-07-17 · main: `1223050d` · Faz 0–6 tamamlandı · **Yayın'a çıkmadı**

---

## 0. ÖNCE BUNU YAP — stale süreç tuzağı

Bu makinede Ctrl+C süreci her zaman öldürmüyor; iki dinleyici kalırsa **eski koddan
500 alırsın** ve hiçbir test doğru sonuç vermez.

```bash
# 1. Çalışan var mı?
netstat -ano | findstr :5001

# 2. Varsa öldür (PID = son sütun)
taskkill /PID <pid> /F

# 3. Temiz başlat (auto-reload bu makinede güvenilmez)
python pybasla.py
```

**Doğrula:** `netstat -ano | findstr :5001` → **tek** satır LISTENING görmelisin.

Giriş: `admin@kokpitim.com` · Yerel DB = Yayın kopyası (tenant 13, users 451).

---

## 1. Otuz saniyelik sağlık kontrolü

Tarayıcıya sırayla yapıştır. Hepsi açılmalı:

| URL | Ne olmalı |
|---|---|
| `http://127.0.0.1:5001/k-plan/strategy` | Stratejik Planlama açılır |
| `http://127.0.0.1:5001/k-radar` | K-Radar hub açılır |
| `http://127.0.0.1:5001/k-report/cfo-dashboard` | CFO paneli açılır |

**Biri açılmazsa dur, bana söyle.** Gerisi anlamsız olur.

---

## 2. Eski adreslerin kırılmadığı (en kritik)

Yayın'da bookmark'lar ve e-posta linkleri var. Eski adres yazınca **yeni adrese
gitmeli**, hata vermemeli. Adres çubuğunu izle:

| Yaz | Adres çubuğu şuna dönmeli |
|---|---|
| `/sp` | `/k-plan/strategy` |
| `/sp/swot` | `/k-plan/strategy/swot` |
| `/process` | `/k-plan/process` |
| `/project` | `/k-plan/project` |
| `/reports/cfo-dashboard` | `/k-report/cfo-dashboard` |
| `/k-rapor` | `/k-report` |
| `/sp/tv` | `/k-radar/savas-odasi` ← Savaş Odası taşındı |

✅ **Aradığın şey:** sayfa açılıyor + adres yeni. 404/500 **yok**.

---

## 3. Üç katman — sidebar'da görünüyor mu

Sol menüye bak. Linkler şu şekilde olmalı (üstüne gelince adres alt köşede görünür):

- **Girdi:** Stratejik Planlama → `/k-plan/...` · Süreç → `/k-plan/process` ·
  Proje → `/k-plan/project` · Bireysel Performans → `/k-plan/individual/...`
- **Teşhis:** K-Radar → `/k-radar` · **K-Radar Araçları** → `/k-radar/ks`
  (eski adı "K-Analiz"di) · Savaş Odası → `/k-radar/savas-odasi`

✅ Hiçbir sidebar linki `/sp`, `/process`, `/reports` **olmamalı**.

---

## 4. En önemli davranış değişikliği — teşhis artık YAZMIYOR

Bu, katman mimarisinin kalbi ve **senin bir yeteneği kaybettiğin yer**. Bilerek yapıldı.

### 4a. K-Radar'da SWOT düzenlenemez (eskiden düzenlenebiliyordu)
1. `/k-radar/ks` aç → SWOT kartına tıkla
2. ✅ **Görmen gereken:** SWOT maddeleri görünüyor, **Kaydet düğmesi YOK**,
   onun yerine **"Stratejik Planlama'da düzenle"** düğmesi var
3. O düğmeye tıkla → `/k-plan/strategy/swot`'a gitmeli

### 4b. Girdi katmanında hâlâ yazabiliyorsun
1. `/k-plan/strategy/swot` aç
2. ✅ Madde ekle → **Kaydet** → kaydedilmeli
3. `/k-radar/ks`'e dön → eklediğin madde **orada da görünmeli** (aynı veri)

⚠️ **Bu doğru davranış:** veri tek yerde (girdi) yazılır, teşhis sadece gösterir.

---

## 5. Yeni girdi evleri (Faz 3'te açıldı)

Bu üç araç eskiden K-Radar'da yazılıyordu; artık girdi katmanında evleri var.
**Aynı ekran, iki adres, farklı yetki:**

| Araç | Girdi (yazabilirsin) | Teşhis (salt-oku) |
|---|---|---|
| Olgunluk | `/k-plan/process/maturity` | `/k-radar/kp/maturity` |
| Değer zinciri | `/k-plan/process/value-chain` | `/k-radar/kp/value-chain` |
| Paydaş | `/k-plan/strategy/stakeholder` | `/k-radar/cross/stakeholder` |

**Test:** Her satır için iki adresi de aç.
✅ Girdi adresinde ekleme/düzenleme düğmeleri **var** · Teşhis adresinde **yok**,
ama veri **aynı** görünüyor.

---

## 6. Risk kuralı — "her risk bir kaynağa bağlı" (Faz 5)

1. `/k-radar/risk` aç → **Yeni Risk** ekle
2. **Kaynak** alanına bak
   ✅ "Manuel" seçeneği **YOK** · "— Kaynak seçin —" ile başlıyor ·
   seçenekler: SWOT, PESTEL, Porter, Süreç, Proje
3. Kaynak **seçmeden** kaydetmeyi dene
   ✅ Kaydetmemeli — hata mesajı vermeli
4. Kaynak seçip kaydet → ✅ kaydedilmeli, listede kaynağı **Türkçe** görünmeli

### Mevcut riskler
Listeye bak: eski "manual" riskler artık kaynağa bağlı (PESTEL/SWOT/Süreç/Proje).

⚠️ **Bilerek dokunulmadı:** Eskişehir Makine (tenant 28) kurumunun 10 riski hâlâ
`Finansal`, `Operasyonel`, `Düzenleyici` gibi **kategori** değeri taşıyor
("AB CBAM karbon vergisi" → `Düzenleyici`). Bunlar gerçek müşteri verisi; doğru
eşlemesi iş bilgisi ister → **senin kararını bekliyor**.

---

## 7. Breadcrumb (Faz 6'da kırılmıştı, düzeltildi)

Sayfa başlığının üstündeki gezinme çizgisi:

| Sayfa | Breadcrumb'da görmen gereken |
|---|---|
| `/k-plan/strategy/swot` | **Stratejik Planlama** > SWOT |
| `/k-plan/process` | **Süreç Yönetimi** |
| `/k-report/cfo-dashboard` | **Raporlar** > CFO Dashboard |

✅ Üst bağlantı **görünüyor** olmalı (boş değil).

---

## 8. K-Radar hub linkleri (Faz 6'da 22 link düzeltildi)

`/k-radar` aç → kutulara tek tek tıklama, ama **birkaçını dene**
(Kurumsal Performans, Stratejik Analiz Paketi, K-Vektör Skoru).

✅ Hepsi açılmalı, adres `/k-report?tab=...` olmalı (eski `/k-rapor?tab=` değil).

---

## Bulursan bana şunu söyle

| Ne gördün | Bana yaz |
|---|---|
| 404 / 500 | **hangi URL'de** |
| Yanlış yere gitti | hangi linke tıkladın, nereye gitti |
| Kaydet düğmesi olmaması gereken yerde **var** | hangi sayfa |
| Kaydet düğmesi olması gereken yerde **yok** | hangi sayfa |
| Breadcrumb boş | hangi sayfa |

---

## Bilinen durumlar — hata DEĞİL

- **`/k-analiz`** hâlâ çalışıyor → `/k-radar/ks`'e gider. Eski bookmark'lar için
  bilerek bırakıldı.
- **Rapor katmanı sidebar'da yok** — K-Radar hub üzerinden erişiliyor. Mevcut
  tasarım, katman işinin kapsamı değildi.
- **`/reports/daily`, `/reports/dashboard`** yönlenmiyor — bunlar dış REST API
  (`ai_bp`/`api_bp`), UI değil. Sözleşmeleri bilerek korundu.
- **SP içindeki "Projeler" ekranı yok** — zaten hiçbir route render etmiyordu
  (ölü kod, Faz 6'da tespit edildi). Silme TASK-258'e bırakıldı.

---

## Test bitince

Bu iş **Yayın'a çıkmadı** (L paketleri kuralı: tüm iş yerelde birikir).
Test/Demo/Yayın'a gitmesi için senin **"deploy"** demen gerekiyor.

Kalan açık kararlar:
1. **Tenant 28'in 10 riski** — kategori değerleri kaynağa mı eşlensin, kategori
   ayrı kolona mı alınsın?
2. **Ölü proje zinciri** (`sp/projeler.html` + `sp_projeler.js` + 6 route) — TASK-258
3. **Şifre sızıntısı** — `scripts/docs/take_screenshots.py` (sen halledecektin)
