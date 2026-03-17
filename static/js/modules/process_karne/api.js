/**
 * Süreç Karnesi API Modülü
 * Tüm sunucu istekleri buradan yönetilir.
 */

const CSRF = () => document.querySelector('meta[name="csrf-token"]')?.content || '';

export function postJSON(url, data) {
    return fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF() },
        body: JSON.stringify(data)
    }).then(r => r.json());
}

export async function fetchKarneData(processId, year, month) {
    let url = `/process/api/karne/${processId}?year=${year}`;
    if (month) url += `&month=${month}`;
    const r = await fetch(url);
    return r.json();
}

export async function fetchKpiDataDetail(kpiId, periodKey, year) {
    const r = await fetch(`/process/api/kpi-data/detail?kpi_id=${kpiId}&period_key=${periodKey}&year=${year}`);
    return r.json();
}

export async function fetchProjeGorevleri(kpiId, year, periodKey, dataDate) {
    const params = new URLSearchParams({ kpi_id: kpiId, year: year, period_key: periodKey || '' });
    if (dataDate) params.append('data_date', dataDate);
    const r = await fetch(`/process/api/kpi-data/proje-gorevleri?${params}`);
    return r.json();
}
