"""Plan Year Template Marketplace — uygulama servisi (Önerilen Hamle #4 — Ö11 başlangıcı).

JSON template'ı bir tenant'a uygular: PlanYear + identity + strategies + sub_strategies
kayıtlarını oluşturur. KPI library opsiyonel (process ataması manuel).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from extensions import db
from app.models.plan_year import PlanYear
from app.models.core import Strategy, SubStrategy
from app.models.tenant_year import TenantYearIdentity


TEMPLATE_DIR = Path(__file__).parent.parent / "templates_data"


def list_templates() -> list[dict]:
    """Mevcut template'ları listele."""
    out = []
    if not TEMPLATE_DIR.exists():
        return out
    for f in TEMPLATE_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            out.append({
                "code": data.get("code"),
                "name": data.get("name"),
                "description": data.get("description"),
                "sector": data.get("sector"),
                "period_years": data.get("period_years"),
                "strategy_count": len(data.get("strategies", [])),
                "kpi_count": len(data.get("kpi_library", [])),
                "file": f.name,
            })
        except Exception:
            continue
    return out


def get_template(code: str) -> Optional[dict]:
    for f in TEMPLATE_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if data.get("code") == code:
                return data
        except Exception:
            continue
    return None


def apply_template_to_tenant(
    tenant_id: int,
    template_code: str,
    target_year: int,
    overwrite_identity: bool = False,
) -> PlanYear:
    """Template'ı tenant + target_year için uygular. PlanYear döner."""
    data = get_template(template_code)
    if not data:
        raise ValueError(f"Template bulunamadı: {template_code}")

    # PlanYear oluştur (zaten varsa kullan)
    existing = PlanYear.query.filter_by(
        tenant_id=tenant_id, year=target_year, scenario_of_id=None
    ).first()
    if existing:
        py = existing
    else:
        py = PlanYear(
            tenant_id=tenant_id,
            year=target_year,
            name=f"{target_year} — {data.get('name', 'Stratejik Plan')}",
            status="draft",
        )
        db.session.add(py)
        db.session.flush()

    # Identity
    ident_data = data.get("identity", {})
    if ident_data:
        ident = TenantYearIdentity.query.filter_by(
            tenant_id=tenant_id, plan_year_id=py.id
        ).first()
        if not ident:
            ident = TenantYearIdentity(tenant_id=tenant_id, plan_year_id=py.id)
            db.session.add(ident)
        if overwrite_identity or not ident.purpose:
            ident.purpose = ident_data.get("purpose")
            ident.vision = ident_data.get("vision")
            ident.core_values = ident_data.get("core_values")
            ident.code_of_ethics = ident_data.get("code_of_ethics")

    # Stratejiler + alt stratejiler
    for s_data in data.get("strategies", []):
        existing_s = Strategy.query.filter_by(
            tenant_id=tenant_id, plan_year_id=py.id, code=s_data.get("code")
        ).first()
        if existing_s:
            strat = existing_s
        else:
            strat = Strategy(
                tenant_id=tenant_id,
                plan_year_id=py.id,
                code=s_data.get("code"),
                title=s_data.get("title"),
                description=s_data.get("description"),
                is_active=True,
            )
            db.session.add(strat)
            db.session.flush()

        for ss_data in s_data.get("sub_strategies", []):
            existing_ss = SubStrategy.query.filter_by(
                strategy_id=strat.id, code=ss_data.get("code")
            ).first()
            if existing_ss:
                continue
            ss = SubStrategy(
                strategy_id=strat.id,
                code=ss_data.get("code"),
                title=ss_data.get("title"),
                description=ss_data.get("description"),
                is_active=True,
            )
            db.session.add(ss)

    db.session.commit()
    return py
