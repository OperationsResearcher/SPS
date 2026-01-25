
with open(r'c:\SPY_Cursor\SP_Code\main\routes.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if '/projeler/' in line and 'gorevler' in line and 'yeni' in line:
            print(f"MATCH LINE {i+1}: {line.strip()}")
        elif 'project_task_create' in line:
             print(f"DEF LINE {i+1}: {line.strip()}")
