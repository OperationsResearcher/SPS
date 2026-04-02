import py_compile

SERVICE_PY = r'c:\kokpitim\app\services\process_performance_service.py'

with open(SERVICE_PY, 'r', encoding='utf-8') as f:
    content = f.read()

# The unmatched brackets are from `return {\n ... \n })`
content = content.replace("            })\n", "            }\n")
content = content.replace("        })\n", "        }\n")

with open(SERVICE_PY, 'w', encoding='utf-8') as f:
    f.write(content)

try:
    py_compile.compile(SERVICE_PY, doraise=True)
    print("Syntax check passed!")
except Exception as e:
    print(f"Syntax error: {e}")
