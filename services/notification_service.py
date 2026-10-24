# -*- coding: utf-8 -*-
"""
Bildirim Servisleri
Görev ve proje bildirimleri için servis fonksiyonları
"""
from datetime import datetime, timedelta, date
from flask import current_app, url_for
from app.models.legacy_bridge import db, Task, Project
from app.models.core import Notification as _CoreNotification, User
from app.utils.tr_time import now_tr
from utils.task_status import COMPLETED_STATUSES, normalize_task_status
import logging

logger = logging.getLogger(__name__)


def Notification(user_id, tip, baslik, mesaj, link=None, project_id=None, task_id=None,
                 ilgili_user_id=None):
    """Legacy imza -> modern `notifications` modeli (D-005). tenant_id kullanicidan turetilir."""
    tenant_id = None
    try:
        u = db.session.get(User, user_id)
        tenant_id = u.tenant_id if u else None
    except Exception as e:
        logger.warning("[notification] tenant cozumlenemedi u=%s: %s", user_id, e)
    return _CoreNotification(
        user_id=user_id,
        tenant_id=tenant_id,
        notification_type=tip,
        title=baslik,
        message=mesaj,
        link=link,
        is_read=False,
        related_user_id=ilgili_user_id,
    )


def _persist(notification) -> bool:
    """Bildirimi SAVEPOINT icinde ekler; hata olursa yalniz onu geri alir (session.rollback YOK)."""
    try:
        with db.session.begin_nested():
            db.session.add(notification)
        return True
    except Exception as e:
        logger.error("[notification] bildirim olusturulamadi: %s", e)
        return False


def _commit() -> bool:
    try:
        db.session.commit()
        return True
    except Exception as e:
        logger.error("[notification] commit hatasi: %s", e)
        return False


def _exists_today(user_id, tip, link) -> bool:
    """Ayni kullanici+tur+link icin bugun (TR) bildirim var mi."""
    start = datetime.combine(now_tr().date(), datetime.min.time())
    return db.session.query(_CoreNotification.id).filter(
        _CoreNotification.user_id == user_id,
        _CoreNotification.notification_type == tip,
        _CoreNotification.link == link,
        _CoreNotification.created_at >= start - timedelta(hours=3),
    ).first() is not None


def _project_leader_ids(project):
    """Bildirimler için tüm lider kullanıcı ID'leri."""
    if not project:
        return []
    try:
        ids = list(project.leader_user_ids())
        seen = set()
        out = []
        for i in ids:
            if i and i not in seen:
                seen.add(i)
                out.append(i)
        return out
    except Exception:
        mid = getattr(project, "manager_id", None)
        return [mid] if mid else []


def create_task_assigned_notification(task_id, assigned_user_id, assigned_by_user_id):
    """
    Görev atama bildirimi oluştur
    
    Args:
        task_id: Görev ID
        assigned_user_id: Görevin atandığı kullanıcı ID
        assigned_by_user_id: Görevi atayan kullanıcı ID
    """
    try:
        task = Task.query.get(task_id)
        assigned_by = User.query.get(assigned_by_user_id)
        
        if not task or not assigned_by:
            return None
        
        notification = Notification(
            user_id=assigned_user_id,
            tip='task_assigned',
            baslik='Yeni Görev Atandı',
            mesaj=f'{assigned_by.first_name} {assigned_by.last_name} size "{task.title}" görevini atadı.',
            link=f'/projeler/{task.project_id}/gorevler/{task_id}',
            project_id=task.project_id,
            task_id=task_id,
            ilgili_user_id=assigned_by_user_id
        )
        _persist(notification)
        _commit()
        
        # E-posta gönderimi için background task'a ekle
        from services.background_tasks import execute_async
        execute_async(send_task_assigned_email, assigned_user_id, task_id)
        
        return notification
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Görev atama bildirimi hatası: {e}')
        return None


def create_task_deadline_reminder_notification(task_id):
    """
    Görev deadline yaklaşma uyarısı oluştur
    
    Args:
        task_id: Görev ID
    """
    try:
        task = Task.query.get(task_id)
        if not task or not task.assigned_to_id or not task.due_date:
            return None
        
        # Varsayılan: deadline'a 1 gün kala
        if task.due_date == now_tr().date() + timedelta(days=1):
            assigned_user = User.query.get(task.assigned_to_id)
            if not assigned_user:
                return None

            # Bugün zaten bildirim üretildiyse tekrar üretme
            existing_notification = _exists_today(task.assigned_to_id, 'task_deadline_reminder', f'/projeler/{task.project_id}/gorevler/{task.id}')
            if existing_notification:
                return None
            
            notification = Notification(
                user_id=task.assigned_to_id,
                tip='task_deadline_reminder',
                baslik='Görev Deadline Uyarısı',
                mesaj=f'"{task.title}" görevinin deadline\'ı yarın ({task.due_date.strftime("%d.%m.%Y")}).',
                link=f'/projeler/{task.project_id}/gorevler/{task_id}',
                project_id=task.project_id,
                task_id=task_id
            )
            _persist(notification)
            _commit()
            
            return notification
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Deadline uyarısı hatası: {e}')
        return None


def create_task_reminder_notification(task_id, user_id):
    """
    Görev hatırlatma bildirimi oluştur (kullanıcının belirlediği tarih/saatte)
    
    Args:
        task_id: Görev ID
        user_id: Hatırlatma yapılacak kullanıcı ID
    """
    try:
        task = Task.query.get(task_id)
        if not task:
            return None
        
        notification = Notification(
            user_id=user_id,
            tip='task_reminder',
            baslik='Görev Hatırlatması',
            mesaj=f'Hatırlatma: "{task.title}" görevi hakkında belirlediğiniz hatırlatma zamanı geldi.',
            link=f'/projeler/{task.project_id}/gorevler/{task_id}',
            project_id=task.project_id,
            task_id=task_id
        )
        _persist(notification)
        _commit()
        
        # E-posta gönderimi için background task'a ekle (varsa)
        try:
            from services.background_tasks import execute_async
            execute_async(send_task_reminder_email, user_id, task_id)
        except Exception as e:  # S10: ciplak except yasak
            # Background task servisi yoksa bildirim yine olusur — ama iz kalsin.
            try:
                from flask import current_app
                current_app.logger.warning('[notification] e-posta kuyruga alinamadi: %s', e)
            except Exception as err:
                logger.error(f"create_task_reminder_notification failed: {err}")
        
        return notification
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Görev hatırlatma bildirimi hatası: {e}')
        return None


def create_task_comment_notification(comment_id, task_id, commenter_user_id):
    """
    Görev yorum bildirimi oluştur (yorum yapan hariç görev sahibine)
    
    Args:
        comment_id: Yorum ID
        task_id: Görev ID
        commenter_user_id: Yorum yapan kullanıcı ID
    """
    try:
        task = Task.query.get(task_id)
        if not task:
            return None
        
        # Görev sahibine bildirim gönder (yorum yapan hariç)
        if task.assigned_to_id and task.assigned_to_id != commenter_user_id:
            commenter = User.query.get(commenter_user_id)
            if commenter:
                notification = Notification(
                    user_id=task.assigned_to_id,
                    tip='task_comment',
                    baslik='Görevinize Yorum Yapıldı',
                    mesaj=f'{commenter.first_name} {commenter.last_name} "{task.title}" görevinize yorum yaptı.',
                    link=f'/projeler/{task.project_id}/gorevler/{task_id}',
                    project_id=task.project_id,
                    task_id=task_id,
                    ilgili_user_id=commenter_user_id
                )
                _persist(notification)
                _commit()
                return notification
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Yorum bildirimi hatası: {e}')
        return None


def create_task_status_change_notification(task_id, old_status, new_status, changed_by_user_id):
    """
    Görev durum değişikliği bildirimi oluştur
    
    Args:
        task_id: Görev ID
        old_status: Eski durum
        new_status: Yeni durum
        changed_by_user_id: Değişikliği yapan kullanıcı ID
    """
    try:
        task = Task.query.get(task_id)
        if not task:
            return None
        
        # Proje üyelerine bildirim gönder
        project = Project.query.get(task.project_id)
        if not project:
            return None
        
        changed_by = User.query.get(changed_by_user_id)
        if not changed_by:
            return None
        
        notifications = []
        
        # Proje liderlerine (çoklu)
        for lid in _project_leader_ids(project):
            if not lid or lid == changed_by_user_id:
                continue
            notification = Notification(
                user_id=lid,
                tip='task_status_changed',
                baslik='Görev Durumu Değişti',
                mesaj=f'{changed_by.first_name} {changed_by.last_name} "{task.title}" görevinin durumunu "{old_status}" → "{new_status}" olarak değiştirdi.',
                link=f'/projeler/{task.project_id}/gorevler/{task_id}',
                project_id=task.project_id,
                task_id=task_id,
                ilgili_user_id=changed_by_user_id
            )
            _persist(notification)
            notifications.append(notification)
        
        # Görev sahibine (değişikliği yapan hariç)
        if task.assigned_to_id and task.assigned_to_id != changed_by_user_id:
            notification = Notification(
                user_id=task.assigned_to_id,
                tip='task_status_changed',
                baslik='Görev Durumunuz Değişti',
                mesaj=f'"{task.title}" görevinin durumu "{old_status}" → "{new_status}" olarak değiştirildi.',
                link=f'/projeler/{task.project_id}/gorevler/{task_id}',
                project_id=task.project_id,
                task_id=task_id,
                ilgili_user_id=changed_by_user_id
            )
            _persist(notification)
            notifications.append(notification)
        
        if notifications:
            _commit()
        
        return notifications
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Durum değişikliği bildirimi hatası: {e}')
        return None


def check_and_send_deadline_reminders():
    """
    Tüm aktif görevler için deadline uyarılarını kontrol et ve gönder
    Background task olarak çalıştırılmalı
    """
    try:
        today = now_tr().date()

        # Proje bazlı reminder_days desteği için yaklaşan görevleri geniş aralıkta al
        # (Varsayılan max 7 gün)
        max_window_days = 7
        try:
            # Bazı projelerde daha büyük reminder_days olabilir; projelerden max'ı bul
            projects = Project.query.all()
            for p in projects:
                settings = p.get_notification_settings() if hasattr(p, 'get_notification_settings') else {}
                days = settings.get('reminder_days') if isinstance(settings, dict) else None
                if isinstance(days, list) and days:
                    candidate = max([int(d) for d in days if isinstance(d, int) or str(d).isdigit()] or [7])
                    if candidate > max_window_days:
                        max_window_days = candidate
        except Exception:
            max_window_days = 7

        window_end = today + timedelta(days=max_window_days)

        # Deadline'ı yaklaşan (window içinde) ve tamamlanmamış görevler
        tasks = Task.query.filter(
            Task.due_date.isnot(None),
            Task.due_date >= today,
            Task.due_date <= window_end,
            Task.status.notin_(COMPLETED_STATUSES),
            Task.assigned_to_id.isnot(None)
        ).all()
        
        # Tüm projeleri batch'le çek (N+1 önlemi)
        _pids = list({t.project_id for t in tasks if t.project_id})
        _projects = {p.id: p for p in Project.query.filter(Project.id.in_(_pids)).all()} if _pids else {}

        # Mevcut bildirimleri tek sorguda batch'le (deduplication icin) — anahtar: (user_id, link)
        _existing_keys = set()
        if tasks:
            _start = datetime.combine(now_tr().date(), datetime.min.time()) - timedelta(hours=3)
            for uid, lnk in db.session.query(_CoreNotification.user_id, _CoreNotification.link).filter(
                _CoreNotification.notification_type == 'task_deadline_reminder',
                _CoreNotification.created_at >= _start,
            ).all():
                _existing_keys.add((uid, lnk))

        notifications_created = 0
        for task in tasks:
            reminder_days = [1]
            try:
                project = _projects.get(task.project_id)
                settings = project.get_notification_settings() if project else {}
                if isinstance(settings, dict) and isinstance(settings.get('reminder_days'), list):
                    reminder_days = [int(d) for d in settings.get('reminder_days') if isinstance(d, int) or str(d).isdigit()]
                    reminder_days = [d for d in reminder_days if d >= 0] or [1]
            except Exception:
                reminder_days = [1]

            days_until_due = (task.due_date - today).days
            if days_until_due not in reminder_days:
                continue

            # Bugün zaten bildirim üretildiyse tekrar üretme (batch lookup)
            _lk = f'/projeler/{task.project_id}/gorevler/{task.id}'
            if (task.assigned_to_id, _lk) in _existing_keys:
                continue
            _existing_keys.add((task.assigned_to_id, _lk))

            # Dinamik mesaj
            try:
                notification = Notification(
                    user_id=task.assigned_to_id,
                    tip='task_deadline_reminder',
                    baslik='Görev Deadline Uyarısı',
                    mesaj=f'"{task.title}" görevinin deadline\'ına {days_until_due} gün kaldı ({task.due_date.strftime("%d.%m.%Y")}).',
                    link=f'/projeler/{task.project_id}/gorevler/{task.id}',
                    project_id=task.project_id,
                    task_id=task.id
                )
                _persist(notification)
                _commit()
                notifications_created += 1
            except Exception as e:
                if current_app:
                    current_app.logger.error(f'Deadline uyarısı oluşturma hatası: {e}')
        
        if current_app:
            current_app.logger.info(f'{notifications_created} deadline uyarısı oluşturuldu')
        
        return notifications_created
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Deadline kontrolü hatası: {e}')
        return 0


def send_task_assigned_email(user_id, task_id):
    """
    Görev atama e-postası gönder (background task)
    """
    try:
        # E-posta gönderim mantığı buraya eklenecek
        # Şu an sadece log
        if current_app:
            current_app.logger.info(f'Görev atama e-postası gönderilecek: User {user_id}, Task {task_id}')
    except Exception as e:
        if current_app:
            current_app.logger.error(f'E-posta gönderme hatası: {e}')


def send_task_reminder_email(user_id, task_id):
    """
    Görev hatırlatma e-postası gönder (background task)
    """
    try:
        # E-posta gönderim mantığı buraya eklenecek
        # Şu an sadece log
        if current_app:
            current_app.logger.info(f'Görev hatırlatma e-postası gönderilecek: User {user_id}, Task {task_id}')
    except Exception as e:
        if current_app:
            current_app.logger.error(f'E-posta gönderme hatası: {e}')


def create_task_overdue_notification(task_id):
    """
    Geciken görev bildirimi oluştur
    
    Args:
        task_id: Görev ID
    """
    try:
        from app.models.legacy_bridge import ProjectRisk
        task = Task.query.get(task_id)
        if not task or not task.due_date:
            return None
        
        project = Project.query.get(task.project_id) if task else None
        settings = project.get_notification_settings() if project and hasattr(project, 'get_notification_settings') else {}

        # Proje bazlı gecikme bildirimi kapalıysa çık
        try:
            if isinstance(settings, dict) and settings.get('overdue_frequency') == 'off':
                return None
        except Exception as e:
            logger.warning(f"[create_task_overdue_notification] suppressed: {e}")

        notify_manager = True
        notify_observers = False
        try:
            if isinstance(settings, dict):
                notify_manager = bool(settings.get('notify_manager', True))
                notify_observers = bool(settings.get('notify_observers', False))
        except Exception as e:
            logger.warning(f"[create_task_overdue_notification] suppressed: {e}")

        # Gecikmiş görev kontrolü
        normalized_status = normalize_task_status(task.status) or task.status
        if task.due_date < now_tr().date() and normalized_status != 'Tamamlandı':
            if not project:
                return None
            
            notifications = []
            
            # Görev sahibine bildirim
            if task.assigned_to_id:
                # Bugün bildirim gönderilmiş mi kontrol et
                existing_notification = _exists_today(task.assigned_to_id, 'task_overdue', f'/projeler/{task.project_id}/gorevler/{task_id}')
                
                if not existing_notification:
                    notification = Notification(
                        user_id=task.assigned_to_id,
                        tip='task_overdue',
                        baslik='Görev Gecikti',
                        mesaj=f'"{task.title}" görevi {task.due_date.strftime("%d.%m.%Y")} tarihinde sona ermişti ve henüz tamamlanmadı.',
                        link=f'/projeler/{task.project_id}/gorevler/{task_id}',
                        project_id=task.project_id,
                        task_id=task_id
                    )
                    _persist(notification)
                    notifications.append(notification)
            
            # Proje liderlerine bildirim
            leader_ids = set(_project_leader_ids(project))
            if notify_manager:
                for lid in leader_ids:
                    if not lid or lid == task.assigned_to_id:
                        continue
                    existing_notification = _exists_today(lid, 'task_overdue', f'/projeler/{task.project_id}/gorevler/{task_id}')
                    if existing_notification:
                        continue
                    notification = Notification(
                        user_id=lid,
                        tip='task_overdue',
                        baslik='Projede Geciken Görev',
                        mesaj=f'"{task.title}" görevi {task.due_date.strftime("%d.%m.%Y")} tarihinde sona ermişti ve henüz tamamlanmadı.',
                        link=f'/projeler/{task.project_id}/gorevler/{task_id}',
                        project_id=task.project_id,
                        task_id=task_id
                    )
                    _persist(notification)
                    notifications.append(notification)

            # Gözlemcilere bildirim (opsiyonel)
            if notify_observers:
                try:
                    for observer in getattr(project, 'observers', []) or []:
                        if not observer or observer.id == task.assigned_to_id or observer.id in leader_ids:
                            continue
                        existing_notification = _exists_today(observer.id, 'task_overdue', f'/projeler/{task.project_id}/gorevler/{task_id}')
                        if existing_notification:
                            continue
                        notification = Notification(
                            user_id=observer.id,
                            tip='task_overdue',
                            baslik='Projede Geciken Görev',
                            mesaj=f'"{task.title}" görevi {task.due_date.strftime("%d.%m.%Y")} tarihinde sona ermişti ve henüz tamamlanmadı.',
                            link=f'/projeler/{task.project_id}/gorevler/{task_id}',
                            project_id=task.project_id,
                            task_id=task_id
                        )
                        _persist(notification)
                        notifications.append(notification)
                except Exception as e:
                    logger.warning(f"[create_task_overdue_notification] observer notification suppressed: {e}")
            
            if notifications:
                _commit()
            
            return notifications
        
        return None
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Gecikme bildirimi hatası: {e}')
        return None


def create_critical_risk_notification(risk_id, created_by_user_id):
    """
    Kritik risk bildirimi oluştur
    
    Args:
        risk_id: Risk ID
        created_by_user_id: Risk oluşturan kullanıcı ID
    """
    try:
        from app.models.legacy_bridge import ProjectRisk
        risk = ProjectRisk.query.get(risk_id)
        if not risk or risk.risk_score < 20:  # Sadece kritik riskler için
            return None
        
        project = Project.query.get(risk.project_id)
        if not project:
            return None
        
        notifications = []
        leader_ids = set(_project_leader_ids(project))
        
        # Proje liderlerine bildirim
        for lid in leader_ids:
            if not lid or lid == created_by_user_id:
                continue
            notification = Notification(
                user_id=lid,
                tip='critical_risk',
                baslik='Kritik Risk Tespit Edildi',
                mesaj=f'"{risk.title}" adlı kritik risk (Skor: {risk.risk_score}) "{project.name}" projesine eklendi.',
                link=f'/projeler/{risk.project_id}',
                project_id=risk.project_id,
                ilgili_user_id=created_by_user_id
            )
            _persist(notification)
            notifications.append(notification)
        
        # Proje üyelerine bildirim
        from app.models.legacy_bridge import project_members
        member_ids = db.session.query(project_members.c.user_id).filter(
            project_members.c.project_id == risk.project_id
        ).all()
        member_ids = [row[0] for row in member_ids]
        
        for member_id in member_ids:
            if member_id != created_by_user_id and member_id not in leader_ids:
                notification = Notification(
                    user_id=member_id,
                    tip='critical_risk',
                    baslik='Projede Kritik Risk',
                    mesaj=f'"{risk.title}" adlı kritik risk (Skor: {risk.risk_score}) "{project.name}" projesine eklendi.',
                    link=f'/projeler/{risk.project_id}',
                    project_id=risk.project_id,
                    ilgili_user_id=created_by_user_id
                )
                _persist(notification)
                notifications.append(notification)
        
        if notifications:
            _commit()
        
        return notifications
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Kritik risk bildirimi hatası: {e}')
        return None


def check_and_send_overdue_notifications():
    """
    Tüm gecikmiş görevler için bildirimleri kontrol et ve gönder
    Background task olarak çalıştırılmalı
    """
    try:
        today = now_tr().date()
        
        # Gecikmiş ve tamamlanmamış görevler
        overdue_tasks = Task.query.filter(
            Task.due_date < today,
            Task.status.notin_(COMPLETED_STATUSES)
        ).all()
        
        notifications_created = 0
        for task in overdue_tasks:
            result = create_task_overdue_notification(task.id)
            if result:
                notifications_created += len(result)
        
        if current_app:
            current_app.logger.info(f'{notifications_created} gecikme bildirimi oluşturuldu')
        
        return notifications_created
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Gecikme kontrolü hatası: {e}')
        return 0


def create_feedback_status_notification(feedback_id, old_status, new_status, updated_by_user_id):
    """
    Geri bildirim durum değişikliği bildirimi oluştur
    
    Args:
        feedback_id: Geri Bildirim ID
        old_status: Eski durum
        new_status: Yeni durum
        updated_by_user_id: Durumu güncelleyen kullanıcı ID
    """
    try:
        from app.models.legacy_bridge import Feedback
        feedback = Feedback.query.get(feedback_id)
        if not feedback:
            return None
        
        updated_by = User.query.get(updated_by_user_id)
        if not updated_by:
            return None
        
        # Durum mesajları
        status_messages = {
            'Bekliyor': 'Geri bildiriminiz alındı ve incelenmeye alındı.',
            'İnceleniyor': 'Geri bildiriminiz inceleniyor.',
            'Çözüldü': 'Geri bildiriminiz çözüldü. Teşekkür ederiz!',
            'Reddedildi': 'Geri bildiriminiz değerlendirildi ancak şu an için uygulanamayacak.'
        }
        
        # Mesaj oluştur
        if new_status in status_messages:
            mesaj = status_messages[new_status]
        else:
            mesaj = f'Geri bildiriminizin durumu "{old_status}" → "{new_status}" olarak güncellendi.'
        
        # Admin notu varsa ekle
        if feedback.admin_note:
            mesaj += f'\n\nAdmin Notu: {feedback.admin_note}'
        
        # Kullanıcıya bildirim gönder
        notification = Notification(
            user_id=feedback.user_id,
            tip='feedback_status_changed',
            baslik='Geri Bildirim Durumu Güncellendi',
            mesaj=mesaj,
            link=f'/admin/feedback',
            ilgili_user_id=updated_by_user_id
        )
        _persist(notification)
        _commit()
        
        if current_app:
            current_app.logger.info(f'Geri bildirim durum bildirimi oluşturuldu: Feedback ID {feedback_id}, Durum: {old_status} → {new_status}')
        
        return notification
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Geri bildirim durum bildirimi hatası: {e}', exc_info=True)
        return None


def check_pg_performance_deviation(pg_veri_id):
    """
    PG verisi kaydedildiğinde performans sapması kontrolü yapar
    Eğer gerçekleşen değer hedefin %10 ve daha fazla altındaysa bildirim oluşturur
    
    Args:
        pg_veri_id: PerformansGostergeVeri ID
    """
    try:
        from app.models.legacy_bridge import PerformansGostergeVeri, BireyselPerformansGostergesi
        
        pg_veri = PerformansGostergeVeri.query.get(pg_veri_id)
        if not pg_veri:
            return None
        
        # Gerçekleşen ve hedef değerleri kontrol et
        if not pg_veri.gerceklesen_deger or not pg_veri.hedef_deger:
            return None
        
        try:
            gerceklesen = float(pg_veri.gerceklesen_deger)
            hedef = float(pg_veri.hedef_deger)
        except (ValueError, TypeError):
            return None
        
        # Hedef 0 veya negatifse oran anlamsız (score_engine `achievement` ile aynı kural)
        if hedef <= 0:
            return None
        
        # Sapma yüzdesini hesapla
        sapma_yuzdesi = ((gerceklesen - hedef) / hedef) * 100
        
        # Eğer gerçekleşen değer hedefin %10 ve daha fazla altındaysa bildirim oluştur
        if sapma_yuzdesi <= -10:
            bireysel_pg = BireyselPerformansGostergesi.query.get(pg_veri.bireysel_pg_id)
            if not bireysel_pg:
                return None
            
            # Kullanıcıya bildirim gönder
            notification = Notification(
                user_id=pg_veri.user_id,
                tip='pg_performance_deviation',
                baslik='Kritik Performans Sapması',
                mesaj=f'"{bireysel_pg.ad}" performans göstergesinde kritik sapma tespit edildi. Gerçekleşen: {gerceklesen}, Hedef: {hedef} (Sapma: %{abs(sapma_yuzdesi):.1f})',
                link=f'/surec/karne?pg_id={pg_veri.bireysel_pg_id}',
                ilgili_user_id=pg_veri.user_id
            )
            _persist(notification)
            
            # Süreç liderine de bildirim gönder (eğer süreçten geliyorsa)
            if bireysel_pg.kaynak == 'Süreç' and bireysel_pg.kaynak_surec_id:
                from app.models.legacy_bridge import surec_liderleri
                lider_ids = db.session.query(surec_liderleri.c.user_id).filter(
                    surec_liderleri.c.surec_id == bireysel_pg.kaynak_surec_id
                ).all()
                lider_ids = [row[0] for row in lider_ids]
                
                for lider_id in lider_ids:
                    if lider_id != pg_veri.user_id:
                        notification = Notification(
                            user_id=lider_id,
                            tip='pg_performance_deviation',
                            baslik='Süreçte Kritik Performans Sapması',
                            mesaj=f'"{bireysel_pg.ad}" performans göstergesinde kritik sapma tespit edildi. Kullanıcı: {User.query.get(pg_veri.user_id).first_name if User.query.get(pg_veri.user_id) else "Bilinmiyor"}, Gerçekleşen: {gerceklesen}, Hedef: {hedef} (Sapma: %{abs(sapma_yuzdesi):.1f})',
                            link=f'/surec/karne?pg_id={pg_veri.bireysel_pg_id}',
                            ilgili_user_id=pg_veri.user_id
                        )
                        _persist(notification)
            
            _commit()
            
            # Webhook tetikle (V2.0.0)
            try:
                from services.webhook_service import trigger_pg_deviation_webhook
                from app.models.legacy_bridge import User
                user = User.query.get(pg_veri.user_id)
                if user and user.tenant_id:
                    trigger_pg_deviation_webhook(
                        user.tenant_id,
                        pg_veri_id,
                        abs(sapma_yuzdesi)
                    )
            except Exception as webhook_error:
                if current_app:
                    current_app.logger.warning(f'Webhook tetikleme hatası: {webhook_error}')
            
            if current_app:
                current_app.logger.info(f'PG performans sapması bildirimi oluşturuldu: PG Veri ID {pg_veri_id}, Sapma: %{abs(sapma_yuzdesi):.1f}')
            
            return notification
        else:
            return None
        
    except Exception as e:
        if current_app:
            current_app.logger.error(f'PG performans sapması kontrolü hatası: {e}')
        return None



























