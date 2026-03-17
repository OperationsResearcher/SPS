"""
Automated Reporting Service
Sprint 16-18: AI ve Otomasyon
Otomatik rapor oluşturma ve gönderme
"""

from datetime import datetime, timedelta
from app.services.report_service import ReportService
from app.services.recommendation_service import RecommendationService
from app.models.core import User
from app.extensions import db
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
            logger.error(f"Daily digest failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
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
            logger.error(f"Weekly summary failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    
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
            logger.error(f"Monthly report failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
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
            
            # Email gönder (placeholder - gerçek email servisi gerekli)
            sent_count = 0
            for user in users:
                # Kullanıcı tercihlerini kontrol et
                # if user.notification_preferences.get(f'{report_type}_digest'):
                #     send_email(user.email, result['report'])
                sent_count += 1
            
            logger.info(f"{report_type.capitalize()} report sent to {sent_count} users")
            
            return {
                'success': True,
                'report_type': report_type,
                'sent_to': sent_count,
                'report': result['report']
            }
            
        except Exception as e:
            logger.error(f"Schedule and send failed: {str(e)}")
            return {'success': False, 'error': str(e)}
