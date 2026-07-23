#!/usr/bin/env bash
# Test ortamı SIFIRDAN kurulum (bağlayıcı §0.6)
# Kod: Yayın git fetch + archive (büyük scp YOK)
# DB : /tmp/kokpitim_db_local.sql.gz (yerelden scp edilmiş gzip plain dump)
#
# Kullanım (sunucuda):
#   sudo bash scripts/ops/oracle/test_sifirdan.sh
#   DUMP=/tmp/foo.sql.gz sudo bash .../test_sifirdan.sh
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib_yayin_common.sh
source "${SCRIPT_DIR}/lib_yayin_common.sh"

TS=$(date +%Y%m%d_%H%M%S)
APP=/opt/kokpitim-test/app
BK=/opt/kokpitim-test/backups
YAPP=/opt/kokpitim/app
DUMP="${DUMP:-/tmp/kokpitim_db_local.sql.gz}"
TEST_DB=kokpitim_test_db
TEST_USER=kokpitim_test_user

mkdir -p "$BK" /opt/kokpitim-test/instance /opt/kokpitim-test/logs

echo "==> [test_sifirdan] 0 env yedek"
sudo cp "$APP/.env" "$BK/app_env_yedek_${TS}" 2>/dev/null || true
sudo cp /opt/kokpitim-test/.env "$BK/env_yedek_${TS}" 2>/dev/null || true

if [[ ! -f "$DUMP" ]]; then
  print_fallback "test-dump" "Dump yok: $DUMP — yerelden gzip dump scp edilmeli"
  exit 3
fi

echo "==> [test_sifirdan] 1 container durdur"
sudo docker rm -f kokpitim-test-web 2>/dev/null || true

echo "==> [test_sifirdan] 2 fetch origin/main (Yayın checkout'a dokunmadan)"
if [[ ! -d "$YAPP/.git" ]]; then
  print_fallback "test-git" "$YAPP/.git yok — Yayın git checkout gerekli"
  exit 2
fi
sudo git -c safe.directory="$YAPP" -C "$YAPP" fetch origin main
MAIN_SHA=$(sudo git -c safe.directory="$YAPP" -C "$YAPP" rev-parse origin/main)
echo "origin/main=$MAIN_SHA"

echo "==> [test_sifirdan] 3 wipe + archive extract"
sudo rm -rf "$APP"
sudo mkdir -p "$APP"
sudo git -c safe.directory="$YAPP" -C "$YAPP" archive "$MAIN_SHA" | sudo tar x -C "$APP"

# .env geri koy
if [[ -f "$BK/app_env_yedek_${TS}" ]]; then
  sudo cp "$BK/app_env_yedek_${TS}" "$APP/.env"
elif [[ -f "$BK/env_yedek_${TS}" ]]; then
  sudo cp "$BK/env_yedek_${TS}" "$APP/.env"
else
  print_fallback "test-env" ".env yedeği yok — ENCRYPTION_KEY kaybı riski"
  exit 4
fi
sudo test -f /opt/kokpitim-test/.env || sudo cp "$APP/.env" /opt/kokpitim-test/.env

echo "==> [test_sifirdan] 4 drop/create DB"
psql_pg -v ON_ERROR_STOP=1 <<SQL
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
  WHERE datname='${TEST_DB}' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS ${TEST_DB};
CREATE DATABASE ${TEST_DB} OWNER ${TEST_USER};
SQL

echo "==> [test_sifirdan] 5 restore (PG18 transaction_timeout + \\restrict temizle)"
# ON_ERROR_STOP=0: kozmetik satırlar; ownership sonra düzeltilir
gunzip -c "$DUMP" \
  | grep -v 'transaction_timeout' \
  | grep -vE '^\\restrict|^\\unrestrict' \
  | psql_pg -d "$TEST_DB" -v ON_ERROR_STOP=0 > "$BK/restore_${TS}.log" 2>&1 || true

fix_table_owner "$TEST_DB" "$TEST_USER"

TENANTS=$(psql_pg -d "$TEST_DB" -At -c 'SELECT count(*) FROM tenants;' || echo 0)
CARDS=$(psql_pg -d "$TEST_DB" -At -c 'SELECT count(*) FROM system_cards;' || echo 0)
if [[ "$TENANTS" == "0" || "$CARDS" == "0" ]]; then
  print_fallback "test-restore" "Restore boş görünüyor (tenants=$TENANTS cards=$CARDS). Log: $BK/restore_${TS}.log"
  exit 5
fi

echo "==> [test_sifirdan] 6 docker build + run (PORT=5050)"
cd "$APP"
sudo docker build -t kokpitim_test:latest -f Dockerfile .
sudo docker rm -f kokpitim-test-web 2>/dev/null || true
sudo docker run -d --name kokpitim-test-web \
  --network host --restart unless-stopped \
  -v "$APP/.env:/app/.env:ro" \
  -v /opt/kokpitim-test/instance:/app/instance \
  -v /opt/kokpitim-test/logs:/app/logs \
  -e PORT=5050 -e FLASK_ENV=production \
  kokpitim_test:latest

echo "==> [test_sifirdan] 7 health + doğrula"
sleep 12
HC=$(health_code http://127.0.0.1:5050/health)
echo "test_health:$HC"
if [[ "$HC" != "200" ]]; then
  print_fallback "test-health" "Health $HC — docker logs kokpitim-test-web"
  sudo docker logs kokpitim-test-web 2>&1 | tail -40 || true
  exit 6
fi

psql_pg -d "$TEST_DB" -At -c "SELECT 'tenants|'||count(*) FROM tenants UNION ALL SELECT 'users|'||count(*) FROM users UNION ALL SELECT 'system_cards|'||count(*) FROM system_cards;"
psql_pg -d "$TEST_DB" -At -c "SELECT version_num FROM alembic_version;"
AVG=$(psql_pg -d "$TEST_DB" -At -c "SELECT ROUND(AVG(LENGTH(COALESCE(description,'')))) FROM system_cards;")
echo "desc_avg|$AVG"
sudo docker exec kokpitim-test-web test -f /app/scripts/seed_card_descriptions.py && echo "seed_script:OK"

echo "TAMAM test_sifirdan code=${MAIN_SHA} ts=${TS}"
