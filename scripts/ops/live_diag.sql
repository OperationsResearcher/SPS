SELECT now() AS ts_utc;

SELECT state, count(*) AS cnt
FROM pg_stat_activity
WHERE datname = current_database()
GROUP BY state
ORDER BY state;

SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    wait_event_type,
    wait_event,
    EXTRACT(EPOCH FROM (now() - query_start))::int AS duration_s,
    LEFT(query, 180) AS query_sample
FROM pg_stat_activity
WHERE datname = current_database()
ORDER BY query_start DESC
LIMIT 25;
