# -*- coding: utf-8 -*-
"""
Proje Yönetimi Servisleri

Task durumu "Tamamlandı" olduğunda otomatik PG veri girişi iş mantığı.
"""

from datetime import datetime, date
from typing import Optional
from flask import current_app
from sqlalchemy import event
from models import (
    db, Task, TaskImpact, BireyselPerformansGostergesi, 
    PerformansGostergeVeri, SurecPerformansGostergesi, TaskSubtask
)
from services.performance_service import (
    get_last_friday_of_month, get_last_friday_of_quarter,
    get_last_friday_of_year, get_ay_ceyreği, get_last_weekday_before_weekend,
    hesapla_durum
)


def handle_task_completion(task: Task, old_status: Optional[str] = None) -> int:
    """
    Task durumu "Tamamlandı" olduğunda Task_Impact tablosundaki 
    tüm ilişkili PG'lere otomatik veri girişi yapar.
    
    Transaction korumalı: Eğer PG verisi yazılırken hata oluşursa,
    görevin durumu eski haline döndürülür (rollback).
    
    Args:
        task: Tamamlanan Task nesnesi
        old_status: Önceki durum (opsiyonel, rollback için kullanılır)
    
    Returns:
        int: İşlenen PG verisi sayısı (0 ise hiç işlenmedi)
    """
    if task.status != 'Tamamlandı':
        return 0
    
    islenen_pg_sayisi = 0
    
    # Task'ın tamamlanma tarihini belirle
    tamamlanma_tarihi = task.completed_at.date() if task.completed_at else (
        task.due_date if task.due_date else date.today()
    )
    
    yil = tamamlanma_tarihi.year
    ay = tamamlanma_tarihi.month
    ceyrek = get_ay_ceyreği(ay)
    
    # Task'ın tüm impact'lerini bul (sadece işlenmemiş olanları)
    impacts = TaskImpact.query.filter_by(
        task_id=task.id,
        is_processed=False  # Mükerrer veri kontrolü: Sadece işlenmemiş impact'leri al
    ).all()
    
    if not impacts:
        if current_app:
            current_app.logger.info(f"Task {task.id} için işlenmemiş impact bulunamadı")
        return 0
    
    # Transaction başlat (subtransaction kullanarak)
    savepoint = None
    try:
        # SQL Server için savepoint oluştur
        savepoint = db.session.begin_nested()
        
        for impact in impacts:
            # Sadece PG ile ilişkili impact'leri işle
            if not impact.related_pg_id:
                continue
            
            try:
                # Bireysel PG'yi bul
                bireysel_pg = BireyselPerformansGostergesi.query.get(impact.related_pg_id)
                if not bireysel_pg:
                    if current_app:
                        current_app.logger.warning(f"Bireysel PG {impact.related_pg_id} bulunamadı")
                    continue
                
                # Süreç PG'sinin hesaplama yöntemini al (kaynak_surec_pg_id üzerinden)
                hesaplama_yontemi = None
                if bireysel_pg.kaynak_surec_pg_id:
                    surec_pg = SurecPerformansGostergesi.query.get(bireysel_pg.kaynak_surec_pg_id)
                    if surec_pg:
                        hesaplama_yontemi = surec_pg.veri_toplama_yontemi or 'Ortalama'
                
                # PG'nin periyodunu al
                pg_periyot = bireysel_pg.periyot or 'Aylık'
                
                # Periyoda göre veri tarihini hesapla
                veri_tarihi = _calculate_veri_tarihi(tamamlanma_tarihi, pg_periyot, yil, ay, ceyrek)
                
                # Veri tarihini periyoda göre normalize et
                giris_periyot_tipi, giris_periyot_no, giris_periyot_ay = _get_periyot_bilgileri(
                    pg_periyot, tamamlanma_tarihi, yil, ay, ceyrek
                )
                
                # Mevcut veriyi kontrol et (aynı tarih için)
                # NOT: Görev durumu sonradan değişse bile oluşturulan PG verisini SİLMEYİZ
                # Bu yüzden sadece aynı tarih için kayıt yoksa yeni kayıt oluşturuyoruz
                # PERFORMANS: Sadece sistem tarafından oluşturulan kayıtları kontrol et
                mevcut_veri = PerformansGostergeVeri.query.filter_by(
                    bireysel_pg_id=bireysel_pg.id,
                    yil=yil,
                    veri_tarihi=veri_tarihi
                ).first()
                
                # Geçmiş tarihli görev için log
                if current_app and tamamlanma_tarihi < date.today():
                    current_app.logger.info(
                        f"Geçmiş tarihli görev tamamlandı: Task {task.id}, "
                        f"Tamamlanma Tarihi: {tamamlanma_tarihi}, "
                        f"Veri Tarihi: {veri_tarihi}, "
                        f"Periyot: {pg_periyot}"
                    )
                
                if mevcut_veri:
                    # Mevcut veri varsa, sistem tarafından oluşturulmuş mu kontrol et
                    # Eğer aciklama'da "Sistem tarafından" yazıyorsa güncelleme yapma
                    if mevcut_veri.aciklama and 'Sistem tarafından Proje Görevi' in mevcut_veri.aciklama:
                        if current_app:
                            current_app.logger.info(
                                f"PG {bireysel_pg.id} için {veri_tarihi} tarihinde sistem kaydı mevcut, güncelleme yapılmıyor"
                            )
                        continue
                    # Eğer manuel kayıt varsa, yeni bir kayıt oluştur (impact_value'yu ekle)
                    # Ama hesaplama yöntemine göre mevcut değerle toplama/ortalama yapmak yerine
                    # yeni değeri direkt ekliyoruz (impact_value direkt kullanılıyor)
                    pass
                
                # Yeni veri oluştur
                impact_value = impact.impact_value
                
                # Hesaplama yöntemi "Toplam" ise ve mevcut veri varsa, mevcut değere ekle
                if hesaplama_yontemi in ['Toplam', 'Toplama'] and mevcut_veri:
                    try:
                        mevcut_deger = float(mevcut_veri.gerceklesen_deger) if mevcut_veri.gerceklesen_deger else 0
                        yeni_deger = mevcut_deger + float(impact_value)
                        impact_value = str(yeni_deger)
                    except (ValueError, TypeError):
                        # Dönüştürme hatası varsa, impact_value'yu olduğu gibi kullan
                        pass
                
                # Yeni kayıt oluştur (eğer mevcut veri yoksa veya Toplam yöntemi kullanılıyorsa güncelle)
                if not mevcut_veri:
                    # Hedef değeri de ekle (eğer PG'de varsa)
                    hedef_deger = None
                    if bireysel_pg.hedef_deger:
                        hedef_deger = bireysel_pg.hedef_deger
                    elif bireysel_pg.kaynak_surec_pg_id:
                        surec_pg = SurecPerformansGostergesi.query.get(bireysel_pg.kaynak_surec_pg_id)
                        if surec_pg and surec_pg.hedef_deger:
                            hedef_deger = surec_pg.hedef_deger
                    
                    pg_veri = PerformansGostergeVeri(
                        bireysel_pg_id=bireysel_pg.id,
                        user_id=bireysel_pg.user_id,  # PG sahibinin ID'si
                        yil=yil,
                        veri_tarihi=veri_tarihi,
                        gerceklesen_deger=impact_value,
                        hedef_deger=hedef_deger,  # Hedef değeri de ekle
                        giris_periyot_tipi=giris_periyot_tipi,
                        giris_periyot_no=giris_periyot_no,
                        giris_periyot_ay=giris_periyot_ay,
                        ceyrek=ceyrek if giris_periyot_tipi == 'ceyrek' else None,
                        ay=ay if giris_periyot_tipi == 'aylik' else None,
                        aciklama=f"Sistem tarafından Proje Görevi (Task ID: {task.id}, '{task.title}') aracılığıyla otomatik oluşturuldu",
                        created_by=bireysel_pg.user_id
                    )
                    db.session.add(pg_veri)
                    
                    # Durum hesaplama (hedef ve gerçekleşen varsa)
                    if hedef_deger and impact_value:
                        try:
                            durum, durum_yuzdesi = hesapla_durum(
                                float(hedef_deger) if hedef_deger else None,
                                float(impact_value) if impact_value else None
                            )
                            pg_veri.durum = durum
                            pg_veri.durum_yuzdesi = durum_yuzdesi
                        except Exception as e:
                            if current_app:
                                current_app.logger.warning(f"PG veri durumu hesaplanamadı: {e}")
                elif hesaplama_yontemi in ['Toplam', 'Toplama']:
                    # Toplam yöntemi için mevcut kaydı güncelle
                    mevcut_veri.gerceklesen_deger = impact_value
                    mevcut_veri.aciklama = f"{mevcut_veri.aciklama or ''}; Sistem tarafından Proje Görevi (Task ID: {task.id}) ile güncellendi"
                    mevcut_veri.updated_by = bireysel_pg.user_id
                    
                    # Durum hesaplama (güncellenmiş değer için)
                    if mevcut_veri.hedef_deger and impact_value:
                        try:
                            durum, durum_yuzdesi = hesapla_durum(
                                float(mevcut_veri.hedef_deger) if mevcut_veri.hedef_deger else None,
                                float(impact_value) if impact_value else None
                            )
                            mevcut_veri.durum = durum
                            mevcut_veri.durum_yuzdesi = durum_yuzdesi
                        except Exception as e:
                            if current_app:
                                current_app.logger.warning(f"PG veri durumu hesaplanamadı: {e}")
                
                if current_app:
                    current_app.logger.info(
                        f"Task {task.id} tamamlandı, PG {bireysel_pg.id} için veri oluşturuldu: "
                        f"tarih={veri_tarihi}, değer={impact_value}, hedef={hedef_deger or 'yok'}"
                    )
                
                # Impact'i işlendi olarak işaretle (mükerrer veri kontrolü)
                impact.is_processed = True
                impact.processed_at = datetime.utcnow()
                
                islenen_pg_sayisi += 1
            
            except Exception as e:
                if current_app:
                    current_app.logger.error(
                        f"Task {task.id} tamamlandığında PG veri girişi hatası (Impact ID: {impact.id}): {str(e)}"
                    )
                import traceback
                if current_app:
                    current_app.logger.error(traceback.format_exc())
                # Bu impact için hata oluştu, diğerlerine devam et
                continue
        
        # Tüm impact'ler başarıyla işlendiyse savepoint'i commit et
        savepoint.commit()
        
    except Exception as e:
        # Genel hata: Tüm transaction'ı rollback et
        if savepoint:
            savepoint.rollback()
        
        # Görevin durumunu eski haline döndür (eğer old_status verilmişse)
        if old_status and task.status == 'Tamamlandı':
            task.status = old_status
            task.completed_at = None
            if current_app:
                current_app.logger.warning(
                    f"Task {task.id} tamamlandığında genel hata oluştu, durum eski haline döndürüldü: {old_status}"
                )
        
        if current_app:
            current_app.logger.error(
                f"Task {task.id} tamamlandığında transaction hatası: {str(e)}"
            )
            import traceback
            current_app.logger.error(traceback.format_exc())
        
        # Hata durumunda 0 döndür (hiçbir veri işlenmedi)
        return 0
    
    # NOT: Ana commit yapılmıyor - çağıran kod commit yapacak
    # Bu sayede transaction kontrolü API endpoint'inde oluyor
    return islenen_pg_sayisi


def update_task_progress_from_subtasks(task_id):
    """
    Görevin ilerleme yüzdesini alt görevlerden otomatik hesapla
    
    Args:
        task_id: Görev ID
    """
    try:
        task = Task.query.get(task_id)
        if not task:
            return
        
        subtasks = TaskSubtask.query.filter_by(task_id=task_id).all()
        
        if subtasks:
            completed_count = sum(1 for st in subtasks if st.is_completed)
            progress = int((completed_count / len(subtasks)) * 100)
            task.progress = progress
            db.session.commit()
        else:
            # Alt görev yoksa progress'i güncelleme
            pass
    except Exception as e:
        db.session.rollback()
        if current_app:
            current_app.logger.error(f'Görev ilerleme güncelleme hatası: {e}')


def _calculate_veri_tarihi(tamamlanma_tarihi: date, pg_periyot: str, yil: int, ay: int, ceyrek: Optional[int]) -> date:
    """
    PG periyoduna göre veri tarihini hesapla.
    
    Args:
        tamamlanma_tarihi: Görevin tamamlanma tarihi
        pg_periyot: PG periyodu (Aylık, Çeyreklik, Yıllık, Haftalık, Günlük)
        yil: Yıl
        ay: Ay
        ceyrek: Çeyrek (opsiyonel)
    
    Returns:
        date: Veri kaydetme tarihi (periyodun son Cuma'sı veya günün kendisi)
    """
    pg_periyot_lower = pg_periyot.lower() if pg_periyot else 'aylik'
    
    # Türkçe karakterleri normalize et
    if 'çeyrek' in pg_periyot_lower or 'ceyrek' in pg_periyot_lower:
        if ceyrek:
            return get_last_friday_of_quarter(ceyrek, yil)
        else:
            return get_last_friday_of_quarter(get_ay_ceyreği(ay), yil)
    elif 'yıllık' in pg_periyot_lower or 'yillik' in pg_periyot_lower:
        return get_last_friday_of_year(yil)
    elif 'haftalık' in pg_periyot_lower or 'haftalik' in pg_periyot_lower:
        # Haftalık için, o haftanın son Cuma'sını döndür
        return get_last_weekday_before_weekend(tamamlanma_tarihi)
    elif 'günlük' in pg_periyot_lower or 'gunluk' in pg_periyot_lower:
        # Günlük için direkt tarihi döndür
        return tamamlanma_tarihi
    else:  # Aylık (varsayılan)
        return get_last_friday_of_month(ay, yil)


def _get_periyot_bilgileri(pg_periyot: str, tamamlanma_tarihi: date, yil: int, ay: int, ceyrek: Optional[int]) -> tuple:
    """
    Periyot tipi, numarası ve ay bilgilerini döndür.
    
    Returns:
        tuple: (periyot_tipi, periyot_no, periyot_ay)
    """
    pg_periyot_lower = pg_periyot.lower() if pg_periyot else 'aylik'
    
    if 'çeyrek' in pg_periyot_lower or 'ceyrek' in pg_periyot_lower:
        ceyrek_no = ceyrek if ceyrek else get_ay_ceyreği(ay)
        return ('ceyrek', ceyrek_no, None)
    elif 'yıllık' in pg_periyot_lower or 'yillik' in pg_periyot_lower:
        return ('yillik', None, None)
    elif 'haftalık' in pg_periyot_lower or 'haftalik' in pg_periyot_lower:
        # Hafta numarasını hesaplamak için performance_service'i kullanabiliriz
        # Basit olarak ayı kullanıyoruz
        return ('haftalik', None, ay)
    elif 'günlük' in pg_periyot_lower or 'gunluk' in pg_periyot_lower:
        return ('gunluk', tamamlanma_tarihi.day, ay)
    else:  # Aylık (varsayılan)
        return ('aylik', ay, None)


# NOT: Event listener kaldırıldı - PG veri girişi API endpoint'inden manuel çağrılıyor
# Bu sayede flash message için işlenen PG sayısı doğru şekilde döndürülebiliyor
# SQLAlchemy Event Listener - Task güncellemelerini dinle (Devre dışı)
# @event.listens_for(Task, 'after_update')
# def task_status_changed(mapper, connection, target):
#     """Task durumu güncellendiğinde çağrılır"""
#     # Bu listener artık kullanılmıyor - API endpoint'inden manuel çağrılıyor



























