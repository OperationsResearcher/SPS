#!/usr/bin/env bash
# Oracle VM — demo.kokpitim.com demo ortamı kurulumu (idempotent)
# Çalıştır: sudo bash setup_demo_env.sh
#
# Önkoşul:
#   - test ortamı çalışıyor (kokpitim_test_db Tomofil verisi içeriyor)
#   - DNS: demo.kokpitim.com → VM IP (Cloudflare proxy kapalı)
#   - main branch'de demo kodları var (TASK-137)
set -euo pipefail

DEMO_DIR="/opt/kokpitim-demo"
APP_DIR="$DEMO_DIR/app"
DB_NAME="kokpitim_demo_db"
DB_USER="kokpitim_demo_user"
DB_PASS_FILE="$DEMO_DIR/.db_password"
APP_PORT="5080"
DOMAIN="demo.kokpitim.com"
CONTAINER_NAME="kokpitim-demo-web"
TEST_DIR="/opt/kokpitim-test"
TEST_DB_NAME="kokpitim_test_db"
TEST_CONTAINER="kokpitim-test-web"

echo "═══════════════════════════════════════════════════════════"
echo "  Kokpitim DEMO ortamı kurulumu"
echo "  Domain: $DOMAIN"
echo "  Dir   : $DEMO_DIR"
echo "  Port  : $APP_PORT"
echo "  DB    : $DB_NAME"
echo "═══════════════════════════════════════════════════════════"

# ─── 1. Dizin yapısı (test'ten kopya) ────────────────────────────────────────
echo "→ [1/8] Dizin yapısı"
if [ ! -d "$DEMO_DIR" ]; then
  mkdir -p "$DEMO_DIR"/{backups,instance,logs}
  # App kodu test'ten kopyala (tarball ile gelen değişiklikler dahil)
  rsync -a --delete "$TEST_DIR/app/" "$APP_DIR/"
  echo "  ✓ $DEMO_DIR oluşturuldu, app/ test'ten kopyalandı"
else
  echo "  ✓ $DEMO_DIR zaten var, app/ güncelleniyor"
  rsync -a "$TEST_DIR/app/" "$APP_DIR/"
fi

# ─── 2. DB kullanıcı + veritabanı ────────────────────────────────────────────
echo "→ [2/8] PostgreSQL kullanıcı + DB"
if [ ! -f "$DB_PASS_FILE" ]; then
  DB_PASS=$(openssl rand -hex 16)
  echo "$DB_PASS" > "$DB_PASS_FILE"
  chmod 600 "$DB_PASS_FILE"
else
  DB_PASS=$(cat "$DB_PASS_FILE")
fi

sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 \
  || sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 \
  || sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
echo "  ✓ DB: $DB_NAME, user: $DB_USER"

# ─── 3. Test DB'den Tomofil verisini kopyala ────────────────────────────────
echo "→ [3/8] Test DB → Demo DB (Tomofil tarball'ı)"
DUMP_FILE="/tmp/kokpitim_test_dump_$(date +%s).sql"
sudo -u postgres pg_dump --clean --if-exists "$TEST_DB_NAME" > "$DUMP_FILE"
echo "  Dump: $(du -h "$DUMP_FILE" | cut -f1)"
PGPASSWORD="$DB_PASS" psql -h localhost -U "$DB_USER" -d "$DB_NAME" -f "$DUMP_FILE" > /dev/null 2>&1 || {
  # cleanup ile pg_dump farklı user'a yazıyor olabilir; sudo ile dene
  sudo -u postgres psql -d "$DB_NAME" -f "$DUMP_FILE" > /dev/null
}
sudo -u postgres psql -d "$DB_NAME" -c "REASSIGN OWNED BY postgres TO $DB_USER;" > /dev/null 2>&1 || true
sudo -u postgres psql -d "$DB_NAME" -c "GRANT ALL ON ALL TABLES IN SCHEMA public TO $DB_USER; GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;"
rm -f "$DUMP_FILE"
echo "  ✓ Veri kopyalandı"

# ─── 4. .env dosyası ─────────────────────────────────────────────────────────
echo "→ [4/8] .env"
SECRET_KEY=$(openssl rand -hex 32)
cat > "$DEMO_DIR/.env" <<ENVEOF
FLASK_ENV=production
SECRET_KEY=$SECRET_KEY
SQLALCHEMY_DATABASE_URI=postgresql://$DB_USER:$DB_PASS@host.docker.internal:5432/$DB_NAME
PORT=$APP_PORT
KOKPITIM_DEMO_MODE=1
DEMO_SESSION_MINUTES=60
DEMO_TENANT_ID=27
SESSION_COOKIE_SAMESITE=Lax
TRUST_PROXY=1
ENVEOF
chmod 600 "$DEMO_DIR/.env"
cp "$DEMO_DIR/.env" "$APP_DIR/.env"
echo "  ✓ .env yazıldı"

# ─── 5. Docker container ─────────────────────────────────────────────────────
echo "→ [5/8] Docker container"
# Mevcut container varsa durdur+sil
sudo docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
# Test container'ının imajını kullan (aynı kod)
TEST_IMAGE=$(sudo docker inspect "$TEST_CONTAINER" --format='{{.Config.Image}}' 2>/dev/null || echo "kokpitim-test-web:latest")
echo "  Image: $TEST_IMAGE"

sudo docker run -d \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  --add-host=host.docker.internal:host-gateway \
  -p "127.0.0.1:$APP_PORT:$APP_PORT" \
  --env-file "$APP_DIR/.env" \
  -v "$DEMO_DIR/instance:/app/instance" \
  -v "$DEMO_DIR/logs:/app/logs" \
  "$TEST_IMAGE"
echo "  ✓ Container ayakta: $CONTAINER_NAME"

# Container'ın hazır olmasını bekle
echo -n "  Container hazır olması bekleniyor"
for i in {1..30}; do
  if sudo docker exec "$CONTAINER_NAME" curl -sf "http://127.0.0.1:$APP_PORT/" -o /dev/null 2>&1; then
    echo " ✓"
    break
  fi
  echo -n "."
  sleep 1
done

# ─── 6. Nginx config ─────────────────────────────────────────────────────────
echo "→ [6/8] Nginx config"
NGINX_CONF="/etc/nginx/sites-available/$DOMAIN.conf"
sudo tee "$NGINX_CONF" > /dev/null <<NGINXEOF
server {
    listen 80;
    server_name $DOMAIN;
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 301 https://\$host\$request_uri; }
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    ssl_certificate     /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 90s;
    }
}
NGINXEOF
sudo ln -sf "$NGINX_CONF" "/etc/nginx/sites-enabled/$DOMAIN.conf"
echo "  ✓ Nginx config yazıldı"

# ─── 7. Let's Encrypt cert ───────────────────────────────────────────────────
echo "→ [7/8] Let's Encrypt SSL"
sudo mkdir -p /var/www/certbot
# HTTP-only önce yükle (certbot HTTP-01 challenge için)
# Geçici minimal HTTP config
cat <<TMPHTTP | sudo tee /etc/nginx/sites-available/$DOMAIN.conf.tmp > /dev/null
server {
    listen 80;
    server_name $DOMAIN;
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 200 'demo bootstrap'; add_header Content-Type text/plain; }
}
TMPHTTP

if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
  sudo cp /etc/nginx/sites-available/$DOMAIN.conf.tmp /etc/nginx/sites-available/$DOMAIN.conf
  sudo nginx -t && sudo systemctl reload nginx
  sudo certbot certonly --webroot -w /var/www/certbot -d "$DOMAIN" \
    --non-interactive --agree-tos -m "bilgi@kokpitim.com" || echo "  ⚠ certbot başarısız — manuel kontrol"
  # Şimdi tam SSL config'i geri yaz
  sudo tee "$NGINX_CONF" > /dev/null <<NGINXEOF2
server {
    listen 80;
    server_name $DOMAIN;
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 301 https://\$host\$request_uri; }
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    ssl_certificate     /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 90s;
    }
}
NGINXEOF2
fi
sudo rm -f /etc/nginx/sites-available/$DOMAIN.conf.tmp
sudo nginx -t && sudo systemctl reload nginx
echo "  ✓ SSL aktif"

# ─── 8. Smoke ────────────────────────────────────────────────────────────────
echo "→ [8/8] Smoke test"
sleep 2
curl -sk -o /dev/null -w "  HTTPS / → HTTP %{http_code}\n" "https://$DOMAIN/"
curl -sk -o /dev/null -w "  HTTPS /demo/ → HTTP %{http_code}\n" "https://$DOMAIN/demo/"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ Demo ortamı hazır: https://$DOMAIN/demo/"
echo "═══════════════════════════════════════════════════════════"
