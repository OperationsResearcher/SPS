# -*- coding: utf-8 -*-
"""
API Routes - Süreç Karnesi Endpoint'leri
"""
from flask import Blueprint, jsonify, request, current_app, send_file
from werkzeug.utils import secure_filename
import os
import uuid
from flask_login import login_required, current_user
from extensions import csrf
from decorators import project_access_required, project_manager_required, project_member_required, project_observer_allowed, role_required


def _invalidate_executive_dashboard_cache(kurum_id: int | None = None):
    """Executive dashboard cache invalidation placeholder.

    Not all deployments use a cache layer; this prevents runtime errors where
    the function is referenced.
    """
    try:
        # If a caching layer is introduced later, invalidate here.
        return
    except Exception:
        return
from models import (
    db, User, Kurum, Surec, AnaStrateji, AltStrateji,
    BireyselFaaliyet, BireyselPerformansGostergesi,
    PerformansGostergeVeri, PerformansGostergeVeriAudit, SurecPerformansGostergesi, SurecFaaliyet,
    FaaliyetTakip, surec_liderleri, surec_uyeleri,
    Notification, UserActivityLog, FavoriKPI, DashboardLayout,
    KullaniciYetki, Project, Task, TaskImpact, TaskComment, TaskMention, ProjectFile,  # Proje Yönetimi modelleri
    Tag, TaskSubtask, TimeEntry, TaskActivity, ProjectTemplate, TaskTemplate, Sprint, TaskSprint,  # Yeni modeller
    ProjectRisk, TaskDependency, IntegrationHook, RuleDefinition, SLA, RecurringTask, WorkingDay, CapacityPlan, RaidItem, TaskBaseline,  # Risk ve bağımlılıklar
    project_leaders,
)
from models import task_predecessors
from sqlalchemy import or_, and_, text, delete, insert
from sqlalchemy.orm import joinedload


def _resolve_project_leader_ids_api(data: dict, kurum_id: int) -> list:
    """JSON: manager_ids (liste) veya geriye dönük manager_id (tek)."""
    out: list = []
    raw = data.get("manager_ids")
    if isinstance(raw, list):
        for x in raw:
            try:
                out.append(int(x))
            except (TypeError, ValueError):
                continue
    elif data.get("manager_id") is not None:
        try:
            out.append(int(data["manager_id"]))
        except (TypeError, ValueError):
            pass
    seen_ids = set()
    result: list = []
    for uid in out:
        if uid in seen_ids:
            continue
        u = User.query.get(uid)
        if u and getattr(u, "kurum_id", None) == kurum_id:
            seen_ids.add(uid)
            result.append(uid)
    return result


def _sync_project_leaders_api(project: Project, kurum_id: int, leader_ids: list) -> None:
    if not leader_ids:
        return
    db.session.execute(delete(project_leaders).where(project_leaders.c.project_id == project.id))
    for uid in leader_ids:
        u = User.query.get(uid)
        if u and getattr(u, "kurum_id", None) == kurum_id:
            db.session.execute(insert(project_leaders).values(project_id=project.id, user_id=uid))
    project.manager_id = leader_ids[0]


from services.performance_service import (
    generatePeriyotVerileri, calculateHedefDeger, hesapla_durum,
    get_ceyrek_aylari, get_ay_ceyreği, get_ay_haftalari, get_ay_gunleri
)
from services.cpm_service import compute_cpm
from services.burn_service import burn_charts
from services.rule_engine_service import list_rules, save_rule, evaluate_rules
from services.digest_service import project_digest
from utils.karne_hesaplamalar import (
    hesapla_basari_puani, hesapla_agirlikli_basari_puani,
    hesapla_onceki_yil_ortalamasi, parse_basari_puani_araliklari
)
from datetime import datetime, timedelta, date
from utils.telemetry import log_event
from werkzeug.security import generate_password_hash
from io import BytesIO
from werkzeug.utils import secure_filename
import os
import uuid
import mimetypes
import json
import re


def _notify_project_team_changes_api(
    project: Project,
    kurum_id: int,
    old_leader_ids: set,
    old_member_ids: set,
) -> None:
    """Yeni atanan proje liderleri ve üyelerine uygulama içi + e-posta bildirimi."""
    try:
        from app.models.core import User as CoreUser
        from app_platform.services.notification_triggers import (
            notify_project_leaders_added,
            notify_project_members_added,
        )
    except Exception:
        return
    actor = CoreUser.query.get(current_user.id)
    if not actor:
        return
    new_l = set(project.leader_user_ids())
    new_m = set(project.member_user_ids())
    notify_project_leaders_added(project, list(new_l - old_leader_ids), actor, kurum_id)
    notify_project_members_added(project, list(new_m - old_member_ids), actor, kurum_id)


def _parse_date_safe(val):
    if not val:
        return None
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    try:
        return datetime.strptime(str(val), '%Y-%m-%d').date()
    except Exception:
        return None

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/activities', methods=['GET'])
@login_required
def get_user_activities():
    """Kullanıcının atandığı görevleri ve aktiviteleri getir"""
    try:
        assigned_to = request.args.get('assigned_to', type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Sadece kendi aktivitelerini veya admin tüm aktiviteleri görebilir
        if assigned_to and assigned_to != current_user.id and current_user.sistem_rol != 'admin':
            return jsonify({'error': 'Yetkisiz erişim'}), 403
        
        user_id = assigned_to if assigned_to else current_user.id
        
        # Son aktiviteleri getir (TaskActivity)
        activities = TaskActivity.query.filter_by(user_id=user_id).order_by(
            TaskActivity.created_at.desc()
        ).limit(limit).all()
        
        result = []
        for activity in activities:
            result.append({
                'id': activity.id,
                'task_id': activity.task_id,
                'activity_type': activity.activity_type,
                'details': activity.details,
                'created_at': activity.created_at.isoformat() if activity.created_at else None
            })
        
        return jsonify({'success': True, 'activities': result})
    
    except Exception as e:
        current_app.logger.error(f"Activities API hatası: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/ai/insights', methods=['GET'])
@login_required
def get_ai_insights():
    """AI Insights - Placeholder endpoint"""
    try:
        # TODO: Gerçek AI insights implementasyonu
        return jsonify({
            'success': True,
            'insights': [],
            'message': 'AI insights özelliği geliştirme aşamasında'
        })
    
    except Exception as e:
        current_app.logger.error(f"AI Insights API hatası: {e}")
        return jsonify({'error': str(e)}), 500






def _default_weight(weight, sibling_count):
    """Skor motoru ile uyumlu: ağırlık atanmamışsa 100 / kardeş sayısı."""
    if sibling_count <= 0:
        return 100.0
    if weight is not None and weight > 0:
        return min(100.0, max(0.0, float(weight)))
    return 100.0 / sibling_count


@api_bp.route('/vision-score', methods=['GET'])
@login_required
def api_vision_score():
    """Point-in-time Vizyon puanı (0-100). as_of_date: YYYY-MM-DD (opsiyonel, varsayılan bugün).
    Yanıtta surec_scores, pg_scores ve isimli listeler (ana_stratejiler, alt_stratejiler, surecler, performans_gostergeleri) ile vizyona katkı (ana_strateji) döner."""
    try:
        from datetime import datetime as dt
        from services.score_engine_service import compute_vision_score
        kurum_id = getattr(current_user, 'kurum_id', None)
        if not kurum_id:
            return jsonify({'success': False, 'message': 'Kurum bilgisi yok'}), 400
        as_of_str = request.args.get('as_of_date')
        as_of_date = None
        if as_of_str:
            try:
                as_of_date = dt.strptime(as_of_str.strip()[:10], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': 'Geçersiz as_of_date (YYYY-MM-DD beklenir)'}), 400
        persist = request.args.get('persist', '').lower() in ('1', 'true', 'yes')
        result = compute_vision_score(kurum_id, as_of_date, persist_pg_scores=persist)
        ana_scores = result.get('ana_strateji_scores', {})
        alt_scores = result.get('alt_strateji_scores', {})
        surec_scores = result.get('surec_scores', {})
        pg_scores = result.get('pg_scores', {})

        # İsimli listeler ve vizyona katkı
        ana_list = AnaStrateji.query.filter_by(kurum_id=kurum_id).order_by(AnaStrateji.id).all()
        n_ana = len(ana_list)
        w_sum_ana = sum(_default_weight(a.weight, n_ana) for a in ana_list) or 1.0
        ana_stratejiler = []
        for a in ana_list:
            sc = ana_scores.get(a.id, 0.0)
            w = _default_weight(a.weight, n_ana)
            vizyona_katki = round((w / w_sum_ana) * sc, 2) if w_sum_ana else 0.0
            ana_stratejiler.append({
                'id': a.id,
                'ad': a.ad or '',
                'score': round(sc, 2),
                'agirlik': round(w, 2),
                'vizyona_katki': vizyona_katki,
            })

        alt_ids = list(alt_scores.keys())
        alt_stratejiler = []
        if alt_ids:
            for alt in AltStrateji.query.filter(AltStrateji.id.in_(alt_ids)).order_by(AltStrateji.id).all():
                alt_stratejiler.append({
                    'id': alt.id,
                    'ad': alt.ad or '',
                    'ana_strateji_id': alt.ana_strateji_id,
                    'score': round(alt_scores.get(alt.id, 0.0), 2),
                })

        surec_ids = list(surec_scores.keys())
        surecler = []
        if surec_ids:
            for s in Surec.query.filter(Surec.id.in_(surec_ids), Surec.silindi == False).order_by(Surec.id).all():
                surecler.append({
                    'id': s.id,
                    'ad': s.ad or '',
                    'score': round(surec_scores.get(s.id, 0.0), 2),
                })

        pg_ids = list(pg_scores.keys())
        performans_gostergeleri = []
        if pg_ids:
            for pg in SurecPerformansGostergesi.query.filter(SurecPerformansGostergesi.id.in_(pg_ids)).order_by(SurecPerformansGostergesi.id).all():
                performans_gostergeleri.append({
                    'id': pg.id,
                    'ad': pg.ad or '',
                    'surec_id': pg.surec_id,
                    'score': round(pg_scores.get(pg.id, 0.0), 2),
                })

        return jsonify({
            'success': True,
            'vision_score': result['vision_score'],
            'as_of_date': result['as_of_date'],
            'kurum_id': kurum_id,
            'ana_strateji_scores': ana_scores,
            'alt_strateji_scores': alt_scores,
            'surec_scores': surec_scores,
            'pg_scores': pg_scores,
            'ana_stratejiler': ana_stratejiler,
            'alt_stratejiler': alt_stratejiler,
            'surecler': surecler,
            'performans_gostergeleri': performans_gostergeleri,
        })
    except Exception as e:
        current_app.logger.exception('Vision score hesaplanamadı: %s', e)
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/vision-score/recalc', methods=['POST'])
@login_required
def api_vision_score_recalc():
    """Tüm hiyerarşide vizyon puanını yeniden hesapla ve PG calculated_score alanlarını güncelle (Skor Motoru aktif)."""
    try:
        from services.score_engine_service import recalc_on_pg_data_change
        kurum_id = getattr(current_user, 'kurum_id', None)
        if not kurum_id:
            return jsonify({'success': False, 'message': 'Kurum bilgisi yok'}), 400
        result = recalc_on_pg_data_change(kurum_id)
        return jsonify({
            'success': True,
            'vision_score': result.get('vision_score', 0),
            'as_of_date': result.get('as_of_date'),
            'kurum_id': kurum_id,
            'message': 'Vizyon puanı tüm hiyerarşide yeniden hesaplandı.',
        })
    except Exception as e:
        current_app.logger.exception('Vision score recalc hatası: %s', e)
        return jsonify({'success': False, 'message': str(e)}), 500


def _build_vision_score_payload_for_ai(kurum_id, as_of_date=None):
    """Skor motoru çıktısını AI Coach'a gönderilecek payload olarak döndürür (surec/PG ağırlıkları dahil)."""
    from datetime import datetime as dt
    from services.score_engine_service import compute_vision_score
    result = compute_vision_score(kurum_id, as_of_date, persist_pg_scores=False)
    ana_scores = result.get('ana_strateji_scores', {})
    alt_scores = result.get('alt_strateji_scores', {})
    surec_scores = result.get('surec_scores', {})
    pg_scores = result.get('pg_scores', {})

    ana_list = AnaStrateji.query.filter_by(kurum_id=kurum_id).order_by(AnaStrateji.id).all()
    n_ana = len(ana_list)
    w_sum_ana = sum(_default_weight(a.weight, n_ana) for a in ana_list) or 1.0
    ana_stratejiler = []
    for a in ana_list:
        sc = ana_scores.get(a.id, 0.0)
        w = _default_weight(a.weight, n_ana)
        vizyona_katki = round((w / w_sum_ana) * sc, 2) if w_sum_ana else 0.0
        ana_stratejiler.append({
            'id': a.id, 'ad': a.ad or '', 'score': round(sc, 2),
            'agirlik': round(w, 2), 'vizyona_katki': vizyona_katki,
        })

    surec_ids = list(surec_scores.keys())
    surecler = []
    if surec_ids:
        for s in Surec.query.filter(Surec.id.in_(surec_ids), Surec.silindi == False).order_by(Surec.id).all():
            sw = float(s.weight) if s.weight is not None else None
            surecler.append({
                'id': s.id, 'ad': s.ad or '', 'score': round(surec_scores.get(s.id, 0.0), 2),
                'agirlik': round(sw, 2) if sw is not None else None,
            })

    pg_ids = list(pg_scores.keys())
    performans_gostergeleri = []
    if pg_ids:
        for pg in SurecPerformansGostergesi.query.filter(SurecPerformansGostergesi.id.in_(pg_ids)).order_by(SurecPerformansGostergesi.id).all():
            w = float(pg.weight) if pg.weight is not None else None
            performans_gostergeleri.append({
                'id': pg.id, 'ad': pg.ad or '', 'surec_id': pg.surec_id,
                'score': round(pg_scores.get(pg.id, 0.0), 2),
                'agirlik': round(w, 2) if w is not None else None,
            })

    return {
        'vision_score': result['vision_score'],
        'as_of_date': result['as_of_date'],
        'kurum_id': kurum_id,
        'ana_stratejiler': ana_stratejiler,
        'surecler': surecler,
        'performans_gostergeleri': performans_gostergeleri,
    }


@api_bp.route('/ai-coach/analyze', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def api_ai_coach_analyze():
    """Skor motoru verilerini hesaplayıp AI Coach (Gemini) ile analiz ettirir; Markdown yanıt döner."""
    try:
        kurum_id = getattr(current_user, 'kurum_id', None)
        if not kurum_id:
            return jsonify({'success': False, 'message': 'Kurum bilgisi yok'}), 400
        as_of_str = request.args.get('as_of_date') or (request.get_json() or {}).get('as_of_date')
        as_of_date = None
        if as_of_str:
            from datetime import datetime as dt
            try:
                as_of_date = dt.strptime(str(as_of_str).strip()[:10], '%Y-%m-%d').date()
            except ValueError:
                pass
        payload = _build_vision_score_payload_for_ai(kurum_id, as_of_date)
        from services.ai_coach_service import analyze_strategic_performance
        result = analyze_strategic_performance(payload)
        if not result.get('success'):
            return jsonify({
                'success': False,
                'message': result.get('error', 'Analiz başarısız.'),
                'analysis_markdown': None,
            }), 200
        return jsonify({
            'success': True,
            'analysis_markdown': result.get('analysis_markdown'),
            'vision_score': payload.get('vision_score'),
            'as_of_date': payload.get('as_of_date'),
            'usage': result.get('usage'),
        })
    except Exception as e:
        current_app.logger.exception('AI Coach analyze hatası: %s', e)
        return jsonify({'success': False, 'message': str(e), 'analysis_markdown': None}), 500


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
            'task_updated',
            task_id=task.id,
            project_id=project_id,
            user_id=current_user.id,
            status=task.status,
        )
        return jsonify({'success': True, 'message': 'Hedefler başarıyla dağıtıldı'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Hedef dağıtma hatası: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500












@api_bp.route('/kurum/upload-logo', methods=['POST'])
@csrf.exempt
@login_required
def api_kurum_upload_logo():
    """Kurum logosunu yükle"""
    try:
        from werkzeug.utils import secure_filename
        from utils.file_validation import validate_uploaded_file
        import os
        import uuid
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'Dosya seçilmedi!'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Dosya seçilmedi!'}), 400
        
        # Güvenli dosya validasyonu (extension + MIME type)
        is_valid, error_msg, mime_type = validate_uploaded_file(file, max_size=5 * 1024 * 1024)  # 5MB max for logos
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        # Güvenli dosya adı oluştur
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Upload klasörünü oluştur
        upload_folder = os.path.join('static', 'uploads', 'logos')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Dosyayı kaydet
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Eski logo dosyasını sil (varsa ve static klasöründeyse)
        kurum = current_user.kurum
        if kurum.logo_url:
            old_logo = kurum.logo_url
            if old_logo.startswith('/static/') or old_logo.startswith('static/'):
                old_path = old_logo.lstrip('/')
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except Exception as e:
                        current_app.logger.warning(f'Eski logo silinemedi: {e}')
        
        # Veritabanında güncelle
        logo_url = f'/static/uploads/logos/{unique_filename}'
        kurum.logo_url = logo_url
        db.session.commit()
        
        current_app.logger.info(f'Kurum logosu güncellendi: {kurum.kisa_ad} -> {unique_filename}')
        
        return jsonify({
            'success': True,
            'message': 'Logo başarıyla yüklendi!',
            'logo_url': logo_url
        }), 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Logo yükleme hatası: {str(e)} - Kullanıcı: {current_user.username}')
        return jsonify({'success': False, 'message': f'Logo yüklenirken hata oluştu: {str(e)}'}), 500, {'Content-Type': 'application/json'}


@api_bp.route('/kurum/<int:kurum_id>/alt-stratejiler', methods=['GET'])
@login_required
@csrf.exempt
def api_kurum_alt_stratejiler(kurum_id):
    """Kurumun tüm alt stratejilerini getir (isteğe bağlı olarak süreçle ilgili olanları filtrele)
    
    Query Parameters:
        - surec_id (int, optional): Belirtilirse, sadece bu süreçle ilgili alt stratejiler döndürülür
    """
    try:
        surec_id = request.args.get('surec_id', type=int)
        current_app.logger.info(f'Kurum alt stratejileri isteği: kurum_id={kurum_id}, surec_id={surec_id}, kullanıcı_kurum_id={current_user.kurum_id}')
        
        # Yetki kontrolü - kullanıcı aynı kurumda olmalı
        if kurum_id != current_user.kurum_id:
            current_app.logger.warning(f'Yetki hatası: kurum_id={kurum_id}, kullanıcı_kurum_id={current_user.kurum_id}')
            return jsonify({'success': False, 'message': 'Bu kuruma erişim yetkiniz yok'}), 403
        
        # Süreçle ilgili olanları filtrele
        if surec_id:
            # Sürecin tanımladığı alt stratejileri al
            surec = Surec.query.filter_by(id=surec_id, silindi=False).first()
            if not surec:
                current_app.logger.warning(f'Süreç bulunamadı: surec_id={surec_id}')
                return jsonify({'success': True, 'alt_stratejiler': []})
            
            # Süreçle ilgili alt stratejileri topla
            alt_stratejiler = []
            for alt_strateji in surec.alt_stratejiler:
                ana_strateji = alt_strateji.ana_strateji
                if ana_strateji:
                    alt_stratejiler.append({
                        'id': alt_strateji.id,
                        'ad': alt_strateji.ad,
                        'code': alt_strateji.code,
                        'ana_strateji': {
                            'id': ana_strateji.id,
                            'ad': ana_strateji.ad,
                            'code': ana_strateji.code
                        }
                    })
            
            current_app.logger.info(f'Süreç {surec_id} ile ilgili alt strateji sayısı: {len(alt_stratejiler)}')
        else:
            # Kurumun tüm alt stratejilerini getir
            ana_stratejiler = AnaStrateji.query.options(
                joinedload(AnaStrateji.alt_stratejiler)
            ).filter_by(kurum_id=kurum_id).all()
            
            current_app.logger.info(f'Bulunan ana strateji sayısı: {len(ana_stratejiler)}')
            
            # Tüm alt stratejileri topla
            alt_stratejiler = []
            for ana_strateji in ana_stratejiler:
                current_app.logger.info(f'Ana strateji: {ana_strateji.ad} (ID: {ana_strateji.id}), alt strateji sayısı: {len(ana_strateji.alt_stratejiler)}')
                for alt_strateji in ana_strateji.alt_stratejiler:
                    alt_stratejiler.append({
                        'id': alt_strateji.id,
                        'ad': alt_strateji.ad,
                        'code': alt_strateji.code,
                        'ana_strateji': {
                            'id': ana_strateji.id,
                            'ad': ana_strateji.ad,
                            'code': ana_strateji.code
                        }
                    })
            
            current_app.logger.info(f'Toplam alt strateji sayısı: {len(alt_stratejiler)}')
        
        return jsonify({
            'success': True,
            'alt_stratejiler': alt_stratejiler
        })
    except Exception as e:
        current_app.logger.error(f'Kurum alt stratejileri getirme hatası: {e}')
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Hata: {str(e)}'}), 500


@api_bp.route('/kurum/update-logo', methods=['POST'])
@csrf.exempt
@login_required
def api_kurum_update_logo():
    """Kurum logo URL'sini güncelle"""
    try:
        data = request.get_json()
        logo_url = data.get('logo_url', '').strip()
        
        if not logo_url:
            return jsonify({'success': False, 'message': 'Logo URL\'si boş olamaz!'}), 400
        
        kurum = current_user.kurum
        kurum.logo_url = logo_url
        db.session.commit()
        
        current_app.logger.info(f'Kurum logo URL\'si güncellendi: {kurum.kisa_ad} -> {logo_url}')
        
        return jsonify({
            'success': True,
            'message': 'Logo URL\'si başarıyla güncellendi!',
            'logo_url': logo_url
        }), 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Logo URL güncelleme hatası: {str(e)} - Kullanıcı: {current_user.username}')
        return jsonify({'success': False, 'message': f'Logo URL\'si güncellenirken hata oluştu: {str(e)}'}), 500, {'Content-Type': 'application/json'}


@api_bp.route('/kurum/toggle-guide-system', methods=['POST'])
@csrf.exempt
@login_required
def api_kurum_toggle_guide_system():
    """Kurum için rehber sistemini aç/kapat"""
    try:
        # Yetki kontrolü - Sadece kurum yöneticileri ve admin
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403
        
        data = request.get_json()
        show_guide_system = data.get('show_guide_system', True)
        
        kurum = current_user.kurum
        if not kurum:
            return jsonify({'success': False, 'message': 'Kurum bulunamadı'}), 404
        
        kurum.show_guide_system = show_guide_system
        db.session.commit()
        
        current_app.logger.info(f'Kurum rehber sistemi güncellendi: {kurum.kisa_ad} -> {"Aktif" if show_guide_system else "Devre Dışı"}')
        
        return jsonify({
            'success': True,
            'message': f'Rehber sistemi {"aktif" if show_guide_system else "devre dışı"} edildi.',
            'show_guide_system': show_guide_system
        }), 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Rehber sistemi güncelleme hatası: {str(e)} - Kullanıcı: {current_user.username}')
        return jsonify({'success': False, 'message': f'Rehber sistemi güncellenirken hata oluştu: {str(e)}'}), 500, {'Content-Type': 'application/json'}


# ============================================================================
# PROJE YÖNETİMİ API ENDPOINT'LERİ
# ============================================================================

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
            except Exception:
                pass
            
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
                except Exception:
                    pass
            
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


@api_bp.route('/projeler/<int:project_id>', methods=['PUT'])
@csrf.exempt
@login_required
def api_proje_guncelle(project_id):
    """Proje güncelle"""
    try:
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        
        data = request.get_json()
        project = Project.query.get_or_404(project_id)
        
        # Yetki kontrolü
        if project.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu projeyi güncelleme yetkiniz yok'}), 403
        
        old_leader_ids = set(project.leader_user_ids())
        old_member_ids = set(project.member_user_ids())
        
        # Proje bilgilerini güncelle
        if 'name' in data:
            project.name = data['name'].strip()
        if 'description' in data:
            project.description = data['description'].strip() if data.get('description') else None
        if 'manager_ids' in data or 'manager_id' in data:
            lids = _resolve_project_leader_ids_api(data, current_user.kurum_id)
            if lids:
                _sync_project_leaders_api(project, current_user.kurum_id, lids)
        
        # İlişkili süreçleri güncelle
        if 'related_process_ids' in data:
            project.related_processes.clear()
            for surec_id in data.get('related_process_ids', []):
                surec = Surec.query.get(surec_id)
                if surec and surec.kurum_id == current_user.kurum_id:
                    project.related_processes.append(surec)
        
        # Üyeleri güncelle
        if 'member_ids' in data:
            project.members.clear()
            for user_id in data.get('member_ids', []):
                user = User.query.get(user_id)
                if user and user.kurum_id == current_user.kurum_id:
                    project.members.append(user)
        
        # Gözlemcileri güncelle
        if 'observer_ids' in data:
            project.observers.clear()
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
        current_app.logger.error(f'Proje güncelleme hatası: {e}')
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

@api_bp.route('/projeler/<int:project_id>/dosyalar', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def api_proje_dosyalar(project_id):
    """Proje dosyalarını getir veya yeni dosya yükle"""
    try:
        project = Project.query.get_or_404(project_id)
        
        # Yetki kontrolü
        if project.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu projeye erişim yetkiniz yok'}), 403
        
        if request.method == 'GET':
            # Dosyaları getir
            # Sadece aktif dosyaları getir (soft-delete) - en son versiyonları göster
            files = ProjectFile.query.filter_by(
                project_id=project_id,
                is_active=True
            ).order_by(ProjectFile.file_name, ProjectFile.version.desc()).all()
            
            # Aynı isimde birden fazla versiyon varsa sadece en son versiyonu göster
            unique_files = {}
            for file in files:
                if file.file_name not in unique_files:
                    unique_files[file.file_name] = file
            
            files = list(unique_files.values())
            files.sort(key=lambda x: x.created_at, reverse=True)
            
            file_list = []
            for file in files:
                user = User.query.get(file.user_id)
                user_name = f"{user.first_name} {user.last_name}" if user and user.first_name else (user.username if user else 'Bilinmiyor')
                
                file_list.append({
                    'id': file.id,
                    'file_name': file.file_name,
                    'file_path': file.file_path,
                    'file_size': file.file_size,
                    'file_type': file.file_type,
                    'description': file.description,
                    'version': file.version if hasattr(file, 'version') else 1,
                    'user_name': user_name,
                    'created_at': file.created_at.isoformat() if file.created_at else None
                })
            
            return jsonify({
                'success': True,
                'files': file_list
            })
        else:  # POST
            # Dosya yükleme
            if 'files' not in request.files:
                return jsonify({'success': False, 'message': 'Dosya bulunamadı'}), 400
            
            files = request.files.getlist('files')
            if not files or files[0].filename == '':
                return jsonify({'success': False, 'message': 'Dosya seçilmedi'}), 400
            
            # Dosya sayısı kontrolü (maksimum 10 dosya)
            MAX_FILES = 10
            if len(files) > MAX_FILES:
                return jsonify({'success': False, 'message': f'Maksimum {MAX_FILES} dosya yükleyebilirsiniz'}), 400
            
            description = request.form.get('description', '').strip()
            
            # Dosya boyutu ve tip kontrolü
            MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
            ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.gif', '.txt', '.zip', '.rar'}
            ALLOWED_MIME_TYPES = {
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'image/jpeg',
                'image/jpg',
                'image/png',
                'image/gif',
                'text/plain',
                'application/zip',
                'application/x-rar-compressed'
            }
            
            upload_folder = os.path.join('static', 'uploads', 'project_files')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            uploaded_count = 0
            errors = []
            
            # MIME type validasyonu için import
            from utils.file_validation import validate_uploaded_file
            
            for file in files:
                if not file or not file.filename:
                    continue
                
                try:
                    # Güvenli dosya validasyonu (extension + MIME type + boyut)
                    is_valid, error_msg, mime_type = validate_uploaded_file(file, max_size=MAX_FILE_SIZE)
                    if not is_valid:
                        errors.append(f"'{file.filename}': {error_msg}")
                        continue
                    
                    filename = secure_filename(file.filename)
                    
                    # Unique filename oluştur
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    file_path = os.path.join(upload_folder, unique_filename)
                    
                    # Dosyayı kaydet
                    file.save(file_path)
                    
                    # Dosya boyutunu al
                    file_size = os.path.getsize(file_path)
                    
                    # MIME type'ı kullan (validasyon fonksiyonundan gelen)
                    file_type = mime_type or 'application/octet-stream'
                    
                    # Aynı isimde dosya var mı kontrol et (versiyonlama için)
                    existing_file = ProjectFile.query.filter_by(
                        project_id=project_id,
                        file_name=filename,
                        is_active=True
                    ).order_by(ProjectFile.version.desc()).first()
                    
                    # Versiyon belirle
                    version = 1
                    parent_file_id = None
                    if existing_file:
                        version = existing_file.version + 1
                        parent_file_id = existing_file.id
                    
                    # Veritabanına kaydet
                    project_file = ProjectFile(
                        project_id=project_id,
                        user_id=current_user.id,
                        file_name=filename,
                        file_path=f'/static/uploads/project_files/{unique_filename}',
                        file_size=file_size,
                        file_type=file_type or 'application/octet-stream',
                        description=description if description else None,
                        version=version,
                        parent_file_id=parent_file_id,
                        is_active=True,
                        scope='PROJECT',  # Proje dosyası
                        category=None  # Proje dosyaları için kategori yok
                    )
                    db.session.add(project_file)
                    uploaded_count += 1
                    
                except Exception as e:
                    current_app.logger.error(f"Dosya yükleme hatası ({filename}): {str(e)}")
                    errors.append(f"'{filename}': {str(e)}")
                    continue
            
            # Eğer hiç dosya yüklenmediyse hata döndür
            if uploaded_count == 0:
                error_message = 'Hiç dosya yüklenemedi. ' + '; '.join(errors) if errors else 'Dosya yükleme hatası'
                return jsonify({'success': False, 'message': error_message}), 400
            
            db.session.commit()
            
            # Başarılı yüklemeler + hatalar varsa uyarı
            message = f'{uploaded_count} dosya başarıyla yüklendi.'
            if errors:
                message += f' Bazı dosyalar yüklenemedi: {"; ".join(errors[:3])}'  # İlk 3 hatayı göster
            
            return jsonify({
                'success': True,
                'message': message,
                'uploaded_count': uploaded_count
            })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Proje dosyaları hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/dokuman-merkezi', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def api_dokuman_merkezi():
    """Kurumsal dosya yönetimi API"""
    try:
        if request.method == 'GET':
            # Kurumsal dosyaları getir
            from sqlalchemy import or_, and_
            corporate_files = ProjectFile.query.filter(
                or_(
                    ProjectFile.scope == 'CORPORATE',
                    and_(ProjectFile.scope == 'PROJECT', ProjectFile.project_id.is_(None))
                ),
                ProjectFile.is_active == True
            ).order_by(ProjectFile.category, ProjectFile.file_name).all()
            
            file_list = []
            for file in corporate_files:
                user = User.query.get(file.user_id)
                user_name = f"{user.first_name} {user.last_name}" if user and user.first_name else (user.username if user else 'Bilinmiyor')
                
                file_list.append({
                    'id': file.id,
                    'file_name': file.file_name,
                    'file_path': file.file_path,
                    'file_size': file.file_size,
                    'file_type': file.file_type,
                    'description': file.description,
                    'category': file.category,
                    'user_name': user_name,
                    'created_at': file.created_at.isoformat() if file.created_at else None
                })
            
            return jsonify({
                'success': True,
                'files': file_list
            })
        
        else:  # POST - Dosya yükleme
            # Yetki kontrolü - Sadece yöneticiler yükleyebilir
            if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi']:
                return jsonify({'success': False, 'message': 'Kurumsal dosya yüklemek için yönetici yetkisi gereklidir'}), 403
            
            if 'files' not in request.files:
                return jsonify({'success': False, 'message': 'Dosya bulunamadı'}), 400
            
            files = request.files.getlist('files')
            if not files or files[0].filename == '':
                return jsonify({'success': False, 'message': 'Dosya seçilmedi'}), 400
            
            category = request.form.get('category', '').strip() or None
            description = request.form.get('description', '').strip() or None
            
            # Dosya yükleme işlemi (proje dosyaları ile aynı mantık)
            MAX_FILES = 10
            MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
            ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.gif', '.txt', '.zip', '.rar'}
            
            upload_folder = os.path.join('static', 'uploads', 'corporate_files')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            uploaded_count = 0
            errors = []
            
            # MIME type validasyonu için import
            from utils.file_validation import validate_uploaded_file
            
            for file in files[:MAX_FILES]:
                if not file or not file.filename:
                    continue
                
                try:
                    # Güvenli dosya validasyonu (extension + MIME type + boyut)
                    is_valid, error_msg, mime_type = validate_uploaded_file(file, max_size=MAX_FILE_SIZE)
                    if not is_valid:
                        errors.append(f"'{file.filename}': {error_msg}")
                        continue
                    
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    file_path = os.path.join(upload_folder, unique_filename)
                    file.save(file_path)
                    
                    file_size = os.path.getsize(file_path)
                    file_type = mime_type or 'application/octet-stream'
                    
                    # Kurumsal dosya kaydet
                    corporate_file = ProjectFile(
                        project_id=None,  # Kurumsal dosya için NULL
                        user_id=current_user.id,
                        file_name=filename,
                        file_path=f'/static/uploads/corporate_files/{unique_filename}',
                        file_size=file_size,
                        file_type=file_type or 'application/octet-stream',
                        description=description,
                        version=1,
                        is_active=True,
                        scope='CORPORATE',
                        category=category
                    )
                    db.session.add(corporate_file)
                    uploaded_count += 1
                
                except Exception as e:
                    current_app.logger.error(f"Kurumsal dosya yükleme hatası ({filename}): {str(e)}")
                    errors.append(f"'{filename}': {str(e)}")
                    continue
            
            if uploaded_count == 0:
                error_message = 'Hiç dosya yüklenemedi. ' + '; '.join(errors) if errors else 'Dosya yükleme hatası'
                return jsonify({'success': False, 'message': error_message}), 400
            
            db.session.commit()
            
            message = f'{uploaded_count} dosya başarıyla yüklendi.'
            if errors:
                message += f' Bazı dosyalar yüklenemedi: {"; ".join(errors[:3])}'
            
            return jsonify({
                'success': True,
                'message': message,
                'uploaded_count': uploaded_count
            })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Doküman merkezi API hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/dokuman-merkezi/<int:file_id>/indir', methods=['GET'])
@login_required
def api_dokuman_merkezi_indir(file_id):
    """Kurumsal dosyayı indir"""
    try:
        corporate_file = ProjectFile.query.get_or_404(file_id)
        
        # Kurumsal dosya kontrolü
        if corporate_file.scope != 'CORPORATE' and corporate_file.project_id is not None:
            return jsonify({'success': False, 'message': 'Bu dosya kurumsal dosya değil'}), 403
        
        # Dosya yolunu kontrol et
        file_path = corporate_file.file_path.lstrip('/')
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'message': 'Dosya bulunamadı'}), 404
        
        return send_file(file_path, as_attachment=True, download_name=corporate_file.file_name)
    
    except Exception as e:
        current_app.logger.error(f'Kurumsal dosya indirme hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/dokuman-merkezi/<int:file_id>', methods=['DELETE'])
@csrf.exempt
@login_required
def api_dokuman_merkezi_sil(file_id):
    """Kurumsal dosyayı sil (soft delete)"""
    try:
        # Yetki kontrolü - Sadece yöneticiler silebilir
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi']:
            return jsonify({'success': False, 'message': 'Kurumsal dosya silmek için yönetici yetkisi gereklidir'}), 403
        
        corporate_file = ProjectFile.query.get_or_404(file_id)
        
        # Kurumsal dosya kontrolü
        if corporate_file.scope != 'CORPORATE' and corporate_file.project_id is not None:
            return jsonify({'success': False, 'message': 'Bu dosya kurumsal dosya değil'}), 403
        
        # Soft delete
        corporate_file.is_active = False
        corporate_file.deleted_at = datetime.utcnow()
        corporate_file.deleted_by_id = current_user.id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Dosya başarıyla silindi'
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Kurumsal dosya silme hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/projeler/<int:project_id>/dosyalar/<int:file_id>/indir', methods=['GET'])
@login_required
def api_proje_dosya_indir(project_id, file_id):
    """Proje dosyasını indir"""
    try:
        project = Project.query.get_or_404(project_id)
        project_file = ProjectFile.query.get_or_404(file_id)
        
        # Yetki kontrolü
        if project.kurum_id != current_user.kurum_id or project_file.project_id != project_id:
            return jsonify({'success': False, 'message': 'Bu dosyaya erişim yetkiniz yok'}), 403
        
        # Dosya yolunu oluştur
        file_path = project_file.file_path.lstrip('/')
        absolute_path = os.path.join('static', 'uploads', 'project_files', os.path.basename(project_file.file_path))
        
        if not os.path.exists(absolute_path):
            return jsonify({'success': False, 'message': 'Dosya bulunamadı'}), 404
        
        return send_file(absolute_path, as_attachment=True, download_name=project_file.file_name)
    except Exception as e:
        current_app.logger.error(f'Dosya indirme hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/projeler/<int:project_id>/dosyalar/<int:file_id>', methods=['DELETE'])
@csrf.exempt
@login_required
def api_proje_dosya_sil(project_id, file_id):
    """Proje dosyasını soft-delete ile sil"""
    try:
        project = Project.query.get_or_404(project_id)
        project_file = ProjectFile.query.get_or_404(file_id)
        
        # Yetki kontrolü (sadece yönetici veya dosyayı yükleyen silebilir)
        if project.kurum_id != current_user.kurum_id or project_file.project_id != project_id:
            return jsonify({'success': False, 'message': 'Bu dosyaya erişim yetkiniz yok'}), 403
        
        # Sadece yönetici veya dosyayı yükleyen silebilir
        from decorators import _get_user_project_role
        user_role = _get_user_project_role(project, current_user.id)
        if user_role != 'manager' and project_file.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Bu dosyayı silme yetkiniz yok'}), 403
        
        # Soft-delete: is_active = False yap
        project_file.is_active = False
        project_file.deleted_at = datetime.utcnow()
        project_file.deleted_by_id = current_user.id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Dosya başarıyla silindi'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Dosya silme hatası: {e}')
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


@api_bp.route('/dashboard/ai-advisor', methods=['GET'])
@login_required
def api_ai_advisor():
    """
    AI Stratejik Danışman verilerini getir
    """
    try:
        # Yetki kontrolü (Manager ve Observer rolleri)
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Bu sayfaya erişim yetkiniz yok'}), 403
        
        from services.ai_advisor_service import generate_strategic_advice
        advisor_data = generate_strategic_advice(current_user.kurum_id)
        
        return jsonify({
            'success': True,
            'data': advisor_data
        })
    
    except Exception as e:
        current_app.logger.error(f'AI danışman API hatası: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/dashboard/ai-advisor/notify', methods=['POST'])
@csrf.exempt
@login_required
def api_ai_advisor_notify():
    """
    AI tavsiyesini ilgili sorumluya bildir
    """
    try:
        data = request.get_json()
        recommendation_id = data.get('recommendation_id')
        target_user_id = data.get('target_user_id')
        target_role = data.get('target_role')
        
        if not recommendation_id:
            return jsonify({'success': False, 'message': 'Tavsiye ID gerekli'}), 400
        
        from services.ai_advisor_service import notify_recommendation
        result = notify_recommendation(recommendation_id, target_user_id, target_role)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Tavsiye bildirildi'
            })
        else:
            return jsonify({'success': False, 'message': 'Bildirim gönderilemedi'}), 500
    
    except Exception as e:
        current_app.logger.error(f'AI tavsiye bildirimi hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/dashboard/executive', methods=['GET'])
@csrf.exempt
@login_required
def api_executive_dashboard():
    """Executive Dashboard verilerini getir"""
    try:
        # Yetki kontrolü - Sadece yönetici ve gözlemci erişebilir
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim', 'gözlemci']:
            return jsonify({'success': False, 'message': 'Bu sayfaya erişim yetkiniz yok'}), 403
        
        from services.executive_dashboard import (
            get_corporate_health_score,
            get_critical_risks,
            get_planning_efficiency,
            get_task_workload_distribution,
            get_executive_summary
        )
        from services.strategic_impact_service import get_strategic_impact_summary
        
        # Filtreleme parametrelerini al
        filters = {}
        department = request.args.get('department')
        manager_id = request.args.get('manager_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if department:
            filters['department'] = department
        if manager_id:
            filters['manager_id'] = manager_id
        if start_date:
            try:
                filters['start_date'] = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        if end_date:
            try:
                filters['end_date'] = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Filtrelenmiş verileri topla
        health_data = get_corporate_health_score(current_user.kurum_id, filters)
        critical_risks = get_critical_risks(current_user.kurum_id, limit=5)
        planning_data = get_planning_efficiency(current_user.kurum_id)
        workload_data = get_task_workload_distribution(current_user.kurum_id)
        executive_summary = get_executive_summary(current_user.kurum_id)
        strategic_impact = get_strategic_impact_summary(current_user.kurum_id)
        
        # Personel Yükü Analizi
        from services.executive_dashboard import get_personnel_workload_analysis
        personnel_workload = get_personnel_workload_analysis(current_user.kurum_id)
        
        return jsonify({
            'success': True,
            'data': {
                'corporate_health': health_data,
                'critical_risks': critical_risks,
                'planning_efficiency': planning_data,
                'workload_distribution': workload_data,
                'executive_summary': executive_summary,
                'personnel_workload': personnel_workload,
                'strategic_impact': strategic_impact
            },
            'filters': filters
        })
    
    except Exception as e:
        current_app.logger.error(f'Executive dashboard API hatası: {e}', exc_info=True)
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
@api_bp.route('/user/layout', methods=['POST'])
@csrf.exempt
@login_required
def api_user_layout():
    """Kullanıcı layout tercihini kaydet"""
    try:
        data = request.get_json()
        layout = data.get('layout')
        
        if layout not in ['classic', 'sidebar']:
            return jsonify({'success': False, 'message': 'Geçersiz layout seçimi'}), 400
        
        current_user.layout_preference = layout
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Layout tercihi kaydedildi'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Layout tercihi kaydetme hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/user/theme', methods=['POST'])
@csrf.exempt
@login_required
def api_user_theme():
    """Kullanıcı tema tercihini kaydet"""
    try:
        data = request.get_json()
        theme = data.get('theme')
        
        if theme not in ['light', 'dark']:
            return jsonify({'success': False, 'message': 'Geçersiz tema seçimi'}), 400
        
        import json
        if current_user.theme_preferences:
            try:
                prefs = json.loads(current_user.theme_preferences)
            except:
                prefs = {}
        else:
            prefs = {}
        
        prefs['theme'] = theme
        current_user.theme_preferences = json.dumps(prefs)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tema tercihi kaydedildi'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Tema tercihi kaydetme hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/kurum/<int:kurum_id>/stratejik-profil', methods=['GET', 'POST'])
@csrf.exempt
@login_required
@role_required(['admin', 'kurum_yoneticisi', 'ust_yonetim', 'surec_lideri'])
def api_kurum_stratejik_profil(kurum_id):
    """Stratejik profil kaydet/getir (mock/cache)."""
    try:
        from extensions import cache
        if current_user.kurum_id != kurum_id and current_user.sistem_rol != 'admin':
            return jsonify({'success': False, 'message': 'Bu kurum için yetkiniz yok'}), 403

        cache_key = f"strategic_profile:{kurum_id}"
        if request.method == 'POST':
            payload = request.get_json() or {}
            cache.set(cache_key, payload, timeout=3600)
            return jsonify({'success': True, 'data': payload})

        data = cache.get(cache_key) or {'inputs': {}, 'ai_suggestions': None}
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        current_app.logger.error(f"Stratejik profil hatası: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/ai/stratejik-oneri', methods=['POST'])
@csrf.exempt
@login_required
@role_required(['admin', 'kurum_yoneticisi', 'ust_yonetim', 'surec_lideri'])
def api_ai_stratejik_oneri():
    """Stratejik AI önerisi (mock)."""
    try:
        api_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        suggestions = {
            'amac': 'Kurum genelinde verimliliği artırmak.',
            'vizyon': 'Sektörde sürdürülebilir ve çevik liderlik.',
            'stratejiler': ['Süreç standardizasyonu', 'Veri odaklı karar alma', 'Yetenek geliştirme']
        }
        return jsonify({'success': True, 'mock': api_key is None, 'suggestions': suggestions})
    except Exception as e:
        current_app.logger.error(f"AI stratejik öneri hatası: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/ai/yeni-oneri', methods=['POST'])
@csrf.exempt
@login_required
@role_required(['admin', 'kurum_yoneticisi', 'ust_yonetim', 'surec_lideri'])
def api_ai_yeni_oneri():
    """Yeni AI önerisi (mock)."""
    try:
        suggestions = {
            'amac': 'Müşteri memnuniyetini artırmak.',
            'vizyon': 'Müşteri odaklı dönüşümde öncü olmak.',
            'stratejiler': ['Servis kalitesi', 'Dijitalleşme', 'Eğitim']
        }
        return jsonify({'success': True, 'suggestions': suggestions})
    except Exception as e:
        current_app.logger.error(f"AI yeni öneri hatası: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/ai/kabul-et', methods=['POST'])
@csrf.exempt
@login_required
@role_required(['admin', 'kurum_yoneticisi', 'ust_yonetim', 'surec_lideri'])
def api_ai_kabul_et():
    """AI önerisini kabul et (mock)."""
    try:
        payload = request.get_json() or {}
        return jsonify({'success': True, 'accepted': True, 'data': payload})
    except Exception as e:
        current_app.logger.error(f"AI kabul hatası: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


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


@api_bp.route('/notifications', methods=['GET'])
@csrf.exempt
@login_required
def api_notifications():
    """Kullanıcının bildirimlerini getir"""
    try:
        from models import Notification
        notifications = Notification.query.filter_by(
            user_id=current_user.id
        ).order_by(
            Notification.created_at.desc()
        ).limit(20).all()
        
        notifications_data = []
        for notif in notifications:
            notifications_data.append({
                'id': notif.id,
                'tip': notif.tip,
                'baslik': notif.baslik,
                'mesaj': notif.mesaj,
                'link': notif.link,
                'okundu': notif.okundu,
                'created_at': notif.created_at.isoformat() if notif.created_at else None,
                'project_id': notif.project_id,
                'task_id': notif.task_id
            })

        unread_count = Notification.query.filter_by(
            user_id=current_user.id,
            okundu=False
        ).count()
        
        return jsonify({
            'success': True,
            # Newer key
            'notifications': notifications_data,
            # Legacy keys used by templates/base.html
            'bildirimler': notifications_data,
            'okunmamis_sayisi': unread_count
        })
    except Exception as e:
        current_app.logger.error(f'Bildirimler getirme hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/notifications/<int:notification_id>/mark-read', methods=['POST'])
@csrf.exempt
@login_required
def api_notification_mark_read(notification_id):
    """Tek bir bildirimi okundu işaretle"""
    try:
        from models import Notification
        notif = Notification.query.get_or_404(notification_id)
        if notif.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Bu bildirime erişim yetkiniz yok'}), 403

        notif.okundu = True
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Bildirim işaretleme hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/notifications/count', methods=['GET'])
@csrf.exempt
@login_required
def api_notifications_count():
    """Okunmamış bildirim sayısını getir"""
    try:
        from models import Notification
        count = Notification.query.filter_by(
            user_id=current_user.id,
            okundu=False
        ).count()
        
        return jsonify({
            'success': True,
            'count': count
        })
    except Exception as e:
        current_app.logger.error(f'Bildirim sayısı getirme hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/notifications/mark-all-read', methods=['POST'])
@csrf.exempt
@login_required
def api_notifications_mark_all_read():
    """Tüm bildirimleri okundu işaretle"""
    try:
        from models import Notification
        Notification.query.filter_by(
            user_id=current_user.id,
            okundu=False
        ).update({'okundu': True})
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tüm bildirimler okundu işaretlendi'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Bildirimler okundu işaretleme hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


# What-If Simülasyon API (V2.0.0)
@api_bp.route('/simulation/what-if', methods=['POST'])
@csrf.exempt
@login_required
def api_what_if_simulation():
    """What-If simülasyonu çalıştır"""
    try:
        from services.ai_advisor_service import simulate_what_if
        
        data = request.get_json()
        
        if not data or 'type' not in data:
            return jsonify({
                'success': False,
                'message': 'Simülasyon tipi (type) gerekli'
            }), 400
        
        # Kurum ID'yi al
        kurum_id = current_user.kurum_id
        if not kurum_id:
            return jsonify({
                'success': False,
                'message': 'Kurum bilgisi bulunamadı'
            }), 400
        
        # Simülasyonu çalıştır
        result = simulate_what_if(kurum_id, data)
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'message': result['error']
            }), 400
        
        return jsonify({
            'success': True,
            'simulation': result
        })
    
    except Exception as e:
        current_app.logger.error(f'What-If simülasyon hatası: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/project/<int:project_id>/simulate', methods=['GET'])
@login_required
def simulate_project(project_id):
    """Proje bazlı What-If simülasyonu (Beta)"""
    try:
        # Projeyi kontrol et
        project = Project.query.get_or_404(project_id)
        
        # Yetki kontrolü
        if project.kurum_id != current_user.kurum_id:
            return jsonify({
                'success': False,
                'message': 'Bu projeye erişim yetkiniz yok'
            }), 403
        
        # İleride gerçek AI modeli çalışacak. Şimdilik mock data:
        import time
        time.sleep(1.5)  # İşlem yapıyor hissi ver
        
        # Proje verilerini analiz et (gerçek veriler)
        tasks = Task.query.filter_by(project_id=project_id).all()
        risks = ProjectRisk.query.filter_by(project_id=project_id).all()
        
        # Risk seviyesini hesapla
        high_risk_count = sum(1 for r in risks if r.impact >= 4 and r.probability >= 4)
        risk_level = 'high' if high_risk_count >= 2 else 'medium' if high_risk_count >= 1 else 'low'
        
        # Senaryolar oluştur
        scenarios = []
        if len(tasks) > 0:
            scenarios.append({
                "description": "Tasarım onayı 1 hafta gecikirse",
                "impact": "+15.000 TL Maliyet"
            })
        if len(risks) > 0:
            scenarios.append({
                "description": "Backend ekibi %50 kapasiteye düşerse",
                "impact": "3 Hafta Gecikme"
            })
        if len(tasks) > 3:
            scenarios.append({
                "description": "Kritik görevlerde kaynak yetersizliği",
                "impact": "Proje bitiş tarihi +2 hafta"
            })
        
        # Varsayılan senaryolar (eğer yeterli veri yoksa)
        if len(scenarios) == 0:
            scenarios = [
                {"description": "Tasarım onayı 1 hafta gecikirse", "impact": "+15.000 TL Maliyet"},
                {"description": "Backend ekibi %50 kapasiteye düşerse", "impact": "3 Hafta Gecikme"}
            ]
        
        # Özet mesajı
        summary = f"Projede {'kritik yol üzerinde' if len(tasks) > 0 else ''} {len(risks)} risk tespit edildi."
        if high_risk_count > 0:
            summary = f"Projede kritik yol üzerinde {high_risk_count} yüksek risk tespit edildi."
        
        # AI Önerisi
        recommendation = "Tasarım onayı için acil toplantı set edilmeli ve kapsam daraltılmalı."
        if high_risk_count >= 2:
            recommendation = "Projede kritik riskler tespit edildi. Acil müdahale planı oluşturulmalı ve kaynak tahsisi gözden geçirilmeli."
        elif len(tasks) > 5:
            recommendation = "Görev sayısı fazla. Paralel çalışma planı yapılmalı ve kritik görevlere öncelik verilmeli."
        
        return jsonify({
            "risk_level": risk_level,
            "summary": summary,
            "scenarios": scenarios,
            "recommendation": recommendation
        })
        
    except Exception as e:
        current_app.logger.error(f'Proje simülasyon hatası: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


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

@api_bp.route('/admin/users')
@login_required
def api_admin_users():
    """Admin panel için kullanıcı listesi"""
    try:
        # Sadece admin / kurum_yoneticisi / ust_yonetim erişebilir
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403
        
        # Sistem admini kontrolü (kurum_id=1)
        is_system_admin = current_user.sistem_rol == 'admin' and current_user.kurum_id == 1
        
        # Kullanıcıları filtrele (sadece aktif kayıtlar)
        if is_system_admin:
            # Sistem yöneticisi: TÜM kullanıcıları görür
            users = User.query.options(db.joinedload(User.kurum)).filter_by(silindi=False).all()
            kurumlar = Kurum.query.filter_by(silindi=False).all()
            surecler = Surec.query.filter_by(silindi=False).all()
        else:
            # Kurum yöneticisi: Sadece kendi kurumundaki kullanıcıları görür
            users = User.query.options(db.joinedload(User.kurum)).filter_by(kurum_id=current_user.kurum_id, silindi=False).all()
            kurumlar = Kurum.query.filter_by(id=current_user.kurum_id, silindi=False).all()
            surecler = Surec.query.filter_by(kurum_id=current_user.kurum_id, silindi=False).all()
        
        users_data = []
        for user in users:
            # Süreç rolleri bilgilerini topla
            process_roles = []
            liderlik_sayisi = db.session.query(surec_liderleri).filter_by(user_id=user.id).count()
            uyelik_sayisi = db.session.query(surec_uyeleri).filter_by(user_id=user.id).count()
            
            # Encoding sorunlarını önlemek için string'leri temizle
            try:
                kurum_adi = user.kurum.ticari_unvan if user.kurum else None
                if kurum_adi:
                    kurum_adi = kurum_adi.encode('utf-8', errors='ignore').decode('utf-8')
            except:
                kurum_adi = None
            
            user_dict = {
                'id': user.id,
                'username': user.username,
                'email': user.email or '',
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'full_name': f"{user.first_name or ''} {user.last_name or ''}".strip(),
                'sistem_rol': user.sistem_rol,
                'kurum_id': user.kurum_id,
                'kurum_adi': kurum_adi,
                'profile_photo': user.profile_photo if hasattr(user, 'profile_photo') else None,
                'process_counts': {
                    'liderlik': liderlik_sayisi,
                    'uyelik': uyelik_sayisi,
                    'toplam': liderlik_sayisi + uyelik_sayisi
                },
                'process_summary': f'{liderlik_sayisi} liderlik, {uyelik_sayisi} üyelik' if (liderlik_sayisi + uyelik_sayisi) > 0 else 'Süreç ataması yok',
                'can_edit': True,  # Admin herkesi düzenleyebilir
                'can_delete': user.id != current_user.id  # Kendini silemez
            }
            users_data.append(user_dict)
        
        # Sistem rolleri listesi
        allowed_roles = ['admin', 'kurum_yoneticisi', 'ust_yonetim', 'kurum_kullanici', 'surec_lideri', 'surec_uyesi']
        
        # İstatistikler
        total_kurumlar = len(kurumlar)
        total_surecler = len(surecler)
        
        return jsonify({
            'success': True,
            'data': {
                'users': users_data,
                'allowed_roles': allowed_roles,
                'is_system_admin': is_system_admin,
                'stats': {
                    'total_users': len(users_data),
                    'total_kurumlar': total_kurumlar,
                    'total_surecler': total_surecler
                }
            }
        })
    except Exception as e:
        current_app.logger.error(f'Kullanıcı listesi hatası: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Kullanıcılar yüklenirken bir hata oluştu'
        }), 500


@api_bp.route('/admin/users/delete/<int:user_id>', methods=['DELETE', 'POST'])
@login_required
def api_admin_delete_user(user_id):
    """Kullanıcı sil (soft delete) - Admin veya kurum yöneticisi silebilir"""
    try:
        # Yetki kontrolü
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Kullanıcı bulunamadı'}), 404
        
        # Kendini silemez
        if user.id == current_user.id:
            return jsonify({'success': False, 'message': 'Kendi hesabınızı silemezsiniz'}), 400
        
        # Kurum yöneticisi sadece kendi kurumundaki kullanıcıları silebilir
        is_system_admin = current_user.sistem_rol == 'admin' and current_user.kurum_id == 1
        if not is_system_admin and user.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu kullanıcıyı silme yetkiniz yok'}), 403
        
        if user.silindi:
            return jsonify({'success': False, 'message': 'Bu kullanıcı zaten silinmiş'}), 400
        
        # SOFT DELETE
        user.silindi = True
        user.deleted_at = datetime.utcnow()
        user.deleted_by = current_user.id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{user.username} kullanıcısı arşivlendi. İsterseniz geri getirebilirsiniz.'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Kullanıcı silme hatası: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/admin/users/<int:user_id>')
@login_required
def api_admin_user_detail(user_id):
    """Kullanıcı detay bilgisi - Sadece kendi kurumundaki kullanıcılar"""
    try:
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403

        # Sistem admini kontrolü (kurum_id=1)
        is_system_admin = current_user.sistem_rol == 'admin' and current_user.kurum_id == 1
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Kullanıcı bulunamadı'}), 404

        # Kurum yöneticisi / üst yönetim sadece kendi kurumundaki kullanıcıları görebilir
        if not is_system_admin and user.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu kullanıcıya erişim yetkiniz yok'}), 403
        
        # Süreç rolleri bilgilerini topla
        process_roles = []
        lider_surecler = db.session.query(surec_liderleri).filter_by(user_id=user.id).all()
        uye_surecler = db.session.query(surec_uyeleri).filter_by(user_id=user.id).all()
        
        # Süreç bilgilerini al
        for lider_surec in lider_surecler:
            surec = Surec.query.get(lider_surec.surec_id)
            if surec:
                if not is_system_admin and surec.kurum_id != current_user.kurum_id:
                    continue
                process_roles.append({
                    'id': surec.id,
                    'ad': surec.ad,
                    'rol': 'surec_lideri',
                    'kurum_adi': surec.kurum.ticari_unvan if surec.kurum else None
                })
        
        for uye_surec in uye_surecler:
            surec = Surec.query.get(uye_surec.surec_id)
            if surec:
                if not is_system_admin and surec.kurum_id != current_user.kurum_id:
                    continue
                process_roles.append({
                    'id': surec.id,
                    'ad': surec.ad,
                    'rol': 'surec_uyesi',
                    'kurum_adi': surec.kurum.ticari_unvan if surec.kurum else None
                })
        
        user_dict = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': f"{user.first_name or ''} {user.last_name or ''}".strip(),
            'sistem_rol': user.sistem_rol,
            'kurum_id': user.kurum_id,
            'kurum_adi': user.kurum.ticari_unvan if user.kurum else None,
            'profile_photo': user.profile_photo if hasattr(user, 'profile_photo') else None,
            'process_roles': process_roles
        }
        
        return jsonify({
            'success': True,
            'data': user_dict
        })
    except Exception as e:
        current_app.logger.error(f'Kullanıcı detay hatası: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/rol-matrisi')
@login_required
def api_rol_matrisi():
    """Yetki paneli için rol matrisi"""
    try:
        if current_user.sistem_rol != 'admin':
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403
        
        # Kullanıcıları getir (sadece kendi kurumundaki kullanıcılar)
        users = User.query.filter_by(kurum_id=current_user.kurum_id).options(
            db.joinedload(User.kurum)
        ).all()
        
        kullanicilar = []
        for user in users:
            kullanicilar.append({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'sistem_rol': user.sistem_rol,
                'kurum_adi': user.kurum.kisa_ad if user.kurum else None
            })
        
        # Yetki kategorileri - Basit bir yapı (ileride veritabanından çekilebilir)
        yetki_kategorileri = [
            {
                'grup': 'Kurum Yönetimi',
                'yetkiler': [
                    {'kod': 'kurum_ozluk_c', 'ad': 'Kurum Oluştur', 'aciklama': 'Yeni kurum oluşturma yetkisi'},
                    {'kod': 'kurum_ozluk_r', 'ad': 'Kurum Oku', 'aciklama': 'Kurum bilgilerini görüntüleme yetkisi'},
                    {'kod': 'kurum_ozluk_u', 'ad': 'Kurum Güncelle', 'aciklama': 'Kurum bilgilerini düzenleme yetkisi'},
                    {'kod': 'kurum_ozluk_d', 'ad': 'Kurum Sil', 'aciklama': 'Kurum silme yetkisi'}
                ]
            },
            {
                'grup': 'Kullanıcı Yönetimi',
                'yetkiler': [
                    {'kod': 'kullanici_yonetimi_c', 'ad': 'Kullanıcı Oluştur', 'aciklama': 'Yeni kullanıcı oluşturma yetkisi'},
                    {'kod': 'kullanici_yonetimi_r', 'ad': 'Kullanıcı Oku', 'aciklama': 'Kullanıcı bilgilerini görüntüleme yetkisi'},
                    {'kod': 'kullanici_yonetimi_u', 'ad': 'Kullanıcı Güncelle', 'aciklama': 'Kullanıcı bilgilerini düzenleme yetkisi'},
                    {'kod': 'kullanici_yonetimi_d', 'ad': 'Kullanıcı Sil', 'aciklama': 'Kullanıcı silme yetkisi'}
                ]
            },
            {
                'grup': 'Süreç Yönetimi',
                'yetkiler': [
                    {'kod': 'surec_yonetimi_c', 'ad': 'Süreç Oluştur', 'aciklama': 'Yeni süreç oluşturma yetkisi'},
                    {'kod': 'surec_yonetimi_r', 'ad': 'Süreç Oku', 'aciklama': 'Süreç bilgilerini görüntüleme yetkisi'},
                    {'kod': 'surec_yonetimi_u', 'ad': 'Süreç Güncelle', 'aciklama': 'Süreç bilgilerini düzenleme yetkisi'},
                    {'kod': 'surec_yonetimi_d', 'ad': 'Süreç Sil', 'aciklama': 'Süreç silme yetkisi'}
                ]
            },
            {
                'grup': 'Stratejik Planlama',
                'yetkiler': [
                    {'kod': 'strateji_yonetimi_c', 'ad': 'Strateji Oluştur', 'aciklama': 'Yeni strateji oluşturma yetkisi'},
                    {'kod': 'strateji_yonetimi_r', 'ad': 'Strateji Oku', 'aciklama': 'Strateji bilgilerini görüntüleme yetkisi'},
                    {'kod': 'strateji_yonetimi_u', 'ad': 'Strateji Güncelle', 'aciklama': 'Strateji bilgilerini düzenleme yetkisi'},
                    {'kod': 'strateji_yonetimi_d', 'ad': 'Strateji Sil', 'aciklama': 'Strateji silme yetkisi'}
                ]
            }
        ]
        
        # Kullanıcıların özel yetkileri (şimdilik boş - ileride veritabanından çekilebilir)
        yetkiler = []
        
        return jsonify({
            'success': True,
            'kullanicilar': kullanicilar,
            'yetki_kategorileri': yetki_kategorileri,
            'yetkiler': yetkiler  # Kullanıcı-özel yetki ilişkileri
        })
    except Exception as e:
        current_app.logger.error(f'Rol matrisi hatası: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/rol-matrisi2')
@login_required
def api_rol_matrisi2():
    """Rol matrisi v2 - rol bazlı filtreleme"""
    try:
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403

        # Admin tüm kullanıcıları görebilir; kurum_yoneticisi ve ust_yonetim sadece kendi kurumunu görür
        is_admin = current_user.sistem_rol == 'admin'

        user_query = User.query.options(db.joinedload(User.kurum))
        if not is_admin:
            user_query = user_query.filter_by(kurum_id=current_user.kurum_id)

        users = user_query.order_by(User.first_name, User.last_name, User.username).all()

        yetki_kategorileri = [
            {
                'grup': 'Kurum Yönetimi',
                'yetkiler': [
                    {'kod': 'kurum_ozluk_c', 'ad': 'Kurum Oluştur', 'aciklama': 'Yeni kurum oluşturma yetkisi'},
                    {'kod': 'kurum_ozluk_r', 'ad': 'Kurum Oku', 'aciklama': 'Kurum bilgilerini görüntüleme yetkisi'},
                    {'kod': 'kurum_ozluk_u', 'ad': 'Kurum Güncelle', 'aciklama': 'Kurum bilgilerini düzenleme yetkisi'},
                    {'kod': 'kurum_ozluk_d', 'ad': 'Kurum Sil', 'aciklama': 'Kurum silme yetkisi'}
                ]
            },
            {
                'grup': 'Kullanıcı Yönetimi',
                'yetkiler': [
                    {'kod': 'kullanici_yonetimi_c', 'ad': 'Kullanıcı Oluştur', 'aciklama': 'Yeni kullanıcı oluşturma yetkisi'},
                    {'kod': 'kullanici_yonetimi_r', 'ad': 'Kullanıcı Oku', 'aciklama': 'Kullanıcı bilgilerini görüntüleme yetkisi'},
                    {'kod': 'kullanici_yonetimi_u', 'ad': 'Kullanıcı Güncelle', 'aciklama': 'Kullanıcı bilgilerini düzenleme yetkisi'},
                    {'kod': 'kullanici_yonetimi_d', 'ad': 'Kullanıcı Sil', 'aciklama': 'Kullanıcı silme yetkisi'}
                ]
            },
            {
                'grup': 'Süreç Yönetimi',
                'yetkiler': [
                    {'kod': 'surec_yonetimi_c', 'ad': 'Süreç Oluştur', 'aciklama': 'Yeni süreç oluşturma yetkisi'},
                    {'kod': 'surec_yonetimi_r', 'ad': 'Süreç Oku', 'aciklama': 'Süreç bilgilerini görüntüleme yetkisi'},
                    {'kod': 'surec_yonetimi_u', 'ad': 'Süreç Güncelle', 'aciklama': 'Süreç bilgilerini düzenleme yetkisi'},
                    {'kod': 'surec_yonetimi_d', 'ad': 'Süreç Sil', 'aciklama': 'Süreç silme yetkisi'}
                ]
            },
            {
                'grup': 'Stratejik Planlama',
                'yetkiler': [
                    {'kod': 'strateji_yonetimi_c', 'ad': 'Strateji Oluştur', 'aciklama': 'Yeni strateji oluşturma yetkisi'},
                    {'kod': 'strateji_yonetimi_r', 'ad': 'Strateji Oku', 'aciklama': 'Strateji bilgilerini görüntüleme yetkisi'},
                    {'kod': 'strateji_yonetimi_u', 'ad': 'Strateji Güncelle', 'aciklama': 'Strateji bilgilerini düzenleme yetkisi'},
                    {'kod': 'strateji_yonetimi_d', 'ad': 'Strateji Sil', 'aciklama': 'Strateji silme yetkisi'}
                ]
            }
        ]

        user_ids = [u.id for u in users]
        kullanici_yetkileri = []
        if user_ids:
            user_yetki_kayitlari = KullaniciYetki.query.filter(KullaniciYetki.user_id.in_(user_ids)).all()
            for kayit in user_yetki_kayitlari:
                kullanici_yetkileri.append({
                    'kullanici_id': kayit.user_id,
                    'yetki_kodu': kayit.yetki_kodu,
                    'aktif': kayit.aktif
                })

        kullanicilar = []
        for user in users:
            kullanicilar.append({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'sistem_rol': user.sistem_rol,
                'kurum_id': user.kurum_id,
                'kurum_adi': user.kurum.kisa_ad if user.kurum else None
            })

        return jsonify({
            'success': True,
            'kullanicilar': kullanicilar,
            'yetki_kategorileri': yetki_kategorileri,
            'yetkiler': kullanici_yetkileri
        })
    except Exception as e:
        current_app.logger.error(f'Rol matrisi2 hatası: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Sunucu hatası: ' + str(e)
        }), 500


@api_bp.route('/rol-matrisi2/update', methods=['POST'])
@csrf.exempt
@login_required
def api_rol_matrisi2_update():
    """Kullanıcı bazlı yetki güncelleme (v2)"""
    try:
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403

        data = request.get_json() or {}
        kullanici_id = data.get('kullanici_id')
        yetki_kodu = data.get('yetki_kodu')
        aktif = bool(data.get('aktif'))

        if not kullanici_id or not yetki_kodu:
            return jsonify({'success': False, 'message': 'Geçersiz istek'}), 400

        hedef_kullanici = User.query.get(kullanici_id)
        if not hedef_kullanici:
            return jsonify({'success': False, 'message': 'Kullanıcı bulunamadı'}), 404

        # Admin tüm kullanıcılara müdahale edebilir; diğer roller sadece kendi kurumundakilere
        if current_user.sistem_rol != 'admin' and hedef_kullanici.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu kullanıcı için yetkiniz yok'}), 403

        kayit = KullaniciYetki.query.filter_by(user_id=hedef_kullanici.id, yetki_kodu=yetki_kodu).first()
        if kayit:
            kayit.aktif = aktif
            kayit.atayan_user_id = current_user.id
            kayit.updated_at = datetime.utcnow()
        else:
            kayit = KullaniciYetki(
                user_id=hedef_kullanici.id,
                yetki_kodu=yetki_kodu,
                aktif=aktif,
                atayan_user_id=current_user.id
            )
            db.session.add(kayit)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Yetki güncellendi', 'aktif': kayit.aktif})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Rol matrisi2 update hatası: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Sunucu hatası: ' + str(e)
        }), 500


# ============================================
# ADMIN USERS UPDATE ENDPOINT
# ============================================

@api_bp.route('/admin/users/update/<int:user_id>', methods=['POST'])
@csrf.exempt
@login_required
def api_admin_update_user(user_id):
    """Admin panel aracılığıyla kullanıcı bilgilerini güncelle"""
    try:
        # Admin / kurum_yoneticisi / ust_yonetim güncelleyebilir
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403

        # Sistem admini kontrolü (kurum_id=1)
        is_system_admin = current_user.sistem_rol == 'admin' and current_user.kurum_id == 1
        
        # Kullanıcıyı bul
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Kullanıcı bulunamadı'}), 404

        # Kurum yöneticisi / üst yönetim sadece kendi kurumundaki kullanıcıları güncelleyebilir
        if not is_system_admin and user.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu kullanıcıyı güncelleme yetkiniz yok'}), 403
        
        # Güncelleme verilerini al
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Geçersiz JSON verisi'}), 400
        
        # Zorunlu alanları kontrol et
        if not data.get('username') or not data.get('email') or not data.get('kurum_id'):
            return jsonify({'success': False, 'message': 'Zorunlu alanlar eksik'}), 400
        
        # Username benzersizliğini kontrol et (kendi username'i hariç)
        if data.get('username') != user.username:
            existing = User.query.filter_by(username=data.get('username')).first()
            if existing:
                return jsonify({'success': False, 'message': 'Bu kullanıcı adı zaten kullanılıyor'}), 400
        
        # Email benzersizliğini kontrol et (kendi email'i hariç)
        if data.get('email') != user.email:
            existing = User.query.filter_by(email=data.get('email')).first()
            if existing:
                return jsonify({'success': False, 'message': 'Bu email zaten kullanılıyor'}), 400
        
        # Kurum kontrol et
        kurum_id = data.get('kurum_id')
        kurum = Kurum.query.get(kurum_id)
        if not kurum:
            return jsonify({'success': False, 'message': 'Geçersiz kurum seçimi'}), 400

        # Admin olmayanlar kurum değiştiremez
        if not is_system_admin and int(kurum_id) != int(current_user.kurum_id):
            return jsonify({'success': False, 'message': 'Sadece kendi kurumunuzda işlem yapabilirsiniz'}), 403

        # Rol kontrolü: Admin olmayanlar admin rolü veremez
        incoming_role = data.get('role') or data.get('system_role')
        if not is_system_admin and incoming_role == 'admin':
            return jsonify({'success': False, 'message': 'Admin rolü atayamazsınız'}), 403
        
        # Kullanıcı bilgilerini güncelle
        user.username = data.get('username')
        user.email = data.get('email')
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '')
        user.sistem_rol = incoming_role or user.sistem_rol
        user.kurum_id = kurum_id
        
        # Şifre güncelleme (opsiyonel)
        if data.get('password') and len(data.get('password', '')) > 0:
            if len(data.get('password')) < 6:
                return jsonify({'success': False, 'message': 'Şifre en az 6 karakter olmalıdır'}), 400
            from werkzeug.security import generate_password_hash
            user.password_hash = generate_password_hash(data.get('password'))
        
        # Profil fotoğrafı güncelleme
        if data.get('profile_photo'):
            user.profile_photo = data.get('profile_photo')
        
        # Veritabanına kaydet
        db.session.commit()
        
        current_app.logger.info(f'Admin {current_user.username} tarafından kullanıcı güncellenmiş: {user.username}')
        
        return jsonify({
            'success': True,
            'message': 'Kullanıcı başarıyla güncellendi',
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'sistem_rol': user.sistem_rol,
                'kurum_id': user.kurum_id
            }
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Kullanıcı güncelleme hatası: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Güncelleme sırasında hata oluştu: {str(e)}'
        }), 500


# EVM API
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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500
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
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/admin/users/add', methods=['POST'])
@csrf.exempt
@login_required
def api_admin_add_user():
    """Yeni kullanıcı ekle (admin veya kurum_yoneticisi)."""
    try:
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403

        data = request.get_json() or {}
        required = ['username', 'email', 'first_name', 'last_name', 'password', 'role', 'kurum_id']
        missing = [k for k in required if not data.get(k)]
        if missing:
            return jsonify({'success': False, 'message': 'Eksik alanlar: ' + ', '.join(missing)}), 400

        # Rol kontrolü: kurum yöneticisi admin oluşturamaz
        if current_user.sistem_rol != 'admin' and data.get('role') == 'admin':
            return jsonify({'success': False, 'message': 'Kurum yöneticisi admin oluşturamaz'}), 403

        # Kurum kontrolü
        kurum_id = int(data.get('kurum_id'))
        if current_user.sistem_rol != 'admin' and current_user.kurum_id != kurum_id:
            return jsonify({'success': False, 'message': 'Sadece kendi kurumunuza kullanıcı ekleyebilirsiniz'}), 403

        if User.query.filter_by(username=data['username']).first():
            return jsonify({'success': False, 'message': 'Bu kullanıcı adı zaten kullanılıyor'}), 400
        if data.get('email') and User.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'message': 'Bu e-posta zaten kullanılıyor'}), 400

        user = User(
            username=data['username'],
            email=data.get('email', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            sistem_rol=data.get('role'),
            kurum_id=kurum_id,
            profile_photo=data.get('profile_photo') or None,
            password_hash=generate_password_hash(data['password'])
        )
        db.session.add(user)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Kullanıcı oluşturuldu', 'user_id': user.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Kullanıcı ekleme hatası: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# --- Bildirim (Notification) Endpointleri ---

@api_bp.route('/notifications', methods=['GET'])
@login_required
def api_get_notifications():
    """Kullanıcının bildirimlerini getir"""
    try:
        notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(50).all()
        return jsonify({
            'success': True,
            'notifications': [{
                'id': n.id,
                'tip': n.tip,
                'baslik': n.baslik,
                'mesaj': n.mesaj,
                'link': n.link,
                'okundu': n.okundu,
                'created_at': n.created_at.isoformat() if n.created_at else None
            } for n in notifications]
        })
    except Exception as e:
        current_app.logger.error(f'Bildirim getirme hatası: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/notifications/<int:notification_id>/mark-read', methods=['POST'])
@login_required
@csrf.exempt
def api_mark_notification_read(notification_id):
    """Bildirimi okundu olarak işaretle"""
    try:
        notification = Notification.query.get_or_404(notification_id)
        if notification.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Yetkiniz yok'}), 403
        
        notification.okundu = True
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Bildirim okundu işaretleme hatası: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
@csrf.exempt
def api_mark_all_notifications_read():
    """Tüm bildirimleri okundu olarak işaretle"""
    try:
        Notification.query.filter_by(user_id=current_user.id, okundu=False).update({'okundu': True})
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Tüm bildirimler okundu işaretleme hatası: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/notifications/count', methods=['GET'])
@login_required
def api_get_notification_count():
    """Okunmamış bildirim sayısını getir"""
    try:
        count = Notification.query.filter_by(user_id=current_user.id, okundu=False).count()
        return jsonify({
            'success': True,
            'count': count
        })
    except Exception as e:
        current_app.logger.error(f'Bildirim sayısı getirme hatası: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


