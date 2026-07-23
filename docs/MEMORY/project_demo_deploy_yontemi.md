---
name: project_demo_deploy_yontemi
description: "Demo VM'e (demo.kokpitim.com) kod deploy etme yöntemi — adımlar, izin akışı, sık hatalar"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3af866c2-0f81-47ca-8ef6-e73c2668665f
---

Demo VM (`129.159.30.175`, `/opt/kokpitim-demo/app`) **git repo DEĞİL** — `.git` yok. Deploy
= değişen dosyaları `scp` ile `/tmp/demo_deploy/`'a kopyala → `sudo cp` ile hedef yerlerine taşı
(sahiplik `197609:197609`) → `docker restart kokpitim-demo-web`. Container bind-mount'lu
(`/opt/kokpitim-demo/app -> /app`), rebuild GEREKMEZ. [[project_test_demo_image_baked_gercegi]]
Test/Yayın'ın aksine bu bilgi zaten biliniyordu ama ilk oturumda unutulup yeniden keşfedildi.

**İzin akışı (önemli, tekrar sorgulanmasın):** Harness "SSH yalnızca operatör" kuralını otomatik
Bash çağrılarına da uyguluyor — kullanıcı sohbette "izin veriyorum" dese bile bazı SSH-yazma
komutları yine de tek tek engellenip onay istenebilir. Kullanıcı "sen çalıştırsana, hepsini
senin yapmanı bekliyorum" dediğinde bu engel kalkıyor (aynı komutlar ikinci denemede geçti).
Yani: SSH okuma (docker inspect, psql SELECT) genelde sorunsuz: yazma/restart komutlarında
bir kez daha "bunu sen yap" onayı gerekebilir, tekrar tekrar sormak yerine doğrudan dene.

**Kalıcı olarak düzeltilmiş script:** `scripts/demo_clone_tenant.py` artık ÇALIŞIYOR ve test
edildi (Tom1/Tom2/Tom3 başarıyla klonlandı). Bir sonraki "demoyu güncelle" isteğinde bu script'i
sıfırdan debug etmeye GEREK YOK — sadece değişen dosyaları scp+restart yeterli. TASK-228'de
(2026-07-07) 2 saat süren asıl neden şuydu: script YENİ yazılıyordu ve gerçek demo DB şemasıyla
`TABLE_PLAN` varsayımları uyuşmuyordu + bir transaction hatası vardı — ikisi de artık kalıcı
olarak giderildi ([[project_tenant_clone_transaction_dersi]]).

**Standart deploy adımları (sıradaki sefer için):**
```
1. git diff ile değişen dosyaları listele
2. scp ile /tmp/demo_deploy/'a kopyala
3. ssh: sudo cp + chown 197609:197609 hedef dosyalara
4. Yeni env değişkeni varsa .env'e ekle (hem /opt/kokpitim-demo/.env hem app/.env)
5. docker restart kokpitim-demo-web
6. Şema/veri değişikliği varsa: demo_baseline snapshot yeniden al
7. curl ile localhost:5080 üzerinden smoke test (dışarıdan demo.kokpitim.com'a curl
   atmak sandbox'tan çalışmıyor olabilir — VM içinden test et)
```
Bu adımlar artık ~10-15 dakikada biter, yeni bir hata çıkmadığı sürece.

**2026-07-08 dersi (Tom1/2/3 kayboldu vakası):** Klon/veri değişikliğinden sonra
`snapshot_baseline()` çağrılmazsa, ilk otomatik sıfırlama (60dk/inaktivite/çıkış)
TÜM public tabloları eski baseline'dan geri yükleyip klonları SİLER — adım 6 atlanamaz.
Ayrıca klondan ÖNCE demo DB'de global sequence resync gerekebilir (id-remap'li
migration'lar sequence drift bırakıyor; belirti: `duplicate key ... _pkey Key (id)=(küçük sayı)`).
Klon scriptinin `process_sub_strategy_links` resync uyarısı zararsızdır (composite PK, id yok).
DİKKAT: klon hatası tek-transaction'da tümünü geri sarar ama script exit 0 dönebiliyor —
başarıyı DB'den tenant sayısıyla teyit et.
