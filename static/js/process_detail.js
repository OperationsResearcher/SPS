/**
 * Process Detail JS
 */

document.addEventListener('DOMContentLoaded', function () {
    // KPI Save
    const saveKpiBtn = document.getElementById('saveKpiBtn');
    if (saveKpiBtn) {
        saveKpiBtn.addEventListener('click', function () {
            const form = document.getElementById('addKpiForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            fetch('/process/api/kpi/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify(data)
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Eklendi!',
                            timer: 1000,
                            showConfirmButton: false
                        }).then(() => window.location.reload());
                    } else {
                        Swal.fire('Hata!', result.message, 'error');
                    }
                });
        });
    }

    // Activity Save
    const saveActivityBtn = document.getElementById('saveActivityBtn');
    if (saveActivityBtn) {
        saveActivityBtn.addEventListener('click', function () {
            const form = document.getElementById('addActivityForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            fetch('/process/api/activity/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify(data)
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Eklendi!',
                            timer: 1000,
                            showConfirmButton: false
                        }).then(() => window.location.reload());
                    } else {
                        Swal.fire('Hata!', result.message, 'error');
                    }
                });
        });
    }
});
