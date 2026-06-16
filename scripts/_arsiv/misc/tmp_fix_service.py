import re
import codecs

SERVICE_PY = r'c:\kokpitim\app\services\process_performance_service.py'
ROUTES_PY = r'c:\kokpitim\app\api\process\performance_routes.py'

# 1. Truncate Service back to line 478
with open(SERVICE_PY, 'r', encoding='utf-8') as f:
    slines = f.readlines()
with open(SERVICE_PY, 'w', encoding='utf-8') as f:
    f.writelines(slines[:479])

# 2. Truncate Routes back to where we started appending (line 117 is end)
with open(ROUTES_PY, 'r', encoding='utf-8') as f:
    rlines = f.readlines()
end_idx = len(rlines)
for i, l in enumerate(rlines):
    if "@process_performance_bp.route('/api/surec/karne/pg-veri-detay'" in l:
        end_idx = i
        break
with open(ROUTES_PY, 'w', encoding='utf-8') as f:
    f.writelines(rlines[:end_idx])

# 3. Read extracted code again
with open(r'c:\kokpitim\tmp_extracted.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 4. Remove decorators
code = re.sub(r'@api_bp\.route.*?\n', '', code)
code = re.sub(r'@login_required\n', '', code)
code = re.sub(r'@csrf\.exempt\n', '', code)

# 5. Rename functions and add 'user' parameter
code = code.replace("def api_surec_karne_pg_veri_detay():", "@staticmethod\ndef get_pg_veri_detay_list(user, surec_pg_id, ceyrek, yil):")
code = code.replace("def export_surec_karnesi_excel():", "@staticmethod\ndef export_surec_karnesi_excel_service(user, surec_id, yil):")
code = code.replace("def api_pg_veri_detay(veri_id):", "@staticmethod\ndef get_pg_veri_detay(user, veri_id):")
code = code.replace("def api_pg_veri_detay_toplu():", "@staticmethod\ndef get_pg_veri_detay_toplu(user, veri_idleri):")
code = code.replace("def api_pg_veri_guncelle(veri_id):", "@staticmethod\ndef update_pg_veri(user, veri_id, gerceklesen_deger, aciklama):")

# 6. Replace current_user with user BEFORE indentation logic
code = code.replace("current_user", "user")

# 7. Remove request parsing
code = re.sub(r"^\s+surec_pg_id\s*=\s*request\.args\.get\('surec_pg_id'.*?\n", "", code, flags=re.MULTILINE)
code = re.sub(r"^\s+ceyrek\s*=\s*request\.args\.get\('ceyrek'.*?\n", "", code, flags=re.MULTILINE)
code = re.sub(r"^\s+yil\s*=\s*request\.args\.get\('yil'.*?\n", "", code, flags=re.MULTILINE)
code = re.sub(r"^\s+surec_id\s*=\s*request\.args\.get\('surec_id'.*?\n", "", code, flags=re.MULTILINE)
code = code.replace("if not request.is_json:", "if False:")
code = code.replace("data = request.get_json() or {}", "")
code = code.replace("veri_idleri = data.get('veri_idleri', [])", "")
code = code.replace("data = request.get_json()", "")
code = code.replace("gerceklesen_deger = data.get('gerceklesen_deger')", "")
code = code.replace("aciklama = data.get('aciklama')", "")

# 8. Add exactly 4 spaces to EACH line to put inside the class
lines = code.split('\n')
indented_lines = []
for line in lines:
    if line.strip() == "" or line.startswith("#" * 80):
        indented_lines.append(line)
    else:
        indented_lines.append("    " + line)

code = '\n'.join(indented_lines)

# 9. Safely cast jsonify to dict
code = code.replace("return jsonify(", "return dict(")

# For excel export, the send_file is returned. Service should just return the output, filename.
code = code.replace("return send_file(", "return tuple([output, filename]) #")

# 10. Append to process_performance_service.py
with open(SERVICE_PY, 'a', encoding='utf-8') as f:
    f.write("\n\n" + code)

# 11. Create the Blueprint endpoints in performance_routes.py
blueprint_endpoints = """
@process_performance_bp.route('/api/surec/karne/pg-veri-detay', methods=['GET'])
@login_required
def route_get_pg_veri_detay_list():
    surec_pg_id = request.args.get('surec_pg_id', type=int)
    ceyrek = request.args.get('ceyrek', type=str)
    yil = request.args.get('yil', type=int, default=datetime.now().year)
    
    try:
        data = ProcessPerformanceService.get_pg_veri_detay_list(current_user, surec_pg_id, ceyrek, yil)
        if isinstance(data, tuple) and hasattr(data[0], 'keys'): return jsonify(data[0]), data[1]
        return jsonify(data)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@process_performance_bp.route('/api/export/surec_karnesi/excel', methods=['GET'])
@login_required
def route_export_surec_karnesi_excel():
    surec_id = request.args.get('surec_id', type=int)
    yil = request.args.get('yil', type=int)
    
    try:
        data = ProcessPerformanceService.export_surec_karnesi_excel_service(current_user, surec_id, yil)
        if isinstance(data, tuple) and len(data) == 2 and isinstance(data[1], str):
            output, filename = data
            from flask import send_file
            return send_file(
                output,
                as_attachment=True,
                download_name=filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        if isinstance(data, list):
            output, filename = data[0], data[1]
            from flask import send_file
            return send_file(output, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        return jsonify(data[0]), data[1]
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@process_performance_bp.route('/api/pg-veri/detay/<int:veri_id>', methods=['GET'])
@login_required
def route_get_pg_veri_detay(veri_id):
    try:
        data = ProcessPerformanceService.get_pg_veri_detay(current_user, veri_id)
        if isinstance(data, tuple) and hasattr(data[0], 'keys'): return jsonify(data[0]), data[1]
        return jsonify(data)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

from extensions import csrf
@process_performance_bp.route('/api/pg-veri/detay/toplu', methods=['POST'])
@login_required
@csrf.exempt
def route_get_pg_veri_detay_toplu():
    data = request.get_json() or {}
    veri_idleri = data.get('veri_idleri', [])
    try:
        res = ProcessPerformanceService.get_pg_veri_detay_toplu(current_user, veri_idleri)
        if isinstance(res, tuple) and hasattr(res[0], 'keys'): return jsonify(res[0]), res[1]
        return jsonify(res)
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
        if isinstance(res, tuple) and hasattr(res[0], 'keys'): return jsonify(res[0]), res[1]
        return jsonify(res)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
"""

with open(ROUTES_PY, 'a', encoding='utf-8') as f:
    f.write("\n\n" + blueprint_endpoints)

import py_compile
try:
    py_compile.compile(SERVICE_PY, doraise=True)
    py_compile.compile(ROUTES_PY, doraise=True)
    print("Syntax check passed!")
except Exception as e:
    print(f"Syntax error: {e}")
