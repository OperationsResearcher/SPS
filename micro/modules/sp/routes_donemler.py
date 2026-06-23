"""Stratejik Planlama — Dönem karşılaştırma."""

from functools import wraps

from flask import render_template, jsonify, request, current_app, session
from flask_login import login_required, current_user
from sqlalchemy.orm import selectinload

from platform_core import app_bp
from app.extensions import csrf
from app.models import db
from sqlalchemy import or_
from app.models.core import Strategy, SubStrategy, Tenant
from app.models.k_vektor import KVektorStrategyWeight, KVektorSubStrategyWeight
from app.services.k_vektor_config_service import (
    apply_single_strategy_k_vektor_weight,
    apply_single_sub_strategy_k_vektor_weight,
    k_vektor_weights_get_dict,
    save_k_vektor_weights,
)
from app.utils.db_sequence import is_pk_duplicate, sync_pg_sequence_if_needed
from app.models.process import Process, ProcessKpi
from app.models.plan_year import (
    PlanYear, KpiYearConfig,
    StrategyYearConfig, SubStrategyYearConfig, ProcessYearConfig,
)
from app.models.project import PlanProject, PlanProjectTask, PlanProjectActivity
from app.services.score_engine_service import compute_vision_score
from app.services.plan_year_service import (
    list_plan_years,
    get_plan_year,
    get_or_create_plan_year,
    close_plan_year,
    clone_plan_year,
    clone_full_plan_year,
    upsert_kpi_year_config,
    get_active_plan_year_for_user,
)
from app.models.tenant_year import TenantYearIdentity

_SP_ROLES = (
    "Admin",
    "admin",
    "tenant_admin",
    "executive_manager",
    "kurum_yoneticisi",
    "ust_yonetim",
)
from micro.modules.sp.helpers import (
    _check_sp_role,
    sp_manage_required,
    _plan_year_to_dict,
    _plan_project_to_dict,
    _plan_task_to_dict,
)

@app_bp.route("/sp/periods")
@login_required
def sp_donemler():
    """SP Dönem yönetimi sayfası."""
    import datetime as _dt
    tenant = current_user.tenant
    tenant_id = current_user.tenant_id
    plan_year_feature = bool(getattr(tenant, "plan_year_enabled", False)) if tenant else False
    current_cal_year = _dt.date.today().year

    if plan_year_feature and tenant_id:
        plan_years_list = list_plan_years(tenant_id)
        active_plan_year_val = session.get("sp_active_year", current_cal_year)
        available_years = [py.year for py in plan_years_list]
        if available_years and active_plan_year_val not in available_years:
            active_plan_year_val = available_years[0]
        active_plan_year_obj = get_plan_year(tenant_id, active_plan_year_val)
    else:
        plan_years_list = []
        active_plan_year_val = current_cal_year
        active_plan_year_obj = None

    return render_template(
        "platform/sp/donemler.html",
        plan_year_feature=plan_year_feature,
        plan_years=plan_years_list,
        active_plan_year=active_plan_year_obj,
        active_plan_year_val=active_plan_year_val,
        current_cal_year=current_cal_year,
        sp_can_manage=_check_sp_role(),
    )


@app_bp.route("/sp/api/period-compare", methods=["GET"])
@login_required
def sp_api_donem_karsilastir():
    """İki stratejik plan dönemini karşılaştırır ve farkları döner."""
    tid = current_user.tenant_id
    y1 = request.args.get("y1", type=int)
    y2 = request.args.get("y2", type=int)

    if not y1 or not y2:
        return jsonify({"success": False, "message": "İki dönem yılı gerekli (y1, y2)."}), 400
    if y1 == y2:
        return jsonify({"success": False, "message": "Aynı dönemi karşılaştıramazsınız."}), 400

    py1 = get_plan_year(tid, y1)
    py2 = get_plan_year(tid, y2)

    if not py1:
        return jsonify({"success": False, "message": f"{y1} dönemi bulunamadı."}), 404
    if not py2:
        return jsonify({"success": False, "message": f"{y2} dönemi bulunamadı."}), 404

    def _status_label(s):
        return {"active": "Aktif", "closed": "Kapalı", "draft": "Taslak", "archived": "Arşiv"}.get(s, s or "—")

    def _fmt_date(dt):
        return dt.strftime("%d.%m.%Y") if dt else "—"

    # ── Meta karşılaştırması ───────────────────────────────────────────────────
    meta_diffs = []
    meta_fields = [
        ("Ad",           py1.name or f"{py1.year} Stratejik Planı", py2.name or f"{py2.year} Stratejik Planı"),
        ("Durum",        _status_label(py1.status),                  _status_label(py2.status)),
        ("Oluşturulma",  _fmt_date(py1.created_at),                  _fmt_date(py2.created_at)),
        ("Kapanış",      _fmt_date(py1.closed_at),                   _fmt_date(py2.closed_at)),
    ]
    for field, v1, v2 in meta_fields:
        meta_diffs.append({"field": field, "y1": v1, "y2": v2, "changed": v1 != v2})

    # ── Yardımcı: source_id eşleştirmesi ─────────────────────────────────────
    def _match_pairs(items1, items2, src_attr):
        """
        Full Clone mimarisinde iki yılın kayıtlarını source_*_id ile eşleştirir.
        Döner: [(item1_or_None, item2_or_None), ...]
        """
        by_id1 = {x.id: x for x in items1}
        by_id2 = {x.id: x for x in items2}
        matched1, matched2 = set(), set()
        pairs = []

        # Y2 → Y1 yönü (Y2 klonlandıysa Y1'den)
        for x2 in items2:
            src = getattr(x2, src_attr, None)
            if src and src in by_id1:
                pairs.append((by_id1[src], x2))
                matched1.add(by_id1[src].id)
                matched2.add(x2.id)

        # Y1 → Y2 yönü (Y1 klonlandıysa Y2'den — ters sıra)
        for x1 in items1:
            if x1.id in matched1:
                continue
            src = getattr(x1, src_attr, None)
            if src and src in by_id2 and by_id2[src].id not in matched2:
                pairs.append((x1, by_id2[src]))
                matched1.add(x1.id)
                matched2.add(by_id2[src].id)

        # Ortak kaynak varsa (ikisi de aynı atadan)
        src_to_x1 = {}
        for x1 in items1:
            if x1.id in matched1:
                continue
            src = getattr(x1, src_attr, None)
            if src:
                src_to_x1[src] = x1
        for x2 in items2:
            if x2.id in matched2:
                continue
            src = getattr(x2, src_attr, None)
            if src and src in src_to_x1:
                x1 = src_to_x1[src]
                pairs.append((x1, x2))
                matched1.add(x1.id)
                matched2.add(x2.id)

        # Sadece Y1'de olanlar
        for x1 in items1:
            if x1.id not in matched1:
                pairs.append((x1, None))

        # Sadece Y2'de olanlar
        for x2 in items2:
            if x2.id not in matched2:
                pairs.append((None, x2))

        # Legacy/overlay kayıtlar: iki yılda da aynı fiziksel satır (aynı id) kullanılmış olabilir.
        # Böyle durumlarda aynı id'leri eşleştirip yalancı "sadece Y1/Y2" farkını önle.
        if pairs:
            only_1 = [a for a, b in pairs if a is not None and b is None]
            only_2 = [b for a, b in pairs if a is None and b is not None]
            by_id_only_2 = {x.id: x for x in only_2}
            repacked = []
            used_2 = set()
            for a, b in pairs:
                if a is not None and b is None and a.id in by_id_only_2:
                    b2 = by_id_only_2[a.id]
                    repacked.append((a, b2))
                    used_2.add(b2.id)
                elif a is None and b is not None and b.id in used_2:
                    continue
                else:
                    repacked.append((a, b))
            pairs = repacked

        return pairs

    # ── Strateji karşılaştırması (strategies tablosu, plan_year_id ile) ──────
    from app.models.core import Strategy as _Strategy, SubStrategy as _SubStrategy
    from app.models.process import Process as _Process, ProcessKpi as _ProcessKpi

    strats1 = _Strategy.query.filter_by(tenant_id=tid, plan_year_id=py1.id, is_active=True).all()
    strats2 = _Strategy.query.filter_by(tenant_id=tid, plan_year_id=py2.id, is_active=True).all()

    strategy_diffs = []
    for s1, s2 in _match_pairs(strats1, strats2, "source_strategy_id"):
        only_in_y1 = s2 is None
        only_in_y2 = s1 is None
        title = (s1 or s2).title
        changed_fields = []
        if s1 and s2:
            if (s1.title or "") != (s2.title or ""):
                changed_fields.append(("Başlık", s1.title or "—", s2.title or "—"))
            if (s1.code or "") != (s2.code or ""):
                changed_fields.append(("Kod", s1.code or "—", s2.code or "—"))
            if (s1.description or "").strip() != (s2.description or "").strip():
                changed_fields.append(("Açıklama", "değişti", "değişti"))
        changed = only_in_y1 or only_in_y2 or bool(changed_fields)
        strategy_diffs.append({
            "title": title,
            "only_in_y1": only_in_y1,
            "only_in_y2": only_in_y2,
            "changed_fields": changed_fields,
            "y1": {"code": s1.code if s1 else None, "title": s1.title if s1 else None},
            "y2": {"code": s2.code if s2 else None, "title": s2.title if s2 else None},
            "changed": changed,
        })

    # ── Alt strateji karşılaştırması ──────────────────────────────────────────
    # Y1/Y2 stratejilerinden alt stratejilere ulaş
    s1_ids = [s.id for s in strats1]
    s2_ids = [s.id for s in strats2]

    ss1 = (_SubStrategy.query
           .filter(_SubStrategy.strategy_id.in_(s1_ids), _SubStrategy.is_active.is_(True))
           .all()) if s1_ids else []
    ss2 = (_SubStrategy.query
           .filter(_SubStrategy.strategy_id.in_(s2_ids), _SubStrategy.is_active.is_(True))
           .all()) if s2_ids else []

    ss_diffs = []
    for s1, s2 in _match_pairs(ss1, ss2, "source_sub_strategy_id"):
        only_in_y1 = s2 is None
        only_in_y2 = s1 is None
        title = (s1 or s2).title
        changed_fields = []
        if s1 and s2:
            if (s1.title or "") != (s2.title or ""):
                changed_fields.append(("Başlık", s1.title or "—", s2.title or "—"))
            if (s1.code or "") != (s2.code or ""):
                changed_fields.append(("Kod", s1.code or "—", s2.code or "—"))
            if (s1.description or "").strip() != (s2.description or "").strip():
                changed_fields.append(("Açıklama", "değişti", "değişti"))
        changed = only_in_y1 or only_in_y2 or bool(changed_fields)
        ss_diffs.append({
            "title": title,
            "only_in_y1": only_in_y1,
            "only_in_y2": only_in_y2,
            "changed_fields": changed_fields,
            "y1": {"code": s1.code if s1 else None, "title": s1.title if s1 else None},
            "y2": {"code": s2.code if s2 else None, "title": s2.title if s2 else None},
            "changed": changed,
        })

    # ── Süreç + KPI karşılaştırması (süreç bazında gruplu) ───────────────────
    # Legacy uyumluluk: plan_year_id NULL süreçler iki yıl için de ortak taban kabul edilir.
    procs1 = _Process.query.filter(
        _Process.tenant_id == tid,
        _Process.is_active.is_(True),
        or_(_Process.plan_year_id == py1.id, _Process.plan_year_id.is_(None)),
    ).all()
    procs2 = _Process.query.filter(
        _Process.tenant_id == tid,
        _Process.is_active.is_(True),
        or_(_Process.plan_year_id == py2.id, _Process.plan_year_id.is_(None)),
    ).all()

    # KPI karşılaştırmasında process_kpi.plan_year_id dolu olmayan legacy kayıtlar da dikkate alınmalı.
    p1_ids = [p.id for p in procs1]
    p2_ids = [p.id for p in procs2]
    kpis1_all = (
        _ProcessKpi.query
        .filter(_ProcessKpi.process_id.in_(p1_ids), _ProcessKpi.is_active.is_(True))
        .all()
    ) if p1_ids else []
    kpis2_all = (
        _ProcessKpi.query
        .filter(_ProcessKpi.process_id.in_(p2_ids), _ProcessKpi.is_active.is_(True))
        .all()
    ) if p2_ids else []

    # Yıllık KPI config'leri (is_included/weight/target vb.) karşılaştırmaya dahil et.
    all_kpi_ids = list({k.id for k in (kpis1_all + kpis2_all)})
    cfg1_map = {}
    cfg2_map = {}
    if all_kpi_ids:
        cfg1_map = {
            c.process_kpi_id: c
            for c in KpiYearConfig.query.filter(
                KpiYearConfig.plan_year_id == py1.id,
                KpiYearConfig.process_kpi_id.in_(all_kpi_ids),
            ).all()
        }
        cfg2_map = {
            c.process_kpi_id: c
            for c in KpiYearConfig.query.filter(
                KpiYearConfig.plan_year_id == py2.id,
                KpiYearConfig.process_kpi_id.in_(all_kpi_ids),
            ).all()
        }

    kpis1_by_proc = {}
    for k in kpis1_all:
        kpis1_by_proc.setdefault(k.process_id, []).append(k)
    kpis2_by_proc = {}
    for k in kpis2_all:
        kpis2_by_proc.setdefault(k.process_id, []).append(k)

    def _kpi_diff(k1, k2):
        only_in_y1 = k2 is None
        only_in_y2 = k1 is None
        title = (k1 or k2).name
        changed_fields = []
        if k1 and k2:
            cfg1 = cfg1_map.get(k1.id)
            cfg2 = cfg2_map.get(k2.id)

            t1 = cfg1.target_value if (cfg1 and cfg1.target_value is not None) else k1.target_value
            t2 = cfg2.target_value if (cfg2 and cfg2.target_value is not None) else k2.target_value
            if (t1 or "") != (t2 or ""):
                changed_fields.append(("Hedef", t1 or "—", t2 or "—"))

            u1 = cfg1.unit if (cfg1 and cfg1.unit is not None) else k1.unit
            u2 = cfg2.unit if (cfg2 and cfg2.unit is not None) else k2.unit
            if (u1 or "") != (u2 or ""):
                changed_fields.append(("Birim", u1 or "—", u2 or "—"))

            d1 = cfg1.direction if (cfg1 and cfg1.direction is not None) else k1.direction
            d2 = cfg2.direction if (cfg2 and cfg2.direction is not None) else k2.direction
            if (d1 or "") != (d2 or ""):
                changed_fields.append(("Yön", d1 or "—", d2 or "—"))

            p1 = cfg1.period if (cfg1 and cfg1.period is not None) else k1.period
            p2 = cfg2.period if (cfg2 and cfg2.period is not None) else k2.period
            if (p1 or "") != (p2 or ""):
                changed_fields.append(("Periyot", p1 or "—", p2 or "—"))

            w1 = cfg1.weight if (cfg1 and cfg1.weight is not None) else (k1.weight or 0)
            w2 = cfg2.weight if (cfg2 and cfg2.weight is not None) else (k2.weight or 0)
            if abs(round(w1 or 0, 3) - round(w2 or 0, 3)) > 0.001:
                changed_fields.append(("Ağırlık", str(w1), str(w2)))

            inc1 = cfg1.is_included if cfg1 is not None else True
            inc2 = cfg2.is_included if cfg2 is not None else True
            if bool(inc1) != bool(inc2):
                changed_fields.append(("Plana Dahil", "Evet" if inc1 else "Hayır", "Evet" if inc2 else "Hayır"))

            if (k1.name or "") != (k2.name or ""):
                changed_fields.append(("Ad", k1.name or "—", k2.name or "—"))
        return {
            "title": title,
            "only_in_y1": only_in_y1,
            "only_in_y2": only_in_y2,
            "changed_fields": changed_fields,
            "changed": only_in_y1 or only_in_y2 or bool(changed_fields),
        }

    process_diffs = []
    for p1, p2 in _match_pairs(procs1, procs2, "source_process_id"):
        only_in_y1 = p2 is None
        only_in_y2 = p1 is None
        title = (p1 or p2).name
        changed_fields = []
        if p1 and p2:
            if (p1.name or "") != (p2.name or ""):
                changed_fields.append(("Ad", p1.name or "—", p2.name or "—"))
            if (p1.code or "") != (p2.code or ""):
                changed_fields.append(("Kod", p1.code or "—", p2.code or "—"))
            if abs(round(p1.weight or 0, 3) - round(p2.weight or 0, 3)) > 0.001:
                changed_fields.append(("Ağırlık", str(p1.weight), str(p2.weight)))
            if (p1.status or "") != (p2.status or ""):
                changed_fields.append(("Durum", p1.status or "—", p2.status or "—"))

        # Bu sürece ait KPI çiftlerini eşleştir
        p1_kpis = kpis1_by_proc.get(p1.id, []) if p1 else []
        p2_kpis = kpis2_by_proc.get(p2.id, []) if p2 else []
        kpi_diffs = [_kpi_diff(k1, k2) for k1, k2 in _match_pairs(p1_kpis, p2_kpis, "source_kpi_id")]

        proc_changed = only_in_y1 or only_in_y2 or bool(changed_fields) or any(k["changed"] for k in kpi_diffs)
        process_diffs.append({
            "title": title,
            "only_in_y1": only_in_y1,
            "only_in_y2": only_in_y2,
            "changed_fields": changed_fields,
            "kpis": kpi_diffs,
            "changed": proc_changed,
        })

    # ── Kimlik alanları karşılaştırması (Misyon, Vizyon, Değerler…) ────────────
    from app.models.tenant_year import TenantYearIdentity
    ident1 = TenantYearIdentity.query.filter_by(plan_year_id=py1.id).first()
    ident2 = TenantYearIdentity.query.filter_by(plan_year_id=py2.id).first()

    _IDENTITY_FIELDS = [
        ("Misyon / Amaç",    "purpose"),
        ("Vizyon",           "vision"),
        ("Değerler",         "core_values"),
        ("Etik Kurallar",    "code_of_ethics"),
        ("Kalite Politikası","quality_policy"),
    ]
    identity_diffs = []
    for label, attr in _IDENTITY_FIELDS:
        v1 = getattr(ident1, attr, None) if ident1 else None
        v2 = getattr(ident2, attr, None) if ident2 else None
        v1 = v1.strip() if v1 else None
        v2 = v2.strip() if v2 else None
        changed = (bool(v1) != bool(v2)) or (v1 or "") != (v2 or "")
        identity_diffs.append({
            "field": label,
            "y1_filled": bool(v1),
            "y2_filled": bool(v2),
            "y1_preview": v1[:150] if v1 else None,
            "y2_preview": v2[:150] if v2 else None,
            "changed": changed,
        })

    def _count_changed(lst):
        return sum(1 for x in lst if x["changed"])

    # ── Initiative (çok yıllık, span tabanlı) ────────────────────────────────
    from app.models.initiative import Initiative as _Initiative
    inits1 = _Initiative.query.filter(
        _Initiative.tenant_id == tid,
        _Initiative.is_active.is_(True),
        _Initiative.start_year <= y1, _Initiative.end_year >= y1,
    ).all()
    inits2 = _Initiative.query.filter(
        _Initiative.tenant_id == tid,
        _Initiative.is_active.is_(True),
        _Initiative.start_year <= y2, _Initiative.end_year >= y2,
    ).all()
    ids1 = {i.id for i in inits1}
    ids2 = {i.id for i in inits2}
    initiatives_block = {
        "y1_total": len(inits1), "y2_total": len(inits2),
        "started_in_y2": [{"id": i.id, "label": f"{i.code or ''} {i.name}".strip()}
                          for i in inits2 if i.id not in ids1],
        "ended_before_y2": [{"id": i.id, "label": f"{i.code or ''} {i.name}".strip()}
                            for i in inits1 if i.id not in ids2],
        "continuing": len(ids1 & ids2),
    }

    # ── OKR & Süreç-Alt Strateji bağ sayımı ──────────────────────────────────
    from app.models.okr import OkrObjective as _OkrObjective
    from app.models.process import ProcessSubStrategyLink as _PSSLink
    okr1 = _OkrObjective.query.filter_by(tenant_id=tid, plan_year_id=py1.id, is_active=True).count()
    okr2 = _OkrObjective.query.filter_by(tenant_id=tid, plan_year_id=py2.id, is_active=True).count()
    p1_ids = [p.id for p in procs1] or [0]
    p2_ids = [p.id for p in procs2] or [0]
    links1 = _PSSLink.query.filter(_PSSLink.process_id.in_(p1_ids)).count()
    links2 = _PSSLink.query.filter(_PSSLink.process_id.in_(p2_ids)).count()

    return jsonify({
        "success": True,
        "y1": _plan_year_to_dict(py1),
        "y2": _plan_year_to_dict(py2),
        "summary": {
            "identity_changed": _count_changed(identity_diffs),
            "meta_changed": sum(1 for m in meta_diffs if m["changed"]),
            "strategies_changed": _count_changed(strategy_diffs),
            "sub_strategies_changed": _count_changed(ss_diffs),
            "processes_changed": sum(1 for p in process_diffs if p["changed"]),
            "kpis_changed": sum(1 for p in process_diffs for k in p["kpis"] if k["changed"]),
            "initiatives_new_in_y2": len(initiatives_block["started_in_y2"]),
            "initiatives_ended_before_y2": len(initiatives_block["ended_before_y2"]),
            "okr_y1": okr1, "okr_y2": okr2,
            "links_y1": links1, "links_y2": links2,
        },
        "diff": {
            "identity": identity_diffs,
            "meta": meta_diffs,
            "strategies": strategy_diffs,
            "sub_strategies": ss_diffs,
            "processes": process_diffs,
            "initiatives": initiatives_block,
            "okr": {"y1_count": okr1, "y2_count": okr2},
            "links": {"y1_count": links1, "y2_count": links2},
        },
    })



# ─── Sprint 54 (Ö1): Çeyreklik Review Wizard ─────────────────────────────────

@app_bp.route("/sp/ceyreklik-review")
@login_required
def sp_quarterly_review_page():
    """Çeyreklik review sayfası."""
    if not _check_sp_role(current_user):
        return render_template("errors/403.html"), 403
    import datetime as _dt
    now = _dt.date.today()
    current_quarter = (now.month - 1) // 3 + 1
    return render_template(
        "platform/sp/ceyreklik_review.html",
        default_year=now.year,
        default_quarter=current_quarter,
    )


@app_bp.route("/sp/api/quarterly-review")
@login_required
def sp_api_quarterly_review():
    """Çeyreklik review JSON."""
    if not _check_sp_role(current_user):
        return jsonify({"error": "yetki yok"}), 403
    year = request.args.get("year", type=int)
    quarter = request.args.get("quarter", type=int)
    if not year or quarter not in (1, 2, 3, 4):
        return jsonify({"error": "year ve quarter (1-4) zorunlu"}), 400
    try:
        from app.services.quarterly_review_service import build_quarterly_review
        data = build_quarterly_review(current_user.tenant_id, year, quarter)
        return jsonify({"success": True, "review": data.to_dict()})
    except Exception as e:
        current_app.logger.error(f"quarterly_review error: {e}", exc_info=True)
        return jsonify({"success": False, "message": "İşlem tamamlanamadı."}), 500
