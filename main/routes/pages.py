# -*- coding: utf-8 -*-
# Otomatik bölüm — `python scripts/dev/split_main_routes.py`
from main.routes._common import *  # noqa: F401,F403
from main.routes import main_bp
from main.deprecated import legacy_html_to_platform
from app.utils.error_handlers import json_error  # S6


# 2026-06-17: /dashboard kaldırıldı — redirect-ölü (GET 301 → /masaustu).
# safe_urls.py fallback: main.dashboard → app_bp.masaustu.




@main_bp.route('/debug/surec-data')
@login_required
def debug_surec_data():
    """Debug endpoint - kullanıcının süreçlerini ve PG sayılarını göster"""
    try:
        current_app.logger.info(f"=== DEBUG SÜREÇ DATA ===")
        current_app.logger.info(f"User: {current_user.id}, Role: {current_user.sistem_rol}, Kurum: {current_user.kurum_id}")
        
        # Kullanıcının süreçlerini belirle
        if current_user.sistem_rol == 'admin':
            surecler = Surec.query.filter_by(silindi=False).all()
        elif current_user.sistem_rol in ['kurum_yoneticisi', 'ust_yonetim']:
            surecler = Surec.query.filter_by(kurum_id=current_user.kurum_id, silindi=False).all()
        else:
            # Normal kullanıcı için lider/üye kontrolü
            lider_surec_ids = db.session.query(surec_liderleri.c.surec_id).filter(
                surec_liderleri.c.user_id == current_user.id
            ).all()
            lider_surec_ids = [sid[0] for sid in lider_surec_ids]
            
            uye_surec_ids = db.session.query(surec_uyeleri.c.surec_id).filter(
                surec_uyeleri.c.user_id == current_user.id
            ).all()
            uye_surec_ids = [sid[0] for sid in uye_surec_ids]
            
            tum_surec_ids = list(set(lider_surec_ids + uye_surec_ids))
            
            if tum_surec_ids:
                surecler = Surec.query.filter(Surec.id.in_(tum_surec_ids)).all()
            else:
                surecler = []
        
        # Her süreç için PG ve faaliyet sayısını topla
        surec_listesi = []
        for s in surecler:
            pg_count = SurecPerformansGostergesi.query.filter_by(surec_id=s.id).count()
            faaliyet_count = SurecFaaliyet.query.filter_by(surec_id=s.id).count()
            
            pg_listesi = []
            for pg in SurecPerformansGostergesi.query.filter_by(surec_id=s.id).all():
                pg_listesi.append({
                    'id': pg.id,
                    'ad': pg.ad,
                    'kodu': pg.kodu if hasattr(pg, 'kodu') else f'PG-{pg.id}'
                })
            
            faaliyet_listesi = []
            for f in SurecFaaliyet.query.filter_by(surec_id=s.id).all():
                faaliyet_listesi.append({
                    'id': f.id,
                    'ad': f.ad
                })
            
            surec_listesi.append({
                'id': s.id,
                'ad': s.ad,
                'pg_sayisi': pg_count,
                'faaliyet_sayisi': faaliyet_count,
                'pg_listesi': pg_listesi,
                'faaliyet_listesi': faaliyet_listesi
            })
        
        return jsonify({
            'success': True,
            'user_info': {
                'id': current_user.id,
                'username': current_user.email,
                'sistem_rol': current_user.sistem_rol,
                'kurum_id': current_user.kurum_id
            },
            'toplam_surec': len(surecler),
            'surecler': surec_listesi
        })
    except Exception as e:
        import traceback
        current_app.logger.error(f'Debug surec data hatası: {e}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        return json_error(e, "[debug_surec_data]", 500)


@main_bp.route('/api/kullanici/sureclerim')
@login_required
def api_kullanici_surecleri():
    """Kullanıcının üye/lider olduğu süreçleri getir - Kurum yöneticileri tüm süreçleri görür"""
    try:
        current_app.logger.info(f"=== SÜREÇLERİM API ÇAĞRILDI ===")
        current_app.logger.info(f"User: {current_user.id}, Role: {current_user.sistem_rol}, Kurum: {current_user.kurum_id}")
        
        # Kurum yöneticileri kendi kurumlarındaki TÜM süreçleri görür; admin tüm kurumları görür
        if current_user.sistem_rol in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            if current_user.sistem_rol == 'admin':
                current_app.logger.info(f"Admin - tüm süreçler getiriliyor")
                surecler = Surec.query.filter_by(silindi=False).all()
            else:
                current_app.logger.info(f"Kurum yöneticisi - kurum süreçleri getiriliyor")
                surecler = Surec.query.filter_by(kurum_id=current_user.kurum_id, silindi=False).all()
            
            return jsonify({
                'success': True,
                'surecler': [{
                    'id': s.id,
                    'ad': s.ad,
                    'dokuman_no': s.dokuman_no or '-',
                    'rev_no': s.rev_no or '-',
                    'is_lider': False,  # Kurum yöneticisi için özel durum
                    'is_uye': False     # Kurum yöneticisi için özel durum
                } for s in surecler],
                'user_role': current_user.sistem_rol  # Kullanıcı rolünü ekle
            })
        
        # Normal kullanıcılar için lider/üye kontrolü
        # Kullanıcının lider olduğu süreçler
        lider_surec_ids = db.session.query(surec_liderleri.c.surec_id).filter(
            surec_liderleri.c.user_id == current_user.id
        ).all()
        lider_surec_ids = [sid[0] for sid in lider_surec_ids]
        
        # Kullanıcının üye olduğu süreçler
        uye_surec_ids = db.session.query(surec_uyeleri.c.surec_id).filter(
            surec_uyeleri.c.user_id == current_user.id
        ).all()
        uye_surec_ids = [sid[0] for sid in uye_surec_ids]
        
        # Tüm süreç ID'leri
        tum_surec_ids = list(set(lider_surec_ids + uye_surec_ids))
        
        current_app.logger.info(f'Kullanıcı {current_user.id} ({current_user.email}) - Lider: {lider_surec_ids}, Üye: {uye_surec_ids}')
        
        # Süreçleri getir (kurum izolasyonu: admin dışı sadece kendi kurumu)
        if tum_surec_ids:
            surecler = Surec.query.filter(
                Surec.id.in_(tum_surec_ids),
                Surec.kurum_id == current_user.kurum_id,
                Surec.silindi == False
            ).all()
        else:
            surecler = []
        
        current_app.logger.info(f'Bulunan süreç sayısı: {len(surecler)}')
        
        return jsonify({
            'success': True,
            'surecler': [{
                'id': s.id,
                'ad': s.ad,
                'dokuman_no': s.dokuman_no or '-',
                'rev_no': s.rev_no or '-',
                'is_lider': s.id in lider_surec_ids,
                'is_uye': s.id in uye_surec_ids
            } for s in surecler],
            'user_role': current_user.sistem_rol  # Kullanıcı rolünü ekle
        })
    except Exception as e:
        current_app.logger.error(f'Süreçler getirilemedi: {e}')
        return json_error(e, "[api_kullanici_surecleri]", 500)


@main_bp.route('/surec/<int:surec_id>/performans-gostergesi/add', methods=['POST'])
@login_required
@csrf.exempt
def surec_performans_gostergesi_add(surec_id):
    """Süreç için yeni performans göstergesi ekle"""
    try:
        # JSON verisini al
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Geçersiz JSON verisi'}), 400
        
        current_app.logger.info(f'Süreç {surec_id} için performans göstergesi ekleme isteği: {data}')
        
        # Zorunlu alan kontrolü
        if not data.get('ad') or not data.get('ad').strip():
            return jsonify({'success': False, 'message': 'Performans göstergesi adı zorunludur'}), 400
        
        # Yetki kontrolü
        surec = Surec.query.get(surec_id)
        if not surec:
            return jsonify({'success': False, 'message': 'Süreç bulunamadı'}), 404
        
        # Kurum izolasyonu: admin dışı sadece kendi kurumu
        if current_user.sistem_rol != 'admin' and surec.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403

        # Yazma yetkisi: sadece yönetim rolleri
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403
        
        # Tarih dönüştürme
        baslangic_tarihi = None
        bitis_tarihi = None
        try:
            if data.get('baslangic_tarihi'):
                baslangic_tarihi = datetime.strptime(data.get('baslangic_tarihi'), '%Y-%m-%d').date()
            if data.get('bitis_tarihi'):
                bitis_tarihi = datetime.strptime(data.get('bitis_tarihi'), '%Y-%m-%d').date()
        except ValueError as e:
            return jsonify({'success': False, 'message': f'Geçersiz tarih formatı: {str(e)}'}), 400
        
        # Alt strateji ID kontrolü
        alt_strateji_id = None
        if data.get('alt_strateji_id'):
            try:
                alt_strateji_id = int(data.get('alt_strateji_id'))
                # Alt stratejinin bu sürece ait olduğunu kontrol et
                alt_strateji = AltStrateji.query.get(alt_strateji_id)
                if alt_strateji and alt_strateji not in surec.alt_stratejiler:
                    return jsonify({'success': False, 'message': 'Seçilen alt strateji bu sürece ait değil'}), 400
            except (ValueError, TypeError):
                alt_strateji_id = None
        
        # Skor motoru ağırlığı (0-100, opsiyonel)
        weight = None
        if data.get('weight') is not None and data.get('weight') != '':
            try:
                w = float(data.get('weight'))
                if 0 <= w <= 100:
                    weight = w
            except (ValueError, TypeError):
                pass

        # Yeni performans göstergesi oluştur
        yeni_pg = SurecPerformansGostergesi(
            surec_id=surec_id,
            ad=data.get('ad', '').strip(),
            aciklama=data.get('aciklama', '').strip() if data.get('aciklama') else None,
            hedef_deger=data.get('hedef_deger', '').strip() if data.get('hedef_deger') else None,
            olcum_birimi=data.get('olcum_birimi', '').strip() if data.get('olcum_birimi') else None,
            periyot=data.get('periyot', 'Aylik'),
            veri_toplama_yontemi=data.get('veri_toplama_yontemi', 'Ortalama'),
            baslangic_tarihi=baslangic_tarihi,
            bitis_tarihi=bitis_tarihi,
            direction=data.get('direction', 'Increasing'),
            basari_puani_araliklari=data.get('basari_puani_araliklari') if data.get('basari_puani_araliklari') else None,
            alt_strateji_id=alt_strateji_id,
            weight=weight
        )
        
        db.session.add(yeni_pg)
        db.session.commit()
        
        current_app.logger.info(f'Süreç {surec_id} için performans göstergesi eklendi: {yeni_pg.id}')
        
        return jsonify({
            'success': True,
            'message': 'Performans göstergesi başarıyla eklendi',
            'pg_id': yeni_pg.id
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Performans göstergesi ekleme hatası: {e}')
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Hata: {str(e)}'}), 500


@main_bp.route('/surec/<int:surec_id>/performans-gostergesi/<int:pg_id>', methods=['GET'])
@login_required
@csrf.exempt
def surec_performans_gostergesi_get(surec_id, pg_id):
    """Süreç için performans göstergesi bilgilerini getir"""
    try:
        # Yetki kontrolü
        surec = Surec.query.get(surec_id)
        if not surec:
            return jsonify({'success': False, 'message': 'Süreç bulunamadı'}), 404
        
        # Kurum izolasyonu: admin dışı sadece kendi kurumu
        if current_user.sistem_rol != 'admin' and surec.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403

        # Yetki notu: admin tüm kurumlarda yetkili olmalı
        if current_user.sistem_rol == 'admin':
            pass
        elif current_user.sistem_rol in ['kurum_yoneticisi', 'ust_yonetim']:
            pass
        else:
            # Normal kullanıcı için lider/üye kontrolü
            lider_mi = db.session.query(surec_liderleri).filter(
                surec_liderleri.c.surec_id == surec_id,
                surec_liderleri.c.user_id == current_user.id
            ).first() is not None
            
            uye_mi = db.session.query(surec_uyeleri).filter(
                surec_uyeleri.c.surec_id == surec_id,
                surec_uyeleri.c.user_id == current_user.id
            ).first() is not None
            
            if not (lider_mi or uye_mi):
                return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403
        
        # Performans göstergesini getir (alt strateji ile birlikte)
        pg = SurecPerformansGostergesi.query.options(
            db.joinedload(SurecPerformansGostergesi.alt_strateji).joinedload(AltStrateji.ana_strateji)
        ).filter_by(
            id=pg_id,
            surec_id=surec_id
        ).first()
        
        if not pg:
            return jsonify({'success': False, 'message': 'Performans göstergesi bulunamadı'}), 404
        
        return jsonify({
            'success': True,
            'gosterge': {
                'id': pg.id,
                'ad': pg.ad,
                'aciklama': pg.aciklama,
                'hedef_deger': pg.hedef_deger,
                'olcum_birimi': pg.olcum_birimi,
                'periyot': pg.periyot,
                'baslangic_tarihi': pg.baslangic_tarihi.strftime('%Y-%m-%d') if pg.baslangic_tarihi else None,
                'bitis_tarihi': pg.bitis_tarihi.strftime('%Y-%m-%d') if pg.bitis_tarihi else None,
                'veri_toplama_yontemi': pg.veri_toplama_yontemi,
                'agirlik': pg.agirlik,
                'weight': pg.weight,
                'onemli': pg.onemli,
                'kodu': pg.kodu,
                'gosterge_turu': pg.gosterge_turu,
                'target_method': pg.target_method,
                'direction': pg.direction,
                'basari_puani_araliklari': pg.basari_puani_araliklari,
                'onceki_yil_ortalamasi': pg.onceki_yil_ortalamasi,
                'alt_strateji_id': pg.alt_strateji_id,
                'alt_strateji': {
                    'id': pg.alt_strateji.id,
                    'ad': pg.alt_strateji.ad,
                    'ana_strateji': {
                        'id': pg.alt_strateji.ana_strateji.id,
                        'ad': pg.alt_strateji.ana_strateji.ad
                    } if pg.alt_strateji and pg.alt_strateji.ana_strateji else None
                } if pg.alt_strateji else None
            }
        })
    except Exception as e:
        current_app.logger.error(f'Performans göstergesi getirme hatası: {e}')
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Hata: {str(e)}'}), 500


@main_bp.route('/surec/<int:surec_id>/performans-gostergesi/<int:pg_id>/update', methods=['POST'])
@login_required
@csrf.exempt
def surec_performans_gostergesi_update(surec_id, pg_id):
    """Süreç için performans göstergesini güncelle"""
    try:
        # JSON verisini al
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Geçersiz JSON verisi'}), 400
        
        current_app.logger.info(f'Süreç {surec_id} için performans göstergesi {pg_id} güncelleme isteği: {data}')
        
        # Yetki kontrolü
        surec = Surec.query.get(surec_id)
        if not surec:
            return jsonify({'success': False, 'message': 'Süreç bulunamadı'}), 404
        
        # Kurum izolasyonu: admin dışı sadece kendi kurumu
        if current_user.sistem_rol != 'admin' and surec.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403

        # Yazma yetkisi: sadece yönetim rolleri
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403
        
        # Performans göstergesini getir
        pg = SurecPerformansGostergesi.query.filter_by(
            id=pg_id,
            surec_id=surec_id
        ).first()
        
        if not pg:
            return jsonify({'success': False, 'message': 'Performans göstergesi bulunamadı'}), 404
        
        # Zorunlu alan kontrolü
        if data.get('ad') and not data.get('ad').strip():
            return jsonify({'success': False, 'message': 'Performans göstergesi adı boş olamaz'}), 400
        
        # Tarih dönüştürme
        baslangic_tarihi = None
        bitis_tarihi = None
        try:
            if data.get('baslangic_tarihi'):
                baslangic_tarihi = datetime.strptime(data.get('baslangic_tarihi'), '%Y-%m-%d').date()
            if data.get('bitis_tarihi'):
                bitis_tarihi = datetime.strptime(data.get('bitis_tarihi'), '%Y-%m-%d').date()
        except ValueError as e:
            return jsonify({'success': False, 'message': f'Geçersiz tarih formatı: {str(e)}'}), 400
        
        # Performans göstergesini güncelle
        if data.get('ad'):
            pg.ad = data.get('ad', '').strip()
        if 'aciklama' in data:
            pg.aciklama = data.get('aciklama', '').strip() if data.get('aciklama') else None
        if 'hedef_deger' in data:
            pg.hedef_deger = data.get('hedef_deger', '').strip() if data.get('hedef_deger') else None
        if 'olcum_birimi' in data:
            pg.olcum_birimi = data.get('olcum_birimi', '').strip() if data.get('olcum_birimi') else None
        if 'periyot' in data:
            pg.periyot = data.get('periyot', 'Aylik')
        if 'veri_toplama_yontemi' in data:
            pg.veri_toplama_yontemi = data.get('veri_toplama_yontemi', 'Ortalama')
        if 'baslangic_tarihi' in data:
            pg.baslangic_tarihi = baslangic_tarihi
        if 'bitis_tarihi' in data:
            pg.bitis_tarihi = bitis_tarihi
        if 'agirlik' in data:
            try:
                pg.agirlik = int(data.get('agirlik', 0))
            except (ValueError, TypeError):
                pg.agirlik = 0
        if 'onemli' in data:
            pg.onemli = bool(data.get('onemli', False))
        if 'kodu' in data:
            pg.kodu = data.get('kodu', '').strip() if data.get('kodu') else None
        if 'gosterge_turu' in data:
            pg.gosterge_turu = data.get('gosterge_turu', '').strip() if data.get('gosterge_turu') else None
        if 'target_method' in data:
            pg.target_method = data.get('target_method', '').strip() if data.get('target_method') else None
        if 'direction' in data:
            pg.direction = data.get('direction', 'Increasing')
        if 'basari_puani_araliklari' in data:
            pg.basari_puani_araliklari = data.get('basari_puani_araliklari') if data.get('basari_puani_araliklari') else None
        if 'onceki_yil_ortalamasi' in data:
            try:
                pg.onceki_yil_ortalamasi = float(data.get('onceki_yil_ortalamasi')) if data.get('onceki_yil_ortalamasi') else None
            except (ValueError, TypeError):
                pg.onceki_yil_ortalamasi = None
        if 'alt_strateji_id' in data:
            try:
                pg.alt_strateji_id = int(data.get('alt_strateji_id')) if data.get('alt_strateji_id') else None
            except (ValueError, TypeError):
                pg.alt_strateji_id = None
        if 'weight' in data:
            w = data.get('weight')
            if w is None or w == '':
                pg.weight = None
            else:
                try:
                    f = float(w)
                    pg.weight = f if 0 <= f <= 100 else None
                except (ValueError, TypeError):
                    pg.weight = None
        
        db.session.commit()
        
        current_app.logger.info(f'Süreç {surec_id} için performans göstergesi {pg_id} güncellendi')
        
        return jsonify({
            'success': True,
            'message': 'Performans göstergesi başarıyla güncellendi',
            'pg_id': pg.id
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Performans göstergesi güncelleme hatası: {e}')
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Hata: {str(e)}'}), 500


@main_bp.route('/surec/<int:surec_id>/performans-gostergesi/<int:pg_id>/delete', methods=['DELETE'])
@login_required
@csrf.exempt
def surec_performans_gostergesi_delete(surec_id, pg_id):
    """Süreç için performans göstergesini sil"""
    try:
        # Yetki kontrolü
        surec = Surec.query.get(surec_id)
        if not surec:
            return jsonify({'success': False, 'message': 'Süreç bulunamadı'}), 404
        
        # Kurum izolasyonu: admin dışı sadece kendi kurumu
        if current_user.sistem_rol != 'admin' and surec.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403

        # Yazma yetkisi: sadece yönetim rolleri
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403
        
        # Performans göstergesini getir
        pg = SurecPerformansGostergesi.query.filter_by(
            id=pg_id,
            surec_id=surec_id
        ).first()
        
        if not pg:
            return jsonify({'success': False, 'message': 'Performans göstergesi bulunamadı'}), 404
        
        pg_ad = pg.ad
        db.session.delete(pg)
        db.session.commit()
        
        current_app.logger.info(f'Süreç {surec_id} için performans göstergesi {pg_id} silindi')
        
        return jsonify({
            'success': True,
            'message': f'"{pg_ad}" performans göstergesi başarıyla silindi'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Performans göstergesi silme hatası: {e}')
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Hata: {str(e)}'}), 500


@main_bp.route('/surec/<int:surec_id>')
@login_required
def get_surec(surec_id):
    """Süreç detaylarını getir - viewSurec fonksiyonu için"""
    try:
        surec = Surec.query.options(
            db.joinedload(Surec.liderler),
            db.joinedload(Surec.uyeler),
            db.joinedload(Surec.alt_stratejiler).joinedload(AltStrateji.ana_strateji),
            db.joinedload(Surec.kurum)
        ).get(surec_id)
        
        if not surec:
            return jsonify({'success': False, 'message': 'Süreç bulunamadı'}), 404
        
        # Kurum izolasyonu: admin dışı sadece kendi kurumu
        if current_user.sistem_rol != 'admin' and surec.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403

        # Yetki kontrolü (admin tüm kurumlarda yetkili)
        if current_user.sistem_rol == 'admin':
            pass
        elif current_user.sistem_rol in ['kurum_yoneticisi', 'ust_yonetim']:
            pass
        else:
            if current_user not in surec.liderler and current_user not in surec.uyeler:
                return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403
        
        # Performans göstergelerini getir
        performans_gostergeleri = SurecPerformansGostergesi.query.filter_by(surec_id=surec_id).all()
        
        # Bağlı alt süreçler (bu sürecin parent'ı olduğu süreçler)
        alt_surecler = [{'id': sub.id, 'ad': sub.ad} for sub in surec.sub_processes.filter_by(silindi=False).order_by(Surec.ad).all()]
        
        return jsonify({
            'success': True,
            'surec': {
                'id': surec.id,
                'ad': surec.ad,
                'parent_id': surec.parent_id,
                'weight': surec.weight,
                'dokuman_no': surec.dokuman_no,
                'rev_no': surec.rev_no,
                'rev_tarihi': surec.rev_tarihi.strftime('%Y-%m-%d') if surec.rev_tarihi else None,
                'ilk_yayin_tarihi': surec.ilk_yayin_tarihi.strftime('%Y-%m-%d') if surec.ilk_yayin_tarihi else None,
                'baslangic_tarihi': surec.baslangic_tarihi.strftime('%Y-%m-%d') if surec.baslangic_tarihi else None,
                'bitis_tarihi': surec.bitis_tarihi.strftime('%Y-%m-%d') if surec.bitis_tarihi else None,
                'durum': surec.durum,
                'ilerleme': surec.ilerleme or 0,
                'baslangic_siniri': surec.baslangic_siniri,
                'bitis_siniri': surec.bitis_siniri,
                'aciklama': surec.aciklama,
                'liderler': [{'id': u.id, 'username': u.username} for u in surec.liderler],
                'uyeler': [{'id': u.id, 'username': u.username} for u in surec.uyeler],
                'alt_stratejiler': [{
                    'id': s.id, 
                    'ad': s.ad,
                    'ana_strateji': {'id': s.ana_strateji.id, 'ad': s.ana_strateji.ad} if s.ana_strateji else None
                } for s in surec.alt_stratejiler],
                'kurum': {'id': surec.kurum.id, 'kisa_ad': surec.kurum.kisa_ad} if surec.kurum else None
            },
            'alt_surecler': alt_surecler,
            'performans_gostergeleri': [{
                'id': pg.id,
                'ad': pg.ad,
                'hedef_deger': pg.hedef_deger,
                # Template uyumu
                'olcum_birimi': pg.olcum_birimi,
                'periyot': pg.periyot,
                # Geriye uyumluluk
                'birim': pg.olcum_birimi
            } for pg in performans_gostergeleri]
        })
    except Exception as e:
        import traceback
        current_app.logger.error(f'Süreç detay hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        return json_error(e, "[get_surec]", 500)


@main_bp.route('/surec/<int:surec_id>/faaliyetler')
@login_required
def get_surec_faaliyetler(surec_id):
    """Süreç faaliyetlerini getir"""
    try:
        surec = Surec.query.get(surec_id)
        if not surec:
            return jsonify({'success': False, 'message': 'Süreç bulunamadı'}), 404
        
        # Kurum izolasyonu: admin dışı sadece kendi kurumu
        if current_user.sistem_rol != 'admin' and surec.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403

        # Yetki kontrolü (admin tüm kurumlarda yetkili)
        if current_user.sistem_rol == 'admin':
            pass
        elif current_user.sistem_rol in ['kurum_yoneticisi', 'ust_yonetim']:
            pass
        else:
            if current_user not in surec.liderler and current_user not in surec.uyeler:
                return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403
        
        faaliyetler = SurecFaaliyet.query.filter_by(surec_id=surec_id).all()
        
        return jsonify({
            'success': True,
            'faaliyetler': [{
                'id': f.id,
                'ad': f.ad,
                'durum': f.durum,
                'ilerleme': f.ilerleme or 0,
                'baslangic_tarihi': f.baslangic_tarihi.strftime('%Y-%m-%d') if f.baslangic_tarihi else None,
                'bitis_tarihi': f.bitis_tarihi.strftime('%Y-%m-%d') if f.bitis_tarihi else None
            } for f in faaliyetler]
        })
    except Exception as e:
        import traceback
        current_app.logger.error(f'Süreç faaliyetleri hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        return json_error(e, "[get_surec_faaliyetler]", 500)


@main_bp.route('/surec/update/<int:surec_id>', methods=['POST'])
@login_required
@csrf.exempt
def update_surec(surec_id):
    """Süreç güncelle - updateSurec fonksiyonu için"""
    try:
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        
        data = request.get_json()
        surec = Surec.query.get(surec_id)
        
        if not surec:
            return jsonify({'success': False, 'message': 'Süreç bulunamadı'}), 404
        
        # Kurum izolasyonu: admin dışı sadece kendi kurumu
        if current_user.sistem_rol != 'admin' and surec.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403

        # Düzenleme yetkisi: sadece yönetim rolleri
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Bu süreci düzenleme yetkiniz yok'}), 403
        
        # Süreç bilgilerini güncelle
        surec.ad = data.get('surec_adi', surec.ad)
        surec.dokuman_no = data.get('dokuman_no', surec.dokuman_no)
        surec.rev_no = data.get('rev_no', surec.rev_no)
        surec.rev_tarihi = datetime.strptime(data['rev_tarihi'], '%Y-%m-%d').date() if data.get('rev_tarihi') else surec.rev_tarihi
        surec.ilk_yayin_tarihi = datetime.strptime(data['ilk_yayin_tarihi'], '%Y-%m-%d').date() if data.get('ilk_yayin_tarihi') else surec.ilk_yayin_tarihi
        surec.baslangic_tarihi = datetime.strptime(data['baslangic_tarihi'], '%Y-%m-%d').date() if data.get('baslangic_tarihi') else surec.baslangic_tarihi
        surec.bitis_tarihi = datetime.strptime(data['bitis_tarihi'], '%Y-%m-%d').date() if data.get('bitis_tarihi') else surec.bitis_tarihi
        surec.durum = data.get('durum', surec.durum)
        surec.ilerleme = data.get('ilerleme', surec.ilerleme)
        surec.baslangic_siniri = data.get('baslangic_siniri', surec.baslangic_siniri)
        surec.bitis_siniri = data.get('bitis_siniri', surec.bitis_siniri)
        surec.aciklama = data.get('aciklama', surec.aciklama)
        # Skor Motoru: ağırlık (0-100)
        if 'weight' in data:
            w = data.get('weight')
            surec.weight = min(100.0, max(0.0, float(w))) if w is not None and str(w).strip() != '' else None
        # Üst süreç (döngü ve kendi kendisi kontrolü)
        new_parent_id = _validate_surec_parent_id(surec.id, data.get('parent_id'), surec.kurum_id)
        surec.parent_id = new_parent_id

        # Liderleri güncelle (kurum izolasyonu); boş liste gönderilirse temizlenir
        if 'lider_ids' in data:
            lider_ids = data.get('lider_ids', [])
            normalized_lider_ids = [int(x) for x in lider_ids] if lider_ids else []
            if not normalized_lider_ids:
                surec.liderler = []
            else:
                surec.liderler = User.query.filter(
                    User.kurum_id == surec.kurum_id,
                    User.id.in_(normalized_lider_ids)
                ).all()
        
        # Üyeleri güncelle (kurum izolasyonu); boş liste gönderilirse temizlenir
        if 'uye_ids' in data:
            uye_ids = data.get('uye_ids', [])
            normalized_uye_ids = [int(x) for x in uye_ids] if uye_ids else []
            if not normalized_uye_ids:
                surec.uyeler = []
            else:
                surec.uyeler = User.query.filter(
                    User.kurum_id == surec.kurum_id,
                    User.id.in_(normalized_uye_ids)
                ).all()
        
        # Alt stratejileri güncelle (kurum izolasyonu); boş liste gönderilirse temizlenir
        strateji_ids = data.get('strateji_ids', None)
        if strateji_ids is None:
            strateji_ids = data.get('alt_strateji_ids', None)
        if 'strateji_ids' in data or 'alt_strateji_ids' in data:
            normalized_strateji_ids = [int(x) for x in (strateji_ids or [])] if strateji_ids else []
            if not normalized_strateji_ids:
                surec.alt_stratejiler = []
            else:
                surec.alt_stratejiler = AltStrateji.query.filter(
                    AltStrateji.id.in_(normalized_strateji_ids),
                    AltStrateji.ana_strateji.has(kurum_id=surec.kurum_id)
                ).all()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Süreç başarıyla güncellendi'
        })
    except ValueError as e:
        db.session.rollback()
        return json_error(e, "[update_surec]", 400)
    except Exception as e:
        db.session.rollback()
        import traceback
        current_app.logger.error(f'Süreç güncelleme hatası: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        return json_error(e, "[update_surec]", 500)


def _parse_optional_date(value: object):
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    return datetime.strptime(text, '%Y-%m-%d').date()


@main_bp.route('/surec/<int:surec_id>/faaliyet/<int:faaliyet_id>')
@login_required
def get_surec_faaliyet_detay(surec_id: int, faaliyet_id: int):
    """Süreç faaliyeti detayını getir - surec_karnesi.html editFaaliyet() için"""
    try:
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403

        surec = Surec.query.get(surec_id)
        if not surec or surec.silindi:
            return jsonify({'success': False, 'message': 'Süreç bulunamadı'}), 404

        if current_user.sistem_rol != 'admin' and surec.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403

        faaliyet = SurecFaaliyet.query.filter_by(id=faaliyet_id, surec_id=surec_id).first()
        if not faaliyet:
            return jsonify({'success': False, 'message': 'Faaliyet bulunamadı'}), 404

        return jsonify({
            'success': True,
            'faaliyet': {
                'id': faaliyet.id,
                'surec_id': faaliyet.surec_id,
                'ad': faaliyet.ad,
                'aciklama': faaliyet.aciklama or '',
                'baslangic_tarihi': faaliyet.baslangic_tarihi.strftime('%Y-%m-%d') if faaliyet.baslangic_tarihi else '',
                'bitis_tarihi': faaliyet.bitis_tarihi.strftime('%Y-%m-%d') if faaliyet.bitis_tarihi else '',
                'durum': faaliyet.durum,
                'ilerleme': faaliyet.ilerleme or 0,
            }
        })
    except Exception as e:
        current_app.logger.error(f'Faaliyet detay hatası: {e}', exc_info=True)
        return json_error(e, "[get_surec_faaliyet_detay]", 500)


@main_bp.route('/surec/<int:surec_id>/faaliyet/add', methods=['POST'])
@login_required
@csrf.exempt
def add_surec_faaliyet(surec_id: int):
    """Süreç faaliyeti ekle - surec_karnesi.html addFaaliyet() için"""
    try:
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403

        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        data = request.get_json() or {}

        surec = Surec.query.get(surec_id)
        if not surec or surec.silindi:
            return jsonify({'success': False, 'message': 'Süreç bulunamadı'}), 404

        if current_user.sistem_rol != 'admin' and surec.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403

        ad = (data.get('ad') or '').strip()
        if not ad:
            return jsonify({'success': False, 'message': 'Faaliyet adı zorunludur'}), 400

        yeni = SurecFaaliyet(
            surec_id=surec_id,
            ad=ad,
            aciklama=(data.get('aciklama') or '').strip() or None,
            baslangic_tarihi=_parse_optional_date(data.get('baslangic_tarihi')),
            bitis_tarihi=_parse_optional_date(data.get('bitis_tarihi')),
            durum=(data.get('durum') or 'Planlandı'),
            ilerleme=int(data.get('ilerleme') or 0),
        )
        db.session.add(yeni)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Faaliyet başarıyla eklendi', 'faaliyet_id': yeni.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Faaliyet ekleme hatası: {e}', exc_info=True)
        return json_error(e, "[add_surec_faaliyet]", 500)


@main_bp.route('/surec/<int:surec_id>/faaliyet/<int:faaliyet_id>/update', methods=['POST'])
@login_required
@csrf.exempt
def update_surec_faaliyet(surec_id: int, faaliyet_id: int):
    """Süreç faaliyeti güncelle - surec_karnesi.html updateFaaliyet() için"""
    try:
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403

        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400
        data = request.get_json() or {}

        surec = Surec.query.get(surec_id)
        if not surec or surec.silindi:
            return jsonify({'success': False, 'message': 'Süreç bulunamadı'}), 404

        if current_user.sistem_rol != 'admin' and surec.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403

        faaliyet = SurecFaaliyet.query.filter_by(id=faaliyet_id, surec_id=surec_id).first()
        if not faaliyet:
            return jsonify({'success': False, 'message': 'Faaliyet bulunamadı'}), 404

        ad = (data.get('ad') or faaliyet.ad).strip()
        if not ad:
            return jsonify({'success': False, 'message': 'Faaliyet adı zorunludur'}), 400

        faaliyet.ad = ad
        faaliyet.aciklama = (data.get('aciklama') or '').strip() or None
        faaliyet.baslangic_tarihi = _parse_optional_date(data.get('baslangic_tarihi'))
        faaliyet.bitis_tarihi = _parse_optional_date(data.get('bitis_tarihi'))
        if 'surec_pg_id' in data:
            faaliyet.surec_pg_id = int(data['surec_pg_id']) if data.get('surec_pg_id') else None

        db.session.commit()

        # Skor Motoru: Aksiyon (faaliyet) güncellendiğinde bağlı PG üzerinden vizyonu yeniden hesapla
        try:
            from services.score_engine_service import recalc_on_faaliyet_change
            recalc_on_faaliyet_change(getattr(faaliyet, 'surec_pg_id', None), surec.kurum_id)
        except Exception as score_err:
            # Best-effort skor yeniden-hesabı; başarısızsa faaliyet yine de kaydedildi,
            # skor bir sonraki tetikte güncellenir. Sessiz yutma (KURALLAR §3) yerine logla.
            current_app.logger.warning(f'[faaliyet_update] skor recalc başarısız: {score_err}')

        return jsonify({'success': True, 'message': 'Faaliyet başarıyla güncellendi'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Faaliyet güncelleme hatası: {e}', exc_info=True)
        return json_error(e, "[update_surec_faaliyet]", 500)


@main_bp.route('/surec/<int:surec_id>/faaliyet/<int:faaliyet_id>/delete', methods=['DELETE'])
@login_required
@csrf.exempt
def delete_surec_faaliyet(surec_id: int, faaliyet_id: int):
    """Süreç faaliyeti sil - surec_karnesi.html deleteFaaliyet() için"""
    try:
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Bu işlem için yetkiniz yok'}), 403

        surec = Surec.query.get(surec_id)
        if not surec or surec.silindi:
            return jsonify({'success': False, 'message': 'Süreç bulunamadı'}), 404

        if current_user.sistem_rol != 'admin' and surec.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403

        faaliyet = SurecFaaliyet.query.filter_by(id=faaliyet_id, surec_id=surec_id).first()
        if not faaliyet:
            return jsonify({'success': False, 'message': 'Faaliyet bulunamadı'}), 404

        db.session.delete(faaliyet)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Faaliyet başarıyla silindi'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Faaliyet silme hatası: {e}', exc_info=True)
        return json_error(e, "[delete_surec_faaliyet]", 500)


def _ensure_int_list(value: object) -> list[int]:
    if value is None:
        return []
    if isinstance(value, list):
        raw = value
    else:
        raw = [value]
    out: list[int] = []
    for item in raw:
        if item is None:
            continue
        text = str(item).strip()
        if not text:
            continue
        out.append(int(text))
    return out


def _validate_same_kurum_user_ids(kurum_id: int, user_ids: list[int]) -> list[User]:
    if not user_ids:
        return []
    users = User.query.filter(User.kurum_id == kurum_id, User.id.in_(user_ids)).all()
    if len(users) != len(set(user_ids)):
        raise ValueError('Seçilen kullanıcılar kurumla uyuşmuyor veya bulunamadı')
    return users


def _validate_same_kurum_alt_stratejiler(kurum_id: int, strateji_ids: list[int]) -> list[AltStrateji]:
    if not strateji_ids:
        return []
    stratejiler = AltStrateji.query.filter(
        AltStrateji.id.in_(strateji_ids),
        AltStrateji.ana_strateji.has(kurum_id=kurum_id)
    ).all()
    if len(stratejiler) != len(set(strateji_ids)):
        raise ValueError('Seçilen stratejiler kurumla uyuşmuyor veya bulunamadı')
    return stratejiler


def _surec_descendant_ids(surec_id: int) -> set:
    """Bir sürecin tüm alt süreç (çocuk, torun, ...) id'lerini döndürür. Sonsuz döngü engellemek için kullanılır."""
    out = set()
    stack = [surec_id]
    while stack:
        pid = stack.pop()
        children = Surec.query.filter_by(parent_id=pid, silindi=False).all()
        for c in children:
            if c.id not in out:
                out.add(c.id)
                stack.append(c.id)
    return out


def _validate_surec_parent_id(surec_id: int | None, parent_id_raw, kurum_id: int) -> int | None:
    """Üst süreç (parent_id) geçerli mi kontrol eder: aynı kurum, kendi kendisi olamaz, döngü olamaz."""
    if parent_id_raw is None or parent_id_raw == '' or (isinstance(parent_id_raw, list) and not parent_id_raw):
        return None
    parent_id = int(parent_id_raw) if not isinstance(parent_id_raw, int) else parent_id_raw
    if parent_id <= 0:
        return None
    parent = Surec.query.filter_by(id=parent_id, silindi=False).first()
    if not parent or parent.kurum_id != kurum_id:
        raise ValueError('Üst süreç aynı kuruma ait olmalı ve bulunmalıdır')
    if surec_id and parent_id == surec_id:
        raise ValueError('Bir süreç kendi üst süreci olamaz')
    if surec_id and parent_id in _surec_descendant_ids(surec_id):
        raise ValueError('Üst süreç seçimi döngü oluşturmaz (alt sürecinizi üst süreç yapamazsınız)')
    return parent_id


@main_bp.route('/surec/get/<int:surec_id>')
@login_required
def surec_get_for_edit(surec_id):
    """Süreç bilgilerini getir - surec_panel.html editSurec() için"""
    try:
        surec = Surec.query.options(
            db.joinedload(Surec.liderler),
            db.joinedload(Surec.uyeler),
            db.joinedload(Surec.alt_stratejiler).joinedload(AltStrateji.ana_strateji),
            db.joinedload(Surec.kurum)
        ).filter_by(id=surec_id, silindi=False).first()

        if not surec:
            return jsonify({'success': False, 'message': 'Süreç bulunamadı'}), 404

        # Kurum izolasyonu: admin dışı sadece kendi kurumu
        if current_user.sistem_rol != 'admin' and surec.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403

        # Düzenleme yetkisi: sadece yönetim rolleri
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Bu süreci düzenleme yetkiniz yok'}), 403

        sub_count = Surec.query.filter_by(parent_id=surec.id, silindi=False).count()
        descendant_ids = list(_surec_descendant_ids(surec.id))
        alt_surecler = [{'id': sub.id, 'ad': sub.ad} for sub in surec.sub_processes.filter_by(silindi=False).order_by(Surec.ad).all()]
        return jsonify({
            'success': True,
            'alt_surecler': alt_surecler,
            'surec': {
                'id': surec.id,
                'ad': surec.ad,
                'parent_id': surec.parent_id,
                'sub_processes_count': sub_count,
                'descendant_ids': descendant_ids,
                'dokuman_no': surec.dokuman_no or '',
                'rev_no': surec.rev_no or '',
                'rev_tarihi': surec.rev_tarihi.strftime('%Y-%m-%d') if surec.rev_tarihi else '',
                'ilk_yayin_tarihi': surec.ilk_yayin_tarihi.strftime('%Y-%m-%d') if surec.ilk_yayin_tarihi else '',
                'baslangic_tarihi': surec.baslangic_tarihi.strftime('%Y-%m-%d') if surec.baslangic_tarihi else '',
                'bitis_tarihi': surec.bitis_tarihi.strftime('%Y-%m-%d') if surec.bitis_tarihi else '',
                'durum': surec.durum,
                'ilerleme': surec.ilerleme or 0,
                'baslangic_siniri': surec.baslangic_siniri or '',
                'bitis_siniri': surec.bitis_siniri or '',
                'aciklama': surec.aciklama or '',
                'weight': getattr(surec, 'weight', None),
                'liderler': [{'id': u.id, 'username': u.username} for u in surec.liderler],
                'uyeler': [{'id': u.id, 'username': u.username} for u in surec.uyeler],
                'alt_stratejiler': [{
                    'id': s.id,
                    'ad': s.ad,
                    'ana_strateji': {'id': s.ana_strateji.id, 'ad': s.ana_strateji.ad} if s.ana_strateji else None
                } for s in surec.alt_stratejiler],
                'kurum': {'id': surec.kurum.id, 'kisa_ad': surec.kurum.kisa_ad} if surec.kurum else None
            }
        })
    except Exception as e:
        current_app.logger.error(f'Süreç getirme hatası: {e}', exc_info=True)
        return json_error(e, "[surec_get_for_edit]", 500)


@main_bp.route('/surec/add-simple', methods=['POST'])
@login_required
@csrf.exempt
def surec_add_simple():
    """Süreç ekle - surec_panel.html form submit için"""
    try:
        # Yetki: normal kullanıcı süreç oluşturamaz
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Süreç oluşturma yetkiniz yok'}), 403

        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type application/json olmalı'}), 400

        data = request.get_json() or {}

        ad = (data.get('surec_adi') or data.get('ad') or '').strip()
        if not ad:
            return jsonify({'success': False, 'message': 'Süreç adı zorunludur'}), 400

        lider_ids = _ensure_int_list(data.get('lider_ids'))
        if not lider_ids:
            return jsonify({'success': False, 'message': 'En az bir lider seçmelisiniz'}), 400

        # Kurum belirleme: admin opsiyonel alabilir; diğerleri kendi kurumuna sabit
        if current_user.sistem_rol == 'admin':
            kurum_id = int(data.get('kurum_id') or current_user.kurum_id)
        else:
            kurum_id = int(current_user.kurum_id)

        kurum = Kurum.query.get(kurum_id)
        if not kurum:
            return jsonify({'success': False, 'message': 'Kurum bulunamadı'}), 404

        uye_ids = _ensure_int_list(data.get('uye_ids'))
        alt_strateji_ids = _ensure_int_list(data.get('alt_strateji_ids') or data.get('strateji_ids'))
        parent_id = _validate_surec_parent_id(None, data.get('parent_id'), kurum_id)

        liderler = _validate_same_kurum_user_ids(kurum_id, lider_ids)
        uyeler = _validate_same_kurum_user_ids(kurum_id, uye_ids)
        alt_stratejiler = _validate_same_kurum_alt_stratejiler(kurum_id, alt_strateji_ids)

        weight_f = None
        if data.get('weight') is not None and str(data.get('weight')).strip() != '':
            try:
                weight_f = min(100.0, max(0.0, float(data.get('weight'))))
            except (ValueError, TypeError):
                weight_f = None
        surec = Surec(
            kurum_id=kurum_id,
            parent_id=parent_id,
            ad=ad,
            weight=weight_f,
            dokuman_no=(data.get('dokuman_no') or '').strip() or None,
            rev_no=(data.get('rev_no') or '').strip() or None,
            rev_tarihi=_parse_optional_date(data.get('rev_tarihi')),
            ilk_yayin_tarihi=_parse_optional_date(data.get('ilk_yayin_tarihi')),
            baslangic_tarihi=_parse_optional_date(data.get('baslangic_tarihi')),
            bitis_tarihi=_parse_optional_date(data.get('bitis_tarihi')),
            durum=(data.get('durum') or 'Aktif'),
            ilerleme=int(data.get('ilerleme') or 0),
            baslangic_siniri=(data.get('baslangic_siniri') or '').strip() or None,
            bitis_siniri=(data.get('bitis_siniri') or '').strip() or None,
            aciklama=(data.get('aciklama') or '').strip() or None,
        )

        surec.liderler = liderler
        surec.uyeler = uyeler
        surec.alt_stratejiler = alt_stratejiler

        db.session.add(surec)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Süreç başarıyla oluşturuldu', 'surec_id': surec.id})
    except ValueError as e:
        db.session.rollback()
        return json_error(e, "[surec_add_simple]", 400)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Süreç oluşturma hatası: {e}', exc_info=True)
        return json_error(e, "[surec_add_simple]", 500)


@main_bp.route('/surec/delete/<int:surec_id>', methods=['DELETE'])
@login_required
@csrf.exempt
def surec_delete(surec_id):
    """Süreç soft-delete"""
    try:
        # Yetki: normal kullanıcı süreç silemez
        if current_user.sistem_rol not in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
            return jsonify({'success': False, 'message': 'Süreç silme yetkiniz yok'}), 403

        surec = Surec.query.filter_by(id=surec_id, silindi=False).first()
        if not surec:
            return jsonify({'success': False, 'message': 'Süreç bulunamadı'}), 404

        # Kurum izolasyonu: admin dışı sadece kendi kurumu
        if current_user.sistem_rol != 'admin' and surec.kurum_id != current_user.kurum_id:
            return jsonify({'success': False, 'message': 'Bu süreçte yetkiniz yok'}), 403

        # Yetki: admin tam; kurum_yoneticisi/ust_yonetim kurum içinde
        if current_user.sistem_rol == 'admin':
            pass
        elif current_user.sistem_rol in ['kurum_yoneticisi', 'ust_yonetim']:
            pass

        # Alt süreçlerin parent_id'sini null yap (yetim kalmasın, kök süreç olsun)
        Surec.query.filter_by(parent_id=surec_id, silindi=False).update({Surec.parent_id: None}, synchronize_session=False)
        surec.silindi = True
        surec.deleted_at = datetime.utcnow()
        surec.deleted_by = current_user.id
        db.session.commit()

        return jsonify({'success': True, 'message': 'Süreç başarıyla silindi'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Süreç silme hatası: {e}', exc_info=True)
        return json_error(e, "[surec_delete]", 500)


# 2026-06-17: /performans-kartim kaldırıldı — redirect-ölü (GET 301 → /bireysel/karne).


