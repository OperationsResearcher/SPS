"""Masaüstüm modülü — kullanıcının kişisel özet ekranı.

Tüm modüllerden gelen:
- Bireysel Performans Göstergeleri (PG) ve süreç PG'leri
- Görevler / faaliyetler
- Okunmamış bildirimler
- Kurum özeti (tenant_admin için)
"""

from datetime import date, timedelta, datetime, time

from flask import render_template, jsonify, request, current_app, Response, url_for
from flask_login import login_required, current_user
from flask_babel import gettext as _
from sqlalchemy import case, or_, and_, inspect as sa_inspect
from flask import session as flask_session

from platform_core import app_bp
from app.models import db
from app.services.date_sovereign import resolve_request_year
from app.utils.process_utils import data_date_to_period_keys
from app.models.process import (
    IndividualPerformanceIndicator,
    IndividualActivity,
    IndividualKpiData,
    ProcessKpi,
    ProcessActivity,
    Process,
    KpiData,
    FavoriteKpi,
    ProcessActivityAssignee,
    process_members,
    process_leaders,
)
from app.models.core import Notification, Strategy, User as CoreUser
from app.models.portfolio_project import Project, Task, project_members, project_leaders

from app_platform.modules.proje.permissions import is_privileged, user_can_edit_tasks
from app_platform.modules.surec.permissions import user_can_access_process
from flask_babel import gettext as _


def _table_exists(table_name: str) -> bool:
    bind = db.session.get_bind() if hasattr(db.session, "get_bind") else None
    if bind is None:
        try:
            bind = db.engine
        except Exception:
            bind = None
    if bind is None:
        return False
    try:
        return bool(sa_inspect(bind).has_table(table_name))
    except Exception:
        return False


def _individual_pg_has_monthly_entry(pg_id: int, user_id: int, year: int, month: int) -> bool:
    """Seçilen ay için `aylik_{month}` anahtarına denk gelen veri var mı?"""
    entries = IndividualKpiData.query.filter_by(
        individual_pg_id=pg_id, year=year, user_id=user_id
    ).all()
    want = f"aylik_{month}"
    for e in entries:
        if not e.data_date:
            continue
        for k in data_date_to_period_keys(e.data_date, year):
            if k == want:
                return True
    return False


@app_bp.route("/desktop/api/ilk-kurulum/gizle", methods=["POST"])
@login_required
def masaustu_ilk_kurulum_gizle():
    """İlk kurulum kontrol listesini bu kullanıcı için gizler."""
    from app.services.ilk_kurulum_service import gizle_ayarla
    try:
        gizle_ayarla(current_user, True)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[masaustu_ilk_kurulum_gizle] {e}")
        return jsonify({"success": False, "message": _("Kaydedilemedi.")}), 500
    return jsonify({"success": True})


@app_bp.route("/desktop")
@login_required
def masaustu():
    """Masaüstüm ana sayfası."""
    user_id = current_user.id
    tenant_id = current_user.tenant_id

    # Bireysel Performans Göstergeleri (aktif, son 5)
    bireysel_pgs = (
        IndividualPerformanceIndicator.query
        .filter_by(user_id=user_id, is_active=True)
        .order_by(IndividualPerformanceIndicator.updated_at.desc())
        .limit(5)
        .all()
    )

    # Bireysel faaliyetler (devam eden); bitiş tarihi yoksa sonda
    bireysel_faaliyetler = (
        IndividualActivity.query
        .filter_by(user_id=user_id, is_active=True)
        .filter(IndividualActivity.status != "Tamamlandı")
        .order_by(
            case((IndividualActivity.end_date.is_(None), 1), else_=0),
            IndividualActivity.end_date.asc(),
        )
        .limit(5)
        .all()
    )

    # Süreç PG'leri — kullanıcının üye/lider olduğu süreçlerden
    from app.models.process import Process, process_members, process_leaders
    member_process_ids = db.session.query(process_members.c.process_id).filter(
        process_members.c.user_id == user_id
    ).subquery()
    leader_process_ids = db.session.query(process_leaders.c.process_id).filter(
        process_leaders.c.user_id == user_id
    ).subquery()

    surec_pg_sorgu = (
        ProcessKpi.query.join(ProcessKpi.process)
        .filter(
            ProcessKpi.is_active.is_(True),
            Process.is_active.is_(True),
            db.or_(
                Process.id.in_(member_process_ids),
                Process.id.in_(leader_process_ids),
            ),
        )
    )
    toplam_surec_pg = surec_pg_sorgu.count()
    surec_pgs = (
        surec_pg_sorgu.order_by(ProcessKpi.updated_at.desc()).limit(5).all()
    )

    # Favori PG'ler — kullanıcının yıldızladığı süreç PG'leri + son ölçüm değeri
    favori_pg_kayitlari = (
        ProcessKpi.query
        .join(FavoriteKpi, FavoriteKpi.process_kpi_id == ProcessKpi.id)
        .join(ProcessKpi.process)
        .filter(
            FavoriteKpi.user_id == user_id,
            FavoriteKpi.is_active.is_(True),
            ProcessKpi.is_active.is_(True),
            Process.is_active.is_(True),
            Process.tenant_id == current_user.tenant_id,
        )
        .order_by(ProcessKpi.updated_at.desc())
        .all()
    )
    favori_pgs = []
    from app.services.score_engine_service import compute_pg_score
    from app.utils.numeric import safe_float
    # PERF-12: favori PG başına ayrı sorgu yerine tek pencere-fonksiyonlu sorgu.
    _son_map = {}
    _fav_ids = [_p.id for _p in favori_pg_kayitlari]
    if _fav_ids:
        from sqlalchemy import func as _func
        _rn = _func.row_number().over(
            partition_by=KpiData.process_kpi_id,
            order_by=(KpiData.year.desc(), KpiData.data_date.desc(), KpiData.id.desc()),
        ).label("rn")
        _sub = (
            db.session.query(KpiData.id.label("kid"), _rn)
            .filter(KpiData.process_kpi_id.in_(_fav_ids), KpiData.is_active.is_(True))
            .subquery()
        )
        for _d in KpiData.query.join(_sub, KpiData.id == _sub.c.kid).filter(_sub.c.rn == 1).all():
            _son_map[_d.process_kpi_id] = _d
    for _pg in favori_pg_kayitlari:
        _son = _son_map.get(_pg.id)
        _hedef = safe_float(_son.target_value if _son and _son.target_value else _pg.target_value)
        _gercek = safe_float(_son.actual_value) if _son else None
        _hedef_orani = (
            compute_pg_score(_hedef, _gercek, _pg.direction or "Increasing")
            if _hedef is not None and _gercek is not None
            else None
        )
        favori_pgs.append({
            "id": _pg.id,
            "name": _pg.name,
            "code": _pg.code,
            "unit": _pg.unit,
            "target_value": _pg.target_value,
            "process_id": _pg.process_id,
            "process_name": _pg.process.name if _pg.process else None,
            "actual_value": _son.actual_value if _son else None,
            "status": _son.status if _son else None,
            # SEM-C: iki semantik ayrı — band ≠ hedef oranı
            "basari_bandi_pct": _son.status_percentage if _son else None,
            "hedef_orani_pct": _hedef_orani,
            "status_percentage": _son.status_percentage if _son else None,  # geriye uyum
        })

    # Okunmamış bildirimler
    bildirimler = (
        Notification.query
        .filter_by(user_id=user_id, is_read=False)
        .order_by(Notification.created_at.desc())
        .limit(5)
        .all()
    )

    # Özet sayılar
    toplam_bireysel_pg = IndividualPerformanceIndicator.query.filter_by(
        user_id=user_id, is_active=True
    ).count()
    toplam_faaliyet = IndividualActivity.query.filter_by(
        user_id=user_id, is_active=True
    ).filter(IndividualActivity.status != "Tamamlandı").count()
    toplam_bildirim = Notification.query.filter_by(
        user_id=user_id, is_read=False
    ).count()

    today = date.today()
    cy, cm = today.year, today.month

    # Bu ay için henüz veri girilmemiş bireysel PG'ler
    all_bireysel_pgs = (
        IndividualPerformanceIndicator.query.filter_by(user_id=user_id, is_active=True).all()
    )
    eksik_pg_bu_ay = [
        pg
        for pg in all_bireysel_pgs
        if not _individual_pg_has_monthly_entry(pg.id, user_id, cy, cm)
    ]

    faaliyet_aktif = IndividualActivity.query.filter_by(
        user_id=user_id, is_active=True
    ).filter(IndividualActivity.status != "Tamamlandı")

    faaliyet_geciken = (
        faaliyet_aktif.filter(
            IndividualActivity.end_date.isnot(None),
            IndividualActivity.end_date < today,
        )
        .order_by(IndividualActivity.end_date.asc())
        .limit(20)
        .all()
    )

    hafta_bitis = today + timedelta(days=7)
    faaliyet_hafta = (
        faaliyet_aktif.filter(
            IndividualActivity.end_date.isnot(None),
            IndividualActivity.end_date > today,
            IndividualActivity.end_date <= hafta_bitis,
        )
        .order_by(IndividualActivity.end_date.asc())
        .limit(20)
        .all()
    )

    faaliyet_bugun = (
        faaliyet_aktif.filter(IndividualActivity.end_date == today)
        .order_by(IndividualActivity.name.asc())
        .limit(20)
        .all()
    )

    # SP Dönem (Plan Year) bilgileri
    _SP_MANAGE_ROLES = ("Admin", "admin", "tenant_admin", "executive_manager", "kurum_yoneticisi", "ust_yonetim")
    sp_can_manage = bool(current_user.role and current_user.role.name in _SP_MANAGE_ROLES)
    plan_year_feature = False
    plan_years_list = []
    active_plan_year_obj = None
    # S8: yıl seçimi session'dan gelir; eskiden takvim yılına sabitti
    active_plan_year_val = resolve_request_year()

    tenant = current_user.tenant
    if tenant and tenant_id:  # K5: yıl bazlılık koşulsuz
        plan_year_feature = True
        try:
            from app.models.plan_year import PlanYear
            from app.services.plan_year_service import list_plan_years, get_plan_year
            plan_years_list = list_plan_years(tenant_id)
            active_plan_year_val = resolve_request_year()
            available_years = [py.year for py in plan_years_list]
            if available_years and active_plan_year_val not in available_years:
                active_plan_year_val = available_years[0]
            active_plan_year_obj = get_plan_year(tenant_id, active_plan_year_val)
        except Exception as _e:
            import logging
            logging.getLogger(__name__).warning(f"[masaustu] plan_year load error: {_e}")

    # Kurum stratejileri (tenant_admin / executive_manager için)
    stratejiler = []
    if tenant_id and current_user.role and current_user.role.name in (
        "tenant_admin", "executive_manager", "Admin"
    ):
        stratejiler = (
            Strategy.query
            .filter_by(tenant_id=tenant_id, is_active=True)
            .order_by(Strategy.code)
            .limit(3)
            .all()
        )

    ay_isimleri = [
        "",
        _("Ocak"),
        _("Şubat"),
        _("Mart"),
        _("Nisan"),
        _("Mayıs"),
        _("Haziran"),
        _("Temmuz"),
        _("Ağustos"),
        _("Eylül"),
        _("Ekim"),
        _("Kasım"),
        _("Aralık"),
    ]
    bu_ay_ad = ay_isimleri[cm] if 1 <= cm <= 12 else str(cm)

    # KOE — Kurumsal Olgunluk Endeksi (L1). Yalnızca yönetici/üst yönetim görür
    # (standart kullanıcı KOE'yi besler ama görmez). Saf okuma, hata sayfayı düşürmez.
    koe = None
    koe_danisman = None
    if sp_can_manage and tenant_id:
        try:
            from app.services.koe_service import compute_koe, yapi_danismani
            koe = compute_koe(tenant_id)
            koe_danisman = yapi_danismani(koe)
        except Exception as koe_err:
            current_app.logger.warning(f"[masaustu] KOE hesaplanamadı: {koe_err}")

    # UX-PLANI B: veri girişi bekleyen PG'lerim (bitmiş dönemi verisiz olanlar). Hata sayfayı düşürmez.
    bekleyen_pg = {"items": [], "toplam": 0}
    try:
        from app.services.bekleyen_pg_service import bekleyen_pg_listesi
        bekleyen_pg = bekleyen_pg_listesi(current_user)
    except Exception as bp_err:
        current_app.logger.warning(f"[masaustu] bekleyen PG listesi alınamadı: {bp_err}")

    # UX-PLANI E: ilk kurulum kontrol listesi (yalnız yönetici, tamamlanmamış, gizlenmemiş).
    ilk_kurulum = None
    try:
        from app.services.ilk_kurulum_service import kontrol_listesi
        ilk_kurulum = kontrol_listesi(current_user)
    except Exception as ik_err:
        current_app.logger.warning(f"[masaustu] ilk kurulum listesi alınamadı: {ik_err}")

    return render_template(
        "platform/masaustu/index.html",
        ilk_kurulum=ilk_kurulum,
        bekleyen_pg=bekleyen_pg,
        koe=koe,
        koe_danisman=koe_danisman,
        bireysel_pgs=bireysel_pgs,
        bireysel_faaliyetler=bireysel_faaliyetler,
        surec_pgs=surec_pgs,
        favori_pgs=favori_pgs,
        bildirimler=bildirimler,
        stratejiler=stratejiler,
        toplam_bireysel_pg=toplam_bireysel_pg,
        toplam_faaliyet=toplam_faaliyet,
        toplam_bildirim=toplam_bildirim,
        toplam_surec_pg=toplam_surec_pg,
        eksik_pg_bu_ay=eksik_pg_bu_ay,
        faaliyet_geciken=faaliyet_geciken,
        faaliyet_hafta=faaliyet_hafta,
        faaliyet_bugun=faaliyet_bugun,
        bu_ay_ad=bu_ay_ad,
        bugun_iso=today.isoformat(),
        plan_year_feature=plan_year_feature,
        plan_years=plan_years_list,
        active_plan_year=active_plan_year_obj,
        active_plan_year_val=active_plan_year_val,
        sp_can_manage=sp_can_manage,
        current_cal_year=date.today().year,
    )


def _parse_iso_date(raw: str | None) -> date | None:
    if not raw:
        return None
    s = str(raw).strip()
    if not s:
        return None
    try:
        return date.fromisoformat(s[:10])
    except ValueError:
        return None


def _year_process_filter(tenant_id):
    """Seçili yılın süreç kopyaları (+ yılı belirsiz olanlar); yıl çözülemezse None.

    Süreçler yıl bazlı kopyalanır (plan_year_id); süzgeç olmazsa aynı süreç her
    yılın kopyasıyla birden çok kez listelenir.
    """
    try:
        from app.services.plan_year_service import get_plan_year
        py = get_plan_year(tenant_id, resolve_request_year())
    except Exception as err:
        current_app.logger.warning(f"[takvim] plan yılı çözülemedi: {err}")
        return None
    if not py:
        return None
    return or_(Process.plan_year_id == py.id, Process.plan_year_id.is_(None))


def _processes_for_activity_quick_create(user) -> list[dict]:
    """Takvimden faaliyet eklenebilecek süreçler (seçili yıla göre).

    Kurum yöneticisi / üst yönetim: kurumdaki tüm aktif süreçler.
    Diğer kullanıcılar: yalnızca üye veya lider oldukları süreçler.
    """
    q = Process.query.filter(
        Process.tenant_id == user.tenant_id,
        Process.is_active.is_(True),
    )
    year_f = _year_process_filter(user.tenant_id)
    if year_f is not None:
        q = q.filter(year_f)
    if not is_privileged(user):
        member_process_ids = db.session.query(process_members.c.process_id).filter(
            process_members.c.user_id == user.id
        )
        leader_process_ids = db.session.query(process_leaders.c.process_id).filter(
            process_leaders.c.user_id == user.id
        )
        q = q.filter(Process.id.in_(member_process_ids.union(leader_process_ids).subquery()))
    rows = q.order_by(Process.code, Process.name).all()
    out = []
    for p in rows:
        nm = p.name or f"Süreç #{p.id}"
        out.append({"id": p.id, "name": f"[{p.code}] {nm}" if p.code else nm})
    return out


def _tenant_user_options(tenant_id) -> list[dict]:
    """Kurumun aktif kullanıcıları (atama ve süzgeç seçicileri için)."""
    out = []
    for u in (
        CoreUser.query.filter_by(tenant_id=tenant_id, is_active=True)
        .order_by(CoreUser.first_name, CoreUser.last_name, CoreUser.email)
        .all()
    ):
        full = f"{(u.first_name or '').strip()} {(u.last_name or '').strip()}".strip() or (u.email or "")
        out.append({"id": int(u.id), "full_name": full, "email": u.email or ""})
    return out


def _projects_for_task_quick_create(user) -> list[dict]:
    """Görev oluşturma yetkisi olan projeler."""
    kid = getattr(user, "kurum_id", None) or getattr(user, "tenant_id", None)
    if not kid:
        return []
    rows = (
        Project.query.filter(Project.kurum_id == kid, Project.is_archived.is_(False))
        .order_by(Project.name)
        .limit(100)
        .all()
    )
    out: list[dict] = []
    for p in rows:
        if user_can_edit_tasks(user, p):
            out.append({"id": p.id, "name": (p.name or f"Proje #{p.id}")})
    return out


def _task_form_meta_calendar(user) -> dict:
    """Proje görevi formu (task_form.html) ile uyumlu PG listesi + kurum kullanıcıları."""
    from app_platform.modules.proje.helpers import kpis_for_tenant, tenant_core_users, kurum_id

    kid = kurum_id()
    kpis = kpis_for_tenant()
    out_kpis = []
    for k in kpis:
        proc = k.process
        code = (getattr(proc, "code", None) or "?") if proc else "?"
        kc = (k.code or "").strip()
        nm = (k.name or "").strip()
        out_kpis.append({"id": k.id, "label": f"[{code}] {kc} {nm}".strip()})
    users = tenant_core_users(kid)
    out_users = []
    for u in users:
        fn = (u.first_name or "").strip()
        ln = (u.last_name or "").strip()
        full_name = f"{fn} {ln}".strip() or (u.email or "")
        out_users.append({"id": int(u.id), "full_name": full_name, "email": u.email or ""})
    return {"kpis": out_kpis, "users": out_users}


_DONE_STATUSES = {"Tamamlandı", "Tamamlandi", "Done", "Completed"}
_CANCEL_STATUSES = {"İptal", "Iptal", "Cancelled", "Canceled"}

_CAL_COLORS = {
    "process_activity": ("#10b981", "#10b981"),
    "project_task": ("#3b82f6", "#3b82f6"),
    "individual_activity": ("#f59e0b", "#d97706"),
}
_CAL_DONE_COLOR = "#94a3b8"
_CAL_CANCEL_COLOR = "#cbd5e1"
_CAL_OVERDUE_COLOR = "#ef4444"


def _calendar_event(*, ev_id, kind, title, start, end, all_day, url, status, overdue_ref, entity_id,
                    can_move, assignees=None, owner=None, process_id=None, timed_reminder=False):
    """Tek takvim olayı sözlüğü — renk durumdan (tamam / iptal / gecikmiş) türetilir."""
    bg, border = _CAL_COLORS[kind]
    st = (status or "").strip()
    done = st in _DONE_STATUSES
    cancelled = st in _CANCEL_STATUSES
    overdue = False
    if not done and not cancelled and overdue_ref is not None:
        ref = overdue_ref.date() if isinstance(overdue_ref, datetime) else overdue_ref
        overdue = ref < date.today()
    classes = [f"cal-ev-{kind}"]
    if done:
        bg = border = _CAL_DONE_COLOR
        classes.append("cal-ev-done")
    elif cancelled:
        bg = border = _CAL_CANCEL_COLOR
        classes.append("cal-ev-cancelled")
    elif overdue:
        bg = border = _CAL_OVERDUE_COLOR
        classes.append("cal-ev-overdue")
    return {
        "id": ev_id,
        "title": title,
        "start": start,
        "end": end,
        "allDay": all_day,
        "backgroundColor": bg,
        "borderColor": border,
        "textColor": "#475569" if cancelled else "#ffffff",
        "url": url,
        "classNames": classes,
        "extendedProps": {
            "sourceType": kind,
            "entityId": entity_id,
            "status": st,
            "done": done,
            "overdue": overdue,
            "canMove": bool(can_move),
            "assignees": assignees or [],
            "owner": owner,
            "processId": process_id,
            "timedReminder": timed_reminder,
        },
    }


def _collect_calendar_events(
    start_d: date,
    end_d: date,
    *,
    org_scope: bool,
    user=None,
    filter_user_id: int | None = None,
    filter_process_id: int | None = None,
) -> list[dict]:
    """Takvim etkinliklerini derle (atananlar veya kurum geneli).

    Kurum kapsamı yalnızca yetkili rollere (Admin / tenant_admin / executive_manager)
    verilir; diğerleri istenen kapsam ne olursa olsun kendi kapsamına düşer.
    Kişi / süreç süzgeçleri de yalnızca kurum kapsamında geçerlidir.
    """
    user = user or current_user
    if org_scope and not is_privileged(user):
        org_scope = False
    if not org_scope:
        filter_user_id = None
        filter_process_id = None
    start_dt = datetime.combine(start_d, time.min)
    end_dt = datetime.combine(end_d, time.max.replace(microsecond=0))
    events: list[dict] = []
    manager = bool(org_scope)  # kurum kapsamı = yetkili rol → her olayı taşıyabilir

    names = {int(u["id"]): u["full_name"] for u in _tenant_user_options(user.tenant_id)} if org_scope else {}

    # 1) Süreç faaliyetleri
    if org_scope:
        proc_q = Process.query.filter(
            Process.tenant_id == user.tenant_id,
            Process.is_active.is_(True),
        )
        if filter_process_id:
            proc_q = proc_q.filter(Process.id == filter_process_id)
        process_ids_sq = proc_q.with_entities(Process.id).subquery()
    else:
        member_process_ids = db.session.query(process_members.c.process_id).filter(
            process_members.c.user_id == user.id
        )
        leader_process_ids = db.session.query(process_leaders.c.process_id).filter(
            process_leaders.c.user_id == user.id
        )
        process_ids_sq = member_process_ids.union(leader_process_ids).subquery()

    act_q = (
        ProcessActivity.query.join(Process, Process.id == ProcessActivity.process_id)
        .filter(
            ProcessActivity.is_active.is_(True),
            Process.id.in_(process_ids_sq),
            or_(
                and_(ProcessActivity.start_at.isnot(None), ProcessActivity.start_at <= end_dt, ProcessActivity.end_at >= start_dt),
                and_(ProcessActivity.start_at.isnot(None), ProcessActivity.end_at.is_(None), ProcessActivity.start_at >= start_dt, ProcessActivity.start_at <= end_dt),
                and_(ProcessActivity.start_date.isnot(None), ProcessActivity.start_date <= end_d, ProcessActivity.end_date >= start_d),
                and_(ProcessActivity.start_date.isnot(None), ProcessActivity.end_date.is_(None), ProcessActivity.start_date >= start_d, ProcessActivity.start_date <= end_d),
            ),
        )
    )
    if filter_user_id:
        act_q = act_q.filter(
            ProcessActivity.id.in_(
                db.session.query(ProcessActivityAssignee.activity_id).filter(
                    ProcessActivityAssignee.user_id == filter_user_id
                )
            )
        )
    activities = act_q.all()

    assignee_map: dict[int, list[str]] = {}
    if org_scope and activities:
        rows = (
            db.session.query(ProcessActivityAssignee.activity_id, ProcessActivityAssignee.user_id)
            .filter(ProcessActivityAssignee.activity_id.in_([a.id for a in activities]))
            .all()
        )
        for aid, uid in rows:
            assignee_map.setdefault(int(aid), []).append(names.get(int(uid), f"#{uid}"))

    for a in activities:
        can_move = manager
        if not can_move:
            try:
                from micro.modules.surec.helpers import _user_can_manage_activity
                can_move = bool(_user_can_manage_activity(user, a.process, a))
            except Exception as err:
                current_app.logger.warning(f"[takvim] taşıma yetkisi çözülemedi: {err}")
        common = dict(
            ev_id=f"process-{a.id}",
            kind="process_activity",
            title=f"{_('Süreç Faaliyeti')}: {a.name}",
            url=f"/process/{a.process_id}/karne?tab=activities",
            status=a.status,
            entity_id=a.id,
            can_move=can_move,
            assignees=assignee_map.get(a.id, []),
            process_id=a.process_id,
        )
        if a.start_at or a.end_at:
            st = a.start_at or datetime.combine(a.start_date, time.min)
            en = a.end_at or (datetime.combine(a.end_date, time.max.replace(microsecond=0)) if a.end_date else st)
            events.append(_calendar_event(
                start=st.strftime("%Y-%m-%dT%H:%M:%S"),
                end=en.strftime("%Y-%m-%dT%H:%M:%S") if en else None,
                all_day=False, overdue_ref=en, **common))
            continue
        # Saat bilgisi yok: all-day
        sd = a.start_date or a.end_date
        ed = a.end_date or a.start_date
        if not sd:
            continue
        events.append(_calendar_event(
            start=sd.isoformat(),
            end=(ed + timedelta(days=1)).isoformat(),
            all_day=True, overdue_ref=ed, **common))

    # 2) Proje görevleri
    kurum_id = getattr(user, "kurum_id", None) or getattr(user, "tenant_id", None)
    if org_scope:
        access_filter = and_(
            Project.kurum_id == kurum_id,
            Project.is_archived.is_(False),
        )
    else:
        # Bazı kurulumlarda project_leaders/project_members fiziksel tablo olarak yok.
        # Bu durumda manager + doğrudan görev ataması ile güvenli fallback uygula.
        proj_access_conds = [Project.manager_id == user.id]
        if _table_exists("project_leaders"):
            leader_proj_ids = db.session.query(project_leaders.c.project_id).filter(
                project_leaders.c.user_id == user.id
            )
            proj_access_conds.append(Project.id.in_(leader_proj_ids))
        if _table_exists("project_members"):
            member_proj_ids = db.session.query(project_members.c.project_id).filter(
                project_members.c.user_id == user.id
            )
            proj_access_conds.append(Project.id.in_(member_proj_ids))
        access_filter = or_(Task.assignee_id == user.id, *proj_access_conds)
    task_q = (
        Task.query.join(Project, Project.id == Task.project_id)
        .filter(
            Task.is_archived.is_(False),
            access_filter,
            or_(
                and_(Task.reminder_date.isnot(None), Task.reminder_date >= start_dt, Task.reminder_date <= end_dt),
                and_(Task.start_date.isnot(None), Task.start_date >= start_d, Task.start_date <= end_d),
                and_(Task.due_date.isnot(None), Task.due_date >= start_d, Task.due_date <= end_d),
            ),
        )
    )
    if filter_user_id:
        task_q = task_q.filter(Task.assignee_id == filter_user_id)
    if filter_process_id:
        task_q = task_q.filter(
            Task.process_kpi_id.in_(
                db.session.query(ProcessKpi.id).filter(ProcessKpi.process_id == filter_process_id)
            )
        )
    for t in task_q.all():
        can_move = manager or int(t.assignee_id or 0) == int(user.id)
        if not can_move:
            try:
                can_move = bool(user_can_edit_tasks(user, t.project))
            except Exception as err:
                current_app.logger.warning(f"[takvim] görev taşıma yetkisi çözülemedi: {err}")
        who = [names[int(t.assignee_id)]] if t.assignee_id and int(t.assignee_id) in names else []
        common = dict(
            ev_id=f"task-{t.id}",
            kind="project_task",
            title=f"{_('Proje Görevi')}: {t.title}",
            url=f"/project/{t.project_id}/task/{t.id}",
            status=t.status,
            entity_id=t.id,
            can_move=can_move,
            assignees=who,
        )
        # Öncelik: saatli hatırlatma
        if t.reminder_date:
            st = t.reminder_date
            en = st + timedelta(minutes=30)
            events.append(_calendar_event(
                start=st.strftime("%Y-%m-%dT%H:%M:%S"),
                end=en.strftime("%Y-%m-%dT%H:%M:%S"),
                all_day=False, overdue_ref=t.due_date or st, timed_reminder=True, **common))
            continue
        sd = t.start_date or t.due_date
        ed = t.due_date or t.start_date
        if not sd:
            continue
        events.append(_calendar_event(
            start=sd.isoformat(),
            end=(ed + timedelta(days=1)).isoformat(),
            all_day=True, overdue_ref=ed, **common))

    # 3) Bireysel faaliyet — kendi kapsamında yalnız oturum sahibi, kurum kapsamında herkes
    ind_q = IndividualActivity.query.filter(IndividualActivity.is_active.is_(True))
    if org_scope:
        ind_q = ind_q.join(CoreUser, CoreUser.id == IndividualActivity.user_id).filter(
            CoreUser.tenant_id == user.tenant_id
        )
        if filter_user_id:
            ind_q = ind_q.filter(IndividualActivity.user_id == filter_user_id)
        if filter_process_id:
            ind_q = ind_q.filter(IndividualActivity.source_process_id == filter_process_id)
    else:
        ind_q = ind_q.filter(IndividualActivity.user_id == user.id)
    for ia in ind_q.all():
        sd = ia.start_date or ia.end_date
        ed = ia.end_date or ia.start_date
        if not sd:
            continue
        if ed < start_d or sd > end_d:
            continue
        mine = int(ia.user_id) == int(user.id)
        owner = None if mine else names.get(int(ia.user_id), f"#{ia.user_id}")
        title = f"{_('Kendime Görev')}: {ia.name}" if mine else f"{_('Bireysel Görev')}: {ia.name} ({owner})"
        events.append(_calendar_event(
            ev_id=f"indiv-{ia.id}",
            kind="individual_activity",
            title=title,
            start=sd.isoformat(),
            end=(ed + timedelta(days=1)).isoformat(),
            all_day=True,
            url="/individual/scorecard" if mine else None,
            status=ia.status,
            overdue_ref=ed,
            entity_id=ia.id,
            can_move=manager or mine,
            owner=owner,
        ))

    return events


def _calendar_range_args() -> tuple[date, date]:
    start_d = _parse_iso_date(request.args.get("start"))
    end_d = _parse_iso_date(request.args.get("end"))
    if not start_d:
        start_d = date.today().replace(day=1)
    if not end_d:
        end_d = start_d + timedelta(days=45)
    if end_d < start_d:
        start_d, end_d = end_d, start_d
    return start_d, end_d


def _int_arg(name: str) -> int | None:
    try:
        v = int(request.args.get(name, ""))
        return v if v > 0 else None
    except (TypeError, ValueError):
        return None


def _calendar_events_response(org_scope: bool):
    start_d, end_d = _calendar_range_args()
    events = _collect_calendar_events(
        start_d, end_d,
        org_scope=org_scope,
        filter_user_id=_int_arg("user_id"),
        filter_process_id=_int_arg("process_id"),
    )
    return jsonify({"success": True, "events": events, "timezone": "Europe/Istanbul"})


@app_bp.route("/api/calendar/events", methods=["GET"])
@login_required
def masaustu_calendar_events():
    """Masaüstü takvimi: yetkili roller için kurum geneli, diğerleri için kişisel kapsam."""
    return _calendar_events_response(org_scope=is_privileged(current_user))


@app_bp.route("/api/calendar/events/org", methods=["GET"])
@login_required
def kurum_calendar_events():
    """Kurum geneli takvim (yalnız yetkili roller; diğerleri kişisel kapsama düşer)."""
    return _calendar_events_response(org_scope=True)


@app_bp.route("/api/calendar/quick-create-meta", methods=["GET"])
@login_required
def api_calendar_quick_create_meta():
    """Takvimden hızlı oluşturma: süreç / proje / bireysel için seçenek listeleri ve bayraklar."""
    processes = _processes_for_activity_quick_create(current_user)
    projects = _projects_for_task_quick_create(current_user)
    privileged = bool(is_privileged(current_user))
    return jsonify(
        {
            "success": True,
            "processes": processes,
            "projects": projects,
            "can_process": len(processes) > 0,
            "can_project": len(projects) > 0,
            "can_individual": True,
            "can_assign_others": privileged,
            "can_filter": privileged,
            "users": _tenant_user_options(current_user.tenant_id) if privileged else [],
            "task_form": _task_form_meta_calendar(current_user),
        }
    )


def _parse_local_dt(raw) -> datetime | None:
    txt = str(raw or "").strip()
    if len(txt) < 10:
        return None
    try:
        if len(txt) >= 19:
            return datetime.strptime(txt[:19].replace(" ", "T"), "%Y-%m-%dT%H:%M:%S")
        if len(txt) >= 16:
            return datetime.strptime(txt[:16].replace(" ", "T"), "%Y-%m-%dT%H:%M")
        return datetime.strptime(txt[:10], "%Y-%m-%d")
    except ValueError:
        return None


@app_bp.route("/api/calendar/event/move", methods=["POST"])
@login_required
def api_calendar_event_move():
    """Sürükle-bırak / yeniden boyutlandırma ile olay tarihini değiştir.

    Yetki, olayın kendi modülündeki kuralla aynıdır (yönetici, süreç lideri/atanan,
    proje üyesi, bireysel faaliyette sahibi).
    """
    data = request.get_json() or {}
    ev_id = str(data.get("id") or "")
    new_start = _parse_local_dt(data.get("start"))
    new_end = _parse_local_dt(data.get("end"))
    all_day = bool(data.get("all_day"))
    kind, _sep, raw_id = ev_id.partition("-")
    if not new_start or not raw_id.isdigit() or kind not in ("process", "task", "indiv"):
        return jsonify({"success": False, "message": _("Geçersiz istek.")}), 400
    rid = int(raw_id)
    # allDay: bitiş dışlayıcı gelir (FullCalendar) → kapsayıcıya çevir
    first = new_start.date()
    if all_day:
        last = (new_end.date() - timedelta(days=1)) if new_end else first
        if last < first:
            last = first
    else:
        last = new_end.date() if new_end else first
    uid = current_user.id
    try:
        if kind == "process":
            act = (
                ProcessActivity.query.join(Process, Process.id == ProcessActivity.process_id)
                .filter(ProcessActivity.id == rid, ProcessActivity.is_active.is_(True),
                        Process.tenant_id == current_user.tenant_id, Process.is_active.is_(True))
                .first()
            )
            if not act:
                return jsonify({"success": False, "message": _("Kayıt bulunamadı.")}), 404
            from micro.modules.surec.helpers import _user_can_manage_activity, muhur_engeli
            if not (is_privileged(current_user) or _user_can_manage_activity(current_user, act.process, act)):
                return jsonify({"success": False, "message": _("Bu faaliyeti değiştirme yetkiniz yok.")}), 403
            engel = muhur_engeli(act)
            if engel:
                return jsonify(engel[0]), engel[1]
            if act.start_at or act.end_at:
                old_s = act.start_at or datetime.combine(act.start_date, time(9, 0))
                old_e = act.end_at or (old_s + timedelta(hours=1))
                if all_day:
                    # Saatli faaliyet gün satırına bırakıldı: saatleri koru, günü kaydır
                    shift = datetime.combine(first, old_s.time()) - old_s
                    act.start_at, act.end_at = old_s + shift, old_e + shift
                else:
                    act.start_at = new_start
                    act.end_at = new_end or (new_start + (old_e - old_s))
                act.start_date = act.start_at.date()
                act.end_date = act.end_at.date()
            else:
                act.start_date, act.end_date = first, last
            res_id = act.id
        elif kind == "task":
            task = (
                Task.query.join(Project, Project.id == Task.project_id)
                .filter(Task.id == rid, Task.is_archived.is_(False),
                        Project.kurum_id == (getattr(current_user, "kurum_id", None) or current_user.tenant_id))
                .first()
            )
            if not task:
                return jsonify({"success": False, "message": _("Kayıt bulunamadı.")}), 404
            if not (int(task.assignee_id or 0) == int(uid) or user_can_edit_tasks(current_user, task.project)):
                return jsonify({"success": False, "message": _("Bu görevi değiştirme yetkiniz yok.")}), 403
            if task.reminder_date:
                task.reminder_date = new_start if not all_day else datetime.combine(first, task.reminder_date.time())
            else:
                task.start_date, task.due_date = first, last
            res_id = task.id
        else:
            ia = IndividualActivity.query.filter_by(id=rid, is_active=True).first()
            owner = db.session.get(CoreUser, ia.user_id) if ia else None
            if not ia or not owner or owner.tenant_id != current_user.tenant_id:
                return jsonify({"success": False, "message": _("Kayıt bulunamadı.")}), 404
            if int(ia.user_id) != int(uid) and not is_privileged(current_user):
                return jsonify({"success": False, "message": _("Bu görevi değiştirme yetkiniz yok.")}), 403
            ia.start_date, ia.end_date = first, last
            res_id = ia.id
        db.session.commit()
        return jsonify({"success": True, "id": res_id})
    except Exception as err:
        db.session.rollback()
        current_app.logger.error(f"[api_calendar_event_move] {err}", exc_info=True)
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400


# ── iCal dışa aktarma / abonelik ─────────────────────────────────────────────
def _ical_serializer():
    from itsdangerous import URLSafeSerializer
    return URLSafeSerializer(current_app.config["SECRET_KEY"], salt="kokpitim-takvim-ical")


def _ics_escape(text) -> str:
    return (str(text or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
            .replace("\r", "").replace("\n", "\\n"))


def _ics_fold(line: str) -> str:
    if len(line.encode("utf-8")) <= 75:
        return line
    parts: list[str] = []
    cur = ""
    for ch in line:
        limit = 75 if not parts else 74
        if len((cur + ch).encode("utf-8")) > limit:
            parts.append(cur)
            cur = ch
        else:
            cur += ch
    parts.append(cur)
    return "\r\n ".join(parts)


def _events_to_ics(events: list[dict], cal_name: str) -> str:
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Kokpitim//Takvim//TR", "CALSCALE:GREGORIAN",
             f"X-WR-CALNAME:{_ics_escape(cal_name)}", "X-WR-TIMEZONE:Europe/Istanbul"]
    for e in events:
        lines += ["BEGIN:VEVENT", f"UID:{e['id']}@kokpitim", f"DTSTAMP:{stamp}",
                  f"SUMMARY:{_ics_escape(e['title'])}"]
        if e.get("allDay"):
            lines.append("DTSTART;VALUE=DATE:" + str(e["start"])[:10].replace("-", ""))
            lines.append("DTEND;VALUE=DATE:" + str(e["end"])[:10].replace("-", ""))
        else:
            lines.append("DTSTART;TZID=Europe/Istanbul:" + str(e["start"]).replace("-", "").replace(":", "")[:15])
            if e.get("end"):
                lines.append("DTEND;TZID=Europe/Istanbul:" + str(e["end"]).replace("-", "").replace(":", "")[:15])
        status = (e.get("extendedProps") or {}).get("status")
        if status:
            lines.append(f"DESCRIPTION:{_ics_escape(status)}")
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(_ics_fold(l) for l in lines) + "\r\n"


@app_bp.route("/api/calendar/ical-link", methods=["GET"])
@login_required
def api_calendar_ical_link():
    """Kişisel iCal abonelik bağlantısı (Google / Outlook / Apple Takvim)."""
    token = _ical_serializer().dumps({"u": int(current_user.id)})
    return jsonify({"success": True, "url": url_for("app_bp.calendar_ical_feed", token=token, _external=True)})


@app_bp.route("/takvim/ical/<token>.ics", methods=["GET"])
def calendar_ical_feed(token: str):
    """Abonelik akışı — oturumsuz; yalnızca imzalı belirteçle, salt okunur, kullanıcının kendi kapsamı."""
    try:
        uid = int(_ical_serializer().loads(token)["u"])
    except Exception:
        return Response("Not found", status=404)
    user = db.session.get(CoreUser, uid)
    if not user or not user.is_active:
        return Response("Not found", status=404)
    today = date.today()
    events = _collect_calendar_events(
        today - timedelta(days=60), today + timedelta(days=365),
        org_scope=is_privileged(user), user=user,
    )
    body = _events_to_ics(events, "Kokpitim")
    return Response(body, mimetype="text/calendar; charset=utf-8",
                    headers={"Cache-Control": "private, max-age=900"})


@app_bp.route("/api/calendar/process/<int:process_id>/activity-form-meta", methods=["GET"])
@login_required
def api_calendar_activity_form_meta(process_id: int):
    """Süreç faaliyeti modalı: PG listesi, atanabilir kullanıcılar, çoklu atama izni (karne ile aynı veri)."""
    p = Process.query.filter_by(
        id=process_id,
        tenant_id=current_user.tenant_id,
        is_active=True,
    ).first()
    if not p:
        return jsonify({"success": False, "message": _("Süreç bulunamadı.")}), 404
    if not user_can_access_process(current_user, p):
        return jsonify({"success": False, "message": _("Bu sürece erişiminiz yok.")}), 403

    kpis = (
        ProcessKpi.query.filter_by(process_id=p.id, is_active=True)
        .order_by(ProcessKpi.code)
        .all()
    )
    kpi_list = []
    for k in kpis:
        kc = (k.code or "").strip() or "?"
        nm = (k.name or "").strip()
        kpi_list.append({"id": k.id, "label": f"[{kc}] {nm}".strip()})

    process_users = []
    seen_uids = set()
    # Yetkili roller (üst yönetim) kurumdaki herkese görev atayabilir
    pool = (
        CoreUser.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
        if is_privileged(current_user)
        else (p.leaders + p.members + p.owners)
    )
    for u in pool:
        if not u or not getattr(u, "is_active", True) or int(u.id) in seen_uids:
            continue
        seen_uids.add(int(u.id))
        fn = (u.first_name or "").strip()
        ln = (u.last_name or "").strip()
        full_name = f"{fn} {ln}".strip() or (u.email or "")
        process_users.append({"id": int(u.id), "full_name": full_name, "email": u.email or ""})

    rn = getattr(current_user.role, "name", None) if current_user.role else None
    can_multi = rn in ("tenant_admin", "executive_manager", "Admin") or any(
        int(u.id) == int(current_user.id) for u in (p.leaders or [])
    )

    return jsonify(
        {
            "success": True,
            "kpis": kpi_list,
            "process_users": process_users,
            "can_multi_assign": bool(can_multi),
        }
    )


@app_bp.route("/api/morning-summary")
@login_required
def api_morning_summary():
    """Yönetici sabah özeti — KPI, faaliyet, proje durumu."""
    from services.executive_morning_service import get_morning_summary
    try:
        data = get_morning_summary(current_user.tenant_id, current_user.id)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        current_app.logger.error(f"[morning_summary] {e}", exc_info=True)
        return jsonify({"success": False, "message": _("Özet yüklenemedi.")}), 500


@app_bp.route("/api/tenant-last-change")
@login_required
def api_tenant_last_change():
    """Tenant'ın son PG veri değişiklik zaman damgası — canlı yenileme sinyali (poll).

    Hafif: tek max sorgusu. Kayıt yoluna dokunmaz.
    """
    from app.models.process import KpiData, ProcessKpi, Process
    tid = current_user.tenant_id
    ts = None
    try:
        ts = (
            db.session.query(db.func.max(KpiData.updated_at))
            .join(ProcessKpi, KpiData.process_kpi_id == ProcessKpi.id)
            .join(Process, ProcessKpi.process_id == Process.id)
            .filter(Process.tenant_id == tid)
            .scalar()
        )
    except Exception as e:
        current_app.logger.info(f"[tenant-last-change] {e}")
    return jsonify({"success": True, "ts": ts.isoformat() if ts else None})


@app_bp.route("/takvim", methods=["GET"])
@login_required
def kurum_takvim():
    """Kurum geneli takvim sayfası."""
    return render_template("platform/calendar/index.html")


# KOE Yapı-Danışmanı'nı yalnızca yönetici/üst yönetim tetikleyebilir (asimetri).
_KOE_DANISMAN_ROLES = (
    "Admin", "admin", "tenant_admin", "executive_manager",
    "kurum_yoneticisi", "ust_yonetim",
)


@app_bp.route("/desktop/api/koe-advisor-ai", methods=["POST"])
@login_required
def masaustu_koe_danisman_ai():
    """KOE Yapı-Danışmanı anlatı + önerilerini LLM ile zenginleştirir (lazy).

    Heuristik boşluk tespiti aynı kalır; yalnızca ifade LLM'le doğallaşır.
    Provider yoksa/çıktı bozuksa heuristik metinle döner (kaynak='heuristik').
    """
    rn = current_user.role.name if current_user.role else None
    if rn not in _KOE_DANISMAN_ROLES:
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403

    tenant_id = current_user.tenant_id
    if not tenant_id:
        return jsonify({"success": False, "message": _("Kurum bulunamadı.")}), 404

    try:
        from app.services.koe_service import compute_koe, yapi_danismani
        koe = compute_koe(tenant_id)
        danisman = yapi_danismani(koe, tenant_id=tenant_id, use_llm=True)
        return jsonify({
            "success": True,
            "kaynak": danisman["kaynak"],
            "anlati": danisman["anlati"],
            "oncelikler": [
                {"baslik": o.get("baslik"), "oneri": o.get("oneri")}
                for o in danisman["oncelikler"]
            ],
        })
    except Exception as e:
        current_app.logger.warning(f"[koe-danisman-ai] {e}")
        return jsonify({"success": False, "message": _("AI danışman çağrılamadı.")}), 500


# ── Yönetim Özeti Dashboard (Faz 4 — üst yönetim '5 saniyede durum') ──────────
@app_bp.route("/yonetim-ozeti")
@login_required
def yonetim_ozeti():
    """Üst yönetim + kurum yöneticisi için tek sayfalık kurum özeti.

    Yalnız privileged roller; diğerleri launcher'a yönlendirilir.
    docs/paketler/ROL-GORUNUM-KATMANI.md Faz 4.
    """
    from flask import redirect, url_for
    from app.constants.roles import is_privileged
    role_name = current_user.role.name if current_user.role else None
    if not is_privileged(role_name):
        return redirect(url_for("app_bp.launcher"))
    return render_template("platform/masaustu/yonetim_ozeti.html")


@app_bp.route("/yonetim-ozeti/api/ozet")
@login_required
def yonetim_ozeti_api():
    """Yönetim özeti verisi (JSON). Yalnız privileged."""
    from app.constants.roles import is_privileged
    role_name = current_user.role.name if current_user.role else None
    if not is_privileged(role_name):
        return jsonify({"success": False, "message": _("Bu sayfaya erişim yetkiniz yok.")}), 403
    try:
        from services.yonetim_ozeti_service import build_yonetim_ozeti
        data = build_yonetim_ozeti(current_user, current_user.tenant_id)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        current_app.logger.error(f"[yonetim_ozeti] {e}", exc_info=True)
        return jsonify({"success": False, "message": _("Özet yüklenemedi.")}), 500
