#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Adil (veya --email) kullanıcısının süreç erişim raporu + isteğe bağlı düzeltme."""
from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("FLASK_ENV", "development")
if not os.environ.get("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "dev-only-script"

from sqlalchemy import or_

from app import create_app
from app.models.core import Tenant, User
from app.models.process import Process, ProcessKpi, process_leaders
from app_platform.modules.surec.permissions import accessible_processes_filter, is_privileged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--email", default=None, help="Tam e-posta (öncelikli)")
    ap.add_argument("--name", default="adil", help="Ad/e-posta parçası (ilike)")
    ap.add_argument(
        "--ensure-leader-on-process",
        type=int,
        default=None,
        metavar="ID",
        help="Bu süreçte kullanıcıyı lider olarak ekle (yoksa)",
    )
    ap.add_argument(
        "--ensure-tenant-match",
        action="store_true",
        help="Kullanıcının tenant_id'sini sürecin tenant_id yap (dikkat!)",
    )
    args = ap.parse_args()

    app = create_app()
    with app.app_context():
        if args.email:
            users = list(User.query.filter(User.email.ilike(args.email.strip())).all())
        else:
            needle = f"%{args.name.strip()}%"
            users = list(
                User.query.filter(
                    or_(
                        User.first_name.ilike(needle),
                        User.last_name.ilike(needle),
                        User.email.ilike(needle),
                    )
                ).all()
            )

        print(f"Eşleşen kullanıcı: {len(users)}")
        for u in users:
            t = Tenant.query.get(u.tenant_id) if u.tenant_id else None
            r = u.role.name if u.role else None
            print("---")
            print(f"id={u.id} email={u.email} ad={u.first_name} {u.last_name}")
            print(f"tenant_id={u.tenant_id} tenant={t.name if t else None}")
            print(f"role={r} ayricalikli={is_privileged(u)}")

            tid = u.tenant_id
            if not tid:
                print("(tenant yok — süreç listesi boş)")
                continue

            q = Process.query.order_by(Process.code)
            acc = accessible_processes_filter(q, u, tid).all()
            print(f"erişilebilir süreç sayısı: {len(acc)}")
            for p in acc:
                nk = ProcessKpi.query.filter_by(process_id=p.id).count()
                code = p.code or "—"
                name = (p.name or "")[:56]
                print(f"  {p.id:4d}  {code:8s}  {name!s}  (PG:{nk})")

        print()
        print("=== Boğaziçi / üniversite adı geçen tenant süreçleri ===")
        for ten in Tenant.query.filter(Tenant.is_active.is_(True)).all():
            if not ten.name:
                continue
            low = ten.name.lower()
            if "bogaz" in low or "boun" in low or "ünivers" in low or "univers" in low:
                print(f"Tenant {ten.id}: {ten.name}")
                for p in Process.query.filter_by(tenant_id=ten.id, is_active=True).order_by(Process.id):
                    nk = ProcessKpi.query.filter_by(process_id=p.id).count()
                    nm = (p.name or "")[:56]
                    print(f"  {p.id:4d}  {p.code or '—':8s}  {nm!s}  (PG:{nk})")

        if args.ensure_leader_on_process and users:
            u = users[0]
            pid = args.ensure_leader_on_process
            proc = Process.query.filter_by(id=pid, is_active=True).first()
            if not proc:
                print(f"HATA: süreç bulunamadı id={pid}")
                return 1
            if args.ensure_tenant_match and u.tenant_id != proc.tenant_id:
                print(
                    f"UYARI: kullanıcı tenant={u.tenant_id}, süreç tenant={proc.tenant_id} — eşitleniyor."
                )
                u.tenant_id = proc.tenant_id
            if u.tenant_id != proc.tenant_id:
                print(
                    f"HATA: tenant uyuşmuyor (kullanıcı {u.tenant_id}, süreç {proc.tenant_id}). "
                    "Önce --ensure-tenant-match veya admin panelinden kurumu düzeltin."
                )
                return 1
            from app.models import db

            ins = process_leaders.insert().values(process_id=pid, user_id=u.id)
            try:
                db.session.execute(ins)
                db.session.commit()
                print(f"OK: kullanıcı {u.id} süreç {pid} liderlerine eklendi.")
            except Exception as e:
                db.session.rollback()
                print(f"(Muhtemelen zaten lider) {e}")
        return 0


def report_heavy_processes():
    """PG veya KpiData sayısı yüksek süreçler (import nerede?)."""
    from sqlalchemy import func

    from app.models.process import KpiData

    app = create_app()
    with app.app_context():
        q = (
            Process.query.join(Tenant)
            .filter(Process.is_active.is_(True))
            .with_entities(
                Process.id,
                Process.code,
                Process.name,
                Tenant.id.label("tid"),
                Tenant.name.label("tname"),
                func.count(ProcessKpi.id).label("nk"),
            )
            .outerjoin(ProcessKpi, ProcessKpi.process_id == Process.id)
            .group_by(Process.id, Process.code, Process.name, Tenant.id, Tenant.name)
            .having(func.count(ProcessKpi.id) > 3)
            .order_by(func.count(ProcessKpi.id).desc())
        )
        print("=== PG sayısı > 3 olan süreçler ===")
        for r in q.limit(25):
            print(f"  proc={r.id} tenant={r.tid} {r.tname!s} code={r.code!s} pg={r.nk} {str(r.name)[:40]}")

        q2 = (
            Process.query.join(Tenant)
            .filter(Process.is_active.is_(True))
            .with_entities(
                Process.id,
                Tenant.id.label("tid"),
                Tenant.name.label("tname"),
                func.count(KpiData.id).label("nd"),
            )
            .outerjoin(ProcessKpi, ProcessKpi.process_id == Process.id)
            .outerjoin(KpiData, KpiData.process_kpi_id == ProcessKpi.id)
            .group_by(Process.id, Tenant.id, Tenant.name)
            .having(func.count(KpiData.id) > 20)
            .order_by(func.count(KpiData.id).desc())
        )
        print()
        print("=== KpiData > 20 olan süreçler ===")
        for r in q2.limit(15):
            print(f"  proc={r.id} tenant={r.tid} {r.tname!s} kpi_data={r.nd}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--heavy":
        report_heavy_processes()
        raise SystemExit(0)
    raise SystemExit(main())
