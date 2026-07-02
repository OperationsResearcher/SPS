# Kart Standardı — Sayfa İlerleme Takibi

> Kaynak: `docs/paketler/kradar.txt` (tekil sayfa + kart sayısı) + `kart-kimlik-standardi.csv`.
> Her sayfa: data-card-code işaretle → keşfet → short_id + açıklama → doğrula.
> base.html/route değişince `python pybasla.py` ile restart.

## ✅ Tamamlanan (önceki turlar)
- /masaustu (MA01-19)
- /sp (SP01-13)
- /process (PR01-07)
- /process/karne (PK01-13)
- /project (PJ01-08)
- /k-radar/ks (KD01-12)
- /k-radar/kp (KD21-24)
- /k-rapor?tab=kurumsal (KR01-07)
- /k-rapor?tab=surec-pg (1 kart — işaretlendi, seed bekliyor)

## ✅ /k-rapor TAMAMEN TAMAM (KR01-81)
- Statik mc-card'lar: KR01-57 (54 kart, 16 sekme) — index.html
- JS-üretilen mini-stat kartlar: KR58-81 (24 kart) — k_rapor.js'e data-card-code
  eklendi + elle DB'ye yazıldı (faaliyet/veri-durumu/uyari/pg-dagilim/aktivite-takvim/
  strateji-kapsama/bildirim-analiz). MutationObserver AJAX'ta yakalıyor.
- Kurumsal Hedefte/Riskli/Kritik (KR03-05) JS-stat — ilk turda yapıldı.
NOT: kr-bir-saglik (bireysel sağlık 4 stat) bloğu CSV'de ayrı kart olarak yoktu,
atlandı — bireysel sekmesinde 2 statik tablo kartı (KR) zaten var.

## ⏳ /raporlar/* — DURUM
TÜM /raporlar sayfaları JS-driven (statik mc-card yok; kartları ayrı JS dosyaları üretir).
short_id öneki: RP. statCard helper'ına 4. param `code` eklenip işaretleniyor;
tablo/kapsayıcı kartlar template'te data-card-code; sonra elle DB seed.

✅ Tamamlanan /raporlar:
- departman-performans (RP01-04)
- yonetici-liderlik (RP05-06)
- cmmi-heatmap (RP07-14)
- hedef-revizyon (RP15-19)
- bireysel-hizalama (RP20-23)
- initiative-bubble (RP24-34)
- initiative-roadmap (RP35-38)
- quarterly-review (RP39-45)
- operasyon-istatistik (RP46-49)
- okr-cascade (RP50-53; objective/key_result/ort/plan_yili stat — 3 örnek objective kartı veri-instance, atlandı)
- sabah-ozeti (RP54-60)
- muda-analizi (RP61-65)
- risk-heatmap (RP66-71)
- early-warning (RP72-75)
- ml-anomaly (RP76-79)
- veri-kalitesi (RP80-87)
- iki-fa (RP88-93)
- audit-paketi (RP94-96)
- onay-zinciri (RP97-101)
- vrio-portfoy (RP102-111; 5 stat + 5 bucket kartı)
- sunburst (RP112)
- cfo-dashboard (RP113-121)
- coo-dashboard (RP122-129)
- chro-dashboard (RP130-138)
- evrim-filmi (RP139)
- strateji-hikayesi (RP140-142)
- sektor-benchmark (RP143-145)
- carbon-trend (RP146-150)
- ai-coach (RP151-154)
- ai-sunum (RP155-157)
- nlp-query (RP158-159)
- bi-connector (RP160-164)

- yatirimci-sunum (RP165-166)
- stratejik-yillik (RP167-168)
- esg-rapor (RP169-170)
- bireysel-karne-batch (RP171-172)
- mobile (RP173)
- hizalama-sankey (RP174-179)

ATLANAN (veri-instance / launcher — kart standardı dışı):
- ai-danisman (JS-üretilen AI öneri içeriği)
- sektorel (8 sektör launcher kartı, for döngüsü)
- pg-proje-etki, esg-yonetim, sektorel-detay (CSV'de kart yok / detay alt sayfa)

## ✅✅ /raporlar TURU TAMAMLANDI: 38 sayfa, RP01-179 (179 kart)
## ✅ strateji-haritasi: /sp/strateji-haritasi, sp_strateji_haritasi.* (6 kart, SP öneki)
   (5 render + str_girisim koşullu — initiative_count varsa görünür)

## 📄 SAYFA KATALOĞU (SystemPage) — 68 sayfa
- system_pages tablosu (migration e5f6a7b8c9d0): code(=kart prefix), name, url, short_id.
- short_id modül-kısa: MA, SP, PR, PK, PJ, KD-KS/KP, KR-<tab>, RP-<sayfa>.
- Sayfa ID rozeti base.html'de: yalnız Admin, sayfa üstünde ortada; sayfadaki ilk
  data-card-code prefix'inden page-meta API ile çözülür.
- Çöp DB kayıtları temizlendi (${code}, {{ ep_codes }}); keşif servisine
  ${/{{/} guard eklendi (tekrar gelmesin).

## 🎉 TÜM KART STANDARDİZASYONU TAMAMLANDI — 343 kart + 68 sayfa DB'de
MA(masaustu) · SP(sp + strateji-haritasi) · PR(process) · PK(karne) · PJ(project) ·
KD(k-radar) · KR(k-rapor 16 sekme) · RP(raporlar 38 sayfa).
Atlananlar (gerekçeli, veri-instance/launcher): sektorel, ai-danisman, okr-objective örnekleri.

ATLANANLAR (veri-instance / launcher — kart standardı dışı):
- sektorel (8 sektör kartı {% for s in sektorler %} ile veri-driven menü; k-radar hub gibi)
- strateji-haritasi → CSV prefix sp_strateji_haritasi (/sp/strateji-haritasi); SP öneki ile
  /sp dünyasında ele alınacak, raporlar değil. 6 kart bekliyor.

### Kalan /raporlar/* (her 'devam'da 3-4 sayfa):
departman-performans(4) · yonetici-liderlik(2) · cmmi-heatmap(8) · hedef-revizyon(5) ·
bireysel-hizalama(4) · initiative-bubble(11) · initiative-roadmap(4) · quarterly-review(7) ·
okr-cascade(7) · sabah-ozeti(7) · operasyon-istatistik(4) · muda-analizi(5) · risk-heatmap(6) ·
early-warning(4) · ml-anomaly(4) · veri-kalitesi(8) · iki-fa(6) · audit-paketi(3) · onay-zinciri(5) ·
vrio-portfoy(10) · sektorel(8) · strateji-haritasi(6) · sunburst(1) · evrim-filmi(1) ·
strateji-hikayesi(3) · sektor-benchmark(3) · cfo-dashboard(9) · coo-dashboard(8) · chro-dashboard(9) ·
yatirimci-sunum(2) · stratejik-yillik(2) · esg-rapor(2) · carbon-trend(5) · ai-danisman(2) ·
ai-coach(4) · ai-sunum(3) · nlp-query(2) · bireysel-karne-batch(2) · mobile(1) · bi-connector(5)

## short_id öneki planı
MA=masaustu · SP=sp · PR=process · PK=karne · PJ=project · KD=k-radar · KR=k-rapor(sekmeler) · RP=raporlar/*

## Not (k-rapor index.html tuzağı)
Otomatik satır-bazlı script bu dosyada iç içe mc-card + çok-satır başlık yüzünden kaydı.
Sekme sekme elle işaretlemek gerekiyor. /raporlar/* ayrı dosyalar daha güvenli.
