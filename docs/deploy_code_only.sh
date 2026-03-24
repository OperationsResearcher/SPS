#!/usr/bin/env bash
set -Eeuo pipefail

# Kokpitim - CODE ONLY deploy script
# - DB'ye dokunmaz
# - VM'de yedek alir
# - Git pull + Docker build + container restart yapar
#
# Kullanim:
#   chmod +x docs/deploy_code_only.sh
#   ./docs/deploy_code_only.sh

APP_DIR="/home/kokpitim.com/public_html"
CONTAINER_NAME="sps-web"
IMAGE_NAME="sps_web_final:latest"
BACKUP_DIR="/home/kokpitim.com/backups"
BRANCH="${BRANCH:-main}"
TS="$(date +%Y%m%d_%H%M%S)"

echo "==> [CODE ONLY] Deploy basladi: $TS"
cd "$APP_DIR"
mkdir -p "$BACKUP_DIR"

echo "==> Yedekler aliniyor (DB + kod snapshot)..."
if sudo docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
  sudo docker cp "$CONTAINER_NAME:/app/instance/kokpitim.db" \
    "$BACKUP_DIR/kokpitim_container_${TS}.db" || true
fi
cp -f "$APP_DIR/instance/kokpitim.db" \
  "$BACKUP_DIR/kokpitim_host_${TS}.db" || true
tar -czf "$BACKUP_DIR/code_${TS}.tar.gz" . || true

echo "==> Kod guncelleniyor (branch: $BRANCH)..."
sudo git pull origin "$BRANCH"

echo "==> Docker image build..."
sudo docker build -t "$IMAGE_NAME" .

echo "==> Container yeniden baslatiliyor..."
if sudo docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
  sudo docker stop "$CONTAINER_NAME" || true
  sudo docker rm "$CONTAINER_NAME" || true
fi
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
echo "OK: Deploy tamamlandi (DB korunmustur)."

