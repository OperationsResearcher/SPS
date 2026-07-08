# -*- coding: utf-8 -*-
"""Proje / gorev / risk / klonlama API rotalari

api/routes.py'den bölündü (davranış/URL değişmedi). Blueprint: api.blueprint.api_bp
"""
from flask import jsonify, request, current_app, send_file
from werkzeug.utils import secure_filename
import os
import uuid
from flask_login import login_required, current_user
from extensions import csrf, db
from sqlalchemy import or_, and_, text, delete, insert
from sqlalchemy.orm import joinedload
from app.utils.project_rbac import (
    project_access_required,
    project_manager_required,
    project_member_required,
    project_observer_allowed,
    role_required,
)
from app.models.portfolio_project import (
    Project,
    Task,
    TaskImpact,
    TaskComment,
    TaskMention,
    ProjectFile,
    Tag,
    TaskSubtask,
    TimeEntry,
    TaskActivity,
    ProjectTemplate,
    TaskTemplate,
    Sprint,
    TaskSprint,
    ProjectRisk,
    TaskDependency,
    IntegrationHook,
    RuleDefinition,
    SLA,
    RecurringTask,
    WorkingDay,
    CapacityPlan,
    RaidItem,
    TaskBaseline,
    project_leaders,
    task_predecessors,
)
from app.models.legacy_bridge import (
    User, Kurum, Surec, AnaStrateji, AltStrateji,
    BireyselFaaliyet, BireyselPerformansGostergesi,
    PerformansGostergeVeri, PerformansGostergeVeriAudit, SurecPerformansGostergesi, SurecFaaliyet,
    FaaliyetTakip, surec_liderleri, surec_uyeleri,
    Notification, UserActivityLog, FavoriKPI, DashboardLayout,
    KullaniciYetki,
)
from api.blueprint import api_bp
from datetime import datetime, timedelta, date
from services.rule_engine_service import evaluate_rules
from api.helpers import (
    _invalidate_executive_dashboard_cache,
    _resolve_project_leader_ids_api,
    _sync_project_leaders_api,
    _notify_project_team_changes_api,
    _parse_date_safe,
)


@api_bp.route('/projeler', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def api_projeler_list():
    """Kullanıcının kurumundaki tüm projeleri getir veya yeni proje oluştur"""
    if request.method == 'GET':
        try:
            projeler = Project.query.filter_by(kurum_id=current_user.kurum_id).all()
            return jsonify({
                'success': True,
                'projeler': [{
                    'id': p.id,
                    'name': p.name,
                    'description': p.description,
                    'manager_id': p.manager_id,
                    'leader_ids': p.leader_user_ids(),
                    'manager_name': f"{p.manager.first_name} {p.manager.last_name}" if p.manager else None,
                    'created_at': p.created_at.isoformat() if p.created_at else None
                } for p in projeler]
            })
        except Exception as e:
            current_app.logger.error(f'Projeler listesi hatası: {e}')
            return jsonify({'success': False, 'message': str(e)}), 500
    else:  # POST
        try:
            if not request.is_json:
                return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
            
            data = request.get_json()
            
            # Zorunlu alan kontrolü
            if not data.get('name') or not data.get('name').strip():
                return jsonify({'success': False, 'message': 'Proje adı zorunludur'}), 400
            leader_ids = _resolve_project_leader_ids_api(data, current_user.kurum_id)
            if not leader_ids:
                return jsonify({'success': False, 'message': 'En az bir proje yöneticisi (lider) zorunludur'}), 400
            if not data.get('start_date'):
                return jsonify({'success': False, 'message': 'Başlangıç tarihi zorunludur'}), 400
            if not data.get('end_date'):
                return jsonify({'success': False, 'message': 'Bitiş tarihi zorunludur'}), 400
            
            # Tarih kontrolü
            try:
                from datetime import datetime
                start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
                end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
                
                if end_date < start_date:
                    return jsonify({'success': False, 'message': 'Bitiş tarihi başlangıç tarihinden önce olamaz'}), 400
            except ValueError:
                return jsonify({'success': False, 'message': 'Geçersiz tarih formatı (YYYY-MM-DD bekleniyor)'}), 400
            
            # Yeni proje oluştur
            new_project = Project(
                kurum_id=current_user.kurum_id,
                name=data.get('name', '').strip(),
                description=data.get('description', '').strip() if data.get('description') else None,
                manager_id=leader_ids[0],
                start_date=start_date,
                end_date=end_date,
                priority=data.get('priority', 'Orta')
            )

            # Bildirim ayarları (JSON) - yoksa default bırak
            try:
                import json
                settings = data.get('notification_settings')
                if isinstance(settings, dict):
                    # Temel normalize
                    reminder_days = settings.get('reminder_days', [7, 3, 1])
                    if not isinstance(reminder_days, list):
                        reminder_days = [7, 3, 1]
                    reminder_days = [int(x) for x in reminder_days if str(x).strip().isdigit() or isinstance(x, int)]
                    reminder_days = sorted(list(set([d for d in reminder_days if d >= 0])), reverse=True) or [7, 3, 1]
                    overdue_frequency = settings.get('overdue_frequency', 'daily')
                    if overdue_frequency not in ['daily', 'off']:
                        overdue_frequency = 'daily'
                    channels = settings.get('channels') if isinstance(settings.get('channels'), dict) else {}
                    normalized = {
                        'reminder_days': reminder_days,
                        'overdue_frequency': overdue_frequency,
                        'channels': {
                            'in_app': True,
                            'email': bool(channels.get('email'))
                        },
                        'notify_manager': bool(settings.get('notify_manager', True)),
                        'notify_observers': bool(settings.get('notify_observers', False))
                    }
                    new_project.notification_settings = json.dumps(normalized, ensure_ascii=False)
            except Exception as e:
                current_app.logger.warning(f"[api_projeler_list] suppressed: {e}")
            
            db.session.add(new_project)
            db.session.flush()  # ID'yi almak için
            _sync_project_leaders_api(new_project, current_user.kurum_id, leader_ids)
            
            # İlişkili süreçleri ekle (silinmiş süreç kontrolü)
            if data.get('related_process_ids'):
                for surec_id in data.get('related_process_ids', []):
                    surec = Surec.query.get(surec_id)
                    if surec and surec.kurum_id == current_user.kurum_id:
                        new_project.related_processes.append(surec)
                    elif not surec:
                        current_app.logger.warning(f"Proje oluşturulurken silinmiş süreç ID'si tespit edildi: {surec_id}")
                    elif surec.kurum_id != current_user.kurum_id:
                        current_app.logger.warning(f"Proje oluşturulurken farklı kuruma ait süreç ID'si tespit edildi: {surec_id}")
            
            # Üyeleri ekle (geçersiz kullanıcı kontrolü)
            if data.get('member_ids'):
                for user_id in data.get('member_ids', []):
                    user = User.query.get(user_id)
                    if user and user.kurum_id == current_user.kurum_id:
                        new_project.members.append(user)
                    elif not user:
                        current_app.logger.warning(f"Proje oluşturulurken silinmiş kullanıcı ID'si tespit edildi: {user_id}")
                    elif user.kurum_id != current_user.kurum_id:
                        current_app.logger.warning(f"Proje oluşturulurken farklı kuruma ait kullanıcı ID'si tespit edildi: {user_id}")
            
            # Gözlemcileri ekle (geçersiz kullanıcı kontrolü)
            if data.get('observer_ids'):
                for user_id in data.get('observer_ids', []):
                    user = User.query.get(user_id)
                    if user and user.kurum_id == current_user.kurum_id:
                        new_project.observers.append(user)
                    elif not user:
                        current_app.logger.warning(f"Proje oluşturulurken silinmiş gözlemci kullanıcı ID'si tespit edildi: {user_id}")
                    elif user.kurum_id != current_user.kurum_id:
                        current_app.logger.warning(f"Proje oluşturulurken farklı kuruma ait gözlemci kullanıcı ID'si tespit edildi: {user_id}")
            
            _notify_project_team_changes_api(
                new_project, current_user.kurum_id, set(), set()
            )
            db.session.commit()
            
            # Yeni proje oluşturulduğunda dashboard cache'i temizle
            _invalidate_executive_dashboard_cache(current_user.kurum_id)
            
            return jsonify({
                'success': True,
                'message': 'Proje başarıyla oluşturuldu',
                'project_id': new_project.id
            })
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Proje oluşturma hatası: {e}')
            return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/projeler/<int:project_id>', methods=['GET', 'PUT'])
@csrf.exempt
@login_required
def api_proje_detay(project_id):
    """Proje detayını getir veya güncelle"""
    try:
        project = Project.query.get_or_404(project_id)
        
        # Yetki kontrolü
        if project.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu projeye erişim yetkiniz yok'}), 403
        
        if request.method == 'GET':
            # Proje detayını getir
            return jsonify({
                'success': True,
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'description': project.description,
                    'manager_id': project.manager_id,
                    'leader_ids': project.leader_user_ids(),
                    'manager_name': f"{project.manager.first_name} {project.manager.last_name}" if project.manager else None,
                    'start_date': project.start_date.isoformat() if project.start_date else None,
                    'end_date': project.end_date.isoformat() if project.end_date else None,
                    'priority': project.priority,
                    'created_at': project.created_at.isoformat() if project.created_at else None,
                    'notification_settings': project.get_notification_settings() if hasattr(project, 'get_notification_settings') else None,
                    'related_process_ids': [s.id for s in project.related_processes],
                    'member_ids': [m.id for m in project.members],
                    'observer_ids': [o.id for o in project.observers]
                }
            })
        else:  # PUT
            if not request.is_json:
                return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
            
            data = request.get_json()
            old_leader_ids = set(project.leader_user_ids())
            old_member_ids = set(project.member_user_ids())
            
            # Proje bilgilerini güncelle
            if data.get('name'):
                project.name = data.get('name', '').strip()
            if 'description' in data:
                project.description = data.get('description', '').strip() if data.get('description') else None
            if 'manager_ids' in data or 'manager_id' in data:
                lids = _resolve_project_leader_ids_api(data, current_user.kurum_id)
                if lids:
                    _sync_project_leaders_api(project, current_user.kurum_id, lids)

            # Bildirim ayarları
            if 'notification_settings' in data:
                try:
                    import json
                    settings = data.get('notification_settings')
                    if isinstance(settings, dict):
                        reminder_days = settings.get('reminder_days', [7, 3, 1])
                        if not isinstance(reminder_days, list):
                            reminder_days = [7, 3, 1]
                        reminder_days = [int(x) for x in reminder_days if str(x).strip().isdigit() or isinstance(x, int)]
                        reminder_days = sorted(list(set([d for d in reminder_days if d >= 0])), reverse=True) or [7, 3, 1]
                        overdue_frequency = settings.get('overdue_frequency', 'daily')
                        if overdue_frequency not in ['daily', 'off']:
                            overdue_frequency = 'daily'
                        channels = settings.get('channels') if isinstance(settings.get('channels'), dict) else {}
                        normalized = {
                            'reminder_days': reminder_days,
                            'overdue_frequency': overdue_frequency,
                            'channels': {
                                'in_app': True,
                                'email': bool(channels.get('email'))
                            },
                            'notify_manager': bool(settings.get('notify_manager', True)),
                            'notify_observers': bool(settings.get('notify_observers', False))
                        }
                        project.notification_settings = json.dumps(normalized, ensure_ascii=False)
                except Exception as e:
                    current_app.logger.warning(f"[api_proje_detay] suppressed: {e}")
            
            # İlişkili süreçleri güncelle
            if 'related_process_ids' in data:
                project.related_processes = []
                for surec_id in data.get('related_process_ids', []):
                    surec = Surec.query.get(surec_id)
                    if surec and surec.kurum_id == current_user.kurum_id:
                        project.related_processes.append(surec)
            
            # Üyeleri güncelle
            if 'member_ids' in data:
                project.members = []
                for user_id in data.get('member_ids', []):
                    user = User.query.get(user_id)
                    if user and user.kurum_id == current_user.kurum_id:
                        project.members.append(user)
            
            # Gözlemcileri güncelle
            if 'observer_ids' in data:
                project.observers = []
                for user_id in data.get('observer_ids', []):
                    user = User.query.get(user_id)
                    if user and user.kurum_id == current_user.kurum_id:
                        project.observers.append(user)
            
            _notify_project_team_changes_api(
                project, current_user.kurum_id, old_leader_ids, old_member_ids
            )
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Proje başarıyla güncellendi'
            })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Proje detay/güncelleme hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500




@api_bp.route('/projeler/<int:project_id>/gorevler', methods=['GET'])
@login_required
@project_observer_allowed
def api_proje_gorevler(project_id, **kwargs):
    """Projenin görevlerini getir"""
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        
        tasks = Task.query.filter_by(project_id=project_id).all()
        return jsonify({
            'success': True,
            'gorevler': [{
                'id': t.id,
                'title': t.title,
                'description': t.description,
                'status': t.status,
                'priority': t.priority,
                'due_date': t.due_date.isoformat() if t.due_date else None,
                'start_date': t.start_date.isoformat() if t.start_date else None,
                'estimated_time': t.estimated_time,
                'actual_time': t.actual_time,
                'parent_id': t.parent_id,
                'created_at': t.created_at.isoformat() if t.created_at else None,
                'assigned_to_id': t.assigned_to_id,
                'external_assignee_name': getattr(t, 'external_assignee_name', None),
                'assigned_to': {
                    'id': t.assigned_to.id,
                    'first_name': t.assigned_to.first_name,
                    'last_name': t.assigned_to.last_name
                } if t.assigned_to else None
            } for t in tasks]
        })
    except Exception as e:
        current_app.logger.error(f'Proje görevleri hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/projeler/<int:project_id>/gorevler/<int:task_id>/yorumlar', methods=['GET'])
@login_required
@project_observer_allowed
def api_gorev_yorumlari_get(project_id, task_id, **kwargs):
    """Görev yorumlarını getir (task_form.html AJAX)"""
    try:
        project = kwargs.get('project')
        task = Task.query.get_or_404(task_id)

        if task.project_id != project_id:
            return jsonify({'success': False, 'message': 'Görev bu projeye ait değil'}), 404

        comments = (
            TaskComment.query.options(joinedload(TaskComment.user))
            .filter_by(task_id=task_id)
            .order_by(TaskComment.created_at.asc())
            .all()
        )

        yorumlar = []
        for c in comments:
            user = c.user
            if user:
                full_name = f"{(user.first_name or '').strip()} {(user.last_name or '').strip()}".strip()
                user_name = full_name or (getattr(user, 'username', None) or 'Bilinmiyor')
            else:
                user_name = 'Bilinmiyor'

            yorumlar.append({
                'id': c.id,
                'task_id': c.task_id,
                'user_id': c.user_id,
                'user_name': user_name,
                'comment_text': c.comment,
                'created_at': c.created_at.isoformat() if c.created_at else None,
            })

        return jsonify({'success': True, 'yorumlar': yorumlar})
    except Exception as e:
        current_app.logger.error(f'Görev yorumları GET hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/projeler/<int:project_id>/gorevler/<int:task_id>/yorumlar', methods=['POST'])
@csrf.exempt
@login_required
@project_member_required
def api_gorev_yorumlari_post(project_id, task_id, **kwargs):
    """Göreve yorum ekle (task_form.html AJAX)"""
    try:
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400

        data = request.get_json(silent=True) or {}
        comment_text = str(data.get('comment_text') or '').strip()
        if not comment_text:
            return jsonify({'success': False, 'message': 'Yorum metni boş olamaz'}), 400

        task = Task.query.get_or_404(task_id)
        if task.project_id != project_id:
            return jsonify({'success': False, 'message': 'Görev bu projeye ait değil'}), 404

        new_comment = TaskComment(
            task_id=task_id,
            user_id=current_user.id,
            comment=comment_text,
        )
        db.session.add(new_comment)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Yorum eklendi', 'comment_id': new_comment.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Görev yorumları POST hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/projeler/<int:project_id>/gorevler', methods=['POST'])
@csrf.exempt
@login_required
@project_member_required  # Üye veya yönetici yetkisi gereklidir (gözlemci görev oluşturamaz)
def api_gorev_olustur(project_id, **kwargs):
    """Yeni görev oluştur"""
    try:
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        
        data = request.get_json()
        project = kwargs.get('project')

        external_assignee_name = data.get('external_assignee_name')
        if external_assignee_name is not None:
            external_assignee_name = str(external_assignee_name).strip()
            if external_assignee_name == '':
                external_assignee_name = None
            elif len(external_assignee_name) > 200:
                external_assignee_name = external_assignee_name[:200]

        assigned_to_id = data.get('assigned_to_id')
        if assigned_to_id in ('', None):
            assigned_to_id = None
        if external_assignee_name:
            assigned_to_id = None
        
        # Tarih dönüştürme
        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.strptime(data.get('due_date'), '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': 'Geçersiz tarih formatı'}), 400
        
        # Hatırlat tarihi dönüştürme
        reminder_date = None
        if data.get('reminder_date'):
            try:
                # Format: 2026-01-13T14:30 (datetime-local HTML5 input format)
                reminder_date = datetime.strptime(data.get('reminder_date'), '%Y-%m-%dT%H:%M')
            except ValueError:
                return jsonify({'success': False, 'message': 'Geçersiz hatırlat tarihi formatı'}), 400

        status_val = data.get('status', 'Yapılacak')
        priority_val = data.get('priority', 'Orta')
        title_val = (data.get('title') or '').strip()
        if not title_val:
            return jsonify({'success': False, 'message': 'Görev başlığı boş olamaz'}), 400

        desc_raw = data.get('description')
        desc_val = None
        if desc_raw is not None:
            desc_val = str(desc_raw).strip() or None

        assignee_id = None if external_assignee_name else assigned_to_id
        if assignee_id is not None:
            try:
                assignee_id = int(assignee_id)
            except (TypeError, ValueError):
                return jsonify({'success': False, 'message': 'Geçersiz atanan kullanıcı'}), 400

        if project is not None and getattr(project, 'id', None) != project_id:
            return jsonify({'success': False, 'message': 'Proje bilgisi uyuşmuyor'}), 400

        task = Task(
            project_id=project_id,
            title=title_val,
            description=desc_val,
            status=status_val,
            priority=priority_val,
            reporter_id=current_user.id,
            assignee_id=assignee_id,
            external_assignee_name=external_assignee_name,
            due_date=due_date,
            reminder_date=reminder_date,
            is_archived=False,
        )
        db.session.add(task)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Görev başarıyla oluşturuldu',
            'task_id': task.id,
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Görev oluşturma hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/projeler/<int:project_id>/gorevler/<int:task_id>', methods=['PUT'])
@csrf.exempt
@login_required
@project_member_required
def api_gorev_guncelle(project_id, task_id, **kwargs):
    """Görev güncelle"""
    try:
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        
        data = request.get_json()
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        task = Task.query.get_or_404(task_id)
        
        # Yetki kontrolü
        if task.project_id != project_id:
            return jsonify({'success': False, 'message': 'Bu görevi güncelleme yetkiniz yok'}), 403
        
        # Görev bilgilerini güncelle
        if 'title' in data:
            task.title = data['title'].strip()
        if 'description' in data:
            task.description = data['description'].strip() if data.get('description') else None
        
        islenen_pg_sayisi = 0
        status_degisti_tamamlandi = False
        
        if 'status' in data:
            old_status = task.status
            task.status = data['status']
            # Eğer durum "Tamamlandı" olarak değiştirildiyse, tamamlanma tarihini kaydet
            if data['status'] == 'Tamamlandı' and old_status != 'Tamamlandı':
                task.completed_at = datetime.utcnow()
                status_degisti_tamamlandi = True
            # Eğer durum "Tamamlandı"dan başka bir duruma değiştirildiyse, completed_at'i null yap
            elif old_status == 'Tamamlandı' and data['status'] != 'Tamamlandı':
                task.completed_at = None
        if 'priority' in data:
            task.priority = data['priority']
        if 'progress' in data:
            try:
                task.progress = max(0, min(100, int(data['progress'])))
            except Exception:
                return jsonify({'success': False, 'message': 'Geçersiz ilerleme değeri'}), 400
        if 'start_date' in data:
            if data['start_date']:
                try:
                    task.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'success': False, 'message': 'Geçersiz başlangıç tarihi formatı'}), 400
            else:
                task.start_date = None
        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'success': False, 'message': 'Geçersiz tarih formatı'}), 400
            else:
                task.due_date = None
        if 'reminder_date' in data:
            if data['reminder_date']:
                try:
                    # Format: 2026-01-13T14:30 (datetime-local HTML5 input format)
                    task.reminder_date = datetime.strptime(data['reminder_date'], '%Y-%m-%dT%H:%M')
                except ValueError:
                    return jsonify({'success': False, 'message': 'Geçersiz hatırlat tarihi formatı'}), 400
            else:
                task.reminder_date = None
        if 'estimated_time' in data:
            task.estimated_time = data['estimated_time']
        if 'actual_time' in data:
            task.actual_time = data['actual_time']
        if 'parent_id' in data:
            task.parent_id = data['parent_id'] if data['parent_id'] else None
        external_assignee_name = data.get('external_assignee_name') if 'external_assignee_name' in data else None
        if external_assignee_name is not None:
            external_assignee_name = str(external_assignee_name).strip()
            if external_assignee_name == '':
                external_assignee_name = None
            elif len(external_assignee_name) > 200:
                external_assignee_name = external_assignee_name[:200]

        if 'assigned_to_id' in data or 'external_assignee_name' in data:
            old_assigned_id = task.assigned_to_id
            new_assigned_id = data.get('assigned_to_id') if data.get('assigned_to_id') else None
            if external_assignee_name:
                new_assigned_id = None
            task.assigned_to_id = new_assigned_id
            if 'external_assignee_name' in data:
                task.external_assignee_name = external_assignee_name
            elif 'assigned_to_id' in data and new_assigned_id:
                # İç kullanıcı seçildiyse dış sorumlu alanını temizle
                task.external_assignee_name = None
            # Atama değiştiyse bildirim ve aktivite log
            if old_assigned_id != task.assigned_to_id:
                from services.notification_service import create_task_assigned_notification
                from services.task_activity_service import log_task_assigned
                if task.assigned_to_id:
                    create_task_assigned_notification(task.id, task.assigned_to_id, current_user.id)
                log_task_assigned(task.id, current_user.id, old_assigned_id, task.assigned_to_id)
        if 'progress' in data:
            task.progress = data['progress']
        
        # Impact'leri güncelle (mevcut impact'leri sil ve yenilerini ekle)
        if 'impacts' in data:
            # Mevcut impact'leri sil
            TaskImpact.query.filter_by(task_id=task_id).delete()
            # Yeni impact'leri ekle
            for impact_data in data.get('impacts', []):
                impact = TaskImpact(
                    task_id=task_id,
                    related_pg_id=impact_data.get('related_pg_id'),
                    related_faaliyet_id=impact_data.get('related_faaliyet_id'),
                    impact_value=str(impact_data.get('impact_value', ''))
                )
                db.session.add(impact)
        
        # Önce görev güncellemelerini kaydet (flush)
        db.session.flush()

        # Kuralları çalıştır (tetikleyici: status_change)
        try:
            if 'status' in data:
                actions = evaluate_rules('status_change', {
                    'project_id': project_id,
                    'task_id': task_id,
                    'new_status': task.status,
                    'old_status': old_status
                })
                if actions:
                    current_app.logger.info(f'Kural motoru {len(actions)} aksiyon döndürdü (uygulama opsiyonel).')
        except Exception as e:
            current_app.logger.warning(f'Kural motoru çalıştırılamadı: {e}')
        
        # Aktivite log
        changes = {}
        if 'title' in data:
            changes['title'] = {'old': task.title, 'new': data['title'].strip()}
        if 'status' in data:
            changes['status'] = {'old': old_status, 'new': data['status']}
        if 'assigned_to_id' in data:
            changes['assigned_to_id'] = {'old': task.assigned_to_id, 'new': data.get('assigned_to_id')}
        
        if changes:
            from services.task_activity_service import log_task_updated
            log_task_updated(task.id, current_user.id, changes)
        
        if status_degisti_tamamlandi:
            from services.task_activity_service import log_task_status_changed
            log_task_status_changed(task.id, current_user.id, old_status, task.status)
            
            # Durum değişikliği bildirimi
            from services.notification_service import create_task_status_change_notification
            create_task_status_change_notification(task.id, old_status, task.status, current_user.id)
        
        # Eğer durum "Tamamlandı" olarak değiştirildiyse, PG veri girişi yap (Transaction korumalı)
        if status_degisti_tamamlandi:
            from services.project_service import handle_task_completion
            try:
                # Transaction içinde PG veri girişi yap
                islenen_pg_sayisi = handle_task_completion(task, old_status)
                
                # PG verisi oluşturulduysa, dashboard cache'i temizle
                if islenen_pg_sayisi > 0:
                    _invalidate_executive_dashboard_cache(project.kurum_id)
            except Exception as e:
                current_app.logger.error(f"Görev tamamlandığında PG veri girişi hatası: {e}")
                islenen_pg_sayisi = 0
                # Hata durumunda rollback yapılacak (project_service içinde)
        
        # Gecikmiş görev kontrolü ve bildirim
        if 'due_date' in data or 'status' in data:
            from services.notification_service import create_task_overdue_notification
            create_task_overdue_notification(task_id)
        
        # Smart Scheduling: Eğer görev tarihi geciktiyse, ardıl görevleri güncelle
        scheduling_result = None
        if 'due_date' in data and task.due_date:
            from services.smart_scheduling import check_and_update_delayed_predecessors
            try:
                scheduling_result = check_and_update_delayed_predecessors(
                    task.id, project_id, current_user.id
                )
            except Exception as e:
                current_app.logger.error(f"Smart scheduling hatası: {e}")
        
        db.session.commit()
        
        response_message = 'Görev başarıyla güncellendi'
        if status_degisti_tamamlandi and islenen_pg_sayisi > 0:
            response_message = f'Görev başarıyla tamamlandı. {islenen_pg_sayisi} adet performans göstergesi için otomatik veri girişi yapıldı.'
        elif status_degisti_tamamlandi and islenen_pg_sayisi == 0:
            response_message = 'Görev başarıyla tamamlandı. (İlişkili performans göstergesi bulunmadı veya veri girişi yapılamadı)'
        
        return jsonify({
            'success': True,
            'message': response_message,
            'islenen_pg_sayisi': islenen_pg_sayisi if status_degisti_tamamlandi else 0
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Görev güncelleme hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/projeler/<int:project_id>/gorevler/<int:task_id>', methods=['DELETE'])
@csrf.exempt
@login_required
@project_manager_required
def api_gorev_sil(project_id, task_id, **kwargs):
    """Görev sil"""
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        task = Task.query.get_or_404(task_id)
        
        # Yetki kontrolü
        if task.project_id != project_id:
            return jsonify({'success': False, 'message': 'Bu görevi silme yetkiniz yok'}), 403
        
        # Impact'leri sil (cascade ile otomatik silinecek ama emin olmak için)
        TaskImpact.query.filter_by(task_id=task_id).delete()
        
        # Aktivite log
        from services.task_activity_service import log_task_deleted
        log_task_deleted(task_id, current_user.id, task.title)
        
        # Görevi sil
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Görev başarıyla silindi'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Görev silme hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


# Görev Bağımlılıkları (Predecessors)
@api_bp.route('/projeler/<int:project_id>/gorevler/<int:task_id>/bagimliliklar', methods=['GET'])
@login_required
@project_observer_allowed
def api_gorev_bagimliliklar_get(project_id, task_id, **kwargs):
    """Bir görevin öncül (predecessor) görevlerini listele (tip ve lag ile)."""
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        task = Task.query.get_or_404(task_id)
        if task.project_id != project.id:
            return jsonify({'success': False, 'message': 'Görev bu projeye ait değil'}), 404

        TaskDependency.__table__.create(db.engine, checkfirst=True)
        deps = TaskDependency.query.filter_by(project_id=project.id, successor_id=task_id).all()
        if deps:
            payload = [{
                'predecessor_id': d.predecessor_id,
                'dependency_type': d.dependency_type or 'FS',
                'lag_days': d.lag_days or 0
            } for d in deps]
            predecessor_ids = [d.predecessor_id for d in deps]
        else:
            preds = db.session.query(task_predecessors.c.predecessor_id).\
                filter(task_predecessors.c.task_id == task_id).all()
            predecessor_ids = [pid for (pid,) in preds]
            payload = [{
                'predecessor_id': pid,
                'dependency_type': 'FS',
                'lag_days': 0
            } for pid in predecessor_ids]

        return jsonify({'success': True, 'task_id': task_id, 'predecessor_ids': predecessor_ids, 'dependencies': payload})
    except Exception as e:
        current_app.logger.error(f'Görev bağımlılıkları GET hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/projeler/<int:project_id>/gorevler/<int:task_id>/bagimliliklar', methods=['POST'])
@csrf.exempt
@login_required
@project_member_required
def api_gorev_bagimliliklar_set(project_id, task_id, **kwargs):
    """Bir görevin öncül (predecessor) görevlerini güncelle (tip ve lag ile)."""
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        task = Task.query.get_or_404(task_id)
        if task.project_id != project.id:
            return jsonify({'success': False, 'message': 'Görev bu projeye ait değil'}), 404

        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        data = request.get_json(silent=True) or {}

        TaskDependency.__table__.create(db.engine, checkfirst=True)
        deps = data.get('dependencies')
        legacy_ids = data.get('predecessor_ids')
        parsed = []

        valid_ids = {t.id for t in Task.query.filter_by(project_id=project_id).all() if t.id != task_id}

        if isinstance(deps, list):
            for d in deps:
                try:
                    pid = int(d.get('predecessor_id'))
                except Exception:
                    continue
                if pid not in valid_ids:
                    continue
                dep_type = (d.get('dependency_type') or 'FS').upper()
                lag = int(d.get('lag_days') or 0)
                parsed.append({'predecessor_id': pid, 'dependency_type': dep_type, 'lag_days': lag})
        elif isinstance(legacy_ids, list):
            for pid in legacy_ids:
                if pid in valid_ids:
                    parsed.append({'predecessor_id': pid, 'dependency_type': 'FS', 'lag_days': 0})

        # temizle ve ekle
        TaskDependency.query.filter_by(project_id=project.id, successor_id=task_id).delete()
        db.session.execute(task_predecessors.delete().where(task_predecessors.c.task_id == task_id))

        if parsed:
            for p in parsed:
                dep = TaskDependency(
                    project_id=project.id,
                    successor_id=task_id,
                    predecessor_id=p['predecessor_id'],
                    dependency_type=p['dependency_type'],
                    lag_days=p['lag_days']
                )
                db.session.add(dep)
            db.session.flush()
            db.session.execute(task_predecessors.insert(), [
                {'task_id': task_id, 'predecessor_id': p['predecessor_id']} for p in parsed
            ])

        db.session.commit()

        return jsonify({'success': True, 'message': 'Bağımlılıklar güncellendi', 'dependencies': parsed})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Görev bağımlılıkları POST hatası: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500
# ============================================================================
# PROJE YÖNETİMİ - DOSYA HAVUZU API ENDPOINT'LERİ
# ============================================================================
@api_bp.route('/projeler/<int:project_id>/riskler', methods=['GET'])
@login_required
def api_proje_riskleri(project_id):
    """Projenin risklerini getir"""
    try:
        project = Project.query.get_or_404(project_id)
        
        # Yetki kontrolü
        if project.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu projeye erişim yetkiniz yok'}), 403
        
        # Riskleri getir (created_by ilişkisini eager load et)
        from sqlalchemy.orm import joinedload
        risks = ProjectRisk.query.options(joinedload(ProjectRisk.created_by)).filter_by(project_id=project_id).all()
        
        # Risk skoruna göre sırala (property olduğu için Python'da sırala)
        risks_sorted = sorted(risks, key=lambda r: (r.impact * r.probability), reverse=True)
        
        risks_data = []
        for r in risks_sorted:
            try:
                # created_by ilişkisini güvenli şekilde al
                created_by_name = None
                try:
                    if r.created_by_id and r.created_by:
                        first_name = getattr(r.created_by, 'first_name', None) or ''
                        last_name = getattr(r.created_by, 'last_name', None) or ''
                        username = getattr(r.created_by, 'username', None) or ''
                        created_by_name = f"{first_name} {last_name}".strip() or username
                except Exception as rel_error:
                    current_app.logger.warning(f'Risk {r.id} created_by ilişki hatası: {rel_error}')
                    created_by_name = None
                
                # Risk skorunu hesapla
                risk_score = r.impact * r.probability
                
                # Risk seviyesini hesapla (skor >= 20 ise Kritik)
                if risk_score <= 6:
                    risk_level = 'Düşük'
                elif risk_score <= 12:
                    risk_level = 'Orta'
                elif risk_score < 20:
                    risk_level = 'Yüksek'
                else:  # risk_score >= 20
                    risk_level = 'Kritik'
                
                risks_data.append({
                    'id': r.id,
                    'title': r.title or '',
                    'description': r.description or '',
                    'impact': r.impact,
                    'probability': r.probability,
                    'risk_score': risk_score,
                    'risk_level': risk_level,
                    'mitigation_plan': r.mitigation_plan or '',
                    'status': r.status or 'Aktif',
                    'created_by': created_by_name,
                    'created_at': r.created_at.isoformat() if r.created_at else None
                })
            except Exception as e:
                current_app.logger.error(f'Risk serialize hatası (ID: {r.id}): {e}', exc_info=True)
                # Hatalı riski atla veya minimal bilgiyle ekle
                try:
                    risk_score = r.impact * r.probability
                    if risk_score <= 6:
                        risk_level = 'Düşük'
                    elif risk_score <= 12:
                        risk_level = 'Orta'
                    elif risk_score < 20:
                        risk_level = 'Yüksek'
                    else:  # risk_score >= 20
                        risk_level = 'Kritik'
                    
                    risks_data.append({
                        'id': r.id,
                        'title': r.title or 'Bilinmeyen Risk',
                        'description': '',
                        'impact': r.impact,
                        'probability': r.probability,
                        'risk_score': risk_score,
                        'risk_level': risk_level,
                        'mitigation_plan': '',
                        'status': r.status or 'Aktif',
                        'created_by': None,
                        'created_at': None
                    })
                except Exception as e2:
                    current_app.logger.error(f'Risk minimal serialize hatası (ID: {r.id}): {e2}')
                    # Bu riski atla
                    continue
        
        return jsonify({
            'success': True,
            'risks': risks_data
        })
    except Exception as e:
        current_app.logger.error(f'Risk listesi API hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/projeler/<int:project_id>/riskler', methods=['POST'])
@csrf.exempt
@login_required
def api_risk_ekle(project_id):
    """Yeni risk ekle"""
    try:
        project = Project.query.get_or_404(project_id)
        
        # Yetki kontrolü
        if project.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu projeye erişim yetkiniz yok'}), 403
        
        data = request.get_json()
        
        risk = ProjectRisk(
            project_id=project_id,
            title=data.get('title', '').strip(),
            description=data.get('description', '').strip(),
            impact=int(data.get('impact', 1)),
            probability=int(data.get('probability', 1)),
            mitigation_plan=data.get('mitigation_plan', '').strip(),
            status=data.get('status', 'Aktif'),
            created_by_id=current_user.id
        )
        
        db.session.add(risk)
        db.session.commit()
        
        # Kritik risk bildirimi oluştur
        if risk.risk_score >= 20:
            from services.notification_service import create_critical_risk_notification
            create_critical_risk_notification(risk.id, current_user.id)
        
        # Risk eklendiğinde dashboard cache'i temizle
        _invalidate_executive_dashboard_cache(project.kurum_id)
        
        # Webhook tetikle (V2.0.0) - Yeni risk eklendiğinde (yüksek risk ise)
        if risk.risk_score >= 20:  # Kritik risk
            try:
                from services.webhook_service import trigger_risk_increase_webhook
                trigger_risk_increase_webhook(
                    project.kurum_id,
                    risk.id,
                    0,  # Yeni risk, eski skor yok
                    risk.risk_score
                )
            except Exception as webhook_error:
                current_app.logger.warning(f'Risk webhook tetikleme hatası: {webhook_error}')
        
        return jsonify({
            'success': True,
            'message': 'Risk başarıyla eklendi',
            'risk': {
                'id': risk.id,
                'risk_score': risk.risk_score,
                'risk_level': risk.risk_level
            }
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Risk ekleme hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/projeler/<int:project_id>/riskler/<int:risk_id>', methods=['PUT'])
@csrf.exempt
@login_required
def api_risk_guncelle(project_id, risk_id):
    """Risk güncelle"""
    try:
        project = Project.query.get_or_404(project_id)
        risk = ProjectRisk.query.get_or_404(risk_id)
        
        # Yetki kontrolü
        if project.kurum_id != current_user.kurum_id or risk.project_id != project_id:
            return jsonify({'success': False, 'message': 'Bu riski güncelleme yetkiniz yok'}), 403
        
        data = request.get_json()
        
        if 'title' in data:
            risk.title = data['title'].strip()
        if 'description' in data:
            risk.description = data['description'].strip()
        if 'impact' in data:
            risk.impact = int(data['impact'])
        if 'probability' in data:
            risk.probability = int(data['probability'])
        if 'mitigation_plan' in data:
            risk.mitigation_plan = data['mitigation_plan'].strip()
        if 'status' in data:
            risk.status = data['status']
        
        # Risk puanı değişti mi kontrol et (impact veya probability değiştiyse)
        risk_score_changed = False
        if 'impact' in data or 'probability' in data:
            old_score = risk.risk_score
            db.session.flush()  # Yeni değerleri hesapla
            if risk.risk_score != old_score:
                risk_score_changed = True
        
        db.session.commit()
        
        # Risk puanı değiştiyse veya durum değiştiyse dashboard cache'i temizle
        if risk_score_changed or 'status' in data:
            _invalidate_executive_dashboard_cache(project.kurum_id)
        
        return jsonify({
            'success': True,
            'message': 'Risk başarıyla güncellendi'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Risk güncelleme hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/projeler/<int:project_id>/riskler/<int:risk_id>', methods=['DELETE'])
@csrf.exempt
@login_required
def api_risk_sil(project_id, risk_id):
    """Risk sil"""
    try:
        project = Project.query.get_or_404(project_id)
        risk = ProjectRisk.query.get_or_404(risk_id)
        
        # Yetki kontrolü
        if project.kurum_id != current_user.kurum_id or risk.project_id != project_id:
            return jsonify({'success': False, 'message': 'Bu riski silme yetkiniz yok'}), 403
        
        db.session.delete(risk)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Risk başarıyla silindi'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Risk silme hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


# AI Erken Uyarı API Endpoint'leri
@api_bp.route('/projeler/<int:project_id>/ai-tahmin', methods=['GET'])
@login_required
def api_ai_tahmin(project_id):
    """AI destekli gecikme olasılığı tahmini"""
    try:
        project = Project.query.get_or_404(project_id)
        
        # Yetki kontrolü
        if project.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu projeye erişim yetkiniz yok'}), 403
        
        from services.ai_early_warning import calculate_delay_probability
        result = calculate_delay_probability(project_id)
        
        if result:
            return jsonify({
                'success': True,
                **result
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Tahmin hesaplanamadı'
            }), 500
    except Exception as e:
        current_app.logger.error(f'AI tahmin API hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


# Kaynak Planlama API Endpoint'leri
@api_bp.route('/projeler/<int:project_id>/kaynak-isi-haritasi', methods=['GET'])
@login_required
def api_kaynak_isi_haritasi(project_id):
    """Proje için kaynak ısı haritası"""
    try:
        project = Project.query.get_or_404(project_id)
        
        # Yetki kontrolü
        if project.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu projeye erişim yetkiniz yok'}), 403
        
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if not start_date_str or not end_date_str:
            # Varsayılan: Bugünden itibaren 30 gün
            from datetime import date, timedelta
            start_date = date.today()
            end_date = start_date + timedelta(days=30)
        else:
            start_date = datetime.fromisoformat(start_date_str).date()
            end_date = datetime.fromisoformat(end_date_str).date()
        
        from services.resource_planning import get_resource_heatmap
        result = get_resource_heatmap(project_id, start_date, end_date)
        
        if result:
            return jsonify({
                'success': True,
                **result
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Isı haritası oluşturulamadı'
            }), 500
    except Exception as e:
        current_app.logger.error(f'Kaynak ısı haritası API hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/projeler/<int:project_id>/klonla', methods=['POST'])
@csrf.exempt
@login_required
def api_proje_klonla(project_id):
    """Projeyi klonla (derin kopyalama)"""
    try:
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        
        data = request.get_json()
        project = Project.query.get_or_404(project_id)
        
        # Yetki kontrolü
        if project.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu projeye erişim yetkiniz yok'}), 403
        
        # Yeni proje adı ve başlangıç tarihi
        new_name = data.get('new_name', '').strip()
        if not new_name:
            return jsonify({'success': False, 'message': 'Yeni proje adı gereklidir'}), 400
        
        new_start_date_str = data.get('new_start_date')
        if not new_start_date_str:
            return jsonify({'success': False, 'message': 'Yeni başlangıç tarihi gereklidir'}), 400
        
        try:
            from datetime import datetime
            new_start_date = datetime.strptime(new_start_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'message': 'Geçersiz tarih formatı (YYYY-MM-DD bekleniyor)'}), 400
        
        keep_assignments = data.get('keep_assignments', True)
        keep_completed_tasks = data.get('keep_completed_tasks', False)
        
        # Proje klonlama servisini kullan
        from services.project_cloning import clone_project
        
        new_project_id = clone_project(
            project_id=project_id,
            new_name=new_name,
            new_start_date=new_start_date,
            keep_assignments=keep_assignments,
            keep_completed_tasks=keep_completed_tasks
        )
        
        if new_project_id:
            return jsonify({
                'success': True,
                'message': 'Proje başarıyla kopyalandı',
                'new_project_id': new_project_id
            })
        else:
            return jsonify({'success': False, 'message': 'Proje kopyalanamadı'}), 500
    
    except Exception as e:
        current_app.logger.error(f'Proje klonlama hatası: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500
@api_bp.route('/projeler/<int:project_id>/gorevler/<int:task_id>/asiri-yukleme-kontrol', methods=['GET'])
@login_required
def api_asiri_yukleme_kontrol(project_id, task_id):
    """Görev atamasının aşırı yükleme yapıp yapmadığını kontrol et"""
    try:
        project = Project.query.get_or_404(project_id)
        task = Task.query.get_or_404(task_id)
        
        # Yetki kontrolü
        if project.kurum_id != current_user.kurum_id or task.project_id != project_id:
            return jsonify({'success': False, 'message': 'Bu göreve erişim yetkiniz yok'}), 403
        
        from services.resource_planning import check_task_overload
        result = check_task_overload(task_id, task.assigned_to_id, task.due_date)
        
        return jsonify({
            'success': True,
            **result
        })
    except Exception as e:
        current_app.logger.error(f'Aşırı yükleme kontrolü API hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


# Kullanıcı Tercihleri API Endpoint'leri
@api_bp.route('/task/<int:task_id>/complete', methods=['POST'])
@csrf.exempt
@login_required
def api_task_complete(task_id):
    """Görevi tamamla ve proje ilerlemesini güncelle"""
    try:
        from datetime import datetime
        
        # Görevi bul
        task = Task.query.get_or_404(task_id)
        
        # Yetki kontrolü - görevin bağlı olduğu projeye erişim yetkisi var mı?
        project = Project.query.get_or_404(task.project_id)
        if project.kurum_id != current_user.kurum_id:
            return jsonify({
                'success': False,
                'message': 'Bu göreve erişim yetkiniz yok'
            }), 403
        
        # Görev zaten tamamlanmış mı?
        if task.status == 'Tamamlandı':
            return jsonify({
                'success': False,
                'message': 'Bu görev zaten tamamlanmış'
            }), 400
        
        # Görevi tamamla
        task.status = 'Tamamlandı'
        task.completed_at = datetime.utcnow()
        db.session.flush()
        
        # OTOMASYON BAŞLANGICI: PG Verisi Oluşturma (V2.5.0)
        pg_created = False
        if task.is_measurable and task.related_indicator_id:
            try:
                # İlişkili PG'yi kontrol et
                related_pg = BireyselPerformansGostergesi.query.get(task.related_indicator_id)
                if related_pg:
                    # Yeni performans değeri kaydı oluştur
                    from datetime import date
                    today = date.today()
                    
                    # Değer hesapla
                    output_value = task.planned_output_value if task.planned_output_value is not None else 1.0
                    
                    # PerformansGostergeVeri kaydı oluştur
                    new_pg_veri = PerformansGostergeVeri(
                        bireysel_pg_id=task.related_indicator_id,
                        yil=today.year,
                        veri_tarihi=today,
                        giris_periyot_tipi='gunluk',
                        giris_periyot_no=today.day,
                        giris_periyot_ay=today.month,
                        ay=today.month,
                        gun=today.day,
                        gerceklesen_deger=str(output_value),
                        aciklama=f"Otomatik: {task.title} tamamlandı.",
                        user_id=current_user.id,
                        created_by=current_user.id,
                        updated_by=current_user.id
                    )
                    db.session.add(new_pg_veri)
                    pg_created = True
                    current_app.logger.info(f'✅ OTOMASYON: Faaliyet "{task.title}" tamamlandı, PG verisi oluşturuldu (PG ID: {task.related_indicator_id}, Değer: {output_value})')
                    print(f"✅ OTOMASYON: Faaliyet '{task.title}' tamamlandı, PG verisi oluşturuldu (PG ID: {task.related_indicator_id}, Değer: {output_value})")
                else:
                    current_app.logger.warning(f'⚠️ OTOMASYON: İlişkili PG bulunamadı (ID: {task.related_indicator_id})')
                    print(f"⚠️ OTOMASYON: İlişkili PG bulunamadı (ID: {task.related_indicator_id})")
            except Exception as pg_error:
                current_app.logger.error(f'❌ OTOMASYON HATASI: PG verisi oluşturulurken hata: {pg_error}', exc_info=True)
                print(f"❌ OTOMASYON HATASI: {pg_error}")
                # Hata olsa bile program devam etsin, görev tamamlanmış olarak işaretlensin
        else:
            if not task.is_measurable:
                print(f"ℹ️ OTOMASYON: Görev ölçülebilir değil (is_measurable=False)")
            if not task.related_indicator_id:
                print(f"ℹ️ OTOMASYON: Görev PG'ye bağlı değil (related_indicator_id=None)")
        # OTOMASYON BİTİŞİ
        
        # Proje ilerlemesini hesapla
        all_tasks = Task.query.filter_by(project_id=project.id).all()
        total_tasks = len(all_tasks)
        completed_tasks = sum(1 for t in all_tasks if t.status == 'Tamamlandı')
        
        # İlerleme yüzdesi hesapla
        new_progress = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)
        
        # Proje modelinde progress alanı yok, bu yüzden hesaplanmış değeri döndüreceğiz
        # İleride Project modeline progress alanı eklenebilir
        
        db.session.commit()
        
        current_app.logger.info(f'Görev tamamlandı: Task ID {task_id}, Proje ilerlemesi: {new_progress}%')
        
        return jsonify({
            'success': True,
            'message': 'Görev başarıyla tamamlandı',
            'new_progress': new_progress,
            'completed_tasks': completed_tasks,
            'total_tasks': total_tasks
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Görev tamamlama hatası: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ============================================
# ADMIN API ENDPOINTS
# ============================================
