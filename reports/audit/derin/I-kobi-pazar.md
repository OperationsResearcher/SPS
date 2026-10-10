# I — KOBİ Pazar Büyüklüğü, Talep Sinyalleri ve Kanallar (Bölüm 2)
Tarih: 2026-10-10. Erişim tarihi tüm kaynaklar: 2026-10-10. Önceki rapor: `reports/audit/07-pazar-musteri.md` (tekrarlanmadı; onun "BULUNAMADI" listesi burada kapatıldı veya yeniden işaretlendi).
Kural: sayı yalnız kaynaklıysa verilir. Varsayımlar ayrı tabloda, "VARSAYIM" etiketli. Kaynakların çoğu ikincil (haber/köşe yazısı/arama özeti); birincil teyit gereken satırlar "TEYİT" ile işaretli.

## 1. Kaynaklı sayılar

| # | Veri | Değer | Kaynak no | Güven |
|---|---|---|---|---|
| a | Aktif girişim, 2024 (TÜİK, geçici) | 3.942.781 | K1 | ikincil |
| b | KOBİ sınıfı girişim, 2024 | ~3.928.000 (%99,6) | K1 | ikincil |
| c | Mikro (1-9) girişim | 3.706.765 (%94) | K2 | ikincil |
| d | Küçük (10-49) KOBİ | 196.312 | K2 | tek köşe yazısı, TÜİK bülteninden TEYİT edilmedi |
| e | Orta (50-249) KOBİ | 33.465 | K2 | aynı; hedef bant bu |
| f | İstihdam payı: 10-49 / 50-249 | %19,3 / %16,9 | K2 | ikincil |
| g | Ciro payı: 10-49 / 50-249 | %19,9 / %20,3 | K2 | ikincil |
| h | KOBİ'ler içinde sektör payı: ticaret / ulaştırma-depolama / imalat | %35,1 / %15,3 / %12,1 | K1 | ikincil |
| i | KOBİ imalatı: KOBİ istihdamının %25,4'ü, katma değerin %34,9'u | — | K1 | ikincil |
| j | KOBİ tanımı | 250 çalışandan az; net satış/bilanço eşiği kaynaklar arasında tutarsız (500 milyon TL vs 10-49 için 100 milyon, 50-249 için 1 milyar TL) | K1, K2 | TEYİT |
| k | Türkiye ISO 9001 geçerli belge | 18.527 (%1,56 artış; "dünya ilk 10"; IAF CertSearch verisi) | K3 | TÜRKAK X paylaşımı, yalnızca arama özeti; yıl belirtilmemiş; sayfa 402 verdi, doğrulanamadı. TEYİT |
| l | Dünya belge sayısı (ISO Survey 2024): ISO 9001 / 14001 / 45001 | 1.474.118 / 676.232 / 542.527 | K4 | ikincil (infografik) |
| m | ISO Survey 2023 ISO 9001 ilk 10 | Türkiye ilk 10'da DEĞİL (10. Fransa 19.987); Çin verisi eksik, sıralama güvenilmez | K5 | ikincil |
| n | Ücretli bulut kullanan girişim (10+ çalışan), 2025 | %20,4 (2023: %16,4); 10-49: %17,3; 50-249: %31,8; 250+: %54,3 | K6 | ikincil (TÜİK 2025 BT kullanım araştırması aktarımı) |
| o | ERP kullanımı (yıl metinde açık değil, 2025 olması muhtemel) | 10-49: %23,6; 50-249: %46,0; 250+: %76,5 | K6 | ikincil |
| p | OSB sayısı | 416 (371 Sanayi Bakanlığı, 45 Tarım Bakanlığı), 2025 sonu | K7 | haber (OSBÜK başkanı beyanı) |
| q | OSB fabrika / istihdam | 68 binden fazla fabrika (Bakan beyanı: ~60 bin üretimde tesis); 2,7 milyondan fazla istihdam; sanayi üretiminin %45'i | K7 | tanım farkı var |
| r | İSO 500 (2025 sonuçları, Haz 2026) istihdam | 803.677 kişi; İkinci 500: 284.876 kişi | K8 | ikincil (Sözcü, İSO verisi) |
| s | İSO 500 üretimden satış toplamı | 11,1 trilyon TL; İkinci 500: 1,750 trilyon TL | K8 | ikincil |
| t | Özel okul (MEB 2024-25) | 14.700 okul; 177.738 öğretmen; 1.539.579 öğrenci | K9 | MEB haberi |
| u | Hastane (2024) | 1.562 toplam; özel hastane ~552 (tek kaynak, TEYİT) | K10 | zayıf |
| v | Yükseköğretim | 208 kurum, 75 vakıf (07 raporundan) | 07 | ikincil |
| w | IDC: Türkiye ICT harcaması 2025 | ~30 milyar USD (+%24 yerel para); yazılım 2025'te ~+%19, 2025-28 YBBO %13 | K11 | IDC basın bülteni özeti |
| x | TÜBİSAD: yazılım sektörü | 761 milyar TL (+%124); önceki yıl pazar 8,7 milyar USD; ihracat 178 milyar TL | K12 | kapsam IDC'den farklı, karşılaştırılamaz |
| y | TÜRKAK toplam akredite kuruluş | 990 (tüm tür; tarihsiz TBMM konuşması) | K13 | zayıf, tarihsiz |

## 2. KOSGEB: fiyat engelini aşma kanalı mı? Hayır (doğrudan değil)
Kaynak: KOSGEB KOBİ Dijital Dönüşüm Destek Programı Yönergesi (Rev.04, 11.05.2026) PDF'i yerelde okundu + resmi program sayfası (K14, K15).
- Mekanizma **kredi faiz desteği**dir (hibe değil): banka (TEB, İş Bankası, Yapı Kredi) kredisinin faizine geri ödemesiz puan desteği. Kredi alt limiti 1.000.000 TL, üst 20.000.000 TL, vade en çok 36 ay, program süresi 24 ay.
- **Yalnız NACE Rev.2 Kısım C (imalat)**; yalnız küçük ve orta ölçek (mikro hariç). Hizmet/sağlık/eğitim kurumları dışarıda.
- Desteklenen gider "yeni makine, teçhizat, yazılım, donanım"; satın alınan varlık işletmeye ait olmalı ve kredi vadesi bitiminden 1 yıl satılamaz/kiralanamaz. Yönerge, dijital dönüşümü IoT, bulut, ERP, süreç otomasyonu vb. olarak tanımlıyor ama **SaaS aboneliği/lisans kiralama açıkça kapsamda değil**; abonelik (OPEX) bir "yatırım kredisi" gider kalemi olarak uyumsuz görünüyor. Bu yorumdur; KOSGEB'den yazılı teyit şart.
- Başvuru ön koşulu: yetkili danışmandan **onaylı dijital dönüşüm/olgunluk raporu** (resmi sayfa: TÜSSİDE, MEXT, İHKİB); son mali yılda pozitif özkaynak, son 3 yılın en az birinde pozitif faaliyet kârı.
- Dolaylı fırsat: onaylı olgunluk danışmanları ve program başvuran imalat KOBİ'leri **kanal/ortak** olabilir; ürün lisanslı/kurulumlu paket olarak sunulursa "yazılım gideri" kapsamı denenebilir (TEYİT; fiyat modelini bozabilir).
- Faiz puanı değeri okunamadı: **BULUNAMADI**. Bloglardaki %60/%80/2 milyon TL rakamları resmi metinle çelişiyor; kullanılmadı.
- SEGEM "%100 hibe, yıllık 5 milyon TL" bilgisi yalnız blogda (K16); danışmanlık programı, yazılım abonelik desteği değil; TEYİT.

## 3. Talep sinyalleri
- Ücretli bulut kullanımı 50-249 bandında %31,8, genelde artışta (2023 %16,4 → 2025 %20,4) (K6). ERP %46 (orta bant): ERP'si olan orta ölçek, kalite/strateji katmanına geçmeye hazır tabanı gösterir.
- ISO 9001: 18.527 belge (K3). Kalite müdürü rolü ve yıllık gözetim/yeniden belgelendirme iç tetikleyicisi için üst sınır.
- KalDer Türkiye Mükemmellik Ödülleri 2025'te 33. kez verildi; EFQM kriterleri jüri ölçütü (K17). **Güncel üye sayısı BULUNAMADI** (yalnız eski Hürriyet haberi: 1.886 üye, 949 destekleyici şirket; tarihi eski, güncel sayılmaz; K18). Ödül başvuru sayısı BULUNAMADI.
- Google Trends / arama hacmi: bu ortamda erişilemedi. **BULUNAMADI.** Manuel: trends.google.com ve Google Ads Keyword Planner ("ISO 9001", "kurumsal performans yönetimi", "KPI takip programı", "EFQM", "stratejik plan yazılımı", TR, 5 yıl).
- LinkedIn "kalite müdürü / strateji müdürü" rol sayısı: **BULUNAMADI** (giriş gerekir). Sales Navigator: Türkiye + unvan + 51-1000 çalışan filtresi.

## 4. TAM / SAM / SOM

### 4.1 Varsayım tablosu (tümü VARSAYIM; kaynaklı olmayan her girdi burada)
| Kod | Varsayım | Düşük | Orta | Yüksek | Dayanak |
|---|---|---|---|---|---|
| V1 | Yıllık ortalama gelir/kurum (ARPA), TL | 60.000 | 120.000 | 200.000 | Fiyat belirlenmedi; ölçülmedi |
| V2 | SAM'a giren pay: kalite/strateji/EFQM odağı olan, dijital olgun orta KOBİ | %15 | %25 | %40 | Hiçbir kaynakta ölçülmedi; saf varsayım |
| V3 | 3 yıllık SOM penetrasyonu (SAM içinde) | %0,5 | %1,5 | %3 | Yerli SaaS, danışman kanalı; müşteri doğrulaması yok |
| V4 | Kapsam | yalnız 50-249 bandı | aynı | aynı | Hedef segment tanımı |

### 4.2 Hesap (kaynaklı girdiler: e = 33.465 [K2]; ücretli bulut oranı %31,8 [K6])
| | Düşük | Orta | Yüksek |
|---|---|---|---|
| **TAM** (kurum) = e | 33.465 | 33.465 | 33.465 |
| TAM (TL/yıl) = e × V1 | 2,01 milyar | 4,02 milyar | 6,69 milyar |
| SAM ön filtre = e × %31,8 (ücretli bulut kullanan orta KOBİ) | 10.642 | 10.642 | 10.642 |
| **SAM** (kurum) = ön filtre × V2 | 1.596 | 2.660 | 4.257 |
| SAM (TL/yıl) = SAM × V1 | 95,8 milyon | 319,2 milyon | 851,4 milyon |
| **SOM** (kurum, 3. yıl) = SAM × V3 | 8 | 40 | 128 |
| SOM ARR (TL/yıl) = SOM × V1 | 0,48 milyon | 4,8 milyon | 25,6 milyon |

Notlar:
- Makullük kontrolü: ISO 9001 belge sayısı 18.527 (K3) tüm ölçekleri kapsar; orta bandın payı bilinmiyor. Orta senaryo SAM (2.660) bunun ~%14'üdür: büyüklük mertebesi olarak makul, kanıt değil.
- 10-49 bandı (196.312, K2) bilerek dışarıda: ücretli bulut %17,3, ERP %23,6 (K6); düşük olgunluk ve fiyat duyarlılığı. Ayrı üst senaryo olarak değerlendirilebilir.
- TÜBİSAD/IDC rakamları (K11, K12) TL TAM'ı doğrulamakta kullanılamaz: kapsam farklı, KOBİ kırılımı yok.
- Kamu/belediye/üniversite TAM'ı bu bölümde yok (Bölüm 1 / 07 raporu).

## 5. Segment profilleri (aciliyet/bütçe hücreleri YORUMDUR; ölçüm değil)

| Segment | Problem | Karar verici | Satın alma tetikleyicisi | Bütçe sinyali | Kanallar |
|---|---|---|---|---|---|
| ISO 9001'li imalatçı (50-249) | Hedef/KPI/süreç performansı Excel'de; yönetimin gözden geçirme girdisi dağınık | Kalite müdürü (öneren), GM (onaylayan) | Belge denetimi/yenileme (hedef-ölçüm kanıtı), müşteri denetimi | ERP %46 + ücretli bulut %31,8 (K6) yazılım harcama alışkanlığına işaret; yazılım bütçe payı BULUNAMADI | Belgelendirme kuruluşları, ISO danışmanları, OSB yönetimleri, sanayi odası, KOSGEB onaylı olgunluk danışmanları |
| İhracatçı KOBİ | Müşteri/tedarikçi denetimi, sürdürülebilirlik talepleri, süreç görünürlüğü | GM + kalite/ihracat müdürü | Alıcı denetimi, uyum talepleri | Ödeme gücü ölçülmedi | İhracatçı birlikleri, sanayi/ticaret odası |
| Aile şirketi kurumsallaşma | Sahip bağımlılığı, hedef netliği, profesyonel yönetici geçişi | Sahip/GM, genelde danışman yönlendirmesiyle | Nesil geçişi, banka/yatırımcı gereği, büyüme tıkanması | BULUNAMADI | Kurumsallaşma danışmanları, KalDer etkinlikleri, odalar, bankaların KOBİ birimleri |
| Özel klinik / özel hastane | Kalite göstergeleri, akreditasyon, süreç performansı | Kalite direktörü / hastane müdürü | Akreditasyon denetimi, grup içi raporlama | Özel hastane ~552, toplam 1.562 (K10, zayıf); poliklinik/tıp merkezi sayısı BULUNAMADI; HBYS entegrasyonu engel (07 raporu) | Sağlık kalite dernekleri, özel hastane birlikleri (üye sayısı BULUNAMADI) |
| Özel okul / vakıf üniversitesi | Stratejik plan, kalite güvencesi, performans karnesi | Genel müdür/kurucu temsilcisi, kalite birimi, strateji daire bşk. | Akreditasyon/kalite dönemi, grup okulu standardizasyonu | 14.700 özel okul (K9; uygun alt küme BULUNAMADI); 75 vakıf üniversitesi (07) | Eğitim kurumları birlikleri (üye sayısı BULUNAMADI), KalDer, YÖK kalite ağları |
| EFQM yolundaki kurum | Öz değerlendirme, ödül başvuru raporu, iyileştirme alanı takibi | Kalite müdürü, GM | KalDer ödül dönemi (yıllık) | Danışman bütçesi (kaynak yok) | KalDer, EFQM danışmanları |

## 6. Hedef listeyi nasıl üretirsin (somut firma adı verilmedi)
1. **ISO belge sorgulama:** IAF CertSearch (iafcertsearch.org): ülke=Türkiye, standart=ISO 9001/14001/45001, sektör (EA kodu) ve şehir filtresi; firma + belgelendirme kuruluşu görünür. TÜRKAK belge doğrulama (tbds.turkak.org.tr) ve belgelendirme kuruluşlarının kendi belgeli firma listeleri tamamlayıcı. CertSearch'te çalışan sayısı yok; 5. adımla zenginleştirilir.
2. **OSB üye listeleri:** her OSB'nin kendi sitesinde firma/katılımcı sayfası; OSBÜK üzerinden 416 OSB dizini. Öncelik: ISO belgeli firma yoğunluğu yüksek OSB'ler (otomotiv yan sanayi, makine, metal, plastik, gıda, tekstil).
3. **İSO 500 / İkinci 500 (iso.org.tr):** yıllık PDF (üretimden satış, istihdam, ihracat). 1.000 firma; çoğu 250+ çalışanlı, yani 50-249 hedefine doğrudan uymaz; referans müşteri ve tedarikçi zinciri keşfi için kullan.
4. **Sanayi/ticaret odası ve ihracatçı birlikleri:** üye dizinleri (çoğu kayıt/izin gerektirir; KVKK ve kurum politikasına uy).
5. **Zenginleştirme:** Ticaret Sicil Gazetesi/MERSİS (sermaye, kuruluş), şirket siteleri ve kariyer sayfaları, LinkedIn (51-250 çalışan bandı), "kalite müdürü / kalite yönetim temsilcisi / strateji müdürü" ilanları (talep sinyali ve kişi bulma).
6. **Kanal ortakları:** ISO/EFQM danışmanları ve belgelendirme kuruluşları (TÜRKAK kapsam araması secure.turkak.org.tr/kapsam/search ile sistem belgelendirme kuruluşları listelenir; sayı BULUNAMADI). KOSGEB onaylı dijital olgunluk danışmanları imalat ICP'si için ayrı kanal.
7. **Puanlama:** belge sayısı/türü (9001+14001+45001), OSB'de olma, ihracat, ERP varlığı, KalDer ödül duyuruları (kalder.org), çalışan bandı.
Not: kişisel veri içeren listeler KVKK kapsamındadır; soğuk iletişim öncesi hukuki dayanak kontrolü gerekir.

## 7. BULUNAMADI / doğrulanamadı listesi
- TÜİK bülteninden (birincil) 10-49 ve 50-249 girişim sayısı ve imalat alt-kırılımı (yalnız köşe yazısı).
- ISO Survey ülke tablosu (iso.org): Türkiye ISO 9001/14001/45001 resmi yıllık sayı. Yalnız TÜRKAK paylaşımının özeti (18.527, yıl yok). ISO 14001 ve 45001 Türkiye sayıları BULUNAMADI.
- KalDer güncel üye sayısı; Mükemmellik Ödülü başvuru ve EFQM yetkinlik sayıları.
- TÜRKAK akredite sistem belgelendirme kuruluşu sayısı (yalnız tarihsiz toplam 990, tüm türler).
- Türkiye SaaS/kurumsal uygulama yazılımı güncel pazar büyüklüğü (USD). IDC ICT 30 milyar USD ve TÜBİSAD 761 milyar TL var, SaaS kırılımı yok. YASAD ve Deloitte raporu bulunamadı.
- KOBİ yazılım harcaması (TL/işletme) anketi; KOBİ'lerde ISO/strateji yazılımı kullanım oranı.
- KOSGEB faiz puanı değeri; SaaS aboneliğinin uygunluğu (yönerge açık değil).
- İhracatçı birlikleri üye sayısı; OSB'lerdeki ISO belgeli firma sayısı; poliklinik/tıp merkezi sayısı; özel okul alt-kırılımı.
- Google Trends / arama hacmi; LinkedIn rol sayıları.
- Ödeme istekliliği ve fiyat: müşteri görüşmesi olmadan yok.

## Kaynaklar
- K1 https://www.alomaliye.com/2025/12/24/kobi-istatistikleri-2024-girisim-sayisi-istihdam-ciro-dis-ticaret-ve-ar-ge/
- K2 https://www.dunya.com/kose-yazisi/ekonominin-belkemigi-kobiler/791544 ; https://www.24saatgazetesi.com/tuik-kobiler-girisimlerin-yuzde-996sini-olusturdu
- K3 https://x.com/turkak/status/2085627799222489402 (arama özeti; sayfa açılamadı)
- K4 https://www.globalstd.com/wp-content/uploads/2025/10/Infografia-ISO-Survey-2024_EN.pdf
- K5 https://www.simpleque.com/what-does-the-2023-iso-survey-tell-us-about-iso-9001-iso-14001-and-iso-45001-certifications/
- K6 https://www.alomaliye.com/2025/09/11/girisimlerde-bilisim-teknolojileri-kullanim-arastirmasi-2025/ (oranlar arama özetinden)
- K7 https://www.ekonomigazetesi.com/ekonomi/turkiyede-osb-sayisi-416ya-ulasti-69552 ; https://www.hurriyet.com.tr/gundem/bakan-kacir-osbler-turk-sanayisinin-omurgasi-niteliginde-42899023
- K8 https://www.cnbce.com/sirket-haberleri/yeni-liste-aciklandi-turkiyenin-sanayi-devleri-belli-oldu-ilk-10a-4-yeni-sirket-girdi-g31750 ; https://www.sozcu.com.tr/dev-fabrikalarda-istihdam-eriyor-p341179
- K9 https://www.meb.gov.tr/2024-2025-orgun-egitim-istatistikleri-aciklandi/haber/38473/tr
- K10 https://www.alomaliye.com/2025/12/04/saglik-harcamalari-istatistikleri-2024/ ; https://www.cumhuriyet.com.tr/saglik/yataklarin-yuzde-54u-ozelde-2259986
- K11 https://my.idc.com/getdoc.jsp?containerId=prMETA53171725
- K12 https://www.bloomberght.com/turk-yazilim-sektoru-yuzde-124-buyuyerek-761-milyar-tl-ye-ulasti-3779950
- K13 https://tbmm.gov.tr/Milletvekili/UyeGenelKurulKonusmalariDetay?eid=35890 ; https://secure.turkak.org.tr/kapsam/search
- K14 KOSGEB Yönergesi PDF: https://webdosya.kosgeb.gov.tr/Content/Upload/Dosya/KOB%C4%B0%20Dijital%20Donusum%20DP/2026/2026.05.12/KOB%C4%B0_Dijital_D%C3%B6n%C3%BC%C5%9F%C3%BCm_Destek_Program%C4%B1_Y%C3%B6nergesi.pdf
- K15 https://www.kosgeb.gov.tr/site/tr/genel/destekdetay/9144/kobi-dijital-donusum-destek-programi
- K16 https://www.ekonomigazetesi.com/ekonomi/kosgebin-2026-hedefi-53-bin-kobiye-destek-62345 ; https://kobitime.com/kosgeb-segem-sektorel-gelisim-merkezi-destek-pragrami/
- K17 https://www.dha.com.tr/kurumsal/34uncu-kalite-kongresinde-oduller-sahiplerini-buldu-2776412
- K18 https://www.hurriyet.com.tr/ekonomi/kalite-adalari-108613 (eski)
