/**
 * Proje Listesi - Arama ve Filtreleme İşlemleri
 * Inline JS bağımsızlaştırma (Phase 4) kapsamında oluşturulmuştur.
 */
document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('projectSearchInput');
    const list = document.getElementById('projectCardList');
    if (!input || !list) return;

    input.addEventListener('input', function() {
        const query = input.value.trim().toLowerCase();
        Array.from(list.children).forEach(card => {
            const text = (card.dataset.projectText || '');
            card.style.display = !query || text.includes(query) ? '' : 'none';
        });
    });
});
