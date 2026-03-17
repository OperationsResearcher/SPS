"""
Machine Learning Service
Sprint 16-18: AI ve Otomasyon
Tahminsel analitik ve forecasting
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from app.models.process import ProcessKpi, KpiData
from app.extensions import db
import logging

logger = logging.getLogger(__name__)


class MLService:
    """Machine Learning servisi - Tahminleme ve forecasting"""
    
    def __init__(self):
        self.scaler = StandardScaler()
    
    def forecast_kpi(self, kpi_id, periods=3):
        """
        KPI için gelecek dönem tahmini
        
        Args:
            kpi_id: ProcessKpi ID
            periods: Kaç dönem ilerisi tahmin edilecek (varsayılan 3 ay)
        
        Returns:
            dict: Tahmin sonuçları
        """
        try:
            # Geçmiş verileri al
            historical_data = KpiData.query.filter_by(
                process_kpi_id=kpi_id,
                is_active=True
            ).order_by(KpiData.data_date).all()
            
            if len(historical_data) < 3:
                return {
                    'success': False,
                    'error': 'Yetersiz veri (minimum 3 dönem gerekli)'
                }
            
            # DataFrame'e dönüştür
            df = pd.DataFrame([{
                'date': d.data_date,
                'actual': d.actual_value,
                'target': d.target_value
            } for d in historical_data])
            
            # Zaman serisi özellikleri
            df['month'] = pd.to_datetime(df['date']).dt.month
            df['quarter'] = pd.to_datetime(df['date']).dt.quarter
            df['days_since_start'] = (pd.to_datetime(df['date']) - pd.to_datetime(df['date'].min())).dt.days
            
            # Model eğit
            X = df[['days_since_start', 'month', 'quarter']].values
            y = df['actual'].values
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Gelecek dönemler için tahmin
            last_date = pd.to_datetime(df['date'].max())
            predictions = []
            
            for i in range(1, periods + 1):
                future_date = last_date + timedelta(days=30 * i)
                future_features = np.array([[
                    (future_date - pd.to_datetime(df['date'].min())).days,
                    future_date.month,
                    future_date.quarter
                ]])
                
                prediction = model.predict(future_features)[0]
                predictions.append({
                    'date': future_date.strftime('%Y-%m-%d'),
                    'predicted_value': round(float(prediction), 2),
                    'confidence': self._calculate_confidence(df, prediction)
                })

            
            # Trend analizi
            trend = 'increasing' if model.coef_[0] > 0 else 'decreasing'
            trend_strength = abs(model.coef_[0])
            
            # Model performansı
            score = model.score(X, y)
            
            return {
                'success': True,
                'kpi_id': kpi_id,
                'predictions': predictions,
                'trend': trend,
                'trend_strength': round(float(trend_strength), 4),
                'model_score': round(float(score), 4),
                'historical_count': len(historical_data)
            }
            
        except Exception as e:
            logger.error(f"Forecast failed for KPI {kpi_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_confidence(self, df, prediction):
        """Tahmin güven skoru hesapla"""
        std = df['actual'].std()
        mean = df['actual'].mean()
        
        if mean == 0:
            return 0.5
        
        # Standart sapmaya göre güven skoru
        deviation = abs(prediction - mean) / std if std > 0 else 0
        confidence = max(0.3, min(0.95, 1 - (deviation * 0.1)))
        
        return round(confidence, 2)
    
    def calculate_achievement_probability(self, kpi_id, target_value=None):
        """
        Hedef başarı olasılığı hesapla
        
        Args:
            kpi_id: ProcessKpi ID
            target_value: Hedef değer (None ise mevcut hedef kullanılır)
        
        Returns:
            dict: Başarı olasılığı ve öneriler
        """
        try:
            kpi = ProcessKpi.query.get(kpi_id)
            if not kpi:
                return {'success': False, 'error': 'KPI bulunamadı'}
            
            # Son 6 ay verisi
            six_months_ago = datetime.now() - timedelta(days=180)
            recent_data = KpiData.query.filter(
                KpiData.process_kpi_id == kpi_id,
                KpiData.data_date >= six_months_ago,
                KpiData.is_active == True
            ).order_by(KpiData.data_date).all()
            
            if len(recent_data) < 3:
                return {
                    'success': False,
                    'error': 'Yetersiz veri'
                }
            
            # Hedef değer
            target = target_value or (recent_data[-1].target_value if recent_data else 0)
            
            # Performans analizi
            achievements = [
                (d.actual_value / d.target_value * 100) if d.target_value > 0 else 0
                for d in recent_data
            ]
            
            avg_achievement = np.mean(achievements)
            trend = np.polyfit(range(len(achievements)), achievements, 1)[0]
            
            # Olasılık hesapla
            if avg_achievement >= 100:
                base_probability = 0.85
            elif avg_achievement >= 90:
                base_probability = 0.70
            elif avg_achievement >= 80:
                base_probability = 0.55
            else:
                base_probability = 0.35
            
            # Trend etkisi
            if trend > 0:
                probability = min(0.95, base_probability + 0.1)
            elif trend < -5:
                probability = max(0.1, base_probability - 0.15)
            else:
                probability = base_probability
            
            # Öneriler
            recommendations = self._generate_recommendations(
                avg_achievement, trend, probability
            )
            
            return {
                'success': True,
                'kpi_id': kpi_id,
                'kpi_name': kpi.kpi.name if kpi.kpi else 'N/A',
                'target_value': target,
                'probability': round(probability, 2),
                'avg_achievement': round(avg_achievement, 2),
                'trend': round(trend, 2),
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Achievement probability failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _generate_recommendations(self, avg_achievement, trend, probability):
        """Aksiyon önerileri oluştur"""
        recommendations = []
        
        if probability < 0.5:
            recommendations.append({
                'priority': 'high',
                'message': 'Hedef başarı riski yüksek. Acil aksiyon gerekli.',
                'action': 'Haftalık takip toplantısı planlayın'
            })
        
        if trend < -3:
            recommendations.append({
                'priority': 'high',
                'message': 'Negatif trend tespit edildi.',
                'action': 'Kök neden analizi yapın'
            })
        
        if avg_achievement < 80:
            recommendations.append({
                'priority': 'medium',
                'message': 'Ortalama performans düşük.',
                'action': 'Hedefleri gözden geçirin veya kaynakları artırın'
            })
        
        if probability > 0.8:
            recommendations.append({
                'priority': 'low',
                'message': 'Hedef başarı olasılığı yüksek.',
                'action': 'Mevcut stratejiye devam edin'
            })
        
        return recommendations
    
    def detect_seasonality(self, kpi_id):
        """
        Mevsimsellik tespiti
        
        Args:
            kpi_id: ProcessKpi ID
        
        Returns:
            dict: Mevsimsellik analizi
        """
        try:
            # Son 12 ay verisi
            one_year_ago = datetime.now() - timedelta(days=365)
            data = KpiData.query.filter(
                KpiData.process_kpi_id == kpi_id,
                KpiData.data_date >= one_year_ago,
                KpiData.is_active == True
            ).order_by(KpiData.data_date).all()
            
            if len(data) < 12:
                return {
                    'success': False,
                    'error': 'Mevsimsellik analizi için minimum 12 ay veri gerekli'
                }
            
            # Aylık ortalamalar
            df = pd.DataFrame([{
                'month': d.data_date.month,
                'value': d.actual_value
            } for d in data])
            
            monthly_avg = df.groupby('month')['value'].mean()
            overall_avg = df['value'].mean()
            
            # Mevsimsellik indeksi
            seasonality_index = {}
            for month in range(1, 13):
                if month in monthly_avg.index:
                    index = (monthly_avg[month] / overall_avg) * 100
                    seasonality_index[month] = round(float(index), 2)
            
            # En yüksek ve en düşük aylar
            max_month = max(seasonality_index, key=seasonality_index.get)
            min_month = min(seasonality_index, key=seasonality_index.get)
            
            # Mevsimsellik var mı?
            variance = np.var(list(seasonality_index.values()))
            has_seasonality = variance > 100
            
            return {
                'success': True,
                'kpi_id': kpi_id,
                'has_seasonality': has_seasonality,
                'seasonality_index': seasonality_index,
                'peak_month': max_month,
                'low_month': min_month,
                'variance': round(float(variance), 2)
            }
            
        except Exception as e:
            logger.error(f"Seasonality detection failed: {str(e)}")
            return {'success': False, 'error': str(e)}
