#!/usr/bin/env bash
set -Eeuo pipefail

# Kokpitim - CODE + DB REPLACE deploy script
# DANGER:
# - Bu script VM'deki DB'yi yerelden yuklenen DB ile DEGISTIRIR.
# - VM DB'de olan ama yeni DB'de olmayan kayitlar kaybolur.
#
# Kullanim:
# 1) Yerelden DB'yi VM'ye yukle:
#    gcloud compute scp C:\kokpitim\instance\kokpitim.db \
#      sps-server-v2:/tmp/kokpitim_new.db --zone=europe-west3-c
#
# 2) VM'de script calistir:
#    chmod +x docs/deploy_with_db_replace.sh
#    CONFIRM_DB_REPLACE=EVET ./docs/deploy_with_db_replace.sh /tmp/kokpitim_new.db
#
# Not: CONFIRM_DB_REPLACE degiskeni verilmezse script durur.

APP_DIR="/home/kokpitim.com/public_html"
CONTAINER_NAME="sps-web"
IMAGE_NAME="sps_web_final:latest"
BACKUP_DIR="/home/kokpitim.com/backups"
BRANCH="${BRANCH:-main}"
NEW_DB_PATH="${1:-/tmp/kokpitim_new.db}"
TS="$(date +%Y%m%d_%H%M%S)"

if [[ "${CONFIRM_DB_REPLACE:-}" != "EVET" ]]; then
  echo "HATA: DB replace onayi eksik. Calistirmak icin:"
  echo "CONFIRM_DB_REPLACE=EVET ./docs/deploy_with_db_replace.sh /tmp/kokpitim_new.db"
  exit 1
fi

if [[ ! -f "$NEW_DB_PATH" ]]; then
  echo "HATA: Yeni DB dosyasi bulunamadi: $NEW_DB_PATH"
  exit 1
fi

echo "==> [CODE + DB REPLACE] Deploy basladi: $TS"
cd "$APP_DIR"
mkdir -p "$BACKUP_DIR"

echo "==> Yedekler aliniyor (kritik)..."
if sudo docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
  sudo docker cp "$CONTAINER_NAME:/app/instance/kokpitim.db" \
    "$BACKUP_DIR/kokpitim_container_${TS}.db" || true
fi
cp -f "$APP_DIR/instance/kokpitim.db" \
  "$BACKUP_DIR/kokpitim_host_${TS}.db" || true
tar -czf "$BACKUP_DIR/code_${TS}.tar.gz" . || true

echo "==> Kod guncelleniyor (branch: $BRANCH)..."
sudo git pull origin "$BRANCH"

echo "==> Container durduruluyor..."
if sudo docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
  sudo docker stop "$CONTAINER_NAME" || true
  sudo docker rm "$CONTAINER_NAME" || true
fi

echo "==> DB replace yapiliyor..."
cp -f "$NEW_DB_PATH" "$APP_DIR/instance/kokpitim.db"
chmod 664 "$APP_DIR/instance/kokpitim.db" || true

echo "==> Docker image build..."
sudo docker build -t "$IMAGE_NAME" .

echo "==> Yeni container baslatiliyor..."
sudo docker run -d \
  --name "$CONTAINER_NAME" \
  -p 80:5000 \
  -v /home/kokpitim.com/public_html/instance:/app/instance \
  "$IMAGE_NAME"

echo "==> Log kontrol..."
sleep 3
sudo docker logs "$CONTAINER_NAME" --tail=80

echo "==> Health check..."
curl -fsS http://127.0.0.1/ >/dev/null
echo "OK: Deploy tamamlandi (DB REPLACE yapildi)."

