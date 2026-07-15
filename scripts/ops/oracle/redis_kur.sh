#!/usr/bin/env bash
# Redis kurulumu — TEK SEFERLİK (TASK-254).
#
# NEDEN AYRI SCRIPT: oracle_safe_deploy.sh her deploy'da koşuyor; Redis kurulumu
# bir kez yapılır. Deploy'a gömmek her seferinde paket yöneticisi çalıştırırdı.
#
# NEDEN HOST'A KURULUYOR (compose değil): oracle_safe_deploy.sh container'ı
# `docker run --network host` ile başlatıyor — yani container host'un ağını
# paylaşıyor ve 127.0.0.1'e bağlanabiliyor. PostgreSQL de tam olarak böyle
# çalışıyor. Aynı deseni izliyoruz.
#
# NE SAĞLAR:
#   - cache (DB 0)      : SimpleCache yerine ortak depo → 8 worker aynı değeri görür
#   - rate limit (DB 1) : memory:// yerine ortak sayaç → limit worker sayısınca gevşemez
#   Ayrı DB numaraları bilinçli: cache flush'ı rate-limit sayaçlarını silmesin.
#
# KULLANIM (operatör, Yayın VM'inde):
#   sudo bash scripts/ops/oracle/redis_kur.sh
#   # sonra /opt/kokpitim/.env dosyasına ekle:
#   #   CACHE_TYPE=RedisCache
#   #   REDIS_URL=redis://127.0.0.1:6379/0
#   #   RATELIMIT_STORAGE_URL=redis://127.0.0.1:6379/1
#   # ve container'ı yeniden BAŞLAT (restart env'i yeniden okumaz — yeni run gerekir)
set -euo pipefail

echo "==> 1/5 Redis kurulumu"
if command -v redis-server >/dev/null 2>&1; then
  echo "    Redis zaten kurulu: $(redis-server --version | head -1)"
else
  apt-get update -qq
  apt-get install -y --no-install-recommends redis-server
fi

echo "==> 2/5 Yapılandırma"
CONF="/etc/redis/redis.conf"
if [ -f "$CONF" ]; then
  cp -n "$CONF" "${CONF}.bak" || true
  # Yalnız localhost dinle — Redis'i internete AÇMA (parola yok, açık = tehlike)
  sed -i 's/^bind .*/bind 127.0.0.1 ::1/' "$CONF"
  sed -i 's/^# *maxmemory .*/maxmemory 256mb/' "$CONF"
  sed -i 's/^# *maxmemory-policy .*/maxmemory-policy allkeys-lru/' "$CONF"
  # AOF: restart'ta rate-limit sayaçları sıfırlanmasın (kısa limit-bypass penceresi)
  sed -i 's/^appendonly .*/appendonly yes/' "$CONF"
  grep -q '^appendonly' "$CONF" || echo 'appendonly yes' >> "$CONF"
else
  echo "    UYARI: $CONF yok — varsayılan yapılandırma kullanılacak"
fi

echo "==> 3/5 Servisi başlat"
systemctl enable redis-server
systemctl restart redis-server
sleep 2

echo "==> 4/5 Doğrulama"
if redis-cli ping | grep -q PONG; then
  echo "    PING -> PONG ✓"
  redis-cli INFO server | grep -E 'redis_version|tcp_port' || true
else
  echo "    HATA: Redis yanit vermiyor!" >&2
  exit 1
fi

# Sadece localhost'tan erişilebilir olduğunu teyit et
echo "==> 5/5 Guvenlik: disaridan erisim kapali mi"
if ss -tlnp 2>/dev/null | grep -q '0.0.0.0:6379'; then
  echo "    UYARI: Redis 0.0.0.0'da dinliyor — INTERNETE ACIK OLABILIR!" >&2
  echo "    /etc/redis/redis.conf icinde 'bind 127.0.0.1 ::1' olmali." >&2
  exit 1
fi
echo "    Yalniz localhost ✓"

cat <<'SON'

────────────────────────────────────────────────────────────
SIRADAKI ADIM (elle):
  1. /opt/kokpitim/.env dosyasina ekle:
       CACHE_TYPE=RedisCache
       REDIS_URL=redis://127.0.0.1:6379/0
       RATELIMIT_STORAGE_URL=redis://127.0.0.1:6379/1

  2. Container'i YENIDEN BASLAT (docker restart YETMEZ — env yeniden
     okunmaz; oracle_safe_deploy.sh calistir veya docker rm + run).

  3. Dogrula:  docker logs kokpitim-web 2>&1 | grep -i 'redis\|cache'
     Beklenen: "[cache] RedisCache kullaniliyor" + "[rate-limit] Redis kullaniliyor"
     Gorulmezse app SimpleCache'e dusmus demektir (hata degil, ama tutarsiz).
────────────────────────────────────────────────────────────
SON
