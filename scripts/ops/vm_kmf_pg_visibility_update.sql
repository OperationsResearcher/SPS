BEGIN;

-- Hedef PG: yalnızca KMF tenant + ilgili KPI adı
WITH target_kpi AS (
  SELECT k.id AS kpi_id
  FROM process_kpis k
  JOIN processes p ON p.id = k.process_id
  JOIN tenants t ON t.id = p.tenant_id
  WHERE t.name = 'Kayseri Model Fabrika'
    AND k.name = 'Tekliflerin Sözleşmeye Dönüşme Oranı - Sürdürülebilirlik'
)
UPDATE kpi_year_configs kyc
SET is_included = CASE WHEN py.year = 2024 THEN FALSE ELSE TRUE END
FROM plan_years py, target_kpi tk
WHERE kyc.plan_year_id = py.id
  AND kyc.process_kpi_id = tk.kpi_id;

COMMIT;
