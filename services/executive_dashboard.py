# -*- coding: utf-8 -*-
"""
Executive Dashboard Servisi
Üst yönetim için kurumsal genel bakış ve analitik veriler
"""
from models import db, Project, Task, ProjectRisk, Surec, User
from services.project_analytics import calculate_surec_saglik_skoru
from sqlalchemy import func, and_, or_
from datetime import datetime, date
from flask import current_app


def get_corporate_health_score(kurum_id, filters=None):
    """
    Kurumsal Sağlık Puanı (0-100)
    Tüm aktif projelerin ve süreçlerin sağlık skorlarının ortalaması
    
    Args:
        kurum_id: Kurum ID
        filters: Filtreleme parametreleri (department, manager_id, start_date, end_date)
    """
    try:
        # Filtreleme uygula (arşivlenmiş projeleri hariç tut)
        projects_query = Project.query.filter_by(kurum_id=kurum_id, is_archived=False)
        
        if filters:
            if filters.get('department'):
                projects_query = projects_query.join(User, Project.manager_id == User.id).filter(
                    User.department == filters['department']
                )
            if filters.get('manager_id'):
                projects_query = projects_query.filter(Project.manager_id == filters['manager_id'])
            if filters.get('start_date') and filters.get('end_date'):
                projects_query = projects_query.filter(
                    and_(
                        Project.start_date >= filters['start_date'],
                        Project.end_date <= filters['end_date']
                    )
                )
        
        # Projelerin sağlık skorlarını hesapla
        projects = projects_query.all()
        project_scores = []
        
        # Performans optimizasyonu: Tüm görevleri ve riskleri tek sorguda getir
        project_ids = [p.id for p in projects]
        if project_ids:
            # Tüm görevleri tek sorguda getir (project_id bazlı grupla)
            all_tasks = Task.query.filter(Task.project_id.in_(project_ids)).all()
            tasks_by_project = {}
            for task in all_tasks:
                if task.project_id not in tasks_by_project:
                    tasks_by_project[task.project_id] = []
                tasks_by_project[task.project_id].append(task)
            
            # Tüm riskleri tek sorguda getir
            all_risks = ProjectRisk.query.filter(
                and_(
                    ProjectRisk.project_id.in_(project_ids),
                    ProjectRisk.status == 'Aktif'
                )
            ).all()
            risks_by_project = {}
            for risk in all_risks:
                if risk.project_id not in risks_by_project:
                    risks_by_project[risk.project_id] = []
                risks_by_project[risk.project_id].append(risk)
        else:
            tasks_by_project = {}
            risks_by_project = {}
        
        today = date.today()
        
        for project in projects:
            # Proje sağlık skorunu hesapla (optimize edilmiş)
            project_tasks = tasks_by_project.get(project.id, [])
            total_tasks = len(project_tasks)
            completed_tasks = sum(1 for t in project_tasks if t.status == 'Tamamlandı')
            
            if total_tasks > 0:
                completion_rate = (completed_tasks / total_tasks) * 100
            else:
                completion_rate = 100  # Görev yoksa mükemmel kabul et
            
            # Gecikme kontrolü (optimize edilmiş)
            overdue_tasks = sum(
                1 for t in project_tasks 
                if t.status != 'Tamamlandı' and t.due_date and t.due_date < today
            )
            
            # Risk faktörü (optimize edilmiş)
            project_risks = risks_by_project.get(project.id, [])
            high_risk_count = sum(
                1 for r in project_risks
                if (r.impact * r.probability >= 20) or (r.impact >= 4) or (r.probability >= 4)
            )
            
            # Proje sağlık skoru hesaplama
            project_score = completion_rate
            
            # Gecikme cezası (her gecikmiş görev %5 düşürür, maksimum %30)
            if total_tasks > 0:
                overdue_penalty = min((overdue_tasks / total_tasks) * 30, 30)
                project_score -= overdue_penalty
            
            # Risk cezası (her yüksek risk %5 düşürür, maksimum %20)
            risk_penalty = min(high_risk_count * 5, 20)
            project_score -= risk_penalty
            
            project_score = max(0, min(100, project_score))  # 0-100 arası sınırla
            project_scores.append(project_score)
        
        # Süreçlerin sağlık skorlarını hesapla
        # Filtreleme uygulanmaz (süreçler proje bazlı değil)
        # Not: Süreçler için is_archived kontrolü project_analytics.py'de yapılacak
        surecler = Surec.query.filter_by(kurum_id=kurum_id).all()
        surec_scores = []
        surec_detaylari = []  # Süreç detaylarını sakla (top_etkenler için)
        
        for surec in surecler:
            try:
                skor_sonucu = calculate_surec_saglik_skoru(surec.id)
                if skor_sonucu and 'skor' in skor_sonucu:
                    surec_scores.append(skor_sonucu['skor'])
                    surec_detaylari.append({
                        'surec_id': surec.id,
                        'surec_adi': surec.name,
                        'skor': skor_sonucu['skor'],
                        'top_etkenler': skor_sonucu.get('top_etkenler', [])
                    })
            except Exception as e:
                # Hata durumunda skor hesaplanamazsa atla
                continue
        
        # Tüm skorları birleştir ve ortalama al
        all_scores = project_scores + surec_scores
        
        if len(all_scores) > 0:
            corporate_score = sum(all_scores) / len(all_scores)
        else:
            corporate_score = 100  # Veri yoksa mükemmel kabul et
        
        # Tüm süreçlerin top etkenlerini birleştir ve en çok görünenleri bul
        tum_etkenler = []
        for detay in surec_detaylari:
            for etken in detay.get('top_etkenler', []):
                tum_etkenler.append(etken)
        
        # En çok görünen top 2 etkeni bul (basit bir sayım)
        etken_sayilari = {}
        for etken in tum_etkenler:
            etken_adi = etken.get('etken', '')
            if etken_adi not in etken_sayilari:
                etken_sayilari[etken_adi] = {
                    'etken': etken_adi,
                    'sayi': 0,
                    'toplam_etki': 0.0,
                    'ornek': etken
                }
            etken_sayilari[etken_adi]['sayi'] += 1
            # Etki değerini parse et ve topla
            try:
                etki_degeri = float(etken.get('etki', '0').replace('%', '').replace('-', ''))
                etken_sayilari[etken_adi]['toplam_etki'] += etki_degeri
            except:
                pass
        
        # En çok görünen ve en yüksek etkiye sahip top 2 etkeni seç
        top_etkenler_list = sorted(
            etken_sayilari.values(),
            key=lambda x: (x['sayi'], x['toplam_etki']),
            reverse=True
        )[:2]
        
        # Formatlanmış top etkenler
        formatlanmis_top_etkenler = []
        for etken in top_etkenler_list:
            formatlanmis_top_etkenler.append({
                'etken': etken['etken'],
                'deger': etken['ornek'].get('deger', ''),
                'etki': etken['ornek'].get('etki', ''),
                'sayi': etken['sayi']  # Kaç süreçte görüldü
            })
        
        return {
            'score': round(corporate_score, 2),
            'project_count': len(projects),
            'surec_count': len(surecler),
            'project_scores': project_scores,
            'surec_scores': surec_scores,
            'top_etkenler': formatlanmis_top_etkenler  # En çok puan kıran top 2 etken
        }
    
    except Exception as e:
        return {
            'score': 0,
            'error': str(e),
            'project_count': 0,
            'surec_count': 0
        }


def get_critical_risks(kurum_id, limit=5):
    """
    En kritik 5 riski getir (Optimize edilmiş)
    Risk puanı = impact * probability
    """
    try:
        # Tüm projelerdeki riskleri getir (tek sorgu ile, arşivlenmiş projeler hariç)
        projects = Project.query.filter_by(kurum_id=kurum_id, is_archived=False).with_entities(Project.id).all()
        project_ids = [p.id for p in projects]
        
        if not project_ids:
            return []
        
        # Aktif riskleri getir ve puanla (optimize edilmiş sorgu)
        # joinedload ile ilişkili verileri tek sorguda getir
        from sqlalchemy.orm import joinedload
        risks = ProjectRisk.query.options(
            joinedload(ProjectRisk.project),
            joinedload(ProjectRisk.created_by)
        ).filter(
            and_(
                ProjectRisk.project_id.in_(project_ids),
                ProjectRisk.status == 'Aktif'
            )
        ).all()
        
        # Riskleri puanla ve sırala
        risk_list = []
        for risk in risks:
            risk_score = risk.impact * risk.probability
            risk_list.append({
                'id': risk.id,
                'title': risk.title,
                'description': risk.description,
                'impact': risk.impact,
                'probability': risk.probability,
                'risk_score': risk_score,
                'risk_level': risk.risk_level,
                'project_id': risk.project_id,
                'project_name': risk.project.name if risk.project else 'Bilinmiyor',
                'mitigation_plan': risk.mitigation_plan,
                'created_by': f"{risk.created_by.first_name} {risk.created_by.last_name}" if risk.created_by else 'Bilinmiyor',
                'created_at': risk.created_at.isoformat() if risk.created_at else None
            })
        
        # Risk puanına göre sırala (yüksekten düşüğe)
        risk_list.sort(key=lambda x: x['risk_score'], reverse=True)
        
        # İlk N riski döndür
        return risk_list[:limit]
    
    except Exception as e:
        return []


def get_planning_efficiency(kurum_id):
    """
    Planlama Verimliliği Analizi
    Proje bazlı: estimated_time vs actual_time karşılaştırması
    """
    try:
        projects = Project.query.filter_by(kurum_id=kurum_id, is_archived=False).all()
        project_data = []
        
        for project in projects:
            # Tamamlanan görevleri getir
            completed_tasks = Task.query.filter_by(
                project_id=project.id,
                status='Tamamlandı'
            ).filter(
                and_(
                    Task.estimated_time.isnot(None),
                    Task.actual_time.isnot(None),
                    Task.estimated_time > 0
                )
            ).all()
            
            if not completed_tasks:
                continue
            
            total_estimated = sum(task.estimated_time for task in completed_tasks)
            total_actual = sum(task.actual_time for task in completed_tasks)
            
            # Sapma yüzdesi (pozitif = fazla süre, negatif = az süre)
            if total_estimated > 0:
                deviation_percent = ((total_actual - total_estimated) / total_estimated) * 100
            else:
                deviation_percent = 0
            
            project_data.append({
                'project_id': project.id,
                'project_name': project.name,
                'task_count': len(completed_tasks),
                'estimated_time': round(total_estimated, 2),
                'actual_time': round(total_actual, 2),
                'deviation_percent': round(deviation_percent, 2),
                'efficiency': 'İyi' if deviation_percent <= 10 else ('Orta' if deviation_percent <= 25 else 'Kötü')
            })
        
        # Sapma yüzdesine göre sırala (en kötüden en iyiye)
        project_data.sort(key=lambda x: x['deviation_percent'], reverse=True)
        
        return project_data
    
    except Exception as e:
        return []


def get_task_workload_distribution(kurum_id):
    """
    Bekleyen İş Yükü Dağılımı
    Açık görevlerin durumlarına göre dağılımı
    """
    try:
        projects = Project.query.filter_by(kurum_id=kurum_id).all()
        project_ids = [p.id for p in projects]
        
        if not project_ids:
            return {}
        
        # Açık görevleri durumlarına göre grupla
        tasks = Task.query.filter(
            and_(
                Task.project_id.in_(project_ids),
                Task.status != 'Tamamlandı'
            )
        ).all()
        
        status_distribution = {}
        for task in tasks:
            status = task.status or 'Belirtilmemiş'
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        # Türkçe durum isimleri için mapping
        status_labels = {
            'Yapılacak': 'Yapılacak',
            'Devam Ediyor': 'Devam Ediyor',
            'Beklemede': 'Beklemede',
            'Test': 'Test',
            'İnceleme': 'İnceleme',
            'Belirtilmemiş': 'Belirtilmemiş'
        }
        
        # Formatlanmış veri
        formatted_data = []
        for status, count in status_distribution.items():
            formatted_data.append({
                'status': status_labels.get(status, status),
                'count': count,
                'percentage': round((count / len(tasks)) * 100, 2) if tasks else 0
            })
        
        # Sayıya göre sırala
        formatted_data.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            'total_tasks': len(tasks),
            'distribution': formatted_data
        }
    
    except Exception as e:
        return {
            'total_tasks': 0,
            'distribution': []
        }


def get_personnel_workload_analysis(kurum_id):
    """
    Personel Yükü Analizi - Aktif görevleri olan personellerin görev sayısı
    Hangi birim/kişi darboğazda? sorusuna yanıt verir
    
    Returns:
        {
            'by_user': [{'user_id': 1, 'user_name': '...', 'task_count': 5, 'department': '...'}, ...],
            'by_department': {'IT': 15, 'İnsan Kaynakları': 8, ...}
        }
    """
    try:
        # Arşivlenmemiş projeler
        projects = Project.query.filter_by(kurum_id=kurum_id, is_archived=False).all()
        project_ids = [p.id for p in projects]
        
        if not project_ids:
            return {
                'by_user': [],
                'by_department': {}
            }
        
        # Aktif görevleri olan kullanıcılar (arşivlenmemiş görevler)
        task_counts = db.session.query(
            Task.assigned_to_id,
            func.count(Task.id).label('task_count')
        ).filter(
            Task.project_id.in_(project_ids),
            Task.status.in_(['Yapılacak', 'Devam Ediyor', 'Beklemede']),
            Task.is_archived == False,
            Task.assigned_to_id.isnot(None)
        ).group_by(Task.assigned_to_id).all()
        
        # Kullanıcı bazlı analiz
        by_user = []
        for user_id, task_count in task_counts:
            user = User.query.get(user_id)
            if user:
                by_user.append({
                    'user_id': user_id,
                    'user_name': f'{user.first_name} {user.last_name}',
                    'task_count': task_count,
                    'department': user.department or 'Belirtilmemiş'
                })
        
        # Departman bazlı analiz
        by_department = {}
        for item in by_user:
            dept = item['department']
            if dept not in by_department:
                by_department[dept] = 0
            by_department[dept] += item['task_count']
        
        # Kullanıcıları görev sayısına göre sırala (en çok görevi olan üstte)
        by_user.sort(key=lambda x: x['task_count'], reverse=True)
        
        return {
            'by_user': by_user[:20],  # En fazla 20 kullanıcı göster
            'by_department': by_department
        }
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Personel yükü analizi hatası: {e}')
        return {
            'by_user': [],
            'by_department': {}
        }


def get_executive_summary(kurum_id):
    """
    AI Destekli Yönetici Özeti
    
    Args:
        kurum_id: Kurum ID
    
    Returns:
        str: Özet metin
    """
    try:
        from services.ai_executive_summary import generate_executive_summary
        summary = generate_executive_summary(kurum_id)
        return summary
    except Exception as e:
        return "Özet oluşturulurken bir hata oluştu."






















