#!/usr/bin/env bash
# Ortak yardımcılar — Yayın/Test deploy scriptleri
# shellcheck disable=SC2034

psql_pg() {
  # "could not change directory to /home/ubuntu" uyarısını bastır
  sudo -u postgres psql "$@" 2> >(grep -v 'could not change directory' >&2)
}

health_code() {
  # nginx :80 /health 404 yanıltıcı — önce uygulama portu
  local url="$1"
  curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$url" || echo '000'
}

fix_table_owner() {
  local db="$1"
  local owner="$2"
  psql_pg -d "$db" -v ON_ERROR_STOP=1 <<SQL
ALTER DATABASE ${db} OWNER TO ${owner};
ALTER SCHEMA public OWNER TO ${owner};
DO \$\$
DECLARE r record;
BEGIN
  FOR r IN SELECT tablename FROM pg_tables WHERE schemaname='public' LOOP
    EXECUTE format('ALTER TABLE public.%I OWNER TO ${owner}', r.tablename);
  END LOOP;
  FOR r IN SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema='public' LOOP
    EXECUTE format('ALTER SEQUENCE public.%I OWNER TO ${owner}', r.sequence_name);
  END LOOP;
END\$\$;
GRANT ALL ON SCHEMA public TO ${owner};
GRANT ALL ON ALL TABLES IN SCHEMA public TO ${owner};
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO ${owner};
SQL
}

print_fallback() {
  local step="$1"
  local detail="${2:-}"
  cat <<EOF

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
FALLBACK — script bu adımda durdu: ${step}
${detail}

Geleneksel yol (canonical):
  docs/SUNUCU-GUNCELLEME-REHBERI.md  §3 (yedek) · §4 (Yayın) · §5/§0.6 (Test sıfırdan)

Elle Yayın:
  ssh -i C:\\crt\\ssh-key-2026-04-18_v4.key ubuntu@129.159.30.175
  cd /opt/kokpitim/app && sudo bash scripts/ops/oracle/oracle_safe_deploy.sh
  sudo docker exec kokpitim-web bash -lc 'cd /app && python3 scripts/seed_card_descriptions.py --calistir'

Elle Test sıfırdan: aynı rehber §0.6 + §5 (container yeniden oluştur).
Ajan: script başarısız → FALLBACK yaz, geleneksel yolla devam et; sessizce yama yapma.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

EOF
}
