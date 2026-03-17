import re

path = r'c:\SPY_Cursor\SP_Code\templates\admin_v3.html'
print(f"Reading {path}...")

try:
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if 'await ' in line:
            print(f"Line {i+1}: {line.strip()}")
            
            # Context (hangi fonksiyon içinde?)
            for j in range(i, max(-1, i-50), -1):
                if 'function' in lines[j] or '=>' in lines[j]:
                    print(f"  In function definition (approx Line {j+1}): {lines[j].strip()}")
                    break

except Exception as e:
    print(f"Error: {e}")
