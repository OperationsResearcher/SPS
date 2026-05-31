"""
Erken Uyarı Servisi — gece çalışan KPI/faaliyet trend analizi.
Tetikleme: app/__init__.py içinde APScheduler ile her gece 02:00.
"""
from __future__ import annotations
from datetime import date, timedelta
from flask import current_app
from app.models import db
from app.models.process import Process, ProcessKpi, KpiData, ProcessActivity
from app.models.core import Notification, User


_WARN_THRESHOLD = 0.80   # hedefin %80 altı → kritik
_TREND_MONTHS   = 3      # kaç ay geriye bakılır


def _send_notification(user_id: int, title: str, message: str, link: str | None = None) -> None:
    """Kullanıcıya sistem bildirimi oluşturur."""
    try:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            link=link or "",
            is_read=False,
        )
        db.session.add(notif)
    except Exception as e:
        current_app.logger.error(f"[early_warning] bildirim oluşturulamadı u={user_id}: {e}")


def _rolling_avg(values: list[float]) -> float | None:
    nums = [v for v in values if v is not None]
    return sum(nums) / len(nums) if nums else None


def run_early_warning(app) -> dict:
    """
    Tüm tenantlar için erken uyarı taraması yapar.
    app context içinde çağrılmalıdır.
    """
    with app.app_context():
        result = {"tenants_scanned": 0, "warnings_sent": 0, "errors": 0}
        today = date.today()
        current_year = today.year
        three_months_ago = today - timedelta(days=90)

        try:
            # Tüm aktif tenant'ların süreç liderlerine bak
            from app.models.core import Tenant
            tenants = Tenant.query.filter_by(is_active=True).all()

            for tenant in tenants:
                result["tenants_scanned"] += 1
                tid = tenant.id

                # Yöneticileri bul (tenant_admin + executive_manager)
                managers = User.query.filter(
                    User.tenant_id == tid,
                    User.is_active == True,
                ).join(User.role).filter(
                    db.text("roles.name IN ('tenant_admin','executive_manager','Admin')")
                ).all()
                manager_ids = [u.id for u in managers]

                # Aktif KPI'ları çek
                kpis = (
                    ProcessKpi.query
                    .join(Process, Process.id == ProcessKpi.process_id)
                    .filter(
                        Process.tenant_id == tid,
                        Process.is_active == True,
                        ProcessKpi.is_active == True,
                    )
                    .all()
                )

                critical_kpis: list[str] = []
                for kpi in kpis:
                    try:
                        target = float(kpi.target_value or 0)
                        if target <= 0:
                            continue
                        # Son 3 ay verisi
                        rows = (
                            KpiData.query
                            .filter(
                                KpiData.process_kpi_id == kpi.id,
                                KpiData.year == current_year,
                                KpiData.data_date >= three_months_ago,
                                KpiData.is_active == True,
                            )
                            .order_by(KpiData.data_date.desc())
                            .limit(6)
                            .all()
                        )
                        if not rows:
                            continue
                        values = []
                        for r in rows:
                            try:
                                values.append(float(r.actual_value))
                            except (TypeError, ValueError):
                                pass
                        avg = _rolling_avg(values)
                        if avg is None:
                            continue
                        direction = (kpi.direction or "Increasing").lower()
                        is_bad = (
                            avg < target * _WARN_THRESHOLD
                            if direction != "decreasing"
                            else avg > target * (2 - _WARN_THRESHOLD)
                        )
                        # Trend: son değer öncekinden daha kötü mü?
                        downtrend = len(values) >= 2 and (
                            values[0] < values[-1]
                            if direction != "decreasing"
                            else values[0] > values[-1]
                        )
                        if is_bad or downtrend:
                            proc = kpi.process
                            critical_kpis.append(
                                f"{kpi.name} ({proc.name if proc else '?'})"
                            )
                            # Süreç liderine de bildirim
                            for leader in (proc.leaders if proc else []):
                                if leader and leader.id not in manager_ids:
                                    _send_notification(
                                        leader.id,
                                        "⚠️ KPI Erken Uyarı",
                                        f"{kpi.name} — hedef performans altında. Lütfen inceleyiniz.",
                                        f"/process/{proc.id}/karne" if proc else None,
                                    )
                                    result["warnings_sent"] += 1
                    except Exception as e:
                        current_app.logger.error(f"[early_warning] kpi={kpi.id}: {e}")
                        result["errors"] += 1

                # Geciken faaliyetler
                overdue_acts = (
                    ProcessActivity.query
                    .join(Process, Process.id == ProcessActivity.process_id)
                    .filter(
                        Process.tenant_id == tid,
                        Process.is_active == True,
                        ProcessActivity.is_active == True,
                        ProcessActivity.status.notin_(["Tamamlandı", "İptal"]),
                        ProcessActivity.end_date < today,
                    )
                    .count()
                )

                # Yöneticilere özet bildirim
                if manager_ids and (critical_kpis or overdue_acts):
                    kpi_part = f"{len(critical_kpis)} KPI hedef altında" if critical_kpis else ""
                    act_part = f"{overdue_acts} geciken faaliyet" if overdue_acts else ""
                    parts = [p for p in [kpi_part, act_part] if p]
                    msg = "Dikkat: " + ", ".join(parts) + ". Detaylar için Masaüstü'nü inceleyiniz."
                    for mid in manager_ids:
                        _send_notification(mid, "📊 Günlük Performans Özeti", msg, "/masaustu")
                        result["warnings_sent"] += 1

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"[early_warning] genel hata: {e}", exc_info=True)
            result["errors"] += 1

        current_app.logger.info(
            f"[early_warning] tamamlandı: {result}"
        )
        return result
