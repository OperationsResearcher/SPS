
import sys
import os
sys.path.append(os.getcwd())
from models import Task
from extensions import db
from app import create_app

app = create_app()
with app.app_context():
    print("Checking tasks in default DB...")
    t = Task.query.get(68)
    if t:
        print(f"Task 68 found in DEFAULT DB: {t.title}")
    else:
        print("Task 68 NOT found in DEFAULT DB")
        
    print(f"DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
