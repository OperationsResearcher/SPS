"""
Bildirim Tetikleyicileri — Micro Platform
Süreç atama, PG değişikliği, faaliyet ve görev bildirimleri.
Hem uygulama içi (DB) hem e-posta bildirimi gönderir.
"""

import threading

from flask import current_app
from app.models import db
from app.models.core import Notification


# ── Bildirim tipi → TenantEmailConfig alanı eşlemesi ──────────────────────────
_NOTIF_PREF_FIELD = {
    "process_assigned": "notify_on_process_assign",
    "kpi_changed":      "notify_on_kpi_change",
    "activity_added":   "notify_on_activity_add",
    "activity_reminder": "notify_on_activity_add",
    "activity_auto_completed": "notify_on_activity_add",
    "task_assigned":    "notify_on_task_assign",
    "task_status_changed": "notify_on_task_assign",
    "project_leader_assigned": "notify_on_task_assign",
    "project_member_assigned": "notify_on_task_assign",
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
        from app_platform.services.email_service import send_notification_email
        action_btn = _ACTION_BTN.format(link=link) if link else ""
        html = _EMAIL_TEMPLATE.format(title=title, message=message, action_btn=action_btn)
        text = f"{title}\n\n{message}\n\n{link or ''}"
        ok, err = send_notification_email(
            to_email=to_user.email,
            subject=title,
            html_body=html,
            tenant_id=tenant_id,
            text_body=text,
        )
        if not ok and err:
            current_app.logger.warning(f"[notification_triggers._send_email] {err}")
    except Exception as e:
        current_app.logger.warning(f"[notification_triggers._send_email] {e}")


def _send_email_async(to_user, title, message, tenant_id, notification_type, link=None):
    """
    E-postayı arka planda gönderir; HTTP yanıtını SMTP gecikmesinden kurtarır.
    Uygulama içi bildirim (_create) yine anında session'a yazılır.
    """
    if not to_user or not getattr(to_user, "id", None):
        return
    uid = int(to_user.id)
    app = current_app._get_current_object()

    def _run():
        with app.app_context():
            try:
                from app.models.core import User

                u = User.query.get(uid)
                if u:
                    _send_email(u, title, message, tenant_id, notification_type, link)
            except Exception as e:
                current_app.logger.warning(f"[notification_triggers._send_email_async] {e}")

    threading.Thread(target=_run, daemon=True).start()


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
    link = f"/process/{process.id}/karne"

    _create(
        user_id=user.id,
        tenant_id=process.tenant_id,
        notification_type="process_assigned",
        title=title,
        message=message,
        link=link,
        related_user_id=actor.id if actor else None,
    )
    _send_email_async(user, title, message, process.tenant_id, "process_assigned", link)


def notify_kpi_change(kpi, process, change_type="eklendi", actor=None):
    """
    Süreçte PG eklendiğinde veya güncellendiğinde sürecin tüm lider ve üyelerine bildirim gönderir.
    """
    actor_name = (actor.first_name or actor.email) if actor else "Sistem"
    title = f"Performans Göstergesi {change_type.capitalize()}: {process.name}"
    message = f"'{kpi.name}' performans göstergesi {change_type}. İşlemi yapan: {actor_name}"
    link = f"/process/{process.id}/karne"

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
    link = f"/process/{process.id}/karne"

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


def notify_activity_reminder(activity, process, user, minutes_before: int, send_email: bool):
    """Faaliyet başlangıç hatırlatması."""
    title = f"Faaliyet Hatırlatması: {process.name}"
    when_text = "şimdi" if int(minutes_before) == 0 else f"{int(minutes_before)} dk sonra"
    message = f"'{activity.name}' faaliyeti {when_text} başlıyor."
    link = f"/process/{process.id}/karne"
    _create(
        user_id=user.id,
        tenant_id=process.tenant_id,
        notification_type="activity_reminder",
        title=title,
        message=message,
        link=link,
    )
    if send_email:
        _send_email_async(user, title, message, process.tenant_id, "activity_reminder", link)


def notify_activity_auto_completed(activity, process, user, send_email: bool):
    """Faaliyet otomatik gerçekleşme bildirimi."""
    title = f"Faaliyet Gerçekleşti: {process.name}"
    message = f"'{activity.name}' faaliyeti bitiş zamanına göre otomatik gerçekleşti olarak işaretlendi."
    link = f"/process/{process.id}/karne"
    _create(
        user_id=user.id,
        tenant_id=process.tenant_id,
        notification_type="activity_auto_completed",
        title=title,
        message=message,
        link=link,
    )
    if send_email:
        _send_email_async(user, title, message, process.tenant_id, "activity_auto_completed", link)


def _project_channels(project) -> dict:
    """Proje bildirim ayarlarından kanal bayrakları (Micro proje formu ile uyumlu)."""
    if project is None or not hasattr(project, "get_notification_settings"):
        return {"in_app": True, "email": True}
    settings = project.get_notification_settings() or {}
    ch = settings.get("channels") or {}
    return {
        "in_app": bool(ch.get("in_app", True)),
        "email": bool(ch.get("email", True)),
    }


def notify_task_assignment(
    task_name,
    assigned_user,
    tenant_id,
    actor=None,
    task_link=None,
    project=None,
    channels_override: dict | None = None,
):
    """
    Bir projede görev atandığında ilgili kullanıcıya bildirim gönderir.
    Hem `notifications` (Micro bildirim merkezi) hem e-posta (SMTP / tenant tercihleri).
    """
    ch = channels_override if channels_override is not None else _project_channels(project)
    actor_name = (actor.first_name or actor.email) if actor else "Sistem"
    title = "Size Görev Atandı"
    message = f"'{task_name}' görevi size atandı. İşlemi yapan: {actor_name}"

    if ch.get("in_app", True):
        _create(
            user_id=assigned_user.id,
            tenant_id=tenant_id,
            notification_type="task_assigned",
            title=title,
            message=message,
            link=task_link,
            related_user_id=actor.id if actor else None,
        )
    if ch.get("email", True):
        _send_email_async(assigned_user, title, message, tenant_id, "task_assigned", task_link)


def notify_project_task_status_change(project, task, old_status: str, new_status: str, actor):
    """
    Micro proje görevinde durum değişince: proje yöneticisi ve görevlendirmeye (atayan hariç)
    uygulama içi + e-posta. Proje ayarları `notify_manager` ve `channels` ile uyumludur.
    """
    if not project or not task or not actor:
        return
    tid = project.kurum_id
    ch = _project_channels(project)
    settings = project.get_notification_settings() if hasattr(project, "get_notification_settings") else {}
    notify_manager = bool(settings.get("notify_manager", True))
    link = f"/project/{project.id}/task/{task.id}"

    def _actor_display(u):
        if not u:
            return "Sistem"
        parts = [getattr(u, "first_name", None) or "", getattr(u, "last_name", None) or ""]
        name = " ".join(p for p in parts if p).strip()
        return name or (getattr(u, "email", None) or "Kullanıcı")

    actor_name = _actor_display(actor)
    from app.models.core import User

    recipients: list = []

    if notify_manager:
        leader_ids = []
        try:
            leader_ids = list(project.leader_user_ids())
        except Exception:
            leader_ids = [project.manager_id] if project.manager_id else []
        notified = {int(actor.id)}
        for lid in leader_ids:
            if not lid or int(lid) in notified:
                continue
            mgr = User.query.get(lid)
            if mgr:
                title = "Görev Durumu Değişti"
                message = (
                    f'{actor_name} "{task.title}" görevinin durumunu '
                    f'"{old_status}" → "{new_status}" olarak değiştirdi.'
                )
                recipients.append((mgr, title, message))
                notified.add(int(lid))

    aid = getattr(task, "assignee_id", None) or getattr(task, "assigned_to_id", None)
    if aid and int(aid) != int(actor.id):
        assignee = User.query.get(aid)
        if assignee:
            title = "Görev Durumunuz Değişti"
            message = (
                f'"{task.title}" görevinin durumu "{old_status}" → "{new_status}" olarak değiştirildi.'
            )
            recipients.append((assignee, title, message))

    for user, title, message in recipients:
        if ch.get("in_app", True):
            _create(
                user_id=user.id,
                tenant_id=tid,
                notification_type="task_status_changed",
                title=title,
                message=message,
                link=link,
                related_user_id=actor.id,
            )
        if ch.get("email", True):
            _send_email_async(user, title, message, tid, "task_status_changed", link)


def _actor_display_name(actor) -> str:
    if not actor:
        return "Sistem"
    fn = (getattr(actor, "first_name", None) or "").strip()
    ln = (getattr(actor, "last_name", None) or "").strip()
    name = f"{fn} {ln}".strip()
    return name or (getattr(actor, "email", None) or "Kullanıcı")


def notify_project_leaders_added(project, added_leader_ids: list[int], actor, tenant_id: int) -> None:
    """Yeni atanan proje liderlerine uygulama içi + e-posta (proje kanal ayarlarına göre)."""
    if not project or not added_leader_ids:
        return
    ch = _project_channels(project)
    actor_name = _actor_display_name(actor)
    link = f"/project/{project.id}"
    aid = getattr(actor, "id", None) if actor else None
    from app.models.core import User as CoreUser

    for uid in added_leader_ids:
        if aid is not None and int(uid) == int(aid):
            continue
        u = CoreUser.query.get(uid)
        if not u or not getattr(u, "is_active", True):
            continue
        title = "Proje lideri olarak atandınız"
        message = f'{actor_name} sizi "{project.name}" projesinde proje lideri olarak atadı.'
        if ch.get("in_app", True):
            _create(
                user_id=uid,
                tenant_id=tenant_id,
                notification_type="project_leader_assigned",
                title=title,
                message=message,
                link=link,
                related_user_id=aid,
            )
        if ch.get("email", True):
            _send_email_async(u, title, message, tenant_id, "project_leader_assigned", link)


def notify_project_members_added(project, added_member_ids: list[int], actor, tenant_id: int) -> None:
    """Yeni atanan proje üyelerine uygulama içi + e-posta (proje kanal ayarlarına göre)."""
    if not project or not added_member_ids:
        return
    ch = _project_channels(project)
    actor_name = _actor_display_name(actor)
    link = f"/project/{project.id}"
    aid = getattr(actor, "id", None) if actor else None
    from app.models.core import User as CoreUser

    for uid in added_member_ids:
        if aid is not None and int(uid) == int(aid):
            continue
        u = CoreUser.query.get(uid)
        if not u or not getattr(u, "is_active", True):
            continue
        title = "Projeye üye olarak atandınız"
        message = f'{actor_name} sizi "{project.name}" projesinin ekibine üye olarak ekledi.'
        if ch.get("in_app", True):
            _create(
                user_id=uid,
                tenant_id=tenant_id,
                notification_type="project_member_assigned",
                title=title,
                message=message,
                link=link,
                related_user_id=aid,
            )
        if ch.get("email", True):
            _send_email_async(u, title, message, tenant_id, "project_member_assigned", link)
