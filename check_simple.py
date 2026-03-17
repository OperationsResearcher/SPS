
import sys
import os
sys.path.append(os.getcwd())
from app import create_app
from models import Task

app = create_app()
with app.app_context():
    t = Task.query.order_by(Task.id.desc()).first()
    if t:
        print(f"LAST TASK ID: {t.id}")
        print(f"TITLE: {t.title}")
        print(f"STATUS: {t.status}")
        print(f"PROJECT ID: {t.project_id}")
        print(f"ASSIGNED TO: {t.assigned_to_id}")
        print(f"REPORTER: {t.reporter_id}")
    else:
        print("NO TASKS FOUND")
