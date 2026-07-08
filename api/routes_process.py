# -*- coding: utf-8 -*-
"""Surec (uyeler, PG dagitim, saglik skoru, PG veri) API rotalari

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
from utils.telemetry import log_event
from api.helpers import (
    _invalidate_executive_dashboard_cache,
    _resolve_project_leader_ids_api,
    _sync_project_leaders_api,
    _notify_project_team_changes_api,
    _parse_date_safe,
)


@api_bp.route('/surec/<int:surec_id>/uyeler', methods=['GET'])
@login_required
def api_surec_uyeler(surec_id: int):
    """Sürecin üyelerini/liderlerini getir (hedef dağıtım modali için)."""
    try:
        surec = Surec.query.options(joinedload(Surec.uyeler), joinedload(Surec.liderler)).get(surec_id)
        if not surec:
            return jsonify({'success': False, 'message': 'Süreç bulunamadı'}), 404

        # Bu liste hedef dağıtımında kullanıldığı için yönetim rolleri ile sınırla
        if current_user.sistem_rol == 'admin':
            pass
        elif current_user.sistem_rol in ['kurum_yoneticisi', 'ust_yonetim']:
            if surec.kurum_id != current_user.kurum_id:
                return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403
        else:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403

        lider_ids = {u.id for u in (surec.liderler or [])}
        uyeler = []
        for user in (surec.uyeler or []):
            ad_soyad = (f"{user.first_name or ''} {user.last_name or ''}").strip() or user.username
            uyeler.append({
                'id': user.id,
                'ad_soyad': ad_soyad,
                'rol': 'Lider' if user.id in lider_ids else 'Üye'
            })

        # Liderler listede yoksa ekle
        for lider in (surec.liderler or []):
            if any(u['id'] == lider.id for u in uyeler):
                continue
            ad_soyad = (f"{lider.first_name or ''} {lider.last_name or ''}").strip() or lider.username
            uyeler.append({
                'id': lider.id,
                'ad_soyad': ad_soyad,
                'rol': 'Lider'
            })

        # UI'da kararlı görünüm için isme göre sırala
        uyeler.sort(key=lambda x: (x.get('rol') != 'Lider', x.get('ad_soyad') or ''))

        return jsonify({'success': True, 'uyeler': uyeler})
    except Exception as e:
        current_app.logger.error(f'Süreç üyeleri getirme hatası: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/surec/<int:surec_id>/performans-gostergesi/<int:pg_id>/dagit', methods=['POST'])
@login_required
@csrf.exempt
def api_surec_pg_hedef_dagit(surec_id: int, pg_id: int):
    """Süreç PG hedefini seçili kullanıcılara dağıt (bireysel hedefler oluşturur/günceller)."""
    try:
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        data = request.get_json() or {}
        kullanicilar = data.get('kullanicilar') or []
        if not isinstance(kullanicilar, list) or len(kullanicilar) == 0:
            return jsonify({'success': False, 'message': 'Dağıtım listesi boş olamaz'}), 400

        surec = Surec.query.get(surec_id)
        if not surec:
            return jsonify({'success': False, 'message': 'Süreç bulunamadı'}), 404

        # Yönetim dışı kullanıcılar hedef dağıtamaz
        if current_user.sistem_rol == 'admin':
            pass
        elif current_user.sistem_rol in ['kurum_yoneticisi', 'ust_yonetim']:
            if surec.kurum_id != current_user.kurum_id:
                return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403
        else:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403

        surec_pg = SurecPerformansGostergesi.query.get(pg_id)
        if not surec_pg or surec_pg.surec_id != surec_id:
            return jsonify({'success': False, 'message': 'Performans göstergesi bulunamadı'}), 404

        for item in kullanicilar:
            try:
                user_id = int(item.get('user_id') or 0)
            except Exception:
                user_id = 0
            if user_id <= 0:
                return jsonify({'success': False, 'message': 'Geçersiz kullanıcı'}), 400

            hedef = item.get('hedef')
            hedef_str = str(hedef).strip() if hedef is not None else None

            user = User.query.get(user_id)
            if not user:
                return jsonify({'success': False, 'message': 'Kullanıcı bulunamadı'}), 404
            if current_user.sistem_rol != 'admin' and user.kurum_id != current_user.kurum_id:
                return jsonify({'success': False, 'message': 'Bu kullanıcı üzerinde işlem yetkiniz yok'}), 403

            bireysel_pg = BireyselPerformansGostergesi.query.filter_by(
                user_id=user_id,
                kaynak='Süreç',
                kaynak_surec_id=surec_id,
                kaynak_surec_pg_id=pg_id
            ).first()

            if not bireysel_pg:
                bireysel_pg = BireyselPerformansGostergesi(
                    user_id=user_id,
                    ad=surec_pg.ad,
                    aciklama=surec_pg.aciklama,
                    hedef_deger=hedef_str,
                    olcum_birimi=surec_pg.olcum_birimi,
                    periyot=surec_pg.periyot,
                    kaynak='Süreç',
                    kaynak_surec_id=surec_id,
                    kaynak_surec_pg_id=pg_id,
                    agirlik=surec_pg.agirlik if hasattr(surec_pg, 'agirlik') else 0,
                    onemli=surec_pg.onemli if hasattr(surec_pg, 'onemli') else False,
                    kodu=surec_pg.kodu if hasattr(surec_pg, 'kodu') else None
                )
                db.session.add(bireysel_pg)
            else:
                bireysel_pg.hedef_deger = hedef_str

        db.session.commit()
        
        log_event(
            current_app.logger,
            'kpi_targets_distributed',
            surec_id=surec_id,
            pg_id=pg_id,
            user_id=current_user.id,
        )
        return jsonify({'success': True, 'message': 'Hedefler başarıyla dağıtıldı'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Hedef dağıtma hatası: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500
@api_bp.route('/surec/<int:surec_id>/saglik-skoru', methods=['GET'])
@login_required
def api_surec_saglik_skoru(surec_id):
    """Süreç sağlık skorunu hesapla ve döndür"""
    try:
        yil = request.args.get('yil', datetime.now().year, type=int)
        
        # Süreç yetki kontrolü
        surec = Surec.query.get_or_404(surec_id)
        
        # Admin tüm süreçlere erişebilir
        if current_user.sistem_rol == 'admin':
            pass
        elif current_user.sistem_rol in ['kurum_yoneticisi', 'ust_yonetim']:
            if surec.kurum_id != current_user.kurum_id:
                return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403
        else:
            lider_mi = db.session.query(surec_liderleri).filter(
                surec_liderleri.c.surec_id == surec_id,
                surec_liderleri.c.user_id == current_user.id
            ).first() is not None
            
            uye_mi = db.session.query(surec_uyeleri).filter(
                surec_uyeleri.c.surec_id == surec_id,
                surec_uyeleri.c.user_id == current_user.id
            ).first() is not None
            
            if not (lider_mi or uye_mi):
                return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403
        
        # Sağlık skorunu hesapla
        from services.project_analytics import calculate_surec_saglik_skoru
        skor_sonucu = calculate_surec_saglik_skoru(surec_id, yil)
        
        if skor_sonucu is None:
            return jsonify({'success': False, 'message': 'Sağlık skoru hesaplanamadı'}), 500
        
        return jsonify({
            'success': True,
            **skor_sonucu
        })
    except Exception as e:
        current_app.logger.error(f'Süreç sağlık skoru API hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


# Risk Yönetimi API Endpoint'leri
@api_bp.route('/pg-veri/sil/<int:veri_id>', methods=['DELETE'])
@csrf.exempt
@login_required
@role_required(['admin', 'kurum_yoneticisi', 'ust_yonetim'])
def api_pg_veri_sil(veri_id):
    """PG veri silme (mock/gerçek)."""
    try:
        veri = PerformansGostergeVeri.query.get(veri_id)
        if not veri:
            return jsonify({'success': True, 'message': 'Veri bulunamadı (mock)'}), 200
        db.session.delete(veri)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Veri silindi'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"PG veri silme hatası: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/pg-veri/proje-gorevleri', methods=['GET'])
@csrf.exempt
@login_required
def api_pg_veri_proje_gorevleri():
    """PG veri proje görevleri (mock)."""
    return jsonify({'success': True, 'data': []})
