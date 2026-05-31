#!/usr/bin/env bash
# kokpitim.com (apex) Cloudflare 522/timeout — SSL SAN eksikligi duzeltmesi
# Calistir: sudo bash scripts/ops/oracle/fix_kokpitim_apex_ssl.sh
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/kokpitim/app}"
HOOK="${APP_DIR}/scripts/ops/oracle/acme_dns_auth_hook.sh"
CERT_NAME="www.kokpitim.com"

echo "==> Mevcut sertifika SAN:"
openssl x509 -in /etc/letsencrypt/live/${CERT_NAME}/fullchain.pem -noout -text 2>/dev/null \
  | grep -A1 "Subject Alternative Name" || true

echo "==> Certbot DNS dogrulama (Cloudflare TXT gerekir)"
echo "    Talimatlar: /opt/kokpitim/backups/acme_dns_*.txt"
chmod +x "$HOOK"

certbot certonly \
  --manual \
  --preferred-challenges dns \
  --cert-name "$CERT_NAME" \
  --expand \
  -d www.kokpitim.com \
  -d kokpitim.com \
  --manual-auth-hook "$HOOK" \
  --non-interactive \
  --agree-tos \
  --register-unsafely-without-email

echo "==> Nginx yeniden yukle"
nginx -t
systemctl reload nginx

echo "==> Dogrulama"
openssl x509 -in /etc/letsencrypt/live/${CERT_NAME}/fullchain.pem -noout -text \
  | grep -A1 "Subject Alternative Name"

curl -fsS -m 15 https://kokpitim.com/health | head -c 200 || echo "UYARI: CF uzerinden apex henuz yanit vermiyor — DNS/SSL yayilimini bekleyin"
echo ""
curl -fsS -m 5 https://www.kokpitim.com/health | head -c 200
echo ""
echo "OK: Sertifika guncellendi."
