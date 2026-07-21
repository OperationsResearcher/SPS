# -*- coding: utf-8 -*-
# Otomatik bölüm — `python scripts/dev/split_main_routes.py`
from main.routes._common import *  # noqa: F401,F403
from main.routes import main_bp
from app.utils.error_handlers import json_error  # S6

# ============================================================================
# PROJE YÖNETİMİ ROTALARI
# ============================================================================

@main_bp.route('/projeler/<int:project_id>/duzenle')
@login_required
def proje_duzenle(project_id):
    """Proje düzenleme → Micro (/project/<id>/edit)."""
    return redirect(url_for('app_bp.project_edit', project_id=project_id))


@main_bp.route('/projeler/<int:project_id>')
@login_required
def proje_detay(project_id):
    """Proje detay → Micro (/project/<id>)."""
    return redirect(url_for('app_bp.project_detail', project_id=project_id))


@main_bp.route('/projeler/<int:project_id>/gorevler/<int:task_id>')
@login_required
def gorev_detay(project_id, task_id):
    """Görev detay → Micro (/project/<pid>/task/<tid>)."""
    return redirect(
        url_for(
            'app_bp.project_task_detail',
            project_id=project_id,
            task_id=task_id,
        )
    )


@main_bp.route('/projeler/<int:project_id>/gorevler/yeni')
@login_required
def gorev_yeni(project_id):
    """Yeni görev → Micro (/project/<id>/task/new)."""
    return redirect(url_for('app_bp.project_task_new', project_id=project_id))


@main_bp.route('/api/muda-hunter/analyze/<int:surec_id>', methods=['POST'])
@login_required
def muda_analyze(surec_id):
    """Süreç verimsizlik analizi API"""
    try:
        surec = Surec.query.filter_by(id=surec_id, kurum_id=current_user.kurum_id).first_or_404()
        
        from app.services.muda_analyzer import MudaAnalyzerService
        findings = MudaAnalyzerService.analyze_process_inefficiency(surec_id, current_user.kurum_id)
        
        return jsonify({
            'success': True,
            'findings': findings,
            'surec_name': surec.surec_adi
        })
    
    except Exception as e:
        current_app.logger.error(f'Muda analiz hatası: {e}')
        return json_error(e, "[muda_analyze]", 500)


@main_bp.route('/api/muda-hunter/efficiency-score', methods=['GET'])
@login_required
def muda_efficiency_score():
    """Genel verimlilik skoru API"""
    try:
        from app.services.muda_analyzer import MudaAnalyzerService
        efficiency_score = MudaAnalyzerService.get_efficiency_score(current_user.kurum_id)
        
        return jsonify({
            'success': True,
            'efficiency_score': efficiency_score
        })
    
    except Exception as e:
        current_app.logger.error(f'Efficiency score hatası: {e}')
        return json_error(e, "[muda_efficiency_score]", 500)


# ============================================
# FAZ 3: İLERİ SEVİYE MODÜLLER ROUTE'LARI
# ============================================

# V61.0 - Titan & Zenith Paketi
@main_bp.route('/admin/get-organization/<kisa_ad>')
@login_required
def admin_get_organization(kisa_ad):
    """Kurum bilgilerini getir"""
    try:
        allowed_roles = {'admin', 'kurum_yoneticisi', 'ust_yonetim'}
        if current_user.sistem_rol not in allowed_roles:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403
        
        kurum = Kurum.query.filter_by(kisa_ad=kisa_ad).first()
        if not kurum:
            return jsonify({'success': False, 'message': 'Kurum bulunamadı'}), 404

        # Admin olmayan kullanıcılar sadece kendi kurumunu görüntüleyebilir
        if current_user.sistem_rol != 'admin' and kurum.id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403
        
        return jsonify({
            'success': True,
            'organization': {
                'id': kurum.id,
                'kisa_ad': kurum.kisa_ad,
                'ticari_unvan': kurum.ticari_unvan,
                'faaliyet_alani': kurum.faaliyet_alani,
                'sektor': kurum.sektor,
                'calisan_sayisi': kurum.calisan_sayisi,
                'email': kurum.email,
                'telefon': kurum.telefon,
                'web_adresi': kurum.web_adresi,
                'vergi_dairesi': kurum.vergi_dairesi if hasattr(kurum, 'vergi_dairesi') else None,
                'vergi_numarasi': kurum.vergi_numarasi if hasattr(kurum, 'vergi_numarasi') else None,
                'logo_url': kurum.logo_url if hasattr(kurum, 'logo_url') else None
            }
        })
    except Exception as e:
        current_app.logger.error(f'Kurum getirme hatası: {e}')
        return json_error(e, "[admin_get_organization]", 500)


@main_bp.route('/admin/add-organization', methods=['POST'])
@login_required
def admin_add_organization():
    """Yeni kurum ekle - Admin tüm kurumları oluşturabilir"""
    try:
        if current_user.sistem_rol != 'admin':
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403

        data = request.get_json()
        kisa_ad = data.get('kisa_ad', '').strip()
        
        if not kisa_ad:
            return jsonify({'success': False, 'message': 'Kısa ad zorunludur'}), 400
        
        # Kurum zaten var mı kontrol et
        existing = Kurum.query.filter_by(kisa_ad=kisa_ad).first()
        if existing:
            return jsonify({'success': False, 'message': 'Bu kısa adla bir kurum zaten mevcut'}), 400
        
        kurum = Kurum(
            kisa_ad=kisa_ad,
            ticari_unvan=data.get('ticari_unvan', '').strip(),
            faaliyet_alani=data.get('faaliyet_alani', '').strip(),
            sektor=data.get('sektor', '').strip(),
            calisan_sayisi=data.get('calisan_sayisi'),
            email=data.get('email', '').strip(),
            telefon=data.get('telefon', '').strip(),
            web_adresi=data.get('web_adresi', '').strip()
        )
        
        # Opsiyonel alanlar
        if hasattr(Kurum, 'vergi_dairesi'):
            kurum.vergi_dairesi = data.get('vergi_dairesi', '').strip() or None
        if hasattr(Kurum, 'vergi_numarasi'):
            kurum.vergi_numarasi = data.get('vergi_numarasi', '').strip() or None
        if hasattr(Kurum, 'logo_url'):
            kurum.logo_url = data.get('logo_url', '').strip() or None
        
        db.session.add(kurum)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Kurum başarıyla oluşturuldu',
            'organization': {
                'id': kurum.id,
                'kisa_ad': kurum.kisa_ad
            }
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Kurum ekleme hatası: {e}')
        return json_error(e, "[admin_add_organization]", 500)


@main_bp.route('/admin/update-organization', methods=['POST'])
@login_required
def admin_update_organization():
    """Kurum bilgilerini güncelle - Admin tüm kurumları düzenleyebilir"""
    try:
        allowed_roles = {'admin', 'kurum_yoneticisi', 'ust_yonetim'}
        if current_user.sistem_rol not in allowed_roles:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403
        
        data = request.get_json()
        kurum_id = data.get('id')
        
        if not kurum_id:
            return jsonify({'success': False, 'message': 'Kurum ID gerekli'}), 400

        kurum = Kurum.query.filter_by(id=kurum_id).first()
        if not kurum:
            return jsonify({'success': False, 'message': 'Kurum bulunamadı'}), 404

        # Admin olmayan kullanıcılar sadece kendi kurumunu düzenleyebilir
        if current_user.sistem_rol != 'admin' and kurum.id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403
        
        # Kısa ad değişiyorsa, yeni kısa ad zaten kullanılıyor mu kontrol et
        new_kisa_ad = data.get('kisa_ad', '').strip()
        # Admin olmayanlar kisa_ad değiştiremesin (URL/bağımlılıklar için güvenli)
        if current_user.sistem_rol != 'admin':
            new_kisa_ad = kurum.kisa_ad

        if new_kisa_ad and new_kisa_ad != kurum.kisa_ad:
            existing = Kurum.query.filter_by(kisa_ad=new_kisa_ad).first()
            if existing:
                return jsonify({'success': False, 'message': 'Bu kısa adla bir kurum zaten mevcut'}), 400
            kurum.kisa_ad = new_kisa_ad
        
        # Diğer alanları güncelle
        if 'ticari_unvan' in data:
            kurum.ticari_unvan = data.get('ticari_unvan', '').strip()
        if 'faaliyet_alani' in data:
            kurum.faaliyet_alani = data.get('faaliyet_alani', '').strip()
        if 'sektor' in data:
            kurum.sektor = data.get('sektor', '').strip()
        if 'calisan_sayisi' in data:
            kurum.calisan_sayisi = data.get('calisan_sayisi')
        if 'email' in data:
            kurum.email = data.get('email', '').strip()
        if 'telefon' in data:
            kurum.telefon = data.get('telefon', '').strip()
        if 'web_adresi' in data:
            kurum.web_adresi = data.get('web_adresi', '').strip()
        
        # Opsiyonel alanlar
        if hasattr(Kurum, 'vergi_dairesi') and 'vergi_dairesi' in data:
            kurum.vergi_dairesi = data.get('vergi_dairesi', '').strip() or None
        if hasattr(Kurum, 'vergi_numarasi') and 'vergi_numarasi' in data:
            kurum.vergi_numarasi = data.get('vergi_numarasi', '').strip() or None
        if hasattr(Kurum, 'logo_url') and 'logo_url' in data:
            kurum.logo_url = data.get('logo_url', '').strip() or None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Kurum başarıyla güncellendi'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Kurum güncelleme hatası: {e}')
        return json_error(e, "[admin_update_organization]", 500)


@main_bp.route('/admin/delete-organization/<int:org_id>', methods=['DELETE'])
@login_required
def admin_delete_organization(org_id):
    """Kurum sil (soft delete) - Sadece sistem admini (kurum_id=1) kurumları silebilir"""
    try:
        # Sadece sistem admini kurumları silebilir
        is_system_admin = current_user.sistem_rol == 'admin' and current_user.kurum_id == 1
        
        if not is_system_admin:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok. Sadece sistem yöneticisi kurum silebilir.'}), 403

        kurum = Kurum.query.get(org_id)
        if not kurum:
            return jsonify({'success': False, 'message': 'Kurum bulunamadı'}), 404
        
        if kurum.silindi:
            return jsonify({'success': False, 'message': 'Bu kurum zaten silinmiş'}), 400

        # SOFT DELETE: Kurumu ve cascade ilişkilerini silindi=True yap
        kurum.silindi = True
        kurum.deleted_at = datetime.utcnow()
        kurum.deleted_by = current_user.id
        
        # Cascade: Kuruma bağlı tüm kullanıcıları soft delete yap
        User.query.filter_by(kurum_id=org_id, silindi=False).update({
            'silindi': True,
            'deleted_at': datetime.utcnow(),
            'deleted_by': current_user.id
        }, synchronize_session=False)
        
        # Cascade: Kuruma bağlı tüm süreçleri soft delete yap
        Surec.query.filter_by(kurum_id=org_id, silindi=False).update({
            'silindi': True,
            'deleted_at': datetime.utcnow(),
            'deleted_by': current_user.id
        }, synchronize_session=False)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Kurum ve ilgili tüm veriler arşivlendi. İsterseniz geri getirebilirsiniz.'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Kurum silme hatası: {e}')
        return json_error(e, "[admin_delete_organization]", 500)


@main_bp.route('/admin/restore-organization/<int:org_id>', methods=['POST'])
@login_required
def admin_restore_organization(org_id):
    """Kurum geri getir (restore) - Sadece sistem admini restore edebilir"""
    try:
        # Sadece sistem admini restore edebilir
        is_system_admin = current_user.sistem_rol == 'admin' and current_user.kurum_id == 1
        
        if not is_system_admin:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok. Sadece sistem yöneticisi kurum geri getirebilir.'}), 403

        kurum = Kurum.query.get(org_id)
        if not kurum:
            return jsonify({'success': False, 'message': 'Kurum bulunamadı'}), 404
        
        if not kurum.silindi:
            return jsonify({'success': False, 'message': 'Bu kurum zaten aktif'}), 400

        # Restore seçeneklerini al
        data = request.get_json() or {}
        restore_users = data.get('restore_users', True)
        restore_processes = data.get('restore_processes', True)

        # Kurumu restore et
        kurum.silindi = False
        kurum.deleted_at = None
        kurum.deleted_by = None
        
        # Cascade: İlişkili verileri restore et
        if restore_users:
            User.query.filter_by(kurum_id=org_id, silindi=True).update({
                'silindi': False,
                'deleted_at': None,
                'deleted_by': None
            }, synchronize_session=False)
        
        if restore_processes:
            Surec.query.filter_by(kurum_id=org_id, silindi=True).update({
                'silindi': False,
                'deleted_at': None,
                'deleted_by': None
            }, synchronize_session=False)
        
        db.session.commit()
        
        restore_info = []
        if restore_users:
            restore_info.append('kullanıcılar')
        if restore_processes:
            restore_info.append('süreçler')
        
        message = f'Kurum başarıyla geri getirildi'
        if restore_info:
            message += f' ({", ".join(restore_info)} dahil)'
        
        return jsonify({
            'success': True,
            'message': message
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Kurum restore hatası: {e}')
        return json_error(e, "[admin_restore_organization]", 500)


@main_bp.route('/api/guide/update-preferences', methods=['POST'])
@login_required
def update_guide_preferences():
    """Kullanıcının guide tercihlerini güncelle"""
    try:
        data = request.get_json()
        page_id = data.get('page_id')
        completed = data.get('completed', False)
        
        if not page_id:
            return jsonify({'success': False, 'message': 'page_id gerekli'}), 400
        
        # Completed walkthroughs JSON'ını güncelle
        completed_walkthroughs = {}
        if current_user.completed_walkthroughs:
            try:
                import json
                completed_walkthroughs = json.loads(current_user.completed_walkthroughs)
            except Exception as e:
                current_app.logger.warning(f"[update_guide_preferences] suppressed: {e}")
        
        if completed:
            completed_walkthroughs[page_id] = True
        
        import json
        current_user.completed_walkthroughs = json.dumps(completed_walkthroughs)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        current_app.logger.error(f'Guide preferences güncelleme hatası: {e}')
        return json_error(e, "[update_guide_preferences]", 500)


@main_bp.route('/api/guide/update-settings', methods=['POST'])
@login_required
def update_guide_settings():
    """Kullanıcının guide ayarlarını güncelle (settings sayfasından)"""
    try:
        data = request.get_json()
        show_page_guides = data.get('show_page_guides', True)
        guide_character_style = data.get('guide_character_style', 'professional')
        
        # Validate character style
        if guide_character_style not in ['professional', 'friendly', 'minimal']:
            return jsonify({'success': False, 'message': 'Geçersiz karakter stili'}), 400
        
        # Update user settings
        current_user.show_page_guides = show_page_guides
        current_user.guide_character_style = guide_character_style
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        current_app.logger.error(f'Guide settings güncelleme hatası: {e}')
        return json_error(e, "[update_guide_settings]", 500)


@main_bp.route('/api/guide/reset-walkthroughs', methods=['POST'])
@login_required
def reset_walkthroughs():
    """Tüm completed walkthroughs'u sıfırla"""
    try:
        current_user.completed_walkthroughs = None
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        current_app.logger.error(f'Walkthrough sıfırlama hatası: {e}')
        return json_error(e, "[reset_walkthroughs]", 500)


@main_bp.route('/admin/feedback/<int:feedback_id>/detail', methods=['GET'])
@login_required
def get_feedback_detail(feedback_id):
    """Geri bildirim detaylarını getir"""
    if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
        return jsonify({'success': False, 'message': 'Yetkiniz yok.'}), 403
    
    try:
        feedback = Feedback.query.get_or_404(feedback_id)
        
        # Yetki kontrolü
        is_system_admin = current_user.sistem_rol == 'admin' and current_user.kurum_id == 1
        if not is_system_admin:
            from app.models.legacy_bridge import User
            user = User.query.get(feedback.user_id)
            if user.kurum_id != current_user.kurum_id:
                return jsonify({'success': False, 'message': 'Bu geri bildirimi görüntüleyemezsiniz.'}), 403
        
        # User bilgilerini güvenli şekilde al
        user_name = feedback.user.first_name or feedback.user.email if feedback.user else 'Bilinmeyen Kullanıcı'
        user_email = feedback.user.email if feedback.user else ''
        
        return jsonify({
            'success': True,
            'feedback': {
                'id': feedback.id,
                'user_name': user_name,
                'user_email': user_email,
                'category': feedback.category,
                'description': feedback.description or '',
                'page_url': feedback.page_url or '',
                'screenshot_path': feedback.screenshot_path or '',
                'status': feedback.status,
                'admin_note': feedback.admin_note or '',
                'created_at': feedback.created_at.strftime('%d.%m.%Y %H:%M') if feedback.created_at else '',
                'updated_at': feedback.updated_at.strftime('%d.%m.%Y %H:%M') if feedback.updated_at else ''
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Feedback detay hatası: {e}', exc_info=True)
        error_message = str(e) if current_app.debug else 'Bir hata oluştu.'
        return jsonify({'success': False, 'message': error_message}), 500


@main_bp.route('/admin/feedback/<int:feedback_id>/update-status', methods=['POST'])
@login_required
def update_feedback_status(feedback_id):
    """Geri bildirim durumunu güncelle"""
    if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
        return jsonify({'success': False, 'message': 'Yetkiniz yok.'}), 403
    
    try:
        data = request.get_json()
        new_status = data.get('status')
        admin_note = data.get('admin_note', '')
        
        feedback = Feedback.query.get_or_404(feedback_id)
        
        # Yetki kontrolü (sistem admini değilse sadece kendi kurumunun feedback'lerini güncelleyebilir)
        is_system_admin = current_user.sistem_rol == 'admin' and current_user.kurum_id == 1
        if not is_system_admin:
            from app.models.legacy_bridge import User
            user = User.query.get(feedback.user_id)
            if user.kurum_id != current_user.kurum_id:
                return jsonify({'success': False, 'message': 'Bu geri bildirimi güncelleyemezsiniz.'}), 403
        
        # Durum kontrolü
        valid_statuses = ['Bekliyor', 'İnceleniyor', 'Çözüldü', 'Reddedildi']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': 'Geçersiz durum.'}), 400
        
        # Eski durumu kaydet (bildirim için)
        old_status = feedback.status
        
        feedback.status = new_status
        if admin_note:
            feedback.admin_note = admin_note
        feedback.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Durum değiştiyse kullanıcıya bildirim gönder
        if old_status != new_status:
            try:
                from services.notification_service import create_feedback_status_notification
                create_feedback_status_notification(feedback.id, old_status, new_status, current_user.id)
            except Exception as e:
                current_app.logger.error(f'Feedback bildirim gönderme hatası: {e}', exc_info=True)
                # Bildirim hatası durumu güncellemeyi engellemez
        
        return jsonify({
            'success': True,
            'message': 'Durum güncellendi.',
            'status': new_status
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Feedback durum güncelleme hatası: {e}', exc_info=True)
        return jsonify({'success': False, 'message': 'Bir hata oluştu.'}), 500


@main_bp.route('/submit-feedback', methods=['POST'])
@login_required
def submit_feedback():
    """
    Kule İletişim Modülü - Geri Bildirim Gönderme
    
    Kullanıcıların sistem hakkında hata bildirimi, öneri veya talep göndermesi için.
    """
    try:
        # Klasör kontrolü ve oluşturma
        feedback_upload_dir = os.path.join(current_app.static_folder, 'uploads', 'feedback')
        if not os.path.exists(feedback_upload_dir):
            os.makedirs(feedback_upload_dir, exist_ok=True)
            current_app.logger.info(f'Feedback upload klasörü oluşturuldu: {feedback_upload_dir}')
        
        # Form verilerini al
        page_url = request.form.get('page_url', '')
        category = request.form.get('category', '')
        description = request.form.get('description', '')
        
        # Validasyon
        if not category or not description:
            return jsonify({
                'success': False,
                'message': 'Kategori ve mesaj alanları zorunludur.'
            }), 400
        
        # Kategori kontrolü (yeni kategoriler)
        valid_categories = ['Tasarım Hatası', 'Hesaplama Hatası', 'Çalışmayan Buton', 'Çalışmayan Fonksiyon', 'Diğer']
        if category not in valid_categories:
            return jsonify({
                'success': False,
                'message': 'Geçersiz kategori seçimi.'
            }), 400
        
        # Kullanıcı kontrolü
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'message': 'Giriş yapmanız gerekiyor.'
            }), 401
        
        # Ekran görüntüsü işleme (varsa)
        screenshot_path = None
        if 'screenshot' in request.files:
            screenshot_file = request.files['screenshot']
            
            # Dosya seçilmiş mi kontrol et
            if screenshot_file and screenshot_file.filename:
                # S7 (2026-07-21): yalnız uzantı kontrolü vardı — dosya
                # `current_app.static_folder` altına, yani WEBROOT'a yazılıyor.
                # Uzantı saldırganın seçtiği bir metin; içerik doğrulanmalı.
                # app/utils/upload_security magic byte + SVG script taraması
                # yapıyor ve projede zaten kullanılıyordu.
                from app.utils.upload_security import validate_uploaded_image
                _blob = screenshot_file.read()
                screenshot_file.seek(0)
                _ok, _msg, _ext = validate_uploaded_image(
                    _blob, {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                )
                if not _ok:
                    current_app.logger.warning(
                        '[feedback_upload] reddedildi (ad=%r): %s',
                        screenshot_file.filename, _msg,
                    )
                    return jsonify({
                        'success': False,
                        'message': 'Sadece resim dosyaları kabul edilir (PNG, JPG, JPEG, GIF, WEBP).'
                    }), 400

                # Güvenli dosya adı oluştur
                original_filename = secure_filename(screenshot_file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
                screenshot_path = os.path.join('uploads', 'feedback', unique_filename)
                full_path = os.path.join(current_app.static_folder, screenshot_path)
                
                # Dosyayı kaydet
                screenshot_file.save(full_path)
                current_app.logger.info(f'Feedback ekran görüntüsü kaydedildi: {full_path}')
        
        # Veritabanına kaydet
        feedback = Feedback(
            user_id=current_user.id,
            page_url=page_url,
            category=category,
            description=description,
            screenshot_path=screenshot_path,
            status='Bekliyor'
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        current_app.logger.info(f'Yeni geri bildirim kaydedildi: ID={feedback.id}, Kullanıcı={current_user.email}, Kategori={category}')
        
        return jsonify({
            'success': True,
            'message': 'Geri bildirim alındı. Teşekkür ederiz!'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Feedback gönderim hatası: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Bir hata oluştu. Lütfen tekrar deneyin.'
        }), 500
