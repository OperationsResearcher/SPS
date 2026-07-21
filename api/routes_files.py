# -*- coding: utf-8 -*-
"""Proje dosyalari ve dokuman merkezi API rotalari

api/routes.py'den bölündü (davranış/URL değişmedi). Blueprint: api.blueprint.api_bp
"""
from flask import jsonify, request, current_app, send_file
from flask_babel import gettext as _
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
        return json_error(e, "[api_proje_dosyalar]", 500)


@api_bp.route('/dokuman-merkezi', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def api_dokuman_merkezi():
    """Kurumsal dosya yönetimi API — UYGULANMADI (501).

    ⚠ BU UÇ HİÇBİR ZAMAN ÇALIŞMADI. Aşağıdaki gövde `ProjectFile` modelinin
    OLMAYAN 8 alanına dayanıyor (ölçüm 2026-07-21):

        kodun beklediği : scope, is_active, category, file_name, file_size,
                          description, version, user_id
        modelde OLAN    : id, project_id, uploader_id, filename, file_path,
                          file_type, created_at

    GET her çağrıda `AttributeError: type object 'ProjectFile' has no
    attribute 'scope'` ile 500 veriyordu.

    POST daha tehlikeliydi: dosyayı ÖNCE diske yazıyor, SONRA DB kaydında
    patlıyordu → `static/uploads/corporate_files/` altında sahipsiz dosya
    birikiyordu (yükleyen "hata" görüyor, dosya sunucuda kalıyor).

    Doğru düzeltme modeli genişletmek + migration yazmaktır; bu bir ürün
    kararı olduğu için burada YAPILMADI. Kırık 500 yerine dürüst 501
    dönülüyor — sessizce yanlış davranmaktansa "uygulanmadı" demek daha iyi.
    Ölü gövde referans olsun diye altta bırakıldı.
    """
    current_app.logger.warning(
        "[api_dokuman_merkezi] uygulanmamış uç çağrıldı (ProjectFile modeli "
        "gerekli alanları taşımıyor) — user=%s", getattr(current_user, "id", None)
    )
    return jsonify({
        'success': False,
        'message': _('Doküman merkezi henüz kullanıma açılmadı.'),
    }), 501


def _api_dokuman_merkezi_olu_govde():
    """Yukarıdaki ucun eski gövdesi — ÇALIŞMAZ, referans amaçlı saklandı."""
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
        return json_error(e, "[_api_dokuman_merkezi_olu_govde]", 500)


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
        return json_error(e, "[api_dokuman_merkezi_indir]", 500)


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
        return json_error(e, "[api_dokuman_merkezi_sil]", 500)


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
        return json_error(e, "[api_proje_dosya_indir]", 500)


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
        from app.utils.project_rbac import _get_user_project_role
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
        return json_error(e, "[api_proje_dosya_sil]", 500)
