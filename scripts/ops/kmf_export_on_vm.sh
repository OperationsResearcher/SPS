#!/usr/bin/env bash
# KMF (Kayseri Model Fabrika) tenant CSV slice + counts — VM'de postgres kullanıcısı ile çalıştırın:
#   sudo cp kmf_export_on_vm.sh /tmp/ && sudo chown postgres:postgres /tmp/kmf_export_on_vm.sh
#   sudo -u postgres bash /tmp/kmf_export_on_vm.sh
set -euo pipefail
DB="${1:-kokpitim_db}"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT="/var/lib/postgresql/kmf_tenant_backup_${STAMP}"
mkdir -p "$OUT"

run_psql() { psql -d "$DB" -v ON_ERROR_STOP=1 "$@"; }

TID="$(run_psql -At -c "
  SELECT id FROM tenants
  WHERE name ILIKE '%Kayseri%Model%Fabrika%'
     OR name ILIKE '%Kayseri Model Fabrika%'
     OR (name ILIKE '%Kayseri%' AND name ILIKE '%Model%' AND name ILIKE '%Fabrika%')
  ORDER BY id
  LIMIT 1;
")"

if [[ -z "${TID}" ]]; then
  echo "ERROR: KMF tenant bulunamadı (tenants isim eşleşmesi)." >&2
  exit 1
fi

TNAME="$(run_psql -At -c "SELECT name FROM tenants WHERE id = ${TID};")"
printf 'kmf_tenant_id=%s\nkmf_tenant_name=%s\n' "${TID}" "${TNAME}" > "${OUT}/meta.txt"

HAS_DEL="$(run_psql -At -c "
  SELECT count(*) FROM information_schema.columns
  WHERE table_schema='public' AND table_name='kpi_data' AND column_name='deleted_at';
")"

if [[ "${HAS_DEL}" == "1" ]]; then
  run_psql -c "
SELECT
  ${TID} AS kmf_tenant_id,
  (SELECT name FROM tenants WHERE id = ${TID}) AS kmf_tenant_name,
  (SELECT count(*) FROM users u WHERE u.tenant_id = ${TID}) AS kullanici_sayisi,
  (SELECT count(*) FROM processes pr WHERE pr.tenant_id = ${TID}) AS surec_sayisi,
  (SELECT count(*) FROM process_kpis pk JOIN processes pr ON pr.id = pk.process_id WHERE pr.tenant_id = ${TID}) AS pg_sayisi,
  (SELECT count(*) FROM kpi_data kd
     JOIN process_kpis pk ON pk.id = kd.process_kpi_id
     JOIN processes pr ON pr.id = pk.process_id
     WHERE pr.tenant_id = ${TID} AND kd.deleted_at IS NULL) AS pgv_sayisi;
" | tee "${OUT}/counts.txt"
else
  run_psql -c "
SELECT
  ${TID} AS kmf_tenant_id,
  (SELECT name FROM tenants WHERE id = ${TID}) AS kmf_tenant_name,
  (SELECT count(*) FROM users u WHERE u.tenant_id = ${TID}) AS kullanici_sayisi,
  (SELECT count(*) FROM processes pr WHERE pr.tenant_id = ${TID}) AS surec_sayisi,
  (SELECT count(*) FROM process_kpis pk JOIN processes pr ON pr.id = pk.process_id WHERE pr.tenant_id = ${TID}) AS pg_sayisi,
  (SELECT count(*) FROM kpi_data kd
     JOIN process_kpis pk ON pk.id = kd.process_kpi_id
     JOIN processes pr ON pr.id = pk.process_id
     WHERE pr.tenant_id = ${TID}) AS pgv_sayisi;
" | tee "${OUT}/counts.txt"
fi

run_psql -c "\\copy (SELECT * FROM tenants WHERE id = ${TID}) TO '${OUT}/tenants.csv' WITH CSV HEADER"
run_psql -c "\\copy (SELECT * FROM users WHERE tenant_id = ${TID}) TO '${OUT}/users.csv' WITH CSV HEADER"
run_psql -c "\\copy (SELECT * FROM processes WHERE tenant_id = ${TID}) TO '${OUT}/processes.csv' WITH CSV HEADER"
run_psql -c "\\copy (SELECT pk.* FROM process_kpis pk JOIN processes pr ON pr.id = pk.process_id WHERE pr.tenant_id = ${TID}) TO '${OUT}/process_kpis.csv' WITH CSV HEADER"
if [[ "${HAS_DEL}" == "1" ]]; then
  run_psql -c "\\copy (SELECT kd.* FROM kpi_data kd JOIN process_kpis pk ON pk.id = kd.process_kpi_id JOIN processes pr ON pr.id = pk.process_id WHERE pr.tenant_id = ${TID} AND kd.deleted_at IS NULL) TO '${OUT}/kpi_data.csv' WITH CSV HEADER"
else
  run_psql -c "\\copy (SELECT kd.* FROM kpi_data kd JOIN process_kpis pk ON pk.id = kd.process_kpi_id JOIN processes pr ON pr.id = pk.process_id WHERE pr.tenant_id = ${TID}) TO '${OUT}/kpi_data.csv' WITH CSV HEADER"
fi

tar czf "${OUT}.tar.gz" -C "$(dirname "$OUT")" "$(basename "$OUT")"
echo "OK: ${OUT}.tar.gz"
