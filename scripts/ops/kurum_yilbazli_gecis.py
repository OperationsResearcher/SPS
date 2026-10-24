"""Bir kurum için yıl bazlı veri geçişi — tek komut, sıralı, doğrulamalı (KMF #16 Yayın geçişi için).

SIRA (değişmez): [0] ön koşul (alembic head, yedek onayı) -> [1] Faz 1.2 clone zinciri -> [2] Faz 1.2b karışık PG
-> [3] Faz 1.5 kpi_data remap -> [4] Faz 1.4 override göçü -> [5] doğrulama (karışık PG=0, görünmez aktif ölçüm=0).

KULLANIM (varsayılan KONTROL: hiçbir şey yazmaz, yalnız her adımın kontrol çıktısını gösterir):
    python scripts/ops/kurum_yilbazli_gecis.py --tenant 16
    python scripts/ops/kurum_yilbazli_gecis.py --tenant 16 --calistir --yedek-onay "<dump dosya adı>"

GÜVENLİK: --calistir için --yedek-onay zorunlu (deploy öncesi alınan dump'ın adı). Adım hata verirse durur;
sonraki adımlar çalışmaz. Bu betik Yayın sunucusunda container içinde çalıştırılır (DB'ye uygulamanın kendi
bağlantısı); yerelde provada SQLALCHEMY_DATABASE_URI ile ayrı bir kopyaya yönlendirilir.
"""
from __future__ import annotations

import argparse
import subprocess
import sys

from sqlalchemy import text

ADIMLAR = [
    ("Faz 1.2 clone zinciri", "scripts/ops/yilbazli_faz1_2_clone_zinciri.py", True),
    ("Faz 1.2b karışık yıllı PG", "scripts/ops/yilbazli_faz1_2b_karisik_pg_duzelt.py", True),
    ("Faz 1.5 kpi_data remap", "scripts/ops/yilbazli_faz1_5_kpi_data_remap.py", False),
    ("Faz 1.4 override göçü", "scripts/ops/yilbazli_faz1_4_override_goc.py", True),
]
HEAD_BEKLENEN = "mg01a2b3c4d5"


def _calistir(yol: str, tenant: int, uygula: bool, tenant_arg: bool) -> int:
    kmd = [sys.executable, yol] + (["--tenant", str(tenant)] if tenant_arg else []) + (["--calistir"] if uygula else [])
    return subprocess.run(kmd).returncode


def _dogrula(tenant: int) -> int:
    sys.path.insert(0, ".")
    from app import create_app
    from extensions import db
    with create_app().app_context():
        c = db.session.connection()
        head = c.execute(text("select version_num from alembic_version")).scalar()
        karisik = c.execute(text("""select count(*) from process_kpis k join processes p on p.id=k.process_id
            join plan_years a on a.id=k.plan_year_id join plan_years b on b.id=p.plan_year_id
            where p.tenant_id=:t and k.is_active and a.year<>b.year"""), {"t": tenant}).scalar()
        gorunmez = c.execute(text("""select count(*) from kpi_data d join process_kpis k on k.id=d.process_kpi_id
            join processes p on p.id=k.process_id join plan_years a on a.id=k.plan_year_id join plan_years b on b.id=p.plan_year_id
            where p.tenant_id=:t and k.is_active and p.is_active and a.year<>b.year"""), {"t": tenant}).scalar()
        yilsiz = c.execute(text("""select count(*) from processes where tenant_id=:t and is_active and plan_year_id is null"""),
                           {"t": tenant}).scalar()
        print(f"\n[5] DOĞRULAMA: alembic={head} | karışık PG={karisik} | yıl uyumsuz ölçüm={gorunmez} | yılsız süreç={yilsiz}")
        return 0 if (karisik == 0 and gorunmez == 0 and yilsiz == 0) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Kurum yıl bazlı veri geçişi (sıralı runner)")
    ap.add_argument("--tenant", type=int, required=True)
    ap.add_argument("--calistir", action="store_true")
    ap.add_argument("--yedek-onay", help="deploy öncesi alınan dump dosya adı (--calistir için zorunlu)")
    a = ap.parse_args()
    if a.calistir and not a.yedek_onay:
        raise SystemExit("--calistir için --yedek-onay <dump adı> zorunlu (önce yedek!)")
    print(f"=== KURUM YIL BAZLI GEÇİŞ  tenant={a.tenant}  [{'UYGULAMA' if a.calistir else 'KONTROL'}]  yedek={a.yedek_onay} ===")
    for ad, yol, tenant_arg in ADIMLAR:
        print(f"\n>>> {ad}")
        rc = _calistir(yol, a.tenant, a.calistir, tenant_arg)
        if rc != 0:
            print(f"!!! {ad} başarısız (rc={rc}) — DURULDU, sonraki adımlar çalıştırılmadı")
            return rc
    if a.calistir:
        return _dogrula(a.tenant)
    print("\nKONTROL tamam (yazılmadı). Not: sonraki adımların kontrolü önceki adım uygulanmadan eksik sayı gösterebilir.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
