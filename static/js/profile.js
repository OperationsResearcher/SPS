/**
 * Profil Sayfası İşlemleri
 * Inline JS temizlenmiş, Zero Defect uyumlu modül.
 */

// Email ve telefon validasyon fonksiyonları
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    // Türk telefon numarası formatları: +90 212 555 0123, 0212 555 0123, 555 123 4567, 5551234567
    const re = /^(\+90\s?)?(\(?\d{3}\)?\s?)?\d{3}[\s-]?\d{2}[\s-]?\d{2}$/;
    return re.test(phone.replace(/\s/g, ''));
}

document.getElementById('profileForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // Şifre değişikliği kontrolü
    if (newPassword || confirmPassword || currentPassword) {
        if (!currentPassword) {
            showToast('Şifre değiştirmek için mevcut şifrenizi girmelisiniz!', 'error');
            return;
        }
        if (newPassword !== confirmPassword) {
            showToast('Yeni şifreler eşleşmiyor!', 'error');
            return;
        }
        if (newPassword.length < 6) {
            showToast('Yeni şifre en az 6 karakter olmalıdır!', 'error');
            return;
        }
    }
    
    // E-posta validasyonu
    const email = document.getElementById('profileEmail').value.trim();
    if (email && !validateEmail(email)) {
        showToast('Lütfen geçerli bir e-posta adresi girin!', 'error');
        document.getElementById('profileEmail').classList.add('is-invalid');
        return;
    }
    document.getElementById('profileEmail').classList.remove('is-invalid');
    
    // Telefon validasyonu
    const phone = document.getElementById('profilePhone').value.trim();
    if (phone && !validatePhone(phone)) {
        showToast('Lütfen geçerli bir telefon numarası girin! (Örn: +90 212 555 0123 veya 0212 555 0123)', 'error');
        document.getElementById('profilePhone').classList.add('is-invalid');
        return;
    }
    document.getElementById('profilePhone').classList.remove('is-invalid');
    
    // Profil fotoğrafı URL validasyonu (opsiyonel - boş bırakılabilir)
    const profilePhotoUrl = document.getElementById('profilePhotoUrl').value.trim();
    if (profilePhotoUrl) {
        // URL veya relative path kontrolü
        const isValidUrl = profilePhotoUrl.startsWith('http://') || 
                          profilePhotoUrl.startsWith('https://') || 
                          profilePhotoUrl.startsWith('/static/') ||
                          profilePhotoUrl.startsWith('static/');
        if (!isValidUrl) {
            showToast('Profil fotoğrafı URL\'si geçerli bir format değil! (http://, https:// veya /static/ ile başlamalı)', 'error');
            document.getElementById('profilePhotoUrl').classList.add('is-invalid');
            return;
        }
    }
    document.getElementById('profilePhotoUrl').classList.remove('is-invalid');
    
    const formData = {
        email: email,
        first_name: document.getElementById('profileFirstAd').value.trim(),
        last_name: document.getElementById('profileLastAd').value.trim(),
        phone: phone,
        title: document.getElementById('profileBaslik').value.trim(),
        department: document.getElementById('profileDepartment').value.trim(),
        profile_photo: profilePhotoUrl,
        current_password: currentPassword,
        new_password: newPassword
    };
    
    // CSRF token'ı al
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    
    fetch('/profile/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken || ''
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        // Response'un JSON olup olmadığını kontrol et
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            return response.text().then(text => {
                console.error('Beklenmeyen response:', text.substring(0, 200));
                throw new Error('Sunucudan JSON yanıt alınamadı. Lütfen sayfayı yenileyip tekrar deneyin.');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            // Şifre alanlarını temizle
            document.getElementById('currentPassword').value = '';
            document.getElementById('newPassword').value = '';
            document.getElementById('confirmPassword').value = '';
            // Sayfayı yenile (profil fotoğrafı güncellemesi için)
            setTimeout(() => location.reload(), 1500);
        } else {
            showToast('Hata: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Profil güncelleme hatası:', error);
        let errorMessage = 'Beklenmedik hata oluştu.';
        if (error.message) {
            errorMessage += ' ' + error.message;
        }
        showToast(errorMessage, 'error');
    });
});

function showToast(message, type) {
    const toastEl = document.getElementById('profileToast');
    const toastMessage = document.getElementById('toastMessage');
    const toastHeader = toastEl.querySelector('.toast-header i');
    
    toastMessage.textContent = message;
    
    // İkon ve renk değiştir
    if (type === 'error') {
        toastHeader.className = 'fas fa-exclamation-circle text-danger me-2';
    } else {
        toastHeader.className = 'fas fa-check-circle text-success me-2';
    }
    
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

// Profil fotoğrafı yükleme
document.getElementById('profilePhotoInput').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    // Dosya tipini kontrol et
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/svg+xml', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showToast('Geçersiz dosya tipi! Lütfen PNG, JPG, GIF, SVG veya WEBP formatında bir resim seçin.', 'error');
        e.target.value = '';
        return;
    }
    
    // Dosya boyutunu kontrol et (5MB)
    if (file.size > 5 * 1024 * 1024) {
        showToast('Dosya boyutu çok büyük! Maksimum 5MB boyutunda dosya yükleyebilirsiniz.', 'error');
        e.target.value = '';
        return;
    }
    
    // FormData oluştur
    const formData = new FormData();
    formData.append('file', file);
    
    // CSRF token'ı ekle
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    if (csrfToken) {
        formData.append('csrf_token', csrfToken);
    }
    
    // Progress göster
    const progressDiv = document.getElementById('photoUploadProgress');
    progressDiv.style.display = 'block';
    
    // Yükleme butonunu devre dışı bırak
    const uploadBtn = document.querySelector('button[onclick*="profilePhotoInput"]');
    if (uploadBtn) uploadBtn.disabled = true;
    
    // AJAX ile yükle
    fetch('/profile/upload-photo', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken || ''
        }
    })
    .then(response => {
        // Response'un JSON olup olmadığını kontrol et
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            return response.text().then(text => {
                console.error('Beklenmeyen response:', text);
                throw new Error('Sunucudan JSON yanıt alınamadı. Lütfen sayfayı yenileyip tekrar deneyin.');
            });
        }
        return response.json();
    })
    .then(data => {
        progressDiv.style.display = 'none';
        if (uploadBtn) uploadBtn.disabled = false;
        
        if (data.success) {
            showToast(data.message, 'success');
            
            // URL alanını güncelle
            const urlInput = document.getElementById('profilePhotoUrl');
            if (urlInput) {
                urlInput.value = data.photo_url;
            }
            
            // Profil fotoğrafını güncelle - URL'i Flask static formatına çevir
            const photoContainer = document.getElementById('profilePhotoContainer');
            let photoUrl = data.photo_url;
            
            // Relative URL ise Flask static formatına çevir
            if (!photoUrl.startsWith('http://') && !photoUrl.startsWith('https://')) {
                if (photoUrl.startsWith('/static/')) {
                    // /static/uploads/profiles/... -> /static/uploads/profiles/... (zaten doğru format)
                    photoUrl = photoUrl;
                } else {
                    // static/ veya /static/ ile başlamıyorsa ekle
                    photoUrl = photoUrl.replace(/^\/?static\//, '').replace(/^\//, '');
                    photoUrl = '/static/' + photoUrl;
                }
            }
            
            // Mevcut fotoğrafı güncelle veya yeni oluştur
            const existingImg = photoContainer.querySelector('#profilePhotoImg');
            const existingDiv = photoContainer.querySelector('.rounded-circle.bg-primary');
            
            if (existingImg) {
                existingImg.src = photoUrl;
                existingImg.style.display = 'block';
                if (existingDiv) {
                    existingDiv.style.display = 'none';
                }
            } else {
                // Yeni img elementi oluştur
                const newImg = document.createElement('img');
                newImg.id = 'profilePhotoImg';
                newImg.src = photoUrl;
                newImg.alt = 'Profil';
                newImg.className = 'rounded-circle';
                newImg.style.cssText = 'width: 150px; height: 150px; object-fit: cover; border: 4px solid #007bff; cursor: pointer;';
                newImg.onclick = function() { document.getElementById('profilePhotoInput').click(); };
                newImg.onerror = function() {
                    this.style.display = 'none';
                    if (existingDiv) {
                        existingDiv.style.display = 'flex';
                    }
                };
                
                if (existingDiv) {
                    existingDiv.style.display = 'none';
                }
                photoContainer.insertBefore(newImg, photoContainer.firstChild);
            }
            
            // Sayfayı kısa bir süre sonra yenile (tüm yerlerde güncellenmesi için)
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('Hata: ' + data.message, 'error');
            e.target.value = '';
        }
    })
    .catch(error => {
        progressDiv.style.display = 'none';
        if (uploadBtn) uploadBtn.disabled = false;
        showToast('Fotoğraf yüklenirken bir hata oluştu: ' + error.message, 'error');
        e.target.value = '';
    });
});
