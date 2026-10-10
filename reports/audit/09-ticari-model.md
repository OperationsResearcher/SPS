# 09 — Ticari Model (Kokpitim)
Tarih: 2026-10-10 | **Tüm sayılar varsayıma dayalı, doğrulanmamıştır.** Gerçek müşteri, ödeme istekliliği veya maliyet verisi yoktur. Rakip fiyatları 06'dan (üçüncü taraf beyanı) alınmıştır.

## 1. Model karşılaştırması
Uygunluk = Kokpitim için hipotez.
| Model | Nasıl çalışır | Artı | Eksi | Segment | Uygunluk |
|---|---|---|---|---|---|
| Tek seferlik lisans | Kalıcı lisans + yıllık bakım | Kamuda "demirbaş" gibi alınabilir; peşin nakit | Gelir sürekliliği yok; sürüm yükü; çok kiracılı SaaS mimarisine ters | Kamunun bir kısmı | Düşük |
| Abonelik (kurum başı, kademeli paket) | Yıllık, Başlangıç/Yönetim/Strateji | Öngörülebilir gelir; mevcut paket yapısına uyar; satın alma basit | Kamuda yıllık hizmet alımı prosedürü | Tüm segmentler | **Yüksek** |
| Kullanıcı bazlı | Kullanıcı/ay (global norm: Perdoo, Cascade) | Büyümeyle gelir artar | Kullanıcı eklemeyi caydırır; "veri girecek az kişi" segmenti; kamu bütçe tahmini zor | KOBİ/OKR tarzı | Orta-Düşük |
| Kurum bazlı (sabit + kullanıcı bandı) | Kurum başı sabit, band içinde kullanıcı | Şeffaf; kamu bütçesine uyar (limit altı tasarlanabilir) | Büyük kurumda değer yakalanmaz (band ile çözülür) | Kamu, üniversite, orta firma | **Yüksek** (abonelikle birleşik) |
| Kullanım bazlı | KPI/veri noktası/AI çağrısı başı | Düşük giriş | Tahmin edilemez fatura; kamuda zor | AI yorum eklentisi | Düşük (yalnız AI kotası) |
| Kurulum / eğitim / danışmanlık | Tek seferlik hizmet | Hızlı nakit; benimseme artar | Ölçeklenmez | Hepsi, özellikle kamu | **Yüksek** (paket olarak) |
| Kurumsal / on-prem | Müşteri sunucusunda | Büyük/hassas kamu için kapı | Destek, sürüm yönetimi, güvenlik sorumluluğu | Büyük kamu/holding | Düşük (özel sözleşme, MVP'de yok) |
| Kanal satışı | Komisyon %15-25 veya iş ortağı fiyatı | CAC düşer, güven | Marj erir; kalite kontrolü | Danışmanlı kurumlar | Orta-Yüksek |

**Öneri [HİPOTEZ]:** kurum bazlı kademeli yıllık abonelik (kullanıcı bandı) + ücretli kurulum/eğitim + AI kotası + danışman komisyonu. Tek seferlik ve on-prem ilk aşamada yok.

## 2. Rakip fiyat referansı (06, beyan/üçüncü taraf; URL'ler 06 §8)
| Rakip | Referans |
|---|---|
| Perdoo | EUR 8-10/kullanıcı/ay, yıllık, min 5 (Tability 2026-07-31); Capterra EUR 6,4/8 |
| Cascade | Ücretsiz plan; tahmin ~$19-29/kullanıcı/ay (ITQlick, resmi değil) |
| Spider Impact | $125/ay (1+), $895/ay (10+), $1.950/ay (25+) (zoftwarehub, 2024-09) |
| ClearPoint | $50/özellik/ay (Capterra) |
| BSC Designer | $59,95/ay veya $599,40/yıl (G2) |
| Quantive | Teams $9/kullanıcı/ay; Vendr medyan $49.370/yıl |
| Envisio | ~$20.000/yıl başlangıç (üçüncü taraf) |
| Planview | AgilePlace $29/kullanıcı/ay; Vendr medyan $72.408/yıl |
| Bimser Ensemble | Fiyat bulunamadı |

Okuma [HİPOTEZ]: global kurum başı yıllık ~$10-70K; 25 kullanıcılı Spider Impact ≈ $23.400/yıl. 1 USD = 42 TL varsayımıyla (kur DOĞRULANMADI) $10K ≈ 420.000 TL. Yerli alıcı satın alma gücü nedeniyle yerli fiyat bu bandın altında konumlanabilir; doğrulama ödeme istekliliği görüşmeleriyle yapılır.

## 3. TL fiyat önerisi aralıkları [HİPOTEZ, KDV hariç, yıllık]
| Paket | Hedef | Kullanıcı bandı | Aralık (TL/yıl) | Gerekçe |
|---|---|---|---|---|
| Başlangıç | KOBİ, küçük kurum | ~10 | 48.000-96.000 | Global OKR araçlarının 10 kullanıcı karşılığının altı; fiyata duyarlı segment |
| Yönetim | Orta ölçek, üniversite birimi, belediye | 25-50 | 150.000-300.000 | Spider 25 kullanıcı ~$23K'nın altı; 340.391 TL kamu limiti altında tasarlanabilir |
| Strateji | Üniversite/büyük kurum | ~100 | 300.000-600.000 | K-Radar+ileri analiz; Quantive/Corporater bandının altı |
| Holding/Kurumsal eklenti | Çok kurum | teklif | +%30-60 veya teklif | API, çok-kurum kırılımı |
| Kurulum ve eğitim | Hepsi | - | 15.000-90.000 tek sefer | 1-5 gün, şablon ve veri aktarımı |
| AI yorum | Eklenti | - | Başlangıçta dahil (kotalı) / 12.000-36.000 | LLM maliyeti yönetilmeli |

Kamu notu: 22/d limiti 340.391 TL (büyükşehir dışı) / 1.021.827 TL (büyükşehir sınırı içi), **resmi teyit gerek** (08 §0). Lisans+kurulum toplamı limit altında tutulabilir; ancak limiti aşmamak için alımı bölmek mevzuata aykırı olabilir, hukuki görüş şart.

## 4. Varsayımlar tablosu
| # | Varsayım | Kötümser | Baz | İyimser | Not |
|---|---|---|---|---|---|
| A1 | Yıl 1 ücretli kurum | 3 | 8 | 18 | Pilot dönüşümü ve satış kapasitesi tahmini |
| A2 | ARPA, TL/yıl | 90.000 | 150.000 | 220.000 | §3 aralık |
| A3 | Kurulum/eğitim geliri, TL/kurum | 10.000 | 25.000 | 40.000 | Paket başı |
| A4 | Brüt marj | %70 | %75 | %80 | Tek Oracle VM; destek emeği belirsiz |
| A5 | Yıllık churn | %25 | %15 | %10 | B2B tipik varsayım, doğrulanmadı |
| A6 | CAC, TL/kurum (doğrudan harcama) | 120.000 | 70.000 | 45.000 | 08 kanal maliyetleri |
| A7 | Pilot->ücretli | %15 | %35 | %50 | Hipotez H6 |
| A8 | Kur 1 USD | 42 TL | 42 TL | 42 TL | Doğrulanmadı |
| A9 | Kurucu emeği | dahil değil | dahil değil | dahil değil | Maliyeti düşük gösterir |
| A10 | Sabit gider/yıl (sunucu, araç, muhasebe, hukuk) | 150.000 | 150.000 | 150.000 | Tahmin |

## 5. Senaryolar (VARSAYIMA DAYALI, DOĞRULANMAMIŞ)
Formüller: abonelik geliri = A1 x A2; hizmet geliri = A1 x A3; CAC toplamı = A1 x A6; LTV = A2 x A4 / A5 (kurulum hariç); geri ödeme (ay) = A6 / (A2 x A4 / 12).
| Metrik | Kötümser | Baz | İyimser |
|---|---|---|---|
| Abonelik geliri (TL) | 270.000 | 1.200.000 | 3.960.000 |
| Kurulum/eğitim geliri (TL) | 30.000 | 200.000 | 720.000 |
| Toplam gelir (TL) | 300.000 | 1.400.000 | 4.680.000 |
| CAC toplamı (TL) | 360.000 | 560.000 | 810.000 |
| Brüt kâr (abonelik x marj + hizmet tam) | ~232.500 | ~1.100.000 | ~3.888.000 |
| Sabit gider | 150.000 | 150.000 | 150.000 |
| Yıl 1 net (CAC ve sabit sonrası, emek hariç) | ~-277.500 | ~+390.000 | ~+2.928.000 |
| LTV (TL) | 252.000 | 750.000 | 1.760.000 |
| LTV/CAC | 2,1 | 10,7 | 39 |
| CAC geri ödeme (ay) | ~23 | ~7,5 | ~3 |

Okuma: baz ve özellikle iyimser senaryodaki LTV/CAC (10,7 ve 39) gerçek dışı yüksektir; CAC yalnız doğrudan harcamadır (kurucu/satış emeği hariç, A9), churn ve ARPA iyimserdir, örneklem küçüktür. Kötümser senaryo yıl 1'de zararla biter, emek eklenince daha da kötüdür. Karar için tek geçerli girdi: ilk 10 fırsat sonrası gerçek pilot dönüşümü, teklif fiyatı ve CAC.
Kırılma notu [HİPOTEZ]: baz varsayımlarla yıl 1 kâr çıkması için ~6+ ücretli kurum gerekir; 3 kurumla zarar beklenir.

## 6. Kamu satın alma ve model etkileşimi
- Kamu alımı genelde bütçe yılına bağlı; çok yıllı sözleşme zor olabilir (doğrulanmadı). Yıllık abonelik uyar.
- 22/d limiti altı fiyat doğrudan temin olanağı verebilir (teyitsiz); kalem ayrıştırmada parçalama yasağı hukuken kontrol edilmeli.
- Ortak yazılım/SPBİS çakışması, yerli yazılım tercihi, güvenlik/KVKK ve sunucu yeri koşulları DOĞRULANAMADI -> kamu satışı öncesi hukuki/teknik araştırma.
- On-prem talebi çıkarsa ayrı sözleşme (+%50-100 [HİPOTEZ]) ve SLA.

## 7. Fiyat deneyleri ve karar noktaları
1) İlk 10 teklifte fiyat A/B (08 §3.8). 2) "Kullanıcı bandı mı sabit mi" sorusu keşifte. 3) Van Westendorp 4 soru, 10 görüşmede. 4) Kurucu müşteri indirimi %20-30, 12 ay sınırlı. 5) 3 ay sonra: kabul <%20 ise fiyatı düşür veya değer vaadini sorgula; >%60 ise fiyat düşük kalmış olabilir, artır.
Fiyat şeffaflığı rakip matrisinde boşluktur (06 §5): "başlangıç fiyatı" yayınlanabilir, kamu için teklif usulü.

## 8. Açık kararlar (kullanıcı)
Kurum bazlı mı kullanıcı bazlı mı; AI maliyet kotası; pilot ücretsiz mi; Yayın çıkış zamanı ve KVKK/sözleşme; komisyon yüzdesi; kur/enflasyon indeksleme maddesi.
