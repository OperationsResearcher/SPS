#!/usr/bin/env bash
# Oracle VM tam yedek — PostgreSQL DB + uygulama kodu + .env
# Kullanım (VM'de):  sudo bash scripts/ops/oracle/oracle_full_backup.sh
#
# Çıktı: /opt/kokpitim/backups/full_YYYYMMDD_HHMMSS/
#   ├── pg_kokpitim_db.sql.gz   (PostgreSQL custom-format dump)
#   ├── app_code.tar.gz         (.git + venv hariç uygulama dizini)
#   ├── env_snapshot.txt        (.env içeriği — HASSAS)
#   ├── alembic_version.txt
#   └── manifest.txt            (boyut + sha256 + tarih)

set -euo pipefail

APP_DIR="${APP_DIR:-/opt/kokpitim/app}"
BACKUP_BASE="${BACKUP_BASE:-/opt/kokpitim/backups}"
PG_DB="${PG_DATABASE:-kokpitim_db}"
TS="$(date +%Y%m%d_%H%M%S)"
OUT="${BACKUP_BASE}/full_${TS}"
CONTAINER="${CONTAINER:-kokpitim-web}"

mkdir -p "$OUT"
echo "==> Yedek dizini: $OUT"

# ── 1) PostgreSQL dump ───────────────────────────────────────────────────────
echo "==> 1/6 PostgreSQL dump ($PG_DB)"
sudo -u postgres pg_dump --format=custom --no-owner --no-privileges "$PG_DB" \
  | gzip -c > "$OUT/pg_${PG_DB}.dump.gz"

# Plain SQL dump (insan-okunur, restore fallback)
sudo -u postgres pg_dump --no-owner --no-privileges "$PG_DB" \
  | gzip -c > "$OUT/pg_${PG_DB}.sql.gz"

# ── 2) Alembic versiyonu ─────────────────────────────────────────────────────
echo "==> 2/6 Alembic versiyon kaydı"
sudo -u postgres psql -d "$PG_DB" -tAc \
  "SELECT version_num FROM alembic_version" > "$OUT/alembic_version.txt" 2>/dev/null \
  || echo "(alembic_version okunamadi)" > "$OUT/alembic_version.txt"

# ── 3) Uygulama kodu ─────────────────────────────────────────────────────────
echo "==> 3/6 Uygulama kodu (tar.gz)"
tar --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
    --exclude='node_modules' --exclude='.venv' --exclude='venv' \
    --exclude='instance' --exclude='backups' --exclude='logs' \
    -czf "$OUT/app_code.tar.gz" -C "$(dirname "$APP_DIR")" "$(basename "$APP_DIR")"

# ── 4) instance/ (yüklemeler, logolar) ───────────────────────────────────────
echo "==> 4/6 instance/"
INST_DIR="$(dirname "$APP_DIR")/instance"
if [ -d "$INST_DIR" ]; then
  tar -czf "$OUT/instance.tar.gz" -C "$(dirname "$INST_DIR")" "$(basename "$INST_DIR")"
else
  echo "(instance dizini yok)" > "$OUT/instance_missing.txt"
fi

# ── 5) .env (HASSAS — sadece root okuyabilsin) ───────────────────────────────
echo "==> 5/6 .env snapshot"
ENV_SRC="${APP_DIR}/.env"
[ -f "$ENV_SRC" ] || ENV_SRC="$(dirname "$APP_DIR")/.env"
if [ -f "$ENV_SRC" ]; then
  cp "$ENV_SRC" "$OUT/env_snapshot.txt"
  chmod 600 "$OUT/env_snapshot.txt"
else
  echo "(.env bulunamadı)" > "$OUT/env_snapshot.txt"
fi

# Git durumu (kod arşivi .git hariç; commit izi ayrı)
if [ -d "$APP_DIR/.git" ]; then
  {
    echo "HEAD=$(git -C "$APP_DIR" rev-parse HEAD 2>/dev/null || echo '?')"
    git -C "$APP_DIR" log -1 --oneline 2>/dev/null || true
    echo "--- status ---"
    git -C "$APP_DIR" status -sb 2>/dev/null || true
  } > "$OUT/git_snapshot.txt"
fi

# ── 6) Manifest ──────────────────────────────────────────────────────────────
echo "==> 6/6 Manifest"
{
  echo "Yedek tarihi : $TS"
  echo "Sunucu       : $(hostname) $(uname -a)"
  echo "PostgreSQL DB: $PG_DB"
  echo "App dizini   : $APP_DIR"
  echo "Container    : $CONTAINER ($(docker inspect -f '{{.Image}}' "$CONTAINER" 2>/dev/null || echo 'down'))"
  echo "Alembic head : $(cat "$OUT/alembic_version.txt")"
  echo ""
  echo "── Dosyalar ─────────────────────────────────────"
  cd "$OUT"
  for f in *; do
    [ -f "$f" ] || continue
    size=$(du -h "$f" | cut -f1)
    sha=$(sha256sum "$f" | cut -c1-16)
    printf "  %-30s %10s  sha256:%s...\n" "$f" "$size" "$sha"
  done
} | tee "$OUT/manifest.txt"

# ── Eski yedek temizliği (30 günden eski full_* dizinleri) ───────────────────
find "$BACKUP_BASE" -maxdepth 1 -type d -name "full_*" -mtime +30 -exec rm -rf {} \; 2>/dev/null || true

# scp ile indirilebilir olsun (ubuntu kullanıcısı)
chmod -R a+rX "$OUT"

echo ""
echo "✅ Yedek tamamlandı: $OUT"
echo "   Toplam boyut: $(du -sh "$OUT" | cut -f1)"
echo ""
echo "▶ Yerele indirmek için (kendi makinende çalıştır):"
echo "   scp -r ubuntu@129.159.30.175:$OUT  ./yedekler/"
