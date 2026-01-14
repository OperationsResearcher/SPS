import codecs

path = r'c:\SPY_Cursor\SP_Code\templates\admin_v3.html'

try:
    with codecs.open(path, 'r', 'utf-8', errors='ignore') as f:
        content = f.read()

    script_block = """
<script>
// Profil Fotoğrafı Yükleme Fonksiyonları (V3 - Injected)
window.handleDüzenleProfilPhotoYükle = function(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            var preview = document.getElementById('editProfilPhotoPreview');
            var img = document.getElementById('editProfilPhotoPreviewImage');
            if (preview && img) {
                img.src = e.target.result;
                preview.style.display = 'block';
            }
            var urlInput = document.getElementById('editUserProfilUrl');
            if (urlInput) urlInput.value = '';
        }
        reader.readAsDataURL(input.files[0]);
    }
};

window.clearDüzenleProfilPhoto = function() {
    var input = document.getElementById('editProfilPhotoFile');
    if (input) input.value = '';
    var preview = document.getElementById('editProfilPhotoPreview');
    if (preview) preview.style.display = 'none';
    var img = document.getElementById('editProfilPhotoPreviewImage');
    if (img) img.src = '';
};

window.handleDüzenleProfilPhotoUrl = function(input) {
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
console.log("Photo handlers loaded.");
</script>
</body>
"""

    if 'window.handleDüzenleProfilPhotoYükle' not in content:
        # replace finding the closing body tag
        if '</body>' in content:
            content = content.replace('</body>', script_block)
            print("Injected photo handlers.")
        else:
            # append to end if no body tag found (rare but possible in fragments)
            content += script_block
            print("Appended photo handlers to EOF.")
    else:
        print("Photo handlers already present.")

    with codecs.open(path, 'w', 'utf-8') as f:
        f.write(content)
        
    print("File saved.")

except Exception as e:
    print(f"Error: {e}")
