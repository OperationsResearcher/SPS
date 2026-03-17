document.addEventListener('DOMContentLoaded', function () {
    const viewButtons = document.querySelectorAll('.btn-view-ticket');
    const statusButtons = document.querySelectorAll('.btn-update-status');
    const btnSaveStatus = document.getElementById('btnSaveStatus');

    viewButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const ticketId = this.getAttribute('data-ticket-id');
            const modal = new bootstrap.Modal(document.getElementById('ticketViewModal'));
            const contentDiv = document.getElementById('ticketViewContent');

            contentDiv.innerHTML = '<div class="text-center my-5"><div class="spinner-border text-primary" role="status"></div></div>';
            modal.show();

            fetch(`/admin/kule-iletisim/${ticketId}/detail`)
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        const ticket = data.ticket;
                        let html = `
                            <div class="row">
                                <div class="col-md-6 mb-3"><strong>Kullanıcı:</strong> ${ticket.user_name}</div>
                                <div class="col-md-6 mb-3"><strong>Kurum:</strong> ${ticket.tenant_name}</div>
                                <div class="col-md-6 mb-3"><strong>Konu:</strong> <span class="badge bg-secondary">${ticket.subject}</span></div>
                                <div class="col-md-6 mb-3"><strong>Durum:</strong> ${ticket.status}</div>
                                <div class="col-md-6 mb-3"><strong>Sayfa:</strong> <a href="${ticket.page_url}" target="_blank">${ticket.page_url}</a></div>
                                <div class="col-md-12 mb-3"><strong>Mesaj:</strong> <div class="p-3 bg-light border rounded mt-2">${ticket.message}</div></div>
                        `;

                        if (ticket.screenshot_path) {
                            html += `
                                <div class="col-md-12 mb-3">
                                    <strong>Ekran Görüntüsü:</strong><br>
                                    <a href="/static/${ticket.screenshot_path}" target="_blank">
                                        <img src="/static/${ticket.screenshot_path}" class="img-fluid rounded mt-2 shadow" style="max-height: 400px;">
                                    </a>
                                </div>
                            `;
                        }

                        html += `</div>`;
                        contentDiv.innerHTML = html;
                    } else {
                        contentDiv.innerHTML = `<div class="alert alert-danger">${data.message || 'Bir hata oluştu.'}</div>`;
                    }
                })
                .catch(err => {
                    contentDiv.innerHTML = `<div class="alert alert-danger">Sunucu bağlantı hatası.</div>`;
                });
        });
    });

    statusButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const ticketId = this.getAttribute('data-ticket-id');
            const status = this.getAttribute('data-status');
            const note = this.getAttribute('data-admin-note');

            document.getElementById('updateTicketId').value = ticketId;
            document.getElementById('updateTicketStatus').value = status;
            document.getElementById('updateAdminNote').value = note;

            const modal = new bootstrap.Modal(document.getElementById('statusUpdateModal'));
            modal.show();
        });
    });

    if (btnSaveStatus) {
        btnSaveStatus.addEventListener('click', function () {
            const ticketId = document.getElementById('updateTicketId').value;
            const status = document.getElementById('updateTicketStatus').value;
            const adminNote = document.getElementById('updateAdminNote').value;

            btnSaveStatus.disabled = true;
            btnSaveStatus.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Güncelleniyor...';

            fetch(`/admin/kule-iletisim/${ticketId}/update`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    status: status,
                    admin_note: adminNote
                })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Başarılı',
                            text: 'Durum güncellendi.'
                        }).then(() => {
                            window.location.reload();
                        });
                    } else {
                        Swal.fire('Hata', data.message, 'error');
                    }
                })
                .catch(err => {
                    Swal.fire('Hata', 'İşlem başarısız.', 'error');
                })
                .finally(() => {
                    btnSaveStatus.disabled = false;
                    btnSaveStatus.innerHTML = 'Kaydet';
                });
        });
    }
});
