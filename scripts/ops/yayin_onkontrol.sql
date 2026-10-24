-- Yayın/Test ön kontrolü (SALT OKUNUR) — deploy-2026-07-08 sonrası 15 migration'ın veri etkisini önceden ölçer.
-- Kullanım (Yayın container'ında):  psql "$DATABASE_URL" -f scripts/ops/yayin_onkontrol.sql > docs/kontrol/yayin_onkontrol_$(date +%F_%H%M).txt
-- Hiçbir şey yazmaz: tek transaction READ ONLY. Çıktıyı deploy ÖNCESİ kontrol dosyasıyla birlikte sakla.
BEGIN READ ONLY;
\pset format aligned
\echo '== 1. Mevcut alembic revizyonu (Yayın bunun ÜSTÜNE migration alacak)'
SELECT version_num FROM alembic_version;

\echo '== 2. Etkilenen tabloların boyutu (kilit/süre riski: büyük tablo = uzun ALTER/UPDATE)'
SELECT c.relname AS tablo, c.reltuples::bigint AS tahmini_satir, pg_size_pretty(pg_total_relation_size(c.oid)) AS boyut
  FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
 WHERE n.nspname = 'public' AND c.relkind = 'r'
   AND c.relname IN ('kpi_data','kpi_data_audits','individual_performance_indicators','project','risk_heatmap_items',
                     'plan_years','users','process_sub_strategy_links','initiatives','system_cards','process_kpis')
 ORDER BY pg_total_relation_size(c.oid) DESC;
SELECT pg_size_pretty(pg_database_size(current_database())) AS veritabani_boyutu,
       (SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()) AS acik_baglanti;

\echo '== 3. [ux01] Mükerrer AKTİF bireysel PG (migration en eskisini bırakıp kalanları is_active=false yapar)'
SELECT count(*) AS pasiflesecek_satir
  FROM individual_performance_indicators
 WHERE is_active AND source_process_kpi_id IS NOT NULL
   AND id NOT IN (SELECT MIN(id) FROM individual_performance_indicators
                   WHERE is_active AND source_process_kpi_id IS NOT NULL
                   GROUP BY user_id, source_process_kpi_id);

\echo '== 4. [e9669] kpi_data yetim user_id (migration NULL''a çeker; ölçüm KORUNUR)'
SELECT count(*) AS yetim_user_id
  FROM kpi_data kd
 WHERE kd.user_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM users u WHERE u.id = kd.user_id);

\echo '== 5. [e9669] period_type dağılımı (migration normalize eder: tanınmayan değer var mı?)'
SELECT period_type, count(*) AS satir FROM kpi_data GROUP BY 1 ORDER BY 2 DESC;

\echo '== 6. [f0aa] Sayıya indirgenecek kpi_data (dolu actual/target metinleri; büyük sayı = uzun backfill)'
SELECT count(*) FILTER (WHERE btrim(actual_value) <> '') AS dolu_actual,
       count(*) FILTER (WHERE btrim(target_value) <> '') AS dolu_target
  FROM kpi_data;

\echo '== 7. [a1f2/yb16] Plan yılı backfill: planı HİÇ olmayan kurum (bu kurumların satırları plan_year_id=NULL kalır)'
SELECT count(*) AS plan_yili_olmayan_aktif_kurum
  FROM tenants t
 WHERE t.is_active AND NOT EXISTS (SELECT 1 FROM plan_years py WHERE py.tenant_id = t.id);
SELECT count(*) AS plan_yili_olmayan_kurumun_projesi
  FROM project p WHERE NOT EXISTS (SELECT 1 FROM plan_years py WHERE py.tenant_id = p.tenant_id);

\echo '== 8. [bi01] Bireysel PG yılı kaynak süreç PG''sinden farklı olan satır (migration hizalar)'
SELECT count(*) AS hizalanacak
  FROM individual_performance_indicators i
  JOIN process_kpis pk ON pk.id = i.source_process_kpi_id
 WHERE i.plan_year_id IS DISTINCT FROM pk.plan_year_id;

\echo '== 9. [b7d3/hd01] Risk ısı haritası: elle girilmiş satır ve proje bağlantısı'
SELECT source_type, count(*) AS satir FROM risk_heatmap_items GROUP BY 1 ORDER BY 2 DESC;

\echo '== 10. [3919] system_cards.description en uzun değer (varchar(512)->Text; kısaltma yok, bilgi amaçlı)'
SELECT max(length(description)) AS en_uzun FROM system_cards;

\echo '== 11. Veri sayıları (deploy SONRASI bununla birebir aynı olmalı; satır kilidi)'
SELECT (SELECT count(*) FROM tenants) AS kurum, (SELECT count(*) FROM users) AS kullanici,
       (SELECT count(*) FROM processes) AS surec, (SELECT count(*) FROM process_kpis) AS surec_pg,
       (SELECT count(*) FROM kpi_data) AS kpi_data, (SELECT count(*) FROM strategies) AS strateji,
       (SELECT count(*) FROM individual_performance_indicators) AS bireysel_pg;
ROLLBACK;
