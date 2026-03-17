# -*- coding: utf-8 -*-
"""
Rapor Servisleri
PDF rapor oluşturma ve dışa aktarma
"""
from datetime import datetime, date
from flask import current_app
from io import BytesIO
from models import (
    db, Project, Task, ProjectRisk, Surec, User
)
from services.project_analytics import calculate_surec_saglik_skoru
from services.executive_dashboard import get_corporate_health_score, get_critical_risks
from sqlalchemy import and_, or_


def generate_project_pdf_report(project_id, kurum_id):
    """
    Bir projenin detaylı PDF raporunu oluştur
    
    Args:
        project_id: Proje ID
        kurum_id: Kurum ID (yetki kontrolü için)
    
    Returns:
        BytesIO: PDF dosyası
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        project = Project.query.get(project_id)
        if not project or project.kurum_id != kurum_id:
            return None
        
        # PDF buffer oluştur
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        story = []
        styles = getSampleStyleSheet()
        
        # Başlık stili
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        # Alt başlık stili
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Normal metin stili
        normal_style = styles['Normal']
        
        # Rapor başlığı
        story.append(Paragraph("PROJE DURUM RAPORU", title_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Proje bilgileri
        story.append(Paragraph(f"<b>Proje Adı:</b> {project.name}", normal_style))
        story.append(Paragraph(f"<b>Proje Yöneticisi:</b> {project.manager.first_name} {project.manager.last_name}" if project.manager else "<b>Proje Yöneticisi:</b> Belirtilmemiş", normal_style))
        story.append(Paragraph(f"<b>Oluşturulma Tarihi:</b> {project.created_at.strftime('%d.%m.%Y') if project.created_at else 'Belirtilmemiş'}", normal_style))
        if project.start_date:
            story.append(Paragraph(f"<b>Başlangıç Tarihi:</b> {project.start_date.strftime('%d.%m.%Y')}", normal_style))
        if project.end_date:
            story.append(Paragraph(f"<b>Bitiş Tarihi:</b> {project.end_date.strftime('%d.%m.%Y')}", normal_style))
        story.append(Paragraph(f"<b>Öncelik:</b> {project.priority or 'Orta'}", normal_style))
        if project.description:
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph(f"<b>Açıklama:</b> {project.description}", normal_style))
        
        story.append(Spacer(1, 0.5*cm))
        story.append(PageBreak())
        
        # Görev istatistikleri
        story.append(Paragraph("GÖREV İSTATİSTİKLERİ", heading_style))
        
        tasks = Task.query.filter_by(project_id=project_id).all()
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == 'Tamamlandı'])
        in_progress_tasks = len([t for t in tasks if t.status == 'Devam Ediyor'])
        overdue_tasks = len([t for t in tasks if t.status != 'Tamamlandı' and t.due_date and t.due_date < date.today()])
        
        task_data = [
            ['Metrik', 'Değer'],
            ['Toplam Görev', str(total_tasks)],
            ['Tamamlanan', str(completed_tasks)],
            ['Devam Eden', str(in_progress_tasks)],
            ['Gecikmiş', str(overdue_tasks)],
            ['Tamamlanma Oranı', f'%{round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)}']
        ]
        
        task_table = Table(task_data, colWidths=[8*cm, 8*cm])
        task_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        story.append(task_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Risk analizi
        story.append(Paragraph("RİSK ANALİZİ", heading_style))
        
        risks = ProjectRisk.query.filter_by(project_id=project_id, status='Aktif').all()
        if risks:
            risk_data = [['Risk Başlığı', 'Etki', 'Olasılık', 'Skor', 'Seviye']]
            for risk in sorted(risks, key=lambda x: x.risk_score, reverse=True):
                risk_data.append([
                    risk.title[:40] + '...' if len(risk.title) > 40 else risk.title,
                    str(risk.impact),
                    str(risk.probability),
                    str(risk.risk_score),
                    risk.risk_level
                ])
            
            risk_table = Table(risk_data, colWidths=[6*cm, 2*cm, 2*cm, 2*cm, 2*cm])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc3545')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            story.append(risk_table)
        else:
            story.append(Paragraph("Aktif risk bulunmamaktadır.", normal_style))
        
        story.append(Spacer(1, 0.5*cm))
        
        # Rapor tarihi
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(f"<i>Rapor Oluşturulma Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}</i>", normal_style))
        
        # PDF oluştur
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f'PDF rapor oluşturma hatası: {e}')
        return None


def generate_executive_dashboard_pdf(kurum_id, filters=None):
    """
    Executive Dashboard PDF raporu oluştur
    
    Args:
        kurum_id: Kurum ID
        filters: Filtreleme parametreleri (department, date_range, manager_id)
    
    Returns:
        BytesIO: PDF dosyası
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        # Filtreleme uygula
        projects_query = Project.query.filter_by(kurum_id=kurum_id)
        
        if filters:
            if filters.get('department'):
                projects_query = projects_query.join(User, Project.manager_id == User.id).filter(
                    User.department == filters['department']
                )
            if filters.get('manager_id'):
                projects_query = projects_query.filter(Project.manager_id == filters['manager_id'])
            if filters.get('start_date') and filters.get('end_date'):
                projects_query = projects_query.filter(
                    and_(
                        Project.start_date >= filters['start_date'],
                        Project.end_date <= filters['end_date']
                    )
                )
        
        projects = projects_query.all()
        
        # PDF buffer oluştur
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        story = []
        styles = getSampleStyleSheet()
        
        # Başlık stili
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        # Alt başlık stili
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        normal_style = styles['Normal']
        
        # Rapor başlığı
        story.append(Paragraph("YÖNETİM KOKPİTİ RAPORU", title_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Filtre bilgileri
        if filters:
            filter_text = "Filtreler: "
            if filters.get('department'):
                filter_text += f"Departman: {filters['department']}, "
            if filters.get('manager_id'):
                manager = User.query.get(filters['manager_id'])
                if manager:
                    filter_text += f"Proje Yöneticisi: {manager.first_name} {manager.last_name}, "
            if filters.get('start_date') and filters.get('end_date'):
                filter_text += f"Tarih Aralığı: {filters['start_date'].strftime('%d.%m.%Y')} - {filters['end_date'].strftime('%d.%m.%Y')}"
            story.append(Paragraph(filter_text, normal_style))
            story.append(Spacer(1, 0.3*cm))
        
        # Kurumsal sağlık skoru
        health_data = get_corporate_health_score(kurum_id)
        story.append(Paragraph("KURUMSAL SAĞLIK SKORU", heading_style))
        story.append(Paragraph(f"<b>Genel Skor:</b> {health_data.get('score', 0):.1f}/100", normal_style))
        story.append(Paragraph(f"<b>Proje Sayısı:</b> {health_data.get('project_count', 0)}", normal_style))
        story.append(Paragraph(f"<b>Süreç Sayısı:</b> {health_data.get('surec_count', 0)}", normal_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Kritik riskler
        story.append(Paragraph("KRİTİK RİSKLER", heading_style))
        critical_risks = get_critical_risks(kurum_id, limit=10)
        if critical_risks:
            risk_data = [['Risk Başlığı', 'Proje', 'Skor', 'Seviye']]
            for risk in critical_risks[:10]:
                risk_data.append([
                    risk['title'][:40] + '...' if len(risk['title']) > 40 else risk['title'],
                    risk['project_name'][:30] + '...' if len(risk['project_name']) > 30 else risk['project_name'],
                    str(risk['risk_score']),
                    risk['risk_level']
                ])
            
            risk_table = Table(risk_data, colWidths=[7*cm, 4*cm, 2*cm, 3*cm])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc3545')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            story.append(risk_table)
        else:
            story.append(Paragraph("Kritik risk bulunmamaktadır.", normal_style))
        
        story.append(Spacer(1, 0.5*cm))
        story.append(PageBreak())
        
        # Proje özeti
        story.append(Paragraph("PROJE ÖZETİ", heading_style))
        if projects:
            project_data = [['Proje Adı', 'Yönetici', 'Başlangıç', 'Bitiş', 'Öncelik']]
            for project in projects[:20]:  # İlk 20 proje
                manager_name = f"{project.manager.first_name} {project.manager.last_name}" if project.manager else "Belirtilmemiş"
                start_date = project.start_date.strftime('%d.%m.%Y') if project.start_date else '-'
                end_date = project.end_date.strftime('%d.%m.%Y') if project.end_date else '-'
                project_data.append([
                    project.name[:35] + '...' if len(project.name) > 35 else project.name,
                    manager_name[:25] + '...' if len(manager_name) > 25 else manager_name,
                    start_date,
                    end_date,
                    project.priority or 'Orta'
                ])
            
            project_table = Table(project_data, colWidths=[5*cm, 4*cm, 2.5*cm, 2.5*cm, 2*cm])
            project_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            story.append(project_table)
        else:
            story.append(Paragraph("Filtrelere uygun proje bulunmamaktadır.", normal_style))
        
        story.append(Spacer(1, 0.5*cm))
        
        # Rapor tarihi
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(f"<i>Rapor Oluşturulma Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}</i>", normal_style))
        
        # PDF oluştur
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Executive dashboard PDF oluşturma hatası: {e}')
        return None






















