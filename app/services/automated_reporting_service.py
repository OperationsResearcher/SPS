"""
Automated Reporting Service
Sprint 16-18: AI ve Otomasyon
Otomatik rapor oluşturma ve gönderme
"""

from datetime import datetime, timedelta
from app.services.report_service import ReportService
from app.services.recommendation_service import RecommendationService
from app.models.core import User
from extensions import db
import logging

logger = logging.getLogger(__name__)


class AutomatedReportingService:
    """Otomatik raporlama servisi"""
    
    def __init__(self):
        self.report_service = ReportService()
        self.recommendation_service = RecommendationService()
    
    def generate_daily_digest(self, tenant_id):
        """
        Günlük özet raporu oluştur
        
        Args:
            tenant_id: Tenant ID
        
        Returns:
            dict: Rapor içeriği
        """
        try:
            # Dünün tarihi
            yesterday = datetime.now() - timedelta(days=1)
            
            # Insights al
            insights = self.recommendation_service.get_smart_insights(tenant_id)
            
            if not insights['success']:
                return insights
            
            # Rapor içeriği
            report = {
                'title': f'Günlük Özet - {yesterday.strftime("%d.%m.%Y")}',
                'date': yesterday.strftime('%Y-%m-%d'),
                'tenant_id': tenant_id,
                'summary': insights['insights']['summary'],
                'highlights': {
                    'top_performers': insights['insights']['top_performers'][:3],
                    'needs_attention': insights['insights']['needs_attention'][:3]
                },
                'generated_at': datetime.now().isoformat()
            }
            
            return {
                'success': True,
                'report': report
            }
            
        except Exception as e:
            logger.error(f"Daily digest failed: {e}")
            return {'success': False, 'error': 'Günlük özet oluşturulurken hata oluştu.'}
    
    def generate_weekly_summary(self, tenant_id):
        """
        Haftalık özet raporu
        
        Args:
            tenant_id: Tenant ID
        
        Returns:
            dict: Rapor içeriği
        """
        try:
            # Son 7 gün
            week_ago = datetime.now() - timedelta(days=7)
            
            # Insights
            insights = self.recommendation_service.get_smart_insights(tenant_id)
            
            if not insights['success']:
                return insights
            
            report = {
                'title': f'Haftalık Özet - {week_ago.strftime("%d.%m")} - {datetime.now().strftime("%d.%m.%Y")}',
                'period': {
                    'start': week_ago.strftime('%Y-%m-%d'),
                    'end': datetime.now().strftime('%Y-%m-%d')
                },
                'tenant_id': tenant_id,
                'summary': insights['insights']['summary'],
                'top_performers': insights['insights']['top_performers'],
                'needs_attention': insights['insights']['needs_attention'],
                'generated_at': datetime.now().isoformat()
            }
            
            return {
                'success': True,
                'report': report
            }
            
        except Exception as e:
            logger.error(f"Weekly summary failed: {e}")
            return {'success': False, 'error': 'Haftalık özet oluşturulurken hata oluştu.'}

    
    def generate_monthly_report(self, tenant_id):
        """
        Aylık performans raporu
        
        Args:
            tenant_id: Tenant ID
        
        Returns:
            dict: Rapor içeriği
        """
        try:
            # Geçen ay
            last_month = datetime.now() - timedelta(days=30)
            
            # Detaylı rapor
            report_data = self.report_service.generate_performance_report(
                tenant_id=tenant_id,
                start_date=last_month,
                end_date=datetime.now()
            )
            
            # Insights ekle
            insights = self.recommendation_service.get_smart_insights(tenant_id)
            
            report = {
                'title': f'Aylık Performans Raporu - {last_month.strftime("%B %Y")}',
                'period': {
                    'start': last_month.strftime('%Y-%m-%d'),
                    'end': datetime.now().strftime('%Y-%m-%d')
                },
                'tenant_id': tenant_id,
                'performance': report_data,
                'insights': insights['insights'] if insights['success'] else {},
                'generated_at': datetime.now().isoformat()
            }
            
            return {
                'success': True,
                'report': report
            }
            
        except Exception as e:
            logger.error(f"Monthly report failed: {e}")
            return {'success': False, 'error': 'Aylık rapor oluşturulurken hata oluştu.'}
    
    def schedule_and_send_reports(self, tenant_id, report_type='daily'):
        """
        Raporları oluştur ve gönder
        
        Args:
            tenant_id: Tenant ID
            report_type: 'daily', 'weekly', 'monthly'
        
        Returns:
            dict: Gönderim sonucu
        """
        try:
            # Rapor oluştur
            if report_type == 'daily':
                result = self.generate_daily_digest(tenant_id)
            elif report_type == 'weekly':
                result = self.generate_weekly_summary(tenant_id)
            else:
                result = self.generate_monthly_report(tenant_id)
            
            if not result['success']:
                return result
            
            # Rapor alacak kullanıcıları bul
            users = User.query.filter_by(
                tenant_id=tenant_id,
                is_active=True
            ).all()
            
            # Email gönder — tenant SMTP yapılandırması üzerinden (TASK-233)
            # Tercih: notification_preferences JSON'ında ilgili digest anahtarı
            # açıkça False ise gönderilmez (tanımsız = gönderilir).
            import json as _json
            from app.services.email_digest_service import _send_via_smtp

            recipients = []
            for user in users:
                try:
                    prefs = _json.loads(user.notification_preferences or "{}")
                except (TypeError, ValueError):
                    prefs = {}
                if prefs.get(f"{report_type}_digest") is False:
                    continue
                if user.email:
                    recipients.append(user.email)

            report = result.get('report') or {}
            subject = f"Kokpitim — {report_type} raporu"
            if isinstance(report, dict):
                rows = "".join(
                    f"<tr><td style='padding:4px 12px 4px 0'><b>{k}</b></td>"
                    f"<td>{v}</td></tr>" for k, v in report.items()
                )
                html = f"<html><body><table>{rows}</table></body></html>"
            else:
                html = f"<html><body><pre>{report}</pre></body></html>"

            sent_count = 0
            if recipients:
                sent_count = _send_via_smtp(tenant_id, recipients, subject, html)
            
            logger.info(f"{report_type.capitalize()} report sent to {sent_count} users")
            
            return {
                'success': True,
                'report_type': report_type,
                'sent_to': sent_count,
                'report': result['report']
            }
            
        except Exception as e:
            logger.error(f"Schedule and send failed: {e}")
            return {'success': False, 'error': 'Rapor gönderimi sırasında hata oluştu.'}
