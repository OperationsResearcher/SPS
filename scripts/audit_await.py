import re

file_path = r'c:\SPY_Cursor\SP_Code\templates\admin_panel.html'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Analyzing {file_path} for 'await' usage outside async functions...")

    for i, line in enumerate(lines):
        if 'await' in line:
            print(f"Line {i+1}: {line.strip()}")
            # Geriye doğru tarayıp fonksiyon tanımını bul
            found_func = False
            for j in range(i, max(-1, i-100), -1):
                l_strip = lines[j].strip()
                if 'function' in l_strip or '=>' in l_strip:
                     # Basit kontrol
                    if 'async' not in l_strip and ('function' in l_strip or ('(' in l_strip and ')' in l_strip and '=>' in l_strip)):
                        print(f"  [POTENTIAL ERROR] Inside NON-ASYNC function/block at line {j+1}: {l_strip}")
                    elif 'async' in l_strip:
                        print(f"  [OK] Inside ASYNC function at line {j+1}: {l_strip}")
                    
                    found_func = True
                    break
            
            if not found_func:
                print("  [WARNING] Could not find function definition for this await.")

except Exception as e:
    print(f"Error: {e}")
