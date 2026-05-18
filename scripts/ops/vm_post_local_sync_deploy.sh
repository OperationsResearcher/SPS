#!/usr/bin/env bash
# VM: yerel arşiv açıldıktan sonra — git pull YOK; pg_dump + Docker + Alembic.
set -euo pipefail

APP_DIR="${APP_DIR:-/home/kokpitim.com/public_html}"
BACKUP_DIR="$APP_DIR/backups"
CONTAINER="${CONTAINER:-sps-web}"
IMAGE="${IMAGE:-sps_web_final:latest}"
PG_DB="${PG_DATABASE:-kokpitim_db}"
TS="$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"

echo "==> 1/4 PostgreSQL tam yedek (gzip)"
sudo -u postgres pg_dump "$PG_DB" | gzip -c >"$BACKUP_DIR/pg_${PG_DB}_post_sync_${TS}.sql.gz"
ls -la "$BACKUP_DIR/pg_${PG_DB}_post_sync_${TS}.sql.gz"

echo "==> 2/4 Docker image + container"
cd "$APP_DIR"
if [ ! -f "$APP_DIR/.env" ]; then
  echo "HATA: $APP_DIR/.env yok."
  exit 1
fi
sudo docker build -t "$IMAGE" .
sudo docker stop "$CONTAINER" 2>/dev/null || true
sudo docker rm "$CONTAINER" 2>/dev/null || true
DOCKER_ENV=(--env-file "$APP_DIR/.env")
if [ -f "$APP_DIR/.env.postgres" ]; then
  DOCKER_ENV+=(--env-file "$APP_DIR/.env.postgres")
fi
sudo docker run -d --name "$CONTAINER" -p 80:5000 \
  --add-host=host.docker.internal:host-gateway \
  -v /home/kokpitim.com/public_html/instance:/app/instance \
  "${DOCKER_ENV[@]}" \
  "$IMAGE"

echo "==> 3/4 Alembic upgrade"
sleep 8
sudo docker exec "$CONTAINER" bash -lc 'cd /app && python3 scripts/run_db_upgrade.py'

echo "==> 4/4 Health"
curl -sS http://127.0.0.1/health || true
echo ""
echo "Tamam. DB yedek: $BACKUP_DIR/pg_${PG_DB}_post_sync_${TS}.sql.gz"
