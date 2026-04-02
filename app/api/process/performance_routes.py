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
    debug_mode = request.args.get('debug', '0') == '1'
    
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
        return jsonify({'success': False, 'message': str(e)}), 500

from app.utils.security_decorators import require_process_access
from extensions import csrf

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
        return jsonify({'success': False, 'message': str(e)}), 500

@process_performance_bp.route('/api/surec/<int:surec_id>/faaliyet/<int:surec_faaliyet_id>/create-bireysel', methods=['POST'])
@login_required
@csrf.exempt
@require_process_access('surec_id')
def api_create_bireysel_faaliyet_from_surec(surec_id, surec_faaliyet_id):
    try:
        data, status = ProcessPerformanceService.create_bireysel_faaliyet_from_surec(current_user, surec_id, surec_faaliyet_id)
        return jsonify(data), status
    except KokpitimError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        current_app.logger.error(f'Bireysel faaliyet oluşturma hatası: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500

@process_performance_bp.route('/api/faaliyet/<int:faaliyet_id>/takip', methods=['POST'])
@login_required
@csrf.exempt
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
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Faaliyet takip kaydetme hatası: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500

@process_performance_bp.route('/api/surec/<int:surec_id>/karne/kaydet', methods=['POST'])
@login_required
@csrf.exempt
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
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Süreç karne kaydedilemedi: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500












@process_performance_bp.route('/api/surec/karne/pg-veri-detay', methods=['GET'])
@login_required
def route_get_pg_veri_detay_list():
    surec_pg_id = request.args.get('surec_pg_id', type=int)
    ceyrek = request.args.get('ceyrek', type=str)
    yil = request.args.get('yil', type=int, default=datetime.now().year)
    
    try:
        data = ProcessPerformanceService.get_pg_veri_detay_list(current_user, surec_pg_id, ceyrek, yil)
        if isinstance(data, tuple) and hasattr(data[0], 'keys'): return jsonify(data[0]), data[1]
        return jsonify(data)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@process_performance_bp.route('/api/export/surec_karnesi/excel', methods=['GET'])
@login_required
def route_export_surec_karnesi_excel():
    surec_id = request.args.get('surec_id', type=int)
    yil = request.args.get('yil', type=int)
    
    try:
        data = ProcessPerformanceService.export_surec_karnesi_excel_service(current_user, surec_id, yil)
        if isinstance(data, tuple) and len(data) == 2 and isinstance(data[1], str):
            output, filename = data
            from flask import send_file
            return send_file(
                output,
                as_attachment=True,
                download_name=filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        if isinstance(data, list):
            output, filename = data[0], data[1]
            from flask import send_file
            return send_file(output, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        return jsonify(data[0]), data[1]
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@process_performance_bp.route('/api/pg-veri/detay/<int:veri_id>', methods=['GET'])
@login_required
def route_get_pg_veri_detay(veri_id):
    try:
        data = ProcessPerformanceService.get_pg_veri_detay(current_user, veri_id)
        if isinstance(data, tuple) and hasattr(data[0], 'keys'): return jsonify(data[0]), data[1]
        return jsonify(data)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

from extensions import csrf
@process_performance_bp.route('/api/pg-veri/detay/toplu', methods=['POST'])
@login_required
@csrf.exempt
def route_get_pg_veri_detay_toplu():
    data = request.get_json() or {}
    veri_idleri = data.get('veri_idleri', [])
    try:
        res = ProcessPerformanceService.get_pg_veri_detay_toplu(current_user, veri_idleri)
        if isinstance(res, tuple) and hasattr(res[0], 'keys'): return jsonify(res[0]), res[1]
        return jsonify(res)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@process_performance_bp.route('/api/pg-veri/guncelle/<int:veri_id>', methods=['PUT'])
@login_required
@csrf.exempt
def route_update_pg_veri(veri_id):
    data = request.get_json() or {}
    gerceklesen_deger = data.get('gerceklesen_deger')
    aciklama = data.get('aciklama')
    try:
        res = ProcessPerformanceService.update_pg_veri(current_user, veri_id, gerceklesen_deger, aciklama)
        if isinstance(res, tuple) and hasattr(res[0], 'keys'): return jsonify(res[0]), res[1]
        return jsonify(res)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
