
path = r'c:\SPY_Cursor\SP_Code\templates\stratejik_planlama_akisi.html'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('--- Lines 2820-2830 ---')
for i in range(2820, 2830):
    if i < len(lines): print(f"{i+1}: {lines[i].rstrip()}")

print('--- Lines 4570-4580 ---')
for i in range(4570, 4580):
    if i < len(lines): print(f"{i+1}: {lines[i].rstrip()}")

print('--- Lines 4620-4630 ---')
for i in range(4620, 4630):
    if i < len(lines): print(f"{i+1}: {lines[i].rstrip()}")

print('--- Lines 5880-5895 ---')
for i in range(5880, 5895):
    if i < len(lines): print(f"{i+1}: {lines[i].rstrip()}")
