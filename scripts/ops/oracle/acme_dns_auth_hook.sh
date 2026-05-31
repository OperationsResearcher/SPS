#!/usr/bin/env bash
# Certbot manual DNS auth hook — Cloudflare TXT kaydı eklenene kadar bekler.
set -euo pipefail

DOMAIN="${CERTBOT_DOMAIN:?}"
VALIDATION="${CERTBOT_VALIDATION:?}"
RECORD="_acme-challenge.${DOMAIN}"
OUT="/opt/kokpitim/backups/acme_dns_${DOMAIN}.txt"

mkdir -p /opt/kokpitim/backups
CF_NAME="_acme-challenge"
if [[ "$DOMAIN" == www.* ]]; then
  CF_NAME="_acme-challenge.www"
fi

cat >"$OUT" <<EOF
Cloudflare → kokpitim.com → DNS → Kayıt ekle

Tip: TXT
Ad (Name): ${CF_NAME}
İçerik (Content): ${VALIDATION}
Proxy: DNS only (gri bulut önerilir)

Tam FQDN: ${RECORD}
Bu dosya: ${OUT}
EOF

# www için _acme-challenge.www, apex için _acme-challenge
if [[ "$DOMAIN" == www.* ]]; then
  echo "[acme] TXT ${RECORD} = ${VALIDATION}" >&2
else
  echo "[acme] TXT ${RECORD} = ${VALIDATION}" >&2
fi

for i in $(seq 1 90); do
  if dig +short TXT "$RECORD" @1.1.1.1 2>/dev/null | tr -d '"' | grep -qF "$VALIDATION"; then
    echo "[acme] DNS yayildi (${DOMAIN})" >&2
    sleep 15
    exit 0
  fi
  sleep 10
done

echo "[acme] HATA: 15 dk icinde TXT kaydi gorunmedi: ${RECORD}" >&2
exit 1
