#!/usr/bin/env bash
# VM (sps-server-v2) üzerinde: kokpitim_merge_target = Alembic head şema + prod data-only dump.
# Önkoşul: /tmp/kokpitim_git_head.tgz tam (git archive ~343MB), dump ve audit SQL yüklü.
#
# Yerelden (PowerShell örnek):
#   gcloud compute scp backups/merge_prep/kokpitim_git_head.tgz sps-server-v2:/tmp/ --zone=europe-west3-c
#   gcloud compute scp backups/merge_prep/kokpitim_vm_data_only_20260410.dump sps-server-v2:/tmp/ --zone=europe-west3-c
#   gcloud compute scp scripts/ops/prod_stabilize_audit_sequence.sql sps-server-v2:/tmp/ --zone=europe-west3-c
#
# VM:
#   sed -i 's/\r$//' scripts/ops/vm_merge_kokpitim_target.sh   # CRLF ise
#   chmod +x scripts/ops/vm_merge_kokpitim_target.sh
#   sudo ./scripts/ops/vm_merge_kokpitim_target.sh
#
# Not: SQLALCHEMY_DATABASE_URI, çalışan sps-web imajından okunur; yalnızca son /kokpitim_db yolu hedef DB ile değiştirilir.

set -euo pipefail

SRC_TGZ="${SRC_TGZ:-/tmp/kokpitim_git_head.tgz}"
DUMP="${DUMP:-/tmp/kokpitim_vm_data_only_20260410.dump}"
AUDIT_SQL="${AUDIT_SQL:-/tmp/prod_stabilize_audit_sequence.sql}"
DEST_DIR="${DEST_DIR:-/tmp/kokpitim_merge_src}"
TARGET_DB="${TARGET_DB:-kokpitim_merge_target}"
CONTAINER="${CONTAINER:-sps-web}"
EXPECTED_MIN_TGZ_BYTES="${EXPECTED_MIN_TGZ_BYTES:-300000000}"

if [[ ! -f "$SRC_TGZ" ]]; then
  echo "HATA: $SRC_TGZ yok"
  exit 1
fi
_sz=$(wc -c <"$SRC_TGZ")
if [[ "$_sz" -lt "$EXPECTED_MIN_TGZ_BYTES" ]]; then
  echo "HATA: $SRC_TGZ çok küçük (${_sz} bayt). SCP yarım kalmış olabilir (tam arşiv ~343MB)."
  exit 1
fi
if [[ ! -f "$DUMP" ]]; then
  echo "HATA: $DUMP yok"
  exit 1
fi
if [[ ! -f "$AUDIT_SQL" ]]; then
  echo "HATA: $AUDIT_SQL yok"
  exit 1
fi

sudo rm -rf "$DEST_DIR"
mkdir -p "$DEST_DIR"
tar -xzf "$SRC_TGZ" -C "$DEST_DIR"

if [[ -n "${SQLALCHEMY_DATABASE_URI_MERGE:-}" ]]; then
  MERGE_URI="$SQLALCHEMY_DATABASE_URI_MERGE"
else
  _line=$(sudo docker inspect "$CONTAINER" --format '{{range .Config.Env}}{{println .}}{{end}}' | grep '^SQLALCHEMY_DATABASE_URI=' || true)
  if [[ -z "$_line" ]]; then
    echo "HATA: $CONTAINER içinde SQLALCHEMY_DATABASE_URI yok. Export: SQLALCHEMY_DATABASE_URI_MERGE=..."
    exit 1
  fi
  BASE_URI="${_line#SQLALCHEMY_DATABASE_URI=}"
  MERGE_URI=$(printf '%s' "$BASE_URI" | sed 's|/kokpitim_db$|/'"${TARGET_DB}"'|')
  if [[ "$MERGE_URI" == "$BASE_URI" ]]; then
    echo "HATA: URI sonu /kokpitim_db değil. Export: SQLALCHEMY_DATABASE_URI_MERGE=postgresql+psycopg2://.../${TARGET_DB}"
    exit 1
  fi
fi

echo "==> Alembic upgrade -> ${TARGET_DB} (python:3.11 one-shot)"
sudo docker run --rm \
  --add-host=host.docker.internal:host-gateway \
  -v "${DEST_DIR}:/app" -w /app \
  -e "SQLALCHEMY_DATABASE_URI=${MERGE_URI}" \
  -e "SECRET_KEY=${SECRET_KEY:-merge-migration-placeholder-not-for-runtime}" \
  python:3.11-slim-bookworm \
  bash -c 'set -euo pipefail
    apt-get update -qq
    DEBIAN_FRONTEND=noninteractive apt-get install -qq -y gcc libpq-dev >/dev/null
    pip install --no-cache-dir -q -r requirements.txt
    python scripts/run_db_upgrade.py'

echo "==> pg_restore öncesi: migration’ın seed’i ile dump çakışmasın"
sudo -u postgres psql -d "$TARGET_DB" -v ON_ERROR_STOP=1 -c 'DELETE FROM system_settings;'

# TOC (-L): dump’taki eski satırları at. pg_restore’u postgres süper kullanıcı ile koştur
# (kokpitim_user ile ENABLE TRIGGER hataları oluşmaz; host PG14 yeterli).
RESTORE_LIST=/tmp/kokpitim_merge_restore.list
echo "==> TOC listesi (alembic_version + task_dependency çıkar)"
pg_restore -l "$DUMP" | grep -v 'TABLE DATA public alembic_version ' | grep -v 'TABLE DATA public task_dependency ' | grep -v 'SEQUENCE SET public task_dependency_id_seq ' > "$RESTORE_LIST"

echo "==> pg_restore --data-only (postgres süper kullanıcı, --disable-triggers)"
set +e
sudo -u postgres pg_restore -d "$TARGET_DB" -L "$RESTORE_LIST" --data-only --no-owner --disable-triggers -v "$DUMP"
_pg_rc=$?
set -e
if [[ "$_pg_rc" -gt 1 ]]; then
  echo "HATA: pg_restore cikis kodu ${_pg_rc}"
  exit "$_pg_rc"
fi
if [[ "$_pg_rc" -eq 1 ]]; then
  echo "UYARI: pg_restore cikis 1 — kalan hata satırlarını logda kontrol edin."
fi

echo "==> audit_logs sequence"
sudo -u postgres psql -d "$TARGET_DB" -v ON_ERROR_STOP=1 -f "$AUDIT_SQL"

echo "OK: ${TARGET_DB} birleştirme adımları tamam. KMF (tenant 16) sayımlarını TASK-084 ile karşılaştırın."
