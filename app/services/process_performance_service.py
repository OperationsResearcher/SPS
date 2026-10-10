# -*- coding: utf-8 -*-
"""
Process Performance Service
Süreç karnesi performans verilerinin hesaplandığı "Business Logic" katmanı.
"""
from typing import Dict, Any, Tuple
import time
from datetime import datetime, timezone

from flask import current_app
from app.models.legacy_bridge import db, Surec, SurecPerformansGostergesi, AltStrateji, surec_liderleri, surec_uyeleri
from services.performance_service import generatePeriyotVerileri, calculateHedefDeger
from utils.karne_hesaplamalar import (
    hesapla_basari_puani, hesapla_agirlikli_basari_puani, parse_basari_puani_araliklari
)
from app.utils.errors import AuthorizationError, ResourceNotFoundError
from flask_babel import gettext as _
import logging

logger = logging.getLogger(__name__)


class ProcessPerformanceService:
    @staticmethod
    def get_process_performance(user, surec_id: int, yil: int, periyot: str, ay: int = None, debug_mode: bool = False) -> Tuple[Dict[str, Any], int]:
        """
        Sürecin performans göstergelerini ve çeyreklik verilerini hesaplar.
        Tanrı nesnelerden (God Objects) iş mantığını ayırmak (Decoupling) için oluşturulmuştur.
        """
        baslangic_zamani = time.time()
        
        # 1. Kaynak ve Yetki Kontrolleri
        surec = Surec.query.options(db.joinedload(Surec.kurum)).get(surec_id)
        if not surec:
            raise ResourceNotFoundError("Süreç bulunamadı.")
            
        if user.sistem_rol == 'admin':
            pass
        elif user.sistem_rol in ['kurum_yoneticisi', 'ust_yonetim']:
            if surec.kurum_id != user.kurum_id:
                raise AuthorizationError("Farklı kurumun sürecine erişim reddedildi.")
        else:
            lider_mi = db.session.query(surec_liderleri).filter(
                surec_liderleri.c.surec_id == surec_id,
                surec_liderleri.c.user_id == user.id
            ).first() is not None
            uye_mi = db.session.query(surec_uyeleri).filter(
                surec_uyeleri.c.surec_id == surec_id,
                surec_uyeleri.c.user_id == user.id
            ).first() is not None
            
            if not (lider_mi or uye_mi):
                raise AuthorizationError("Bu süreçte yetkiniz yok.")
                
        # 2. Veri Çekimi
        from app.models.core import SubStrategy
        surec_pgler = SurecPerformansGostergesi.query.options(
            db.joinedload(SurecPerformansGostergesi.sub_strategy).joinedload(SubStrategy.strategy)
        ).filter_by(surec_id=surec_id).all()
        
        gostergeler = []
        hata_listesi = []
        
        # 3. Hesaplama (Business Logic)
        for pg in surec_pgler:
            try:
                hesaplama_yontemi = getattr(pg, 'veri_toplama_yontemi', 'Ortalama')
                
                veriler = generatePeriyotVerileri(
                    periyot=periyot,
                    pg_id=pg.id,
                    yil=yil,
                    pg_hedef_deger=pg.hedef_deger,
                    pg_periyot=pg.periyot,
                    hesaplama_yontemi=hesaplama_yontemi,
                    direction=getattr(pg, 'direction', 'Increasing'),
                    ay=ay
                )
                
                gosterim_hedef_deger = calculateHedefDeger(
                    pg.hedef_deger, pg.periyot, periyot, hesaplama_yontemi
                )
                
                ana_strateji_kodu = None
                alt_strateji_kodu = None
                if pg.sub_strategy:
                    alt_strateji_kodu = getattr(pg.sub_strategy, 'code', None)
                    if pg.sub_strategy.strategy:
                        ana_strateji_kodu = getattr(pg.sub_strategy.strategy, 'code', None)
                
                onceki_yil_ortalamasi = getattr(pg, 'onceki_yil_ortalamasi', None)
                basari_puani_araliklari = parse_basari_puani_araliklari(getattr(pg, 'basari_puani_araliklari', None))
                
                yil_sonu_gerceklesen = None
                if periyot == 'ceyrek' and veriler:
                    ceyrek_degerler = []
                    for veri in veriler:
                        if veri.get('gerceklesen_deger') is not None:
                            try:
                                ceyrek_degerler.append(float(veri['gerceklesen_deger']))
                            except (ValueError, TypeError) as err:
                                logger.warning(f"get_process_performance failed: {err}")
                    if ceyrek_degerler:
                        if hesaplama_yontemi in ['Toplama', 'SUM']:
                            yil_sonu_gerceklesen = sum(ceyrek_degerler)
                        else:  # Ortalama
                            yil_sonu_gerceklesen = sum(ceyrek_degerler) / len(ceyrek_degerler)
                
                basari_puani = None
                agirlikli_basari_puani = None
                
                if yil_sonu_gerceklesen is not None and basari_puani_araliklari:
                    direction = getattr(pg, 'direction', 'Increasing')
                    basari_puani = hesapla_basari_puani(yil_sonu_gerceklesen, basari_puani_araliklari, direction)
                    try:
                        pg.basari_puani = basari_puani
                        agirlik = getattr(pg, 'agirlik', 0)
                        agirlikli_basari_puani = hesapla_agirlikli_basari_puani(basari_puani, agirlik)
                        pg.agirlikli_basari_puani = agirlikli_basari_puani
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        current_app.logger.warning(f"Başarı puanı kaydedilirken hata: {e}")
                
                gostergeler.append({
                    'id': pg.id,
                    'surec_pg_id': pg.id,
                    'ad': pg.ad,
                    'kodu': getattr(pg, 'kodu', f'PG-{pg.id}'),
                    'hedef_deger': pg.hedef_deger,
                    'gosterim_hedef_deger': round(gosterim_hedef_deger, 2) if gosterim_hedef_deger is not None else None,
                    'olcum_birimi': pg.olcum_birimi,
                    'periyot': pg.periyot,
                    'agirlik': getattr(pg, 'agirlik', 0),
                    'onemli': getattr(pg, 'onemli', False),
                    'veri_toplama_yontemi': hesaplama_yontemi,
                    'veriler': veriler,
                    'ana_strateji_kodu': ana_strateji_kodu,
                    'alt_strateji_kodu': alt_strateji_kodu,
                    'gosterge_turu': getattr(pg, 'gosterge_turu', None),
                    'target_method': getattr(pg, 'target_method', None),
                    'onceki_yil_ortalamasi': round(onceki_yil_ortalamasi, 2) if onceki_yil_ortalamasi is not None else None,
                    'basari_puani': basari_puani,
                    'agirlikli_basari_puani': round(agirlikli_basari_puani, 2) if agirlikli_basari_puani is not None else None,
                    'basari_puani_araliklari': basari_puani_araliklari,
                    'yil_sonu_gerceklesen': round(yil_sonu_gerceklesen, 2) if yil_sonu_gerceklesen is not None else None
                })
            except Exception as pg_error:
                import traceback
                error_trace = traceback.format_exc()
                hata_listesi.append({
                    'pg_id': pg.id,
                    'pg_ad': pg.ad,
                    'hata': str(pg_error),
                    'traceback': error_trace if debug_mode else None
                })
                continue
                
        gecen_sure = time.time() - baslangic_zamani
        current_app.logger.info(f"Süreç Karnesi Servisi tamamlandı, geçen süre: {gecen_sure:.2f} saniye")
        
        response_data = {
            'success': True,
            'gostergeler': gostergeler
        }
        
        if debug_mode and hata_listesi:
            response_data['hatalar'] = hata_listesi
            response_data['toplam_pg'] = len(surec_pgler)
            response_data['basarili_pg'] = len(gostergeler)
            response_data['hatali_pg'] = len(hata_listesi)
            
        return response_data, 200

    @staticmethod
    def get_process_activities(user, surec_id: int, yil: int) -> Tuple[Dict[str, Any], int]:
        from app.models.legacy_bridge import db, SurecFaaliyet, BireyselFaaliyet, FaaliyetTakip
        
        surec_faaliyetler = SurecFaaliyet.query.filter_by(surec_id=surec_id).all()
        surec_faaliyet_ids = [f.id for f in surec_faaliyetler]
        
        bireysel_map = {}
        if surec_faaliyet_ids:
            bireyseller = BireyselFaaliyet.query.filter(
                BireyselFaaliyet.user_id == user.id,
                BireyselFaaliyet.kaynak == 'Süreç',
                BireyselFaaliyet.kaynak_surec_id == surec_id,
                BireyselFaaliyet.kaynak_surec_faaliyet_id.in_(surec_faaliyet_ids)
            ).all()
            bireysel_map = {b.kaynak_surec_faaliyet_id: b for b in bireyseller if b.kaynak_surec_faaliyet_id}

        takip_map = {}
        bireysel_ids = [b.id for b in bireysel_map.values()]
        if bireysel_ids:
            takip_rows = FaaliyetTakip.query.filter(
                FaaliyetTakip.user_id == user.id,
                FaaliyetTakip.yil == yil,
                FaaliyetTakip.bireysel_faaliyet_id.in_(bireysel_ids)
            ).all()
            for row in takip_rows:
                takip_map.setdefault(row.bireysel_faaliyet_id, []).append({
                    'ay': row.ay,
                    'gerceklesti': bool(row.gerceklesti)
                })

        faaliyetler = []
        for faaliyet in surec_faaliyetler:
            bireysel = bireysel_map.get(faaliyet.id)
            bireysel_id = bireysel.id if bireysel else 0
            faaliyetler.append({
                'id': bireysel_id,
                'surec_faaliyet_id': faaliyet.id,
                'ad': faaliyet.ad,
                'oneri': faaliyet.aciklama,
                'takip': takip_map.get(bireysel_id, [])
            })
        
        return {'success': True, 'faaliyetler': faaliyetler}, 200

    @staticmethod
    def create_bireysel_faaliyet_from_surec(user, surec_id: int, surec_faaliyet_id: int) -> Tuple[Dict[str, Any], int]:
        from app.models.legacy_bridge import db, SurecFaaliyet, BireyselFaaliyet
        from app.utils.errors import ResourceNotFoundError
        
        surec_faaliyet = SurecFaaliyet.query.filter_by(id=surec_faaliyet_id, surec_id=surec_id).first()
        if not surec_faaliyet:
            raise ResourceNotFoundError("Faaliyet bulunamadı.")

        mevcut = BireyselFaaliyet.query.filter_by(
            user_id=user.id,
            kaynak='Süreç',
            kaynak_surec_id=surec_id,
            kaynak_surec_faaliyet_id=surec_faaliyet_id
        ).first()
        if mevcut:
            return {'success': True, 'bireysel_faaliyet_id': mevcut.id}, 200

        yeni = BireyselFaaliyet(
            user_id=user.id,
            ad=surec_faaliyet.ad,
            aciklama=surec_faaliyet.aciklama,
            baslangic_tarihi=surec_faaliyet.baslangic_tarihi,
            bitis_tarihi=surec_faaliyet.bitis_tarihi,
            durum=surec_faaliyet.durum,
            ilerleme=surec_faaliyet.ilerleme,
            kaynak='Süreç',
            kaynak_surec_id=surec_id,
            kaynak_surec_faaliyet_id=surec_faaliyet_id,
            kurum_id=surec_faaliyet.surec.kurum_id if surec_faaliyet.surec else user.kurum_id
        )
        db.session.add(yeni)
        try:
            db.session.commit()
            return {'success': True, 'bireysel_faaliyet_id': yeni.id}, 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Bireysel Faaliyet oluşturma hatası: {e}')
            raise Exception('Veritabanı hatası oluştu.')

    @staticmethod
    def save_activity_tracking(user, faaliyet_id: int, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        from app.models.legacy_bridge import db, BireyselFaaliyet, FaaliyetTakip
        from datetime import datetime, date
        from app.utils.errors import ResourceNotFoundError, AuthorizationError

        yil = int(data.get('yil') or datetime.now().year)
        ay = int(data.get('ay') or 0)
        if ay < 1 or ay > 12:
            raise ValueError("Ay 1-12 aralığında olmalı")
        
        gerceklesti = bool(data.get('gerceklesti'))

        faaliyet = BireyselFaaliyet.query.get(faaliyet_id)
        if not faaliyet:
            raise ResourceNotFoundError("Faaliyet bulunamadı")
        
        if faaliyet.user_id != user.id:
            raise AuthorizationError("Bu faaliyet üzerinde yetkiniz yok")

        takip = FaaliyetTakip.query.filter_by(
            bireysel_faaliyet_id=faaliyet_id,
            user_id=user.id,
            yil=yil,
            ay=ay
        ).first()

        if not takip:
            takip = FaaliyetTakip(
                bireysel_faaliyet_id=faaliyet_id,
                user_id=user.id,
                yil=yil,
                ay=ay,
                gerceklesti=gerceklesti
            )
            db.session.add(takip)
        else:
            takip.gerceklesti = gerceklesti

        takip.tamamlanma_tarihi = date.today() if gerceklesti else None

        db.session.commit()
        return {'success': True}, 200

    @staticmethod
    def save_performance_data(user, surec_id: int, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        from app.models.legacy_bridge import (
            db, Surec, User, BireyselPerformansGostergesi,
            PerformansGostergeVeri, SurecPerformansGostergesi
        )
        from services.performance_service import (
            get_last_friday_of_month, get_last_friday_of_quarter, 
            get_last_friday_of_year, get_last_friday_of_week, get_last_friday_of_day,
            hesapla_durum
        )
        from datetime import datetime
        from app.utils.errors import ResourceNotFoundError, AuthorizationError

        yil = int(data.get('yil') or datetime.now().year)
        pg_verileri = data.get('pg_verileri') or []

        for veri in pg_verileri:
            pg_id = int(veri.get('pg_id', 0))
            surec_pg_id = int(veri.get('surec_pg_id', 0))

            veri_sahibi_id = veri.get('user_id') or veri.get('kullanici_id')
            veri_sahibi_id = int(veri_sahibi_id) if veri_sahibi_id else int(user.id)

            if user.sistem_rol != 'admin':
                veri_sahibi = User.query.get(veri_sahibi_id)
                if not veri_sahibi:
                    raise ResourceNotFoundError("Kullanıcı bulunamadı")
                if veri_sahibi.kurum_id != user.kurum_id:
                    raise AuthorizationError("Bu kullanıcı üzerinde işlem yetkiniz yok")

            surec_pg = None
            if surec_pg_id > 0:
                surec_pg = SurecPerformansGostergesi.query.get(surec_pg_id)
                if not surec_pg or surec_pg.surec_id != surec_id:
                    raise ValueError("Geçersiz süreç performans göstergesi")

            periyot_tipi = veri.get('periyot_tipi')
            periyot_no = veri.get('periyot_no')
            ceyrek = int(veri.get('ceyrek', 0))
            ay = int(veri.get('ay', 0))
            field = veri.get('field')
            value = veri.get('value')
            aciklama = veri.get('aciklama', '')

            if pg_id == 0 and surec_pg_id > 0:
                if not surec_pg:
                    continue

                bireysel_pg = BireyselPerformansGostergesi(
                    user_id=veri_sahibi_id,
                    ad=surec_pg.ad,
                    aciklama=surec_pg.aciklama,
                    hedef_deger=surec_pg.hedef_deger,
                    olcum_birimi=surec_pg.olcum_birimi,
                    periyot=surec_pg.periyot,
                    kaynak='Süreç',
                    kaynak_surec_id=surec_id,
                    kaynak_surec_pg_id=surec_pg_id,
                    agirlik=surec_pg.agirlik if hasattr(surec_pg, 'agirlik') else 0,
                    onemli=surec_pg.onemli if hasattr(surec_pg, 'onemli') else False,
                    kodu=surec_pg.kodu if hasattr(surec_pg, 'kodu') else None
                )
                db.session.add(bireysel_pg)
                db.session.flush()
                pg_id = bireysel_pg.id

            if pg_id == 0:
                continue

            if periyot_tipi:
                if periyot_tipi == 'ceyrek':
                    ceyrek = int(periyot_no) if periyot_no else None
                    ay = None
                elif periyot_tipi == 'aylik':
                    ay = int(periyot_no) if periyot_no else None
                    ceyrek = None
                elif periyot_tipi == 'yillik':
                    ceyrek = None
                    ay = None
                else:
                    ay = int(veri.get('ay', 0)) if veri.get('ay') else None
            elif ceyrek > 0:
                periyot_tipi = 'ceyrek'
                periyot_no = ceyrek
                ay = None
            elif ay > 0:
                periyot_tipi = 'aylik'
                periyot_no = ay
                ceyrek = None
            else:
                periyot_tipi = 'yillik'
                periyot_no = None
                ceyrek = None
                ay = None

            if periyot_tipi == 'ceyrek' and periyot_no:
                veri_tarihi = get_last_friday_of_quarter(int(periyot_no), yil)
            elif periyot_tipi == 'aylik' and periyot_no:
                veri_tarihi = get_last_friday_of_month(int(periyot_no), yil)
            elif periyot_tipi == 'yillik':
                veri_tarihi = get_last_friday_of_year(yil)
            elif periyot_tipi == 'haftalik' and periyot_no and ay:
                veri_tarihi = get_last_friday_of_week(int(ay), int(periyot_no), yil)
            elif periyot_tipi == 'gunluk' and periyot_no and ay:
                veri_tarihi = get_last_friday_of_day(int(ay), int(periyot_no), yil)
            else:
                veri_tarihi = datetime.now().date()

            bireysel_pg = BireyselPerformansGostergesi.query.get(pg_id)
            if not bireysel_pg:
                raise ResourceNotFoundError("Performans göstergesi bulunamadı")
            if bireysel_pg.user_id != veri_sahibi_id:
                raise AuthorizationError("Bu gösterge üzerinde yetkiniz yok")

            if bireysel_pg.kaynak == 'Süreç':
                if bireysel_pg.kaynak_surec_id != surec_id:
                    raise AuthorizationError("Bu süreçte yetkiniz yok")
            elif bireysel_pg.kaynak_surec_pg_id:
                kaynak_surec_pg = SurecPerformansGostergesi.query.get(bireysel_pg.kaynak_surec_pg_id)
                if not kaynak_surec_pg or kaynak_surec_pg.surec_id != surec_id:
                    raise AuthorizationError("Bu süreçte yetkiniz yok")

            pg_veri = PerformansGostergeVeri.query.filter_by(
                bireysel_pg_id=pg_id,
                user_id=veri_sahibi_id,
                yil=yil,
                veri_tarihi=veri_tarihi
            ).first()

            if not pg_veri:
                pg_veri = PerformansGostergeVeri(
                    bireysel_pg_id=pg_id,
                    user_id=veri_sahibi_id,
                    yil=yil,
                    veri_tarihi=veri_tarihi,
                    giris_periyot_tipi=periyot_tipi,
                    giris_periyot_no=periyot_no,
                    giris_periyot_ay=ay,
                    ceyrek=ceyrek if ceyrek else None,
                    ay=ay if ay else None,
                    created_by=user.id
                )
                db.session.add(pg_veri)
            else:
                pg_veri.giris_periyot_tipi = periyot_tipi
                pg_veri.giris_periyot_no = periyot_no
                pg_veri.giris_periyot_ay = ay
                pg_veri.ceyrek = ceyrek if ceyrek else None
                pg_veri.ay = ay if ay else None
                pg_veri.updated_by = user.id

            if field == 'hedef':
                pg_veri.hedef_deger = value
            elif field == 'gerceklesen':
                pg_veri.gerceklesen_deger = value
                pg_veri.veri_tarihi = veri_tarihi
                if aciklama:
                    pg_veri.aciklama = aciklama
                pg_veri.updated_by = user.id

                if pg_veri.hedef_deger and pg_veri.gerceklesen_deger:
                    durum, durum_yuzdesi = hesapla_durum(
                        float(pg_veri.hedef_deger) if pg_veri.hedef_deger else None,
                        float(pg_veri.gerceklesen_deger) if pg_veri.gerceklesen_deger else None,
                        # B3: azalan gostergelerde oran ters cikiyordu.
                        direction=getattr(pg_veri.individual_pg, 'direction', 'Increasing'),
                    )
                    pg_veri.durum = durum
                    pg_veri.durum_yuzdesi = durum_yuzdesi

        db.session.commit()

        try:
            kurum_id = getattr(user, 'kurum_id', None)
            if kurum_id:
                from services.score_engine_service import recalc_on_pg_data_change
                recalc_on_pg_data_change(kurum_id)
        except Exception as ex:
            current_app.logger.debug(f"Skor motoru güncellemesi atlandı: {ex}")

        return {'success': True, 'message': 'Veriler başarıyla kaydedildi'}, 200

    # KOD-04: get_pg_veri_detay_list / export_surec_karnesi_excel_service / get_pg_veri_detay /
    # get_pg_veri_detay_toplu / update_pg_veri kaldırıldı (60 tanımsız ad, her çağrı 500; tek istemci
    # ölü static/js/surec_karnesi.js). Modern karne: micro/modules/surec/routes_karne.py.
