# -*- coding: utf-8 -*-
"""Admin / kullanici / kurum ayarlari / bildirim / rol matrisi API rotalari

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
from werkzeug.security import generate_password_hash
from api.helpers import (
    _invalidate_executive_dashboard_cache,
    _resolve_project_leader_ids_api,
    _sync_project_leaders_api,
    _notify_project_team_changes_api,
    _parse_date_safe,
)


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
        kurum = current_user.tenant
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
        current_app.logger.error(f'Logo yükleme hatası: {str(e)} - Kullanıcı: {current_user.email}')
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
        current_app.logger.info(f'Kurum alt stratejileri isteği: kurum_id={kurum_id}, surec_id={surec_id}, kullanıcı_kurum_id={current_user.tenant_id}')
        
        # Yetki kontrolü - kullanıcı aynı kurumda olmalı
        if kurum_id != current_user.tenant_id:
            current_app.logger.warning(f'Yetki hatası: kurum_id={kurum_id}, kullanıcı_kurum_id={current_user.tenant_id}')
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
        
        kurum = current_user.tenant
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
        current_app.logger.error(f'Logo URL güncelleme hatası: {str(e)} - Kullanıcı: {current_user.email}')
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
        
        kurum = current_user.tenant
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
        current_app.logger.error(f'Rehber sistemi güncelleme hatası: {str(e)} - Kullanıcı: {current_user.email}')
        return jsonify({'success': False, 'message': f'Rehber sistemi güncellenirken hata oluştu: {str(e)}'}), 500, {'Content-Type': 'application/json'}


# ============================================================================
# PROJE YÖNETİMİ API ENDPOINT'LERİ
# ============================================================================
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
@api_bp.route('/notifications', methods=['GET'])
@csrf.exempt
@login_required
def api_notifications():
    """Kullanıcının bildirimlerini getir"""
    try:
        from app.models.legacy_bridge import Notification
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
        from app.models.legacy_bridge import Notification
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
        from app.models.legacy_bridge import Notification
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
        from app.models.legacy_bridge import Notification
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
@api_bp.route('/admin/users')
@login_required
def api_admin_users():
    """Admin panel için kullanıcı listesi"""
    try:
        # Sadece admin / kurum_yoneticisi / ust_yonetim erişebilir
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403
        
        # Sistem admini kontrolü (kurum_id=1)
        is_system_admin = current_user.sistem_rol == 'admin' and current_user.tenant_id == 1
        
        # Kullanıcıları filtrele (sadece aktif kayıtlar)
        if is_system_admin:
            # Sistem yöneticisi: TÜM kullanıcıları görür
            users = User.query.options(db.joinedload(User.kurum)).filter_by(silindi=False).all()
            kurumlar = Kurum.query.filter_by(silindi=False).all()
            surecler = Surec.query.filter_by(silindi=False).all()
        else:
            # Kurum yöneticisi: Sadece kendi kurumundaki kullanıcıları görür
            users = User.query.options(db.joinedload(User.kurum)).filter_by(kurum_id=current_user.tenant_id, silindi=False).all()
            kurumlar = Kurum.query.filter_by(id=current_user.tenant_id, silindi=False).all()
            surecler = Surec.query.filter_by(kurum_id=current_user.tenant_id, silindi=False).all()
        
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
        is_system_admin = current_user.sistem_rol == 'admin' and current_user.tenant_id == 1
        if not is_system_admin and user.kurum_id != current_user.tenant_id:
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
        is_system_admin = current_user.sistem_rol == 'admin' and current_user.tenant_id == 1
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Kullanıcı bulunamadı'}), 404

        # Kurum yöneticisi / üst yönetim sadece kendi kurumundaki kullanıcıları görebilir
        if not is_system_admin and user.kurum_id != current_user.tenant_id:
            return jsonify({'success': False, 'message': 'Bu kullanıcıya erişim yetkiniz yok'}), 403
        
        # Süreç rolleri bilgilerini topla
        process_roles = []
        lider_surecler = db.session.query(surec_liderleri).filter_by(user_id=user.id).all()
        uye_surecler = db.session.query(surec_uyeleri).filter_by(user_id=user.id).all()
        
        # Süreç bilgilerini al
        for lider_surec in lider_surecler:
            surec = Surec.query.get(lider_surec.surec_id)
            if surec:
                if not is_system_admin and surec.kurum_id != current_user.tenant_id:
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
                if not is_system_admin and surec.kurum_id != current_user.tenant_id:
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
        users = User.query.filter_by(kurum_id=current_user.tenant_id).options(
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
            user_query = user_query.filter_by(kurum_id=current_user.tenant_id)

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
        if current_user.sistem_rol != 'admin' and hedef_kullanici.kurum_id != current_user.tenant_id:
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
        is_system_admin = current_user.sistem_rol == 'admin' and current_user.tenant_id == 1
        
        # Kullanıcıyı bul
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Kullanıcı bulunamadı'}), 404

        # Kurum yöneticisi / üst yönetim sadece kendi kurumundaki kullanıcıları güncelleyebilir
        if not is_system_admin and user.kurum_id != current_user.tenant_id:
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
        if not is_system_admin and int(kurum_id) != int(current_user.tenant_id):
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
        
        current_app.logger.info(f'Admin {current_user.email} tarafından kullanıcı güncellenmiş: {user.username}')
        
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
        if current_user.sistem_rol != 'admin' and current_user.tenant_id != kurum_id:
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
