#!/usr/bin/env bash
# 4 katman kontrolü — Yayın (ve isteğe bağlı yerel SHA karşılaştırması)
# Kullanım (sunucuda):
#   bash scripts/ops/oracle/dort_katman_kontrol.sh [BEKLENEN_MAIN_SHA]
# Yerel orchestrator beklenen SHA'yı argüman olarak geçirir.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib_yayin_common.sh
source "${SCRIPT_DIR}/lib_yayin_common.sh"

APP="${APP_DIR:-/opt/kokpitim/app}"
DB="${PG_DATABASE:-kokpitim_db}"
EXPECTED_SHA="${1:-}"

echo "============================================================"
echo "  4 KATMAN KONTROL — Yayın"
echo "============================================================"

echo ""
echo "--- 1) KOD ---"
if [[ ! -d "$APP/.git" ]]; then
  echo "HATA: $APP git checkout değil"
  print_fallback "kod" "$APP/.git yok"
  exit 2
fi
CUR=$(sudo git -c safe.directory="$APP" -C "$APP" rev-parse HEAD)
CUR_MSG=$(sudo git -c safe.directory="$APP" -C "$APP" log -1 --oneline)
echo "Yayın HEAD : $CUR"
echo "            $CUR_MSG"
if [[ -n "$EXPECTED_SHA" ]]; then
  if [[ "$CUR" == "$EXPECTED_SHA"* ]] || [[ "$EXPECTED_SHA" == "$CUR"* ]]; then
    echo "Beklenen  : $EXPECTED_SHA — EŞİT"
  else
    echo "Beklenen  : $EXPECTED_SHA — FARKLI (deploy pull gerekli)"
  fi
fi

echo ""
echo "--- 2) ŞEMA ---"
ALEMBIC=$(psql_pg -d "$DB" -At -c 'SELECT version_num FROM alembic_version;' || echo 'YOK')
DESC_TYPE=$(psql_pg -d "$DB" -At -c "SELECT data_type FROM information_schema.columns WHERE table_name='system_cards' AND column_name='description';" || echo '?')
echo "alembic_version : $ALEMBIC"
echo "system_cards.description tipi : $DESC_TYPE"
if [[ "$DESC_TYPE" == "character varying" ]]; then
  echo "UYARI: description hâlâ varchar — Text migration (391945351814) + seed SIRASI zorunlu"
fi

echo ""
echo "--- 3) VERİ (sayımlar) ---"
for t in tenants users processes process_kpis kpi_data process_activities strategies sub_strategies project task system_cards; do
  c=$(psql_pg -d "$DB" -At -c "SELECT count(*) FROM ${t};" || echo '?')
  echo "${t}|${c}"
done
AVG=$(psql_pg -d "$DB" -At -c "SELECT ROUND(AVG(LENGTH(COALESCE(description,'')))) FROM system_cards;" || echo '?')
echo "system_cards ort.krk|${AVG}"

echo ""
echo "--- 4) TEK-SEFERLİK (ipucu) ---"
echo "Seed kaydı otoritesi: docs/kontrol/seed_calistirma_kaydi.md"
echo "Kart seed script: scripts/seed_card_descriptions.py"
if [[ "${AVG}" =~ ^[0-9]+$ ]] && [[ "$AVG" -lt 200 ]]; then
  echo "UYARI: açıklama ort. ${AVG} < 200 — seed_card_descriptions muhtemelen eksik/eski"
fi

echo ""
echo "--- HEALTH ---"
echo "yayin:5000 -> $(health_code http://127.0.0.1:5000/health)"
echo "test:5050  -> $(health_code http://127.0.0.1:5050/health)"
echo "(nginx :80 /health 404 normal olabilir — :5000 kullan)"
echo "============================================================"
