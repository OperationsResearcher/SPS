# -*- coding: utf-8 -*-
# Otomatik bölüm — `python scripts/dev/split_main_routes.py`
from main.routes._common import *  # noqa: F401,F403
from main.routes import main_bp
from main.deprecated import legacy_html_to_platform


@main_bp.route('/kurum-paneli')
@login_required
@legacy_html_to_platform
def kurum_paneli():
    """
    Stratejik Yönetim Kokpiti
    
    Vizyon → Strateji → Süreç → PG → Proje hiyerarşisini analiz eder.
    BSC perspektif analizi, ağırlıklı performans hesaplamaları ve proje sağlık durumu sunar.
    """
    # Yetki kontrolü
    if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
        flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Kurum ID belirleme
        kurum_id = current_user.kurum_id
        is_admin = current_user.sistem_rol == 'admin'
        
        # Kurum bilgilerini getir
        if is_admin:
            kurumlar = Kurum.query.filter_by(silindi=False).all()
            kurum = kurumlar[0] if kurumlar else None
        else:
            kurum = Kurum.query.get(kurum_id)
            kurumlar = [kurum] if kurum else []
        
        # ============================================================
        # A. VİZYON VE GLOBAL SKOR
        # ============================================================
        vizyon = kurum.vizyon if kurum else "Vizyon henüz tanımlanmamış."
        
        # Global skor: Tüm aktif PG'lerin ağırlıklı başarı puanı ortalaması
        global_score_query = db.session.query(
            db.func.avg(SurecPerformansGostergesi.agirlikli_basari_puani)
        ).join(Surec).filter(
            Surec.silindi == False,
            Surec.durum.in_(['Aktif', 'Devam Ediyor'])
        )
        
        if not is_admin:
            global_score_query = global_score_query.filter(Surec.kurum_id == kurum_id)
        
        global_score_result = global_score_query.scalar()
        global_score = int(global_score_result) if global_score_result else 0
        
        # ============================================================
        # B. BSC PERSPEKTİF DAĞILIMI (Radar Chart)
        # ============================================================
        bsc_query = db.session.query(
            AnaStrateji.perspective,
            db.func.count(AnaStrateji.id).label('count')
        )
        
        if not is_admin:
            bsc_query = bsc_query.filter(AnaStrateji.kurum_id == kurum_id)
        
        bsc_data = bsc_query.group_by(AnaStrateji.perspective).all()
        
        # BSC perspektif haritası
        bsc_map = {
            'FINANSAL': 'Finansal',
            'MUSTERI': 'Müşteri',
            'SUREC': 'Süreç',
            'OGRENME': 'Öğrenme'
        }
        
        bsc_distribution = {
            'labels': [],
            'data': [],
            'colors': ['#667eea', '#11998e', '#4facfe', '#f093fb']
        }
        
        for perspective, count in bsc_data:
            if perspective:
                label = bsc_map.get(perspective, perspective)
                bsc_distribution['labels'].append(label)
                bsc_distribution['data'].append(count)
        
        # Eksik perspektifleri 0 ile doldur
        for key, label in bsc_map.items():
            if label not in bsc_distribution['labels']:
                bsc_distribution['labels'].append(label)
                bsc_distribution['data'].append(0)
        
        # ============================================================
        # C. STRATEJİK İLERLEME (Ana Stratejiler)
        # ============================================================
        strategic_progress = []
        
        ana_strateji_query = AnaStrateji.query
        if not is_admin:
            ana_strateji_query = ana_strateji_query.filter_by(kurum_id=kurum_id)
        
        ana_stratejiler = ana_strateji_query.all()
        
        for ana_strateji in ana_stratejiler:
            # Alt stratejilerin ortalama başarısını hesapla
            alt_stratejiler = ana_strateji.alt_stratejiler
            
            if alt_stratejiler:
                # Her alt stratejiye bağlı PG'lerin ortalama başarı puanı
                total_score = 0
                total_count = 0
                
                for alt_strateji in alt_stratejiler:
                    pg_scores = db.session.query(
                        db.func.avg(SurecPerformansGostergesi.basari_puani)
                    ).filter(
                        SurecPerformansGostergesi.alt_strateji_id == alt_strateji.id
                    ).scalar()
                    
                    if pg_scores:
                        total_score += pg_scores
                        total_count += 1
                
                avg_score = int(total_score / total_count) if total_count > 0 else 0
            else:
                avg_score = 0
            
            strategic_progress.append({
                'id': ana_strateji.id,
                'code': ana_strateji.code or '',
                'ad': ana_strateji.ad,
                'perspective': ana_strateji.perspective or 'SUREC',
                'skor': avg_score,
                'alt_strateji_sayisi': len(alt_stratejiler)
            })
        
        # ============================================================
        # D. SÜREÇ ISI HARİTASI (En İyi ve En Riskli Süreçler)
        # ============================================================
        surec_query = db.session.query(
            Surec.id,
            Surec.ad,
            Surec.code,
            Surec.weight,
            Surec.ilerleme,
            db.func.avg(SurecPerformansGostergesi.agirlikli_basari_puani).label('avg_score')
        ).outerjoin(
            SurecPerformansGostergesi
        ).filter(
            Surec.silindi == False
        ).group_by(
            Surec.id, Surec.ad, Surec.code, Surec.weight, Surec.ilerleme
        )
        
        if not is_admin:
            surec_query = surec_query.filter(Surec.kurum_id == kurum_id)
        
        surec_data = surec_query.all()
        
        # Skorlara göre sırala
        surec_list = []
        for s in surec_data:
            surec_list.append({
                'id': s.id,
                'ad': s.ad,
                'code': s.code or '',
                'weight': float(s.weight) if s.weight else 0.0,
                'ilerleme': s.ilerleme or 0,
                'skor': int(s.avg_score) if s.avg_score else 0
            })
        
        # Skora göre sırala
        surec_list_sorted = sorted(surec_list, key=lambda x: x['skor'], reverse=True)
        
        top_processes = surec_list_sorted[:5]  # En başarılı 5
        risky_processes = surec_list_sorted[-5:][::-1]  # En riskli 5 (ters çevir)
        
        # ============================================================
        # E. PROJE ETKİSİ (Proje Sağlık Durumu)
        # ============================================================
        project_query = Project.query.filter_by(is_archived=False)
        
        if not is_admin:
            project_query = project_query.filter_by(kurum_id=kurum_id)
        
        total_projects = project_query.count()
        
        # Sağlık durumu dağılımı
        health_distribution = {
            'Mükemmel': 0,
            'İyi': 0,
            'Dikkat': 0,
            'Kritik': 0
        }
        
        projects = project_query.all()
        for project in projects:
            health = project.health_status or 'İyi'
            if health in health_distribution:
                health_distribution[health] += 1
            else:
                # Varsayılan
                if project.health_score and project.health_score >= 80:
                    health_distribution['Mükemmel'] += 1
                elif project.health_score and project.health_score >= 50:
                    health_distribution['İyi'] += 1
                else:
                    health_distribution['Dikkat'] += 1
        
        # Tamamlanma yüzdesi (Bitiş tarihi geçmiş projeler)
        today = date.today()
        completed_projects = 0
        for project in projects:
            if project.end_date and project.end_date < today:
                completed_projects += 1
        
        completion_rate = int((completed_projects / total_projects) * 100) if total_projects > 0 else 0
        
        project_impact = {
            'total': total_projects,
            'health_distribution': health_distribution,
            'completion_rate': completion_rate
        }
        
        # ============================================================
        # F. MEVCUT VERİLER (Eski Yapı ile Uyumluluk)
        # ============================================================
        try:
            if is_admin:
                degerler = Deger.query.all()
                etik_kurallari = EtikKural.query.all()
                kalite_politikalari = KalitePolitikasi.query.all()
                uyeler = User.query.filter_by(silindi=False).all()
                surecler = Surec.query.filter_by(silindi=False).all()
            else:
                degerler = Deger.query.filter_by(kurum_id=kurum_id).all()
                etik_kurallari = EtikKural.query.filter_by(kurum_id=kurum_id).all()
                kalite_politikalari = KalitePolitikasi.query.filter_by(kurum_id=kurum_id).all()
                uyeler = User.query.filter_by(kurum_id=kurum_id, silindi=False).all()
                surecler = Surec.query.filter_by(kurum_id=kurum_id, silindi=False).all()
        except Exception as e:
            current_app.logger.error(f"Kurum bilgileri getirilirken hata: {e}")
            degerler = []
            etik_kurallari = []
            kalite_politikalari = []
            uyeler = []
            surecler = []
        
        # ============================================================
        # TEMPLATE'E GÖNDERİLECEK VERİLER
        # ============================================================
        return render_template('kurum_panel.html',
                             # Kurum Bilgileri
                             kurum=kurum,
                             kurumlar=kurumlar if is_admin else None,
                             
                             # Stratejik Veri Motoru
                             vizyon=vizyon,
                             global_score=global_score,
                             bsc_distribution=bsc_distribution,
                             strategic_progress=strategic_progress,
                             top_processes=top_processes,
                             risky_processes=risky_processes,
                             project_impact=project_impact,
                             
                             # Mevcut Veriler (Uyumluluk)
                             ana_stratejiler=ana_stratejiler,
                             degerler=degerler,
                             etik_kurallari=etik_kurallari,
                             kalite_politikalari=kalite_politikalari,
                             surecler=surecler,
                             uyeler=uyeler)
                             
    except Exception as e:
        import traceback
        current_app.logger.error(f'Kurum Paneli (Stratejik Kokpit) hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        return f"Stratejik Kokpit yüklenirken hata oluştu: {str(e)}", 500


@main_bp.route('/v3/kurum-paneli')
@login_required
def kurum_paneli_v3():
    """
    Stratejik Yönetim Kokpiti V3 (Dual Mode: Standard + Visual)
    
    - Standart Mod: Chart.js tabanlı temiz dashboard
    - Görsel Mod: Apache ECharts ile interaktif veri görselleştirme
    """
    # Yetki kontrolü
    if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
        flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Kurum ID belirleme
        kurum_id = current_user.kurum_id
        is_admin = current_user.sistem_rol == 'admin'
        
        # Kurum bilgilerini getir
        if is_admin:
            kurumlar = Kurum.query.filter_by(silindi=False).all()
            kurum = kurumlar[0] if kurumlar else None
        else:
            kurum = Kurum.query.get(kurum_id)
            kurumlar = [kurum] if kurum else []
        
        # ============================================================
        # A. VİZYON VE GLOBAL SKOR
        # ============================================================
        vizyon = kurum.vizyon if kurum else "Vizyonumuz: Sektörde öncü, yenilikçi ve sürdürülebilir bir kurum olmak."
        
        # Global skor: Tüm aktif PG'lerin ağırlıklı başarı puanı ortalaması
        global_score_query = db.session.query(
            db.func.avg(SurecPerformansGostergesi.agirlikli_basari_puani)
        ).join(Surec).filter(
            Surec.silindi == False,
            Surec.durum.in_(['Aktif', 'Devam Ediyor'])
        )
        
        if not is_admin:
            global_score_query = global_score_query.filter(Surec.kurum_id == kurum_id)
        
        global_score_result = global_score_query.scalar()
        global_score = int(global_score_result) if global_score_result else 0
        
        # ============================================================
        # B. BSC PERSPEKTİF DAĞILIMI (Radar Chart)
        # ============================================================
        bsc_query = db.session.query(
            AnaStrateji.perspective,
            db.func.count(AnaStrateji.id).label('count')
        )
        
        if not is_admin:
            bsc_query = bsc_query.filter(AnaStrateji.kurum_id == kurum_id)
        
        bsc_data = bsc_query.group_by(AnaStrateji.perspective).all()
        
        # BSC perspektif haritası
        bsc_map = {
            'FINANSAL': 'Finansal',
            'MUSTERI': 'Müşteri',
            'SUREC': 'Süreç',
            'OGRENME': 'Öğrenme'
        }
        
        bsc_distribution = {
            'labels': [],
            'data': [],
            'colors': ['#667eea', '#11998e', '#4facfe', '#f093fb']
        }
        
        for perspective, count in bsc_data:
            if perspective:
                label = bsc_map.get(perspective, perspective)
                bsc_distribution['labels'].append(label)
                bsc_distribution['data'].append(count)
        
        # Eksik perspektifleri 0 ile doldur
        for key, label in bsc_map.items():
            if label not in bsc_distribution['labels']:
                bsc_distribution['labels'].append(label)
                bsc_distribution['data'].append(0)
        
        # ============================================================
        # C. STRATEJİK İLERLEME (Ana Stratejiler)
        # ============================================================
        strategic_progress = []
        
        ana_strateji_query = AnaStrateji.query
        if not is_admin:
            ana_strateji_query = ana_strateji_query.filter_by(kurum_id=kurum_id)
        
        ana_stratejiler = ana_strateji_query.all()
        
        for ana_strateji in ana_stratejiler:
            # Alt stratejilerin ortalama başarısını hesapla
            alt_stratejiler = ana_strateji.alt_stratejiler
            
            if alt_stratejiler:
                # Her alt stratejiye bağlı PG'lerin ortalama başarı puanı
                total_score = 0
                total_count = 0
                
                for alt_strateji in alt_stratejiler:
                    pg_scores = db.session.query(
                        db.func.avg(SurecPerformansGostergesi.basari_puani)
                    ).filter(
                        SurecPerformansGostergesi.alt_strateji_id == alt_strateji.id
                    ).scalar()
                    
                    if pg_scores:
                        total_score += pg_scores
                        total_count += 1
                
                avg_score = int(total_score / total_count) if total_count > 0 else 0
            else:
                avg_score = 0
            
            strategic_progress.append({
                'id': ana_strateji.id,
                'code': ana_strateji.code or '',
                'ad': ana_strateji.ad,
                'perspective': ana_strateji.perspective or 'SUREC',
                'skor': avg_score,
                'alt_strateji_sayisi': len(alt_stratejiler)
            })
        
        # ============================================================
        # D. SÜREÇ ISI HARİTASI (En İyi ve En Riskli Süreçler)
        # ============================================================
        surec_query = db.session.query(
            Surec.id,
            Surec.ad,
            Surec.code,
            Surec.weight,
            Surec.ilerleme,
            db.func.avg(SurecPerformansGostergesi.agirlikli_basari_puani).label('avg_score')
        ).outerjoin(
            SurecPerformansGostergesi
        ).filter(
            Surec.silindi == False
        ).group_by(
            Surec.id, Surec.ad, Surec.code, Surec.weight, Surec.ilerleme
        )
        
        if not is_admin:
            surec_query = surec_query.filter(Surec.kurum_id == kurum_id)
        
        surec_data = surec_query.all()
        
        # Skorlara göre sırala
        surec_list = []
        for s in surec_data:
            surec_list.append({
                'id': s.id,
                'ad': s.ad,
                'code': s.code or '',
                'weight': float(s.weight) if s.weight else 0.0,
                'ilerleme': s.ilerleme or 0,
                'skor': int(s.avg_score) if s.avg_score else 0
            })
        
        # Skora göre sırala
        surec_list_sorted = sorted(surec_list, key=lambda x: x['skor'], reverse=True)
        
        top_processes = surec_list_sorted[:5]  # En başarılı 5
        risky_processes = surec_list_sorted[-5:][::-1]  # En riskli 5 (ters çevir)
        
        # ============================================================
        # E. PROJE ETKİSİ (Proje Sağlık Durumu)
        # ============================================================
        project_query = Project.query.filter_by(is_archived=False)
        
        if not is_admin:
            project_query = project_query.filter_by(kurum_id=kurum_id)
        
        total_projects = project_query.count()
        
        # Sağlık durumu dağılımı
        health_distribution = {
            'Mükemmel': 0,
            'İyi': 0,
            'Dikkat': 0,
            'Kritik': 0
        }
        
        projects = project_query.all()
        for project in projects:
            health = project.health_status or 'İyi'
            if health in health_distribution:
                health_distribution[health] += 1
            else:
                # Varsayılan
                if project.health_score and project.health_score >= 80:
                    health_distribution['Mükemmel'] += 1
                elif project.health_score and project.health_score >= 50:
                    health_distribution['İyi'] += 1
                else:
                    health_distribution['Dikkat'] += 1
        
        # Tamamlanma yüzdesi (Bitiş tarihi geçmiş projeler)
        today = date.today()
        completed_projects = 0
        for project in projects:
            if project.end_date and project.end_date < today:
                completed_projects += 1
        
        completion_rate = int((completed_projects / total_projects) * 100) if total_projects > 0 else 0
        
        project_impact = {
            'total': total_projects,
            'health_distribution': health_distribution,
            'completion_rate': completion_rate
        }
        
        # ============================================================
        # TEMPLATE'E GÖNDERİLECEK VERİLER (V3)
        # ============================================================
        return render_template('v3/kurum_panel.html',
                             # Kurum Bilgileri
                             kurum=kurum,
                             kurumlar=kurumlar if is_admin else None,
                             
                             # Stratejik Veri Motoru
                             vizyon=vizyon,
                             global_score=global_score,
                             bsc_distribution=bsc_distribution,
                             strategic_progress=strategic_progress,
                             top_processes=top_processes,
                             risky_processes=risky_processes,
                             project_impact=project_impact)
                             
    except Exception as e:
        import traceback
        current_app.logger.error(f'Kurum Paneli V3 hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        return f"Stratejik Kokpit V3 yüklenirken hata oluştu: {str(e)}", 500


@main_bp.route('/v3/skor-motoru')
@login_required
def skor_motoru_detay():
    """Skor Motoru detay sayfası: Vizyon puanı, ana/alt strateji, süreç ve PG skorları (API'den)."""
    if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
        flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
        return redirect(url_for('main.dashboard'))
    return render_template('v3/skor_motoru_detay.html')


@main_bp.route('/v3/kurum-paneli/visual')
@login_required
def kurum_paneli_visual():
    """
    Stratejik Yönetim Kokpiti - Görsel Mod (Sadece ECharts)
    """
    # Yetki kontrolü
    if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
        flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Kurum ID belirleme
        kurum_id = current_user.kurum_id
        is_admin = current_user.sistem_rol == 'admin'
        
        # Kurum bilgilerini getir
        if is_admin:
            kurumlar = Kurum.query.filter_by(silindi=False).all()
            kurum = kurumlar[0] if kurumlar else None
        else:
            kurum = Kurum.query.get(kurum_id)
            kurumlar = [kurum] if kurum else []
        
        # ============================================================
        # A. VİZYON VE GLOBAL SKOR
        # ============================================================
        vizyon = kurum.vizyon if kurum else "Vizyonumuz: Sektörde öncü, yenilikçi ve sürdürülebilir bir kurum olmak."
        
        # Global skor: Tüm aktif PG'lerin ağırlıklı başarı puanı ortalaması
        global_score_query = db.session.query(
            db.func.avg(SurecPerformansGostergesi.agirlikli_basari_puani)
        ).join(Surec).filter(
            Surec.silindi == False,
            Surec.durum.in_(['Aktif', 'Devam Ediyor'])
        )
        
        if not is_admin:
            global_score_query = global_score_query.filter(Surec.kurum_id == kurum_id)
        
        global_score_result = global_score_query.scalar()
        global_score = int(global_score_result) if global_score_result else 0
        
        # ============================================================
        # B. BSC PERSPEKTİF DAĞILIMI (Radar Chart)
        # ============================================================
        bsc_query = db.session.query(
            AnaStrateji.perspective,
            db.func.count(AnaStrateji.id).label('count')
        )
        
        if not is_admin:
            bsc_query = bsc_query.filter(AnaStrateji.kurum_id == kurum_id)
        
        bsc_data = bsc_query.group_by(AnaStrateji.perspective).all()
        
        # BSC perspektif haritası
        bsc_map = {
            'FINANSAL': 'Finansal',
            'MUSTERI': 'Müşteri',
            'SUREC': 'Süreç',
            'OGRENME': 'Öğrenme'
        }
        
        bsc_distribution = {
            'labels': [],
            'data': [],
            'colors': ['#667eea', '#11998e', '#4facfe', '#f093fb']
        }
        
        for perspective, count in bsc_data:
            if perspective:
                label = bsc_map.get(perspective, perspective)
                bsc_distribution['labels'].append(label)
                bsc_distribution['data'].append(count)
        
        # Eksik perspektifleri 0 ile doldur
        for key, label in bsc_map.items():
            if label not in bsc_distribution['labels']:
                bsc_distribution['labels'].append(label)
                bsc_distribution['data'].append(0)
        
        # ============================================================
        # C. STRATEJİK İLERLEME (Ana Stratejiler)
        # ============================================================
        strategic_progress = []
        
        ana_strateji_query = AnaStrateji.query
        if not is_admin:
            ana_strateji_query = ana_strateji_query.filter_by(kurum_id=kurum_id)
        
        ana_stratejiler = ana_strateji_query.all()
        
        for ana_strateji in ana_stratejiler:
            # Alt stratejilerin ortalama başarısını hesapla
            alt_stratejiler = ana_strateji.alt_stratejiler
            
            if alt_stratejiler:
                # Her alt stratejiye bağlı PG'lerin ortalama başarı puanı
                total_score = 0
                total_count = 0
                
                for alt_strateji in alt_stratejiler:
                    pg_scores = db.session.query(
                        db.func.avg(SurecPerformansGostergesi.basari_puani)
                    ).filter(
                        SurecPerformansGostergesi.alt_strateji_id == alt_strateji.id
                    ).scalar()
                    
                    if pg_scores:
                        total_score += pg_scores
                        total_count += 1
                
                avg_score = int(total_score / total_count) if total_count > 0 else 0
            else:
                avg_score = 0
            
            strategic_progress.append({
                'id': ana_strateji.id,
                'code': ana_strateji.code or '',
                'ad': ana_strateji.ad,
                'perspective': ana_strateji.perspective or 'SUREC',
                'skor': avg_score,
                'alt_strateji_sayisi': len(alt_stratejiler)
            })
        
        # ============================================================
        # D. SÜREÇ ISI HARİTASI (En İyi ve En Riskli Süreçler)
        # ============================================================
        surec_query = db.session.query(
            Surec.id,
            Surec.ad,
            Surec.code,
            Surec.weight,
            Surec.ilerleme,
            db.func.avg(SurecPerformansGostergesi.agirlikli_basari_puani).label('avg_score')
        ).outerjoin(
            SurecPerformansGostergesi
        ).filter(
            Surec.silindi == False
        ).group_by(
            Surec.id, Surec.ad, Surec.code, Surec.weight, Surec.ilerleme
        )
        
        if not is_admin:
            surec_query = surec_query.filter(Surec.kurum_id == kurum_id)
        
        surec_data = surec_query.all()
        
        # Skorlara göre sırala
        surec_list = []
        for s in surec_data:
            surec_list.append({
                'id': s.id,
                'ad': s.ad,
                'code': s.code or '',
                'weight': float(s.weight) if s.weight else 0.0,
                'ilerleme': s.ilerleme or 0,
                'skor': int(s.avg_score) if s.avg_score else 0
            })
        
        # Skora göre sırala
        surec_list_sorted = sorted(surec_list, key=lambda x: x['skor'], reverse=True)
        
        top_processes = surec_list_sorted[:5]  # En başarılı 5
        risky_processes = surec_list_sorted[-5:][::-1]  # En riskli 5 (ters çevir)
        
        # ============================================================
        # E. PROJE ETKİSİ (Proje Sağlık Durumu)
        # ============================================================
        project_query = Project.query.filter_by(is_archived=False)
        
        if not is_admin:
            project_query = project_query.filter_by(kurum_id=kurum_id)
        
        total_projects = project_query.count()
        
        # Sağlık durumu dağılımı
        health_distribution = {
            'Mükemmel': 0,
            'İyi': 0,
            'Dikkat': 0,
            'Kritik': 0
        }
        
        projects = project_query.all()
        for project in projects:
            health = project.health_status or 'İyi'
            if health in health_distribution:
                health_distribution[health] += 1
            else:
                # Varsayılan
                if project.health_score and project.health_score >= 80:
                    health_distribution['Mükemmel'] += 1
                elif project.health_score and project.health_score >= 50:
                    health_distribution['İyi'] += 1
                else:
                    health_distribution['Dikkat'] += 1
        
        # Tamamlanma yüzdesi (Bitiş tarihi geçmiş projeler)
        today = date.today()
        completed_projects = 0
        for project in projects:
            if project.end_date and project.end_date < today:
                completed_projects += 1
        
        completion_rate = int((completed_projects / total_projects) * 100) if total_projects > 0 else 0
        
        project_impact = {
            'total': total_projects,
            'health_distribution': health_distribution,
            'completion_rate': completion_rate
        }
        
        # ============================================================
        # TEMPLATE'E GÖNDERİLECEK VERİLER (V3 VISUAL)
        # ============================================================
        return render_template('v3/kurum_panel_visual.html',
                             # Kurum Bilgileri
                             kurum=kurum,
                             kurumlar=kurumlar if is_admin else None,
                             
                             # Stratejik Veri Motoru
                             vizyon=vizyon,
                             global_score=global_score,
                             bsc_distribution=bsc_distribution,
                             strategic_progress=strategic_progress,
                             top_processes=top_processes,
                             risky_processes=risky_processes,
                             project_impact=project_impact)
                             
    except Exception as e:
        import traceback
        current_app.logger.error(f'Kurum Paneli Visual V3 hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        return f"Stratejik Kokpit Visual V3 yüklenirken hata oluştu: {str(e)}", 500



@main_bp.route('/admin/seed_db')
@login_required
def seed_db():
    """Veritabanına demo veri ekle - Sadece admin için"""
    try:
        # Sadece admin rolü için
        if current_user.sistem_rol != 'admin':
            flash('Bu işlem için yetkiniz yok.', 'error')
            return redirect(url_for('main.dashboard'))
        
        from services.seeder import seed_all
        
        results = seed_all(db)
        
        if results['hata']:
            flash(f'Demo veri oluşturulurken hata oluştu: {results["hata"]}', 'error')
        else:
            flash(
                f'Demo veriler başarıyla oluşturuldu! '
                f'Kurum: {results["kurumlar"]}, Kullanıcı: {results["users"]}, '
                f'Ana Strateji: {results["ana_stratejiler"]}, Alt Strateji: {results["alt_stratejiler"]}, '
                f'Süreç: {results["surecler"]}, Proje: {results["projeler"]}, Görev: {results["gorevler"]}',
                'success'
            )
        
        return redirect(url_for('main.admin_panel'))
    except Exception as e:
        current_app.logger.error(f'Seed DB hatası: {e}')
        flash('Demo veri oluşturulurken bir hata oluştu.', 'error')
        return redirect(url_for('main.admin_panel'))


@main_bp.route('/admin-panel')
@login_required
def admin_panel():
    """Admin Panel sayfası - Sistem yöneticileri ve kurum yöneticileri için"""
    # Admin veya kurum_yoneticisi erişebilir
    if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
        flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    from app.models.legacy_bridge import Kurum, User, Surec, AnaStrateji
    
    # Sistem admini (kurum_id=1) - TÜM kurumlar, TÜM kullanıcılar, TÜM süreçler
    is_system_admin = current_user.sistem_rol == 'admin' and current_user.kurum_id == 1
    
    if is_system_admin:
        # Sistem yöneticisi: Tüm veriler (sadece aktif kayıtlar)
        kurumlar = Kurum.query.filter_by(silindi=False).all()
        kullanicilar = User.query.filter_by(silindi=False).all()
        surecler = Surec.query.filter_by(silindi=False).all()
    else:
        # Kurum yöneticisi: Sadece kendi kurumunun verileri (sadece aktif kayıtlar)
        kurumlar = Kurum.query.filter_by(id=current_user.kurum_id, silindi=False).all()
        kullanicilar = User.query.filter_by(kurum_id=current_user.kurum_id, silindi=False).all()
        surecler = Surec.query.filter_by(kurum_id=current_user.kurum_id, silindi=False).all()
    
    current_app.logger.info(f'Admin panel loading for {current_user.username} (sistem_admin={is_system_admin}): {len(kullanicilar)} users, {len(kurumlar)} organizations')
    
    # Geri bildirim istatistikleri (admin panel için)
    from app.models.legacy_bridge import Feedback
    is_system_admin_for_feedback = current_user.sistem_rol == 'admin' and current_user.kurum_id == 1
    if is_system_admin_for_feedback:
        pending_count = Feedback.query.filter_by(status='Bekliyor').count()
    else:
        user_ids_feedback = [u.id for u in User.query.filter_by(kurum_id=current_user.kurum_id).all()]
        pending_count = Feedback.query.filter(Feedback.user_id.in_(user_ids_feedback), Feedback.status == 'Bekliyor').count() if user_ids_feedback else 0
    
    return render_template('admin_panel.html',
                         kurumlar=kurumlar,
                         kullanicilar=kullanicilar,
                         pending_count=pending_count,
                         surecler=surecler,
                         is_system_admin=is_system_admin,
                         total_users=User.query.count(),
                         total_strategies=AnaStrateji.query.count())


# ─────────────────────────────────────────────────────────────────────────────
# DALGA 1.6 (2026-06-16): Ölü legacy admin upload route'ları kaldırıldı:
#   /admin/download-user-template, /admin/upload-users-excel,
#   /admin/upload-profile-photo, /admin/upload-logo
# Tetikleyici UI (templates/admin_panel.html) render-ölüydü: GET /admin-panel
# middleware (legacy_sunset) ile 301 → app_bp.yonetim_paneli (runtime teyit edildi).
# Aktif ui/templates'de referans yok. Modern karşılıklar canlı: micro/modules/admin
# (/admin/users/sample-excel, /admin/users/bulk-import, /admin/tenants/logo/<id>).
# Profil-foto admin-upload'ın modern karşılığı henüz yok ama legacy de erişilemezdi.
# ─────────────────────────────────────────────────────────────────────────────


@main_bp.route('/kurum-yonetim')
@login_required
@legacy_html_to_platform
def kurum_yonetim_page():
    """Kurum Yönetimi sayfası"""
    # Kurum yöneticileri için
    if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
        flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Basit bir kurum yönetimi sayfası
        kurum = Kurum.query.get(current_user.kurum_id)
        return render_template('base.html', 
                             page_title='Kurum Yönetimi',
                             content=f'<div class="container mt-4"><h2>Kurum Yönetimi</h2><p>Kurum: {kurum.kisa_ad if kurum else "Bilinmiyor"}</p><p>Kurum yönetimi sayfası yakında eklenecek.</p></div>')
    except Exception as e:
        import traceback
        current_app.logger.error(f'Kurum yönetimi sayfası hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        return f"Sayfa yüklenirken hata oluştu: {str(e)}", 500


@main_bp.route('/admin/fix-bsc-schema')
@login_required
def fix_bsc_schema():
    """BSC kolonlarını ve bağlantı tablosunu veri kaybı olmadan ekler."""
    if current_user.sistem_rol != 'admin':
        flash('Bu işlem için yetkiniz yok.', 'danger')
        return redirect(url_for('main.dashboard'))

    try:
        from sqlalchemy import text

        with db.engine.connect() as conn:
            table_info = conn.execute(text("PRAGMA table_info('ana_strateji')")).fetchall()
            existing_columns = {row[1] for row in table_info}

            if 'perspective' not in existing_columns:
                conn.execute(text("ALTER TABLE ana_strateji ADD COLUMN perspective VARCHAR(20)"))
            if 'bsc_code' not in existing_columns:
                conn.execute(text("ALTER TABLE ana_strateji ADD COLUMN bsc_code VARCHAR(10)"))
            conn.commit()

        with db.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS strategy_map_link (
                    id INTEGER PRIMARY KEY,
                    source_id INTEGER NOT NULL,
                    target_id INTEGER NOT NULL,
                    connection_type VARCHAR(30) NOT NULL DEFAULT 'CAUSE_EFFECT',
                    UNIQUE(source_id, target_id),
                    FOREIGN KEY(source_id) REFERENCES ana_strateji(id),
                    FOREIGN KEY(target_id) REFERENCES ana_strateji(id)
                )
            """))
            conn.commit()

        return "BSC şeması güncellendi. <a href='/bsc/map/%d'>BSC Haritası</a>" % current_user.kurum_id
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'BSC şema güncelleme hatası: {e}', exc_info=True)
        return f"Hata: {str(e)}", 500

# Proje yönetimi görünümleri: Kanban, Takvim, Gantt
@main_bp.route('/projeler/<int:project_id>/kanban')
@login_required
def project_kanban(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        if project.kurum_id != current_user.kurum_id:
            flash('Bu projeye erişim yetkiniz yok.', 'danger')
            return redirect(url_for('main.dashboard'))
        return redirect(url_for('app_bp.project_view_kanban', project_id=project_id))
    except Exception as e:
        current_app.logger.error(f'Kanban sayfası hatası: {e}')
        return f'Hata: {str(e)}', 500


@main_bp.route('/projeler/<int:project_id>/takvim')
@login_required
def project_calendar(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        if project.kurum_id != current_user.kurum_id:
            flash('Bu projeye erişim yetkiniz yok.', 'danger')
            return redirect(url_for('main.dashboard'))
        return redirect(url_for('app_bp.project_view_calendar', project_id=project_id))
    except Exception as e:
        current_app.logger.error(f'Takvim sayfası hatası: {e}')
        return f'Hata: {str(e)}', 500


@main_bp.route('/projeler/<int:project_id>/gantt')
@login_required
def project_gantt(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        if project.kurum_id != current_user.kurum_id:
            flash('Bu projeye erişim yetkiniz yok.', 'danger')
            return redirect(url_for('main.dashboard'))
        return redirect(url_for('app_bp.project_view_gantt', project_id=project_id))
    except Exception as e:
        current_app.logger.error(f'Gantt sayfası hatası: {e}')
        return f'Hata: {str(e)}', 500


@main_bp.route('/projeler/<int:project_id>/cpm')
@login_required
def project_cpm(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        if project.kurum_id != current_user.kurum_id:
            flash('Bu projeye erişim yetkiniz yok.', 'danger')
            return redirect(url_for('main.dashboard'))
        return render_template('projects/cpm.html', project=project)
    except Exception as e:
        current_app.logger.error(f'CPM sayfası hatası: {e}')
        return f'Hata: {str(e)}', 500


@main_bp.route('/projeler/<int:project_id>/raid')
@login_required
def project_raid(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        if project.kurum_id != current_user.kurum_id:
            flash('Bu projeye erişim yetkiniz yok.', 'danger')
            return redirect(url_for('main.dashboard'))
        return redirect(url_for('app_bp.project_view_raid', project_id=project_id))
    except Exception as e:
        current_app.logger.error(f'RAID sayfası hatası: {e}')
        return f'Hata: {str(e)}', 500


@main_bp.route('/projeler/<int:project_id>/baseline')
@login_required
def project_baseline(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        if project.kurum_id != current_user.kurum_id:
            flash('Bu projeye erişim yetkiniz yok.', 'danger')
            return redirect(url_for('main.dashboard'))
        return render_template('projects/baseline.html', project=project)
    except Exception as e:
        current_app.logger.error(f'Baseline sayfası hatası: {e}')
        return f'Hata: {str(e)}', 500


@main_bp.route('/projeler/<int:project_id>/kapasite')
@login_required
def project_capacity(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        if project.kurum_id != current_user.kurum_id:
            flash('Bu projeye erişim yetkiniz yok.', 'danger')
            return redirect(url_for('main.dashboard'))
        return render_template('projects/capacity.html', project=project)
    except Exception as e:
        current_app.logger.error(f'Kapasite sayfası hatası: {e}')
        return f'Hata: {str(e)}', 500


@main_bp.route('/projeler/<int:project_id>/integrations')
@login_required
def project_integrations(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        if project.kurum_id != current_user.kurum_id:
            flash('Bu projeye erişim yetkiniz yok.', 'danger')
            return redirect(url_for('main.dashboard'))
        return render_template('projects/integrations.html', project=project)
    except Exception as e:
        current_app.logger.error(f'Integrations sayfası hatası: {e}')
        return f'Hata: {str(e)}', 500


@main_bp.route('/projeler/<int:project_id>/kurallar')
@login_required
def project_rules(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        if project.kurum_id != current_user.kurum_id:
            flash('Bu projeye erişim yetkiniz yok.', 'danger')
            return redirect(url_for('main.dashboard'))
        return render_template('projects/rules.html', project=project)
    except Exception as e:
        current_app.logger.error(f'Kurallar sayfası hatası: {e}')
        return f'Hata: {str(e)}', 500


@main_bp.route('/projeler/<int:project_id>/sla')
@login_required
def project_sla(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        if project.kurum_id != current_user.kurum_id:
            flash('Bu projeye erişim yetkiniz yok.', 'danger')
            return redirect(url_for('main.dashboard'))
        return render_template('projects/sla.html', project=project)
    except Exception as e:
        current_app.logger.error(f'SLA sayfası hatası: {e}')
        return f'Hata: {str(e)}', 500


@main_bp.route('/projeler/<int:project_id>/tekrarlayan')
@login_required
def project_recurring(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        if project.kurum_id != current_user.kurum_id:
            flash('Bu projeye erişim yetkiniz yok.', 'danger')
            return redirect(url_for('main.dashboard'))
        return render_template('projects/recurring.html', project=project)
    except Exception as e:
        current_app.logger.error(f'Recurring sayfası hatası: {e}')
        return f'Hata: {str(e)}', 500


@main_bp.route('/projeler/<int:project_id>/calisma-gunleri')
@login_required
def project_workdays(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        if project.kurum_id != current_user.kurum_id:
            flash('Bu projeye erişim yetkiniz yok.', 'danger')
            return redirect(url_for('main.dashboard'))
        return render_template('projects/workdays.html', project=project)
    except Exception as e:
        current_app.logger.error(f'Çalışma günleri sayfası hatası: {e}')
        return f'Hata: {str(e)}', 500


@main_bp.route('/projeler/<int:project_id>/bagimlilik-matrisi')
@login_required
def project_dependency_matrix(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        if project.kurum_id != current_user.kurum_id:
            flash('Bu projeye erişim yetkiniz yok.', 'danger')
            return redirect(url_for('main.dashboard'))
        return render_template('projects/dependency_matrix.html', project=project)
    except Exception as e:
        current_app.logger.error(f'Bağımlılık matrisi sayfası hatası: {e}')
        return f'Hata: {str(e)}', 500


@main_bp.route('/portfoy-ozeti')
@login_required
def portfolio_summary():
    try:
        return render_template('projects/portfolio.html')
    except Exception as e:
        current_app.logger.error(f'Portföy özeti sayfası hatası: {e}')
        return f'Hata: {str(e)}', 500


@main_bp.route('/stratejik-planlama-akisi')
@login_required
def stratejik_planlama_akisi():
    """SP Akış Diyagramı sayfası"""
    try:
        kurum = current_user.kurum
        
        # Kurumun değerlerini getir
        degerler = Deger.query.filter_by(kurum_id=kurum.id).all()
        
        # Kurumun etik kurallarını getir
        etik_kurallari = EtikKural.query.filter_by(kurum_id=kurum.id).all()
        
        # Kurumun kalite politikalarını getir
        kalite_politikalari = KalitePolitikasi.query.filter_by(kurum_id=kurum.id).all()
        
        # Kurumun amaç ve vizyon bilgileri (kurum modelinden)
        amac = kurum.amac
        vizyon = kurum.vizyon
        
        # Kurumun ana stratejilerini getir (alt stratejileriyle birlikte)
        ana_stratejiler = AnaStrateji.query.filter_by(kurum_id=kurum.id).all()
        
        # Her ana strateji için alt stratejileri yükle
        for ana_str in ana_stratejiler:
            ana_str.alt_stratejiler = AltStrateji.query.filter_by(ana_strateji_id=ana_str.id).all()
        
        # Kurumun süreçlerini getir (performans göstergeleriyle birlikte)
        surecler = Surec.query.filter_by(kurum_id=kurum.id, silindi=False).all()
        
        # Her süreç için performans göstergelerini yükle
        for surec in surecler:
            surec.performans_gostergeleri = SurecPerformansGostergesi.query.filter_by(surec_id=surec.id).all()

        # --- Skor Hesapları (0-100 normalize) ---
        def _normalize_score(raw_value: int, max_value: int) -> int:
            if not max_value or max_value <= 0:
                return 0
            try:
                val = int(round((float(raw_value) / float(max_value)) * 100.0))
            except Exception:
                return 0
            return max(0, min(100, val))

        # Strateji-Süreç ilişki skorları (A=9, B=3)
        try:
            sub_strategies = AltStrateji.query.join(AnaStrateji).filter(
                AnaStrateji.kurum_id == kurum.id
            ).all()

            matrix_relations = StrategyProcessMatrix.query.join(AltStrateji).join(AnaStrateji).filter(
                AnaStrateji.kurum_id == kurum.id
            ).all()

            relations_map = {}
            for rel in matrix_relations:
                relations_map[(rel.sub_strategy_id, rel.process_id)] = int(rel.relationship_score or 0)

            # Süreç skorları: tüm alt strateji ilişkilerinin toplamı
            process_max_raw = 9 * len(sub_strategies)
            process_scores_norm = {}
            for proc in surecler:
                raw_total = 0
                for sub in sub_strategies:
                    raw_total += relations_map.get((sub.id, proc.id), 0)
                process_scores_norm[proc.id] = _normalize_score(raw_total, process_max_raw)

            # Alt strateji skorları: tüm süreç ilişkilerinin toplamı
            sub_max_raw = 9 * len(surecler)
            sub_scores_norm = {}
            sub_scores_raw = {}
            for sub in sub_strategies:
                raw_total = 0
                for proc in surecler:
                    raw_total += relations_map.get((sub.id, proc.id), 0)
                sub_scores_raw[sub.id] = raw_total
                sub_scores_norm[sub.id] = _normalize_score(raw_total, sub_max_raw)

            # Ana strateji skorları: alt stratejilerinin toplamı
            main_scores_norm = {}
            for main in ana_stratejiler:
                if not getattr(main, 'alt_stratejiler', None):
                    main_scores_norm[main.id] = 0
                    continue
                raw_total = sum(sub_scores_raw.get(sub.id, 0) for sub in (main.alt_stratejiler or []))
                main_max_raw = 9 * len(surecler) * len(main.alt_stratejiler)
                main_scores_norm[main.id] = _normalize_score(raw_total, main_max_raw)

            # KPI (PG) skorları: agirlikli_basari_puani (maks ~5.0) -> 0-100
            kpi_scores_norm = {}
            for proc in surecler:
                for kpi in (getattr(proc, 'performans_gostergeleri', None) or []):
                    if kpi.agirlikli_basari_puani is None:
                        continue
                    try:
                        kpi_scores_norm[kpi.id] = _normalize_score(float(kpi.agirlikli_basari_puani), 5.0)  # type: ignore[arg-type]
                    except Exception:
                        continue
        except Exception as _score_err:
            current_app.logger.warning(f'SP Akış skor hesaplama atlandı: {_score_err}')
            process_scores_norm = {}
            sub_scores_norm = {}
            main_scores_norm = {}
            kpi_scores_norm = {}
        
        return render_template('stratejik_planlama_akisi.html', 
                             kurum=kurum,
                             degerler=degerler,
                             etik_kurallari=etik_kurallari,
                             kalite_politikalari=kalite_politikalari,
                             amac=amac,
                             vizyon=vizyon,
                             ana_stratejiler=ana_stratejiler,
                             surecler=surecler,
                             process_scores_norm=process_scores_norm,
                             sub_scores_norm=sub_scores_norm,
                             main_scores_norm=main_scores_norm,
                             kpi_scores_norm=kpi_scores_norm)
    except Exception as e:
        import traceback
        current_app.logger.error(f'SP Akış Diyagramı sayfası render hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        return f"Template render hatası: {str(e)}", 500


@main_bp.route('/stratejik-planlama-akisi/dinamik')
@login_required
@legacy_html_to_platform
def stratejik_planlama_akisi_dinamik():
    """Dinamik SP Akış (graf) sayfası"""
    try:
        kurum = current_user.kurum
        return render_template('stratejik_planlama_akisi_dinamik.html', kurum=kurum)
    except Exception as e:
        current_app.logger.error(f'Dinamik SP Akış sayfası hatası: {e}')
        flash('Dinamik SP Akış sayfası yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.stratejik_planlama_akisi'))


@main_bp.route('/api/strategic-planning/graph')
@login_required
def api_strategic_planning_graph():
    """Dinamik SP akışı için graf verisini döndürür (nodes/edges + skorlar)."""
    try:
        kurum = current_user.kurum

        def _normalize_score(raw_value, max_value) -> int:
            try:
                if not max_value or float(max_value) <= 0:
                    return 0
                val = int(round((float(raw_value) / float(max_value)) * 100.0))
                return max(0, min(100, val))
            except Exception:
                return 0

        main_strategies = AnaStrateji.query.filter_by(kurum_id=kurum.id).order_by(AnaStrateji.code, AnaStrateji.ad).all()
        sub_strategies = AltStrateji.query.join(AnaStrateji).filter(
            AnaStrateji.kurum_id == kurum.id
        ).order_by(AltStrateji.code, AltStrateji.ad).all()
        processes = Surec.query.filter_by(kurum_id=kurum.id, silindi=False).order_by(Surec.weight.desc(), Surec.code, Surec.ad).all()
        projects = Project.query.filter_by(kurum_id=kurum.id, is_archived=False).order_by(Project.name).all()
        kpis = SurecPerformansGostergesi.query.join(Surec).filter(
            Surec.kurum_id == kurum.id
        ).order_by(Surec.code, SurecPerformansGostergesi.kodu, SurecPerformansGostergesi.ad).all()

        matrix_relations = StrategyProcessMatrix.query.join(AltStrateji).join(AnaStrateji).filter(
            AnaStrateji.kurum_id == kurum.id
        ).all()

        relations_map = {}
        for rel in matrix_relations:
            relations_map[(rel.sub_strategy_id, rel.process_id)] = int(rel.relationship_score or 0)

        # Totals
        process_max_raw = 9 * len(sub_strategies)
        process_totals_raw = {}
        process_scores_norm = {}
        for proc in processes:
            raw_total = 0
            for sub in sub_strategies:
                raw_total += relations_map.get((sub.id, proc.id), 0)
            process_totals_raw[proc.id] = raw_total
            process_scores_norm[proc.id] = _normalize_score(raw_total, process_max_raw)

        sub_max_raw = 9 * len(processes)
        sub_totals_raw = {}
        sub_scores_norm = {}
        for sub in sub_strategies:
            raw_total = 0
            for proc in processes:
                raw_total += relations_map.get((sub.id, proc.id), 0)
            sub_totals_raw[sub.id] = raw_total
            sub_scores_norm[sub.id] = _normalize_score(raw_total, sub_max_raw)

        main_scores_norm = {}
        # main->subs mapping
        subs_by_main = {}
        for sub in sub_strategies:
            subs_by_main.setdefault(sub.ana_strateji_id, []).append(sub)
        for main in main_strategies:
            subs = subs_by_main.get(main.id, [])
            if not subs:
                main_scores_norm[main.id] = 0
                continue
            raw_total = sum(sub_totals_raw.get(s.id, 0) for s in subs)
            main_max_raw = 9 * len(processes) * len(subs)
            main_scores_norm[main.id] = _normalize_score(raw_total, main_max_raw)

        # KPI score: agirlikli_basari_puani (0-5) => 0-100
        kpi_scores_norm = {}
        for kpi in kpis:
            if kpi.agirlikli_basari_puani is None:
                continue
            kpi_scores_norm[kpi.id] = _normalize_score(kpi.agirlikli_basari_puani, 5.0)

        # Nodes / edges for vis-network
        nodes = []
        edges = []
        kurum_panel_url = url_for('main.kurum_paneli')

        def _label_with_score(prefix: str, name: str, score: int) -> str:
            base = f"{prefix} {name}".strip()
            return f"{base}\n({score}%)"

        # Vision node (top level)
        if kurum.vizyon:
            nodes.append({
                'id': 'vision',
                'group': 'vision',
                'shape': 'box',
                'color': '#8b5cf6',
                'label': f"VİZYON\n{kurum.vizyon[:80]}...",
                'title': f"<b>Vizyon</b><br/>{kurum.vizyon}",
                'url': kurum_panel_url,
                'level': 0,
                'font': {'size': 18, 'bold': True}
            })

        # Main strategy nodes
        for main in main_strategies:
            score = main_scores_norm.get(main.id, 0)
            code = (main.code or '').strip()
            prefix = f"{code}" if code else "ANA"
            nodes.append({
                'id': f"main_{main.id}",
                'group': 'main_strategy',
                'shape': 'box',
                'color': '#f97316',
                'label': _label_with_score(prefix, main.ad, score),
                'title': f"<b>{main.ad}</b><br/>Skor: <b>{score}%</b>",
                'url': kurum_panel_url,
                'level': 1,
                'score': score,
            })

        # Sub strategy nodes
        for sub in sub_strategies:
            score = sub_scores_norm.get(sub.id, 0)
            code = (sub.code or '').strip()
            prefix = f"{code}" if code else "ALT"
            nodes.append({
                'id': f"sub_{sub.id}",
                'group': 'sub_strategy',
                'shape': 'box',
                'color': '#0891b2',
                'label': _label_with_score(prefix, sub.ad, score),
                'title': f"<b>{sub.ad}</b><br/>Skor: <b>{score}%</b>",
                'url': kurum_panel_url,
                'level': 2,
                'score': score,
            })
            # main -> sub edge
            edges.append({
                'from': f"main_{sub.ana_strateji_id}",
                'to': f"sub_{sub.id}",
                'arrows': 'to',
                'color': {'color': '#94a3b8'},
                'width': 1,
                'dashes': True,
            })

        # Vision to main strategies edges
        if kurum.vizyon:
            for main in main_strategies:
                edges.append({
                    'from': 'vision',
                    'to': f"main_{main.id}",
                    'arrows': 'to',
                    'color': {'color': '#c084fc'},
                    'width': 3,
                    'dashes': False,
                })

        # Process nodes
        for proc in processes:
            score = process_scores_norm.get(proc.id, 0)
            code = (proc.code or '').strip()
            prefix = f"{code}" if code else "SR"
            nodes.append({
                'id': f"proc_{proc.id}",
                'group': 'process',
                'shape': 'ellipse',
                'color': '#059669',
                'label': _label_with_score(prefix, proc.ad, score),
                'title': f"<b>{proc.ad}</b><br/>Skor: <b>{score}%</b>",
                'url': kurum_panel_url,
                'level': 3,
                'score': score,
            })

        # Sub -> Process edges (A+B)
        for sub in sub_strategies:
            for proc in processes:
                rel_score = relations_map.get((sub.id, proc.id), 0)
                if rel_score not in (3, 9):
                    continue
                label = 'A' if rel_score == 9 else 'B'
                edges.append({
                    'from': f"sub_{sub.id}",
                    'to': f"proc_{proc.id}",
                    'arrows': 'to',
                    'label': f"{label}",
                    'title': f"İlişki Skoru: {rel_score} ({label})",
                    'color': {'color': '#16a34a' if rel_score == 9 else '#f59e0b'},
                    'width': 3 if rel_score == 9 else 1,
                })

        # KPI nodes + Process -> KPI edges
        for kpi in kpis:
            score = kpi_scores_norm.get(kpi.id)
            score_txt = f" ({score}%)" if score is not None else ""
            label = (kpi.kodu or '').strip()
            if label:
                label = f"{label}: {kpi.ad}{score_txt}"
            else:
                label = f"PG: {kpi.ad}{score_txt}"
            nodes.append({
                'id': f"kpi_{kpi.id}",
                'group': 'kpi',
                'shape': 'box',
                'color': '#7c3aed',
                'label': label,
                'title': f"<b>{kpi.ad}</b><br/>Ağırlıklı Puan: <b>{(kpi.agirlikli_basari_puani if kpi.agirlikli_basari_puani is not None else '-')}</b><br/>Skor: <b>{(str(score) + '%' if score is not None else '-')}</b>",
                'url': kurum_panel_url,
                'level': 4,
                'score': score if score is not None else None,
            })
            edges.append({
                'from': f"proc_{kpi.surec_id}",
                'to': f"kpi_{kpi.id}",
                'arrows': 'to',
                'color': {'color': '#c4b5fd'},
                'width': 1,
            })

        # Project nodes + Project -> Process edges
        for project in projects:
            related_processes = list(project.related_processes or [])
            project_raw = sum(process_totals_raw.get(p.id, 0) for p in related_processes)
            project_max = 9 * len(sub_strategies) * len(related_processes)
            project_score = _normalize_score(project_raw, project_max)
            nodes.append({
                'id': f"proj_{project.id}",
                'group': 'project',
                'shape': 'diamond',
                'color': '#f97316',
                'label': _label_with_score('PRJ', project.name, project_score),
                'title': f"<b>{project.name}</b><br/>Skor: <b>{project_score}%</b>",
                'url': kurum_panel_url,
                'level': 4,
                'score': project_score,
            })

            for proc in related_processes:
                edges.append({
                    'from': f"proj_{project.id}",
                    'to': f"proc_{proc.id}",
                    'arrows': 'to',
                    'color': {'color': '#fb923c'},
                    'width': 2,
                })

            # Derived: Project -> SubStrategy edges (only if >0)
            if related_processes:
                max_rel = 9 * len(related_processes)
                for sub in sub_strategies:
                    raw_rel = 0
                    for proc in related_processes:
                        raw_rel += relations_map.get((sub.id, proc.id), 0)
                    if raw_rel <= 0:
                        continue
                    rel_norm = _normalize_score(raw_rel, max_rel)
                    edges.append({
                        'from': f"proj_{project.id}",
                        'to': f"sub_{sub.id}",
                        'arrows': 'to',
                        'label': f"{rel_norm}%",
                        'title': f"Projeden Alt Stratejiye Türetilmiş Etki: {rel_norm}%",
                        'color': {'color': '#a855f7'},
                        'width': 1,
                        'dashes': True,
                    })

        return jsonify({
            'success': True,
            'nodes': nodes,
            'edges': edges,
            'meta': {
                'kurum_id': kurum.id,
                'main_strategies': len(main_strategies),
                'sub_strategies': len(sub_strategies),
                'processes': len(processes),
                'projects': len(projects),
                'kpis': len(kpis),
            }
        })
    except Exception as e:
        import traceback
        current_app.logger.error(f'SP graph API hatası: {e}')
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': str(e)}), 500


@main_bp.route('/api/ai/insights')
@login_required
def api_ai_insights():
    """AI Insight'ları getir"""
    try:
        from services.ai_service import AIService
        insights = AIService.get_insights_for_user(current_user.id, current_user.kurum_id)
        return jsonify({
            'success': True,
            'insights': insights
        })
    except Exception as e:
        current_app.logger.error(f'AI insights hatası: {e}')
        return jsonify({
            'success': False,
            'message': 'Insight\'lar yüklenemedi',
            'insights': []
        }), 500


@main_bp.route('/api/ai/ask', methods=['POST'])
@login_required
def api_ai_ask():
    """AI'ya soru sor"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'message': 'Lütfen bir soru girin'
            }), 400
        
        from services.ai_service import AIService
        answer = AIService.ask_question(current_user.id, question)
        
        return jsonify({
            'success': True,
            'answer': answer['answer'],
            'suggestions': answer.get('suggestions', [])
        })
    except Exception as e:
        current_app.logger.error(f'AI ask hatası: {e}')
        return jsonify({
            'success': False,
            'message': 'Soru işlenemedi'
        }), 500

        return jsonify({
            'success': False,
            'message': 'Soru işlenemedi'
        }), 500

# ==========================================
# KURUM PANELİ CRUD İŞLEMLERİ
# ==========================================

# --- Ana Strateji ---
