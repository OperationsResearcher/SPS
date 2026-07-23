---
name: project-test-demo-image-baked-gercegi
description: "Test/Demo container kodu bind-mount DEĞİL, image-baked — docker cp olmadan deploy etkisizdir; 2026-07-05'te keşfedildi"
metadata: 
  node_type: memory
  type: project
  originSessionId: 1c201b8f-7e54-4158-89cc-c16526a01fc7
---

`docs/SUNUCU-GUNCELLEME-REHBERI.md`'de uzun süre "Test/Demo kodu BIND-MOUNT, güncelleme = dosya değiştir +
`docker restart`" yazıyordu. 2026-07-05'te bu **Test için yanlış** çıktı: `docker inspect kokpitim-test-web`
yalnızca `.env`/`instance`/`logs` mount ediyor — uygulama kodu image'a build anında gömülü. Host dizinine
(`/opt/kokpitim-test/app/...`) `scp`/tarball ile dosya koymak çalışan container'ı **etkilemiyor**,
`docker restart` de etkilemiyor (aynı image'ı yeniden başlatıyor, dosya sistemini yenilemiyor).

**GÜNCELLEME (2026-07-07, TASK-228):** `kokpitim-demo-web` için bu tekrar `docker inspect` ile teyit
edildi ve **DEMO GERÇEKTEN BIND-MOUNT'LU** çıktı (`/opt/kokpitim-demo/app -> /app`, `/opt/kokpitim-demo/
instance -> /app/instance`, `/opt/kokpitim-demo/logs -> /app/logs`, hepsi RW). Yani **Test ve Demo
container'ları farklı davranıyor** — Test image-baked, Demo bind-mount. Demo'ya deploy: host dosyasını
scp+cp ile güncelle → `docker restart` yeterli, `docker cp` gerekmez. Ama körü körüne güvenme — HER
ortamda deploy öncesi `docker inspect <container> --format '{{json .Mounts}}'` ile o anki gerçek durumu
teyit et, bu iki container'ın davranışı gelecekte de değişebilir (rebuild edilirse image-baked olabilir).

**Why:** Bu yüzden `tour.py`/`kule_service.py` düzeltmesi "Test'e deploy edildi" denip container'a hiç
ulaşmamıştı — `docker exec kokpitim-test-web grep ...` ile container içi dosya içeriği kontrol edilince
eski/hatalı kod çıktı. Kaç önceki deploy'un da sessizce etkisiz kaldığı bilinmiyor (geriye dönük
doğrulama yapılmadı).

**How to apply:** Test/Demo'ya kod deploy ederken artık ZORUNLU ek adım: host dizinini güncelledikten
sonra `docker cp <host-yol> kokpitim-test-web:/app/<yol>` ile çalışan container'ın kendi dosya sistemine
de yaz, SONRA `docker restart`. Deploy sonrası MUTLAKA `docker exec <container> grep -n "<beklenen>" <yol>`
ile container İÇİNDEKİ dosyayı doğrula — host'ta doğru görünmesi yeterli kanıt değil. Detaylı yordam +
kod örneği: `docs/SUNUCU-GUNCELLEME-REHBERI.md` §1a ve §5.

Aynı oturumda ayrıca: yerel PG18 → sunucu PG14 arası dump/restore yaparken `--format=plain` kullan
(custom format çapraz sürümde `pg_restore: unsupported version` verir), PG18 dump'ındaki `\restrict`/
`\unrestrict` satırlarını `grep -v` ile temizle, ve `sudo -u postgres psql -f` ile restore edilen
tabloların sahipliğini mutlaka app kullanıcısına devret (yoksa "permission denied", sequence sync da
sessizce başarısız görünür).

**GÜNCELLEME (2026-07-15, Demo+Test+Yayın deploy):** `docker inspect` ile üçü de teyit edildi:
Demo `/opt/kokpitim-demo/app -> /app` BIND-MOUNT (delta dosya koy + `docker restart` yeterli, `docker cp`
gerekmez); Test `.env`/`instance`/`logs` mount ama `/app` IMAGE-BAKED; Yayın sadece `instance` mount,
image-baked. **Test bayat kalma tuzağı:** Test image 2026-07-02 tarihliydi = ~2 hafta geride; delta yama
`app/__init__.py`'yi güncelledi ama onun import ettiği `app/utils/tenant_guard.py` (commit de8d7610, 92ce6a8
ÖNCESİ) Test tabanında hiç yoktu → `ModuleNotFoundError` → worker boot fail. Delta-yama bayat tabana yama
olur; kovalamak deneme-yanılmadır. **Doğru çözüm (kurala uygun, "Test sıfırdan kurulur"):** `app/.env`'i
yedekle → `rm -rf app` → `git clone -b main` → `.env` geri koy → `docker build` → yeni container.
**ENCRYPTION_KEY .env tuzağı:** Test'te İKİ .env var — `/opt/kokpitim-test/.env` (May 26, ENCRYPTION_KEY YOK)
ve `/opt/kokpitim-test/app/.env` (Jul 2, ENCRYPTION_KEY VAR + 7 kritik değişken). Doğru mount `app/.env`;
yanlışını mount edince `RuntimeError: ENCRYPTION_KEY zorunludur` → boot fail. Deploy öncesi
`grep -c ENCRYPTION_KEY <env>` ile hangi .env'in dolu olduğunu teyit et. Yayın deploy'u `oracle_safe_deploy.sh`
ile sorunsuz: PG yedek → satır sayısı diff (değişmedi) → build → Alembic (migration yoktu). Script'in son
health check'i `http://127.0.0.1/health` (port 80/nginx) deniyor → 404 verir ama YANILTICI; app port 5000'de,
`curl :5000/health` ile teyit et.

İlgili: [[project_seed_script_deploy_acigi]], [[project_yedekleme_ve_db]], [[project_encryption_key_deploy_riski]], [[feedback_deploy_4_katman_ve_test_demo_sifirla]]
