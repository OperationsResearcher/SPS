
with open(r'c:\SPY_Cursor\SP_Code\main\routes.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'projeler' in line and 'route' in line:
            print(f"{i+1}: {line.strip()}")
        if 'gorevler' in line and 'yeni' in line and 'route' in line:
            print(f"{i+1}: {line.strip()}")
