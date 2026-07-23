---
name: project_tenant_clone_transaction_dersi
description: "PostgreSQL: sessizce yutulan bir hata transaction'ı abort eder, sonraki COMMIT rollback'e döner — demo_clone_tenant.py'de yaşanan kök neden"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3af866c2-0f81-47ca-8ef6-e73c2668665f
---

TASK-228'de (2026-07-07) `scripts/demo_clone_tenant.py` "✓ klonlandı: 102076 kayıt" diye
başarı mesajı veriyordu ama commit sonrası hiçbir satır kalıcı olmuyordu — RETURNING id bile
doğru dönüyordu ama SELECT hep 0 buluyordu. Debug 1.5+ saat sürdü çünkü belirti (sessiz veri
kaybı, exception yok) yanıltıcıydı.

**Kök neden:** Sequence-resync döngüsü, `id` kolonu olmayan composite-PK tablolarda
(`process_sub_strategy_links` gibi) `pg_get_serial_sequence(...)` çağırınca PostgreSQL hatası
alıyordu. Bu hata Python'da `except Exception: pass` ile yutuluyordu — AMA PostgreSQL tarafında
transaction "aborted" durumuna geçiyor. Aborted transaction'da sonraki her komut (COMMIT dahil)
sessizce reddedilir/rollback olur, exception fırlatmaz eğer connection düzeyinde yakalanmıyorsa.

**Genel ders — her yerde geçerli:** PostgreSQL + SQLAlchemy'de bir transaction içinde HERHANGİ
bir statement hata verirse (`try/except: pass` ile yutulsa bile), o transaction'ın geri kalanı
zehirlenir. Kurallar:
1. Bir transaction'da riskli/best-effort işlemler (sequence resync, opsiyonel temizlik vb.)
   varsa bunları TAMAMEN AYRI bir `engine.begin()` bloğunda yap — ana veri transaction'ı
   commit olduktan SONRA.
2. `except Exception: pass` asla "güvenli" değildir eğer aynı transaction'da başka DML
   devam edecekse — sessiz görünür ama transaction'ı bozar.
3. Şüpheli "veri kayboldu ama hata yok" durumlarında ilk kontrol: ayrı transaction'larda
   best-effort try/except var mı, ve ana transaction ile aynı connection'ı mı paylaşıyor.

**Diğer küçük ama tekrarlayabilecek hatalar (aynı script'te):**
- `user` tablosu PostgreSQL reserved keyword — tırnaksız `SELECT * FROM user` yanlış parse
  olabilir, her zaman `"user"` gibi çift tırnakla yaz.
- JSON/JSONB kolonlu satırları ham SQL INSERT ile yazarken dict/list tipini `json.dumps` ile
  serialize etmeden bind etme — `psycopg.ProgrammingError: cannot adapt type 'dict'` verir.
  `tenant_backup_service._coerce_row_bind_params` bu işi zaten yapıyor, tekrar yazmak yerine
  import edip kullan.
- TABLE_PLAN'daki WHERE clause varsayımları (örn. `kpi_data_audits.process_kpi_id`) gerçek
  şemayla uyuşmayabilir (gerçeği `kpi_data_id`ymiş) — yeni bir tabloya dokunmadan önce
  `information_schema.columns`'tan gerçek kolon adını doğrula, TABLE_PLAN'a körü körüne güvenme.

Bu script artık düzeltilmiş halde repoda duruyor ([[project_demo_deploy_yontemi]]) — bir
sonraki tenant klonlama ihtiyacında bu script tekrar kullanılabilir, sıfırdan yazılmasına
gerek yok.
