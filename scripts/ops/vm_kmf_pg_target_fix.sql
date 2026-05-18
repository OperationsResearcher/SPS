BEGIN;

UPDATE process_kpis k
SET is_active = TRUE
WHERE k.id = (
  SELECT k2.id
  FROM process_kpis k2
  JOIN processes p ON p.id = k2.process_id
  JOIN tenants t ON t.id = p.tenant_id
  WHERE t.name ILIKE '%Kayseri%Model%Fabrika%'
    AND p.name ILIKE '%PAZARLAMA%'
    AND k2.name = 'Tekliflerin Sözleşmeye Dönüşme Oranı - Sürdürülebilirlik'
  ORDER BY k2.id
  LIMIT 1
);

INSERT INTO kpi_year_configs (plan_year_id, process_kpi_id, is_included, created_at, updated_at)
SELECT
  py.id AS plan_year_id,
  (
    SELECT k2.id
    FROM process_kpis k2
    JOIN processes p ON p.id = k2.process_id
    JOIN tenants t ON t.id = p.tenant_id
    WHERE t.name ILIKE '%Kayseri%Model%Fabrika%'
      AND p.name ILIKE '%PAZARLAMA%'
      AND k2.name = 'Tekliflerin Sözleşmeye Dönüşme Oranı - Sürdürülebilirlik'
    ORDER BY k2.id
    LIMIT 1
  ) AS process_kpi_id,
  CASE WHEN py.year = 2024 THEN FALSE ELSE TRUE END AS is_included,
  NOW(),
  NOW()
FROM plan_years py
JOIN tenants t ON t.id = py.tenant_id
WHERE t.name ILIKE '%Kayseri%Model%Fabrika%'
ON CONFLICT (plan_year_id, process_kpi_id)
DO UPDATE SET
  is_included = EXCLUDED.is_included,
  updated_at = NOW();

COMMIT;
