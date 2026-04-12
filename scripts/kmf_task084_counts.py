# -*- coding: utf-8 -*-
"""TASK-084 KMF dört sayı + plan_years (tenant varsayılan 16). VM/yerel psql karşılaştırması için."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_script = Path(__file__).resolve()
ROOT = _script.parents[1]
for d in (ROOT, Path("/app")):
    if (d / "run.py").exists():
        ROOT = d
        break
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import text  # noqa: E402

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402


def main() -> int:
    tid = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    app = create_app()
    with app.app_context():
        row = db.session.execute(
            text("SELECT id, name FROM tenants WHERE id = :tid"),
            {"tid": tid},
        ).mappings().first()
        out = {"tenant_id": tid, "tenant": dict(row) if row else None}
        if not row:
            print(json.dumps(out, ensure_ascii=False, indent=2))
            return 1
        u = db.session.execute(
            text("SELECT count(*) FROM users WHERE tenant_id=:tid"),
            {"tid": tid},
        ).scalar()
        p = db.session.execute(
            text("SELECT count(*) FROM processes WHERE tenant_id=:tid"),
            {"tid": tid},
        ).scalar()
        pk = db.session.execute(
            text(
                "SELECT count(*) FROM process_kpis pk "
                "JOIN processes pr ON pr.id = pk.process_id "
                "WHERE pr.tenant_id=:tid"
            ),
            {"tid": tid},
        ).scalar()
        pgv = db.session.execute(
            text(
                "SELECT count(*) FROM kpi_data kd "
                "JOIN process_kpis pk ON pk.id = kd.process_kpi_id "
                "JOIN processes pr ON pr.id = pk.process_id "
                "WHERE pr.tenant_id=:tid AND kd.deleted_at IS NULL"
            ),
            {"tid": tid},
        ).scalar()
        py = db.session.execute(
            text("SELECT count(*) FROM plan_years WHERE tenant_id=:tid"),
            {"tid": tid},
        ).scalar()
        st = db.session.execute(
            text("SELECT count(*) FROM strategies WHERE tenant_id=:tid"),
            {"tid": tid},
        ).scalar()
        sst = db.session.execute(
            text(
                "SELECT count(*) FROM sub_strategies ss "
                "JOIN strategies s ON s.id = ss.strategy_id "
                "WHERE s.tenant_id=:tid"
            ),
            {"tid": tid},
        ).scalar()
        out["kullanici"] = int(u)
        out["surec"] = int(p)
        out["pg"] = int(pk)
        out["pgv"] = int(pgv)
        out["plan_years"] = int(py)
        out["strateji"] = int(st)
        out["alt_strateji"] = int(sst)
        print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
