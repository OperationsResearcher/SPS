"""
Bildirim Tetikleyicileri — Micro Platform
Süreç atama, PG değişikliği, faaliyet ve görev bildirimleri.
Hem uygulama içi (DB) hem e-posta bildirimi gönderir.
"""

from flask import current_app
from app.models import db
from app.models.core import Notification


# ── Bildirim tipi → TenantEmailConfig alanı eşlemesi ──────────────────────────
_NOTIF_PREF_FIELD = {
    "process_assigned": "notify_on_process_assign",
    "kpi_changed":      "notify_on_kpi_change",
    "activity_added":   "notify_on_activity_add",
    "task_assigned":    "notify_on_task_assign",
}

# ── E-posta HTML şablonları ────────────────────────────────────────────────────
_EMAIL_TEMPLATE = """\
<!DOCTYPE html>
<html lang="tr">
<body style="font-family:Arial,sans-serif;background:#f8fafc;margin:0;padding:24px;">
  <div style="max-width:520px;margin:0 auto;background:#fff;border-radius:10px;
              box-shadow:0 2px 8px rgba(0,0,0,.08);overflow:hidden;">
    <div style="background:#4f46e5;padding:20px 28px;">
      <span style="color:#fff;font-size:18px;font-weight:700;">Kokpitim</span>
    </div>
    <div style="padding:28px;">
      <h2 style="margin:0 0 12px;font-size:16px;color:#1e293b;">{title}</h2>
      <p style="margin:0 0 20px;font-size:14px;color:#475569;line-height:1.6;">{message}</p>
      {action_btn}
    </div>
    <div style="padding:14px 28px;background:#f1f5f9;font-size:11px;color:#94a3b8;">
      Bu e-posta Kokpitim platformu tarafından otomatik gönderilmiştir.
    </div>
  </div>
</body>
</html>
"""

_ACTION_BTN = """\
<a href="{link}" style="display:inline-block;padding:10px 22px;background:#4f46e5;
   color:#fff;border-radius:6px;text-decoration:none;font-size:13px;font-weight:600;">
  Görüntüle
</a>
"""


def _email_pref_enabled(tenant_id, notification_type):
    """Tenant'ın bu bildirim tipi için mail göndermesi gerekiyor mu?"""
    try:
        from app.models.email_config import TenantEmailConfig
        cfg = TenantEmailConfig.query.filter_by(tenant_id=tenant_id).first()
        if cfg is None:
            return True   # kayıt yoksa varsayılan: açık
        field = _NOTIF_PREF_FIELD.get(notification_type, "")
        return bool(getattr(cfg, field, True))
    except Exception as e:
        current_app.logger.warning(f"[notification_triggers._email_pref_enabled] {e}")
        return True


def _send_email(to_user, title, message, tenant_id, notification_type, link=None):
    """Kullanıcıya e-posta gönderir — tercih kapalıysa atlar."""
    if not to_user.email:
        return
    if not _email_pref_enabled(tenant_id, notification_type):
        return
    try:
        from micro.services.email_service import send_notification_email
        action_btn = _ACTION_BTN.format(link=link) if link else ""
        html = _EMAIL_TEMPLATE.format(title=title, message=message, action_btn=action_btn)
        text = f"{title}\n\n{message}\n\n{link or ''}"
        send_notification_email(
            to_email=to_user.email,
            subject=title,
            html_body=html,
            tenant_id=tenant_id,
            text_body=text,
        )
    except Exception as e:
        current_app.logger.warning(f"[notification_triggers._send_email] {e}")


def _create(user_id, tenant_id, notification_type, title, message, link=None, related_user_id=None):
    """Tek bir uygulama içi bildirim kaydı oluşturur ve WebSocket ile iletir."""
    try:
        notif = Notification(
            user_id=user_id,
            tenant_id=tenant_id,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
            is_read=False,
            related_user_id=related_user_id,
        )
        db.session.add(notif)
        db.session.flush()

        try:
            from app.extensions import socketio
            socketio.emit(
                "new_notification",
                {"id": notif.id, "title": title, "message": message, "type": notification_type},
                room=f"user_{user_id}",
            )
        except Exception as ws_err:
            current_app.logger.warning(f"[notification_triggers] WebSocket push failed: {ws_err}")

    except Exception as e:
        current_app.logger.error(f"[notification_triggers._create] {e}")


def notify_process_assignment(process, user, role, actor=None):
    """
    Kullanıcı bir sürece lider veya üye olarak atandığında bildirim gönderir.
    """
    actor_name = (actor.first_name or actor.email) if actor else "Sistem"
    title = f"Sürece Atandınız: {process.name}"
    message = f"{actor_name} sizi '{process.name}' sürecine {role} olarak atadı."
    link = f"/micro/surec/{process.id}/karne"

    _create(
        user_id=user.id,
        tenant_id=process.tenant_id,
        notification_type="process_assigned",
        title=title,
        message=message,
        link=link,
        related_user_id=actor.id if actor else None,
    )
    _send_email(user, title, message, process.tenant_id, "process_assigned", link)


def notify_kpi_change(kpi, process, change_type="eklendi", actor=None):
    """
    Süreçte PG eklendiğinde veya güncellendiğinde sürecin tüm lider ve üyelerine bildirim gönderir.
    """
    actor_name = (actor.first_name or actor.email) if actor else "Sistem"
    title = f"Performans Göstergesi {change_type.capitalize()}: {process.name}"
    message = f"'{kpi.name}' performans göstergesi {change_type}. İşlemi yapan: {actor_name}"
    link = f"/micro/surec/{process.id}/karne"

    recipients = set()
    for u in process.leaders:
        recipients.add(u.id)
    for u in process.members:
        recipients.add(u.id)
    if actor:
        recipients.discard(actor.id)

    # Kullanıcı nesnelerini id → user map'i ile al
    from app.models.core import User
    users = {u.id: u for u in User.query.filter(User.id.in_(recipients)).all()}

    for uid in recipients:
        _create(
            user_id=uid,
            tenant_id=process.tenant_id,
            notification_type="kpi_changed",
            title=title,
            message=message,
            link=link,
            related_user_id=actor.id if actor else None,
        )
        if uid in users:
            _send_email(users[uid], title, message, process.tenant_id, "kpi_changed", link)


def notify_activity_assignment(activity, process, actor=None):
    """
    Sürece faaliyet eklendiğinde sürecin tüm lider ve üyelerine bildirim gönderir.
    """
    actor_name = (actor.first_name or actor.email) if actor else "Sistem"
    title = f"Yeni Faaliyet: {process.name}"
    message = f"'{activity.name}' faaliyeti eklendi. İşlemi yapan: {actor_name}"
    link = f"/micro/surec/{process.id}/karne"

    recipients = set()
    for u in process.leaders:
        recipients.add(u.id)
    for u in process.members:
        recipients.add(u.id)
    if actor:
        recipients.discard(actor.id)

    from app.models.core import User
    users = {u.id: u for u in User.query.filter(User.id.in_(recipients)).all()}

    for uid in recipients:
        _create(
            user_id=uid,
            tenant_id=process.tenant_id,
            notification_type="activity_added",
            title=title,
            message=message,
            link=link,
            related_user_id=actor.id if actor else None,
        )
        if uid in users:
            _send_email(users[uid], title, message, process.tenant_id, "activity_added", link)


def notify_task_assignment(task_name, assigned_user, tenant_id, actor=None, task_link=None):
    """
    Bir projede görev atandığında ilgili kullanıcıya bildirim gönderir.
    """
    actor_name = (actor.first_name or actor.email) if actor else "Sistem"
    title = "Size Görev Atandı"
    message = f"'{task_name}' görevi size atandı. İşlemi yapan: {actor_name}"

    _create(
        user_id=assigned_user.id,
        tenant_id=tenant_id,
        notification_type="task_assigned",
        title=title,
        message=message,
        link=task_link,
        related_user_id=actor.id if actor else None,
    )
    _send_email(assigned_user, title, message, tenant_id, "task_assigned", task_link)
