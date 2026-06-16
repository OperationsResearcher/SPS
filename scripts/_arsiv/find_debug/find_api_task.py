
with open(r'c:\SPY_Cursor\SP_Code\api\routes.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'api/projeler/' in line and 'gorevler' in line:
            print(f"ROUTE LINE {i+1}: {line.strip()}")
        if 'Task(' in line and '=' in line and 'task' in line.lower():
            print(f"TASK INSTANCE {i+1}: {line.strip()}")
