import codecs

path = r'c:\SPY_Cursor\SP_Code\templates\admin_v3.html'

try:
    with codecs.open(path, 'r', 'utf-8', errors='ignore') as f:
        content = f.read()

    script_ajax = """
<script>
// AJAX Photo Handlers - Automatically uploads to server
window.handlePhotoUpload = function(input) {
    if (input.files && input.files[0]) {
        var file = input.files[0];
        
        // Önizleme hemen göster
        var reader = new FileReader();
        reader.onload = function(e) {
            var preview = document.getElementById('editProfilPhotoPreview');
            var img = document.getElementById('editProfilPhotoPreviewImage');
            if (preview && img) {
                img.src = e.target.result;
                preview.style.display = 'block';
                // Opacity düşür (yükleniyor hissi)
                img.style.opacity = '0.5';
            }
        }
        reader.readAsDataURL(file);

        // Sunucuya Yükle
        var formData = new FormData();
        formData.append('file', file);
        
        var csrf = document.querySelector('meta[name="csrf-token"]')?.content || '';

        fetch('/admin/upload-user-photo', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrf
            }
        })
        .then(r => r.json())
        .then(data => {
            var img = document.getElementById('editProfilPhotoPreviewImage');
            if (img) img.style.opacity = '1';

            if (data.success) {
                // Input değerini güncelle
                var urlInput = document.getElementById('editUserProfilUrl');
                if (urlInput) urlInput.value = data.url;
                console.log("Photo uploaded: " + data.url);
                if (typeof showToast === 'function') showToast('success', 'Fotoğraf yüklendi', 'Başarılı');
            } else {
                if (typeof showToast === 'function') showToast('error', 'Hata: ' + (data.message || 'Bilinmeyen hata'), 'Hata');
                else console.error(data.message || 'Fotoğraf yükleme hatası');
            }
        })
        .catch(err => {
            var img = document.getElementById('editProfilPhotoPreviewImage');
            if (img) img.style.opacity = '1';
            console.error(err);
            if (typeof showToast === 'function') showToast('error', 'Yükleme hatası', 'Hata');
        });
    }
};

window.clearPhoto = function() {
    var input = document.getElementById('editProfilPhotoFile');
    if (input) input.value = '';
    var preview = document.getElementById('editProfilPhotoPreview');
    if (preview) preview.style.display = 'none';
    var img = document.getElementById('editProfilPhotoPreviewImage');
    if (img) img.src = '';
    
    // URL inputunu da temizle
    var urlInput = document.getElementById('editUserProfilUrl');
    if (urlInput) urlInput.value = '';
};

window.handlePhotoUrl = function(input) {
    var val = input.value;
    if (val) {
        var preview = document.getElementById('editProfilPhotoPreview');
        var img = document.getElementById('editProfilPhotoPreviewImage');
        if (preview && img) {
            img.src = val;
            preview.style.display = 'block';
        }
        var fileInput = document.getElementById('editProfilPhotoFile');
        if (fileInput) fileInput.value = '';
    }
};
console.log("AJAX Photo handlers loaded.");
</script>
</body>
"""

    if '</body>' in content:
        content = content.replace('</body>', script_ajax)
        print("Injected AJAX handlers.")
    else:
        content += script_ajax
        print("Appended AJAX handlers.")

    with codecs.open(path, 'w', 'utf-8') as f:
        f.write(content)
    
    print("Saved.")

except Exception as e:
    print(f"Error: {e}")
