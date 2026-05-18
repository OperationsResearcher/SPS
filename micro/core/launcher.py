"""Launcher — kök ana sayfa (modül seçim ekranı)."""

import datetime

from flask import render_template, session as flask_session
from flask_login import login_required, current_user

from platform_core import app_bp
from app_platform.core.module_registry import get_accessible_modules


_SP_MANAGE_ROLES = ("Admin", "admin", "tenant_admin", "executive_manager", "kurum_yoneticisi", "ust_yonetim")


def _get_plan_year_context():
    """Launcher için plan year context verisini hazırlar."""
    tenant = current_user.tenant
    tenant_id = current_user.tenant_id
    current_cal_year = datetime.date.today().year

    if not (tenant and getattr(tenant, "plan_year_enabled", False) and tenant_id):
        return dict(
            plan_year_feature=False,
            plan_years=[],
            active_plan_year=None,
            active_plan_year_val=current_cal_year,
            sp_can_manage=False,
            current_cal_year=current_cal_year,
        )

    try:
        from app.services.plan_year_service import list_plan_years, get_plan_year
        plan_years_list = list_plan_years(tenant_id)
        active_plan_year_val = flask_session.get("sp_active_year", current_cal_year)
        available_years = [py.year for py in plan_years_list]
        if available_years and active_plan_year_val not in available_years:
            active_plan_year_val = available_years[0]
        active_plan_year_obj = get_plan_year(tenant_id, active_plan_year_val)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"[launcher] plan_year load error: {e}")
        plan_years_list = []
        active_plan_year_val = current_cal_year
        active_plan_year_obj = None

    return dict(
        plan_year_feature=True,
        plan_years=plan_years_list,
        active_plan_year=active_plan_year_obj,
        active_plan_year_val=active_plan_year_val,
        sp_can_manage=bool(current_user.role and current_user.role.name in _SP_MANAGE_ROLES),
        current_cal_year=current_cal_year,
    )


@app_bp.route("/launcher")
@app_bp.route("/masaustu-launcher")
@login_required
def launcher():
    """Modül launcher ekranı."""
    modules = get_accessible_modules(current_user)
    ctx = _get_plan_year_context()
    return render_template("platform/launcher.html", modules=modules, **ctx)


@app_bp.route("/")
def platform_root():
    """Kök URL — giriş yapmışsa launcher, yapmamışsa marketing."""
    from flask_login import current_user as _cu
    if _cu.is_authenticated:
        return redirect(url_for("app_bp.launcher"))
    # Marketing tanıtım sayfası
    return render_template(
        "marketing/index.html",
        page_title="Kokpitim — Stratejik Yönetim Platformu",
        page_description="Strateji, süreç, KPI ve bireysel performansı tek platformda yönetin.",
    )
