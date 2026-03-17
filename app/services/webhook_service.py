"""
Webhook Service
Sprint 13-15: API ve Entegrasyonlar
Webhook yönetimi ve event dispatching
"""

from app.extensions import db
from typing import Dict, List
import requests
import hmac
import hashlib
import json
from datetime import datetime

class WebhookService:
    """Webhook yönetim servisi"""
    
    # Event tipleri
    EVENT_KPI_CREATED = 'kpi.created'
    EVENT_KPI_UPDATED = 'kpi.updated'
    EVENT_KPI_DELETED = 'kpi.deleted'
    EVENT_PROCESS_CREATED = 'process.created'
    EVENT_PROCESS_UPDATED = 'process.updated'
    EVENT_ALERT_TRIGGERED = 'alert.triggered'
    
    @staticmethod
    def dispatch_event(event_type: str, data: Dict, tenant_id: int):
        """
        Event dispatch et
        
        Args:
            event_type: Event tipi (kpi.created, kpi.updated, etc.)
            data: Event verisi
            tenant_id: Tenant ID
        """
        # Tenant'ın webhook'larını al
        webhooks = WebhookService.get_active_webhooks(tenant_id, event_type)
        
        for webhook in webhooks:
            WebhookService.send_webhook(webhook, event_type, data)
    
    @staticmethod
    def send_webhook(webhook: Dict, event_type: str, data: Dict):
        """
        Webhook gönder
        
        Args:
            webhook: Webhook konfigürasyonu
            event_type: Event tipi
            data: Event verisi
        """
        payload = {
            'event': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Kokpitim-Webhook/1.0'
        }
        
        # HMAC signature (güvenlik için)
        if webhook.get('secret'):
            signature = WebhookService.generate_signature(
                payload, 
                webhook['secret']
            )
            headers['X-Webhook-Signature'] = signature
        
        try:
            response = requests.post(
                webhook['url'],
                json=payload,
                headers=headers,
                timeout=10
            )
            
            # Log webhook delivery
            WebhookService.log_delivery(
                webhook_id=webhook['id'],
                event_type=event_type,
                status_code=response.status_code,
                response_body=response.text[:1000]
            )
            
        except Exception as e:
            # Log failed delivery
            WebhookService.log_delivery(
                webhook_id=webhook['id'],
                event_type=event_type,
                status_code=0,
                error=str(e)
            )
    
    @staticmethod
    def generate_signature(payload: Dict, secret: str) -> str:
        """
        HMAC signature oluştur
        
        Args:
            payload: Webhook payload
            secret: Webhook secret
        
        Returns:
            HMAC signature (hex)
        """
        message = json.dumps(payload, sort_keys=True).encode()
        signature = hmac.new(
            secret.encode(),
            message,
            hashlib.sha256
        ).hexdigest()
        
        return f'sha256={signature}'
    
    @staticmethod
    def verify_signature(payload: Dict, signature: str, secret: str) -> bool:
        """
        HMAC signature doğrula
        
        Args:
            payload: Webhook payload
            signature: Gelen signature
            secret: Webhook secret
        
        Returns:
            True if valid, False otherwise
        """
        expected_signature = WebhookService.generate_signature(payload, secret)
        return hmac.compare_digest(signature, expected_signature)
    
    @staticmethod
    def get_active_webhooks(tenant_id: int, event_type: str) -> List[Dict]:
        """
        Aktif webhook'ları getir
        
        Args:
            tenant_id: Tenant ID
            event_type: Event tipi
        
        Returns:
            Webhook listesi
        """
        # TODO: Database'den webhook'ları çek
        # webhooks = Webhook.query.filter_by(
        #     tenant_id=tenant_id,
        #     is_active=True
        # ).filter(
        #     Webhook.events.contains([event_type])
        # ).all()
        
        # Placeholder
        return []
    
    @staticmethod
    def log_delivery(webhook_id: int, event_type: str, status_code: int, 
                     response_body: str = None, error: str = None):
        """
        Webhook delivery log
        
        Args:
            webhook_id: Webhook ID
            event_type: Event tipi
            status_code: HTTP status code
            response_body: Response body
            error: Error message
        """
        # TODO: Database'e log kaydet
        # log = WebhookDelivery(
        #     webhook_id=webhook_id,
        #     event_type=event_type,
        #     status_code=status_code,
        #     response_body=response_body,
        #     error=error,
        #     delivered_at=datetime.utcnow()
        # )
        # db.session.add(log)
        # db.session.commit()
        
        print(f"Webhook delivery: {webhook_id} - {event_type} - {status_code}")


# Helper functions
def trigger_kpi_created_webhook(kpi_data: Dict, tenant_id: int):
    """KPI oluşturuldu webhook'u"""
    WebhookService.dispatch_event(
        WebhookService.EVENT_KPI_CREATED,
        kpi_data,
        tenant_id
    )


def trigger_kpi_updated_webhook(kpi_data: Dict, tenant_id: int):
    """KPI güncellendi webhook'u"""
    WebhookService.dispatch_event(
        WebhookService.EVENT_KPI_UPDATED,
        kpi_data,
        tenant_id
    )


def trigger_alert_webhook(alert_data: Dict, tenant_id: int):
    """Alert webhook'u"""
    WebhookService.dispatch_event(
        WebhookService.EVENT_ALERT_TRIGGERED,
        alert_data,
        tenant_id
    )
