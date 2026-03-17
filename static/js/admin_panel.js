// Kurum Ýþlemleri
async function confirmDelete(title, text) {
    // SweetAlert varsa kullan, yoksa tarayıcı confirm'üne düş
    if (typeof Swal !== 'undefined') {
        const result = await Swal.fire({
            title: title || 'Emin misiniz?',
            text: text || '',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Evet, sil',
            cancelButtonText: 'İptal'
        });
        return result.isConfirmed;
    }
    const message = text ? `${title}\n\n${text}` : (title || 'Emin misiniz?');
    return window.confirm(message);
}

// Kullanıcı listesi arama (server-rendered tablo)
function filterUserList() {
    const input = document.getElementById('user-search-input');
    const term = (input?.value || '').toLowerCase();
    const rows = document.querySelectorAll('#userTableBody tr');
    rows.forEach(row => {
        const haystack = row.textContent.toLowerCase();
        row.style.display = term === '' || haystack.includes(term) ? '' : 'none';
    });
}

// Kurum Ýþlemleri
function viewOrganization(orgAd) {
    // Loading göster
    const modalBody = document.querySelector('#viewOrganizationModal .modal-body');
    if (modalBody) {
        showLoading('viewOrgContent', 'Kurum bilgileri yükleniyor...');
    }
    fetch(`/admin/get-organization/${orgAd}`)
        .then(response => response.json())
        .then(data => {
            console.log('Kurum verisi:', data); // Debug log
            if (data.success) {
                const org = data.organization;
                console.log('Organization object:', org); // Debug log
                document.getElementById('viewOrgLogo').src = org.logo_url || '/static/images/default-org-logo.png';
                document.getElementById('viewOrgKisaAd').textContent = org.kisa_ad || '-';
                document.getElementById('viewOrgTicariUnvan').textContent = org.ticari_unvan || '-';
                document.getElementById('viewOrgSektor').textContent = org.sektor || '-';
                document.getElementById('viewOrgCalisanSayisi').textContent = org.calisan_sayisi || '-';
                document.getElementById('viewOrgFaaliyetAlani').textContent = org.faaliyet_alani || '-';
                document.getElementById('viewOrgEmail').textContent = org.email || '-';
                document.getElementById('viewOrgTelefon').textContent = org.telefon || '-';
                document.getElementById('viewOrgWeb').textContent = org.web_adresi || '-';
                document.getElementById('viewOrgVergiDairesi').textContent = org.vergi_dairesi || '-';
                document.getElementById('viewOrgVergiNumarasi').textContent = org.vergi_numarasi || '-';
                // Store for edit
                window.currentOrgAd = orgAd;
                const modal = new bootstrap.Modal(document.getElementById('viewOrganizationModal'), {
                    backdrop: true,
                    keyboard: true
                });
                modal.show();
            } else {
                showToast('error', data.message || 'Ýþlem gerçekleþtirilemedi. Lütfen tekrar deneyin.');
            }
        })
        .catch(error => {
            console.error('Fetch error:', error); // Debug log
            if (error.name === 'TipError' && error.message.includes('fetch')) {
                showToast('error', 'Sunucuya baÝlanılamıyor. Lütfen internet baÝlantınızı kontrol edin.');
            } else {
                showToast('error', 'Bir hata oluþtu: ' + (error.message || 'Bilinmeyen hata'));
            }
        });
}
function editOrganizationFromGörüntüle() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('viewOrganizationModal'));
    modal.hide();
    setTimeout(() => editOrganization(window.currentOrgAd), 300);
}
function editOrganization(orgAd) {
    fetch(`/admin/get-organization/${orgAd}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const org = data.organization;
                document.getElementById('editOrgId').value = org.id;
                document.getElementById('editOrgOldKisaAd').value = org.kisa_ad;
                document.getElementById('editOrgKisaAd').value = org.kisa_ad || '';
                document.getElementById('editOrgTicariUnvan').value = org.ticari_unvan || '';
                document.getElementById('editOrgFaaliyetAlani').value = org.faaliyet_alani || '';
                document.getElementById('editOrgSektor').value = org.sektor || '';
                document.getElementById('editOrgCalisanSayisi').value = org.calisan_sayisi || '';
                document.getElementById('editOrgEmail').value = org.email || '';
                document.getElementById('editOrgTelefon').value = org.telefon || '';
                document.getElementById('editOrgWeb').value = org.web_adresi || '';
                document.getElementById('editOrgVergiDairesi').value = org.vergi_dairesi || '';
                document.getElementById('editOrgVergiNumarasi').value = org.vergi_numarasi || '';
                document.getElementById('editOrgLogoUrl').value = org.logo_url || '';
                // Logo önizlemesi
                if (org.logo_url) {
                    showDüzenleLogoPreview(org.logo_url);
                } else {
                    hideDüzenleLogoPreview();
                }
                const modal = new bootstrap.Modal(document.getElementById('editOrganizationModal'), {
                    backdrop: true,
                    keyboard: true
                });
                modal.show();
            } else {
                showToast('error', data.message || 'Ýþlem gerçekleþtirilemedi. Lütfen tekrar deneyin.');
            }
        })
        .catch(error => {
            if (error.name === 'TipError' && error.message.includes('fetch')) {
                showToast('error', 'Sunucuya baÝlanılamıyor. Lütfen internet baÝlantınızı kontrol edin.');
            } else {
                showToast('error', 'Bir hata oluþtu: ' + (error.message || 'Bilinmeyen hata'));
            }
        });
}
function updateOrganization() {
    const formData = {
        id: document.getElementById('editOrgId').value,
        old_kisa_ad: document.getElementById('editOrgOldKisaAd').value,
        kisa_ad: document.getElementById('editOrgKisaAd').value.trim(),
        ticari_unvan: document.getElementById('editOrgTicariUnvan').value.trim(),
        faaliyet_alani: document.getElementById('editOrgFaaliyetAlani').value.trim(),
        sektor: document.getElementById('editOrgSektor').value.trim(),
        calisan_sayisi: document.getElementById('editOrgCalisanSayisi').value,
        email: document.getElementById('editOrgEmail').value.trim(),
        telefon: document.getElementById('editOrgTelefon').value.trim(),
        web_adresi: document.getElementById('editOrgWeb').value.trim(),
        vergi_dairesi: document.getElementById('editOrgVergiDairesi').value.trim(),
        vergi_numarasi: document.getElementById('editOrgVergiNumarasi').value.trim(),
        logo_url: document.getElementById('editOrgLogoUrl').value.trim()
    };
    if (!formData.kisa_ad || !formData.ticari_unvan) {
        showToast('warning', 'Lütfen zorunlu alanları doldurun!', 'Eksik Bilgi');
        return;
    }
    // E-posta validasyonu
    if (formData.email && !validateEmail(formData.email)) {
        showToast('warning', 'Lütfen geçerli bir e-posta adresi girin!', 'Validasyon Hatası');
        document.getElementById('editOrgEmail').classList.add('is-invalid');
        return;
    }
    // Telefon validasyonu
    if (formData.telefon && !validatePhone(formData.telefon)) {
        showToast('warning', 'Lütfen geçerli bir telefon numarası girin! (Çrn: +90 212 555 0123 veya 0212 555 0123)', 'Validasyon Hatası');
        document.getElementById('editOrgTelefon').classList.add('is-invalid');
        return;
    }

    const csrf = document.querySelector('meta[name="csrf-token"]')?.content || '';
    fetch('/admin/update-organization', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf
        },
        body: JSON.stringify(formData)
    })
    .then(async (response) => {
        const contentType = response.headers.get('content-type') || '';
        if (!response.ok) {
            if (contentType.includes('application/json')) {
                const errData = await response.json();
                throw new Error(errData?.message || `HTTP ${response.status}`);
            }
            throw new Error(`HTTP ${response.status} ${response.statusText}`);
        }
        if (!contentType.includes('application/json')) {
            throw new Error('Sunucudan beklenen JSON yanıtı gelmedi. (CSRF/hata sayfası olabilir)');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            if (typeof window.showToast === 'function') {
                window.showToast('success', data.message || 'Kurum güncellendi', 'Başarılı');
            }
            const modal = bootstrap.Modal.getInstance(document.getElementById('editOrganizationModal'));
            modal.hide();
            reloadPage(1500);
        } else {
            if (typeof window.showToast === 'function') {
                window.showToast('error', 'Hata: ' + (data.message || 'İşlem başarısız'), 'Hata');
            }
        }
    })
    .catch(error => {
        if (typeof window.showToast === 'function') {
            window.showToast('error', 'Beklenmedik hata: ' + (error.message || 'Bilinmeyen hata'), 'Hata');
        }
    });
}
async function deleteOrganization(orgAd, orgId) {
    const confirmed = await confirmDelete(`"${orgAd}" kurumunu silmek istediðinizden emin misiniz?`, "Bu iþlem geri alınamaz ve kurumdaki tüm kullanıcılar, süreçler ve veriler silinecektir!");
    if (confirmed) {
        const csrf = document.querySelector('meta[name="csrf-token"]')?.content || '';
        fetch(`/admin/delete-organization/${orgId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, 'success');
                reloadPage(1500);
            } else {
                showToast('error', data.message || 'Ýþlem gerçekleþtirilemedi. Lütfen tekrar deneyin.');
            }
        })
        .catch(error => {
            if (error.name === 'TipError' && error.message.includes('fetch')) {
                showToast('error', 'Sunucuya baÝlanılamıyor. Lütfen internet baÝlantınızı kontrol edin.');
            } else {
                showToast('error', 'Bir hata oluþtu: ' + (error.message || 'Bilinmeyen hata'));
            }
        });
    }
}
function openNewOrganizationModal() {
    try {
        const modalEl = document.getElementById('newOrgModal');
        if (!modalEl) {
            console.error('newOrgModal bulunamadı!');
            if (typeof window.showToast === 'function') {
                window.showToast('error', 'Modal elementi bulunamadı. Sayfayı yenileyin.', 'Hata');
            }
            return;
        }
        // Form alanlarını temizle
        const form = document.getElementById('newOrgForm');
        if (form) {
            form.reset();
        }
        if (typeof clearLogo === 'function') {
            clearLogo();
        }
        // Modal'ı göster
        const modal = new bootstrap.Modal(modalEl, {
            backdrop: true,
            keyboard: true
        });
        modal.show();
    } catch (error) {
        console.error('Modal açma hatası:', error);
        if (typeof window.showToast === 'function') {
            window.showToast('error', 'Modal açılırken hata oluþtu: ' + error.message, 'Hata');
        }
    }
}
// Yeni kurum oluştur
function createNewOrganization(evt) {
    const formData = {
        kisa_ad: document.getElementById('newOrgKisaAd').value.trim(),
        ticari_unvan: document.getElementById('newOrgTicariUnvan').value.trim(),
        faaliyet_alani: document.getElementById('newOrgFaaliyetAlani').value.trim(),
        calisan_sayisi: document.getElementById('newOrgCalisanSayisi').value,
        sektor: document.getElementById('newOrgSektor').value,
        email: document.getElementById('newOrgEmail').value.trim(),
        telefon: document.getElementById('newOrgTelefon').value.trim(),
        web_adresi: document.getElementById('newOrgWeb').value.trim(),
        vergi_dairesi: document.getElementById('newOrgVergiDairesi').value.trim(),
        vergi_numarasi: document.getElementById('newOrgVergiNumarasi').value.trim(),
        logo_url: document.getElementById('newOrgLogoUrl').value.trim()
    };
    // Zorunlu alan kontrolü
    if (!formData.kisa_ad || !formData.ticari_unvan) {
        showToast('warning', 'Lütfen zorunlu alanları (*) doldurun!', 'Eksik Bilgi');
        return;
    }
    // E-posta validasyonu
    if (formData.email && !validateEmail(formData.email)) {
        showToast('warning', 'Lütfen geçerli bir e-posta adresi girin!', 'Validasyon Hatası');
        document.getElementById('newOrgEmail').classList.add('is-invalid');
        return;
    }
    // Telefon validasyonu
    if (formData.telefon && !validatePhone(formData.telefon)) {
        showToast('warning', 'Lütfen geçerli bir telefon numarası girin! (Örn: +90 212 555 0123 veya 0212 555 0123)', 'Validasyon Hatası');
        document.getElementById('newOrgTelefon').classList.add('is-invalid');
        return;
    }
    // Submit butonunu devre dışı bırak
    const submitBtn = (evt && evt.target) ? evt.target : document.getElementById('createOrgSubmitBtn');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Oluşturuluyor...';
    }

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    fetch('/admin/add-organization', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
        },
        body: JSON.stringify(formData)
    })
    .then(async (response) => {
        const contentType = response.headers.get('content-type') || '';
        if (!contentType.includes('application/json')) {
            const text = await response.text();
            // CSRF hatası çoğu zaman HTML döndürür; kullanıcıya anlamlı mesaj verelim.
            const hint = text && text.toLowerCase().includes('csrf')
                ? ' (CSRF token eksik/yanlış olabilir)'
                : '';
            throw new Error('Sunucudan JSON yanıt alınamadı' + hint);
        }
        const data = await response.json();
        if (!response.ok && data && data.message) {
            throw new Error(data.message);
        }
        return data;
    })
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            // Modal'ı kapat
            const modal = bootstrap.Modal.getInstance(document.getElementById('newOrgModal'));
            modal.hide();
            // Sayfayı yenile
            reloadPage(1500);
        } else {
            showToast('Hata: ' + data.message, 'error');
        }
    })
    .catch(error => {
        showToast('Beklenmedik hata: ' + error.message, 'error');
    })
    .finally(() => {
        // Submit butonunu tekrar aktif et
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-save me-2"></i>Kurum Oluştur';
        }
    });
}
// Kullanıcı Ýþlemleri - Yeni API tabanlı versiyon
let adminUsersCache = [];
let adminAllowedRoles = [];
let adminSystemRoles = [];
let adminProcessRoles = [];
let currentDüzenleUserId = null;
let currentDüzenleUserData = null;
const PROCESS_ROLES = ['surec_lideri', 'surec_uyesi'];
const ROLE_BADGES = {
    'sistem_admin': { text: 'Sistem Admin', class: 'bg-danger' },
    'admin': { text: 'Sistem Admin', class: 'bg-danger' },
    'kurum_yetkilisi': { text: 'Kurum Yetkilisi', class: 'bg-warning' },
    'kurum_yoneticisi': { text: 'Kurum Yöneticisi', class: 'bg-warning' },
    'ust_yonetim': { text: 'Üst Yönetim', class: 'bg-info' },
    'surec_lideri': { text: 'Süreç Lideri', class: 'bg-success' },
    'surec_uyesi': { text: 'Süreç Üyesi', class: 'bg-primary' },
    'kurum_kullanici': { text: 'Kurum Kullanıcısı', class: 'bg-secondary' },
    'user': { text: 'Kullanıcı', class: 'bg-secondary' }
};
function escapeHtml(unsafe) {
    if (unsafe === null || unsafe === undefined) return '';
    return unsafe
        .toString()
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
function getRoleBadge(role) {
    const normalized = (role || '').toLowerCase();
    const badge = ROLE_BADGES[normalized] || ROLE_BADGES.user;
    return `<span class="badge ${badge.class} mb-1">${badge.text}</span>`;
}
function renderUserRow(user) {
    const initials = escapeHtml((user.username || '?').charAt(0).toUpperCase());
    const fullAd = user.full_name
        ? escapeHtml(user.full_name)
        : (user.first_name || user.last_name
            ? `${escapeHtml(user.first_name || '')} ${escapeHtml(user.last_name || '')}`.trim()
            : '<span class="text-muted">-</span>');
    const profileCell = user.profile_photo
        ? `<img src="${escapeHtml(user.profile_photo)}" alt="${escapeHtml(user.username)}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 50%;">`
        : `<div style="width: 40px; height: 40px; background: linear-gradient(45deg, #007bff, #28a745); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">${initials}</div>`;
    const systemRole = user.sistem_rol || user.role;
    const roleBadgeHtml = getRoleBadge(systemRole);
    const roleDisplay = escapeHtml(user.role_display || '');
    const processCounts = user.process_counts || { liderlik: 0, uyelik: 0, toplam: 0 };
    const processÖzet = user.process_summary
        ? escapeHtml(user.process_summary)
        : 'Süreç ataması yok';
    const processTooltip = `Liderlik: ${processCounts.liderlik || 0}  Üyelik: ${processCounts.uyelik || 0}  Toplam: ${processCounts.toplam || 0}`;
    const processesInfo = `<span class="text-muted small" title="${escapeHtml(processTooltip)}"><i class="fas fa-info-circle me-1"></i>${processÖzet}</span>`;
    const kurumAdi = user.kurum_adi ? escapeHtml(user.kurum_adi) : '-';
    const buttons = `
        <div class="btn-group" role="group" aria-label="Kullanıcı işlemleri">
            <button class="btn btn-sm btn-outline-info" onclick="viewUser(${user.id})" title="Görüntüle">
                <i class="fas fa-eye"></i>
            </button>
            ${user.can_edit ? `
            <button class="btn btn-sm btn-outline-primary" onclick="editUser(${user.id})" title="Düzenle">
                <i class="fas fa-edit"></i>
            </button>` : `
            <button class="btn btn-sm btn-outline-secondary" disabled title="Bu kullanıcıyı düzenleme yetkiniz yok">
                <i class="fas fa-lock"></i>
            </button>`}
            ${user.can_delete ? `
            <button class="btn btn-sm btn-outline-danger" onclick="deleteUser(${user.id}, '${escapeHtml(user.username)}')" title="Sil">
                <i class="fas fa-trash"></i>
            </button>` : ''}
        </div>
    `;
    return `
        <tr>
            <td>${profileCell}</td>
            <td>${escapeHtml(user.username)}</td>
            <td>${fullAd}</td>
            <td>${escapeHtml(user.email || '')}</td>
            <td>
                <div class="d-flex flex-column">
                    ${roleBadgeHtml}
                    ${roleDisplay ? `<span class="text-muted small">${roleDisplay}</span>` : ''}
                    <div class="small mt-1">${processesInfo}</div>
                </div>
            </td>
            <td class="text-center">${kurumAdi}</td>
            <td class="text-center">${buttons}</td>
        </tr>
    `;
}
function populateRoleSelect(selectId, selectedValue = '') {
    const select = document.getElementById(selectId);
    if (!select) return;
    const current = selectedValue || select.dataset.defaultValue || '';
    const roles = adminSystemRoles.length ? adminSystemRoles : ['kurum_kullanici'];
    const optionItems = roles.map(role => {
        const badge = ROLE_BADGES[role] || ROLE_BADGES.user;
        return `<option value="${role}">${badge.text}</option>`;
    });
    select.innerHTML = `<option value="">Sistem rolü seçiniz...</option>${optionItems.join('')}`;
    if (current) {
        select.value = current;
    } else if (roles.length > 0) {
        select.value = roles[0];
    }
}
function populateProcessRoleSelect(selectId, selectedValue = '') {
    const select = document.getElementById(selectId);
    if (!select) return;
    const current = selectedValue || select.dataset.defaultValue || '';
    const roles = adminProcessRoles.length ? adminProcessRoles : PROCESS_ROLES;
    const optionItems = roles.map(role => {
        const badge = ROLE_BADGES[role] || ROLE_BADGES.user;
        return `<option value="${role}">${badge.text}</option>`;
    });
    select.innerHTML = `<option value="">Süreç rolü seçiniz...</option>${optionItems.join('')}`;
    if (current) {
        select.value = current;
    }
}
function setUserTableLoading() {
    const tbody = document.getElementById('userTableBody');
    const empty = document.getElementById('userTableEmpty');
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Yükleniyor...</span>
                    </div>
                    <div class="text-muted mt-3">Kullanıcı listesi yükleniyor...</div>
                </td>
            </tr>
        `;
    }
    if (empty) empty.style.display = 'none';
}
// Pagination deÝiþkenleri
let currentUserPage = 1;
const usersPerPage = 20;
function loadAdminUsers() {
    setUserTableLoading();
    fetch('/api/admin/users')
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                throw new Error(data.message || 'Kullanıcı listesi alınamadı.');
            }
            adminUsersCache = data.data.users || [];
            adminAllowedRoles = data.data.allowed_roles || [];
            adminSystemRoles = adminAllowedRoles.filter(role => !PROCESS_ROLES.includes(role));
            if (!adminSystemRoles.includes('kurum_kullanici')) {
                adminSystemRoles.unshift('kurum_kullanici');
            }
            adminProcessRoles = PROCESS_ROLES.filter(role => adminAllowedRoles.includes(role));
            if (adminProcessRoles.length === 0) {
                adminProcessRoles = PROCESS_ROLES.slice();
            }
            const tbody = document.getElementById('userTableBody');
            const empty = document.getElementById('userTableEmpty');
            if (adminUsersCache.length === 0) {
                if (tbody) tbody.innerHTML = '';
                if (empty) empty.style.display = 'block';
                renderUserPagination();
                return;
            }
            if (empty) empty.style.display = 'none';
            renderUserTable();
            renderUserPagination();
            const newRoleSelect = document.getElementById('newUserRole');
            const editRoleSelect = document.getElementById('editUserRole');
            const newProcessSelect = document.getElementById('newUserProcessRole');
            const editProcessSelect = document.getElementById('editUserProcessRole');
            populateRoleSelect('newUserRole');
            populateRoleSelect('editUserRole', editRoleSelect ? editRoleSelect.value : '');
            populateProcessRoleSelect('newUserProcessRole');
            populateProcessRoleSelect('editUserProcessRole', editProcessSelect ? editProcessSelect.value : '');
            showRoleAçıklama(newRoleSelect ? newRoleSelect.value : '');
            showRoleAçıklamaDüzenle(editRoleSelect ? editRoleSelect.value : '');
        })
        .catch(error => {
            showToast('error', 'Kullanıcı listesi yüklenirken hata oluþtu: ' + error.message, 'Hata');
        });
}
function renderUserTable() {
    const tbody = document.getElementById('userTableBody');
    if (!tbody) return;
    const startIndex = (currentUserPage - 1) * usersPerPage;
    const endIndex = startIndex + usersPerPage;
    const pageUsers = adminUsersCache.slice(startIndex, endIndex);
    if (pageUsers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center py-5 text-muted">Bu sayfada kullanıcı bulunmuyor.</td></tr>';
        return;
    }
    tbody.innerHTML = pageUsers.map(renderUserRow).join('');
}
function renderUserPagination() {
    const totalPages = Math.ceil(adminUsersCache.length / usersPerPage);
    const container = document.getElementById('userPagination');
    if (!container) return;
    container.className = 'd-flex flex-wrap justify-content-between align-items-center mt-3 gap-2';

    if (totalPages <= 1) {
        container.innerHTML = `<div class="text-muted small">Toplam ${adminUsersCache.length} kullanıcı</div>`;
        return;
    }

    let paginationHTML = '';
    paginationHTML += `<div class="text-muted small">Toplam ${adminUsersCache.length} kullanıcı · Sayfa ${currentUserPage} / ${totalPages}</div>`;
    paginationHTML += `<nav><ul class="pagination pagination-sm mb-0">`;
    // Önceki sayfa
    paginationHTML += `
        <li class="page-item ${currentUserPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changeUserPage(${currentUserPage - 1}); return false;">Önceki</a>
        </li>
    `;
    // Sayfa numaraları
    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentUserPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    if (endPage - startPage < maxVisiblePages - 1) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    if (startPage > 1) {
        paginationHTML += `<li class="page-item"><a class="page-link" href="#" onclick="changeUserPage(1); return false;">1</a></li>`;
        if (startPage > 2) {
            paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
    }
    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `
            <li class="page-item ${i === currentUserPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="changeUserPage(${i}); return false;">${i}</a>
            </li>
        `;
    }
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
        paginationHTML += `<li class="page-item"><a class="page-link" href="#" onclick="changeUserPage(${totalPages}); return false;">${totalPages}</a></li>`;
    }
    // Sonraki sayfa
    paginationHTML += `
        <li class="page-item ${currentUserPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changeUserPage(${currentUserPage + 1}); return false;">Sonraki</a>
        </li>
    `;
    paginationHTML += `</ul></nav>`;

    container.innerHTML = paginationHTML;
}
function changeUserPage(page) {
    const totalPages = Math.ceil(adminUsersCache.length / usersPerPage);
    if (page < 1 || page > totalPages) return;
    currentUserPage = page;
    renderUserTable();
    renderUserPagination();
    // Sayfanın üstüne kaydır
    document.getElementById('userTableBody').scrollIntoView({ behavior: 'smooth', block: 'start' });
}
function viewUser(userId) {
    (async () => {
        try {
            const res = await fetch(`/api/admin/users/${userId}`);
            const data = await res.json();
            if (!res.ok || !data.success) throw new Error(data.message || 'Kullanıcı bilgisi alınamadı.');
            const user = data.data;
            currentDüzenleUserId = user.id;

            const photo = document.getElementById('viewUserPhoto');
            if (photo) {
                photo.src = user.profile_photo || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.username)}&background=007bff&color=fff`;
            }
            const setText = (id, val) => {
                const el = document.getElementById(id);
                if (el) el.textContent = val;
            };
            setText('viewUserUsername', user.username);
            setText('viewUserEmail', user.email || '-');
            setText('viewUserId', user.id);
            setText('viewUserKurum', user.kurum_adi || '-');

            const roleBadge = document.getElementById('viewUserRoleBadge');
            if (roleBadge) {
                const roleKey = user.sistem_rol || user.role;
                const badge = ROLE_BADGES[roleKey] || ROLE_BADGES.user;
                roleBadge.textContent = user.role_display || badge.text;
                roleBadge.className = 'badge ' + badge.class;
            }

            const proc = document.getElementById('viewUserProcesses');
            if (proc) {
                if (user.process_roles && user.process_roles.length) {
                    const items = user.process_roles.map(pr => {
                        const badge = ROLE_BADGES[pr.rol] || ROLE_BADGES.user;
                        const icon = pr.rol === 'surec_lideri' ? 'fa-crown text-warning' : 'fa-users text-primary';
                        return `<li class="list-group-item d-flex justify-content-between align-items-center">
                                    <div>
                                        <i class="fas ${icon} me-2"></i>${escapeHtml(pr.ad)}
                                        ${pr.kurum_adi ? `<span class="badge bg-light text-muted ms-2">${escapeHtml(pr.kurum_adi)}</span>` : ''}
                                    </div>
                                    <span class="badge ${badge.class}">${badge.text}</span>
                                </li>`;
                    }).join('');
                    proc.innerHTML = `<div class="card border-0 bg-light"><div class="card-body p-0"><ul class="list-group list-group-flush">${items}</ul></div></div>`;
                } else {
                    proc.innerHTML = '<p class="text-muted"><i class="fas fa-info-circle me-2"></i>Bu kullanıcıya atanmış süreç rolü yok.</p>';
                }
            }

            const modal = new bootstrap.Modal(document.getElementById('viewUserModal'));
            modal.show();
        } catch (err) {
            showToast('Kullanıcı bilgisi alınırken hata oluştu: ' + err.message, 'error');
        }
    })();
}
function editUserFromGörüntüle() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('viewUserModal'));
    modal?.hide();
    if (currentDüzenleUserId) {
        setTimeout(() => editUser(currentDüzenleUserId), 300);
    }
}
async function editUser(userId) {
    try {
        const res = await fetch(`/api/admin/users/${userId}`);
        const data = await res.json();
        if (!res.ok || !data.success) throw new Error(data.message || 'Kullanıcı bilgileri yüklenemedi');
        const user = data.data;
        currentDüzenleUserId = user.id;
        const setVal = (id, val = '') => {
            const el = document.getElementById(id);
            if (el) el.value = val;
        };
        setVal('editUserId', user.id);
        setVal('editUserUsername', user.username);
        setVal('editUserFirstAd', user.first_name || '');
        setVal('editUserLastAd', user.last_name || '');
        setVal('editUserEmail', user.email || '');
        setVal('editUserPassword', '');
        setVal('editUserProfilUrl', user.profile_photo || '');
        setVal('editUserKurum', user.kurum_id || '');
        const roleSel = document.getElementById('editUserRole');
        if (roleSel) roleSel.value = user.sistem_rol || user.role || '';
        const processSel = document.getElementById('editUserProcessRole');
        if (processSel) processSel.value = user.surec_rol || '';
        const modal = new bootstrap.Modal(document.getElementById('editUserModal'));
        modal.show();
    } catch (err) {
        showToast('error', 'Hata: ' + err.message);
    }
}
function saveUserChanges() {
    return updateUser();
}
function updateUser() {
    if (!currentDüzenleUserId) {
        showToast('error', 'Güncellenecek kullanıcı bulunamadı.');
        return;
    }
    const csrf = document.querySelector('meta[name="csrf-token"]')?.content || '';
    const systemRole = document.getElementById('editUserRole').value;
    const processRole = document.getElementById('editUserProcessRole').value;
    const formData = {
        username: document.getElementById('editUserUsername').value.trim(),
        first_name: document.getElementById('editUserFirstAd').value.trim(),
        last_name: document.getElementById('editUserLastAd').value.trim(),
        email: document.getElementById('editUserEmail').value.trim(),
        password: document.getElementById('editUserPassword').value,
        role: systemRole,
        system_role: systemRole,
        process_role: processRole || null,
        kurum_id: document.getElementById('editUserKurum').value,
        profile_photo: document.getElementById('editUserProfilUrl').value.trim()
    };
    if (!formData.username || !formData.email || !formData.role || !formData.kurum_id) {
        showToast('warning', 'Lütfen zorunlu alanları doldurun!');
        return;
    }
    fetch(`/api/admin/users/update/${currentDüzenleUserId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf
        },
        body: JSON.stringify(formData)
    })
    .then(res => res.json().then(data => ({ res, data })))
    .then(({ res, data }) => {
        if (!res.ok || !data.success) throw new Error(data.message || 'Güncelleme başarısız');
        showToast('success', 'Kullanıcı güncellendi');
        bootstrap.Modal.getInstance(document.getElementById('editUserModal'))?.hide();
        setTimeout(() => location.reload(), 1200);
    })
    .catch(err => {
        showToast('error', 'Hata: ' + err.message);
    });
}
async function deleteUser(userId, username) {
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
  Swal.fire({
    title: 'Kullanıcı Sil',
    text: `"${username}" kullanıcısını silmek istediğinize emin misiniz?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#dc3545',
    cancelButtonColor: '#6c757d',
    confirmButtonText: 'Evet, Sil',
    cancelButtonText: 'İptal'
  }).then(async (result) => {
    if (result.isConfirmed) {
      try {
        const response = await fetch(`/api/admin/users/delete/${userId}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
          }
        });
        const data = await response.json();
        if (response.ok) {
                    showToast('success', `Kullanıcı başarıyla silindi: ${data.message}`);
          setTimeout(() => location.reload(), 1500);
        } else {
                    showToast('error', `Hata: ${data.message || 'Bilinmeyen hata'}`);
        }
      } catch (error) {
                showToast('error', `Hata: ${error.message}`);
      }
    }
  });
}
// Expose functions for inline onclick handlers
window.viewUser = viewUser;
window.editUser = editUser;
window.deleteUser = deleteUser;
window.editUserFromGörüntüle = editUserFromGörüntüle;
window.saveUserChanges = saveUserChanges;
window.updateUser = updateUser;
function createNewUser() {
    const kurumSelect = document.getElementById('newUserKurum');
    const submitBtn = document.getElementById('newUserSubmitButton');
    const systemRole = document.getElementById('newUserRole').value;
    const processRole = document.getElementById('newUserProcessRole').value;
    const formData = {
        username: document.getElementById('newUserUsername').value.trim(),
        first_name: document.getElementById('newUserFirstAd').value.trim(),
        last_name: document.getElementById('newUserLastAd').value.trim(),
        email: document.getElementById('newUserEmail').value.trim(),
        password: document.getElementById('newUserPassword').value,
        role: systemRole,
        system_role: systemRole,
        process_role: processRole || null,
        kurum_id: kurumSelect ? (kurumSelect.disabled ? kurumSelect.options[kurumSelect.selectedIndex].value : kurumSelect.value) : null,
        profile_photo: document.getElementById('newUserProfilUrl').value.trim()
    };
    if (!formData.username || !formData.first_name || !formData.last_name || !formData.email || !formData.password || !formData.role || !formData.kurum_id) {
        showToast('warning', 'Lütfen tüm zorunlu alanları (*) doldurun!');
        return;
    }
    // E-posta validasyonu
    if (!validateEmail(formData.email)) {
        showToast('warning', 'Lütfen geçerli bir e-posta adresi girin!', 'Validasyon Hatası');
        document.getElementById('newUserEmail').classList.add('is-invalid');
        return;
    }
    if (formData.password.length < 6) {
        showToast('warning', 'Şifre en az 6 karakter olmalıdır!');
        return;
    }
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Oluşturuluyor...';
    }
    fetch('/api/admin/users/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(res => res.json())
    .then(data => {
        if (!data.success) {
            throw new Error(data.message || 'Kullanıcı oluşturulamadı.');
        }
        showToast(data.message, 'success');
        const modal = bootstrap.Modal.getInstance(document.getElementById('newUserModal'));
        modal.hide();
        loadAdminUsers();
        document.getElementById('newUserForm').reset();
        clearProfilPhoto();
    })
    .catch(error => {
        showToast('Kullanıcı oluşturulurken hata oluştu: ' + error.message, 'error');
    })
    .finally(() => {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-save me-2"></i>Kullanıcı Oluştur';
        }
    });
}
function openNewUserModal() {
    try {
        const modalEl = document.getElementById('newUserModal');
        if (!modalEl) {
            console.error('newUserModal bulunamadı!');
            if (typeof window.showToast === 'function') {
                window.showToast('error', 'Modal elementi bulunamadı. Sayfayı yenileyin.', 'Hata');
            }
            return;
        }
        const form = document.getElementById('newUserForm');
        if (form) {
            form.reset();
        }
        if (typeof clearProfilPhoto === 'function') {
            clearProfilPhoto();
        }
        if (typeof populateRoleSelect === 'function') {
            populateRoleSelect('newUserRole');
        }
        if (typeof populateProcessRoleSelect === 'function') {
            populateProcessRoleSelect('newUserProcessRole');
        }
        const roleSelect = document.getElementById('newUserRole');
        if (roleSelect && typeof showRoleAçıklama === 'function') {
            showRoleAçıklama(roleSelect.value);
        }
        const modal = new bootstrap.Modal(modalEl, {
            backdrop: true,
            keyboard: true
        });
        modal.show();
    } catch (error) {
        console.error('Modal açma hatası:', error);
        if (typeof window.showToast === 'function') {
            window.showToast('error', 'Modal açılırken hata oluþtu: ' + error.message, 'Hata');
        }
    }
}
// ===========================
// Toplu Kullanıcı Yükleme Fonksiyonları
// ===========================
function downloadUserTemplate() {
    // Excel Şablonunu İndir
    if (typeof window.showToast === 'function') {
        window.showToast('info', 'Excel Şablonu İndiriliyor...', 'Bilgi');
    }
    window.location.href = '/admin/download-user-template';
}
function openBulkYükleModal() {
    try {
        const modalEl = document.getElementById('bulkYükleModal');
        if (!modalEl) {
            console.error('bulkYükleModal bulunamadı!');
            if (typeof window.showToast === 'function') {
                window.showToast('error', 'Modal elementi bulunamadı. Sayfayı yenileyin.', 'Hata');
            }
            return;
        }
        // Form alanlarını temizle
        const fileInput = document.getElementById('bulkYükleFile');
        if (fileInput) {
            fileInput.value = '';
        }
        const progressEl = document.getElementById('uploadProgress');
        if (progressEl) {
            progressEl.style.display = 'none';
        }
        const resultEl = document.getElementById('uploadResult');
        if (resultEl) {
            resultEl.style.display = 'none';
        }
        // Modal'ı göster
        const modal = new bootstrap.Modal(modalEl, {
            backdrop: true,
            keyboard: true
        });
        modal.show();
    } catch (error) {
        console.error('Modal açma hatası:', error);
        if (typeof window.showToast === 'function') {
            window.showToast('error', 'Modal açılırken hata oluþtu: ' + error.message, 'Hata');
        }
    }
}
function uploadBulkUsers() {
    const fileInput = document.getElementById('bulkYükleFile');
    const file = fileInput.files[0];
    // Dosya seçilmiş mi kontrol et
    if (!file) {
        if (typeof window.showToast === 'function') {
            window.showToast('warning', 'Lütfen bir Excel dosyası seçin!', 'Uyarı');
        }
        return;
    }
    // Dosya uzantısı kontrolü
    const fileAd = file.name.toLowerCase();
    if (!fileAd.endsWith('.xlsx') && !fileAd.endsWith('.xls')) {
        if (typeof window.showToast === 'function') {
            window.showToast('error', 'Sadece Excel dosyaları (.xlsx, .xls) yüklenebilir!', 'Hata');
        }
        return;
    }
    // Progress bar göster
    document.getElementById('uploadProgress').style.display = 'block';
    document.getElementById('uploadResult').style.display = 'none';
    // FormData oluştur
    const formData = new FormData();
    formData.append('excel_file', file);
    const csrf = document.querySelector('meta[name="csrf-token"]')?.content;
    const headers = {};
    if (csrf) headers['X-CSRFToken'] = csrf;
    // Dosyayı sunucuya gönder
    fetch('/admin/upload-users-excel', {
        method: 'POST',
        headers,
        body: formData
    })
    .then(async (response) => {
        const contentType = response.headers.get('content-type') || '';
        if (!response.ok) {
            if (contentType.includes('application/json')) {
                const errData = await response.json();
                throw new Error(errData?.message || `HTTP ${response.status}`);
            }
            // Muhtemelen CSRF/HTML hata sayfası
            throw new Error(`HTTP ${response.status} ${response.statusText}`);
        }

        if (!contentType.includes('application/json')) {
            throw new Error('Sunucudan beklenen JSON yanıtı gelmedi. (CSRF veya hata sayfası olabilir)');
        }
        return response.json();
    })
    .then(data => {
        // Progress bar gizle
        document.getElementById('uploadProgress').style.display = 'none';
        if (data.success) {
            // Sonuç mesajını göster
            let resultHTML = `
                <div class="alert alert-${data.error_count > 0 ? 'warning' : 'success'}" role="alert">
                    <h6 class="alert-heading">
                        <i class="fas fa-${data.error_count > 0 ? 'exclamation-triangle' : 'check-circle'} me-2"></i>
                        Yükleme Tamamlandı
                    </h6>
                    <hr>
                    <p class="mb-2">
                        <strong>${data.success_count}</strong> kullanıcı başarıyla eklendi.
                        ${data.error_count > 0 ? `<br><strong>${data.error_count}</strong> kullanıcı eklenemedi.` : ''}
                    </p>
            `;
            // Hata detayları varsa göster
            if (data.errors && data.errors.length > 0) {
                resultHTML += `
                    <hr>
                    <p class="mb-2"><strong>Hatalar:</strong></p>
                    <ul class="mb-0 small">
                `;
                data.errors.forEach(error => {
                    resultHTML += `<li>${error}</li>`;
                });
                resultHTML += `</ul>`;
                if (data.error_count > data.errors.length) {
                    resultHTML += `<p class="small text-muted mb-0 mt-2">... ve ${data.error_count - data.errors.length} hata daha</p>`;
                }
            }
            resultHTML += `</div>`;
            document.getElementById('uploadResult').innerHTML = resultHTML;
            document.getElementById('uploadResult').style.display = 'block';
            // Toast bildirim
            if (typeof window.showToast === 'function') {
                window.showToast(data.error_count > 0 ? 'warning' : 'success', data.message, data.error_count > 0 ? 'Uyarı' : 'Başarılı');
            }
            // Baþarılı ise sayfayı yenile
            if (data.success_count > 0) {
                reloadPage(3000);
            }
        } else {
            // Hata mesajı
            document.getElementById('uploadResult').innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    <strong>Hata:</strong> ${data.message}
                </div>
            `;
            document.getElementById('uploadResult').style.display = 'block';
            if (typeof window.showToast === 'function') {
                window.showToast('error', 'Hata: ' + data.message, 'Hata');
            }
        }
    })
    .catch(error => {
        // Progress bar gizle
        document.getElementById('uploadProgress').style.display = 'none';
        // Hata mesajı
        document.getElementById('uploadResult').innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="fas fa-exclamation-circle me-2"></i>
                <strong>Beklenmedik Hata:</strong> ${error.message}
            </div>
        `;
        document.getElementById('uploadResult').style.display = 'block';
        if (typeof window.showToast === 'function') {
            window.showToast('error', 'Beklenmedik hata: ' + error.message, 'Hata');
        }
    });
}
// Inline tetikleyiciler için global erişim
window.createNewUser = createNewUser;
window.openNewUserModal = openNewUserModal;
window.downloadUserTemplate = downloadUserTemplate;
window.openBulkYükleModal = openBulkYükleModal;
window.uploadBulkUsers = uploadBulkUsers;
// Logo Ýþleme Fonksiyonları
function handleLogoYükle(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        // Dosya boyutu kontrolü (16MB)
        if (file.size > 16 * 1024 * 1024) {
            showToast('error', 'Dosya boyutu 16MB\'dan büyük olamaz!', 'Hata');
            input.value = '';
            return;
        }
        // Dosya türü kontrolü
        const allowedTips = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/svg+xml', 'image/webp'];
        if (!allowedTips.includes(file.type)) {
            showToast('error', 'Geçersiz dosya formatı! Sadece PNG, JPG, JPEG, GIF, SVG, WEBP desteklenir.', 'Hata');
            input.value = '';
            return;
        }
        // Logo yükleme
        const formData = new FormData();
        formData.append('logo', file);
        const csrf = document.querySelector('meta[name="csrf-token"]')?.content;
        const headers = {};
        if (csrf) headers['X-CSRFToken'] = csrf;
        // Yükle butonu göster
        input.disabled = true;
        input.parentElement.innerHTML += '<div class="spinner-border spinner-border-sm ms-2" id="uploadSpinner"></div>';
        fetch('/admin/upload-logo', {
            method: 'POST',
            headers,
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // URL alanını doldur ve önizlemeyi göster
                document.getElementById('newOrgLogoUrl').value = data.logo_url;
                showLogoPreview(data.logo_url);
                showToast('success', data.message, 'Baþarılı');
            } else {
                showToast('error', data.message || 'Logo yüklenirken bir hata oluþtu', 'Hata');
            }
        })
        .catch(error => {
            handleAjaxError(error, 'Logo yüklenirken bir hata oluþtu');
        })
        .finally(() => {
            input.disabled = false;
            const spinner = document.getElementById('uploadSpinner');
            if (spinner) spinner.remove();
        });
    }
}
// Global scope'a ekle
window.handleLogoYükle = handleLogoYükle;

// ASCII-safe aliases (inline HTML handlers are more reliable this way)
function handleLogoYukle(input) {
    return window.handleLogoYükle ? window.handleLogoYükle(input) : undefined;
}
window.handleLogoYukle = handleLogoYukle;

function handleLogoUrl(input) {
    const url = input.value.trim();
    if (url) {
        showLogoPreview(url);
    } else {
        hideLogoPreview();
    }
}
function showLogoPreview(url) {
    const preview = document.getElementById('logoPreview');
    const previewImage = document.getElementById('logoPreviewImage');
    previewImage.src = url;
    previewImage.onerror = function() {
        showToast('error', 'Logo URL\'si geçersiz veya eriþilemiyor!', 'Hata');
        hideLogoPreview();
    };
    previewImage.onload = function() {
        preview.style.display = 'block';
    };
}
function hideLogoPreview() {
    document.getElementById('logoPreview').style.display = 'none';
    document.getElementById('logoPreviewImage').src = '';
}
function clearLogo() {
    document.getElementById('newOrgLogoUrl').value = '';
    document.getElementById('logoFile').value = '';
    hideLogoPreview();
}
// Profil FotoÝrafı Ýþleme Fonksiyonları
function handleProfilPhotoYükle(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        // Dosya boyutu kontrolü (16MB)
        if (file.size > 16 * 1024 * 1024) {
            showToast('warning', 'Dosya boyutu 16MB\'dan büyük olamaz!', 'Uyarı');
            input.value = '';
            return;
        }
        // Dosya türü kontrolü
        const allowedTips = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/webp'];
        if (!allowedTips.includes(file.type)) {
            showToast('warning', 'Geçersiz dosya formatı! Sadece PNG, JPG, JPEG, GIF, WEBP desteklenir.', 'Uyarı');
            input.value = '';
            return;
        }
        // FotoÝraf yükleme
        const formData = new FormData();
        formData.append('profile_photo', file);
        const csrf = document.querySelector('meta[name="csrf-token"]')?.content;
        const headers = {};
        if (csrf) headers['X-CSRFToken'] = csrf;
        // Yükle butonu göster
        input.disabled = true;
        input.parentElement.innerHTML += '<div class="spinner-border spinner-border-sm ms-2" id="photoYükleSpinner"></div>';
        fetch('/admin/upload-profile-photo', {
            method: 'POST',
            headers,
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // URL alanını doldur ve önizlemeyi göster
                document.getElementById('newUserProfilUrl').value = data.photo_url;
                showProfilPhotoPreview(data.photo_url);
                showToast('success', data.message, 'Baþarılı');
            } else {
                showToast('error', data.message || 'Profil fotoÝrafı yüklenirken bir hata oluþtu', 'Hata');
            }
        })
        .catch(error => {
            handleAjaxError(error, 'Profil fotoÝrafı yüklenirken bir hata oluþtu');
        })
        .finally(() => {
            input.disabled = false;
            const spinner = document.getElementById('photoYükleSpinner');
            if (spinner) spinner.remove();
        });
    }
}
// Global scope'a ekle
window.handleProfilPhotoYükle = handleProfilPhotoYükle;

function handleProfilPhotoUrl(input) {
    const url = input.value.trim();
    if (url) {
        showProfilPhotoPreview(url);
        clearAvatarSelection();
    } else {
        hideProfilPhotoPreview();
    }
}
// Global scope'a ekle
window.handleProfilPhotoUrl = handleProfilPhotoUrl;

function selectIconAvatar(element, iconAd, gradient, iconClass) {
    // Çnceki seçimleri temizle
    const allAvatars = element.closest('.d-flex').querySelectorAll('.avatar-option');
    allAvatars.forEach(avatar => {
        avatar.style.border = '2px solid transparent';
    });
    // Bu avatar'ı seçili yap
    element.style.border = '3px solid #007bff';
    // Canvas kullanarak avatar oluþtur
    const canvas = document.createElement('canvas');
    canvas.width = 200;
    canvas.height = 200;
    const ctx = canvas.getContext('2d');
    // Gradient renklerini ayıkla
    const colors = gradient.match(/#[a-fA-F0-9]{6}/g) || ['#007bff', '#0056b3'];
    // Gradient oluþtur
    const grd = ctx.createLinearGradient(0, 0, 200, 200);
    grd.addColorStop(0, colors[0]);
    grd.addColorStop(1, colors[1] || colors[0]);
    // Daire çiz
    ctx.beginPath();
    ctx.arc(100, 100, 98, 0, 2 * Math.PI);
    ctx.fillStyle = grd;
    ctx.fill();
    // Icon yazısını çiz (FontAwesome karakterini simüle et)
    ctx.fillStyle = 'white';
    ctx.font = 'bold 80px "Font Awesome 5 Free"';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    // Icon class'ından emoji veya basit metin çıkar
    const iconMap = {
        'fa-water': 'ð§', 'fa-sun': 'âï¸', 'fa-leaf': 'ð', 'fa-tree': 'ð³',
        'fa-snowflake': 'âï¸', 'fa-fire': 'ð¥', 'fa-cat': 'ð±', 'fa-dog': 'ð¶',
        'fa-butterfly': 'ð¦', 'fa-fish': 'ð ', 'fa-dove': 'ðï¸', 'fa-frog': 'ð¸',
        'fa-star': 'â­', 'fa-moon': 'ð', 'fa-rocket': 'ð', 'fa-satellite': 'ð°ï¸',
        'fa-globe': 'ð', 'fa-meteor': 'âï¸', 'fa-futbol': 'â½', 'fa-basketball-ball': 'ð',
        'fa-swimmer': 'ð', 'fa-biking': 'ð´', 'fa-running': 'ð', 'fa-trophy': 'ð',
        'fa-briefcase': 'ð¼', 'fa-crown': 'ð', 'fa-gem': 'ð', 'fa-heart': 'â¤ï¸',
        'fa-lightbulb': 'ð¡', 'fa-cog': 'âï¸', 'fa-guitar': 'ð¸', 'fa-headphones': 'ð§',
        'fa-microphone': 'ð¤', 'fa-drum': 'ð¥', 'fa-piano': 'ð¹', 'fa-pizza-slice': 'ð',
        'fa-hamburger': 'ð', 'fa-ice-cream': 'ð¦', 'fa-birthday-cake': 'ð',
        'fa-apple-alt': 'ð', 'fa-plane': 'âï¸', 'fa-suitcase-rolling': 'ð§³',
        'fa-ship': 'ð¢', 'fa-camera': 'ð·', 'fa-map': 'ðºï¸', 'fa-compass': 'ð§­',
        'fa-music': 'ðµ', 'fa-gamepad': 'ð®', 'fa-utensils': 'ð´', 'fa-coffee': 'â'
    };
    const iconText = iconMap[iconClass] || 'â­';
    ctx.fillText(iconText, 100, 105);
    // Canvas'ı Data URL'ye çevir
    const avatarDataUrl = canvas.toDataURL('image/png');
    // URL alanını doldur
    document.getElementById('newUserProfilUrl').value = avatarDataUrl;
    // Çnizlemeyi göster
    showProfilPhotoPreview(avatarDataUrl);
}
function createIconAvatarDataUrl(gradient, iconClass, size = 128) {
    // SVG kullanarak daha kaliteli avatar oluþtur
    const gradientId = 'grad_' + Math.random().toString(36).substr(2, 9);
    // Gradient renklerini ayıkla
    const colors = gradient.match(/#[a-fA-F0-9]{6}|rgb\([^)]+\)/g) || ['#007bff', '#0056b3'];
    // Icon SVG pathları - Çok daha kapsamlı koleksiyon
    const iconPaths = {
        // DoÝa Teması
        'fa-sun': 'M256 160c-52.9 0-96 43.1-96 96s43.1 96 96 96 96-43.1 96-96-43.1-96-96-96zm246.4 80.5l-94.7-47.3 33.5-100.4c4.5-13.6-8.4-26.5-21.9-21.9l-100.4 33.5-47.3-94.7c-6.4-12.8-24.6-12.8-31 0l-47.3 94.7L92.7 70.8c-13.6-4.5-26.5 8.4-21.9 21.9l33.5 100.4-94.7 47.3c-12.8 6.4-12.8 24.6 0 31l94.7 47.3-33.5 100.4c-4.5 13.6 8.4 26.5 21.9 21.9l100.4-33.5 47.3 94.7c6.4 12.8 24.6 12.8 31 0l47.3-94.7 100.4 33.5c13.6 4.5 26.5-8.4 21.9-21.9l-33.5-100.4 94.7-47.3c13-6.5 13-24.7.2-31.1zm-155.9 106c-49.9 49.9-131.1 49.9-181 0-49.9-49.9-49.9-131.1 0-181 49.9-49.9 131.1-49.9 181 0 49.9 49.9 49.9 131.1 0 181z',
        'fa-water': 'M218.5 234.3c-8.7-36.1 18.2-66.3 54.3-66.3s63 30.2 54.3 66.3c-4.6 19.2-18.6 34.8-36.6 40.9l-5.7 1.9v54.9c0 8.8-7.2 16-16 16s-16-7.2-16-16v-54.9l-5.7-1.9c-18-6.1-32-21.7-36.6-40.9z',
        'fa-leaf': 'M272.5 5.7c-15-5.2-31.5 2.2-37.4 16.7L194.5 87.7c-2.6 6.4-7.7 11.4-14.2 13.9L115.1 123.2c-14.5 5.8-21.9 22.4-16.7 37.4l39.6 114.3c2.6 7.5 2 15.9-1.3 22.9L76.8 370.9c-7.4 15.8-.1 35.4 16.6 41.9l114.3 44.2c7.5 2.9 15.9 2.3 22.9-1.3l73.1-37.9c14.5-7.5 32.5-2.1 40.8 12.3L395 505.2c8.7 15 28.4 19.8 43.1 10.5l114.3-72.6c7.1-4.5 12.3-11.2 14.6-19.1l27.9-94.3c5.2-17.6-6.4-35.9-24.7-38.8L498 284.8c-7.1-1.1-13.4-5.3-17.4-11.6L439.2 206c-8.7-13.8-6.9-32 4.3-44.1l68.8-74.1c11.9-12.8 11.9-32.9 0-45.7L439.2 68c-11.2-12-13-30.3-4.3-44.1L476.3 6.8c8.7-13.8 6.9-32-4.3-44.1C460.1-49.2 439.7-49.2 427.8-37.3L272.5 5.7z',
        'fa-tree': 'M128 384c0 17.7 14.3 32 32 32h64v96c0 17.7 14.3 32 32 32h128c17.7 0 32-14.3 32-32v-96h64c17.7 0 32-14.3 32-32 0-123.7-100.3-224-224-224S128 260.3 128 384z',
        'fa-fire': 'M216.85 158.64c-.78-25.33-27.03-45.64-52.36-45.64-25.33 0-51.58 20.31-52.36 45.64-.78 25.33 26.25 51.58 52.36 51.58s53.14-26.25 52.36-51.58zM256 0C114.62 0 0 114.62 0 256s114.62 256 256 256 256-114.62 256-256S397.38 0 256 0zm0 464c-114.87 0-208-93.13-208-208S141.13 48 256 48s208 93.13 208 208-93.13 208-208 208z',
        'fa-snowflake': 'M224 128l-32-32v32l-32-32 32 32h-32l32 32-32 32h32l-32 32 32-32v32l32-32-32-32 32-32h32l-32-32 32-32z',
        // Hayvanlar Teması
        'fa-cat': 'M290.59 192c-20.18 0-106.82 1.98-162.59 85.95V192c0-52.94-43.06-96-96-96-17.67 0-32 14.33-32 32s14.33 32 32 32c17.64 0 32 14.36 32 32v256c0 35.3 28.72 64 64 64h176c8.84 0 16-7.16 16-16v-16c0-17.67-14.33-32-32-32h-32l128-96v144c0 9.43 8.57 16 16 16h32c8.84 0 16-7.16 16-16V289.86c-10.29 2.67-20.89 4.54-32 4.54-61.81 0-113.52-44.05-125.41-102.4z',
        'fa-dog': 'M298.2 156.6c-52.7-25.7-114.5-10.5-150.2 32.8l55.2 55.2c6.3 6.3 6.3 16.4 0 22.6l-11.3 4.7L130.4 217c-42.3 35.7-57.5 97.5-31.8 150.2 20.5 42.1 61.8 67.9 107.8 67.9z',
        'fa-butterfly': 'M256 352c17.7 0 32-14.3 32-32V64c0-35.3-28.7-64-64-64s-64 28.7-64 64v256c0 17.7 14.3 32 32 32z',
        'fa-fish': 'M298.2 156.6c-52.7-25.7-114.5-10.5-150.2 32.8l55.2 55.2c6.3 6.3 6.3 16.4 0 22.6-3.1 3.1-7.2 4.7-11.3 4.7s-8.2-1.6-11.3-4.7L130.4 217c-42.3 35.7-57.5 97.5-31.8 150.2 20.5 42.1 61.8 67.9 107.8 67.9z',
        'fa-dove': 'M256 96c0-17.7 14.3-32 32-32s32 14.3 32 32-14.3 32-32 32-32-14.3-32-32zM160 256c0-35.3 28.7-64 64-64s64 28.7 64 64-28.7 64-64 64-64-28.7-64-64z',
        'fa-frog': 'M224 96c0-35.3 28.7-64 64-64s64 28.7 64 64-28.7 64-64 64-64-28.7-64-64zM96 224c0-17.7 14.3-32 32-32s32 14.3 32 32-14.3 32-32 32-32-14.3-32-32z',
        // Uzay Teması
        'fa-star': 'M259.3 17.8L194 150.2 47.9 171.5c-26.2 3.8-36.7 36.1-17.7 54.6l105.7 103-25 145.5c-4.5 26.3 23.2 46 46.4 33.7L288 439.6l130.7 68.7c23.2 12.2 50.9-7.4 46.4-33.7l-25-145.5 105.7-103c19-18.5 8.5-50.8-17.7-54.6L382 150.2 316.7 17.8c-11.7-23.6-45.6-23.9-57.4 0z',
        'fa-moon': 'M279.135 512c78.756 0 150.982-35.804 198.844-94.775 28.27-34.831-2.558-85.722-46.249-77.401-82.348 15.683-158.272-47.268-158.272-130.792 0-48.424 26.06-92.292 67.434-115.836z',
        'fa-rocket': 'M156.6 384.9L125.7 354c-8.5-8.5-11.9-20.8-9.2-32.2l35-135.4c7.9-30.2 26.5-56.8 52-73.8L362.3 16.7c7.8-4.2 17.6-3 24.2 2.8l24.9 21.9c6.6 5.8 7.8 15.6 3 23.4l-95.4 155.7c-17 27.7-43.6 46.3-73.8 52z',
        'fa-satellite': 'M128 256c0-70.7 57.3-128 128-128s128 57.3 128 128-57.3 128-128 128-128-57.3-128-128zM256 160c-17.7 0-32 14.3-32 32s14.3 32 32 32 32-14.3 32-32-14.3-32-32-32z',
        'fa-globe': 'M352 256c0 22.2-1.2 43.6-3.3 64H163.3c-2.2-20.4-3.3-41.8-3.3-64s1.2-43.6 3.3-64H348.7c2.2 20.4 3.3 41.8 3.3 64z',
        'fa-meteor': 'M320 32c0-9.9-4.5-19.2-12.3-25.2S289.8-1.4 280.2 1l-179.9 46.1C90.7 49.7 86 54.6 86 60.3v40.5c0 10.9 8.8 19.7 19.7 19.7s19.7-8.8 19.7-19.7V67.8l17.3-4.4v333.1c0 5.7 4.7 10.3 10.3 10.3h165.4c5.7 0 10.3-4.7 10.3-10.3V32z',
        // Spor Teması
        'fa-futbol': 'M177.1 228.6L207.9 320h96.3l30.7-91.4c3.4-10.2-2.9-21.2-13.4-23.1L256 192.7l-65.5 12.8c-10.5 1.9-16.8 12.9-13.4 23.1z',
        'fa-basketball-ball': 'M212.8 4.4c-52.2 18.8-93.6 60.2-112.4 112.4L4.4 212.8c-6.2 6.2-6.2 16.4 0 22.6l196.8 196.8c6.2 6.2 16.4 6.2 22.6 0l196.8-196.8c6.2-6.2 6.2-16.4 0-22.6L324.6 116.8c-18.8-52.2-60.2-93.6-112.4-112.4z',
        'fa-swimmer': 'M256 96c53 0 96-43 96-96s-43-96-96-96-96 43-96 96 43 96 96 96zM352.1 128H159.9c-35.5 0-64.2 28.7-64.2 64.2v78.7c0 17.7 14.3 32 32 32s32-14.3 32-32v-46.7h192v46.7c0 17.7 14.3 32 32 32s32-14.3 32-32v-78.7c0-35.5-28.7-64.2-64.2-64.2z',
        'fa-biking': 'M400 96c26.5 0 48-21.5 48-48S426.5 0 400 0s-48 21.5-48 48 21.5 48 48 48zM352 128c-8.8 0-16 7.2-16 16v48c0 8.8 7.2 16 16 16h64c8.8 0 16-7.2 16-16v-48c0-8.8-7.2-16-16-16h-64z',
        'fa-running': 'M272 96c26.5 0 48-21.5 48-48S298.5 0 272 0s-48 21.5-48 48 21.5 48 48 48zM113.69 247.93c-22.13 6.3-35.43 29.11-29.13 51.24l35.43 124.01c6.3 22.13 29.11 35.43 51.24 29.13l124.01-35.43c22.13-6.3 35.43-29.11 29.13-51.24l-35.43-124.01c-6.3-22.13-29.11-35.43-51.24-29.13L113.69 247.93z',
        'fa-trophy': 'M400 0H112c-26.51 0-48 21.49-48 48v48c0 26.51 21.49 48 48 48h288c26.51 0 48-21.49 48-48V48c0-26.51-21.49-48-48-48zM224 416h64v64c0 17.67 14.33 32 32 32h32c17.67 0 32-14.33 32-32v-64h64c35.35 0 64-28.65 64-64V224H160v128c0 35.35 28.65 64 64 64z',
        // Ýþ Teması
        'fa-briefcase': 'M320 336c0 8.8-7.2 16-16 16H208c-8.8 0-16-7.2-16-16V64c0-8.8 7.2-16 16-16h96c8.8 0 16 7.2 16 16v272zM96 128h64v224H96c-53 0-96-43-96-96V224c0-53 43-96 96-96z',
        'fa-crown': 'M256 0l70.5 84.6L416 64 395.6 153.6 480 192l-84.4 38.4L416 320l-89.5-20.6L256 384l-70.5-84.6L96 320l20.4-89.6L32 192l84.4-38.4L96 64l89.5 20.6L256 0z',
        'fa-gem': 'M256 0L128 128l128 128 128-128L256 0zM64 256c0-17.7 14.3-32 32-32h32l64-64-64-64H96c-17.7 0-32-14.3-32-32V64c0-17.7 14.3-32 32-32h320c17.7 0 32 14.3 32 32v384c0 17.7-14.3 32-32 32H96c-17.7 0-32-14.3-32-32V256z',
        'fa-heart': 'M462.3 62.6C407.5 15.9 326 24.3 275.7 76.2L256 96.5l-19.7-20.3C186.1 24.3 104.5 15.9 49.7 62.6c-62.8 53.6-66.1 149.8-9.9 207.9l193.5 199.8c12.5 12.9 32.8 12.9 45.3 0l193.5-199.8c56.3-58.1 53-154.3-9.8-207.9z',
        'fa-lightbulb': 'M352 104c0-54.7-26.2-103.2-66.6-134.1-8.1-6.2-19.4-5.8-27.2 1L205.4 23.7c-7.8 6.8-8.2 18.5-1 25.9C246.8 88.3 272 129.1 272 176v80c0 8.8 7.2 16 16 16h64c8.8 0 16-7.2 16-16v-152z',
        'fa-cog': 'M495.9 166.6c3.2 8.7.5 18.4-6.4 24.6l-43.3 39.4c1.1 8.3 1.7 16.8 1.7 25.4s-.6 17.1-1.7 25.4l43.3 39.4c6.9 6.2 9.6 15.9 6.4 24.6-4.4 11.9-9.7 23.3-15.8 34.3l-4.7 8.1c-6.6 11-14 21.4-22.1 31.2-5.9 7.2-15.7 9.6-24.5 6.8l-55.7-17.7c-13.4 10.3-28.2 18.9-44 25.4l-12.5 57.1c-2 9.1-9 16.3-18.2 17.8-13.8 2.3-28 3.5-42.5 3.5s-28.7-1.2-42.5-3.5c-9.2-1.5-16.2-8.7-18.2-17.8l-12.5-57.1c-15.8-6.5-30.6-15.1-44-25.4L83.1 425.9c-8.8 2.8-18.6.3-24.5-6.8-8.1-9.8-15.5-20.2-22.1-31.2l-4.7-8.1c-6.1-11-11.4-22.4-15.8-34.3-3.2-8.7-.5-18.4 6.4-24.6l43.3-39.4C64.6 273.1 64 264.6 64 256s.6-17.1 1.7-25.4L22.4 191.2c-6.9-6.2-9.6-15.9-6.4-24.6 4.4-11.9 9.7-23.3 15.8-34.3l4.7-8.1c6.6-11 14-21.4 22.1-31.2 5.9-7.2 15.7-9.6 24.5-6.8l55.7 17.7c13.4-10.3 28.2-18.9 44-25.4l12.5-57.1c2-9.1 9-16.3 18.2-17.8C227.3 1.2 241.5 0 256 0s28.7 1.2 42.5 3.5c9.2 1.5 16.2 8.7 18.2 17.8l12.5 57.1c15.8 6.5 30.6 15.1 44 25.4l55.7-17.7c8.8-2.8 18.6-.3 24.5 6.8 8.1 9.8 15.5 20.2 22.1 31.2l4.7 8.1c6.1 11 11.4 22.4 15.8 34.3zM256 336c44.2 0 80-35.8 80-80s-35.8-80-80-80-80 35.8-80 80 35.8 80 80 80z',
        // Müzik Teması Ýkonları
        'fa-guitar': 'M502.63 39.15c12.5-12.5 12.5-32.75 0-45.25s-32.75-12.5-45.25 0L320 131.29V96c0-17.67-14.33-32-32-32s-32 14.33-32 32v256c0 17.67 14.33 32 32 32s32-14.33 32-32V204.71l137.38-137.38c12.5-12.5 12.5-32.75 0-45.25z',
        'fa-headphones': 'M256 32C114.52 32 0 146.496 0 288v64c0 35.328 28.672 64 64 64h32c17.664 0 32-14.336 32-32V288c0-17.664-14.336-32-32-32H64c-5.376 0-10.368 1.472-14.848 3.712C67.776 138.368 152.064 64 256 64s188.224 74.368 206.848 195.712C458.368 257.472 453.376 256 448 256h-32c-17.664 0-32 14.336-32 32v96c0 17.664 14.336 32 32 32h32c35.328 0 64-28.672 64-64v-64C512 146.496 397.48 32 256 32z',
        'fa-microphone': 'M176 352c53.02 0 96-42.98 96-96V96c0-53.02-42.98-96-96-96S80 42.98 80 96v160c0 53.02 42.98 96 96 96zm160-160h-16c-8.84 0-16 7.16-16 16v48c0 74.8-64.49 134.82-140.79 127.38C96.71 376.89 48 317.11 48 250.3V208c0-8.84-7.16-16-16-16H16c-8.84 0-16 7.16-16 16v40.16c0 89.64 63.97 169.55 152 181.69V464H96c-8.84 0-16 7.16-16 16v16c0 8.84 7.16 16 16 16h160c8.84 0 16-7.16 16-16v-16c0-8.84-7.16-16-16-16h-56v-33.77C285.71 418.47 352 344.9 352 256v-48c0-8.84-7.16-16-16-16z',
        'fa-drum': 'M431.87 312.64C432.21 306.5 432 301.31 432 296c0-137.83-110.3-248-248-248C46.17 48 0 158.17 0 296c0 5.31-.21 10.5.13 16.64C31.47 455.8 132.89 512 256 512c123.11 0 224.53-56.2 255.87-199.36z',
        'fa-piano': 'M32 32v448h96V32H32zm64 288h-32v-64h32v64zm0-96h-32v-64h32v64zm0-96h-32V64h32v64zM160 480h64V32h-64v448zm96 0h64V32h-64v448zm96 0h64V32h-64v448zm96 0h32V32h-32v448z',
        // Yemek Teması Ýkonları
        'fa-pizza-slice': 'M158.87 366.53c-9.38 0-17.03-7.65-17.03-17.03 0-9.38 7.65-17.03 17.03-17.03s17.03 7.65 17.03 17.03c0 9.38-7.65 17.03-17.03 17.03zM256 130.69L467.62 442H44.38L256 130.69z',
        'fa-hamburger': 'M464 192h-16c-8.8 0-16-7.2-16-16s7.2-16 16-16h16c26.5 0 48-21.5 48-48S490.5 64 464 64H48C21.5 64 0 85.5 0 112s21.5 48 48 48h16c8.8 0 16 7.2 16 16s-7.2 16-16 16H48c-26.5 0-48 21.5-48 48s21.5 48 48 48h416c26.5 0 48-21.5 48-48s-21.5-48-48-48z',
        'fa-ice-cream': 'M368 160h-96V96c0-53.02-42.98-96-96-96s-96 42.98-96 96v64H80c-26.51 0-48 21.49-48 48v32c0 26.51 21.49 48 48 48h16v128c0 53.02 42.98 96 96 96s96-42.98 96-96V288h16v128c0 53.02 42.98 96 96 96s96-42.98 96-96V288h16c26.51 0 48-21.49 48-48v-32c0-26.51-21.49-48-48-48z',
        'fa-birthday-cake': 'M448 384c35.3 0 64-28.7 64-64V224c0-35.3-28.7-64-64-64H64c-35.3 0-64 28.7-64 64v96c0 35.3 28.7 64 64 64h384zM224 208c0-8.8 7.2-16 16-16s16 7.2 16 16v48c0 8.8-7.2 16-16 16s-16-7.2-16-16v-48zm96 0c0-8.8 7.2-16 16-16s16 7.2 16 16v48c0 8.8-7.2 16-16 16s-16-7.2-16-16v-48z',
        'fa-apple-alt': 'M350.85 129c25.97 4.67 47.27 18.67 63.92 42 14.65 20.67 24.64 46.67 29.96 78 4.67 27.33 4.67 57.33 0 90-7.99 47.33-23.97 85.33-47.94 114-23.97 28.67-52.26 43-84.87 43-28.44 0-52.26-9.33-71.47-28-19.21-18.67-28.81-42.67-28.81-72 0-30.67 9.6-55.33 28.81-74s43.03-28 71.47-28c21.31 0 39.69 6 55.14 18 15.45 12 23.18 28.67 23.18 50 0 18.67-5.99 33.33-17.98 44s-26.64 16-43.95 16c-14.65 0-26.31-4-34.98-12s-13.01-18.67-13.01-32c0-10.67 3.33-19.33 9.99-26s14.65-10 24.31-10 17.65 3.33 24.31 10 9.99 15.33 9.99 26c0 8-2.33 14.67-6.99 20s-10.98 8-18.98 8-14.32-2.67-18.98-8-6.99-12-6.99-20c0-13.33 4.66-24 13.98-32s20.31-12 34.98-12c17.31 0 31.97 5.33 43.95 16s17.98 25.33 17.98 44c0-21.33-7.73-38-23.18-50s-33.83-18-55.14-18c-28.44 0-52.26 9.33-71.47 28s-28.81 43.33-28.81 74c0 29.33 9.6 53.33 28.81 72s43.03 28 71.47 28c32.61 0 60.9-14.33 84.87-43s39.95-66.67 47.94-114c4.67-32.67 4.67-62.67 0-90-5.32-31.33-15.31-57.33-29.96-78-16.65-23.33-37.95-37.33-63.92-42z',
        // Seyahat Teması Ýkonları
        'fa-plane': 'M472.19 332.7l-144.02-68.36-128.07-128.07L131.74 98.95c-8.49-8.49-22.23-8.49-30.72 0L76.69 123.28c-8.49 8.49-8.49 22.23 0 30.72l68.36 144.02 128.07 128.07-37.32 68.36c-8.49 8.49-8.49 22.23 0 30.72l24.33 24.33c8.49 8.49 22.23 8.49 30.72 0l68.36-37.32 144.02-68.36c8.49-8.49 8.49-22.23 0-30.72l-68.36-144.02L332.7 200.72l37.32-68.36c8.49-8.49 8.49-22.23 0-30.72l-24.33-24.33c-8.49-8.49-22.23-8.49-30.72 0l-68.36 37.32L102.59 182.99c-8.49 8.49-8.49 22.23 0 30.72l144.02 68.36L374.68 410.14l68.36 37.32c8.49 8.49 22.23 8.49 30.72 0l24.33-24.33c8.49-8.49 8.49-22.23 0-30.72l-37.32-68.36 68.36-144.02c8.49-8.49 8.49-22.23 0-30.72z',
        'fa-suitcase-rolling': 'M128 480V351.99c0-17.67-14.33-32-32-32s-32 14.33-32 32V480c0 17.67 14.33 32 32 32s32-14.33 32-32zM384 480V351.99c0-17.67-14.33-32-32-32s-32 14.33-32 32V480c0 17.67 14.33 32 32 32s32-14.33 32-32zM480 256v96c0 53.02-42.98 96-96 96H128c-53.02 0-96-42.98-96-96v-96c0-53.02 42.98-96 96-96h80V96c0-53.02 42.98-96 96-96h32c53.02 0 96 42.98 96 96v64h80c53.02 0 96 42.98 96 96z',
        'fa-ship': 'M416 473.14l-4-.62V384c0-26.51-21.49-48-48-48H148c-26.51 0-48 21.49-48 48v88.52l-4 .62c-22.25 3.45-39.32 22.25-39.99 45.06-.78 26.74 20.29 48.82 46.99 48.82h266c26.7 0 47.77-22.08 46.99-48.82-.67-22.81-17.74-41.61-39.99-45.06z',
        'fa-camera': 'M464 64H336c-16 0-29.875-9.125-36.5-22.375L282 16C276 6.125 264.125 0 252 0H180c-12.125 0-24 6.125-30 16l-17.5 25.625C125.875 54.875 112 64 96 64H48C21.5 64 0 85.5 0 112v288c0 26.5 21.5 48 48 48h416c26.5 0 48-21.5 48-48V112c0-26.5-21.5-48-48-48zM216 368c-66.25 0-120-53.75-120-120s53.75-120 120-120 120 53.75 120 120-53.75 120-120 120z',
        'fa-map': 'M0 192l160-53.33v106.66L0 298.67V192zm160 138.67L0 384v-42.67l160-53.33v42.67zM192 106.67V160l160-53.33v106.66L192 266.67V320l160-53.33v106.66L192 426.67V480l-32-10.67V21.33L192 32v74.67z',
        'fa-compass': 'M256 8C119.033 8 8 119.033 8 256s111.033 248 248 248 248-111.033 248-248S392.967 8 256 8zm0 448c-110.532 0-200-89.451-200-200 0-110.532 89.451-200 200-200 110.532 0 200 89.451 200 200 0 110.532-89.451 200-200 200zm-32-152l32-32 32 32-32 32-32-32z'
    };
    // Icon isimini path'e çevir
    let iconPath = iconPaths['fa-star']; // Varsayılan
    for (let key in iconPaths) {
        if (iconClass.includes(key.replace('fa-', ''))) {
            iconPath = iconPaths[key];
            break;
        }
    }
    // SVG oluþtur
    const svg = `
        <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="${gradientId}" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:${colors[0]};stop-opacity:1" />
                    <stop offset="100%" style="stop-color:${colors[1] || colors[0]};stop-opacity:1" />
                </linearGradient>
            </defs>
            <circle cx="${size/2}" cy="${size/2}" r="${size/2-2}" fill="url(#${gradientId})" />
            <g transform="translate(${size/2}, ${size/2}) scale(${size/512 * 0.6}) translate(-256, -256)">
                <path d="${iconPath}" fill="white" opacity="0.9"/>
            </g>
        </svg>
    `;
    // SVG'yi data URL'ye çevir
    return 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svg)));
}
function selectSimpleAvatar(imgElement, avatarUrl) {
    clearAvatarSelection();
    imgElement.style.border = '3px solid #007bff';
    const profileUrlInput = document.getElementById('newUserProfilUrl');
    if (profileUrlInput) {
        profileUrlInput.value = avatarUrl;
    }
    const fileInput = document.getElementById('profilePhotoFile');
    if (fileInput) {
        fileInput.value = '';
    }
    showProfilPhotoPreview(avatarUrl);
}
function clearAvatarSelection() {
    const avatars = document.querySelectorAll('img[onclick*="selectSimpleAvatar"], .avatar-option');
    avatars.forEach(avatar => {
        avatar.style.border = '2px solid transparent';
    });
}
function showProfilPhotoPreview(url) {
    const preview = document.getElementById('profilePhotoPreview');
    const previewImage = document.getElementById('profilePhotoPreviewImage');
    previewImage.src = url;
    previewImage.onerror = function() {
        showToast('error', 'Profil fotoÝrafı URL\'si geçersiz veya eriþilemiyor!', 'Hata');
        hideProfilPhotoPreview();
    };
    previewImage.onload = function() {
        preview.style.display = 'block';
    };
}
function hideProfilPhotoPreview() {
    document.getElementById('profilePhotoPreview').style.display = 'none';
    document.getElementById('profilePhotoPreviewImage').src = '';
}
function clearProfilPhoto() {
    document.getElementById('newUserProfilUrl').value = '';
    document.getElementById('profilePhotoFile').value = '';
    clearAvatarSelection();
    hideProfilPhotoPreview();
}
// Düzenleme modalı için profil fotoÝrafı fonksiyonları
function handleDüzenleProfilPhotoYükle(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        // Dosya boyutu kontrolü (16MB)
        if (file.size > 16 * 1024 * 1024) {
            showToast('warning', 'Dosya boyutu 16MB\'dan büyük olamaz!', 'Uyarı');
            input.value = '';
            return;
        }
        // Dosya türü kontrolü
        const allowedTips = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/webp'];
        if (!allowedTips.includes(file.type)) {
            showToast('warning', 'Geçersiz dosya formatı! Sadece PNG, JPG, JPEG, GIF, WEBP desteklenir.', 'Uyarı');
            input.value = '';
            return;
        }
        // FotoÝraf yükleme
        const formData = new FormData();
        formData.append('profile_photo', file);
        const csrf = document.querySelector('meta[name="csrf-token"]')?.content;
        const headers = {};
        if (csrf) headers['X-CSRFToken'] = csrf;
        input.disabled = true;
        fetch('/admin/upload-profile-photo', {
            method: 'POST',
            headers,
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('editUserProfilUrl').value = data.photo_url;
                showDüzenleProfilPhotoPreview(data.photo_url);
                showToast('success', data.message || 'Fotoğraf başarıyla yüklendi!');
            } else {
                showToast('error', data.message || 'İşlem gerçekleştirilemedi. Lütfen tekrar deneyin.');
            }
        })
        .catch(error => {
            showToast('error', 'Yükleme hatası: ' + error.message);
        })
        .finally(() => {
            input.disabled = false;
        });
    }
}
// Global scope'a ekle
window.handleDüzenleProfilPhotoYükle = handleDüzenleProfilPhotoYükle;

function handleDüzenleProfilPhotoUrl(input) {
    const url = input.value.trim();
    if (url) {
        showDüzenleProfilPhotoPreview(url);
    } else {
        hideDüzenleProfilPhotoPreview();
    }
}
function showDüzenleProfilPhotoPreview(url) {
    const preview = document.getElementById('editProfilPhotoPreview');
    const previewImage = document.getElementById('editProfilPhotoPreviewImage');
    previewImage.src = url;
    previewImage.onerror = function() {
        showToast('Profil fotoÝrafı URL\'si geçersiz veya eriþilemiyor!', 'error');
        hideDüzenleProfilPhotoPreview();
    };
    previewImage.onload = function() {
        preview.style.display = 'block';
    };
}
function hideDüzenleProfilPhotoPreview() {
    const preview = document.getElementById('editProfilPhotoPreview');
    if (preview) {
        preview.style.display = 'none';
        document.getElementById('editProfilPhotoPreviewImage').src = '';
    }
}
function clearDüzenleProfilPhoto() {
    document.getElementById('editUserProfilUrl').value = '';
    document.getElementById('editProfilPhotoFile').value = '';
    hideDüzenleProfilPhotoPreview();
}
// Global scope'a ekle
window.handleDüzenleProfilPhotoUrl = handleDüzenleProfilPhotoUrl;
window.clearDüzenleProfilPhoto = clearDüzenleProfilPhoto;

// ASCII-safe aliases (inline HTML handlers are more reliable this way)
function handleDuzenleProfilPhotoYukle(input) {
    return window.handleDüzenleProfilPhotoYükle
        ? window.handleDüzenleProfilPhotoYükle(input)
        : undefined;
}
function handleDuzenleProfilPhotoUrl(input) {
    return window.handleDüzenleProfilPhotoUrl
        ? window.handleDüzenleProfilPhotoUrl(input)
        : undefined;
}
function clearDuzenleProfilPhoto() {
    return window.clearDüzenleProfilPhoto
        ? window.clearDüzenleProfilPhoto()
        : undefined;
}
window.handleDuzenleProfilPhotoYukle = handleDuzenleProfilPhotoYukle;
window.handleDuzenleProfilPhotoUrl = handleDuzenleProfilPhotoUrl;
window.clearDuzenleProfilPhoto = clearDuzenleProfilPhoto;

// Düzenleme modalı için logo fonksiyonları
function handleDüzenleLogoYükle(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        // Dosya boyutu kontrolü (16MB)
        if (file.size > 16 * 1024 * 1024) {
            showToast('error', 'Dosya boyutu 16MB\'dan büyük olamaz!', 'Hata');
            input.value = '';
            return;
        }
        // Dosya türü kontrolü
        const allowedTips = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/svg+xml', 'image/webp'];
        if (!allowedTips.includes(file.type)) {
            showToast('error', 'Geçersiz dosya formatı! Sadece PNG, JPG, JPEG, GIF, SVG, WEBP desteklenir.', 'Hata');
            input.value = '';
            return;
        }
        // Logo yükleme
        const formData = new FormData();
        formData.append('logo', file);
        const csrf = document.querySelector('meta[name="csrf-token"]')?.content;
        const headers = {};
        if (csrf) headers['X-CSRFToken'] = csrf;
        input.disabled = true;
        fetch('/admin/upload-logo', {
            method: 'POST',
            headers,
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('editOrgLogoUrl').value = data.logo_url;
                showDüzenleLogoPreview(data.logo_url);
                showToast('success', data.message || 'Logo başarıyla yüklendi!');
            } else {
                showToast('error', data.message || 'Ýþlem gerçekleþtirilemedi. Lütfen tekrar deneyin.');
            }
        })
        .catch(error => {
            showToast('error', 'Yükle hatası: ' + error.message);
        })
        .finally(() => {
            input.disabled = false;
        });
    }
}
// Global scope'a ekle
window.handleDüzenleLogoYükle = handleDüzenleLogoYükle;

function handleDuzenleLogoYukle(input) {
    return window.handleDüzenleLogoYükle ? window.handleDüzenleLogoYükle(input) : undefined;
}
function handleDuzenleLogoUrl(input) {
    return window.handleDüzenleLogoUrl ? window.handleDüzenleLogoUrl(input) : undefined;
}
function clearDuzenleLogo() {
    return window.clearDüzenleLogo ? window.clearDüzenleLogo() : undefined;
}
window.handleDuzenleLogoYukle = handleDuzenleLogoYukle;
window.handleDuzenleLogoUrl = handleDuzenleLogoUrl;
window.clearDuzenleLogo = clearDuzenleLogo;

function handleDüzenleLogoUrl(input) {
    const url = input.value.trim();
    if (url) {
        showDüzenleLogoPreview(url);
    } else {
        hideDüzenleLogoPreview();
    }
}
function showDüzenleLogoPreview(url) {
    const preview = document.getElementById('editLogoPreview');
    const previewImage = document.getElementById('editLogoPreviewImage');
    previewImage.src = url;
    previewImage.onerror = function() {
        showToast('Logo URL\'si geçersiz veya eriþilemiyor!', 'error');
        hideDüzenleLogoPreview();
    };
    previewImage.onload = function() {
        preview.style.display = 'block';
    };
}
function hideDüzenleLogoPreview() {
    const preview = document.getElementById('editLogoPreview');
    if (preview) {
        preview.style.display = 'none';
        document.getElementById('editLogoPreviewImage').src = '';
    }
}
function clearDüzenleLogo() {
    document.getElementById('editOrgLogoUrl').value = '';
    document.getElementById('editLogoFile').value = '';
    hideDüzenleLogoPreview();
}
window.clearDüzenleLogo = clearDüzenleLogo;
// ============================================
// SÜREÇ YÇNETÝMÝ FONKSÝYONLARI
// ============================================
// Kullanıcıları kuruma göre filtrele
function filterUsersByKurum(kurumId, selectElementId) {
    const selectElement = document.getElementById(selectElementId);
    const options = selectElement.querySelectorAll('option');
    // Tüm seçenekleri göster/gizle
    options.forEach(option => {
        if (option.value === '') {
            // Varsayılan seçenek
            option.style.display = 'block';
            if (kurumId) {
                option.textContent = 'Lider seçiniz...';
            } else {
                option.textContent = 'Çnce kurum seçin...';
            }
        } else {
            const optionKurumId = option.getAttribute('data-kurum-id');
            if (!kurumId || optionKurumId === kurumId) {
                option.style.display = 'block';
            } else {
                option.style.display = 'none';
            }
        }
    });
    // Seçimi sıfırla
    selectElement.value = '';
}
// Yeni süreç oluþtur
function createNewProcess(evt) {
    const kurumSelect = document.getElementById('newProcessKurum');
    const kurumId = kurumSelect.disabled ? kurumSelect.options[kurumSelect.selectedIndex].value : kurumSelect.value;
    const formData = {
        ad: document.getElementById('newProcessAd').value.trim(),
        kurum_id: kurumId,
        lider_id: document.getElementById('newProcessLider').value,
        dokuman_no: document.getElementById('newProcessDokuman').value.trim(),
        rev_no: document.getElementById('newProcessRevizyon').value.trim(),
        durum: document.getElementById('newProcessDurum').value,
        ilerleme: document.getElementById('newProcessIlerleme').value,
        baslangic_tarihi: document.getElementById('newProcessBaslangic').value,
        bitis_tarihi: document.getElementById('newProcessBitis').value,
        aciklama: document.getElementById('newProcessAciklama').value.trim()
    };
    // Zorunlu alan kontrolü
    if (!formData.ad || !formData.kurum_id || !formData.lider_id) {
        showToast('warning', 'Lütfen zorunlu alanları (*) doldurun!', 'Eksik Bilgi');
        return;
    }
    // Submit butonunu devre dıþı bırak
    const submitBtn = (evt && evt.target) ? evt.target : document.getElementById('newProcessSubmitBtn');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Oluþturuluyor...';
    }
    fetch('/admin/add-process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('success', data.message, 'Baþarılı');
            const modal = bootstrap.Modal.getInstance(document.getElementById('newProcessModal'));
            modal.hide();
            reloadPage(0, false);
        } else {
            showToast('error', data.message || 'Süreç oluþturulurken bir hata oluþtu', 'Hata');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        handleAjaxError(error, 'Süreç oluþturulurken bir hata oluþtu');
    })
    .finally(() => {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-save me-2"></i>Süreç Oluþtur';
        }
    });
}
// Süreç görüntüle
function viewProcess(processId) {
    showToast('info', 'Süreç detay görüntüleme özelliÝi geliþtirilecek. Süreç ID: ' + processId, 'Bilgi');
}
// Süreç düzenle
function editProcess(processId) {
    console.log('Süreç düzenleme baþladı, ID:', processId);
    // Süreç bilgilerini al
    fetch(`/admin/get-process/${processId}`)
        .then(response => response.json())
        .then(data => {
            console.log('Süreç verileri yüklendi:', data);
            if (data.success) {
                const surec = data.surec;
                document.getElementById('editProcessId').value = surec.id;
                document.getElementById('editProcessAd').value = surec.ad;
                document.getElementById('editProcessDurum').value = surec.durum;
                document.getElementById('editProcessDokuman').value = surec.dokuman_no || '';
                document.getElementById('editProcessRevizyon').value = surec.rev_no || '';
                document.getElementById('editProcessBaslangic').value = surec.baslangic_tarihi || '';
                document.getElementById('editProcessBitis').value = surec.bitis_tarihi || '';
                document.getElementById('editProcessIlerleme').value = surec.ilerleme || 0;
                document.getElementById('editProcessIlerlemeValue').textContent = (surec.ilerleme || 0) + '%';
                document.getElementById('editProcessAciklama').value = surec.aciklama || '';
                // Çoklu lider seçimi için verileri yükle
                loadDüzenleProcessLiderler(surec);
                const modal = new bootstrap.Modal(document.getElementById('editProcessModal'), {
                    backdrop: true,
                    keyboard: true
                });
                modal.show();
            } else {
                showToast('error', data.message || 'Süreç bilgileri yüklenirken bir hata oluþtu', 'Hata');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            handleAjaxError(error, 'Süreç bilgileri yüklenirken bir hata oluþtu');
        });
}
/**
 * Düzenleme formunda mevcut liderleri yükle
 */
function loadDüzenleProcessLiderler(surec) {
    const target = document.getElementById('edit_lider_ids');
    target.innerHTML = '';
    console.log('Lider yükleme iþlemi baþladı:', surec.liderler);
    if (surec.liderler && surec.liderler.length > 0) {
        console.log('Lider sayısı:', surec.liderler.length);
        surec.liderler.forEach((lider, index) => {
            console.log(`Lider ${index + 1}:`, lider);
            const option = new Option(lider.username, lider.id);
            target.add(option);
        });
    } else {
        console.log('Lider bulunamadı');
    }
    console.log('Lider yükleme tamamlandı');
}
/**
 * Lider ekleme fonksiyonu
 */
function addDüzenleLiderler() {
    const source = document.getElementById('edit_lider_source');
    const target = document.getElementById('edit_lider_ids');
    const selected = Array.from(source.selectedOptions);
    console.log('Lider ekleme iþlemi baþladı');
    console.log('Seçilen liderler:', selected.map(opt => ({value: opt.value, text: opt.text})));
    if (selected.length === 0) {
        showToast('warning', 'Lütfen önce sol taraftan lider seçin!', 'Uyarı');
        return;
    }
    let addedCount = 0;
    selected.forEach(opt => {
        // Zaten eklenmemiþ ise ekle
        if (!Array.from(target.options).find(o => o.value === opt.value)) {
            const newOpt = new Option(opt.text, opt.value);
            target.add(newOpt);
            addedCount++;
            console.log(`Lider eklendi: ${opt.text}`);
        } else {
            console.log(`Lider zaten mevcut: ${opt.text}`);
        }
    });
    if (addedCount > 0) {
        showToast('success', `${addedCount} lider eklendi!`, 'Baþarılı');
    } else {
        showToast('warning', 'Seçilen liderler zaten mevcut!', 'Uyarı');
    }
    console.log('Lider ekleme tamamlandı');
}
/**
 * Lider çıkarma fonksiyonu
 */
function removeDüzenleLiderler() {
    const target = document.getElementById('edit_lider_ids');
    const selected = Array.from(target.selectedOptions);
    console.log('Lider çıkarma iþlemi baþladı');
    console.log('Çıkarılacak liderler:', selected.map(opt => ({value: opt.value, text: opt.text})));
    if (selected.length === 0) {
        showToast('warning', 'Lütfen önce saÝ taraftan çıkarılacak lideri seçin!', 'Uyarı');
        return;
    }
    const removedCount = selected.length;
    selected.forEach(opt => {
        opt.remove();
        console.log(`Lider çıkarıldı: ${opt.text}`);
    });
    showToast('info', `${removedCount} lider çıkarıldı!`, 'Bilgi');
    console.log('Lider çıkarma tamamlandı');
}
// Süreç güncelle
function updateProcess(evt) {
    const processId = document.getElementById('editProcessId').value;
    // Çoklu lider seçimi için lider ID'lerini topla
    const liderIds = Array.from(document.getElementById('edit_lider_ids').options).map(opt => opt.value);
    console.log('Güncelleme iþlemi baþladı');
    console.log('Seçilen liderler:', liderIds);
    const formData = {
        ad: document.getElementById('editProcessAd').value.trim(),
        lider_ids: liderIds, // Çoklu lider seçimi
        dokuman_no: document.getElementById('editProcessDokuman').value.trim(),
        rev_no: document.getElementById('editProcessRevizyon').value.trim(),
        durum: document.getElementById('editProcessDurum').value,
        ilerleme: document.getElementById('editProcessIlerleme').value,
        baslangic_tarihi: document.getElementById('editProcessBaslangic').value,
        bitis_tarihi: document.getElementById('editProcessBitis').value,
        aciklama: document.getElementById('editProcessAciklama').value.trim()
    };
    // Zorunlu alan kontrolü
    if (!formData.ad || liderIds.length === 0) {
        showToast('warning', 'Lütfen süreç adı ve en az bir lider seçin!', 'Eksik Bilgi');
        return;
    }
    const submitBtn = (evt && evt.target) ? evt.target : document.getElementById('editProcessSubmitBtn');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Güncelleniyor...';
    }
    fetch(`/admin/update-process/${processId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('success', data.message, 'Baþarılı');
            const modal = bootstrap.Modal.getInstance(document.getElementById('editProcessModal'));
            modal.hide();
            reloadPage(0, false);
        } else {
            showToast('error', data.message || 'Süreç güncellenirken bir hata oluþtu', 'Hata');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        handleAjaxError(error, 'Süreç güncellenirken bir hata oluþtu');
    })
    .finally(() => {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-save me-2"></i>Güncelle';
        }
    });
}
// Süreç sil
async function deleteProcess(processId) {
    const confirmed = await confirmDelete('Bu süreci silmek istediðinizden emin misiniz?', 'Bu iþlem geri alınamaz!');
    if (confirmed) {
        fetch(`/admin/delete-process/${processId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('success', data.message, 'Baþarılı');
                reloadPage(0, false);
            } else {
                showToast('error', data.message || 'Süreç silinirken bir hata oluþtu', 'Hata');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            handleAjaxError(error, 'Süreç silinirken bir hata oluþtu');
        });
    }
}
// Süreç üyelerini yönet
function manageProcessUsers(processId, processAd) {
    document.getElementById('manageProcessId').value = processId;
    document.getElementById('processUsersModalBaþlık').textContent = processAd + ' - Üye Yönetimi';
    // Mevcut üyeleri yükle
    loadProcessUsers(processId);
    const modal = new bootstrap.Modal(document.getElementById('processUsersModal'), {
        backdrop: true,
        keyboard: true
    });
    modal.show();
}
// Süreç üyelerini yükle
function loadProcessUsers(processId) {
    const listDiv = document.getElementById('processUsersList');
    listDiv.innerHTML = '<div class="text-center text-muted"><i class="fas fa-spinner fa-spin fa-2x"></i><p class="mt-2">Yükleniyor...</p></div>';
    // Gerçek API'den veri çekilecek (þimdilik mock)
    fetch(`/admin/get-process/${processId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.surec) {
                const surec = data.surec;
                let html = '';
                if (surec.uyeler && surec.uyeler.length > 0) {
                    html = '<div class="list-group">';
                    surec.uyeler.forEach(uye => {
                        if (uye.id != surec.lider_id) {
                            html += `
                                <div class="list-group-item d-flex justify-content-between align-items-center">
                                    <div>
                                        <i class="fas fa-user me-2 text-primary"></i>
                                        <strong>${uye.username}</strong>
                                        <small class="text-muted ms-2">${uye.email}</small>
                                    </div>
                                    <button class="btn btn-sm btn-outline-danger" onclick="removeProcessMember(${processId}, ${uye.id}, '${uye.username}')">
                                        <i class="fas fa-times"></i> Çıkar
                                    </button>
                                </div>
                            `;
                        }
                    });
                    html += '</div>';
                } else {
                    html = '<div class="text-center text-muted py-3"><i class="fas fa-info-circle me-2"></i>Henüz üye eklenmemiþ</div>';
                }
                listDiv.innerHTML = html;
            } else {
                listDiv.innerHTML = '<div class="alert alert-danger">Üyeler yüklenemedi!</div>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            listDiv.innerHTML = '<div class="alert alert-danger">Hata oluþtu!</div>';
        });
}
// Süreç üyesi ekle
function addProcessMember() {
    const processId = document.getElementById('manageProcessId').value;
    const userId = document.getElementById('newMemberSelect').value;
    if (!userId) {
        showToast('warning', 'Lütfen bir kullanıcı seçin!', 'Eksik Bilgi');
        return;
    }
    fetch(`/admin/process/${processId}/add-member`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('success', data.message, 'Baþarılı');
            document.getElementById('newMemberSelect').value = '';
            loadProcessUsers(processId);
        } else {
            showToast('error', data.message || 'Üye eklenirken bir hata oluþtu', 'Hata');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        handleAjaxError(error, 'Üye eklenirken bir hata oluþtu');
    });
}
// Süreç üyesini çıkar
async function removeProcessMember(processId, userId, username) {
    const confirmed = await confirmDialog({title: "Kullanıcı Çıkarma", text: `${username} kullanıcısını süreçten çıkarmak istediðinizden emin misiniz?`, icon: "question"});
    if (confirmed) {
        fetch(`/admin/process/${processId}/remove-member/${userId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('success', data.message, 'Baþarılı');
                loadProcessUsers(processId);
            } else {
                showToast('error', data.message || 'Üye çıkarılırken bir hata oluþtu', 'Hata');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            handleAjaxError(error, 'Üye çıkarılırken bir hata oluþtu');
        });
    }
}
// ============================================
// STRATEJÝK PLANLAMA FONKSÝYONLARI
// ============================================
// Tab açıldıÝında veri yükle
document.addEventListener('DOMContentLoaded', function() {
    // Kullanıcılar tab'ı açıldıðında kullanıcı listesini yükle
    const usersTab = document.getElementById('users-tab');
    if (usersTab) {
        usersTab.addEventListener('shown.bs.tab', function() {
            loadAdminUsers();
        });
    }
    // Rol matrisi tab'ı açıldıðında rol matrisini yükle
    const rolMatrisiTab = document.getElementById('rol-matrisi-tab');
    if (rolMatrisiTab) {
        rolMatrisiTab.addEventListener('shown.bs.tab', function() {
            loadRolMatrisi();
        });
    }
    // Strateji tab'ı açıldıðında verileri yükle
    const strategyTab = document.getElementById('strategy-tab');
    if (strategyTab) {
        strategyTab.addEventListener('shown.bs.tab', function() {
            loadAllStrategyData();
        });
    }
});
function loadAllStrategyData() {
    loadDegerler();
    loadEtikKurallar();
    loadKalitePolitikalari();
    loadAnaStratejiler();
}
// Deðerler
function loadDegerler() {
    const listDiv = document.getElementById('degerList');
    listDiv.innerHTML = '<div class="text-center text-muted py-3"><i class="fas fa-spinner fa-spin"></i> Yükleniyor...</div>';
    fetch('/admin/get-degerler')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.degerler.length > 0) {
                let html = '';
                data.degerler.forEach(item => {
                    html += `
                        <div class="list-group-item">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <h6 class="mb-1">${item.baslik}</h6>
                                    ${item.aciklama ? `<p class="mb-0 small text-muted">${item.aciklama}</p>` : ''}
                                </div>
                                <div>
                                    <button class="btn btn-sm btn-outline-primary" onclick="editDeger(${item.id})"><i class="fas fa-edit"></i></button>
                                    <button class="btn btn-sm btn-outline-danger" onclick="deleteDeger(${item.id})"><i class="fas fa-trash"></i></button>
                                </div>
                            </div>
                        </div>
                    `;
                });
                listDiv.innerHTML = html;
            } else {
                listDiv.innerHTML = '<div class="text-center text-muted py-3"><i class="fas fa-info-circle"></i> Henüz deÝer eklenmemiþ</div>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            listDiv.innerHTML = '<div class="alert alert-danger">Yükleme hatası!</div>';
        });
}
function saveDeger() {
    const editId = document.getElementById('degerDüzenleId').value;
    const data = {
        kurum_id: document.getElementById('degerKurum').value,
        baslik: document.getElementById('degerBaslik').value.trim(),
        aciklama: document.getElementById('degerAciklama').value.trim()
    };
    if (!data.baslik) {
        showToast('warning', 'Lütfen baþlık girin!', 'Eksik Bilgi');
        return;
    }
    const url = editId ? `/admin/update-deger/${editId}` : '/admin/add-deger';
    const method = editId ? 'PUT' : 'POST';
    fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('success', data.message, 'Baþarılı');
            bootstrap.Modal.getInstance(document.getElementById('degerModal')).hide();
            loadDegerler();
        } else {
            showToast('error', data.message || 'Deðer kaydedilirken bir hata oluþtu', 'Hata');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        handleAjaxError(error, 'Deðer kaydedilirken bir hata oluþtu');
    });
}
function editDeger(id) {
    // Basit implementasyon - geliþtirilecek
    showToast('info', 'Düzenleme özelliÝi yakında eklenecek. ID: ' + id, 'Bilgi');
}
async function deleteDeger(id) {
    const confirmed = await confirmDelete('Bu deðeri silmek istediðinizden emin misiniz?');
    if (confirmed) {
        fetch(`/admin/delete-deger/${id}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('success', data.message, 'Baþarılı');
                loadDegerler();
            } else {
                showToast('error', data.message || 'Deðer silinirken bir hata oluþtu', 'Hata');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            handleAjaxError(error, 'Deðer silinirken bir hata oluþtu');
        });
    }
}
// Etik Kurallar
function loadEtikKurallar() {
    const listDiv = document.getElementById('etikKuralList');
    listDiv.innerHTML = '<div class="text-center text-muted py-3"><i class="fas fa-spinner fa-spin"></i> Yükleniyor...</div>';
    fetch('/admin/get-etik-kurallar')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.etik_kurallar.length > 0) {
                let html = '';
                data.etik_kurallar.forEach(item => {
                    html += `
                        <div class="list-group-item">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <h6 class="mb-1">${item.baslik}</h6>
                                    ${item.aciklama ? `<p class="mb-0 small text-muted">${item.aciklama}</p>` : ''}
                                </div>
                                <div>
                                    <button class="btn btn-sm btn-outline-danger" onclick="deleteEtikKural(${item.id})"><i class="fas fa-trash"></i></button>
                                </div>
                            </div>
                        </div>
                    `;
                });
                listDiv.innerHTML = html;
            } else {
                listDiv.innerHTML = '<div class="text-center text-muted py-3"><i class="fas fa-info-circle"></i> Henüz etik kural eklenmemiþ</div>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            listDiv.innerHTML = '<div class="alert alert-danger">Yükleme hatası!</div>';
        });
}
function saveEtikKural() {
    const data = {
        kurum_id: document.getElementById('etikKuralKurum').value,
        baslik: document.getElementById('etikKuralBaslik').value.trim(),
        aciklama: document.getElementById('etikKuralAciklama').value.trim()
    };
    if (!data.baslik) {
        showToast('warning', 'Lütfen baþlık girin!', 'Eksik Bilgi');
        return;
    }
    fetch('/admin/add-etik-kural', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('success', data.message, 'Baþarılı');
            bootstrap.Modal.getInstance(document.getElementById('etikKuralModal')).hide();
            loadEtikKurallar();
        } else {
            showToast('error', data.message || 'Etik kural eklenirken bir hata oluþtu', 'Hata');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        handleAjaxError(error, 'Etik kural eklenirken bir hata oluþtu');
    });
}
async function deleteEtikKural(id) {
    const confirmed = await confirmDelete('Bu etik kuralı silmek istediðinizden emin misiniz?');
    if (confirmed) {
        fetch(`/admin/delete-etik-kural/${id}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('success', data.message, 'Baþarılı');
                loadEtikKurallar();
            } else {
                showToast('error', data.message || 'Etik kural silinirken bir hata oluþtu', 'Hata');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            handleAjaxError(error, 'Etik kural silinirken bir hata oluþtu');
        });
    }
}
// Kalite Politikaları
function loadKalitePolitikalari() {
    const listDiv = document.getElementById('kalitePolitikasiList');
    listDiv.innerHTML = '<div class="text-center text-muted py-3"><i class="fas fa-spinner fa-spin"></i> Yükleniyor...</div>';
    fetch('/admin/get-kalite-politikalari')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.politikalar.length > 0) {
                let html = '';
                data.politikalar.forEach(item => {
                    html += `
                        <div class="list-group-item">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <h6 class="mb-1">${item.baslik}</h6>
                                    ${item.aciklama ? `<p class="mb-0 small text-muted">${item.aciklama}</p>` : ''}
                                </div>
                                <div>
                                    <button class="btn btn-sm btn-outline-danger" onclick="deleteKalitePolitikasi(${item.id})"><i class="fas fa-trash"></i></button>
                                </div>
                            </div>
                        </div>
                    `;
                });
                listDiv.innerHTML = html;
            } else {
                listDiv.innerHTML = '<div class="text-center text-muted py-3"><i class="fas fa-info-circle"></i> Henüz kalite politikası eklenmemiþ</div>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            listDiv.innerHTML = '<div class="alert alert-danger">Yükleme hatası!</div>';
        });
}
function saveKalitePolitikasi() {
    const data = {
        kurum_id: document.getElementById('kalitePolitikasiKurum').value,
        baslik: document.getElementById('kalitePolitikasiBaslik').value.trim(),
        aciklama: document.getElementById('kalitePolitikasiAciklama').value.trim()
    };
    if (!data.baslik) {
        showToast('warning', 'Lütfen baþlık girin!', 'Eksik Bilgi');
        return;
    }
    fetch('/admin/add-kalite-politikasi', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('success', data.message, 'Baþarılı');
            bootstrap.Modal.getInstance(document.getElementById('kalitePolitikasiModal')).hide();
            loadKalitePolitikalari();
        } else {
            showToast('error', data.message || 'Kalite politikası eklenirken bir hata oluþtu', 'Hata');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        handleAjaxError(error, 'Kalite politikası eklenirken bir hata oluþtu');
    });
}
async function deleteKalitePolitikasi(id) {
    const confirmed = await confirmDelete('Bu kalite politikasını silmek istediðinizden emin misiniz?');
    if (confirmed) {
        fetch(`/admin/delete-kalite-politikasi/${id}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('success', data.message, 'Baþarılı');
                loadKalitePolitikalari();
            } else {
                showToast('error', data.message || 'Kalite politikası silinirken bir hata oluþtu', 'Hata');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            handleAjaxError(error, 'Kalite politikası silinirken bir hata oluþtu');
        });
    }
}
// Ana Stratejiler
function loadAnaStratejiler() {
    const listDiv = document.getElementById('anaStratejiList');
    listDiv.innerHTML = '<div class="text-center text-muted py-3"><i class="fas fa-spinner fa-spin"></i> Yükleniyor...</div>';
    fetch('/admin/get-ana-stratejiler')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.stratejiler.length > 0) {
                let html = '';
                data.stratejiler.forEach(item => {
                    html += `
                        <div class="list-group-item list-group-item-action" style="cursor: pointer;" onclick="showAltStratejiler(${item.id}, '${item.ad}')">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <h6 class="mb-1">${item.ad} <i class="fas fa-arrow-right text-muted small"></i></h6>
                                    ${item.aciklama ? `<p class="mb-0 small text-muted">${item.aciklama}</p>` : ''}
                                </div>
                                <div onclick="event.stopPropagation();">
                                    <button class="btn btn-sm btn-outline-danger" onclick="deleteAnaStrateji(${item.id})"><i class="fas fa-trash"></i></button>
                                </div>
                            </div>
                        </div>
                    `;
                });
                listDiv.innerHTML = html;
            } else {
                listDiv.innerHTML = '<div class="text-center text-muted py-3"><i class="fas fa-info-circle"></i> Henüz ana strateji eklenmemiþ</div>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            listDiv.innerHTML = '<div class="alert alert-danger">Yükleme hatası!</div>';
        });
}
function saveAnaStrateji() {
    const data = {
        kurum_id: document.getElementById('anaStratejiKurum').value,
        ad: document.getElementById('anaStratejiAd').value.trim(),
        aciklama: document.getElementById('anaStratejiAciklama').value.trim()
    };
    if (!data.ad) {
        showToast('warning', 'Lütfen ad girin!', 'Eksik Bilgi');
        return;
    }
    fetch('/admin/add-ana-strateji', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('success', data.message, 'Baþarılı');
            bootstrap.Modal.getInstance(document.getElementById('anaStratejiModal')).hide();
            loadAnaStratejiler();
        } else {
            showToast('error', data.message || 'Ana strateji eklenirken bir hata oluþtu', 'Hata');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        handleAjaxError(error, 'Ana strateji eklenirken bir hata oluþtu');
    });
}
async function deleteAnaStrateji(id) {
    const confirmed = await confirmDelete('Bu ana stratejiyi ve baðlı tüm alt stratejileri silmek istediðinizden emin misiniz?', 'Bu iþlem geri alınamaz!');
    if (confirmed) {
        fetch(`/admin/delete-ana-strateji/${id}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('success', data.message, 'Baþarılı');
                loadAnaStratejiler();
            } else {
                showToast('error', data.message || 'Ana strateji silinirken bir hata oluþtu', 'Hata');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            handleAjaxError(error, 'Ana strateji silinirken bir hata oluþtu');
        });
    }
}
function showAltStratejiler(anaStratejiId, anaStratejiAd) {
    document.getElementById('altStratejiAnaId').value = anaStratejiId;
    document.getElementById('altStratejiBaþlık').textContent = anaStratejiAd + ' - Alt Stratejiler';
    document.getElementById('altStratejiSection').style.display = 'block';
    loadAltStratejiler(anaStratejiId);
}
// Alt Stratejiler
function loadAltStratejiler(anaStratejiId) {
    const listDiv = document.getElementById('altStratejiList');
    listDiv.innerHTML = '<div class="text-center text-muted py-3"><i class="fas fa-spinner fa-spin"></i> Yükleniyor...</div>';
    fetch(`/admin/get-alt-stratejiler/${anaStratejiId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.alt_stratejiler.length > 0) {
                let html = '';
                data.alt_stratejiler.forEach(item => {
                    html += `
                        <div class="list-group-item">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <h6 class="mb-1">${item.ad}</h6>
                                    ${item.aciklama ? `<p class="mb-0 small text-muted">${item.aciklama}</p>` : ''}
                                </div>
                                <div>
                                    <button class="btn btn-sm btn-outline-danger" onclick="deleteAltStrateji(${item.id})"><i class="fas fa-trash"></i></button>
                                </div>
                            </div>
                        </div>
                    `;
                });
                listDiv.innerHTML = html;
            } else {
                listDiv.innerHTML = '<div class="text-center text-muted py-3"><i class="fas fa-info-circle"></i> Henüz alt strateji eklenmemiþ</div>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            listDiv.innerHTML = '<div class="alert alert-danger">Yükleme hatası!</div>';
        });
}
function openAltStratejiModal() {
    const anaId = document.getElementById('altStratejiAnaId').value;
    if (!anaId) {
        showToast('warning', 'Çnce bir ana strateji seçin!', 'Uyarı');
        return;
    }
    const modal = new bootstrap.Modal(document.getElementById('altStratejiModal'), {
        backdrop: true,
        keyboard: true
    });
    modal.show();
}
function saveAltStrateji() {
    const anaId = document.getElementById('altStratejiAnaId').value;
    const data = {
        ana_strateji_id: anaId,
        ad: document.getElementById('altStratejiAd').value.trim(),
        aciklama: document.getElementById('altStratejiAciklama').value.trim()
    };
    if (!data.ad) {
        showToast('warning', 'Lütfen ad girin!', 'Eksik Bilgi');
        return;
    }
    fetch('/admin/add-alt-strateji', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('success', data.message, 'Baþarılı');
            bootstrap.Modal.getInstance(document.getElementById('altStratejiModal')).hide();
            loadAltStratejiler(anaId);
        } else {
            showToast('error', data.message || 'Alt strateji eklenirken bir hata oluþtu', 'Hata');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        handleAjaxError(error, 'Alt strateji eklenirken bir hata oluþtu');
    });
}
async function deleteAltStrateji(id) {
    const anaId = document.getElementById('altStratejiAnaId').value;
    const confirmed = await confirmDelete('Bu alt stratejiyi silmek istediðinizden emin misiniz?');
    if (confirmed) {
        fetch(`/admin/delete-alt-strateji/${id}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('success', data.message, 'Baþarılı');
                loadAltStratejiler(anaId);
            } else {
                showToast('error', data.message || 'Alt strateji silinirken bir hata oluþtu', 'Hata');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            handleAjaxError(error, 'Alt strateji silinirken bir hata oluþtu');
        });
    }
}
function getRoleAçıklama(role) {
    if (!role) return '';
    const key = role.toLowerCase();
    const descriptions = {
        'kurum_kullanici': 'Normal kurum çalıþanı. Sadece atandıÝı süreçleri görür ve yönetir. Süreç Lideri/Üyesi rolleri süreç atamalarında belirlenir.',
        'user': 'Normal kurum çalıþanı. Sadece atandıÝı süreçleri görür ve yönetir. Süreç Lideri/Üyesi rolleri süreç atamalarında belirlenir.',
        'ust_yonetim': 'Kurumdaki üst düzey yönetici. Tüm süreçleri görüntüleyebilir, stratejik kararlar alabilir ve raporları inceleyebilir.',
        'kurum_yetkilisi': 'Kurum yöneticisi. Tüm kullanıcıları ve süreçleri yönetebilir, kurum bilgilerini güncelleyebilir.',
        'sistem_admin': 'Sistem yöneticisi. Tüm kurumları ve kullanıcıları yönetebilir, sistem ayarlarını deÝiþtirebilir.',
        'admin': 'Sistem yöneticisi. Tüm kurumları ve kullanıcıları yönetebilir, sistem ayarlarını deÝiþtirebilir.'
    };
    return descriptions[key] || '';
}
// Rol açıklamalarını göster
function showRoleAçıklama(role) {
    const descriptionDiv = document.getElementById('roleAçıklama');
    const descText = document.getElementById('roleDescText');
    const description = getRoleAçıklama(role);
    if (description) {
        descText.textContent = description;
        descriptionDiv.style.display = 'block';
    } else if (descriptionDiv) {
        descriptionDiv.style.display = 'none';
    }
}
function showRoleAçıklamaDüzenle(role) {
    const descriptionDiv = document.getElementById('editRoleAçıklama');
    const descText = document.getElementById('editRoleDescText');
    if (!descriptionDiv || !descText) return;
    const description = getRoleAçıklama(role);
    if (description) {
        descText.textContent = description;
        descriptionDiv.style.display = 'block';
    } else {
        descriptionDiv.style.display = 'none';
    }
}
// ===========================
// Toast Notification Sistemi
// ===========================
// Toast container'ı oluþtur
function createToastContainer() {
    if (!document.getElementById('toast-container')) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.classAd = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
}
// showToast wrapper - hem eski hem yeni formatı destekler
(function() {
    const originalShowToast = window.showToast;
    window.showToast = function(...args) {
        // EÝer base.html'deki showToast yüklüyse onu kullan
        if (originalShowToast && typeof originalShowToast === 'function') {
            // Yeni format: showToast(type, message, title)
            if (args.length >= 2 && ['success', 'error', 'warning', 'info'].includes(args[0])) {
                return originalShowToast(args[0], args[1], args[2] || null);
            }
            // Eski format: showToast(message, type, duration) - dönüþtür
            else if (args.length >= 2 && typeof args[0] === 'string' && ['success', 'error', 'warning', 'info'].includes(args[1])) {
                return originalShowToast(args[1], args[0], args[2] || null);
            }
            // Tek parametre: mesaj olarak kabul et
            else if (args.length === 1) {
                return originalShowToast('info', args[0]);
            }
            // Varsayılan
            return originalShowToast('info', args.join(' '));
        } else {
            console.error('showToast fonksiyonu bulunamadı!', args);
        }
    };
})();
// Sayfa yüklendiÝinde kontrol ve baþlatma
document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin Panel yükleniyor...');
    const userSearch = document.getElementById('user-search-input');
    if (userSearch) {
        userSearch.addEventListener('input', filterUserList);
    }
    // Bootstrap kontrolü
    if (typeof bootstrap === 'undefined') {
        console.error('Bootstrap yüklenmemiþ!');
        document.body.insertAdjacentHTML(
            'afterbegin',
            '<div class="container mt-4"><div class="alert alert-danger">Bootstrap yüklenmemiş. Sayfayı yenileyin.</div></div>'
        );
        return;
    }
    console.log('Bootstrap yüklü:', bootstrap);
    // Modal elementlerini kontrol et
    const modals = {
        'newOrgModal': 'Kurum Ekle',
        'newUserModal': 'Kullanıcı Ekle',
        'bulkYükleModal': 'Toplu Kullanıcı Yükle'
    };
    for (const [modalId, modalAd] of Object.entries(modals)) {
        const modalEl = document.getElementById(modalId);
        if (!modalEl) {
            console.error(`${modalAd} modal'ı bulunamadı! (${modalId})`);
        } else {
            console.log(`${modalAd} modal'ı bulundu:`, modalEl);
        }
    }
    // Butonları kontrol et
    const buttons = {
        'openNewOrganizationModal': 'Kurum Ekle butonu',
        'openNewUserModal': 'Kullanıcı Ekle butonu',
        'openBulkYükleModal': 'Toplu Yükle butonu',
        'downloadUserTemplate': 'Excel Şablonu İndir butonu'
    };
    for (const [funcAd, buttonAd] of Object.entries(buttons)) {
        if (typeof window[funcAd] !== 'function') {
            console.error(`${buttonAd} fonksiyonu bulunamadı! (${funcAd})`);
        } else {
            console.log(`${buttonAd} fonksiyonu mevcut:`, window[funcAd]);
        }
    }
    // Yeni Süreç Modalı açıldıÝında
    const newProcessModal = document.getElementById('newProcessModal');
    if (newProcessModal) {
        newProcessModal.addEventListener('shown.bs.modal', function() {
            const kurumSelect = document.getElementById('newProcessKurum');
            if (kurumSelect && kurumSelect.value && typeof filterUsersByKurum === 'function') {
                filterUsersByKurum(kurumSelect.value, 'newProcessLider');
            }
        });
    }
    // Yeni Kullanıcı Modalı açıldıÝında
    const newUserModal = document.getElementById('newUserModal');
    if (newUserModal) {
        newUserModal.addEventListener('shown.bs.modal', function() {
            // Gelecekte ihtiyaç olursa buraya eklenebilir
        });
    }
    console.log('Admin Panel yükleme tamamlandı.');
});
// ============ ROL MATRÝSÝ FONKSÝYONLARI ============
function loadRolMatrisi() {
    const loading = document.getElementById('rol-matrisi-loading');
    const content = document.getElementById('rol-matrisi-content');
    const error = document.getElementById('rol-matrisi-error');
    if (!loading || !content || !error) {
        console.error('Rol matrisi elementleri bulunamadı!');
        return;
    }
    // Loading göster
    loading.style.display = 'block';
    content.style.display = 'none';
    error.style.display = 'none';
    console.log('Rol matrisi yükleniyor...');
    fetch('/api/rol-matrisi')
        .then(r => {
            console.log('API yanıtı:', r.status, r.statusText);
            if (!r.ok) {
                throw new Error(`HTTP ${r.status}: ${r.statusText}`);
            }
            return r.json();
        })
        .then(data => {
            console.log('Rol matrisi verisi:', data);
            console.log('Kullanıcı sayısı:', data.kullanicilar ? data.kullanicilar.length : 0);
            console.log('Yetki kategorisi sayısı:', data.yetki_kategorileri ? data.yetki_kategorileri.length : 0);
            console.log('Yetki sayısı:', data.yetkiler ? data.yetkiler.length : 0);
            if (data.success === true && data.kullanicilar && data.yetki_kategorileri) {
                try {
                    renderRolMatrisi(data);
                    loading.style.display = 'none';
                    content.style.display = 'block';
                } catch (e) {
                    console.error('Rol matrisi render hatası:', e);
                    throw e;
                }
            } else {
                throw new Error(data.message || 'Rol matrisi yüklenemedi - Gerekli veriler eksik');
            }
        })
        .catch(err => {
            console.error('Rol matrisi yükleme hatası:', err);
            loading.style.display = 'none';
            error.style.display = 'block';
            const errorText = error.querySelector('strong');
            if (errorText && errorText.nextSibling) {
                errorText.nextSibling.textContent = ' ' + err.message;
            }
            if (typeof window.showToast === 'function') {
                window.showToast('error', 'Rol matrisi yüklenirken hata oluþtu: ' + err.message, 'Hata');
            }
        });
}
function renderRolMatrisi(data) {
    const content = document.getElementById('rol-matrisi-content');
    const kullanicilar = data.kullanicilar || [];
    const yetkiKategorileri = data.yetki_kategorileri || [];
    const yetkiler = data.yetkiler || [];
    console.log('Render - Kullanıcı sayısı:', kullanicilar.length);
    console.log('Render - Yetki kategorisi sayısı:', yetkiKategorileri.length);
    console.log('Render - Ýlk kullanıcı:', kullanicilar[0]);
    if (!kullanicilar || kullanicilar.length === 0) {
        content.innerHTML = '<div class="alert alert-info">Henüz kullanıcı bulunmamaktadır.</div>';
        return;
    }
    if (!yetkiKategorileri || yetkiKategorileri.length === 0) {
        content.innerHTML = '<div class="alert alert-warning">Yetki kategorileri bulunamadı.</div>';
        return;
    }
    // Arama ve filtreleme alanı
    let html = `
        <div class="row mb-3">
            <div class="col-md-6">
                <div class="input-group">
                    <span class="input-group-text"><i class="fas fa-search"></i></span>
                    <input type="text" class="form-control" id="kullaniciArama" placeholder="Kullanıcı ara..." onkeyup="filterKullanicilar()">
                </div>
            </div>
            <div class="col-md-3">
                <select class="form-select" id="rolFiltresi" onchange="filterKullanicilar()">
                    <option value="">Tüm Roller</option>
                    <option value="admin">Admin</option>
                    <option value="kurum_yoneticisi">Kurum Yöneticisi</option>
                    <option value="ust_yonetim">Üst Yönetim</option>
                    <option value="kurum_kullanici">Kurum Kullanıcısı</option>
                </select>
            </div>
            <div class="col-md-3">
                <button class="btn btn-outline-secondary" onclick="clearFiltreles()">
                    <i class="fas fa-times"></i> Filtreleri Temizle
                </button>
            </div>
        </div>
        <div class="table-responsive" style="max-height: 650px; overflow: auto;">
            <div style="overflow-x: auto; max-width: 100%;">
                <table class="table table-bordered table-hover table-sm" style="font-size: 0.85rem; min-width: 1200px;">
                    <thead class="table-light" style="position: sticky; top: 0; z-index: 100;">
                        <tr>
                            <th rowspan="2" style="vertical-align: middle; width: 140px; font-weight: 600;">Kullanıcı</th>`;
            // Kategori baþlıkları - Gruplandırılmıþ
            yetkiKategorileri.forEach(kat => {
                if (!kat.yetkiler || !Array.isArray(kat.yetkiler)) return;
                html += `<th colspan="${kat.yetkiler.length}" class="text-center bg-primary text-white" style="font-size: 0.85rem; padding: 8px;">${kat.grup}</th>`;
            });
            html += `</tr><tr>`;
            // Alt baþlıklar - Gruplandırılmıþ CRUD
            yetkiKategorileri.forEach(kat => {
                if (!kat.yetkiler || !Array.isArray(kat.yetkiler)) return;
                // Her kategori için CRUD grupları
                const crudGroups = {};
                kat.yetkiler.forEach(yetki => {
                    const baseAd = yetki.kod.replace(/_[crud]$/, '');
                    if (!crudGroups[baseAd]) {
                        crudGroups[baseAd] = [];
                    }
                    crudGroups[baseAd].push(yetki);
                });
                // Her CRUD grubu için baþlık
                Object.keys(crudGroups).forEach(baseAd => {
                    const group = crudGroups[baseAd];
                    const groupAd = group[0].ad.replace(/ (Oluştur|Oku|Güncelle|Sil)$/, '');
                    html += `<th colspan="4" class="text-center bg-secondary text-white" style="font-size: 0.8rem; padding: 6px;">${groupAd}</th>`;
                });
            });
            html += `</tr><tr>`;
            // CRUD iþlemleri
            yetkiKategorileri.forEach(kat => {
                if (!kat.yetkiler || !Array.isArray(kat.yetkiler)) return;
                const crudGroups = {};
                kat.yetkiler.forEach(yetki => {
                    const baseAd = yetki.kod.replace(/_[crud]$/, '');
                    if (!crudGroups[baseAd]) {
                        crudGroups[baseAd] = [];
                    }
                    crudGroups[baseAd].push(yetki);
                });
                Object.keys(crudGroups).forEach(baseAd => {
                    const group = crudGroups[baseAd];
                    // CRUD sırasına göre sırala
                    const crudOrder = ['c', 'r', 'u', 'd'];
                    crudOrder.forEach(crud => {
                        const yetki = group.find(y => y.kod.endsWith('_' + crud));
                        if (yetki) {
                            const crudAd = crud === 'c' ? 'Oluştur' : crud === 'r' ? 'Oku' : crud === 'u' ? 'Güncelle' : 'Sil';
                            html += `<th class="text-center" style="width: 60px; font-size: 0.7rem; padding: 4px;" title="${yetki.aciklama}">${crudAd}</th>`;
                        }
                    });
                });
            });
    html += `</tr></thead><tbody id="kullaniciTablosu">`;
    // Kullanıcı satırları
    kullanicilar.forEach((user, idx) => {
        const bgColor = idx % 2 === 0 ? '' : 'table-light';
        const displayAd = (user.first_name && user.last_name) 
            ? `${user.first_name} ${user.last_name}` 
            : (user.first_name || user.last_name || user.username || 'Bilinmeyen');
        html += `
            <tr class="${bgColor} kullanici-satir" data-kullanici="${displayAd.toLowerCase()}" data-rol="${user.sistem_rol}">
                <td style="font-size: 0.85rem; padding: 8px; font-weight: 500;">
                    <div class="fw-bold">${displayAd}</div>
                    <small class="text-muted">${user.sistem_rol}</small>
                </td>`;
        // Her kategori için checkbox'lar
        yetkiKategorileri.forEach(kat => {
            if (!kat.yetkiler || !Array.isArray(kat.yetkiler)) {
                console.warn('Kategori yetkileri eksik:', kat);
                return;
            }
            kat.yetkiler.forEach(yetki => {
                const yetkiVar = yetkiler.find(y => 
                    y.kullanici_id === user.id && y.yetki_kodu === yetki.kod
                );
                // Sistem rolüne göre varsayılan yetki kontrolü
                let isChecked = '';
                let disabled = '';
                if (user.sistem_rol === 'admin') {
                    // Admin her þeye yetkili
                    isChecked = 'checked';
                    disabled = 'disabled';
                } else if (user.sistem_rol === 'kurum_yoneticisi') {
                    // Kurum yöneticisi: Kurum + Kullanıcı + Süreç yetkileri
                    if (yetki.kod.startsWith('kurum_') || 
                        yetki.kod.startsWith('kullanici_') ||
                        yetki.kod.startsWith('surec_')) {
                        isChecked = 'checked';
                    }
                } else if (user.sistem_rol === 'ust_yonetim') {
                    // Üst yönetim: Kurum + Süreç yetkileri
                    if (yetki.kod.startsWith('kurum_') ||
                        yetki.kod.startsWith('surec_')) {
                        isChecked = 'checked';
                    }
                } else if (user.sistem_rol === 'kurum_kullanici') {
                    // Kurum kullanıcısı: Hiçbir yetki yok (sadece kendi bilgilerini görebilir)
                    isChecked = '';
                }
                // Çzel yetki varsa onu kullan (özel yetki sistem rolünden öncelikli)
                if (yetkiVar) {
                    isChecked = yetkiVar.aktif ? 'checked' : '';
                }
                const checkboxId = `rol_${user.id}_${yetki.kod}`;
                html += `
                    <td class="text-center" style="padding: 6px;">
                        <input type="checkbox" 
                               class="form-check-input" 
                               id="${checkboxId}"
                               ${isChecked}
                               ${disabled}
                               onchange="updateRolYetki(${user.id}, '${yetki.kod}', this.checked)"
                               style="cursor: pointer; width: 18px; height: 18px;">
                    </td>`;
            });
        });
        html += `</tr>`;
    });
    html += `</tbody></table></div></div>`;
    content.innerHTML = html;
}
function updateRolYetki(kullaniciId, yetkiKodu, aktif) {
    const checkboxId = `rol_${kullaniciId}_${yetkiKodu}`;
    const checkbox = document.getElementById(checkboxId);
    if (!checkbox) return;
    // Optimistic update
    checkbox.checked = aktif;
    fetch('/api/rol-matrisi/update', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            kullanici_id: kullaniciId,
            yetki_kodu: yetkiKodu,
            aktif: aktif
        })
    })
    .then(r => r.json())
    .then(data => {
        if(data.success) {
            showToast('success', data.message || 'Yetki güncellendi');
        } else {
            showToast('error', data.message || 'Kayıt başarısız');
            // Hata durumunda checkbox'ı eski haline döndür
            checkbox.checked = !aktif;
        }
    })
    .catch(err => {
        showToast('error', 'Bağlantı hatası: ' + err.message);
        // Hata durumunda checkbox'ı eski haline döndür
        checkbox.checked = !aktif;
    });
}
function saveRolMatrisi() {
    showToast('success', 'Yetki değişiklikleri kaydedildi ve tablo yenilendi.');
    loadRolMatrisi();
}
// ============ ROL MATRİSİ 2 FONKSİYONLARI ============
function loadRolMatrisi2() {
    const loading = document.getElementById('rol-matrisi2-loading');
    const content = document.getElementById('rol-matrisi2-content');
    const error = document.getElementById('rol-matrisi2-error');
    if (!loading || !content || !error) {
        console.error('Rol matrisi 2 elementleri bulunamadı!');
        return;
    }
    loading.style.display = 'block';
    content.style.display = 'none';
    error.style.display = 'none';
    fetch('/api/rol-matrisi2')
        .then(r => {
            if (!r.ok) {
                throw new Error(`HTTP ${r.status}: ${r.statusText}`);
            }
            return r.json();
        })
        .then(data => {
            if (data.success) {
                renderRolMatrisi2(data);
                loading.style.display = 'none';
                content.style.display = 'block';
            } else {
                throw new Error(data.message || 'Rol matrisi 2 getirilemedi');
            }
        })
        .catch(err => {
            console.error('Rol matrisi 2 yükleme hatası:', err);
            loading.style.display = 'none';
            error.style.display = 'block';
            if (typeof window.showToast === 'function') {
                window.showToast('error', err.message, 'Hata');
            }
        });
}
function renderRolMatrisi2(data) {
    const content = document.getElementById('rol-matrisi2-content');
    const kullanicilar = data.kullanicilar || [];
    const yetkiKategorileri = data.yetki_kategorileri || [];
    const yetkiler = data.yetkiler || [];
    if (!kullanicilar.length) {
        content.innerHTML = '<div class="alert alert-info">Gösterilecek kullanıcı bulunamadı.</div>';
        return;
    }
    if (!yetkiKategorileri.length) {
        content.innerHTML = '<div class="alert alert-warning">Yetki kategorisi tanımlı değil.</div>';
        return;
    }
    const kurumSet = new Set();
    kullanicilar.forEach(u => {
        if (u.kurum_adi) {
            kurumSet.add(u.kurum_adi);
        }
    });
    const kurumListesi = Array.from(kurumSet);
    let html = `
        <div class="row mb-3">
            <div class="col-md-4">
                <div class="input-group">
                    <span class="input-group-text"><i class="fas fa-search"></i></span>
                    <input type="text" class="form-control" id="kullaniciArama2" placeholder="Kullanıcı ara..." onkeyup="filterKullanicilar2()">
                </div>
            </div>
            <div class="col-md-3">
                <select class="form-select" id="rolFiltresi2" onchange="filterKullanicilar2()">
                    <option value="">Tüm Roller</option>
                    <option value="admin">Admin</option>
                    <option value="kurum_yoneticisi">Kurum Yöneticisi</option>
                    <option value="ust_yonetim">Üst Yönetim</option>
                    <option value="kurum_kullanici">Kurum Kullanıcısı</option>
                </select>
            </div>`;
    html += `
            <div class="col-md-3">
                <select class="form-select" id="kurumFiltresi2" onchange="filterKullanicilar2()">
                    <option value="">Tüm Kurumlar</option>`;
    kurumListesi.forEach(k => {
        html += `<option value="${k}">${k}</option>`;
    });
    html += `
                </select>
            </div>
            <div class="col-md-2">
                <button class="btn btn-outline-secondary w-100" onclick="clearFiltreles2()">
                    <i class="fas fa-times"></i> Temizle
                </button>
            </div>
        </div>
        <div class="table-responsive" style="max-height: 650px; overflow: auto;">
            <div style="overflow-x: auto; max-width: 100%;">
                <table class="table table-bordered table-hover table-sm" style="font-size: 0.85rem; min-width: 1200px;">
                    <thead class="table-light" style="position: sticky; top: 0; z-index: 100;">
                        <tr>
                            <th rowspan="2" style="vertical-align: middle; width: 180px; font-weight: 600;">Kullanıcı</th>`;
    yetkiKategorileri.forEach(kat => {
        if (Array.isArray(kat.yetkiler)) {
            html += `<th colspan="${kat.yetkiler.length}" class="text-center bg-primary text-white" style="font-size: 0.85rem; padding: 8px;">${kat.grup}</th>`;
        }
    });
    html += `</tr><tr>`;
    yetkiKategorileri.forEach(kat => {
        if (!Array.isArray(kat.yetkiler)) return;
        const crudGroups = {};
        kat.yetkiler.forEach(yetki => {
            const baseAd = yetki.kod.replace(/_[crud]$/, '');
            crudGroups[baseAd] = crudGroups[baseAd] || [];
            crudGroups[baseAd].push(yetki);
        });
        Object.keys(crudGroups).forEach(baseAd => {
            const group = crudGroups[baseAd];
            const groupAd = group[0].ad.replace(/ (Oluştur|Oku|Güncelle|Sil)$/, '');
            html += `<th colspan="4" class="text-center bg-secondary text-white" style="font-size: 0.8rem; padding: 6px;">${groupAd}</th>`;
        });
    });
    html += `</tr><tr>`;
    yetkiKategorileri.forEach(kat => {
        if (!Array.isArray(kat.yetkiler)) return;
        const crudGroups = {};
        kat.yetkiler.forEach(yetki => {
            const baseAd = yetki.kod.replace(/_[crud]$/, '');
            crudGroups[baseAd] = crudGroups[baseAd] || [];
            crudGroups[baseAd].push(yetki);
        });
        ['c', 'r', 'u', 'd'].forEach(crud => {
            Object.keys(crudGroups).forEach(baseAd => {
                const group = crudGroups[baseAd];
                const yetki = group.find(y => y.kod.endsWith('_' + crud));
                if (yetki) {
                    const crudAd = crud === 'c' ? 'Oluştur' : crud === 'r' ? 'Oku' : crud === 'u' ? 'Güncelle' : 'Sil';
                    html += `<th class="text-center" style="width: 60px; font-size: 0.7rem; padding: 4px;" title="${yetki.aciklama}">${crudAd}</th>`;
                }
            });
        });
    });
    html += `</tr></thead><tbody id="kullaniciTablosu2">`;
    kullanicilar.forEach((user, idx) => {
        const displayAd = (user.first_name && user.last_name)
            ? `${user.first_name} ${user.last_name}`
            : (user.first_name || user.last_name || user.username || 'Bilinmeyen');
        const kurumAd = user.kurum_adi || '-';
        const bgColor = idx % 2 === 0 ? '' : 'table-light';
        html += `
            <tr class="${bgColor} kullanici-satir-2" data-kullanici="${displayAd.toLowerCase()}" data-rol="${user.sistem_rol}" data-kurum="${kurumAd}">
                <td style="font-size: 0.85rem; padding: 8px; font-weight: 500;">
                    <div class="fw-bold">${displayAd}</div>
                    <small class="text-muted">${user.sistem_rol}${kurumAd ? ' • ' + kurumAd : ''}</small>
                </td>`;
        yetkiKategorileri.forEach(kat => {
            if (!Array.isArray(kat.yetkiler)) return;
            kat.yetkiler.forEach(yetki => {
                const kayit = yetkiler.find(y => y.kullanici_id === user.id && y.yetki_kodu === yetki.kod);
                let isChecked = '';
                let disabled = '';
                if (user.sistem_rol === 'admin') {
                    isChecked = 'checked';
                    disabled = 'disabled';
                } else if (user.sistem_rol === 'kurum_yoneticisi') {
                    if (yetki.kod.startsWith('kurum_') || yetki.kod.startsWith('kullanici_') || yetki.kod.startsWith('surec_')) {
                        isChecked = 'checked';
                    }
                } else if (user.sistem_rol === 'ust_yonetim') {
                    if (yetki.kod.startsWith('kurum_') || yetki.kod.startsWith('surec_')) {
                        isChecked = 'checked';
                    }
                }
                if (kayit) {
                    isChecked = kayit.aktif ? 'checked' : '';
                }
                const checkboxId = `rol2_${user.id}_${yetki.kod}`;
                html += `
                    <td class="text-center" style="padding: 6px;">
                        <input type="checkbox"
                               class="form-check-input"
                               id="${checkboxId}"
                               ${isChecked}
                               ${disabled}
                               onchange="updateRolYetki2(${user.id}, '${yetki.kod}', this.checked)"
                               style="cursor: pointer; width: 18px; height: 18px;">
                    </td>`;
            });
        });
        html += `</tr>`;
    });
    html += `</tbody></table></div></div>`;
    content.innerHTML = html;
}
function updateRolYetki2(kullaniciId, yetkiKodu, aktif) {
    const checkbox = document.getElementById(`rol2_${kullaniciId}_${yetkiKodu}`);
    if (!checkbox) return;
    checkbox.checked = aktif;
    fetch('/api/rol-matrisi2/update', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            kullanici_id: kullaniciId,
            yetki_kodu: yetkiKodu,
            aktif: aktif
        })
    })
    .then(r => r.json())
    .then(data => {
        if (!data.success) {
            checkbox.checked = !aktif;
            showToast('error', data.message || 'Kayıt başarısız');
        } else {
            showToast('success', data.message || 'Yetki güncellendi ve kaydedildi.');
        }
    })
    .catch(err => {
        checkbox.checked = !aktif;
        showToast('error', 'Bağlantı hatası: ' + err.message);
    });
}
function saveRolMatrisi2() {
    showToast('success', 'Yetki değişiklikleri kaydedildi ve tablo yenilendi.');
    loadRolMatrisi2();
}
function filterKullanicilar2() {
    const arama = (document.getElementById('kullaniciArama2')?.value || '').toLowerCase();
    const rol = document.getElementById('rolFiltresi2')?.value || '';
    const kurum = document.getElementById('kurumFiltresi2')?.value || '';
    const satirlar = document.querySelectorAll('.kullanici-satir-2');
    satirlar.forEach(satir => {
        const ad = satir.getAttribute('data-kullanici') || '';
        const satirRol = satir.getAttribute('data-rol') || '';
        const satirKurum = satir.getAttribute('data-kurum') || '';
        const uygun = (arama === '' || ad.includes(arama)) && (rol === '' || satirRol === rol) && (kurum === '' || satirKurum === kurum);
        satir.style.display = uygun ? '' : 'none';
    });
}
function clearFiltreles2() {
    const arama = document.getElementById('kullaniciArama2');
    const rol = document.getElementById('rolFiltresi2');
    const kurum = document.getElementById('kurumFiltresi2');
    if (arama) arama.value = '';
    if (rol) rol.value = '';
    if (kurum) kurum.value = '';
    filterKullanicilar2();
}
// Inline handlerlar için global export
window.loadRolMatrisi = loadRolMatrisi;
window.saveRolMatrisi = saveRolMatrisi;
window.renderRolMatrisi = renderRolMatrisi;
window.filterKullanicilar = filterKullanicilar;
window.clearFiltreles = clearFiltreles;
window.loadRolMatrisi2 = loadRolMatrisi2;
window.saveRolMatrisi2 = saveRolMatrisi2;
window.renderRolMatrisi2 = renderRolMatrisi2;
window.filterKullanicilar2 = filterKullanicilar2;
window.clearFiltreles2 = clearFiltreles2;
// ============ ROL MATRÝSÝ FÝLTRELEME FONKSÝYONLARI ============
function filterKullanicilar() {
    const aramaMetni = document.getElementById('kullaniciArama').value.toLowerCase();
    const rolFiltresi = document.getElementById('rolFiltresi').value;
    const satirlar = document.querySelectorAll('.kullanici-satir');
    satirlar.forEach(satir => {
        const kullaniciAdi = satir.getAttribute('data-kullanici') || '';
        const kullaniciRolu = satir.getAttribute('data-rol') || '';
        const aramaUygun = aramaMetni === '' || kullaniciAdi.includes(aramaMetni);
        const rolUygun = rolFiltresi === '' || kullaniciRolu === rolFiltresi;
        if (aramaUygun && rolUygun) {
            satir.style.display = '';
        } else {
            satir.style.display = 'none';
        }
    });
}
function clearFiltreles() {
    document.getElementById('kullaniciArama').value = '';
    document.getElementById('rolFiltresi').value = '';
    filterKullanicilar();
}
// Rol Matrisi tab'ına tıklandıÝında OTOMATIK yükle
document.addEventListener('DOMContentLoaded', function() {
    const rolMatrisi2Tab = document.getElementById('rol-matrisi2-tab');
    if (rolMatrisi2Tab) {
        rolMatrisi2Tab.addEventListener('shown.bs.tab', function() {
            loadRolMatrisi2();
        });
        const rolMatrisi2Pane = document.getElementById('rol-matrisi2');
        if (rolMatrisi2Pane && rolMatrisi2Pane.classList.contains('active')) {
            loadRolMatrisi2();
        }
    }
});
document.addEventListener('DOMContentLoaded', function() {
    loadAdminUsers();
});

document.addEventListener('DOMContentLoaded', function() {
    const kurumSelect = document.getElementById('newProcessKurum');
    if (kurumSelect && kurumSelect.dataset.initFilter && kurumSelect.value) {
        if (typeof filterUsersByKurum === 'function') {
            filterUsersByKurum(kurumSelect.value, 'newProcessLider');
        }
    }
});

// Fallbacks: Eğer üstteki büyük script çalışmazsa butonlar yine de işlesin
(function() {
    const getCsrf = () => document.querySelector('meta[name="csrf-token"]')?.content || '';
    const safeBadge = (role) => {
        const badges = (typeof ROLE_BADGES !== 'undefined' && ROLE_BADGES) || {};
        return badges[role] || badges.user || { text: '', class: 'bg-secondary' };
    };

    // Basit sil onayı fallback'i
    if (typeof window.confirmDelete !== 'function') {
        window.confirmDelete = function(title, text) {
            if (typeof Swal !== 'undefined') {
                return Swal.fire({
                    title: title || 'Emin misiniz?',
                    text: text || '',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#dc3545',
                    cancelButtonColor: '#6c757d',
                    confirmButtonText: 'Evet, sil',
                    cancelButtonText: 'İptal'
                }).then(result => !!result.isConfirmed);
            }
            const message = text ? `${title}\n\n${text}` : (title || 'Emin misiniz?');
            return Promise.resolve(window.confirm(message));
        };
    }

    // Kurum görüntüleme fallback'i
    if (typeof window.viewOrganization !== 'function') {
        window.viewOrganization = function(orgAd) {
            return fetch(`/admin/get-organization/${orgAd}`)
                .then(res => res.json())
                .then(data => {
                    if (!data || !data.success) throw new Error((data && data.message) || 'Kurum getirilemedi');
                    const modalEl = document.getElementById('viewOrganizationModal');
                    if (modalEl) {
                        document.getElementById('viewOrgLogo').src = data.organization.logo_url || '/static/images/default-org-logo.png';
                        document.getElementById('viewOrgKisaAd').textContent = data.organization.kisa_ad || '-';
                        document.getElementById('viewOrgTicariUnvan').textContent = data.organization.ticari_unvan || '-';
                        document.getElementById('viewOrgSektor').textContent = data.organization.sektor || '-';
                        document.getElementById('viewOrgCalisanSayisi').textContent = data.organization.calisan_sayisi || '-';
                        document.getElementById('viewOrgFaaliyetAlani').textContent = data.organization.faaliyet_alani || '-';
                        document.getElementById('viewOrgEmail').textContent = data.organization.email || '-';
                        document.getElementById('viewOrgTelefon').textContent = data.organization.telefon || '-';
                        document.getElementById('viewOrgWeb').textContent = data.organization.web_adresi || '-';
                        document.getElementById('viewOrgVergiDairesi').textContent = data.organization.vergi_dairesi || '-';
                        document.getElementById('viewOrgVergiNumarasi').textContent = data.organization.vergi_numarasi || '-';
                        window.currentOrgAd = orgAd;
                        const modal = new bootstrap.Modal(modalEl, { backdrop: true, keyboard: true });
                        modal.show();
                    } else {
                        showToast('info', `Kurum: ${data.organization.kisa_ad}`);
                    }
                    return data;
                })
                .catch(err => {
                    showToast('error', err.message || 'Kurum getirilemedi');
                });
        };
    }

    // Kurum düzenleme fallback'i
    if (typeof window.editOrganization !== 'function') {
        window.editOrganization = function(orgAd) {
            return fetch(`/admin/get-organization/${orgAd}`)
                .then(res => res.json())
                .then(data => {
                    if (!data || !data.success) throw new Error((data && data.message) || 'Kurum getirilemedi');
                    const org = data.organization;
                    document.getElementById('editOrgId').value = org.id;
                    document.getElementById('editOrgOldKisaAd').value = org.kisa_ad;
                    document.getElementById('editOrgKisaAd').value = org.kisa_ad || '';
                    document.getElementById('editOrgTicariUnvan').value = org.ticari_unvan || '';
                    document.getElementById('editOrgFaaliyetAlani').value = org.faaliyet_alani || '';
                    document.getElementById('editOrgSektor').value = org.sektor || '';
                    document.getElementById('editOrgCalisanSayisi').value = org.calisan_sayisi || '';
                    document.getElementById('editOrgEmail').value = org.email || '';
                    document.getElementById('editOrgTelefon').value = org.telefon || '';
                    document.getElementById('editOrgWeb').value = org.web_adresi || '';
                    document.getElementById('editOrgVergiDairesi').value = org.vergi_dairesi || '';
                    document.getElementById('editOrgVergiNumarasi').value = org.vergi_numarasi || '';
                    document.getElementById('editOrgLogoUrl').value = org.logo_url || '';
                    const modal = new bootstrap.Modal(document.getElementById('editOrganizationModal'), { backdrop: true, keyboard: true });
                    modal.show();
                    return data;
                })
                .catch(err => {
                    showToast('error', err.message || 'Kurum düzenleme açılmadı');
                });
        };
    }

    // Kurum silme fallback'i
    if (typeof window.deleteOrganization !== 'function') {
        window.deleteOrganization = function(orgAd, orgId) {
            const ask = (typeof window.confirmDelete === 'function')
                ? window.confirmDelete(`"${orgAd}" kurumunu silmek istediğinize emin misiniz?`, 'Bu işlem geri alınamaz ve kurumdaki tüm kullanıcılar, süreçler ve veriler silinecektir!')
                : Promise.resolve(window.confirm('Emin misiniz?'));

            return Promise.resolve(ask)
                .then(confirmed => {
                    if (!confirmed) return;
                    const csrf = document.querySelector('meta[name="csrf-token"]')?.content || '';
                    return fetch(`/admin/delete-organization/${orgId}`, {
                        method: 'DELETE',
                        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf }
                    })
                        .then(res => res.json())
                        .then(data => {
                            if (!data || !data.success) throw new Error((data && data.message) || 'Kurum silinemedi');
                            if (window.showToast) showToast('success', data.message || 'Kurum silindi');
                            setTimeout(() => location.reload(), 1200);
                            return data;
                        });
                })
                .catch(err => {
                    showToast('error', err.message || 'Kurum silinemedi');
                });
        };
    }

    // Rol Matrisi 2 için en azından temel işlemler tanımlı olsun
    if (typeof window.updateRolYetki2 !== 'function') {
        window.updateRolYetki2 = function(kullaniciId, yetkiKodu, aktif) {
            const checkbox = document.getElementById(`rol2_${kullaniciId}_${yetkiKodu}`);
            if (checkbox) checkbox.checked = aktif;

            return fetch('/api/rol-matrisi2/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ kullanici_id: kullaniciId, yetki_kodu: yetkiKodu, aktif })
            })
                .then(res => res.json())
                .then(data => {
                    if (!data || !data.success) {
                        if (checkbox) checkbox.checked = !aktif;
                        if (window.showToast) showToast('error', (data && data.message) || 'Kayıt başarısız');
                    } else {
                        if (window.showToast) showToast('success', data.message || 'Yetki güncellendi ve kaydedildi.');
                    }
                    return data;
                })
                .catch(err => {
                    if (checkbox) checkbox.checked = !aktif;
                    if (window.showToast) showToast('error', 'Bağlantı hatası: ' + err.message);
                });
        };
    }

    if (typeof window.renderRolMatrisi2 !== 'function') {
        window.renderRolMatrisi2 = function(data) {
            const content = document.getElementById('rol-matrisi2-content');
            if (!content) return;
            const kullanicilar = data.kullanicilar || [];
            const yetkiler = data.yetkiler || [];
            const kategoriler = data.yetki_kategorileri || [];
            if (!kullanicilar.length) {
                content.innerHTML = '<div class="alert alert-info">Gösterilecek kullanıcı yok.</div>';
                return;
            }
            let html = '<div class="table-responsive"><table class="table table-bordered table-sm"><thead><tr><th>Kullanıcı</th>';
            kategoriler.forEach(k => {
                (k.yetkiler || []).forEach(y => { html += `<th>${y.ad}</th>`; });
            });
            html += '</tr></thead><tbody>';
            kullanicilar.forEach(u => {
                const ad = (u.first_name && u.last_name) ? `${u.first_name} ${u.last_name}` : (u.username || '');
                html += `<tr><td>${ad} <small class="text-muted">${u.sistem_rol || ''}</small></td>`;
                kategoriler.forEach(k => {
                    (k.yetkiler || []).forEach(y => {
                        const kayit = yetkiler.find(r => r.kullanici_id === u.id && r.yetki_kodu === y.kod);
                        const isChecked = kayit ? kayit.aktif : (u.sistem_rol === 'admin');
                        const disabled = u.sistem_rol === 'admin' ? 'disabled' : '';
                        html += `<td class="text-center"><input type="checkbox" id="rol2_${u.id}_${y.kod}" ${isChecked ? 'checked' : ''} ${disabled} onchange="updateRolYetki2(${u.id}, '${y.kod}', this.checked)"></td>`;
                    });
                });
                html += '</tr>';
            });
            html += '</tbody></table></div>';
            content.innerHTML = html;
        };
    }

    if (typeof window.loadRolMatrisi2 !== 'function') {
        window.loadRolMatrisi2 = async function() {
            const loading = document.getElementById('rol-matrisi2-loading');
            const content = document.getElementById('rol-matrisi2-content');
            const error = document.getElementById('rol-matrisi2-error');
            if (loading) loading.style.display = 'block';
            if (content) content.style.display = 'none';
            if (error) error.style.display = 'none';
            try {
                const res = await fetch('/api/rol-matrisi2');
                const data = await res.json();
                if (!res.ok || !data.success) throw new Error(data.message || 'Rol matrisi 2 yüklenemedi');
                if (typeof window.renderRolMatrisi2 === 'function') window.renderRolMatrisi2(data);
                if (loading) loading.style.display = 'none';
                if (content) content.style.display = 'block';
            } catch (err) {
                console.error('Rol matrisi 2 fallback hatası:', err);
                if (loading) loading.style.display = 'none';
                if (error) error.style.display = 'block';
                if (window.showToast) showToast('error', err.message);
            }
        };
    }

    if (typeof window.saveRolMatrisi2 !== 'function') {
        window.saveRolMatrisi2 = function() {
            if (window.showToast) showToast('success', 'Yetki değişiklikleri kaydedildi ve tablo yenilendi.');
            window.loadRolMatrisi2?.();
        };
    }

    if (typeof window.filterKullanicilar2 !== 'function') {
        window.filterKullanicilar2 = function() {
            const arama = (document.getElementById('kullaniciArama2')?.value || '').toLowerCase();
            const rol = document.getElementById('rolFiltresi2')?.value || '';
            const kurum = document.getElementById('kurumFiltresi2')?.value || '';
            document.querySelectorAll('.kullanici-satir-2').forEach(satir => {
                const ad = satir.getAttribute('data-kullanici') || '';
                const satirRol = satir.getAttribute('data-rol') || '';
                const satirKurum = satir.getAttribute('data-kurum') || '';
                const uygun = (arama === '' || ad.includes(arama)) && (rol === '' || satirRol === rol) && (kurum === '' || satirKurum === kurum);
                satir.style.display = uygun ? '' : 'none';
            });
        };
    }

    if (typeof window.clearFiltreles2 !== 'function') {
        window.clearFiltreles2 = function() {
            const arama = document.getElementById('kullaniciArama2');
            const rol = document.getElementById('rolFiltresi2');
            const kurum = document.getElementById('kurumFiltresi2');
            if (arama) arama.value = '';
            if (rol) rol.value = '';
            if (kurum) kurum.value = '';
            window.filterKullanicilar2?.();
        };
    }

    if (typeof window.viewUser !== 'function') {
        window.viewUser = async function(userId) {
            try {
                const res = await fetch(`/api/admin/users/${userId}`);
                const data = await res.json();
                if (!res.ok || !data.success) throw new Error(data.message || 'Kullanıcı bilgisi alınamadı.');
                const user = data.data;
                window.currentDüzenleUserId = user.id;

                const photo = document.getElementById('viewUserPhoto');
                if (photo) photo.src = user.profile_photo || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.username)}&background=007bff&color=fff`;
                const setText = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
                setText('viewUserUsername', user.username);
                setText('viewUserEmail', user.email || '-');
                setText('viewUserId', user.id);
                setText('viewUserKurum', user.kurum_adi || '-');
                const roleBadge = document.getElementById('viewUserRoleBadge');
                if (roleBadge) {
                    const badge = safeBadge(user.sistem_rol || user.role);
                    roleBadge.textContent = user.role_display || badge.text;
                    roleBadge.className = 'badge ' + badge.class;
                }
                const proc = document.getElementById('viewUserProcesses');
                if (proc) {
                    if (user.process_roles && user.process_roles.length) {
                        const items = user.process_roles.map(pr => {
                            const badge = safeBadge(pr.rol);
                            const icon = pr.rol === 'surec_lideri' ? 'fa-crown text-warning' : 'fa-users text-primary';
                            return `<li class="list-group-item d-flex justify-content-between align-items-center">
                                        <div>
                                            <i class="fas ${icon} me-2"></i>${(pr.ad || '')}
                                            ${pr.kurum_adi ? `<span class="badge bg-light text-muted ms-2">${pr.kurum_adi}</span>` : ''}
                                        </div>
                                        <span class="badge ${badge.class}">${badge.text}</span>
                                    </li>`;
                        }).join('');
                        proc.innerHTML = `<div class="card border-0 bg-light"><div class="card-body p-0"><ul class="list-group list-group-flush">${items}</ul></div></div>`;
                    } else {
                        proc.innerHTML = '<p class="text-muted"><i class="fas fa-info-circle me-2"></i>Bu kullanıcıya atanmış süreç rolü yok.</p>';
                    }
                }
                new bootstrap.Modal(document.getElementById('viewUserModal')).show();
            } catch (err) {
                showToast('error', 'Kullanıcı bilgisi alınamadı: ' + err.message);
            }
        };
    }

    if (typeof window.editUser !== 'function') {
        window.editUser = async function(userId) {
            try {
                const res = await fetch(`/api/admin/users/${userId}`);
                const data = await res.json();
                if (!res.ok || !data.success) throw new Error(data.message || 'Kullanıcı bilgileri yüklenemedi');
                const user = data.data;
                window.currentDüzenleUserId = user.id;
                const setVal = (id, val = '') => { const el = document.getElementById(id); if (el) el.value = val; };
                setVal('editUserId', user.id);
                setVal('editUserUsername', user.username);
                setVal('editUserFirstAd', user.first_name || '');
                setVal('editUserLastAd', user.last_name || '');
                setVal('editUserEmail', user.email || '');
                setVal('editUserPassword', '');
                setVal('editUserProfilUrl', user.profile_photo || '');
                setVal('editUserKurum', user.kurum_id || '');
                const roleSel = document.getElementById('editUserRole');
                if (roleSel) roleSel.value = user.sistem_rol || user.role || '';
                const processSel = document.getElementById('editUserProcessRole');
                if (processSel) processSel.value = user.surec_rol || '';
                new bootstrap.Modal(document.getElementById('editUserModal')).show();
            } catch (err) {
                showToast('error', 'Hata: ' + err.message);
            }
        };
    }

    if (typeof window.editUserFromGörüntüle !== 'function') {
        window.editUserFromGörüntüle = function() {
            const modal = bootstrap.Modal.getInstance(document.getElementById('viewUserModal'));
            modal?.hide();
            if (window.currentDüzenleUserId) setTimeout(() => window.editUser(window.currentDüzenleUserId), 300);
        };
    }

    if (typeof window.updateUser !== 'function') {
        window.updateUser = function() {
            const id = window.currentDüzenleUserId || document.getElementById('editUserId')?.value;
            if (!id) { if (showToast) showToast('Güncellenecek kullanıcı yok', 'error'); return; }
            const systemRole = document.getElementById('editUserRole')?.value;
            const processRole = document.getElementById('editUserProcessRole')?.value;
            const body = {
                username: document.getElementById('editUserUsername')?.value?.trim(),
                first_name: document.getElementById('editUserFirstAd')?.value?.trim(),
                last_name: document.getElementById('editUserLastAd')?.value?.trim(),
                email: document.getElementById('editUserEmail')?.value?.trim(),
                password: document.getElementById('editUserPassword')?.value,
                role: systemRole,
                system_role: systemRole,
                process_role: processRole || null,
                kurum_id: document.getElementById('editUserKurum')?.value,
                profile_photo: document.getElementById('editUserProfilUrl')?.value?.trim()
            };
            if (!body.username || !body.email || !body.role || !body.kurum_id) {
                showToast('warning', 'Lütfen zorunlu alanları doldurun!');
                return;
            }
            return fetch(`/api/admin/users/update/${id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
                body: JSON.stringify(body)
            })
                .then(res => res.json().then(data => ({ res, data })))
                .then(({ res, data }) => {
                    if (!res.ok || !data.success) throw new Error(data.message || 'Güncelleme başarısız');
                    if (typeof showToast === 'function') showToast('Kullanıcı güncellendi', 'success');
                    const modal = bootstrap.Modal.getInstance(document.getElementById('editUserModal'));
                    modal?.hide();
                    setTimeout(() => location.reload(), 1200);
                    return data;
                })
                .catch(err => {
                    showToast('error', 'Hata: ' + err.message);
                });
        };
    }
    if (typeof window.saveUserChanges !== 'function') {
        window.saveUserChanges = () => window.updateUser();
    }

    if (typeof window.deleteUser !== 'function') {
        window.deleteUser = function(userId, username) {
            const ask = (typeof Swal !== 'undefined')
                ? Swal.fire({
                    title: 'Kullanıcı Sil',
                    text: `"${username}" kullanıcısını silmek istediğinize emin misiniz?`,
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#dc3545',
                    cancelButtonColor: '#6c757d',
                    confirmButtonText: 'Evet, Sil',
                    cancelButtonText: 'İptal'
                }).then(r => !!r.isConfirmed)
                : Promise.resolve(confirm(`"${username}" silinsin mi?`));

            return Promise.resolve(ask)
                .then(proceed => {
                    if (!proceed) return;
                    return fetch(`/api/admin/users/delete/${userId}`, {
                        method: 'DELETE',
                        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() }
                    })
                        .then(res => res.json().then(data => ({ res, data })))
                        .then(({ res, data }) => {
                            if (!res.ok) throw new Error((data && data.message) || 'Silme başarısız');
                            if (typeof showToast === 'function') showToast('Kullanıcı silindi', 'success');
                            setTimeout(() => location.reload(), 1000);
                            return data;
                        });
                })
                .catch(err => {
                    showToast('error', 'Hata: ' + err.message);
                });
        };
    }

})();
