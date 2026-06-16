import re

with open(r'c:\kokpitim\tmp_extracted.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Remove decorators
code = re.sub(r'@api_bp\.route.*?\n', '', code)
code = re.sub(r'@login_required\n', '', code)
code = re.sub(r'@csrf\.exempt\n', '', code)

# 2. Rename functions and add 'user' parameter
code = code.replace("def api_surec_karne_pg_veri_detay():", "    @staticmethod\n    def get_pg_veri_detay_list(user, surec_pg_id, ceyrek, yil):")
code = code.replace("def export_surec_karnesi_excel():", "    @staticmethod\n    def export_surec_karnesi_excel_service(user, surec_id, yil):")
code = code.replace("def api_pg_veri_detay(veri_id):", "    @staticmethod\n    def get_pg_veri_detay(user, veri_id):")
code = code.replace("def api_pg_veri_detay_toplu():", "    @staticmethod\n    def get_pg_veri_detay_toplu(user, veri_idleri):")
code = code.replace("def api_pg_veri_guncelle(veri_id):", "    @staticmethod\n    def update_pg_veri(user, veri_id, gerceklesen_deger, aciklama):")

# 3. Fix indentations: all lines must be indented by 4 more spaces to be inside the class ProcessPerformanceService
lines = code.split('\n')
indented_lines = []
for line in lines:
    if line.startswith("    @staticmethod"):
        indented_lines.append(line)
    elif line.strip() == "" or line.startswith("#" * 80):
        indented_lines.append(line)
    else:
        # Increase indent by 4 spaces
        indented_lines.append("    " + line)

code = '\n'.join(indented_lines)

# 4. Replace current_user with user
code = code.replace("current_user", "user")

# 5. Remove request parsing (since they are passed as args now)
code = re.sub(r"^\s+surec_pg_id\s*=\s*request\.args\.get\('surec_pg_id'.*?\n", "", code, flags=re.MULTILINE)
code = re.sub(r"^\s+ceyrek\s*=\s*request\.args\.get\('ceyrek'.*?\n", "", code, flags=re.MULTILINE)
code = re.sub(r"^\s+yil\s*=\s*request\.args\.get\('yil'.*?\n", "", code, flags=re.MULTILINE)
code = re.sub(r"^\s+surec_id\s*=\s*request\.args\.get\('surec_id'.*?\n", "", code, flags=re.MULTILINE)
# For toplu:
code = code.replace("if not request.is_json:", "if False:")
code = code.replace("data = request.get_json() or {}", "")
code = code.replace("veri_idleri = data.get('veri_idleri', [])", "")
# For guncelle:
code = code.replace("data = request.get_json()", "")
code = code.replace("gerceklesen_deger = data.get('gerceklesen_deger')", "")
code = code.replace("aciklama = data.get('aciklama')", "")

# 6. Replace return jsonify({...}), status with return {...}, status
# This is tricky with regex because jsonify spans multiple lines.
# We will just replace "return jsonify(" with "return " and let the developer fix remaining parens if any.
code = code.replace("return jsonify({", "return {")
# But then the closing `})` or `}), status` will be unmatched.
# Since python dicts return { ... }, we don't need to change it if we replace jsonify( { with {
# Let's use regex:
code = re.sub(r'return jsonify\(\{', 'return {', code)
code = re.sub(r'\}\),\s*(\d{3})', r'}, \1', code)
code = re.sub(r'\}\)', r'}', code)

# For excel export, the send_file is returned. Service should just return the output, filename.
code = code.replace("return send_file(", "return output, filename #")

# 7. Append to process_performance_service.py
SERVICE_PY = r'c:\kokpitim\app\services\process_performance_service.py'
with open(SERVICE_PY, 'a', encoding='utf-8') as f:
    f.write("\n\n" + code)

# 8. Create the Blueprint endpoints in performance_routes.py
blueprint_endpoints = """
@process_performance_bp.route('/api/surec/karne/pg-veri-detay', methods=['GET'])
@login_required
def route_get_pg_veri_detay_list():
    surec_pg_id = request.args.get('surec_pg_id', type=int)
    ceyrek = request.args.get('ceyrek', type=str)
    yil = request.args.get('yil', type=int, default=datetime.now().year)
    
    try:
        data = ProcessPerformanceService.get_pg_veri_detay_list(current_user, surec_pg_id, ceyrek, yil)
        return jsonify(data) if isinstance(data, dict) else jsonify(data[0]), data[1] if isinstance(data, tuple) else 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@process_performance_bp.route('/api/export/surec_karnesi/excel', methods=['GET'])
@login_required
def route_export_surec_karnesi_excel():
    surec_id = request.args.get('surec_id', type=int)
    yil = request.args.get('yil', type=int)
    
    try:
        output, filename = ProcessPerformanceService.export_surec_karnesi_excel_service(current_user, surec_id, yil)
        from flask import send_file
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@process_performance_bp.route('/api/pg-veri/detay/<int:veri_id>', methods=['GET'])
@login_required
def route_get_pg_veri_detay(veri_id):
    try:
        data = ProcessPerformanceService.get_pg_veri_detay(current_user, veri_id)
        return jsonify(data) if isinstance(data, dict) else jsonify(data[0]), data[1] if isinstance(data, tuple) else 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@process_performance_bp.route('/api/pg-veri/detay/toplu', methods=['POST'])
@login_required
@csrf.exempt
def route_get_pg_veri_detay_toplu():
    data = request.get_json() or {}
    veri_idleri = data.get('veri_idleri', [])
    try:
        res = ProcessPerformanceService.get_pg_veri_detay_toplu(current_user, veri_idleri)
        return jsonify(res) if isinstance(res, dict) else jsonify(res[0]), res[1] if isinstance(res, tuple) else 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@process_performance_bp.route('/api/pg-veri/guncelle/<int:veri_id>', methods=['PUT'])
@login_required
@csrf.exempt
def route_update_pg_veri(veri_id):
    data = request.get_json() or {}
    gerceklesen_deger = data.get('gerceklesen_deger')
    aciklama = data.get('aciklama')
    try:
        res = ProcessPerformanceService.update_pg_veri(current_user, veri_id, gerceklesen_deger, aciklama)
        return jsonify(res) if isinstance(res, dict) else jsonify(res[0]), res[1] if isinstance(res, tuple) else 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
"""

ROUTES_PY = r'c:\kokpitim\app\api\process\performance_routes.py'
with open(ROUTES_PY, 'a', encoding='utf-8') as f:
    f.write("\n\n" + blueprint_endpoints)

print("Semantic Refactoring Complete!")
