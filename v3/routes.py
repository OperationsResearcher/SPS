from flask import render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.dashboard import UserDashboardSettings
from models import Task, Note, Project, Surec, Notification, BireyselPerformansGostergesi, PerformansGostergeVeri
import json
from datetime import date, timedelta, datetime

# Blueprint'i __init__.py'den import et (tekrar tanımlama!)
from . import v3_bp

def calculate_strategic_summary(user):
    """
    Stratejik Özet Hesaplama
    Kullanıcının erişebildiği tüm projelerin sağlık durumunu ve kritik riskleri hesaplar.
    """
    today = date.today()
    three_days_ago = today - timedelta(days=3)
    
    # Kullanıcının dahil olduğu projeler (yönetici, üye veya gözlemci)
    user_projects = Project.query.filter(
        db.or_(
            Project.manager_id == user.id,
            Project.members.any(id=user.id),
            Project.observers.any(id=user.id)
        ),
        Project.is_archived == False
    ).all()
    
    # 1. GENEL SAĞLIK SKORU HESAPLAMA
    if not user_projects:
        health_score = 100  # Proje yoksa varsayılan sağlıklı
        health_status = "Mükemmel"
        health_color = "success"
    else:
        # Proje bazlı sağlık skorları
        project_scores = []
        
        for project in user_projects:
            # Eğer health_score alanı varsa kullan
            if hasattr(project, 'health_score') and project.health_score is not None:
                project_scores.append(project.health_score)
            else:
                # Dinamik hesaplama: Görev tamamlanma oranına göre
                total_tasks = Task.query.filter_by(project_id=project.id, is_archived=False).count()
                if total_tasks > 0:
                    completed_tasks = Task.query.filter_by(
                        project_id=project.id,
                        is_archived=False
                    ).filter(Task.status.in_(['Tamamlandı', 'Completed'])).count()
                    
                    overdue_tasks = Task.query.filter(
                        Task.project_id == project.id,
                        Task.is_archived == False,
                        Task.due_date < today,
                        Task.status.notin_(['Tamamlandı', 'Completed'])
                    ).count()
                    
                    # Skor hesaplama: Tamamlanma oranı - Gecikme cezası
                    completion_rate = (completed_tasks / total_tasks) * 100
                    overdue_penalty = (overdue_tasks / total_tasks) * 30  # Her gecikmiş görev -30 puan
                    
                    project_score = max(0, min(100, completion_rate - overdue_penalty))
                    project_scores.append(project_score)
                else:
                    project_scores.append(100)  # Görev yoksa sağlıklı sayılır
        
        # Ortalama skor
        health_score = int(sum(project_scores) / len(project_scores)) if project_scores else 100
        
        # Durum ve renk belirleme
        if health_score >= 80:
            health_status = "Mükemmel"
            health_color = "success"
        elif health_score >= 50:
            health_status = "İyi"
            health_color = "warning"
        else:
            health_status = "Dikkat!"
            health_color = "danger"
    
    # 2. KRİTİK RİSKLER (ALERTS)
    alerts = []
    
    for project in user_projects:
        # Risk 1: Gecikmiş görevler
        overdue_tasks = Task.query.filter(
            Task.project_id == project.id,
            Task.is_archived == False,
            Task.due_date < today,
            Task.status.notin_(['Tamamlandı', 'Completed'])
        ).count()
        
        if overdue_tasks > 0:
            alerts.append({
                'type': 'danger',
                'icon': 'fa-exclamation-triangle',
                'message': f"{project.name}: {overdue_tasks} görev gecikmiş",
                'action_url': f'/projects/{project.id}'
            })
        
        # Risk 2: Bugün biten görevler
        due_today = Task.query.filter(
            Task.project_id == project.id,
            Task.is_archived == False,
            Task.due_date == today,
            Task.status.notin_(['Tamamlandı', 'Completed'])
        ).count()
        
        if due_today > 0:
            alerts.append({
                'type': 'warning',
                'icon': 'fa-clock',
                'message': f"{project.name}: {due_today} görev bugün bitiyor",
                'action_url': f'/projects/{project.id}'
            })
        
        # Risk 3: Son 3 günde aktivite yok (Duraklama)
        recent_activity = Task.query.filter(
            Task.project_id == project.id,
            Task.created_at >= three_days_ago
        ).count()
        
        recent_updates = Task.query.filter(
            Task.project_id == project.id,
            Task.completed_at >= three_days_ago
        ).count()
        
        if recent_activity == 0 and recent_updates == 0:
            total_tasks = Task.query.filter_by(project_id=project.id, is_archived=False).count()
            if total_tasks > 0:  # Sadece aktif görevi olan projelerde uyar
                alerts.append({
                    'type': 'info',
                    'icon': 'fa-pause-circle',
                    'message': f"{project.name}: Son 3 gündür aktivite yok",
                    'action_url': f'/projects/{project.id}'
                })
    
    # Uyarıları önceliğe göre sırala (danger > warning > info)
    priority_order = {'danger': 0, 'warning': 1, 'info': 2}
    alerts.sort(key=lambda x: priority_order.get(x['type'], 3))
    
    # En fazla 5 uyarı göster
    alerts = alerts[:5]
    
    return {
        'health_score': health_score,
        'health_status': health_status,
        'health_color': health_color,
        'alerts': alerts,
        'total_projects': len(user_projects)
    }


@v3_bp.route('/dashboard')
@login_required
def dashboard():
    """V3 Dashboard ana sayfası - Kapsayıcı tarih filtreleme mantığı ile"""
    
    # 1. Kullanıcı ayarlarını yükle
    settings = UserDashboardSettings.query.filter_by(user_id=current_user.id).first()
    
    # Varsayılan widget düzeni
    default_layout = [
        {"id": "widget-actions", "visible": True},
        {"id": "widget-2", "visible": True},
        {"id": "widget-3", "visible": True},
        {"id": "widget-4", "visible": True},
        {"id": "widget-5", "visible": True},
        {"id": "widget-notifications", "visible": True},
        {"id": "widget-quick-data", "visible": True},
        {"id": "widget-processes", "visible": True},
        {"id": "widget-projects", "visible": True},
    ]

    layout_config = default_layout
    if settings and settings.layout_config:
        try:
            saved_layout = json.loads(settings.layout_config)
            saved_ids = [w.get('id') for w in saved_layout]
            
            # Eski widget'ları yenilerine çevir
            needs_update = False
            for w in saved_layout:
                if w['id'] == 'widget-6': 
                    w['id'] = 'widget-notifications'
                    needs_update = True
                if w['id'] == 'widget-7': 
                    w['id'] = 'widget-quick-data'
                    needs_update = True
                if w['id'] == 'widget-1':
                    w['id'] = 'widget-actions'
                    needs_update = True
            
            # Tanımlanmamış eski widget'ları temizle (örn: widget-9)
            saved_layout = [w for w in saved_layout if w.get('id') != 'widget-9']
            
            # Yeni widgetları ekle
            current_ids = [w.get('id') for w in saved_layout]
            for widget in default_layout:
                if widget['id'] not in current_ids:
                    # Eski isimleriyle var mı kontrol et
                    is_renamed_6 = (widget['id'] == 'widget-notifications' and 'widget-6' in current_ids)
                    is_renamed_7 = (widget['id'] == 'widget-quick-data' and 'widget-7' in current_ids)
                    is_renamed_1 = (widget['id'] == 'widget-actions' and 'widget-1' in current_ids)
                    
                    if not is_renamed_6 and not is_renamed_7 and not is_renamed_1:
                        saved_layout.append(widget)
                        needs_update = True
            
            layout_config = saved_layout
        except json.JSONDecodeError:
            layout_config = default_layout

    # 2. Görev filtreleme - MATEMATİKSEL KAPSAYICILIK MANTIĞI
    today = date.today()
    week_end = today + timedelta(days=7)
    month_end = today + timedelta(days=30)
    year_end = date(today.year, 12, 31)
    
    # TÜM görevleri çek (Tamamlananlar dahil, sadece arşivlenmemişler)
    all_tasks = Task.query.filter(
        Task.assigned_to_id == current_user.id,
        Task.is_archived == False
    ).order_by(Task.due_date.asc()).all()

    # Görev grupları
    task_groups = {
        'overdue': [],
        'today': [],
        'week': [],
        'month': [],
        'year': []
    }

    # MATEMATİKSEL KAPSAYICILIK: Her görev tüm uygun kategorilere eklenir
    # Kural: Today ⊆ Week ⊆ Month ⊆ Year
    for task in all_tasks:
        if not task.due_date:
            continue
            
        due = task.due_date if isinstance(task.due_date, date) else task.due_date.date()
        
        # 1. GEÇMIŞ (Sadece geçmiş, diğer kategorilere dahil değil)
        if due < today:
            task_groups['overdue'].append(task)
            continue  # Geçmiş görevler diğer kategorilere eklenmez
        
        # 2. BUGÜN (Bugün olan görevler aynı zamanda Week, Month, Year'a da dahil)
        if due == today:
            task_groups['today'].append(task)
            task_groups['week'].append(task)
            task_groups['month'].append(task)
            task_groups['year'].append(task)
            continue
        
        # 3. BU HAFTA (Bugün hariç, +7 gün içinde)
        # Bu hafta olan görevler aynı zamanda Month ve Year'a da dahil
        if due <= week_end:
            task_groups['week'].append(task)
            task_groups['month'].append(task)
            task_groups['year'].append(task)
            continue
        
        # 4. BU AY (Hafta hariç, +30 gün içinde)
        # Bu ay olan görevler aynı zamanda Year'a da dahil
        if due <= month_end:
            task_groups['month'].append(task)
            task_groups['year'].append(task)
            continue
        
        # 5. BU YIL (Ay hariç, yıl sonuna kadar)
        if due <= year_end:
            task_groups['year'].append(task)
    
    # SIRALAMA: Önce Pending, Sonra Completed
    def sort_tasks(task_list):
        """Görevleri durumuna göre sırala: Pending önce, Completed sonra"""
        return sorted(task_list, key=lambda t: (
            t.status in ['Tamamlandı', 'Completed'],  # False (0) önce, True (1) sonra
            t.due_date or date.max  # Tarihe göre ikincil sıralama
        ))
    
    # Tüm grupları sırala
    for key in task_groups:
        task_groups[key] = sort_tasks(task_groups[key])
    
    # SEKME SAYAÇLARI: Sadece PENDING görevleri say (Tamamlananlar hariç)
    task_counts = {}
    for key, tasks in task_groups.items():
        pending_tasks = [t for t in tasks if t.status not in ['Tamamlandı', 'Completed']]
        task_counts[key] = len(pending_tasks)

    # 3. İstatistikler
    completed_count = Task.query.filter(
        Task.assigned_to_id == current_user.id,
        Task.status.in_(['Tamamlandı', 'Completed'])
    ).count()
    
    pending_count = Task.query.filter(
        Task.assigned_to_id == current_user.id,
        Task.status.notin_(['Tamamlandı', 'Completed'])
    ).count()
    
    total_tasks = completed_count + pending_count
    performance_score = int((completed_count / total_tasks) * 100) if total_tasks > 0 else 75

    stats = {
        "completed_tasks": completed_count,
        "pending_tasks": pending_count,
        "performance": performance_score
    }
    
    # 4. Karalama Defteri (Postit) Varsayılan İçerik
    postit_content = ""
    
    # GERÇEK BİLDİRİMLERİ ÇEK (Okunmamış, son 20)
    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        okundu=False
    ).order_by(Notification.created_at.desc()).limit(20).all()

    # 7. Bekleyen KPI Veri Girişleri (Hızlı Veri)
    # Kullanıcının sorumlu olduğu, aktif ve bu ay henüz veri girilmemiş PG'ler
    today = date.today()
    current_year = today.year
    current_month = today.month
    
    # 1. Kullanıcının sorumlu olduğu tüm aktif PG'ler
    my_kpis = BireyselPerformansGostergesi.query.filter_by(
        user_id=current_user.id, 
        durum='Devam Ediyor'
    ).all()
    
    pending_kpis = []
    for kpi in my_kpis:
        # Bu ay için veri girilmiş mi?
        entry_exists = PerformansGostergeVeri.query.filter(
            PerformansGostergeVeri.bireysel_pg_id == kpi.id,
            db.extract('year', PerformansGostergeVeri.veri_tarihi) == current_year,
            db.extract('month', PerformansGostergeVeri.veri_tarihi) == current_month
        ).first()
        
        if not entry_exists:
            pending_kpis.append(kpi)

    active_projects = [
        {"name": "Dijital Dönüşüm 2.0", "progress": 75, "color": "success"},
        {"name": "İK Reorganizasyon", "progress": 45, "color": "warning"},
        {"name": "Yeni CRM Entegrasyonu", "progress": 20, "color": "danger"},
    ]

    # 5. Karalama Defteri Notları
    notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.created_at.desc()).limit(10).all()

    # 6. Stratejik Özet (Sağlık Skoru ve Kritik Riskler)
    strategic_summary = calculate_strategic_summary(current_user)

    # 7. Kritik Teslimatlar (Upcoming Deadlines)
    today = date.today()
    deadline_threshold = today + timedelta(days=14)
    
    # Kullanıcının sorumlu olduğu veya atandığı yaklaşan görevler
    upcoming_tasks = Task.query.filter(
        Task.assigned_to_id == current_user.id,
        Task.due_date.isnot(None),
        Task.due_date.between(today, deadline_threshold),
        Task.status.notin_(['Tamamlandı', 'Completed']),
        Task.is_archived == False
    ).order_by(Task.due_date.asc()).limit(5).all()
    
    # Her görev için kalan gün hesapla
    upcoming_deadlines = []
    for task in upcoming_tasks:
        days_left = (task.due_date - today).days
        upcoming_deadlines.append({
            'task': task,
            'days_left': days_left,
            'project_name': task.project.name if task.project else 'Proje Yok',
            'priority': task.priority,
            'due_date': task.due_date
        })

    # 7. Süreçlerim (My Processes)
    my_processes = Surec.query.filter(
        db.or_(
            Surec.liderler.any(id=current_user.id),
            Surec.uyeler.any(id=current_user.id),
            Surec.owners.any(id=current_user.id)
        ),
        Surec.durum.in_(['Aktif', 'Devam Ediyor']),
        Surec.silindi == False
    ).order_by(Surec.created_at.desc()).limit(50).all()

    # 8. Projelerim (My Projects)
    #current_user'ın üye veya yönetici olduğu projeler.
    #Sıralama: Termin tarihi en yakın olan veya en son güncellenenler üstte.
    #Limit: 5 adet.
    my_projects = Project.query.filter(
        db.or_(
            Project.manager_id == current_user.id,
            Project.members.any(id=current_user.id)
        ),
        Project.is_archived == False
    ).order_by(Project.end_date.asc(), Project.updated_at.desc()).limit(50).all()

    return render_template('v3/dashboard.html',
                           layout_config=layout_config,
                           task_groups=task_groups,
                           task_counts=task_counts,
                           stats=stats,
                           postit_content=postit_content,
                           notifications=notifications,
                           pending_kpis=pending_kpis,
                           active_projects=active_projects,
                           notes=notes,
                           strategic_summary=strategic_summary,
                           upcoming_deadlines=upcoming_deadlines,
                           my_processes=my_processes,
                           my_projects=my_projects)

@v3_bp.route('/gorev/tamamla/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    """Görevi tamamla"""
    task = Task.query.get_or_404(task_id)
    
    # Yetki kontrolü
    if task.assigned_to_id == current_user.id or task.reporter_id == current_user.id:
        task.status = 'Tamamlandı'
        task.completed_at = db.func.now()
        task.progress = 100
        db.session.commit()
    
    return redirect(url_for('v3.dashboard'))

@v3_bp.route('/api/save_layout', methods=['POST'])
@login_required
def save_layout():
    """Widget düzenini kaydet"""
    data = request.get_json()
    layout_data = data.get('layout')
    
    if not layout_data:
        return jsonify({"success": False, "message": "No layout data"}), 400
        
    settings = UserDashboardSettings.query.filter_by(user_id=current_user.id).first()
    if not settings:
        settings = UserDashboardSettings(user_id=current_user.id)
        db.session.add(settings)
    
    settings.layout_config = json.dumps(layout_data)
    settings.updated_at = db.func.now()
    
    try:
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@v3_bp.route('/not/ekle', methods=['POST'])
@login_required
def add_note():
    """Yeni not ekle"""
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    
    if not title:
        flash('Not başlığı gereklidir.', 'warning')
        return redirect(url_for('v3.dashboard'))
    
    note = Note(
        user_id=current_user.id,
        title=title,
        content=content
    )
    
    try:
        db.session.add(note)
        db.session.commit()
        flash('Not başarıyla eklendi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Not eklenirken hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('v3.dashboard'))

@v3_bp.route('/not/sil/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    """Not sil"""
    note = Note.query.get_or_404(note_id)
    
    # Güvenlik kontrolü: Sadece kendi notunu silebilir
    if note.user_id != current_user.id:
        flash('Bu notu silme yetkiniz yok.', 'danger')
        return redirect(url_for('v3.dashboard'))
    
    try:
        db.session.delete(note)
        db.session.commit()
        flash('Not başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Not silinirken hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('v3.dashboard'))


@v3_bp.route('/hizli-veri/kaydet/<int:kpi_id>', methods=['POST'])
@login_required
def save_quick_data(kpi_id):
    """Hızlı Veri Girişi Kaydet"""
    try:
        data = request.get_json()
        deger = data.get('deger')
        
        if deger is None:
            return jsonify({'success': False, 'message': 'Değer boş olamaz.'}), 400
            
        try:
            deger_float = float(deger)
        except ValueError:
            return jsonify({'success': False, 'message': 'Geçersiz sayısal değer.'}), 400
            
        kpi = BireyselPerformansGostergesi.query.get_or_404(kpi_id)
        
        # Yetki Kontrolü
        if kpi.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Yetkiniz yok.'}), 403
            
        today = date.today()
        
        # Yeni Veri Kaydı
        yeni_veri = PerformansGostergeVeri(
            bireysel_pg_id=kpi.id,
            user_id=current_user.id,
            yil=today.year,
            veri_tarihi=today,
            gerceklesen_deger=str(deger_float),
            giris_periyot_tipi='aylik',
            giris_periyot_ay=today.month,
            created_by=current_user.id
        )
        
        db.session.add(yeni_veri)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Veri başarıyla kaydedildi.'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

