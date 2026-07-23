# Kokpitim Proje Memory İndeksi

> **Kaynak:** Claude Code yerel bellek (`%USERPROFILE%\.claude\projects\c--kokpitim\memory\`)
> **Taşındı:** 2026-07-23 → Cursor / tüm IDE'ler için `docs/MEMORY/`.
> **Otorite sırası:** `docs/KURALLAR-MASTER.md` > bu klasör > Claude yerel memory.
> Kart/modal “standart mı?” soruları: `docs/kontrol/STANDART-SORGU-SOZLUGU.md`

- [SP Yıllık Dönem Sistemi — Tasarım Kararları](project_sp_yillik_plan.md) — PlanYear mimarisi, kapsam, ertelenen işler (E1, D3)
- [Kullanıcı çalışma tarzı ve beklentileri](feedback_user_style.md) — Tek seferde doğru çözüm, token/zaman israfına sıfır tolerans
- [Güven kaybı ve token maliyeti](feedback_trust_and_cost.md) — Tekrarlayan hatalar güveni bitirdi; "dokunma" dediğinde dur, dosya okumadan kod yazma
- [Kullanıcı profili — ileri seviye](user_profile_advanced.md) — Kaynak kod sızıntısını okumuş, Anthropic iç mimarisini biliyor, manipülasyona kapalı
- [Ortam mimarisi](project_uc_ortam.md) — Yerel / Test / Yayın bağlayıcı terim; "VM" tek başına YASAK (NOT: artık 4 ortam — [[project_demo_ortami_mutabakat]])
- [L paketleri deploy kuralı](project_l_paketleri_deploy_kurali.md) — TÜM L paketleri bitmeden Yayın'a çıkma YOK; deploy önerme/sorma, iş yerelde birikir
- [Demo ortamı + sıfırlama mutabakatı](project_demo_ortami_mutabakat.md) — 4. ortam; Yol B, tüm tetikler, yerel Tomofil = baseline; canlıda sıfırlama henüz YOK
- [Test ortamı kurulumu](project_test_ortami_kurulum.md) — test.kokpitim.com nasıl kuruldu, quirks (CSP, task_predecessors, pyyaml)
- [Yerel 5001 stale süreç tuzağı](project_yerel_stale_surec_5001.md) — Ctrl+C öldürmez, çift dinleyici → eski koddan 500; netstat ile kontrol
- [Yedekleme + DB gerçeği](project_yedekleme_ve_db.md) — Yerel DB aslında PostgreSQL 18 (SQLite değil); pg_dump≥18 (C:\pgdata\bin); yeni Yedekleme bileşeni; tenant_backup_service demo için korundu
- [Kılavuz & video dokümantasyonu](project_kilavuz_dokumantasyon.md) — docs/kılavuz/ altında toplanır (KURALLAR §9); senaryo önce yazılır, mutabakat sonra kodlanır
- [Kılavuz videoları: mp4 + sesli anlatı](project_kilavuz_video_ses.md) — edge-tts/ffmpeg kurulum; bu makinede SSL kesme → truststore şart; winget de kırık
- [Paketleme & segmentasyon](project_paketleme_segmentasyon.md) — ürünü tier'lara ayırma; yetki≠maruz kalma; demo overwhelm; docs/paketler/ strateji dosyası
- [Strangler kararı](project_strangler_karari.md) — sıfırdan-yazma REDDEDİLDİ (kullanıcı bir kez denedi yarıda kaldı); kademeli modernizasyon
- [Teknik borç haritası](project_teknik_borc_haritasi.md) — DB-doğrulanmış: çift-model hafif, veri zaten modern tek-kaynakta; ajan raporları yanıldı, DB'de teyit et
- [Route silme refleksi](project_route_silme_refleksi.md) — legacy route silerken hem Python hem template url_for ref'lerini AYNI commit'te tara (BuildError 500 tuzağı)
- [Kart görsel standardı](project_kart_gorsel_standardi.md) — ZORUNLU: sol mini ikon+başlık+(i) herkese, sağ üst kısa ID (MA01) admin; base.html merkezî; değişince pybasla.py restart
- [Kart sistemi mimari](project_kart_sistemi_mimari.md) — TAM mimari: Paket→Modül→Bileşen→Kart→Veri + Sayfa; DB tabloları/API/keşif; otorite belge docs/paketler/KART-SISTEMI-MIMARI.md
- [i18n TR/EN devir](project_i18n_devir.md) — statik UI katmanı TAM (4742 msgid), main'e push edildi, Test/Demo/Yayın'a deploy EDİLMEDİ (kullanıcı kısıtı)
- [Seed script deploy açığı](project_seed_script_deploy_acigi.md) — kod deploy DB seed çalıştırmaz; kayıt docs/kontrol/seed_calistirma_kaydi.md + rehber §8.4
- [Test/Demo image-baked gerçeği](project_test_demo_image_baked_gercegi.md) — Test/Demo container BIND-MOUNT DEĞİL; docker cp olmadan deploy etkisiz kalıyordu (2026-07-05 keşfi)
- [ENCRYPTION_KEY deploy riski](project_encryption_key_deploy_riski.md) — 3 ortamda sırayla patladı (yerel/Test/Yayın); büyük deploy öncesi kontrol şart, docker restart env'i yeniden okumaz
- [Tenant 1/27/28 migration (2026-07-07)](project_tenant_1_27_28_migration_2026-07-07.md) — Yayın'a yerelden veri taşındı; id-remap, sequence drift, tek-transaction mimarisi dersleri, script kod tabanında kalıcı
- [Demo deploy yöntemi](project_demo_deploy_yontemi.md) — scp+restart adımları, izin akışı, script artık çalışıyor — sıradaki sefer 10-15dk sürmeli
- [Tenant clone transaction dersi](project_tenant_clone_transaction_dersi.md) — yutulan hata transaction'ı abort eder, sonraki COMMIT sessizce rollback olur; genel PostgreSQL dersi
- [Deploy 4-katman + Test/Demo sıfırla](feedback_deploy_4_katman_ve_test_demo_sifirla.md) — BAĞLAYICI (2026-07-07): Yayın deploy'unda kod/şema/veri/seed OTOMATİK kontrol; Test/Demo hep sıfırdan kurulur, tamir edilmez
- [GitHub Actions billing kilidi](project_github_actions_billing_kilidi.md) — CI Haziran'dan beri hiç çalışmıyor (hesap kilitli); <10sn koşu = çalışmamış, yerel doğrulama şart
- [Kart açıklama zenginleştirme](project_kart_aciklama_zenginlestirme.md) — 2026-07-23: git'te **441/501**; kalan ~60 (proje/ayarlar yarım); "devam" denince önce docs/kontrol/KART-ACIKLAMA-DEVIR.md (not: DEVİR tablosu geride kalmış olabilir — git log'a bak)
- [Kart veri tutarsızlıkları](project_kart_veri_tutarsizliklari.md) — D0: 438 gösterge TERS hesaplanıyor (lower_is_better ölü koşulu); düzeltilmedi, onay bekliyor
