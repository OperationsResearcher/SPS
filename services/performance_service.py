# -*- coding: utf-8 -*-
"""
Performans Göstergesi Hesaplama Servisleri

Bu modül, performans göstergeleri için hedef değer hesaplama, periyot verileri oluşturma
ve veri toplama/agregasyon işlemlerini içerir.

Flask bağımlılıklarından bağımsızdır, sadece SQLAlchemy ve iş mantığı içerir.
SQL Server uyumlu olarak tasarlanmıştır.
"""

from datetime import datetime, date, timedelta
from calendar import monthrange
from typing import List, Dict, Optional, Tuple, Any
from flask import current_app
from sqlalchemy import or_, and_
from models import BireyselPerformansGostergesi, PerformansGostergeVeri


# ============================================================================
# Yardımcı Fonksiyonlar (Tarih Hesaplamaları)
# ============================================================================

def get_last_weekday_before_weekend(tarih: date) -> date:
    """
    Eğer tarih hafta içi (Pazartesi-Cuma) ise tarihi döndürür.
    Eğer hafta sonu (Cumartesi-Pazar) ise önceki Cuma'yı döndürür.
    
    Args:
        tarih: datetime.date veya datetime.datetime nesnesi
    
    Returns:
        date: Hafta içi ise tarih, hafta sonu ise önceki Cuma
    """
    if isinstance(tarih, datetime):
        tarih = tarih.date()
    
    # Haftanın hangi günü? (0=Pazartesi, 4=Cuma, 5=Cumartesi, 6=Pazar)
    gun_indeks = tarih.weekday()
    
    if gun_indeks <= 4:  # Pazartesi-Cuma arası (hafta içi)
        return tarih
    else:  # Cumartesi veya Pazar (hafta sonu)
        # Önceki Cuma'ya git
        gun_farki = gun_indeks - 4  # Cumartesi için 1, Pazar için 2
        return tarih - timedelta(days=gun_farki)


def get_last_friday_of_month(ay: int, yil: int) -> date:
    """Bir ayın son gününü döndürür - hafta içi ise son gün, hafta sonu ise son cuma"""
    # Ayın son gününü bul
    _, gun_sayisi = monthrange(yil, ay)
    ay_son_gunu = datetime(yil, ay, gun_sayisi).date()
    
    # Hafta içi ise son gün, hafta sonu ise son cuma
    return get_last_weekday_before_weekend(ay_son_gunu)


def get_last_friday_of_year(yil: int) -> date:
    """Bir yılın son gününü döndürür - hafta içi ise son gün, hafta sonu ise son cuma"""
    yil_son_gunu = datetime(yil, 12, 31).date()
    return get_last_weekday_before_weekend(yil_son_gunu)


def get_last_friday_of_quarter(ceyrek: int, yil: int) -> date:
    """Bir çeyreğin son gününü döndürür - hafta içi ise son gün, hafta sonu ise son cuma"""
    # Çeyreğin son ayını bul
    son_ay = ceyrek * 3  # 1->3, 2->6, 3->9, 4->12
    _, gun_sayisi = monthrange(yil, son_ay)
    ceyrek_son_gunu = datetime(yil, son_ay, gun_sayisi).date()
    
    # Hafta içi ise son gün, hafta sonu ise son cuma
    return get_last_weekday_before_weekend(ceyrek_son_gunu)


def get_last_friday_of_week(ay: int, hafta_no: int, yil: int) -> date:
    """
    Bir haftanın son Cuma'sını PDF mantığına göre döndürür.
    
    Not: hafta_no artık yıl genelinde numaralandırılmış (1-52).
    ay parametresi sadece filtreleme için kullanılır.
    
    Args:
        ay: Ay numarası (1-12) - filtreleme için
        hafta_no: Yıl genelinde hafta numarası (1-52)
        yil: Yıl
    
    Returns:
        date: Haftanın son Cuma'sı (veri kaydetme tarihi)
    """
    # Yılın tüm haftalarını al
    yil_haftalari = get_yil_haftalari_pdf_format(yil)
    
    # Belirtilen hafta numarasını bul
    for hafta in yil_haftalari:
        if hafta['hafta_no'] == hafta_no:
            # Haftanın veri tarihini döndür (son Cuma)
            return hafta.get('veri_tarihi', hafta['bitis_tarih'])
    
    # Hafta bulunamadıysa, ayın son Cuma'sını döndür
    return get_last_friday_of_month(ay, yil)


def get_last_friday_of_day(ay: int, gun: int, yil: int) -> date:
    """Bir günün tarihini döndürür (günün kendisi)"""
    try:
        return datetime(yil, ay, gun).date()
    except ValueError:
        # Geçersiz tarih (örn. 31 Şubat) - ayın son gününü döndür
        _, gun_sayisi = monthrange(yil, ay)
        return datetime(yil, ay, gun_sayisi).date()


def get_yil_haftalari_pdf_format(yil: int) -> List[Dict[str, Any]]:
    """
    PDF'deki takvim mantığına göre yılın tüm haftalarını oluşturur.
    
    Özellikler:
    - Yılın ilk Pazartesi'sinden başlar (önceki yıldan başlayabilir)
    - Yıl genelinde 1-52 arası numaralandırma
    - Her hafta Pazartesi-Pazar (7 gün) - gösterim için
    - Veri kaydetme tarihi: Haftanın son Cuma'sı (iş günü mantığı)
    - Ay sınırlarını geçen haftalar dahil
    
    Returns:
        List[Dict]: Her hafta için {
            'hafta_no': int, 
            'baslangic_tarih': date (Pazartesi), 
            'bitis_tarih': date (Pazar - gösterim için),
            'veri_tarihi': date (Cuma - veri kaydetme için)
        }
    """
    haftalar = []
    
    # Yılın ilk günü
    ilk_gun = datetime(yil, 1, 1)
    
    # İlk Pazartesi'yi bul (PDF mantığı: yılın ilk Pazartesi'si)
    gun_indeks = ilk_gun.weekday()  # 0=Pazartesi, 6=Pazar
    if gun_indeks == 0:
        ilk_pazartesi = ilk_gun
    else:
        # Bir sonraki Pazartesi (ama önceki yıldan başlayabilir)
        # Eğer yılın 1'i Pazartesi değilse, o haftanın Pazartesi'sini bul
        ilk_pazartesi = ilk_gun - timedelta(days=gun_indeks)
    
    # Yılın son günü
    son_gun = datetime(yil, 12, 31)
    
    # Son Pazar'ı bul (yılın son Pazar'ı) - gösterim için
    son_gun_indeks = son_gun.weekday()
    if son_gun_indeks == 6:  # Pazar
        son_pazar = son_gun
    else:
        # Bir sonraki Pazar (ama yılın dışına çıkabilir)
        son_pazar = son_gun + timedelta(days=(6 - son_gun_indeks))
        if son_pazar.year != yil:
            # Yılın son günü Pazar değilse, en son Pazar'ı bul
            son_pazar = son_gun - timedelta(days=(son_gun_indeks + 1))
    
    # İlk Pazartesi'den başlayarak tüm haftaları oluştur
    hafta_no = 1
    pazartesi = ilk_pazartesi
    
    # Yılın son Pazar'ına kadar devam et
    while pazartesi.date() <= son_pazar.date():
        # Haftanın Pazar'ını bul (Pazartesi + 6 gün)
        pazar = pazartesi + timedelta(days=6)
        
        # Pazar yılın son Pazar'ından sonraysa, son Pazar'ı kullan
        if pazar.date() > son_pazar.date():
            pazar = son_pazar
        
        # Haftanın son Cuma'sını bul (veri kaydetme tarihi için)
        # Pazartesi + 4 gün = Cuma
        cuma = pazartesi + timedelta(days=4)
        
        # Eğer Cuma yılın dışındaysa, haftanın son iş gününü bul
        if cuma.year != yil or cuma.date() > pazar.date():
            # Haftanın son iş gününü bul (Pazar'dan önceki son Cuma)
            if pazar.weekday() >= 4:  # Cuma, Cumartesi veya Pazar
                cuma = pazar - timedelta(days=(pazar.weekday() - 4))
            else:  # Pazartesi-Perşembe
                # Önceki Cuma'yı bul
                cuma = pazar - timedelta(days=(pazar.weekday() + 3))
        
        # Haftayı ekle (yılın içindeki veya yılı kapsayan haftalar)
        haftalar.append({
            'hafta_no': hafta_no,
            'baslangic_tarih': pazartesi.date(),  # Pazartesi - gösterim için
            'bitis_tarih': pazar.date(),  # Pazar - gösterim için (7 gün)
            'veri_tarihi': cuma.date()  # Cuma - veri kaydetme için (iş günü)
        })
        
        hafta_no += 1
        pazartesi = pazartesi + timedelta(days=7)
        
        # Maksimum 52 hafta (PDF standardı)
        if hafta_no > 52:
            break
    
    return haftalar


def get_yil_haftalari(yil: int) -> List[Dict[str, Any]]:
    """Yılın TÜM haftalarını döndürür (Pazartesi-Cuma, son Cuma = veri_tarihi)
    
    Not: Bu fonksiyon PDF mantığını kullanır. Eski kod için geriye dönük uyumluluk.
    """
    return get_yil_haftalari_pdf_format(yil)


def get_yil_gunleri(yil: int) -> List[Dict[str, Any]]:
    """Yılın TÜM günlerini döndürür"""
    gunler = []
    gun_no = 1
    
    baslangic = datetime(yil, 1, 1)
    bitis = datetime(yil, 12, 31)
    
    current = baslangic
    while current <= bitis:
        gunler.append({
            'gun_no': gun_no,
            'tarih': current.date(),
            'ay': current.month,
            'gun': current.day
        })
        gun_no += 1
        current += timedelta(days=1)
    
    return gunler


def get_ay_haftalari(ay: int, yil: int) -> List[Dict[str, Any]]:
    """
    Bir ayın haftalarını PDF mantığına göre döndürür.
    
    PDF mantığı:
    - Yıl genelinde hafta numaraları kullanılır (1-52)
    - Haftalar Pazartesi-Pazar (7 gün) gösterilir
    - Eğer bir haftanın iki ayda da günü varsa her iki ayda da görünür
    - Örneğin Ocak'ta Hafta 05 (27 Ocak - 2 Şubat) Şubat'ta da görünür
    
    Args:
        ay: Ay numarası (1-12)
        yil: Yıl
    
    Returns:
        List[Dict]: Belirtilen ayın haftaları (yıl genelinde numaralandırılmış)
    """
    # Yılın tüm haftalarını al (PDF mantığına göre)
    yil_haftalari = get_yil_haftalari_pdf_format(yil)
    
    # Ayın ilk ve son günlerini bul
    _, gun_sayisi = monthrange(yil, ay)
    ay_ilk_gun = datetime(yil, ay, 1).date()
    ay_son_gun = datetime(yil, ay, gun_sayisi).date()
    
    # Bu ayı kapsayan veya ayın içindeki haftaları filtrele
    # Mantık: Bir hafta ayın herhangi bir gününü kapsıyorsa o ayda görünür
    ay_haftalari = []
    for hafta in yil_haftalari:
        baslangic = hafta['baslangic_tarih']  # Pazartesi
        bitis = hafta['bitis_tarih']  # Pazar
        
        # Hafta bu ayı kapsıyor mu kontrol et:
        # 1. Haftanın başlangıcı (Pazartesi) ayın içinde
        # 2. Haftanın bitişi (Pazar) ayın içinde
        # 3. Hafta ayın ilk gününü içeriyor
        # 4. Hafta ayın son gününü içeriyor
        # 5. Hafta ayın hemen öncesinde veya sonrasında (ay sınırını geçiyor)
        if (baslangic.month == ay or bitis.month == ay or 
            (baslangic <= ay_ilk_gun <= bitis) or 
            (baslangic <= ay_son_gun <= bitis)):
            ay_haftalari.append(hafta)
    
    return ay_haftalari


def get_ay_gunleri(ay: int, yil: int) -> List[Dict[str, Any]]:
    """Bir ayın tüm günlerini döndürür"""
    _, gun_sayisi = monthrange(yil, ay)
    
    gunler = []
    for gun in range(1, gun_sayisi + 1):
        gunler.append({
            'gun_no': gun,
            'tarih': datetime(yil, ay, gun).date()
        })
    
    return gunler


def get_ceyrek_aylari(ceyrek: int) -> List[int]:
    """Çeyrekten ayları hesapla"""
    if ceyrek == 1:
        return [1, 2, 3]  # Ocak, Şubat, Mart
    elif ceyrek == 2:
        return [4, 5, 6]  # Nisan, Mayıs, Haziran
    elif ceyrek == 3:
        return [7, 8, 9]  # Temmuz, Ağustos, Eylül
    elif ceyrek == 4:
        return [10, 11, 12]  # Ekim, Kasım, Aralık
    return []


def get_ay_ceyreği(ay: int) -> Optional[int]:
    """Aydan çeyreği hesapla"""
    if ay in [1, 2, 3]:
        return 1
    elif ay in [4, 5, 6]:
        return 2
    elif ay in [7, 8, 9]:
        return 3
    elif ay in [10, 11, 12]:
        return 4
    return None


# ============================================================================
# Ana Hesaplama Fonksiyonları
# ============================================================================

def calculateHedefDeger(
    pg_hedef_deger: Optional[str],
    pg_periyot: Optional[str],
    gosterim_periyot: str,
    hesaplama_yontemi: Optional[str]
) -> Optional[float]:
    """
    PG hedef değerini gösterim periyoduna göre hesapla
    
    Args:
        pg_hedef_deger: Performans göstergesi hedef değeri (string veya sayı)
        pg_periyot: PG periyodu (Aylık, Çeyreklik, Yıllık, Haftalık, Günlük)
        gosterim_periyot: Gösterim periyodu (yillik, ceyrek, aylik, haftalik, gunluk)
        hesaplama_yontemi: Hesaplama yöntemi (Toplam, Ortalama, Son Değer)
    
    Returns:
        float: Hesaplanmış hedef değer veya None
    """
    if not pg_hedef_deger:
        return None
    
    try:
        hedef = float(pg_hedef_deger)
    except (ValueError, TypeError):
        return pg_hedef_deger  # Sayıya çevrilemezse olduğu gibi döndür
    
    # Eğer hesaplama yöntemi Toplam değilse, hedef aynı kalır
    if hesaplama_yontemi not in ['Toplam', 'Toplama']:
        return hedef
    
    # Toplam ise gösterim periyoduna göre hesapla
    # PG periyodunu normalize et
    pg_periyot_normalized = pg_periyot.lower() if pg_periyot else 'aylik'
    # Türkçe karakterleri normalize et
    if 'çeyrek' in pg_periyot_normalized or 'çeyreklik' in pg_periyot_normalized:
        pg_periyot_normalized = 'ceyrek'
    elif 'aylık' in pg_periyot_normalized or 'aylik' in pg_periyot_normalized:
        pg_periyot_normalized = 'aylik'
    elif 'yıllık' in pg_periyot_normalized or 'yillik' in pg_periyot_normalized:
        pg_periyot_normalized = 'yillik'
    elif 'haftalık' in pg_periyot_normalized or 'haftalik' in pg_periyot_normalized:
        pg_periyot_normalized = 'haftalik'
    elif 'günlük' in pg_periyot_normalized or 'gunluk' in pg_periyot_normalized:
        pg_periyot_normalized = 'gunluk'
    
    # Gösterim periyoduna göre hedef hesapla
    if gosterim_periyot == 'yillik':
        # Yıllık gösterim
        if pg_periyot_normalized == 'gunluk':
            return hedef * 365
        elif pg_periyot_normalized == 'haftalik':
            return hedef * 52
        elif pg_periyot_normalized == 'aylik':
            return hedef * 12
        elif pg_periyot_normalized == 'ceyrek':
            return hedef * 4
        elif pg_periyot_normalized == 'yillik':
            return hedef
    
    elif gosterim_periyot == 'ceyrek':
        # Çeyreklik gösterim (3 ay)
        if pg_periyot_normalized == 'gunluk':
            return hedef * 90  # 90 gün = 3 ay
        elif pg_periyot_normalized == 'haftalik':
            return hedef * 13  # 13 hafta ≈ 3 ay
        elif pg_periyot_normalized == 'aylik':
            return hedef * 3
        elif pg_periyot_normalized == 'ceyrek':
            return hedef
        elif pg_periyot_normalized == 'yillik':
            return hedef / 4
    
    elif gosterim_periyot == 'aylik':
        # Aylık gösterim
        if pg_periyot_normalized == 'gunluk':
            return hedef * 30  # 30 gün = 1 ay
        elif pg_periyot_normalized == 'haftalik':
            return hedef * 4  # 4 hafta = 1 ay
        elif pg_periyot_normalized == 'aylik':
            return hedef
        elif pg_periyot_normalized == 'ceyrek':
            return hedef / 3
        elif pg_periyot_normalized == 'yillik':
            return hedef / 12
    
    elif gosterim_periyot == 'haftalik':
        # Haftalık gösterim
        if pg_periyot_normalized == 'gunluk':
            return hedef * 7  # 7 gün = 1 hafta
        elif pg_periyot_normalized == 'haftalik':
            return hedef
        elif pg_periyot_normalized == 'aylik':
            return hedef / 4  # 1 ay = 4 hafta
        elif pg_periyot_normalized == 'ceyrek':
            return hedef / 13  # 1 çeyrek = 13 hafta
        elif pg_periyot_normalized == 'yillik':
            return hedef / 52
    
    elif gosterim_periyot == 'gunluk':
        # Günlük gösterim
        if pg_periyot_normalized == 'gunluk':
            return hedef
        elif pg_periyot_normalized == 'haftalik':
            return hedef / 7  # 1 hafta = 7 gün
        elif pg_periyot_normalized == 'aylik':
            return hedef / 30  # 1 ay = 30 gün
        elif pg_periyot_normalized == 'ceyrek':
            return hedef / 90  # 1 çeyrek = 90 gün
        elif pg_periyot_normalized == 'yillik':
            return hedef / 365
    
    # Varsayılan olarak hedef aynı kalır
    return hedef


def hesapla_durum(hedef_deger: Optional[float], gerceklesen_deger: Optional[float]) -> Tuple[Optional[str], Optional[float]]:
    """
    Durum ve durum yüzdesini hesapla
    
    Args:
        hedef_deger: Hedef değer
        gerceklesen_deger: Gerçekleşen değer
    
    Returns:
        Tuple: (durum, durum_yuzdesi) - ('Başarılı', 'Kısmen Başarılı', 'Başarısız' veya None)
    """
    if not hedef_deger or not gerceklesen_deger:
        return None, None
    
    try:
        durum_yuzdesi = (gerceklesen_deger / float(hedef_deger)) * 100
        
        if durum_yuzdesi >= 100:
            durum = 'Başarılı'
        elif durum_yuzdesi >= 75:
            durum = 'Kısmen Başarılı'
        else:
            durum = 'Başarısız'
        
        return durum, durum_yuzdesi
    except:
        return None, None


def get_verileri_topla(
    bireysel_pgler: List[BireyselPerformansGostergesi],
    yil: int,
    periyot_son_cuma_tarihi: Optional[date],
    hesaplama_yontemi: Optional[str],
    periyot_tipi: Optional[str] = None,
    verinin_tarihi_araligi: Optional[Tuple[date, date]] = None
) -> Tuple[Optional[float], List[str], List[int]]:
    """
    Hesaplama yöntemine göre veri toplama:
    - Toplama: İlgili tarihe kadar (<=) girilen tüm PG verileri toplanır
    - Ortalama: İlgili tarihe kadar (<=) PG verilerinin ortalaması alınır
    - Son Değer: İlgili tarihe kadar (<=) girilen en son değer alınır
    
    Args:
        bireysel_pgler: Bireysel PG listesi
        yil: Yıl
        periyot_son_cuma_tarihi: Periyodun son Cuması (gösterim tarihi) - bu tarihe kadar olan veriler alınır
        hesaplama_yontemi: 'Toplama', 'Ortalama' veya 'Son Değer' (None ise varsayılan: Ortalama)
        periyot_tipi: Hangi periyot için (ceyrek, aylik, haftalik, yillik, gunluk)
        verinin_tarihi_araligi: (opsiyonel) Verinin hangi tarih aralığında olması gerektiği
    
    Returns:
        Tuple: (gerceklesen_deger, kullanicilar_listesi, veri_idleri_listesi)
    """
    try:
        # Hesaplama yöntemi None ise varsayılan olarak Ortalama kullan
        if hesaplama_yontemi is None:
            hesaplama_yontemi = 'Ortalama'
        
        # 'Toplama' yerine 'Toplam' kontrolü de yap (eski kodlarla uyumluluk için)
        if hesaplama_yontemi == 'Toplama':
            hesaplama_yontemi = 'Toplam'
        
        veriler = []
        kullanicilar = set()
        veri_idleri = []
        
        # Tarih tipi kontrolü
        if periyot_son_cuma_tarihi is not None and not isinstance(periyot_son_cuma_tarihi, date):
            if current_app:
                current_app.logger.error(f"get_verileri_topla: Geçersiz tarih tipi: {type(periyot_son_cuma_tarihi)}")
            return None, [], []
        
        for bireysel_pg in bireysel_pgler:
            # Tarih aralığı varsa, verilerin sadece o aralıkta olması gerektiğini kontrol et
            # Eğer tarih aralığı yoksa, sadece periyot_son_cuma_tarihi kontrolü yap (geriye dönük uyumluluk)
            if verinin_tarihi_araligi:
                try:
                    baslangic, bitis = verinin_tarihi_araligi
                    # Tarih aralığı ile filtrele - veriler sadece bu periyot içinde olmalı
                    # ÖNEMLİ: Yıllık veriler sadece yılın son periyodunda görünmeli (her ayda değil)
                    # Yıllık veri = veri_tarihi yılın son Cuması, bu yüzden sadece Aralık ayında görünür
                    if hesaplama_yontemi == 'Son Değer':
                        # Son Değer için: O periyodun sonuna kadar (periyot_son_cuma_tarihi) girilen en son değeri al
                        # ÖNEMLİ: Tarih aralığı filtresini IGNORE et, sadece periyodun sonuna kadar olan tüm verileri kontrol et
                        # Bu sayede o periyodun sonuna kadar girilen en son değer gösterilir
                        veri_kayitlari = PerformansGostergeVeri.query.filter(
                            PerformansGostergeVeri.bireysel_pg_id == bireysel_pg.id,
                            PerformansGostergeVeri.yil == yil,
                            PerformansGostergeVeri.veri_tarihi <= periyot_son_cuma_tarihi  # Periyodun sonuna kadar
                        ).order_by(
                            PerformansGostergeVeri.created_at.desc()  # En son oluşturulan (girilen) veri
                        ).limit(1).all()  # Sadece 1 kayıt al
                        
                        # Debug log
                        if current_app and veri_kayitlari:
                            current_app.logger.info(f"Son Değer bulundu: PG {bireysel_pg.id}, Veri Tarihi: {veri_kayitlari[0].veri_tarihi}, Created: {veri_kayitlari[0].created_at}, Değer: {veri_kayitlari[0].gerceklesen_deger}")
                        elif current_app:
                            current_app.logger.warning(f"Son Değer bulunamadı: PG {bireysel_pg.id}, Periyot Son Cuma: {periyot_son_cuma_tarihi}")
                    else:
                        # Toplam ve Ortalama için: Tüm verileri al
                        # Sıralama: En yeni veriler önce (created_at desc) - modal'da en son veriyi göstermek için
                        veri_kayitlari = PerformansGostergeVeri.query.filter(
                            PerformansGostergeVeri.bireysel_pg_id == bireysel_pg.id,
                            PerformansGostergeVeri.yil == yil,
                            PerformansGostergeVeri.veri_tarihi >= baslangic,
                            PerformansGostergeVeri.veri_tarihi <= bitis
                        ).order_by(PerformansGostergeVeri.veri_tarihi.desc(), PerformansGostergeVeri.created_at.desc()).all()
                except Exception as e:
                    if current_app:
                        current_app.logger.error(f"get_verileri_topla: Tarih aralığı sorgusu hatası: {e}")
                    continue
            else:
                # Tarih aralığı yoksa, sadece periyot_son_cuma_tarihi kontrolü yap (geriye dönük uyumluluk)
                if hesaplama_yontemi == 'Son Değer':
                    # Son Değer için: O periyodun sonuna kadar girilen en son değeri al
                    # En son oluşturulan (girilen) veriyi al
                    veri_kayitlari = PerformansGostergeVeri.query.filter(
                        PerformansGostergeVeri.bireysel_pg_id == bireysel_pg.id,
                        PerformansGostergeVeri.yil == yil,
                        PerformansGostergeVeri.veri_tarihi <= periyot_son_cuma_tarihi  # Periyodun sonuna kadar
                    ).order_by(
                        PerformansGostergeVeri.created_at.desc()  # En son oluşturulan (girilen) veri
                    ).limit(1).all()  # Sadece 1 kayıt al
                else:
                    # Toplam ve Ortalama için: Tüm verileri al
                    # Sıralama: En yeni veriler önce (created_at desc) - modal'da en son veriyi göstermek için
                    veri_kayitlari = PerformansGostergeVeri.query.filter(
                        PerformansGostergeVeri.bireysel_pg_id == bireysel_pg.id,
                        PerformansGostergeVeri.yil == yil,
                        PerformansGostergeVeri.veri_tarihi <= periyot_son_cuma_tarihi  # İlgili tarihe kadar
                    ).order_by(PerformansGostergeVeri.veri_tarihi.desc(), PerformansGostergeVeri.created_at.desc()).all()
            
            # Verileri topla
            for veri in veri_kayitlari:
                if veri and veri.gerceklesen_deger is not None:
                    try:
                        deger = float(veri.gerceklesen_deger)
                        veriler.append(deger)
                        veri_idleri.append(veri.id)
                        
                        if veri.user:
                            kullanici_adi = f"{veri.user.first_name} {veri.user.last_name}"
                            kullanicilar.add(kullanici_adi)
                    except (ValueError, TypeError) as e:
                        if current_app:
                            current_app.logger.warning(f"get_verileri_topla: Değer dönüştürme hatası: {e}")
                        pass
        
        # Hesaplama yöntemine göre sonucu hesapla
        if not veriler:
            # Debug log
            if current_app and hesaplama_yontemi == 'Son Değer':
                current_app.logger.warning(f"Son Değer için veri bulunamadı: PG sayısı={len(bireysel_pgler)}, Periyot Son Cuma={periyot_son_cuma_tarihi}")
            return None, [], []
        
        if hesaplama_yontemi == 'Toplam':
            # Tüm verileri topla
            gerceklesen = sum(veriler)
            # veri_idleri için tüm ID'leri kullan (zaten tüm veriler eklendi)
        elif hesaplama_yontemi == 'Son Değer':
            # Son Değer için: En son girilen değeri al
            # Eğer limit(1) ile filtrelenmişse zaten tek eleman var
            # Ama eğer birden fazla bireysel PG varsa, her birinden en son değeri alıp sonra en son girileni seçmeliyiz
            if len(veriler) == 1:
                gerceklesen = veriler[0]
            else:
                # Birden fazla değer varsa, en son girilen değeri al (veri_idleri'ne göre sıralama yapılabilir)
                # Ancak sorgu zaten created_at.desc() ile sıralandığı için ilk eleman en son girilen
                gerceklesen = veriler[0] if veriler else None
            
            # veri_idleri için sadece son verinin ID'sini kullan
            if veri_idleri:
                veri_idleri = [veri_idleri[0]]
        else:  # Ortalama veya varsayılan
            # Verilerin ortalamasını al
            gerceklesen = sum(veriler) / len(veriler)
            # veri_idleri için tüm ID'leri kullan (zaten tüm veriler eklendi)
        
        return gerceklesen, list(kullanicilar), veri_idleri
    
    except Exception as e:
        import traceback
        if current_app:
            current_app.logger.error(f"get_verileri_topla: Beklenmeyen hata: {e}")
            current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return None, [], []


def generatePeriyotVerileri(
    periyot: str,
    pg_id: int,
    yil: int,
    pg_hedef_deger: Optional[str] = None,
    pg_periyot: Optional[str] = None,
    hesaplama_yontemi: Optional[str] = None,
    ay: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Periyoda göre veri yapısı oluştur ve gerçek verileri getir
    
    Args:
        periyot: Gösterim periyodu (ceyrek, aylik, haftalik, gunluk, yillik)
        pg_id: Performans göstergesi ID'si
        yil: Yıl
        pg_hedef_deger: PG hedef değeri
        pg_periyot: PG periyodu
        hesaplama_yontemi: Hesaplama yöntemi
        ay: Ay numarası (1-12) - Sadece haftalık ve günlük görünümler için kullanılır
    
    Returns:
        List[Dict]: Periyot verileri listesi
    """
    veriler = []
    
    # Her periyot için hedef değeri hesapla
    hedef_deger = calculateHedefDeger(pg_hedef_deger, pg_periyot, periyot, hesaplama_yontemi) if pg_hedef_deger else None
    
    # Süreç PG'sine bağlı bireysel PG'leri bul
    bireysel_pgler = BireyselPerformansGostergesi.query.filter_by(
        kaynak_surec_pg_id=pg_id
    ).all()
    
    if periyot == 'ceyrek':
        # 4 çeyrek için veri - HER ZAMAN 4 KOLON - AKILLI GÖSTERİM
        for ceyrek_no in range(1, 5):
            periyot_son_cuma = get_last_friday_of_quarter(ceyrek_no, yil)
            
            # Çeyreğin başlangıç ve bitiş tarihleri
            baslangic_ay = (ceyrek_no - 1) * 3 + 1
            bitis_ay = ceyrek_no * 3
            ceyrek_baslangic = date(yil, baslangic_ay, 1)
            # Bitiş ayının son gününü doğru hesapla
            _, bitis_ay_gun_sayisi = monthrange(yil, bitis_ay)
            ceyrek_bitis = date(yil, bitis_ay, bitis_ay_gun_sayisi)
            
            # Bu çeyrek içindeki verileri topla (akıllı gösterim)
            gerceklesen, kullanicilar, veri_idleri = get_verileri_topla(
                bireysel_pgler, yil, periyot_son_cuma, hesaplama_yontemi,
                'ceyrek', (ceyrek_baslangic, ceyrek_bitis)
            )
            durum, durum_yuzdesi = hesapla_durum(hedef_deger, gerceklesen)
            
            veriler.append({
                'ceyrek': ceyrek_no,
                'hedef_deger': round(hedef_deger, 2) if hedef_deger is not None else '-',
                'gerceklesen_deger': str(round(gerceklesen, 2)) if gerceklesen is not None else None,
                'durum': durum,
                'durum_yuzdesi': durum_yuzdesi,
                'kullanicilar': kullanicilar,
                'veri_idleri': veri_idleri
            })
            
    elif periyot == 'yillik':
        # 1 Yıl - HER ZAMAN 1 KOLON - AKILLI GÖSTERİM
        periyot_son_cuma = get_last_friday_of_year(yil)
        
        # Yılın başlangıç ve bitiş tarihleri
        yil_baslangic = date(yil, 1, 1)
        yil_bitis = date(yil, 12, 31)
        
        # Bu yıl içindeki verileri topla (akıllı gösterim)
        gerceklesen, kullanicilar, veri_idleri = get_verileri_topla(
            bireysel_pgler, yil, periyot_son_cuma, hesaplama_yontemi,
            'yillik', (yil_baslangic, yil_bitis)
        )
        durum, durum_yuzdesi = hesapla_durum(hedef_deger, gerceklesen)
        
        veriler.append({
            'periyot': 'yillik',
            'yil': yil,
            'hedef_deger': round(hedef_deger, 2) if hedef_deger is not None else '-',
            'gerceklesen_deger': str(round(gerceklesen, 2)) if gerceklesen is not None else None,
            'durum': durum,
            'durum_yuzdesi': durum_yuzdesi,
            'kullanicilar': kullanicilar,
            'veri_idleri': veri_idleri
        })
        
    elif periyot == 'aylik':
        # 12 ay için veri - HER ZAMAN 12 KOLON - AKILLI GÖSTERİM
        for ay_no in range(1, 13):
            periyot_son_cuma = get_last_friday_of_month(ay_no, yil)
            
            # Ayın başlangıç ve bitiş tarihleri
            _, ay_gun_sayisi = monthrange(yil, ay_no)
            ay_baslangic = date(yil, ay_no, 1)
            ay_bitis = date(yil, ay_no, ay_gun_sayisi)
            
            # Bu ay içindeki verileri topla (akıllı gösterim)
            gerceklesen, kullanicilar, veri_idleri = get_verileri_topla(
                bireysel_pgler, yil, periyot_son_cuma, hesaplama_yontemi,
                'aylik', (ay_baslangic, ay_bitis)
            )
            durum, durum_yuzdesi = hesapla_durum(hedef_deger, gerceklesen)
            
            veriler.append({
                'ay': ay_no,
                'hedef_deger': round(hedef_deger, 2) if hedef_deger is not None else '-',
                'gerceklesen_deger': str(round(gerceklesen, 2)) if gerceklesen is not None else None,
                'durum': durum,
                'durum_yuzdesi': durum_yuzdesi,
                'kullanicilar': kullanicilar,
                'veri_idleri': veri_idleri
            })
            
    elif periyot == 'haftalik':
        # Ay belirtilmişse sadece o ayın haftalarını göster
        if ay and 1 <= ay <= 12:
            haftalar = get_ay_haftalari(ay, yil)
        else:
            # Ay belirtilmemişse tüm yılın haftalarını göster (varsayılan)
            haftalar = get_yil_haftalari(yil)
        
        for hafta_bilgi in haftalar:
            hafta_no = hafta_bilgi['hafta_no']
            # Veri kaydetme tarihi: Haftanın son Cuma'sı (iş günü mantığı)
            periyot_son_cuma = hafta_bilgi.get('veri_tarihi', hafta_bilgi['bitis_tarih'])  # Haftanın son Cuması
            hafta_baslangic = hafta_bilgi['baslangic_tarih']  # Pazartesi (gösterim için)
            hafta_bitis = hafta_bilgi['bitis_tarih']  # Pazar (gösterim için - 7 gün)
            
            # Bu hafta içindeki verileri topla (akıllı gösterim)
            # Veri kaydetme tarihi: periyot_son_cuma (Cuma)
            # Gösterim aralığı: hafta_baslangic - hafta_bitis (Pazartesi-Pazar)
            gerceklesen, kullanicilar, veri_idleri = get_verileri_topla(
                bireysel_pgler, yil, periyot_son_cuma, hesaplama_yontemi,
                'haftalik', (hafta_baslangic, hafta_bitis)
            )
            durum, durum_yuzdesi = hesapla_durum(hedef_deger, gerceklesen)
            
            veriler.append({
                'hafta': hafta_no,
                'baslangic_tarih': hafta_bilgi['baslangic_tarih'].strftime('%d.%m.%Y') if hafta_bilgi.get('baslangic_tarih') else None,
                'bitis_tarih': hafta_bilgi['bitis_tarih'].strftime('%d.%m.%Y') if hafta_bilgi.get('bitis_tarih') else None,
                'hedef_deger': round(hedef_deger, 2) if hedef_deger is not None else '-',
                'gerceklesen_deger': str(round(gerceklesen, 2)) if gerceklesen is not None else None,
                'durum': durum,
                'durum_yuzdesi': durum_yuzdesi,
                'kullanicilar': kullanicilar,
                'veri_idleri': veri_idleri
            })
            
    elif periyot == 'gunluk':
        # Ay belirtilmişse sadece o ayın günlerini göster
        if ay and 1 <= ay <= 12:
            gunler = get_ay_gunleri(ay, yil)
        else:
            # Ay belirtilmemişse tüm yılın günlerini göster (varsayılan)
            gunler = get_yil_gunleri(yil)
        
        for gun_bilgi in gunler:
            gun_no = gun_bilgi['gun_no']
            veri_tarihi = gun_bilgi['tarih']  # Direkt tarih (günlük için son Cuma değil)
            
            # Günlük için direkt tarihe eşleşen verileri bul
            gerceklesen, kullanicilar, veri_idleri = get_verileri_topla(
                bireysel_pgler, yil, veri_tarihi, hesaplama_yontemi,
                'gunluk', (veri_tarihi, veri_tarihi)  # Aynı gün
            )
            durum, durum_yuzdesi = hesapla_durum(hedef_deger, gerceklesen)
            
            # Türkçe gün isimleri
            gun_isimleri = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
            tarih_obje = gun_bilgi['tarih']
            gun_adi = gun_isimleri[tarih_obje.weekday()]
            
            # Ay isimleri
            ay_isimleri = ['', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
            ay_adi = ay_isimleri[tarih_obje.month]
            
            veriler.append({
                'gun': gun_no,
                'tarih': tarih_obje.strftime('%d.%m.%Y'),
                'tarih_gun': tarih_obje.day,
                'tarih_ay': ay_adi,
                'tarih_yil': tarih_obje.year,
                'tarih_gun_adi': gun_adi,
                'hedef_deger': round(hedef_deger, 2) if hedef_deger is not None else '-',
                'gerceklesen_deger': str(round(gerceklesen, 2)) if gerceklesen is not None else None,
                'durum': durum,
                'durum_yuzdesi': durum_yuzdesi,
                'kullanicilar': kullanicilar,
                'veri_idleri': veri_idleri
            })
    
    return veriler

