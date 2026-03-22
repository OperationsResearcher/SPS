#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boğaziçi tenant'ında eksik H1.1 alt stratejisini oluşturur, tenant dışı H1.1 linkini düzeltir,
isteğe bağlı olarak kmf_s11_import çağrısını yapar.

Kullanım (proje kökü):
  py scripts/ensure_boun_h11_and_import_s11.py --tenant-name "Boğaziçi Üniversitesi"
  py scripts/ensure_boun_h11_and_import_s11.py --tenant-id 7 --process-id 18 --skip-import
  py scripts/ensure_boun_h11_and_import_s11.py --tenant-id 7 --process-id 18 --json docs/KMF/s11-extracted.json --actor-user-id 31
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("FLASK_ENV", "development")
if not os.environ.get("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "dev-only-script"

from app import create_app
from app.models import db
from app.models.core import Strategy, SubStrategy, Tenant
from app.models.process import Process, ProcessSubStrategyLink


H11_CODE = "H1.1"
H11_TITLE = (
    "İletişimi, iş birliğini, eleştirel düşünmeyi ve yaratıcılığı teşvik eden "
    "kapsayıcı eğitim ve öğretim ortamları geliştirmek."
)


def find_tenant(tenant_id: int | None, tenant_name: str | None) -> Tenant | None:
    if tenant_id is not None:
        return Tenant.query.filter_by(id=tenant_id, is_active=True).first()
    if tenant_name:
        q = tenant_name.strip()
        return Tenant.query.filter(Tenant.name.ilike(f"%{q}%"), Tenant.is_active.is_(True)).first()
    return None


def ensure_h11_for_tenant(tenant_id: int) -> SubStrategy:
    """SA1 altında aktif H1.1 yoksa oluşturur."""
    sa1 = (
        Strategy.query.filter_by(tenant_id=tenant_id, is_active=True)
        .filter(Strategy.code == "SA1")
        .first()
    )
    if not sa1:
        raise RuntimeError(f"tenant_id={tenant_id} için SA1 stratejisi bulunamadı.")

    existing = (
        SubStrategy.query.filter_by(strategy_id=sa1.id, is_active=True)
        .filter(db.func.lower(SubStrategy.code) == H11_CODE.lower())
        .first()
    )
    if existing:
        return existing

    ss = SubStrategy(
        strategy_id=sa1.id,
        code=H11_CODE,
        title=H11_TITLE[:200],
        description=H11_TITLE if len(H11_TITLE) > 200 else None,
        is_active=True,
    )
    db.session.add(ss)
    db.session.flush()
    return ss


def rewire_process_h11(process_id: int, tenant_id: int, h11: SubStrategy) -> None:
    proc = Process.query.filter_by(id=process_id, tenant_id=tenant_id, is_active=True).first()
    if not proc:
        raise RuntimeError(f"Süreç yok veya tenant uyuşmuyor: id={process_id} tenant={tenant_id}")

    # Tenant dışı veya yanlış H1.1 linklerini kaldır
    for link in list(proc.process_sub_strategy_links):
        ss = db.session.get(SubStrategy, link.sub_strategy_id)
        st = db.session.get(Strategy, ss.strategy_id) if ss else None
        if not ss or not st or st.tenant_id != tenant_id:
            db.session.delete(link)
            continue
        if ss.code and ss.code.strip().lower() == H11_CODE.lower() and ss.id != h11.id:
            db.session.delete(link)

    ids = {l.sub_strategy_id for l in proc.process_sub_strategy_links}
    if h11.id not in ids:
        db.session.add(
            ProcessSubStrategyLink(
                process_id=process_id,
                sub_strategy_id=h11.id,
                contribution_pct=None,
            )
        )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tenant-id", type=int, default=None)
    ap.add_argument("--tenant-name", type=str, default="Boğaziçi Üniversitesi")
    ap.add_argument("--process-id", type=int, required=True)
    ap.add_argument("--actor-user-id", type=int, default=None, help="Import için (tenant kullanıcısı)")
    ap.add_argument("--json", type=str, default="docs/KMF/s11-extracted.json")
    ap.add_argument("--skip-import", action="store_true")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    app = create_app()
    with app.app_context():
        ten = find_tenant(args.tenant_id, args.tenant_name)
        if not ten:
            print("Kurum bulunamadı.", file=sys.stderr)
            return 1
        print(f"Kurum: id={ten.id} name={ten.name!r}")

        h11 = ensure_h11_for_tenant(ten.id)
        db.session.commit()
        print(f"H1.1 alt strateji: id={h11.id} code={h11.code!r}")

        rewire_process_h11(args.process_id, ten.id, h11)
        db.session.commit()
        print(f"Süreç {args.process_id} H1.1 bağlantısı tenant {ten.id} ile hizalandı.")

    if args.skip_import:
        print("Import atlandı (--skip-import).")
        return 0

    actor = args.actor_user_id
    if not actor:
        print("--actor-user-id gerekli (import için).", file=sys.stderr)
        return 1

    jp = os.path.join(ROOT, args.json.replace("/", os.sep))
    if not os.path.isfile(jp):
        print(f"JSON yok: {jp}", file=sys.stderr)
        return 1

    cmd = [
        sys.executable,
        os.path.join(ROOT, "scripts", "kmf_s11_import.py"),
        "--process-id",
        str(args.process_id),
        "--actor-user-id",
        str(actor),
        "--json",
        jp,
        "--wipe-kpis",
        "--seed",
        str(args.seed),
    ]
    print("Çalıştırılıyor:", " ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
