"""Masaüstüm modülü — kullanıcının kişisel özet ekranı.

Tüm modüllerden gelen:
- Bireysel Performans Göstergeleri (PG) ve süreç PG'leri
- Görevler / faaliyetler
- Okunmamış bildirimler
- Kurum özeti (tenant_admin için)
"""

from datetime import date, timedelta

from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import case

from micro import micro_bp
from app.models import db
from app.utils.process_utils import data_date_to_period_keys
from app.models.process import (
    IndividualPerformanceIndicator,
    IndividualActivity,
    IndividualKpiData,
    ProcessKpi,
)
from app.models.core import Notification, Strategy


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
