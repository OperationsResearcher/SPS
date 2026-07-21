# -*- coding: utf-8 -*-
"""Proje yonetimi ileri ozellikler (EVM, CPM, SLA, RAID, kapasite, portfoy) API rotalari

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
import json
from services.cpm_service import compute_cpm
from services.burn_service import burn_charts
from services.rule_engine_service import list_rules, save_rule
from services.digest_service import project_digest
from api.helpers import (
    _invalidate_executive_dashboard_cache,
    _resolve_project_leader_ids_api,
    _sync_project_leaders_api,
    _notify_project_team_changes_api,
    _parse_date_safe,
)
from app.utils.error_handlers import json_error  # S6


@api_bp.route('/projeler/<int:project_id>/evm', methods=['GET'])
@login_required
@project_observer_allowed
def api_proje_evm(project_id, **kwargs):
    """Proje için basit EVM metriklerini (PV/EV/AC/SPI/CPI) döndür."""
    try:
        from services.evm_service import compute_project_evm
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        result = compute_project_evm(project.id)
        return jsonify({'success': True, 'evm': result})
    except Exception as e:
        current_app.logger.error(f'EVM API hatası: {e}')
        return json_error(e, "[api_proje_evm]", 500)


# CPM / Kritik Yol API
@api_bp.route('/projeler/<int:project_id>/cpm', methods=['GET'])
@login_required
@project_observer_allowed
def api_proje_cpm(project_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        result = compute_cpm(project.id)
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f'CPM API hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_cpm]", 500)


# Burnup/Burndown API
@api_bp.route('/projeler/<int:project_id>/burn', methods=['GET'])
@login_required
@project_observer_allowed
def api_proje_burn(project_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        result = burn_charts(project.id)
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f'Burn API hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_burn]", 500)


# Rule engine API
@api_bp.route('/projeler/<int:project_id>/kurallar', methods=['GET', 'POST'])
@csrf.exempt
@login_required
@project_member_required
def api_proje_kurallar(project_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        # tabloyu oluştur
        RuleDefinition.__table__.create(db.engine, checkfirst=True)

        if request.method == 'GET':
            return jsonify({'success': True, 'rules': list_rules(project.id)})

        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        data = request.get_json(silent=True) or {}
        rule_id = save_rule(
            project.id,
            name=data.get('name', 'Kural'),
            trigger=data.get('trigger', 'status_change'),
            condition=data.get('condition') or {},
            actions=data.get('actions') or [],
            is_active=bool(data.get('is_active', True))
        )
        return jsonify({'success': True, 'rule_id': rule_id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Kural API hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_kurallar]", 500)


# SLA API
@api_bp.route('/projeler/<int:project_id>/sla', methods=['GET', 'POST'])
@csrf.exempt
@login_required
@project_member_required
def api_proje_sla(project_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        SLA.__table__.create(db.engine, checkfirst=True)

        if request.method == 'GET':
            items = SLA.query.filter((SLA.project_id == project.id) | (SLA.project_id.is_(None))).all()
            return jsonify({'success': True, 'sla': [
                {'id': s.id, 'name': s.name, 'target_hours': s.target_hours, 'breach_policy': s.breach_policy, 'is_active': s.is_active}
                for s in items
            ]})

        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        data = request.get_json(silent=True) or {}
        s = SLA(
            project_id=project.id,
            name=data.get('name', 'SLA'),
            target_hours=int(data.get('target_hours', 24)),
            breach_policy=data.get('breach_policy'),
            is_active=bool(data.get('is_active', True))
        )
        db.session.add(s)
        db.session.commit()
        return jsonify({'success': True, 'sla_id': s.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'SLA API hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_sla]", 500)


# Tekrarlayan Görevler API
@api_bp.route('/projeler/<int:project_id>/tekrarlayan', methods=['GET', 'POST'])
@csrf.exempt
@login_required
@project_member_required
def api_proje_tekrarlayan(project_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        RecurringTask.__table__.create(db.engine, checkfirst=True)

        if request.method == 'GET':
            items = RecurringTask.query.filter_by(project_id=project.id).all()
            return jsonify({'success': True, 'recurring': [
                {
                    'id': r.id,
                    'title': r.title,
                    'cron_expr': r.cron_expr,
                    'template_task_id': r.template_task_id,
                    'next_run_at': r.next_run_at.isoformat() if r.next_run_at else None,
                    'is_active': r.is_active
                } for r in items
            ]})

        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        data = request.get_json(silent=True) or {}
        r = RecurringTask(
            project_id=project.id,
            title=data.get('title', 'Tekrarlayan Görev'),
            cron_expr=data.get('cron_expr', 'weekly'),
            template_task_id=data.get('template_task_id'),
            is_active=bool(data.get('is_active', True))
        )
        db.session.add(r)
        db.session.commit()
        return jsonify({'success': True, 'recurring_id': r.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Tekrarlayan görev API hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_tekrarlayan]", 500)


# Entegrasyon webhooks (Slack/Teams/Outlook)
@api_bp.route('/projeler/<int:project_id>/integrations', methods=['GET', 'POST'])
@csrf.exempt
@login_required
@project_member_required
def api_proje_integrations(project_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        IntegrationHook.__table__.create(db.engine, checkfirst=True)

        if request.method == 'GET':
            hooks = IntegrationHook.query.filter_by(project_id=project.id).all()
            return jsonify({'success': True, 'hooks': [
                {'id': h.id, 'provider': h.provider, 'url': h.url, 'is_active': h.is_active}
                for h in hooks
            ]})

        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        data = request.get_json(silent=True) or {}
        if not data.get('url'):
            return jsonify({'success': False, 'message': 'URL zorunludur'}), 400
        h = IntegrationHook(
            project_id=project.id,
            provider=data.get('provider', 'slack'),
            url=data.get('url', ''),
            is_active=bool(data.get('is_active', True))
        )
        db.session.add(h)
        db.session.commit()
        return jsonify({'success': True, 'hook_id': h.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Integration API hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_integrations]", 500)


# Haftalık digest (özet)
@api_bp.route('/projeler/<int:project_id>/digest/weekly', methods=['GET'])
@login_required
@project_observer_allowed
def api_proje_digest(project_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        summary = project_digest(project.id)
        return jsonify({'success': True, 'digest': summary})
    except Exception as e:
        current_app.logger.error(f'Digest API hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_digest]", 500)


# RAID kayıtları
@api_bp.route('/projeler/<int:project_id>/raid', methods=['GET', 'POST'])
@csrf.exempt
@login_required
@project_member_required
def api_proje_raid(project_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        RaidItem.__table__.create(db.engine, checkfirst=True)

        if request.method == 'GET':
            items = RaidItem.query.filter_by(project_id=project.id).all()
            return jsonify({'success': True, 'items': [
                {
                    'id': r.id,
                    'type': r.item_type,
                    'item_type': r.item_type,
                    'title': r.title,
                    'description': r.description,
                    'status': r.status,
                    'owner_id': r.owner_id,
                    # Risk alanları - getattr ile safe access
                    'probability': getattr(r, 'probability', None),
                    'impact': getattr(r, 'impact', None),
                    'mitigation_plan': getattr(r, 'mitigation_plan', None),
                    # Assumption alanları
                    'assumption_validation_date': (
                        getattr(r, 'assumption_validation_date', None).isoformat()
                        if getattr(getattr(r, 'assumption_validation_date', None), 'isoformat', None)
                        else getattr(r, 'assumption_validation_date', None)
                    ),
                    'assumption_validated': getattr(r, 'assumption_validated', None),
                    'assumption_notes': getattr(r, 'assumption_notes', None),
                    # Issue alanları
                    'issue_urgency': getattr(r, 'issue_urgency', None),
                    'issue_affected_work': getattr(r, 'issue_affected_work', None),
                    # Dependency alanları
                    'dependency_type': getattr(r, 'dependency_type', None),
                    'dependency_task_id': getattr(r, 'dependency_task_id', None),
                    'created_at': r.created_at.isoformat() if r.created_at else None
                } for r in items
            ]})

        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        data = request.get_json(silent=True) or {}
        r = RaidItem(
            project_id=project.id,
            item_type=data.get('item_type') or data.get('type', 'Risk'),
            title=data.get('title', 'Başlık'),
            description=data.get('description'),
            owner_id=data.get('owner_id'),
            status=data.get('status', 'Open')
        )
        
        # Risk alanları
        if r.item_type == 'Risk':
            r.probability = int(data.get('probability', 3))
            r.impact = int(data.get('impact', 3))
            r.mitigation_plan = data.get('mitigation_plan')
        
        # Assumption alanları
        elif r.item_type == 'Assumption':
            r.assumption_validation_date = _parse_date_safe(data.get('assumption_validation_date'))
            r.assumption_notes = data.get('assumption_notes')
        
        # Issue alanları
        elif r.item_type == 'Issue':
            r.issue_urgency = data.get('issue_urgency', 'Orta')
            r.issue_affected_work = data.get('issue_affected_work')
        
        # Dependency alanları
        elif r.item_type == 'Dependency':
            r.dependency_type = data.get('dependency_type', 'SS')
            r.dependency_task_id = data.get('dependency_task_id')
        
        db.session.add(r)
        db.session.commit()
        return jsonify({'success': True, 'raid_id': r.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'RAID API hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_raid]", 500)


# RAID item update/delete
@api_bp.route('/projeler/<int:project_id>/raid/<int:item_id>', methods=['PUT', 'DELETE'])
@csrf.exempt
@login_required
@project_member_required
def api_proje_raid_item(project_id, item_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        item = RaidItem.query.filter_by(id=item_id, project_id=project.id).first_or_404()
        
        if request.method == 'DELETE':
            db.session.delete(item)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Silindi'})
        
        # PUT
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        data = request.get_json(silent=True) or {}
        item.item_type = data.get('item_type') or data.get('type') or item.item_type
        item.title = data.get('title', item.title)
        item.description = data.get('description', item.description)
        item.status = data.get('status', item.status)
        item.owner_id = data.get('owner_id', item.owner_id)
        
        # Risk alanları
        if item.item_type == 'Risk':
            if 'probability' in data:
                item.probability = int(data['probability'])
            if 'impact' in data:
                item.impact = int(data['impact'])
            if 'mitigation_plan' in data:
                item.mitigation_plan = data['mitigation_plan']
        
        # Assumption alanları
        elif item.item_type == 'Assumption':
            if 'assumption_validation_date' in data:
                item.assumption_validation_date = _parse_date_safe(data['assumption_validation_date'])
            if 'assumption_notes' in data:
                item.assumption_notes = data['assumption_notes']
        
        # Issue alanları
        elif item.item_type == 'Issue':
            if 'issue_urgency' in data:
                item.issue_urgency = data['issue_urgency']
            if 'issue_affected_work' in data:
                item.issue_affected_work = data['issue_affected_work']
        
        # Dependency alanları
        elif item.item_type == 'Dependency':
            if 'dependency_type' in data:
                item.dependency_type = data['dependency_type']
            if 'dependency_task_id' in data:
                item.dependency_task_id = data['dependency_task_id']
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Güncellendi'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'RAID item API hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_raid_item]", 500)


# Portföy özet ve risk skoru
@api_bp.route('/portfoy/ozet', methods=['GET'])
@login_required
def api_portfoy_ozet():
    try:
        # Aynı kurum projeleri
        projects = Project.query.filter_by(kurum_id=current_user.kurum_id).all()
        items = []
        total_projects = len(projects)
        active_projects = 0
        risky_projects = 0
        total_risk = 0
        
        for p in projects:
            tasks = Task.query.filter_by(project_id=p.id).all()
            overdue = [t for t in tasks if t.due_date and t.due_date < datetime.utcnow().date() and (t.status or '').lower() != 'tamamlandı']
            progress = sum(float(t.progress or 0) for t in tasks) / len(tasks) if tasks else 0
            risk_score = min(100, len(overdue) * 10)
            
            if progress > 0 and progress < 100:
                active_projects += 1
            if risk_score >= 50:
                risky_projects += 1
            total_risk += risk_score
            
            items.append({
                'project_id': p.id,
                'name': p.name,
                'health_score': p.health_score,
                'risk_score': risk_score,
                'overdue_count': len(overdue),
                'progress_avg': round(progress, 1)
            })
        
        avg_risk = total_risk / total_projects if total_projects > 0 else 0
        
        return jsonify({
            'success': True,
            'total_projects': total_projects,
            'active_projects': active_projects,
            'risky_projects': risky_projects,
            'average_risk_score': round(avg_risk, 1),
            'projects': items
        })
    except Exception as e:
        current_app.logger.error(f'Portföy özet hatası: {e}', exc_info=True)
        return json_error(e, "[api_portfoy_ozet]", 500)


# Çapraz bağımlılık matrisi (proje içi)
@api_bp.route('/projeler/<int:project_id>/bagimlilik-matrisi', methods=['GET'])
@login_required
@project_observer_allowed
def api_proje_bagimlilik_matrisi(project_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        TaskDependency.__table__.create(db.engine, checkfirst=True)
        deps = TaskDependency.query.filter_by(project_id=project.id).all()
        matrix = [
            {
                'predecessor_id': d.predecessor_id,
                'successor_id': d.successor_id,
                'type': d.dependency_type,
                'lag_days': d.lag_days
            } for d in deps
        ]
        return jsonify({'success': True, 'matrix': matrix})
    except Exception as e:
        current_app.logger.error(f'Bağımlılık matrisi hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_bagimlilik_matrisi]", 500)


# Baseline kayıtları
@api_bp.route('/projeler/<int:project_id>/baseline', methods=['GET', 'POST'])
@csrf.exempt
@login_required
@project_member_required
def api_proje_baseline(project_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        TaskBaseline.__table__.create(db.engine, checkfirst=True)

        if request.method == 'GET':
            baselines = TaskBaseline.query.join(Task, Task.id == TaskBaseline.task_id).filter(Task.project_id == project.id).all()
            return jsonify({'success': True, 'baselines': [
                {
                    'task_id': b.task_id,
                    'planned_start': b.planned_start.isoformat() if b.planned_start else None,
                    'planned_end': b.planned_end.isoformat() if b.planned_end else None,
                    'planned_effort': b.planned_effort
                } for b in baselines
            ]})

        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        data = request.get_json(silent=True) or {}
        items = data.get('items', [])
        if not isinstance(items, list):
            return jsonify({'success': False, 'message': 'items list olmalı'}), 400

        TaskBaseline.query.join(Task, Task.id == TaskBaseline.task_id).filter(Task.project_id == project.id).delete(synchronize_session=False)
        for it in items:
            tid = it.get('task_id')
            if not tid:
                continue
            task = Task.query.get(tid)
            if not task or task.project_id != project.id:
                continue
            b = TaskBaseline(
                task_id=tid,
                planned_start=_parse_date_safe(it.get('planned_start')),
                planned_end=_parse_date_safe(it.get('planned_end')),
                planned_effort=it.get('planned_effort')
            )
            db.session.add(b)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Baseline güncellendi'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Baseline API hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_baseline]", 500)


# Kapasite planı
@api_bp.route('/projeler/<int:project_id>/kapasite', methods=['GET', 'POST'])
@csrf.exempt
@login_required
@project_member_required
def api_proje_kapasite(project_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        CapacityPlan.__table__.create(db.engine, checkfirst=True)

        if request.method == 'GET':
            plans = CapacityPlan.query.filter_by(project_id=project.id).all()
            return jsonify({'success': True, 'plans': [
                {
                    'id': p.id,
                    'user_id': p.user_id,
                    'weekly_hours': p.weekly_hours,
                    'start_date': p.start_date.isoformat() if p.start_date else None,
                    'end_date': p.end_date.isoformat() if p.end_date else None
                } for p in plans
            ]})

        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        data = request.get_json(silent=True) or {}
        p = CapacityPlan(
            project_id=project.id,
            user_id=data.get('user_id'),
            weekly_hours=float(data.get('weekly_hours', 40)),
            start_date=_parse_date_safe(data.get('start_date')),
            end_date=_parse_date_safe(data.get('end_date'))
        )
        db.session.add(p)
        db.session.commit()
        return jsonify({'success': True, 'plan_id': p.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Kapasite API hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_kapasite]", 500)


# Çalışma günü takvimi
@api_bp.route('/projeler/<int:project_id>/calisma-gunleri', methods=['GET', 'POST'])
@csrf.exempt
@login_required
@project_member_required
def api_proje_calisma_gunleri(project_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        WorkingDay.__table__.create(db.engine, checkfirst=True)

        if request.method == 'GET':
            days = WorkingDay.query.filter_by(project_id=project.id).all()
            return jsonify({'success': True, 'days': [
                {
                    'date': d.date.isoformat(),
                    'is_working': d.is_working
                } for d in days
            ]})

        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        data = request.get_json(silent=True) or {}
        items = data.get('days', [])
        if not isinstance(items, list):
            return jsonify({'success': False, 'message': 'days list olmalı'}), 400
        WorkingDay.query.filter_by(project_id=project.id).delete()
        for it in items:
            dval = _parse_date_safe(it.get('date'))
            if not dval:
                continue
            wd = WorkingDay(project_id=project.id, date=dval, is_working=bool(it.get('is_working', True)))
            db.session.add(wd)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Çalışma günleri güncellendi'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Çalışma günü API hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_calisma_gunleri]", 500)


# iCal export (read-only takvim)
@api_bp.route('/projeler/<int:project_id>/ical', methods=['GET'])
@login_required
@project_observer_allowed
def api_proje_ical(project_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        tasks = Task.query.filter_by(project_id=project.id).all()
        lines = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            f'X-WR-CALNAME:{project.name}',
        ]
        for t in tasks:
            if not t.due_date and not t.start_date:
                continue
            start = (t.start_date or t.due_date).strftime('%Y%m%d')
            end = (t.due_date or t.start_date).strftime('%Y%m%d')
            safe_desc = (t.description or '').replace('\n', ' ')
            lines.extend([
                'BEGIN:VEVENT',
                f'UID:{t.id}@projeler',
                f'SUMMARY:{t.title}',
                f'DTSTART;VALUE=DATE:{start}',
                f'DTEND;VALUE=DATE:{end}',
                f'DESCRIPTION:{safe_desc[:200]}',
                'END:VEVENT'
            ])
        lines.append('END:VCALENDAR')
        ical_str = '\r\n'.join(lines)
        return current_app.response_class(ical_str, mimetype='text/calendar')
    except Exception as e:
        current_app.logger.error(f'iCal export hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_ical]", 500)


# DELETE endpoints for project management resources
@api_bp.route('/projeler/<int:project_id>/kapasite/<int:plan_id>', methods=['DELETE'])
@csrf.exempt
@login_required
@project_member_required
def api_proje_kapasite_delete(project_id, plan_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        plan = CapacityPlan.query.filter_by(id=plan_id, project_id=project.id).first_or_404()
        db.session.delete(plan)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Kapasite planı silindi'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Kapasite silme hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_kapasite_delete]", 500)


@api_bp.route('/projeler/<int:project_id>/integrations/<int:hook_id>', methods=['DELETE'])
@csrf.exempt
@login_required
@project_member_required
def api_proje_integration_delete(project_id, hook_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        hook = IntegrationHook.query.filter_by(id=hook_id, project_id=project.id).first_or_404()
        db.session.delete(hook)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Webhook silindi'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Webhook silme hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_integration_delete]", 500)


@api_bp.route('/projeler/<int:project_id>/kurallar/<int:rule_id>', methods=['DELETE'])
@csrf.exempt
@login_required
@project_member_required
def api_proje_kural_delete(project_id, rule_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        rule = RuleDefinition.query.filter_by(id=rule_id, project_id=project.id).first_or_404()
        db.session.delete(rule)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Kural silindi'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Kural silme hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_kural_delete]", 500)


@api_bp.route('/projeler/<int:project_id>/sla/<int:sla_id>', methods=['DELETE'])
@csrf.exempt
@login_required
@project_member_required
def api_proje_sla_delete(project_id, sla_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        sla = SLA.query.filter_by(id=sla_id, project_id=project.id).first_or_404()
        db.session.delete(sla)
        db.session.commit()
        return jsonify({'success': True, 'message': 'SLA silindi'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'SLA silme hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_sla_delete]", 500)


@api_bp.route('/projeler/<int:project_id>/tekrarlayan/<int:recurring_id>', methods=['DELETE'])
@csrf.exempt
@login_required
@project_member_required
def api_proje_tekrarlayan_delete(project_id, recurring_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        recurring = RecurringTask.query.filter_by(id=recurring_id, project_id=project.id).first_or_404()
        db.session.delete(recurring)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Tekrarlayan görev silindi'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Tekrarlayan görev silme hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_tekrarlayan_delete]", 500)


# Kapasite planı güncelle
@api_bp.route('/projeler/<int:project_id>/kapasite/<int:plan_id>', methods=['PUT'])
@csrf.exempt
@login_required
@project_member_required
def api_proje_kapasite_update(project_id, plan_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        plan = CapacityPlan.query.filter_by(id=plan_id, project_id=project.id).first_or_404()
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        data = request.get_json(silent=True) or {}
        plan.user_id = data.get('user_id', plan.user_id)
        plan.weekly_hours = float(data.get('weekly_hours', plan.weekly_hours))
        plan.start_date = _parse_date_safe(data.get('start_date')) or plan.start_date
        plan.end_date = _parse_date_safe(data.get('end_date'))
        db.session.commit()
        return jsonify({'success': True, 'message': 'Kapasite planı güncellendi'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Kapasite güncelleme hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_kapasite_update]", 500)


# Entegrasyon güncelle
@api_bp.route('/projeler/<int:project_id>/integrations/<int:hook_id>', methods=['PUT'])
@csrf.exempt
@login_required
@project_member_required
def api_proje_integration_update(project_id, hook_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        hook = IntegrationHook.query.filter_by(id=hook_id, project_id=project.id).first_or_404()
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        data = request.get_json(silent=True) or {}
        hook.provider = data.get('provider', hook.provider)
        hook.url = data.get('url', hook.url)
        hook.is_active = bool(data.get('is_active', hook.is_active))
        db.session.commit()
        return jsonify({'success': True, 'message': 'Webhook güncellendi'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Webhook güncelleme hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_integration_update]", 500)


# Kural güncelle
@api_bp.route('/projeler/<int:project_id>/kurallar/<int:rule_id>', methods=['PUT'])
@csrf.exempt
@login_required
@project_member_required
def api_proje_kural_update(project_id, rule_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        rule = RuleDefinition.query.filter_by(id=rule_id, project_id=project.id).first_or_404()
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        data = request.get_json(silent=True) or {}
        rule.name = data.get('name', rule.name)
        rule.trigger = data.get('trigger', rule.trigger)
        if 'condition' in data:
            rule.condition_json = json.dumps(data.get('condition') or {})
        if 'actions' in data:
            rule.actions_json = json.dumps(data.get('actions') or [])
        rule.is_active = bool(data.get('is_active', rule.is_active))
        db.session.commit()
        return jsonify({'success': True, 'message': 'Kural güncellendi'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Kural güncelleme hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_kural_update]", 500)


# SLA güncelle
@api_bp.route('/projeler/<int:project_id>/sla/<int:sla_id>', methods=['PUT'])
@csrf.exempt
@login_required
@project_member_required
def api_proje_sla_update(project_id, sla_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        s = SLA.query.filter_by(id=sla_id, project_id=project.id).first_or_404()
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        data = request.get_json(silent=True) or {}
        s.name = data.get('name', s.name)
        s.target_hours = int(data.get('target_hours', s.target_hours))
        s.breach_policy = data.get('breach_policy', s.breach_policy)
        s.is_active = bool(data.get('is_active', s.is_active))
        db.session.commit()
        return jsonify({'success': True, 'message': 'SLA güncellendi'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'SLA güncelleme hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_sla_update]", 500)


# Tekrarlayan görev güncelle
@api_bp.route('/projeler/<int:project_id>/tekrarlayan/<int:recurring_id>', methods=['PUT'])
@csrf.exempt
@login_required
@project_member_required
def api_proje_tekrarlayan_update(project_id, recurring_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        r = RecurringTask.query.filter_by(id=recurring_id, project_id=project.id).first_or_404()
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        data = request.get_json(silent=True) or {}
        r.title = data.get('title', r.title)
        r.cron_expr = data.get('cron_expr', r.cron_expr)
        r.template_task_id = data.get('template_task_id', r.template_task_id)
        r.is_active = bool(data.get('is_active', r.is_active))
        db.session.commit()
        return jsonify({'success': True, 'message': 'Tekrarlayan görev güncellendi'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Tekrarlayan görev güncelleme hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_tekrarlayan_update]", 500)
# Proje ekibini getir (kapasite planı için gerekli)
@api_bp.route('/projeler/<int:project_id>/ekip', methods=['GET'])
@login_required
@project_observer_allowed
def api_proje_ekip(project_id, **kwargs):
    try:
        project = kwargs.get('project') or Project.query.get_or_404(project_id)
        team = []
        if project.manager:
            team.append({'id': project.manager.id, 'name': f'{project.manager.first_name} {project.manager.last_name}', 'role': 'Yönetici'})
        for member in project.members:
            team.append({'id': member.id, 'name': f'{member.first_name} {member.last_name}', 'role': 'Üye'})
        return jsonify({'success': True, 'team': team})
    except Exception as e:
        current_app.logger.error(f'Ekip API hatası: {e}', exc_info=True)
        return json_error(e, "[api_proje_ekip]", 500)
