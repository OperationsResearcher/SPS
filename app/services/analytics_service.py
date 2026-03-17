"""
Analytics Service
Sprint 10-12: Analytics ve Raporlama
Gelişmiş analitik ve raporlama servisi
"""

from app.extensions import db
from app.models.process import Process, ProcessKpi, KpiData
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from sqlalchemy import func, and_, or_

class AnalyticsService:
    """Analytics ve raporlama servisi"""
    
    @staticmethod
    def get_performance_trend(
        process_id: int,
        kpi_id: int,
        start_date: datetime,
        end_date: datetime,
        frequency: str = 'monthly'
    ) -> Dict:
        """
        KPI performans trendi
        
        Args:
            process_id: Süreç ID
            kpi_id: KPI ID
            start_date: Başlangıç tarihi
            end_date: Bitiş tarihi
            frequency: Frekans (daily, weekly, monthly, quarterly)
        
        Returns:
            Trend verisi (dates, actual_values, target_values, performance_rates)
        """
        # KPI verilerini çek
        kpi_data = KpiData.query.filter(
            KpiData.process_kpi_id == kpi_id,
            KpiData.data_date.between(start_date, end_date),
            KpiData.is_active == True
        ).order_by(KpiData.data_date).all()
        
        if not kpi_data:
            return {
                'dates': [],
                'actual_values': [],
                'target_values': [],
                'performance_rates': []
            }
        
        # DataFrame'e çevir
        df = pd.DataFrame([{
            'date': d.data_date,
            'actual': d.actual_value,
            'target': d.target_value
        } for d in kpi_data])
        
        # Frekansa göre grupla
        if frequency == 'daily':
            grouped = df
        elif frequency == 'weekly':
            df['week'] = df['date'].dt.to_period('W')
            grouped = df.groupby('week').agg({
                'actual': 'mean',
                'target': 'mean'
            }).reset_index()
            grouped['date'] = grouped['week'].dt.start_time
        elif frequency == 'monthly':
            df['month'] = df['date'].dt.to_period('M')
            grouped = df.groupby('month').agg({
                'actual': 'mean',
                'target': 'mean'
            }).reset_index()
            grouped['date'] = grouped['month'].dt.start_time
        elif frequency == 'quarterly':
            df['quarter'] = df['date'].dt.to_period('Q')
            grouped = df.groupby('quarter').agg({
                'actual': 'mean',
                'target': 'mean'
            }).reset_index()
            grouped['date'] = grouped['quarter'].dt.start_time
        else:
            grouped = df
        
        # Performans oranını hesapla
        grouped['performance_rate'] = (grouped['actual'] / grouped['target'] * 100).round(2)
        
        return {
            'dates': grouped['date'].dt.strftime('%Y-%m-%d').tolist(),
            'actual_values': grouped['actual'].tolist(),
            'target_values': grouped['target'].tolist(),
            'performance_rates': grouped['performance_rate'].tolist()
        }

    
    @staticmethod
    def get_process_health_score(process_id: int, year: int = None) -> Dict:
        """
        Süreç sağlık skoru
        
        Returns:
            {
                'overall_score': 85.5,
                'kpi_scores': [...],
                'status': 'good',
                'recommendations': [...]
            }
        """
        if year is None:
            year = datetime.now().year
        
        # Süreç KPI'larını çek
        kpis = ProcessKpi.query.filter_by(
            process_id=process_id,
            is_active=True
        ).all()
        
        if not kpis:
            return {
                'overall_score': 0,
                'kpi_scores': [],
                'status': 'no_data',
                'recommendations': ['KPI tanımlanmamış']
            }
        
        kpi_scores = []
        total_weight = 0
        weighted_score = 0
        
        for kpi in kpis:
            # Son veriyi al
            latest_data = KpiData.query.filter_by(
                process_kpi_id=kpi.id,
                is_active=True
            ).order_by(KpiData.data_date.desc()).first()
            
            if latest_data and latest_data.target_value > 0:
                performance = (latest_data.actual_value / latest_data.target_value) * 100
                weight = kpi.weight or 1
                
                kpi_scores.append({
                    'kpi_id': kpi.id,
                    'kpi_name': kpi.name,
                    'performance': round(performance, 2),
                    'weight': weight,
                    'status': AnalyticsService._get_performance_status(performance)
                })
                
                weighted_score += performance * weight
                total_weight += weight
        
        overall_score = round(weighted_score / total_weight, 2) if total_weight > 0 else 0
        status = AnalyticsService._get_performance_status(overall_score)
        recommendations = AnalyticsService._generate_recommendations(kpi_scores, overall_score)
        
        return {
            'overall_score': overall_score,
            'kpi_scores': kpi_scores,
            'status': status,
            'recommendations': recommendations
        }
    
    @staticmethod
    def _get_performance_status(performance: float) -> str:
        """Performans durumu"""
        if performance >= 100:
            return 'excellent'
        elif performance >= 90:
            return 'good'
        elif performance >= 80:
            return 'fair'
        elif performance >= 70:
            return 'poor'
        else:
            return 'critical'
    
    @staticmethod
    def _generate_recommendations(kpi_scores: List[Dict], overall_score: float) -> List[str]:
        """Öneriler oluştur"""
        recommendations = []
        
        # Genel durum
        if overall_score < 70:
            recommendations.append('Acil aksiyon gerekiyor: Genel performans kritik seviyede')
        elif overall_score < 80:
            recommendations.append('Dikkat: Performans hedefin altında')
        elif overall_score >= 100:
            recommendations.append('Tebrikler! Tüm hedefler aşıldı')
        
        # Düşük performanslı KPI'lar
        poor_kpis = [k for k in kpi_scores if k['performance'] < 80]
        if poor_kpis:
            recommendations.append(f'{len(poor_kpis)} KPI hedefin altında: {", ".join([k["kpi_name"] for k in poor_kpis[:3]])}')
        
        # Yüksek ağırlıklı düşük performanslı KPI'lar
        critical_kpis = [k for k in kpi_scores if k['performance'] < 70 and k['weight'] > 5]
        if critical_kpis:
            recommendations.append(f'Yüksek öncelikli KPI\'lar kritik seviyede: {", ".join([k["kpi_name"] for k in critical_kpis])}')
        
        return recommendations
    
    @staticmethod
    def get_comparative_analysis(
        process_ids: List[int],
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Süreçler arası karşılaştırmalı analiz
        
        Returns:
            {
                'processes': [...],
                'comparison_data': {...}
            }
        """
        comparison_data = []
        
        for process_id in process_ids:
            process = Process.query.get(process_id)
            if not process:
                continue
            
            health = AnalyticsService.get_process_health_score(process_id)
            
            comparison_data.append({
                'process_id': process_id,
                'process_name': process.name,
                'process_code': process.code,
                'overall_score': health['overall_score'],
                'status': health['status'],
                'kpi_count': len(health['kpi_scores'])
            })
        
        # Sıralama (en yüksek skordan en düşüğe)
        comparison_data.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return {
            'processes': comparison_data,
            'best_performer': comparison_data[0] if comparison_data else None,
            'worst_performer': comparison_data[-1] if comparison_data else None,
            'average_score': round(sum([p['overall_score'] for p in comparison_data]) / len(comparison_data), 2) if comparison_data else 0
        }
    
    @staticmethod
    def get_anomaly_detection(
        kpi_id: int,
        lookback_days: int = 90,
        threshold: float = 2.0
    ) -> Dict:
        """
        Anomali tespiti (basit istatistiksel yöntem)
        
        Args:
            kpi_id: KPI ID
            lookback_days: Geriye bakış günü
            threshold: Standart sapma eşiği
        
        Returns:
            Anomali verisi
        """
        start_date = datetime.now() - timedelta(days=lookback_days)
        
        kpi_data = KpiData.query.filter(
            KpiData.process_kpi_id == kpi_id,
            KpiData.data_date >= start_date,
            KpiData.is_active == True
        ).order_by(KpiData.data_date).all()
        
        if len(kpi_data) < 10:
            return {
                'anomalies': [],
                'message': 'Yeterli veri yok (minimum 10 veri noktası gerekli)'
            }
        
        # DataFrame'e çevir
        df = pd.DataFrame([{
            'date': d.data_date,
            'value': d.actual_value
        } for d in kpi_data])
        
        # İstatistikler
        mean = df['value'].mean()
        std = df['value'].std()
        
        # Anomalileri tespit et (z-score yöntemi)
        df['z_score'] = (df['value'] - mean) / std
        df['is_anomaly'] = df['z_score'].abs() > threshold
        
        anomalies = df[df['is_anomaly']].to_dict('records')
        
        return {
            'anomalies': [{
                'date': a['date'].strftime('%Y-%m-%d'),
                'value': a['value'],
                'z_score': round(a['z_score'], 2),
                'deviation': round(((a['value'] - mean) / mean) * 100, 2)
            } for a in anomalies],
            'statistics': {
                'mean': round(mean, 2),
                'std': round(std, 2),
                'min': round(df['value'].min(), 2),
                'max': round(df['value'].max(), 2)
            }
        }
    
    @staticmethod
    def get_forecast(
        kpi_id: int,
        periods: int = 3,
        method: str = 'moving_average'
    ) -> Dict:
        """
        Basit tahminleme (moving average)
        
        Args:
            kpi_id: KPI ID
            periods: Tahmin periyodu
            method: Tahmin yöntemi (moving_average, linear_trend)
        
        Returns:
            Tahmin verisi
        """
        # Son 12 aylık veriyi al
        start_date = datetime.now() - timedelta(days=365)
        
        kpi_data = KpiData.query.filter(
            KpiData.process_kpi_id == kpi_id,
            KpiData.data_date >= start_date,
            KpiData.is_active == True
        ).order_by(KpiData.data_date).all()
        
        if len(kpi_data) < 3:
            return {
                'forecast': [],
                'message': 'Yeterli veri yok (minimum 3 veri noktası gerekli)'
            }
        
        df = pd.DataFrame([{
            'date': d.data_date,
            'value': d.actual_value
        } for d in kpi_data])
        
        if method == 'moving_average':
            # 3 aylık hareketli ortalama
            window = min(3, len(df))
            forecast_value = df['value'].tail(window).mean()
            
            forecast = []
            last_date = df['date'].max()
            
            for i in range(1, periods + 1):
                next_date = last_date + timedelta(days=30 * i)
                forecast.append({
                    'date': next_date.strftime('%Y-%m-%d'),
                    'forecast_value': round(forecast_value, 2),
                    'confidence': 'medium'
                })
        
        elif method == 'linear_trend':
            # Basit lineer trend
            df['x'] = range(len(df))
            slope = (df['value'].iloc[-1] - df['value'].iloc[0]) / len(df)
            
            forecast = []
            last_date = df['date'].max()
            last_value = df['value'].iloc[-1]
            
            for i in range(1, periods + 1):
                next_date = last_date + timedelta(days=30 * i)
                forecast_value = last_value + (slope * i)
                forecast.append({
                    'date': next_date.strftime('%Y-%m-%d'),
                    'forecast_value': round(forecast_value, 2),
                    'confidence': 'low'
                })
        
        else:
            forecast = []
        
        return {
            'forecast': forecast,
            'method': method,
            'historical_data': df.tail(6).to_dict('records')
        }
