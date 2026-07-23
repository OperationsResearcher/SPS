---
name: project_demo_ortami_mutabakat
description: "Demo ortamı (demo.kokpitim.com) yapısı + sıfırlama mutabakatı; Yol B, tüm tetikler, yerel Tomofil = baseline"
metadata: 
  node_type: memory
  type: project
  originSessionId: 0265ef0d-566e-4066-930c-3200531599d0
---

Demo = 4. ortam (Yerel/Test/**Demo**/Yayın). `demo.kokpitim.com` · Oracle VM `129.159.30.175` · `/opt/kokpitim-demo` · port **5080** · container `kokpitim-demo-web` · DB `kokpitim_demo_db` · `KOKPITIM_DEMO_MODE=1`. Tek Tomofil tenant'ı (`DEMO_TENANT_ID` vars. 27) ziyaretçi deneyimine açık.

**2026-06-02 kullanıcı mutabakatı (bağlayıcı, KURALLAR-MASTER §8.4'e işlendi):** Demo'da "oturum bitince Tomofil baseline'a sıfırlanır" özelliği **canlıda HENÜZ YOK** (demo/routes.py v1: `/demo/end` ve timeout sadece flask session temizliyor, veriye dokunmuyor). Kurulacak. Karar:
- **Yol B** seçildi: tek paylaşılan Tomofil + snapshot'tan geri yükleme (S3 per-session clone değil — v2'ye ertelendi).
- Sıfırlama tetikleri: **hepsi** (manuel çıkış + 60dk süre dolumu + inaktivite).
- Eşzamanlı ziyaretçi çakışması **bilinçli kabul edildi** (engel değil).
- Baseline = **yereldeki güncel Tomofil tenant'ının hali** → demo'ya aktarılacak.
- Hedef: sıfırlama özelliğini kur + güncel kod + baseline DB'yi demo'ya aktar.

**Kırmızı çizgiler:** Demo komutları YALNIZCA `*-demo` hedeflerine dokunur; Test/Yayın ASLA. Saf kod deploy'u DB'ye dokunmaz; seed/wipe/migration yalnızca kullanıcı açıkça isteyince. Yayın (Canlı) kullanıcı verisi = kırmızı çizgi, her güncellemede önce yedek. Detay tasarım: `docs/DEMO-ORTAMI-PLAN.md`. [[project_uc_ortam]]

**2026-06-09 operasyonel doğrulama (deploy + reseed çalıştı):**
- Canlı `kokpitim-demo-web` container'ı **app bind-mount'lu** (`/opt/kokpitim-demo/app -> /app`) — yani kod güncelleme = tarball aç + `docker restart` (rebuild YOK). DİKKAT: `setup_demo_env.sh`'deki `docker run` bunu göstermiyor ama canlı container'da VAR; körlemesine güvenme, `docker inspect ... .Mounts` ile teyit et.
- **Reseed akışı (çalışan):** yerelde `tenant_backup_service.export_tenant_json(27)` → `.json.gz` → scp → `/opt/kokpitim-demo/instance/` → `docker exec -w /app kokpitim-demo-web python -m scripts.demo_load_tomofil /app/instance/<dosya>` → doğrula → `python -m scripts.demo_baseline snapshot`. Yükleme `fk_safe_tenant_load` (236 FK düşür/geri-ekle). Yerel Tomofil = **tenant 27** (demo Tomofil de 27, aynı ID).
- Yükleme öncesi mutlaka `pg_dump kokpitim_demo_db` güvenlik yedeği (FK-drop yarıda kalırsa diye). Kılavuz executor importları lazy + `_is_local` → demo'da edge-tts/playwright GEREKMEZ, deploy çökmez.

**2026-06-09 ŞEMA KAYMASI dersi (önemli):** Demo DB şeması **alembic-takipsiz** ve eskiydi (157 tablo, `project.initiative_id` YOK, project 34 sütun). Yeni kodu deploy edince `/kurum` & `/project` 500 verdi (`column project.initiative_id does not exist`). Saf kod deploy'u şemayı migrate ETMEZ. **Sürüm tuzağı:** yerel PG **18**, VM PG **14** → yerel `pg_dump` (full/schema) PG14'e geri yüklenemez (pg_dump geriye uyumsuz). Çözüm (çalıştı): (1) demo'da `DROP SCHEMA public CASCADE` (postgres, önce bağlantıları `pg_terminate_backend`) → (2) container içinde `db.create_all()` ile şemayı **PG14-native** kur (162 tablo) + `CREATE TABLE alembic_version` → (3) veriyi **sürüm-bağımsız** yükle: yerelden `pg_dump --data-only --disable-triggers --no-owner` (COPY, ~3MB), `zcat | sudo -u postgres psql` (PG18 SET satırları zararsız hata verir, ON_ERROR_STOP=0) → (4) `GRANT ALL` demo_user → (5) restart + `demo_baseline snapshot` (161 tablo). alembic_version `f5215370eebd` data dump'tan geldi. NOT: tenant export json.gz **eksik** (74/162 tablo — okr/swot/bsc/initiatives kapsam dışı); tam veri için data-only COPY dump şart. Demo artık 6 tenant'ın tamamını taşıyor (yalnız Tomofil 27 UI'da görünür).
