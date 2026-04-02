
    // Yeni Süreç Formu Göster/Gizle

    function toggleYeniSurecForm() {

        const container = document.getElementById('yeni-surec-form-container');

        const btn = document.getElementById('toggleBtn');



        if (container.classList.contains('show')) {

            // Gizle

            container.classList.remove('show');

            btn.innerHTML = '<i class="bi bi-plus-circle-fill"></i> Yeni Süreç Oluştur';

            // Yukarı scroll

            window.scrollTo({ top: 0, behavior: 'smooth' });

        } else {

            // Göster

            container.classList.add('show');

            btn.innerHTML = '<i class="bi bi-x-lg"></i> Formu Kapat';

            // Forma scroll

            setSaatout(() => {

                container.scrollIntoGörüntüle({ behavior: 'smooth', block: 'start' });

            }, 300);

        }

    }



    // Lider ekleme/çıkarma fonksiyonları (Çoklu)

    function addLiderler() {

        const source = document.getElementById('lider_source');

        const target = document.getElementById('lider_ids');

        const selected = Array.from(source.selectedOptions);



        selected.forEach(opt => {

            // Zaten eklenmemiş ise ekle

            if (!Array.from(target.options).find(o => o.value === opt.value)) {

                const newOpt = new Option(opt.text, opt.value);

                target.add(newOpt);

            }

        });

    }



    function removeLiderler() {

        const target = document.getElementById('lider_ids');

        const selected = Array.from(target.selectedOptions);

        selected.forEach(opt => opt.remove());

    }



    // Düzenleme formu lider ekleme/çıkarma fonksiyonları

    function addDüzenleLiderler() {

        const modal = document.querySelector('.modal.show');

        const source = modal ? modal.querySelector('#edit_lider_source') : document.getElementById('edit_lider_source');

        const target = modal ? modal.querySelector('#edit_lider_ids') : document.getElementById('edit_lider_ids');

        if (!source || !target) { showToast('warning', 'Form alanı bulunamadı.', 'Uyarı'); return; }

        const selected = Array.from(source.selectedOptions);



        console.log('Lider ekleme işlemi başladı');

        console.log('Seçilen liderler:', selected.map(opt => ({ value: opt.value, text: opt.text })));



        if (selected.length === 0) {

            showToast('warning', 'Lütfen önce sol taraftan lider seçin!', 'Uyarı');

            return;

        }



        let addedCount = 0;

        selected.forEach(opt => {

            // Zaten eklenmemiş ise ekle

            if (!Array.from(target.options).find(o => o.value === opt.value)) {

                const newOpt = new Option(opt.text, opt.value);

                target.add(newOpt);

                addedCount++;

                console.log(`Lider eklendi: ${opt.text}`);

            } else {

                console.log(`Lider zaten mevcut: ${opt.text}`);

            }

        });



        if (addedCount > 0) {

            showToast('success', `${addedCount} lider eklendi!`, 'Başarılı');

        } else {

            showToast('warning', 'Seçilen liderler zaten mevcut!', 'Uyarı');

        }



        console.log('Lider ekleme tamamlandı');

    }



    function removeDüzenleLiderler() {

        const modal = document.querySelector('.modal.show');

        const target = modal ? modal.querySelector('#edit_lider_ids') : document.getElementById('edit_lider_ids');

        if (!target) { showToast('warning', 'Form alanı bulunamadı.', 'Uyarı'); return; }

        const selected = Array.from(target.selectedOptions);



        console.log('Lider çıkarma işlemi başladı');

        console.log('Çıkarılacak liderler:', selected.map(opt => ({ value: opt.value, text: opt.text })));



        if (selected.length === 0) {

            showToast('warning', 'Lütfen önce sağ taraftan çıkarılacak lideri seçin!', 'Uyarı');

            return;

        }



        const removedCount = selected.length;

        selected.forEach(opt => {

            opt.remove();

            console.log(`Lider çıkarıldı: ${opt.text}`);

        });



        showToast('success', `${removedCount} lider çıkarıldı!`, 'Başarılı');

        console.log('Lider çıkarma tamamlandı');

    }



    function addDüzenleUyeler() {

        const modal = document.querySelector('.modal.show');

        const source = modal ? modal.querySelector('#edit_uye_source') : document.getElementById('edit_uye_source');

        const target = modal ? modal.querySelector('#edit_uye_ids') : document.getElementById('edit_uye_ids');

        if (!source || !target) { showToast('warning', 'Form alanı bulunamadı.', 'Uyarı'); return; }

        const selected = Array.from(source.selectedOptions);

        let addedCount = 0;



        selected.forEach(opt => {

            // Zaten eklenmemiş ise ekle

            if (!Array.from(target.options).find(o => o.value === opt.value)) {

                const newOpt = new Option(opt.text, opt.value);

                target.add(newOpt);

                addedCount++;

            }

        });



        if (addedCount > 0) {

            const message = addedCount > 1 ? `${addedCount} üye eklendi.` : `'${selected[0].text}' ekibe eklendi.`;

            showToast('success', message, 'Başarılı');

        }

    }



    function removeDüzenleUyeler() {

        const modal = document.querySelector('.modal.show');

        const target = modal ? modal.querySelector('#edit_uye_ids') : document.getElementById('edit_uye_ids');

        if (!target) { showToast('warning', 'Form alanı bulunamadı.', 'Uyarı'); return; }

        const selected = Array.from(target.selectedOptions);

        const removedCount = selected.length;

        selected.forEach(opt => opt.remove());



        if (removedCount > 0) {

            const message = removedCount > 1 ? `${removedCount} üye çıkarıldı.` : `Üye çıkarıldı.`;

            showToast('success', message, 'Başarılı');

        }

    }



    /**
    
     * Düzenleme formunda mevcut liderleri yükle
    
     */

    function loadDüzenleSurecLiderler(surec) {

        const modalEl = document.getElementById('editSurecModal');

        const target = modalEl ? modalEl.querySelector('#edit_lider_ids') : document.getElementById('edit_lider_ids');

        if (!target) return;

        target.innerHTML = '';



        console.log('Lider yükleme işlemi başladı:', surec.liderler);



        if (surec.liderler && surec.liderler.length > 0) {

            console.log('Lider sayısı:', surec.liderler.length);

            surec.liderler.forEach((lider, index) => {

                console.log(`Lider ${index + 1}:`, lider);

                const option = new Option(lider.username, lider.id);

                target.add(option);

            });

        } else {

            console.log('Lider bulunamadı');

        }



        console.log('Lider yükleme tamamlandı');

    }



    /**
    
     * Düzenleme formunda mevcut üyeleri yükle
    
     */

    function loadDüzenleSurecUyeler(surec) {

        const modalEl = document.getElementById('editSurecModal');

        const target = modalEl ? modalEl.querySelector('#edit_uye_ids') : document.getElementById('edit_uye_ids');

        if (!target) return;

        target.innerHTML = '';



        console.log('Üye yükleme işlemi başladı:', surec.uyeler);



        if (surec.uyeler && surec.uyeler.length > 0) {

            console.log('Üye sayısı:', surec.uyeler.length);

            surec.uyeler.forEach((uye, index) => {

                console.log(`Üye ${index + 1}:`, uye);

                const option = new Option(uye.username, uye.id);

                target.add(option);

            });

        } else {

            console.log('Üye bulunamadı');

        }



        console.log('Üye yükleme tamamlandı');

    }



    /**
    
     * Düzenleme formunda mevcut alt stratejileri yükle
    
     */

    function loadDüzenleSurecStratejiler(surec) {

        const modalEl = document.getElementById('editSurecModal');

        const target = modalEl ? modalEl.querySelector('#edit_strateji_ids') : document.getElementById('edit_strateji_ids');

        if (!target) return;

        target.innerHTML = '';



        console.log('Alt strateji yükleme işlemi başladı:', surec.alt_stratejiler);



        if (surec.alt_stratejiler && surec.alt_stratejiler.length > 0) {

            console.log('Alt strateji sayısı:', surec.alt_stratejiler.length);



            // Ana stratejilere göre grupla

            const groupedStrategies = {};

            surec.alt_stratejiler.forEach((strateji, index) => {

                console.log(`Alt Strateji ${index + 1}:`, strateji);

                const mainStrategyAd = strateji.ana_strateji ? strateji.ana_strateji.ad : 'Bilinmiyor';



                if (!groupedStrategies[mainStrategyAd]) {

                    groupedStrategies[mainStrategyAd] = [];

                }

                groupedStrategies[mainStrategyAd].push({

                    id: strateji.id,

                    name: strateji.ad

                });

            });



            // Her ana strateji için grup oluştur

            Object.keys(groupedStrategies).forEach(mainStrategyAd => {

                const strategies = groupedStrategies[mainStrategyAd];



                // Ana strateji başlığı (optgroup benzeri)

                const mainStrategyDiv = document.createElement('div');

                mainStrategyDiv.className = 'strategy-group';

                mainStrategyDiv.innerHTML = `

                <div class="strategy-group-header">

                    <strong>${mainStrategyAd}</strong>

                </div>

            `;



                // Alt stratejileri ekle

                strategies.forEach(strategy => {

                    const strategyDiv = document.createElement('div');

                    strategyDiv.className = 'strategy-item';

                    strategyDiv.setAttribute('data-strategy-id', strategy.id);

                    strategyDiv.innerHTML = `

                    <div class="strategy-sub">${strategy.name}</div>

                `;

                    strategyDiv.onclick = () => toggleDüzenleStrategySelection(strategy.id);

                    strategyDiv.ondblclick = () => removeDüzenleStrategyItem(strategy.id);

                    mainStrategyDiv.appendChild(strategyDiv);

                });



                target.appendChild(mainStrategyDiv);

            });

        } else {

            console.log('Alt strateji bulunamadı');

        }



        console.log('Alt strateji yükleme tamamlandı');

    }



    // Süreç Düzenle modalında bağlı alt süreçleri listele; tıklayınca o sürecin düzenlemesine geç
    function fillEditAltSureclerList(altSurecler) {
        const wrap = document.getElementById('edit_alt_surecler_wrap');
        const list = document.getElementById('edit_alt_surecler_list');
        if (!wrap || !list) return;
        list.innerHTML = '';
        if (!altSurecler || altSurecler.length === 0) {
            wrap.style.display = 'none';
            return;
        }
        wrap.style.display = 'block';
        altSurecler.forEach(function (sub) {
            const item = document.createElement('a');
            item.href = '#';
            item.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
            item.innerHTML = '<span><i class="bi bi-arrow-return-right me-2 text-muted"></i>' + (sub.ad || 'Süreç #' + sub.id) + '</span><span class="badge bg-primary">Düzenle</span>';
            item.onclick = function (e) {
                e.preventDefault();
                var modalEl = document.getElementById('editSurecModal');
                var modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();
                if (typeof cleanupOverlayAndBackdrop === 'function') cleanupOverlayAndBackdrop();
                setTimeout(function () { editProcess(sub.id); }, 300);
            };
            list.appendChild(item);
        });
    }

    // Düzenleme formu için strateji ekleme fonksiyonu

    function addDüzenleStratejiler() {

        const modal = document.querySelector('.modal.show');

        const source = modal ? modal.querySelector('#edit_strateji_source') : document.getElementById('edit_strateji_source');

        const target = modal ? modal.querySelector('#edit_strateji_ids') : document.getElementById('edit_strateji_ids');

        if (!source || !target) { showToast('warning', 'Form alanı bulunamadı.', 'Uyarı'); return; }

        const selected = Array.from(source.selectedOptions);



        if (selected.length === 0) {

            showToast('warning', 'Lütfen önce sol taraftan strateji seçin!', 'Uyarı');

            return;

        }



        let addedCount = 0;



        // Ana stratejilere göre grupla

        const groupedStrategies = {};

        selected.forEach(opt => {

            const mainStrategyAd = opt.dataset.mainStrategyName || opt.dataset.mainStrategyAd || '';

            const subStrategyAd = opt.text;



            if (!groupedStrategies[mainStrategyAd]) {

                groupedStrategies[mainStrategyAd] = [];

            }

            groupedStrategies[mainStrategyAd].push({

                id: opt.value,

                name: subStrategyAd

            });

        });



        // Her ana strateji için grup oluştur

        Object.keys(groupedStrategies).forEach(mainStrategyAd => {

            const strategies = groupedStrategies[mainStrategyAd];



            // Ana strateji başlığı (optgroup benzeri)

            const mainStrategyDiv = document.createElement('div');

            mainStrategyDiv.className = 'strategy-group';

            mainStrategyDiv.innerHTML = `

            <div class="strategy-group-header">

                <strong>${mainStrategyAd}</strong>

            </div>

        `;



            // Alt stratejileri ekle

            strategies.forEach(strategy => {

                // Zaten eklenmemiş ise ekle

                if (!target.querySelector(`[data-strategy-id="${strategy.id}"]`)) {

                    const strategyDiv = document.createElement('div');

                    strategyDiv.className = 'strategy-item';

                    strategyDiv.setAttribute('data-strategy-id', strategy.id);

                    strategyDiv.innerHTML = `

                    <div class="strategy-sub">${strategy.name}</div>

                `;

                    strategyDiv.onclick = () => toggleDüzenleStrategySelection(strategy.id);

                    strategyDiv.ondblclick = () => removeDüzenleStrategyItem(strategy.id);

                    mainStrategyDiv.appendChild(strategyDiv);

                    addedCount++;

                }

            });



            // Eğer bu ana strateji için yeni alt strateji eklendiyse, grubu ekle

            if (mainStrategyDiv.children.length > 1) { // header + items

                target.appendChild(mainStrategyDiv);

            }

        });



        if (addedCount > 0) {

            showToast('success', `${addedCount} strateji eklendi!`, 'Başarılı');

        } else {

            showToast('warning', 'Seçilen stratejiler zaten ekli!', 'Uyarı');

        }

    }



    // Düzenleme formu için strateji çıkarma fonksiyonu

    function removeDüzenleStratejiler() {

        const modal = document.querySelector('.modal.show');

        const target = modal ? modal.querySelector('#edit_strateji_ids') : document.getElementById('edit_strateji_ids');

        if (!target) { showToast('warning', 'Form alanı bulunamadı.', 'Uyarı'); return; }

        const selectedItems = target.querySelectorAll('.strategy-item.selected');



        if (selectedItems.length === 0) {

            showToast('warning', 'Lütfen önce sağ taraftan strateji seçin!', 'Uyarı');

            return;

        }



        selectedItems.forEach(item => {

            item.remove();

        });



        showToast('success', `${selectedItems.length} strateji çıkarıldı!`, 'Başarılı');

    }



    // Düzenleme formu için strateji item çıkarma fonksiyonu

    function removeDüzenleStrategyItem(strategyId) {

        const modal = document.querySelector('.modal.show');

        const target = modal ? modal.querySelector('#edit_strateji_ids') : document.getElementById('edit_strateji_ids');

        const item = target ? target.querySelector(`.strategy-item[data-strategy-id="${strategyId}"]`) : null;

        if (item) {

            item.remove();

            showToast('success', 'Strateji çıkarıldı!', 'Başarılı');

        }

    }



    // Düzenleme formu için strateji seçim toggle fonksiyonu

    function toggleDüzenleStrategySelection(strategyId) {

        const modal = document.querySelector('.modal.show');

        const target = modal ? modal.querySelector('#edit_strateji_ids') : document.getElementById('edit_strateji_ids');

        const item = target ? target.querySelector(`.strategy-item[data-strategy-id="${strategyId}"]`) : null;

        if (item) {

            item.classList.toggle('selected');

        }

    }



    // Üye ekleme/çıkarma fonksiyonları

    function addUyeler() {

        const source = document.getElementById('uye_source');

        const target = document.getElementById('uye_ids');

        const selected = Array.from(source.selectedOptions);

        let addedCount = 0;



        selected.forEach(opt => {

            // Zaten eklenmemiş ise ekle

            if (!Array.from(target.options).find(o => o.value === opt.value)) {

                const newOpt = new Option(opt.text, opt.value);

                target.add(newOpt);

                addedCount++;

            }

        });



        if (addedCount > 0) {

            const message = addedCount > 1 ? `${addedCount} üye eklendi.` : `'${selected[0].text}' ekibe eklendi.`;

            showToast('success', message, 'Başarılı');

        }

    }



    function removeUyeler() {

        const target = document.getElementById('uye_ids');

        const selected = Array.from(target.selectedOptions);

        const removedCount = selected.length;

        selected.forEach(opt => opt.remove());



        if (removedCount > 0) {

            const message = removedCount > 1 ? `${removedCount} üye çıkarıldı.` : `Üye çıkarıldı.`;

            showToast('success', message, 'Başarılı');

        }

    }



    // Strateji ekleme/çıkarma fonksiyonları

    function addStratejiler() {

        const source = document.getElementById('strateji_source');

        const target = document.getElementById('alt_strateji_ids');

        const selected = Array.from(source.selectedOptions);

        let addedCount = 0;



        selected.forEach(opt => {

            // Zaten eklenmemiş ise ekle

            if (!Array.from(target.options).find(o => o.value === opt.value)) {

                // Ana strateji bilgisini al

                const optgroup = opt.parentElement;

                const anaStratejiAdi = optgroup.label;

                const altStratejiAdi = opt.text;



                // Basit text formatında option oluştur

                const newOpt = new Option();

                newOpt.value = opt.value;

                newOpt.text = `${anaStratejiAdi} →†’ ${altStratejiAdi}`;

                target.add(newOpt);

                addedCount++;

            }

        });



        if (addedCount > 0) {

            const message = addedCount > 1 ? `${addedCount} strateji eklendi.` : `'${selected[0].text}' stratejisi eklendi.`;

            showToast('success', message, 'Başarılı');

        }

    }



    function removeStratejiler() {

        const target = document.getElementById('alt_strateji_ids');

        const selected = Array.from(target.selectedOptions);

        const removedCount = selected.length;

        selected.forEach(opt => opt.remove());



        if (removedCount > 0) {

            const message = removedCount > 1 ? `${removedCount} strateji çıkarıldı.` : `Strateji çıkarıldı.`;

            showToast('success', message, 'Başarılı');

        }

    }



    // Seçimleri temizle

    function resetSelections() {

        document.getElementById('lider_ids').innerHTML = '';

        document.getElementById('uye_ids').innerHTML = '';

        document.getElementById('alt_strateji_ids').innerHTML = '';

    }



    // Anti-ghosting: overlay ve modal backdrop temizliği (global, her yerden çağrılabilir)
    function cleanupOverlayAndBackdrop() {
        var backdrops = document.querySelectorAll('.modal-backdrop');
        for (var i = 0; i < backdrops.length; i++) backdrops[i].remove();
        var guideOverlays = document.querySelectorAll('.guide-overlay');
        for (var j = 0; j < guideOverlays.length; j++) guideOverlays[j].remove();
        document.body.classList.remove('modal-open');
        document.body.style.removeProperty('overflow');
        document.body.style.removeProperty('padding-right');
        if (document.body.style.pointerEvents === 'none') document.body.style.removeProperty('pointer-events');
    }

    // Erişilebilirlik: modal kapandığında odağı ana sayfaya döndür (aria-hidden / focus kilidi önleme)
    function focusResetOnModalHide() {
        var active = document.activeElement;
        if (!active || active === document.body) return;
        var inModal = active.closest && active.closest('.modal');
        if (!inModal) return;
        active.blur();
        document.body.setAttribute('tabindex', '-1');
        try { document.body.focus(); } catch (e) {}
    }

    document.addEventListener('DOMContentLoaded', function () {
        cleanupOverlayAndBackdrop();
        function onModalHidden() {
            focusResetOnModalHide();
            cleanupOverlayAndBackdrop();
        }
        /* Açılışta modalı body'ye taşı: main (z-index:1) içinde kalırsa backdrop (1050) modalın üstüne biner (hayalet ekran). */
        function ensureModalInBody(ev) {
            var el = ev.target;
            if (el && el.nodeType === 1 && el.parentNode !== document.body) {
                document.body.appendChild(el);
            }
        }
        var modalIds = ['editSurecModal', 'newProcessModal', 'surecDetayModal', 'editProcessModal'];
        for (var k = 0; k < modalIds.length; k++) {
            var el = document.getElementById(modalIds[k]);
            if (el) {
                el.addEventListener('show.bs.modal', ensureModalInBody);
                el.addEventListener('hide.bs.modal', focusResetOnModalHide); /* aria-hidden uygulanmadan önce odağı dışarı al */
                el.addEventListener('hidden.bs.modal', onModalHidden);
            }
        }
    });
    window.addEventListener('error', function () { cleanupOverlayAndBackdrop(); });
    window.addEventListener('unhandledrejection', function () { cleanupOverlayAndBackdrop(); });

    // Süreç ağacı collapse/expand: özyinelemeli tüm alt süreçleri gizle/göster (DOM üzerinden, performanslı)
    document.addEventListener('DOMContentLoaded', function () {
        var tbody = document.getElementById('surec-tree-tbody');
        if (!tbody) return;
        function getDescendantIds(rootId) {
            var rows = tbody.querySelectorAll('tr.surec-tree-row');
            var parentToIds = {};
            var id;
            for (var i = 0; i < rows.length; i++) {
                id = rows[i].getAttribute('data-parent-id');
                if (!id) continue;
                if (!parentToIds[id]) parentToIds[id] = [];
                parentToIds[id].push(rows[i].getAttribute('data-surec-id'));
            }
            var out = [];
            var stack = [rootId];
            while (stack.length) {
                var pid = stack.pop();
                var children = parentToIds[pid];
                if (!children) continue;
                for (var j = 0; j < children.length; j++) {
                    out.push(children[j]);
                    stack.push(children[j]);
                }
            }
            return out;
        }
        tbody.addEventListener('click', function (e) {
            var btn = e.target.closest('.surec-tree-toggle');
            if (!btn) return;
            var surecId = btn.getAttribute('data-surec-id');
            var descendantIds = getDescendantIds(surecId);
            var icon = btn.querySelector('.surec-toggle-icon');
            var isCurrentlyVisible = btn.getAttribute('data-descendants-visible') !== 'false';
            var show = !isCurrentlyVisible;
            for (var k = 0; k < descendantIds.length; k++) {
                var row = tbody.querySelector('tr.surec-tree-row[data-surec-id="' + descendantIds[k] + '"]');
                if (row) row.style.display = show ? '' : 'none';
            }
            btn.setAttribute('data-descendants-visible', show ? 'true' : 'false');
            if (icon) {
                icon.classList.toggle('bi-chevron-down', show);
                icon.classList.toggle('bi-chevron-right', !show);
            }
        });
    });

    // Form submit

    document.addEventListener('DOMContentLoaded', function () {

        document.getElementById('surec-form').addEventListener('submit', function (e) {

            e.preventDefault();



            // Tüm seçimleri array'e çevir

            const liderIds = Array.from(document.getElementById('lider_ids').options).map(opt => opt.value);

            const uyeIds = Array.from(document.getElementById('uye_ids').options).map(opt => opt.value);

            const altStratejiIds = Array.from(document.getElementById('alt_strateji_ids').options).map(opt => opt.value);



            // İşlem başladı mesajı

            showToast('info', 'Yeni süreç oluşturuluyor...', '→³ İşlem Devam Ediyor');



            fetch('/surec/add-simple', {

                method: 'POST',

                headers: { 'Content-Type': 'application/json' },

                body: JSON.stringify({

                    surec_adi: document.getElementById('ad').value,

                    parent_id: (() => { const el = document.getElementById('surec_parent_id'); return (el && el.value) ? parseInt(el.value, 10) : null; })(),

                    dokuman_no: document.getElementById('dokuman_no').value,

                    rev_no: document.getElementById('rev_no').value,

                    rev_tarihi: document.getElementById('rev_tarihi').value,

                    ilk_yayin_tarihi: document.getElementById('ilk_yayin_tarihi').value,

                    baslangic_tarihi: document.getElementById('baslangic_tarihi').value,

                    bitis_tarihi: document.getElementById('bitis_tarihi').value,

                    durum: document.getElementById('durum').value,

                    ilerleme: document.getElementById('ilerleme').value,

                    lider_ids: liderIds,

                    uye_ids: uyeIds,

                    alt_strateji_ids: altStratejiIds,

                    baslangic_siniri: document.getElementById('baslangic_siniri').value,

                    bitis_siniri: document.getElementById('bitis_siniri').value,

                    aciklama: document.getElementById('aciklama').value

                })

            })

                .then(function (r) { return r.json().then(function (data) { return { status: r.status, data: data }; }); })

                .then(function (res) {

                    var data = res.data;

                    if (data.success) {

                        // Başarı mesajı

                        showToast('success', data.message, 'Başarılı');

                        // Formu temizle

                        document.getElementById('surec-form').reset();

                        resetSelections();

                        if (typeof cleanupOverlayAndBackdrop === 'function') cleanupOverlayAndBackdrop();

                        // Sayfayı yenile

                        setTimeout(function () { location.reload(); }, 1500);

                    } else {

                        showToast('error', data.message, res.status === 400 ? 'Validasyon Hatası' : 'Hata');
                        if (typeof cleanupOverlayAndBackdrop === 'function') cleanupOverlayAndBackdrop();

                    }

                })

                .catch(function (err) {

                    showToast('error', 'Hata: ' + err.message, 'Bağlantı Hatası');
                    if (typeof cleanupOverlayAndBackdrop === 'function') cleanupOverlayAndBackdrop();

                });

        });

    });



    // Süreç detaylarını görüntüle

    function viewSurec(id) {

        const modal = new bootstrap.Modal(document.getElementById('surecDetayModal'));

        modal.show();



        fetch(`/surec/${id}`)

            .then(r => r.json())

            .then(data => {

                const surec = data.surec;

                const gostergeler = data.performans_gostergeleri || [];



                // Faaliyetleri yükle

                fetch(`/surec/${id}/faaliyetler`)

                    .then(r => r.json())

                    .then(faaliyetData => {

                        const faaliyetler = faaliyetData.faaliyetler || [];



                        // Detay HTML'ini oluştur

                        document.getElementById('surec-detay-icerik').innerHTML = `

                <div class="row">

                    <div class="col-12">

                        <h4 class="text-primary mb-4">

                            <i class="bi bi-diagram-3-fill me-2"></i>${surec.ad}

                        </h4>

                    </div>

                </div>

                

                <!-- Temel Bilgiler -->

                <div class="row mb-4">

                    <div class="col-md-6">

                        <div class="card bg-light">

                            <div class="card-header bg-primary text-white">

                                <h6 class="mb-0"><i class="bi bi-info-circle-fill me-2"></i>Temel Bilgiler</h6>

                            </div>

                            <div class="card-body">

                                <p><strong>Doküman No:</strong> ${surec.dokuman_no || '-'}</p>

                                <p><strong>Revizyon No:</strong> ${surec.rev_no || '-'}</p>

                                <p><strong>Revizyon Tarihi:</strong> ${surec.rev_tarihi || '-'}</p>

                                <p><strong>İlk Yayın Tarihi:</strong> ${surec.ilk_yayin_tarihi || '-'}</p>

                                <p><strong>Durum:</strong> <span class="badge bg-${surec.durum === 'Aktif' ? 'success' : surec.durum === 'Pasif' ? 'secondary' : 'warning'}">${surec.durum}</span></p>

                                <p><strong>İlerleme:</strong> 

                                    <div class="progress mt-1" style="height: 20px;">

                                        <div class="progress-bar bg-${surec.ilerleme >= 75 ? 'success' : surec.ilerleme >= 50 ? 'info' : surec.ilerleme >= 25 ? 'warning' : 'danger'}" 

                                             style="width: ${surec.ilerleme}%">${surec.ilerleme}%</div>

                                    </div>

                                </p>

                            </div>

                        </div>

                    </div>

                    <div class="col-md-6">

                        <div class="card bg-light">

                            <div class="card-header bg-success text-white">

                                <h6 class="mb-0"><i class="bi bi-calendar-event me-2"></i>Tarih Bilgileri</h6>

                            </div>

                            <div class="card-body">

                                <p><strong>Başlangıç Tarihi:</strong> ${surec.baslangic_tarihi || '-'}</p>

                                <p><strong>Bitiş Tarihi:</strong> ${surec.bitis_tarihi || '-'}</p>

                                <p><strong>Kurum:</strong> ${surec.kurum || '-'}</p>

                                <p><strong>Başlangıç Sınırı:</strong> ${surec.baslangic_siniri || '-'}</p>

                                <p><strong>Bitiş Sınırı:</strong> ${surec.bitis_siniri || '-'}</p>

                            </div>

                        </div>

                    </div>

                </div>

                

                <!-- Ekip ve Stratejiler -->

                <div class="row mb-4">

                    <div class="col-md-4">

                        <div class="card bg-light">

                            <div class="card-header bg-warning text-dark">

                                <h6 class="mb-0"><i class="bi bi-star-fill me-2"></i>Süreç Liderleri</h6>

                            </div>

                            <div class="card-body">

                                ${surec.liderler && surec.liderler.length > 0 ?

                                surec.liderler.map(lider => `<span class="badge bg-primary me-1 mb-1">${lider.username}</span>`).join('') :

                                '<span class="text-muted">Lider atanmamış</span>'

                            }

                            </div>

                        </div>

                    </div>

                    <div class="col-md-4">

                        <div class="card bg-light">

                            <div class="card-header bg-info text-white">

                                <h6 class="mb-0"><i class="bi bi-people-fill me-2"></i>Süreç Üyeleri</h6>

                            </div>

                            <div class="card-body">

                                ${surec.uyeler && surec.uyeler.length > 0 ?

                                surec.uyeler.map(uye => `<span class="badge bg-secondary me-1 mb-1">${uye.username}</span>`).join('') :

                                '<span class="text-muted">Üye atanmamış</span>'

                            }

                            </div>

                        </div>

                    </div>

                    <div class="col-md-4">

                        <div class="card bg-light">

                            <div class="card-header bg-dark text-white">

                                <h6 class="mb-0"><i class="bi bi-bullseye me-2"></i>Alt Stratejiler</h6>

                            </div>

                            <div class="card-body">

                                ${surec.alt_stratejiler && surec.alt_stratejiler.length > 0 ?

                                (() => {

                                    // Ana stratejilere göre grupla

                                    const groupedStrategies = {};

                                    surec.alt_stratejiler.forEach(strateji => {

                                        const mainStrategyAd = strateji.ana_strateji.ad;

                                        if (!groupedStrategies[mainStrategyAd]) {

                                            groupedStrategies[mainStrategyAd] = [];

                                        }

                                        groupedStrategies[mainStrategyAd].push(strateji);

                                    });



                                    // Grupları HTML olarak oluştur

                                    return Object.keys(groupedStrategies).map(mainStrategyAd => {

                                        const strategies = groupedStrategies[mainStrategyAd];

                                        return `

                                                <div class="strategy-group mb-3">

                                                    <div class="strategy-group-header bg-primary text-white p-2 rounded-top">

                                                        <strong><i class="bi bi-diagram-2 me-1"></i>${mainStrategyAd}</strong>

                                                    </div>

                                                    <div class="strategy-group-content bg-light p-2 rounded-bottom border border-top-0">

                                                        ${strategies.map(strateji => `

                                                            <div class="strategy-item mb-1 p-2 bg-white rounded border-start border-primary border-3">

                                                                <small class="text-dark fw-medium">${strateji.ad}</small>

                                                            </div>

                                                        `).join('')}

                                                    </div>

                                                </div>

                                            `;

                                    }).join('');

                                })() :

                                '<span class="text-muted"><i class="bi bi-info-circle me-1"></i>Strateji atanmamış</span>'

                            }

                            </div>

                        </div>

                    </div>

                </div>

                

                <!-- Açıklama -->

                ${surec.aciklama ? `

                <div class="row mb-4">

                    <div class="col-12">

                        <div class="card bg-light">

                            <div class="card-header bg-secondary text-white">

                                <h6 class="mb-0"><i class="bi bi-chat-text me-2"></i>Açıklama</h6>

                            </div>

                            <div class="card-body">

                                <p class="mb-0">${surec.aciklama}</p>

                            </div>

                        </div>

                    </div>

                </div>

                ` : ''}

                

                <!-- Performans Göstergeleri -->

                ${gostergeler && gostergeler.length > 0 ? `

                <div class="row mb-4">

                    <div class="col-12">

                        <div class="card bg-light">

                            <div class="card-header bg-primary text-white">

                                <h6 class="mb-0"><i class="bi bi-graph-up me-2"></i>Performans Göstergeleri</h6>

                            </div>

                            <div class="card-body">

                                <div class="table-responsive">

                                    <table class="table table-sm">

                                        <thead>

                                            <tr>

                                                <th>Gösterge Adı</th>

                                                <th>Hedef Değer</th>

                                                <th>Ç–lçüm Birimi</th>

                                                <th>Periyot</th>

                                            </tr>

                                        </thead>

                                        <tbody>

                                            ${gostergeler.map(gosterge => `

                                                <tr>

                                                    <td>${gosterge.ad}</td>

                                                    <td>${gosterge.hedef_deger || '-'}</td>

                                                    <td>${gosterge.olcum_birimi || '-'}</td>

                                                    <td>${gosterge.periyot || '-'}</td>

                                                </tr>

                                            `).join('')}

                                        </tbody>

                                    </table>

                                </div>

                            </div>

                        </div>

                    </div>

                </div>

                ` : ''}

                

                <!-- Faaliyetler -->

                ${faaliyetler && faaliyetler.length > 0 ? `

                <div class="row mb-4">

                    <div class="col-12">

                        <div class="card bg-light">

                            <div class="card-header bg-success text-white">

                                <h6 class="mb-0"><i class="bi bi-list-task me-2"></i>Faaliyetler</h6>

                            </div>

                            <div class="card-body">

                                <div class="table-responsive">

                                    <table class="table table-sm">

                                        <thead>

                                            <tr>

                                                <th>Faaliyet Adı</th>

                                                <th>Durum</th>

                                                <th>İlerleme</th>

                                                <th>Başlangıç</th>

                                                <th>Bitiş</th>

                                            </tr>

                                        </thead>

                                        <tbody>

                                            ${faaliyetler.map(faaliyet => `

                                                <tr>

                                                    <td>${faaliyet.ad}</td>

                                                    <td><span class="badge bg-${faaliyet.durum === 'Tamamlandı' ? 'success' : faaliyet.durum === 'Devam Ediyor' ? 'primary' : 'warning'}">${faaliyet.durum}</span></td>

                                                    <td>${faaliyet.ilerleme}%</td>

                                                    <td>${faaliyet.baslangic_tarihi || '-'}</td>

                                                    <td>${faaliyet.bitis_tarihi || '-'}</td>

                                                </tr>

                                            `).join('')}

                                        </tbody>

                                    </table>

                                </div>

                            </div>

                        </div>

                    </div>

                </div>

                ` : ''}

            `;

                    });

            });

    }



    // Düzenleme fonksiyonu

    function editSurec(id) {

        // Süreç bilgilerini getir

        fetch(`/surec/get/${id}`)

            .then(r => r.json())

            .then(data => {

                if (data.success) {

                    const surec = data.surec;

                    console.log('Süreç verileri yüklendi:', surec);



                    // Form alanlarını güvenli şekilde doldur

                    const elements = {

                        'edit_surec_id': surec.id,

                        'edit_ad': surec.ad,

                        'edit_dokuman_no': surec.dokuman_no || '',

                        'edit_rev_no': surec.rev_no || '',

                        'edit_rev_tarihi': surec.rev_tarihi || '',

                        'edit_ilk_yayin_tarihi': surec.ilk_yayin_tarihi || '',

                        'edit_baslangic_tarihi': surec.baslangic_tarihi || '',

                        'edit_bitis_tarihi': surec.bitis_tarihi || '',

                        'edit_durum': surec.durum,

                        'edit_ilerleme': surec.ilerleme,

                        'edit_baslangic_siniri': surec.baslangic_siniri || '',

                        'edit_bitis_siniri': surec.bitis_siniri || '',

                        'edit_aciklama': surec.aciklama || ''

                    };



                    // Tüm alanları güvenli şekilde doldur

                    Object.keys(elements).forEach(key => {

                        const element = document.getElementById(key);

                        if (element) {

                            element.value = elements[key];

                        }

                    });



                    // Liderleri yükle

                    loadDüzenleSurecLiderler(surec);



                    // Üyeleri yükle

                    loadDüzenleSurecUyeler(surec);



                    // Alt stratejileri yükle

                    loadDüzenleSurecStratejiler(surec);

                    // Bağlı alt süreçleri listele (tıklayınca o sürece geç)
                    fillEditAltSureclerList(data.alt_surecler || []);

                    // Modalı göster

                    const modal = new bootstrap.Modal(document.getElementById('editSurecModal'));

                    modal.show();

                } else {

                    showToast('error', data.message);
                    if (typeof cleanupOverlayAndBackdrop === 'function') cleanupOverlayAndBackdrop();

                }

            })

            .catch(function (err) {

                showToast('error', 'Süreç bilgileri yüklenirken hata: ' + err.message);
                if (typeof cleanupOverlayAndBackdrop === 'function') cleanupOverlayAndBackdrop();

            });

    }



    // Düzenleme formu submit fonksiyonu

    function updateSurec(e) {

        e.preventDefault();



        const surecId = document.getElementById('edit_surec_id').value;



        // İşlem başladı mesajı

        showToast('info', 'Süreç güncelleniyor...', 'İşlem Devam Ediyor');



        // Lider, üye ve strateji bilgilerini topla (açık modal içinden)

        const formModal = e.target && e.target.closest ? e.target.closest('.modal') : null;

        const stratejiContainer = formModal ? formModal.querySelector('#edit_strateji_ids') : document.getElementById('edit_strateji_ids');

        const liderSelect = formModal ? formModal.querySelector('#edit_lider_ids') : document.getElementById('edit_lider_ids');

        const uyeSelect = formModal ? formModal.querySelector('#edit_uye_ids') : document.getElementById('edit_uye_ids');

        const liderIds = liderSelect ? Array.from(liderSelect.options).map(opt => parseInt(opt.value)) : [];

        const uyeIds = uyeSelect ? Array.from(uyeSelect.options).map(opt => parseInt(opt.value)) : [];

        const stratejiIds = stratejiContainer ? Array.from(stratejiContainer.querySelectorAll('.strategy-item')).map(item => parseInt(item.getAttribute('data-strategy-id'))) : [];



        fetch('/surec/update/' + surecId, {

            method: 'POST',

            headers: { 'Content-Type': 'application/json' },

            body: JSON.stringify({

                surec_adi: document.getElementById('edit_ad').value,

                dokuman_no: document.getElementById('edit_dokuman_no').value,

                rev_no: document.getElementById('edit_rev_no').value,

                rev_tarihi: document.getElementById('edit_rev_tarihi').value,

                ilk_yayin_tarihi: document.getElementById('edit_ilk_yayin_tarihi').value,

                baslangic_tarihi: document.getElementById('edit_baslangic_tarihi').value,

                bitis_tarihi: document.getElementById('edit_bitis_tarihi').value,

                durum: document.getElementById('edit_durum').value,

                ilerleme: document.getElementById('edit_ilerleme').value,

                baslangic_siniri: document.getElementById('edit_baslangic_siniri').value,

                bitis_siniri: document.getElementById('edit_bitis_siniri').value,

                aciklama: document.getElementById('edit_aciklama').value,

                parent_id: (function () { var el = document.getElementById('edit_parent_id'); return (el && el.value) ? parseInt(el.value, 10) : null; })(),

                weight: (function () { var el = document.getElementById('edit_weight'); return (el && el.value !== '') ? parseFloat(el.value) : null; })(),

                lider_ids: liderIds,

                uye_ids: uyeIds,

                strateji_ids: stratejiIds

            })

        })

            .then(function (r) { return r.json().then(function (data) { return { status: r.status, data: data }; }); })

            .then(function (res) {

                var data = res.data;

                if (data.success) {

                    showToast('success', data.message, 'Başarılı');

                    var modalElement = document.getElementById('editSurecModal');

                    var modal = bootstrap.Modal.getInstance(modalElement);

                    if (modal) modal.hide();

                    if (typeof cleanupOverlayAndBackdrop === 'function') cleanupOverlayAndBackdrop();

                    setTimeout(function () { location.reload(); }, 1500);

                } else {

                    showToast('error', data.message, res.status === 400 ? 'Validasyon Hatası' : 'Hata');
                    if (typeof cleanupOverlayAndBackdrop === 'function') cleanupOverlayAndBackdrop();

                }

            })

            .catch(function (err) {

                showToast('error', 'Güncelleme hatası: ' + err.message, 'Bağlantı Hatası');
                if (typeof cleanupOverlayAndBackdrop === 'function') cleanupOverlayAndBackdrop();

            });

    }



    // Silme fonksiyonu

    function deleteSurec(id, name) {

        if (confirm('Silmek istediğinizden emin misiniz?\n\nSüreç: ' + name)) {

            showToast('info', 'Süreç siliniyor...', 'İşlem Devam Ediyor');



            fetch('/surec/delete/' + id, { method: 'DELETE' })

                .then(r => r.json())

                .then(data => {

                    if (data.success) {

                        showToast('success', data.message, 'Başarılı');

                        if (typeof cleanupOverlayAndBackdrop === 'function') cleanupOverlayAndBackdrop();

                        setTimeout(function () { location.reload(); }, 1500);

                    } else {

                        showToast('error', data.message, 'Hata');
                        if (typeof cleanupOverlayAndBackdrop === 'function') cleanupOverlayAndBackdrop();

                    }

                })

                .catch(function (err) {

                    showToast('error', 'Silme işlemi başarısız: ' + err.message, 'Hata');
                    if (typeof cleanupOverlayAndBackdrop === 'function') cleanupOverlayAndBackdrop();

                });

        }

    }



    // Yeni süreç formu için lider ekleme fonksiyonu

    function addNewLiderler() {

        const source = document.getElementById('new_lider_source');

        const target = document.getElementById('new_lider_ids');

        const selected = Array.from(source.selectedOptions);



        if (selected.length === 0) {

            showToast('warning', 'Lütfen önce sol taraftan lider seçin!', 'Uyarı');

            return;

        }



        let addedCount = 0;

        selected.forEach(opt => {

            if (!Array.from(target.options).find(o => o.value === opt.value)) {

                const newOpt = new Option(opt.text, opt.value);

                target.add(newOpt);

                addedCount++;

            }

        });



        if (addedCount > 0) {

            showToast('success', `${addedCount} lider eklendi!`, 'Başarılı');

        } else {

            showToast('info', 'Seçilen liderler zaten mevcut!', 'Bilgi');

        }

    }



    // Yeni süreç formu için lider çıkarma fonksiyonu

    function removeNewLiderler() {

        const target = document.getElementById('new_lider_ids');

        const selected = Array.from(target.selectedOptions);



        if (selected.length === 0) {

            showToast('warning', 'Lütfen önce sağ taraftan lider seçin!', 'Uyarı');

            return;

        }



        selected.forEach(opt => {

            target.removeChild(opt);

        });



        showToast('success', `${selected.length} lider çıkarıldı!`, 'Başarılı');

    }



    // Yeni süreç formu için üye ekleme fonksiyonu

    function addNewUyeler() {

        const source = document.getElementById('new_uye_source');

        const target = document.getElementById('new_uye_ids');

        const selected = Array.from(source.selectedOptions);



        console.log('Yeni süreç üye ekleme işlemi başladı');

        console.log('Seçilen üyeler:', selected.map(opt => ({ value: opt.value, text: opt.text })));



        if (selected.length === 0) {

            showToast('warning', 'Lütfen önce sol taraftan üye seçin!', 'Uyarı');

            return;

        }



        let addedCount = 0;

        selected.forEach(opt => {

            // Zaten eklenmemiş ise ekle

            if (!Array.from(target.options).find(o => o.value === opt.value)) {

                const newOpt = new Option(opt.text, opt.value);

                target.add(newOpt);

                addedCount++;

            }

        });



        if (addedCount > 0) {

            const message = addedCount > 1 ? `${addedCount} üye eklendi.` : `'${selected[0].text}' ekibe eklendi.`;

            showToast('success', message, 'Başarılı');

        } else {

            showToast('warning', 'Seçilen üyeler zaten mevcut!', 'Uyarı');

        }

    }



    // Yeni süreç formu için üye çıkarma fonksiyonu

    function removeNewUyeler() {

        const target = document.getElementById('new_uye_ids');

        const selected = Array.from(target.selectedOptions);



        console.log('Yeni süreç üye çıkarma işlemi başladı');

        console.log('Çıkarılacak üyeler:', selected.map(opt => ({ value: opt.value, text: opt.text })));



        if (selected.length === 0) {

            showToast('warning', 'Lütfen önce sağ taraftan üye seçin!', 'Uyarı');

            return;

        }



        const removedCount = selected.length;

        selected.forEach(opt => {

            target.removeChild(opt);

        });



        const message = removedCount > 1 ? `${removedCount} üye çıkarıldı.` : `Üye çıkarıldı.`;

        showToast('success', message, 'Başarılı');

    }



    // Yeni süreç formu için strateji ekleme fonksiyonu

    function addNewStratejiler() {

        const source = document.getElementById('new_strateji_source');

        const target = document.getElementById('new_strateji_ids');

        const selected = Array.from(source.selectedOptions);



        if (selected.length === 0) {

            showToast('warning', 'Lütfen önce sol taraftan strateji seçin!', 'Uyarı');

            return;

        }



        let addedCount = 0;



        // Ana stratejilere göre grupla

        const groupedStrategies = {};

        selected.forEach(opt => {

            const mainStrategyAd = opt.dataset.mainStrategyName || opt.dataset.mainStrategyAd || '';

            const subStrategyAd = opt.text;



            if (!groupedStrategies[mainStrategyAd]) {

                groupedStrategies[mainStrategyAd] = [];

            }

            groupedStrategies[mainStrategyAd].push({

                id: opt.value,

                name: subStrategyAd

            });

        });



        // Her ana strateji için grup oluştur

        Object.keys(groupedStrategies).forEach(mainStrategyAd => {

            const strategies = groupedStrategies[mainStrategyAd];



            // Ana strateji başlığı (optgroup benzeri)

            const mainStrategyDiv = document.createElement('div');

            mainStrategyDiv.className = 'strategy-group';

            mainStrategyDiv.innerHTML = `

            <div class="strategy-group-header">

                <strong>${mainStrategyAd}</strong>

            </div>

        `;



            // Alt stratejileri ekle

            strategies.forEach(strategy => {

                // Zaten eklenmemiş ise ekle

                if (!target.querySelector(`[data-strategy-id="${strategy.id}"]`)) {

                    const strategyDiv = document.createElement('div');

                    strategyDiv.className = 'strategy-item';

                    strategyDiv.setAttribute('data-strategy-id', strategy.id);

                    strategyDiv.innerHTML = `

                    <div class="strategy-sub">${strategy.name}</div>

                `;

                    strategyDiv.onclick = () => toggleStrategySelection(strategy.id);

                    strategyDiv.ondblclick = () => removeStrategyItem(strategy.id);

                    mainStrategyDiv.appendChild(strategyDiv);

                    addedCount++;

                }

            });



            // Eğer bu ana strateji için yeni alt strateji eklendiyse, grubu ekle

            if (mainStrategyDiv.children.length > 1) { // header + items

                target.appendChild(mainStrategyDiv);

            }

        });



        if (addedCount > 0) {

            showToast('success', `${addedCount} strateji eklendi!`, 'Başarılı');

        } else {

            showToast('info', 'Seçilen stratejiler zaten mevcut!', 'Bilgi');

        }

    }



    // Yeni süreç formu için strateji çıkarma fonksiyonu

    function removeNewStratejiler() {

        const target = document.getElementById('new_strateji_ids');

        const selectedItems = target.querySelectorAll('.strategy-item.selected');



        if (selectedItems.length === 0) {

            showToast('warning', 'Lütfen önce sağ taraftan strateji seçin!', 'Uyarı');

            return;

        }



        selectedItems.forEach(item => {

            item.remove();

        });



        showToast('success', `${selectedItems.length} strateji çıkarıldı!`, 'Başarılı');

    }



    // Strateji seçimini toggle etme fonksiyonu

    function toggleStrategySelection(strategyId) {

        const target = document.getElementById('new_strateji_ids');

        const item = target.querySelector(`[data-strategy-id="${strategyId}"]`);

        if (item) {

            item.classList.toggle('selected');

        }

    }



    // Strateji öğesini çıkarma fonksiyonu

    function removeStrategyItem(strategyId) {

        const target = document.getElementById('new_strateji_ids');

        const item = target.querySelector(`[data-strategy-id="${strategyId}"]`);

        if (item) {

            item.remove();

            showToast('success', 'Strateji çıkarıldı!', 'Başarılı');

        }

    }



    // Yeni Süreç Oluşturma Fonksiyonu

    const IS_ADMIN = window.CONFIG.IS_ADMIN;

    function onNewProcessKurumChange(kurumId) {

        filterUsersByKurum(kurumId, 'new_lider_source');

        filterUsersByKurum(kurumId, 'new_uye_source');

    }

    document.addEventListener('DOMContentLoaded', function () {

        const kurumSelect = document.getElementById('newProcessKurum');

        if (kurumSelect && kurumSelect.value) {

            onNewProcessKurumChange(kurumSelect.value);

        }

    });

    function createNewProcess() {

        // Çoklu lider seçimi için lider ID'lerini topla

        const liderIds = Array.from(document.getElementById('new_lider_ids').options).map(opt => opt.value);

        const uyeIds = Array.from(document.getElementById('new_uye_ids').options).map(opt => opt.value);

        const stratejiIds = Array.from(document.querySelectorAll('#new_strateji_ids .strategy-item')).map(item => item.getAttribute('data-strategy-id'));



        const parentIdEl = document.getElementById('newProcessParentId');
        const formData = {

            ad: document.getElementById('newProcessAd').value.trim(),

            parent_id: (parentIdEl && parentIdEl.value) ? parseInt(parentIdEl.value, 10) : null,

            weight: (function () { var el = document.getElementById('newProcessWeight'); return (el && el.value !== '') ? parseFloat(el.value) : null; })(),

            lider_ids: liderIds, // Çoklu lider seçimi

            uye_ids: uyeIds, // Çoklu üye seçimi

            strateji_ids: stratejiIds, // Çoklu strateji seçimi

            dokuman_no: document.getElementById('newProcessDokuman').value.trim(),

            rev_no: document.getElementById('newProcessRevizyon').value.trim(),

            rev_tarihi: document.getElementById('newProcessRevTarihi').value,

            ilk_yayin_tarihi: document.getElementById('newProcessIlkYayinTarihi').value,

            durum: document.getElementById('newProcessDurum').value,

            ilerleme: document.getElementById('newProcessIlerleme').value,

            baslangic_tarihi: document.getElementById('newProcessBaslangic').value,

            bitis_tarihi: document.getElementById('newProcessBitis').value,

            baslangic_siniri: document.getElementById('newProcessBaslangicSiniri').value.trim(),

            bitis_siniri: document.getElementById('newProcessBitisSiniri').value.trim(),

            aciklama: document.getElementById('newProcessAciklama').value.trim()

        };

        var kurumEl = document.getElementById('newProcessKurum');
        formData.kurum_id = kurumEl ? kurumEl.value : (typeof CURRENT_USER_KURUM_ID !== 'undefined' ? CURRENT_USER_KURUM_ID : '');

        // Zorunlu alan kontrolü
        if (!formData.ad || !formData.kurum_id || liderIds.length === 0) {

            const msg = 'Lütfen süreç adı ve en az bir lider seçin!';

            showToast('warning', msg, 'Uyarı');

            return;

        }



        const submitBtn = document.querySelector('button[onclick="createNewProcess()"]');

        submitBtn.disabled = true;

        submitBtn.innerHTML = '<i class="bi bi-spinner-border spinner-border-sm me-2"></i>Oluşturuluyor...';



        fetch('/admin/create-process', {

            method: 'POST',

            headers: {

                'Content-Type': 'application/json',

            },

            body: JSON.stringify(formData)

        })

            .then(response => response.json())

            .then(data => {

                if (data.success) {

                    showToast('success', 'Süreç başarıyla oluşturuldu!', 'Başarılı');

                    const modal = bootstrap.Modal.getInstance(document.getElementById('newProcessModal'));

                    if (modal) modal.hide();

                    if (typeof cleanupOverlayAndBackdrop === 'function') cleanupOverlayAndBackdrop();

                    setTimeout(function () { location.reload(); }, 1500);

                } else {

                    showToast('error', data.message, 'Hata');
                    if (typeof cleanupOverlayAndBackdrop === 'function') cleanupOverlayAndBackdrop();

                }

            })

            .catch(function (error) {

                console.error('Error:', error);
                showToast('error', 'Süreç oluşturulurken hata oluştu!', 'Bağlantı Hatası');
                if (typeof cleanupOverlayAndBackdrop === 'function') cleanupOverlayAndBackdrop();

            })

            .finally(function () {

                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="bi bi-save-fill me-2"></i>Süreç Oluştur';

            });

    }



    // Kurum seçimine göre kullanıcıları filtrele

    function filterUsersByKurum(kurumId, selectId) {

        const select = document.getElementById(selectId);

        if (!select) return;

        const options = select.querySelectorAll('option');



        options.forEach(option => {

            if (option.value === '') return; // Boş seçenek her zaman görünür



            const userKurumId = option.getAttribute('data-kurum-id');

            if (!kurumId || userKurumId === kurumId) {

                option.style.display = 'block';

            } else {

                option.style.display = 'none';

            }

        });



        // Seçimi sıfırla (multiple select'lerde güvenli)

        Array.from(select.options).forEach(opt => {

            opt.selected = false;

        });

    }



    // Süreç düzenleme fonksiyonu

    function editProcess(processId) {

        console.log('Süreç düzenleme başladı, ID:', processId);



        // Süreç bilgilerini al

        fetch(`/admin/get-process/${processId}`)

            .then(response => response.json())

            .then(data => {

                console.log('Süreç verileri yüklendi:', data);



                if (data.success) {

                    const surec = data.surec;

                    console.log('Süreç liderleri:', surec.liderler);

                    console.log('Süreç üyeleri:', surec.uyeler);

                    console.log('Süreç alt stratejileri:', surec.alt_stratejiler);

                    document.getElementById('edit_surec_id').value = surec.id;

                    document.getElementById('edit_ad').value = surec.ad;

                    var editParentEl = document.getElementById('edit_parent_id');
                    if (editParentEl) {
                        Array.from(editParentEl.options).forEach(function (opt) { opt.disabled = false; });
                        editParentEl.value = surec.parent_id || '';
                        var forbiddenIds = [surec.id].concat(surec.descendant_ids || []);
                        Array.from(editParentEl.options).forEach(function (opt) {
                            var vid = opt.value ? parseInt(opt.value, 10) : null;
                            if (vid && forbiddenIds.indexOf(vid) !== -1) opt.disabled = true;
                        });
                    }
                    document.getElementById('edit_dokuman_no').value = surec.dokuman_no || '';

                    document.getElementById('edit_rev_no').value = surec.rev_no || '';

                    document.getElementById('edit_rev_tarihi').value = surec.rev_tarihi || '';

                    document.getElementById('edit_ilk_yayin_tarihi').value = surec.ilk_yayin_tarihi || '';

                    document.getElementById('edit_baslangic_tarihi').value = surec.baslangic_tarihi || '';

                    document.getElementById('edit_bitis_tarihi').value = surec.bitis_tarihi || '';

                    document.getElementById('edit_durum').value = surec.durum;

                    document.getElementById('edit_ilerleme').value = surec.ilerleme || 0;

                    document.getElementById('edit_baslangic_siniri').value = surec.baslangic_siniri || '';

                    document.getElementById('edit_bitis_siniri').value = surec.bitis_siniri || '';

                    document.getElementById('edit_aciklama').value = surec.aciklama || '';

                    var editWeightEl = document.getElementById('edit_weight');
                    if (editWeightEl) editWeightEl.value = (surec.weight != null && surec.weight !== '') ? surec.weight : '';

                    // Çoklu lider seçimi için verileri yükle

                    loadDüzenleSurecLiderler(surec);



                    // Çoklu üye seçimi için verileri yükle

                    loadDüzenleSurecUyeler(surec);



                    // Alt strateji seçimi için verileri yükle

                    loadDüzenleProcessStratejiler(surec);

                    // Bağlı alt süreçleri listele (tıklayınca o sürece geç)
                    fillEditAltSureclerList(data.alt_surecler || []);

                    const modal = new bootstrap.Modal(document.getElementById('editSurecModal'));

                    modal.show();

                } else {

                    showToast('error', data.message || 'Süreç bilgileri yüklenirken bir hata oluştu', 'Hata');
                    if (typeof cleanupOverlayAndBackdrop === 'function') cleanupOverlayAndBackdrop();

                }

            })

            .catch(function (error) {

                console.error('Error:', error);
                handleAjaxError(error, 'Süreç bilgileri yüklenirken bir hata oluştu');
                if (typeof cleanupOverlayAndBackdrop === 'function') cleanupOverlayAndBackdrop();

            });

    }



    // Düzenleme formunda mevcut liderleri yükle

    function loadDüzenleProcessLiderler(surec) {

        console.log('loadDüzenleProcessLiderler çağrıldı');

        const target = document.getElementById('edit_lider_ids');

        console.log('edit_lider_ids elementi:', target);

        if (!target) {

            console.error('edit_lider_ids elementi bulunamadı!');

            return;

        }

        target.innerHTML = '';



        console.log('Lider yükleme işlemi başladı:', surec.liderler);



        if (surec.liderler && surec.liderler.length > 0) {

            console.log('Lider sayısı:', surec.liderler.length);

            surec.liderler.forEach((lider, index) => {

                console.log(`Lider ${index + 1}:`, lider);

                const option = new Option(lider.username, lider.id);

                console.log('Oluşturulan option:', option);

                console.log('Option eklenmeden önce target.options.length:', target.options.length);

                target.add(option);

                console.log('Option eklendikten sonra target.options.length:', target.options.length);

            });

        } else {

            console.log('Lider bulunamadı');

        }



        console.log('Lider yükleme tamamlandı');

    }



    // Düzenleme formunda mevcut üyeleri yükle

    function loadDüzenleProcessUyeler(surec) {

        console.log('loadDüzenleProcessUyeler çağrıldı');

        const target = document.getElementById('edit_uye_ids');

        console.log('edit_uye_ids elementi:', target);

        if (!target) {

            console.error('edit_uye_ids elementi bulunamadı!');

            return;

        }

        target.innerHTML = '';



        console.log('Üye yükleme işlemi başladı:', surec.uyeler);



        if (surec.uyeler && surec.uyeler.length > 0) {

            console.log('Üye sayısı:', surec.uyeler.length);

            surec.uyeler.forEach((uye, index) => {

                console.log(`Üye ${index + 1}:`, uye);

                const option = new Option(uye.username, uye.id);

                target.add(option);

            });

        } else {

            console.log('Üye bulunamadı');

        }



        console.log('Üye yükleme tamamlandı');

    }



    // Düzenleme formunda mevcut stratejileri yükle

    function loadDüzenleProcessStratejiler(surec) {

        const target = document.getElementById('edit_strateji_ids');

        target.innerHTML = '';



        console.log('Strateji yükleme işlemi başladı:', surec.alt_stratejiler);



        if (surec.alt_stratejiler && surec.alt_stratejiler.length > 0) {

            console.log('Strateji sayısı:', surec.alt_stratejiler.length);



            // Ana stratejilere göre grupla

            const groupedStrategies = {};

            surec.alt_stratejiler.forEach((strateji, index) => {

                console.log(`Strateji ${index + 1}:`, strateji);



                const mainStrategyAd = strateji.ana_strateji.ad;

                if (!groupedStrategies[mainStrategyAd]) {

                    groupedStrategies[mainStrategyAd] = [];

                }

                groupedStrategies[mainStrategyAd].push({

                    id: strateji.id,

                    name: strateji.ad

                });

            });



            // Her ana strateji için grup oluştur

            Object.keys(groupedStrategies).forEach(mainStrategyAd => {

                const strategies = groupedStrategies[mainStrategyAd];



                // Ana strateji başlığı (optgroup benzeri)

                const mainStrategyDiv = document.createElement('div');

                mainStrategyDiv.className = 'strategy-group';

                mainStrategyDiv.innerHTML = `

                <div class="strategy-group-header">

                    <strong>${mainStrategyAd}</strong>

                </div>

            `;



                // Alt stratejileri ekle

                strategies.forEach(strategy => {

                    const strategyDiv = document.createElement('div');

                    strategyDiv.className = 'strategy-item';

                    strategyDiv.setAttribute('data-strategy-id', strategy.id);

                    strategyDiv.innerHTML = `

                    <div class="strategy-sub">${strategy.name}</div>

                `;

                    strategyDiv.onclick = () => toggleDüzenleStrategySelection(strategy.id);

                    strategyDiv.ondblclick = () => removeDüzenleStrategyItem(strategy.id);

                    mainStrategyDiv.appendChild(strategyDiv);

                });



                target.appendChild(mainStrategyDiv);

            });

        } else {

            console.log('Strateji bulunamadı');

        }



        console.log('Strateji yükleme tamamlandı');

    }



    // Lider ekleme fonksiyonu (açık modal içinden)

    function addDüzenleLiderler() {

        const modal = document.querySelector('.modal.show');

        const source = modal ? modal.querySelector('#edit_lider_source') : document.getElementById('edit_lider_source');

        const target = modal ? modal.querySelector('#edit_lider_ids') : document.getElementById('edit_lider_ids');

        if (!source || !target) { showToast('warning', 'Form alanı bulunamadı.', 'Uyarı'); return; }

        const selected = Array.from(source.selectedOptions);



        console.log('Lider ekleme işlemi başladı');

        console.log('Seçilen liderler:', selected.map(opt => ({ value: opt.value, text: opt.text })));



        if (selected.length === 0) {

            showToast('warning', 'Lütfen önce sol taraftan lider seçin!', 'Uyarı');

            return;

        }



        let addedCount = 0;

        selected.forEach(opt => {

            // Zaten eklenmemiş ise ekle

            if (!Array.from(target.options).find(o => o.value === opt.value)) {

                const newOpt = new Option(opt.text, opt.value);

                target.add(newOpt);

                addedCount++;

                console.log(`Lider eklendi: ${opt.text}`);

            } else {

                console.log(`Lider zaten mevcut: ${opt.text}`);

            }

        });



        if (addedCount > 0) {

            showToast('success', `${addedCount} lider eklendi!`, 'Başarılı');

        } else {

            showToast('warning', 'Seçilen liderler zaten mevcut!', 'Uyarı');

        }



        console.log('Lider ekleme tamamlandı');

    }



    // Lider çıkarma fonksiyonu (açık modal içinden)

    function removeDüzenleLiderler() {

        const modal = document.querySelector('.modal.show');

        const target = modal ? modal.querySelector('#edit_lider_ids') : document.getElementById('edit_lider_ids');

        if (!target) { showToast('warning', 'Form alanı bulunamadı.', 'Uyarı'); return; }

        const selected = Array.from(target.selectedOptions);



        console.log('Lider çıkarma işlemi başladı');

        console.log('Çıkarılacak liderler:', selected.map(opt => ({ value: opt.value, text: opt.text })));



        if (selected.length === 0) {

            showToast('warning', 'Lütfen önce sağ taraftan çıkarılacak lideri seçin!', 'Uyarı');

            return;

        }



        const removedCount = selected.length;

        selected.forEach(opt => {

            opt.remove();

            console.log(`Lider çıkarıldı: ${opt.text}`);

        });



        showToast('success', `${removedCount} lider çıkarıldı!`, 'Başarılı');

        console.log('Lider çıkarma tamamlandı');

    }



    // Süreç güncelleme fonksiyonu

    function updateProcess() {

        const processId = document.getElementById('editProcessId').value;



        // Çoklu lider/üye/strateji seçimi (açık modal içinden)

        const modal = document.querySelector('.modal.show');

        const stratejiContainer = modal ? modal.querySelector('#edit_strateji_ids') : document.getElementById('edit_strateji_ids');

        const liderSelect = modal ? modal.querySelector('#edit_lider_ids') : document.getElementById('edit_lider_ids');

        const uyeSelect = modal ? modal.querySelector('#edit_uye_ids') : document.getElementById('edit_uye_ids');

        const liderIds = liderSelect ? Array.from(liderSelect.options).map(opt => opt.value) : [];

        const uyeIds = uyeSelect ? Array.from(uyeSelect.options).map(opt => opt.value) : [];

        const stratejiIds = stratejiContainer ? Array.from(stratejiContainer.querySelectorAll('.strategy-item')).map(item => item.getAttribute('data-strategy-id')) : [];



        console.log('Güncelleme işlemi başladı');

        console.log('Seçilen liderler:', liderIds);

        console.log('Seçilen üyeler:', uyeIds);



        const formData = {

            ad: document.getElementById('editProcessAd').value.trim(),

            lider_ids: liderIds, // Çoklu lider seçimi

            uye_ids: uyeIds, // Çoklu üye seçimi

            strateji_ids: stratejiIds, // Çoklu strateji seçimi

            dokuman_no: document.getElementById('editProcessDokuman').value.trim(),

            rev_no: document.getElementById('editProcessRevizyon').value.trim(),

            rev_tarihi: document.getElementById('editProcessRevTarihi').value,

            ilk_yayin_tarihi: document.getElementById('editProcessIlkYayinTarihi').value,

            durum: document.getElementById('editProcessDurum').value,

            ilerleme: document.getElementById('editProcessIlerleme').value,

            baslangic_tarihi: document.getElementById('editProcessBaslangic').value,

            bitis_tarihi: document.getElementById('editProcessBitis').value,

            baslangic_siniri: document.getElementById('editProcessBaslangicSiniri').value.trim(),

            bitis_siniri: document.getElementById('editProcessBitisSiniri').value.trim(),

            aciklama: document.getElementById('editProcessAciklama').value.trim()

        };



        // Zorunlu alan kontrolü

        if (!formData.ad || liderIds.length === 0) {

            showToast('warning', 'Lütfen süreç adı ve en az bir lider seçin!', 'Eksik Bilgi');

            return;

        }



        const submitBtn = document.querySelector('button[onclick="updateProcess()"]');

        submitBtn.disabled = true;

        submitBtn.innerHTML = '<i class="bi bi-spinner-border spinner-border-sm me-2"></i>Güncelleniyor...';



        fetch('/admin/update-process/' + processId, {

            method: 'PUT',

            headers: { 'Content-Type': 'application/json' },

            body: JSON.stringify(formData)

        })

            .then(function (r) { return r.json().then(function (data) { return { status: r.status, data: data }; }); })

            .then(function (res) {

                var data = res.data;

                if (data.success) {

                    showToast('success', 'Süreç başarıyla güncellendi!', 'Başarılı');

                    if (typeof cleanupOverlayAndBackdrop === 'function') cleanupOverlayAndBackdrop();

                    setTimeout(function () { location.reload(); }, 1500);

                } else {

                    showToast('error', data.message, res.status === 400 ? 'Validasyon Hatası' : 'Hata');
                    if (typeof cleanupOverlayAndBackdrop === 'function') cleanupOverlayAndBackdrop();

                }

            })

            .catch(function (error) {

                console.error('Error:', error);
                showToast('error', 'Süreç güncellenirken hata oluştu!', 'Hata');
                if (typeof cleanupOverlayAndBackdrop === 'function') cleanupOverlayAndBackdrop();

            })

            .finally(function () {

                submitBtn.disabled = false;

                submitBtn.innerHTML = '<i class="bi bi-save-fill me-2"></i>Güncelle';

            });

    }



    // Toast bildirim fonksiyonu

    function showToast(type, message, title = '') {

        // Bootstrap toast container oluştur

        let toastContainer = document.getElementById('toast-container');

        if (!toastContainer) {

            toastContainer = document.createElement('div');

            toastContainer.id = 'toast-container';

            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';

            toastContainer.style.zIndex = '9999';

            document.body.appendChild(toastContainer);

        }



        // Toast ID oluştur

        const toastId = 'toast-' + Tarih.now();



        // Toast HTML oluştur

        const toastHTML = `

        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">

            <div class="toast-header bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : type === 'info' ? 'info' : 'primary'} text-white">

                <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : type === 'info' ? 'info-circle' : 'bell'} me-2"></i>

                <strong class="me-auto">${title || (type === 'success' ? 'Başarılı' : type === 'error' ? 'Hata' : type === 'info' ? 'Bilgi' : 'Bildirim')}</strong>

                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>

            </div>

            <div class="toast-body">

                ${message}

            </div>

        </div>

    `;



        // Toast'u container'a ekle

        toastContainer.insertAdjacentHTML('beforeend', toastHTML);



        // Toast'u göster

        const toastElement = document.getElementById(toastId);

        const toast = new bootstrap.Toast(toastElement, {

            autohide: true,

            delay: type === 'error' ? 5000 : 3000

        });



        toast.show();



        // Toast kapandığında DOM'dan kaldır

        toastElement.addEventListener('hidden.bs.toast', function () {

            toastElement.remove();

        });

    }

