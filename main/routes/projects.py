# -*- coding: utf-8 -*-
# Otomatik bölüm — `python scripts/dev/split_main_routes.py`
from main.routes._common import *  # noqa: F401,F403
from main.routes import main_bp

# ============================================================================
# PROJE YÖNETİMİ ROTALARI
# ============================================================================

@main_bp.route('/projeler')
@login_required
def projeler():
    """Kök /kok/projeler → Micro proje listesi (/project)."""
    return redirect(url_for('app_bp.project_list', **request.args))


@main_bp.route('/projeler/yeni')
@login_required
def proje_yeni():
    """Yeni proje → Micro form (/project/new)."""
    return redirect(url_for('app_bp.project_new'))


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


@main_bp.route('/dokuman-merkezi')
@login_required
def dokuman_merkezi():
    """Kurumsal dosya yönetimi sayfası"""
    try:
        # Kategorilere göre dosyaları getir
        from sqlalchemy import or_, and_
        
        # Kurumsal dosyaları getir (scope='CORPORATE' veya project_id NULL)
        corporate_files = ProjectFile.query.filter(
            or_(
                ProjectFile.scope == 'CORPORATE',
                and_(ProjectFile.scope == 'PROJECT', ProjectFile.project_id.is_(None))
            ),
            ProjectFile.is_active == True
        ).order_by(ProjectFile.category, ProjectFile.file_name).all()
        
        # Kategorilere göre grupla
        files_by_category = {}
        for file in corporate_files:
            category = file.category or 'Diğer'
            if category not in files_by_category:
                files_by_category[category] = []
            files_by_category[category].append(file)
        
        # Kullanıcı yetkisi kontrolü (yönetici mi?)
        can_upload = current_user.sistem_rol in ['admin', 'kurum_yoneticisi']
        
        return render_template('corporate_files.html',
                             files_by_category=files_by_category,
                             can_upload=can_upload)
    except Exception as e:
        import traceback
        current_app.logger.error(f'Doküman merkezi sayfası hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        return f"Sayfa yüklenirken hata oluştu: {str(e)}", 500


@main_bp.route('/dashboard/executive')
@login_required
def executive_dashboard():
    """Yönetim Kokpiti - Executive Dashboard"""
    try:
        # Yetki kontrolü - Sadece yönetici ve gözlemci erişebilir
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim', 'gözlemci']:
            return "Bu sayfaya erişim yetkiniz yok", 403
        
        from services.strategic_impact_service import get_strategic_impact_summary

        strategic_impact = get_strategic_impact_summary(current_user.kurum_id)

        return render_template('executive_dashboard.html',
                             strategic_impact=strategic_impact)
    except Exception as e:
        import traceback
        current_app.logger.error(f'Executive dashboard sayfası hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        return f"Sayfa yüklenirken hata oluştu: {str(e)}", 500


@main_bp.route('/proje-analitik')
@login_required
def proje_analitik():
    """Proje Analitik sayfası - Süreç sağlık skoru ve analitik raporlar"""
    try:
        from services.project_analytics import calculate_surec_saglik_skoru
        from app.models.legacy_bridge import Surec
        
        # Kullanıcının erişebileceği süreçleri getir
        if current_user.sistem_rol == 'admin':
            surecler = Surec.query.all()
        elif current_user.sistem_rol == 'kurum_yoneticisi':
            surecler = Surec.query.all()
        else:
            # Kullanıcının üye/lider olduğu süreçler
            surecler = Surec.query.join(surec_liderleri).filter(
                surec_liderleri.c.user_id == current_user.id
            ).union(
                Surec.query.join(surec_uyeleri).filter(
                    surec_uyeleri.c.user_id == current_user.id
                )
            ).all()
        
        # Her süreç için sağlık skorunu hesapla
        surec_skorlari = []
        for surec in surecler:
            skor = calculate_surec_saglik_skoru(surec.id)
            if skor:
                surec_skorlari.append({
                    'surec': surec,
                    'skor': skor
                })
        
        # Skorlara göre sırala (yüksekten düşüğe)
        surec_skorlari.sort(key=lambda x: x['skor']['skor'], reverse=True)
        
        return render_template('proje_analitik.html',
                             surec_skorlari=surec_skorlari)
    except Exception as e:
        import traceback
        current_app.logger.error(f'Proje Analitik sayfası hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        flash('Analitik sayfası yüklenirken hata oluştu.', 'danger')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/zaman-takibi')
@login_required
def zaman_takibi():
    """Zaman Takibi (Timesheet) sayfası"""
    try:
        from datetime import datetime, timedelta
        
        # Varsayılan tarih aralığı: Bu hafta
        bugun = datetime.now().date()
        hafta_basi = bugun - timedelta(days=bugun.weekday())
        hafta_sonu = hafta_basi + timedelta(days=6)
        
        # Kullanıcının time entry'lerini getir
        entries = TimeEntry.query.filter_by(user_id=current_user.id).filter(
            TimeEntry.start_time >= datetime.combine(hafta_basi, datetime.min.time()),
            TimeEntry.start_time <= datetime.combine(hafta_sonu, datetime.max.time())
        ).order_by(TimeEntry.start_time.desc()).all()
        
        # Aktif time entry var mı?
        active_entry = TimeEntry.query.filter_by(
            user_id=current_user.id,
            end_time=None
        ).first()
        
        # Toplam süre hesapla
        toplam_dakika = sum(entry.duration_minutes or 0 for entry in entries if entry.duration_minutes)
        toplam_saat = toplam_dakika / 60.0
        
        return render_template('zaman_takibi.html',
                             entries=entries,
                             active_entry=active_entry,
                             toplam_saat=toplam_saat,
                             hafta_basi=hafta_basi,
                             hafta_sonu=hafta_sonu)
    except Exception as e:
        import traceback
        current_app.logger.error(f'Zaman Takibi sayfası hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        flash('Zaman takibi sayfası yüklenirken hata oluştu.', 'danger')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/gorev-aktivite-log')
@login_required
def gorev_aktivite_log():
    """Görev Aktivite Log sayfası - Görev değişiklik geçmişi"""
    try:
        # Kullanıcının erişebileceği projeler
        if current_user.sistem_rol == 'admin':
            projects = Project.query.all()
        else:
            projects = Project.query.filter_by(kurum_id=current_user.kurum_id).all()
        
        project_ids = [p.id for p in projects]
        
        # Bu projelerdeki görevlerin aktivitelerini getir
        task_ids = [t.id for t in Task.query.filter(Task.project_id.in_(project_ids)).all()]
        
        activities = TaskActivity.query.filter(
            TaskActivity.task_id.in_(task_ids)
        ).order_by(TaskActivity.created_at.desc()).limit(100).all()
        
        return render_template('gorev_aktivite_log.html',
                             activities=activities)
    except Exception as e:
        import traceback
        current_app.logger.error(f'Görev Aktivite Log sayfası hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        flash('Aktivite log sayfası yüklenirken hata oluştu.', 'danger')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/sistem-degisiklik-gunlugu')
@login_required
def sistem_degisiklik_gunlugu():
    """Sistem Değişiklik Günlüğü - Audit Trail UI"""
    # Sadece yöneticiler erişebilir
    if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
        flash('Bu sayfaya erişim yetkiniz yok.', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Filtreleme parametreleri
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        islem_tipi = request.args.get('islem_tipi', '')
        user_id = request.args.get('user_id', 0, type=int)
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        # Base query
        query = PerformansGostergeVeriAudit.query
        
        # Filtreleme
        if islem_tipi:
            query = query.filter(PerformansGostergeVeriAudit.islem_tipi == islem_tipi)
        if user_id:
            query = query.filter(PerformansGostergeVeriAudit.islem_yapan_user_id == user_id)
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(PerformansGostergeVeriAudit.islem_tarihi >= start_dt)
            except:
                pass
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
                query = query.filter(PerformansGostergeVeriAudit.islem_tarihi <= end_dt)
            except:
                pass
        
        # Sıralama (en yeni önce)
        query = query.order_by(PerformansGostergeVeriAudit.islem_tarihi.desc())
        
        # Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        audit_logs = pagination.items
        
        # Kullanıcı listesi (filtre için)
        users = User.query.filter_by(kurum_id=current_user.kurum_id).order_by(User.first_name).all()
        
        # İşlem tipleri
        islem_tipleri = ['OLUSTUR', 'GUNCELLE', 'SIL']
        
        return render_template(
            'sistem_degisiklik_gunlugu.html',
            audit_logs=audit_logs,
            pagination=pagination,
            users=users,
            islem_tipleri=islem_tipleri,
            current_filters={
                'islem_tipi': islem_tipi,
                'user_id': user_id,
                'start_date': start_date,
                'end_date': end_date
            }
        )
    except Exception as e:
        current_app.logger.error(f'Audit log sayfası hatası: {e}', exc_info=True)
        flash('Sistem değişiklik günlüğü yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/akilli-planlama')
@login_required
def akilli_planlama():
    """Akıllı Planlama sayfası - Geciken görevler için otomatik tarih güncelleme"""
    try:
        from datetime import date
        
        # Kullanıcının erişebileceği projeler
        if current_user.sistem_rol == 'admin':
            projects = Project.query.all()
        else:
            projects = Project.query.filter_by(kurum_id=current_user.kurum_id).all()
        
        project_ids = [p.id for p in projects]
        
        # Geciken görevleri bul
        bugun = date.today()
        geciken_gorevler = Task.query.filter(
            Task.project_id.in_(project_ids),
            Task.status.notin_(COMPLETED_STATUSES),
            Task.due_date < bugun,
            Task.due_date.isnot(None)
        ).order_by(Task.due_date.asc()).all()
        
        return render_template('akilli_planlama.html',
                             geciken_gorevler=geciken_gorevler,
                             bugun=bugun)
    except Exception as e:
        import traceback
        current_app.logger.error(f'Akıllı Planlama sayfası hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        flash('Akıllı planlama sayfası yüklenirken hata oluştu.', 'danger')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/setup_test_pg_automation')
@login_required
def setup_test_pg_automation():
    """Test için PG otomasyonu hazırlama route'u (Geçici)"""
    try:
        # 1. İlk görevi bul
        task = Task.query.first()
        
        if not task:
            return "❌ Görev bulunamadı. Önce bir görev oluşturun."
        
        # 2. İlk bireysel PG'yi bul (veya oluştur)
        pg = BireyselPerformansGostergesi.query.filter_by(user_id=current_user.id).first()
        
        if not pg:
            # Demo PG oluştur
            pg = BireyselPerformansGostergesi(
                user_id=current_user.id,
                ad="Test Performans Göstergesi (Otomasyon)",
                aciklama="Otomasyon testi için oluşturuldu",
                hedef_deger="100",
                olcum_birimi="Adet",
                periyot="Aylik",
                kaynak="Bireysel"
            )
            db.session.add(pg)
            db.session.flush()
        
        # 3. Görevi ölçülebilir yap ve PG'ye bağla
        task.is_measurable = True
        task.planned_output_value = 100.0
        task.related_indicator_id = pg.id
        
        db.session.commit()
        
        return f"""
        ✅ Test görevi hazırlandı!<br><br>
        <strong>Görev ID:</strong> {task.id}<br>
        <strong>Görev Adı:</strong> {task.title}<br>
        <strong>PG ID:</strong> {pg.id}<br>
        <strong>PG Adı:</strong> {pg.ad}<br>
        <strong>Planlanan Değer:</strong> {task.planned_output_value}<br><br>
        <strong>Şimdi yapılacaklar:</strong><br>
        1. Proje detay sayfasına gidin<br>
        2. Bu görevi tamamlayın (Bitir butonuna tıklayın)<br>
        3. Otomatik olarak PG verisi oluşturulacak!<br><br>
        <a href="/projeler/{task.project_id}">Proje Detay Sayfasına Git</a>
        """
        
    except Exception as e:
        db.session.rollback()
        import traceback
        current_app.logger.error(f'Test setup hatası: {e}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        return f"❌ Hata: {str(e)}<br><br>Traceback:<br><pre>{traceback.format_exc()}</pre>"


@main_bp.route('/debug/schema_check')
@login_required
def debug_schema_check():
    """Veritabanı şema kontrolü - Task tablosu sütunlarını kontrol et"""
    try:
        from sqlalchemy import inspect
        
        # Task modelini inspect et
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('task')]
        
        # Kontrol edilecek sütunlar
        required_columns = ['is_measurable', 'planned_output_value', 'related_indicator_id']
        
        result = []
        result.append("=== VERITABANI SEMA KONTROLU ===\n\n")
        result.append(f"Task tablosu toplam {len(columns)} sütun içeriyor.\n\n")
        
        all_present = True
        for col_name in required_columns:
            if col_name in columns:
                result.append(f"✅ {col_name}: MEVCUT\n")
            else:
                result.append(f"❌ {col_name}: EKSIK\n")
                all_present = False
        
        result.append("\n=== SONUC ===\n")
        if all_present:
            result.append("✅ Tüm sütunlar mevcut! Otomasyon için hazır.\n")
        else:
            result.append("❌ Bazı sütunlar eksik. Migration gerekli.\n")
        
        result.append("\n=== TUM SUTUNLAR ===\n")
        result.append(", ".join(columns))
        
        return "<pre>" + "".join(result) + "</pre>"
        
    except Exception as e:
        import traceback
        return f"<pre>❌ Hata: {str(e)}\n\nTraceback:\n{traceback.format_exc()}</pre>"


@main_bp.route('/debug/monitor')
@login_required
def debug_monitor():
    """Canlı izleme paneli - Son görevler ve PG verileri"""
    try:
        # Son 5 görev
        last_tasks = Task.query.order_by(Task.created_at.desc()).limit(5).all()
        
        # Son 5 PG verisi (otomasyonla oluşanlar)
        last_pg_veriler = PerformansGostergeVeri.query.order_by(PerformansGostergeVeri.created_at.desc()).limit(5).all()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Debug Monitor - Sistem İzleme</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                h1 { color: #333; }
                table { width: 100%; border-collapse: collapse; background: white; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #4CAF50; color: white; }
                tr:hover { background-color: #f5f5f5; }
                .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; }
                .badge-success { background: #28a745; color: white; }
                .badge-danger { background: #dc3545; color: white; }
                .badge-warning { background: #ffc107; color: black; }
                .badge-info { background: #17a2b8; color: white; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔍 Sistem Tanı ve İzleme Paneli</h1>
                <p><strong>Son Güncelleme:</strong> """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
                
                <h2>📋 Son 5 Görev</h2>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Adı</th>
                            <th>Durum</th>
                            <th>Ölçülebilir?</th>
                            <th>Planlanan Değer</th>
                            <th>Bağlı PG ID</th>
                            <th>Tamamlanma Tarihi</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for task in last_tasks:
            is_measurable_badge = '<span class="badge badge-success">Evet</span>' if task.is_measurable else '<span class="badge badge-danger">Hayır</span>'
            status_badge = f'<span class="badge badge-{"success" if task.status == "Tamamlandı" else "warning"}">{task.status}</span>'
            pg_id = task.related_indicator_id if task.related_indicator_id else '-'
            planned_value = task.planned_output_value if task.planned_output_value is not None else '-'
            completed = task.completed_at.strftime('%Y-%m-%d %H:%M') if task.completed_at else '-'
            
            html += f"""
                        <tr>
                            <td>{task.id}</td>
                            <td>{task.title}</td>
                            <td>{status_badge}</td>
                            <td>{is_measurable_badge}</td>
                            <td>{planned_value}</td>
                            <td>{pg_id}</td>
                            <td>{completed}</td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
                
                <h2>📊 Son 5 PG Verisi</h2>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Tarih</th>
                            <th>Değer</th>
                            <th>Açıklama</th>
                            <th>PG ID</th>
                            <th>Kullanıcı</th>
                            <th>Oluşturulma</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for pg_veri in last_pg_veriler:
            is_auto = 'Otomatik' in (pg_veri.aciklama or '')
            auto_badge = '<span class="badge badge-info">Otomatik</span>' if is_auto else '<span class="badge">Manuel</span>'
            user_name = pg_veri.user.first_name + ' ' + pg_veri.user.last_name if pg_veri.user else '-'
            created = pg_veri.created_at.strftime('%Y-%m-%d %H:%M') if pg_veri.created_at else '-'
            
            html += f"""
                        <tr>
                            <td>{pg_veri.id}</td>
                            <td>{pg_veri.veri_tarihi.strftime('%Y-%m-%d') if pg_veri.veri_tarihi else '-'}</td>
                            <td>{pg_veri.gerceklesen_deger}</td>
                            <td>{auto_badge} {pg_veri.aciklama[:50] if pg_veri.aciklama else '-'}</td>
                            <td>{pg_veri.bireysel_pg_id}</td>
                            <td>{user_name}</td>
                            <td>{created}</td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
                
                <p><a href="/debug/schema_check">🔍 Şema Kontrolü</a> | 
                   <a href="/dashboard">🏠 Dashboard</a></p>
            </div>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        import traceback
        return f"<pre>❌ Hata: {str(e)}\n\nTraceback:\n{traceback.format_exc()}</pre>"


@main_bp.route('/debug/force_trigger/<int:task_id>')
@login_required
def debug_force_trigger(task_id):
    """Manuel otomasyon tetikleme testi"""
    try:
        from datetime import date
        
        # Görevi bul
        task = Task.query.get_or_404(task_id)
        
        # Görevi ölçülebilir yap ve değerleri set et
        task.is_measurable = True
        task.planned_output_value = 50.0
        
        # PG ID'yi kontrol et - eğer yoksa ilk PG'yi bul veya oluştur
        if not task.related_indicator_id:
            pg = BireyselPerformansGostergesi.query.filter_by(user_id=current_user.id).first()
            if not pg:
                # Demo PG oluştur
                pg = BireyselPerformansGostergesi(
                    user_id=current_user.id,
                    ad="Test Performans Göstergesi (Manuel Tetikleme)",
                    aciklama="Manuel tetikleme testi için oluşturuldu",
                    hedef_deger="100",
                    olcum_birimi="Adet",
                    periyot="Aylik",
                    kaynak="Bireysel"
                )
                db.session.add(pg)
                db.session.flush()
            task.related_indicator_id = pg.id
        
        db.session.flush()
        
        # Otomasyon mantığını manuel çalıştır
        result = {
            'success': False,
            'task_id': task_id,
            'task_title': task.title,
            'is_measurable': task.is_measurable,
            'planned_output_value': task.planned_output_value,
            'related_indicator_id': task.related_indicator_id,
            'pg_created': False,
            'pg_veri_id': None,
            'error': None
        }
        
        if task.is_measurable and task.related_indicator_id:
            try:
                # İlişkili PG'yi kontrol et
                related_pg = BireyselPerformansGostergesi.query.get(task.related_indicator_id)
                if related_pg:
                    # Yeni performans değeri kaydı oluştur
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
                        aciklama=f"Otomatik: {task.title} tamamlandı. (Manuel Tetikleme)",
                        user_id=current_user.id,
                        created_by=current_user.id,
                        updated_by=current_user.id
                    )
                    db.session.add(new_pg_veri)
                    db.session.flush()
                    
                    result['pg_created'] = True
                    result['pg_veri_id'] = new_pg_veri.id
                    result['success'] = True
                    result['message'] = f'PG verisi başarıyla oluşturuldu (ID: {new_pg_veri.id})'
                else:
                    result['error'] = f'İlişkili PG bulunamadı (ID: {task.related_indicator_id})'
            except Exception as pg_error:
                result['error'] = f'PG verisi oluşturulurken hata: {str(pg_error)}'
        else:
            result['error'] = 'Görev ölçülebilir değil veya PG ID yok'
        
        db.session.commit()
        
        return jsonify(result)
        
    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@main_bp.route('/debug/fix_and_reset')
@login_required
def debug_fix_and_reset():
    """Test ortamını sıfırla ve eksik referansları tamamla"""
    try:
        result_messages = []
        
        # Adım 1: İndikatör Kontrolü (BireyselPerformansGostergesi ID=1)
        pg = BireyselPerformansGostergesi.query.get(1)
        if not pg:
            # ID=1 olan PG yoksa oluştur
            # Önce mevcut kullanıcının PG'sini kontrol et
            existing_pg = BireyselPerformansGostergesi.query.filter_by(
                user_id=current_user.id,
                ad="Test KPI"
            ).first()
            
            if existing_pg:
                # Mevcut PG'yi kullan
                pg = existing_pg
                result_messages.append(f"ℹ️ Mevcut Test KPI kullanılıyor (ID: {pg.id})")
            else:
                # Yeni PG oluştur
                pg = BireyselPerformansGostergesi(
                    user_id=current_user.id,
                    ad="Test KPI",
                    aciklama="Test ortamı için otomatik oluşturuldu",
                    hedef_deger="100",
                    olcum_birimi="Adet",
                    periyot="Aylik",
                    kaynak="Bireysel",
                    durum="Devam Ediyor"
                )
                db.session.add(pg)
                db.session.flush()
                result_messages.append(f"✅ İndikatör oluşturuldu (ID: {pg.id}): 'Test KPI'")
        else:
            result_messages.append(f"ℹ️ İndikatör (ID:1) zaten mevcut: '{pg.ad}'")
        
        # Adım 2: Görevi Sıfırla (Task ID=1)
        task = Task.query.get(1)
        if not task:
            # Görev 1 yoksa, ilk görevi bul veya oluştur
            task = Task.query.first()
            if not task:
                # Hiç görev yoksa, bir proje bul ve görev oluştur
                project = Project.query.first()
                if project:
                    task = Task(
                        project_id=project.id,
                        title="Test Görevi (Otomasyon Testi)",
                        description="Otomasyon testi için oluşturuldu",
                        status="Yapılacak",
                        priority="Orta"
                    )
                    db.session.add(task)
                    db.session.flush()
                    result_messages.append("✅ Yeni test görevi oluşturuldu (ID: {})".format(task.id))
                else:
                    return "<pre>❌ Hata: Hiç proje bulunamadı. Önce bir proje oluşturun.</pre>"
            else:
                result_messages.append(f"ℹ️ Görev 1 bulunamadı, ilk görev kullanılıyor (ID: {task.id})")
        
        # Görevi sıfırla
        task.status = 'Yapılacak'
        task.completed_at = None
        task.is_measurable = True
        task.planned_output_value = 50.0
        task.related_indicator_id = pg.id  # ID=1 olan PG'ye bağla
        
        result_messages.append(f"✅ Görev (ID: {task.id}) sıfırlandı:")
        result_messages.append(f"   - Durum: 'Yapılacak'")
        result_messages.append(f"   - Tamamlanma Tarihi: None")
        result_messages.append(f"   - Ölçülebilir: True")
        result_messages.append(f"   - Planlanan Değer: 50.0")
        result_messages.append(f"   - Bağlı PG ID: {pg.id}")
        
        # Adım 3: Kaydet
        db.session.commit()
        
        result_messages.append("\n✅ Sistem sıfırlandı ve hazır!")
        result_messages.append(f"\n📝 Şimdi yapılacaklar:")
        result_messages.append(f"   1. Proje detay sayfasına gidin: /projeler/{task.project_id}")
        result_messages.append(f"   2. Görev (ID: {task.id}) 'Bitir' butonuna tıklayın")
        result_messages.append(f"   3. Otomatik olarak PG verisi oluşturulacak!")
        
        return "<pre>" + "\n".join(result_messages) + "</pre>"
        
    except Exception as e:
        db.session.rollback()
        import traceback
        return f"<pre>❌ Hata: {str(e)}\n\nTraceback:\n{traceback.format_exc()}</pre>"


@main_bp.route('/debug/init_strategy_db')
@login_required
def debug_init_strategy_db():
    """Stratejik Planlama V3.0 veritabanı migration - Yeni tabloları ve ilişkileri oluşturur"""
    try:
        from app.models.legacy_bridge import CorporateIdentity, AnaStrateji, AltStrateji, Surec, SurecPerformansGostergesi
        
        result_messages = []
        result_messages.append("=== STRATEJİK PLANLAMA V3.0 VERİTABANI MİGRATİON ===\n")
        
        # Tüm tabloları oluştur
        db.create_all()
        result_messages.append("✅ Tüm tablolar oluşturuldu (veya zaten mevcut)")
        
        # Yeni tabloları kontrol et
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        # CorporateIdentity tablosu kontrolü
        if 'corporate_identity' in existing_tables:
            result_messages.append("✅ corporate_identity tablosu mevcut")
        else:
            result_messages.append("⚠️ corporate_identity tablosu bulunamadı (create_all çalıştırıldı)")
        
        # Association table'ları kontrol et
        if 'process_owners' in existing_tables:
            result_messages.append("✅ process_owners association table mevcut")
        else:
            result_messages.append("⚠️ process_owners association table bulunamadı")
        
        if 'strategy_process_matrix' in existing_tables:
            result_messages.append("✅ strategy_process_matrix association table mevcut")
        else:
            result_messages.append("⚠️ strategy_process_matrix association table bulunamadı")
        
        # Mevcut tablolardaki yeni kolonları kontrol et (PostgreSQL: Alembic önerilir)
        result_messages.append("\n=== YENİ KOLONLAR KONTROLÜ ===")
        result_messages.append("⚠️ Not: PostgreSQL'de şema değişiklikleri için Alembic migration kullanın.")
        result_messages.append("Aşağıdaki kolonlar eklenmeli:")
        result_messages.append("  - ana_strateji: code, name")
        result_messages.append("  - alt_strateji: code, name")
        result_messages.append("  - surec: code, name, weight")
        result_messages.append("  - surec_performans_gostergesi: calculation_method, target_method, unit, direction")
        
        result_messages.append("\n✅ Migration tamamlandı!")
        result_messages.append("\n📝 Sonraki Adımlar:")
        result_messages.append("  1. Eksik kolonlar için Alembic revision oluşturup flask db upgrade çalıştırın")
        result_messages.append("  2. Veya uygun SQL migration scriptini uygulayın")
        
        return "<pre>" + "\n".join(result_messages) + "</pre>"
        
    except Exception as e:
        db.session.rollback()
        import traceback
        return f"<pre>❌ Hata: {str(e)}\n\nTraceback:\n{traceback.format_exc()}</pre>"


@main_bp.route('/debug/init_strategy_v3')
@login_required
def debug_init_strategy_v3():
    """Stratejik Planlama V3.0 veritabanı initialization - Excel yapısına göre tabloları oluşturur"""
    try:
        from app.models.legacy_bridge import (
            CorporateIdentity, AnaStrateji, AltStrateji, Surec,
            SurecPerformansGostergesi,
        )
        
        result_messages = []
        result_messages.append("=== STRATEJİK PLANLAMA V3.0 VERİTABANI INITIALIZATION ===\n")
        result_messages.append("Excel: SP VE SÜREÇ YAPISI dosyasına göre yapılandırılıyor...\n")
        
        # Tüm tabloları oluştur
        db.create_all()
        result_messages.append("✅ Tüm tablolar oluşturuldu (veya zaten mevcut)")
        
        # Yeni tabloları kontrol et
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        # CorporateIdentity tablosu kontrolü
        if 'corporate_identity' in existing_tables:
            result_messages.append("✅ corporate_identity tablosu mevcut (Excel: Misyon, Vizyon, Değerler)")
        else:
            result_messages.append("⚠️ corporate_identity tablosu bulunamadı (create_all çalıştırıldı)")
        
        # Association table'ları kontrol et
        if 'process_owners' in existing_tables:
            result_messages.append("✅ process_owners association table mevcut (Çoklu Süreç Sahipliği)")
        else:
            result_messages.append("⚠️ process_owners association table bulunamadı")
        
        if 'strategy_process_matrix' in existing_tables:
            result_messages.append("✅ strategy_process_matrix association table mevcut (Excel: SP - Süreç Matrisi)")
        else:
            result_messages.append("⚠️ strategy_process_matrix association table bulunamadı")
        
        # Mevcut tablolardaki yeni kolonları kontrol et
        result_messages.append("\n=== YENİ KOLONLAR KONTROLÜ ===")
        result_messages.append("⚠️ Not: PostgreSQL'de şema değişiklikleri için Alembic migration kullanın.")
        result_messages.append("Aşağıdaki kolonlar eklenmeli:")
        result_messages.append("  - corporate_identity: YENİ TABLO (vizyon, misyon, kalite_politikasi, degerler)")
        result_messages.append("  - ana_strateji: code (UNIQUE), name")
        result_messages.append("  - alt_strateji: code, name, target_method")
        result_messages.append("  - surec: code, name, weight")
        result_messages.append("  - surec_performans_gostergesi: calculation_method, target_method, unit, direction")
        result_messages.append("  - strategy_process_matrix: relationship_score (A=9, B=3)")
        
        result_messages.append("\n=== EXCEL YAPISI EŞLEŞTİRMESİ ===")
        result_messages.append("✅ CorporateIdentity ↔ Excel: 'Misyon, Vizyon, Değerler' sayfası")
        result_messages.append("✅ AnaStrateji ↔ Excel: 'ST1, ST2' yapıları")
        result_messages.append("✅ AltStrateji ↔ Excel: 'ST1.1' yapıları (target_method ile)")
        result_messages.append("✅ Surec ↔ Excel: 'KMF Süreçler' sayfası (code, name, weight)")
        result_messages.append("✅ StrategyProcessMatrix ↔ Excel: 'SP - Süreç Matrisi' (A=9, B=3)")
        result_messages.append("✅ SurecPerformansGostergesi ↔ Excel: KPI yapısı (calculation_method, target_method)")
        
        result_messages.append("\n✅ V3.0 Mimari Kurulumu Tamamlandı!")
        result_messages.append("\n📝 Sonraki Adımlar:")
        result_messages.append("  1. Eksik kolonlar için Alembic / SQL migration uygulayın")
        result_messages.append("  2. Excel verilerini import edin")
        result_messages.append("  3. CRUD endpoint'lerini kullanarak veri girişi yapın")
        
        return "<pre>" + "\n".join(result_messages) + "</pre>"
        
    except Exception as e:
        db.session.rollback()
        import traceback
        return f"<pre>❌ Hata: {str(e)}\n\nTraceback:\n{traceback.format_exc()}</pre>"


# ============================================
# FAZ 2: OPERASYONEL MÜKEMMELLİK ROUTE'LARI
# ============================================

# V59.0 - Hoshin Kanri Paketi
@main_bp.route('/okr/<int:objective_id>/comment', methods=['POST'])
@login_required
def okr_comment(objective_id):
    """OKR/Hedef yorum ekleme - Hoshin Catchball"""
    try:
        data = request.get_json() if request.is_json else request.form
        comment_text = data.get('comment_text', '').strip()
        comment_type = data.get('comment_type', 'feedback')
        
        if not comment_text:
            return jsonify({'success': False, 'message': 'Yorum metni boş olamaz'}), 400
        
        # AltStrateji kontrolü
        objective = AltStrateji.query.filter_by(id=objective_id).first_or_404()
        
        # Yetki kontrolü - kullanıcı aynı kurumda olmalı
        if objective.ana_strateji.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Yetkisiz erişim'}), 403
        
        comment = ObjectiveComment(
            objective_id=objective_id,
            user_id=current_user.id,
            comment_text=comment_text,
            comment_type=comment_type,
            status='active'
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Yorum eklendi',
            'comment': {
                'id': comment.id,
                'comment_text': comment.comment_text,
                'comment_type': comment.comment_type,
                'user_name': current_user.first_name or current_user.username,
                'created_at': comment.created_at.isoformat()
            }
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'OKR comment hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@main_bp.route('/mtbp')
@login_required
def mtbp():
    """Mid-Term Business Plan (MTBP) sayfası"""
    try:
        kurum = current_user.kurum
        plans = StrategicPlan.query.filter_by(
            kurum_id=kurum.id
        ).order_by(StrategicPlan.start_date.desc()).all()
        
        return render_template('mtbp.html', plans=plans, kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'MTBP sayfası hatası: {e}')
        flash('MTBP sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/mtbp/add', methods=['POST'])
@login_required
@csrf.exempt
def mtbp_add():
    """Yeni MTBP planı ekleme"""
    try:
        data = request.get_json() if request.is_json else request.form
        
        plan = StrategicPlan(
            kurum_id=current_user.kurum_id,
            plan_name=data.get('plan_name', '').strip(),
            plan_type='mtbp',
            start_date=datetime.strptime(data.get('start_date'), '%Y-%m-%d').date(),
            end_date=datetime.strptime(data.get('end_date'), '%Y-%m-%d').date(),
            description=data.get('description', ''),
            status='draft',
            created_by=current_user.id
        )
        
        db.session.add(plan)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Plan oluşturuldu', 'plan_id': plan.id})
        else:
            flash('Plan başarıyla oluşturuldu.', 'success')
            return redirect(url_for('main.mtbp'))
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'MTBP ekleme hatası: {e}')
        if request.is_json:
            return jsonify({'success': False, 'message': str(e)}), 500
        else:
            flash('Plan oluşturulurken bir hata oluştu.', 'error')
            return redirect(url_for('main.mtbp'))


@main_bp.route('/gemba')
@login_required
def gemba():
    """Gemba Walk sayfası - Dijital Gemba"""
    try:
        kurum = current_user.kurum
        walks = GembaWalk.query.filter_by(
            kurum_id=kurum.id
        ).order_by(GembaWalk.walk_date.desc()).limit(50).all()
        
        surecler = Surec.query.filter_by(kurum_id=kurum.id).all()
        
        return render_template('gemba.html', walks=walks, surecler=surecler, kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'Gemba sayfası hatası: {e}')
        flash('Gemba Walk sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/gemba/add', methods=['POST'])
@login_required
@csrf.exempt
def gemba_add():
    """Yeni Gemba Walk kaydı ekleme"""
    try:
        data = request.get_json() if request.is_json else request.form
        
        walk = GembaWalk(
            kurum_id=current_user.kurum_id,
            surec_id=int(data.get('surec_id')) if data.get('surec_id') else None,
            conducted_by=current_user.id,
            walk_date=datetime.strptime(data.get('walk_date', datetime.utcnow().strftime('%Y-%m-%d')), '%Y-%m-%d').date(),
            location=data.get('location', ''),
            observations=data.get('observations', '').strip(),
            findings=data.get('findings', ''),
            improvements=data.get('improvements', ''),
            status='completed'
        )
        
        db.session.add(walk)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Gemba Walk kaydı eklendi', 'walk_id': walk.id})
        else:
            flash('Gemba Walk kaydı başarıyla eklendi.', 'success')
            return redirect(url_for('main.gemba'))
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Gemba ekleme hatası: {e}')
        if request.is_json:
            return jsonify({'success': False, 'message': str(e)}), 500
        else:
            flash('Gemba Walk kaydı eklenirken bir hata oluştu.', 'error')
            return redirect(url_for('main.gemba'))


# V60.0 - Talent & Risk Paketi
@main_bp.route('/competencies')
@login_required
def competencies():
    """Yetkinlik Matrisi sayfası"""
    try:
        kurum = current_user.kurum
        competencies_list = Competency.query.filter_by(kurum_id=kurum.id).all()
        
        # Kullanıcı yetkinliklerini getir
        user_competencies = UserCompetency.query.filter_by(user_id=current_user.id).all()
        user_competency_map = {uc.competency_id: uc.level for uc in user_competencies}
        
        # Tüm kullanıcıların yetkinlikleri (heatmap için)
        all_user_competencies = UserCompetency.query.join(User).filter(
            User.kurum_id == kurum.id
        ).all()
        
        return render_template('competencies.html', 
                             competencies=competencies_list,
                             user_competency_map=user_competency_map,
                             all_user_competencies=all_user_competencies,
                             kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'Competencies sayfası hatası: {e}')
        flash('Yetkinlik Matrisi sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/risks')
@login_required
def risks():
    """Stratejik Risk Yönetimi sayfası"""
    try:
        kurum = current_user.kurum
        risks_list = StrategicRisk.query.filter_by(kurum_id=kurum.id).order_by(
            StrategicRisk.risk_score.desc()
        ).all()
        
        # Risk seviyelerine göre grupla
        risk_levels = {
            'Kritik': [r for r in risks_list if r.risk_level == 'Kritik'],
            'Yüksek': [r for r in risks_list if r.risk_level == 'Yüksek'],
            'Orta': [r for r in risks_list if r.risk_level == 'Orta'],
            'Düşük': [r for r in risks_list if r.risk_level == 'Düşük']
        }
        
        return render_template('risks.html', risks=risks_list, risk_levels=risk_levels, kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'Risks sayfası hatası: {e}')
        flash('Risk Yönetimi sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/risks/add', methods=['POST'])
@login_required
def risks_add():
    """Yeni risk ekle"""
    try:
        kurum = current_user.kurum
        probability = int(request.form.get('probability', 3))
        impact = int(request.form.get('impact', 3))
        risk_score = probability * impact
        
        # Risk seviyesini belirle
        if risk_score >= 21:
            risk_level = 'Kritik'
        elif risk_score >= 13:
            risk_level = 'Yüksek'
        elif risk_score >= 7:
            risk_level = 'Orta'
        else:
            risk_level = 'Düşük'
        
        risk = StrategicRisk(
            kurum_id=kurum.id,
            risk_name=request.form.get('risk_name'),
            risk_category=request.form.get('risk_category', 'strategic'),
            description=request.form.get('description'),
            probability=probability,
            impact=impact,
            risk_score=risk_score,
            risk_level=risk_level,
            mitigation_strategy=request.form.get('mitigation_strategy'),
            created_by=current_user.id
        )
        db.session.add(risk)
        db.session.commit()
        flash('Risk başarıyla eklendi.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Risk ekleme hatası: {e}')
        flash('Risk eklenirken bir hata oluştu.', 'error')
    return redirect(url_for('main.risks'))


@main_bp.route('/executive-report')
@login_required
def executive_report():
    """Yönetim Kurulu Özeti sayfası"""
    try:
        kurum = current_user.kurum
        
        # Üst yönetim rolü kontrolü
        if current_user.sistem_rol not in ['admin', 'ust_yonetim', 'kurum_yoneticisi']:
            flash('Bu sayfaya erişim yetkiniz bulunmamaktadır.', 'error')
            return redirect(url_for('main.dashboard'))
        
        # Özet verileri topla
        stats = {
            'total_processes': Surec.query.filter_by(kurum_id=kurum.id).count(),
            'active_risks': StrategicRisk.query.filter_by(kurum_id=kurum.id, status='open').count(),
            'critical_risks': StrategicRisk.query.filter_by(kurum_id=kurum.id).filter(
                StrategicRisk.risk_score >= 20
            ).count(),
            'total_users': User.query.filter_by(kurum_id=kurum.id).count()
        }
        
        # Son eklenen riskler
        recent_risks = StrategicRisk.query.filter_by(kurum_id=kurum.id).order_by(
            StrategicRisk.created_at.desc()
        ).limit(10).all()
        
        return render_template('executive_report.html', stats=stats, recent_risks=recent_risks, kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'Executive report hatası: {e}')
        flash('Yönetim Kurulu Özeti sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


# V65.0 - Muda Hunter
@main_bp.route('/muda-hunter')
@login_required
def muda_hunter():
    """Muda Hunter sayfası - Süreç Verimsizlik Analizi"""
    try:
        kurum = current_user.kurum
        surecler = Surec.query.filter_by(kurum_id=kurum.id).all()
        
        # Mevcut muda bulguları
        findings = MudaFinding.query.filter_by(kurum_id=kurum.id).order_by(
            MudaFinding.created_at.desc()
        ).all()
        
        # Verimlilik skoru
        from services.muda_analyzer import MudaAnalyzerService
        efficiency_score = MudaAnalyzerService.get_efficiency_score(kurum.id)
        
        return render_template('muda_hunter.html', 
                             surecler=surecler,
                             findings=findings,
                             efficiency_score=efficiency_score,
                             kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'Muda Hunter sayfası hatası: {e}')
        flash('Muda Hunter sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/api/muda-hunter/analyze/<int:surec_id>', methods=['POST'])
@login_required
def muda_analyze(surec_id):
    """Süreç verimsizlik analizi API"""
    try:
        surec = Surec.query.filter_by(id=surec_id, kurum_id=current_user.kurum_id).first_or_404()
        
        from services.muda_analyzer import MudaAnalyzerService
        findings = MudaAnalyzerService.analyze_process_inefficiency(surec_id, current_user.kurum_id)
        
        return jsonify({
            'success': True,
            'findings': findings,
            'surec_name': surec.surec_adi
        })
    
    except Exception as e:
        current_app.logger.error(f'Muda analiz hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@main_bp.route('/api/muda-hunter/efficiency-score', methods=['GET'])
@login_required
def muda_efficiency_score():
    """Genel verimlilik skoru API"""
    try:
        from services.muda_analyzer import MudaAnalyzerService
        efficiency_score = MudaAnalyzerService.get_efficiency_score(current_user.kurum_id)
        
        return jsonify({
            'success': True,
            'efficiency_score': efficiency_score
        })
    
    except Exception as e:
        current_app.logger.error(f'Efficiency score hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================
# FAZ 3: İLERİ SEVİYE MODÜLLER ROUTE'LARI
# ============================================

# V61.0 - Titan & Zenith Paketi
@main_bp.route('/crisis')
@login_required
def crisis():
    """Kriz Komuta Merkezi sayfası"""
    try:
        kurum = current_user.kurum
        crises = CrisisMode.query.filter_by(kurum_id=kurum.id).order_by(
            CrisisMode.activated_at.desc()
        ).all()
        
        return render_template('crisis.html', crises=crises, kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'Crisis sayfası hatası: {e}')
        flash('Kriz Komuta Merkezi sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/crisis/add', methods=['POST'])
@login_required
def crisis_add():
    """Yeni kriz ekle"""
    try:
        kurum = current_user.kurum
        crisis = CrisisMode(
            kurum_id=kurum.id,
            crisis_name=request.form.get('crisis_name'),
            crisis_type=request.form.get('crisis_type', 'other'),
            description=request.form.get('description'),
            severity='high',
            status='active',
            activated_at=datetime.utcnow(),
            activated_by=current_user.id
        )
        db.session.add(crisis)
        db.session.commit()
        flash('Kriz başarıyla bildirildi.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Kriz ekleme hatası: {e}')
        flash('Kriz eklenirken bir hata oluştu.', 'error')
    return redirect(url_for('main.crisis'))


@main_bp.route('/succession')
@login_required
def succession():
    """Halefiyet Planlaması sayfası"""
    try:
        kurum = current_user.kurum
        plans = SuccessionPlan.query.filter_by(kurum_id=kurum.id).order_by(
            SuccessionPlan.created_at.desc()
        ).all()
        
        return render_template('succession.html', plans=plans, kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'Succession sayfası hatası: {e}')
        flash('Halefiyet Planlaması sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/reorg')
@login_required
def reorg():
    """Dinamik Organizasyon Tasarımcısı sayfası"""
    try:
        kurum = current_user.kurum
        scenarios = OrgScenario.query.filter_by(kurum_id=kurum.id).order_by(
            OrgScenario.created_at.desc()
        ).all()
        
        return render_template('reorg.html', scenarios=scenarios, kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'Reorg sayfası hatası: {e}')
        flash('Organizasyon Tasarımcısı sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/ona')
@login_required
def ona():
    """ONA (Organizasyonel Ağ Analizi) sayfası"""
    try:
        kurum = current_user.kurum
        influence_scores = InfluenceScore.query.filter_by(kurum_id=kurum.id).order_by(
            InfluenceScore.score.desc()
        ).limit(50).all()
        
        return render_template('ona.html', influence_scores=influence_scores, kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'ONA sayfası hatası: {e}')
        flash('ONA sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/market-watch')
@login_required
def market_watch():
    """Market Watcher sayfası"""
    try:
        kurum = current_user.kurum
        intels = MarketIntel.query.filter_by(kurum_id=kurum.id).order_by(
            MarketIntel.collected_at.desc()
        ).limit(100).all()
        
        return render_template('market_watch.html', intels=intels, kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'Market Watch sayfası hatası: {e}')
        flash('Market Watcher sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


# V62.0 - Corporate Consciousness
@main_bp.route('/wellbeing')
@login_required
def wellbeing():
    """Tükenmişlik Kalkanı sayfası"""
    try:
        kurum = current_user.kurum
        scores = WellbeingScore.query.filter_by(
            kurum_id=kurum.id
        ).order_by(WellbeingScore.score_date.desc()).limit(100).all()
        
        user_scores = WellbeingScore.query.filter_by(
            user_id=current_user.id
        ).order_by(WellbeingScore.score_date.desc()).limit(30).all()
        
        return render_template('wellbeing.html', scores=scores, user_scores=user_scores, kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'Wellbeing sayfası hatası: {e}')
        flash('Tükenmişlik Kalkanı sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/simulation')
@login_required
def simulation():
    """Monte Carlo Simülatörü sayfası"""
    try:
        kurum = current_user.kurum
        scenarios = SimulationScenario.query.filter_by(kurum_id=kurum.id).order_by(
            SimulationScenario.created_at.desc()
        ).all()
        
        return render_template('simulation.html', scenarios=scenarios, kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'Simulation sayfası hatası: {e}')
        flash('Monte Carlo Simülatörü sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/simulation/add', methods=['POST'])
@login_required
def simulation_add():
    """Yeni simülasyon senaryosu ekle"""
    try:
        kurum = current_user.kurum
        scenario = SimulationScenario(
            kurum_id=kurum.id,
            scenario_name=request.form.get('scenario_name'),
            scenario_type=request.form.get('scenario_type', 'financial'),
            description=request.form.get('description'),
            variables=request.form.get('variables', '{}'),
            iterations=int(request.form.get('iterations', 10000)),
            status='draft',
            created_by=current_user.id
        )
        db.session.add(scenario)
        db.session.commit()
        flash('Simülasyon senaryosu başarıyla eklendi.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Simülasyon ekleme hatası: {e}')
        flash('Simülasyon eklenirken bir hata oluştu.', 'error')
    return redirect(url_for('main.simulation'))


@main_bp.route('/simulation/<int:scenario_id>/run', methods=['POST'])
@login_required
def simulation_run(scenario_id):
    """Simülasyon çalıştır"""
    try:
        scenario = SimulationScenario.query.get_or_404(scenario_id)
        if scenario.kurum_id != current_user.kurum_id:
            return jsonify({'error': 'Yetkisiz erişim'}), 403
        
        from services.monte_carlo_service import run_monte_carlo_simulation
        
        # Variables JSON formatında olmalı
        variables = json.loads(scenario.variables) if isinstance(scenario.variables, str) else scenario.variables
        
        result = run_monte_carlo_simulation(
            variables=variables,
            iterations=scenario.iterations,
            simulation_type=scenario.scenario_type
        )
        
        if result.get('success'):
            scenario.status = 'completed'
            scenario.results = json.dumps(result)
            db.session.commit()
            return jsonify({
                'success': True,
                'result': result
            })
        else:
            scenario.status = 'failed'
            db.session.commit()
            return jsonify({
                'success': False,
                'error': result.get('error', 'Bilinmeyen hata')
            }), 400
    except Exception as e:
        current_app.logger.error(f'Simülasyon çalıştırma hatası: {e}')
        return jsonify({'error': str(e)}), 500


@main_bp.route('/deep-work/toggle', methods=['POST'])
@login_required
@csrf.exempt
def deep_work_toggle():
    """Deep Work oturumu başlat/durdur"""
    try:
        data = request.get_json() if request.is_json else request.form
        action = data.get('action', 'start')  # start veya stop
        
        if action == 'start':
            session = DeepWorkSession(
                user_id=current_user.id,
                start_time=datetime.utcnow(),
                status='active'
            )
            db.session.add(session)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Deep Work oturumu başlatıldı', 'session_id': session.id})
        else:
            # Son aktif oturumu bul ve durdur
            session = DeepWorkSession.query.filter_by(
                user_id=current_user.id,
                status='active'
            ).order_by(DeepWorkSession.start_time.desc()).first()
            
            if session:
                session.end_time = datetime.utcnow()
                session.duration_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
                session.status = 'completed'
                db.session.commit()
                return jsonify({'success': True, 'message': 'Deep Work oturumu durduruldu', 'duration': session.duration_minutes})
            else:
                return jsonify({'success': False, 'message': 'Aktif oturum bulunamadı'}), 404
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Deep Work toggle hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


# V63.0 - Transcendence Pack
@main_bp.route('/synthetic-lab')
@login_required
def synthetic_lab():
    """Sentetik Müşteri Laboratuvarı sayfası"""
    try:
        kurum = current_user.kurum
        personas = Persona.query.filter_by(kurum_id=kurum.id).all()
        simulations = ProductSimulation.query.filter_by(kurum_id=kurum.id).order_by(
            ProductSimulation.created_at.desc()
        ).limit(50).all()
        
        return render_template('synthetic_lab.html', personas=personas, simulations=simulations, kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'Synthetic Lab sayfası hatası: {e}')
        flash('Sentetik Müşteri Laboratuvarı sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/governance')
@login_required
def governance():
    """DAO Yönetimi sayfası"""
    try:
        kurum = current_user.kurum
        contracts = SmartContract.query.filter_by(kurum_id=kurum.id).all()
        proposals = DaoProposal.query.filter_by(kurum_id=kurum.id).order_by(
            DaoProposal.created_at.desc()
        ).limit(50).all()
        
        return render_template('governance.html', contracts=contracts, proposals=proposals, kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'Governance sayfası hatası: {e}')
        flash('DAO Yönetimi sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/metaverse')
@login_required
def metaverse():
    """Metaverse Departman İkizi sayfası"""
    try:
        kurum = current_user.kurum
        departments = MetaverseDepartment.query.filter_by(kurum_id=kurum.id).all()
        
        return render_template('metaverse.html', departments=departments, kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'Metaverse sayfası hatası: {e}')
        flash('Metaverse Departman İkizi sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/legacy-chat')
@login_required
def legacy_chat():
    """Kurucu Miras AI sayfası"""
    try:
        kurum = current_user.kurum
        knowledge = LegacyKnowledge.query.filter_by(kurum_id=kurum.id).order_by(
            LegacyKnowledge.created_at.desc()
        ).limit(100).all()
        
        return render_template('legacy_chat.html', knowledge=knowledge, kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'Legacy Chat sayfası hatası: {e}')
        flash('Kurucu Miras AI sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


# ============================================
# FAZ 4: NIRVANA LEGACY ROUTE'LARI
# ============================================

# V66.0 - Nirvana Legacy Paketi
@main_bp.route('/game-theory')
@login_required
def game_theory():
    """Oyun Teorisi (Game Theory Grid) sayfası"""
    try:
        kurum = current_user.kurum
        competitors = Competitor.query.filter_by(kurum_id=kurum.id).all()
        scenarios = GameScenario.query.filter_by(kurum_id=kurum.id).order_by(
            GameScenario.created_at.desc()
        ).limit(50).all()
        
        # Nash dengesi hesaplamaları için servisi import et
        from services.game_theory_service import calculate_nash_equilibrium, get_strategy_recommendation
        
        # Senaryolar için Nash dengesi sonuçlarını hesapla
        scenario_results = []
        for scenario in scenarios:
            if scenario.payoffs and scenario.nash_equilibrium:
                try:
                    nash_result = calculate_nash_equilibrium(scenario.payoffs)
                    recommendation = get_strategy_recommendation(nash_result)
                    scenario_results.append({
                        'scenario': scenario,
                        'nash_result': nash_result,
                        'recommendation': recommendation
                    })
                except Exception as e:
                    current_app.logger.warning(f'Nash dengesi hesaplama hatası (scenario {scenario.id}): {e}')
        
        return render_template('game_theory.html', 
                             competitors=competitors, 
                             scenarios=scenarios, 
                             scenario_results=scenario_results,
                             kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'Game Theory sayfası hatası: {e}')
        flash('Oyun Teorisi sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/game-theory/scenario/<int:scenario_id>/calculate-nash', methods=['POST'])
@login_required
def calculate_nash_for_scenario(scenario_id):
    """Belirli bir senaryo için Nash dengesi hesapla"""
    try:
        scenario = GameScenario.query.get_or_404(scenario_id)
        
        # Sadece kendi kurumunun senaryosunu hesaplayabilir
        if scenario.kurum_id != current_user.kurum_id:
            return jsonify({'error': 'Yetkisiz erişim'}), 403
        
        from services.game_theory_service import calculate_nash_equilibrium, get_strategy_recommendation
        
        if not scenario.payoffs:
            return jsonify({'error': 'Kazanç matrisi bulunamadı'}), 400
        
        nash_result = calculate_nash_equilibrium(scenario.payoffs)
        recommendation = get_strategy_recommendation(nash_result)
        
        # Sonucu senaryoya kaydet
        scenario.nash_equilibrium = json.dumps(nash_result)
        scenario.strategy_recommendation = recommendation
        db.session.commit()
        
        return jsonify({
            'success': True,
            'nash_result': nash_result,
            'recommendation': recommendation
        })
    except Exception as e:
        current_app.logger.error(f'Nash dengesi hesaplama hatası: {e}')
        return jsonify({'error': str(e)}), 500


@main_bp.route('/knowledge-graph')
@login_required
def knowledge_graph():
    """Bilgi Grafığı sayfası"""
    try:
        kurum = current_user.kurum
        # Bilgi grafığı için veri topla (stratejiler, süreçler, projeler, vb.)
        strategies = AltStrateji.query.join(AnaStrateji).filter(
            AnaStrateji.kurum_id == kurum.id
        ).all()
        processes = Surec.query.filter_by(kurum_id=kurum.id).all()
        projects = Project.query.filter_by(kurum_id=kurum.id).all()
        
        # Bilgi grafığı servisi ile veri yapısını oluştur
        from services.knowledge_graph_service import build_knowledge_graph_data, calculate_centrality_metrics
        
        graph_data = build_knowledge_graph_data(strategies, processes, projects)
        centrality_metrics = calculate_centrality_metrics(graph_data['nodes'], graph_data['edges'])
        
        return render_template('knowledge_graph.html', 
                             strategies=strategies, 
                             processes=processes, 
                             projects=projects,
                             graph_data=graph_data,
                             centrality_metrics=centrality_metrics,
                             kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'Knowledge Graph sayfası hatası: {e}')
        flash('Bilgi Grafığı sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/black-swan')
@login_required
def black_swan():
    """Siyah Kuğu Simülatörü (Doomsday Prepper) sayfası"""
    try:
        kurum = current_user.kurum
        scenarios = DoomsdayScenario.query.filter_by(kurum_id=kurum.id).order_by(
            DoomsdayScenario.severity_level.desc()
        ).all()
        
        return render_template('black_swan.html', scenarios=scenarios, kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'Black Swan sayfası hatası: {e}')
        flash('Siyah Kuğu Simülatörü sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/library')
@login_required
def library():
    """Omega'nın Kitabı (Auto-Biography) sayfası"""
    try:
        kurum = current_user.kurum
        chronicles = YearlyChronicle.query.filter_by(kurum_id=kurum.id).order_by(
            YearlyChronicle.year.desc()
        ).all()
        
        return render_template('library.html', chronicles=chronicles, kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'Library sayfası hatası: {e}')
        flash('Omega\'nın Kitabı sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))


# ============================================
# ADMIN API ENDPOINTS
# ============================================

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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


@main_bp.route('/admin/deleted-organizations', methods=['GET'])
@login_required
def admin_deleted_organizations():
    """Silinmiş kurumlar listesi - Sadece sistem admini görebilir"""
    try:
        # Sadece sistem admini görebilir
        is_system_admin = current_user.sistem_rol == 'admin' and current_user.kurum_id == 1
        
        if not is_system_admin:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403

        deleted_kurumlar = Kurum.query.filter_by(silindi=True).all()
        
        kurumlar_data = []
        for kurum in deleted_kurumlar:
            user_count = User.query.filter_by(kurum_id=kurum.id, silindi=True).count()
            surec_count = Surec.query.filter_by(kurum_id=kurum.id, silindi=True).count()
            
            deleter = None
            if kurum.deleted_by:
                deleter_user = User.query.get(kurum.deleted_by)
                if deleter_user:
                    deleter = f"{deleter_user.first_name} {deleter_user.last_name}"
            
            kurumlar_data.append({
                'id': kurum.id,
                'kisa_ad': kurum.kisa_ad,
                'ticari_unvan': kurum.ticari_unvan,
                'deleted_at': kurum.deleted_at.strftime('%d.%m.%Y %H:%M') if kurum.deleted_at else None,
                'deleted_by_name': deleter,
                'user_count': user_count,
                'surec_count': surec_count
            })
        
        return jsonify({
            'success': True,
            'data': kurumlar_data
        })
    except Exception as e:
        current_app.logger.error(f'Silinmiş kurumlar listesi hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


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
            except:
                pass
        
        if completed:
            completed_walkthroughs[page_id] = True
        
        import json
        current_user.completed_walkthroughs = json.dumps(completed_walkthroughs)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        current_app.logger.error(f'Guide preferences güncelleme hatası: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


@main_bp.route('/yardim-merkezi')
@login_required
def help_center():
    """İnteraktif Yardım Merkezi"""
    return render_template('help_center.html', title='Yardım Merkezi')


@main_bp.route('/admin/feedback')
@login_required
def admin_feedback():
    """
    Admin - Kule İletişim Modülü Geri Bildirim Yönetimi
    
    Admin ve kurum yöneticileri için geri bildirimleri görüntüleme ve yönetme sayfası.
    """
    # Yetki kontrolü
    if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
        flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Sistem admini kontrolü
    is_system_admin = current_user.sistem_rol == 'admin' and current_user.kurum_id == 1
    
    # Filtreleme parametreleri
    status_filter = request.args.get('status', 'all')
    category_filter = request.args.get('category', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Query oluştur
    query = Feedback.query
    
    # Sistem admini değilse sadece kendi kurumunun kullanıcılarının feedback'lerini göster
    if not is_system_admin:
        from app.models.legacy_bridge import User
        user_ids = [u.id for u in User.query.filter_by(kurum_id=current_user.kurum_id).all()]
        query = query.filter(Feedback.user_id.in_(user_ids))
    
    # Durum filtresi
    if status_filter != 'all':
        query = query.filter(Feedback.status == status_filter)
    
    # Kategori filtresi
    if category_filter != 'all':
        query = query.filter(Feedback.category == category_filter)
    
    # Sıralama (en yeni önce)
    query = query.order_by(Feedback.created_at.desc())
    
    # Sayfalama
    feedbacks = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # İstatistikler
    total_count = Feedback.query.count() if is_system_admin else Feedback.query.filter(Feedback.user_id.in_(user_ids)).count()
    pending_count = Feedback.query.filter_by(status='Bekliyor').count() if is_system_admin else Feedback.query.filter(Feedback.user_id.in_(user_ids), Feedback.status == 'Bekliyor').count()
    in_progress_count = Feedback.query.filter_by(status='İnceleniyor').count() if is_system_admin else Feedback.query.filter(Feedback.user_id.in_(user_ids), Feedback.status == 'İnceleniyor').count()
    resolved_count = Feedback.query.filter_by(status='Çözüldü').count() if is_system_admin else Feedback.query.filter(Feedback.user_id.in_(user_ids), Feedback.status == 'Çözüldü').count()
    
    return render_template('admin/feedback_management.html',
                         feedbacks=feedbacks,
                         status_filter=status_filter,
                         category_filter=category_filter,
                         total_count=total_count,
                         pending_count=pending_count,
                         in_progress_count=in_progress_count,
                         resolved_count=resolved_count,
                         is_system_admin=is_system_admin)


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
        user_name = feedback.user.first_name or feedback.user.username if feedback.user else 'Bilinmeyen Kullanıcı'
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
                # Dosya uzantısı kontrolü
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                file_ext = screenshot_file.filename.rsplit('.', 1)[1].lower() if '.' in screenshot_file.filename else ''
                
                if file_ext not in allowed_extensions:
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
        
        current_app.logger.info(f'Yeni geri bildirim kaydedildi: ID={feedback.id}, Kullanıcı={current_user.username}, Kategori={category}')
        
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
