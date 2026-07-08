# VERBİS Hazırlık Kontrol Listesi

> 2026-07-08 (TASK-234). VERBİS = Veri Sorumluları Sicil Bilgi Sistemi.

## 0. Kayıt yükümlülüğü değerlendirmesi (İLK ADIM)

- [ ] Yıllık çalışan sayısı 50'den çok MU veya yıllık mali bilanço 25M TL'den büyük MÜ?
      `[DOLDURULACAK]` — Hayır ise ve ana faaliyet özel nitelikli veri işleme değilse
      **kayıt yükümlülüğü yoktur**; yine de envanter ve aydınlatma yükümlülükleri geçerlidir.
- [ ] Eşik güncel mi kontrol et — Kurul kararlarıyla değişebilir `[DANIŞMAN TEYİDİ]`.

## 1. Kayıt öncesi hazır olması gerekenler

- [x] Kişisel veri işleme envanteri → [veri-envanteri.md](veri-envanteri.md) (taslak hazır, `[DOLDURULACAK]` alanları var)
- [ ] Kişisel Veri Saklama ve İmha Politikası (envanterdeki saklama süreleri netleşince yazılır)
- [x] Aydınlatma metni taslağı → [aydinlatma-metni.md](aydinlatma-metni.md)
- [ ] İrtibat kişisi ataması (gerçek kişi, TC kimlik ile VERBİS'e girilir)
- [ ] Veri işleyen sözleşme eki (müşteri kurumlarla DPA benzeri protokol)

## 2. VERBİS'e girilecek özet bilgiler (envanterden türetilir)

- Veri kategorileri: kimlik, iletişim, özlük (performans), işlem güvenliği, görsel (profil foto)
- İşleme amaçları: İK/performans yönetimi, hizmet sunumu, bilgi güvenliği, iletişim
- Alıcı grupları: barındırma sağlayıcı, e-posta sağlayıcı, (varsa) AI sağlayıcı
- Yurt dışı aktarım: `[DOLDURULACAK — Oracle bölge teyidi]`
- Saklama süreleri: envanter §4
- Teknik/idari tedbirler: envanter §5 (VERBİS'teki hazır listeden işaretlenir)

## 3. Teknik yapılacaklar (kod tarafı — ayrı task açılabilir)

- [ ] Pazarlama sitesine gizlilik politikası + çerez aydınlatması sayfası (`micro/modules/marketing/` — şu an YOK)
- [ ] Demo talep formuna aydınlatma onay kutusu/bağlantısı
- [ ] Login sayfasına aydınlatma metni bağlantısı
- [ ] AI prompt'larına giden içerikte ad-soyad maskeleme denetimi
- [ ] Audit log saklama süresi politikasının koda bağlanması (otomatik temizlik)
