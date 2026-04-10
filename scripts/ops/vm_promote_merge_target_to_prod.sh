#!/usr/bin/env bash
# VM (sps-server-v2): kokpitim_merge_target -> canlı uygulama adı kokpitim_db (ALTER DATABASE RENAME).
#
# Önkoşullar:
#   - Bakım penceresi; kullanıcı trafiği yok.
#   - kokpitim_merge_target doğrulanmış (TASK-084 KMF vb.).
#   - TASK-083 snapshot / pg_dump yedeği hazır.
#
# Kullanım (yalnızca kasıtlı onayla):
#   export CONFIRM_PROD_DATABASE_PROMOTE=yes
#   sudo ./scripts/ops/vm_promote_merge_target_to_prod.sh
#
# Ortam:
#   MERGE_DB=kokpitim_merge_target  PROD_DB=kokpitim_db  CONTAINER=sps-web
#   STOP_CONTAINER=1 (varsayılan: konteyneri durdur/başlat)

set -euo pipefail

MERGE_DB="${MERGE_DB:-kokpitim_merge_target}"
PROD_DB="${PROD_DB:-kokpitim_db}"
CONTAINER="${CONTAINER:-sps-web}"
STOP_CONTAINER="${STOP_CONTAINER:-1}"

if [[ "${CONFIRM_PROD_DATABASE_PROMOTE:-}" != "yes" ]]; then
  echo "HATA: Canlı DB yeniden adlandırma için export edin: CONFIRM_PROD_DATABASE_PROMOTE=yes"
  exit 1
fi

TS="$(date +%Y%m%d_%H%M%S)"
BACKUP_NAME="${PROD_DB}_pre_promote_${TS}"

echo "==> Hedef: ${MERGE_DB} -> ${PROD_DB}; mevcut ${PROD_DB} -> ${BACKUP_NAME}"

for db in "$MERGE_DB" "$PROD_DB"; do
  if ! sudo -u postgres psql -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='${db}'" | grep -q 1; then
    echo "HATA: Veritabani yok: ${db}"
    exit 1
  fi
done

if [[ "$STOP_CONTAINER" == "1" ]] && sudo docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo "==> Docker stop: $CONTAINER"
  sudo docker stop "$CONTAINER"
fi

echo "==> Aktif baglantilari kes (hedef DB'ler)"
sudo -u postgres psql -d postgres -v ON_ERROR_STOP=1 -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname IN ('${PROD_DB}','${MERGE_DB}') AND pid <> pg_backend_pid();"

echo "==> RENAME: ${PROD_DB} -> ${BACKUP_NAME}"
sudo -u postgres psql -d postgres -v ON_ERROR_STOP=1 -c "ALTER DATABASE \"${PROD_DB}\" RENAME TO \"${BACKUP_NAME}\";"

echo "==> RENAME: ${MERGE_DB} -> ${PROD_DB}"
sudo -u postgres psql -d postgres -v ON_ERROR_STOP=1 -c "ALTER DATABASE \"${MERGE_DB}\" RENAME TO \"${PROD_DB}\";"

if [[ "$STOP_CONTAINER" == "1" ]]; then
  echo "==> Docker start: $CONTAINER"
  sudo docker start "$CONTAINER"
  sleep 2
  sudo docker logs "$CONTAINER" --tail 25 || true
fi

echo ""
echo "OK: Uygulama artik URI'deki ${PROD_DB} veritabanina bakiyor."
echo "Geri alma (manuel, baglantilari kestikten sonra):"
echo "  ALTER DATABASE \"${PROD_DB}\" RENAME TO \"${MERGE_DB}\";"
echo "  ALTER DATABASE \"${BACKUP_NAME}\" RENAME TO \"${PROD_DB}\";"
echo "Eski prod icerigi su an: ${BACKUP_NAME}"
