"""
Push Notification API Routes
Sprint 19-21: Mobile & PWA
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.services.push_notification_service import PushNotificationService
import os

push_bp = Blueprint('push_api', __name__, url_prefix='/api/push')


def get_push_service():
    """Get push notification service instance"""
    return PushNotificationService(
        vapid_private_key=os.getenv('VAPID_PRIVATE_KEY'),
        vapid_public_key=os.getenv('VAPID_PUBLIC_KEY'),
        vapid_claims={
            'sub': f"mailto:{os.getenv('VAPID_CLAIM_EMAIL', 'admin@kokpitim.com')}"
        }
    )


@push_bp.route('/vapid-key', methods=['GET'])
@login_required
def get_vapid_key():
    """Get VAPID public key for push subscription"""
    public_key = os.getenv('VAPID_PUBLIC_KEY')
    
    if not public_key:
        return jsonify({'error': 'VAPID key not configured'}), 500
    
    return jsonify({'public_key': public_key})


@push_bp.route('/subscribe', methods=['POST'])
@login_required
def subscribe():
    """Subscribe to push notifications"""
    try:
        subscription_info = request.json
        
        if not subscription_info or 'endpoint' not in subscription_info:
            return jsonify({'error': 'Invalid subscription data'}), 400
        
        push_service = get_push_service()
        subscription = push_service.subscribe(current_user.id, subscription_info)
        
        return jsonify({
            'success': True,
            'message': 'Push bildirimleri aktif edildi'
        })
    
    except Exception as e:
        current_app.logger.error(f"Push subscription failed: {str(e)}")
        return jsonify({'error': 'Subscription failed'}), 500



@push_bp.route('/unsubscribe', methods=['POST'])
@login_required
def unsubscribe():
    """Unsubscribe from push notifications"""
    try:
        subscription_info = request.json
        
        if not subscription_info or 'endpoint' not in subscription_info:
            return jsonify({'error': 'Invalid subscription data'}), 400
        
        push_service = get_push_service()
        push_service.unsubscribe(current_user.id, subscription_info['endpoint'])
        
        return jsonify({
            'success': True,
            'message': 'Push bildirimleri devre dışı bırakıldı'
        })
    
    except Exception as e:
        current_app.logger.error(f"Push unsubscribe failed: {str(e)}")
        return jsonify({'error': 'Unsubscribe failed'}), 500


@push_bp.route('/test', methods=['POST'])
@login_required
def test_notification():
    """Send test push notification"""
    try:
        push_service = get_push_service()
        count = push_service.send_notification(
            user_id=current_user.id,
            title='Test Bildirimi',
            body='Push bildirimleri başarıyla çalışıyor!',
            url='/'
        )
        
        if count > 0:
            return jsonify({
                'success': True,
                'message': f'{count} cihaza bildirim gönderildi'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Aktif abonelik bulunamadı'
            }), 404
    
    except Exception as e:
        current_app.logger.error(f"Test notification failed: {str(e)}")
        return jsonify({'error': 'Test notification failed'}), 500
