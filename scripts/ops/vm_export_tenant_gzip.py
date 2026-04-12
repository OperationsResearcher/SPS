# -*- coding: utf-8 -*-
"""Konteyner içi: tenant_id için tenant_backup_service.export_tenant_json → /tmp dosyası."""
from __future__ import annotations

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

from app import create_app  # noqa: E402
from services.tenant_backup_service import export_tenant_json  # noqa: E402


def main() -> int:
    if len(sys.argv) < 2:
        print("Kullanim: vm_export_tenant_gzip.py <tenant_id> [cikti_yolu]", file=sys.stderr)
        return 1
    tid = int(sys.argv[1])
    out = Path(sys.argv[2] if len(sys.argv) > 2 else f"/tmp/kmf_tenant_{tid}.json.gz")
    app = create_app()
    with app.app_context():
        raw = export_tenant_json(tid)
    out.write_bytes(raw)
    print(str(out.resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
