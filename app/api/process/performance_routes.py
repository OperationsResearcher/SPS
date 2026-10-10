# -*- coding: utf-8 -*-
"""
Process Performance API Routes (Modular Blueprint)
Süreç karnesi performans verileri için ayrıştırılmış mikro-denetleyici.
"""
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from datetime import datetime

from app.services.process_performance_service import ProcessPerformanceService
from app.utils.errors import KokpitimError

# Blueprint tanımı. Mevcut sistemde /api prefix'i ana uygulamada veriliyor olabilir
# Biz /api/process alt yapısını kurarak geleceğe dönük bir yapı kuralım, 
# ancak mevcut önyüz (frontend) entegrasyonu kırılmasın diye url_prefix ayarını /api bırakabiliriz.
process_performance_bp = Blueprint('process_performance_bp', __name__)

@process_performance_bp.route('/api/surec/<int:surec_id>/karne/performans', methods=['GET'])
@login_required
def api_surec_karne_performans(surec_id):
    """
    Sürecin performans göstergelerini ve çeyreklik verilerini getirir.
    (Business Logic app/services/process_performance_service.py'ye aktarılmıştır - Zero Defect Arch)
    """
    yil = request.args.get('yil', datetime.now().year, type=int)
    periyot = request.args.get('periyot', 'ceyrek', type=str)
    ay = request.args.get('ay', None, type=int)
    # Güvenlik: debug parametresi sadece Admin role için aktif (stack trace exposure korumusu)
    _is_admin = bool(current_user.is_authenticated and current_user.role
                     and (current_user.role.name or "").lower() == "admin")
    debug_mode = (request.args.get('debug', '0') == '1') and _is_admin

    try:
        data, status = ProcessPerformanceService.get_process_performance(
            user=current_user,
            surec_id=surec_id,
            yil=yil,
            periyot=periyot,
            ay=ay,
            debug_mode=debug_mode
        )
        return jsonify(data), status
    except KokpitimError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        current_app.logger.error(f'Performans verileri getirilemedi: {e}', exc_info=True)
        return jsonify({'success': False, 'message': 'Sunucu hatası oluştu.'}), 500

from app.utils.security_decorators import require_process_access

@process_performance_bp.route('/api/surec/<int:surec_id>/karne/faaliyetler', methods=['GET'])
@login_required
@require_process_access('surec_id')
def api_surec_karne_faaliyetler(surec_id):
    yil = request.args.get('yil', datetime.now().year, type=int)
    try:
        data, status = ProcessPerformanceService.get_process_activities(current_user, surec_id, yil)
        return jsonify(data), status
    except KokpitimError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        current_app.logger.error(f'Faaliyet verileri getirilemedi: {e}', exc_info=True)
        return jsonify({'success': False, 'message': 'Sunucu hatası oluştu.'}), 500

@process_performance_bp.route('/api/surec/<int:surec_id>/faaliyet/<int:surec_faaliyet_id>/create-bireysel', methods=['POST'])
@login_required
@require_process_access('surec_id')
def api_create_bireysel_faaliyet_from_surec(surec_id, surec_faaliyet_id):
    try:
        data, status = ProcessPerformanceService.create_bireysel_faaliyet_from_surec(current_user, surec_id, surec_faaliyet_id)
        return jsonify(data), status
    except KokpitimError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        current_app.logger.error(f'Bireysel faaliyet oluşturma hatası: {e}', exc_info=True)
        return jsonify({'success': False, 'message': 'Sunucu hatası oluştu.'}), 500

@process_performance_bp.route('/api/faaliyet/<int:faaliyet_id>/takip', methods=['POST'])
@login_required
def api_faaliyet_takip_kaydet(faaliyet_id):
    """Bireysel faaliyetin aylık takibini kaydet (Process API Controller)."""
    try:
        data, status = ProcessPerformanceService.save_activity_tracking(
            user=current_user,
            faaliyet_id=faaliyet_id,
            data=request.get_json() or {}
        )
        return jsonify(data), status
    except KokpitimError as e:
        return jsonify(e.to_dict()), e.status_code
    except ValueError as e:
        return jsonify({'success': False, 'message': 'İşlem tamamlanamadı.'}), 400
    except Exception as e:
        current_app.logger.error(f'Faaliyet takip kaydetme hatası: {e}', exc_info=True)
        return jsonify({'success': False, 'message': 'Sunucu hatası oluştu.'}), 500

@process_performance_bp.route('/api/surec/<int:surec_id>/karne/kaydet', methods=['POST'])
@login_required
@require_process_access('surec_id')
def api_surec_karne_kaydet(surec_id):
    """Süreç karnesi verilerini kaydet (Process API Controller)."""
    try:
        data, status = ProcessPerformanceService.save_performance_data(
            user=current_user,
            surec_id=surec_id,
            data=request.get_json() or {}
        )
        return jsonify(data), status
    except KokpitimError as e:
        return jsonify(e.to_dict()), e.status_code
    except ValueError as e:
        return jsonify({'success': False, 'message': 'İşlem tamamlanamadı.'}), 400
    except Exception as e:
        current_app.logger.error(f'Süreç karne kaydedilemedi: {e}', exc_info=True)
        return jsonify({'success': False, 'message': 'Sunucu hatası oluştu.'}), 500
# KOD-04: pg-veri-detay, export/surec_karnesi/excel, pg-veri/detay(+toplu), pg-veri/guncelle uçları
# kaldırıldı (servis fonksiyonları tanımsız adlarla 500 veriyordu).
