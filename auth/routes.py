# -*- coding: utf-8 -*-
"""
Authentication Routes
Login, logout ve profil yönetimi route'ları
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Kurum, UserActivityLog
from extensions import limiter, csrf
import json
import os
import uuid
import logging

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    """Ana sayfa. Kullanıcı giriş yapmışsa dashboard'a, yapmamışsa login sayfasına yönlendirir."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10/minute;100/hour", error_message="Çok fazla giriş denemesi. Lütfen biraz bekleyip tekrar deneyin.")
def login():
    """Kullanıcı giriş sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        kurum_id = request.form.get('kurum_id')
        quick_login = request.form.get('quick_login')  # Kolay giriş checkbox
        
        if not username:
            flash('Lütfen bir kullanıcı seçin.', 'danger')
            kurumlar = Kurum.query.order_by(Kurum.kisa_ad).all()
            kullanicilar = User.query.order_by(User.kurum_id, User.first_name, User.username).all()
            return render_template('login.html', kurumlar=kurumlar, kullanicilar=kullanicilar)
        
        # Kurum ID varsa önce hem username hem kurum_id ile ara
        # Bulunamazsa sadece username ile ara (kurum_id yanlış olabilir)
        user = None
        if kurum_id:
            user = User.query.filter_by(username=username, kurum_id=kurum_id).first()
        
        # Kurum ID ile bulunamadıysa veya kurum ID yoksa, sadece username ile ara
        if not user:
            user = User.query.filter_by(username=username).first()
        
        # Kolay giriş: şifre doğrulamasız giriş yapma
        if quick_login and user:
            login_user(user, remember=True)
            current_app.logger.info(f'Kullanıcı kolay giriş yaptı: {user.username} (ID: {user.id}, Kurum: {user.kurum.kisa_ad})')
            
            # Aktivite logu
            try:
                activity = UserActivityLog(
                    user_id=user.id,
                    tip='login',
                    baslik='Kolay Giriş',
                    aciklama='Sistem kolay giriş seçeneğiyle açıldı.'
                )
                db.session.add(activity)
                db.session.commit()
            except Exception as e:
                current_app.logger.error(f'Aktivite kaydetme hatası: {str(e)}')
                db.session.rollback()
            
            flash(f'Hoş geldiniz {user.username}!', 'success')
            return redirect(url_for('main.dashboard'))
        
        # Normal giriş: şifre doğrulama
        if not password:
            flash('Lütfen kullanıcı adı ve şifre girin veya kolay giriş seçeneğini kullanın.', 'danger')
            kurumlar = Kurum.query.order_by(Kurum.kisa_ad).all()
            kullanicilar = User.query.order_by(User.kurum_id, User.first_name, User.username).all()
            return render_template('login.html', kurumlar=kurumlar, kullanicilar=kullanicilar)
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            current_app.logger.info(f'Kullanıcı giriş yaptı: {user.username} (ID: {user.id}, Kurum: {user.kurum.kisa_ad})')
            
            # Aktivite logu
            try:
                activity = UserActivityLog(
                    user_id=user.id,
                    tip='login',
                    baslik='Oturum Açıldı',
                    aciklama='Sisteme başarıyla giriş yapıldı.'
                )
                db.session.add(activity)
                db.session.commit()
            except Exception as e:
                current_app.logger.error(f'Aktivite kaydetme hatası: {str(e)}')
                db.session.rollback()
            
            flash(f'Hoş geldiniz {user.username}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            current_app.logger.warning(f'Başarısız giriş denemesi: {username}')
            flash('Giriş bilgileriniz hatalı. Lütfen kullanıcı adı ve şifrenizi kontrol edin.', 'danger')
    
    # Kurumları ve tüm kullanıcıları getir
    kurumlar = Kurum.query.order_by(Kurum.kisa_ad).all()
    kullanicilar = User.query.order_by(User.kurum_id, User.first_name, User.username).all()
    return render_template('login.html', kurumlar=kurumlar, kullanicilar=kullanicilar)


@auth_bp.route('/easy-login')
def easy_login():
    """Kolay giriş sayfası - Tüm kullanıcıları listele (Development Only)"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    users = User.query.order_by(
        User.sistem_rol.desc(),  # Admin önce
        User.kurum_id,
        User.username
    ).all()
    
    return render_template('easy_login.html', users=users, form=None)


@auth_bp.route('/logout')
@login_required
def logout():
    """Kullanıcı çıkış işlemi"""
    current_app.logger.info(f'Kullanıcı çıkış yaptı: {current_user.username} (ID: {current_user.id})')
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    """Kullanıcı profil sayfası"""
    return render_template('profile.html')


@auth_bp.route('/profile/update', methods=['POST'])
@csrf.exempt  # JSON API için CSRF'den muaf (login_required zaten güvenlik sağlıyor)
@login_required
def update_profile():
    """Kullanıcı profilini güncelle"""
    try:
        data = request.get_json()
        
        # Şifre değişikliği kontrolü
        if data.get('current_password') or data.get('new_password'):
            if not data.get('current_password'):
                return jsonify({'success': False, 'message': 'Şifre değiştirmek için mevcut şifrenizi girmelisiniz!'}), 400
            
            if not check_password_hash(current_user.password_hash, data.get('current_password')):
                return jsonify({'success': False, 'message': 'Mevcut şifre yanlış!'}), 400
            
            if not data.get('new_password'):
                return jsonify({'success': False, 'message': 'Yeni şifre girmelisiniz!'}), 400
            
            if len(data.get('new_password', '')) < 6:
                return jsonify({'success': False, 'message': 'Yeni şifre en az 6 karakter olmalıdır!'}), 400
            
            # Şifreyi güncelle
            current_user.password_hash = generate_password_hash(data.get('new_password'))
        
        # E-posta değişikliği kontrolü
        if data.get('email') != current_user.email:
            existing = User.query.filter_by(email=data.get('email')).first()
            if existing and existing.id != current_user.id:
                return jsonify({'success': False, 'message': 'Bu e-posta adresi başka bir kullanıcı tarafından kullanılıyor!'}), 400
            current_user.email = data.get('email')
        
        # Profil bilgilerini güncelle
        current_user.first_name = data.get('first_name', '')
        current_user.last_name = data.get('last_name', '')
        current_user.phone = data.get('phone', '')
        current_user.title = data.get('title', '')
        current_user.department = data.get('department', '')
        current_user.profile_photo = data.get('profile_photo', '')
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Profil başarıyla güncellendi.'}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Profil güncelleme hatası: {str(e)}')
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Profil güncellenirken hata oluştu: {str(e)}'}), 500, {'Content-Type': 'application/json'}


@auth_bp.route('/profile/upload-photo', methods=['POST'])
@csrf.exempt  # File upload için CSRF'den muaf tutuyoruz (login_required zaten var)
@login_required
def upload_profile_photo():
    """Kullanıcı kendi profil fotoğrafını yükle"""
    try:
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'Dosya seçilmedi!'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Dosya seçilmedi!'}), 400
        
        # Dosya tipini kontrol et
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'success': False, 'message': f'Geçersiz dosya tipi! İzin verilen tipler: {", ".join(allowed_extensions)}'}), 400
        
        # Güvenli dosya adı oluştur
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Upload klasörünü oluştur
        upload_folder = os.path.join('static', 'uploads', 'profiles')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Dosyayı kaydet
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Eski fotoğrafı sil (varsa ve static klasöründeyse)
        if current_user.profile_photo:
            old_photo = current_user.profile_photo
            if old_photo.startswith('/static/') or old_photo.startswith('static/'):
                old_path = old_photo.lstrip('/')
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except Exception as e:
                        current_app.logger.warning(f'Eski profil fotoğrafı silinemedi: {e}')
        
        # Veritabanında güncelle
        current_user.profile_photo = f'/static/uploads/profiles/{unique_filename}'
        db.session.commit()
        
        logging.info(f'Profil fotoğrafı güncellendi: {current_user.username} -> {unique_filename}')
        
        return jsonify({
            'success': True,
            'message': 'Profil fotoğrafı başarıyla yüklendi!',
            'photo_url': current_user.profile_photo
        }), 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Profil fotoğrafı yükleme hatası: {str(e)} - Kullanıcı: {current_user.username}')
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Profil fotoğrafı yüklenirken hata oluştu: {str(e)}'}), 500, {'Content-Type': 'application/json'}


@auth_bp.route('/settings')
@login_required
def settings():
    """Kullanıcı ayarlar sayfası"""
    return render_template('settings.html')


@auth_bp.route('/api/user/theme', methods=['POST'])
@login_required
def api_user_theme():
    """Kullanıcı tema tercihini kaydet"""
    try:
        data = request.get_json()
        theme = data.get('theme', 'light')
        
        import json
        prefs = {}
        if current_user.theme_preferences:
            try:
                prefs = json.loads(current_user.theme_preferences)
            except:
                pass
        
        prefs['theme'] = theme
        current_user.theme_preferences = json.dumps(prefs)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Tema tercihi kaydedildi'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@auth_bp.route('/api/user/layout', methods=['POST'])
@login_required
def api_user_layout():
    """Kullanıcı layout tercihini kaydet"""
    try:
        data = request.get_json()
        layout = data.get('layout', 'classic')
        
        if layout not in ['classic', 'sidebar']:
            return jsonify({'success': False, 'message': 'Geçersiz layout'}), 400
        
        current_user.layout_preference = layout
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Layout tercihi kaydedildi'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@auth_bp.route('/settings/notifications', methods=['POST'])
@login_required
def update_notification_settings():
    """Bildirim ayarlarını güncelle"""
    try:
        data = request.get_json()
        # TODO: Bildirim ayarlarını veritabanına kaydet
        # Şimdilik başarılı döndür
        current_app.logger.info(f'Bildirim ayarları güncellendi: {current_user.username}')
        return jsonify({'success': True, 'message': 'Bildirim ayarları kaydedildi!'})
    except Exception as e:
        current_app.logger.error(f'Bildirim ayarları hatası: {str(e)}')
        return jsonify({'success': False, 'message': str(e)}), 500