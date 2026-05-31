#!/usr/bin/env python3
"""micro modül routes.py dosyalarını alt modüllere böler (tek seferlik bakım aracı)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _read(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines(keepends=True)


def _write(path: Path, parts: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(parts), encoding="utf-8")


def _slice(lines: list[str], start: int, end: int) -> list[str]:
    return lines[start - 1 : end]


def _module_header(doc: str, imports: list[str], helper_import: str) -> list[str]:
    """__future__ importları dosya başında kalmalı."""
    future = [ln for ln in imports if ln.startswith("from __future__")]
    rest = [ln for ln in imports if not ln.startswith("from __future__")]
    return [f'"""{doc}"""\n\n'] + future + rest + [helper_import]


def split_surec() -> None:
    src = ROOT / "micro/modules/surec/routes.py"
    lines = _read(src)
    imports = _slice(lines, 1, 55)
    helpers_body = _slice(lines, 57, 222)

    surec_helper_import = (
        "from micro.modules.surec.helpers import (\n"
        "    _apply_sub_strategy_links,\n"
        "    _is_kpi_data_audit_pk_duplicate,\n"
        "    _is_notification_pk_duplicate,\n"
        "    _is_process_activity_pk_duplicate,\n"
        "    _latest_delete_audit_by_kpi_data_ids,\n"
        "    _latest_update_audit_by_kpi_data_ids,\n"
        "    _parent_options_with_depth,\n"
        "    _process_for_user,\n"
        "    _user_can_add_activity,\n"
        "    _user_can_manage_activity,\n"
        "    _user_display_name,\n"
        "    _users_pick_json,\n"
        ")\n\n"
    )

    _write(
        ROOT / "micro/modules/surec/helpers.py",
        _module_header("Süreç modülü — ortak yardımcılar ve importlar.", imports, "")
        + helpers_body,
    )

    chunks = [
        ("routes_process.py", 224, 660, "Sayfa ve süreç CRUD"),
        ("routes_kpi.py", 662, 898, "KPI CRUD API"),
        ("routes_kpi_data.py", 900, 1358, "KPI veri (PGV) API"),
        ("routes_activity.py", 1360, 1830, "Faaliyet API"),
        ("routes_karne.py", 1832, 2207, "Karne ve yıl çözümleme API"),
        ("routes_legacy.py", 2210, 2230, "Eski /surec URL yönlendirmeleri"),
    ]
    for fname, start, end, doc in chunks:
        body = _slice(lines, start, end)
        _write(
            ROOT / f"micro/modules/surec/{fname}",
            _module_header(f"Süreç modülü — {doc}.", imports, surec_helper_import) + body,
        )

    aggregator = '''"""Süreç Yönetimi — rotalar alt modüllerde kayıtlıdır."""

from micro.modules.surec import routes_process  # noqa: F401
from micro.modules.surec import routes_kpi  # noqa: F401
from micro.modules.surec import routes_kpi_data  # noqa: F401
from micro.modules.surec import routes_activity  # noqa: F401
from micro.modules.surec import routes_karne  # noqa: F401
from micro.modules.surec import routes_legacy  # noqa: F401
'''
    (ROOT / "micro/modules/surec/routes.py").write_text(aggregator, encoding="utf-8")
    print("surec: split OK")


def split_sp() -> None:
    src = ROOT / "micro/modules/sp/routes.py"
    lines = _read(src)
    imports = _slice(lines, 1, 48)
    helpers = _slice(lines, 51, 65)

    _write(
        ROOT / "micro/modules/sp/helpers.py",
        _module_header("SP modülü — ortak yardımcılar.", imports, "") + helpers,
    )

    helper_import = (
        "from micro.modules.sp.helpers import _check_sp_role, sp_manage_required\n\n"
    )

    chunks = [
        ("routes_pages.py", 68, 296, "SP ana sayfa ve kurumsal kimlik"),
        ("routes_strategy.py", 299, 511, "Strateji ve alt strateji API"),
        ("routes_flow.py", 513, 645, "Strateji akışı sayfaları ve graf"),
        ("routes_plan_year.py", 647, 872, "Plan yılı API"),
        ("routes_donemler.py", 874, 1275, "Dönem karşılaştırma"),
        ("routes_sp_proje.py", 1277, 1453, "SP proje ve görev API"),
        ("routes_analysis.py", 1455, len(lines), "SWOT/TOWS/PESTLE/OKR/BSC API"),
    ]
    for fname, start, end, doc in chunks:
        body = _slice(lines, start, end)
        _write(
            ROOT / f"micro/modules/sp/{fname}",
            _module_header(f"Stratejik Planlama — {doc}.", imports, helper_import) + body,
        )

    # routes_plan_year and routes_analysis use _plan_year_to_dict, _plan_project_to_dict - in file
    aggregator = '''"""Stratejik Planlama — rotalar alt modüllerde kayıtlıdır."""

from micro.modules.sp import routes_pages  # noqa: F401
from micro.modules.sp import routes_strategy  # noqa: F401
from micro.modules.sp import routes_flow  # noqa: F401
from micro.modules.sp import routes_plan_year  # noqa: F401
from micro.modules.sp import routes_donemler  # noqa: F401
from micro.modules.sp import routes_sp_proje  # noqa: F401
from micro.modules.sp import routes_analysis  # noqa: F401
'''
    (ROOT / "micro/modules/sp/routes.py").write_text(aggregator, encoding="utf-8")
    print("sp: split OK")


if __name__ == "__main__":
    split_surec()
    split_sp()
