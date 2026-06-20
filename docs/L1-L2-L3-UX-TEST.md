# L1 / L2 / L3 — UX Test Yönergesi

> Bu oturumda yapılan tüm değişiklikleri tarayıcıdan elle test etmek için.
> Tüm değişiklikler **yalnızca Yerel** (127.0.0.1:5001). Yayın'a çıkmadı.

## 0. Başlat
```
cd c:\kokpitim
python pybasla.py
```
"Running on http://127.0.0.1:5001" görünce tarayıcıda aç: **http://127.0.0.1:5001**

**Giriş:** Tomofil yöneticisi (executive_manager) ile gir — L1/L3 ekranları yönetici-only.
Örnek hesap: `deniz.tunc@kokpitim.com` (şifre sende). KOE/AI/ESG/analizler standart kullanıcıda görünmez.

---

## L1 — Başlangıç paketi (kimlik + KOE + AI danışman)

| # | Ekran | URL | Ne test et |
|---|-------|-----|-----------|
| 1 | Masaüstü | `/masaustu` | **KOE kartı** (Kurumsal Olgunluk Endeksi) görünüyor mu? 4 boyut + skor. Altında **"✨ AI ile zenginleştir"** butonu — tıkla (AI sağlayıcı yoksa "yapılandırılmamış" mesajı verir, bu normal). |
| 2 | Kurum Paneli | `/kurum` | Kimlik akordeonunu aç: **Değerler / Etik / Kalite** artık **madde madde** (eski tek paragraf değil). "Madde ekle" ile ekle, kalem/çöp ile düzenle-sil. |
| 3 | Bireysel Karne | `/bireysel/karne` | "Yeni PG" ekle → formda **Katman** seçimi (Standart/Stratejik). Stratejik seçince **strateji bağı** dropdown'ı çıkar. Listede stratejik olanlarda **mor "Stratejik" rozeti**. |
| 4 | Rol etiketi | her sayfa sol-alt / profil | Rolün **"Üst Yönetim"** yazıyor (eski "Kurum Üst Yönetimi" değil). `/profil`'de de tutarlı. |

**Asimetri kontrolü (opsiyonel):** standart kullanıcıyla gir → Masaüstü'nde KOE kartı **görünmemeli**.

---

## L2 — Paket sistemi (gating)

| # | Ekran | URL | Ne test et |
|---|-------|-----|-----------|
| 5 | Kurum ekle (paket seçimi) | `/admin/tenants` | "Kurum Ekle" → formda **Abonelik Paketi** dropdown'ında 4 paket: **Başlangıç / Yönetim / Strateji / Master Package**. (Gerçek kurum oluşturmana gerek yok, dropdown'ı görmen yeter.) |
| 6 | Mevcut paketler | `/admin/tenants` | Tablo "Paket" kolonunda tenant'lar **Master Package** (hepsi full erişimli). |

**Not:** Gating çalışıyor ama tüm tenant'lar Master (full) olduğu için yüzeyde modül kaybı görmezsin — bu kasıtlı. Gerçek tier farkını görmek istersen bir test kurumunu "Başlangıç" paketine alıp o kurumun kullanıcısıyla girersen sidebar'da süreç/PGV modüllerinin **kapandığını** görürsün.

---

## L3 — Strateji paketi (ileri analizler)

| # | Ekran | URL | Ne test et |
|---|-------|-----|-----------|
| 7 | SP Menü | `/sp/menu` | Yeni kartlar: **SWOT, TOWS, PESTEL, Porter 5 Güç, Dengeli Karne (BSC)**. |
| 8 | SWOT | `/sp/swot` | 4 kutu (Güçlü/Zayıf/Fırsat/Tehdit). "Madde ekle" → **Kaydet**. Sayfayı yenile → veri kalıcı mı? |
| 9 | TOWS | `/sp/tows` | 4 strateji kombinasyonu (SO/ST/WO/WT). Aynı ekle-kaydet akışı. |
| 10 | PESTEL | `/sp/pestel` | 6 kategori (Politik…Yasal). Ekle-kaydet. |
| 11 | Porter | `/sp/porter` | 5 güç. Her güçte **1–5 baskı skoru** (butonlar) + madde + Kaydet. |
| 12 | BSC | `/sp/bsc` | 4 perspektif kartı (Finansal/Müşteri/İç Süreç/Öğrenme) + KPI'lar. Atanmamış KPI'da dropdown'dan perspektif seç → karta taşınır. "Otomatik sınıflandır" dene. |
| 13 | ESG | `/raporlar/esg-yonetim` | "Metrik ekle" (E/S/G, birim, hedef) → metriğe "Değer gir" (yıl + değer). Sonra `/raporlar/esg-rapor`'dan "Metrikleri Yönet" linki de buraya getirir. |
| 14 | Değer Zinciri | `/k-radar/kp/deger-zinciri` | Özet + altta **Değer Zinciri Faaliyetleri** (Birincil/Destek). "Faaliyet ekle" → muda türü + süreç bağı. |
| 15 | Kapasite | Proje aç → **Kapasite** sekmesi | Bir projeye gir (`/project/...`), üst navda **Kapasite** sekmesi. "Kapasite ekle" → kişi + haftalık saat + tarih. (Projede ekip üyesi olmalı.) |
| 16 | Program Gantt | `/project/portfolio` | Üstte **Program Zaman Çizelgesi** — projeler tek Gantt'ta, bar renkleri skora göre (yeşil/sarı/gri). Bar üstüne gel → tarih popup. **(Bu görseli ben test edemedim, asıl bunu doğrula.)** |

---

## Hızlı kontrol listesi (her ekranda)
- [ ] Sayfa **açılıyor mu** (boş/500 değil)?
- [ ] **Ekle → Kaydet → yenile** sonrası veri **kalıcı mı**?
- [ ] **Sil** çalışıyor mu?
- [ ] Türkçe karakterler düzgün mü (ş/ç/ğ/ı bozuk değil)?

## Sorun çıkarsa
Ekran adı + ne yaptığın + hata/ekran görüntüsünü paylaş — runtime'da birlikte teşhis ederiz.
En kritik teyit: **#16 Program Gantt görseli** ve **#1 KOE AI butonu**.
