
try:
    with open(r'c:\SPY_Cursor\SP_Code\templates\surec_karnesi.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if 'addPerformansModal' in line:
                print(f"Line {i+1}: {line.strip()}")
except Exception as e:
    print(e)
