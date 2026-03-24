#!/usr/bin/env bash
# VM: kod + Alembic (ekleme migration) — veri silmez.
# Önkoşul: /home/kokpitim.com/public_html içinde kod güncel (git pull yapılmış olabilir).
set -euo pipefail

APP_DIR="/home/kokpitim.com/public_html"
BACKUP_DIR="$APP_DIR/backups"
CONTAINER="sps-web"
IMAGE="sps_web_final:latest"
PG_DB="${PG_DATABASE:-kokpitim_db}"
TS="$( date +%Y%m%d_%H%M%S )"

mkdir -p "$BACKUP_DIR"

echo "==> 1/6 PostgreSQL tam yedek (gzip)"
sudo -u postgres pg_dump "$PG_DB" | gzip -c > "$BACKUP_DIR/pg_${PG_DB}_full_${TS}.sql.gz"
ls -la "$BACKUP_DIR/pg_${PG_DB}_full_${TS}.sql.gz"

echo "==> 2/6 Temel tablo satır sayıları (önce)"
COUNT_BEFORE="$BACKUP_DIR/rowcounts_before_${TS}.txt"
sudo -u postgres psql -d "$PG_DB" -At -c "
SELECT 'tenants|'||count(*) FROM tenants
UNION ALL SELECT 'users|'||count(*) FROM users
UNION ALL SELECT 'processes|'||count(*) FROM processes
UNION ALL SELECT 'process_kpis|'||count(*) FROM process_kpis
UNION ALL SELECT 'kpi_data|'||count(*) FROM kpi_data
UNION ALL SELECT 'process_activities|'||count(*) FROM process_activities
UNION ALL SELECT 'project|'||count(*) FROM project
UNION ALL SELECT 'task|'||count(*) FROM task;
" | sort > "$COUNT_BEFORE"
cat "$COUNT_BEFORE"

echo "==> 3/6 Git pull"
cd "$APP_DIR"
sudo git pull origin main

echo "==> 4/6 Docker image + container"
sudo docker build -t "$IMAGE" .
sudo docker stop "$CONTAINER" 2>/dev/null || true
sudo docker rm "$CONTAINER" 2>/dev/null || true
sudo docker run -d --name "$CONTAINER" -p 80:5000 \
  -v /home/kokpitim.com/public_html/instance:/app/instance \
  "$IMAGE"

echo "==> 5/6 Alembic upgrade (Flask CLI yerine run_db_upgrade.py)"
sleep 5
sudo docker exec "$CONTAINER" bash -lc 'cd /app && python3 scripts/run_db_upgrade.py'

echo "==> 6/6 Satır sayıları (sonra) — önceki ile aynı olmalı"
COUNT_AFTER="$BACKUP_DIR/rowcounts_after_${TS}.txt"
sudo -u postgres psql -d "$PG_DB" -At -c "
SELECT 'tenants|'||count(*) FROM tenants
UNION ALL SELECT 'users|'||count(*) FROM users
UNION ALL SELECT 'processes|'||count(*) FROM processes
UNION ALL SELECT 'process_kpis|'||count(*) FROM process_kpis
UNION ALL SELECT 'kpi_data|'||count(*) FROM kpi_data
UNION ALL SELECT 'process_activities|'||count(*) FROM process_activities
UNION ALL SELECT 'project|'||count(*) FROM project
UNION ALL SELECT 'task|'||count(*) FROM task;
" | sort > "$COUNT_AFTER"

if diff -q "$COUNT_BEFORE" "$COUNT_AFTER" >/dev/null; then
  echo "OK: Temel tablo satır sayıları değişmedi."
else
  echo "HATA: Satır sayıları farklı — yedek: $BACKUP_DIR/pg_${PG_DB}_full_${TS}.sql.gz"
  diff "$COUNT_BEFORE" "$COUNT_AFTER" || true
  exit 1
fi

echo "==> Health"
curl -sS http://127.0.0.1/health || true
echo ""
echo "Tamam. Yedek: $BACKUP_DIR/pg_${PG_DB}_full_${TS}.sql.gz"
