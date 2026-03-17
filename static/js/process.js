/**
 * Process Management JS
 */

document.addEventListener('DOMContentLoaded', function () {
    const saveProcessBtn = document.getElementById('saveProcessBtn');
    if (saveProcessBtn) {
        saveProcessBtn.addEventListener('click', function () {
            const form = document.getElementById('addProcessForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            // Add parent_id if it exists in the URL (for sub-processes)
            const urlParams = new URLSearchParams(window.location.search);
            const parentId = urlParams.get('parent_id');
            if (parentId) data.parent_id = parentId;

            fetch('/process/api/add', {
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
                            title: 'Başarılı!',
                            text: result.message,
                            timer: 1500,
                            showConfirmButton: false
                        }).then(() => {
                            window.location.reload();
                        });
                    } else {
                        Swal.fire('Hata!', result.message, 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    Swal.fire('Hata!', 'Bir sorun oluştu.', 'error');
                });
        });
    }

    // KPI and Activity save buttons would go here if they are on the index page
    // For now, let's just implement the delete global function
});

function deleteProcess(id, name) {
    Swal.fire({
        title: 'Emin misiniz?',
        text: `"${name}" sürecini silmek istediğinize emin misiniz? Bu işlem geri alınamaz (ancak veriler arşivlenir).`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Evet, Sil!',
        cancelButtonText: 'Vazgeç'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/process/api/delete/${id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                }
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        Swal.fire('Silindi!', result.message, 'success').then(() => {
                            window.location.reload();
                        });
                    } else {
                        Swal.fire('Hata!', result.message, 'error');
                    }
                });
        }
    });
}
