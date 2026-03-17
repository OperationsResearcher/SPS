"""
Push Notification Service
Handles web push notifications using pywebpush
"""

from pywebpush import webpush, WebPushException
from app.extensions import db
from app.models.notification import PushSubscription
import json
import logging

logger = logging.getLogger(__name__)


class PushNotificationService:
    """Service for sending web push notifications"""
    
    def __init__(self, vapid_private_key, vapid_public_key, vapid_claims):
        self.vapid_private_key = vapid_private_key
        self.vapid_public_key = vapid_public_key
        self.vapid_claims = vapid_claims
    
    def subscribe(self, user_id, subscription_info):
        """
        Save push subscription for a user
        
        Args:
            user_id: User ID
            subscription_info: Subscription object from browser
        
        Returns:
            PushSubscription object
        """
        try:
            # Check if subscription already exists
            existing = PushSubscription.query.filter_by(
                user_id=user_id,
                endpoint=subscription_info['endpoint']
            ).first()
            
            if existing:
                # Update existing subscription
                existing.p256dh = subscription_info['keys']['p256dh']
                existing.auth = subscription_info['keys']['auth']
                existing.is_active = True
            else:
                # Create new subscription
                subscription = PushSubscription(
                    user_id=user_id,
                    endpoint=subscription_info['endpoint'],
                    p256dh=subscription_info['keys']['p256dh'],
                    auth=subscription_info['keys']['auth']
                )
                db.session.add(subscription)
            
            db.session.commit()
            logger.info(f"Push subscription saved for user {user_id}")

            
            return existing if existing else subscription
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to save push subscription: {str(e)}")
            raise
    
    def unsubscribe(self, user_id, endpoint):
        """
        Remove push subscription
        
        Args:
            user_id: User ID
            endpoint: Subscription endpoint
        """
        try:
            subscription = PushSubscription.query.filter_by(
                user_id=user_id,
                endpoint=endpoint
            ).first()
            
            if subscription:
                subscription.is_active = False
                db.session.commit()
                logger.info(f"Push subscription removed for user {user_id}")
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to remove push subscription: {str(e)}")
            raise
    
    def send_notification(self, user_id, title, body, url=None, icon=None):
        """
        Send push notification to user
        
        Args:
            user_id: User ID
            title: Notification title
            body: Notification body
            url: URL to open on click
            icon: Icon URL
        
        Returns:
            Number of successful sends
        """
        subscriptions = PushSubscription.query.filter_by(
            user_id=user_id,
            is_active=True
        ).all()
        
        if not subscriptions:
            logger.warning(f"No active subscriptions for user {user_id}")
            return 0
        
        payload = {
            'title': title,
            'body': body,
            'url': url or '/',
            'icon': icon or '/static/img/icon-192.png'
        }
        
        success_count = 0
        
        for subscription in subscriptions:
            try:
                webpush(
                    subscription_info={
                        'endpoint': subscription.endpoint,
                        'keys': {
                            'p256dh': subscription.p256dh,
                            'auth': subscription.auth
                        }
                    },
                    data=json.dumps(payload),
                    vapid_private_key=self.vapid_private_key,
                    vapid_claims=self.vapid_claims
                )
                success_count += 1
                logger.info(f"Push notification sent to user {user_id}")
                
            except WebPushException as e:
                logger.error(f"Push notification failed: {str(e)}")
                
                # If subscription is invalid, deactivate it
                if e.response and e.response.status_code in [404, 410]:
                    subscription.is_active = False
                    db.session.commit()
        
        return success_count
    
    def send_bulk_notification(self, user_ids, title, body, url=None, icon=None):
        """
        Send push notification to multiple users
        
        Args:
            user_ids: List of user IDs
            title: Notification title
            body: Notification body
            url: URL to open on click
            icon: Icon URL
        
        Returns:
            Total number of successful sends
        """
        total_success = 0
        
        for user_id in user_ids:
            count = self.send_notification(user_id, title, body, url, icon)
            total_success += count
        
        return total_success
