
import sys
import os
import json
from datetime import date, datetime

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from app import create_app
from models import Task, Project, User
from extensions import db

app = create_app()

def serialize_date(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return None

with app.app_context():
    project_id = 2
    print(f"Checking Tasks for Project ID: {project_id}")
    
    project = Project.query.get(project_id)
    if not project:
        print("Project NOT FOUND!")
        sys.exit(1)
        
    print(f"Project Name: {project.name}")
    
    tasks = Task.query.filter_by(project_id=project_id).all()
    print(f"Total Tasks Found: {len(tasks)}")
    
    task_list = []
    for t in tasks:
        print(f"Task ID: {t.id} | Title: {t.title} | Status: {t.status} | Archived: {t.is_archived}")
        
        # Simulate API payload construction
        try:
            task_data = {
                'id': t.id,
                'title': t.title,
                'description': t.description,
                'status': t.status,
                'priority': t.priority,
                'due_date': serialize_date(t.due_date),
                'start_date': serialize_date(getattr(t, 'start_date', None)),
                'estimated_time': t.estimated_time,
                'actual_time': t.actual_time,
                'parent_id': getattr(t, 'parent_id', None),
                'created_at': serialize_date(t.created_at),
                'assigned_to_id': t.assigned_to_id,
                'external_assignee_name': getattr(t, 'external_assignee_name', None),
                'assigned_to': None
            }
            if t.assigned_to:
                task_data['assigned_to'] = {
                    'id': t.assigned_to.id,
                    'first_name': t.assigned_to.first_name,
                    'last_name': t.assigned_to.last_name
                }
            task_list.append(task_data)
        except Exception as e:
            print(f"ERROR serializing task {t.id}: {e}")

    # Try to dump JSON to ensure it works
    try:
        json_output = json.dumps({'success': True, 'gorevler': task_list})
        print("\nJSON Serialization: SUCCESS")
        print(f"Payload Size: {len(json_output)} bytes")
    except Exception as e:
        print(f"\nJSON Serialization: FAILED - {e}")

