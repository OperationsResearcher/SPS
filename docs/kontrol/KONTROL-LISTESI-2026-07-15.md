# Kontrol Listesi — 15/16 Temmuz 2026 oturumu

> **Nerede kontrol edilir:** https://test.kokpitim.com — Test ortamı bu oturumun tüm işleriyle güncel.
> **Yayın'a çıkılmadı.** Yayın hâlâ eski sürümde; müşteri verisine dokunulmadı.
> Sürüm: `5d1f14fe` · Test alembic: `c927a97a2fef` · 588 test geçti / 0 başarısız

---

## 1. 🏆 Hedef Manipülasyonu Radarı — asıl iş bu

**Ne yapar:** Rakipler "hedefe ulaştın mı?" sorar. Bu, **"hedefin kendisi dürüst mü?"** sorar — biri dönem sonuna yakın hedefi aşağı çekmişse yakalar.

**Nerede:** `https://test.kokpitim.com/yonetim-ozeti` — **ayrı bir "Radar" ekranı yok**, Yönetim Özeti'nin içinde çalışır.

**Nasıl kontrol edilir:**
1. Bir PG'ye (Performans Göstergesi) git, **hedefi düşür** (örn. 280 → 210), kaydet
2. `/yonetim-ozeti` ekranını aç
3. Şunu görmelisin: **"aşağı · -25.0% · <senin adın>"**

**Doğrulandı mı:** ✅ Yerelde uçtan uca (gerçek API'den 280→210 → radar yakaladı). Test'te servis çalışıyor (hata vermiyor, 0 değişim döndürüyor — Test'te henüz hedef değişikliği yok, **beklenen**).

**Not:** Radar yalnızca **bugünden sonraki** hedef değişikliklerini görür. Geçmiş değişiklikler kayıt altında değildi — sistem eskiden "ne'den ne'ye" bilgisini saklamıyordu. Bu oturumda saklamaya başladı.

---

## 2. Tahmin ekranı — kırıktı, düzeldi

**Sorun neydi:** Analiz > Tahmin ekranı **380 süreçten 366'sında "veri yok"** diyordu. Veri vardı; ekran yanlış yere bakıyordu.

**Nerede:** `https://test.kokpitim.com/analysis` (Analiz ekranı)

**Nasıl kontrol edilir:**
1. `/analysis` ekranını aç
2. Rastgele birkaç süreç seç, tahmin/forecast kısmına bak
3. Artık tahmin **gelmeli** ("veri yok" değil)
4. Güven etiketi (yüksek/orta/düşük) artık **gerçek ölçüme** dayanıyor — eskiden sabit yazıyordu

**Doğrulandı mı:** ✅ Yerelde. Virgüllü değerler (`12,5`) de artık tahmine dahil.

---

## 3. Modül Kullanım Özeti (yeni ekran)

**Ne yapar:** Hangi modül gerçekten kullanılıyor, kim kullanıyor — denetim kayıtlarından.

**Nerede:** `https://test.kokpitim.com/admin/araclar/loglar` (Yönetim Paneli > Araçlar > Loglar) — yalnız Admin

**Ne göreceksiniz — çarpıcı bulgu:**
> **27 kullanıcı giriş yapıyor, yalnız 7'si veri giriyor.** %74 sadece bakıyor.
> PG Veri Girişi: 270 işlem, ama sadece 3 kullanıcıdan.

**⚠️ Sınırı:** Bu ekran *"hangi ekran açılmıyor"* sorusunu **cevaplamaz**. Sistem yalnızca kayıt ekleme/değiştirme ve giriş işlemlerini izliyor; sayfa görüntüleme izlenmiyor. Ekranda bu not yazılı.

---

## 4. Dürüstlük düzeltmeleri

| Ne | Nerede kontrol edilir |
|---|---|
| **Benchmark kaynak uyarısı** | Karşılaştırma ekranlarında artık verinin nereden geldiği yazıyor — uydurma sayı sunulmuyor |
| **KVKK / yerel yapay zekâ** | Kurum kendi sunucusundaki modeli kullanabiliyor → veri yurt dışına çıkmıyor. **Zaten çalışıyordu, belgesizdi.** Belgelendi + testle korundu. |

**Neden önemli:** KVKK hiçbir ülkeye yeterlilik kararı vermemiş. Her yurt dışı yapay zekâ çağrısı yasal yük getiriyor. Yerel model bunu tamamen çözüyor — satışta güçlü koz.

---

## 5. Görünmez altyapı (ekranda görünmez ama kritik)

| İş | Ne değişti |
|---|---|
| **Sayısal ayna kolonları** | 366.716 satır — analizler artık metin ayrıştırmıyor, sayı okuyor (hızlı + doğru) |
| **Dönem tipi tekilleştirme** | `aylık`/`aylik`/`AYLIK` karmaşası bitti |
| **202 bozuk satır onarıldı** | Silinmiş kullanıcılara bağlı ölçümler — **ölçüm korundu**, yalnız "kim girdi" bilgisi düştü |
| **Redis + güvenli geri çekilme** | Redis yoksa sistem çökmüyor, belleğe düşüyor. Redis'e **bakıp** karar veriyor, adresin şekline değil. |

**Kontrol:** Bu maddeler için özel bir şey yapmanız gerekmez. Sistem eskisi gibi çalışıyorsa doğru.

---

## 6. Yayın → Yerel veri çekme (yeni yordam)

**Ne için:** Yayın'daki gerçek veriyle yerelde test + Yayın'ın yedeği.

**Nasıl kullanılır:** Bana **"yayındaki verileri yerele çek"** deyin — hangi oturum, hangi IDE fark etmez, kural dosyasına bağlandı (§8.6).

**Güvenlik:** Yayın'a **hiçbir şey yazmaz** (tek işlem: salt-okunur yedek alma). Yerelde silinecek veri varsa **kendiliğinden durur**.

**Bugünkü ilk kıyas — 169 tablo:**

| | Yayın | Yerel |
|---|---:|---:|
| PG verileri (`kpi_data`) | 366.716 | **366.716** ✅ |
| Süreçler | 380 | **380** ✅ |
| Bireysel PG verileri | 19.159 | **19.159** ✅ |

**Sonuç: veriniz zaten senkron.** Yayın'da olup yerelde olmayan 3 kurum var ama **içleri boş** (4 kullanıcı, 0 süreç, 0 PG). Çekilecek anlamlı veri yok.

⚠️ **Bu hafta veri gelince** komutu verin — o zaman çekmeye değer.

---

## 7. Test ortamı gerçek bir hata yakaladı

Migration **yerelde geçti, Test'te patladı**. Sebep ölçüldü:

| | `kpi_data.user_id` FK'si |
|---|---|
| Yerel | **var** |
| Test | **yok** |

Kod FK'nın adını sabit varsaymıştı. *"Yerelde geçti" ≠ "her yerde geçer"* — Test tam bunun için var, işini yaptı. Düzeltildi, yerelde `downgrade → upgrade` turuyla kanıtlandı, Test'te uygulandı.

---

## Sizin kararınızı bekleyenler

| # | Konu | Durum |
|---|---|---|
| 1 | **29 kırık route + mock temizliği** (TASK-258) | Harita hazır (29/29 blok, 762 satır). `/risks`, `/crisis`, `/executive-report` **bugün tıklanınca 500 veriyor** — Yardım Merkezi'nden birine link var. Acil değil (kimse o ekranlarda değil), ama "yokluk" değil "kırıklık". |
| 2 | **Fiyat modeli** | Ertelendi. Kanıt hazır: %74 sadece bakıyor → per-seat bu kitleyi öldürür. |
| 3 | **MCP server** | Ertelendi. Yeni bileşen + yeni dış veri kapısı → mimari karar. |
| 4 | **Yayın deploy** | Yapılmadı. L paketleri kuralı: tüm L paketleri bitmeden Yayın'a çıkış yok. |

---

## Bugün yapılmayanlar — açıkça

- ❌ **Yayın'a deploy edilmedi** — Yayın eski sürümde, müşteri verisine dokunulmadı
- ❌ **Yayın'dan veri çekilmedi** — yordam hazır, çalıştırılmadı
- ❌ **Demo'ya gönderilmedi**
- ⚠️ **GitHub Actions CI hâlâ çalışmıyor** (hesap kilidi, Haziran'dan beri). Orada yeşil tik görürseniz **koşmadığı** anlamına gelir. Geçerli doğrulama: yereldeki 588 test.
