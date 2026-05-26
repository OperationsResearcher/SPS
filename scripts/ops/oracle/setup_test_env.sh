#!/usr/bin/env bash
# Oracle VM — test.kokpitim.com staging ortamı kurulumu
# Çalıştır: sudo bash setup_test_env.sh
#
# Beklenen:
#   - /tmp/local-to-test.dump (yerel PG dump, custom format)
#   - DNS: test.kokpitim.com → 129.159.30.175 (ayarlandı)
#   - Boş port: 5050

set -euo pipefail

TEST_DIR="/opt/kokpitim-test"
APP_DIR="$TEST_DIR/app"
REPO_URL="https://github.com/OperationsResearcher/SPS.git"
BRANCH="main"
DB_NAME="kokpitim_test_db"
DB_USER="kokpitim_test_user"
DB_PASS_FILE="$TEST_DIR/.db_password"
APP_PORT="5050"
DOMAIN="test.kokpitim.com"
CONTAINER_NAME="kokpitim-test-web"

echo "═══════════════════════════════════════════════════════════"
echo "  Kokpitim TEST ortamı kurulumu"
echo "  Domain: $DOMAIN"
echo "  Dir   : $TEST_DIR"
echo "  Port  : $APP_PORT"
echo "  DB    : $DB_NAME"
echo "═══════════════════════════════════════════════════════════"

# ─── 1) Dizin yapısı ──────────────────────────────────────────────
echo ">> 1) Dizin yapısı oluşturuluyor..."
mkdir -p "$TEST_DIR"/{backups,instance/uploads/tenant_logos,logs}
chown -R ubuntu:ubuntu "$TEST_DIR"

# ─── 2) Repo clone ────────────────────────────────────────────────
echo ">> 2) Kod clone'lanıyor..."
if [ -d "$APP_DIR/.git" ]; then
    cd "$APP_DIR" && sudo -u ubuntu git fetch origin && sudo -u ubuntu git reset --hard origin/$BRANCH
else
    sudo -u ubuntu git clone -b $BRANCH "$REPO_URL" "$APP_DIR"
fi

# ─── 3) PostgreSQL DB + user ──────────────────────────────────────
echo ">> 3) PostgreSQL hazırlanıyor..."
if [ ! -f "$DB_PASS_FILE" ]; then
    openssl rand -base64 24 | tr -d '/+=' | head -c 24 > "$DB_PASS_FILE"
    chmod 600 "$DB_PASS_FILE"
    chown ubuntu:ubuntu "$DB_PASS_FILE"
fi
DB_PASS=$(cat "$DB_PASS_FILE")

sudo -u postgres psql <<SQL
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$DB_USER') THEN
        CREATE ROLE $DB_USER LOGIN PASSWORD '$DB_PASS';
    ELSE
        ALTER ROLE $DB_USER PASSWORD '$DB_PASS';
    END IF;
END
\$\$;
SQL

# DB drop & recreate (idempotent)
sudo -u postgres dropdb --if-exists "$DB_NAME"
sudo -u postgres createdb -O "$DB_USER" "$DB_NAME"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# ─── 4) Dump restore ──────────────────────────────────────────────
echo ">> 4) DB dump restore ediliyor..."
if [ -f /tmp/local-to-test.dump ]; then
    sudo -u postgres pg_restore --no-owner --role="$DB_USER" -d "$DB_NAME" /tmp/local-to-test.dump 2>&1 | tail -5 || true
    # Tüm objelerin sahibini test_user'a ata
    sudo -u postgres psql -d "$DB_NAME" -c "REASSIGN OWNED BY postgres TO $DB_USER;" 2>/dev/null || true
else
    echo "  ! /tmp/local-to-test.dump bulunamadı, atlanıyor"
fi

# ─── 5) .env oluştur ──────────────────────────────────────────────
echo ">> 5) .env yazılıyor..."
ENV_FILE="$TEST_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    # Üretim .env'inden kopyala (SMTP + diğer secret'lar için)
    if [ -f /opt/kokpitim/.env ]; then
        cp /opt/kokpitim/.env "$ENV_FILE"
    fi
    # Üretime özgü değerleri override et
    cat >> "$ENV_FILE" <<ENVEOF

# ═══ TEST ORTAMI OVERRIDE (setup_test_env.sh) ═══
FLASK_ENV=production
DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)
SQLALCHEMY_DATABASE_URI=postgresql://$DB_USER:$DB_PASS@127.0.0.1:5432/$DB_NAME
DATABASE_URL=postgresql://$DB_USER:$DB_PASS@127.0.0.1:5432/$DB_NAME
PORT=$APP_PORT
ENVEOF
    chmod 600 "$ENV_FILE"
    chown ubuntu:ubuntu "$ENV_FILE"
fi

# ─── 6) instance/uploads kopyala (logo, profil fotoğraf vb.) ───
echo ">> 6) Statik upload'ları yerelden taşı (varsa)..."
if [ -d /opt/kokpitim/instance/uploads ]; then
    rsync -a /opt/kokpitim/instance/uploads/ "$TEST_DIR/instance/uploads/" || true
    chown -R ubuntu:ubuntu "$TEST_DIR/instance"
fi

# ─── 7) Docker container ──────────────────────────────────────────
echo ">> 7) Docker container build & run..."
cd "$APP_DIR"
# Üretim imajını ödünç al — yeniden build et (kod farklılığı olabilir)
sudo docker build -t kokpitim_test:latest -f Dockerfile . 2>&1 | tail -3 || {
    echo "  ! Build başarısız — üretim imajını kullanıyoruz"
    sudo docker tag kokpitim_web:latest kokpitim_test:latest || true
}

# Eski container varsa sil
sudo docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

# Yeni container — host network ile (üretim deseni)
sudo docker run -d \
    --name "$CONTAINER_NAME" \
    --network host \
    --restart unless-stopped \
    -v "$TEST_DIR/.env":/app/.env:ro \
    -v "$TEST_DIR/instance":/app/instance \
    -v "$TEST_DIR/logs":/app/logs \
    -e PORT=$APP_PORT \
    -e FLASK_ENV=production \
    kokpitim_test:latest

# ─── 8) Nginx config ──────────────────────────────────────────────
echo ">> 8) Nginx config yazılıyor..."
NGINX_CONF="/etc/nginx/sites-available/$DOMAIN.conf"
cat > "$NGINX_CONF" <<NGINX
server {
    listen 80;
    server_name $DOMAIN;

    # Let's Encrypt challenge için
    location /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
    }

    location / {
        return 301 https://\$host\$request_uri;
    }
}

# HTTPS server bloğu certbot tarafından eklenecek
server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    # SSL sertifikası certbot tarafından doldurulacak
    # ssl_certificate     /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    client_max_body_size 32M;

    location / {
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
    }
}
NGINX

mkdir -p /var/www/letsencrypt
ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# ─── 9) Let's Encrypt SSL ─────────────────────────────────────────
echo ">> 9) Let's Encrypt SSL sertifikası alınıyor..."
# HTTPS bloğunu geçici devre dışı bırak (sertifika almak için sadece HTTP)
sed -i 's|^server {$|# server {|; s|^    listen 443|#     listen 443|' "$NGINX_CONF" || true
# Aslında daha temiz: ayrı geçici config
cat > "$NGINX_CONF" <<NGINX2
server {
    listen 80;
    server_name $DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
    }

    location / {
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
NGINX2
nginx -t && systemctl reload nginx

# Certbot
certbot certonly --webroot -w /var/www/letsencrypt -d "$DOMAIN" \
    --non-interactive --agree-tos --email admin@kokpitim.com \
    --no-eff-email || echo "  ! Certbot başarısız — manuel müdahale"

# SSL'li config
if [ -f /etc/letsencrypt/live/$DOMAIN/fullchain.pem ]; then
    cat > "$NGINX_CONF" <<NGINX3
server {
    listen 80;
    server_name $DOMAIN;
    location /.well-known/acme-challenge/ { root /var/www/letsencrypt; }
    location / { return 301 https://\$host\$request_uri; }
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    ssl_certificate     /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 32M;

    location / {
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
    }
}
NGINX3
    nginx -t && systemctl reload nginx
    echo "  ✓ HTTPS aktif"
fi

# ─── 10) Smoke test ───────────────────────────────────────────────
echo ">> 10) Smoke test..."
sleep 5
curl -sS -o /dev/null -w "HTTP %{http_code} (yerel) — http://127.0.0.1:$APP_PORT/\n" "http://127.0.0.1:$APP_PORT/" || true
curl -sS -o /dev/null -w "HTTP %{http_code} (https) — https://$DOMAIN/\n" "https://$DOMAIN/" || true

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  TAMAMLANDI — https://$DOMAIN/"
echo "  Container: $CONTAINER_NAME (port $APP_PORT)"
echo "  DB: $DB_NAME"
echo "  Yapılandırma: $TEST_DIR"
echo "═══════════════════════════════════════════════════════════"
