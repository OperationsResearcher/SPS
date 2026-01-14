# -*- coding: utf-8 -*-
"""
Audit Log Otomasyonu Servisi
SQLAlchemy event listener'ları ile otomatik audit log kayıtları
"""
from sqlalchemy import event
from sqlalchemy.orm import Session
from datetime import datetime


def register_audit_listeners(db):
    """Audit event listener'ları kaydet"""
    
    @event.listens_for(Session, 'before_flush')
    def receive_before_flush(session, flush_context, instances):
        """Flush öncesi değişiklikleri yakala"""
        from models import PerformansGostergeVeriAudit, PerformansGostergeVeri
        
        for instance in session.new:
            # Yeni kayıtlar için audit log oluştur
            if isinstance(instance, PerformansGostergeVeri):
                _create_audit_log(session, instance, 'INSERT', None, instance)
        
        for instance in session.dirty:
            # Değişen kayıtlar için audit log oluştur
            if isinstance(instance, PerformansGostergeVeri):
                # Eski değerleri almak için session.get_history kullan
                history = session.get_history(instance, 'gerceklesen_deger')
                if history.has_changes():
                    old_value = history.deleted[0] if history.deleted else None
                    new_value = history.added[0] if history.added else instance.gerceklesen_deger
                    _create_audit_log(session, instance, 'UPDATE', old_value, new_value)
        
        for instance in session.deleted:
            # Silinen kayıtlar için audit log oluştur
            if isinstance(instance, PerformansGostergeVeri):
                _create_audit_log(session, instance, 'DELETE', instance, None)


def _create_audit_log(session, instance, operation, old_value, new_value):
    """Audit log kaydı oluştur"""
    from models import PerformansGostergeVeriAudit
    from flask_login import current_user
    
    try:
        # İşlem tipini Türkçe'ye çevir
        islem_tipi_map = {
            'INSERT': 'OLUSTUR',
            'UPDATE': 'GUNCELLE',
            'DELETE': 'SIL'
        }
        islem_tipi = islem_tipi_map.get(operation, operation)
        
        # Kullanıcı ID'si
        user_id = current_user.id if current_user.is_authenticated else None
        
        audit = PerformansGostergeVeriAudit(
            pg_veri_id=instance.id if hasattr(instance, 'id') and instance.id else None,
            islem_tipi=islem_tipi,
            eski_deger=str(old_value) if old_value is not None else None,
            yeni_deger=str(new_value) if new_value is not None else None,
            islem_yapan_user_id=user_id or 1,  # Varsayılan sistem kullanıcısı
            islem_tarihi=datetime.utcnow()
        )
        session.add(audit)
    except Exception as e:
        # Audit log hatası uygulamayı durdurmamalı
        import logging
        logging.getLogger(__name__).warning(f"Audit log oluşturma hatası: {e}")


def register_model_audit_listeners():
    """Tüm modeller için genel audit listener'ları kaydet"""
    # Bu fonksiyon gelecekte diğer modeller için de genişletilebilir
    pass

