# Skor Motoru – Tarayıcıdan Test Yönergesi

Son yapılan değişiklikleri (Skor Motoru, Vizyon puanı, PG/süreç/faaliyet tetikleyicileri) tarayıcıdan doğrulamak için bu adımları izleyin.

---

## Ön koşullar

1. **Uygulama çalışıyor olmalı**  
   Örn: `http://127.0.0.1:5001` veya kullandığınız port.

2. **Giriş yapmış olmalısınız**  
   Kuruma bağlı bir kullanıcı (kurum_id olan; örn. Technova kullanıcıları).

3. **F12 geliştirici araçları açık olsun**  
   **Network** sekmesinden istekleri ve yanıtları göreceksiniz.

---

## Test 1: Vizyon puanı API (GET – sadece hesapla)

**Amaç:** Point-in-time vizyon puanının hesaplandığını görmek.

1. Giriş yaptıktan sonra tarayıcıda şu adresi açın:
   ```
   http://127.0.0.1:5001/api/vision-score
   ```
   (Port farklıysa `5001` yerine kendi portunuzu yazın.)

2. **Beklenen:** JSON yanıt; örn:
   ```json
   {
     "success": true,
     "vision_score": 0,
     "as_of_date": "2026-02-01",
     "kurum_id": 1,
     "ana_strateji_scores": { ... },
     "alt_strateji_scores": { ... },
     "surec_scores": { ... },
     "pg_scores": { ... },
     "ana_stratejiler": [ { "id", "ad", "score", "agirlik", "vizyona_katki" }, ... ],
     "alt_stratejiler": [ { "id", "ad", "ana_strateji_id", "score" }, ... ],
     "surecler": [ { "id", "ad", "score" }, ... ],
     "performans_gostergeleri": [ { "id", "ad", "surec_id", "score" }, ... ]
   }
   ```
   - `vision_score`: 0–100 arası sayı.
   - Veri yoksa 0, veri varsa hesaplanan puan gelir.
   - İsimli listeler (ana_stratejiler, alt_stratejiler, surecler, performans_gostergeleri) skorları ad ile birlikte döner; ana_stratejiler'de `vizyona_katki` (ağırlıklı pay) da vardır.

3. **Tarih ile deneme:**  
   Aynı sayfada:
   ```
   http://127.0.0.1:5001/api/vision-score?as_of_date=2024-12-31
   ```
   `as_of_date` o tarihe göre hesaplama yapar.

4. **Hata kontrolü:**  
   - `success: false` veya 400/500: F12 → Network’te ilgili isteğe tıklayıp **Response** içeriğine bakın.  
   - "Kurum bilgisi yok": Kullandığınız kullanıcının `kurum_id` atanmamış; kurum atanmış başka kullanıcı ile deneyin.

---

## Test 2: Vizyon puanı yeniden hesaplama (POST – recalc)

**Amaç:** Tüm hiyerarşide vizyon + PG `calculated_score` güncellemesinin tetiklenmesi.

1. F12 → **Console** sekmesini açın.

2. Şu kodu yapıştırıp Enter’a basın (portu kendi değerinize göre değiştirin):
   ```javascript
   fetch('http://127.0.0.1:5001/api/vision-score/recalc', {
     method: 'POST',
     credentials: 'include',
     headers: { 'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || '' }
   }).then(r => r.json()).then(console.log).catch(console.error);
   ```

3. **Beklenen:** Konsolda JSON; örn:
   ```json
   { "success": true, "vision_score": ..., "as_of_date": "...", "kurum_id": 1, "message": "Vizyon puanı tüm hiyerarşide yeniden hesaplandı." }
   ```

4. **Alternatif (curl / Postman):**  
   - URL: `POST http://127.0.0.1:5001/api/vision-score/recalc`  
   - Giriş yapmış oturumun cookie’leri gönderilmeli (tarayıcıdan kopyalayabilirsiniz).

---

## Test 3: PG verisi kaydedince tetikleyici (Skor Motoru)

**Amaç:** Süreç karnesinde PG verisi kaydettiğinizde vizyon puanının otomatik yeniden hesaplanması.

1. **Süreç Paneli** sayfasına gidin:  
   `http://127.0.0.1:5001/surec-paneli`

2. Bir sürece tıklayıp **Süreç Karnesi** (veya ilgili karne) sayfasına girin.  
   Veya doğrudan süreç karnesi URL’inizi kullanın (örn. `/surec/<surec_id>/karne`).

3. F12 → **Network** sekmesini açın; sayfada filtre olarak **XHR** veya **Fetch** seçin.

4. Karnede **PG verisi girin veya güncelleyin** (hedef/gerçekleşen alanları) ve **Kaydet** butonuna basın.

5. **Network**’te `karne/kaydet` veya benzeri bir **POST** isteği görünmeli; yanıt `success: true` olmalı.

6. Hemen ardından **GET /api/vision-score** çağrısı yapın (Test 1’deki gibi aynı URL’i yenileyin veya Console’da `fetch('/api/vision-score').then(r=>r.json()).then(console.log)`).  
   - Vizyon puanının veriye göre güncellenmiş olması beklenir (veri yeterliyse 0’dan farklı bir değer).

---

## Test 4: PG verisi güncelleme (PUT) tetikleyici

**Amaç:** Mevcut bir PG verisi güncellendiğinde Skor Motoru’nun tetiklenmesi.

1. Süreç karnesinde veya PG veri detay sayfasında **mevcut bir veriyi düzenleyin** (gerçekleşen değer vb.).

2. F12 → **Network**’te `pg-veri/guncelle` veya `guncelle` içeren bir **PUT** (veya POST) isteğini bulun.

3. İstek başarılı olduktan sonra tekrar **GET /api/vision-score** ile vizyon puanına bakın; değişikliğe göre güncel olmalı.

---

## Test 5: Faaliyet güncelleme + PG bağlantısı (isteğe bağlı)

**Amaç:** Faaliyet güncellendiğinde, bağlı PG üzerinden recalc tetiklenmesi.

1. Bir sürecin **faaliyet** listesine gidin (süreç detay / karne sayfasında faaliyetler bölümü).

2. Bir faaliyeti **düzenleyin** (ad, açıklama, tarih vb.).  
   Eğer arayüzde “Bağlı PG” (surec_pg_id) seçimi varsa, bir PG seçip kaydedin.

3. F12 → **Network**’te faaliyet **update** isteğini (POST) kontrol edin; yanıt 200 ve `success: true` olmalı.

4. Sonrasında **GET /api/vision-score** veya **POST /api/vision-score/recalc** ile vizyon puanının güncellenmiş olduğunu kontrol edin.

---

## Özet kontrol listesi

| # | Test | Nasıl | Beklenen |
|---|------|--------|----------|
| 1 | GET vizyon puanı | `/api/vision-score` açmak | JSON, `vision_score` 0–100 |
| 2 | POST recalc | Console’da `fetch(.../recalc)` | `success: true`, `message` |
| 3 | PG veri kaydet | Karne’de veri kaydetmek | Kayıt başarılı; sonra vision-score güncel |
| 4 | PG veri güncelle | Mevcut veriyi düzenleyip kaydetmek | Güncelleme başarılı; vision-score güncel |
| 5 | Faaliyet güncelle | Faaliyet düzenleyip kaydetmek | Güncelleme başarılı; recalc tetiklenir |

---

## Sık karşılaşılan durumlar

- **401 Unauthorized:** Oturum açılmamış; önce giriş yapın.
- **"Kurum bilgisi yok":** Kullanıcıya kurum atanmamış; farklı kullanıcı veya admin ile kurum atayın.
- **vision_score hep 0:** Kurumda PG verisi (hedef/gerçekleşen) yok veya Bireysel PG → Süreç PG bağlantısı yok; önce PG verisi girin ve gerekirse **POST /api/vision-score/recalc** çalıştırın.
- **CORS / credential hatası:** API’yi aynı origin’den (aynı site/port) çağırın; `credentials: 'include'` kullanın.

Bu yönergeyi takip ederek Skor Motoru ve vizyon puanı hesaplamasını tarayıcıdan uçtan uca doğrulayabilirsiniz.

---

## AI Coach (Gemini entegrasyonu)

Skor motoru verileri AI Coach ile analiz ettirilir; Gemini "En Düşük Efor / En Yüksek Etki" ile 3 aksiyon önerir.

### Ön koşul

- `.env` dosyasında `GEMINI_API_KEY` veya `GOOGLE_API_KEY` tanımlı olmalı.

### Test adımları

1. Giriş yapın (admin / kurum_yoneticisi / ust_yonetim).
2. Sol menüden **AI Coach** sekmesine gidin (`/ai-coach`).
3. **Stratejik Analiz Başlat** butonuna tıklayın.
4. **Beklenen:** İlerleme metni ("Gemini verileri analiz ediyor...") görünür; ardından analiz sonucu Markdown kartında gelir (başlıklar, listeler, 3 aksiyon önerisi).
5. API doğrudan test: `POST /api/ai-coach/analyze` (JSON body: `{}`) → yanıtta `success`, `analysis_markdown`, `vision_score`, `as_of_date` olmalı.

### Sık durumlar

- **"GEMINI_API_KEY veya GOOGLE_API_KEY tanımlı değil":** `.env` içine API anahtarını ekleyin.
- **403 / yetkisiz:** Sadece admin, kurum_yoneticisi, ust_yonetim AI Coach sayfasına erişebilir.
