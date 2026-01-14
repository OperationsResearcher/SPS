# -*- coding: utf-8 -*-
"""
AI Destekli Yönetici Özeti Servisi
Dashboard için akıllı durum özetleme
"""
from datetime import date, datetime
from flask import current_app
from models import (
    db, Project, Task, ProjectRisk
)
from sqlalchemy import and_, or_


def generate_executive_summary(kurum_id):
    """
    Yönetici için AI destekli durum özeti oluştur
    
    En büyük 3 risk ve en acil 3 görevi analiz ederek
    tek bir paragrafta özet sunar.
    
    Args:
        kurum_id: Kurum ID
    
    Returns:
        str: Özet metin
    """
    try:
        # Tüm projeleri getir
        projects = Project.query.filter_by(kurum_id=kurum_id).all()
        if not projects:
            return "Henüz proje bulunmamaktadır. Yeni projeler oluşturarak başlayabilirsiniz."
        
        project_ids = [p.id for p in projects]
        
        # En büyük 3 riski bul (risk_score'a göre)
        critical_risks = ProjectRisk.query.filter(
            and_(
                ProjectRisk.project_id.in_(project_ids),
                ProjectRisk.status == 'Aktif'
            )
        ).order_by(
            (ProjectRisk.impact * ProjectRisk.probability).desc()
        ).limit(3).all()
        
        # En acil 3 görevi bul (due_date'e göre, gecikmiş veya yakın tarihli)
        today = date.today()
        urgent_tasks = Task.query.filter(
            and_(
                Task.project_id.in_(project_ids),
                Task.status != 'Tamamlandı',
                Task.due_date.isnot(None)
            )
        ).order_by(
            Task.due_date.asc()
        ).limit(5).all()
        
        # En acil 3'ü seç (gecikmiş veya bugünden itibaren 3 gün içinde)
        urgent_tasks_filtered = []
        for task in urgent_tasks:
            days_until_due = (task.due_date - today).days
            if days_until_due <= 3 or days_until_due < 0:
                urgent_tasks_filtered.append(task)
                if len(urgent_tasks_filtered) >= 3:
                    break
        
        # Özet metni oluştur
        summary_parts = []
        
        # Risk özeti
        if critical_risks:
            risk_titles = [f'"{r.title}"' for r in critical_risks]
            risk_summary = f"En kritik riskler: {', '.join(risk_titles)}"
            if len(critical_risks) == 1:
                risk_summary = f"Kritik bir risk tespit edildi: {risk_titles[0]} (Skor: {critical_risks[0].risk_score})"
            else:
                risk_scores = [str(r.risk_score) for r in critical_risks]
                risk_summary = f"{len(critical_risks)} kritik risk tespit edildi: {', '.join(risk_titles)} (Skorlar: {', '.join(risk_scores)})"
            summary_parts.append(risk_summary)
        
        # Görev özeti
        if urgent_tasks_filtered:
            task_titles = [f'"{t.title}"' for t in urgent_tasks_filtered]
            overdue_count = sum(1 for t in urgent_tasks_filtered if t.due_date < today)
            
            if overdue_count > 0:
                task_summary = f"{overdue_count} gecikmiş görev var: {', '.join(task_titles[:overdue_count])}"
                if len(urgent_tasks_filtered) > overdue_count:
                    task_summary += f" ve {len(urgent_tasks_filtered) - overdue_count} acil görev yaklaşıyor"
            else:
                task_summary = f"Yaklaşan {len(urgent_tasks_filtered)} acil görev var: {', '.join(task_titles)}"
            summary_parts.append(task_summary)
        
        # Özet cümlesi oluştur
        if summary_parts:
            if critical_risks and urgent_tasks_filtered:
                summary = f"Bugün odaklanmanız gereken alan şudur: {summary_parts[0]}. Ayrıca, {summary_parts[1]}. Bu konulara öncelik verilmesi önerilir."
            elif critical_risks:
                summary = f"Bugün odaklanmanız gereken alan şudur: {summary_parts[0]}. Bu risklerin yönetimi ve azaltılması için acil aksiyon alınması gerekmektedir."
            elif urgent_tasks_filtered:
                summary = f"Bugün odaklanmanız gereken alan şudur: {summary_parts[0]}. Bu görevlerin zamanında tamamlanması için gerekli kaynakların ayrılması önerilir."
            else:
                summary = "Şu anda kritik bir durum tespit edilmemiştir. Projeler normal seyrinde ilerlemektedir."
        else:
            summary = "Şu anda kritik bir durum tespit edilmemiştir. Projeler normal seyrinde ilerlemektedir."
        
        return summary
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f'AI yönetici özeti oluşturma hatası: {e}')
        return "Özet oluşturulurken bir hata oluştu. Lütfen daha sonra tekrar deneyin."





















