# DB birleştirme: Veri = VM (prod), Şema = yerel migration head

Bu runbook, **VM’deki tüm kullanıcı verisini** koruyup **tablo/kolon yapısını** repodaki Alembic head’e (ör. `d4e5f6g7h8i9`) taşımak için kullanılır.

## Önkoşullar

- Hedef ortamda `pg_restore` / `pg_dump` (PostgreSQL client 14+ uyumlu).
- Yerel repoda `python -m flask db heads` tek head gösteriyor olmalı.
- **Referans yedekler:** `backups/vm_safety_20260410/`, GCP disk snapshot’ları (`TASK-083`).
- **KMF kontrol:** `backups/kmf_pre_merge_reference/` + `TASK-084` sayıları.

## Hazır artefact’lar (yerel repo)

| Dosya | Açıklama |
|-------|----------|
| `backups/merge_prep/kokpitim_vm_data_only_20260410.dump` | VM `kokpitim_db` **yalnızca veri** (`pg_dump -Fc --data-only`) |
| `scripts/ops/prod_stabilize_audit_sequence.sql` | `audit_logs` sequence hizalama (idempotent) |
| `scripts/ops/kmf_export_on_vm.sh` | Birleşme sonrası KMF sayım + CSV dilimi |

`pg_dump` sırasında **döngüsel FK** uyarıları normaldir; restore’da `--disable-triggers` kullanın.

---

## Aşama 1 — Boş hedef veritabanı + yerel şema

1. Boş DB oluşturun (örnek isim: `kokpitim_merge_target`).

2. Uygulama bağlantısını bu DB’ye yönlendirin:
   - `SQLALCHEMY_DATABASE_URI=postgresql://.../kokpitim_merge_target`

3. Şemayı oluşturun:
   ```bash
   python -m flask db upgrade
   ```

4. Doğrulama:
   ```bash
   python -m flask db current
   ```
   Çıktı, hedef head revision olmalı (ör. `d4e5f6g7h8i9`).

---

## Aşama 2 — VM verisini yükleme (data-only)

1. **Yazmayı durdurun** (uygulama kapalı veya maintenance).

2. Restore (örnek):
   ```bash
   pg_restore -h HOST -U USER -d kokpitim_merge_target \
     --data-only \
     --no-owner \
     --disable-triggers \
     -v \
     kokpitim_vm_data_only_20260410.dump
   ```

3. Hata çıkarsa:
   - `ERROR` satırını not edin (çoğunlukla: yeni şemada NOT NULL kolon, kaldırılmış tablo, tip uyumsuzluğu).
   - Gerekirse tek tablo `pg_restore -t tablo_adi` veya küçük düzeltme migration’ı / tek seferlik SQL.

---

## Aşama 3 — Sequence ve tutarlılık

1. Audit ve diğer seri alanlar:
   ```bash
   psql -d kokpitim_merge_target -f scripts/ops/prod_stabilize_audit_sequence.sql
   ```

2. Gerekirse ek tablolar için `MAX(id)` → `setval` (import sonrası duplicate PK önlemi).

---

## Aşama 4 — KMF kontrol mekanizması (TASK-084)

Birleşme sonrası **aynı tanımlarla** sayıları karşılaştırın:

| Metrik | Birleşme öncesi (VM, TASK-084) |
|--------|--------------------------------|
| tenant_id | 16 |
| Kullanıcı | 8 |
| Süreç | 11 |
| PG | 135 |
| PGV (`kpi_data`, `deleted_at IS NULL`) | 318 |

1. Hedef DB’de tenant `id` hâlâ 16 mı ve ad aynı mı kontrol edin (import’ta id değişmezse doğrudan karşılaştırılır).

2. VM’de veya hedefte `scripts/ops/kmf_tenant_backup_and_counts.sql` içindeki mantığı `tenant_id = 16` ile çalıştırın veya `kmf_export_on_vm.sh` mantığını hedef `DATABASE_URL` ile uyarlayın.

3. Dört sayı **aynı** değilse: veri kaybı veya filtre/tenant eşleşmesi hatası vardır; merge onaylanmaz.

---

## Aşama 5 — Prod’a taşıma (ayrı pencere)

1. TASK-083 rollback hazır olsun.
2. Aynı sıra: boş prod clone veya bakım penceresinde hedef DB → `upgrade` → data-only restore → sequence → KMF kontrol → uygulama aç.

---

## Notlar

- **Tavizsiz veri:** Kaynak tek dosya: `kokpitim_vm_data_only_*.dump`. Yerel DB’deki satırlar bu merge’e karıştırılmamalıdır.
- **Daha yeni prod dump:** Canlıya geçmeden önce VM’den taze `--data-only` alıp dosya adını güncelleyin.
- Canlı container’da `flask db` import sorunu yaşandıysa, migration’ı **şemayı taşıyan ortamda** (yerel veya düzeltilmiş image) çalıştırıp prod’a sadece **hazır şema + restore** uygulayın.
