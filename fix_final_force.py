
path = r'c:\SPY_Cursor\SP_Code\templates\stratejik_planlama_akisi.html'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Force replace the broken string (it is consistent across all errors)
broken = "]else 'false' }"
fixed = "] else 'false' }};"

if broken in content:
    print(f"Found {content.count(broken)} instances of broken syntax.")
    content = content.replace(broken, fixed)
else:
    print("Broken syntax not found via string matching!")

# Also check for single closing brace variant if indentation varies
broken2 = "]else 'false'}"
if broken2 in content:
    print(f"Found {content.count(broken2)} instances of broken syntax variant 2.")
    content = content.replace(broken2, fixed)

# Remove the garbage `};` lines that follow
# These are likely `    };` or `    }; \n`
# We use regex to be safe about whitespace
import re
content = re.sub(r'^\s*\}\;\s*$', '', content, flags=re.MULTILINE)

# Remove `let currentSection = '';` specifically
content = content.replace("    let currentSection = '';", "")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied force fix.")
