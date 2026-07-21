"""K-Radar — K-Performans (KP) route'ları."""

from datetime import datetime, timezone
from flask import jsonify, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_required

from platform_core import app_bp
from app.services.date_sovereign import resolve_request_year
from app.models import db
from app.models.process import Process
from app.models.k_radar_domain import ProcessMaturity
from flask_babel import gettext as _
from micro.modules.k_radar.routes_common import (
    _can_manage_k_radar, _required_tenant_id, _safe_json, _forbidden_json, _scope_tuples,
)


@app_bp.route("/k-radar/kp")
@login_required
def k_radar_kp():
    return render_template("platform/k_radar/kp.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kp/darbogaz")
@login_required
def k_radar_kp_darbogaz():
    return render_template("platform/k_radar/kp_darbogaz.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kp/value-chain")
@login_required
def k_radar_kp_deger_zinciri():
    """Teşhis katmanı — değer zinciri SALT OKU.

    Girdi evi `/k-plan/process/value-chain` (aynı şablon, can_manage=True).
    """
    return render_template("platform/k_radar/kp_deger_zinciri.html", can_manage_k_radar=False)


@app_bp.route("/k-plan/process/value-chain")
@login_required
def k_plan_deger_zinciri():
    """Girdi katmanı — değer zincirinin TEK SAHİBİ (yazar).

    Katman mimarisi Faz 3 (2026-07-17): değer zinciri verisi teşhiste
    yazılıyordu; girdi evi burada açıldı. K-Radar aynı şablonu salt-oku gösterir.
    """
    return render_template("platform/k_radar/kp_deger_zinciri.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kp/pareto")
@login_required
def k_radar_kp_pareto():
    return render_template("platform/k_radar/kp_pareto.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kp/sla")
@login_required
def k_radar_kp_sla():
    return render_template("platform/k_radar/kp_sla.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kp/benchmark")
@login_required
def k_radar_kp_benchmark():
    return render_template("platform/k_radar/kp_benchmark.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kp/oee")
@login_required
def k_radar_kp_oee():
    return render_template("platform/k_radar/kp_oee.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kp/vsm")
@login_required
def k_radar_kp_vsm():
    return render_template("platform/k_radar/kp_vsm.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kp/capacity")
@login_required
def k_radar_kp_kapasite():
    return render_template("platform/k_radar/kp_kapasite.html", can_manage_k_radar=_can_manage_k_radar())


def _olgunluk_context(tenant_id: int):
    rows = (
        ProcessMaturity.query.filter_by(tenant_id=tenant_id, is_active=True)
        .order_by(ProcessMaturity.updated_at.desc())
        .limit(100)
        .all()
    )
    processes = (
        Process.query.filter_by(tenant_id=tenant_id, is_active=True)
        .order_by(Process.code, Process.name)
        .all()
    )
    return rows, processes


@app_bp.route("/k-radar/kp/maturity")
@login_required
def k_radar_kp_olgunluk():
    """Teşhis katmanı — CMMI olgunluk ısı haritası SALT OKU.

    Girdi evi `/k-plan/process/maturity` (aynı şablon, can_manage=True).
    Hedef tasarımda planlanan taşıma: olgunluk süreç verisidir, sahibi Girdi.
    """
    rows, processes = _olgunluk_context(_required_tenant_id())
    return render_template(
        "platform/k_radar/kp_olgunluk.html",
        can_manage_k_radar=False,
        rows=rows,
        processes=processes,
    )


@app_bp.route("/k-plan/process/maturity")
@login_required
def k_plan_olgunluk():
    """Girdi katmanı — süreç olgunluğunun TEK SAHİBİ (yazar).

    Katman mimarisi Faz 3 (2026-07-17): olgunluk K-Radar domain'inde
    yazılıyordu; hedef tasarım gereği girdi evine taşındı.
    """
    rows, processes = _olgunluk_context(_required_tenant_id())
    return render_template(
        "platform/k_radar/kp_olgunluk.html",
        can_manage_k_radar=_can_manage_k_radar(),
        rows=rows,
        processes=processes,
    )


# Girdi katmanı (Faz 3): yazma /k-plan/ altında. Endpoint adı sözleşme gereği
# korundu — şablondaki url_for otomatik uyum sağlar.
@app_bp.route("/k-plan/process/maturity/add", methods=["POST"])
@login_required
def k_radar_kp_olgunluk_ekle():
    if not _can_manage_k_radar():
        return render_template("platform/errors/403.html"), 403
    tenant_id = _required_tenant_id()
    process_id = request.form.get("process_id", type=int)
    maturity_level = request.form.get("maturity_level", type=int)
    dimension = (request.form.get("dimension") or "").strip() or None
    if not process_id or not maturity_level:
        flash(_("Süreç ve seviye zorunludur."), "danger")
        return redirect(url_for("app_bp.k_plan_olgunluk"))
    row = ProcessMaturity(
        tenant_id=tenant_id,
        process_id=process_id,
        maturity_level=max(1, min(5, maturity_level)),
        dimension=dimension,
        assessed_by=current_user.id,
        assessed_at=datetime.now(timezone.utc),
        is_active=True,
    )
    db.session.add(row)
    db.session.commit()
    flash(_("Olgunluk kaydı eklendi."), "success")
    return redirect(url_for("app_bp.k_plan_olgunluk"))


@app_bp.route("/k-radar/api/kp")
@login_required
def k_radar_api_kp():
    from services.k_radar_service import get_kp_data
    _sp, _ = _scope_tuples()
    return _safe_json(lambda: jsonify({"success": True, "data": get_kp_data(_required_tenant_id(), _sp, year=resolve_request_year())}))


@app_bp.route("/k-radar/api/kp/radar")
@login_required
def k_radar_api_kp_radar():
    """Süreç olgunluk radarı — 5 boyutta 0-100 skor.

    Boyutlar:
      - Performans (PG hedef üstü oranı)
      - Veri Kapsamı (PG'lerin kaçında veri var)
      - Olgunluk (kritik KPI yokluğu temelli)
      - Faaliyet Zamanlaması (gecikmesiz oranı)
      - Risk (açık risk yokluğu)
    """
    from sqlalchemy import text as _t
    tid = _required_tenant_id()
    # K2: bu uç kendi ham SQL'ini kullanıyor (get_kp_data'ya gitmiyor) ve
    # kpi_data sorgularında YIL FİLTRESİ YOKTU → 2020 ile 2026 yanıtı
    # byte-byte aynıydı (pg_total=251, pg_on_target=219 sabit).
    yil = resolve_request_year()
    try:
        # PG hedef üstü + veri kapsamı (tek sorgu)
        r1 = db.session.execute(_t("""
            SELECT
              count(DISTINCT k.id) FILTER (WHERE k.is_active) AS total,
              count(DISTINCT k.id) FILTER (
                WHERE k.is_active AND EXISTS (
                  SELECT 1 FROM kpi_data kd
                  WHERE kd.process_kpi_id=k.id AND kd.is_active=true
                    AND kd.year = :y
                )
              ) AS with_data,
              count(DISTINCT k.id) FILTER (
                WHERE k.is_active AND EXISTS (
                  SELECT 1 FROM kpi_data kd
                  WHERE kd.process_kpi_id=k.id AND kd.is_active=true
                    AND kd.year = :y
                    AND kd.actual_value ~ '^-?[0-9]+\\.?[0-9]*$'
                    AND kd.target_value ~ '^-?[0-9]+\\.?[0-9]*$'
                    AND kd.actual_value::float >= kd.target_value::float
                )
              ) AS on_target
            FROM process_kpis k
            JOIN processes p ON k.process_id=p.id
            WHERE p.tenant_id=:t
        """), {"t": tid, "y": yil}).fetchone()
        total = int(r1.total or 0) if r1 else 0
        with_data = int(r1.with_data or 0) if r1 else 0
        on_target = int(r1.on_target or 0) if r1 else 0
        perf = round((on_target / with_data) * 100, 1) if with_data else 0
        coverage = round((with_data / total) * 100, 1) if total else 0

        # Faaliyet zamanlaması
        r2 = db.session.execute(_t("""
            SELECT
              sum(CASE WHEN a.status != 'Tamamlandı' AND a.end_date < CURRENT_DATE THEN 1 ELSE 0 END) AS overdue,
              count(*) AS total
            FROM process_activities a
            JOIN processes p ON a.process_id=p.id
            WHERE p.tenant_id=:t AND a.is_active=true
        """), {"t": tid}).fetchone()
        a_total = int(r2.total or 0) if r2 else 0
        a_overdue = int(r2.overdue or 0) if r2 else 0
        timing = round(max(0, 100 - (a_overdue / a_total) * 100), 1) if a_total else 100

        # Risk (yoksa 100, varsa açık risk başına -10 puan)
        try:
            r3 = db.session.execute(_t("""
                SELECT sum(CASE WHEN status != 'Closed' THEN 1 ELSE 0 END) AS open_c
                FROM risk_heatmap_items WHERE tenant_id=:t AND is_active=true
            """), {"t": tid}).fetchone()
            open_risks = int(r3.open_c or 0) if r3 else 0
        except Exception as _e:
            # Aynı tuzak (bkz. aşağıdaki olgunluk bloğu): yutulan DB hatası
            # transaction'ı abort bırakır. Ayrıca KURALLAR §3 her except'te
            # app.logger.error zorunlu kılıyor — burada sessizdi.
            db.session.rollback()
            current_app.logger.error("[k_radar_kp] risk sayımı yapılamadı: %s", _e)
            open_risks = 0
        risk_score = max(0, 100 - open_risks * 10)

        # Olgunluk: ortalama olgunluk skorları (kp_olgunluk)
        maturity = perf  # varsayılan: performans yansır
        try:
            r4 = db.session.execute(_t("""
                SELECT AVG(skor)::float AS avg_skor
                FROM k_radar_kp_olgunluk
                WHERE tenant_id=:t
            """), {"t": tid}).fetchone()
            if r4 and r4.avg_skor is not None:
                maturity = round(float(r4.avg_skor) * 20, 1)  # 1-5 → 20-100
        except Exception as _e:
            # ⚠ ROLLBACK ZORUNLU: PostgreSQL'de başarısız bir sorgu
            # transaction'ı ABORT eder. `except` hatayı yutsa bile sonraki
            # HER sorgu "current transaction is aborted" ile düşer.
            #
            # Ölçüm 2026-07-21: `k_radar_kp_olgunluk` tablosu DB'de HİÇ YOK
            # (kodda 3 yerde geçiyor, migration'ı yazılmamış). Bu tek yutulan
            # hata yüzünden 7 uç birden 500 veriyordu:
            #   /k-radar/api/{ks,kp/maturity,kpr/evm,kpr/gantt,kpr/risk,
            #                 kpr/resource-capacity} + /k-report/api/pi-dagilim
            # Hatanın kendisi zararsızdı; zarar ROLLBACK'in yokluğundandı.
            db.session.rollback()
            current_app.logger.error("[k_radar_kp] olgunluk skoru hesaplanamadı: %s", _e)

        return jsonify({"success": True, "data": {
            "labels": ["Performans", "Veri Kapsamı", "Olgunluk", "Faaliyet Zamanlaması", "Risk Yönetimi"],
            "values": [perf, coverage, maturity, timing, risk_score],
            "raw": {
                "pg_total": total, "pg_with_data": with_data, "pg_on_target": on_target,
                "act_total": a_total, "act_overdue": a_overdue,
                "open_risks": open_risks,
            }
        }})
    except Exception as e:
        current_app.logger.exception("[kp_radar] %s", e)
        return jsonify({"success": False, "message": _("Radar verisi alınamadı.")}), 500


@app_bp.route("/k-radar/api/kp/maturity")
@login_required
def k_radar_api_kp_olgunluk():
    def _build():
        tenant_id = _required_tenant_id()
        rows = (
            ProcessMaturity.query.filter_by(tenant_id=tenant_id, is_active=True)
            .order_by(ProcessMaturity.updated_at.desc())
            .limit(200)
            .all()
        )
        return jsonify({
            "success": True,
            "data": {
                "rows": [
                    {
                        "id": r.id,
                        "process_id": r.process_id,
                        "maturity_level": r.maturity_level,
                        "dimension": r.dimension,
                        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
                    }
                    for r in rows
                ]
            },
        })
    return _safe_json(_build)


@app_bp.route("/k-plan/process/api/maturity", methods=["POST"])
@login_required
def k_radar_api_kp_olgunluk_create():
    if not _can_manage_k_radar():
        return _forbidden_json()
    payload = request.get_json(silent=True) or {}
    process_id = payload.get("process_id")
    maturity_level = payload.get("maturity_level")
    dimension = (payload.get("dimension") or "").strip() or None
    if not process_id or not maturity_level:
        return jsonify({"success": False, "message": "process_id ve maturity_level zorunlu"}), 400
    def _create():
        row = ProcessMaturity(
            tenant_id=_required_tenant_id(),
            process_id=int(process_id),
            maturity_level=max(1, min(5, int(maturity_level))),
            dimension=dimension,
            assessed_by=current_user.id,
            assessed_at=datetime.now(timezone.utc),
            is_active=True,
        )
        db.session.add(row)
        db.session.commit()
        return jsonify({"success": True, "data": {"id": row.id}})
    return _safe_json(_create)


@app_bp.route("/k-plan/process/api/maturity/<int:row_id>", methods=["PUT"])
@login_required
def k_radar_api_kp_olgunluk_update(row_id: int):
    if not _can_manage_k_radar():
        return _forbidden_json()
    payload = request.get_json(silent=True) or {}
    maturity_level = payload.get("maturity_level")
    dimension = (payload.get("dimension") or "").strip() or None
    if maturity_level is None:
        return jsonify({"success": False, "message": "maturity_level zorunlu"}), 400

    def _update():
        row = ProcessMaturity.query.filter_by(id=row_id, tenant_id=_required_tenant_id(), is_active=True).first()
        if not row:
            return jsonify({"success": False, "message": _("Kayıt bulunamadı")}), 404
        row.maturity_level = max(1, min(5, int(maturity_level)))
        row.dimension = dimension
        row.assessed_by = current_user.id
        row.assessed_at = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({"success": True, "data": {"id": row.id}})

    return _safe_json(_update)


@app_bp.route("/k-plan/process/api/maturity/<int:row_id>", methods=["DELETE"])
@login_required
def k_radar_api_kp_olgunluk_delete(row_id: int):
    if not _can_manage_k_radar():
        return _forbidden_json()

    def _delete():
        row = ProcessMaturity.query.filter_by(id=row_id, tenant_id=_required_tenant_id(), is_active=True).first()
        if not row:
            return jsonify({"success": False, "message": _("Kayıt bulunamadı")}), 404
        row.is_active = False
        db.session.commit()
        return jsonify({"success": True, "data": {"id": row.id}})

    return _safe_json(_delete)


@app_bp.route("/k-radar/api/kp/darbogaz")
@login_required
def k_radar_api_kp_darbogaz():
    from services.k_radar_service import get_kp_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_kp_extended_data(_required_tenant_id(), _scope_tuples()[0], year=resolve_request_year()).get("darbogaz", {})}))


@app_bp.route("/k-radar/api/kp/value-chain")
@login_required
def k_radar_api_kp_deger_zinciri():
    from services.k_radar_service import get_kp_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_kp_extended_data(_required_tenant_id(), _scope_tuples()[0], year=resolve_request_year()).get("deger_zinciri", {})}))


# ── Değer Zinciri öğe CRUD (L3 eksik tamamlama) ───────────────────────────────
# value_chain_items tablosu + okuma vardı ama GİRİŞ route'u yoktu (dead code).

_VC_CATEGORIES = ("primary", "support")
# Yalın üretim 7 muda (israf) — opsiyonel etiket
_VC_MUDA = ("", "fazla_uretim", "bekleme", "tasima", "fazla_isleme",
            "stok", "hareket", "hata")


def _vc_item_dict(it):
    return {
        "id": it.id, "category": it.category, "title": it.title,
        "note": it.note or "", "muda_type": it.muda_type or "",
        "linked_process_id": it.linked_process_id,
    }


@app_bp.route("/k-radar/api/kp/value-chain/items", methods=["GET"])
@login_required
def k_radar_api_vc_items_list():
    """Değer zinciri öğeleri (birincil/destek) — liste."""
    from app.models.k_radar_domain import ValueChainItem
    tid = _required_tenant_id()

    def _build():
        items = (ValueChainItem.query
                 .filter_by(tenant_id=tid, is_active=True)
                 .order_by(ValueChainItem.category, ValueChainItem.id).all())
        procs = (Process.query.filter_by(tenant_id=tid, is_active=True)
                 .order_by(Process.code).all())
        return jsonify({
            "success": True,
            "items": [_vc_item_dict(i) for i in items],
            "categories": list(_VC_CATEGORIES),
            "muda_types": list(_VC_MUDA),
            "processes": [{"id": p.id, "name": p.name, "code": p.code or ""} for p in procs],
        })
    return _safe_json(_build)


@app_bp.route("/k-plan/process/api/value-chain/items", methods=["POST"])
@login_required
def k_radar_api_vc_item_add():
    if not _can_manage_k_radar():
        return _forbidden_json()
    from app.models.k_radar_domain import ValueChainItem
    tid = _required_tenant_id()
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    category = (data.get("category") or "").strip()
    if not title:
        return jsonify({"success": False, "message": _("Başlık zorunludur.")}), 400
    if category not in _VC_CATEGORIES:
        return jsonify({"success": False, "message": _("Geçersiz kategori.")}), 400
    try:
        it = ValueChainItem(
            tenant_id=tid, title=title, category=category,
            note=(data.get("note") or "").strip() or None,
            muda_type=(data.get("muda_type") or "").strip() or None,
            linked_process_id=_vc_proc(data.get("linked_process_id"), tid),
            is_active=True,
        )
        db.session.add(it)
        db.session.commit()
        return jsonify({"success": True, "id": it.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[vc_item_add] {e}", exc_info=True)
        return jsonify({"success": False, "message": _("Öğe eklenemedi.")}), 500


@app_bp.route("/k-plan/process/api/value-chain/items/<int:item_id>", methods=["POST"])
@login_required
def k_radar_api_vc_item_update(item_id):
    if not _can_manage_k_radar():
        return _forbidden_json()
    from app.models.k_radar_domain import ValueChainItem
    tid = _required_tenant_id()
    it = ValueChainItem.query.filter_by(id=item_id, tenant_id=tid, is_active=True).first()
    if not it:
        return jsonify({"success": False, "message": _("Öğe bulunamadı.")}), 404
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    category = (data.get("category") or it.category or "").strip()
    if not title:
        return jsonify({"success": False, "message": _("Başlık zorunludur.")}), 400
    if category not in _VC_CATEGORIES:
        return jsonify({"success": False, "message": _("Geçersiz kategori.")}), 400
    try:
        it.title = title
        it.category = category
        it.note = (data.get("note") or "").strip() or None
        it.muda_type = (data.get("muda_type") or "").strip() or None
        it.linked_process_id = _vc_proc(data.get("linked_process_id"), tid)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[vc_item_update] {e}", exc_info=True)
        return jsonify({"success": False, "message": _("Öğe güncellenemedi.")}), 500


@app_bp.route("/k-plan/process/api/value-chain/items/<int:item_id>/delete", methods=["POST"])
@login_required
def k_radar_api_vc_item_delete(item_id):
    if not _can_manage_k_radar():
        return _forbidden_json()
    from app.models.k_radar_domain import ValueChainItem
    tid = _required_tenant_id()
    it = ValueChainItem.query.filter_by(id=item_id, tenant_id=tid, is_active=True).first()
    if not it:
        return jsonify({"success": False, "message": _("Öğe bulunamadı.")}), 404
    try:
        it.is_active = False  # soft delete (KURALLAR §3)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[vc_item_delete] {e}", exc_info=True)
        return jsonify({"success": False, "message": _("Öğe silinemedi.")}), 500


def _vc_proc(raw, tid):
    """linked_process_id'yi tenant izolasyonlu doğrula → id veya None."""
    if raw in (None, "", "null"):
        return None
    try:
        pid = int(raw)
    except (TypeError, ValueError):
        return None
    ok = Process.query.filter_by(id=pid, tenant_id=tid, is_active=True).first()
    return pid if ok else None


@app_bp.route("/k-radar/api/kp/pareto")
@login_required
def k_radar_api_kp_pareto():
    from services.k_radar_service import get_kp_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_kp_extended_data(_required_tenant_id(), _scope_tuples()[0], year=resolve_request_year()).get("pareto", {})}))


@app_bp.route("/k-radar/api/kp/sla")
@login_required
def k_radar_api_kp_sla():
    from services.k_radar_service import get_kp_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_kp_extended_data(_required_tenant_id(), _scope_tuples()[0], year=resolve_request_year()).get("sla", {})}))


@app_bp.route("/k-radar/api/kp/benchmark")
@login_required
def k_radar_api_kp_benchmark():
    from services.k_radar_service import get_kp_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_kp_extended_data(_required_tenant_id(), _scope_tuples()[0], year=resolve_request_year()).get("benchmark", {})}))


@app_bp.route("/k-radar/api/kp/oee")
@login_required
def k_radar_api_kp_oee():
    from services.k_radar_service import get_kp_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_kp_extended_data(_required_tenant_id(), _scope_tuples()[0], year=resolve_request_year()).get("oee", {})}))


@app_bp.route("/k-radar/api/kp/vsm")
@login_required
def k_radar_api_kp_vsm():
    from services.k_radar_service import get_kp_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_kp_extended_data(_required_tenant_id(), _scope_tuples()[0], year=resolve_request_year()).get("vsm", {})}))


@app_bp.route("/k-radar/api/kp/capacity")
@login_required
def k_radar_api_kp_kapasite():
    from services.k_radar_service import get_kp_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_kp_extended_data(_required_tenant_id(), _scope_tuples()[0], year=resolve_request_year()).get("kapasite", {})}))
