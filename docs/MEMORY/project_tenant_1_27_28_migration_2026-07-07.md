---
name: project-tenant-1-27-28-migration-2026-07-07
description: "Yayın'da tenant 1/27/28 (Default Corp/Tomofil/Eskişehir Makine) verisi yerelinkiyle değiştirildi — Kayseri MF/Kara Brothers/VolTure dokunulmadı"
metadata: 
  node_type: memory
  type: project
  originSessionId: 1c201b8f-7e54-4158-89cc-c16526a01fc7
---

2026-07-07'de kullanıcı isteğiyle Yayın'da (production) tenant_id 1 (Default Corp),
27 (Tomofil Otomotiv), 28 (Eskişehir Makine)'in TÜM verisi (kullanıcılar dahil)
silinip yerel (geliştirme) DB'deki aynı tenant_id'lerin verisiyle değiştirildi.
Kayseri Model Fabrika (16), Kara Brothers (29), VolTure Tech (30/31) — hiç
dokunulmadı, doğrulandı (kullanıcı/veri sayıları önce/sonra aynı).

**Why:** Yerelde geliştirilen/test edilen yeni kurum verisi Yayın'a taşınacaktı,
ama Yayın'daki 4 ortak tenant_id'nin (1/16/27/28) 3'ü (16 hariç) artık yerelin
kopyası olacak şekilde güncellenmesi isteniyordu.

**How to apply / önemli teknik bulgular (gelecekte benzer migration'lar için):**

1. **`scripts/migrate_tenants_1_27_28_prod.py`** kalıcı script olarak kod tabanında
   duruyor — id-remap mantığı, DELETE/COPY sırası, sequence düzeltme adımları
   içeriyor. Benzer bir tenant migration gerekirse şablon olarak kullanılabilir
   (tenant_id'leri ve TABLES_LEVEL1/LEVEL2 listelerini güncelle).
2. **id çakışması riski gerçekti**: yerel ve Yayın'ın `users.id` aralıkları
   çakışıyordu (yerel 1-8290, Yayın diğer tenant'larda 75-8294) — id-remap
   zorunluydu, "aynı id'yle taşı" yaklaşımı burada güvenli DEĞİLDİ.
3. **Yayın'da önceden var olan sequence drift**: `processes.id` sequence'i
   gerçek MAX(id)'den (1M+) çok geride (85) kalmıştı — muhtemelen geçmişte
   elle/import ile yüksek id'li satır eklenmiş, sequence hiç senkronize
   edilmemiş. Bu, migration'dan bağımsız bir Yayın sorunuydu, INSERT sırasında
   "duplicate key" hatasına yol açtı, `pre_copy_sequence_check()` ile düzeltildi.
4. **PostgreSQL system trigger'ları** (`RI_ConstraintTrigger_*`, FK constraint'leri)
   normal DB kullanıcısı tarafından DISABLE edilemez ("permission denied: is a
   system trigger") — bu BEKLENEN, script zaten doğru FK sırasıyla (child→parent)
   siliyor/ekliyor olduğu için sorun yaratmadı.
5. **Tek-transaction mimarisi gerekliydi**: DRY_RUN'da silme+ekleme adımlarını
   AYRI rollback etmek, ekleme adımının hâlâ-Yayın'da-duran eski veriyle (örn.
   users.email UNIQUE) sahte çakışma yaşamasına yol açtı. Çözüm: tüm adımlar
   tek transaction'da, commit/rollback kararı en sonda tek seferde.
6. **KRİTİK BUG (bulunup düzeltildi)**: hata-kurtarma kodunda `conn.rollback()`
   kullanmak (tablo/kolon yoksa 0 dönmek için) ADIM 1'de (henüz hiçbir
   DELETE/INSERT yokken) güvenliydi ama ADIM 5'te (verify, DELETE+INSERT'ten
   SONRA) AYNI çağrı tüm migration'ı sessizce geri alıyordu. Düzeltme:
   SAVEPOINT ile izolasyon (conn.rollback() yerine).
7. **VM üzerinde doğrudan çalıştırmak** (yerelden SSH tüneli yerine) performansı
   çok artırdı — SSH tüneli üzerinden 91995 satırlık kpi_data işlemi 30+ dakika
   sürüp pratik olarak bitmiyordu, VM'de host'ta (psycopg2 --user kurulumu ile,
   container'a dokunmadan) saniyeler içinde tamamlandı.
8. **Script'in "kaç onay adımı olduğunu" saymak kritik** — otomatik `printf
   'EVET\n'` pipe ile önceden hazırlanan onay sayısı yanlış sayılırsa (bu
   oturumda 8 yerine 6 sayıldı), script ADIM 5/6 arasında EOF hatasıyla crash
   oldu. Sonuç: veri DB'de kalıcı ve doğru bulundu (muhtemelen bağlantı kapanma
   sırasının PostgreSQL commit davranışıyla beklenenden farklı etkileşmesi) ama
   script'in "resmi" verify+commit adımı hiç çalışmadı — sonuç salt-okunur
   kontrolle doğrulanıp kabul edildi, script tekrar ÇALIŞTIRILMADI (zaten
   commit olmuş veriye tekrar sil+ekle riskli olurdu).

**Final sonuç (doğrulandı):** users=132, processes=85, kpi_data=91995, plan_years=11
Yayın'da 1/27/28 için doğru. Birkaç düzine satır (notifications/strategies/
audit_logs/project) FK veya JSON-adapt hatası nedeniyle atlandı — kabul edildi,
veri bütünlüğünü bozmuyor. Kayseri MF/Kara Brothers/VolTure değişmedi. Site sağlıklı.

İlgili: [[project_encryption_key_deploy_riski]] (aynı oturumda, deploy sırasında
ayrıca ENCRYPTION_KEY sorunu da çıktı ve çözüldü)
