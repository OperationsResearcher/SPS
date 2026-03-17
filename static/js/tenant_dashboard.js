document.addEventListener("DOMContentLoaded", function () {
    // 1. Chart Rendering
    const chartContainer = document.getElementById("dashboardChartContainer");
    if (chartContainer) {
        try {
            const rawData = chartContainer.getAttribute("data-chart-data");
            const chartData = JSON.parse(rawData);

            const ctx = document.getElementById('tenantOverviewChart').getContext('2d');

            // Limit the chart so it looks good even if values are low
            let maxLimit = chartData.max_limit || 10;
            if (chartData.user_count > maxLimit) {
                maxLimit = chartData.user_count + 5;
            }

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Aktif Kullanıcılar', 'Açık Talepler', 'Maks. Kullanıcı Limiti'],
                    datasets: [{
                        label: 'Metrikler',
                        data: [chartData.user_count, chartData.active_tickets, maxLimit],
                        backgroundColor: [
                            'rgba(102, 126, 234, 0.8)',  // Primary
                            'rgba(240, 147, 251, 0.8)',  // Warning/Danger
                            'rgba(17, 153, 142, 0.8)'    // Success
                        ],
                        borderColor: [
                            'rgb(102, 126, 234)',
                            'rgb(240, 147, 251)',
                            'rgb(17, 153, 142)'
                        ],
                        borderWidth: 2,
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            padding: 10,
                            bodyFont: {
                                size: 14
                            },
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                borderDash: [5, 5],
                                color: 'rgba(0,0,0,0.05)'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    },
                    animation: {
                        duration: 1500,
                        easing: 'easeOutQuart'
                    }
                }
            });
        } catch (e) {
            console.error("Dashboard grafiği yüklenirken hata oluştu:", e);
        }
    }

    // 2. Card Collapse Toggle Functionality
    const collapseBtns = document.querySelectorAll(".collapse-btn");
    collapseBtns.forEach(btn => {
        btn.addEventListener("click", function () {
            const cardBody = this.closest(".card").querySelector(".card-body-collapsible");
            const icon = this.querySelector("i");

            if (cardBody.classList.contains("collapsed")) {
                cardBody.classList.remove("collapsed");
                icon.classList.remove("fa-chevron-down");
                icon.classList.add("fa-chevron-up");
            } else {
                cardBody.classList.add("collapsed");
                icon.classList.remove("fa-chevron-up");
                icon.classList.add("fa-chevron-down");
            }
        });
    });

    // 3. Tooltips Initialization
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // 4. Dynamic Strategy Modal Handling
    const editTriggers = document.querySelectorAll(".edit-trigger");
    const dynamicStrategyModal = document.getElementById("dynamicStrategyModal");
    let bsModal = null;

    if (dynamicStrategyModal) {
        bsModal = new bootstrap.Modal(dynamicStrategyModal);
    }

    editTriggers.forEach(trigger => {
        trigger.addEventListener("click", function () {
            const field = this.getAttribute("data-field");
            const title = this.getAttribute("data-title");

            const rawContentDiv = document.getElementById("raw-" + field);
            const rawValue = rawContentDiv ? rawContentDiv.textContent : "";

            document.getElementById("dsModalTitleText").innerText = title + ' Düzenle';
            document.getElementById("dsFieldName").value = field;
            document.getElementById("dsFieldValue").value = rawValue;

            if (bsModal) bsModal.show();

            // hide tooltip on click
            const tooltipInstance = bootstrap.Tooltip.getInstance(this);
            if (tooltipInstance) {
                tooltipInstance.hide();
            }
        });
    });

    const dsSaveBtn = document.getElementById("dsSaveBtn");
    if (dsSaveBtn) {
        dsSaveBtn.addEventListener("click", function () {
            const fieldName = document.getElementById("dsFieldName").value;
            const fieldValue = document.getElementById("dsFieldValue").value;

            const csrfTokenElement = document.querySelector('meta[name="csrf-token"]');
            const csrfToken = csrfTokenElement ? csrfTokenElement.getAttribute("content") : '';

            dsSaveBtn.disabled = true;
            dsSaveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Kaydediliyor...';

            fetch('/kurum-paneli/update-strategy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    field_name: fieldName,
                    field_value: fieldValue
                })
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        Swal.fire({
                            title: 'Başarılı!',
                            text: result.message,
                            icon: 'success',
                            confirmButtonText: 'Tamam'
                        }).then(() => {
                            window.location.reload();
                        });
                    } else {
                        Swal.fire({
                            title: 'Hata!',
                            text: result.message || 'Veriler kaydedilirken bir hata oluştu.',
                            icon: 'error',
                            confirmButtonText: 'Anladım'
                        });
                    }
                })
                .catch(error => {
                    console.error('Error saving strategy:', error);
                    Swal.fire({
                        title: 'Hata!',
                        text: 'Sunucuyla iletişim kurulurken bir hata oluştu.',
                        icon: 'error',
                        confirmButtonText: 'Anladım'
                    });
                })
                .finally(() => {
                    dsSaveBtn.disabled = false;
                    dsSaveBtn.innerHTML = '<i class="fas fa-save me-2"></i>Kaydet';
                });
        });
    }

    // 5. Strategy Planning Add/Edit Sub Strategy Modal
    const addSubStrategyModal = document.getElementById('addSubStrategyModal');
    if (addSubStrategyModal) {
        addSubStrategyModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const parentIdInput = document.getElementById('parentStrategyId');
            const editSubIdInput = document.getElementById('editSubStrategyId');
            const modalTitle = document.getElementById('addSubStrategyModalLabel');
            const subTitleInput = document.getElementById('subStrategyTitle');
            const subDescInput = document.getElementById('subStrategyDesc');
            if (button && button.classList.contains('add-sub-strategy-btn')) {
                const strategyId = button.getAttribute('data-strategy-id');
                if (parentIdInput) parentIdInput.value = strategyId || '';
                if (editSubIdInput) editSubIdInput.value = '';
                if (modalTitle) modalTitle.innerHTML = '<i class="fas fa-plus-circle me-2"></i>Alt Strateji Ekle';
                if (subTitleInput) subTitleInput.value = '';
                if (subDescInput) subDescInput.value = '';
            } else if (button && button.classList.contains('edit-sub-strategy-btn')) {
                const subId = button.getAttribute('data-sub-id');
                const subTitle = button.getAttribute('data-sub-title') || '';
                const subDesc = button.getAttribute('data-sub-description') || '';
                const strategyId = button.closest('[data-strategy-id]')?.getAttribute('data-strategy-id');
                if (parentIdInput) parentIdInput.value = strategyId || '';
                if (editSubIdInput) editSubIdInput.value = subId || '';
                if (modalTitle) modalTitle.innerHTML = '<i class="fas fa-edit me-2"></i>Alt Strateji Düzenle';
                if (subTitleInput) subTitleInput.value = subTitle;
                if (subDescInput) subDescInput.value = subDesc;
            }
        });
    }

    // Edit Sub Strategy - open modal and prefill
    document.querySelectorAll('.edit-sub-strategy-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const subId = this.getAttribute('data-sub-id');
            const subTitle = this.getAttribute('data-sub-title') || '';
            const subDesc = this.getAttribute('data-sub-description') || '';
            const strategyId = this.closest('[data-strategy-id]')?.getAttribute('data-strategy-id') || '';
            document.getElementById('parentStrategyId').value = strategyId;
            document.getElementById('editSubStrategyId').value = subId;
            document.getElementById('addSubStrategyModalLabel').innerHTML = '<i class="fas fa-edit me-2"></i>Alt Strateji Düzenle';
            document.getElementById('subStrategyTitle').value = subTitle;
            document.getElementById('subStrategyDesc').value = subDesc;
            new bootstrap.Modal(document.getElementById('addSubStrategyModal')).show();
        });
    });

    // Delete Sub Strategy
    document.querySelectorAll('.delete-sub-strategy-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const id = this.getAttribute('data-sub-id');
            const title = this.getAttribute('data-sub-title') || 'Alt Strateji';
            Swal.fire({
                title: 'Emin misiniz?',
                html: `"<strong>${title}</strong>" alt stratejisi silinecek.`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#dc3545',
                cancelButtonText: 'Vazgeç',
                confirmButtonText: 'Evet, Sil'
            }).then(result => {
                if (!result.isConfirmed) return;
                const csrf = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
                fetch(`/kurum-paneli/delete-sub-strategy/${id}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
                    body: JSON.stringify({})
                }).then(r => r.json()).then(res => {
                    if (res.success) Swal.fire('Silindi!', res.message, 'success').then(() => location.reload());
                    else Swal.fire('Hata!', res.message, 'error');
                }).catch(() => Swal.fire('Hata!', 'Bağlantı hatası', 'error'));
            });
        });
    });

    // Edit Main Strategy
    document.querySelectorAll('.edit-main-strategy-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            const id = this.getAttribute('data-strategy-id');
            const title = this.getAttribute('data-strategy-title') || '';
            const desc = this.getAttribute('data-strategy-description') || '';
            document.getElementById('editMainStrategyId').value = id;
            document.getElementById('editMainStrategyTitle').value = title;
            document.getElementById('editMainStrategyDesc').value = desc;
            new bootstrap.Modal(document.getElementById('editMainStrategyModal')).show();
        });
    });

    // Delete Main Strategy
    document.querySelectorAll('.delete-main-strategy-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            const id = this.getAttribute('data-strategy-id');
            const title = this.getAttribute('data-strategy-title') || 'Ana Strateji';
            Swal.fire({
                title: 'Emin misiniz?',
                html: `"<strong>${title}</strong>" ana stratejisi silinecek. Alt stratejiler de etkilenir.`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#dc3545',
                cancelButtonText: 'Vazgeç',
                confirmButtonText: 'Evet, Sil'
            }).then(result => {
                if (!result.isConfirmed) return;
                const csrf = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
                fetch(`/kurum-paneli/delete-main-strategy/${id}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
                    body: JSON.stringify({})
                }).then(r => r.json()).then(res => {
                    if (res.success) Swal.fire('Silindi!', res.message, 'success').then(() => location.reload());
                    else Swal.fire('Hata!', res.message, 'error');
                }).catch(() => Swal.fire('Hata!', 'Bağlantı hatası', 'error'));
            });
        });
    });

    // Save Edit Main Strategy
    const saveEditMainStrategyBtn = document.getElementById('saveEditMainStrategyBtn');
    if (saveEditMainStrategyBtn) {
        saveEditMainStrategyBtn.addEventListener('click', function () {
            const id = document.getElementById('editMainStrategyId').value;
            const title = document.getElementById('editMainStrategyTitle').value.trim();
            if (!title) {
                document.getElementById('editMainStrategyTitle').reportValidity();
                return;
            }
            const desc = document.getElementById('editMainStrategyDesc').value;
            const csrf = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
            saveEditMainStrategyBtn.disabled = true;
            saveEditMainStrategyBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Kaydediliyor...';
            fetch(`/kurum-paneli/update-main-strategy/${id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
                body: JSON.stringify({ title: title, description: desc })
            }).then(r => r.json()).then(res => {
                if (res.success) Swal.fire('Başarılı!', res.message, 'success').then(() => location.reload());
                else Swal.fire('Hata!', res.message, 'error');
            }).catch(() => Swal.fire('Hata!', 'Bağlantı hatası', 'error')).finally(() => {
                saveEditMainStrategyBtn.disabled = false;
                saveEditMainStrategyBtn.innerHTML = '<i class="fas fa-save me-2"></i>Kaydet';
            });
        });
    }

    // Save Main Strategy
    const saveMainStrategyBtn = document.getElementById('saveMainStrategyBtn');
    if (saveMainStrategyBtn) {
        saveMainStrategyBtn.addEventListener('click', function () {
            const form = document.getElementById('addMainStrategyForm');
            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }

            const title = document.getElementById('mainStrategyTitle').value;
            const desc = document.getElementById('mainStrategyDesc').value;
            const csrfTokenElement = document.querySelector('meta[name="csrf-token"]');
            const csrfToken = csrfTokenElement ? csrfTokenElement.getAttribute("content") : '';

            saveMainStrategyBtn.disabled = true;
            saveMainStrategyBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Kaydediliyor...';

            fetch('/kurum-paneli/add-strategy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    title: title,
                    description: desc
                })
            })
                .then(res => res.json())
                .then(result => {
                    if (result.success) {
                        Swal.fire('Başarılı!', result.message, 'success').then(() => window.location.reload());
                    } else {
                        Swal.fire('Hata!', result.message, 'error');
                    }
                })
                .catch(error => {
                    console.error(error);
                    Swal.fire('Hata!', 'Bağlantı hatası', 'error');
                })
                .finally(() => {
                    saveMainStrategyBtn.disabled = false;
                    saveMainStrategyBtn.innerHTML = '<i class="fas fa-save me-2"></i>Kaydet';
                });
        });
    }

    // Save Sub Strategy (Add or Update)
    const saveSubStrategyBtn = document.getElementById('saveSubStrategyBtn');
    if (saveSubStrategyBtn) {
        saveSubStrategyBtn.addEventListener('click', function () {
            const form = document.getElementById('addSubStrategyForm');
            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }

            const editSubId = document.getElementById('editSubStrategyId').value;
            const strategyId = document.getElementById('parentStrategyId').value;
            const title = document.getElementById('subStrategyTitle').value.trim();
            const desc = document.getElementById('subStrategyDesc').value;
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute("content") || '';

            saveSubStrategyBtn.disabled = true;
            saveSubStrategyBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Kaydediliyor...';

            const isEdit = editSubId && editSubId.length > 0;
            const url = isEdit ? `/kurum-paneli/update-sub-strategy/${editSubId}` : '/kurum-paneli/add-sub-strategy';
            const body = isEdit
                ? { title: title, description: desc }
                : { strategy_id: strategyId, title: title, description: desc };

            fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify(body)
            })
                .then(res => res.json())
                .then(result => {
                    if (result.success) {
                        Swal.fire('Başarılı!', result.message, 'success').then(() => window.location.reload());
                    } else {
                        Swal.fire('Hata!', result.message, 'error');
                    }
                })
                .catch(error => {
                    console.error(error);
                    Swal.fire('Hata!', 'Bağlantı hatası', 'error');
                })
                .finally(() => {
                    saveSubStrategyBtn.disabled = false;
                    saveSubStrategyBtn.innerHTML = '<i class="fas fa-save me-2"></i>Kaydet';
                });
        });
    }
});
