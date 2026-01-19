// ==========================================
// CSRF Yardımcıları (Flask-WTF CSRF açık)
// ==========================================

function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}

function ensureCsrfInFormData(formData) {
    const csrfToken = getCsrfToken();
    if (csrfToken && formData && !formData.has('csrf_token')) {
        formData.append('csrf_token', csrfToken);
    }
    return csrfToken;
}

function csrfHeaders(extraHeaders = {}) {
    const csrfToken = getCsrfToken();
    if (!csrfToken) return extraHeaders;
    return { ...extraHeaders, 'X-CSRFToken': csrfToken };
}

async function postForm(url, formData) {
    ensureCsrfInFormData(formData);
    return fetch(url, {
        method: 'POST',
        body: formData,
        headers: csrfHeaders()
    });
}

// Kart Gizle/Göster Fonksiyonu
function toggleCardBody(button) {
    const card = button.closest('.card');
    const cardBody = card.querySelector('.card-body-collapsible');
    const icon = button.querySelector('i');
    
    if (cardBody.classList.contains('collapsed')) {
        // Aç
        cardBody.classList.remove('collapsed');
        icon.classList.remove('fa-chevron-down');
        icon.classList.add('fa-chevron-up');
        button.setAttribute('title', 'Gizle');
    } else {
        // Kapat
        cardBody.classList.add('collapsed');
        icon.classList.remove('fa-chevron-up');
        icon.classList.add('fa-chevron-down');
        button.setAttribute('title', 'Göster');
    }
}

// Toast bildirimi göster
function showToast(message, type = 'success') {
    const toastContainer = document.createElement('div');
    toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
    toastContainer.style.zIndex = '9999';
    
    const toastHTML = `
        <div class="toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'}" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.innerHTML = toastHTML;
    document.body.appendChild(toastContainer);
    
    // Başarılı işlemlerde Stratejik Planlama Akışı'nı bilgilendir
    if (type === 'success') {
        notifyStratejikPlanlamaGüncelle();
    }
    
    const toast = new bootstrap.Toast(toastContainer.querySelector('.toast'), { delay: 3000 });
    toast.show();
    
    setTimeout(() => toastContainer.remove(), 4000);
}

// ==========================
// SWOT / PESTLE / TOWS
// ==========================
function getKurumId() {
    const panel = document.getElementById('analizPanel');
    const kurumId = panel ? panel.dataset.kurumId : '';
    return kurumId ? Number(kurumId) : null;
}

function showAddSwotModal() {
    const modal = new bootstrap.Modal(document.getElementById('swotModal'));
    modal.show();
}

function showAddPestleModal() {
    const modal = new bootstrap.Modal(document.getElementById('pestleModal'));
    modal.show();
}

function showAddTowsModal() {
    const modal = new bootstrap.Modal(document.getElementById('towsModal'));
    modal.show();
}

async function saveAnaliz(form, url, modalId) {
    const kurumId = getKurumId();
    if (!kurumId) {
        showToast('Kurum bilgisi bulunamadı. Lütfen sayfayı yenileyin.', 'error');
        return;
    }
    const data = Object.fromEntries(new FormData(form));
    try {
        const response = await fetch(url.replace('{kurum_id}', kurumId), {
            method: 'POST',
            headers: csrfHeaders({ 'Content-Type': 'application/json' }),
            body: JSON.stringify(data)
        });
        const contentType = response.headers.get('content-type') || '';
        if (!contentType.includes('application/json')) {
            throw new Error('Sunucudan JSON yanıtı alınamadı.');
        }
        const res = await response.json();
        if (res.success) {
            bootstrap.Modal.getInstance(document.getElementById(modalId)).hide();
            showToast('Kayıt başarıyla oluşturuldu.');
            location.reload();
        } else {
            showToast(res.message || 'Kayıt oluşturulamadı.', 'error');
        }
    } catch (error) {
        showToast('Bir hata oluştu: ' + error.message, 'error');
    }
}

async function deleteAnaliz(url) {
    try {
        const response = await fetch(url, {
            method: 'DELETE',
            headers: csrfHeaders()
        });
        const contentType = response.headers.get('content-type') || '';
        if (!contentType.includes('application/json')) {
            throw new Error('Sunucudan JSON yanıtı alınamadı.');
        }
        const res = await response.json();
        if (res.success) {
            showToast('Silme işlemi tamamlandı.');
            location.reload();
        } else {
            showToast(res.message || 'Silme işlemi başarısız.', 'error');
        }
    } catch (error) {
        showToast('Bir hata oluştu: ' + error.message, 'error');
    }
}

function deleteSwot(id) {
    if (!confirm('Silmek istediğinize emin misiniz?')) return;
    deleteAnaliz(`/api/swot/${id}`);
}

function deletePestle(id) {
    if (!confirm('Silmek istediğinize emin misiniz?')) return;
    deleteAnaliz(`/api/pestle/${id}`);
}

function deleteTows(id) {
    if (!confirm('Silmek istediğinize emin misiniz?')) return;
    deleteAnaliz(`/api/tows/${id}`);
}

const swotForm = document.getElementById('swotForm');
if (swotForm) {
    swotForm.addEventListener('submit', function (e) {
        e.preventDefault();
        saveAnaliz(swotForm, '/api/kurum/{kurum_id}/swot', 'swotModal');
    });
}

const pestleForm = document.getElementById('pestleForm');
if (pestleForm) {
    pestleForm.addEventListener('submit', function (e) {
        e.preventDefault();
        saveAnaliz(pestleForm, '/api/kurum/{kurum_id}/pestle', 'pestleModal');
    });
}

const towsForm = document.getElementById('towsForm');
if (towsForm) {
    towsForm.addEventListener('submit', function (e) {
        e.preventDefault();
        saveAnaliz(towsForm, '/api/kurum/{kurum_id}/tows', 'towsModal');
    });
}

// Amaç ve Vizyon Düzenle
function editAmacVizyon() {
    const modal = new bootstrap.Modal(document.getElementById('amacVizyonModal'));
    modal.show();
}

document.getElementById('amacVizyonForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    ensureCsrfInFormData(formData);
    
    try {
        const response = await postForm('/kurum/update-amac-vizyon', formData);
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('amac-display').textContent = formData.get('amac') || 'Kurum amacı henüz tanımlanmamış.';
            document.getElementById('vizyon-display').textContent = formData.get('vizyon') || 'Kurum vizyonu henüz tanımlanmamış.';
            
            bootstrap.Modal.getInstance(document.getElementById('amacVizyonModal')).hide();
            showToast(data.message);
            
            // Stratejik planlama akışı sayfasını bilgilendir
            notifyStratejikPlanlamaGüncelle();
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('Bir hata oluştu: ' + error.message, 'error');
    }
});

// Değer İşlemleri
function showEkleDegerModal() {
    document.getElementById('degerModalBaşlık').textContent = 'Değer Ekle';
    document.getElementById('deger_id').value = '';
    document.getElementById('deger_baslik').value = '';
    document.getElementById('deger_aciklama').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('degerModal'));
    modal.show();
}

function editDeger(id, baslik, aciklama) {
    document.getElementById('degerModalBaşlık').textContent = 'Değer Düzenle';
    document.getElementById('deger_id').value = id;
    document.getElementById('deger_baslik').value = baslik;
    document.getElementById('deger_aciklama').value = aciklama;
    
    const modal = new bootstrap.Modal(document.getElementById('degerModal'));
    modal.show();
}

async function deleteDeger(id, baslik) {
    if (!confirm(`"${baslik}" değerini silmek istediğinizden emin misiniz?`)) return;
    
    try {
        const formData = new FormData();
        const response = await postForm(`/kurum/degerler/delete/${id}`, formData);
        const data = await response.json();
        
        if (data.success) {
            document.querySelector(`#degerler-container [data-id="${id}"]`).remove();
            
            if (document.querySelectorAll('#degerler-container [data-id]').length === 0) {
                document.getElementById('degerler-container').innerHTML = `
                    <p class="text-muted text-center py-3">
                        <i class="fas fa-info-circle me-2"></i>
                        Henüz değer tanımlanmamış.
                    </p>
                `;
            }
            
            showToast(data.message);
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('Bir hata oluştu: ' + error.message, 'error');
    }
}

document.getElementById('degerForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    ensureCsrfInFormData(formData);
    const degerId = document.getElementById('deger_id').value;
    
    const url = degerId ? `/kurum/degerler/update/${degerId}` : '/kurum/degerler/add';
    
    try {
        const response = await postForm(url, formData);
        const data = await response.json();
        
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('degerModal')).hide();
            showToast(data.message);
            location.reload(); // Reload to show changes
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('Bir hata oluştu: ' + error.message, 'error');
    }
});

// Etik Kural İşlemleri
function showEkleEtikKuralModal() {
    document.getElementById('etikKuralModalBaşlık').textContent = 'Etik Kural Ekle';
    document.getElementById('etik_kural_id').value = '';
    document.getElementById('etik_kural_baslik').value = '';
    document.getElementById('etik_kural_aciklama').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('etikKuralModal'));
    modal.show();
}

function editEtikKural(id, baslik, aciklama) {
    document.getElementById('etikKuralModalBaşlık').textContent = 'Etik Kural Düzenle';
    document.getElementById('etik_kural_id').value = id;
    document.getElementById('etik_kural_baslik').value = baslik;
    document.getElementById('etik_kural_aciklama').value = aciklama;
    
    const modal = new bootstrap.Modal(document.getElementById('etikKuralModal'));
    modal.show();
}

async function deleteEtikKural(id, baslik) {
    if (!confirm(`"${baslik}" etik kuralını silmek istediğinizden emin misiniz?`)) return;
    
    try {
        const formData = new FormData();
        const response = await postForm(`/kurum/etik-kurallari/delete/${id}`, formData);
        const data = await response.json();
        
        if (data.success) {
            document.querySelector(`#etik-kurallari-container [data-id="${id}"]`).remove();
            
            if (document.querySelectorAll('#etik-kurallari-container [data-id]').length === 0) {
                document.getElementById('etik-kurallari-container').innerHTML = `
                    <p class="text-muted text-center py-3">
                        <i class="fas fa-info-circle me-2"></i>
                        Henüz etik kuralı tanımlanmamış.
                    </p>
                `;
            }
            
            showToast(data.message);
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('Bir hata oluştu: ' + error.message, 'error');
    }
}

document.getElementById('etikKuralForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    ensureCsrfInFormData(formData);
    const etikKuralId = document.getElementById('etik_kural_id').value;
    
    const url = etikKuralId ? `/kurum/etik-kurallari/update/${etikKuralId}` : '/kurum/etik-kurallari/add';
    
    try {
        const response = await postForm(url, formData);
        const data = await response.json();
        
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('etikKuralModal')).hide();
            showToast(data.message);
            location.reload();
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('Bir hata oluştu: ' + error.message, 'error');
    }
});

// Kalite Politikası İşlemleri
function showEkleKalitePolitikasiModal() {
    document.getElementById('kalitePolitikasiModalBaşlık').textContent = 'Kalite Politikası Ekle';
    document.getElementById('kalite_politikasi_id').value = '';
    document.getElementById('kalite_politikasi_baslik').value = '';
    document.getElementById('kalite_politikasi_aciklama').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('kalitePolitikasiModal'));
    modal.show();
}

function editKalitePolitikasi(id, baslik, aciklama) {
    document.getElementById('kalitePolitikasiModalBaşlık').textContent = 'Kalite Politikası Düzenle';
    document.getElementById('kalite_politikasi_id').value = id;
    document.getElementById('kalite_politikasi_baslik').value = baslik;
    document.getElementById('kalite_politikasi_aciklama').value = aciklama;
    
    const modal = new bootstrap.Modal(document.getElementById('kalitePolitikasiModal'));
    modal.show();
}

async function deleteKalitePolitikasi(id, baslik) {
    if (!confirm(`"${baslik}" kalite politikasını silmek istediğinizden emin misiniz?`)) return;
    
    try {
        const formData = new FormData();
        const response = await postForm(`/kurum/kalite-politikalari/delete/${id}`, formData);
        const data = await response.json();
        
        if (data.success) {
            document.querySelector(`#kalite-politikalari-container [data-id="${id}"]`).remove();
            
            if (document.querySelectorAll('#kalite-politikalari-container [data-id]').length === 0) {
                document.getElementById('kalite-politikalari-container').innerHTML = `
                    <p class="text-muted text-center py-3">
                        <i class="fas fa-info-circle me-2"></i>
                        Henüz kalite politikası tanımlanmamış.
                    </p>
                `;
            }
            
            showToast(data.message);
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('Bir hata oluştu: ' + error.message, 'error');
    }
}

document.getElementById('kalitePolitikasiForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    ensureCsrfInFormData(formData);
    const kalitePolitikasiId = document.getElementById('kalite_politikasi_id').value;
    
    const url = kalitePolitikasiId ? `/kurum/kalite-politikalari/update/${kalitePolitikasiId}` : '/kurum/kalite-politikalari/add';
    
    try {
        const response = await postForm(url, formData);
        const data = await response.json();
        
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('kalitePolitikasiModal')).hide();
            showToast(data.message);
            location.reload();
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('Bir hata oluştu: ' + error.message, 'error');
    }
});

// Ana Strateji İşlemleri
function showEkleAnaStratejiModal() {
    document.getElementById('anaStratejiModalBaşlık').textContent = 'Ana Strateji Ekle';
    document.getElementById('ana_strateji_id').value = '';
    document.getElementById('ana_strateji_ad').value = '';
    document.getElementById('ana_strateji_aciklama').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('anaStratejiModal'));
    modal.show();
}

function editAnaStrateji(id, ad, aciklama) {
    document.getElementById('anaStratejiModalBaşlık').textContent = 'Ana Strateji Düzenle';
    document.getElementById('ana_strateji_id').value = id;
    document.getElementById('ana_strateji_ad').value = ad;
    document.getElementById('ana_strateji_aciklama').value = aciklama;
    
    const modal = new bootstrap.Modal(document.getElementById('anaStratejiModal'));
    modal.show();
}

async function deleteAnaStrateji(id, ad) {
    if (!confirm(`"${ad}" ana stratejisini ve tüm bağlı alt stratejileri silmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz!`)) return;
    
    try {
        const formData = new FormData();
        const response = await postForm(`/kurum/ana-stratejiler/delete/${id}`, formData);
        const data = await response.json();
        
        if (data.success) {
            // Card layout için güncellendi
            const cardCol = document.querySelector(`.col[data-id="${id}"]`);
            if (cardCol) {
                cardCol.style.transition = 'all 0.5s ease';
                cardCol.style.opacity = '0';
                cardCol.style.transform = 'scale(0.8)';
                setTimeout(() => cardCol.remove(), 500);
            }
            showToast(data.message);
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('Bir hata oluştu: ' + error.message, 'error');
    }
}

document.getElementById('anaStratejiForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    ensureCsrfInFormData(formData);
    const anaStratejiId = document.getElementById('ana_strateji_id').value;
    
    const url = anaStratejiId ? `/kurum/ana-stratejiler/update/${anaStratejiId}` : '/kurum/ana-stratejiler/add';
    
    try {
        const response = await postForm(url, formData);
        const data = await response.json();
        
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('anaStratejiModal')).hide();
            showToast(data.message);
            location.reload();
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('Bir hata oluştu: ' + error.message, 'error');
    }
});

// Alt Strateji İşlemleri
function showEkleAltStratejiModal(anaStratejiId, anaStratejiAd) {
    document.getElementById('altStratejiModalBaşlık').textContent = 'Alt Strateji Ekle';
    document.getElementById('alt_strateji_id').value = '';
    document.getElementById('alt_strateji_ana_id').value = anaStratejiId;
    document.getElementById('alt_strateji_ana_ad').value = anaStratejiAd;
    document.getElementById('alt_strateji_ad').value = '';
    document.getElementById('alt_strateji_aciklama').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('altStratejiModal'));
    modal.show();
}

function editAltStrateji(id, anaStratejiId, ad, aciklama) {
    document.getElementById('altStratejiModalBaşlık').textContent = 'Alt Strateji Düzenle';
    document.getElementById('alt_strateji_id').value = id;
    document.getElementById('alt_strateji_ana_id').value = anaStratejiId;
    document.getElementById('alt_strateji_ad').value = ad;
    document.getElementById('alt_strateji_aciklama').value = aciklama;
    
    // Card layout için güncellendi - ana strateji adını karttan al
    const anaStratejiCard = document.querySelector(`.col[data-id="${anaStratejiId}"] .card-title`);
    const anaStratejiAd = anaStratejiCard ? anaStratejiCard.textContent.trim().replace(/^.*?\s+/, '') : '';
    document.getElementById('alt_strateji_ana_ad').value = anaStratejiAd;
    
    const modal = new bootstrap.Modal(document.getElementById('altStratejiModal'));
    modal.show();
}

async function deleteAltStrateji(id, ad) {
    if (!confirm(`"${ad}" alt stratejisini silmek istediğinizden emin misiniz?`)) return;
    
    try {
        const formData = new FormData();
        const response = await postForm(`/kurum/alt-stratejiler/delete/${id}`, formData);
        const data = await response.json();
        
        if (data.success) {
            // Card layout için güncellendi
            const altStratejiItem = document.querySelector(`.alt-strateji-item[data-id="${id}"]`);
            if (altStratejiItem) {
                altStratejiItem.style.transition = 'all 0.3s ease';
                altStratejiItem.style.opacity = '0';
                altStratejiItem.style.transform = 'translateX(-20px)';
                setTimeout(() => {
                    altStratejiItem.remove();
                    
                    // Alt strateji sayısını güncelle
                    const container = altStratejiItem.closest('.alt-stratejiler-container');
                    if (container && container.querySelectorAll('.alt-strateji-item').length === 0) {
                        container.innerHTML = `
                            <div class="text-center py-3 bg-light rounded-3 border border-dashed">
                                <i class="fas fa-inbox text-muted mb-2" style="font-size: 1.5rem; opacity: 0.5;"></i>
                                <p class="text-muted small mb-0">Henüz alt strateji yok</p>
                                <small class="text-muted" style="font-size: 0.7rem;">Alt strateji eklemek için aşağıdaki butona tıklayın</small>
                            </div>
                        `;
                    }
                }, 300);
            }
            
            showToast(data.message);
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('Bir hata oluştu: ' + error.message, 'error');
    }
}

document.getElementById('altStratejiForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    ensureCsrfInFormData(formData);
    const altStratejiId = document.getElementById('alt_strateji_id').value;
    
    const url = altStratejiId ? `/kurum/alt-stratejiler/update/${altStratejiId}` : '/kurum/alt-stratejiler/add';
    
    try {
        const response = await postForm(url, formData);
        const data = await response.json();
        
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('altStratejiModal')).hide();
            showToast(data.message);
            location.reload();
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('Bir hata oluştu: ' + error.message, 'error');
    }
});

// Progress bar animasyonları
document.addEventListener('DOMContentLoaded', function() {
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = width;
        }, 500);
    });
});

// ==========================================
// CANLI GÜNCELLEME BİLDİRİMİ
// ==========================================

/**
 * Stratejik planlama akışı sayfasını bilgilendir
 * LocalStorage kullanarak diğer sekmelere veri değişikliği sinyali gönderir
 */
function notifyStratejikPlanlamaGüncelle() {
    try {
        // Son güncelleme zamanını kaydet
        const updateData = {
            timestamp: new Date().toISOString(),
            page: 'kurum_panel',
            message: 'Kurum verileri güncellendi'
        };
        
        localStorage.setItem('sp_data_updated', JSON.stringify(updateData));
        
        console.log('Stratejik planlama akışı bilgilendirildi:', updateData);
        
        // 1 saniye sonra temizle (diğer sekmeler algıladı mı kontrol için)
        setTimeout(() => {
            localStorage.removeItem('sp_data_updated');
        }, 1000);
    } catch (error) {
        console.error('LocalStorage hatası:', error);
    }
}

// Logo yükleme fonksiyonları
let selectedLogoFile = null;

function handleLogoFileSelect(input) {
    const file = input.files[0];
    if (!file) {
        selectedLogoFile = null;
        return;
    }
    
    // Dosya tipi kontrolü
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/svg+xml', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showToast('Geçersiz dosya tipi! Sadece resim dosyaları (png, jpg, gif, svg, webp) yükleyebilirsiniz.', 'error');
        input.value = '';
        selectedLogoFile = null;
        return;
    }
    
    // Dosya boyutu kontrolü (5MB)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
        showToast('Dosya boyutu çok büyük! Maksimum 5MB dosya yükleyebilirsiniz.', 'error');
        input.value = '';
        selectedLogoFile = null;
        return;
    }
    
    selectedLogoFile = file;
    
    // Önizleme göster
    const reader = new FileReader();
    reader.onload = function(e) {
        const previewImg = document.getElementById('currentLogo');
        if (previewImg) {
            previewImg.src = e.target.result;
            previewImg.style.display = 'block';
            const alertDiv = previewImg.nextElementSibling;
            if (alertDiv && alertDiv.classList.contains('alert')) {
                alertDiv.style.display = 'none';
            }
        }
    };
    reader.readAsDataURL(file);
}

async function saveLogo() {
    const logoUrlInput = document.getElementById('logoUrlInput');
    const saveBtn = document.getElementById('saveLogoBtn');
    const progressDiv = document.getElementById('logoUploadProgress');
    const progressBar = progressDiv.querySelector('.progress-bar');
    
    // Dosya yükleme varsa önce dosyayı yükle
    if (selectedLogoFile) {
        try {
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Yükleniyor...';
            progressDiv.style.display = 'block';
            progressBar.style.width = '0%';
            progressBar.setAttribute('aria-valuenow', '0');
            progressBar.textContent = '0%';
            
            const formData = new FormData();
            formData.append('file', selectedLogoFile);
            
            // CSRF token'ı ekle
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
            if (csrfToken) {
                formData.append('csrf_token', csrfToken);
            }
            
            const response = await fetch('/api/kurum/upload-logo', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken || ''
                }
            });
            
            // Response'un JSON olup olmadığını kontrol et
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const text = await response.text();
                console.error('Beklenmeyen response:', text);
                throw new Error('Sunucudan JSON yanıt alınamadı.');
            }
            
            const data = await response.json();
            
            progressDiv.style.display = 'none';
            
            if (data.success) {
                // URL input'unu güncelle
                if (logoUrlInput) {
                    logoUrlInput.value = data.logo_url;
                }
                // Logo görüntüsünü güncelle
                const currentLogo = document.getElementById('currentLogo');
                if (currentLogo) {
                    const logoUrl = data.logo_url.startsWith('http')
                        ? data.logo_url
                        : (data.logo_url.startsWith('/') ? data.logo_url : `/${data.logo_url}`);
                    currentLogo.src = logoUrl;
                    currentLogo.style.display = 'block';
                    const alertDiv = currentLogo.nextElementSibling;
                    if (alertDiv && alertDiv.classList.contains('alert')) {
                        alertDiv.style.display = 'none';
                    }
                }
                showToast('Logo başarıyla yüklendi!', 'success');
                selectedLogoFile = null;
                document.getElementById('logoFileInput').value = '';
            } else {
                throw new Error(data.message || 'Logo yüklenemedi.');
            }
        } catch (error) {
            progressDiv.style.display = 'none';
            showToast('Logo yüklenirken hata oluştu: ' + error.message, 'error');
        } finally {
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="fas fa-save me-2"></i>Logoyu Kaydet';
        }
    } else if (logoUrlInput && logoUrlInput.value.trim()) {
        // Sadece URL güncellemesi
        try {
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Kaydediliyor...';
            
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
            
            const response = await fetch('/api/kurum/update-logo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken || ''
                },
                body: JSON.stringify({
                    logo_url: logoUrlInput.value.trim()
                })
            });
            
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const text = await response.text();
                console.error('Beklenmeyen response:', text);
                throw new Error('Sunucudan JSON yanıt alınamadı.');
            }
            
            const data = await response.json();
            
            if (data.success) {
                // Logo görüntüsünü güncelle
                const currentLogo = document.getElementById('currentLogo');
                if (currentLogo) {
                    const logoUrl = data.logo_url.startsWith('http')
                        ? data.logo_url
                        : (data.logo_url.startsWith('/') ? data.logo_url : `/${data.logo_url}`);
                    currentLogo.src = logoUrl;
                    currentLogo.style.display = 'block';
                    const alertDiv = currentLogo.nextElementSibling;
                    if (alertDiv && alertDiv.classList.contains('alert')) {
                        alertDiv.style.display = 'none';
                    }
                }
                showToast('Logo URL\'si başarıyla güncellendi!', 'success');
            } else {
                throw new Error(data.message || 'Logo güncellenemedi.');
            }
        } catch (error) {
            showToast('Logo güncellenirken hata oluştu: ' + error.message, 'error');
        } finally {
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="fas fa-save me-2"></i>Logoyu Kaydet';
        }
    } else {
        showToast('Lütfen bir logo dosyası seçin veya logo URL\'si girin!', 'warning');
    }
}

// Rehber Sistemi Toggle
async function toggleGuideSystem(enabled) {
    try {
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        
        const response = await fetch('/api/kurum/toggle-guide-system', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken || ''
            },
            body: JSON.stringify({
                show_guide_system: enabled
            })
        });
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('Beklenmeyen response:', text);
            throw new Error('Sunucudan JSON yanıt alınamadı.');
        }
        
        const data = await response.json();
        
        if (data.success) {
            showToast(
                enabled 
                    ? 'İnteraktif rehber sistemi tüm kurum için aktif edildi.' 
                    : 'İnteraktif rehber sistemi tüm kurum için devre dışı bırakıldı.', 
                'success'
            );
            
            // Sayfayı yenile (eğer kullanıcı rehber sistemi kapatıyorsa)
            if (!enabled) {
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            }
        } else {
            throw new Error(data.message || 'Ayar güncellenemedi.');
        }
    } catch (error) {
        showToast('Ayar güncellenirken hata oluştu: ' + error.message, 'error');
        // Hata durumunda checkbox'ı eski haline çevir
        const checkbox = document.getElementById('guideSystemSwitch');
        if (checkbox) {
            checkbox.checked = !enabled;
        }
    }
}


// ==========================================
// SWOT / PESTLE / TOWS ANALİZ FONKSİYONLARI
// ==========================================

// SWOT Modal Aç
function showAddSwotModal() {
    const modal = new bootstrap.Modal(document.getElementById('swotModal'));
    modal.show();
}

// PESTLE Modal Aç
function showAddPestleModal() {
    const modal = new bootstrap.Modal(document.getElementById('pestleModal'));
    modal.show();
}

// TOWS Modal Aç
function showAddTowsModal() {
    const modal = new bootstrap.Modal(document.getElementById('towsModal'));
    modal.show();
}

// Global scope'a expose et (inline onclick için)
window.showAddSwotModal = showAddSwotModal;
window.showAddPestleModal = showAddPestleModal;
window.showAddTowsModal = showAddTowsModal;
window.deleteSwot = deleteSwot;
window.deletePestle = deletePestle;
window.deleteTows = deleteTows;

// SWOT Form Handler
document.addEventListener('DOMContentLoaded', function() {
    const swotForm = document.getElementById('swotForm');
    if (swotForm) {
        swotForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            const kurumId = window.KURUM_ID || 
                           document.querySelector('[data-kurum-id]')?.dataset.kurumId || 
                           null;
            
            if (!kurumId) {
                showToast('Kurum ID bulunamadı', 'error');
                return;
            }
            
            try {
                const csrfToken = getCsrfToken();
                const response = await fetch(`/api/kurum/${kurumId}/swot`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken || ''
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    bootstrap.Modal.getInstance(document.getElementById('swotModal')).hide();
                    showToast('SWOT analizi başarıyla kaydedildi', 'success');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showToast(result.message || 'Kayıt başarısız', 'error');
                }
            } catch (error) {
                showToast('Hata: ' + error.message, 'error');
            }
        });
    }
    
    // PESTLE Form Handler
    const pestleForm = document.getElementById('pestleForm');
    if (pestleForm) {
        pestleForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            const kurumId = window.KURUM_ID || 
                           document.querySelector('[data-kurum-id]')?.dataset.kurumId || 
                           null;
            
            if (!kurumId) {
                showToast('Kurum ID bulunamadı', 'error');
                return;
            }
            
            try {
                const csrfToken = getCsrfToken();
                const response = await fetch(`/api/kurum/${kurumId}/pestle`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken || ''
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    bootstrap.Modal.getInstance(document.getElementById('pestleModal')).hide();
                    showToast('PESTLE analizi başarıyla kaydedildi', 'success');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showToast(result.message || 'Kayıt başarısız', 'error');
                }
            } catch (error) {
                showToast('Hata: ' + error.message, 'error');
            }
        });
    }
    
    // TOWS Form Handler
    const towsForm = document.getElementById('towsForm');
    if (towsForm) {
        towsForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            const kurumId = window.KURUM_ID || 
                           document.querySelector('[data-kurum-id]')?.dataset.kurumId || 
                           null;
            
            if (!kurumId) {
                showToast('Kurum ID bulunamadı', 'error');
                return;
            }
            
            try {
                const csrfToken = getCsrfToken();
                const response = await fetch(`/api/kurum/${kurumId}/tows`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken || ''
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    bootstrap.Modal.getInstance(document.getElementById('towsModal')).hide();
                    showToast('TOWS analizi başarıyla kaydedildi', 'success');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showToast(result.message || 'Kayıt başarısız', 'error');
                }
            } catch (error) {
                showToast('Hata: ' + error.message, 'error');
            }
        });
    }
});

// Delete Fonksiyonları
async function deleteSwot(id) {
    if (!confirm('Bu SWOT analizini silmek istediğinize emin misiniz?')) return;
    
    try {
        const csrfToken = getCsrfToken();
        const response = await fetch(`/api/swot/${id}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken || ''
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('SWOT analizi silindi', 'success');
            setTimeout(() => location.reload(), 800);
        } else {
            showToast(result.message || 'Silme başarısız', 'error');
        }
    } catch (error) {
        showToast('Hata: ' + error.message, 'error');
    }
}

async function deletePestle(id) {
    if (!confirm('Bu PESTLE analizini silmek istediğinize emin misiniz?')) return;
    
    try {
        const csrfToken = getCsrfToken();
        const response = await fetch(`/api/pestle/${id}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken || ''
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('PESTLE analizi silindi', 'success');
            setTimeout(() => location.reload(), 800);
        } else {
            showToast(result.message || 'Silme başarısız', 'error');
        }
    } catch (error) {
        showToast('Hata: ' + error.message, 'error');
    }
}

async function deleteTows(id) {
    if (!confirm('Bu TOWS analizini silmek istediğinize emin misiniz?')) return;
    
    try {
        const csrfToken = getCsrfToken();
        const response = await fetch(`/api/tows/${id}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken || ''
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('TOWS analizi silindi', 'success');
            setTimeout(() => location.reload(), 800);
        } else {
            showToast(result.message || 'Silme başarısız', 'error');
        }
    } catch (error) {
        showToast('Hata: ' + error.message, 'error');
    }
}
