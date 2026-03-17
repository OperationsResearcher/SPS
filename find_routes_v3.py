
with open(r'c:\SPY_Cursor\SP_Code\main\routes.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'POST' in line and (('gorevler' in line) or ('task' in line)):
             print(f"POST LINE {i+1}: {line.strip()}")
