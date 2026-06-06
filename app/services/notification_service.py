"""
Notification Service
Sprint 7-9: Real-Time ve Bildirimler
Akıllı bildirim sistemi
"""

from extensions import db
from app.models.core import User
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

class NotificationService:
    """Bildirim yönetim servisi"""
    
    # Bildirim tipleri
    PERFORMANCE_ALERT = 'performance_alert'
    TASK_REMINDER = 'task_reminder'
    COLLABORATION = 'collaboration'
    ACHIEVEMENT = 'achievement'
    SYSTEM = 'system'
    
    # Bildirim öncelikleri
    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'
    PRIORITY_URGENT = 'urgent'
    
    @staticmethod
    def create_notification(
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        priority: str = PRIORITY_MEDIUM,
        action_url: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Bildirim oluştur
        
        Args:
            user_id: Kullanıcı ID
            notification_type: Bildirim tipi
            title: Başlık
            message: Mesaj
            priority: Öncelik (low, medium, high, urgent)
            action_url: Aksiyon URL'i
            metadata: Ek bilgiler
        """
        from app.models.notification import Notification
        from app.utils.db_sequence import add_and_commit_with_retry

        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            priority=priority,
            action_url=action_url,
            metadata=metadata,
            is_read=False
        )

        add_and_commit_with_retry(notification, "notifications_ext")
        
        # Real-time push (WebSocket)
        NotificationService._push_realtime(user_id, notification)
        
        return notification

    
    @staticmethod
    def _push_realtime(user_id: int, notification):
        """Real-time bildirim gönder (WebSocket)"""
        try:
            from app.extensions import socketio
            
            socketio.emit(
                'new_notification',
                {
                    'id': notification.id,
                    'type': notification.type,
                    'title': notification.title,
                    'message': notification.message,
                    'priority': notification.priority,
                    'action_url': notification.action_url,
                    'created_at': notification.created_at.isoformat()
                },
                room=f'user_{user_id}'
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Real-time push error: {e}")
    
    @staticmethod
    def bulk_create(
        user_ids: List[int],
        notification_type: str,
        title: str,
        message: str,
        priority: str = "medium",
        action_url: Optional[str] = None,
        tenant_id: Optional[int] = None,
    ) -> int:
        """Birden fazla kullanıcıya aynı bildirimi toplu oluşturur.

        For döngüsü yerine tek sorguda INSERT — N+1 önlemi.
        Döner: oluşturulan bildirim sayısı.
        """
        from app.models.notification import Notification
        from app.utils.db_sequence import commit_with_retry

        if not user_ids:
            return 0

        now = datetime.now(timezone.utc)

        def _stage():
            db.session.bulk_save_objects([
                Notification(
                    user_id=uid,
                    tenant_id=tenant_id,
                    type=notification_type,
                    title=title,
                    message=message,
                    priority=priority,
                    action_url=action_url,
                    is_read=False,
                    created_at=now,
                )
                for uid in user_ids
            ])

        _stage()
        # PK sequence desync (import/restore sonrası) → hizala + tekrar dene
        commit_with_retry("notifications_ext", restage=_stage)
        return len(user_ids)

    @staticmethod
    def send_performance_alert(user_id: int, kpi_name: str, actual: float, target: float, deviation: float):
        """Performans uyarısı gönder"""
        title = f"Performans Uyarısı: {kpi_name}"
        message = f"{kpi_name} hedefin %{abs(deviation):.1f} {'üstünde' if deviation > 0 else 'altında'}. "
        message += f"Gerçekleşen: {actual}, Hedef: {target}"
        
        priority = NotificationService.PRIORITY_HIGH if abs(deviation) > 20 else NotificationService.PRIORITY_MEDIUM
        
        return NotificationService.create_notification(
            user_id=user_id,
            notification_type=NotificationService.PERFORMANCE_ALERT,
            title=title,
            message=message,
            priority=priority,
            metadata={'kpi_name': kpi_name, 'actual': actual, 'target': target, 'deviation': deviation}
        )
    
    @staticmethod
    def send_task_reminder(user_id: int, task_description: str, due_date: datetime, days_remaining: int):
        """Görev hatırlatıcısı gönder"""
        title = "Görev Hatırlatıcısı"
        
        if days_remaining == 0:
            message = f"Bugün: {task_description}"
            priority = NotificationService.PRIORITY_URGENT
        elif days_remaining == 1:
            message = f"Yarın: {task_description}"
            priority = NotificationService.PRIORITY_HIGH
        else:
            message = f"{days_remaining} gün içinde: {task_description}"
            priority = NotificationService.PRIORITY_MEDIUM
        
        return NotificationService.create_notification(
            user_id=user_id,
            notification_type=NotificationService.TASK_REMINDER,
            title=title,
            message=message,
            priority=priority,
            metadata={'task': task_description, 'due_date': due_date.isoformat(), 'days_remaining': days_remaining}
        )
    
    @staticmethod
    def send_collaboration_notification(user_id: int, actor_name: str, action: str, resource: str):
        """İşbirliği bildirimi gönder"""
        title = "İşbirliği Bildirimi"
        message = f"{actor_name} {action}: {resource}"
        
        return NotificationService.create_notification(
            user_id=user_id,
            notification_type=NotificationService.COLLABORATION,
            title=title,
            message=message,
            priority=NotificationService.PRIORITY_LOW,
            metadata={'actor': actor_name, 'action': action, 'resource': resource}
        )
    
    @staticmethod
    def send_achievement_notification(user_id: int, achievement: str, description: str):
        """Başarı bildirimi gönder"""
        title = f"🎉 Tebrikler! {achievement}"
        message = description
        
        return NotificationService.create_notification(
            user_id=user_id,
            notification_type=NotificationService.ACHIEVEMENT,
            title=title,
            message=message,
            priority=NotificationService.PRIORITY_LOW,
            metadata={'achievement': achievement}
        )
    
    @staticmethod
    def get_user_notifications(user_id: int, unread_only: bool = False, limit: int = 50):
        """Kullanıcı bildirimlerini getir"""
        from app.models.notification import Notification
        
        query = Notification.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        return query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def mark_as_read(notification_id: int, user_id: int = None):
        """Bildirimi okundu olarak işaretle — user_id verilirse sahiplik doğrulanır."""
        from app.models.notification import Notification

        q = Notification.query.filter_by(id=notification_id)
        if user_id is not None:
            q = q.filter_by(user_id=user_id)
        notification = q.first()
        if notification:
            notification.is_read = True
            notification.read_at = datetime.now(timezone.utc)
            db.session.commit()
    
    @staticmethod
    def mark_all_as_read(user_id: int):
        """Tüm bildirimleri okundu olarak işaretle"""
        from app.models.notification import Notification
        
        Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({
            'is_read': True,
            'read_at': datetime.now(timezone.utc)
        })
        db.session.commit()
    
    @staticmethod
    def delete_notification(notification_id: int):
        """Bildirimi sil"""
        from app.models.notification import Notification
        
        notification = Notification.query.get(notification_id)
        if notification:
            db.session.delete(notification)
            db.session.commit()
    
    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """Okunmamış bildirim sayısı"""
        from app.models.notification import Notification
        
        return Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
