# K-Radar UI Kabul Checklist (Faz F)

Bu kontrol listesi, K-Radar ekranlarının fonksiyonel kabulü için yerel test adımlarını içerir.

## 1) Hub

- [ ] Toplam skor kartları yükleniyor (KS/KP/KPR/Toplam)
- [ ] Öneri listesi geliyor
- [ ] Yönetici kullanıcıda Onayla/Reddet butonları görünüyor
- [ ] Yönetici olmayan kullanıcıda butonlar görünmüyor
- [ ] Kural tetikleyiciler kartı dolu/boş durumda doğru metin veriyor
- [ ] Aksiyon geçmişi filtre/sayfalama çalışıyor
- [ ] CSV indir butonu filtre parametresiyle doğru dosya indiriyor

## 2) KS Modülleri

- [ ] SWOT, PESTLE, TOWS, Gap, OKR, Hoshin, Ansoff, BCG, BSC, EFQM sayfaları açılıyor
- [ ] Her sayfa API'den gelen metrikleri doğru gösteriyor
- [ ] Veri yok senaryosunda ekran çökmeden `0`/`-` fallback gösteriyor

## 3) KP Modülleri

- [ ] Olgunluk CRUD (ekle/güncelle/sil) yönetici kullanıcıda çalışıyor
- [ ] Yönetici olmayan kullanıcı write işlem yapamıyor
- [ ] Darboğaz, Değer Zinciri, Pareto, SLA, Benchmark, OEE, VSM, Kapasite metrikleri yükleniyor
- [ ] 30g trend alanları tüm KP alt sayfalarda görünüyor

## 4) KPR Modülleri

- [ ] CPM analiz akışı (proje seç + analiz et) çalışıyor
- [ ] EVM, Risk, Kaynak Kapasite, Gantt sayfaları metrik basıyor
- [ ] Boş veri durumunda ekranlar fallback ile stabil

## 5) Cross Modülleri

- [ ] Isı haritası ve detay panel etkileşimli çalışıyor
- [ ] Paydaş CRUD + filtre/sıralama çalışıyor
- [ ] Rekabet, A3/5Neden, Anket sayfaları metrik basıyor

## 6) Güvenlik / İzolasyon

- [ ] Tenant-A kullanıcısı Tenant-B verisini göremiyor
- [ ] Write endpointler sadece yetkili roller için açık
- [ ] API hata durumları kullanıcıya anlaşılır toast/mesaj döndürüyor

## 7) Tarayıcı ve UX

- [ ] Sayfalar yenilenince duplicate event bind olmuyor
- [ ] Uzun listelerde performans kabul edilebilir
- [ ] Türkçe karakterler ve tarih formatı ekranda doğru
