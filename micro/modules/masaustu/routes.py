"""Masaüstüm modülü — kullanıcının kişisel özet ekranı.

Tüm modüllerden gelen:
- Bireysel Performans Göstergeleri (PG) ve süreç PG'leri
- Görevler / faaliyetler
- Okunmamış bildirimler
- Kurum özeti (tenant_admin için)
"""

from datetime import date, timedelta, datetime, time

from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import case, or_, and_, inspect as sa_inspect

from micro import micro_bp
from app.models import db
from app.utils.process_utils import data_date_to_period_keys
from app.models.process import (
    IndividualPerformanceIndicator,
    IndividualActivity,
    IndividualKpiData,
    ProcessKpi,
    ProcessActivity,
    Process,
    process_members,
    process_leaders,
)
from app.models.core import Notification, Strategy
from models import Project, Task, project_members, project_leaders


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


@micro_bp.route("/masaustu")
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
            ProcessKpi.is_active == True,
            Process.is_active == True,
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
        "Ocak",
        "Şubat",
        "Mart",
        "Nisan",
        "Mayıs",
        "Haziran",
        "Temmuz",
        "Ağustos",
        "Eylül",
        "Ekim",
        "Kasım",
        "Aralık",
    ]
    bu_ay_ad = ay_isimleri[cm] if 1 <= cm <= 12 else str(cm)

    return render_template(
        "micro/masaustu/index.html",
        bireysel_pgs=bireysel_pgs,
        bireysel_faaliyetler=bireysel_faaliyetler,
        surec_pgs=surec_pgs,
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


def _collect_calendar_events(start_d: date, end_d: date, *, org_scope: bool) -> list[dict]:
    """Takvim etkinliklerini derle (atananlar veya kurum geneli)."""
    start_dt = datetime.combine(start_d, time.min)
    end_dt = datetime.combine(end_d, time.max.replace(microsecond=0))
    user = current_user
    events: list[dict] = []

    # 1) Süreç faaliyetleri
    if org_scope:
        process_ids_sq = (
            Process.query.filter(
                Process.tenant_id == user.tenant_id,
                Process.is_active.is_(True),
            )
            .with_entities(Process.id)
            .subquery()
        )
    else:
        member_process_ids = db.session.query(process_members.c.process_id).filter(
            process_members.c.user_id == user.id
        )
        leader_process_ids = db.session.query(process_leaders.c.process_id).filter(
            process_leaders.c.user_id == user.id
        )
        process_ids_sq = member_process_ids.union(leader_process_ids).subquery()

    activities = (
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
        .all()
    )
    for a in activities:
        if a.start_at or a.end_at:
            st = a.start_at or datetime.combine(a.start_date, time.min)
            en = a.end_at or (datetime.combine(a.end_date, time.max.replace(microsecond=0)) if a.end_date else st)
            if not st:
                continue
            events.append(
                {
                    "id": f"process-{a.id}",
                    "title": f"Süreç Faaliyeti: {a.name}",
                    "start": st.strftime("%Y-%m-%dT%H:%M:%S"),
                    "end": en.strftime("%Y-%m-%dT%H:%M:%S") if en else None,
                    "allDay": False,
                    "backgroundColor": "#10b981",
                    "borderColor": "#10b981",
                    "textColor": "#ffffff",
                    "url": f"/process/{a.process_id}/karne?tab=activities",
                    "extendedProps": {"sourceType": "process_activity"},
                }
            )
            continue

        # Saat bilgisi yok: all-day
        sd = a.start_date or a.end_date
        ed = a.end_date or a.start_date
        if not sd:
            continue
        events.append(
            {
                "id": f"process-{a.id}",
                "title": f"Süreç Faaliyeti: {a.name}",
                "start": sd.isoformat(),
                "end": (ed + timedelta(days=1)).isoformat() if ed else (sd + timedelta(days=1)).isoformat(),
                "allDay": True,
                "backgroundColor": "#10b981",
                "borderColor": "#10b981",
                "textColor": "#ffffff",
                "url": f"/process/{a.process_id}/karne?tab=activities",
                "extendedProps": {"sourceType": "process_activity"},
            }
        )

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
    tasks = (
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
        .all()
    )
    for t in tasks:
        # Öncelik: saatli hatırlatma
        if t.reminder_date:
            st = t.reminder_date
            en = st + timedelta(minutes=30)
            events.append(
                {
                    "id": f"task-{t.id}",
                    "title": f"Proje Görevi: {t.title}",
                    "start": st.strftime("%Y-%m-%dT%H:%M:%S"),
                    "end": en.strftime("%Y-%m-%dT%H:%M:%S"),
                    "allDay": False,
                    "backgroundColor": "#3b82f6",
                    "borderColor": "#3b82f6",
                    "textColor": "#ffffff",
                    "url": f"/project/{t.project_id}/task/{t.id}",
                    "extendedProps": {"sourceType": "project_task"},
                }
            )
            continue

        sd = t.start_date or t.due_date
        ed = t.due_date or t.start_date
        if not sd:
            continue
        events.append(
            {
                "id": f"task-{t.id}",
                "title": f"Proje Görevi: {t.title}",
                "start": sd.isoformat(),
                "end": (ed + timedelta(days=1)).isoformat() if ed else (sd + timedelta(days=1)).isoformat(),
                "allDay": True,
                "backgroundColor": "#3b82f6",
                "borderColor": "#3b82f6",
                "textColor": "#ffffff",
                "url": f"/project/{t.project_id}/task/{t.id}",
                "extendedProps": {"sourceType": "project_task"},
            }
        )

    return events


@micro_bp.route("/api/calendar/events", methods=["GET"])
@login_required
def masaustu_calendar_events():
    """Masaüstü ortak takvim etkinlikleri (süreç faaliyet + proje görev)."""
    start_d = _parse_iso_date(request.args.get("start"))
    end_d = _parse_iso_date(request.args.get("end"))
    today = date.today()
    if not start_d:
        start_d = today.replace(day=1)
    if not end_d:
        end_d = start_d + timedelta(days=45)
    if end_d < start_d:
        start_d, end_d = end_d, start_d

    events = _collect_calendar_events(start_d, end_d, org_scope=False)
    return jsonify({"success": True, "events": events, "timezone": "Europe/Istanbul"})


@micro_bp.route("/api/calendar/events/org", methods=["GET"])
@login_required
def kurum_calendar_events():
    """Kurum geneli ortak takvim etkinlikleri."""
    start_d = _parse_iso_date(request.args.get("start"))
    end_d = _parse_iso_date(request.args.get("end"))
    today = date.today()
    if not start_d:
        start_d = today.replace(day=1)
    if not end_d:
        end_d = start_d + timedelta(days=45)
    if end_d < start_d:
        start_d, end_d = end_d, start_d

    events = _collect_calendar_events(start_d, end_d, org_scope=True)
    return jsonify({"success": True, "events": events, "timezone": "Europe/Istanbul"})


@micro_bp.route("/takvim", methods=["GET"])
@login_required
def kurum_takvim():
    """Kurum geneli takvim sayfası."""
    return render_template("micro/calendar/index.html")
