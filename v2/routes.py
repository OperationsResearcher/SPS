# -*- coding: utf-8 -*-
from flask import render_template
from flask_login import login_required, current_user
from . import v2_bp

from datetime import date
from utils.task_status import COMPLETED_STATUSES
from models import Task, Project, Surec, AnaStrateji, AltStrateji, SurecPerformansGostergesi

@v2_bp.route('/masam')
@login_required # Giriş yapmış kullanıcılar görebilsin
def masam():
    """V2 - Kişisel Çalışma Masası"""
    today = date.today()
    
    # Kullanıcının aktif görevlerini getir
    # assignee_id = current_user.id VE status bitmemiş VE arşivlenmemiş
    my_tasks = Task.query.filter(
        Task.assignee_id == current_user.id,
        Task.is_archived == False,
        ~Task.status.in_(COMPLETED_STATUSES)
    ).order_by(Task.due_date.asc()).all()
    
    # İstatistikleri hafızada hesapla (extra DB sorgusu yapmamak için)
    overdue_count = 0
    today_count = 0
    
    for t in my_tasks:
        if t.due_date:
            if t.due_date < today:
                overdue_count += 1
            elif t.due_date == today:
                today_count += 1
                
    return render_template('v2/masam.html', 
                         my_tasks=my_tasks, 
                         overdue_count=overdue_count,
                         today_count=today_count,
                         today=today)

@v2_bp.route('/yonetim')
@login_required
def yonetim():
    """V2 - Yönetim Paneli"""
    # Aktif Projeler (Arşivlenmemiş)
    all_projects = Project.query.filter_by(is_archived=False).all()
    
    # Aktif Süreçler (Silinmemiş)
    active_processes = Surec.query.filter_by(silindi=False).all()
    
    # İstatistikler
    total_projects = len(all_projects)
    # Tamamlanan proje: health_score=100 olanları varsayacağız (status kolonu olmadığı için)
    completed_projects = len([p for p in all_projects if p.health_score == 100])
    
    # Tamamlanma Oranı (Tüm aktif projelerin health_score ortalaması)
    avg_completion = 0
    if total_projects > 0:
        total_score = sum([p.health_score or 0 for p in all_projects])
        avg_completion = int(total_score / total_projects)
        
    process_count = len(active_processes)
    
    return render_template('v2/yonetim.html',
                         all_projects=all_projects,
                         active_processes=active_processes,
                         stats={
                             'total_projects': total_projects,
                             'completed_projects': completed_projects,
                             'avg_completion': avg_completion,
                             'process_count': process_count
                         })

@v2_bp.route('/strateji')
@login_required
def strateji():
    """V2 - Stratejik Planlama ve Kurumsal Karne (BSC)"""
    # 1. Stratejik Amaçları Çek (Ana Stratejiler)
    strategies = AnaStrateji.query.filter_by(kurum_id=current_user.kurum_id).all()
    
    # Eğer strateji yoksa, boş bir liste döndür ama projeleri "Girişim" olarak ele alabiliriz
    # Ancak UI'da strateji kartları istendiği için boş gelebilir.
    
    # 2. KPI İstatistikleri (Tüm Kurum İçin)
    # İlişkili Süreçler üzerinden KPI'lara erişim
    # Surec -> SurecPerformansGostergesi
    all_kpis = SurecPerformansGostergesi.query.join(Surec).filter(Surec.kurum_id == current_user.kurum_id).all()
    
    total_kpis = len(all_kpis)
    successful_kpis = 0
    warning_kpis = 0
    failed_kpis = 0
    
    # KPI İstatistiklerini Hesapla (Basit mantık: puana veya duruma göre)
    for kpi in all_kpis:
        # Örnek mantık: basari_puani üzerinden veya durum alanından
        score = kpi.basari_puani or 0
        if score >= 90:
            successful_kpis += 1
        elif score >= 70:
            warning_kpis += 1
        else:
            failed_kpis += 1
            
    kpi_stats = {
        'total': total_kpis,
        'success': successful_kpis,
        'warning': warning_kpis,
        'fail': failed_kpis,
        'success_rate': int((successful_kpis / total_kpis * 100)) if total_kpis > 0 else 0
    }
    
    # 3. Her Strateji İçin Durum Belirle (Mocking/Calculation)
    # Gerçek hayatta bu veriler alt stratejiler ve KPI'lardan toplanarak hesaplanır.
    strategy_data = []
    
    # Perspektiflere göre gruplama için
    perspectives = {
        'Finansal': [],
        'Müşteri': [],
        'Süreç': [],
        'Öğrenme': []
    }
    
    total_progress_sum = 0
    
    for s in strategies:
        # Alt stratejileri bul
        subs = AltStrateji.query.filter_by(ana_strateji_id=s.id).all()
        
        # Bu stratejiye bağlı KPI sayısı (Alt stratejiler üzerinden)
        # Basitlik adına random/mock yerine varsa gerçek veri, yoksa varsayılan atayalım
        try:
            # Alt stratejilerin bağlı olduğu KPI'ları sayabiliriz (ilişki varsa)
            # Şu an modelde AltStrateji -> backref='performans_gostergeleri' var (surec_performans_gostergesi tablosunda)
            linked_kpis_count = 0
            total_score = 0
            for sub in subs:
                kpis = sub.performans_gostergeleri
                linked_kpis_count += len(kpis)
                for k in kpis:
                    total_score += (k.basari_puani or 0)
            
            avg_score = int(total_score / linked_kpis_count) if linked_kpis_count > 0 else 0
        except:
            avg_score = 0
            
        status_color = 'success' if avg_score >= 80 else 'warning' if avg_score >= 50 else 'danger'
        
        # Strateji nesnesine geçici attribute ekle (template render için)
        s_dict = {
            'obj': s,
            'progress': avg_score, # İlerleme %
            'status_class': status_color,
            'sub_count': len(subs),
            'kpi_count': linked_kpis_count if 'linked_kpis_count' in locals() else 0,
            'responsible': 'Yönetim Kurulu' # Varsayılan sorumlu
        }
        strategy_data.append(s_dict)
        
        # Genel ilerleme için topla
        total_progress_sum += avg_score
        
        # Perspektiflere dağıt (Mapping: Database value -> UI Label)
        # DB'de genelde: FINANSAL, MUSTERI, SUREC, OGRENME tutuluyor olabilir.
        # Basit eşleştirme yapalım
        p_key = s.perspective or 'Diğer'
        if 'FINANS' in p_key.upper(): 
            perspectives['Finansal'].append(s_dict)
        elif 'MUSTERI' in p_key.upper() or 'MÜŞTERİ' in p_key.upper():
            perspectives['Müşteri'].append(s_dict)
        elif 'SUREC' in p_key.upper() or 'SÜREÇ' in p_key.upper():
            perspectives['Süreç'].append(s_dict)
        elif 'OGRENME' in p_key.upper() or 'ÖĞRENME' in p_key.upper() or 'GELISIM' in p_key.upper():
            perspectives['Öğrenme'].append(s_dict)
            
    overall_progress = int(total_progress_sum / len(strategies)) if strategies else 0

    return render_template('v2/strateji.html', 
                         strategies=strategy_data,
                         kpi_stats=kpi_stats,
                         overall_progress=overall_progress,
                         perspectives=perspectives)
