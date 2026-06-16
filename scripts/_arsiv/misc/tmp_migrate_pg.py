import re

ROUTES_PY = r'c:\kokpitim\api\routes.py'
SERVICE_PY = r'c:\kokpitim\app\services\process_performance_service.py'
NEW_ROUTES_PY = r'c:\kokpitim\app\api\process\performance_routes.py'

# The exact line numbers from our AST analysis
# api_surec_karne_pg_veri_detay: 555-729
# export_surec_karnesi_excel: 734-861
# api_pg_veri_detay: 867-1019
# api_pg_veri_detay_toplu: 1025-1203
# api_pg_veri_guncelle: 1209-1324

# Let's target api_surec_karne_pg_veri_detay for now as a Phase.
# Wait, if we just extract the code block from 553 to 730
with open(ROUTES_PY, 'r', encoding='utf-8') as f:
    lines = f.readlines()

def extract_block(start_match, end_match):
    start_idx = -1
    end_idx = -1
    for i, line in enumerate(lines):
        if start_match in line and start_idx == -1:
            # Go back up to get decorators
            j = i
            while j > 0 and lines[j-1].strip().startswith('@'):
                j -= 1
            start_idx = j
            
        if end_idx == -1 and start_idx != -1 and i > start_idx + 10:
            if end_match in line:
                end_idx = i
                break
    return start_idx, end_idx

# We will just manually read the file and extract it via script.
target_starts = [
    "@api_bp.route('/surec/karne/pg-veri-detay'",
    "@api_bp.route('/export/surec_karnesi/excel'",
    "@api_bp.route('/pg-veri/detay/<int:veri_id>'",
    "@api_bp.route('/pg-veri/detay/toplu'",
    "@api_bp.route('/pg-veri/guncelle/<int:veri_id>'"
]

extracted_blocks = []
new_lines = []
skip_until = -1

for i, line in enumerate(lines):
    if i <= skip_until:
        continue
        
    is_target = False
    for t_idx, target in enumerate(target_starts):
        if target in line:
            # Found a target route!
            is_target = True
            # The start is this line. Let's find where it ends.
            # It ends before the next @api_bp.route or at the end of the file.
            end_idx = len(lines) - 1
            for j in range(i + 1, len(lines)):
                if lines[j].startswith('@api_bp.route') or lines[j].startswith('@app.route'):
                    # The previous line is the end (minus blanks)
                    end_idx = j - 1
                    while lines[end_idx].strip() == '':
                        end_idx -= 1
                    break
            
            block = lines[i:end_idx+1]
            extracted_blocks.append((target, block))
            skip_until = end_idx
            
            # Insert a delegation stub in routes.py
            func_name = ""
            for bline in block:
                if bline.startswith("def "):
                    func_name = bline.split("def ")[1].split("(")[0]
                    break
                    
            stub = [
                f"{line}",
                f"def {func_name}(*args, **kwargs):\n",
                f"    # LOGIC MIGRATED TO app\\api\\process\\performance_routes.py\n",
                f"    from flask import redirect, url_for\n",
                f"    return jsonify({{'success': False, 'message': 'This endpoint is deprecated. Use the new /api/process/performance endpoints.'}}), 410\n\n"
            ]
            
            # Wait, instead of stubbing, let's just delete them completely since we will register them in the new blueprint.
            # Actually, deleting them is best.
            break
            
    if not is_target:
        new_lines.append(line)

# Write the pruned api/routes.py
with open(ROUTES_PY, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

# Write the extracted blocks to a temporary file so the AI can read and adapt them
with open(r'c:\kokpitim\tmp_extracted.py', 'w', encoding='utf-8') as f:
    for target, block in extracted_blocks:
        f.writelines(block)
        f.write("\n\n" + "#" * 80 + "\n\n")

print(f"Extraction complete. Pruned {len(lines) - len(new_lines)} lines from routes.py")
print(f"Extracted blocks saved to tmp_extracted.py")
