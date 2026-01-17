# -*- coding: utf-8 -*-
"""
AI Destekli Erken Uyarı Servisleri
Gecikme olasılığı tahmini ve proje bitiş tarihi tahmini
"""
from datetime import datetime, date, timedelta
from flask import current_app
from models import (
    db, Project, Task, TaskActivity, ProjectRisk
)
from sqlalchemy import func
import statistics


def calculate_delay_probability(project_id):
    """
    Projenin gecikme olasılığını hesaplar
    
    Algoritma:
    1. Tamamlanan görevlerin estimated_time vs actual_time karşılaştırması
    2. Ortalama sapma oranı hesaplama
    3. Aktif görevlerin tahmini sürelerine sapma oranını uygulama
    4. Toplam gecikme tahmini
    
    Returns:
        dict: {
            'delay_probability': float (0-100),
            'estimated_completion_date': date,
            'planned_completion_date': date,
            'days_delay': int,
            'confidence': float (0-100),
            'insights': list
        }
    """
    try:
        project = Project.query.get(project_id)
        if not project:
            return None
        
        # Projenin tüm görevlerini getir
        all_tasks = Task.query.filter_by(project_id=project_id).all()
        
        # Projenin aktif risklerini getir (risk faktörü için)
        active_risks = ProjectRisk.query.filter_by(
            project_id=project_id,
            status='Aktif'
        ).all()
        
        # Risk faktörünü hesapla (risk skorlarına göre)
        risk_factor = 0.0
        critical_risks_count = 0
        high_risks_count = 0
        
        if active_risks:
            for risk in active_risks:
                risk_score = risk.risk_score  # impact * probability
                if risk_score >= 20:  # Kritik risk
                    risk_factor += 0.15  # Her kritik risk %15 gecikme olasılığı ekler
                    critical_risks_count += 1
                elif risk_score >= 15:  # Yüksek risk
                    risk_factor += 0.10  # Her yüksek risk %10 gecikme olasılığı ekler
                    high_risks_count += 1
                elif risk_score >= 9:  # Orta risk
                    risk_factor += 0.05  # Her orta risk %5 gecikme olasılığı ekler
        
        # Risk faktörünü maksimum %50 ile sınırla
        risk_factor = min(0.5, risk_factor)
        
        if not all_tasks:
            # Görev yoksa ama risk varsa, risk faktörüne göre gecikme olasılığı hesapla
            if active_risks:
                delay_probability_from_risks = min(100, risk_factor * 100)
                insights = []
                if critical_risks_count > 0:
                    insights.append(f"{critical_risks_count} kritik risk tespit edildi")
                if high_risks_count > 0:
                    insights.append(f"{high_risks_count} yüksek risk tespit edildi")
                insights.append("Risk faktörü gecikme olasılığını artırıyor")
                
                return {
                    'delay_probability': round(delay_probability_from_risks, 1),
                    'estimated_completion_date': None,
                    'planned_completion_date': None,
                    'days_delay': 0,
                    'confidence': 30,  # Risk bazlı tahmin için düşük güven
                    'insights': insights,
                    'risk_based': True
                }
            else:
                return {
                    'delay_probability': 0,
                    'estimated_completion_date': None,
                    'planned_completion_date': None,
                    'days_delay': 0,
                    'confidence': 0,
                    'insights': ['Henüz görev bulunmamaktadır']
                }
        
        # Tamamlanan görevlerin sapma analizi
        completed_tasks = [t for t in all_tasks if t.status == 'Tamamlandı' and t.estimated_time and t.actual_time]
        
        deviation_ratios = []
        if completed_tasks:
            for task in completed_tasks:
                if task.estimated_time > 0:
                    ratio = task.actual_time / task.estimated_time
                    deviation_ratios.append(ratio)
        
        # Ortalama sapma oranı (1.0 = tam zamanında, >1.0 = gecikme)
        avg_deviation = statistics.mean(deviation_ratios) if deviation_ratios else 1.0
        
        # Aktif görevlerin toplam tahmini süresi
        active_tasks = [t for t in all_tasks if t.status != 'Tamamlandı' and t.estimated_time]
        total_estimated_hours = sum(t.estimated_time for t in active_tasks)
        
        # Gecikme tahmini (sapma oranına göre)
        if avg_deviation > 1.0:
            delay_hours = total_estimated_hours * (avg_deviation - 1.0)
        else:
            delay_hours = 0
        
        # En geç bitiş tarihini bul (aktif görevlerin due_date'lerinden)
        latest_due_date = None
        for task in active_tasks:
            if task.due_date:
                if latest_due_date is None or task.due_date > latest_due_date:
                    latest_due_date = task.due_date
        
        # Tahmini tamamlanma tarihi
        estimated_completion = latest_due_date
        if delay_hours > 0 and latest_due_date:
            # Günlük 8 saat çalışma varsayımı
            delay_days = int(delay_hours / 8)
            estimated_completion = latest_due_date + timedelta(days=delay_days)
        
        # Gecikme olasılığı hesaplama (görev bazlı)
        delay_probability = 0
        if avg_deviation > 1.0:
            # Sapma oranına göre olasılık (1.0 = %0, 1.5 = %50, 2.0 = %100)
            delay_probability = min(100, (avg_deviation - 1.0) * 100)
        
        # Risk faktörünü ekle (risk bazlı gecikme olasılığı)
        risk_based_probability = min(100, risk_factor * 100)
        
        # İki olasılığı birleştir (görev bazlı + risk bazlı)
        # Görev bazlı olasılık daha ağırlıklı (0.7), risk bazlı daha az ağırlıklı (0.3)
        if delay_probability > 0 or risk_based_probability > 0:
            if delay_probability > 0:
                # Görev verisi varsa, risk faktörünü ekle
                combined_probability = (delay_probability * 0.7) + (risk_based_probability * 0.3)
            else:
                # Sadece risk verisi varsa, risk bazlı olasılığı kullan
                combined_probability = risk_based_probability
        else:
            combined_probability = 0
        
        delay_probability = min(100, combined_probability)
        
        # Güven seviyesi (tamamlanan görev sayısına göre)
        confidence = min(100, (len(completed_tasks) / max(1, len(all_tasks))) * 100)
        
        # Risk varsa güven seviyesini artır (risk verisi ek bilgi sağlar)
        if active_risks:
            confidence = min(100, confidence + 20)
        
        # İçgörüler
        insights = []
        if avg_deviation > 1.2:
            insights.append(f"Tamamlanan görevler ortalama %{int((avg_deviation - 1) * 100)} gecikme gösteriyor")
        if delay_hours > 0:
            insights.append(f"Tahmini gecikme: {int(delay_hours / 8)} iş günü")
        if critical_risks_count > 0:
            insights.append(f"⚠️ {critical_risks_count} kritik risk proje zamanlamasını etkileyebilir")
        if high_risks_count > 0:
            insights.append(f"⚠️ {high_risks_count} yüksek risk tespit edildi")
        if len(completed_tasks) < 3 and len(all_tasks) > 0:
            insights.append("Daha fazla veri toplandıkça tahmin daha doğru olacaktır")
        if not completed_tasks and active_risks:
            insights.append("Risk analizi gecikme olasılığını artırıyor")
        
        return {
            'delay_probability': round(delay_probability, 1),
            'estimated_completion_date': estimated_completion.isoformat() if estimated_completion else None,
            'planned_completion_date': latest_due_date.isoformat() if latest_due_date else None,
            'days_delay': int(delay_hours / 8) if delay_hours > 0 else 0,
            'confidence': round(confidence, 1),
            'insights': insights,
            'avg_deviation': round(avg_deviation, 2),
            'completed_tasks_count': len(completed_tasks),
            'active_tasks_count': len(active_tasks),
            'risk_factor': round(risk_factor * 100, 1),  # Risk faktörü yüzde olarak
            'critical_risks_count': critical_risks_count,
            'high_risks_count': high_risks_count
        }
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f'AI erken uyarı hesaplama hatası: {e}')
        return None


def get_project_completion_probability(project_id, target_date):
    """
    Projenin belirli bir tarihte tamamlanma olasılığını hesaplar
    
    Args:
        project_id: Proje ID
        target_date: Hedef tamamlanma tarihi (date)
    
    Returns:
        float: Tamamlanma olasılığı (0-100)
    """
    try:
        delay_data = calculate_delay_probability(project_id)
        if not delay_data:
            return 50.0  # Varsayılan
        
        estimated_date_str = delay_data.get('estimated_completion_date')
        if not estimated_date_str:
            return 50.0
        
        estimated_date = datetime.fromisoformat(estimated_date_str).date()
        
        # Tarih farkına göre olasılık hesaplama
        days_diff = (estimated_date - target_date).days
        
        if days_diff <= 0:
            # Tahmini tarih hedef tarihten önce veya eşitse yüksek olasılık
            probability = max(50, 100 - abs(days_diff) * 2)
        else:
            # Tahmini tarih hedef tarihten sonraysa düşük olasılık
            probability = max(10, 100 - (days_diff * 5))
        
        return min(100, max(0, probability))
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Tamamlanma olasılığı hesaplama hatası: {e}')
        return 50.0

























