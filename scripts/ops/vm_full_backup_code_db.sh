#!/usr/bin/env bash
# VM üzerinde çalıştır: tam PostgreSQL dökümü + public_html kod arşivi (backups klasörü hariç).
set -euo pipefail

APP_ROOT="/home/kokpitim.com"
CODE_DIR="${APP_ROOT}/public_html"
PG_DB="${PG_DATABASE:-kokpitim_db}"
TS="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="${APP_ROOT}/backup_manual_${TS}"

sudo mkdir -p "$OUT_DIR"
sudo chmod 755 "$OUT_DIR"

echo "==> DB dump: ${PG_DB} -> ${OUT_DIR}/kokpitim_db_full_${TS}.sql.gz"
sudo bash -c "sudo -u postgres pg_dump \"$PG_DB\" | gzip -c > \"$OUT_DIR/kokpitim_db_full_${TS}.sql.gz\""
sudo ls -lah "${OUT_DIR}/kokpitim_db_full_${TS}.sql.gz"

echo "==> Kod arşivi (public_html; backups alt klasörü hariç — DB ayrı alındı)"
sudo tar czpf "${OUT_DIR}/kokpitim_public_html_${TS}.tar.gz" \
  -C "$APP_ROOT" \
  --exclude='public_html/backups' \
  public_html
sudo ls -lah "${OUT_DIR}/kokpitim_public_html_${TS}.tar.gz"

echo "==> Özet"
sudo ls -la "$OUT_DIR"
echo "EXPORT_DIR=$OUT_DIR"
echo "$OUT_DIR" > /tmp/kokpitim_last_backup_dir.txt
echo "Kayıt: /tmp/kokpitim_last_backup_dir.txt"
