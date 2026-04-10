-- Kayseri Model Fabrika (KMF) — referans sayımları (VM / merge sonrası karşılaştırma)
-- Çalıştırma: psql -d kokpitim_db -v ON_ERROR_STOP=1 -f kmf_tenant_backup_and_counts.sql
\pset footer off

WITH kmf AS (
  SELECT id, name
  FROM tenants
  WHERE name ILIKE '%Kayseri%Model%Fabrika%'
     OR name ILIKE '%Kayseri Model Fabrika%'
     OR (name ILIKE '%Kayseri%' AND name ILIKE '%Model%' AND name ILIKE '%Fabrika%')
  ORDER BY id
  LIMIT 1
)
SELECT
  k.id AS kmf_tenant_id,
  k.name AS kmf_tenant_name,
  (SELECT count(*) FROM users u WHERE u.tenant_id = k.id) AS kullanici_sayisi,
  (SELECT count(*) FROM processes pr WHERE pr.tenant_id = k.id) AS surec_sayisi,
  (SELECT count(*)
   FROM process_kpis pk
   JOIN processes pr ON pr.id = pk.process_id
   WHERE pr.tenant_id = k.id) AS pg_sayisi,
  (SELECT count(*)
   FROM kpi_data kd
   JOIN process_kpis pk ON pk.id = kd.process_kpi_id
   JOIN processes pr ON pr.id = pk.process_id
   WHERE pr.tenant_id = k.id
     AND kd.deleted_at IS NULL) AS pgv_sayisi
FROM kmf k;

-- Eşleşme yoksa boş döner; o zaman tenants listesinden manuel id ile sorgu gerekir.
