#!/usr/bin/env python3
"""split_module_routes sonrası çift docstring / import düzeltmesi."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SP_IMPORT = """from micro.modules.sp.helpers import (
    _check_sp_role,
    sp_manage_required,
    _plan_year_to_dict,
    _plan_project_to_dict,
    _plan_task_to_dict,
)

"""
OLD_SP = "from micro.modules.sp.helpers import _check_sp_role, sp_manage_required\n\n"


def main() -> None:
    for p in (ROOT / "micro/modules/sp").glob("routes_*.py"):
        t = p.read_text(encoding="utf-8")
        t = t.replace('"""Stratejik Planlama modülü."""\n\n', "", 1)
        t = t.replace(OLD_SP, SP_IMPORT)
        p.write_text(t, encoding="utf-8")

    for p in (ROOT / "micro/modules/surec").glob("routes_*.py"):
        t = p.read_text(encoding="utf-8")
        t = t.replace('"""Süreç Yönetimi modülü."""\n\n', "", 1)
        p.write_text(t, encoding="utf-8")

    proje = ROOT / "micro/modules/sp/routes_sp_proje.py"
    t = proje.read_text(encoding="utf-8")
    marker = "# ── Yardımcılar"
    if marker in t:
        proje.write_text(t[: t.index(marker)].rstrip() + "\n", encoding="utf-8")
    print("fixed headers")


if __name__ == "__main__":
    main()
