
with open(r'c:\SPY_Cursor\SP_Code\api\routes.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'api/projeler/' in line and 'gorevler' in line and 'GET' in line:
            print(f"GET TASKS ROUTE {i+1}: {line.strip()}")
