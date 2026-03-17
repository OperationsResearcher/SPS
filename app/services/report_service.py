"""
Report Service
Sprint 10-12: Analytics ve Raporlama
Rapor oluşturma ve export servisi
"""

from app.extensions import db
from app.models.process import Process, ProcessKpi, KpiData
from app.services.analytics_service import AnalyticsService
from datetime import datetime
from typing import Dict, List
import io
import pandas as pd

class ReportService:
    """Rapor oluşturma servisi"""
    
    @staticmethod
    def generate_performance_report(
        process_id: int,
        start_date: datetime,
        end_date: datetime,
        format: str = 'json'
    ) -> Dict:
        """
        Performans raporu oluştur
        
        Args:
            process_id: Süreç ID
            start_date: Başlangıç tarihi
            end_date: Bitiş tarihi
            format: Rapor formatı (json, excel, pdf)
        
        Returns:
            Rapor verisi
        """
        process = Process.query.get(process_id)
        if not process:
            return {'error': 'Süreç bulunamadı'}
        
        # Süreç bilgileri
        report_data = {
            'report_info': {
                'title': f'{process.name} Performans Raporu',
                'process_code': process.code,
                'process_name': process.name,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'generated_at': datetime.now().isoformat()
            },
            'summary': {},
            'kpi_details': [],
            'trends': [],
            'recommendations': []
        }
        
        # Süreç sağlık skoru
        health = AnalyticsService.get_process_health_score(process_id)
        report_data['summary'] = {
            'overall_score': health['overall_score'],
            'status': health['status'],
            'total_kpis': len(health['kpi_scores']),
            'excellent_kpis': len([k for k in health['kpi_scores'] if k['status'] == 'excellent']),
            'good_kpis': len([k for k in health['kpi_scores'] if k['status'] == 'good']),
            'poor_kpis': len([k for k in health['kpi_scores'] if k['status'] in ['poor', 'critical']])
        }
        
        # KPI detayları
        kpis = ProcessKpi.query.filter_by(
            process_id=process_id,
            is_active=True
        ).all()
        
        for kpi in kpis:
            # Trend verisi
            trend = AnalyticsService.get_performance_trend(
                process_id, kpi.id, start_date, end_date, 'monthly'
            )
            
            # Son veri
            latest_data = KpiData.query.filter_by(
                process_kpi_id=kpi.id,
                is_active=True
            ).order_by(KpiData.data_date.desc()).first()
            
            kpi_detail = {
                'kpi_code': kpi.code,
                'kpi_name': kpi.name,
                'unit': kpi.unit,
                'frequency': kpi.frequency,
                'weight': kpi.weight,
                'latest_actual': latest_data.actual_value if latest_data else None,
                'latest_target': latest_data.target_value if latest_data else None,
                'latest_performance': round((latest_data.actual_value / latest_data.target_value * 100), 2) if latest_data and latest_data.target_value > 0 else None,
                'trend': trend
            }
            
            report_data['kpi_details'].append(kpi_detail)
        
        # Öneriler
        report_data['recommendations'] = health['recommendations']
        
        # Format'a göre export
        if format == 'excel':
            return ReportService._export_to_excel(report_data)
        elif format == 'pdf':
            return ReportService._export_to_pdf(report_data)
        else:
            return report_data
    
    @staticmethod
    def _export_to_excel(report_data: Dict) -> bytes:
        """Excel export"""
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Özet sayfası
            summary_df = pd.DataFrame([report_data['summary']])
            summary_df.to_excel(writer, sheet_name='Özet', index=False)
            
            # KPI detayları
            kpi_df = pd.DataFrame(report_data['kpi_details'])
            kpi_df.to_excel(writer, sheet_name='KPI Detayları', index=False)
            
            # Öneriler
            recommendations_df = pd.DataFrame({
                'Öneriler': report_data['recommendations']
            })
            recommendations_df.to_excel(writer, sheet_name='Öneriler', index=False)
        
        output.seek(0)
        return output.getvalue()

    
    @staticmethod
    def _export_to_pdf(report_data: Dict) -> bytes:
        """
        PDF export (placeholder - gerçek implementasyon için reportlab gerekli)
        """
        # TODO: reportlab ile PDF oluşturma
        return b'PDF export not implemented yet'
    
    @staticmethod
    def generate_dashboard_report(
        tenant_id: int,
        year: int = None
    ) -> Dict:
        """
        Dashboard özet raporu
        
        Returns:
            Dashboard verisi
        """
        if year is None:
            year = datetime.now().year
        
        # Tenant süreçleri
        processes = Process.query.filter_by(
            tenant_id=tenant_id,
            is_active=True
        ).all()
        
        dashboard_data = {
            'tenant_id': tenant_id,
            'year': year,
            'summary': {
                'total_processes': len(processes),
                'total_kpis': 0,
                'average_performance': 0,
                'excellent_processes': 0,
                'good_processes': 0,
                'poor_processes': 0
            },
            'process_scores': [],
            'top_performers': [],
            'needs_attention': []
        }
        
        total_score = 0
        process_scores = []
        
        for process in processes:
            health = AnalyticsService.get_process_health_score(process.id, year)
            
            process_score = {
                'process_id': process.id,
                'process_name': process.name,
                'process_code': process.code,
                'score': health['overall_score'],
                'status': health['status'],
                'kpi_count': len(health['kpi_scores'])
            }
            
            process_scores.append(process_score)
            total_score += health['overall_score']
            dashboard_data['summary']['total_kpis'] += len(health['kpi_scores'])
            
            # Durum sayıları
            if health['status'] == 'excellent':
                dashboard_data['summary']['excellent_processes'] += 1
            elif health['status'] == 'good':
                dashboard_data['summary']['good_processes'] += 1
            elif health['status'] in ['poor', 'critical']:
                dashboard_data['summary']['poor_processes'] += 1
        
        # Ortalama performans
        if len(processes) > 0:
            dashboard_data['summary']['average_performance'] = round(total_score / len(processes), 2)
        
        # Sıralama
        process_scores.sort(key=lambda x: x['score'], reverse=True)
        dashboard_data['process_scores'] = process_scores
        
        # En iyi performans gösterenler (top 5)
        dashboard_data['top_performers'] = process_scores[:5]
        
        # Dikkat gerektiren (bottom 5)
        dashboard_data['needs_attention'] = [p for p in process_scores if p['score'] < 80][:5]
        
        return dashboard_data
    
    @staticmethod
    def generate_custom_report(
        report_config: Dict
    ) -> Dict:
        """
        Özel rapor oluştur
        
        Args:
            report_config: {
                'title': 'Rapor Başlığı',
                'process_ids': [1, 2, 3],
                'kpi_ids': [10, 20, 30],
                'start_date': '2024-01-01',
                'end_date': '2024-12-31',
                'metrics': ['trend', 'comparison', 'forecast'],
                'format': 'json'
            }
        """
        report_data = {
            'title': report_config.get('title', 'Özel Rapor'),
            'generated_at': datetime.now().isoformat(),
            'sections': []
        }
        
        start_date = datetime.strptime(report_config['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(report_config['end_date'], '%Y-%m-%d')
        
        # Trend analizi
        if 'trend' in report_config.get('metrics', []):
            trend_section = {
                'type': 'trend',
                'title': 'Trend Analizi',
                'data': []
            }
            
            for kpi_id in report_config.get('kpi_ids', []):
                kpi = ProcessKpi.query.get(kpi_id)
                if kpi:
                    trend = AnalyticsService.get_performance_trend(
                        kpi.process_id, kpi_id, start_date, end_date, 'monthly'
                    )
                    trend_section['data'].append({
                        'kpi_name': kpi.name,
                        'trend': trend
                    })
            
            report_data['sections'].append(trend_section)
        
        # Karşılaştırmalı analiz
        if 'comparison' in report_config.get('metrics', []):
            comparison = AnalyticsService.get_comparative_analysis(
                report_config.get('process_ids', []),
                start_date,
                end_date
            )
            
            report_data['sections'].append({
                'type': 'comparison',
                'title': 'Karşılaştırmalı Analiz',
                'data': comparison
            })
        
        # Tahminleme
        if 'forecast' in report_config.get('metrics', []):
            forecast_section = {
                'type': 'forecast',
                'title': 'Tahminleme',
                'data': []
            }
            
            for kpi_id in report_config.get('kpi_ids', []):
                kpi = ProcessKpi.query.get(kpi_id)
                if kpi:
                    forecast = AnalyticsService.get_forecast(kpi_id, periods=3)
                    forecast_section['data'].append({
                        'kpi_name': kpi.name,
                        'forecast': forecast
                    })
            
            report_data['sections'].append(forecast_section)
        
        return report_data
    
    @staticmethod
    def schedule_report(
        report_config: Dict,
        schedule: Dict
    ) -> Dict:
        """
        Rapor zamanlama (placeholder)
        
        Args:
            report_config: Rapor konfigürasyonu
            schedule: {
                'frequency': 'daily|weekly|monthly',
                'recipients': ['email1@example.com', 'email2@example.com'],
                'format': 'excel|pdf'
            }
        """
        # TODO: Celery task ile zamanlanmış rapor gönderimi
        return {
            'scheduled': True,
            'frequency': schedule['frequency'],
            'next_run': 'TBD'
        }
