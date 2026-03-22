/**
 * Süreç Karnesi Hesaplama Modülü
 * Başarı puanı, skor hesaplamaları.
 */

function coerceBasariAralikStr(v) {
    if (v == null) return null;
    if (typeof v === 'object' && !Array.isArray(v)) {
        const r = v.aralik ?? v.range;
        if (r == null || String(r).trim() === '') return null;
        return String(r).trim();
    }
    const s = String(v).trim();
    return s || null;
}

export function hesaplaBasariPuani(pct, araliklar) {
    for (let puan = 1; puan <= 5; puan++) {
        const raw = araliklar[puan] || araliklar[String(puan)];
        const aralik = coerceBasariAralikStr(raw);
        if (!aralik) continue;
        const [minStr, maxStr] = aralik.split('-');
        const min = parseFloat(minStr) || 0;
        const max = maxStr !== undefined ? parseFloat(maxStr) : Infinity;
        if (pct >= min && pct <= max) return puan;
    }
    return null;
}
