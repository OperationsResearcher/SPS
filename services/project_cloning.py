# -*- coding: utf-8 -*-
"""
Proje Klonlama Servisi
Projeleri derin kopyalama, tarih kaydırma ve şablonlama işlemleri
"""
from datetime import datetime, timedelta
from models import db, Project, Task, ProjectRisk, ProjectFile, TaskImpact
from datetime import datetime, timedelta


def clone_project(project_id, new_name, new_start_date, keep_assignments=True, keep_completed_tasks=False):
    """
    Projeyi derin kopyalama (Deep Copy) ile klonla
    
    Args:
        project_id: Kopyalanacak proje ID'si
        new_name: Yeni proje adı
        new_start_date: Yeni projenin başlangıç tarihi (datetime.date)
        keep_assignments: Atanan kişileri koru (True) veya temizle (False)
        keep_completed_tasks: Tamamlanan görevleri kopyala (True) veya atla (False)
    
    Returns:
        Yeni proje ID'si veya None (hata durumunda)
    """
    try:
        # Kaynak projeyi getir
        source_project = Project.query.get(project_id)
        if not source_project:
            return None
        
        # Tarih delta'sını hesapla (eski projenin ilk görev tarihi ile yeni başlangıç tarihi arasındaki fark)
        source_tasks = Task.query.filter_by(project_id=project_id).all()
        source_start_date = None
        
        if source_tasks:
            # En erken görev tarihini bul
            earliest_dates = [t.due_date for t in source_tasks if t.due_date]
            if earliest_dates:
                source_start_date = min(earliest_dates)
        
        # Eğer görev tarihi yoksa, proje oluşturulma tarihini kullan
        if not source_start_date:
            source_start_date = source_project.created_at.date() if source_project.created_at else datetime.now().date()
        
        # Tarih farkını hesapla
        date_delta = (new_start_date - source_start_date).days
        
        # Yeni projeyi oluştur
        new_project = Project(
            kurum_id=source_project.kurum_id,
            name=new_name,
            manager_id=source_project.manager_id if keep_assignments else None,
            description=f"Kopya: {source_project.description}" if source_project.description else None,
            template_id=source_project.template_id
        )
        
        db.session.add(new_project)
        db.session.flush()  # ID'yi almak için
        
        # Proje üyelerini kopyala
        if source_project.members:
            new_project.members = source_project.members[:]
        
        # Proje gözlemcilerini kopyala
        if source_project.observers:
            new_project.observers = source_project.observers[:]
        
        # İlişkili süreçleri kopyala
        if source_project.related_processes:
            new_project.related_processes = source_project.related_processes[:]
        
        # Görevleri kopyala (hiyerarşik yapıyı koru)
        task_mapping = {}  # Eski task ID -> Yeni task ID mapping
        
        # Önce parent görevleri kopyala (parent_id NULL olanlar)
        parent_tasks = [t for t in source_tasks if not t.parent_id]
        
        def copy_task_recursive(source_task, parent_id=None):
            """Görevi ve alt görevlerini recursive olarak kopyala"""
            # Tamamlanan görevleri atla (eğer keep_completed_tasks False ise)
            if not keep_completed_tasks and source_task.status == 'Tamamlandı':
                return None
            
            # Yeni görev oluştur
            new_task = Task(
                project_id=new_project.id,
                parent_id=parent_id,
                assigned_to_id=source_task.assigned_to_id if keep_assignments else None,
                title=source_task.title,
                description=source_task.description,
                priority=source_task.priority,
                status='Yapılacak',  # Tüm görevleri başlangıç durumuna al
                progress=0,  # İlerlemeyi sıfırla
                estimated_time=source_task.estimated_time,
                actual_time=None,  # Gerçekleşen süreyi temizle
                due_date=None  # Tarih kaydırma için önce None yap
            )
            
            # Tarih kaydırma
            if source_task.due_date:
                new_task.due_date = source_task.due_date + timedelta(days=date_delta)
            
            db.session.add(new_task)
            db.session.flush()  # ID'yi almak için
            
            # Mapping'i kaydet
            task_mapping[source_task.id] = new_task.id
            
            # TaskImpact'leri kopyala
            if hasattr(source_task, 'impacts'):
                for impact in source_task.impacts:
                    new_impact = TaskImpact(
                        task_id=new_task.id,
                        related_pg_id=impact.related_pg_id,
                        related_faaliyet_id=impact.related_faaliyet_id,
                        impact_value=impact.impact_value
                    )
                    db.session.add(new_impact)
            
            # Alt görevleri kopyala (recursive)
            child_tasks = [t for t in source_tasks if t.parent_id == source_task.id]
            for child_task in child_tasks:
                copy_task_recursive(child_task, new_task.id)
            
            return new_task.id
        
        # Tüm parent görevleri kopyala
        for parent_task in parent_tasks:
            copy_task_recursive(parent_task)
        
        # Predecessor ilişkilerini kopyala (task_mapping kullanarak)
        for source_task in source_tasks:
            if source_task.id in task_mapping:
                new_task_id = task_mapping[source_task.id]
                # Predecessor'ları bul ve kopyala
                if hasattr(source_task, 'predecessors') and source_task.predecessors:
                    for pred in source_task.predecessors:
                        if pred.id in task_mapping:
                            # Predecessor ilişkisini ekle (task_predecessors table)
                            from models import task_predecessors
                            from sqlalchemy import insert
                            db.session.execute(
                                insert(task_predecessors).values(
                                    task_id=new_task_id,
                                    predecessor_id=task_mapping[pred.id]
                                )
                            )
        
        # Riskleri kopyala
        source_risks = ProjectRisk.query.filter_by(project_id=project_id).all()
        for source_risk in source_risks:
            new_risk = ProjectRisk(
                project_id=new_project.id,
                title=source_risk.title,
                description=source_risk.description,
                impact=source_risk.impact,
                probability=source_risk.probability,
                mitigation_plan=source_risk.mitigation_plan,
                status='Aktif',  # Riskleri aktif duruma al
                created_by_id=source_risk.created_by_id
            )
            db.session.add(new_risk)
        
        # Dosya klasör yapısını kopyala (dosya içeriği değil, sadece referans)
        # Not: Fiziksel dosyalar kopyalanmaz, sadece referanslar oluşturulur
        source_files = ProjectFile.query.filter_by(project_id=project_id, is_active=True).all()
        for source_file in source_files:
            # Dosya referansını kopyala (fiziksel dosya kopyalanmaz)
            new_file = ProjectFile(
                project_id=new_project.id,
                user_id=source_file.user_id,
                file_name=f"Kopya - {source_file.file_name}",
                file_path=source_file.file_path,  # Aynı dosya yolunu kullan (veya yeni bir yol oluştur)
                file_size=source_file.file_size,
                file_type=source_file.file_type,
                description=f"Kopya: {source_file.description}" if source_file.description else None,
                version=1,
                is_active=True
            )
            db.session.add(new_file)
        
        db.session.commit()
        
        return new_project.id
    
    except Exception as e:
        db.session.rollback()
        raise e






















