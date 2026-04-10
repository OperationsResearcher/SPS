## Prod Migration Merge Runbook (`b9c0d1e2f3a8` -> `d4e5f6g7h8i9`)

Bu runbook, prod stabilizasyonu ve yerel migration hattini guvenli bir sekilde birlestirmek icindir.

### 0) Kapsam

- **Prod mevcut revision:** `b9c0d1e2f3a8`
- **Hedef revision:** `d4e5f6g7h8i9`
- **Gecis sirasinda uygulanacak ops fix:** `scripts/ops/prod_stabilize_audit_sequence.sql`

### 1) Hazirlik ve checkpoint

1. Tam DB dump al.
2. VM disk snapshot al.
3. Aktif container/image bilgisini not et.
4. Bakim penceresi belirle (dusuk trafik).

Basari kriteri:
- Dump dosyasi olusturuldu.
- Snapshot `READY`.

### 2) Staging prova (zorunlu)

1. Prod dump'i staging DB'ye yukle.
2. Uygulama kodunu hedef branch'e cek.
3. Ops fix uygula:
   - `psql -d <staging_db> -f scripts/ops/prod_stabilize_audit_sequence.sql`
4. Migration uygula:
   - `python -m flask db upgrade`
5. Smoke test calistir:
   - login/logout
   - admin panel gecisleri
   - hizli sayfa gecisleri
   - kritik endpointler

Basari kriteri:
- `python -m flask db current` -> `d4e5f6g7h8i9`
- 5xx/timeout yok.
- Audit duplicate key hatasi yok.

### 3) Canli gecis (A sonra B)

#### A) Ops stabilizasyon (schema disi)

1. Prod DB yedegini tekrar al (ikinci checkpoint).
2. Ops SQL uygula:
   - `psql -d kokpitim_db -f scripts/ops/prod_stabilize_audit_sequence.sql`
3. Hemen kontrol:
   - `SELECT MAX(id) FROM audit_logs;`
   - `SELECT last_value, is_called FROM audit_logs_id_seq;`

#### B) Migration gecisi

1. Hedef kodu deploy et.
2. Migration calistir:
   - `python -m flask db upgrade`
3. Revision kontrol:
   - `python -m flask db current`
4. Gerekirse uygulama container'ini kontrollu restart et.

Basari kriteri:
- Prod revision `d4e5f6g7h8i9`.
- Panel ve kritik endpointler normal.
- 524 dalgasi tekrar etmiyor.

### 4) Post-deploy izleme (30-60 dk)

- `docker logs` ve uygulama error loglari.
- DB active session/wait kontrolleri.
- Cloudflare 52x kodlari.
- Kullanici tarafindan hizli gecis testi.

### 5) Rollback plani

Herhangi bir kritik hata durumunda:

1. Uygulamayi onceki stabil image'a dondur.
2. DB'yi en son alinan dump/snapshot'tan geri don.
3. Trafigi rollback sonrasi smoke test ile ac.

### 6) Notlar

- Ops SQL idempotenttir, tekrar calissa da zarar vermez.
- Prod'a migration tek seferde degil, sadece staging provasi basariliysa uygulanir.
- Bu runbook schema migration'i ile operasyonel fix'i ayri katmanlarda tutar.
