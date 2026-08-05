#!/usr/bin/env bash
# Yayın: kart açıklama seed (+ isteğe bağlı ek seed'ler)
# ÖNKOŞUL: Text migration uygulanmış olmalı (description tipi = text)
# Kullanım:
#   sudo bash scripts/ops/oracle/yayin_seed_kart.sh
#   EXTRA_SEEDS="scripts/seed_foo.py" sudo bash .../yayin_seed_kart.sh
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib_yayin_common.sh
source "${SCRIPT_DIR}/lib_yayin_common.sh"

DB="${PG_DATABASE:-kokpitim_db}"
CONTAINER="${CONTAINER:-kokpitim-web}"

echo "==> [yayin_seed] description tipi kontrol"
DESC_TYPE=$(psql_pg -d "$DB" -At -c "SELECT data_type FROM information_schema.columns WHERE table_name='system_cards' AND column_name='description';")
echo "description=$DESC_TYPE"
if [[ "$DESC_TYPE" != "text" ]]; then
  print_fallback "seed-schema" "description=$DESC_TYPE (text değil). Önce alembic upgrade (391945351814). Seed ÇALIŞTIRILMADI."
  exit 7
fi

echo "==> [yayin_seed] KONTROL"
sudo docker exec "$CONTAINER" bash -lc 'cd /app && python3 scripts/seed_card_descriptions.py' | tee /tmp/seed_kart_kontrol.txt | tail -25

echo "==> [yayin_seed] UYGULA"
sudo docker exec "$CONTAINER" bash -lc 'cd /app && python3 scripts/seed_card_descriptions.py --calistir' | tee /tmp/seed_kart_uygula.txt | tail -25

# İsteğe bağlı ek seed'ler (boşlukla ayrılmış)
if [[ -n "${EXTRA_SEEDS:-}" ]]; then
  for s in $EXTRA_SEEDS; do
    echo "==> [yayin_seed] ekstra: $s"
    sudo docker exec "$CONTAINER" bash -lc "cd /app && python3 $s" || {
      print_fallback "extra-seed" "$s başarısız"
      exit 8
    }
  done
fi

echo "==> [yayin_seed] doğrula"
psql_pg -d "$DB" -At -c "SELECT version_num FROM alembic_version;"
AVG=$(psql_pg -d "$DB" -At -c "SELECT COUNT(*), ROUND(AVG(LENGTH(COALESCE(description,'')))) FROM system_cards;")
echo "cards_avg|$AVG"
HC=$(health_code http://127.0.0.1:5000/health)
echo "yayin_health:$HC"
PH=$(health_code https://www.kokpitim.com/health)
echo "public_health:$PH"
if [[ "$HC" != "200" ]]; then
  print_fallback "seed-health" "Yayın :5000 health=$HC"
  exit 6
fi
echo "TAMAM yayin_seed"
