
import sys
import os

sys.path.append(os.getcwd())
from app import create_app
from models import Task

app = create_app()
with app.app_context():
    print("-" * 30)
    print("Searching for task: 'v3 tes3'")
    tasks = Task.query.filter(Task.title.like('%v3 tes3%')).all()
    
    if not tasks:
        print("TASK NOT FOUND IN DB!")
    else:
        for t in tasks:
            print(f"Task Found: ID={t.id}")
            print(f"Title: {t.title}")
            print(f"Project ID: {t.project_id}")
            print(f"Status: {t.status}")
            print(f"Assigned To: {t.assigned_to_id}")
            print(f"Reporter: {t.reporter_id}")
            print(f"Archived: {t.is_archived}")
            
    print("-" * 30)
    print("Checking Project 2 Tasks count:")
    p2_tasks = Task.query.filter_by(project_id=2).count()
    print(f"Total tasks for Project 2: {p2_tasks}")
