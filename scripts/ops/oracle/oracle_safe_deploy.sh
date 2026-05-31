#!/usr/bin/env bash
# Oracle VM (kokpitim-v2): kod + Alembic — veri silmez.
# Onkosul: /opt/kokpitim/app icinde git pull yapilmis veya bu betik pull yapar.
# Terim: "VM" = Oracle; GCP icin scripts/vm_safe_deploy.sh (legacy).
set -euo pipefail

APP_DIR="/opt/kokpitim/app"
ENV_FILE="/opt/kokpitim/.env"
INST_DIR="/opt/kokpitim/instance"
BACKUP_DIR="/opt/kokpitim/backups"
CONTAINER="kokpitim-web"
IMAGE="kokpitim_web:latest"
PG_DB="${PG_DATABASE:-kokpitim_db}"
TS="$( date +%Y%m%d_%H%M%S )"

mkdir -p "$BACKUP_DIR"

echo "==> 1/6 PostgreSQL tam yedek (gzip)"
sudo -u postgres pg_dump "$PG_DB" | gzip -c > "$BACKUP_DIR/pg_${PG_DB}_full_${TS}.sql.gz"
ls -la "$BACKUP_DIR/pg_${PG_DB}_full_${TS}.sql.gz"

echo "==> 2/6 Temel tablo satir sayilari (once)"
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
git pull origin main

echo "==> 4/6 Docker image + container (host network)"
if [ ! -f "$ENV_FILE" ]; then
  echo "HATA: $ENV_FILE yok."
  exit 1
fi
if ! grep -qE '^[[:space:]]*SQLALCHEMY_DATABASE_URI=.*postgresql' "$ENV_FILE"; then
  echo "HATA: $ENV_FILE icinde SQLALCHEMY_DATABASE_URI (postgresql) gerekli."
  exit 1
fi

docker build -t "$IMAGE" .
docker stop "$CONTAINER" 2>/dev/null || true
docker rm "$CONTAINER" 2>/dev/null || true
# PG sadece 127.0.0.1 — host.docker.internal yerine 127.0.0.1
sed -i.bak 's/host\.docker\.internal/127.0.0.1/g' "$ENV_FILE" || true
docker run -d --name "$CONTAINER" --restart unless-stopped \
  --network host \
  -v "$INST_DIR:/app/instance" \
  --env-file "$ENV_FILE" \
  -e FLASK_ENV=production \
  -e TRUST_PROXY=1 \
  "$IMAGE"

echo "==> 5/6 Alembic upgrade"
sleep 5
docker exec "$CONTAINER" bash -lc 'cd /app && python3 scripts/run_db_upgrade.py'

echo "==> 6/6 Satir sayilari (sonra)"
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
  echo "OK: Temel tablo satir sayilari degismedi."
else
  echo "HATA: Satir sayilari farkli — yedek: $BACKUP_DIR/pg_${PG_DB}_full_${TS}.sql.gz"
  diff "$COUNT_BEFORE" "$COUNT_AFTER" || true
  exit 1
fi

echo "==> Health"
curl -sS http://127.0.0.1/health || curl -sS http://127.0.0.1:5000/health || true
echo ""
echo "Tamam. Yedek: $BACKUP_DIR/pg_${PG_DB}_full_${TS}.sql.gz"
