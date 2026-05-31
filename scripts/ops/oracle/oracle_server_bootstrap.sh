#!/usr/bin/env bash
# Oracle kokpitim-v2: Faz 1-4 (PG + restore + docker + nginx hazirlik)
# Onkosul: /tmp/kokpitim_deploy/ altinda dump, instance.tar.gz, .env, app (git clone veya tar)
set -euo pipefail

DEPLOY_DIR="/tmp/kokpitim_deploy"
APP_DIR="/opt/kokpitim/app"
INST_DIR="/opt/kokpitim/instance"
ENV_FILE="/opt/kokpitim/.env"
CONTAINER="kokpitim-web"
IMAGE="kokpitim_web:latest"
PG_DB="kokpitim_db"
GIT_REPO="${GIT_REPO:-https://github.com/OperationsResearcher/SPS.git}"
GIT_REF="${GIT_REF:-main}"

echo "==> 0/8 Disk (docker cache — calisan containerlara dokunulmaz)"
docker builder prune -af 2>/dev/null || true
docker image prune -af 2>/dev/null || true
df -h / | tail -1

echo "==> 1/8 Dizinler"
sudo mkdir -p /opt/kokpitim/{app,instance,backups,logs}
sudo chown -R ubuntu:ubuntu /opt/kokpitim

echo "==> 2/8 PostgreSQL"
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='kokpitim_user'" | grep -q 1; then
  PW=$(grep -E '^KOKPITIM_DB_PASSWORD=' "$DEPLOY_DIR/oracle_db.env" 2>/dev/null | cut -d= -f2- || echo 'CHANGE_ME')
  sudo -u postgres psql -c "CREATE USER kokpitim_user WITH PASSWORD '${PW}';"
fi
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='${PG_DB}'" | grep -q 1 || \
  sudo -u postgres createdb -O kokpitim_user "$PG_DB"

DUMP=$(ls -1 "$DEPLOY_DIR"/kokpitim_db*.dump 2>/dev/null | head -1)
if [ -z "$DUMP" ]; then
  echo "HATA: $DEPLOY_DIR icinde kokpitim_db*.dump yok"
  exit 1
fi
echo "==> 3/8 pg_restore: $DUMP"
sudo -u postgres pg_restore -d "$PG_DB" --clean --if-exists --no-owner --role=kokpitim_user "$DUMP" 2>/dev/null || \
  sudo -u postgres pg_restore -d "$PG_DB" --no-owner "$DUMP"
sudo -u postgres psql -d "$PG_DB" -At -c "
SELECT 'tenants|'||count(*) FROM tenants
UNION ALL SELECT 'users|'||count(*) FROM users
UNION ALL SELECT 'kpi_data|'||count(*) FROM kpi_data;"

echo "==> 4/8 instance/"
if [ -f "$DEPLOY_DIR/instance.tar.gz" ]; then
  rm -rf "$INST_DIR"/*
  tar xzf "$DEPLOY_DIR/instance.tar.gz" -C /opt/kokpitim --strip-components=1 2>/dev/null || \
    tar xzf "$DEPLOY_DIR/instance.tar.gz" -C "$INST_DIR" --strip-components=1
fi
chown -R ubuntu:ubuntu "$INST_DIR"

echo "==> 5/8 Uygulama kodu (git)"
if [ ! -d "$APP_DIR/.git" ]; then
  git clone "$GIT_REPO" "$APP_DIR"
fi
cd "$APP_DIR"
git fetch origin 2>/dev/null || true
git checkout "$GIT_REF" 2>/dev/null || git checkout main || true

echo "==> 6/8 .env"
cp "$DEPLOY_DIR/.env" "$ENV_FILE"
# Oracle: container -> host PG
sed -i 's|host.docker.internal|host.docker.internal|g' "$ENV_FILE"
grep -q '^FLASK_ENV=' "$ENV_FILE" || echo 'FLASK_ENV=production' >> "$ENV_FILE"
grep -q '^TRUST_PROXY=' "$ENV_FILE" || echo 'TRUST_PROXY=1' >> "$ENV_FILE"
grep -q '^RATELIMIT_STORAGE_URL=' "$ENV_FILE" || echo 'RATELIMIT_STORAGE_URL=memory://' >> "$ENV_FILE"

echo "==> 7/8 Docker build + run (port 8088)"
cd "$APP_DIR"
docker build -t "$IMAGE" .
docker stop "$CONTAINER" 2>/dev/null || true
docker rm "$CONTAINER" 2>/dev/null || true
sed -i 's/host.docker.internal/127.0.0.1/' "$ENV_FILE"
docker run -d --name "$CONTAINER" --restart unless-stopped \
  --network host \
  -v "$INST_DIR:/app/instance" \
  --env-file "$ENV_FILE" \
  -e FLASK_ENV=production \
  -e TRUST_PROXY=1 \
  "$IMAGE"
sleep 8
docker exec "$CONTAINER" bash -lc 'cd /app && python3 scripts/run_db_upgrade.py' || true
curl -sS http://127.0.0.1:8088/health || echo "health bekleniyor..."

echo "==> 8/8 nginx (www) — manuel dogrulama"
NGX="/etc/nginx/sites-available/www.kokpitim.com"
if [ ! -f "$NGX" ]; then
  sudo tee "$NGX" > /dev/null <<'NGXEOF'
server {
    listen 80;
    server_name www.kokpitim.com kokpitim.com;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGXEOF
  sudo ln -sf "$NGX" /etc/nginx/sites-enabled/www.kokpitim.com
  sudo nginx -t && sudo systemctl reload nginx
  echo "NOT: certbot icin: sudo certbot --nginx -d www.kokpitim.com -d kokpitim.com"
fi
echo "BOOTSTRAP TAMAM"
