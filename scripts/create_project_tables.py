# -*- coding: utf-8 -*-
"""
Project modülü tablolarını oluşturma scripti
SQL Server'da project, task ve ilgili tabloları oluşturur
"""
import sys
import os

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from __init__ import create_app
from extensions import db
from models import Project, Task, TaskImpact, TaskComment, TaskMention, ProjectFile, Tag, TaskSubtask, TimeEntry, TaskActivity, ProjectTemplate, TaskTemplate, Sprint, TaskSprint, ProjectRisk

def create_project_tables():
    """Project modülü tablolarını oluştur"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Project modülü tabloları oluşturuluyor...")
            
            # Tüm modelleri import et (zaten yukarıda import edildi)
            # Tabloları oluştur
            db.create_all()
            
            print("✓ Tüm tablolar başarıyla oluşturuldu!")
            
            # Tabloların oluşturulduğunu doğrula
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            project_tables = ['project', 'task', 'task_impact', 'task_comment', 'task_mention', 
                            'project_file', 'tag', 'task_subtask', 'time_entry', 'task_activity',
                            'project_template', 'task_template', 'sprint', 'task_sprint', 'project_risk',
                            'project_members', 'project_observers', 'project_related_processes', 
                            'task_predecessors']
            
            print("\nOluşturulan tablolar:")
            for table in project_tables:
                if table in tables:
                    print(f"  ✓ {table}")
                else:
                    print(f"  ✗ {table} (BULUNAMADI!)")
            
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    success = create_project_tables()
    if success:
        print("\n✓ İşlem tamamlandı!")
        sys.exit(0)
    else:
        print("\n❌ İşlem başarısız!")
        sys.exit(1)





















