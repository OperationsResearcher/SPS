import codecs

path = r'c:\SPY_Cursor\SP_Code\main\routes.py'

try:
    with codecs.open(path, 'r', 'utf-8', errors='ignore') as f:
        content = f.read()

    if '/admin/upload-user-photo' in content:
        print("Endpoint already exists.")
    else:
        new_code = """

@main_bp.route('/admin/upload-user-photo', methods=['POST'])
@login_required
def upload_user_photo():
    import os
    import uuid
    from werkzeug.utils import secure_filename
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Dosya bulunamadı'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Dosya seçilmedi'}), 400
        
    if file:
        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
             return jsonify({'success': False, 'message': 'Desteklenmeyen dosya formatı'}), 400
             
        # Benzersiz isim
        unique_filename = f"user_{uuid.uuid4().hex}{ext}"
        
        # Klasör check
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'users')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # Kaydet
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # URL döndür
        url = f"/static/uploads/users/{unique_filename}"
        return jsonify({'success': True, 'url': url})
        
    return jsonify({'success': False, 'message': 'Yükleme başarısız'}), 500
"""
        content += new_code
        
        with codecs.open(path, 'w', 'utf-8') as f:
            f.write(content)
            print("Endpoint added to routes.py")

except Exception as e:
    print(f"Error: {e}")
