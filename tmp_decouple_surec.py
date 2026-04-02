import os

HTML_PATH = r'c:\kokpitim\templates\surec_panel.html'
JS_PATH = r'c:\kokpitim\static\js\surec_panel.js'
CSS_PATH = r'c:\kokpitim\static\css\surec_panel.css'

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# CSS is exactly at lines 14-400 (index 13 to 399)
css_block = lines[13:400]
css_content = "".join(css_block[1:-1])  # Exclude <style> and </style>

# JS is exactly at lines 1709-4925 (index 1708 to 4924)
js_block = lines[1708:4925]
js_content = "".join(js_block[1:-1])  # Exclude <script> and </script>

# Replace Jinja binding in JS
js_content = js_content.replace(
    "{{ 'true' if current_user.sistem_rol == 'admin' else 'false' }}",
    "window.CONFIG.IS_ADMIN"
)

# Write CSS
with open(CSS_PATH, 'w', encoding='utf-8') as f:
    f.write(css_content)

# Write JS
with open(JS_PATH, 'w', encoding='utf-8') as f:
    f.write(js_content)

# Rebuild HTML
new_html_pieces = []
new_html_pieces.extend(lines[:13])
new_html_pieces.append('<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/surec_panel.css\') }}">\n')
new_html_pieces.extend(lines[400:1708])

config_script = """
{% block scripts %}
{{ super() }}
<script>
    window.CONFIG = {
        IS_ADMIN: {{ 'true' if current_user.sistem_rol == 'admin' else 'false' }}
    };
</script>
<script src="{{ url_for('static', filename='js/surec_panel.js') }}"></script>
"""
new_html_pieces.append(config_script)
new_html_pieces.extend(lines[4925:])

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    for line in new_html_pieces:
        f.write(line)

print("Decoupling Successful!")
print(f"CSS isolated: {len(css_content)} bytes")
print(f"JS isolated: {len(js_content)} bytes")
print(f"HTML reduced from {len("".join(lines))} to {len("".join(new_html_pieces))} bytes")
