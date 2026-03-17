
with open(r'c:\SPY_Cursor\SP_Code\main\routes.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'Task(' in line or 'Task (' in line:
            print(f"TASK INSTANCE {i+1}: {line.strip()}")
        if 'models.Task' in line:
             print(f"MODELS TASK {i+1}: {line.strip()}")
