# -*- coding: utf-8 -*-
"""Paylaşılan import ve yardımcılar — main route paketi."""
from flask import render_template, redirect, url_for, current_app, jsonify, request, flash, send_file
from flask_login import login_required, current_user
from extensions import csrf, db
from app.models.portfolio_project import (
    Project,
    Task,
    TaskImpact,
    TaskComment,
    TaskMention,
    ProjectFile,
    ProjectRisk,
    TaskActivity,
    TimeEntry,
    project_related_processes,
    project_members,
    project_observers,
    project_leaders,
)
from app.models.legacy_bridge import (
    Surec, Kurum, User, AnaStrateji, AltStrateji, surec_liderleri, surec_uyeleri,
    DashboardLayout, BireyselPerformansGostergesi, SurecPerformansGostergesi,
    PerformansGostergeVeri, PerformansGostergeVeriAudit, BireyselFaaliyet, SurecFaaliyet, UserActivityLog,
    Deger, EtikKural, KalitePolitikasi,
    MainStrategy, SubStrategy, Process, StrategyProcessMatrix,
    # Faz 2 Modelleri
    ObjectiveComment, StrategicPlan, PlanItem, GembaWalk,
    Competency, UserCompetency, StrategicRisk, MudaFinding,
    # Faz 3 Modelleri
    CrisisMode, SafetyCheck, SuccessionPlan, OrgScenario, OrgChange, InfluenceScore, MarketIntel,
    WellbeingScore, SimulationScenario, DeepWorkSession,
    Persona, ProductSimulation, SmartContract, DaoProposal, DaoVote, MetaverseDepartment, LegacyKnowledge,
    # Faz 4 Modelleri
    Competitor, GameScenario, DoomsdayScenario, YearlyChronicle,
    # V67 Modelleri
    Activity,
    # Feedback Modülü
    Feedback
)
from datetime import datetime, timedelta, date
from io import BytesIO, StringIO
import json
import os
import re
import uuid
from werkzeug.utils import secure_filename
from utils.task_status import COMPLETED_STATUSES
from app.utils.project_rbac import role_required

from main.routes import main_bp
from main.deprecated import legacy_html_to_platform


def _get_user_project_role_for_page(project: Project):
    """Sayfa route'ları için proje rolü belirler.

    Returns:
        'manager' | 'member' | 'observer' | None
    """
    user_id = current_user.id

    if project.manager_id == user_id:
        return 'manager'

    if (
        db.session.query(project_leaders)
        .filter(project_leaders.c.project_id == project.id, project_leaders.c.user_id == user_id)
        .first()
    ):
        return 'manager'

    member_exists = db.session.query(project_members).filter(
        project_members.c.project_id == project.id,
        project_members.c.user_id == user_id,
    ).first() is not None
    if member_exists:
        return 'member'

    observer_exists = db.session.query(project_observers).filter(
        project_observers.c.project_id == project.id,
        project_observers.c.user_id == user_id,
    ).first() is not None
    if observer_exists:
        return 'observer'

    if hasattr(current_user, 'sistem_rol') and current_user.sistem_rol in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
        return 'manager'

    # İlişkili süreç liderleri manager kabul edilir
    try:
        related_ids = [p.id for p in (project.related_processes or [])]
        if related_ids:
            is_leader = db.session.query(surec_liderleri).filter(
                surec_liderleri.c.surec_id.in_(related_ids),
                surec_liderleri.c.user_id == user_id,
            ).first() is not None
            if is_leader:
                return 'manager'
    except Exception:
        pass

    return None


@main_bp.route('/')
def index():
    """Kök — oturum varsa launcher; yoksa tanıtım (marketing), doğrudan /login değil."""
    if current_user.is_authenticated:
        return redirect(url_for('app_bp.launcher'))
    try:
        return redirect(url_for('marketing_bp.index'))
    except Exception:
        return render_template('auth/login.html')


@main_bp.route('/offline')
def offline():
    """Offline sayfası - PWA için"""
    return render_template('offline.html')


def get_mock_data():
    """V67 DEPRECATED: Eski mock data fonksiyonu - Fallback için korunuyor.
    Artık Activity.query kullanılmalı. Bu fonksiyon sadece migration script'inde kullanılıyor.
    """
    # V67: Artık veritabanından çekiyoruz, bu fonksiyon sadece geriye uyumluluk için
    from app.models.legacy_bridge import Activity
    activities = Activity.query.order_by(Activity.date.desc()).all()
    
    # Dictionary formatına çevir (template uyumluluğu için)
    result = []
    for activity in activities:
        result.append({
            'id': activity.id,
            'source': activity.source,
            'project': activity.project.name if activity.project else activity.project_name or 'N/A',
            'subject': activity.subject,
            'status': activity.status,
            'priority': activity.priority,
            'date': activity.date.strftime('%Y-%m-%d') if activity.date else None
        })
    
    # Eğer veritabanında hiç kayıt yoksa, eski mock veriyi döndür (ilk kurulum için)
    if not result:
        return [
            {'id': 101, 'source': 'Redmine', 'project': 'Omega V66', 'subject': 'Login Güvenlik Yaması', 'status': 'Açık', 'priority': 'High', 'date': '2025-12-29'},
            {'id': 102, 'source': 'Jira', 'project': 'Mobil App', 'subject': 'Bildirim Hatası', 'status': 'Beklemede', 'priority': 'Normal', 'date': '2025-12-29'},
            {'id': 103, 'source': 'Dahili', 'project': 'Sunucu', 'subject': 'Disk Temizliği', 'status': 'Tamamlandı', 'priority': 'Low', 'date': '2025-12-28'},
            {'id': 104, 'source': 'Redmine', 'project': 'Omega V66', 'subject': 'DB Migrasyonu', 'status': 'Açık', 'priority': 'High', 'date': '2025-12-30'},
            {'id': 105, 'source': 'CRM', 'project': 'Satış', 'subject': 'Müşteri Listesi', 'status': 'Devam', 'priority': 'Normal', 'date': '2025-12-30'}
        ]
    
    return result


