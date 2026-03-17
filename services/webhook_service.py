# -*- coding: utf-8 -*-
"""
Webhook Dispatch Servisi
Kritik olaylar için webhook gönderimi
"""
import requests
import json
from datetime import datetime
from flask import current_app
from models import db, Kurum
from typing import Dict, Optional, List


def dispatch_webhook(kurum_id: int, event_type: str, payload: Dict) -> bool:
    """
    Webhook gönder
    
    Args:
        kurum_id: Kurum ID
        event_type: Olay tipi ('pg_deviation', 'risk_increase', 'task_overdue', vb.)
        payload: Gönderilecek veri
    
    Returns:
        bool: Başarılı ise True
    """
    try:
        # Kurum webhook URL'lerini al (gelecekte veritabanından)
        # Şimdilik environment variable'dan al
        webhook_urls = _get_webhook_urls(kurum_id, event_type)
        
        if not webhook_urls:
            if current_app:
                current_app.logger.debug(f'Kurum {kurum_id} için {event_type} webhook URL bulunamadı')
            return False
        
        # Webhook payload'u hazırla
        webhook_payload = {
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'kurum_id': kurum_id,
            'data': payload
        }
        
        # Her URL'e gönder
        success_count = 0
        for url in webhook_urls:
            try:
                response = requests.post(
                    url,
                    json=webhook_payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=5  # 5 saniye timeout
                )
                
                if response.status_code in [200, 201, 202]:
                    success_count += 1
                    if current_app:
                        current_app.logger.info(f'Webhook başarılı: {url}, Event: {event_type}')
                else:
                    if current_app:
                        current_app.logger.warning(
                            f'Webhook hata: {url}, Status: {response.status_code}, '
                            f'Event: {event_type}'
                        )
            
            except requests.exceptions.RequestException as e:
                if current_app:
                    current_app.logger.error(f'Webhook gönderim hatası ({url}): {e}')
                continue
        
        return success_count > 0
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Webhook dispatch hatası: {e}', exc_info=True)
        return False


def _get_webhook_urls(kurum_id: int, event_type: str) -> List[str]:
    """
    Kurum için webhook URL'lerini al
    
    Args:
        kurum_id: Kurum ID
        event_type: Olay tipi
    
    Returns:
        List[str]: Webhook URL listesi
    """
    import os
    
    # Environment variable'dan al (format: WEBHOOK_URL_<KURUM_ID>_<EVENT_TYPE>)
    env_key = f'WEBHOOK_URL_{kurum_id}_{event_type.upper()}'
    url = os.environ.get(env_key)
    
    if url:
        return [url]
    
    # Genel webhook URL (tüm event'ler için)
    general_key = f'WEBHOOK_URL_{kurum_id}'
    general_url = os.environ.get(general_key)
    
    if general_url:
        return [general_url]
    
    # Global webhook URL (tüm kurumlar için)
    global_url = os.environ.get('WEBHOOK_URL_GLOBAL')
    
    if global_url:
        return [global_url]
    
    return []


def trigger_pg_deviation_webhook(kurum_id: int, pg_veri_id: int, deviation_percentage: float):
    """
    PG sapması webhook'u tetikle
    
    Args:
        kurum_id: Kurum ID
        pg_veri_id: PG veri ID
        deviation_percentage: Sapma yüzdesi
    """
    from models import PerformansGostergeVeri, BireyselPerformansGostergesi
    
    try:
        pg_veri = PerformansGostergeVeri.query.get(pg_veri_id)
        if not pg_veri:
            return
        
        bireysel_pg = BireyselPerformansGostergesi.query.get(pg_veri.pg_id)
        
        payload = {
            'pg_veri_id': pg_veri_id,
            'pg_id': pg_veri.pg_id,
            'pg_name': bireysel_pg.ad if bireysel_pg else 'Bilinmiyor',
            'hedef_deger': float(pg_veri.hedef_deger) if pg_veri.hedef_deger else 0,
            'gerceklesen_deger': float(pg_veri.gerceklesen_deger) if pg_veri.gerceklesen_deger else 0,
            'deviation_percentage': deviation_percentage,
            'durum': pg_veri.durum,
            'veri_tarihi': pg_veri.veri_tarihi.isoformat() if pg_veri.veri_tarihi else None
        }
        
        dispatch_webhook(kurum_id, 'pg_deviation', payload)
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f'PG deviation webhook hatası: {e}')


def trigger_risk_increase_webhook(kurum_id: int, risk_id: int, old_score: int, new_score: int):
    """
    Risk artışı webhook'u tetikle
    
    Args:
        kurum_id: Kurum ID
        risk_id: Risk ID
        old_score: Eski risk skoru
        new_score: Yeni risk skoru
    """
    from models import ProjectRisk, Project
    
    try:
        risk = ProjectRisk.query.get(risk_id)
        if not risk:
            return
        
        project = risk.project
        
        payload = {
            'risk_id': risk_id,
            'risk_title': risk.title,
            'project_id': risk.project_id,
            'project_name': project.name if project else 'Bilinmiyor',
            'old_score': old_score,
            'new_score': new_score,
            'probability': risk.probability,
            'impact': risk.impact,
            'risk_level': risk.risk_level
        }
        
        dispatch_webhook(kurum_id, 'risk_increase', payload)
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Risk increase webhook hatası: {e}')




















