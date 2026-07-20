# -*- coding: utf-8 -*-
"""
Konteyner içi: JSON'daki plan_years satırlarını tenant_id için yazar.
Önce DELETE FROM plan_years WHERE tenant_id=:tid (CASCADE alt kayıtları siler).
Başka tenant'ların kullandığı id ile çakışma varsa tüm satırlar yeni id bloğuna taşınır;
template_source_id eşlemesi güncellenir.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

def _repo_root() -> Path:
    script = Path(__file__).resolve()
    for d in [script.parent, *script.parents]:
        if (d / "run.py").exists():
            return d
    if (Path("/app") / "run.py").exists():
        return Path("/app")
    raise RuntimeError("run.py bulunamadi (repo veya /app bekleniyor).")


ROOT = _repo_root()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import text  # noqa: E402

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402


def main() -> int:
    if len(sys.argv) < 2:
        print("Kullanim: vm_apply_plan_years.py <json_yolu>", file=sys.stderr)
        return 1
    path = Path(sys.argv[1])
    payload = json.loads(path.read_text(encoding="utf-8"))
    tenant_id = int(payload["tenant_id"])
    rows: list[dict] = payload["rows"]
    if not rows:
        print("rows bos", file=sys.stderr)
        return 1

    app = create_app()
    with app.app_context():
        r = db.session.execute(text("SELECT id FROM plan_years")).fetchall()
        used_ids = {int(row[0]) for row in r}
        incoming_ids = [int(r["id"]) for r in rows]
        need_remap = any(i in used_ids for i in incoming_ids)

        id_map: dict[int, int] = {}
        if need_remap:
            mx = db.session.execute(
                text("SELECT COALESCE(MAX(id), 0) FROM plan_years")
            ).scalar() or 0
            nxt = int(mx) + 1
            for r in sorted(rows, key=lambda x: int(x["id"])):
                oid = int(r["id"])
                id_map[oid] = nxt
                nxt += 1
        else:
            for r in rows:
                id_map[int(r["id"])] = int(r["id"])

        db.session.execute(
            text("DELETE FROM plan_years WHERE tenant_id = :tid"),
            {"tid": tenant_id},
        )
        db.session.commit()

        for r in sorted(rows, key=lambda x: int(x["id"])):
            oid = int(r["id"])
            nid = id_map[oid]
            ts = r.get("template_source_id")
            if ts is not None:
                ts = id_map.get(int(ts), int(ts))
            cols = {
                "id": nid,
                "tenant_id": tenant_id,
                "year": int(r["year"]),
                "name": r.get("name"),
                "status": r.get("status") or "active",
                "template_source_id": ts,
                "created_at": r.get("created_at"),
                "closed_at": r.get("closed_at"),
            }
            db.session.execute(
                text(
                    "INSERT INTO plan_years "
                    '(id, tenant_id, year, name, status, template_source_id, created_at, closed_at) '
                    "VALUES (:id, :tenant_id, :year, :name, :status, :template_source_id, "
                    ":created_at, :closed_at)"
                ),
                cols,
            )
        db.session.commit()

        try:
            db.session.execute(
                text(
                    "SELECT setval(pg_get_serial_sequence('plan_years', 'id'), "
                    "(SELECT COALESCE(MAX(id), 1) FROM plan_years))"
                )
            )
            db.session.commit()
        except Exception:
            db.session.rollback()

        print(
            json.dumps(
                {"tenant_id": tenant_id, "inserted": len(rows), "id_remap": need_remap},
                indent=2,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
