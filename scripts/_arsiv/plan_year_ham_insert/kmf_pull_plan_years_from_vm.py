# -*- coding: utf-8 -*-
"""VM (sps-web) tenant plan_years -> yerel DB (aynı tenant_id). gcloud gerekir."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _gcloud() -> str | None:
    for name in ("gcloud", "gcloud.cmd", "gcloud.exe"):
        p = shutil.which(name)
        if p:
            return p
    for base in (
        Path(r"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin"),
        Path(r"C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin"),
    ):
        for n in ("gcloud.cmd", "gcloud.exe"):
            if (base / n).is_file():
                return str(base / n)
    return None


def main() -> int:
    tid = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    g = _gcloud()
    if not g:
        print("gcloud yok", file=sys.stderr)
        return 1
    vm_script = "/tmp/dump_py_plan_years.py"
    local_tmp = ROOT / "backups" / "kmf_hybrid_sync" / "_dump_plan_years_vm.py"
    local_tmp.parent.mkdir(parents=True, exist_ok=True)
    local_tmp.write_text(
        f"import json, sys\nsys.path.insert(0, '/app')\n"
        "from app import create_app\nfrom sqlalchemy import text\nfrom extensions import db\n"
        "from services.tenant_backup_service import _serialize\n"
        "tid = int(sys.argv[1])\napp = create_app()\n"
        "with app.app_context():\n"
        "    res = db.session.execute(\n"
        "        text('SELECT * FROM plan_years WHERE tenant_id = :tid ORDER BY year'),\n"
        "        {'tid': tid},\n"
        "    )\n"
        "    cols = list(res.keys())\n"
        "    rows = [{c: _serialize(v) for c, v in zip(cols, row)} for row in res.fetchall()]\n"
        "print(json.dumps({'tenant_id': tid, 'rows': rows}, ensure_ascii=False))\n",
        encoding="utf-8",
    )
    subprocess.run(
        [g, "compute", "scp", str(local_tmp), f"sps-server-v2:{vm_script}", "--zone=europe-west3-c"],
        check=True,
    )
    inner = (
        f"sudo docker cp {vm_script} sps-web:/tmp/dump_py_plan_years.py "
        f"&& sudo docker exec sps-web bash -lc 'cd /app && python3 /tmp/dump_py_plan_years.py {tid}'"
    )
    p = subprocess.run(
        [g, "compute", "ssh", "sps-server-v2", "--zone=europe-west3-c", "--command", inner],
        capture_output=True,
        encoding="utf-8",
        check=True,
    )
    snap = json.loads(p.stdout.strip())
    outf = ROOT / "backups" / "kmf_hybrid_sync" / f"plan_years_from_vm_tenant_{tid}.json"
    outf.write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")

    from app import create_app
    from services.tenant_backup_service import _coerce_row_bind_params
    from sqlalchemy import text

    from extensions import db

    app = create_app()
    rows = snap.get("rows") or []
    if not rows:
        print("VM'de plan_years yok")
        return 1
    with app.app_context():
        db.session.execute(text("DELETE FROM plan_years WHERE tenant_id = :tid"), {"tid": tid})
        for r in sorted(rows, key=lambda x: int(x["id"])):
            ts = r.get("template_source_id")
            bind = _coerce_row_bind_params(
                {
                    "id": int(r["id"]),
                    "tenant_id": tid,
                    "year": int(r["year"]),
                    "name": r.get("name"),
                    "status": r.get("status") or "active",
                    "template_source_id": ts,
                    "created_at": r.get("created_at"),
                    "closed_at": r.get("closed_at"),
                }
            )
            db.session.execute(
                text(
                    "INSERT INTO plan_years "
                    '(id, tenant_id, year, name, status, template_source_id, created_at, closed_at) '
                    "VALUES (:id, :tenant_id, :year, :name, :status, :template_source_id, "
                    ":created_at, :closed_at) ON CONFLICT (id) DO UPDATE SET "
                    "year = EXCLUDED.year, name = EXCLUDED.name, status = EXCLUDED.status, "
                    "template_source_id = EXCLUDED.template_source_id, "
                    "created_at = EXCLUDED.created_at, closed_at = EXCLUDED.closed_at"
                ),
                bind,
            )
        db.session.commit()
    print("Yerel plan_years guncellendi:", len(rows), "satir. Kaynak:", outf)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
