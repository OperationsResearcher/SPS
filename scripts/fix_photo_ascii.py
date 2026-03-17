import codecs

path = r'c:\SPY_Cursor\SP_Code\templates\admin_v3.html'

try:
    with codecs.open(path, 'r', 'utf-8', errors='ignore') as f:
        content = f.read()

    # 1. HTML çağrılarını güncelle
    # Sadece 1 kez mi, tümünü mü? replace tümünü yapar.
    old_upload = 'handleDüzenleProfilPhotoYükle(this)'
    new_upload = 'handlePhotoUpload(this)'
    if old_upload in content:
        content = content.replace(old_upload, new_upload)
        print("Updated upload handler call.")

    old_url = 'handleDüzenleProfilPhotoUrl(this)'
    new_url = 'handlePhotoUrl(this)'
    if old_url in content:
        content = content.replace(old_url, new_url)
        print("Updated URL handler call.")
        
    old_clear = 'clearDüzenleProfilPhoto()'
    new_clear = 'clearPhoto()'
    if old_clear in content:
        content = content.replace(old_clear, new_clear)
        print("Updated clear handler call.")

    # 2. Script bloğu
    script_ascii = """
<script>
// ASCII Photo Handlers - NO TURKISH CHARACTERS IN FUNCTION NAMES
window.handlePhotoUpload = function(input) {
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

window.clearPhoto = function() {
    var input = document.getElementById('editProfilPhotoFile');
    if (input) input.value = '';
    var preview = document.getElementById('editProfilPhotoPreview');
    if (preview) preview.style.display = 'none';
    var img = document.getElementById('editProfilPhotoPreviewImage');
    if (img) img.src = '';
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
console.log("ASCII Photo handlers loaded.");
</script>
</body>
"""

    if 'ASCII Photo handlers' not in content:
        if '</body>' in content:
            content = content.replace('</body>', script_ascii)
            print("Injected ASCII handlers.")
        else:
            content += script_ascii
            print("Appended ASCII handlers.")

    with codecs.open(path, 'w', 'utf-8') as f:
        f.write(content)
    
    print("Saved.")

except Exception as e:
    print(f"Error: {e}")
