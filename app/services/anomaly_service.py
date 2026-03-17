"""
Anomaly Detection Service
Sprint 16-18: AI ve Otomasyon
Anormal veri tespiti ve uyarılar
"""

import numpy as np
from datetime import datetime, timedelta
from app.models.process import ProcessKpi, KpiData
from app.services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)


class AnomalyService:
    """Anomali tespit servisi"""
    
    def __init__(self):
        self.notification_service = NotificationService()
    
    def detect_anomalies(self, kpi_id, method='zscore', threshold=2.5):
        """
        KPI verilerinde anomali tespit et
        
        Args:
            kpi_id: ProcessKpi ID
            method: Tespit yöntemi ('zscore', 'iqr', 'moving_avg')
            threshold: Eşik değeri
        
        Returns:
            dict: Tespit edilen anomaliler
        """
        try:
            # Son 6 ay verisi
            six_months_ago = datetime.now() - timedelta(days=180)
            data = KpiData.query.filter(
                KpiData.process_kpi_id == kpi_id,
                KpiData.data_date >= six_months_ago,
                KpiData.is_active == True
            ).order_by(KpiData.data_date).all()
            
            if len(data) < 10:
                return {
                    'success': False,
                    'error': 'Yetersiz veri (minimum 10 kayıt gerekli)'
                }
            
            values = np.array([d.actual_value for d in data])
            dates = [d.data_date for d in data]
            
            # Anomali tespiti
            if method == 'zscore':
                anomalies = self._detect_zscore(values, threshold)
            elif method == 'iqr':
                anomalies = self._detect_iqr(values)
            else:
                anomalies = self._detect_moving_avg(values, threshold)
            
            # Anomali detayları
            anomaly_details = []
            for idx in anomalies:
                anomaly_details.append({
                    'date': dates[idx].strftime('%Y-%m-%d'),
                    'value': float(values[idx]),
                    'deviation': self._calculate_deviation(values, idx),
                    'severity': self._calculate_severity(values, idx)
                })

            
            return {
                'success': True,
                'kpi_id': kpi_id,
                'method': method,
                'total_points': len(data),
                'anomaly_count': len(anomalies),
                'anomalies': anomaly_details
            }
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _detect_zscore(self, values, threshold):
        """Z-score yöntemi ile anomali tespiti"""
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            return []
        
        z_scores = np.abs((values - mean) / std)
        return np.where(z_scores > threshold)[0].tolist()
    
    def _detect_iqr(self, values):
        """IQR (Interquartile Range) yöntemi"""
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)
        
        return np.where((values < lower_bound) | (values > upper_bound))[0].tolist()
    
    def _detect_moving_avg(self, values, threshold):
        """Hareketli ortalama yöntemi"""
        window = min(5, len(values) // 3)
        moving_avg = np.convolve(values, np.ones(window)/window, mode='valid')
        
        # Padding for alignment
        padding = len(values) - len(moving_avg)
        moving_avg = np.pad(moving_avg, (padding//2, padding - padding//2), mode='edge')
        
        deviations = np.abs(values - moving_avg)
        threshold_value = np.mean(deviations) + threshold * np.std(deviations)
        
        return np.where(deviations > threshold_value)[0].tolist()
    
    def _calculate_deviation(self, values, idx):
        """Sapma yüzdesi hesapla"""
        mean = np.mean(values)
        if mean == 0:
            return 0
        return round(((values[idx] - mean) / mean) * 100, 2)
    
    def _calculate_severity(self, values, idx):
        """Anomali şiddeti (low, medium, high)"""
        deviation = abs(self._calculate_deviation(values, idx))
        
        if deviation > 50:
            return 'high'
        elif deviation > 25:
            return 'medium'
        else:
            return 'low'
    
    def monitor_and_alert(self, kpi_id, user_id):
        """
        KPI'ı izle ve anomali varsa uyar
        
        Args:
            kpi_id: ProcessKpi ID
            user_id: Uyarı gönderilecek kullanıcı
        
        Returns:
            bool: Anomali tespit edildi mi?
        """
        try:
            result = self.detect_anomalies(kpi_id)
            
            if not result['success']:
                return False
            
            if result['anomaly_count'] > 0:
                # En son anomali
                latest_anomaly = result['anomalies'][-1]
                
                # Bildirim gönder
                self.notification_service.create_notification(
                    user_id=user_id,
                    notification_type='anomaly_detected',
                    title='Anomali Tespit Edildi',
                    message=f"KPI'da anormal değer tespit edildi: {latest_anomaly['value']} ({latest_anomaly['severity']} seviye)",
                    priority='high' if latest_anomaly['severity'] == 'high' else 'medium',
                    action_url=f'/process/kpi/{kpi_id}',
                    extra_data={
                        'kpi_id': kpi_id,
                        'anomaly': latest_anomaly
                    }
                )
                
                logger.info(f"Anomaly alert sent for KPI {kpi_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Monitor and alert failed: {str(e)}")
            return False
