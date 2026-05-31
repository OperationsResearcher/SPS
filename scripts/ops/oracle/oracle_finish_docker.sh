#!/usr/bin/env bash
set -euo pipefail
cd /opt/kokpitim/app
echo "==> docker build"
docker build -t kokpitim_web:latest .
docker stop kokpitim-web 2>/dev/null || true
docker rm kokpitim-web 2>/dev/null || true
docker run -d --name kokpitim-web --restart unless-stopped \
  -p 127.0.0.1:8088:5000 \
  --add-host=host.docker.internal:host-gateway \
  -v /opt/kokpitim/instance:/app/instance \
  --env-file /opt/kokpitim/.env \
  -e FLASK_ENV=production \
  -e TRUST_PROXY=1 \
  kokpitim_web:latest
sleep 12
docker exec kokpitim-web bash -lc 'cd /app && python3 scripts/run_db_upgrade.py' || true
curl -sS http://127.0.0.1:8088/health
echo DONE
