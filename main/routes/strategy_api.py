# -*- coding: utf-8 -*-
# Otomatik bölüm — `python scripts/dev/split_main_routes.py`
from main.routes._common import *  # noqa: F401,F403
from main.routes import main_bp
from main.deprecated import legacy_html_to_platform

# ─────────────────────────────────────────────────────────────────────────────
# DALGA 1 (2026-06-16): Legacy kurum kimlik + strateji yazma route'ları kaldırıldı.
# Bunlar legacy `kurum`/`ana_strateji`/`alt_strateji`/`deger`/`etik_kural`/
# `kalite_politikasi` tablolarına yazıyordu (çift-model borcu). Tamamı ÖLÜYDÜ:
# çağıran tüm template'ler (templates/admin_v3.html, kurum_panel.html …) ya hiç
# render edilmiyor ya da /kurum-paneli, /admin-panel gibi route'lar
# legacy_redirect ile modern platforma 301 yönleniyordu. Canlı yazma yolu modern
# tenants + tenant_year_identities (micro/modules/kurum + sp). Veri kaybı 0
# (legacy alanlar tüm tenant'larda boştu — teyit edildi).
# Kaldırılan route'lar: /kurum/ana-stratejiler/*, /kurum/alt-stratejiler/*,
#   /kurum/update-amac-vizyon, /kurum/degerler/*, /kurum/etik-kurallari/*,
#   /kurum/kalite-politikalari/*
# ─────────────────────────────────────────────────────────────────────────────




@main_bp.route('/ai-chat')
@login_required
def ai_chat():
    """AI Chat sayfası"""
    return render_template('ai_chat.html')


# 2026-06-17: /stratejik-asistan kaldırıldı — redirect-ölüydü (GET 301 → /sp,
# runtime teyit). safe_urls.py fallback: main.stratejik_asistan → app_bp.sp.
# (ai_chat ve ai_coach CANLI — 302→login, dokunulmadı.)


@main_bp.route('/ai-coach')
@login_required
def ai_coach_page():
    """AI Coach sayfası - Skor motoru verilerini Gemini ile analiz ettirir."""
    try:
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
            return redirect(url_for('main.dashboard'))
        return render_template('ai_coach.html')
    except Exception as e:
        import traceback
        current_app.logger.error(f'AI Coach sayfası hatası: {str(e)}')
        current_app.logger.error(traceback.format_exc())
        return f"Sayfa yüklenemedi: {str(e)}", 500


@main_bp.route('/strategy/matrix')
@login_required
def strategy_matrix():
    """Strateji-Süreç Matrisi görüntüleme sayfası"""
    try:
        # Tüm alt stratejileri ana stratejileriyle birlikte çek
        sub_strategies = db.session.query(SubStrategy).join(MainStrategy).filter(
            MainStrategy.kurum_id == current_user.kurum_id
        ).order_by(MainStrategy.code, SubStrategy.code).all()
        
        # Tüm süreçleri çek (weight veya code sırasına göre)
        processes = Process.query.filter_by(kurum_id=current_user.kurum_id).order_by(
            Process.weight.desc(), Process.code
        ).all()
        
        # Tüm matris ilişkilerini çek
        matrix_relations = StrategyProcessMatrix.query.join(SubStrategy).join(MainStrategy).filter(
            MainStrategy.kurum_id == current_user.kurum_id
        ).all()
        
        # İlişkileri dictionary'ye çevir: relations_map[(sub_strategy_id, process_id)] = score
        relations_map = {}
        for relation in matrix_relations:
            key = (relation.sub_strategy_id, relation.process_id)
            relations_map[key] = relation.relationship_score
        
        # Ana stratejileri gruplamak için
        main_strategies = {}
        for sub_strategy in sub_strategies:
            main_id = sub_strategy.ana_strateji_id
            if main_id not in main_strategies:
                main_strategy = MainStrategy.query.get(main_id)
                main_strategies[main_id] = {
                    'strategy': main_strategy,
                    'subs': []
                }
            main_strategies[main_id]['subs'].append(sub_strategy)
        
        # Her süreç için toplam puan hesapla
        process_totals = {}
        for process in processes:
            total_score = 0
            for sub_strategy in sub_strategies:
                key = (sub_strategy.id, process.id)
                score = relations_map.get(key, 0)
                total_score += score
            process_totals[process.id] = total_score
        
        # En yüksek puana sahip ilk 3 süreci belirle (önem derecesi için)
        sorted_processes = sorted(process_totals.items(), key=lambda x: x[1], reverse=True)
        top_3_process_ids = {pid for pid, score in sorted_processes[:3]} if len(sorted_processes) >= 3 else set()
        
        return render_template('strategy/matrix.html',
                             sub_strategies=sub_strategies,
                             processes=processes,
                             relations_map=relations_map,
                             main_strategies=main_strategies,
                             process_totals=process_totals,
                             top_3_process_ids=top_3_process_ids)
    except Exception as e:
        import traceback
        current_app.logger.error(f'Strateji Matrisi sayfası hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        flash(f'Matris görüntülenirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/strategy/update_cell', methods=['POST'])
@login_required
@csrf.exempt  # AJAX için CSRF muafiyeti
def update_strategy_cell():
    """Strateji-Süreç matris hücresini güncelle (Toggle: Yok->9->3->Sil)"""
    try:
        data = request.get_json()
        sub_strategy_id = data.get('sub_strategy_id')
        process_id = data.get('process_id')
        
        if not sub_strategy_id or not process_id:
            return jsonify({'success': False, 'error': 'Eksik parametre'}), 400
        
        # Kullanıcının kurumuna ait strateji ve süreç olduğunu kontrol et
        sub_strategy = SubStrategy.query.join(MainStrategy).filter(
            SubStrategy.id == sub_strategy_id,
            MainStrategy.kurum_id == current_user.kurum_id
        ).first()
        
        process = Process.query.filter_by(
            id=process_id,
            kurum_id=current_user.kurum_id
        ).first()
        
        if not sub_strategy or not process:
            return jsonify({'success': False, 'error': 'Strateji veya süreç bulunamadı'}), 404
        
        # Mevcut ilişkiyi kontrol et
        relation = StrategyProcessMatrix.query.filter_by(
            sub_strategy_id=sub_strategy_id,
            process_id=process_id
        ).first()
        
        # Toggle mantığı: Yok -> 9 (A) -> 3 (B) -> Sil
        if not relation:
            # İlişki yoksa -> Puanı 9 (A) yap
            new_relation = StrategyProcessMatrix(
                sub_strategy_id=sub_strategy_id,
                process_id=process_id,
                relationship_score=9
            )
            db.session.add(new_relation)
            db.session.commit()
            return jsonify({
                'success': True,
                'new_score': 9,
                'text': 'A',
                'class': 'bg-success-subtle text-success-emphasis',
                'title': 'Puan: 9 (Güçlü İlişki - A)'
            })
        elif relation.relationship_score == 9:
            # Puan 9 ise -> Puanı 3 (B) yap
            relation.relationship_score = 3
            db.session.commit()
            return jsonify({
                'success': True,
                'new_score': 3,
                'text': 'B',
                'class': 'bg-warning-subtle text-warning-emphasis',
                'title': 'Puan: 3 (Zayıf İlişki - B)'
            })
        elif relation.relationship_score == 3:
            # Puan 3 ise -> İlişkiyi sil
            db.session.delete(relation)
            db.session.commit()
            return jsonify({
                'success': True,
                'new_score': None,
                'text': '-',
                'class': 'text-muted',
                'title': 'İlişki yok'
            })
        else:
            # Beklenmeyen puan değeri, 9'a sıfırla
            relation.relationship_score = 9
            db.session.commit()
            return jsonify({
                'success': True,
                'new_score': 9,
                'text': 'A',
                'class': 'bg-success-subtle text-success-emphasis',
                'title': 'Puan: 9 (Güçlü İlişki - A)'
            })
            
    except Exception as e:
        import traceback
        current_app.logger.error(f'Matris hücresi güncelleme hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@main_bp.route('/strategy/projects')
@login_required
@role_required(['admin', 'kurum_yoneticisi', 'ust_yonetim'])
def strategy_projects():
    """Stratejik Proje Portföyü - Projeleri stratejik puana göre sırala"""
    try:
        # 1. Süreç puanlarını hesapla (strategy_matrix mantığı)
        sub_strategies = db.session.query(SubStrategy).join(MainStrategy).filter(
            MainStrategy.kurum_id == current_user.kurum_id
        ).all()
        
        processes = Process.query.filter_by(kurum_id=current_user.kurum_id).all()
        
        matrix_relations = StrategyProcessMatrix.query.join(SubStrategy).join(MainStrategy).filter(
            MainStrategy.kurum_id == current_user.kurum_id
        ).all()
        
        # İlişkileri dictionary'ye çevir
        relations_map = {}
        for relation in matrix_relations:
            key = (relation.sub_strategy_id, relation.process_id)
            relations_map[key] = relation.relationship_score
        
        # Her süreç için toplam puan hesapla
        process_totals = {}
        for process in processes:
            total_score = 0
            for sub_strategy in sub_strategies:
                key = (sub_strategy.id, process.id)
                score = relations_map.get(key, 0)
                total_score += score
            process_totals[process.id] = total_score
        
        # 2. Tüm projeleri çek
        projects = Project.query.filter_by(kurum_id=current_user.kurum_id, is_archived=False).all()
        
        # 3. Her proje için stratejik puan hesapla
        projects_with_scores = []
        for project in projects:
            # Projenin bağlı olduğu süreçlerin puanlarını topla
            project_score = 0
            related_process_names = []
            for process in project.related_processes:
                process_score = process_totals.get(process.id, 0)
                project_score += process_score
                related_process_names.append({
                    'name': process.ad,
                    'code': process.code,
                    'score': process_score
                })
            
            projects_with_scores.append({
                'project': project,
                'strategic_score': project_score,
                'related_processes': related_process_names
            })
        
        # 4. Puana göre büyükten küçüğe sırala
        projects_with_scores.sort(key=lambda x: x['strategic_score'], reverse=True)
        
        return render_template('strategy/project_portfolio.html',
                             projects_with_scores=projects_with_scores,
                             process_totals=process_totals)
    except Exception as e:
        import traceback
        current_app.logger.error(f'Stratejik Proje Portföyü hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        flash(f'Proje portföyü görüntülenirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/strategy/project/<int:id>')
@login_required
@role_required(['admin', 'kurum_yoneticisi', 'ust_yonetim'])
def strategy_project_detail(id):
    """Stratejik Proje Detay Sayfası - Projenin stratejik uyum analizi"""
    try:
        # Projeyi çek
        project = Project.query.filter_by(id=id, kurum_id=current_user.kurum_id).first_or_404()
        
        # Süreç puanlarını hesapla (strategy_matrix mantığı)
        sub_strategies = db.session.query(SubStrategy).join(MainStrategy).filter(
            MainStrategy.kurum_id == current_user.kurum_id
        ).all()
        
        processes = Process.query.filter_by(kurum_id=current_user.kurum_id).all()
        
        matrix_relations = StrategyProcessMatrix.query.join(SubStrategy).join(MainStrategy).filter(
            MainStrategy.kurum_id == current_user.kurum_id
        ).all()
        
        # İlişkileri dictionary'ye çevir
        relations_map = {}
        for relation in matrix_relations:
            key = (relation.sub_strategy_id, relation.process_id)
            relations_map[key] = relation.relationship_score
        
        # Her süreç için toplam puan hesapla
        process_totals = {}
        for process in processes:
            total_score = 0
            for sub_strategy in sub_strategies:
                key = (sub_strategy.id, process.id)
                score = relations_map.get(key, 0)
                total_score += score
            process_totals[process.id] = total_score
        
        # Projenin bağlı süreçleri ve puanları
        project_processes = []
        total_strategic_score = 0
        strong_relations = 0  # A (9 puan)
        weak_relations = 0    # B (3 puan)
        
        for process in project.related_processes:
            process_score = process_totals.get(process.id, 0)
            total_strategic_score += process_score
            
            # Bu süreç için matris ilişkilerini say
            for sub_strategy in sub_strategies:
                key = (sub_strategy.id, process.id)
                score = relations_map.get(key, 0)
                if score == 9:
                    strong_relations += 1
                elif score == 3:
                    weak_relations += 1
            
            project_processes.append({
                'process': process,
                'score': process_score
            })
        
        # Süreçleri puana göre sırala
        project_processes.sort(key=lambda x: x['score'], reverse=True)
        
        # Mevcut bağlı süreç ID'lerini al (modal için)
        related_process_ids = [p.id for p in project.related_processes]
        
        return render_template('strategy/project_detail.html',
                             project=project,
                             project_processes=project_processes,
                             total_strategic_score=total_strategic_score,
                             strong_relations=strong_relations,
                             weak_relations=weak_relations,
                             processes=processes,
                             process_totals=process_totals,
                             related_process_ids=related_process_ids)
    except Exception as e:
        import traceback
        current_app.logger.error(f'Proje detay sayfası hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        flash(f'Proje detayı görüntülenirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('main.strategy_projects'))


@main_bp.route('/strategy/project/<int:id>/update_processes', methods=['POST'])
@login_required
@role_required(['admin', 'kurum_yoneticisi', 'ust_yonetim'])
def strategy_project_update_processes(id):
    """Proje-Süreç ilişkilerini güncelle"""
    try:
        # Projeyi çek ve yetki kontrolü yap
        project = Project.query.filter_by(id=id, kurum_id=current_user.kurum_id).first_or_404()
        
        # Formdan gelen seçili süreç ID'lerini al
        selected_process_ids = request.form.getlist('process_ids')
        selected_process_ids = [int(pid) for pid in selected_process_ids if pid]
        
        # Süreçlerin kullanıcının kurumuna ait olduğunu kontrol et
        valid_processes = Process.query.filter_by(kurum_id=current_user.kurum_id).filter(
            Process.id.in_(selected_process_ids)
        ).all()
        
        # Mevcut ilişkileri temizle
        project.related_processes.clear()
        
        # Yeni seçilen süreçleri ekle
        for process in valid_processes:
            project.related_processes.append(process)
        
        # Değişiklikleri kaydet
        db.session.commit()
        
        flash('Süreç ilişkileri başarıyla güncellendi.', 'success')
        return redirect(url_for('main.strategy_project_detail', id=project.id))
        
    except Exception as e:
        import traceback
        current_app.logger.error(f'Proje süreç güncelleme hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        db.session.rollback()
        flash(f'Süreç ilişkileri güncellenirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('main.strategy_project_detail', id=id))


@main_bp.route('/strategy/project/add', methods=['POST'])
@login_required
@role_required(['admin', 'kurum_yoneticisi', 'ust_yonetim'])
def strategy_project_add():
    """Yeni proje oluştur"""
    try:
        # Form verilerini al
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        priority = request.form.get('priority', 'Orta')

        # Bildirim ayarları
        reminder_days_raw = (request.form.get('notification_reminder_days') or '').strip()
        overdue_frequency = (request.form.get('notification_overdue_frequency') or 'daily').strip().lower()
        notify_manager = request.form.get('notification_notify_manager') is not None
        notify_observers = request.form.get('notification_notify_observers') is not None
        channel_email = request.form.get('notification_channel_email') is not None

        reminder_days = [7, 3, 1]
        if reminder_days_raw:
            parts = [p.strip() for p in re.split(r"[;,\s]+", reminder_days_raw) if p.strip()]
            parsed_days = []
            for part in parts:
                if part.isdigit():
                    parsed_days.append(int(part))
            parsed_days = sorted(list(set([d for d in parsed_days if d >= 0])), reverse=True)
            if parsed_days:
                reminder_days = parsed_days

        if overdue_frequency not in ['daily', 'off']:
            overdue_frequency = 'daily'

        notification_settings = {
            'reminder_days': reminder_days,
            'overdue_frequency': overdue_frequency,
            'channels': {'in_app': True, 'email': channel_email},
            'notify_manager': notify_manager,
            'notify_observers': notify_observers,
        }
        
        # Validasyon
        if not name:
            flash('Proje adı zorunludur.', 'error')
            return redirect(url_for('main.strategy_projects'))
        
        # Tarihleri parse et
        start_date = None
        end_date = None
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Yeni proje oluştur
        new_project = Project(
            name=name,
            description=description if description else None,
            start_date=start_date,
            end_date=end_date,
            priority=priority,
            kurum_id=current_user.kurum_id,
            manager_id=current_user.id  # Varsayılan olarak oturum açan kullanıcıyı yönetici yap
        )

        try:
            new_project.notification_settings = json.dumps(notification_settings, ensure_ascii=False)
        except Exception:
            pass
        
        db.session.add(new_project)
        db.session.commit()
        
        flash('Proje başarıyla oluşturuldu.', 'success')
        return redirect(url_for('main.strategy_projects'))
        
    except Exception as e:
        import traceback
        current_app.logger.error(f'Proje oluşturma hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        db.session.rollback()
        flash(f'Proje oluşturulurken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('main.strategy_projects'))


@main_bp.route('/strategy/project/<int:id>/edit', methods=['POST'])
@login_required
@role_required(['admin', 'kurum_yoneticisi', 'ust_yonetim'])
def strategy_project_edit(id):
    """Proje bilgilerini güncelle"""
    try:
        # Projeyi çek ve yetki kontrolü yap
        project = Project.query.filter_by(id=id, kurum_id=current_user.kurum_id).first_or_404()
        
        # Form verilerini al
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        priority = request.form.get('priority', 'Orta')

        # Bildirim ayarları
        reminder_days_raw = (request.form.get('notification_reminder_days') or '').strip()
        overdue_frequency = (request.form.get('notification_overdue_frequency') or '').strip().lower()
        notify_manager = request.form.get('notification_notify_manager') is not None
        notify_observers = request.form.get('notification_notify_observers') is not None
        channel_email = request.form.get('notification_channel_email') is not None

        reminder_days = None
        if reminder_days_raw:
            parts = [p.strip() for p in re.split(r"[;,\s]+", reminder_days_raw) if p.strip()]
            parsed_days = []
            for part in parts:
                if part.isdigit():
                    parsed_days.append(int(part))
            parsed_days = sorted(list(set([d for d in parsed_days if d >= 0])), reverse=True)
            if parsed_days:
                reminder_days = parsed_days

        if overdue_frequency and overdue_frequency not in ['daily', 'off']:
            overdue_frequency = ''
        
        # Validasyon
        if not name:
            flash('Proje adı zorunludur.', 'error')
            return redirect(url_for('main.strategy_projects'))
        
        # Tarihleri parse et
        start_date = None
        end_date = None
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Projeyi güncelle
        project.name = name
        project.description = description if description else None
        project.start_date = start_date
        project.end_date = end_date
        project.priority = priority

        # notification_settings merge
        try:
            current_settings = project.get_notification_settings()
            if reminder_days is not None:
                current_settings['reminder_days'] = reminder_days
            if overdue_frequency:
                current_settings['overdue_frequency'] = overdue_frequency
            current_settings['notify_manager'] = notify_manager
            current_settings['notify_observers'] = notify_observers
            current_settings.setdefault('channels', {})
            current_settings['channels']['in_app'] = True
            current_settings['channels']['email'] = channel_email
            project.notification_settings = json.dumps(current_settings, ensure_ascii=False)
        except Exception:
            pass
        
        db.session.commit()
        
        flash('Proje başarıyla güncellendi.', 'success')
        return redirect(url_for('main.strategy_projects'))
        
    except Exception as e:
        import traceback
        current_app.logger.error(f'Proje güncelleme hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        db.session.rollback()
        flash(f'Proje güncellenirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('main.strategy_projects'))


@main_bp.route('/strategy/project/<int:id>/delete', methods=['POST'])
@login_required
@role_required(['admin', 'kurum_yoneticisi', 'ust_yonetim'])
def strategy_project_delete(id):
    """Projeyi sil"""
    try:
        # Projeyi çek ve yetki kontrolü yap
        project = Project.query.filter_by(id=id, kurum_id=current_user.kurum_id).first_or_404()
        
        project_name = project.name
        
        # İlişkili süreçleri temizle
        project.related_processes.clear()
        
        # Projeyi sil
        db.session.delete(project)
        db.session.commit()
        
        flash(f'"{project_name}" projesi başarıyla silindi.', 'success')
        return redirect(url_for('main.strategy_projects'))
        
    except Exception as e:
        import traceback
        current_app.logger.error(f'Proje silme hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        db.session.rollback()
        flash(f'Proje silinirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('main.strategy_projects'))


@main_bp.route('/strategy/project/<int:id>/clone', methods=['POST'])
@login_required
@role_required(['admin', 'kurum_yoneticisi', 'ust_yonetim'])
def strategy_project_clone(id):
    """Projeyi klonla (kopyala)"""
    try:
        # Kaynak projeyi çek ve yetki kontrolü yap
        source_project = Project.query.filter_by(id=id, kurum_id=current_user.kurum_id).first_or_404()
        
        # Form verilerini al
        new_name = request.form.get('name', '').strip()
        copy_processes = request.form.get('copy_processes') == '1'
        copy_description = request.form.get('copy_description') == '1'
        copy_priority = request.form.get('copy_priority') == '1'
        
        # Validasyon
        if not new_name:
            flash('Yeni proje adı zorunludur.', 'error')
            return redirect(url_for('main.strategy_projects'))
        
        # Yeni proje oluştur
        new_project = Project(
            name=new_name,
            description=source_project.description if copy_description else None,
            priority=source_project.priority if copy_priority else 'Orta',
            kurum_id=current_user.kurum_id,
            manager_id=current_user.id,
            start_date=date.today(),  # Bugünün tarihi
            end_date=None  # Bitiş tarihi boş bırakılabilir veya hesaplanabilir
        )
        
        # Eğer kaynak projenin bitiş tarihi varsa, süreyi hesapla ve yeni bitiş tarihini ayarla
        if source_project.start_date and source_project.end_date:
            duration = (source_project.end_date - source_project.start_date).days
            new_project.end_date = date.today() + timedelta(days=duration)
        
        db.session.add(new_project)
        db.session.flush()  # ID'yi almak için
        
        # Süreç ilişkilerini kopyala
        if copy_processes:
            for process in source_project.related_processes:
                new_project.related_processes.append(process)
        
        db.session.commit()
        
        flash(f'Proje başarıyla kopyalandı: "{new_name}"', 'success')
        return redirect(url_for('main.strategy_projects'))
        
    except Exception as e:
        import traceback
        current_app.logger.error(f'Proje klonlama hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        db.session.rollback()
        flash(f'Proje kopyalanırken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('main.strategy_projects'))


@main_bp.route('/strategy/kpis')
@login_required
def strategy_kpis():
    """KPI Yönetim Paneli - Performans Göstergeleri Listesi"""
    try:
        # Tüm KPI'ları çek
        kpis = SurecPerformansGostergesi.query.join(Surec).filter(
            Surec.kurum_id == current_user.kurum_id
        ).order_by(Surec.code, SurecPerformansGostergesi.ad).all()
        
        # Süreçleri de çek (modal için)
        processes = Process.query.filter_by(kurum_id=current_user.kurum_id).order_by(Process.code).all()
        
        # Her KPI için başarı oranı hesapla
        kpis_with_scores = []
        total_kpis = 0
        achieved_count = 0
        critical_count = 0
        
        for kpi in kpis:
            total_kpis += 1
            
            # Hedef ve gerçekleşen değerleri parse et
            target_value = None
            actual_value = None
            
            if kpi.hedef_deger:
                try:
                    target_value = float(kpi.hedef_deger)
                except (ValueError, TypeError):
                    pass
            
            # Gerçekleşen değer için PerformansGostergeVeri tablosundan en son değeri al
            # Not: SurecPerformansGostergesi süreç bazlı, BireyselPerformansGostergesi bireysel
            # Şimdilik basit yaklaşım: hedef_deger'ı kullan, gerçek veri girişi için ayrı bir mekanizma gerekebilir
            # İleride SurecPerformansGostergesi için özel bir veri tablosu oluşturulabilir
            
            # Başarı oranı hesapla
            success_rate = None
            if target_value and target_value > 0:
                # Şimdilik gerçekleşen değer yoksa başarı oranı hesaplanamaz
                # İleride PerformansGostergeVeri veya yeni bir tablo üzerinden çekilebilir
                success_rate = None
            elif target_value == 0:
                success_rate = None  # Hedef sıfır ise hesaplama yapma
            
            # Kritik kontrolü (başarı oranı %70'in altındaysa kritik)
            is_critical = False
            if success_rate is not None and success_rate < 70:
                critical_count += 1
                is_critical = True
            elif success_rate is not None and success_rate >= 100:
                achieved_count += 1
            
            kpis_with_scores.append({
                'kpi': kpi,
                'target_value': target_value,
                'actual_value': actual_value,
                'success_rate': success_rate,
                'is_critical': is_critical
            })
        
        # Özet istatistikler
        summary_stats = {
            'total': total_kpis,
            'achieved': achieved_count,
            'critical': critical_count,
            'pending': total_kpis - achieved_count - critical_count if total_kpis > 0 else 0
        }
        
        return render_template('strategy/kpi_dashboard.html',
                             kpis_with_scores=kpis_with_scores,
                             summary_stats=summary_stats,
                             processes=processes)
    except Exception as e:
        import traceback
        current_app.logger.error(f'KPI Dashboard hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        flash(f'KPI paneli görüntülenirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/strategy/kpi/add', methods=['POST'])
@login_required
def strategy_kpi_add():
    """Yeni KPI ekle"""
    try:
        # Form verilerini al
        name = request.form.get('name', '').strip()
        process_id = request.form.get('process_id')
        unit = request.form.get('unit', '').strip()
        target_value_str = request.form.get('target_value', '').strip()
        direction = request.form.get('direction', 'Artan')
        description = request.form.get('description', '').strip()
        
        # Validasyon
        if not name:
            flash('Gösterge adı zorunludur.', 'error')
            return redirect(url_for('main.strategy_kpis'))
        
        if not process_id:
            flash('Süreç seçimi zorunludur.', 'error')
            return redirect(url_for('main.strategy_kpis'))
        
        # Sürecin kullanıcının kurumuna ait olduğunu kontrol et
        process = Process.query.filter_by(id=int(process_id), kurum_id=current_user.kurum_id).first()
        if not process:
            flash('Geçersiz süreç seçimi.', 'error')
            return redirect(url_for('main.strategy_kpis'))
        
        # Hedef değeri parse et (String olarak saklanacak)
        target_value_str_final = target_value_str if target_value_str else None
        
        # Direction'ı model formatına çevir
        direction_model = 'Increasing' if direction == 'Artan' else 'Decreasing'
        
        # Yeni KPI oluştur
        new_kpi = SurecPerformansGostergesi(
            ad=name,
            surec_id=int(process_id),
            birim=unit if unit else None,
            olcum_birimi=unit if unit else None,  # Eski alan
            unit=unit if unit else None,  # V3.0 alanı
            hedef_deger=target_value_str_final,
            direction=direction_model,  # V3.0 alanı (Increasing/Decreasing)
            aciklama=description if description else None
        )
        
        db.session.add(new_kpi)
        db.session.commit()
        
        flash('KPI başarıyla oluşturuldu.', 'success')
        return redirect(url_for('main.strategy_kpis'))
        
    except Exception as e:
        import traceback
        current_app.logger.error(f'KPI oluşturma hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        db.session.rollback()
        flash(f'KPI oluşturulurken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('main.strategy_kpis'))

