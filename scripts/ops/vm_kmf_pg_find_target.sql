SELECT
  k.id AS kpi_id,
  k.name AS kpi_name,
  k.is_active,
  p.id AS process_id,
  p.name AS process_name,
  COUNT(kyc.id) AS cfg_count,
  SUM(CASE WHEN kyc.is_included IS FALSE THEN 1 ELSE 0 END) AS cfg_false_count
FROM process_kpis k
JOIN processes p ON p.id = k.process_id
JOIN tenants t ON t.id = p.tenant_id
LEFT JOIN kpi_year_configs kyc ON kyc.process_kpi_id = k.id
WHERE t.name ILIKE '%Kayseri%Model%Fabrika%'
  AND p.name ILIKE '%PAZARLAMA%'
  AND k.name ILIKE '%Teklif%'
GROUP BY k.id, k.name, k.is_active, p.id, p.name
ORDER BY k.id;
