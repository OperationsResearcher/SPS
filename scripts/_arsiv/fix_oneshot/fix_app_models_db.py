import os

files = [
    'app/models/audit.py',
    'app/models/email_config.py',
    'app/models/process.py',
    'app/models/saas.py',
    'app/models/strategy.py',
    'app/models/notification.py',
]

for path in files:
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = content.replace('from app.models import db', 'from extensions import db')
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Updated: {path}')
    else:
        print(f'No change: {path}')
