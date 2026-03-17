"""
Recommendation Service
Sprint 16-18: AI ve Otomasyon
Akıllı öneriler ve insights
"""

from datetime import datetime, timedelta
from app.models.process import Process, ProcessKpi, KpiData
from app.services.ml_service import MLService
from app.services.anomaly_service import AnomalyService
import logging

logger = logging.getLogger(__name__)


class RecommendationService:
    """Akıllı öneri servisi"""
    
    def __init__(self):
        self.ml_service = MLService()
        self.anomaly_service = AnomalyService()
    
    def get_process_recommendations(self, process_id):
        """
        Süreç için öneriler oluştur
        
        Args:
            process_id: Process ID
        
        Returns:
            dict: Öneriler ve insights
        """
        try:
            process = Process.query.get(process_id)
            if not process:
                return {'success': False, 'error': 'Süreç bulunamadı'}
            
            recommendations = []
            insights = []
            
            # KPI'ları analiz et
            kpis = ProcessKpi.query.filter_by(
                process_id=process_id,
                is_active=True
            ).all()
            
            for kpi in kpis:
                # Performans analizi
                perf_rec = self._analyze_kpi_performance(kpi)
                if perf_rec:
                    recommendations.extend(perf_rec)
                
                # Trend analizi
                trend_insight = self._analyze_kpi_trend(kpi)
                if trend_insight:
                    insights.append(trend_insight)
                
                # Anomali kontrolü
                anomaly_rec = self._check_kpi_anomalies(kpi)
                if anomaly_rec:
                    recommendations.extend(anomaly_rec)
            
            # Önceliklendirme
            recommendations = sorted(
                recommendations,
                key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']],
                reverse=True
            )
            
            return {
                'success': True,
                'process_id': process_id,
                'process_name': process.name,
                'recommendations': recommendations[:10],  # Top 10
                'insights': insights,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Process recommendations failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    
    def _analyze_kpi_performance(self, kpi):
        """KPI performans analizi"""
        recommendations = []
        
        # Son 3 ay verisi
        three_months_ago = datetime.now() - timedelta(days=90)
        recent_data = KpiData.query.filter(
            KpiData.process_kpi_id == kpi.id,
            KpiData.data_date >= three_months_ago,
            KpiData.is_active == True
        ).all()
        
        if len(recent_data) < 2:
            return recommendations
        
        # Ortalama başarı oranı
        achievements = [
            (d.actual_value / d.target_value * 100) if d.target_value > 0 else 0
            for d in recent_data
        ]
        avg_achievement = sum(achievements) / len(achievements)
        
        # Düşük performans
        if avg_achievement < 70:
            recommendations.append({
                'kpi_id': kpi.id,
                'kpi_name': kpi.kpi.name if kpi.kpi else 'N/A',
                'priority': 'high',
                'type': 'performance',
                'title': 'Düşük Performans',
                'message': f'Son 3 ayda ortalama %{avg_achievement:.1f} başarı. Hedefin altında.',
                'action': 'Kök neden analizi yapın ve aksiyon planı oluşturun'
            })
        
        # Orta performans
        elif avg_achievement < 90:
            recommendations.append({
                'kpi_id': kpi.id,
                'kpi_name': kpi.kpi.name if kpi.kpi else 'N/A',
                'priority': 'medium',
                'type': 'performance',
                'title': 'İyileştirme Fırsatı',
                'message': f'Ortalama %{avg_achievement:.1f} başarı. Hedefe yakın.',
                'action': 'Küçük iyileştirmelerle hedefe ulaşabilirsiniz'
            })
        
        return recommendations
    
    def _analyze_kpi_trend(self, kpi):
        """KPI trend analizi"""
        try:
            # Tahmin al
            forecast = self.ml_service.forecast_kpi(kpi.id, periods=3)
            
            if not forecast['success']:
                return None
            
            trend = forecast['trend']
            strength = forecast['trend_strength']
            
            if trend == 'decreasing' and strength > 0.5:
                return {
                    'kpi_id': kpi.id,
                    'kpi_name': kpi.kpi.name if kpi.kpi else 'N/A',
                    'type': 'trend',
                    'severity': 'warning',
                    'message': f'Negatif trend tespit edildi (güç: {strength:.2f})',
                    'forecast': forecast['predictions']
                }
            elif trend == 'increasing' and strength > 0.5:
                return {
                    'kpi_id': kpi.id,
                    'kpi_name': kpi.kpi.name if kpi.kpi else 'N/A',
                    'type': 'trend',
                    'severity': 'positive',
                    'message': f'Pozitif trend devam ediyor (güç: {strength:.2f})',
                    'forecast': forecast['predictions']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {str(e)}")
            return None
    
    def _check_kpi_anomalies(self, kpi):
        """KPI anomali kontrolü"""
        recommendations = []
        
        try:
            result = self.anomaly_service.detect_anomalies(kpi.id)
            
            if result['success'] and result['anomaly_count'] > 0:
                latest = result['anomalies'][-1]
                
                recommendations.append({
                    'kpi_id': kpi.id,
                    'kpi_name': kpi.kpi.name if kpi.kpi else 'N/A',
                    'priority': 'high' if latest['severity'] == 'high' else 'medium',
                    'type': 'anomaly',
                    'title': 'Anormal Değer Tespit Edildi',
                    'message': f"Tarih: {latest['date']}, Değer: {latest['value']}, Sapma: {latest['deviation']}%",
                    'action': 'Veri doğruluğunu kontrol edin ve nedeni araştırın'
                })
        
        except Exception as e:
            logger.error(f"Anomaly check failed: {str(e)}")
        
        return recommendations
    
    def get_smart_insights(self, tenant_id):
        """
        Tenant için akıllı insights
        
        Args:
            tenant_id: Tenant ID
        
        Returns:
            dict: Insights ve öneriler
        """
        try:
            insights = {
                'top_performers': [],
                'needs_attention': [],
                'trending_up': [],
                'trending_down': [],
                'summary': {}
            }
            
            # Tüm aktif süreçler
            processes = Process.query.filter_by(
                tenant_id=tenant_id,
                is_active=True
            ).all()
            
            total_kpis = 0
            on_target = 0
            below_target = 0
            
            for process in processes:
                kpis = ProcessKpi.query.filter_by(
                    process_id=process.id,
                    is_active=True
                ).all()
                
                for kpi in kpis:
                    total_kpis += 1
                    
                    # Son veri
                    latest = KpiData.query.filter_by(
                        process_kpi_id=kpi.id,
                        is_active=True
                    ).order_by(KpiData.data_date.desc()).first()
                    
                    if not latest:
                        continue
                    
                    achievement = (latest.actual_value / latest.target_value * 100) if latest.target_value > 0 else 0
                    
                    if achievement >= 100:
                        on_target += 1
                        insights['top_performers'].append({
                            'kpi_name': kpi.kpi.name if kpi.kpi else 'N/A',
                            'process_name': process.name,
                            'achievement': round(achievement, 1)
                        })
                    elif achievement < 80:
                        below_target += 1
                        insights['needs_attention'].append({
                            'kpi_name': kpi.kpi.name if kpi.kpi else 'N/A',
                            'process_name': process.name,
                            'achievement': round(achievement, 1)
                        })
            
            # Özet
            insights['summary'] = {
                'total_kpis': total_kpis,
                'on_target': on_target,
                'below_target': below_target,
                'on_target_percentage': round((on_target / total_kpis * 100) if total_kpis > 0 else 0, 1)
            }
            
            # Sırala ve sınırla
            insights['top_performers'] = sorted(
                insights['top_performers'],
                key=lambda x: x['achievement'],
                reverse=True
            )[:5]
            
            insights['needs_attention'] = sorted(
                insights['needs_attention'],
                key=lambda x: x['achievement']
            )[:5]
            
            return {
                'success': True,
                'tenant_id': tenant_id,
                'insights': insights,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Smart insights failed: {str(e)}")
            return {'success': False, 'error': str(e)}
