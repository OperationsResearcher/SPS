
path = r'c:\SPY_Cursor\SP_Code\templates\stratejik_planlama_akisi.html'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

keywords = [
    'function createSwotItem',
    'function createTowsItem',
    'const canEdit =',
    'canEdit ='
]

for i, line in enumerate(lines):
    for k in keywords:
        if k in line:
            print(f"Line {i+1}: {line.strip()}")
