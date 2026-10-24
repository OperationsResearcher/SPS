# KMF (Kayseri Model Fabrika) — Yayın verisi: yedek, envanter, prova ve canlı sonrası kontrol

> Hazırlayan: Claude, 2026-10-24. **Kural:** Yayın'a yalnız salt okunur erişim yapıldı (`pg_dump` + salt okunur dosya tar'ı); Yayın'a hiçbir yazma yok.
> Kurum: `tenants.id = 16`, kısa ad **KMF**. Bu belge deploy etmez; deploy yalnız kullanıcı "test'e gönderelim / yayına çıkalım" dediğinde.

## 1. Yerel yedek (ne, nerede)
| Ne | Yol | Not |
|---|---|---|
| **Yayın tam DB dökümü** | `backups/yayin/yayin_2026-10-24_1028.dump` (9,1 MB, sha256 `5d0625db…b490c9`) | 2026-10-24 10:28 (İstanbul) anı. 170 tablo, 518.960 satır. `pg_restore -l` ile içerik doğrulandı. **Bu dosya Yayın'ın gerçek yedeğidir: silme.** |
| Yayın kullanıcı dosyaları | `backups/yayin/yayin_instance_2026-10-24_1028.tar.gz` (66 KB) | `uploads/tenant_logos/16.png` (**KMF logosu**) ve `7.webp`. Bunlar `pg_dump`'a girmez. |
| Referans kopya (dokunulmaz) | yerel DB **`kokpitim_yayin_oncesi`** | dökümün birebir restore'u; canlı sonrası kıyasın "ÖNCE" tarafı. **Değiştirme/silme.** |

⚠ **Yerel kopya tek başına yedek değildir:** dump + tar + `.sha256` dosyalarını ayrı bir diske (harici disk / bulut) de kopyala. `backups/` git'e girmez.
Yayın sunucusunda kod `4cb738bb` (2026-09-08), alembic `bi01c4e5f6a7`, PostgreSQL 14.24 (aarch64), veritabanı 328 MB. KMF'ye ait son ölçüm girişi 2026-10-02, son denetim kaydı 2026-10-23 (kullanıcılar aktif).

## 2. KMF'de hangi verimiz var (otomatik envanter)
Tablo listesi elle tutulmaz: `scripts/ops/kurum_veri_kiyas.py envanter <db> --kurum KMF` kurumun satırlarını `tenants` + `tenant_id` + **FK zinciri** (`kpi_data` gibi `tenant_id`'siz tablolar dahil) ile bulur; FK'siz `*_id` bağlantılarını emniyet ağı olarak ekler. Sonuç: **29 tabloda 22.219 satır**.

| Varlık | Satır | | Varlık | Satır |
|---|---:|---|---|---:|
| Kullanıcı (2 kurum yöneticisi + 6 üst yönetici aktif, 2 üst yönetici pasif) | 10 | | Ölçüm `kpi_data` (2020: 21, 2021: 114, 2022: 104, 2023: 106, 2024: 151, 2025: 170, 2026: 79) | 1.000 |
| Plan yılı (2020–2022 taslak, 2023–2025 kapalı, 2026 aktif) | 7 | | Ölçüm denetim kaydı `kpi_data_audits` | 884 |
| Strateji / alt strateji | 6 / 21 | | Bireysel ölçüm / bireysel PG / bireysel faaliyet | 830 / 207 / 2 |
| Süreç (SR1–SR11) | 11 | | Mühür denetim kaydı `plan_year_seal_audits` | 40 |
| Süreç PG'si (162 aktif; 146 yılsız + 41 yıl etiketli kopya) | 187 | | K-Vektör ayar snapshot | 9 |
| Süreç–alt strateji bağı | 41 | | SWOT / TOWS / BSC perspektif | 1 / 1 / 1 |
| Süreç lideri / üyesi | 11 / 25 | | Faaliyet / hatırlatma / atanan | 5 / 12 / 4 |
| Bildirim (7.760'ı FK'siz, `user_id` ile eklendi) | 16.275 | | Denetim logu / LLM kullanım logu | 1.884 / 717 |

Süreçler (aktif PG sayısı, yıl kopyaları dahil): SR1 5, SR2 10, SR3 11, SR4 20, SR5 **36**, SR6 30, SR7 6, SR8 12, SR9 9, SR10 8, SR11 15.
Tam tablo listesi: `python scripts/ops/kurum_veri_kiyas.py envanter kokpitim_yayin_oncesi --kurum KMF`.

## 3. Prova: Yayın kopyası üzerinde, deploy'un yapacağı her şey
Yöntem: Yayın dökümü **iki ayrı yerel DB'ye** yüklendi; biri referans (`..._oncesi`), diğerinde (`kokpitim_yayin_prova`) deploy'un adımları sırayla uygulandı: ① `scripts/run_db_upgrade.py` (deploy'un kullandığı komut) ② `yilbazli_faz1_2 --tenant 16` ③ `yilbazli_faz1_5` ④ `yilbazli_faz1_4 --tenant 16` (6 Ekim TASK-311'deki yerel sıra). Hiçbir e-posta/zamanlayıcı çalıştırılmadı.

| Kontrol | Sonuç |
|---|---|
| Migration'lar (`gs01 → ux01 → mg01`) | ✅ hatasız (Yayın `bi01`'de; bekleyen **3** migration, önceki raporun "15"i yanlıştı) |
| Tüm 170 tablonun satır sayısı önce/sonra (yalnız migration) | ✅ **birebir aynı** (518.960) |
| **13 kurumun hepsi, satır/PK kıyası** (migration sonrası) | ✅ **kayıp 0** |
| KMF, değer düzeyinde kıyas (migration + veri geçişi sonrası) | ✅ **KAYIP YOK**: 22.219 → 23.605 satır (fark = klonlanan 66 süreç, 36 strateji, 126 alt strateji, 786 PG, 103 bireysel PG vb.) |
| Veri geçişi sonrası KMF yapısı ↔ yerel `kokpitim_db` | ✅ 77 süreç, 42 strateji, 147 alt strateji, 973 PG, 310 bireysel PG, 287 bağ **aynı** (provada yerelin durumu yeniden üretildi) |
| `yilbazli_dogrulama.py` | 10/19, **yerelle aynı** (bilinen artıklar: 204 aktif PG ölçümü başka kurumlarda, 10 kapalı bayrak) |
| Aracın kendi doğruluğu (negatif kontrol) | ✅ bilerek silinen satır, değişen değer ve ad yakalandı, çıkış kodu 2 |

Beklenen (açıklanabilir) değişimler: `kpi_data.process_kpi_id` 785 ölçüm yılın PG kopyasına yeniden bağlandı (Faz 1.5), `process_kpis.is_included` 15 PG "bu yıl karneye dahil değil" işareti kopyalara taşındı (Faz 1.4), plan yılı bağlantıları (Faz 1.2), `users.session_version` yeni kolon.

## 4. 🔴 Bulgular (canlıya çıkıştan ÖNCE bilinmeli)
1. **Veri geçişi şart.** Yayın'da tek yapı farkı KMF'dir (11 süreç/187 PG yılsız; yerelde 77/973). Tomofil, EMS, Default ve diğer tüm kurumlar Yayın ile yerelde **birebir aynı**. Kod + migration deploy edilip KMF veri geçişi (Faz 1.2/1.5/1.4) yapılmazsa yeni kod yıl bazlı yapı bulamaz: Yayın'da 2026 plan yılına bağlı PG yalnızca 2'dir (yerelde 128), karne özetleri bozuk çıkar (ör. SR5 "7 PG'den 7'ine veri girilmemiş"). Geçiş, migration gibi otomatik gelmez (REHBER §0 madde 7, 4. katman) ve Yayın'da **henüz uygulanmadı** (TASK-311: "Yayın'da uygulanması AÇIK").
2. **31 PG kopyası "karışık yapıda" (28 ölçüm görünmez kalır).** Yayın'da SR5 (23), SR8 (7), SR11 (1) süreçlerinde, süreç yılsızken PG'lerin bir kısmı **zaten yıl etiketli kopyalardı** (2021–2026). Faz 1.2 bu süreçleri yılsız sayıp 2020'ye bağlıyor ve 2021–2026 için **yeniden, boş** kopyalar üretiyor; gerçek yıl ölçümleri ise 2020 sürecine bağlı eski kopyalarda kalıyor. Sonuç: 31 PG kopyasının 24'ünün toplam **28 ölçümü** (ör. SR5 Eğitim 2021) yıl bazlı karnelerde **görünmüyor** (kayıp değil, görünmezlik; satırlar duruyor). Yerelde de aynı durum var (provada yerelle aynı sonuç çıktı). Düzeltme bir veri tasarımı kararı: yıl kopyasını doğru yıl sürecine taşıma + alt strateji eşleme + boş kopyayı emekli etme. **Karar bekliyor** (öneri: kontrol/uygulama betiği yazıp provada doğrula).
3. **Karne rakamları ve görünüm değişir** (hepsi açıklanabilir; 870 PG-yıl kaydında ölçüldü):
   - `achievement` (başarı yüzdesi) 343 PG-yılda **boştu, doldu**; başarı ölçeği (1–5) etiketi 337'de eklendi.
   - **PG 402 Elektrik (Toplama):** eski kod `2175,807` gibi virgüllü ondalıkları sayamıyordu (2021 toplamı 3054 gösteriyordu); doğrusu **6773,44**.
   - **PG 361 Ödüle Başvuran (Son Değer, 2025):** iki kayıt var (değer 2, 06.04'te; değer 8, 01.10'da); eski kod eskiyi (2), yeni kod **en son girileni (8)** gösterir. PG 327'de aynı gün girilmiş çok sayıda test değeri var, en sonuncu (777) seçilir.
   - Değer yazımı: `11 → 11.0`, `%100 → 100.0` (% işareti kalkar), `94,25 → 94.25`, `-` olarak girilmiş boş alanlar artık gösterilmez. (Veri değişmez, yalnız görünüm.)
   - **2026 süreç özeti** (şimdi Yayın → geçiş + yeni kod):

| Süreç | Sağlık skoru | Hedef ulaşma | PG sayısı | Veri girilmemiş PG |
|---|---|---|---|---|
| SR1 | %0 (Riski) → %0 (Veri yok) | %0 → - | 5 → 5 | 3 → 5 |
| SR2 | %51 (Orta) → %60 (Orta) | %72 → %86 | 10 → 10 | 4 → 5 |
| SR3 | %0 (Veri yok) → %0 (Veri yok) | - | 11 → 11 | 11 → 11 |
| SR4 | %0 (Riski) → %0 (Veri yok) | %0 → - | 20 → 20 | 17 → 20 |
| SR5 | %0 (Riski) → %0 (Veri yok) | %0 → - | 36 → 13 | 33 → 13 |
| SR6 | %0 (Riski) → %0 (Veri yok) | %0 → - | 30 → 30 | 17 → 30 |
| SR7 | %69 (Orta) → %68 (Orta) | %98 → %98 | 6 → 6 | 3 → 3 |
| SR8 | %50 (Riski) → %66 (Orta) | %71 → %94 | 12 → 5 | 7 → 1 |
| SR9 | %0 (Veri yok) → %0 (Veri yok) | - | 9 → 9 | 9 → 9 |
| SR10 | %30 (Riski) → %70 (Orta) | %43 → %100 | 8 → 8 | 1 → 5 |
| SR11 | %0 (Riski) → %0 (Veri yok) | %0 → - | 15 → 14 | 4 → 14 |

   "PG sayısı" düşüşü (SR5 36 → 13) kayıp değil: eski görünüm bütün yılların PG kopyalarını karıştırıp sayıyordu, yeni görünüm yalnız seçili yılın PG'lerini gösterir. 2026'da ölçümü olmayan PG'ler "Riski" yerine "Veri yok" olur. SR10 (%30 → %70) ve SR8 (%50 → %66) gibi sıçramalar **KMF sorumlusuyla Test'te doğrulanmalı**.
   - KMF'de yılın kopyasına bağlanamayan ölçüm yalnız **139** (hepsi pasif PG, bilinen K14 istisnası, görünmez).

## 5. Canlıya çıkış sonrası "eksik var mı" kontrolü (tekrarlanabilir)
Canlıda kullanıcılar çalışmaya devam eder: **deploy'dan hemen önce referansı yenile**, deploy + veri geçişi sonrası tekrar çek ve kıyasla.
```powershell
cd C:\kokpitim
# 1) Deploy'dan hemen ÖNCE (baseline'ı güncelle; eskisi kalsın, yeni ad ver)
python scripts/ops/yayin_kopya_al.py --db kokpitim_yayin_oncesi_YYYYAAGG
# 2) ... deploy + KMF veri geçişi ...
# 3) Deploy'dan SONRA
python scripts/ops/yayin_kopya_al.py --db kokpitim_yayin_sonrasi
# 4) KMF satır satır kıyas (çıkış kodu 0 = kayıp yok, 2 = KAYIP)
python scripts/ops/kurum_veri_kiyas.py kiyas kokpitim_yayin_oncesi_YYYYAAGG kokpitim_yayin_sonrasi --kurum KMF --out docs/kontrol/kmf_kiyas_YYYYAAGG.md
# 5) Tüm kurumlar, hızlı mod (PK kümesi + sayı): her kurum için --tenant-id ile tekrarla
python scripts/ops/kurum_veri_kiyas.py kiyas kokpitim_yayin_oncesi_YYYYAAGG kokpitim_yayin_sonrasi --tenant-id 27 --hizli
```
Yorum: **🔴 Kayıp = 0 olmalı.** 🟡 "Eklenen" = deploy arasında girilen canlı veri + klonlar (normal). 🟢 "Beklenen" = migration/veri geçişi. 🟠 "Beklenmeyen değişmiş" = incelenir (yeni bir migration kasıtlıysa `BEKLENEN_KOLON_DEGISIMI` listesine gerekçesiyle eklenir). KMF logosu (`uploads/tenant_logos/16.png`) docker volume'unda kalır; deploy sonrası `/tenant-logo/16` 200 vermeli.

## 6. Açık kararlar
1. Karışık yapılı 31 PG kopyası / 28 ölçüm: düzeltme betiği yazılıp provada doğrulansın mı? (öneri: evet, KMF veri geçişinden ÖNCE)
2. KMF veri geçişi (Faz 1.2/1.5/1.4) Yayın'da hangi aşamada ve kim tetikleyecek (Test'te önce prova: Test sıfırdan kurulur, KMF verisi Yayın dökümünden gelir)?
3. Karne farklarının (özellikle SR10/SR8/SR2) KMF sorumlusuyla Test'te doğrulanması.
