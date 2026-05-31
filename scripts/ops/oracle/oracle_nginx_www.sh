#!/usr/bin/env bash
set -euo pipefail
sudo cp /tmp/www.kokpitim.com.nginx.conf /etc/nginx/sites-available/www.kokpitim.com
sudo ln -sf /etc/nginx/sites-available/www.kokpitim.com /etc/nginx/sites-enabled/www.kokpitim.com
sudo nginx -t
sudo systemctl reload nginx
echo "nginx www OK (HTTP). SSL: sudo certbot --nginx -d www.kokpitim.com -d kokpitim.com"
