/**
 * process_karne.js — Süreç Karnesi JS (Modüler Yapı)
 * api.js ve calculations.js modüllerini kullanır.
 */
import { postJSON } from './modules/process_karne/api.js';
import { hesaplaBasariPuani } from './modules/process_karne/calculations.js';


/* ── State ───────────────────────────── */
const container = document.querySelector('[data-process-id]');
let currentProcessId = container ? parseInt(container.dataset.processId) : null;
let currentYear = container ? parseInt(container.dataset.currentYear) : new Date().getFullYear();
let currentPeriyot = 'ceyrek';
let currentOffset = 0;
let trendChart = null;
let kpiChart = null;
let isFirstKarneLoad = true;

/* ── Init ────────────────────────────── */
document.addEventListener('DOMContentLoaded', function () {

    const yilSel = document.getElementById('yilSelect');
    if (yilSel) {
        currentYear = parseInt(yilSel.value);
        yilSel.addEventListener('change', function () {
            currentYear = parseInt(this.value);
            currentOffset = 0;
            const yilBil = document.getElementById('yilBilgisi');
            if (yilBil) yilBil.textContent = currentYear;
            updatePeriyotLabel();
            loadKarneData();
        });
    }

    const surecSel = document.getElementById('surecSelect');
    if (surecSel) {
        surecSel.addEventListener('change', function () {
            if (this.value) window.location.href = `/process/${this.value}/karne`;
        });
    }

    const periyotSel = document.getElementById('periyotSelect');
    if (periyotSel) {
        currentPeriyot = periyotSel.value;
        periyotSel.addEventListener('change', function () {
            currentPeriyot = this.value;
            currentOffset = 0;
            updatePeriyotLabel();
            loadKarneData();
        });
    }

    // Veri giriş sihirbazı
    const wizBtn = document.getElementById('openDataEntryWizardBtn');
    if (wizBtn) {
        wizBtn.addEventListener('click', () => {
            const wYil = document.getElementById('wiz_yil');
            if (wYil) wYil.value = currentYear;
            new bootstrap.Modal(document.getElementById('dataEntryWizardModal')).show();
        });
    }

    // Wizard: süreç değişince PG'leri yükle
    const wizSurec = document.getElementById('wiz_surec');
    if (wizSurec) {
        wizSurec.addEventListener('change', function () { loadWizardPGs(this.value); });
        if (currentProcessId) loadWizardPGs(currentProcessId);
    }

    // Wizard: periyot tipi
    const wizPeriyot = document.getElementById('wiz_periyot_tipi');
    if (wizPeriyot) wizPeriyot.addEventListener('change', updateWizardPeriodHelp);

    // Wizard Kaydet
    const wizSaveBtn = document.getElementById('wizSaveBtn');
    if (wizSaveBtn) wizSaveBtn.addEventListener('click', saveWizardData);

    // PG Kaydet
    const savePGBtn = document.getElementById('savePGBtn');
    if (savePGBtn) savePGBtn.addEventListener('click', savePG);

    // PG Güncelle
    const updatePGBtn = document.getElementById('updatePGBtn');
    if (updatePGBtn) updatePGBtn.addEventListener('click', updatePG);

    // Faaliyet Kaydet
    const saveFaaliyetBtn = document.getElementById('saveFaaliyetBtn');
    if (saveFaaliyetBtn) saveFaaliyetBtn.addEventListener('click', saveFaaliyet);

    // Faaliyet Güncelle
    const updateFaaliyetBtn = document.getElementById('updateFaaliyetBtn');
    if (updateFaaliyetBtn) updateFaaliyetBtn.addEventListener('click', updateFaaliyet);

    // Excel Export
    const exportBtn = document.getElementById('exportExcelBtn');
    if (exportBtn) exportBtn.addEventListener('click', exportToExcel);

    // Favori KPI toggle
    document.body.addEventListener('click', function (e) {
        const btn = e.target.closest('.favori-kpi-btn');
        if (btn) {
            e.preventDefault();
            toggleFavoriteKpi(btn);
        }
    });

    // Veri Detay modal kapandığında orphan backdrop/body sınıflarını temizle (hayalet overlay önlemi)
    const veriDetayModalEl = document.getElementById('veriDetayModal');
    if (veriDetayModalEl) {
        veriDetayModalEl.addEventListener('hidden.bs.modal', function () {
            document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
        });
    }

    // Veri Düzenle modal: Kaydet butonu
    const veriDuzenleSaveBtn = document.getElementById('veriDuzenleSaveBtn');
    if (veriDuzenleSaveBtn) {
        veriDuzenleSaveBtn.addEventListener('click', function () {
            const editModalEl = document.getElementById('veriDuzenleModal');
            const actualInput = document.getElementById('veriDuzenleActual');
            const descInput = document.getElementById('veriDuzenleDesc');
            const entryId = editModalEl && editModalEl.dataset.editEntryId ? parseInt(editModalEl.dataset.editEntryId) : 0;
            const kpiId = editModalEl && editModalEl.dataset.editKpiId ? editModalEl.dataset.editKpiId : '';
            const periodKey = editModalEl && editModalEl.dataset.editPeriodKey || '';
            if (!entryId || !kpiId) return;
            const actualValue = actualInput ? actualInput.value.trim() : '';
            const description = descInput ? descInput.value.trim() : '';
            if (!actualValue) {
                if (typeof Swal !== 'undefined') Swal.fire('Uyarı', 'Gerçekleşen değer zorunludur.', 'warning');
                return;
            }
            veriDuzenleSaveBtn.disabled = true;
            postJSON(`/process/api/kpi-data/update/${entryId}`, { actual_value: actualValue, description })
                .then(res => {
                    veriDuzenleSaveBtn.disabled = false;
                    if (res.success) {
                        bootstrap.Modal.getInstance(editModalEl).hide();
                        if (typeof Swal !== 'undefined') Swal.fire({ icon: 'success', title: 'Güncellendi!', timer: 1000, showConfirmButton: false });
                        loadVeriDetayContent(parseInt(kpiId), periodKey);
                        loadKarneData();
                    } else {
                        if (typeof Swal !== 'undefined') Swal.fire('Hata!', res.message || 'Güncelleme başarısız.', 'error');
                    }
                })
                .catch(() => {
                    veriDuzenleSaveBtn.disabled = false;
                    if (typeof Swal !== 'undefined') Swal.fire('Hata!', 'Güncelleme sırasında bir hata oluştu.', 'error');
                });
        });
    }

    // Bugünün tarihi
    const wizTarih = document.getElementById('wiz_tarih');
    if (wizTarih) wizTarih.value = new Date().toISOString().split('T')[0];

    updatePeriyotLabel();
    if (currentProcessId) loadKarneData();

    // Kart durumlarını localStorage'dan oku ve uygula
    const CARD_IDS = ['saglikSkoruBody', 'trendAnalizBody', 'pgTabloBody', 'faaliyetBody'];
    const CARD_ORDER_IDS = ['saglikSkoruCard', 'trendAnalizCard', 'pgTabloCard', 'faaliyetCard'];
    const storageKey = 'karne-card-states' + (currentProcessId ? '-' + currentProcessId : '');
    const orderStorageKey = 'karne-card-order' + (currentProcessId ? '-' + currentProcessId : '');
    let savedStates = {};
    try {
        savedStates = JSON.parse(localStorage.getItem(storageKey) || '{}');
    } catch (e) { /* ignore */ }

    CARD_IDS.forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        const shouldShow = savedStates[id] !== false;
        if (!shouldShow) {
            el.classList.remove('show');
        }
    });

    // Kart sırasını localStorage'dan uygula
    const container = document.getElementById('karneCardsContainer');
    if (container && typeof Sortable !== 'undefined') {
        let savedOrder = [];
        try {
            savedOrder = JSON.parse(localStorage.getItem(orderStorageKey) || '[]');
        } catch (e) { /* ignore */ }
        if (Array.isArray(savedOrder) && savedOrder.length === CARD_ORDER_IDS.length) {
            const cards = Array.from(container.querySelectorAll('.karne-draggable-card'));
            const byId = {};
            cards.forEach(c => { const id = c.dataset.cardId; if (id) byId[id] = c; });
            savedOrder.forEach(cardId => {
                const card = byId[cardId];
                if (card) container.appendChild(card);
            });
        }
        new Sortable(container, {
            handle: '.karne-drag-handle',
            filter: '.modal',
            animation: 200,
            ghostClass: 'karne-sortable-ghost',
            onEnd: function () {
                const ids = Array.from(container.querySelectorAll('.karne-draggable-card'))
                    .map(c => c.dataset.cardId).filter(Boolean);
                try {
                    localStorage.setItem(orderStorageKey, JSON.stringify(ids));
                } catch (e) { /* ignore */ }
            }
        });
    }

    // Tooltip'leri etkinleştir
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
        new bootstrap.Tooltip(el);
    });

    // Kart küçültme ikonlarını güncelle (chevron) + durumu kaydet
    function saveKarneCardStates() {
        const state = {};
        CARD_IDS.forEach(id => {
            const el = document.getElementById(id);
            if (el) state[id] = el.classList.contains('show');
        });
        try {
            localStorage.setItem(storageKey, JSON.stringify(state));
        } catch (e) { /* ignore */ }
    }

    document.querySelectorAll('.karne-collapse-icon').forEach(icon => {
        const targetId = icon.getAttribute('data-bs-target');
        if (!targetId) return;
        const target = document.querySelector(targetId);
        if (!target) return;
        if (target.classList.contains('show')) {
            icon.classList.remove('bi-chevron-down');
            icon.classList.add('bi-chevron-up');
        }
        target.addEventListener('show.bs.collapse', () => {
            icon.classList.remove('bi-chevron-down');
            icon.classList.add('bi-chevron-up');
            saveKarneCardStates();
        });
        target.addEventListener('hide.bs.collapse', () => {
            icon.classList.remove('bi-chevron-up');
            icon.classList.add('bi-chevron-down');
            saveKarneCardStates();
        });
    });
});

/* ── Wizard: PG yükle ──────────────── */
function loadWizardPGs(processId) {
    if (!processId) return;
    fetch(`/process/api/kpi/list/${processId}`)
        .then(r => r.json())
        .then(res => {
            const sel = document.getElementById('wiz_pg');
            if (!sel) return;
            sel.innerHTML = '<option value="">-- PG Seçiniz --</option>';
            (res.kpis || []).forEach(k => {
                const opt = document.createElement('option');
                opt.value = k.id;
                opt.textContent = `${k.code || ''} ${k.name}`;
                opt.dataset.period = k.period || '';
                sel.appendChild(opt);
            });
        });
}

/* ── Wizard: Periyot bilgisi ─────────── */
function updateWizardPeriodHelp() {
    const pt = document.getElementById('wiz_periyot_tipi').value;
    const noSel = document.getElementById('wiz_period_no');
    const ayContainer = document.getElementById('wiz_ay_container');
    if (!noSel) return;
    noSel.innerHTML = '';
    if (ayContainer) ayContainer.style.display = 'none';
    if (pt === 'yillik' || pt === '') {
        noSel.innerHTML = '<option value="1">Yıl (1)</option>';
    } else if (pt === 'ceyrek') {
        ['I. Çeyrek (1)', 'II. Çeyrek (2)', 'III. Çeyrek (3)', 'IV. Çeyrek (4)'].forEach((lbl, i) => {
            const opt = document.createElement('option');
            opt.value = i + 1; opt.textContent = lbl; noSel.appendChild(opt);
        });
    } else if (pt === 'aylik') {
        const aylar = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'];
        aylar.forEach((lbl, i) => {
            const opt = document.createElement('option');
            opt.value = i + 1; opt.textContent = `${lbl} (${i + 1})`; noSel.appendChild(opt);
        });
    } else if (pt === 'haftalik') {
        if (ayContainer) ayContainer.style.display = 'block';
        for (let i = 1; i <= 5; i++) {
            const opt = document.createElement('option');
            opt.value = i; opt.textContent = `Hafta ${i}`; noSel.appendChild(opt);
        }
    } else if (pt === 'gunluk') {
        if (ayContainer) ayContainer.style.display = 'block';
        for (let i = 1; i <= 31; i++) {
            const opt = document.createElement('option');
            opt.value = i; opt.textContent = `Gün ${i}`; noSel.appendChild(opt);
        }
    }
}

/* ── Wizard Kaydet ──────────────────── */
function saveWizardData() {
    const pgId = document.getElementById('wiz_pg').value;
    const deger = document.getElementById('wiz_deger').value.trim();
    if (!pgId || !deger) {
        Swal.fire('Uyarı', 'PG ve Gerçekleşen Değer zorunludur.', 'warning');
        return;
    }

    let periodType = document.getElementById('wiz_periyot_tipi').value;
    if (!periodType) {
        const pgOpt = document.getElementById('wiz_pg').options[document.getElementById('wiz_pg').selectedIndex];
        const pgPeriyot = (pgOpt?.dataset?.period || '').toLowerCase();
        if (pgPeriyot.includes('yıllık') || pgPeriyot.includes('yillik')) periodType = 'yillik';
        else if (pgPeriyot.includes('çeyrek')) periodType = 'ceyrek';
        else if (pgPeriyot.includes('aylık') || pgPeriyot.includes('aylik')) periodType = 'aylik';
        else periodType = 'yillik';
    }

    const periodNo = parseInt(document.getElementById('wiz_period_no').value) || 1;
    const data = {
        kpi_id: pgId,
        year: parseInt(document.getElementById('wiz_yil').value),
        period_type: periodType,
        period_no: periodNo,
        actual_value: deger,
        data_date: document.getElementById('wiz_tarih').value || new Date().toISOString().split('T')[0],
        description: document.getElementById('wiz_aciklama').value,
    };
    if ((periodType === 'haftalik' || periodType === 'gunluk') && document.getElementById('wiz_ay_container')?.style.display !== 'none') {
        const aySel = document.getElementById('wiz_ay_select');
        if (aySel) data.period_month = parseInt(aySel.value) || 1;
    }

    postJSON('/process/api/kpi-data/add', data).then(res => {
        if (res.success) {
            Swal.fire({ icon: 'success', title: 'Kaydedildi!', timer: 1500, showConfirmButton: false });
            bootstrap.Modal.getInstance(document.getElementById('dataEntryWizardModal'))?.hide();
            if (data.year !== currentYear) {
                currentYear = data.year;
                const yilSel = document.getElementById('yilSelect');
                if (yilSel) yilSel.value = currentYear;
                const yilBil = document.getElementById('yilBilgisi');
                if (yilBil) yilBil.textContent = currentYear;
            }
            loadKarneData();
        } else {
            Swal.fire('Hata!', res.message, 'error');
        }
    });
}

/* ── Görüntülenen Periyot (Önceki/Sonraki ile) ─── */
function getViewedYear() {
    if (currentPeriyot === 'gunluk') {
        const d = new Date(currentYear || new Date().getFullYear(), 0, 1);
        d.setMonth(d.getMonth() + currentOffset);
        return d.getFullYear();
    }
    return (currentYear || new Date().getFullYear()) + currentOffset;
}

function getViewedMonth() {
    if (currentPeriyot !== 'gunluk') return null;
    const d = new Date(currentYear || new Date().getFullYear(), 0, 1);
    d.setMonth(d.getMonth() + currentOffset);
    return d.getMonth() + 1;
}

/* ── Karne Verisi Yükle ──────────────── */
function loadKarneData() {
    if (!currentProcessId) return;
    const viewedYear = getViewedYear();
    let url = `/process/api/karne/${currentProcessId}?year=${viewedYear}`;
    fetch(url)
        .then(r => r.json())
        .then(res => {
            if (!res.success) return;
            updateSkorPanel(res.kpis);
            updateYoneticiOzeti(res.kpis);
            updateTrendChart(res.kpis);
            rebuildPGTableByPeriyot(res.kpis, res.favorite_kpi_ids || []);
            updateActivityTracks(res.activities || []);
            // Yıl/Gösterim değişince (ilk yükleme hariç) PG kartını aç — ilk yüklemede localStorage durumu geçerli
            if (!isFirstKarneLoad) expandPGCardAndScroll();
            isFirstKarneLoad = false;
        })
        .catch(err => console.error('Karne data load error:', err));
}

/** Yıl veya Gösterim değişince PG kartını genişlet; kapalıysa scroll yap */
function expandPGCardAndScroll() {
    const pgBody = document.getElementById('pgTabloBody');
    if (!pgBody) return;
    const wasCollapsed = !pgBody.classList.contains('show');
    const bsCollapse = bootstrap.Collapse.getInstance(pgBody) || new bootstrap.Collapse(pgBody, { toggle: false });
    bsCollapse.show();
    if (wasCollapsed) {
        const pgCard = pgBody.closest('.card');
        if (pgCard) pgCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

/* ── Skor Paneli ─────────────────────── */
function updateSkorPanel(kpis) {
    const total = kpis.length;
    const totalEl = document.getElementById('totalKPICount');
    if (totalEl) totalEl.textContent = total;

    let success = 0, risk = 0;
    let totalPct = 0;
    kpis.forEach(k => {
        const entries = k.entries || {};
        const entryCount = Object.keys(entries).length;

        if (entryCount > 0 && k.target_value) {
            const target = parseFloat(k.target_value);
            const vals = Object.values(entries).map(v => parseFloat(v)).filter(v => !isNaN(v));
            if (vals.length && !isNaN(target) && target > 0) {
                const avg = vals.reduce((a, b) => a + b, 0) / vals.length;
                const pct = (avg / target) * 100;
                if (pct >= 100) success++;
                else if (pct >= 70) risk++;
                else risk++;
                totalPct += Math.min(pct, 120);
            } else { success++; } // veri var ama sayısal değil
        } else if (entryCount > 0) {
            success++;
        } else {
            risk++;
        }
    });

    const succEl = document.getElementById('successKPICount');
    if (succEl) succEl.textContent = success;
    const riskEl = document.getElementById('riskKPICount');
    if (riskEl) riskEl.textContent = risk;

    const pct = total > 0 ? Math.round((success / total) * 100) : 0;
    const pgHedefText = document.getElementById('pgHedefText');
    if (pgHedefText) pgHedefText.textContent = pct + '%';
    const pgHedefBar = document.getElementById('pgHedefBar');
    if (pgHedefBar) pgHedefBar.style.width = pct + '%';
    const gaugeVal = document.getElementById('gaugeValue');
    if (gaugeVal) gaugeVal.textContent = pct;

    const durumEl = document.getElementById('saglikSkoruDurum');
    if (durumEl) {
        let durum = 'Veri Bekleniyor';
        if (total === 0) durum = 'PG Eklenmemiş';
        else if (pct >= 90) durum = '🟢 Mükemmel';
        else if (pct >= 70) durum = '🟢 İyi';
        else if (pct >= 50) durum = '🟡 Orta';
        else if (pct >= 25) durum = '🟠 Dikkat';
        else if (pct > 0) durum = '🔴 Kritik';
        durumEl.textContent = durum;
    }

    drawGauge(pct);
    drawKpiPieChart(success, risk);
}

/* ── Yönetici Özeti Kartı ───────────────── */
function updateYoneticiOzeti(kpis) {
    const container = document.getElementById('yoneticiOzetiContent');
    if (!container) return;

    if (!kpis || kpis.length === 0) {
        container.innerHTML = '<div class="yonetici-ozeti-empty-msg"><i class="bi bi-inbox"></i><p class="mt-2 mb-0">Henüz performans göstergesi eklenmemiş. PG Ekle ile ekleyebilirsiniz.</p></div>';
        return;
    }

    const items = kpis.map(k => {
        const entries = k.entries || {};
        const allVals = Object.values(entries).map(v => parseFloat(v)).filter(v => !isNaN(v));
        const hesaplamaYontemi = k.data_collection_method || 'Ortalama';
        const olcumPeriyodu = k.period || '';
        const yillikHedef = computeYillikHedef(k.target_value, olcumPeriyodu, hesaplamaYontemi);
        const skorTarget = yillikHedef !== null ? yillikHedef : parseFloat(k.target_value);
        const entryCount = Object.keys(entries).filter(kk => entries[kk] !== '' && entries[kk] != null).length;
        const totalPeriodKeys = Object.keys(entries).length;

        let pct = null;
        let skorDisplay = '—';
        let compareValDisplay = null;
        let targetDisplay = (k.target_value != null && k.target_value !== '') ? String(k.target_value) : '—';

        if (allVals.length > 0 && !isNaN(skorTarget) && skorTarget > 0) {
            const compareVal = (hesaplamaYontemi === 'Toplama' || hesaplamaYontemi === 'Toplam')
                ? allVals.reduce((a, b) => a + b, 0)
                : allVals[allVals.length - 1];
            compareValDisplay = Number.isInteger(compareVal) ? compareVal : compareVal.toFixed(2);
            pct = Math.round((compareVal / skorTarget) * 100);
            if (k.direction === 'Decreasing') pct = compareVal > 0 ? Math.round((skorTarget / compareVal) * 100) : 0;

            let basariAraliklari = null;
            try {
                basariAraliklari = k.basari_puani_araliklari ? (typeof k.basari_puani_araliklari === 'string' ? JSON.parse(k.basari_puani_araliklari) : k.basari_puani_araliklari) : null;
            } catch (e) { basariAraliklari = null; }

            if (basariAraliklari) {
                const puan = hesaplaBasariPuani(pct, basariAraliklari);
                skorDisplay = puan !== null ? `${puan}/5` : `%${pct}`;
            } else {
                skorDisplay = `%${pct}`;
            }
        }

        let durumClass = 'yonetici-ozeti-veri-yok';
        let durumBadgeClass = 'durum-veri-yok';
        let durumLabel = 'Veri Yok';
        let skorClass = 'text-secondary';
        let progressPct = 0;

        if (pct !== null) {
            progressPct = Math.min(pct, 100);
            if (pct >= 100) {
                durumClass = 'yonetici-ozeti-iyi';
                durumBadgeClass = 'durum-iyi';
                durumLabel = 'Hedef Üzeri';
                skorClass = 'text-success';
            } else if (pct >= 80) {
                durumClass = 'yonetici-ozeti-dikkat';
                durumBadgeClass = 'durum-dikkat';
                durumLabel = 'Dikkat';
                skorClass = 'text-warning';
            } else {
                durumClass = 'yonetici-ozeti-kritik';
                durumBadgeClass = 'durum-kritik';
                durumLabel = 'Kritik';
                skorClass = 'text-danger';
            }
        }

        const metaParts = [];
        if (k.unit) metaParts.push(`Birim: ${k.unit}`);
        metaParts.push(`Ölçüm: ${olcumPeriyodu || '-'}`);
        if (entryCount > 0) metaParts.push(`${entryCount} periyotta veri`);
        const meta = metaParts.join(' · ');

        const progressColor = progressPct >= 100 ? '#198754' : progressPct >= 80 ? '#ffc107' : '#dc3545';

        return `<div class="yonetici-ozeti-item ${durumClass}" data-kpi-id="${k.id}">
            <div class="yonetici-ozeti-main">
                <div class="yonetici-ozeti-code">${(k.code || '').replace(/</g, '&lt;')}</div>
                <div class="yonetici-ozeti-name">${(k.name || '-').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</div>
                <div class="yonetici-ozeti-meta">${meta}</div>
                ${compareValDisplay !== null ? `<div class="yonetici-ozeti-meta mt-1"><strong>Hedef:</strong> ${targetDisplay} ${hesaplamaYontemi === 'Toplama' || hesaplamaYontemi === 'Toplam' ? '(yıllık ' + (yillikHedef != null ? (Number.isInteger(yillikHedef) ? yillikHedef : yillikHedef.toFixed(2)) : '-') + ')' : ''} &nbsp;|&nbsp; <strong>Gerçekleşen:</strong> ${compareValDisplay}</div>` : ''}
            </div>
            <div class="yonetici-ozeti-stats">
                ${pct !== null ? `<div class="yonetici-ozeti-progress" title="Hedef tutma: %${pct}"><div class="yonetici-ozeti-progress-bar" style="width:${progressPct}%; background:${progressColor};"></div></div>` : ''}
                <div class="yonetici-ozeti-skor ${skorClass}">${skorDisplay}</div>
                <span class="yonetici-ozeti-durum ${durumBadgeClass}">${durumLabel}</span>
            </div>
        </div>`;
    });

    container.innerHTML = items.join('');
}

/* ── Gauge Canvas ─────────────────────── */
function drawGauge(pct) {
    const canvas = document.getElementById('gaugeChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width, h = canvas.height;
    const cx = w / 2, cy = h / 2, r = Math.min(w, h) / 2 - 10;
    ctx.clearRect(0, 0, w, h);
    ctx.beginPath();
    ctx.arc(cx, cy, r, Math.PI, 2 * Math.PI);
    ctx.lineWidth = 18; ctx.strokeStyle = '#e9ecef'; ctx.stroke();
    const color = pct >= 80 ? '#198754' : pct >= 60 ? '#ffc107' : pct >= 40 ? '#fd7e14' : '#dc3545';
    ctx.beginPath();
    ctx.arc(cx, cy, r, Math.PI, Math.PI + (Math.PI * pct / 100));
    ctx.lineWidth = 18; ctx.strokeStyle = color; ctx.lineCap = 'round'; ctx.stroke();
}

/* ── KPI Pie Chart ─────────────────── */
function drawKpiPieChart(success, risk) {
    const ctx = document.getElementById('kpiStatusChart')?.getContext('2d');
    if (!ctx) return;
    if (kpiChart) kpiChart.destroy();
    kpiChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Veri Girilmiş', 'Veri Bekleniyor'],
            datasets: [{ data: [success, risk], backgroundColor: ['#198754', '#ffc107'], borderWidth: 2 }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { boxWidth: 12 } } } }
    });
}

/* ── Trend Chart ─────────────────────── */
function updateTrendChart(kpis) {
    const ctx = document.getElementById('trendChart')?.getContext('2d');
    if (!ctx) return;
    if (trendChart) trendChart.destroy();
    const labels = ['I. Çeyrek', 'II. Çeyrek', 'III. Çeyrek', 'IV. Çeyrek'];
    const data = [0, 0, 0, 0];
    kpis.forEach(k => {
        for (let q = 1; q <= 4; q++) {
            const val = k.entries[`ceyrek_${q}`];
            if (val !== undefined && val !== null && val !== '') data[q - 1]++;
        }
    });
    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Veri Girilen PG Sayısı',
                data,
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13,110,253,0.1)',
                tension: 0.4, fill: true, pointRadius: 5, pointHoverRadius: 7,
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: { y: { min: 0, ticks: { stepSize: 1 } } },
            plugins: { legend: { display: false } }
        }
    });
}

/* ── PG Tablosu: Hedef Değer Hesaplama (Hesaplama Yöntemi + Ölçüm/Gösterim Periyodu) ── */
/**
 * Periyot başına hedef değer hesapla.
 * - Toplama: Ölçüm periyodundan yıllığa çevir, sonra gösterim periyoduna pay et.
 * - Ortalama / Son Değer: Hedef her hücrede aynı.
 * @param {number} targetValue - Temel hedef değer
 * @param {string} olcumPeriyodu - Ölçüm Periyodu: Yıllık, Çeyreklik, Aylık, Haftalık, Günlük
 * @param {string} hesaplamaYontemi - Toplama, Ortalama, Son Değer
 * @param {string} gosterimPeriyodu - ceyrek, yillik, aylik, haftalik, gunluk
 * @param {string} periodKey - ceyrek_1, aylik_3, yillik_1 vb.
 * @returns {number|null} Hücre hedefi veya null
 */
function _normPeriyot(s) {
    return (s || '').toLowerCase().replace(/ı/g, 'i').replace(/ü/g, 'u').replace(/ö/g, 'o').replace(/ç/g, 'c').replace(/ğ/g, 'g').trim();
}

/** Toplama için yıllık hedef hesapla (Ölçüm periyodundan) */
function computeYillikHedef(targetValue, olcumPeriyodu, hesaplamaYontemi) {
    const tv = parseFloat(targetValue);
    if (isNaN(tv) || tv <= 0) return null;
    if (hesaplamaYontemi !== 'Toplama' && hesaplamaYontemi !== 'Toplam') return tv;
    const olcumCarpan = { yillik: 1, ceyrek: 4, ceyreklik: 4, aylik: 12, haftalik: 52, gunluk: 365 };
    const olcumNorm = _normPeriyot(olcumPeriyodu);
    const carpan = olcumCarpan[olcumNorm] ?? (olcumNorm.includes('yil') ? 1 : olcumNorm.includes('ceyrek') ? 4 : olcumNorm.includes('ay') ? 12 : olcumNorm.includes('hafta') ? 52 : olcumNorm.includes('gun') ? 365 : 1);
    return tv * carpan;
}

function computeCellTarget(targetValue, olcumPeriyodu, hesaplamaYontemi, gosterimPeriyodu, periodKey) {
    const tv = parseFloat(targetValue);
    if (isNaN(tv) || tv <= 0) return null;
    if (hesaplamaYontemi === 'Ortalama' || hesaplamaYontemi === 'Son Değer' || !hesaplamaYontemi) {
        return tv;
    }
    if (hesaplamaYontemi !== 'Toplama' && hesaplamaYontemi !== 'Toplam') return tv;

    const yillikHedef = computeYillikHedef(targetValue, olcumPeriyodu, hesaplamaYontemi);
    if (yillikHedef === null) return null;
    const gosterimBolum = { yillik: 1, ceyrek: 4, aylik: 12, haftalik: 52, gunluk: 365 };
    const bolum = gosterimBolum[gosterimPeriyodu] || 4;
    return Math.round((yillikHedef / bolum) * 1000) / 1000;
}

/* ── PG Tablosu: Gösterim'e Göre Yeniden Oluştur ──────────── */
const PERIOD_CONFIG = {
    ceyrek: [
        { key: 'ceyrek_1', label: 'I. Çeyrek' },
        { key: 'ceyrek_2', label: 'II. Çeyrek' },
        { key: 'ceyrek_3', label: 'III. Çeyrek' },
        { key: 'ceyrek_4', label: 'IV. Çeyrek' }
    ],
    yillik: [{ key: 'yillik_1', label: 'Yıl Sonu' }],
    aylik: [
        { key: 'aylik_1', label: 'Ocak' }, { key: 'aylik_2', label: 'Şubat' }, { key: 'aylik_3', label: 'Mart' },
        { key: 'aylik_4', label: 'Nisan' }, { key: 'aylik_5', label: 'Mayıs' }, { key: 'aylik_6', label: 'Haziran' },
        { key: 'aylik_7', label: 'Temmuz' }, { key: 'aylik_8', label: 'Ağustos' }, { key: 'aylik_9', label: 'Eylül' },
        { key: 'aylik_10', label: 'Ekim' }, { key: 'aylik_11', label: 'Kasım' }, { key: 'aylik_12', label: 'Aralık' }
    ],
    haftalik: (() => {
        const aylar = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara'];
        const arr = [];
        for (let m = 1; m <= 12; m++) {
            for (let w = 1; w <= 5; w++) {
                arr.push({ key: `haftalik_${w}_${m}`, label: `${aylar[m - 1]} H${w}` });
            }
        }
        return arr;
    })(),
    gunluk: null
};

function getPeriodsForPeriyot() {
    const viewedYear = getViewedYear();
    if (currentPeriyot === 'gunluk') {
        const viewedMonth = getViewedMonth();
        if (!viewedMonth) return [];
        const lastDay = new Date(viewedYear, viewedMonth, 0).getDate();
        const arr = [];
        for (let d = 1; d <= lastDay; d++) {
            arr.push({ key: `gunluk_${d}_${viewedMonth}`, label: String(d), isDay: true });
        }
        return arr;
    }
    if (currentPeriyot === 'yillik') {
        return [{ key: 'yillik_1', label: 'Yıl Sonu' }];
    }
    if (currentPeriyot === 'ceyrek') {
        return PERIOD_CONFIG.ceyrek;
    }
    if (currentPeriyot === 'aylik') {
        return PERIOD_CONFIG.aylik;
    }
    if (currentPeriyot === 'haftalik') {
        return PERIOD_CONFIG.haftalik;
    }
    return PERIOD_CONFIG.ceyrek || [];
}

function rebuildPGTableByPeriyot(kpis, favoriteKpiIds = []) {
    const favSet = new Set(favoriteKpiIds);
    const thead = document.getElementById('performansTableHead');
    const tbody = document.getElementById('performansTbody');
    if (!thead || !tbody) return;

    const periyot = getPeriodsForPeriyot();
    const periods = Array.isArray(periyot) ? periyot : [];
    const isGunluk = currentPeriyot === 'gunluk' && periods.length > 0 && periods[0].isDay;
    const aylar = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'];
    const monthName = isGunluk ? aylar[(getViewedMonth() || 1) - 1] : '';

    if (isGunluk) {
        let row1 = '<tr><th rowspan="2" class="col-code">Kodu</th><th rowspan="2" class="col-strategy">Ana Strateji</th><th rowspan="2" class="col-strategy">Alt Strateji</th><th rowspan="2">Performans Adı</th><th rowspan="2" class="col-weight">Ağırlık (%)</th><th rowspan="2" class="col-unit">Birim</th><th rowspan="2" class="col-period">Ölçüm Per.</th><th rowspan="2" class="col-target-main">Yıllık Hedef</th>';
        row1 += `<th colspan="${periods.length}" class="text-center">${monthName}</th>`;
        row1 += '<th rowspan="2" class="col-target">Başarı Puanı</th><th rowspan="2" class="col-actions no-print">İşlemler</th></tr><tr>';
        periods.forEach(p => {
            row1 += `<th class="col-quarter text-center kpi-day-col">${p.label}</th>`;
        });
        row1 += '</tr>';
        thead.innerHTML = row1;
    } else {
        let thRow1 = '<tr><th rowspan="2" class="col-code">Kodu</th><th rowspan="2" class="col-strategy">Ana Strateji</th><th rowspan="2" class="col-strategy">Alt Strateji</th><th rowspan="2">Performans Adı</th><th rowspan="2" class="col-weight">Ağırlık (%)</th><th rowspan="2" class="col-unit">Birim</th><th rowspan="2" class="col-period">Ölçüm Per.</th><th rowspan="2" class="col-target-main">Yıllık Hedef</th>';
        let thRow2 = '<tr>';
        periods.forEach(p => {
            thRow1 += `<th colspan="3" class="text-center">${p.label}</th>`;
            thRow2 += '<th class="col-quarter">Hedef</th><th class="col-quarter">Gerç.</th><th class="col-quarter">Durum</th>';
        });
        thRow1 += '<th rowspan="2" class="col-target">Başarı Puanı</th><th rowspan="2" class="col-actions no-print">İşlemler</th></tr>';
        thead.innerHTML = thRow1 + thRow2;
    }

    if (!kpis || kpis.length === 0) {
        const periodCols = isGunluk ? periods.length : periods.length * 3;
        const colspan = 8 + periodCols + 2;
        tbody.innerHTML = `<tr><td colspan="${colspan}" class="text-center text-muted py-5"><i class="bi bi-inbox" style="font-size:3rem;"></i><p class="mt-3">Henüz performans göstergesi eklenmemiş. "PG Ekle" butonunu kullanın.</p></td></tr>`;
        applyColumnVisibility();
        return;
    }

    let basariAraliklari;
    const rows = kpis.map(k => {
        try {
            basariAraliklari = k.basari_puani_araliklari ? (typeof k.basari_puani_araliklari === 'string' ? JSON.parse(k.basari_puani_araliklari) : k.basari_puani_araliklari) : null;
        } catch (e) { basariAraliklari = null; }

        const strategyTitle = (k.strategy_title || '-').toString().substring(0, 20);
        const subStrategyTitle = (k.sub_strategy_title || '-').toString().substring(0, 20);
        const kpiName = (k.name || '-').toString().replace(/</g, '&lt;').replace(/>/g, '&gt;');
        const targetValRaw = k.target_value || '-';
        const hesaplamaYontemi = k.data_collection_method || 'Ortalama';
        const olcumPeriyodu = k.period || '';
        const yillikHedef = computeYillikHedef(k.target_value, olcumPeriyodu, hesaplamaYontemi);
        const yillikHedefDisplay = yillikHedef !== null ? (Number.isInteger(yillikHedef) ? yillikHedef : yillikHedef.toFixed(2)) : targetValRaw;
        const favCls = favSet.has(k.id) ? 'bi-star-fill text-warning' : 'bi-star';

        let fixedCols = `<td class="col-code">${k.code || ''}</td><td class="col-strategy small">${strategyTitle}${(k.strategy_title || '').length > 20 ? '...' : ''}</td><td class="col-strategy small">${subStrategyTitle}${(k.sub_strategy_title || '').length > 20 ? '...' : ''}</td><td class="fw-medium">${kpiName}</td><td class="col-weight text-center">${k.weight || '-'}</td><td class="col-unit text-center">${k.unit || '-'}</td><td class="col-period text-center"><span class="badge bg-secondary">${olcumPeriyodu || '-'}</span></td><td class="col-target-main text-center fw-bold text-primary">${yillikHedefDisplay}</td>`;

        const entries = k.entries || {};
        let periodCells = '';
        if (isGunluk) {
            periods.forEach(p => {
                const val = entries[p.key];
                const hasVal = val !== undefined && val !== null && val !== '';
                const dataCls = hasVal ? 'table-success' : '';
                periodCells += `<td class="col-quarter text-center kpi-data-cell ${dataCls}" data-kpi="${k.id}" data-period="${p.key}" style="cursor:pointer;" onclick="openVeriDetay(${k.id}, '${p.key}')">${hasVal ? (typeof val === 'number' ? val : String(val)) : '—'}</td>`;
            });
        } else {
            periods.forEach(p => {
                const val = entries[p.key];
                const hasVal = val !== undefined && val !== null && val !== '';
                const cellTarget = computeCellTarget(k.target_value, olcumPeriyodu, hesaplamaYontemi, currentPeriyot, p.key);
                const target = cellTarget !== null ? cellTarget : parseFloat(k.target_value);
                const actual = parseFloat(val);
                let durumHtml = '—';
                if (hasVal && !isNaN(target) && !isNaN(actual) && target > 0) {
                    const ratio = k.direction === 'Decreasing' ? (actual > 0 ? target / actual : 0) : actual / target;
                    const cls = ratio >= 1 ? 'text-success' : ratio >= 0.8 ? 'text-warning' : 'text-danger';
                    const icon = ratio >= 1 ? '✅' : ratio >= 0.8 ? '⚠️' : '❌';
                    durumHtml = `<span class="${cls}" title="${Math.round(ratio * 100)}%">${icon}</span>`;
                }
                const hedefDisplay = cellTarget !== null ? (Number.isInteger(cellTarget) ? cellTarget : cellTarget.toFixed(2)) : targetValRaw;
                const dataCls = hasVal ? 'table-success' : '';
                periodCells += `<td class="col-quarter text-center kpi-hedef-cell">${hedefDisplay}</td><td class="col-quarter text-center kpi-data-cell ${dataCls}" data-kpi="${k.id}" data-period="${p.key}" style="cursor:pointer;" onclick="openVeriDetay(${k.id}, '${p.key}')">${hasVal ? (typeof val === 'number' ? val : String(val)) : '—'}</td><td class="col-quarter text-center kpi-durum-cell" data-kpi="${k.id}" data-durum-period="${p.key}">${durumHtml}</td>`;
            });
        }

        const allVals = Object.values(entries).map(v => parseFloat(v)).filter(v => !isNaN(v));
        let skorHtml = '—';
        const skorTarget = yillikHedef !== null ? yillikHedef : parseFloat(k.target_value);
        if (allVals.length > 0 && !isNaN(skorTarget) && skorTarget > 0) {
            const compareVal = (hesaplamaYontemi === 'Toplama' || hesaplamaYontemi === 'Toplam')
                ? allVals.reduce((a, b) => a + b, 0)
                : allVals[allVals.length - 1];
            let pct = Math.round((compareVal / skorTarget) * 100);
            if (k.direction === 'Decreasing') pct = compareVal > 0 ? Math.round((skorTarget / compareVal) * 100) : 0;
            if (basariAraliklari) {
                const puan = hesaplaBasariPuani(pct, basariAraliklari);
                if (puan !== null) {
                    const cls = puan >= 4 ? 'text-success' : puan >= 3 ? 'text-warning' : 'text-danger';
                    skorHtml = `<span class="${cls} fw-bold">${puan}/5</span>`;
                } else {
                    skorHtml = `<span class="${pct >= 100 ? 'text-success' : pct >= 80 ? 'text-warning' : 'text-danger'} fw-bold">%${pct}</span>`;
                }
            } else {
                skorHtml = `<span class="${pct >= 100 ? 'text-success' : pct >= 80 ? 'text-warning' : 'text-danger'} fw-bold">%${pct}</span>`;
            }
        }

        const kpiNameForDelete = (k.name || '').replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '&quot;');
        const actions = `<div class="btn-group btn-group-sm"><button class="btn btn-outline-warning favori-kpi-btn" data-kpi-id="${k.id}" title="Favorilere ekle/kaldır" aria-label="Favori"><i class="bi ${favCls}"></i></button><button class="btn btn-outline-primary" onclick="editKPI(${k.id})" title="Düzenle"><i class="bi bi-pencil"></i></button><button class="btn btn-outline-danger" onclick="deleteKPI(${k.id}, '${kpiNameForDelete}')" title="Sil"><i class="bi bi-trash"></i></button></div>`;

        return `<tr data-kpi-id="${k.id}" data-kpi-period="${k.period}" data-kpi-target="${k.target_value || ''}" data-kpi-direction="${k.direction || 'Increasing'}" data-kpi-basari="${k.basari_puani_araliklari || ''}">${fixedCols}${periodCells}<td class="col-target text-center kpi-skor-cell" data-kpi="${k.id}">${skorHtml}</td><td class="col-actions no-print">${actions}</td></tr>`;
    });

    tbody.innerHTML = rows.join('');
    applyColumnVisibility();
}

/* ── Faaliyet Aylık Takip Güncelle ── */
function updateActivityTracks(activities) {
    activities.forEach(a => {
        const tracks = a.monthly_tracks || {};
        for (let m = 1; m <= 12; m++) {
            const cell = document.querySelector(`.faaliyet-ay-cell[data-activity-id="${a.id}"][data-ay="${m}"]`);
            if (!cell) continue;
            const done = tracks[m] === true;
            cell.innerHTML = done
                ? '<span class="badge bg-success">✓</span>'
                : '<span class="text-muted small">—</span>';
            cell.dataset.completed = done ? 'true' : 'false';
        }
    });
}

/* ── Faaliyet Aylık Toggle ──────────── */
function toggleFaaliyet(cell) {
    const actId = cell.dataset.activityId;
    const month = parseInt(cell.dataset.ay);
    const current = cell.dataset.completed === 'true';
    const newVal = !current;

    // Optimistic update
    cell.innerHTML = newVal
        ? '<span class="badge bg-success">✓</span>'
        : '<span class="text-muted small">—</span>';
    cell.dataset.completed = newVal ? 'true' : 'false';

    postJSON('/process/api/activity/track', {
        activity_id: actId,
        year: currentYear,
        month: month,
        completed: newVal
    }).then(res => {
        if (!res.success) {
            // Geri al
            cell.innerHTML = current
                ? '<span class="badge bg-success">✓</span>'
                : '<span class="text-muted small">—</span>';
            cell.dataset.completed = current ? 'true' : 'false';
            Swal.fire('Hata!', res.message || 'Kayıt başarısız.', 'error');
        }
    }).catch(() => {
        cell.innerHTML = current
            ? '<span class="badge bg-success">✓</span>'
            : '<span class="text-muted small">—</span>';
        cell.dataset.completed = current ? 'true' : 'false';
    });
}

/* ── Veri Detay Modal ──────────────── */
function loadVeriDetayContent(kpiId, periodKey) {
    const content = document.getElementById('veriDetayContent');
    if (!content) return;
    content.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary"></div></div>';

    fetch(`/process/api/kpi-data/detail?kpi_id=${kpiId}&period_key=${periodKey}&year=${currentYear}`)
        .then(r => r.json())
        .then(res => {
            if (!res.success) {
                content.innerHTML = `<div class="alert alert-danger">Veri yüklenemedi.</div>`;
                return;
            }

            const periodLabels = {
                'ceyrek_1': 'I. Çeyrek', 'ceyrek_2': 'II. Çeyrek',
                'ceyrek_3': 'III. Çeyrek', 'ceyrek_4': 'IV. Çeyrek',
                'yillik_1': 'Yıl Sonu', 'aylik_1': 'Ocak', 'aylik_2': 'Şubat', 'aylik_3': 'Mart',
                'aylik_4': 'Nisan', 'aylik_5': 'Mayıs', 'aylik_6': 'Haziran',
                'aylik_7': 'Temmuz', 'aylik_8': 'Ağustos', 'aylik_9': 'Eylül',
                'aylik_10': 'Ekim', 'aylik_11': 'Kasım', 'aylik_12': 'Aralık',
                'haftalik_1_1': 'Ocak Hafta 1', 'haftalik_2_1': 'Ocak Hafta 2', 'gunluk_30_6': '30 Haziran'
            };
            const aylar = ['', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'];
            let periodLabel = periodLabels[periodKey];
            if (!periodLabel && periodKey.startsWith('haftalik_')) {
                const m = periodKey.split('_')[2];
                periodLabel = aylar[parseInt(m, 10)] + ' Hafta ' + (periodKey.split('_')[1] || '');
            }
            if (!periodLabel && periodKey.startsWith('gunluk_')) {
                const p = periodKey.split('_');
                periodLabel = (p[1] || '') + ' ' + (aylar[parseInt(p[2], 10)] || '');
            }
            if (!periodLabel) periodLabel = periodKey;

            const hasEntries = res.entries && res.entries.length > 0;
            const hasAudits = res.audits && res.audits.length > 0;
            if (!hasEntries && !hasAudits) {
                content.innerHTML = `
                    <div class="text-center py-4">
                        <i class="bi bi-inbox display-4 text-muted"></i>
                        <p class="mt-3 text-muted"><strong>${res.kpi_name}</strong> — ${periodLabel} ${res.year}</p>
                        <p class="text-muted">Bu periyot için henüz veri girilmemiş.</p>
                    </div>
                    <div class="border-top mt-3 pt-3" id="pgVeriProjeGorevleriSection">
                        <h6 class="text-muted"><i class="bi bi-link-45deg me-1"></i>Bu Veriyi Besleyen Proje Görevleri</h6>
                        <div id="pgProjeGorevleriList" class="small text-muted mb-0">Yükleniyor...</div>
                    </div>`;
                loadPGProjeGorevleri(content, kpiId, null, periodKey);
                return;
            }

            let html = `
                <h6 class="mb-3">
                    <i class="bi bi-speedometer2 me-2 text-primary"></i>
                    ${res.kpi_name} — <span class="badge bg-primary">${periodLabel}</span>
                    <span class="badge bg-secondary ms-1">${res.year}</span>
                </h6>`;

            if (hasEntries) {
                html += `
                <h6 class="text-muted mb-2"><i class="bi bi-table me-1"></i>Periyoda İlişkin Veriler</h6>
                <div class="table-responsive">
                    <table class="table table-sm table-hover" id="veriDetayEntriesTable">
                        <thead class="table-light">
                            <tr>
                                <th>Veri Tarihi</th>
                                <th>Giriş Tarihi</th>
                                <th>İşlem</th>
                                <th>Gerçekleşen</th>
                                <th>Hedef</th>
                                <th>Açıklama</th>
                                <th>Kullanıcı</th>
                                <th class="no-print">İşlemler</th>
                            </tr>
                        </thead>
                        <tbody>`;
                window._veriDetayEntries = res.entries;
                window._veriDetayKpiId = kpiId;
                window._veriDetayPeriodKey = periodKey;
                res.entries.forEach(e => {
                    const veriTarih = e.data_date ? new Date(e.data_date).toLocaleDateString('tr-TR') : '-';
                    const girisTarih = e.created_at ? new Date(e.created_at).toLocaleString('tr-TR') : '-';
                    html += `<tr data-entry-id="${e.id}" data-actual="${(e.actual_value || '').toString().replace(/"/g, '&quot;')}" data-desc="${(e.description || '').toString().replace(/"/g, '&quot;')}">
                        <td><small>${veriTarih}</small></td>
                        <td><small>${girisTarih}</small></td>
                        <td><span class="badge bg-success">Ekleme</span></td>
                        <td><strong class="text-primary">${(e.actual_value || '').toString().replace(/</g, '&lt;').replace(/>/g, '&gt;')}</strong></td>
                        <td>${(e.target_value || '-').toString().replace(/</g, '&lt;')}</td>
                        <td><small class="text-muted">${(e.description || '-').toString().replace(/</g, '&lt;').replace(/>/g, '&gt;')}</small></td>
                        <td><small><i class="bi bi-person-fill"></i> ${(e.user || '').toString().replace(/</g, '&lt;')}</small></td>
                        <td class="no-print">
                            <button class="btn btn-sm btn-outline-primary btn-edit-veri" data-entry-id="${e.id}" title="Düzenle"><i class="bi bi-pencil"></i></button>
                            <button class="btn btn-sm btn-outline-danger btn-delete-veri" data-entry-id="${e.id}" data-actual="${(e.actual_value || '').toString().replace(/</g, '&lt;')}" title="Sil"><i class="bi bi-trash"></i></button>
                        </td>
                    </tr>`;
                });
                html += '</tbody></table></div>';
                const vals = res.entries.map(e => parseFloat(e.actual_value)).filter(v => !isNaN(v));
                if (vals.length > 0) {
                    const toplam = vals.reduce((a, b) => a + b, 0);
                    const ort = (toplam / vals.length).toFixed(2);
                    html += `<div class="alert alert-info mt-2 mb-2">
                        <strong>Özet:</strong> Toplam giriş: ${res.entries.length} | Toplam değer: ${toplam.toFixed(2)} | Ortalama: ${ort}
                    </div>`;
                }
            }

            if (hasAudits) {
                html += `
                <h6 class="text-muted mt-3 mb-2"><i class="bi bi-clock-history me-1"></i>İşlem Geçmişi (Kim, Hangi Amaçla, Hangi Değerle)</h6>
                <div class="table-responsive">
                    <table class="table table-sm table-hover">
                        <thead class="table-light">
                            <tr>
                                <th>Tarih</th>
                                <th>İşlem</th>
                                <th>Kullanıcı</th>
                                <th>Eski Değer</th>
                                <th>Yeni Değer</th>
                                <th>Açıklama</th>
                            </tr>
                        </thead>
                        <tbody>`;
                res.audits.forEach(a => {
                    const badge = a.action_type === 'CREATE' ? 'bg-success' : a.action_type === 'UPDATE' ? 'bg-warning text-dark' : 'bg-danger';
                    const date = a.created_at ? new Date(a.created_at).toLocaleString('tr-TR') : '-';
                    html += `<tr>
                        <td><small>${date}</small></td>
                        <td><span class="badge ${badge}">${a.action_label || a.action_type}</span></td>
                        <td><small><i class="bi bi-person-fill"></i> ${(a.user || '').replace(/</g, '&lt;')}</small></td>
                        <td><small>${(a.old_value != null ? a.old_value : '-').toString().replace(/</g, '&lt;')}</small></td>
                        <td><small class="text-primary fw-bold">${(a.new_value != null ? a.new_value : '-').toString().replace(/</g, '&lt;')}</small></td>
                        <td><small class="text-muted">${(a.action_detail || '-').toString().replace(/</g, '&lt;')}</small></td>
                    </tr>`;
                });
                html += '</tbody></table></div>';
            }

            html += `
                <div class="border-top mt-3 pt-3" id="pgVeriProjeGorevleriSection">
                    <h6 class="text-muted"><i class="bi bi-link-45deg me-1"></i>Bu Veriyi Besleyen Proje Görevleri</h6>
                    <div id="pgProjeGorevleriList" class="small text-muted">Yükleniyor...</div>
                </div>`;

            content.innerHTML = html;
            const firstEntry = res.entries[0];
            const dataDate = firstEntry && firstEntry.data_date ? firstEntry.data_date : null;
            loadPGProjeGorevleri(content, kpiId, dataDate, periodKey);
        })
        .catch(() => {
            content.innerHTML = `<div class="alert alert-danger">Veri yüklenirken hata oluştu.</div>`;
        });
}

function openVeriDetay(kpiId, periodKey) {
    const modalEl = document.getElementById('veriDetayModal');
    if (!modalEl) return;
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
    loadVeriDetayContent(kpiId, periodKey);
}

document.body.addEventListener('click', function (e) {
    const editBtn = e.target.closest('#veriDetayContent .btn-edit-veri');
    if (editBtn) {
        e.preventDefault();
        const row = editBtn.closest('tr');
        const entryId = parseInt(editBtn.dataset.entryId);
        const kpiId = window._veriDetayKpiId;
        const periodKey = window._veriDetayPeriodKey;
        const actual = row ? (row.dataset.actual || '') : '';
        const desc = row ? (row.dataset.desc || '') : '';
        if (entryId && kpiId && periodKey !== undefined) {
            editVeriDetayEntry(entryId, kpiId, periodKey, actual, desc);
        }
        return;
    }
    const delBtn = e.target.closest('#veriDetayContent .btn-delete-veri');
    if (delBtn) {
        e.preventDefault();
        const entryId = parseInt(delBtn.dataset.entryId);
        const actualDisplay = delBtn.dataset.actual || '';
        const kpiId = window._veriDetayKpiId;
        const periodKey = window._veriDetayPeriodKey;
        if (entryId && kpiId !== undefined) {
            deleteVeriDetayEntry(entryId, kpiId, periodKey, actualDisplay);
        }
        return;
    }
});

function loadPGProjeGorevleri(containerEl, kpiId, dataDate, periodKey) {
    const listEl = containerEl ? containerEl.querySelector('#pgProjeGorevleriList') : document.getElementById('pgProjeGorevleriList');
    if (!listEl) return;
    const params = new URLSearchParams({ kpi_id: kpiId, year: currentYear, period_key: periodKey || '' });
    if (dataDate) params.append('data_date', dataDate);
    fetch(`/process/api/kpi-data/proje-gorevleri?${params}`)
        .then(r => r.json())
        .then(res => {
            if (res.success && res.gorevler && res.gorevler.length > 0) {
                listEl.innerHTML = res.gorevler.map(g => `<div class="mb-1"><i class="bi bi-check2-square me-1"></i>${g.title || g.ad || 'Görev'}</div>`).join('');
            } else {
                listEl.innerHTML = 'Henüz proje görevi bağlantısı yok.';
            }
        })
        .catch(() => { if (listEl) listEl.innerHTML = 'Yüklenemedi.'; });
}

function editVeriDetayEntry(entryId, kpiId, periodKey, currentActual, currentDesc) {
    const actualVal = (currentActual || '').replace(/&quot;/g, '"');
    const descVal = (currentDesc || '').replace(/&quot;/g, '"');
    const editModalEl = document.getElementById('veriDuzenleModal');
    const actualInput = document.getElementById('veriDuzenleActual');
    const descInput = document.getElementById('veriDuzenleDesc');
    if (!editModalEl || !actualInput || !descInput) return;
    actualInput.value = actualVal;
    descInput.value = descVal;
    editModalEl.dataset.editEntryId = String(entryId);
    editModalEl.dataset.editKpiId = String(kpiId);
    editModalEl.dataset.editPeriodKey = periodKey || '';
    const editModal = new bootstrap.Modal(editModalEl);
    editModal.show();
}

function deleteVeriDetayEntry(entryId, kpiId, periodKey, actualDisplay) {
    Swal.fire({
        title: 'Veriyi Sil',
        html: `<p>Bu veri kalıcı olarak silinecek.</p>${actualDisplay ? `<p><strong>Değer:</strong> ${actualDisplay.replace(/</g, '&lt;')}</p>` : ''}`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonText: 'Vazgeç',
        confirmButtonText: 'Sil'
    }).then(r => {
        if (!r.isConfirmed) return;
        postJSON(`/process/api/kpi-data/delete/${entryId}`, {}).then(res => {
            if (res.success) {
                Swal.fire({ icon: 'success', title: 'Silindi!', timer: 1000, showConfirmButton: false });
                loadVeriDetayContent(parseInt(kpiId), periodKey);
                loadKarneData();
            } else {
                Swal.fire('Hata!', res.message || 'Silme başarısız.', 'error');
            }
        }).catch(() => Swal.fire('Hata!', 'Silme sırasında bir hata oluştu.', 'error'));
    });
}

/* ── Periyot Label ──────────────────── */
function updatePeriyotLabel() {
    const label = document.getElementById('periyotNavigasyonLabel');
    if (!label) return;
    const names = { ceyrek: 'Çeyreklik', yillik: 'Yıllık', aylik: 'Aylık', haftalik: 'Haftalık', gunluk: 'Günlük' };
    const viewedYear = getViewedYear();
    let txt = '';
    if (currentPeriyot === 'gunluk') {
        const viewedMonth = getViewedMonth();
        const aylar = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'];
        txt = `${viewedYear} - ${aylar[(viewedMonth || 1) - 1]} - Günlük Görünümü`;
    } else {
        txt = `${viewedYear} - ${names[currentPeriyot] || currentPeriyot} Görünümü`;
    }
    label.textContent = txt;
}

function navigate(dir) {
    if (dir === 'prev') currentOffset--;
    else currentOffset++;
    updatePeriyotLabel();
    loadKarneData();
}

/* ── Sütun Toggle ──────────────────── */
function toggleCol(selector) {
    document.querySelectorAll('#performansTable ' + selector).forEach(el => {
        el.style.display = el.style.display === 'none' ? '' : 'none';
    });
}

function toggleColByClass(className) {
    document.querySelectorAll('#performansTable .' + className).forEach(el => {
        el.style.display = el.style.display === 'none' ? '' : 'none';
    });
}

/** Sütun gösterimi checkbox durumlarını tabloya uygula (tablo yenilendiğinde çağrılır) */
function applyColumnVisibility() {
    const mapping = [
        { id: 'col_code_chk', selector: '.col-code' },
        { id: 'col_strategy_chk', selector: '.col-strategy' },
        { id: 'col_weight_chk', selector: '.col-weight' },
        { id: 'col_unit_chk', selector: '.col-unit' },
        { id: 'col_period_chk', selector: '.col-period' },
        { id: 'col_target_chk', selector: '.col-target-main' }
    ];
    mapping.forEach(({ id, selector }) => {
        const chk = document.getElementById(id);
        if (!chk) return;
        const show = chk.checked;
        document.querySelectorAll('#performansTable ' + selector).forEach(el => {
            el.style.display = show ? '' : 'none';
        });
    });
}

/* ── Başarı Puanı Form Toggle ──────── */
function toggleBasariPuaniForm(mode) {
    const checkboxId = mode === 'add' ? 'pg_basari_puani_kullan' : 'edit_pg_basari_kullan';
    const divId = mode === 'add' ? 'pg_basari_puani_div' : 'edit_pg_basari_div';
    const checkbox = document.getElementById(checkboxId);
    const div = document.getElementById(divId);
    if (checkbox && div) {
        div.style.display = checkbox.checked ? 'block' : 'none';
    }
}

/* ── Modal Openers ─────────────────── */
function showAddPGForm() {
    new bootstrap.Modal(document.getElementById('addPGModal')).show();
}
function showAddFaaliyetForm() {
    new bootstrap.Modal(document.getElementById('addFaaliyetModal')).show();
}

/** Başarı puanı JSON hücresi: string veya { aralik, aciklama } */
function parseBasariPuaniCell(entry) {
    if (entry == null) return { aralik: '', aciklama: '' };
    if (typeof entry === 'object' && !Array.isArray(entry)) {
        return {
            aralik: String(entry.aralik || entry.range || '').trim(),
            aciklama: String(entry.aciklama || entry.label || entry.description || '').trim()
        };
    }
    return { aralik: String(entry).trim(), aciklama: '' };
}

/** Formdan JSON: açıklama varsa nesne, yoksa eski uyumluluk için düz string */
function buildBasariPuaniJson(aralikBase, aciklamaBase) {
    const o = {};
    for (let i = 1; i <= 5; i++) {
        const ar = document.getElementById(`${aralikBase}${i}`)?.value?.trim() || '';
        const ac = document.getElementById(`${aciklamaBase}${i}`)?.value?.trim() || '';
        if (ar || ac) {
            if (ac) o[i] = { aralik: ar, aciklama: ac };
            else o[i] = ar;
        }
    }
    return Object.keys(o).length ? JSON.stringify(o) : null;
}

/* ── PG Kaydet ─────────────────────── */
function savePG() {
    const basariKullan = document.getElementById('pg_basari_puani_kullan')?.checked;
    let basariAraliklari = null;
    if (basariKullan) {
        basariAraliklari = buildBasariPuaniJson('bp_aralik_', 'bp_aciklama_');
    }

    const data = {
        process_id: document.getElementById('pg_process_id').value,
        name: document.getElementById('pg_ad').value.trim(),
        code: document.getElementById('pg_kod')?.value?.trim() || '',
        target_value: document.getElementById('pg_hedef').value.trim(),
        unit: document.getElementById('pg_birim').value.trim(),
        period: document.getElementById('pg_periyot').value,
        direction: document.getElementById('pg_direction').value,
        weight: document.getElementById('pg_agirlik').value || 0,
        sub_strategy_id: document.getElementById('pg_alt_strateji').value || null,
        data_collection_method: document.getElementById('pg_hesaplama').value,
        gosterge_turu: document.getElementById('pg_gosterge_turu')?.value || null,
        target_method: document.getElementById('pg_hedef_yontemi')?.value || null,
        onceki_yil_ortalamasi: document.getElementById('pg_onceki_yil')?.value || null,
        basari_puani_araliklari: basariAraliklari,
        description: document.getElementById('pg_aciklama').value,
    };
    if (!data.name) { Swal.fire('Uyarı', 'Gösterge adı zorunludur.', 'warning'); return; }

    postJSON('/process/api/kpi/add', data).then(res => {
        if (res.success) {
            Swal.fire({ icon: 'success', title: 'Eklendi!', timer: 1000, showConfirmButton: false })
                .then(() => location.reload());
        } else {
            Swal.fire('Hata!', res.message, 'error');
        }
    });
}

/* ── KPI Düzenle Modal ──────────────── */
function editKPI(id) {
    fetch(`/process/api/kpi/get/${id}`)
        .then(r => r.json())
        .then(res => {
            if (!res.success) { Swal.fire('Hata!', 'KPI bilgisi alınamadı.', 'error'); return; }
            const k = res.kpi;

            // Formu doldur
            document.getElementById('edit_pg_id').value = k.id;
            document.getElementById('edit_pg_ad').value = k.name || '';
            document.getElementById('edit_pg_kod').value = k.code || '';
            document.getElementById('edit_pg_hedef').value = k.target_value || '';
            document.getElementById('edit_pg_birim').value = k.unit || '';
            document.getElementById('edit_pg_periyot').value = k.period || 'Çeyreklik';
            document.getElementById('edit_pg_direction').value = k.direction || 'Increasing';
            document.getElementById('edit_pg_agirlik').value = k.weight || '';
            document.getElementById('edit_pg_hesaplama').value = k.data_collection_method || 'Ortalama';
            document.getElementById('edit_pg_gosterge_turu').value = k.gosterge_turu || '';
            document.getElementById('edit_pg_hedef_yontemi').value = k.target_method || '';
            document.getElementById('edit_pg_onceki_yil').value = k.onceki_yil_ortalamasi || '';
            document.getElementById('edit_pg_aciklama').value = k.description || '';

            const altStratejiSel = document.getElementById('edit_pg_alt_strateji');
            if (altStratejiSel && k.sub_strategy_id) altStratejiSel.value = k.sub_strategy_id;

            // Başarı puanı
            const basariCheckbox = document.getElementById('edit_pg_basari_kullan');
            const basariDiv = document.getElementById('edit_pg_basari_div');
            const defaultBpLabels = {
                1: 'Beklentinin Çok Altında', 2: 'İyileştirmeye Açık', 3: 'Hedefe Ulaşmış',
                4: 'Hedefin Üzerinde', 5: 'Mükemmel'
            };
            if (k.basari_puani_araliklari) {
                try {
                    const araliklar = typeof k.basari_puani_araliklari === 'string'
                        ? JSON.parse(k.basari_puani_araliklari)
                        : k.basari_puani_araliklari;
                    if (basariCheckbox) basariCheckbox.checked = true;
                    if (basariDiv) basariDiv.style.display = 'block';
                    for (let i = 1; i <= 5; i++) {
                        const raw = araliklar[i] ?? araliklar[String(i)];
                        const cell = parseBasariPuaniCell(raw);
                        const el = document.getElementById(`edit_bp_aralik_${i}`);
                        const elAc = document.getElementById(`edit_bp_aciklama_${i}`);
                        if (el) el.value = cell.aralik;
                        if (elAc) elAc.value = cell.aciklama || defaultBpLabels[i] || '';
                    }
                } catch (e) { /* ignore */ }
            } else {
                if (basariCheckbox) basariCheckbox.checked = false;
                if (basariDiv) basariDiv.style.display = 'none';
                for (let i = 1; i <= 5; i++) {
                    const el = document.getElementById(`edit_bp_aralik_${i}`);
                    const elAc = document.getElementById(`edit_bp_aciklama_${i}`);
                    if (el) el.value = '';
                    if (elAc) elAc.value = defaultBpLabels[i] || '';
                }
            }

            new bootstrap.Modal(document.getElementById('editPGModal')).show();
        })
        .catch(() => Swal.fire('Hata!', 'Sunucu hatası.', 'error'));
}

/* ── PG Güncelle ─────────────────────── */
function updatePG() {
    const id = document.getElementById('edit_pg_id').value;
    if (!id) return;

    const basariKullan = document.getElementById('edit_pg_basari_kullan')?.checked;
    let basariAraliklari = null;
    if (basariKullan) {
        basariAraliklari = buildBasariPuaniJson('edit_bp_aralik_', 'edit_bp_aciklama_');
    }

    const data = {
        name: document.getElementById('edit_pg_ad').value.trim(),
        code: document.getElementById('edit_pg_kod')?.value?.trim() || '',
        target_value: document.getElementById('edit_pg_hedef').value.trim(),
        unit: document.getElementById('edit_pg_birim').value.trim(),
        period: document.getElementById('edit_pg_periyot').value,
        direction: document.getElementById('edit_pg_direction').value,
        weight: document.getElementById('edit_pg_agirlik').value || 0,
        sub_strategy_id: document.getElementById('edit_pg_alt_strateji').value || null,
        data_collection_method: document.getElementById('edit_pg_hesaplama').value,
        gosterge_turu: document.getElementById('edit_pg_gosterge_turu')?.value || null,
        target_method: document.getElementById('edit_pg_hedef_yontemi')?.value || null,
        onceki_yil_ortalamasi: document.getElementById('edit_pg_onceki_yil')?.value || null,
        basari_puani_araliklari: basariAraliklari,
        description: document.getElementById('edit_pg_aciklama')?.value || '',
    };

    if (!data.name) { Swal.fire('Uyarı', 'Gösterge adı zorunludur.', 'warning'); return; }

    postJSON(`/process/api/kpi/update/${id}`, data).then(res => {
        if (res.success) {
            Swal.fire({ icon: 'success', title: 'Güncellendi!', timer: 1000, showConfirmButton: false })
                .then(() => location.reload());
        } else {
            Swal.fire('Hata!', res.message, 'error');
        }
    });
}

/* ── Favori KPI Toggle ────────────────── */
function toggleFavoriteKpi(btn) {
    const kpiId = btn.dataset.kpiId;
    if (!kpiId) return;
    postJSON('/process/api/favorite-kpi/toggle', { process_kpi_id: parseInt(kpiId) })
        .then(res => {
            if (res.success) {
                const icon = btn.querySelector('i');
                if (icon) {
                    icon.classList.toggle('bi-star-fill', res.favorite);
                    icon.classList.toggle('bi-star', !res.favorite);
                    icon.classList.toggle('text-warning', res.favorite);
                }
            } else if (typeof Swal !== 'undefined') {
                Swal.fire('Hata!', res.message || 'İşlem başarısız.', 'error');
            }
        });
}

/* ── KPI Sil ─────────────────────────── */
function deleteKPI(id, name) {
    Swal.fire({
        title: 'Emin misiniz?',
        html: `<strong>"${name}"</strong> PG silinecek.`,
        icon: 'warning', showCancelButton: true,
        confirmButtonColor: '#dc3545', cancelButtonText: 'Vazgeç', confirmButtonText: 'Sil'
    }).then(r => {
        if (!r.isConfirmed) return;
        postJSON(`/process/api/kpi/delete/${id}`, {}).then(res => {
            if (res.success) {
                Swal.fire({ icon: 'success', timer: 800, showConfirmButton: false })
                    .then(() => location.reload());
            } else Swal.fire('Hata!', res.message, 'error');
        });
    });
}

/* ── Faaliyet Kaydet ─────────────────── */
function saveFaaliyet() {
    const data = {
        process_id: document.getElementById('faaliyet_process_id').value,
        name: document.getElementById('faaliyet_ad').value.trim(),
        process_kpi_id: document.getElementById('faaliyet_kpi').value || null,
        start_date: document.getElementById('faaliyet_baslangic').value || null,
        end_date: document.getElementById('faaliyet_bitis').value || null,
        status: document.getElementById('faaliyet_durum')?.value || 'Planlandı',
        description: document.getElementById('faaliyet_aciklama').value,
    };
    if (!data.name) { Swal.fire('Uyarı', 'Faaliyet adı zorunludur.', 'warning'); return; }

    postJSON('/process/api/activity/add', data).then(res => {
        if (res.success) {
            Swal.fire({ icon: 'success', timer: 800, showConfirmButton: false })
                .then(() => location.reload());
        } else Swal.fire('Hata!', res.message, 'error');
    });
}

/* ── Faaliyet Düzenle Modal ──────────── */
function editFaaliyet(id) {
    fetch(`/process/api/activity/get/${id}`)
        .then(r => r.json())
        .then(res => {
            if (!res.success) { Swal.fire('Hata!', 'Faaliyet bilgisi alınamadı.', 'error'); return; }
            const a = res.activity;
            document.getElementById('edit_faaliyet_id').value = a.id;
            document.getElementById('edit_faaliyet_ad').value = a.name || '';
            document.getElementById('edit_faaliyet_baslangic').value = a.start_date || '';
            document.getElementById('edit_faaliyet_bitis').value = a.end_date || '';
            document.getElementById('edit_faaliyet_durum').value = a.status || 'Planlandı';
            document.getElementById('edit_faaliyet_ilerleme').value = a.progress || 0;
            document.getElementById('edit_faaliyet_aciklama').value = a.description || '';
            new bootstrap.Modal(document.getElementById('editFaaliyetModal')).show();
        })
        .catch(() => Swal.fire('Hata!', 'Sunucu hatası.', 'error'));
}

/* ── Faaliyet Güncelle ─────────────── */
function updateFaaliyet() {
    const id = document.getElementById('edit_faaliyet_id').value;
    if (!id) return;
    const data = {
        name: document.getElementById('edit_faaliyet_ad').value.trim(),
        start_date: document.getElementById('edit_faaliyet_baslangic').value || null,
        end_date: document.getElementById('edit_faaliyet_bitis').value || null,
        status: document.getElementById('edit_faaliyet_durum').value,
        progress: document.getElementById('edit_faaliyet_ilerleme').value || 0,
        description: document.getElementById('edit_faaliyet_aciklama').value,
    };
    if (!data.name) { Swal.fire('Uyarı', 'Faaliyet adı zorunludur.', 'warning'); return; }

    postJSON(`/process/api/activity/update/${id}`, data).then(res => {
        if (res.success) {
            Swal.fire({ icon: 'success', timer: 800, showConfirmButton: false })
                .then(() => location.reload());
        } else Swal.fire('Hata!', res.message, 'error');
    });
}

/* ── Faaliyet Sil ─────────────────────── */
function deleteFaaliyet(id, name) {
    Swal.fire({
        title: 'Emin misiniz?',
        html: `<strong>"${name}"</strong> faaliyeti silinecek.`,
        icon: 'warning', showCancelButton: true,
        confirmButtonColor: '#dc3545', cancelButtonText: 'Vazgeç', confirmButtonText: 'Sil'
    }).then(r => {
        if (!r.isConfirmed) return;
        postJSON(`/process/api/activity/delete/${id}`, {}).then(res => {
            if (res.success) {
                Swal.fire({ icon: 'success', timer: 800, showConfirmButton: false })
                    .then(() => location.reload());
            } else Swal.fire('Hata!', res.message, 'error');
        });
    });
}

/* ── Excel Export ─────────────────── */
function exportToExcel() {
    if (!currentProcessId) {
        Swal.fire({ icon: 'warning', title: 'Uyarı', text: 'Önce bir süreç seçin.' });
        return;
    }
    const url = `/process/api/export/surec-karnesi/excel?process_id=${currentProcessId}&year=${currentYear}`;
    const a = document.createElement('a');
    a.href = url;
    a.download = `surec_karnesi_${currentYear}.xlsx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    Swal.fire({ icon: 'success', title: 'Dışa aktarıldı!', text: 'Excel dosyası indirildi.', timer: 1500, showConfirmButton: false });
}

/* ── Global (onclick) ─────────────────── */
if (typeof window !== 'undefined') {
    window.showAddPGForm = showAddPGForm;
    window.showAddFaaliyetForm = showAddFaaliyetForm;
    window.navigate = navigate;
    window.openVeriDetay = openVeriDetay;
    window.editKPI = editKPI;
    window.deleteKPI = deleteKPI;
    window.toggleFaaliyet = toggleFaaliyet;
    window.editFaaliyet = editFaaliyet;
    window.deleteFaaliyet = deleteFaaliyet;
    window.toggleCol = toggleCol;
    window.toggleColByClass = toggleColByClass;
    window.toggleBasariPuaniForm = toggleBasariPuaniForm;
    window.editVeriDetayEntry = editVeriDetayEntry;
    window.deleteVeriDetayEntry = deleteVeriDetayEntry;
}
