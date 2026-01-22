
path = r'c:\SPY_Cursor\SP_Code\templates\stratejik_planlama_akisi.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

print("--- Occurrences of 'function createSwotItem' ---")
count = 0
pos = 0
while True:
    pos = content.find('function createSwotItem', pos)
    if pos == -1: break
    # Find line number
    line_no = content.count('\n', 0, pos) + 1
    print(f"Line {line_no}")
    pos += 1
    count += 1
if count == 0: print("None found!")

print("\n--- Occurrences of 'let currentSection' ---")
count = 0
pos = 0
while True:
    pos = content.find('let currentSection', pos)
    if pos == -1: break
    line_no = content.count('\n', 0, pos) + 1
    print(f"Line {line_no}")
    pos += 1
    count += 1
if count == 0: print("None found!")
