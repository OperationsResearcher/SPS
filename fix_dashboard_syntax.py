
import os

file_path = os.path.join(os.getcwd(), 'templates', 'v3', 'dashboard.html')

print(f"Reading file: {file_path}")

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Hatalı blok tespiti (esnek boşluklarla)
old_block = """            const score = {{ stats.performance }
        };"""
        
new_block = """            const score = {{ stats.performance }};"""

if old_block in content:
    print("Found exact broken block. Fixing...")
    new_content = content.replace(old_block, new_block)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print("File updated successfully.")
else:
    print("Exact block match failed. Trying line-by-line analysis.")
    lines = content.split('\n')
    fixed_lines = []
    for i, line in enumerate(lines):
        if "const score = {{ stats.performance }" in line and "}}" not in line:
            print(f"Found broken line at {i+1}: {line}")
            fixed_lines.append("            const score = {{ stats.performance }};")
            # Bir sonraki satır '};' ise onu atla
            if i+1 < len(lines) and "};" in lines[i+1]:
                print(f"Skipping next line: {lines[i+1]}")
                lines[i+1] = "__JAILBREAK_DELETE__"
        elif line == "__JAILBREAK_DELETE__":
            continue
        else:
            fixed_lines.append(line)
            
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    print("Line-by-line fix applied.")
