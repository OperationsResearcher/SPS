
import sys
import os
import json
from datetime import date, datetime

sys.path.append(os.getcwd())
from app import create_app
from models import Task, Project, User

app = create_app()

def serialize(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return None

with app.app_context():
    print("-" * 50)
    print("CHECKING TASK 68")
    t68 = Task.query.get(68)
    if t68:
        print(f"Task 68 Found: {t68.title}")
        print(f"Project ID: {t68.project_id}")
        print(f"Status: {t68.status}")
        print(f"Is Archived: {t68.is_archived}")
        print(f"Created At: {t68.created_at}")
    else:
        print("Task 68 NOT FOUND in DB!")
    
    print("-" * 50)
    print("CHECKING PROJECT 2 TASKS (DB QUERY)")
    p2_tasks = Task.query.filter_by(project_id=2).all()
    found = False
    for t in p2_tasks:
        if t.id == 68:
            found = True
            print(f"-> Task 68 is present in Project 2 query results.")
    
    if not found:
        print("-> Task 68 is MISSING from Project 2 query results!")

    print(f"Total tasks for Project 2: {len(p2_tasks)}")
    
    print("-" * 50)
    print("CHECKING API LOGIC SIMULATION")
    # API Logic: Task.query.filter_by(project_id=2).all()
    # Sonra JSON serialization
    try:
        tasks_data = [{
            'id': t.id,
            'title': t.title,
            'status': t.status,
            'assigned_to_id': t.assigned_to_id
        } for t in p2_tasks]
        
        # Check if 68 is in serialization
        in_json = any(x['id'] == 68 for x in tasks_data)
        print(f"Is Task 68 present in JSON data? {in_json}")
    except Exception as e:
        print(f"Error during serialization: {e}")

