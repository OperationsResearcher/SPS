SELECT
  py.year,
  k.id AS kpi_id,
  k.name AS kpi_name,
  k.is_active,
  kyc.id AS cfg_id,
  kyc.is_included
FROM kpi_year_configs kyc
JOIN plan_years py ON py.id = kyc.plan_year_id
JOIN process_kpis k ON k.id = kyc.process_kpi_id
JOIN processes p ON p.id = k.process_id
JOIN tenants t ON t.id = p.tenant_id
WHERE t.name = 'Kayseri Model Fabrika'
  AND k.name = 'Tekliflerin Sözleşmeye Dönüşme Oranı - Sürdürülebilirlik'
ORDER BY py.year;
