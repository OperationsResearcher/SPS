#!/usr/bin/env bash
# VM PostgreSQL Gecis Scripti
# Bu script VM'de calistirilir. Once: git pull ile guncel kodu alin.
#
# Kullanim:
#   export PG_PASSWORD="GÜÇLÜ_ŞİFRE_BURAYA"
#   chmod +x scripts/vm_postgres_migration.sh
#   ./scripts/vm_postgres_migration.sh
#
# veya tek satirda:
#   PG_PASSWORD='sifreniz' ./scripts/vm_postgres_migration.sh

set -Eeuo pipefail

APP_DIR="${APP_DIR:-/home/kokpitim.com/public_html}"
CONTAINER_NAME="sps-web"
IMAGE_NAME="sps_web_final:latest"
BACKUP_DIR="/home/kokpitim.com/backups"
TS="$(date +%Y%m%d_%H%M%S)"

if [[ -z "${PG_PASSWORD:-}" ]]; then
  echo "HATA: PG_PASSWORD environment variable gerekli."
  echo "Ornek: PG_PASSWORD='sifreniz' ./scripts/vm_postgres_migration.sh"
  exit 1
fi

# Container'dan host PostgreSQL'e: 172.17.0.1 (Docker bridge)
# ip addr show docker0 | grep inet ile dogrulayin
PG_HOST="${PG_HOST:-172.17.0.1}"
PG_URI="postgresql://kokpitim_user:${PG_PASSWORD}@${PG_HOST}/kokpitim_db"

echo "==> [VM PostgreSQL Gecis] Basladi: $TS"
cd "$APP_DIR"
mkdir -p "$BACKUP_DIR"

# --- 1. SQLite yedeği ---
echo "==> 1/7 SQLite yedegi aliniyor..."
if sudo docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
  sudo docker cp "$CONTAINER_NAME:/app/instance/kokpitim.db" \
    "$BACKUP_DIR/kokpitim_sqlite_${TS}.db" || true
fi
if [[ -f "$APP_DIR/instance/kokpitim.db" ]]; then
  cp -f "$APP_DIR/instance/kokpitim.db" "$BACKUP_DIR/kokpitim_host_${TS}.db"
fi
SQLITE_PATH="${SQLITE_PATH:-$APP_DIR/instance/kokpitim.db}"
if [[ ! -f "$SQLITE_PATH" ]]; then
  SQLITE_PATH="$BACKUP_DIR/kokpitim_host_${TS}.db"
fi
echo "    SQLite yedek: $BACKUP_DIR/kokpitim_sqlite_${TS}.db"

# --- 2. PostgreSQL kurulu mu kontrol ---
echo "==> 2/7 PostgreSQL kontrol..."
if ! systemctl is-active --quiet postgresql 2>/dev/null; then
  echo "    PostgreSQL kuruluyor..."
  sudo apt-get update -qq
  sudo apt-get install -y postgresql postgresql-contrib
  sudo systemctl start postgresql
  sudo systemctl enable postgresql
fi

# --- 3. Veritabani ve kullanici ---
echo "==> 3/7 Veritabani ve kullanici olusturuluyor..."
if ! sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='kokpitim_user'" | grep -q 1; then
  sudo -u postgres psql -c "CREATE USER kokpitim_user WITH PASSWORD '${PG_PASSWORD}';"
else
  sudo -u postgres psql -c "ALTER USER kokpitim_user WITH PASSWORD '${PG_PASSWORD}';"
fi
if ! sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='kokpitim_db'" | grep -q 1; then
  sudo -u postgres psql -c "CREATE DATABASE kokpitim_db OWNER kokpitim_user;"
fi
sudo -u postgres psql -d kokpitim_db -c "GRANT ALL ON SCHEMA public TO kokpitim_user;"
sudo -u postgres psql -d kokpitim_db -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO kokpitim_user;" 2>/dev/null || true

# --- 4. pg_hba.conf ---
echo "==> 4/7 pg_hba.conf guncelleniyor..."
PG_HBA="/etc/postgresql/$(ls /etc/postgresql/ 2>/dev/null | head -1)/main/pg_hba.conf"
if [[ -f "$PG_HBA" ]] && ! grep -q "172.17.0.0/16" "$PG_HBA"; then
  echo "host    kokpitim_db    kokpitim_user    172.17.0.0/16    md5" | sudo tee -a "$PG_HBA"
  echo "host    kokpitim_db    kokpitim_user    127.0.0.1/32    md5" | sudo tee -a "$PG_HBA"
  sudo systemctl reload postgresql
fi

# --- 5. Schema (flask db upgrade) ---
echo "==> 5/7 PostgreSQL schema olusturuluyor (flask db upgrade)..."
sudo docker build -t "$IMAGE_NAME" . -q
sudo docker run --rm \
  -v "$APP_DIR:/app" \
  -e FLASK_APP=app.py \
  -e SQLALCHEMY_DATABASE_URI="$PG_URI" \
  -w /app \
  "$IMAGE_NAME" \
  flask db upgrade

# --- 6. Veri tasima ---
echo "==> 6/7 SQLite -> PostgreSQL veri tasimasi..."
sudo docker run --rm \
  -v "$APP_DIR:/app" \
  -e SQLALCHEMY_DATABASE_URI="$PG_URI" \
  -e TRUNCATE_FIRST=1 \
  -w /app \
  "$IMAGE_NAME" \
  python scripts/sqlite_to_postgres.py

# --- 7. Container PostgreSQL ile baslat ---
echo "==> 7/7 Container yeniden baslatiliyor (PostgreSQL ile)..."
if sudo docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
  sudo docker stop "$CONTAINER_NAME" || true
  sudo docker rm "$CONTAINER_NAME" || true
fi
sudo docker run -d \
  --name "$CONTAINER_NAME" \
  -p 80:5000 \
  -v "$APP_DIR/instance:/app/instance" \
  -e SQLALCHEMY_DATABASE_URI="$PG_URI" \
  "$IMAGE_NAME"

echo ""
echo "==> Log kontrol..."
sleep 3
sudo docker logs "$CONTAINER_NAME" --tail=30

echo ""
echo "==> Health check..."
curl -fsS http://127.0.0.1/ -o /dev/null && echo "OK: Site erisilebilir." || echo "UYARI: Health check basarisiz, loglari kontrol edin."

echo ""
echo "==> PostgreSQL gecisi tamamlandi."
echo "    https://kokpitim.com adresinden test edin."
