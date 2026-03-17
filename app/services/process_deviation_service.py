# -*- coding: utf-8 -*-
"""
Process Deviation Service
PG performans sapması kontrolü ve bildirim oluşturma.
Hedefin %10 ve üzeri altında gerçekleşen değerlerde bildirim oluşturur.
"""
from typing import Optional
from flask import current_app

from app.models import db
from app.models.process import KpiData, ProcessKpi, Process
from app.models.core import Notification, User


def _parse_float(val) -> Optional[float]:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    try:
        s = str(val).strip().replace(',', '.')
        return float(s) if s else None
    except (ValueError, TypeError):
        return None


def check_pg_performance_deviation(
    kpi_data_id: int,
    sapma_esik_yuzde: float = 10.0
) -> Optional[Notification]:
    """
    KPI verisi kaydedildiğinde/güncellendiğinde performans sapması kontrolü yapar.
    Gerçekleşen değer hedefin sapma_esik_yuzde altındaysa bildirim oluşturur.

    Args:
        kpi_data_id: KpiData ID
        sapma_esik_yuzde: Sapma eşiği (varsayılan %10)

    Returns:
        Oluşturulan Notification veya None
    """
    try:
        entry = KpiData.query.get(kpi_data_id)
        if not entry or not entry.is_active:
            return None

        kpi = ProcessKpi.query.get(entry.process_kpi_id)
        if not kpi:
            return None

        target = _parse_float(entry.target_value) or _parse_float(kpi.target_value)
        actual = _parse_float(entry.actual_value)

        if target is None or actual is None or target == 0:
            return None

        sapma_yuzdesi = ((actual - target) / target) * 100

        direction = (kpi.direction or 'Increasing').strip()
        kritik_sapma = False
        if direction == 'Decreasing':
            kritik_sapma = sapma_yuzdesi >= sapma_esik_yuzde
        else:
            kritik_sapma = sapma_yuzdesi <= -sapma_esik_yuzde

        if not kritik_sapma:
            return None

        process = Process.query.get(kpi.process_id)
        if not process or not process.tenant_id:
            return None

        user_name = ''
        if entry.user_id:
            u = User.query.get(entry.user_id)
            if u:
                user_name = f"{(u.first_name or '')} {(u.last_name or '')}".strip() or u.email

        notification = Notification(
            user_id=entry.user_id,
            tenant_id=process.tenant_id,
            notification_type='pg_performance_deviation',
            title='Kritik Performans Sapması',
            message=(
                f'"{kpi.name}" performans göstergesinde kritik sapma tespit edildi. '
                f'Gerçekleşen: {actual}, Hedef: {target} (Sapma: %{abs(sapma_yuzdesi):.1f})'
            ),
            link=f'/process/{process.id}/karne',
            process_id=process.id,
            related_user_id=entry.user_id
        )
        db.session.add(notification)

        for leader in process.leaders:
            if leader.id != entry.user_id:
                notif_leader = Notification(
                    user_id=leader.id,
                    tenant_id=process.tenant_id,
                    notification_type='pg_performance_deviation',
                    title='Süreçte Kritik Performans Sapması',
                    message=(
                        f'"{kpi.name}" performans göstergesinde kritik sapma tespit edildi. '
                        f'Kullanıcı: {user_name or "Bilinmiyor"}, '
                        f'Gerçekleşen: {actual}, Hedef: {target} (Sapma: %{abs(sapma_yuzdesi):.1f})'
                    ),
                    link=f'/process/{process.id}/karne',
                    process_id=process.id,
                    related_user_id=entry.user_id
                )
                db.session.add(notif_leader)

        db.session.commit()

        if current_app:
            current_app.logger.info(
                f'PG performans sapması bildirimi: KpiData ID {kpi_data_id}, Sapma: %{abs(sapma_yuzdesi):.1f}'
            )

        return notification

    except Exception as e:
        db.session.rollback()
        if current_app:
            current_app.logger.error(f'PG sapma kontrolü hatası: {e}')
        return None
