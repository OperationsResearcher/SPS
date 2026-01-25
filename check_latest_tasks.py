
import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from app import create_app
from models import Task, Project, User
from extensions import db

app = create_app()

with app.app_context():
    print("-" * 50)
    print("SON 5 GÖREV (Tasks)")
    print("-" * 50)
    
    tasks = Task.query.order_by(Task.id.desc()).limit(5).all()
    
    if not tasks:
        print("HİÇ GÖREV BULUNAMADI!")
    
    for t in tasks:
        reporter_name = "Yok"
        if t.reporter_id:
            reporter = User.query.get(t.reporter_id)
            if reporter:
                reporter_name = f"{reporter.username} (ID: {t.reporter_id})"
            else:
                reporter_name = f"Bilinmeyen (ID: {t.reporter_id})"
                
        assignee_name = "Atanmamış"
        if t.assigned_to_id:
            assignee = User.query.get(t.assigned_to_id)
            if assignee:
                assignee_name = f"{assignee.username} (ID: {t.assigned_to_id})"
        elif getattr(t, 'external_assignee_name', None):
            assignee_name = f"Dış: {t.external_assignee_name}"

        project_name = "Proje Yok"
        if t.project:
            project_name = f"{t.project.name} (ID: {t.project_id})"
            
        print(f"ID: {t.id}")
        print(f"Başlık: {t.title}")
        print(f"Proje: {project_name}")
        print(f"Durum: {t.status}")
        print(f"Atanan: {assignee_name}")
        print(f"Oluşturan: {reporter_name}")
        print(f"Arşivlendi mi?: {t.is_archived}")
        print("-" * 30)

    # Dashboard Sorgusu Kontrolü
    # Dashboard sorgusu: Task.query.filter_by(assigned_to_id=current_user.id, status='Beklemede').limit(5).all()
    # Bu sorguyu simüle edelim (User ID 1 varsayımıyla veya reporter'ı kullanarak)
    
    if tasks:
        last_task = tasks[0]
        if last_task.reporter_id:
            user_id = last_task.reporter_id
            print(f"\nDashboard Sorgusu Testi (User ID: {user_id})")
            print("Sorgu: Task.query.filter_by(assigned_to_id=user_id, status='Beklemede')")
            
            dash_tasks = Task.query.filter_by(assigned_to_id=user_id, status='Beklemede').all()
            print(f"Bulunan 'Beklemede' sayısı: {len(dash_tasks)}")
            
            # Doğrusu ne olmalı? Yapılacak + Devam Ediyor + Beklemede
            print("Önerilen Sorgu: status in ['Yapılacak', 'Devam Ediyor', 'Beklemede']")
            from utils.task_status import COMPLETED_STATUSES
            # COMPLETED_STATUSES genellikle ['Tamamlandı', 'İptal', 'Kapalı']
            
            open_tasks = Task.query.filter(
                Task.assigned_to_id == user_id,
                ~Task.status.in_(['Tamamlandı', 'Kapalı', 'İptal']),
                Task.is_archived == False
            ).all()
            print(f"Bulunan Açık Görev Sayısı: {len(open_tasks)}")
