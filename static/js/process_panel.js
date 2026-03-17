/**
 * process_panel.js — Süreç Yönetim Paneli JS
 */

const CSRF = () => document.querySelector('meta[name="csrf-token"]')?.content || '';

function postJSON(url, data) {
    return fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF() },
        body: JSON.stringify(data)
    }).then(r => r.json());
}

/* ── Alt Strateji Satırları ───────────────────────── */
const STRATEGIES = () => window.KOKPIT_STRATEGIES || [];

function renderSubStrategyLinks(links) {
    const container = document.getElementById('ep_sub_strategy_links');
    if (!container) return;
    container.innerHTML = '';
    if (!links.length) {
        addSubStrategyRow(container, null, null, null);
        return;
    }
    links.forEach(l => {
        const strat = findStrategyBySubId(l.sub_strategy_id);
        const strategyId = strat ? strat.id : null;
        addSubStrategyRow(container, strategyId, l.sub_strategy_id, l.contribution_pct, false);
    });
    bindSubStrategyRowEvents();
}

function findSubStrategyById(id) {
    for (const s of STRATEGIES()) {
        const ss = (s.sub_strategies || []).find(x => x.id === id);
        if (ss) return { ...ss, strategy_id: s.id };
    }
    return null;
}

function findStrategyBySubId(subId) {
    return STRATEGIES().find(s => (s.sub_strategies || []).some(ss => ss.id === subId));
}

function addSubStrategyRow(container, strategyId, subStrategyId, contributionPct, bind = true) {
    if (!container) container = document.getElementById('ep_sub_strategy_links');
    const row = document.createElement('div');
    row.className = 'row g-2 mb-2 ep-sub-strategy-row align-items-end';
    const strategies = STRATEGIES();
    const strategy = strategies.find(s => s.id === strategyId) || strategies[0];
    const subStrategies = strategy ? (strategy.sub_strategies || []) : [];
    const selectedSub = subStrategies.find(ss => ss.id === subStrategyId) || (subStrategies[0] || null);

    row.innerHTML = `
        <div class="col-md-4">
            <label class="form-label small">Ana Strateji</label>
            <select class="form-select form-select-sm ep-strategy-select">
                ${strategies.map(s => `<option value="${s.id}" ${s.id == (strategy?.id) ? 'selected' : ''}>${(s.code || '')} ${(s.title || '').substring(0, 50)}</option>`).join('')}
            </select>
        </div>
        <div class="col-md-4">
            <label class="form-label small">Alt Strateji</label>
            <select class="form-select form-select-sm ep-sub-strategy-select">
                ${subStrategies.map(ss => `<option value="${ss.id}" ${ss.id == (selectedSub?.id) ? 'selected' : ''}>${(ss.code || '')} ${(ss.title || '').substring(0, 45)}</option>`).join('')}
            </select>
        </div>
        <div class="col-md-2">
            <label class="form-label small">Katkı %</label>
            <input type="number" class="form-control form-control-sm ep-contribution-input" min="0" max="100" step="0.5" placeholder="40" value="${contributionPct != null ? contributionPct : ''}">
        </div>
        <div class="col-md-2">
            <button type="button" class="btn btn-outline-danger btn-sm ep-remove-row" title="Kaldır"><i class="bi bi-trash"></i></button>
        </div>`;
    container.appendChild(row);
    if (bind) bindSubStrategyRowEvents();
}

function bindSubStrategyRowEvents() {
    document.querySelectorAll('.ep-strategy-select').forEach(sel => {
        sel.removeEventListener('change', onStrategyChange);
        sel.addEventListener('change', onStrategyChange);
    });
    document.querySelectorAll('.ep-remove-row').forEach(btn => {
        btn.removeEventListener('click', onRemoveRow);
        btn.addEventListener('click', onRemoveRow);
    });
}

function onStrategyChange(e) {
    const row = e.target.closest('.ep-sub-strategy-row');
    const subSel = row.querySelector('.ep-sub-strategy-select');
    const strategyId = parseInt(e.target.value);
    const strategy = STRATEGIES().find(s => s.id === strategyId);
    const subs = strategy ? (strategy.sub_strategies || []) : [];
    subSel.innerHTML = subs.map(ss => `<option value="${ss.id}">${(ss.code || '')} ${(ss.title || '').substring(0, 45)}</option>`).join('');
}

function onRemoveRow(e) {
    const row = e.target.closest('.ep-sub-strategy-row');
    const container = document.getElementById('ep_sub_strategy_links');
    if (container && container.querySelectorAll('.ep-sub-strategy-row').length > 1) {
        row.remove();
    }
}

function collectSubStrategyLinks() {
    const rows = document.querySelectorAll('.ep-sub-strategy-row');
    const links = [];
    rows.forEach(row => {
        const subId = row.querySelector('.ep-sub-strategy-select')?.value;
        const pct = row.querySelector('.ep-contribution-input')?.value?.trim();
        if (subId) {
            links.push({
                sub_strategy_id: parseInt(subId),
                contribution_pct: pct ? parseFloat(pct) : null
            });
        }
    });
    return links;
}

document.addEventListener('DOMContentLoaded', function () {
    const addBtn = document.getElementById('ep_add_sub_strategy_row');
    if (addBtn) {
        addBtn.addEventListener('click', function () {
            addSubStrategyRow(null, null, null, null, true);
        });
    }
});

/* ── Lider/Üye Transfer ─────────────────────────── */
function transferUsers(fromId, toId) {
    const fromEl = document.getElementById(fromId);
    const toEl = document.getElementById(toId);
    Array.from(fromEl.selectedOptions).forEach(opt => {
        // sadece hedefte yoksa ekle
        if (!Array.from(toEl.options).some(o => o.value === opt.value)) {
            toEl.appendChild(opt.cloneNode(true));
        }
        fromEl.removeChild(opt);
    });
}

/* ── Yeni Süreç ─────────────────────────── */
document.addEventListener('DOMContentLoaded', function () {
    const saveNewBtn = document.getElementById('saveNewProcessBtn');
    if (saveNewBtn) {
        saveNewBtn.addEventListener('click', function () {
            const leaderIds = Array.from(document.getElementById('np_lider_ids').options).map(o => o.value);
            const memberIds = Array.from(document.getElementById('np_uye_ids').options).map(o => o.value);

            const data = {
                name: document.getElementById('np_name').value.trim(),
                code: document.getElementById('np_code').value.trim(),
                status: document.getElementById('np_status').value,
                document_no: document.getElementById('np_document_no').value.trim(),
                revision_no: document.getElementById('np_revision_no').value.trim(),
                revision_date: document.getElementById('np_revision_date').value,
                first_publish_date: document.getElementById('np_first_publish_date').value,
                parent_id: document.getElementById('np_parent_id').value || null,
                start_boundary: document.getElementById('np_start_boundary').value,
                end_boundary: document.getElementById('np_end_boundary').value,
                description: document.getElementById('np_description').value,
                progress: document.getElementById('np_progress').value || 0,
                leader_ids: leaderIds,
                member_ids: memberIds,
            };

            if (!data.name) {
                Swal.fire('Uyarı!', 'Süreç adı zorunludur.', 'warning'); return;
            }

            postJSON('/process/api/add', data).then(res => {
                if (res.success) {
                    Swal.fire({ icon: 'success', title: 'Kaydedildi!', text: res.message, timer: 1200, showConfirmButton: false })
                        .then(() => location.reload());
                } else {
                    Swal.fire('Hata!', res.message, 'error');
                }
            });
        });
    }

    /* ── Düzenle Kaydet ─── */
    const saveEditBtn = document.getElementById('saveEditProcessBtn');
    if (saveEditBtn) {
        saveEditBtn.addEventListener('click', function () {
            const id = document.getElementById('ep_id').value;
            const leaderIds = Array.from(document.getElementById('ep_lider_ids').options).map(o => o.value);
            const memberIds = Array.from(document.getElementById('ep_uye_ids').options).map(o => o.value);
            const subStrategyLinks = collectSubStrategyLinks();

            const data = {
                name: document.getElementById('ep_name').value.trim(),
                code: document.getElementById('ep_code').value.trim(),
                status: document.getElementById('ep_status').value,
                document_no: document.getElementById('ep_document_no').value.trim(),
                revision_no: document.getElementById('ep_revision_no').value.trim(),
                revision_date: document.getElementById('ep_revision_date').value,
                first_publish_date: document.getElementById('ep_first_publish_date').value,
                parent_id: document.getElementById('ep_parent_id').value || null,
                start_boundary: document.getElementById('ep_start_boundary').value,
                end_boundary: document.getElementById('ep_end_boundary').value,
                description: document.getElementById('ep_description').value,
                progress: document.getElementById('ep_progress').value || 0,
                leader_ids: leaderIds,
                member_ids: memberIds,
                sub_strategy_links: subStrategyLinks,
            };

            postJSON(`/process/api/update/${id}`, data).then(res => {
                if (res.success) {
                    Swal.fire({ icon: 'success', title: 'Güncellendi!', timer: 1200, showConfirmButton: false })
                        .then(() => location.reload());
                } else {
                    Swal.fire('Hata!', res.message, 'error');
                }
            });
        });
    }
});

/* ── Görüntüle ─── */
function viewProcess(id) {
    const modal = new bootstrap.Modal(document.getElementById('viewProcessModal'));
    document.getElementById('viewProcessBody').innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary"></div></div>';
    modal.show();

    fetch(`/process/api/get/${id}`).then(r => r.json()).then(res => {
        if (!res.success) { document.getElementById('viewProcessBody').innerHTML = '<p class="text-danger">Yüklenemedi.</p>'; return; }
        const p = res.process;
        document.getElementById('view_process_title').textContent = p.name;
        document.getElementById('view_karne_btn').href = `/process/${id}/karne`;
        document.getElementById('viewProcessBody').innerHTML = `
            <div class="row g-3">
                <div class="col-md-6"><strong>Kod:</strong> ${p.code || '—'}</div>
                <div class="col-md-6"><strong>Durum:</strong> ${p.status || '—'}</div>
                <div class="col-md-6"><strong>Doküman No:</strong> ${p.document_no || '—'}</div>
                <div class="col-md-6"><strong>Revizyon No:</strong> ${p.revision_no || '—'}</div>
                <div class="col-md-6"><strong>Revizyon Tarihi:</strong> ${p.revision_date || '—'}</div>
                <div class="col-md-6"><strong>İlk Yayın:</strong> ${p.first_publish_date || '—'}</div>
                <div class="col-md-6"><strong>İlerleme:</strong> ${p.progress || 0}%</div>
                <div class="col-12"><strong>Açıklama:</strong> ${p.description || '—'}</div>
                <div class="col-md-6"><strong>Başlangıç Sınırı:</strong> ${p.start_boundary || '—'}</div>
                <div class="col-md-6"><strong>Bitiş Sınırı:</strong> ${p.end_boundary || '—'}</div>
            </div>`;
    });
}

/* ── Düzenle ─── */
function editProcess(id) {
    fetch(`/process/api/get/${id}`).then(r => r.json()).then(res => {
        if (!res.success) { Swal.fire('Hata!', 'Süreç bilgisi alınamadı.', 'error'); return; }
        const p = res.process;
        document.getElementById('ep_id').value = p.id;
        document.getElementById('ep_name').value = p.name;
        document.getElementById('ep_code').value = p.code || '';
        document.getElementById('ep_status').value = p.status || 'Aktif';
        document.getElementById('ep_document_no').value = p.document_no || '';
        document.getElementById('ep_revision_no').value = p.revision_no || '';
        document.getElementById('ep_revision_date').value = p.revision_date || '';
        document.getElementById('ep_first_publish_date').value = p.first_publish_date || '';
        document.getElementById('ep_parent_id').value = p.parent_id || '';
        document.getElementById('ep_start_boundary').value = p.start_boundary || '';
        document.getElementById('ep_end_boundary').value = p.end_boundary || '';
        document.getElementById('ep_description').value = p.description || '';
        document.getElementById('ep_progress').value = p.progress || 0;

        // Lider/üye listelerini temizle ve dolu olarak set et
        const lidirsTarget = document.getElementById('ep_lider_ids');
        const liderSource = document.getElementById('ep_lider_source');
        lidirsTarget.innerHTML = '';
        Array.from(liderSource.options).forEach(o => {
            if (p.leader_ids.includes(parseInt(o.value))) {
                lidirsTarget.appendChild(o.cloneNode(true));
            }
        });

        const uyeTarget = document.getElementById('ep_uye_ids');
        const uyeSource = document.getElementById('ep_uye_source');
        uyeTarget.innerHTML = '';
        Array.from(uyeSource.options).forEach(o => {
            if (p.member_ids.includes(parseInt(o.value))) {
                uyeTarget.appendChild(o.cloneNode(true));
            }
        });

        // Alt Stratejiler satırlarını doldur
        renderSubStrategyLinks(p.sub_strategy_links || []);

        new bootstrap.Modal(document.getElementById('editProcessModal')).show();
    });
}

/* ── Sil ─── */
function deleteProcess(id, name) {
    Swal.fire({
        title: 'Emin misiniz?',
        html: `<strong>"${name}"</strong> süreci silinecek.<br>Veriler arşivlenir.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Evet, Sil!',
        cancelButtonText: 'Vazgeç'
    }).then(result => {
        if (result.isConfirmed) {
            postJSON(`/process/api/delete/${id}`, {}).then(res => {
                if (res.success) {
                    Swal.fire({ icon: 'success', title: 'Silindi!', timer: 1000, showConfirmButton: false })
                        .then(() => location.reload());
                } else {
                    Swal.fire('Hata!', res.message, 'error');
                }
            });
        }
    });
}
