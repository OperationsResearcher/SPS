# -*- coding: utf-8 -*-
"""
Performance Service Testleri
V1'den taşınan iş mantığı fonksiyonlarını test eder
"""
import pytest
from datetime import date, datetime
from services.performance_service import (
    calculateHedefDeger,
    generatePeriyotVerileri,
    get_verileri_topla,
    hesapla_durum,
    get_last_friday_of_month,
    get_last_friday_of_quarter,
    get_last_friday_of_year
)

class TestPerformanceService:
    """Performance Service fonksiyonları için testler"""
    
    def test_calculateHedefDeger_basit(self):
        """Basit hedef değer hesaplama testi"""
        # Test: Basit sayısal değer (Ortalama yöntemi - değişmez)
        result = calculateHedefDeger("100", "Aylık", "aylik", "Ortalama")
        assert result == 100.0
        
        result = calculateHedefDeger("50.5", "Aylık", "aylik", "Ortalama")
        assert result == 50.5
        
    def test_calculateHedefDeger_toplam(self):
        """Toplam hesaplama yöntemi testi"""
        # Aylık PG, Yıllık gösterim: 100 * 12 = 1200
        result = calculateHedefDeger("100", "Aylık", "yillik", "Toplam")
        assert result == 1200.0
        
        # Çeyreklik PG, Yıllık gösterim: 100 * 4 = 400
        result = calculateHedefDeger("100", "Çeyreklik", "yillik", "Toplam")
        assert result == 400.0
        
    def test_hesapla_durum(self):
        """Durum hesaplama testi"""
        # Hedef: 100, Gerçekleşen: 120 (%120) - >= 100 -> "Başarılı"
        durum, yuzde = hesapla_durum(100.0, 120.0)
        assert durum == "Başarılı"
        assert abs(yuzde - 120.0) < 0.01
        
        # Hedef: 100, Gerçekleşen: 80 (%80) - >= 75 -> "Kısmen Başarılı"
        durum, yuzde = hesapla_durum(100.0, 80.0)
        assert durum == "Kısmen Başarılı"
        assert abs(yuzde - 80.0) < 0.01
        
        # Hedef: 100, Gerçekleşen: 50 (%50) - < 75 -> "Başarısız"
        durum, yuzde = hesapla_durum(100.0, 50.0)
        assert durum == "Başarısız"
        assert abs(yuzde - 50.0) < 0.01
        
        # Hedef: 100, Gerçekleşen: 100 (%100) - >= 100 -> "Başarılı"
        durum, yuzde = hesapla_durum(100.0, 100.0)
        assert durum == "Başarılı"
        assert abs(yuzde - 100.0) < 0.01
        
    def test_get_last_friday_of_month(self):
        """Ayın son Cuma günü hesaplama testi"""
        # 2025 Ocak ayının son Cuma günü (parametre sırası: ay, yil)
        result = get_last_friday_of_month(1, 2025)
        assert result.year == 2025
        assert result.month == 1
        
        # 2025 Şubat ayının son Cuma günü
        result = get_last_friday_of_month(2, 2025)
        assert result.year == 2025
        assert result.month == 2
        
    def test_get_last_friday_of_quarter(self):
        """Çeyreğin son Cuma günü hesaplama testi"""
        # 2025 Q1 (Ocak-Şubat-Mart) - parametre sırası: ceyrek, yil
        result = get_last_friday_of_quarter(1, 2025)
        assert result.year == 2025
        assert result.month == 3  # Mart ayı
        
        # 2025 Q2 (Nisan-Mayıs-Haziran)
        result = get_last_friday_of_quarter(2, 2025)
        assert result.year == 2025
        assert result.month == 6  # Haziran ayı
        
    def test_get_last_friday_of_year(self):
        """Yılın son Cuma günü hesaplama testi"""
        result = get_last_friday_of_year(2025)
        assert result.year == 2025
        assert result.month == 12  # Aralık ayı

