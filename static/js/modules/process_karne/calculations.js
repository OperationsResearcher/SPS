/**
 * Süreç Karnesi Hesaplama Modülü
 * Başarı puanı, skor hesaplamaları.
 */

export function hesaplaBasariPuani(pct, araliklar) {
    for (let puan = 1; puan <= 5; puan++) {
        const aralik = araliklar[puan] || araliklar[String(puan)];
        if (!aralik) continue;
        const [minStr, maxStr] = aralik.split('-');
        const min = parseFloat(minStr) || 0;
        const max = maxStr !== undefined ? parseFloat(maxStr) : Infinity;
        if (pct >= min && pct <= max) return puan;
    }
    return null;
}
