/**
 * Performans Kartım — Bireysel Panel
 * Bireysel PG ve faaliyetleri yükler, gösterir.
 */
(function () {
    'use strict';

    const API = {
        performansKartim: null,
        kullaniciSurecleri: null
    };

    function init() {
        if (window.CONFIG) {
            API.performansKartim = window.CONFIG.apiPerformansKartim || '/process/api/performans-kartim';
            API.kullaniciSurecleri = window.CONFIG.apiKullaniciSurecleri || '/process/api/kullanici-surecleri';
        } else {
            API.performansKartim = '/process/api/performans-kartim';
            API.kullaniciSurecleri = '/process/api/kullanici-surecleri';
        }

        const yilSelect = document.getElementById('yilSelect');
        if (yilSelect) {
            yilSelect.addEventListener('change', loadData);
        }

        loadData();
    }

    function loadData() {
        const yilSelect = document.getElementById('yilSelect');
        const year = yilSelect ? parseInt(yilSelect.value, 10) : new Date().getFullYear();

        fetch(`${API.performansKartim}?year=${year}`, {
            method: 'GET',
            credentials: 'same-origin',
            headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data && data.success) {
                    renderPG(data.performans_gostergeleri || []);
                    renderFaaliyetler(data.faaliyetler || []);
                }
            })
            .catch(function (err) {
                console.error('Performans Kartım yükleme hatası:', err);
                if (typeof Swal !== 'undefined') {
                    Swal.fire({ icon: 'error', title: 'Hata', text: 'Veriler yüklenirken bir hata oluştu.' });
                }
            });
    }

    function renderPG(list) {
        const container = document.getElementById('pgList');
        const empty = document.getElementById('pgEmptyState');
        const countEl = document.getElementById('pgCount');

        if (!container || !empty) return;

        countEl && (countEl.textContent = list.length);

        if (list.length === 0) {
            empty.style.display = 'block';
            container.classList.remove('show');
            container.classList.add('initially-hidden');
            container.innerHTML = '';
            return;
        }

        empty.style.display = 'none';
        container.classList.remove('initially-hidden');
        container.classList.add('show');
        container.innerHTML = list.map(function (pg) {
            const entries = pg.entries || {};
            const cev1 = entries.ceyrek_1 || '-';
            const cev2 = entries.ceyrek_2 || '-';
            const cev3 = entries.ceyrek_3 || '-';
            const cev4 = entries.ceyrek_4 || '-';
            const yillik = entries.yillik_1 || '-';
            const src = pg.source === 'Süreç' && pg.source_process_name
                ? '<span class="badge bg-secondary">' + escapeHtml(pg.source_process_name) + '</span>'
                : '';
            const favIcon = pg.is_favorite
                ? '<i class="bi bi-star-fill text-warning ms-1" title="Favori"></i>'
                : '';
            return (
                '<div class="col-md-6 col-lg-4">' +
                '<div class="card pg-card h-100">' +
                '<div class="card-body">' +
                '<h6 class="card-title">' + escapeHtml(pg.name || '') + favIcon + ' ' + src + '</h6>' +
                '<p class="card-text small text-muted mb-2">Hedef: ' + escapeHtml(pg.target_value || '-') +
                (pg.unit ? ' ' + escapeHtml(pg.unit) : '') + '</p>' +
                '<table class="table table-sm table-bordered mb-0">' +
                '<thead><tr><th>Ç1</th><th>Ç2</th><th>Ç3</th><th>Ç4</th><th>Yıllık</th></tr></thead>' +
                '<tbody><tr><td>' + escapeHtml(String(cev1)) + '</td><td>' + escapeHtml(String(cev2)) +
                '</td><td>' + escapeHtml(String(cev3)) + '</td><td>' + escapeHtml(String(cev4)) +
                '</td><td>' + escapeHtml(String(yillik)) + '</td></tr></tbody></table>' +
                '</div></div></div>'
            );
        }).join('');
    }

    function renderFaaliyetler(list) {
        const container = document.getElementById('actList');
        const empty = document.getElementById('actEmptyState');
        const countEl = document.getElementById('actCount');

        if (!container || !empty) return;

        countEl && (countEl.textContent = list.length);

        if (list.length === 0) {
            empty.style.display = 'block';
            container.classList.remove('show');
            container.classList.add('initially-hidden');
            container.innerHTML = '';
            return;
        }

        empty.style.display = 'none';
        container.classList.remove('initially-hidden');
        container.classList.add('show');
        container.innerHTML = list.map(function (act) {
            const src = act.source === 'Süreç' && act.source_process_name
                ? '<span class="badge bg-secondary faaliyet-badge-surec">' + escapeHtml(act.source_process_name) + '</span>'
                : '';
            return (
                '<div class="list-group-item d-flex justify-content-between align-items-center">' +
                '<div>' +
                '<strong>' + escapeHtml(act.name || '') + '</strong> ' + src +
                '<br><small class="text-muted">' + escapeHtml(act.description || '') + '</small>' +
                '</div>' +
                '<span class="badge bg-' + (act.status === 'Tamamlandı' ? 'success' : 'primary') + '">' +
                escapeHtml(act.status || 'Planlandı') + '</span>' +
                '</div>'
            );
        }).join('');
    }

    function escapeHtml(s) {
        if (s == null) return '';
        const d = document.createElement('div');
        d.textContent = s;
        return d.innerHTML;
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
