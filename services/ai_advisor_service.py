# -*- coding: utf-8 -*-
"""
AI Stratejik Danışman Servisi
Tüm sistem verilerini sentezleyerek stratejik tavsiyeler üretir
"""
from datetime import date, datetime, timedelta
from flask import current_app
from models import (
    db, Project, Task, ProjectRisk, Surec, User,
    PerformansGostergeVeri, BireyselPerformansGostergesi, Notification
)
from sqlalchemy import and_, or_, func
from services.executive_dashboard import (
    get_corporate_health_score, get_critical_risks,
    get_personnel_workload_analysis
)
from services.project_analytics import calculate_surec_saglik_skoru


def generate_strategic_advice(kurum_id):
    """
    AI Stratejik Danışman - Tüm sistem verilerini analiz ederek tavsiyeler üretir
    
    Args:
        kurum_id: Kurum ID
    
    Returns:
        dict: {
            'system_summary': {...},
            'highlighted_risks': [...],
            'ai_recommendations': [...]
        }
    """
    try:
        # 1. Sistem Özeti
        system_summary = _generate_system_summary(kurum_id)
        
        # 2. Öne Çıkan Riskler
        highlighted_risks = _get_highlighted_risks(kurum_id)
        
        # 3. AI Tavsiyeleri
        ai_recommendations = _generate_ai_recommendations(kurum_id, system_summary, highlighted_risks)
        
        return {
            'system_summary': system_summary,
            'highlighted_risks': highlighted_risks,
            'ai_recommendations': ai_recommendations,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f'AI danışman analizi hatası: {e}', exc_info=True)
        return {
            'system_summary': {'error': str(e)},
            'highlighted_risks': [],
            'ai_recommendations': [],
            'generated_at': datetime.utcnow().isoformat()
        }


def simulate_what_if(kurum_id, simulation_params):
    """
    What-If Simülasyon Motoru
    Yönetici, bir projenin bitiş tarihini veya bir PG'nin gerçekleşen değerini 
    "sanal olarak" değiştirdiğinde, Süreç Sağlık Skorunun nasıl etkileneceğini hesaplar.
    
    Args:
        kurum_id: Kurum ID
        simulation_params: {
            'type': 'project_end_date' | 'pg_value' | 'risk_probability',
            'project_id': int (project_end_date için),
            'pg_id': int (pg_value için),
            'new_value': float/date (yeni değer),
            'risk_id': int (risk_probability için),
            'new_probability': int (risk_probability için)
        }
    
    Returns:
        dict: {
            'original_score': float,
            'simulated_score': float,
            'impact': float,  # Değişim miktarı
            'impact_percentage': float,  # Yüzde değişim
            'affected_processes': [...],
            'recommendations': [...]
        }
    """
    try:
        from services.project_analytics import calculate_surec_saglik_skoru
        from services.executive_dashboard import get_corporate_health_score
        
        # 1. Orijinal durumu hesapla
        original_health = get_corporate_health_score(kurum_id)
        original_score = original_health.get('score', 0)
        
        # 2. Simülasyon tipine göre işlem yap
        sim_type = simulation_params.get('type')
        
        if sim_type == 'project_end_date':
            # Proje bitiş tarihi simülasyonu
            project_id = simulation_params.get('project_id')
            new_end_date = simulation_params.get('new_value')
            
            if not project_id or not new_end_date:
                return {'error': 'project_id ve new_value (tarih) gerekli'}
            
            # Projeyi geçici olarak güncelle (simülasyon için)
            project = Project.query.get(project_id)
            if not project:
                return {'error': 'Proje bulunamadı'}
            
            original_end_date = project.end_date
            project.end_date = new_end_date if isinstance(new_end_date, date) else datetime.strptime(new_end_date, '%Y-%m-%d').date()
            
            # İlişkili süreçleri bul
            affected_processes = []
            if hasattr(project, 'related_processes'):
                for surec in project.related_processes:
                    affected_processes.append({
                        'id': surec.id,
                        'ad': surec.ad,
                        'original_score': calculate_surec_saglik_skoru(surec.id),
                        'simulated_score': None  # Simülasyon sonrası hesaplanacak
                    })
            
            # Simüle edilmiş skoru hesapla
            simulated_health = get_corporate_health_score(kurum_id)
            simulated_score = simulated_health.get('score', 0)
            
            # Projeyi geri al
            project.end_date = original_end_date
            db.session.commit()
            
        elif sim_type == 'pg_value':
            # PG gerçekleşen değer simülasyonu
            pg_id = simulation_params.get('pg_id')
            new_value = simulation_params.get('new_value')
            
            if not pg_id or new_value is None:
                return {'error': 'pg_id ve new_value gerekli'}
            
            # PG verisini bul (en son veri)
            pg_veri = PerformansGostergeVeri.query.filter_by(pg_id=pg_id).order_by(
                PerformansGostergeVeri.veri_tarihi.desc()
            ).first()
            
            if not pg_veri:
                return {'error': 'PG verisi bulunamadı'}
            
            # Orijinal değeri sakla
            original_value = pg_veri.gerceklesen_deger
            
            # Simüle et
            pg_veri.gerceklesen_deger = str(new_value)
            
            # İlişkili süreç skorunu hesapla
            bireysel_pg = BireyselPerformansGostergesi.query.get(pg_id)
            affected_processes = []
            if bireysel_pg and bireysel_pg.kaynak_surec_pg_id:
                surec_pg = SurecPerformansGostergesi.query.get(bireysel_pg.kaynak_surec_pg_id)
                if surec_pg:
                    surec = Surec.query.get(surec_pg.surec_id)
                    if surec:
                        original_surec_result = calculate_surec_saglik_skoru(surec.id)
                        original_surec_score = original_surec_result.get('skor', 0) if isinstance(original_surec_result, dict) else (original_surec_result if isinstance(original_surec_result, (int, float)) else 0)
                        # Simüle edilmiş skor (yeniden hesapla)
                        simulated_surec_result = calculate_surec_saglik_skoru(surec.id)
                        simulated_surec_score = simulated_surec_result.get('skor', 0) if isinstance(simulated_surec_result, dict) else (simulated_surec_result if isinstance(simulated_surec_result, (int, float)) else 0)
                        affected_processes.append({
                            'id': surec.id,
                            'ad': surec.name if hasattr(surec, 'name') else surec.ad,
                            'original_score': original_surec_score,
                            'simulated_score': simulated_surec_score
                        })
            
            # Simüle edilmiş kurumsal skor
            simulated_health = get_corporate_health_score(kurum_id)
            simulated_score = simulated_health.get('score', 0)
            
            # Geri al
            pg_veri.gerceklesen_deger = original_value
            db.session.commit()
            
        elif sim_type == 'risk_probability':
            # Risk olasılığı simülasyonu
            risk_id = simulation_params.get('risk_id')
            new_probability = simulation_params.get('new_probability')
            
            if not risk_id or new_probability is None:
                return {'error': 'risk_id ve new_probability gerekli'}
            
            risk = ProjectRisk.query.get(risk_id)
            if not risk:
                return {'error': 'Risk bulunamadı'}
            
            original_probability = risk.probability
            risk.probability = new_probability
            
            # İlişkili proje ve süreçleri bul
            project = risk.project
            affected_processes = []
            if project and hasattr(project, 'related_processes'):
                for surec in project.related_processes:
                    original_score = calculate_surec_saglik_skoru(surec.id)
                    simulated_score = calculate_surec_saglik_skoru(surec.id)  # Risk faktörü değişti
                    affected_processes.append({
                        'id': surec.id,
                        'ad': surec.ad,
                        'original_score': original_score,
                        'simulated_score': simulated_score
                    })
            
            simulated_health = get_corporate_health_score(kurum_id)
            simulated_score = simulated_health.get('score', 0)
            
            # Geri al
            risk.probability = original_probability
            db.session.commit()
            
        else:
            return {'error': f'Bilinmeyen simülasyon tipi: {sim_type}'}
        
        # 3. Etki analizi
        impact = simulated_score - original_score
        impact_percentage = (impact / original_score * 100) if original_score > 0 else 0
        
        # 4. Öneriler
        recommendations = []
        if impact < -5:
            recommendations.append({
                'severity': 'high',
                'message': 'Bu değişiklik kurumsal sağlık skorunu önemli ölçüde düşürecek. Dikkatli olunmalı.'
            })
        elif impact > 5:
            recommendations.append({
                'severity': 'positive',
                'message': 'Bu değişiklik kurumsal sağlık skorunu artıracak. Önerilir.'
            })
        
        return {
            'original_score': round(original_score, 2),
            'simulated_score': round(simulated_score, 2),
            'impact': round(impact, 2),
            'impact_percentage': round(impact_percentage, 2),
            'affected_processes': affected_processes,
            'recommendations': recommendations,
            'simulation_type': sim_type,
            'simulated_at': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f'What-If simülasyon hatası: {e}', exc_info=True)
        return {
            'error': str(e),
            'original_score': 0,
            'simulated_score': 0,
            'impact': 0,
            'impact_percentage': 0
        }


def _generate_system_summary(kurum_id):
    """Sistem genel durum özeti"""
    try:
        # Kurumsal sağlık skoru
        health_data = get_corporate_health_score(kurum_id)
        corporate_score = health_data.get('score', 0)
        
        # Proje sayıları
        total_projects = Project.query.filter_by(kurum_id=kurum_id, is_archived=False).count()
        active_projects = Project.query.filter_by(kurum_id=kurum_id, is_archived=False).count()
        
        # Görev durumları
        project_ids = [p.id for p in Project.query.filter_by(kurum_id=kurum_id, is_archived=False).all()]
        if project_ids:
            total_tasks = Task.query.filter(
                Task.project_id.in_(project_ids),
                Task.is_archived == False
            ).count()
            completed_tasks = Task.query.filter(
                Task.project_id.in_(project_ids),
                Task.status == 'Tamamlandı',
                Task.is_archived == False
            ).count()
            overdue_tasks = Task.query.filter(
                Task.project_id.in_(project_ids),
                Task.status != 'Tamamlandı',
                Task.due_date < date.today(),
                Task.is_archived == False
            ).count()
        else:
            total_tasks = 0
            completed_tasks = 0
            overdue_tasks = 0
        
        # Risk sayıları
        if project_ids:
            total_risks = ProjectRisk.query.filter(
                ProjectRisk.project_id.in_(project_ids),
                ProjectRisk.status == 'Aktif'
            ).count()
            critical_risks = ProjectRisk.query.filter(
                ProjectRisk.project_id.in_(project_ids),
                ProjectRisk.status == 'Aktif'
            ).filter(
                or_(
                    ProjectRisk.impact * ProjectRisk.probability >= 20,
                    ProjectRisk.impact >= 4,
                    ProjectRisk.probability >= 4
                )
            ).count()
        else:
            total_risks = 0
            critical_risks = 0
        
        # PG sapma sayısı (son 30 gün içinde)
        # NOT: veri_tarihi bazlı sorgulama yapıyoruz (created_at yerine)
        # Çünkü geçmiş tarihli görevler için veri oluşturulduğunda veri_tarihi geçmiş olabilir
        thirty_days_ago = date.today() - timedelta(days=30)
        pg_deviations = db.session.query(PerformansGostergeVeri).join(
            BireyselPerformansGostergesi
        ).filter(
            BireyselPerformansGostergesi.user_id.in_(
                db.session.query(User.id).filter_by(kurum_id=kurum_id).subquery()
            ),
            PerformansGostergeVeri.gerceklesen_deger.isnot(None),
            PerformansGostergeVeri.hedef_deger.isnot(None),
            # Hem created_at hem de veri_tarihi kontrolü yap (yeni oluşturulan veya güncel veriler)
            or_(
                PerformansGostergeVeri.created_at >= datetime.combine(thirty_days_ago, datetime.min.time()),
                PerformansGostergeVeri.veri_tarihi >= thirty_days_ago
            )
        ).all()
        
        pg_deviation_count = 0
        for pg_veri in pg_deviations:
            try:
                gerceklesen = float(pg_veri.gerceklesen_deger)
                hedef = float(pg_veri.hedef_deger)
                if hedef > 0:
                    sapma = ((gerceklesen - hedef) / hedef) * 100
                    if sapma <= -10:  # %10 ve daha fazla altında
                        pg_deviation_count += 1
            except (ValueError, TypeError):
                continue
        
        # Durum değerlendirmesi
        if corporate_score >= 75:
            overall_status = 'İyi'
            status_color = 'success'
        elif corporate_score >= 50:
            overall_status = 'Orta'
            status_color = 'warning'
        else:
            overall_status = 'Kritik'
            status_color = 'danger'
        
        return {
            'corporate_health_score': round(corporate_score, 2),
            'overall_status': overall_status,
            'status_color': status_color,
            'total_projects': total_projects,
            'active_projects': active_projects,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks,
            'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2),
            'total_risks': total_risks,
            'critical_risks': critical_risks,
            'pg_deviations': pg_deviation_count
        }
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Sistem özeti oluşturma hatası: {e}')
        return {'error': str(e)}


def _get_highlighted_risks(kurum_id):
    """Öne çıkan riskleri getir"""
    try:
        critical_risks = get_critical_risks(kurum_id, limit=5)
        
        highlighted = []
        for risk in critical_risks:
            highlighted.append({
                'id': risk['id'],
                'title': risk['title'],
                'description': risk.get('description', '')[:200] + '...' if risk.get('description', '') else '',
                'risk_score': risk['risk_score'],
                'risk_level': risk['risk_level'],
                'project_id': risk['project_id'],
                'project_name': risk['project_name'],
                'impact': risk['impact'],
                'probability': risk['probability'],
                'mitigation_plan': risk.get('mitigation_plan', '')
            })
        
        return highlighted
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Öne çıkan riskler hatası: {e}')
        return []


def _generate_ai_recommendations(kurum_id, system_summary, highlighted_risks):
    """AI tavsiyeleri üret"""
    try:
        recommendations = []
        
        # 1. Kurumsal sağlık skoru bazlı tavsiyeler
        corporate_score = system_summary.get('corporate_health_score', 0)
        if corporate_score < 50:
            recommendations.append({
                'id': f'rec_{len(recommendations) + 1}',
                'type': 'critical',
                'title': 'Kurumsal Sağlık Skoru Düşük',
                'description': f'Kurumsal sağlık skorunuz {corporate_score:.1f} seviyesinde. Bu kritik bir seviyedir ve acil müdahale gerektirir.',
                'action': 'review_all_projects',
                'action_label': 'Tüm Projeleri İncele',
                'action_url': '/projeler',
                'priority': 'high'
            })
        elif corporate_score < 75:
            recommendations.append({
                'id': f'rec_{len(recommendations) + 1}',
                'type': 'warning',
                'title': 'Kurumsal Sağlık Skoru İyileştirilebilir',
                'description': f'Kurumsal sağlık skorunuz {corporate_score:.1f} seviyesinde. İyileştirme için önlemler alınması önerilir.',
                'action': 'review_projects',
                'action_label': 'Projeleri İncele',
                'action_url': '/projeler',
                'priority': 'medium'
            })
        
        # 2. Gecikmiş görevler bazlı tavsiyeler
        overdue_tasks = system_summary.get('overdue_tasks', 0)
        if overdue_tasks > 5:
            recommendations.append({
                'id': f'rec_{len(recommendations) + 1}',
                'type': 'critical',
                'title': f'{overdue_tasks} Gecikmiş Görev Var',
                'description': f'{overdue_tasks} adet gecikmiş görev tespit edildi. Bu görevlerin acilen ele alınması ve kaynak aktarımı yapılması önerilir.',
                'action': 'review_overdue_tasks',
                'action_label': 'Gecikmiş Görevleri İncele',
                'action_url': '/projeler?filter=overdue',
                'priority': 'high'
            })
        elif overdue_tasks > 0:
            recommendations.append({
                'id': f'rec_{len(recommendations) + 1}',
                'type': 'warning',
                'title': f'{overdue_tasks} Gecikmiş Görev',
                'description': f'{overdue_tasks} adet gecikmiş görev var. Bu görevlerin takibi yapılmalıdır.',
                'action': 'review_overdue_tasks',
                'action_label': 'Gecikmiş Görevleri İncele',
                'action_url': '/projeler?filter=overdue',
                'priority': 'medium'
            })
        
        # 3. Kritik riskler bazlı tavsiyeler
        critical_risks_count = system_summary.get('critical_risks', 0)
        if critical_risks_count > 3:
            recommendations.append({
                'id': f'rec_{len(recommendations) + 1}',
                'type': 'critical',
                'title': f'{critical_risks_count} Kritik Risk Tespit Edildi',
                'description': f'{critical_risks_count} adet kritik risk tespit edildi. Bu risklerin acilen yönetilmesi ve azaltılması gerekmektedir.',
                'action': 'review_risks',
                'action_label': 'Riskleri İncele',
                'action_url': '/dashboard/executive',
                'priority': 'high'
            })
        elif critical_risks_count > 0:
            recommendations.append({
                'id': f'rec_{len(recommendations) + 1}',
                'type': 'warning',
                'title': f'{critical_risks_count} Kritik Risk',
                'description': f'{critical_risks_count} adet kritik risk var. Bu risklerin yönetim planlarının gözden geçirilmesi önerilir.',
                'action': 'review_risks',
                'action_label': 'Riskleri İncele',
                'action_url': '/dashboard/executive',
                'priority': 'medium'
            })
        
        # 4. PG sapmaları bazlı tavsiyeler
        pg_deviations = system_summary.get('pg_deviations', 0)
        if pg_deviations > 5:
            recommendations.append({
                'id': f'rec_{len(recommendations) + 1}',
                'type': 'warning',
                'title': f'{pg_deviations} Performans Sapması Tespit Edildi',
                'description': f'Son 30 günde {pg_deviations} adet performans göstergesi hedefin %10 altında gerçekleşti. Süreç performanslarının gözden geçirilmesi önerilir.',
                'action': 'review_pg_deviations',
                'action_label': 'PG Sapmalarını İncele',
                'action_url': '/surec/karne',
                'priority': 'medium'
            })
        
        # 5. Proje-süreç ilişkisi bazlı tavsiyeler
        recommendations.extend(_analyze_project_process_relationships(kurum_id))
        
        # 6. Kaynak dağılımı bazlı tavsiyeler
        recommendations.extend(_analyze_resource_distribution(kurum_id))
        
        # Önceliğe göre sırala (high -> medium -> low)
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        recommendations.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 1), reverse=True)
        
        return recommendations[:10]  # En fazla 10 tavsiye
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f'AI tavsiyeleri oluşturma hatası: {e}')
        return []


def _analyze_project_process_relationships(kurum_id):
    """Proje-süreç ilişkilerini analiz et ve tavsiyeler üret"""
    recommendations = []
    
    try:
        # Tüm süreçleri getir
        surecler = Surec.query.filter_by(kurum_id=kurum_id).all()
        
        for surec in surecler:
            # Süreç sağlık skorunu hesapla
            skor_sonucu = calculate_surec_saglik_skoru(surec.id)
            if not skor_sonucu or 'skor' not in skor_sonucu:
                continue
            
            surec_skoru = skor_sonucu['skor']
            
            # Süreç skoru düşükse ve bağlı projeler varsa
            if surec_skoru < 60:
                from models import project_related_processes
                bagli_proje_ids = db.session.query(project_related_processes.c.project_id).filter(
                    project_related_processes.c.surec_id == surec.id
                ).all()
                bagli_proje_ids = [row[0] for row in bagli_proje_ids]
                
                if bagli_proje_ids:
                    # Bağlı projelerin durumunu kontrol et
                    bagli_projeler = Project.query.filter(
                        Project.id.in_(bagli_proje_ids),
                        Project.is_archived == False
                    ).all()
                    
                    for proje in bagli_projeler:
                        # Proje görevlerini kontrol et
                        proje_gorevleri = Task.query.filter_by(
                            project_id=proje.id,
                            is_archived=False
                        ).all()
                        
                        geciken_gorevler = [t for t in proje_gorevleri 
                                          if t.status != 'Tamamlandı' and t.due_date and t.due_date < date.today()]
                        
                        if len(geciken_gorevler) > 2:
                            recommendations.append({
                                'id': f'rec_process_{surec.id}_{proje.id}',
                                'type': 'warning',
                                'title': f'{surec.name} Sürecindeki Performans Düşüşü',
                                'description': f'"{surec.name}" sürecindeki performans düşüşü ({surec_skoru:.1f} skor) "{proje.name}" projesindeki {len(geciken_gorevler)} gecikmiş görevden kaynaklanıyor olabilir. Kaynak aktarımı önerilir.',
                                'action': 'review_project',
                                'action_label': 'Projeyi İncele',
                                'action_url': f'/projeler/{proje.id}',
                                'priority': 'medium',
                                'related_process_id': surec.id,
                                'related_project_id': proje.id
                            })
                            break  # Her süreç için bir tavsiye yeter
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Proje-süreç ilişkisi analizi hatası: {e}')
    
    return recommendations


def _analyze_resource_distribution(kurum_id):
    """Kaynak dağılımını analiz et ve tavsiyeler üret"""
    recommendations = []
    
    try:
        workload_data = get_personnel_workload_analysis(kurum_id)
        
        # En yüklü kullanıcıları bul
        by_user = workload_data.get('by_user', [])
        if by_user:
            max_tasks = by_user[0].get('task_count', 0)
            avg_tasks = sum(u.get('task_count', 0) for u in by_user) / len(by_user) if by_user else 0
            
            # Eğer en yüklü kullanıcı ortalamanın 2 katından fazla göreve sahipse
            if max_tasks > avg_tasks * 2 and max_tasks > 10:
                top_user = by_user[0]
                recommendations.append({
                    'id': f'rec_resource_{top_user.get("user_id")}',
                    'type': 'warning',
                    'title': 'Kaynak Dağılımı Dengesiz',
                    'description': f'{top_user.get("user_name")} kullanıcısı {max_tasks} aktif göreve sahip (ortalama: {avg_tasks:.1f}). Görev dağılımının yeniden dengelenmesi önerilir.',
                    'action': 'review_workload',
                    'action_label': 'Yük Dağılımını İncele',
                    'action_url': '/dashboard/executive',
                    'priority': 'medium',
                    'related_user_id': top_user.get('user_id')
                })
        
        # Departman bazlı dengesizlik
        by_department = workload_data.get('by_department', {})
        if len(by_department) > 1:
            dept_values = list(by_department.values())
            max_dept = max(dept_values)
            min_dept = min(dept_values)
            
            if max_dept > min_dept * 3 and max_dept > 15:
                max_dept_name = [k for k, v in by_department.items() if v == max_dept][0]
                recommendations.append({
                    'id': f'rec_dept_{max_dept_name}',
                    'type': 'info',
                    'title': 'Departman Yükü Dengesiz',
                    'description': f'"{max_dept_name}" departmanı {max_dept} aktif göreve sahip. Departmanlar arası kaynak aktarımı değerlendirilebilir.',
                    'action': 'review_department_workload',
                    'action_label': 'Departman Yükünü İncele',
                    'action_url': '/dashboard/executive',
                    'priority': 'low'
                })
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Kaynak dağılımı analizi hatası: {e}')
    
    return recommendations


def notify_recommendation(recommendation_id, target_user_id=None, target_role=None):
    """
    Tavsiyeyi ilgili sorumluya bildir
    
    Args:
        recommendation_id: Tavsiye ID
        target_user_id: Belirli bir kullanıcıya gönder (opsiyonel)
        target_role: Belirli bir role gönder (opsiyonel, örn: 'ust_yonetim')
    """
    try:
        # Bu fonksiyon ileride genişletilebilir
        # Şimdilik sadece log
        if current_app:
            current_app.logger.info(f'Tavsiye bildirimi: {recommendation_id}, Target: {target_user_id or target_role}')
        
        return True
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Tavsiye bildirimi hatası: {e}')
        return False





















