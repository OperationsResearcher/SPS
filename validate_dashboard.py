
import sys
import os
from jinja2 import Environment, FileSystemLoader

# Add current dir to path
sys.path.append(os.getcwd())

template_dir = os.path.join(os.getcwd(), 'templates')
env = Environment(loader=FileSystemLoader(template_dir))

try:
    print("Validating v3/dashboard.html...")
    template = env.get_template('v3/dashboard.html')
    print("Template Syntax is OK.")
except Exception as e:
    print("\nTEMPLATE ERROR FOUND:")
    print(e)
    # Hatanın detaylarını yazdır
    if hasattr(e, 'lineno'):
        print(f"Line number: {e.lineno}")
