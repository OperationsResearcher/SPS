"""Süreç modülü — Karne ve yıl çözümleme API."""

from __future__ import annotations
from flask_babel import gettext as _

from datetime import datetime, timezone, date, timedelta
from io import BytesIO

from flask import render_template, jsonify, request, current_app, redirect, abort, send_file, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload

from platform_core import app_bp
from app.models import db
from sqlalchemy import or_, func as _sqla_func
from app.models.process import (
    Process,
    ProcessSubStrategyLink,
    ProcessKpi,
    ProcessActivity,
    ProcessActivityAssignee,
    ProcessActivityReminder,
    ActivityTrack,
    KpiData,
    KpiDataAudit,
    FavoriteKpi,
)
from app.models.core import User, Strategy, SubStrategy, Tenant
from app.services.plan_year_service import (
    get_plan_year, get_kpi_configs_bulk, get_active_plan_year_for_user, list_plan_years,
    upsert_kpi_year_config,
)
from app.services.score_engine_service import compute_process_scores_internal
from app.utils.audit_logger import AuditLogger
from app.utils.db_sequence import is_pk_duplicate, sync_kpi_data_related_sequences, sync_pg_sequence_if_needed
from app.utils.process_utils import (
    validate_process_parent_id,
    last_day_of_period,
    data_date_to_period_keys,
    validate_same_tenant_sub_strategies,
)
from utils.karne_hesaplamalar import (
    hesapla_basari_puani as _hesapla_basari_puani,
    parse_basari_puani_araliklari as _parse_bpa,
)

from app_platform.modules.surec.permissions import (
    accessible_processes_filter,
    can_crud_process_entity,
    user_can_access_process,
    user_can_crud_pg_and_activity,
    user_can_edit_kpi_data_row,
    user_can_edit_process_record,
    user_can_enter_pgv,
)
from micro.modules.surec.helpers import (
    _apply_sub_strategy_links,
    _is_kpi_data_audit_pk_duplicate,
    _is_notification_pk_duplicate,
    _is_process_activity_pk_duplicate,
    _latest_delete_audit_by_kpi_data_ids,
    _latest_update_audit_by_kpi_data_ids,
    _parent_options_with_depth,
    _process_for_user,
    _user_can_add_activity,
    _user_can_manage_activity,
    _user_display_name,
    _users_pick_json,
)

# ──────────────────────────────────────────────────
# API — Yıl değişimi: aynı kod → hedef yılın process_id'si
# ──────────────────────────────────────────────────

@app_bp.route("/process/api/resolve-for-year", methods=["GET"])
@login_required
def surec_api_resolve_for_year():
    """
    Karne yıl navigasyonu: mevcut process.code + hedef yıl → hedef yılın process_id.
    Query params: process_id=<int>, year=<int>
    Döner: {success, process_id, process_name, url}
    """
    src_id = request.args.get("process_id", type=int)
    year   = request.args.get("year", type=int)
    if not src_id or not year:
        return jsonify({"success": False, "message": "process_id ve year zorunlu."}), 400

    src = Process.query.filter_by(
        id=src_id, tenant_id=current_user.tenant_id, is_active=True
    ).first()
    if not src:
        return jsonify({"success": False, "message": _("Süreç bulunamadı.")}), 404

    # Hedef plan year
    target_py = get_plan_year(current_user.tenant_id, year)
    if not target_py:
        return jsonify({"success": False, "message": f"{year} yılı SPDönemi bulunamadı."}), 404

    # Aynı code'lu süreci o yılda bul
    target = None
    if src.code:
        target = Process.query.filter_by(
            tenant_id=current_user.tenant_id,
            code=src.code,
            plan_year_id=target_py.id,
            is_active=True,
        ).first()

    # code yoksa ya da bulunamazsa — source_id zinciriyle traverse et
    if not target:
        # source_id chain: mevcut süreçten kaynak yıla git, hedef yılı bul
        target = _resolve_process_by_source_chain(src, target_py.id)

    if not target:
        return jsonify({
            "success": False,
            "message": f"Bu süreç {year} döneminde bulunamadı.",
            "year": year,
        }), 404

    from flask import url_for as _url_for
    return jsonify({
        "success": True,
        "process_id": target.id,
        "process_name": target.name,
        "url": _url_for("app_bp.surec_karne", process_id=target.id),
    })


def _resolve_process_by_source_chain(proc: Process, target_plan_year_id: int):
    """
    Verilen sürecin kaynak zincirini takip ederek target_plan_year_id'ye ait
    klonunu bulur. Tenant'ın tüm source_process_id zincirini tek sorguda çeker.
    """
    tid = proc.tenant_id

    # Tenant'ın tüm klonlu süreçlerini tek sorguda çek (source_process_id != NULL olanlar)
    all_clones: list[Process] = (
        Process.query
        .filter(
            Process.tenant_id == tid,
            Process.is_active.is_(True),
            Process.source_process_id.isnot(None),
        )
        .with_entities(
            Process.id,
            Process.source_process_id,
            Process.plan_year_id,
            Process.code,
        )
        .all()
    )

    # Lookup yapıları: id→row, source→children
    by_id: dict[int, object] = {}
    children_of: dict[int, list] = {}
    for row in all_clones:
        by_id[row.id] = row
        children_of.setdefault(row.source_process_id, []).append(row)

    # Kökü bul: source_process_id zincirinde NULL'a ulaş (by_id'de olmayan id kök)
    root_id = proc.id
    visited_up = {proc.id}
    cur = by_id.get(proc.id)
    while cur and cur.source_process_id:
        if cur.source_process_id in visited_up:
            break
        visited_up.add(cur.source_process_id)
        parent = by_id.get(cur.source_process_id)
        if not parent:
            root_id = cur.source_process_id
            break
        cur = parent
        root_id = cur.id

    # BFS: kökten hedef plan_year_id'yi bul (bellekte, DB'ye gitmeden)
    from collections import deque
    queue = deque([root_id])
    seen = {root_id}

    # Kök doğrudan hedef yıla ait olabilir — tek sorguyla kontrol et
    root_proc = Process.query.filter_by(id=root_id, plan_year_id=target_plan_year_id).first()
    if root_proc:
        return root_proc

    while queue:
        node_id = queue.popleft()
        for ch in children_of.get(node_id, []):
            if ch.id in seen:
                continue
            seen.add(ch.id)
            if ch.plan_year_id == target_plan_year_id:
                return Process.query.get(ch.id)
            queue.append(ch.id)
    return None


# ──────────────────────────────────────────────────
# API — Karne AJAX verisi
# ──────────────────────────────────────────────────

@app_bp.route("/process/api/karne/<int:process_id>", methods=["GET"])
@login_required
def surec_api_karne(process_id):
    """Karne sayfasının yıl bazlı KPI + faaliyet aylık takip verisini döner."""
    p = _process_for_user(process_id)
    if not p:
        abort(404)
    if not user_can_access_process(current_user, p):
        abort(403)
    year = request.args.get("year", datetime.now().year, type=int)

    # Seçili yıla ait plan_year'ı çöz (varsa) — PG'leri buna göre filtrele
    _py_for_year = None
    if current_user.tenant_id:
        try:
            _py_for_year = get_plan_year(current_user.tenant_id, year)
        except Exception:
            _py_for_year = None

    kpis_q = (
        ProcessKpi.query
        .options(
            selectinload(ProcessKpi.sub_strategy).selectinload(SubStrategy.strategy),
        )
        .filter_by(process_id=p.id, is_active=True)
    )
    if _py_for_year is not None:
        # PG plan_year'a bağlıysa eşleşmeli; legacy (NULL) PG'ler her zaman gösterilir
        kpis_q = kpis_q.filter(
            (ProcessKpi.plan_year_id == _py_for_year.id) | (ProcessKpi.plan_year_id.is_(None))
        )
    kpis = kpis_q.all()
    activities = (
        ProcessActivity.query
        .options(
            selectinload(ProcessActivity.assignment_links).selectinload(ProcessActivityAssignee.user),
            selectinload(ProcessActivity.reminders),
            selectinload(ProcessActivity.process_kpi),
        )
        .filter_by(process_id=p.id, is_active=True)
        .all()
    )
    favorite_kpi_ids = {
        f.process_kpi_id
        for f in FavoriteKpi.query.filter_by(user_id=current_user.id).all()
    }

    # Yıllık KPI config: bulk çek (N+1 önlemi) — sadece plan_year_enabled ise
    _plan_year_obj = None
    if current_user.tenant_id and getattr(current_user.tenant, "plan_year_enabled", False):
        _plan_year_obj = get_plan_year(current_user.tenant_id, year)
    _kpi_cfg_map = get_kpi_configs_bulk(kpis, _plan_year_obj) if kpis else {}

    # N+1 önlemi: tüm KPI verilerini tek sorguda çek (mevcut yıl + önceki yıl)
    prev_y = year - 1
    if kpis:
        kpi_ids = [k.id for k in kpis]
        _all_kpi_data = (
            KpiData.query
            .filter(
                KpiData.process_kpi_id.in_(kpi_ids),
                KpiData.year.in_([year, prev_y]),
                KpiData.is_active.is_(True),
            )
            .order_by(KpiData.process_kpi_id, KpiData.data_date)
            .all()
        )
        _kpi_data_map: dict[tuple, list] = {}
        for entry in _all_kpi_data:
            _kpi_data_map.setdefault((entry.process_kpi_id, entry.year), []).append(entry)
    else:
        _kpi_data_map = {}

    # N+1 önlemi: tüm ActivityTrack'leri tek sorguda çek
    if activities:
        activity_ids = [a.id for a in activities]
        _all_tracks = (
            ActivityTrack.query
            .filter(ActivityTrack.activity_id.in_(activity_ids), ActivityTrack.year == year)
            .all()
        )
        _tracks_map: dict[int, list] = {}
        for t in _all_tracks:
            _tracks_map.setdefault(t.activity_id, []).append(t)
    else:
        _tracks_map = {}

    def _parse_float(v):
        try:
            return float(v) if v not in (None, "") else None
        except (ValueError, TypeError):
            return None

    def _aggregate(entries_with_keys, method):
        by_key = {}
        for key, val_str, dt in entries_with_keys:
            by_key.setdefault(key, []).append((val_str, _parse_float(val_str), dt))
        result = {}
        for key, items in by_key.items():
            m = (method or "").lower()
            numeric = [(v, d) for _, v, d in items if v is not None]
            if m in ("toplama", "toplam") and numeric:
                result[key] = str(sum(v for v, _ in numeric))
            elif m == "ortalama" and numeric:
                result[key] = str(round(sum(v for v, _ in numeric) / len(numeric), 2))
            else:
                last = max(items, key=lambda x: x[2] or date(1900, 1, 1))
                result[key] = last[0]
        return result

    def _rollup_year_actual(method: str | None, raw_rows: list) -> float | None:
        """Yıl içindeki ham PGV satırlarından tek özet değer (PGV yoksa None)."""
        m = (method or "").lower()
        raw_nums = [_parse_float(e.actual_value) for e in raw_rows]
        raw_nums = [x for x in raw_nums if x is not None]
        if m in ("toplama", "toplam"):
            return float(sum(raw_nums)) if raw_nums else None
        if m == "ortalama":
            return round(sum(raw_nums) / len(raw_nums), 6) if raw_nums else None
        if raw_rows:
            last_e = max(raw_rows, key=lambda e: e.data_date or date(1900, 1, 1))
            return _parse_float(last_e.actual_value)
        return None

    kpi_list = []
    for k in kpis:
        entries = _kpi_data_map.get((k.id, year), [])
        entries_with_keys = []
        for e in entries:
            for key in data_date_to_period_keys(e.data_date, year):
                entries_with_keys.append((key, e.actual_value, e.data_date))
        entries_by_period = _aggregate(entries_with_keys, k.data_collection_method)

        prev_rows = _kpi_data_map.get((k.id, prev_y), [])
        year_rollup = _rollup_year_actual(k.data_collection_method, entries)
        prev_rollup = _rollup_year_actual(k.data_collection_method, prev_rows)
        prev_from_pgv = prev_rollup is not None

        strategy_title = ""
        if k.sub_strategy and k.sub_strategy.strategy:
            strategy_title = k.sub_strategy.strategy.title

        sub_st = k.sub_strategy

        # Yıllık config varsa kullan, yoksa ProcessKpi fallback
        _ycfg = _kpi_cfg_map.get(k.id, {})
        _target_value = _ycfg.get("target_value", k.target_value)
        _unit = _ycfg.get("unit", k.unit)
        _period = _ycfg.get("period", k.period)
        _direction = _ycfg.get("direction", k.direction or "Increasing")
        _method = _ycfg.get("data_collection_method", k.data_collection_method or "Ortalama")
        _bpa = _ycfg.get("basari_puani_araliklari", k.basari_puani_araliklari)
        _target_method = _ycfg.get("target_method", k.target_method)
        _weight = _ycfg.get("weight", k.weight)
        _oy_raw = _ycfg.get("onceki_yil_ortalamasi", getattr(k, "onceki_yil_ortalamasi", None))
        _is_included = _ycfg.get("is_included", True)
        _config_source = _ycfg.get("_config_source", "process_kpi")

        # ── Başarı puanı: ham gerçekleşen değer ile aralık karşılaştırması ──────
        _basari_puani = None
        if year_rollup is not None and _bpa:
            try:
                _bpa_dict = _parse_bpa(_bpa) if isinstance(_bpa, str) else _bpa
                _basari_puani = _hesapla_basari_puani(year_rollup, _bpa_dict, _direction or "Increasing")
            except Exception:
                pass

        if not _is_included:
            continue

        kpi_list.append({
            "id": k.id,
            "name": k.name,
            "code": k.code,
            "target_value": _target_value,
            "unit": _unit,
            "period": _period,
            "data_collection_method": _method,
            "direction": _direction,
            "weight": _weight,
            "target_method": _target_method,
            "sub_strategy_id": k.sub_strategy_id,
            "strategy_title": strategy_title or "-",
            "sub_strategy_title": sub_st.title if sub_st else "-",
            "sub_strategy_code": (sub_st.code or "").strip() if sub_st else "",
            "basari_puani_araliklari": _bpa,
            "basari_puani": _basari_puani,
            "is_favorite": k.id in favorite_kpi_ids,
            "is_included": _is_included,
            "config_source": _config_source,
            "entries": entries_by_period,
            "year_rollup": round(float(year_rollup), 6) if year_rollup is not None else None,
            "onceki_yil_ortalamasi": round(float(_oy_raw), 6) if _oy_raw is not None else None,
            "prev_year_from_pgv": prev_from_pgv,
            "prev_year_rollup": round(float(prev_rollup), 6) if prev_rollup is not None else None,
        })

    act_list = []
    for a in activities:
        tracks = _tracks_map.get(a.id, [])
        tracks_map = {t.month: t.completed for t in tracks}
        assignee_links = sorted(a.assignment_links, key=lambda z: z.order_no or 0)
        assignees = []
        for link in assignee_links:
            u = link.user
            if not u:
                continue
            full_name = (f"{(u.first_name or '').strip()} {(u.last_name or '').strip()}").strip() or (u.email or "")
            assignees.append({
                "id": int(u.id),
                "full_name": full_name,
                "email": u.email,
                "order_no": link.order_no,
            })
        can_manage = user_can_crud_pg_and_activity(current_user, p) or any(
            int(x["id"]) == int(current_user.id) for x in assignees
        )
        act_list.append({
            "id": a.id,
            "name": a.name,
            "description": a.description,
            "status": a.status,
            "progress": a.progress,
            "start_date": str(a.start_date) if a.start_date else None,
            "end_date": str(a.end_date) if a.end_date else None,
            "start_at": a.start_at.isoformat(timespec="minutes") if a.start_at else None,
            "end_at": a.end_at.isoformat(timespec="minutes") if a.end_at else None,
            "notify_email": bool(a.notify_email),
            "process_kpi_id": a.process_kpi_id,
            "process_kpi_name": a.process_kpi.name if a.process_kpi else None,
            "assignee_ids": [x["id"] for x in assignees],
            "assignees": assignees,
            "first_assignee_id": a.first_assignee_id,
            "reminder_offsets": [int(r.minutes_before) for r in sorted(a.reminders, key=lambda z: z.minutes_before, reverse=True)],
            "monthly_tracks": tracks_map,
            "can_manage": bool(can_manage),
        })

    process_users = []
    seen_uids = set()
    for u in (p.leaders + p.members + p.owners):
        if not u or not u.is_active or int(u.id) in seen_uids:
            continue
        seen_uids.add(int(u.id))
        full_name = (f"{(u.first_name or '').strip()} {(u.last_name or '').strip()}").strip() or (u.email or "")
        process_users.append({"id": int(u.id), "full_name": full_name, "email": u.email})

    return jsonify({
        "success": True,
        "process": {
            "id": p.id,
            "name": p.name,
            "document_no": p.document_no,
            "revision_no": p.revision_no,
        },
        "year": year,
        "kpis": kpi_list,
        "activities": act_list,
        "process_users": process_users,
        "favorite_kpi_ids": list(favorite_kpi_ids),
        "permissions": {
            "can_crud_pg": user_can_crud_pg_and_activity(current_user, p),
            "can_enter_pgv": user_can_enter_pgv(current_user, p),
            "can_crud_activity": _user_can_add_activity(current_user, p),
            "can_track_activity": user_can_access_process(current_user, p),
        },
    })


@app_bp.route("/process/api/karne/<int:process_id>/export-xlsx", methods=["POST"])
@login_required
def surec_api_karne_export_xlsx(process_id):
    """Karne tablosunu istemcinin ürettiği başlık/satırlarla gerçek .xlsx olarak döner."""
    p = _process_for_user(process_id)
    if not p or not user_can_access_process(current_user, p):
        abort(403)
    payload = request.get_json() or {}
    headers = payload.get("headers")
    rows = payload.get("rows")
    year = payload.get("year", "")
    if not isinstance(headers, list) or not isinstance(rows, list):
        return jsonify({"success": False, "message": _("Geçersiz istek gövdesi.")}), 400
    if len(headers) > 200 or len(rows) > 2000:
        return jsonify({"success": False, "message": _("Çok fazla sütun veya satır.")}), 400
    try:
        from openpyxl import Workbook
    except ImportError:
        current_app.logger.error("[surec_api_karne_export_xlsx] openpyxl yok")
        return jsonify({"success": False, "message": _("Sunucuda Excel dışa aktarma kullanılamıyor.")}), 500

    wb = Workbook()
    ws = wb.active
    ws.title = "Karne"

    def _cell(v):
        if v is None:
            return ""
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return v
        return str(v)

    ws.append([_cell(h) for h in headers])
    nh = len(headers)
    for raw in rows:
        if not isinstance(raw, list):
            continue
        line = [_cell(raw[i]) if i < len(raw) else "" for i in range(nh)]
        ws.append(line)

    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)
    base = f"surec_karne_{p.id}_{year}"
    try:
        from werkzeug.utils import secure_filename

        fname = secure_filename(base) or base
    except Exception:
        fname = base
    if not fname.endswith(".xlsx"):
        fname = f"{fname}.xlsx"
    return send_file(
        bio,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=fname,
    )


# ── Inline AI Yönetici Özeti (karne üstü) ─────────────────────────────────────

def _karne_heuristik_ozet(p, year, skor, durum, detay, recs):
    """LLM olmadan da çalışan deterministik Türkçe yönetici özeti."""
    ad = (p.name or "Süreç").strip()
    detay = detay or {}
    parts = []
    if skor is not None:
        try:
            parts.append(f"{ad} {year} sağlık skoru %{float(skor):.0f}"
                         + (f" ({durum})." if durum else "."))
        except (TypeError, ValueError):
            pass
    ulasma = detay.get("pg_hedef_ulasma_orani")
    if ulasma is not None:
        try:
            parts.append(f"PG hedef ulaşma oranı %{float(ulasma):.0f}.")
        except (TypeError, ValueError):
            pass
    pg_sayisi = detay.get("pg_sayisi") or 0
    veri = detay.get("veri_girilen_pg")
    if pg_sayisi and veri is not None and veri < pg_sayisi:
        parts.append(f"{pg_sayisi} PG'den {pg_sayisi - veri}'ine veri girilmemiş — "
                     "veri disiplinini güçlendirin.")
    yuksek = [r for r in (recs or []) if r.get("priority") == "high"]
    kaynak_rec = yuksek[0] if yuksek else ((recs or [None])[0])
    if kaynak_rec:
        msg = (kaynak_rec.get("message") or kaynak_rec.get("action")
               or kaynak_rec.get("title") or "").strip()
        if msg:
            etiket = "Kırmızı bayrak" if yuksek else "Öneri"
            parts.append(f"{etiket}: {msg.rstrip('.')}.")
    if not parts:
        parts.append(f"{ad} için {year} yılında özet üretecek yeterli veri yok; PG verisi girin.")
    return " ".join(parts)


@app_bp.route("/process/api/karne/<int:process_id>/ai-ozet", methods=["GET"])
@login_required
def surec_api_karne_ai_ozet(process_id):
    """Karne üstü 2-3 cümlelik Türkçe yönetici özeti.

    Her zaman deterministik heuristik döner; LLM yapılandırılmışsa onunla cilalanır.
    Bu sayede yerelde LLM anahtarı olmadan da çalışır.
    """
    p = _process_for_user(process_id)
    if not p:
        abort(404)
    if not user_can_access_process(current_user, p):
        abort(403)
    year = request.args.get("year", datetime.now().year, type=int)

    # 1) Hazır hesaplama servislerinden metrikleri topla
    skor = durum = None
    detay = {}
    try:
        from app.services.process_health_service import calculate_process_health_score
        h = calculate_process_health_score(process_id, year) or {}
        skor = h.get("skor")
        durum = h.get("durum")
        detay = h.get("detay") or {}
    except Exception as e:
        current_app.logger.info(f"[karne-ai-ozet] health fallback ({e})")

    recs = []
    try:
        from app.services.recommendation_service import RecommendationService
        rr = RecommendationService().get_process_recommendations(process_id)
        if isinstance(rr, dict) and rr.get("success"):
            recs = rr.get("recommendations") or []
    except Exception as e:
        current_app.logger.info(f"[karne-ai-ozet] rec fallback ({e})")

    # 2) Deterministik heuristik (her zaman üretilir)
    ozet = _karne_heuristik_ozet(p, year, skor, durum, detay, recs)
    kaynak = "heuristik"

    # 3) Opsiyonel LLM cilası (anahtar yoksa heuristik kalır)
    try:
        from app.services.llm_gateway import call_llm
        veri_ozeti = (
            f"Süreç: {p.name}. Yıl: {year}. Sağlık skoru: {skor}. Durum: {durum}. "
            f"PG hedef ulaşma: {detay.get('pg_hedef_ulasma_orani')}. "
            f"PG sayısı: {detay.get('pg_sayisi')}, veri girilen: {detay.get('veri_girilen_pg')}. "
            "Öneriler: " + "; ".join(
                (r.get('message') or r.get('title') or '') for r in recs[:4]
            )
        )
        prompt = (
            "Aşağıdaki süreç performans verisinden, bir yöneticinin tek bakışta okuyacağı "
            "2-3 cümlelik Türkçe özet yaz. Sırasıyla: kazanım(lar), kırmızı bayrak(lar) ve "
            "bu hafta odaklanılacak tek konu. Sade, net, abartısız.\n\n" + veri_ozeti
        )
        res = call_llm(
            tenant_id=current_user.tenant_id, endpoint="karne_ozet",
            prompt=prompt,
            system_prompt="Sen kısa ve net konuşan bir Türkçe strateji danışmanısın.",
            user_id=current_user.id, max_output_tokens=240,
        )
        if isinstance(res, dict) and res.get("text"):
            ozet = res["text"].strip()
            kaynak = "ai"
    except Exception as e:
        current_app.logger.info(f"[karne-ai-ozet] LLM fallback ({e})")

    return jsonify({
        "success": True, "ozet": ozet, "kaynak": kaynak,
        "skor": skor, "durum": durum, "year": year,
    })
