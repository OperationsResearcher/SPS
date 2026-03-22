from app import app
from flask import render_template
import os

def verify():
    print("Verifying template synthesis...")
    file_path = os.path.join(app.root_path, 'templates', 'v3', 'dashboard.html')
    print(f"Reading file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if 180 <= i+1 <= 200:
                    print(f"{i+1}: {line.rstrip()}")
    except Exception as e:
        print(f"File read error: {e}")

    with app.app_context():
        try:
            with app.test_request_context('/v3/dashboard'):
                layout_config = [{"id": "widget-1", "visible": True}]
                my_tasks = []
                stats = {'performance': 75, 'completed_tasks': 10, 'pending_tasks': 5}
                postit_content = "Test"

                render_template('v3/dashboard.html', layout_config=layout_config, my_tasks=my_tasks, stats=stats, postit_content=postit_content)
                print("TEMPLATE_SYNTAX_CHECK_PASSED")
        except Exception as e:
            print(f"TEMPLATE_ERROR: {e}")

if __name__ == "__main__":
    verify()
