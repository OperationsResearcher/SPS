# -*- coding: utf-8 -*-
"""
Project Service Testleri
"""
import pytest
from datetime import date, datetime
from services.project_service import handle_task_completion, _calculate_veri_tarihi, _get_periyot_bilgileri
from models import Task, TaskImpact, BireyselPerformansGostergesi, PerformansGostergeVeri, SurecPerformansGostergesi


class TestProjectService:
    """Project Service fonksiyonları için testler"""
    
    def test_calculate_veri_tarihi_aylik(self, app):
        """Aylık periyot için veri tarihi hesaplama"""
        with app.app_context():
            tamamlanma_tarihi = date(2025, 3, 15)
            veri_tarihi = _calculate_veri_tarihi(tamamlanma_tarihi, 'Aylık', 2025, 3, 1)
            # Aylık periyotta ayın son Cuma'sı olmalı
            assert veri_tarihi.year == 2025
            assert veri_tarihi.month == 3
    
    def test_calculate_veri_tarihi_ceyrek(self, app):
        """Çeyreklik periyot için veri tarihi hesaplama"""
        with app.app_context():
            tamamlanma_tarihi = date(2025, 3, 15)
            veri_tarihi = _calculate_veri_tarihi(tamamlanma_tarihi, 'Çeyreklik', 2025, 3, 1)
            # Çeyreklik periyotta çeyreğin son Cuma'sı olmalı
            assert veri_tarihi.year == 2025
            assert veri_tarihi.month == 3  # Q1'in son ayı
    
    def test_get_periyot_bilgileri_aylik(self, app):
        """Aylık periyot bilgileri"""
        with app.app_context():
            tamamlanma_tarihi = date(2025, 3, 15)
            periyot_tipi, periyot_no, periyot_ay = _get_periyot_bilgileri(
                'Aylık', tamamlanma_tarihi, 2025, 3, 1
            )
            assert periyot_tipi == 'Aylık'
            assert periyot_no == 3
            assert periyot_ay == 3
    
    def test_handle_task_completion_no_impacts(self, app, test_task):
        """Impact olmayan görev tamamlama"""
        with app.app_context():
            test_task.status = 'Tamamlandı'
            test_task.completed_at = datetime.now()
            
            islenen = handle_task_completion(test_task)
            assert islenen == 0  # Impact yok, işlenen yok
    
    def test_handle_task_completion_with_impact(self, app, test_task, test_user):
        """Impact'li görev tamamlama"""
        from models import db
        
        with app.app_context():
            # Bireysel PG oluştur
            bireysel_pg = BireyselPerformansGostergesi(
                user_id=test_user.id,
                ad='Test PG',
                periyot='Aylık',
                hedef_deger=100.0,
                olcum_birimi='Adet'
            )
            db.session.add(bireysel_pg)
            db.session.flush()
            
            # TaskImpact oluştur
            impact = TaskImpact(
                task_id=test_task.id,
                related_pg_id=bireysel_pg.id,
                impact_value='5',
                is_processed=False
            )
            db.session.add(impact)
            db.session.commit()
            
            # Görevi tamamla
            test_task.status = 'Tamamlandı'
            test_task.completed_at = datetime.now()
            
            islenen = handle_task_completion(test_task)
            
            # En az 1 PG verisi oluşturulmalı
            assert islenen >= 1
            
            # Impact işlenmiş olmalı
            db.session.refresh(impact)
            assert impact.is_processed == True
            
            # PG verisi oluşturulmuş olmalı
            pg_veri = PerformansGostergeVeri.query.filter_by(
                pg_id=bireysel_pg.id
            ).first()
            assert pg_veri is not None
            assert float(pg_veri.gerceklesen_deger) == 5.0




















