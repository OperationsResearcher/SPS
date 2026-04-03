-- PostgreSQL: kpi_data / kpi_data_audits id sekanslarini MAX(id) ile hizala.
-- Calistirma: psql -d kokpitim_db -v ON_ERROR_STOP=1 -f fix_kpi_data_sequences.sql
SELECT setval(
    pg_get_serial_sequence('kpi_data', 'id'),
    COALESCE((SELECT MAX(id) FROM kpi_data), 0) + 1,
    false
);
SELECT setval(
    pg_get_serial_sequence('kpi_data_audits', 'id'),
    COALESCE((SELECT MAX(id) FROM kpi_data_audits), 0) + 1,
    false
);
