#!/usr/bin/env bash
set -euo pipefail
PW='MfGMfG__46604660'
sudo -u postgres psql -c "ALTER USER kokpitim_user WITH PASSWORD '${PW}';"
sudo -u postgres psql -d kokpitim_db -c "GRANT ALL ON SCHEMA public TO kokpitim_user;"
PGPASSWORD="$PW" psql -h 127.0.0.1 -U kokpitim_user -d kokpitim_db -c "SELECT count(*) AS tenants FROM tenants;"
docker restart kokpitim-web
sleep 6
curl -sS http://127.0.0.1:5000/health
echo
