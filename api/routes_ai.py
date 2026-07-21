# -*- coding: utf-8 -*-
"""AI / vizyon skoru / stratejik oneri / dashboard advisor / simulasyon API rotalari

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
from api.helpers import (
    _invalidate_executive_dashboard_cache,
    _resolve_project_leader_ids_api,
    _sync_project_leaders_api,
    _notify_project_team_changes_api,
    _parse_date_safe,
)
from app.utils.error_handlers import json_error  # S6


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
        return json_error(e, "[api_vision_score]", 500)


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
        return json_error(e, "[api_vision_score_recalc]", 500)


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
        # K12: `request.get_json()` Content-Type application/json değilse
        # 415 FIRLATIR (None dönmez). Uç GET'i de kabul ettiği için düz bir
        # GET isteği her seferinde 415 → dıştaki except → 500 veriyordu.
        # silent=True hata yerine None döndürür.
        as_of_str = request.args.get('as_of_date') or (request.get_json(silent=True) or {}).get('as_of_date')
        as_of_date = None
        if as_of_str:
            from datetime import datetime as dt
            try:
                as_of_date = dt.strptime(str(as_of_str).strip()[:10], '%Y-%m-%d').date()
            except ValueError:
                pass
        payload = _build_vision_score_payload_for_ai(kurum_id, as_of_date)
        from services.ai_coach_service import analyze_strategic_performance
        result = analyze_strategic_performance(
            payload,
            tenant_id=getattr(current_user, "tenant_id", kurum_id),
            user_id=getattr(current_user, "id", None),
        )
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
        # S6: str(e) SQL cümlesi/parametre sızdırabiliyordu; log yukarıda zaten var.
        return jsonify({
            'success': False,
            'message': _('Analiz tamamlanamadı.'),
            'analysis_markdown': None,
        }), 500
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
        return json_error(e, "[api_ai_advisor]", 500)


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
        return json_error(e, "[api_ai_advisor_notify]", 500)


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
        return json_error(e, "[api_executive_dashboard]", 500)
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
        return json_error(e, "[api_kurum_stratejik_profil]", 500)


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
        return json_error(e, "[api_ai_stratejik_oneri]", 500)


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
        return json_error(e, "[api_ai_yeni_oneri]", 500)


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
        return json_error(e, "[api_ai_kabul_et]", 500)
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
            'message': _('İşlem tamamlanamadı.'),  # S6: str(e) sızdırıyordu
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
            'message': _('İşlem tamamlanamadı.'),  # S6: str(e) sızdırıyordu
        }), 500
