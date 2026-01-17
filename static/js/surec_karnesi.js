// console.log('=== SÜREÇ KARNESİ SCRIPT BAŞLADI ===');

    let mevcutSurecId = null;
    let mevcutYil = new Date().getFullYear();
    let mevcutPeriyot = 'ceyrek'; // Varsayılan çeyrek
    let mevcutAy = new Date().getMonth() + 1; // Varsayılan olarak mevcut ay (1-12)
    let surecBilgileri = {}; // Süreç ID'sine göre is_lider bilgisini sakla
    let kullaniciRolu = null; // Kullanıcının sistemsel rolü

    // Toast bildirim fonksiyonu
    function showToast(message, type = 'info', duration = 5000) {
        // type: 'success', 'error', 'warning', 'info'
        let toastContainer = document.getElementById('toastContainer');

        // Eğer container yoksa oluştur
        if (!toastContainer) {
            // Container'ı body'nin sonuna ekle
            const containerDiv = document.createElement('div');
            containerDiv.className = 'toast-container position-fixed top-0 end-0 p-3';
            containerDiv.style.zIndex = '9999';
            containerDiv.innerHTML = '<div id="toastContainer"></div>';
            document.body.appendChild(containerDiv);
            toastContainer = document.getElementById('toastContainer');
        }

        if (!toastContainer) {
            // Hala bulunamadıysa alert kullan (fallback)
            console.error('Toast container bulunamadı!', message);
            return;
        }

        const toastId = 'toast-' + Date.now();

        const bgClass = {
            'success': 'bg-success',
            'error': 'bg-danger',
            'warning': 'bg-warning',
            'info': 'bg-info'
        }[type] || 'bg-info';

        const icon = {
            'success': 'bi-check-circle-fill',
            'error': 'bi-x-circle-fill',
            'warning': 'bi-exclamation-triangle-fill',
            'info': 'bi-info-circle-fill'
        }[type] || 'bi-info-circle-fill';

        const toastHtml = `
        <div id="${toastId}" class="toast ${bgClass} text-white" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="${duration}">
            <div class="toast-header ${bgClass} text-white border-0">
                <i class="bi ${icon} me-2"></i>
                <strong class="me-auto">${type === 'success' ? 'Başarılı' : type === 'error' ? 'Hata' : type === 'warning' ? 'Uyarı' : 'Bilgi'}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = document.getElementById(toastId);
        if (toastElement) {
            const toast = new bootstrap.Toast(toastElement);
            toast.show();

            // Toast kapandıktan sonra DOM'dan kaldır
            toastElement.addEventListener('hidden.bs.toast', () => {
                toastElement.remove();
            });
        }
    }

    // Confirm dialog yerine toast ile onay modalı
    function showConfirmToast(message, onConfirm, onCancel = null) {
        let toastContainer = document.getElementById('toastContainer');

        // Eğer container yoksa oluştur
        if (!toastContainer) {
            // Container'ı body'nin sonuna ekle
            const containerDiv = document.createElement('div');
            containerDiv.className = 'toast-container position-fixed top-0 end-0 p-3';
            containerDiv.style.zIndex = '9999';
            containerDiv.innerHTML = '<div id="toastContainer"></div>';
            document.body.appendChild(containerDiv);
            toastContainer = document.getElementById('toastContainer');
        }

        if (!toastContainer) {
            // Hala bulunamadıysa confirm kullan (fallback)
            console.error('Toast container bulunamadı!');
            if (confirm(message)) {
                if (onConfirm) onConfirm();
            } else {
                if (onCancel) onCancel();
            }
            return;
        }

        const toastId = 'toast-confirm-' + Date.now();

        const toastDiv = document.createElement('div');
        toastDiv.id = toastId;
        toastDiv.className = 'toast bg-warning text-dark';
        toastDiv.setAttribute('role', 'alert');
        toastDiv.setAttribute('aria-live', 'assertive');
        toastDiv.setAttribute('aria-atomic', 'true');
        toastDiv.setAttribute('data-bs-autohide', 'false');

        toastDiv.innerHTML = `
        <div class="toast-header bg-warning text-dark border-0">
            <i class="bi bi-question-circle-fill me-2"></i>
            <strong class="me-auto">Onay</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            <p class="mb-3">${message}</p>
            <div class="d-flex gap-2">
                <button class="btn btn-sm btn-success confirm-yes-btn">
                    <i class="bi bi-check-lg"></i> Evet
                </button>
                <button class="btn btn-sm btn-secondary confirm-no-btn">
                    <i class="bi bi-x-lg"></i> Hayır
                </button>
            </div>
        </div>
    `;

        toastContainer.appendChild(toastDiv);
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);

        // Event listener'ları ekle
        const yesBtn = toastElement.querySelector('.confirm-yes-btn');
        const noBtn = toastElement.querySelector('.confirm-no-btn');

        yesBtn.addEventListener('click', () => {
            toast.hide();
            if (onConfirm) onConfirm();
            toastElement.remove();
        });

        noBtn.addEventListener('click', () => {
            toast.hide();
            if (onCancel) onCancel();
            toastElement.remove();
        });

        // Close butonuna da listener ekle
        toastElement.querySelector('.btn-close').addEventListener('click', () => {
            if (onCancel) onCancel();
        });

        toast.show();

        // Toast kapandıktan sonra DOM'dan kaldır
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    // Periyot değiştirme fonksiyonu - BASİT!
    function changePeriyot() {
        mevcutPeriyot = document.getElementById('periyotSelect').value;
        console.log('Periyot değişti:', mevcutPeriyot);

        // Haftalık ve günlük görünümler için mevcut ayı ayarla
        if (mevcutPeriyot === 'haftalik' || mevcutPeriyot === 'gunluk') {
            mevcutAy = new Date().getMonth() + 1; // Varsayılan olarak mevcut ay
        }
        
        // Navigasyon label'ını güncelle
        updatePeriyotNavigasyonLabel();

        if (mevcutSurecId) {
            // Tablo başlıklarını güncelle
            updateTableHeaders();
            // Performans göstergelerini yeniden yükle
            loadPerformansGostergeleri(mevcutSurecId, mevcutYil);
        }
    }
    
    // Navigasyon label'ını güncelle
    function updatePeriyotNavigasyonLabel() {
        const label = document.getElementById('periyotNavigasyonLabel');
        
        if (!label) return;
        
        const periyotAdiMap = {
            'ceyrek': 'Çeyrek Görünümü',
            'yillik': 'Yıllık Görünümü',
            'aylik': 'Aylık Görünümü',
            'haftalik': 'Haftalık Görünümü',
            'gunluk': 'Günlük Görünümü'
        };
        
        if (mevcutPeriyot === 'haftalik' || mevcutPeriyot === 'gunluk') {
            const aylar = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'];
            const ayAdi = aylar[mevcutAy - 1] || '';
            label.textContent = `${mevcutYil} - ${ayAdi} (${periyotAdiMap[mevcutPeriyot]})`;
        } else {
            label.textContent = `${mevcutYil} - ${periyotAdiMap[mevcutPeriyot] || mevcutPeriyot}`;
        }
    }
    
    // Akıllı navigasyon: Periyoda göre doğru fonksiyonu çağır
    function navigate(direction) {
        if (mevcutPeriyot === 'haftalik' || mevcutPeriyot === 'gunluk') {
            navigateAy(direction);
        } else {
            navigatePeriyot(direction);
        }
    }

    // Periyot navigasyon fonksiyonları
    // Ay navigasyonu (haftalık ve günlük görünümler için)
    function navigateAy(direction) {
        if (mevcutPeriyot !== 'haftalik' && mevcutPeriyot !== 'gunluk') {
            return; // Sadece haftalık ve günlük görünümlerde çalışır
        }

        if (direction === 'prev') {
            // Önceki ay
            if (mevcutAy > 1) {
                mevcutAy = mevcutAy - 1;
            } else {
                // Önceki yılın Aralık ayı
                mevcutAy = 12;
                mevcutYil = mevcutYil - 1;
                const yilSelect = document.getElementById('yilSelect');
                if (yilSelect) {
                    yilSelect.value = mevcutYil;
                }
                document.getElementById('yilBilgisi').textContent = mevcutYil;
            }
        } else {
            // Sonraki ay
            if (mevcutAy < 12) {
                mevcutAy = mevcutAy + 1;
            } else {
                // Sonraki yılın Ocak ayı
                mevcutAy = 1;
                mevcutYil = mevcutYil + 1;
                const yilSelect = document.getElementById('yilSelect');
                if (yilSelect) {
                    yilSelect.value = mevcutYil;
                }
                document.getElementById('yilBilgisi').textContent = mevcutYil;
            }
        }

        // Verileri yeniden yükle
        if (mevcutSurecId) {
            updatePeriyotNavigasyonLabel();  // Label'ı güncelle
            loadPerformansGostergeleri(mevcutSurecId, mevcutYil);
        }
    }

    function navigatePeriyot(direction) {
        // Yıl referansını güncelle
        const yilSelect = document.getElementById('yilSelect');
        let yeniYil = parseInt(mevcutYil);

        if (mevcutPeriyot === 'yillik') {
            // Yıllık görünüm: Önceki/Sonraki yıl
            if (direction === 'prev') {
                yeniYil = yeniYil - 1;
            } else {
                yeniYil = yeniYil + 1;
            }
        } else if (mevcutPeriyot === 'ceyrek') {
            // Çeyreklik görünüm: Önceki/Sonraki yılın çeyrekleri
            if (direction === 'prev') {
                yeniYil = yeniYil - 1;
            } else {
                yeniYil = yeniYil + 1;
            }
        } else if (mevcutPeriyot === 'aylik') {
            // Aylık görünüm: Önceki/Sonraki yılın ayları
            if (direction === 'prev') {
                yeniYil = yeniYil - 1;
            } else {
                yeniYil = yeniYil + 1;
            }
        } else if (mevcutPeriyot === 'haftalik' || mevcutPeriyot === 'gunluk') {
            // Haftalık ve günlük görünüm: navigateAy kullanılacak, burada bir şey yapma
            return;
        }

        // Yıl değiştiyse güncelle
        if (yeniYil !== mevcutYil) {
            mevcutYil = yeniYil;
            yilSelect.value = mevcutYil;
            document.getElementById('yilBilgisi').textContent = mevcutYil;
        }

        // Tabloyu yenile
        if (mevcutSurecId) {
            updatePeriyotNavigasyonLabel();  // Label'ı güncelle
            updateTableHeaders();
            loadPerformansGostergeleri(mevcutSurecId, mevcutYil);
        }
    }

    // Tablo başlıklarını periyoda göre güncelle
    function updateTableHeaders() {
        const thead = document.querySelector('#performansTable thead');
        let headerHtml = '';

        // Tarih hesaplama fonksiyonları
        const getTarihEtiketi = (periyotTipi, indeks) => {
            const yil = mevcutYil;
            const aylar = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'];
            const bugun = new Date();
            const simdikiYil = bugun.getFullYear();
            const simdikiAy = bugun.getMonth(); // 0-11
            const simdikiGun = bugun.getDate();
            const simdikiHaftaGunu = bugun.getDay(); // 0=Pazar, 1=Pazartesi, ..., 6=Cumartesi

            // Eğer seçilen yıl gelecek yıl veya geçmiş yıl ise, o yılın başlangıcını referans al
            const referansYil = yil;
            const referansAy = (yil === simdikiYil) ? simdikiAy : 0; // Aynı yılsa mevcut ayı, değilse Ocak ayını kullan
            const referansGun = (yil === simdikiYil && referansAy === simdikiAy) ? simdikiGun : 1;

            if (periyotTipi === 'ceyrek') {
                // Çeyrek ay aralıkları: I.Çeyrek=Ocak-Mart, II.Çeyrek=Nisan-Haziran, vb.
                const ceyrekAylar = [
                    [1, 3],   // I. Çeyrek: Ocak-Mart
                    [4, 6],   // II. Çeyrek: Nisan-Haziran
                    [7, 9],   // III. Çeyrek: Temmuz-Eylül
                    [10, 12]  // IV. Çeyrek: Ekim-Aralık
                ];
                const [baslangicAy, bitisAy] = ceyrekAylar[indeks - 1];

                // Eğer mevcut çeyrekteysek, gerçek tarihleri göster
                let gosterilecekBaslangicAy = baslangicAy;
                let gosterilecekBitisAy = bitisAy;

                if (yil === simdikiYil) {
                    const mevcutCeyrek = Math.floor(simdikiAy / 3) + 1; // Hangi çeyrek (1-4)
                    if (mevcutCeyrek === indeks) {
                        // Mevcut çeyrekteyiz, gerçek ay bilgisini kullan
                        gosterilecekBaslangicAy = Math.floor(simdikiAy / 3) * 3 + 1;
                        gosterilecekBitisAy = Math.min(gosterilecekBaslangicAy + 2, 12);
                    }
                }

                return `${aylar[gosterilecekBaslangicAy - 1]}-${aylar[gosterilecekBitisAy - 1]} ${yil}`;
            } else if (periyotTipi === 'aylik') {
                // Mevcut ayı göster
                let gosterilecekAy = indeks - 1;
                if (yil === simdikiYil) {
                    // Aynı yıldaysak, en azından mevcut ayı göster
                    if (indeks - 1 === simdikiAy || indeks - 1 < simdikiAy) {
                        gosterilecekAy = indeks - 1;
                    }
                }
                return `${aylar[gosterilecekAy]} ${yil}`;
            } else if (periyotTipi === 'haftalik') {
                // BASİT: Sadece hafta numarası
                return `Hafta ${indeks}`;
            } else if (periyotTipi === 'gunluk') {
                // BASİT: Sadece gün numarası
                return `Gün ${indeks}`;
            } else if (periyotTipi === 'yillik') {
                return `${yil}`;
            }
            return '';
        };

        // Periyot adını Türkçe'ye çevir
        const getPeriyotAdi = (periyot) => {
            const periyotMap = {
                'ceyrek': 'Çeyreklik',
                'yillik': 'Yıllık',
                'aylik': 'Aylık',
                'haftalik': 'Haftalık',
                'gunluk': 'Günlük'
            };
            return periyotMap[periyot] || periyot;
        };

        if (mevcutPeriyot === 'ceyrek') {
            headerHtml = `
            <tr>
                <th rowspan="2" class="col-code">Kodu</th>
                <th rowspan="2" class="col-description">Ana Strateji</th>
                <th rowspan="2" class="col-description">Alt Strateji</th>
                <th rowspan="2" class="col-description">Performans Adı</th>
                <th rowspan="2" class="col-description">Göst. Türü</th>
                <th rowspan="2" class="col-description">Hedef Belirl. Yön.</th>
                <th rowspan="2" class="col-weight">Göst. Ağırlığı (%)</th>
                <th rowspan="2" class="col-description">Birim</th>
                <th rowspan="2" class="col-period">Ölçüm Per.</th>
                <th rowspan="2" class="col-target">Önceki Yıl Ort.</th>
                <th rowspan="2" class="col-target">Hedef</th>
                <th colspan="3">I. Çeyrek<br><small>${getTarihEtiketi('ceyrek', 1)}</small></th>
                <th colspan="3">II. Çeyrek<br><small>${getTarihEtiketi('ceyrek', 2)}</small></th>
                <th colspan="3">III. Çeyrek<br><small>${getTarihEtiketi('ceyrek', 3)}</small></th>
                <th colspan="3">IV. Çeyrek<br><small>${getTarihEtiketi('ceyrek', 4)}</small></th>
                <th rowspan="2" class="col-target">Yıl Sonu</th>
                <th rowspan="2" class="col-target">Başarı Puanı</th>
                <th rowspan="2" class="col-target">Ağırlıklı Başarı Puanı</th>
                <th rowspan="2" class="col-method">Hesaplama Yöntemi</th>
            </tr>
            <tr>
                <th class="col-quarter">Hedef</th>
                <th class="col-quarter">Gerç.</th>
                <th class="col-quarter">Durum</th>
                <th class="col-quarter">Hedef</th>
                <th class="col-quarter">Gerç.</th>
                <th class="col-quarter">Durum</th>
                <th class="col-quarter">Hedef</th>
                <th class="col-quarter">Gerç.</th>
                <th class="col-quarter">Durum</th>
                <th class="col-quarter">Hedef</th>
                <th class="col-quarter">Gerç.</th>
                <th class="col-quarter">Durum</th>
            </tr>
        `;
        } else if (mevcutPeriyot === 'yillik') {
            // Yılı veri'den al, yoksa mevcutYil kullan
            let gosterilecekYil = mevcutYil;

            headerHtml = `
            <tr>
                <th class="col-code">Kodu</th>
                <th class="col-description">Performans Adı</th>
                <th class="col-target">Hedef</th>
                <th class="col-period">Periyot</th>
                <th class="col-weight">Ağırlık (%)</th>
                <th class="col-method">Hesaplama Yöntemi</th>
                <th class="col-quarter">${gosterilecekYil}<br><small>Hedef</small></th>
                <th class="col-quarter">Gerç.</th>
                <th class="col-quarter">Durum</th>
                <th class="col-actions">İşlemler</th>
            </tr>
        `;
        } else if (mevcutPeriyot === 'aylik') {
            const aylar = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara'];
            headerHtml = `
            <tr>
                <th rowspan="2" class="col-code">Kodu</th>
                <th rowspan="2" class="col-description">Performans Adı</th>
                <th rowspan="2" class="col-target">Hedef</th>
                <th rowspan="2" class="col-period">Periyot</th>
                <th rowspan="2" class="col-weight">Ağırlık (%)</th>
                <th rowspan="2" class="col-method">Hesaplama Yöntemi</th>
                <th colspan="3">${aylar[0]}<br><small>${getTarihEtiketi('aylik', 1)}</small></th>
                ${aylar.slice(1, -1).map((ay, index) => `<th colspan="3">${ay}<br><small>${getTarihEtiketi('aylik', index + 2)}</small></th>`).join('')}
                <th colspan="3">${aylar[11]}<br><small>${getTarihEtiketi('aylik', 12)}</small></th>
                <th rowspan="2" class="col-actions">İşlemler</th>
            </tr>
            <tr>
                ${aylar.map(() => `
                    <th class="col-quarter">Hedef</th>
                    <th class="col-quarter">Gerç.</th>
                    <th class="col-quarter">Durum</th>
                `).join('')}
            </tr>
        `;
        } else if (mevcutPeriyot === 'haftalik' || mevcutPeriyot === 'gunluk') {
            // Haftalık ve günlük başlıklar API'den veri geldikten sonra dinamik oluşturulacak
            const aylar = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'];
            const ayAdi = aylar[mevcutAy - 1] || 'Aylık';
            headerHtml = `
            <tr>
                <th colspan="100" class="text-center text-muted py-3">
                    <i class="bi bi-hourglass-split"></i> ${ayAdi} ${mevcutYil} - Veriler yükleniyor...
                </th>
            </tr>
        `;
        }

        thead.innerHTML = headerHtml;
    }

    // Debug fonksiyonu
    function debugSurecData() {
        console.log('=== DEBUG SÜREÇ VERİLERİ ===');

        fetch('/debug/surec-data')
            .then(r => r.json())
            .then(data => {
                console.log('Debug Data:', data);

                if (data.success) {
                    let message = `Kullanıcı: ${data.user_info.username} (${data.user_info.sistem_rol})\n`;
                    message += `Kurum ID: ${data.user_info.kurum_id}\n`;
                    message += `Toplam Süreç: ${data.toplam_surec}\n\n`;

                    if (data.surecler.length > 0) {
                        data.surecler.forEach(surec => {
                            message += `Süreç: ${surec.ad} (ID: ${surec.id})\n`;
                            message += `  PG Sayısı: ${surec.pg_sayisi}\n`;
                            message += `  Faaliyet Sayısı: ${surec.faaliyet_sayisi}\n`;

                            if (surec.pg_listesi.length > 0) {
                                message += `  PG'ler:\n`;
                                surec.pg_listesi.forEach(pg => {
                                    message += `    - ${pg.ad} (${pg.kodu})\n`;
                                });
                            }

                            if (surec.faaliyet_listesi.length > 0) {
                                message += `  Faaliyetler:\n`;
                                surec.faaliyet_listesi.forEach(faaliyet => {
                                    message += `    - ${faaliyet.ad}\n`;
                                });
                            }
                            message += '\n';
                        });
                    } else {
                        message += 'Hiç süreç bulunamadı!';
                    }

                    showToast(message, 'info', 10000);
                } else {
                    showToast('Debug hatası: ' + data.message, 'error');
                }
            })
            .catch(err => {
                console.error('Debug hatası:', err);
                showToast('Debug hatası: ' + err.message, 'error');
            });
    }

    // Sayfa yüklendiğinde kullanıcının süreçlerini getir
    document.addEventListener('DOMContentLoaded', function () {
        console.log('DOM Yüklendi!');

        // Yıl dropdown'unu mevcut yıl ile güncelle (opsiyon yoksa ekle)
        const yilSelect = document.getElementById('yilSelect');
        const currentYear = new Date().getFullYear();
        if (yilSelect) {
            const hasCurrent = Array.from(yilSelect.options).some(opt => parseInt(opt.value) === currentYear);
            if (!hasCurrent) {
                const opt = new Option(currentYear.toString(), currentYear.toString());
                // En üste ekle ki varsayılan seçilsin
                yilSelect.insertBefore(opt, yilSelect.firstChild);
            }
            yilSelect.value = currentYear;
        }
        mevcutYil = currentYear;
        const yilBilgisi = document.getElementById('yilBilgisi');
        if (yilBilgisi) {
            yilBilgisi.textContent = currentYear;
        }

        loadKullaniciSurecleri();

        // Form event listener'ları ekle (güvenlik için)
        const editPerformansForm = document.getElementById('editPerformansForm');
        if (editPerformansForm) {
            editPerformansForm.addEventListener('submit', function (e) {
                e.preventDefault();
                updatePerformansGostergesi(e);
            });
        }

        const editFaaliyetForm = document.getElementById('editFaaliyetForm');
        if (editFaaliyetForm) {
            editFaaliyetForm.addEventListener('submit', function (e) {
                e.preventDefault();
                updateFaaliyet(e);
            });
        }
    });

    // Kullanıcının üye olduğu süreçleri getir
    function loadKullaniciSurecleri() {
        console.log('loadKullaniciSurecleri() çağrıldı');
        fetch('/api/kullanici/sureclerim')
            .then(r => {
                console.log('API yanıtı geldi, status:', r.status);
                return r.json();
            })
            .then(data => {
                console.log('API datası:', data);
                const select = document.getElementById('surecSelect');
                select.innerHTML = '<option value="">-- Süreç Seçiniz --</option>';

                // Kullanıcı rolünü sakla
                if (data.user_role) {
                    kullaniciRolu = data.user_role;
                }

                if (data.success && data.surecler.length > 0) {
                    console.log('Süreç sayısı:', data.surecler.length);

                    // Ana süreç seçimi için
                    data.surecler.forEach(surec => {
                        const option = document.createElement('option');
                        option.value = surec.id;
                        option.textContent = surec.ad;
                        option.dataset.dokumanNo = surec.dokuman_no || '-';
                        option.dataset.revNo = surec.rev_no || '-';
                        option.dataset.isLider = surec.is_lider ? 'true' : 'false';
                        select.appendChild(option);

                        // Süreç bilgilerini sakla
                        surecBilgileri[surec.id] = {
                            is_lider: surec.is_lider || false,
                            is_uye: surec.is_uye || false
                        };
                    });

                    // VGS (Veri Giriş Sihirbazı) için süreç seçimi
                    const wizardSelect = document.getElementById('wizard-surec-select');
                    if (wizardSelect) {
                        wizardSelect.innerHTML = '<option value="">-- Süreç Seçiniz --</option>';
                        data.surecler.forEach(surec => {
                            const option = document.createElement('option');
                            option.value = surec.id;
                            option.textContent = surec.ad;
                            wizardSelect.appendChild(option);
                        });
                    }
                } else {
                    console.log('Süreç bulunamadı veya success=false');
                    select.innerHTML = '<option value="">Henüz bir süreçte yer almıyorsunuz</option>';

                    // VGS için de boş yap
                    const wizardSelect = document.getElementById('wizard-surec-select');
                    if (wizardSelect) {
                        wizardSelect.innerHTML = '<option value="">Henüz bir süreçte yer almıyorsunuz</option>';
                    }
                }
            })
            .catch(err => {
                console.error('Süreçler yüklenemedi:', err);
            });
    }

    // Süreç karnesi verilerini yükle
    function loadSurecKarnesi() {
        const surecSelect = document.getElementById('surecSelect');
        const surecId = surecSelect.value;

        if (!surecId) {
            document.getElementById('surecAdi').textContent = 'Süreç seçiniz...';
            document.getElementById('dokumanNo').textContent = '-';
            document.getElementById('revNo').textContent = '-';
            document.getElementById('performansTbody').innerHTML = '<tr><td colspan="27" class="text-center text-muted py-5"><i class="bi bi-inbox" style="font-size: 3rem;"></i><p class="mt-3">Lütfen bir süreç seçiniz</p></td></tr>';
            document.getElementById('faaliyetTbody').innerHTML = '<tr><td colspan="15" class="text-center text-muted py-5"><i class="bi bi-inbox" style="font-size: 3rem;"></i><p class="mt-3">Lütfen bir süreç seçiniz</p></td></tr>';
            // Butonları gizle
            toggleAddButtons(false);
            return;
        }

        mevcutSurecId = surecId;
        mevcutYil = document.getElementById('yilSelect').value;
        mevcutPeriyot = document.getElementById('periyotSelect').value;

        // Haftalık ve günlük görünümler için mevcut ayı ayarla
        if (mevcutPeriyot === 'haftalik' || mevcutPeriyot === 'gunluk') {
            mevcutAy = new Date().getMonth() + 1; // Varsayılan olarak mevcut ay
        }

        // Süreç bilgilerini güncelle
        const selectedOption = surecSelect.options[surecSelect.selectedIndex];
        document.getElementById('surecAdi').textContent = selectedOption.textContent;
        document.getElementById('dokumanNo').textContent = selectedOption.dataset.dokumanNo;
        document.getElementById('revNo').textContent = selectedOption.dataset.revNo;
        document.getElementById('yilBilgisi').textContent = mevcutYil;

        // Yazma butonları sadece yönetim rollerinde görünür
        const isYonetim = kullaniciRolu && ['admin', 'kurum_yoneticisi', 'ust_yonetim'].includes(kullaniciRolu);
        toggleAddButtons(isYonetim);

        // Tablo başlıklarını güncelle
        updateTableHeaders();
        
        // Navigasyon label'ını güncelle
        updatePeriyotNavigasyonLabel();

        // Süreç sağlık skorunu yükle
        loadSurecSaglikSkoru(surecId, mevcutYil);

        // Performans göstergelerini yükle
        loadPerformansGostergeleri(surecId, mevcutYil);

        // Faaliyetleri yükle
        loadFaaliyetler(surecId, mevcutYil);
    }

    // PG ve Faaliyet ekleme butonlarını göster/gizle
    function toggleAddButtons(isLider) {
        // Üst kısımdaki butonlar
        const pgEkleBtn = document.querySelector('button[onclick="showAddPerformansForm()"]');
        const faaliyetEkleBtn = document.querySelector('button[onclick="showAddFaaliyetForm()"]');
        const wizardBtn = document.getElementById('openDataEntryWizardBtn');

        // Card header'daki butonlar
        const pgEkleCardBtn = document.querySelector('.card-header button[onclick="showAddPerformansForm()"]');
        const faaliyetEkleCardBtn = document.querySelector('.card-header button[onclick="showAddFaaliyetForm()"]');

        // Butonları göster/gizle
        const buttons = [wizardBtn, pgEkleBtn, faaliyetEkleBtn, pgEkleCardBtn, faaliyetEkleCardBtn];
        buttons.forEach(btn => {
            if (btn) {
                if (isLider) {
                    btn.style.display = '';
                } else {
                    btn.style.display = 'none';
                }
            }
        });
    }

    // Sütun gösterim kontrolü için fonksiyonlar
    let sutunVisibilityMap = {
        'col-code': true,
        'col-description-1': true, // Ana Strateji
        'col-description-2': true, // Alt Strateji
        'col-description-3': true, // Performans Adı
        'col-description-4': true, // Göst. Türü
        'col-description-5': true, // Hedef Belirl. Yön.
        'col-description-6': true, // Birim
        'col-weight': true,
        'col-period': true,
        'col-target-1': true, // Önceki Yıl Ort.
        'col-target-2': true, // Hedef
        'col-method': true
    };

    // Sütun indexlerini sabit olarak tanımla
    const SUTUN_INDEXLER = {
        'col-code': 0,
        'col-description-1': 1, // Ana Strateji
        'col-description-2': 2, // Alt Strateji
        'col-description-3': 3, // Performans Adı
        'col-description-4': 4, // Göst. Türü
        'col-description-5': 5, // Hedef Belirl. Yön.
        'col-weight': 6,
        'col-description-6': 7, // Birim
        'col-period': 8,
        'col-target-1': 9, // Önceki Yıl Ort.
        'col-target-2': 10, // Hedef
        'col-method': null // Dinamik hesaplanacak - çeyrek sütunlarından sonra gelir
    };

    function toggleSutunVisibility(className, index = null) {
        // Sütun key'ini oluştur
        const sutunKey = index !== null ? `${className}-${index}` : className;

        // Checkbox'ı bul ve durumunu al
        let checkbox = null;
        if (index !== null) {
            checkbox = document.querySelector(`input[data-sutun="${className}"][data-sutun-index="${index}"]`);
        } else {
            checkbox = document.querySelector(`input[data-sutun="${className}"]:not([data-sutun-index])`);
        }

        if (checkbox) {
            sutunVisibilityMap[sutunKey] = checkbox.checked;
            saveSutunVisibilityToStorage();
        }

        // Sütun indexini belirle
        let columnIndex = null;
        if (className === 'col-method') {
            // Hesaplama Yöntemi için: İlk satırda col-method class'ına sahip son sütunu bul
            const firstRow = document.querySelector('#performansTable tbody tr');
            if (firstRow) {
                const cells = firstRow.querySelectorAll('td');
                // col-method class'ına sahip son sütunu bul
                for (let i = cells.length - 1; i >= 0; i--) {
                    if (cells[i].classList.contains('col-method')) {
                        columnIndex = i;
                        break;
                    }
                }
            }
            if (columnIndex === null) {
                console.warn('Hesaplama Yöntemi sütunu bulunamadı');
                return;
            }
        } else {
            columnIndex = SUTUN_INDEXLER[sutunKey];
        }

        if (columnIndex === null || columnIndex === undefined) {
            console.warn(`Sütun index bulunamadı: ${sutunKey}`);
            return;
        }

        // Tüm satırlarda bu sütunu gizle/göster
        const isVisible = sutunVisibilityMap[sutunKey] !== false;

        // Header'daki sütunları gizle/göster - data-column-index attribute'una göre
        const thead = document.querySelector('#performansTable thead');
        if (thead) {
            thead.querySelectorAll('tr').forEach(tr => {
                const headers = tr.querySelectorAll('th, td');
                headers.forEach((th, idx) => {
                    const thColumnIndex = th.getAttribute('data-column-index');
                    if (thColumnIndex !== null && parseInt(thColumnIndex) === columnIndex) {
                        th.style.display = isVisible ? '' : 'none';
                    } else if (thColumnIndex === null && idx === columnIndex && th.classList.contains(className)) {
                        // data-column-index yoksa index ve class'a göre kontrol et
                        if (index !== null) {
                            // col-description ve col-target için index kontrolü yapılmalı
                            // Şimdilik sadece index'e göre kontrol edelim
                            th.style.display = isVisible ? '' : 'none';
                        } else {
                            th.style.display = isVisible ? '' : 'none';
                        }
                    }
                });
            });
        }

        // Body'deki tüm satırlarda bu sütunu gizle/göster
        const tbody = document.querySelector('#performansTable tbody');
        if (tbody) {
            tbody.querySelectorAll('tr').forEach(tr => {
                const cells = tr.querySelectorAll('td');
                if (cells[columnIndex]) {
                    cells[columnIndex].style.display = isVisible ? '' : 'none';
                }
            });
        }
    }

    function saveSutunVisibilityToStorage() {
        try {
            const key = `sutun_visibility_${mevcutSurecId}_${mevcutYil}`;
            localStorage.setItem(key, JSON.stringify(sutunVisibilityMap));
        } catch (e) {
            console.error('Sütun görünürlük ayarları kaydedilemedi:', e);
        }
    }

    function loadSutunVisibilityFromStorage() {
        try {
            const key = `sutun_visibility_${mevcutSurecId}_${mevcutYil}`;
            const saved = localStorage.getItem(key);
            if (saved) {
                const savedMap = JSON.parse(saved);
                // Kaydedilmiş ayarları güncelle
                Object.keys(savedMap).forEach(key => {
                    sutunVisibilityMap[key] = savedMap[key];
                });

                // Checkbox'ları güncelle
                Object.keys(sutunVisibilityMap).forEach(key => {
                    const isVisible = sutunVisibilityMap[key] !== false;
                    // Key'i parse et (örn: "col-description-1" -> className="col-description", index=1)
                    if (key.includes('-') && /^\d+$/.test(key.split('-').pop())) {
                        const parts = key.split('-');
                        const index = parts[parts.length - 1];
                        const className = parts.slice(0, -1).join('-');
                        const checkbox = document.querySelector(`input[data-sutun="${className}"][data-sutun-index="${index}"]`);
                        if (checkbox) {
                            checkbox.checked = isVisible;
                        }
                    } else {
                        // col-code, col-weight, col-period, col-method gibi
                        const checkbox = document.querySelector(`input[data-sutun="${key}"]:not([data-sutun-index])`);
                        if (checkbox) {
                            checkbox.checked = isVisible;
                        }
                    }
                });

                // Tüm sütunları güncelle (DOM'a uygula)
                Object.keys(sutunVisibilityMap).forEach(key => {
                    const parts = key.split('-');
                    if (parts.length >= 3 && /^\d+$/.test(parts[parts.length - 1])) {
                        const className = parts.slice(0, -1).join('-');
                        const index = parseInt(parts[parts.length - 1]);
                        toggleSutunVisibility(className, index);
                    } else {
                        toggleSutunVisibility(key);
                    }
                });
            }
        } catch (e) {
            console.error('Sütun görünürlük ayarları yüklenemedi:', e);
        }
    }

    // Performans göstergelerini yükle
    // PG gösterim kontrolü için fonksiyonlar (ESKİ - ARTIK KULLANILMIYOR)
    let pgVisibilityMap = {}; // {pgId: true/false}

    function updatePGCheckboxes(gostergeler) {
        const container = document.getElementById('pgCheckboxContainer');
        if (!container) return;

        container.innerHTML = '';

        if (!gostergeler || gostergeler.length === 0) {
            container.innerHTML = '<span class="text-muted small">PG bulunamadı</span>';
            return;
        }

        // LocalStorage'dan kaydedilmiş görünürlük ayarlarını yükle
        const savedVisibility = loadPGVisibilityFromStorage();

        gostergeler.forEach(pg => {
            const checkboxId = `pg_checkbox_${pg.id}`;
            const isChecked = savedVisibility[pg.id] !== undefined ? savedVisibility[pg.id] : true; // Varsayılan: hepsi görünür

            pgVisibilityMap[pg.id] = isChecked;

            const checkboxDiv = document.createElement('div');
            checkboxDiv.className = 'form-check form-check-inline';
            checkboxDiv.innerHTML = `
            <input class="form-check-input" type="checkbox" id="${checkboxId}" 
                   data-pg-id="${pg.id}" ${isChecked ? 'checked' : ''} 
                   onchange="togglePGVisibility(${pg.id})">
            <label class="form-check-label" for="${checkboxId}">
                ${pg.ad || `PG ${pg.id}`}
            </label>
        `;
            container.appendChild(checkboxDiv);
        });
    }

    function togglePGVisibility(pgId) {
        const checkbox = document.getElementById(`pg_checkbox_${pgId}`);
        if (!checkbox) return;

        pgVisibilityMap[pgId] = checkbox.checked;
        savePGVisibilityToStorage();

        // Tabloyu yeniden yükle (API'yi tekrar çağırmadan, sadece görünürlüğü değiştir)
        filterAndRenderPGTable();
    }

    function getVisiblePGIds() {
        return Object.keys(pgVisibilityMap)
            .filter(pgId => pgVisibilityMap[pgId] === true)
            .map(id => parseInt(id));
    }

    function savePGVisibilityToStorage() {
        try {
            const key = `pg_visibility_${mevcutSurecId}_${mevcutYil}`;
            localStorage.setItem(key, JSON.stringify(pgVisibilityMap));
        } catch (e) {
            console.error('PG görünürlük ayarları kaydedilemedi:', e);
        }
    }

    function loadPGVisibilityFromStorage() {
        try {
            const key = `pg_visibility_${mevcutSurecId}_${mevcutYil}`;
            const saved = localStorage.getItem(key);
            return saved ? JSON.parse(saved) : {};
        } catch (e) {
            console.error('PG görünürlük ayarları yüklenemedi:', e);
            return {};
        }
    }

    function filterAndRenderPGTable() {
        // Mevcut tablodaki satırların görünürlüğünü güncelle
        if (mevcutSurecId && mevcutYil) {
            const visiblePGIds = getVisiblePGIds();

            // Mevcut tüm satırları al
            const tbody = document.getElementById('performansTbody');
            if (!tbody) return;

            // Her satırı kontrol et ve görünürlüğünü ayarla
            tbody.querySelectorAll('tr[data-pg-id]').forEach(tr => {
                const pgIdAttr = tr.getAttribute('data-pg-id');
                if (pgIdAttr) {
                    const pgId = parseInt(pgIdAttr);
                    const isVisible = visiblePGIds.length === 0 || visiblePGIds.includes(pgId);
                    tr.style.display = isVisible ? '' : 'none';
                }
            });
        }
    }


    function loadPerformansGostergeleri(surecId, yil) {
        console.log('=== PERFORMANS GÖSTERGELERİ YÜKLEME BAŞLADI ===');
        console.log('Süreç ID:', surecId, 'Yıl:', yil, 'Periyot:', mevcutPeriyot, 'Ay:', mevcutAy);

        // API URL - yıl, periyot ve (haftalık/günlük için) ay
        let url = `/api/surec/${surecId}/karne/performans?yil=${yil}&periyot=${mevcutPeriyot}`;

        // Haftalık ve günlük görünümlerde ay parametresi ekle
        if ((mevcutPeriyot === 'haftalik' || mevcutPeriyot === 'gunluk') && mevcutAy) {
            url += `&ay=${mevcutAy}`;
        }

        console.log('API URL:', url);

        fetch(url)
            .then(r => {
                console.log('API Response Status:', r.status);
                if (!r.ok) {
                    throw new Error(`HTTP ${r.status}: ${r.statusText}`);
                }
                return r.json();
            })
            .then(data => {
                console.log('API Data:', data);
                console.log('Success:', data.success);
                console.log('Göstergeler:', data.gostergeler);
                console.log('Gösterge sayısı:', data.gostergeler ? data.gostergeler.length : 'undefined');

                const tbody = document.getElementById('performansTbody');

                if (!data.success) {
                    console.error('API başarısız:', data.message);
                    tbody.innerHTML = '<tr><td colspan="27" class="text-center text-danger py-3">API Hatası: ' + (data.message || 'Bilinmeyen hata') + '</td></tr>';
                    return;
                }

                if (!data.gostergeler || data.gostergeler.length === 0) {
                    console.log('Gösterge yok');
                    tbody.innerHTML = '<tr><td colspan="27" class="text-center text-muted py-3">Bu süreçte henüz performans göstergesi bulunmuyor</td></tr>';
                    return;
                }

                tbody.innerHTML = '';

                console.log('Gösterge sayısı:', data.gostergeler.length);

                // Başarı puanı aralıkları var mı kontrol et (en az bir PG'de varsa göster)
                let basariPuaniVarMi = false;
                data.gostergeler.forEach(pg => {
                    // basari_puani_araliklari JSON string veya object olabilir
                    let araliklar = pg.basari_puani_araliklari;
                    if (typeof araliklar === 'string' && araliklar) {
                        try {
                            araliklar = JSON.parse(araliklar);
                        } catch (e) {
                            araliklar = null;
                        }
                    }
                    if (araliklar && typeof araliklar === 'object' && Object.keys(araliklar).length > 0) {
                        basariPuaniVarMi = true;
                    }
                });

                // Başarı puanı sütunlarını göster/gizle (CSS class ile)
                const thead = document.querySelector('#performansTable thead');
                if (thead) {
                    thead.querySelectorAll('th').forEach(th => {
                        const thText = th.textContent.trim();
                        if (thText === 'Başarı Puanı' || thText === 'Ağırlıklı Başarı Puanı') {
                            if (basariPuaniVarMi) {
                                th.classList.remove('d-none');
                            } else {
                                th.classList.add('d-none');
                            }
                        }
                    });
                }

                // Haftalık ve günlük için başlıkları dinamik oluştur (veri dizisini gönder)
                if (mevcutPeriyot === 'haftalik' || mevcutPeriyot === 'gunluk') {
                    if (data.gostergeler.length > 0 && data.gostergeler[0].veriler) {
                        updateTableHeadersDynamic(data.gostergeler[0].veriler);
                    }
                }

                // Tüm PG'leri render et
                const allGostergeler = data.gostergeler;

                allGostergeler.forEach((pg, index) => {
                    const tr = document.createElement('tr');
                    tr.className = pg.onemli ? 'row-important' : (index % 2 === 0 ? 'row-normal' : 'row-alt');
                    tr.setAttribute('data-pg-id', pg.id); // PG ID'sini data attribute olarak ekle

                    // pgAdEscaped'i döngü dışında tanımla
                    const pgAdEscaped = (pg.ad || '').replace(/'/g, "\\'");

                    // Hedef değeri: Eğer hesaplanmış hedef varsa onu, yoksa orijinal hedefi göster
                    // 2 ondalık basamak göster (eğer tam sayı değilse)
                    let hedefGosterim = pg.gosterim_hedef_deger !== undefined && pg.gosterim_hedef_deger !== null
                        ? pg.gosterim_hedef_deger
                        : pg.hedef_deger;

                    // Sayısal değer ise ve tam sayı değilse 2 ondalık göster
                    if (hedefGosterim !== null && hedefGosterim !== undefined && hedefGosterim !== '-') {
                        const hedefNum = parseFloat(hedefGosterim);
                        if (!isNaN(hedefNum)) {
                            // Tam sayı değilse 2 ondalık göster
                            if (hedefNum % 1 !== 0) {
                                hedefGosterim = parseFloat(hedefNum.toFixed(2));
                            } else {
                                hedefGosterim = hedefNum;
                            }
                        }
                    }

                    // Periyot adını gösterim periyoduna göre göster
                    const periyotAdlari = {
                        'ceyrek': 'Çeyreklik',
                        'yillik': 'Yıllık',
                        'aylik': 'Aylık',
                        'haftalik': 'Haftalık',
                        'gunluk': 'Günlük'
                    };
                    const gosterimPeriyotAdi = periyotAdlari[mevcutPeriyot] || mevcutPeriyot;

                    // Hesaplama yöntemi adını formatla
                    const hesaplamaYontemi = pg.veri_toplama_yontemi || 'Ortalama';
                    const hesaplamaYontemiAdlari = {
                        'Toplam': 'Toplam',
                        'Toplama': 'Toplam',
                        'Ortalama': 'Ortalama',
                        'Son Değer': 'Son Değer',
                        'Son Deger': 'Son Değer'
                    };
                    const hesaplamaYontemiGosterim = hesaplamaYontemiAdlari[hesaplamaYontemi] || hesaplamaYontemi;

                    // Target method adını formatla (DH, HKY, SH, vb.)
                    const targetMethodAdlari = {
                        'DH': 'DH',
                        'HKY': 'HKY',
                        'SH': 'SH',
                        'RG': 'RG',
                        'HK': 'HK',
                        'SGH': 'SGH'
                    };
                    const targetMethodGosterim = pg.target_method ? (targetMethodAdlari[pg.target_method] || pg.target_method) : '-';

                    // Ağırlığı float olarak göster (0-1 arası ise 100 ile çarp)
                    let agirlikGosterim = pg.agirlik || 0;
                    if (agirlikGosterim > 0 && agirlikGosterim < 1) {
                        agirlikGosterim = (agirlikGosterim * 100).toFixed(2);
                    }

                    let html = `
                    <td class="col-code">${pg.kodu || 'PG-' + pg.id}</td>
                    <td class="col-description">${pg.ana_strateji_kodu || '-'}</td>
                    <td class="col-description">${pg.alt_strateji_kodu || '-'}</td>
                    <td class="col-description">${pg.ad}</td>
                    <td class="col-description">${pg.gosterge_turu || '-'}</td>
                    <td class="col-description">${targetMethodGosterim}</td>
                    <td class="col-weight">${agirlikGosterim}%</td>
                    <td class="col-description">${pg.olcum_birimi || '-'}</td>
                    <td class="col-period">${gosterimPeriyotAdi}</td>
                    <td class="col-target">${pg.onceki_yil_ortalamasi !== null && pg.onceki_yil_ortalamasi !== undefined ? pg.onceki_yil_ortalamasi.toFixed(2) : '-'}</td>
                    <td class="col-target">${hedefGosterim || '-'} ${pg.olcum_birimi || ''}</td>
                `;

                    // Periyoda göre veri hücreleri oluştur
                    html += generatePeriyotCells(pg, pgAdEscaped);

                    // Yıl sonu gerçekleşen değer
                    const yilSonuGerceklesen = pg.yil_sonu_gerceklesen !== null && pg.yil_sonu_gerceklesen !== undefined ? pg.yil_sonu_gerceklesen.toFixed(2) : '-';
                    html += `<td class="col-target">${yilSonuGerceklesen}</td>`;

                    // Başarı puanı (sadece aralıklar varsa göster)
                    if (basariPuaniVarMi) {
                        const basariPuaniGosterim = pg.basari_puani !== null && pg.basari_puani !== undefined ? pg.basari_puani : '-';
                        html += `<td class="col-target"><strong>${basariPuaniGosterim}</strong></td>`;

                        // Ağırlıklı başarı puanı
                        const agirlikliBasariPuaniGosterim = pg.agirlikli_basari_puani !== null && pg.agirlikli_basari_puani !== undefined ? pg.agirlikli_basari_puani.toFixed(2) : '-';
                        html += `<td class="col-target"><strong>${agirlikliBasariPuaniGosterim}</strong></td>`;
                    } else {
                        // Başarı puanı yoksa boş hücreler ekle (başlıklarla uyum için ama gizli)
                        html += `<td class="col-target d-none"></td>`;
                        html += `<td class="col-target d-none"></td>`;
                    }

                    // Hesaplama yöntemi
                    html += `<td class="col-method"><span class="badge bg-info">${hesaplamaYontemiGosterim}</span></td>`;

                    // İşlemler sütunu (sadece yönetim rolleri)
                    const isYonetim = kullaniciRolu && ['admin', 'kurum_yoneticisi', 'ust_yonetim'].includes(kullaniciRolu);
                    html += `
                    <td class="col-actions">
                        ${isYonetim ? `
                        <div class="btn-group" role="group">
                            <button type="button" class="btn btn-sm btn-info text-white" onclick="openHedefDagitimModal(${pg.id}, '${pgAdEscaped}', ${pg.hedef_deger || 0})" title="Hedefi Dağıt">
                                <i class="bi bi-diagram-3"></i>
                            </button>
                            <button type="button" class="btn btn-sm btn-warning" onclick="editPerformansGostergesi(${pg.id})" title="Düzenle">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button type="button" class="btn btn-sm btn-danger" onclick="deletePerformansGostergesi(${pg.id}, '${pgAdEscaped}')" title="Sil">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                        ` : '<span class="text-muted small">-</span>'}
                    </td>
                `;

                    tr.innerHTML = html;
                    tbody.appendChild(tr);
                // console.log(`PG ${index + 1} eklendi`);
            });

            // console.log('=== PERFORMANS GÖSTERGELERİ YÜKLEME BİTTİ ===');
                updateDashboardSummary(data.gostergeler);

                // Trend Grafiğini güncelle
                updateTrendChart(data.gostergeler);

                // Tablo render edildikten sonra sütun görünürlük ayarlarını uygula
                setTimeout(() => {
                    loadSutunVisibilityFromStorage();
                }, 100);
            })
            .catch(err => {
                console.error('!!! PERFORMANS GÖSTERGELERİ HATA !!!', err);
                console.error('Hata detayı:', err.message);
                console.error('Stack trace:', err.stack);

                const tbody = document.getElementById('performansTbody');
                tbody.innerHTML = '<tr><td colspan="27" class="text-center text-danger py-3">Hata: ' + err.message + '</td></tr>';
            });
    }

    // --- DASHBOARD WIDGET FUNCTIONS ---

    // Dashboard Widgetlarını Güncelle
    function updateDashboardSummary(gostergeler) {
        if (!gostergeler) return;

        const parseNumberTR = (val) => {
            if (val === null || val === undefined) return null;
            if (typeof val === 'number') return isNaN(val) ? null : val;
            let s = String(val).trim();
            if (!s) return null;
            s = s.replace(/\s/g, '').replace('%', '');
            // 1.234,56 -> 1234.56
            if (s.includes(',') && s.includes('.')) {
                s = s.replace(/\./g, '').replace(',', '.');
            } else {
                s = s.replace(',', '.');
            }
            const n = parseFloat(s);
            return isNaN(n) ? null : n;
        };

        // "Total KPI" burada en azından hedefi sayısal olanları sayalım
        let total = 0;
        let success = 0;
        let risk = 0; // Kısmen
        let fail = 0; // Başarısız

        let totalScore = 0;
        let countedKpis = 0;

        gostergeler.forEach(pg => {
            // Yıl sonu gerçekleşen varsa onu kullan
            let gerceklesen = pg.yil_sonu_gerceklesen !== null ? parseNumberTR(pg.yil_sonu_gerceklesen) : null;

            // Yoksa son veriyi bul (veriler arrayinden)
            if (gerceklesen === null && pg.veriler && pg.veriler.length > 0) {
                // Veriler içinde gerçekleşen değeri olan son kaydı bul
                // Veriler genelde oluşturulma tarihine göre değil periyoda göre sıralıdır
                // Ama biz dolu olan son veriyi arıyoruz
                for (let i = pg.veriler.length - 1; i >= 0; i--) {
                    if (pg.veriler[i].gerceklesen_deger !== null && pg.veriler[i].gerceklesen_deger !== undefined) {
                        const val = parseNumberTR(pg.veriler[i].gerceklesen_deger);
                        if (val !== null) {
                            gerceklesen = val;
                            break;
                        }
                    }
                }
            }

            // Periyot seçimine göre backend'in hesapladığı hedefi öncelikle kullan
            const hedef = (pg.gosterim_hedef_deger !== undefined && pg.gosterim_hedef_deger !== null)
                ? parseNumberTR(pg.gosterim_hedef_deger)
                : parseNumberTR(pg.hedef_deger);

            if (hedef !== null && hedef !== 0) {
                total++;
            }

            // Eğer geçerli bir karşılaştırma yapılabiliyorsa
            if (gerceklesen !== null && hedef !== null && hedef !== 0) {
                // Yüzde hesapla
                let yuzde = (gerceklesen / hedef) * 100;

                // Direction kontrolü (Eğer "Decreasing" ise mantık ters işler - şimdilik varsayılan Increasing)
                // Gelecekte pg.direction eklenebilir.

                if (yuzde >= 100) {
                    success++;
                } else if (yuzde >= 75) {
                    risk++;
                } else {
                    fail++;
                }

                // Skor katkısı (capped at 120%)
                totalScore += Math.min(yuzde, 120);
                countedKpis++;
            } else {
                // Veri yoksa veya hedef 0 ise Nötr sayılır
            }
        });

        // UI Güncelleme - Sayılar
        const totalEl = document.getElementById('totalKPIConunt');
        if (totalEl) totalEl.textContent = total;

        const successEl = document.getElementById('successKPICount');
        if (successEl) successEl.textContent = success;

        const riskEl = document.getElementById('riskKPICount');
        if (riskEl) {
            riskEl.textContent = risk + fail; // Riskli + Başarısız toplamını göster (Kırmızı kartta)
            // Veya sadece fail? Kullanıcı "Riskli" başlığı altında toplam sorunlu sayısını görmek isteyebilir.
        }

        // Genel Hedef Tutma Oranı Barı
        let totalSuccessRate = countedKpis > 0 ? (totalScore / countedKpis) : 0;
        const pgHedefBar = document.getElementById('pgHedefBar');
        const pgHedefText = document.getElementById('pgHedefText');

        if (pgHedefBar && pgHedefText) {
            pgHedefBar.style.width = `${Math.min(totalSuccessRate, 100)}%`;
            pgHedefText.textContent = `${totalSuccessRate.toFixed(1)}%`;

            // Renk ayarla
            pgHedefBar.className = 'progress-bar ' + (totalSuccessRate >= 80 ? 'bg-success' : (totalSuccessRate >= 50 ? 'bg-warning' : 'bg-danger'));
        }

        // Pie Chart Çizimi
        drawKPIStatusChart(success, risk, fail);
    }

    let kpiChartInstance = null;
    function drawKPIStatusChart(success, risk, fail) {
        const ctx = document.getElementById('kpiStatusChart');
        if (!ctx) return;

        const legendEl = document.getElementById('kpiStatusLegend');

        // Eğer veri yoksa boş bir chart gösterme, placeholder göster veya 0'lar
        if (success + risk + fail === 0) {
            // Veri yok durumu
            if (kpiChartInstance) kpiChartInstance.destroy();
            // Canvas'ı temizle
            const cctx = ctx.getContext('2d');
            cctx.clearRect(0, 0, ctx.width, ctx.height);
            if (legendEl) {
                legendEl.innerHTML = '<div class="text-muted small">Veri yok</div>';
            }
            return;
        }

        if (kpiChartInstance) {
            kpiChartInstance.destroy();
        }

        kpiChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Başarılı', 'Kısmen', 'Başarısız'],
                datasets: [{
                    data: [success, risk, fail],
                    backgroundColor: ['#28a745', '#ffc107', '#dc3545'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            boxWidth: 10,
                            padding: 10,
                            font: { size: 11 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                let label = context.label || '';
                                let value = context.raw || 0;
                                let total = context.dataset.data.reduce((a, b) => a + b, 0);
                                let percentage = Math.round((value / total) * 100) + '%';
                                return `${label}: ${value} (${percentage})`;
                            }
                        }
                    }
                },
                cutout: '65%'
            }
        });

        if (legendEl) {
            legendEl.innerHTML = '';
        }
    }

    // Periyoda göre veri hücreleri oluştur - BASİT TAKVİM YAPISI
    function generatePeriyotCells(pg, pgAdEscaped) {
        let html = '';
        // Hedef değeri: Gösterim periyoduna göre hesaplanmış hedef varsa onu kullan
        let hedefDeger = pg.gosterim_hedef_deger !== undefined && pg.gosterim_hedef_deger !== null
            ? pg.gosterim_hedef_deger
            : pg.hedef_deger || '-';

        // Sayısal değer ise ve tam sayı değilse 2 ondalık göster
        if (hedefDeger !== null && hedefDeger !== undefined && hedefDeger !== '-') {
            const hedefNum = parseFloat(hedefDeger);
            if (!isNaN(hedefNum)) {
                // Tam sayı değilse 2 ondalık göster
                if (hedefNum % 1 !== 0) {
                    hedefDeger = parseFloat(hedefNum.toFixed(2));
                } else {
                    hedefDeger = hedefNum;
                }
            }
        }

        // Veri map'i oluştur (hızlı erişim için)
        const veriMap = {};
        if (pg.veriler && pg.veriler.length > 0) {
            pg.veriler.forEach(v => {
                if (mevcutPeriyot === 'ceyrek') {
                    veriMap[v.ceyrek] = v;
                } else if (mevcutPeriyot === 'yillik') {
                    veriMap['yillik'] = v;
                } else if (mevcutPeriyot === 'aylik') {
                    veriMap[v.ay] = v;
                } else if (mevcutPeriyot === 'haftalik') {
                    veriMap[v.hafta] = v;
                } else if (mevcutPeriyot === 'gunluk') {
                    veriMap[v.gun] = v;
                }
            });
        }

        if (mevcutPeriyot === 'ceyrek') {
            // 4 Çeyrek - HER ZAMAN 4 KOLON
            for (let ceyrek = 1; ceyrek <= 4; ceyrek++) {
                const veri = veriMap[ceyrek] || {};
                html += createVeriHucre(veri, hedefDeger);
            }
        } else if (mevcutPeriyot === 'yillik') {
            // 1 Yıl - HER ZAMAN 1 KOLON
            const veri = veriMap['yillik'] || {};
            html += createVeriHucre(veri, hedefDeger);
        } else if (mevcutPeriyot === 'aylik') {
            // 12 Ay - HER ZAMAN 12 KOLON
            for (let ay = 1; ay <= 12; ay++) {
                const veri = veriMap[ay] || {};
                html += createVeriHucre(veri, hedefDeger);
            }
        } else if (mevcutPeriyot === 'haftalik') {
            // AYIN HAFTALARI - Backend'den gelen veri dizisini sırasıyla kullan
            if (pg.veriler && pg.veriler.length > 0) {
                // Her veri için 3 hücre (Hedef, Gerç., Durum) oluştur
                pg.veriler.forEach(veri => {
                    html += createVeriHucre(veri, hedefDeger, `Hafta ${veri.hafta || ''}`);
                });
            }
        } else if (mevcutPeriyot === 'gunluk') {
            // AYIN GÜNLERİ - Backend'den gelen veri dizisini sırasıyla kullan
            if (pg.veriler && pg.veriler.length > 0) {
                // Her veri için 3 hücre (Hedef, Gerç., Durum) oluştur
                pg.veriler.forEach(veri => {
                    html += createVeriHucre(veri, hedefDeger, `Gün ${veri.gun || ''}`);
                });
            }
        }

        return html;
    }

    // Veri hücresi oluştur - Helper fonksiyon
    function createVeriHucre(veri, hedefDeger, titleSuffix = '') {
        const durumClass = getDurumClass(veri.durum_yuzdesi);
        // En son girilen verinin ID'sini al (veri_idleri dizisinin ilk elemanı)
        // Backend'de veriler en yeni önce (created_at desc) sıralanıyor
        const veriId = veri.veri_idleri && veri.veri_idleri.length > 0
            ? veri.veri_idleri[0]  // En son veri ID'si (backend'de ilk sırada)
            : null;
        // Tüm veri ID'lerini JSON string olarak data attribute'a ekle
        const veriIdleriJSON = veri.veri_idleri && veri.veri_idleri.length > 0
            ? JSON.stringify(veri.veri_idleri)
            : '[]';
        // veri_idleri dizisini güvenli şekilde kullan (null/undefined kontrolü)
        const veriIdleriArray = veri.veri_idleri && veri.veri_idleri.length > 0 ? veri.veri_idleri : [];
        const onclickHandler = veriIdleriArray.length > 0 ? `onclick="openPGVeriDetay([${veriIdleriArray.join(',')}])"` : '';
        const titleText = veri.kullanicilar && veri.kullanicilar.length > 0
            ? `Veri girenler: ${veri.kullanicilar.join(', ')}`
            : (titleSuffix || 'Veri detaylarını görmek için tıklayın');

        let kullaniciBilgisi = '';
        if (veri.kullanicilar && veri.kullanicilar.length > 0) {
            kullaniciBilgisi = `<br><small class="text-muted"><i class="bi bi-people"></i> ${veri.kullanicilar.join(', ')}</small>`;
        }

        return `
        <td>${veri.hedef_deger || hedefDeger}</td>
        <td class="clickable-cell" 
            ${onclickHandler}
            title="${titleText}"
            style="${veriId ? 'cursor: pointer;' : ''} background-color: ${veri.gerceklesen_deger ? '#e8f5e9' : '#fff3e0'};">
            ${veri.gerceklesen_deger ? `<strong>${veri.gerceklesen_deger}</strong>${veriId ? '<i class="fas fa-info-circle text-primary ms-1"></i>' : ''}${kullaniciBilgisi}` : '<strong>-</strong>'}
        </td>
        <td class="${durumClass}">${veri.durum || '-'}</td>
    `;
    }

    // Faaliyetleri yükle
    function loadFaaliyetler(surecId, yil) {
        fetch(`/api/surec/${surecId}/karne/faaliyetler?yil=${yil}`)
            .then(r => r.json())
            .then(data => {
                const tbody = document.getElementById('faaliyetTbody');

                if (!data.success || data.faaliyetler.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="16" class="text-center text-muted py-3">Bu süreçte henüz faaliyet bulunmuyor</td></tr>';
                    return;
                }

                tbody.innerHTML = '';

                data.faaliyetler.forEach((faaliyet, index) => {
                    const tr = document.createElement('tr');
                    tr.className = index % 2 === 0 ? 'row-normal' : 'row-alt';

                    let html = `
                    <td class="col-code">${index + 1}</td>
                    <td class="col-description">${faaliyet.ad}</td>
                `;

                    // 12 ay için checkbox hücreleri
                    for (let ay = 1; ay <= 12; ay++) {
                        const takip = faaliyet.takip.find(t => t.ay === ay) || {};
                        const checked = takip.gerceklesti ? 'X' : '';
                        const checkedClass = takip.gerceklesti ? 'text-success fw-bold' : 'text-muted';

                        html += `
                        <td class="checkbox-cell ${checkedClass}" 
                            data-faaliyet-id="${faaliyet.id}" 
                            data-surec-faaliyet-id="${faaliyet.surec_faaliyet_id}"
                            data-ay="${ay}"
                            onclick="toggleFaaliyet(this)">
                            ${checked}
                        </td>
                    `;
                    }

                    // ÖNE. kolonu (Öneri)
                    html += `<td><input type="text" class="form-control form-control-sm" 
                    value="${faaliyet.oneri || ''}" 
                    data-faaliyet-id="${faaliyet.id}" 
                    data-field="oneri"></td>`;

                    // İşlemler sütunu
                    const faaliyetAdEscaped = (faaliyet.ad || '').replace(/'/g, "\\'");
                    // Yetki kontrolü: Sadece yönetim rolleri edit/delete yapabilir
                    const isYetkili = kullaniciRolu && ['admin', 'kurum_yoneticisi', 'ust_yonetim'].includes(kullaniciRolu);

                    html += `
                    <td class="col-actions">
                        <div class="btn-group btn-group-sm" role="group">
                            ${isYetkili ? `
                                <button class="btn btn-outline-warning btn-sm" 
                                        onclick="editFaaliyet(${faaliyet.surec_faaliyet_id})" 
                                        title="Düzenle">
                                    <i class="bi bi-pencil"></i>
                                </button>
                                <button class="btn btn-outline-danger btn-sm" 
                                        onclick="deleteFaaliyet(${faaliyet.surec_faaliyet_id}, '${faaliyetAdEscaped}')" 
                                        title="Sil">
                                    <i class="bi bi-trash"></i>
                                </button>
                            ` : '<span class="text-muted small">-</span>'}
                        </div>
                    </td>
                `;

                    tr.innerHTML = html;
                    tbody.appendChild(tr);
                });
            })
            .catch(err => {
                console.error('Faaliyetler yüklenemedi:', err);
            });
    }

    // Durum yüzdesine göre CSS class döndür
    function getDurumClass(yuzde) {
        if (!yuzde) return '';
        if (yuzde >= 80) return 'status-success';
        if (yuzde >= 50) return 'status-warning';
        return 'status-danger';
    }

    // Gerçekleşen değer girildiğinde durumu hesapla
    function hesaplaDurum(input) {
        const pgId = input.dataset.pgId;
        const ceyrek = input.dataset.ceyrek;
        const row = input.closest('tr');

        // Hedef ve gerçekleşen değerleri al
        const hedefInput = row.querySelector(`input[data-pg-id="${pgId}"][data-ceyrek="${ceyrek}"][data-field="hedef"]`);
        const gerceklesenInput = input;

        const hedef = parseFloat(hedefInput.value) || 0;
        const gerceklesen = parseFloat(gerceklesenInput.value) || 0;

        if (hedef === 0) return;

        // Yüzde hesapla
        const yuzde = (gerceklesen / hedef) * 100;

        // Durum hücresini bul ve güncelle
        const durumCell = gerceklesenInput.closest('td').nextElementSibling;

        let durum, durumClass;
        if (yuzde >= 80) {
            durum = '✓ Başarılı';
            durumClass = 'status-success';
        } else if (yuzde >= 50) {
            durum = '◐ Kısmen';
            durumClass = 'status-warning';
        } else {
            durum = '✗ Başarısız';
            durumClass = 'status-danger';
        }

        durumCell.className = durumClass;
        durumCell.textContent = durum;
        durumCell.title = `${yuzde.toFixed(1)}%`;
    }

    // Faaliyet checkbox toggle
    function toggleFaaliyet(cell) {
        const faaliyetId = cell.dataset.faaliyetId || '0';
        const surecFaaliyetId = cell.dataset.surecFaaliyetId;
        const ay = cell.dataset.ay;
        const mevcutDurum = cell.textContent.trim() === 'X';
        const yeniDurum = !mevcutDurum;

        // Eğer bireysel faaliyet yoksa (id=0), önce oluştur
        if (faaliyetId === '0' && surecFaaliyetId) {
            // Backend'de otomatik oluşturacağız
            fetch(`/api/surec/${mevcutSurecId}/faaliyet/${surecFaaliyetId}/create-bireysel`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        cell.dataset.faaliyetId = data.bireysel_faaliyet_id;
                        // Şimdi takibi kaydet
                        saveFaaliyetTakip(data.bireysel_faaliyet_id, ay, yeniDurum, cell, mevcutDurum);
                    } else {
                        console.error('Bireysel faaliyet oluşturulamadı');
                        return;
                    }
                })
                .catch(err => {
                    console.error('Hata:', err);
                });
        } else {
            saveFaaliyetTakip(faaliyetId, ay, yeniDurum, cell, mevcutDurum);
        }
    }

    function saveFaaliyetTakip(faaliyetId, ay, yeniDurum, cell, mevcutDurum) {
        // Görsel güncelleme
        cell.textContent = yeniDurum ? 'X' : '';
        cell.className = yeniDurum ? 'checkbox-cell text-success fw-bold' : 'checkbox-cell text-muted';

        // Backend'e kaydet
        fetch(`/api/faaliyet/${faaliyetId}/takip`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                yil: mevcutYil,
                ay: parseInt(ay),
                gerceklesti: yeniDurum
            })
        })
            .then(r => r.json())
            .then(data => {
                if (!data.success) {
                    console.error('Faaliyet takip kaydedilemedi:', data.message);
                    // Geri al
                    cell.textContent = mevcutDurum ? 'X' : '';
                    cell.className = mevcutDurum ? 'checkbox-cell text-success fw-bold' : 'checkbox-cell text-muted';
                }
            })
            .catch(err => {
                console.error('Hata:', err);
            });
    }

    // Tüm verileri kaydet
    function kaydetTumVeriler() {
        if (!mevcutSurecId) {
            showToast('Lütfen önce bir süreç seçin!', 'warning');
            return;
        }

        const isYonetim = kullaniciRolu && ['admin', 'kurum_yoneticisi', 'ust_yonetim'].includes(kullaniciRolu);
        if (!isYonetim) {
            showToast('Bu işlem için yetkiniz yok!', 'error');
            return;
        }

        // Performans gösterge verilerini topla
        const pgVerileri = [];
        document.querySelectorAll('#performansTable input[data-pg-id]').forEach(input => {
            if (input.value.trim()) {  // Sadece dolu alanları kaydet
                pgVerileri.push({
                    pg_id: input.dataset.pgId,
                    surec_pg_id: input.dataset.surecPgId,
                    ceyrek: input.dataset.ceyrek,
                    field: input.dataset.field,
                    value: input.value
                });
            }
        });

        // Kaydet
        fetch(`/api/surec/${mevcutSurecId}/karne/kaydet`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                yil: mevcutYil,
                pg_verileri: pgVerileri
            })
        })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    showToast('✅ Tüm veriler kaydedildi!', 'success');
                    loadSurecKarnesi(); // Yenile
                } else {
                    showToast('❌ Hata: ' + data.message, 'error');
                }
            })
            .catch(err => {
                console.error('Kayıt hatası:', err);
                showToast('❌ Kayıt sırasında hata oluştu!', 'error');
            });
    }

    // ============================================
    // YENİ: PG VERİ DETAY MODAL FONKSİYONLARI
    // ============================================

    function showPGVeriDetay(surecPgId, ceyrek, pgAd, periyotAd) {
        console.log('PG Veri Detay Modal açılıyor:', { surecPgId, ceyrek, pgAd, periyotAd });

        // Modal bilgilerini doldur
        document.getElementById('detay-pg-ad').textContent = pgAd;
        document.getElementById('detay-periyot').textContent = periyotAd;
        document.getElementById('detay-yil').textContent = mevcutYil;

        // Geçmiş verileri yükle
        const container = document.getElementById('detay-veriler-liste');
        container.innerHTML = '<div class="text-center py-3"><div class="spinner-border spinner-border-sm" role="status"></div><p class="text-muted small mt-2">Veriler yükleniyor...</p></div>';

        // API'den verileri al
        fetch(`/api/surec/karne/pg-veri-detay?surec_pg_id=${surecPgId}&ceyrek=${ceyrek}&yil=${mevcutYil}`)
            .then(r => r.json())
            .then(data => {
                console.log('API Veri Detay Response:', data);

                if (data.success && data.veriler.length > 0) {
                    console.log('İlk veri:', data.veriler[0]);

                    let html = '<table class="table table-sm table-hover">';
                    html += '<thead class="table-light"><tr>';
                    html += '<th>Tarih</th><th>Kullanıcı</th><th>Hedef</th><th>Gerçekleşen</th><th>Durum</th><th>Açıklama</th>';
                    html += '</tr></thead><tbody>';

                    data.veriler.forEach(v => {
                        console.log('Veri satırı:', v);
                        const durumBadge = v.durum === 'Başarılı' ? 'success' : v.durum === 'Kısmen Başarılı' ? 'warning' : 'danger';

                        html += '<tr>';
                        html += `<td><small>${formatDate(v.veri_tarihi)}</small></td>`;
                        html += `<td><small><i class="bi bi-person-fill"></i> ${v.kullanici_adi || 'Bilinmiyor'}</small></td>`;
                        html += `<td><small>${v.hedef_deger}</small></td>`;
                        html += `<td><small><strong>${v.gerceklesen_deger}</strong></small></td>`;
                        html += `<td><span class="badge bg-${durumBadge}">${v.durum}</span></td>`;
                        html += `<td><small class="text-muted">${v.aciklama || '-'}</small></td>`;
                        html += '</tr>';
                    });

                    html += '</tbody></table>';

                    // Özet bilgiler
                    const toplam = data.veriler.reduce((sum, v) => sum + parseFloat(v.gerceklesen_deger || 0), 0);
                    const ortalama = toplam / data.veriler.length;

                    html += '<div class="alert alert-info mt-3">';
                    html += '<strong>Özet:</strong><br>';
                    html += `<i class="bi bi-people"></i> Toplam ${data.veriler.length} kullanıcı veri girdi<br>`;
                    html += `<i class="bi bi-calculator"></i> Toplam: ${toplam.toFixed(2)}<br>`;
                    html += `<i class="bi bi-graph-up"></i> Ortalama: ${ortalama.toFixed(2)}`;
                    html += '</div>';

                    container.innerHTML = html;
                } else {
                    container.innerHTML = '<p class="text-muted text-center">Bu periyot için henüz veri girişi yapılmamış.</p>';
                }
            })
            .catch(err => {
                console.error('Veri detay yükleme hatası:', err);
                container.innerHTML = '<p class="text-danger text-center">Veriler yüklenirken hata oluştu.</p>';
            });

        // Modal'ı göster
        const modal = new bootstrap.Modal(document.getElementById('pgVeriDetayModal'));
        modal.show();
    }

    function formatDate(dateStr) {
        if (!dateStr) return '-';
        const date = new Date(dateStr);
        return date.toLocaleDateString('tr-TR');
    }

    // ============ SÜREÇ PERFORMANS GÖSTERGESİ EKLEME ============

    // Başarı Puanı Yapılandırması Toggle Fonksiyonu
    function toggleBasariPuaniYapilandirma(mode) {
        const divId = mode === 'add' ? 'pg_basari_puani_yapilandirma_div' : 'edit_pg_basari_puani_yapilandirma_div';
        const checkboxId = mode === 'add' ? 'pg_basari_puani_kullan' : 'edit_pg_basari_puani_kullan';

        const checkbox = document.getElementById(checkboxId);
        const div = document.getElementById(divId);

        if (checkbox && div) {
            if (checkbox.checked) {
                div.style.display = 'block';
            } else {
                div.style.display = 'none';
                // Form alanlarını temizle
                if (mode === 'add') {
                    document.getElementById('pg_direction').value = 'Increasing';
                    for (let i = 1; i <= 5; i++) {
                        document.getElementById(`bp_aralik_${i}`).value = '';
                        // Varsayılan açıklamaları geri yükle
                        const varsayilanAciklamalar = {
                            '1': 'Beklentinin Çok Altında',
                            '2': 'İyileştirmeye Açık',
                            '3': 'Hedefe Ulaşmış',
                            '4': 'Hedefin Üzerinde',
                            '5': 'Mükemmel'
                        };
                        document.getElementById(`bp_aciklama_${i}`).value = varsayilanAciklamalar[i.toString()];
                    }
                } else {
                    document.getElementById('edit_pg_direction').value = 'Increasing';
                    for (let i = 1; i <= 5; i++) {
                        document.getElementById(`edit_bp_aralik_${i}`).value = '';
                        // Varsayılan açıklamaları geri yükle
                        const varsayilanAciklamalar = {
                            '1': 'Beklentinin Çok Altında',
                            '2': 'İyileştirmeye Açık',
                            '3': 'Hedefe Ulaşmış',
                            '4': 'Hedefin Üzerinde',
                            '5': 'Mükemmel'
                        };
                        document.getElementById(`edit_bp_aciklama_${i}`).value = varsayilanAciklamalar[i.toString()];
                    }
                }
            }
        }
    }

    // Dinamik tablo başlıkları oluştur - BASİT TAKVİM YAPISI (TARİHLİ)
    function updateTableHeadersDynamic(verilerArray) {
        const thead = document.querySelector('#performansTable thead');
        let headerHtml = '';

        if (mevcutPeriyot === 'haftalik' && verilerArray && verilerArray.length > 0) {
            // AYIN HAFTALARI - TARİH ARALIKLARI İLE + AY NAVİGASYONU
            const aylar = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'];
            const ayAdi = aylar[mevcutAy - 1] || 'Aylık';

            headerHtml = `
            <tr>
                <th rowspan="2" class="col-code">Kodu</th>
                <th rowspan="2" class="col-description">Performans Adı</th>
                <th rowspan="2" class="col-target">Hedef</th>
                <th rowspan="2" class="col-period">Periyot</th>
                <th rowspan="2" class="col-weight">Ağırlık (%)</th>
                <th rowspan="2" class="col-method">Hesaplama Yöntemi</th>
        `;

            // AYIN HAFTALARI - Tarih aralıkları ile (örn: "2-9 Kasım 2025" veya "29 Kasım - 5 Aralık 2025")
            verilerArray.forEach((veri, index) => {
                let tarihMetni = `Hafta ${veri.hafta}`;

                if (veri.baslangic_tarih && veri.bitis_tarih) {
                    // Tarih formatını parse et: "02.11.2025" -> "2-9 Kasım 2025"
                    const baslangicParts = veri.baslangic_tarih.split('.');
                    const bitisParts = veri.bitis_tarih.split('.');

                    if (baslangicParts.length === 3 && bitisParts.length === 3) {
                        const baslangicGun = parseInt(baslangicParts[0]);
                        const bitisGun = parseInt(bitisParts[0]);
                        const baslangicAyNo = parseInt(baslangicParts[1]);
                        const bitisAyNo = parseInt(bitisParts[1]);
                        const yil = baslangicParts[2];

                        const ayIsimleri = ['', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'];

                        if (baslangicAyNo === bitisAyNo) {
                            // Aynı ay içinde
                            const ayAdi = ayIsimleri[baslangicAyNo] || '';
                            tarihMetni = `${baslangicGun}-${bitisGun} ${ayAdi} ${yil}`;
                        } else {
                            // Farklı aylar (örn: 29 Kasım - 5 Aralık)
                            const baslangicAyAdi = ayIsimleri[baslangicAyNo] || '';
                            const bitisAyAdi = ayIsimleri[bitisAyNo] || '';
                            tarihMetni = `${baslangicGun} ${baslangicAyAdi} - ${bitisGun} ${bitisAyAdi} ${yil}`;
                        }
                    }
                }

                // Hafta sütunları
                headerHtml += `<th colspan="3">${tarihMetni}</th>`;
            });

            headerHtml += `
                <th rowspan="2" class="col-actions">İşlemler</th>
            </tr>
            <tr>
        `;

            // İkinci satır: Hedef, Gerçekleşen, Durum
            verilerArray.forEach(() => {
                headerHtml += `
                <th class="col-quarter">Hedef</th>
                <th class="col-quarter">Gerç.</th>
                <th class="col-quarter">Durum</th>
            `;
            });
            headerHtml += '</tr>';

        } else if (mevcutPeriyot === 'gunluk' && verilerArray && verilerArray.length > 0) {
            // AYIN GÜNLERİ - TARİH + GÜN ADI İLE + AY NAVİGASYONU
            const aylar = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'];
            const ayAdi = aylar[mevcutAy - 1] || 'Aylık';

            headerHtml = `
            <tr>
                <th rowspan="2" class="col-code">Kodu</th>
                <th rowspan="2" class="col-description">Performans Adı</th>
                <th rowspan="2" class="col-target">Hedef</th>
                <th rowspan="2" class="col-period">Periyot</th>
                <th rowspan="2" class="col-weight">Ağırlık (%)</th>
                <th rowspan="2" class="col-method">Hesaplama Yöntemi</th>
        `;

            // AYIN GÜNLERİ (sadece ilk 30'unu göster, scroll edilebilir)
            const gosterilecekSayi = Math.min(verilerArray.length, 30);
            for (let i = 0; i < gosterilecekSayi; i++) {
                const veri = verilerArray[i];
                const tarihMetni = veri.tarih_gun && veri.tarih_ay && veri.tarih_yil && veri.tarih_gun_adi
                    ? `${veri.tarih_gun} ${veri.tarih_ay} ${veri.tarih_yil} ${veri.tarih_gun_adi}`
                    : (veri.tarih || `Gün ${veri.gun}`);

                // Gün sütunları
                headerHtml += `<th colspan="3">${tarihMetni}</th>`;
            }
            if (verilerArray.length > 30) {
                headerHtml += `<th colspan="3" class="text-muted">... (${verilerArray.length - 30} gün daha, yatay kaydırın)</th>`;
            }

            headerHtml += `
                <th rowspan="2" class="col-actions">İşlemler</th>
            </tr>
            <tr>
        `;

            // İkinci satır: Hedef, Gerçekleşen, Durum (her gün için 3 sütun)
            for (let i = 0; i < gosterilecekSayi; i++) {
                headerHtml += `
                <th class="col-quarter">Hedef</th>
                <th class="col-quarter">Gerç.</th>
                <th class="col-quarter">Durum</th>
            `;
            }
            if (verilerArray.length > 30) {
                // "... (X gün daha)" mesajı için 3 sütun
                headerHtml += `
                <th class="col-quarter">...</th>
                <th class="col-quarter">...</th>
                <th class="col-quarter">...</th>
            `;
            }
            headerHtml += '</tr>';
        }

        if (headerHtml) {
            thead.innerHTML = headerHtml;
        }
    }

    function showAddPerformansForm() {
        if (!mevcutSurecId) {
            showToast('Lütfen önce bir süreç seçiniz!', 'warning');
            return;
        }

        const modalElement = document.getElementById('addPerformansModal');
        const modal = new bootstrap.Modal(modalElement);

        // Modal açıldıktan sonra alt stratejileri yükle
        modalElement.addEventListener('shown.bs.modal', function onModalShown() {
            loadAltStratejiler('add');
            // Event listener'ı bir kez çalıştıktan sonra kaldır
            modalElement.removeEventListener('shown.bs.modal', onModalShown);
        }, { once: true });

        modal.show();
    }

    // Alt stratejileri yükle ve dropdown'ı doldur (Kurumun tüm alt stratejileri)
    function loadAltStratejiler(mode) {
        if (!mevcutSurecId) {
            console.error('loadAltStratejiler: mevcutSurecId yok!');
            return Promise.resolve();
        }

        console.log('loadAltStratejiler çağrıldı, mode:', mode, 'surecId:', mevcutSurecId);

        const selectId = mode === 'add' ? 'pg_alt_strateji' : 'edit_pg_alt_strateji';
        const select = document.getElementById(selectId);
        if (!select) {
            console.error('loadAltStratejiler: Select elementi bulunamadı:', selectId);
            return Promise.resolve();
        }

        // Önce süreç bilgisini al (kurum_id için)
        return fetch(`/surec/${mevcutSurecId}`)
            .then(r => {
                console.log('API yanıtı status:', r.status);
                if (!r.ok) {
                    throw new Error(`HTTP ${r.status}: ${r.statusText}`);
                }
                return r.json();
            })
            .then(data => {
                console.log('Süreç bilgisi alındı:', data);
                if (!data.success || !data.surec) {
                    throw new Error('Süreç bilgisi alınamadı');
                }

                // Kurum ID'yi farklı şekillerde almayı dene
                let kurumId = null;
                if (data.surec.kurum && data.surec.kurum.id) {
                    kurumId = data.surec.kurum.id;
                } else if (data.surec.kurum_id) {
                    kurumId = data.surec.kurum_id;
                }

                console.log('Kurum ID:', kurumId, 'data.surec.kurum:', data.surec.kurum);

                if (!kurumId) {
                    console.error('Kurum ID bulunamadı. data.surec:', JSON.stringify(data.surec, null, 2));
                    select.innerHTML = '<option value="">-- Alt Strateji Seçiniz (Kurum ID bulunamadı) --</option>';
                    return Promise.resolve();
                }

                console.log('Kurum ID bulundu, alt stratejiler yükleniyor:', kurumId);

                // Süreçle ilgili alt stratejileri getir
                return fetch(`/api/kurum/${kurumId}/alt-stratejiler?surec_id=${mevcutSurecId}`)
                    .then(r => {
                        console.log('Alt stratejiler API yanıtı status:', r.status);
                        if (!r.ok) {
                            throw new Error(`HTTP ${r.status}: ${r.statusText}`);
                        }
                        return r.json();
                    })
                    .then(altStratejilerData => {
                        console.log('Alt stratejiler API yanıtı data:', altStratejilerData);
                        if (altStratejilerData && altStratejilerData.success && altStratejilerData.alt_stratejiler) {
                            console.log('Süreçle ilgili alt strateji sayısı:', altStratejilerData.alt_stratejiler.length);
                            select.innerHTML = '<option value="">-- Alt Strateji Seçiniz --</option>';

                            // Alt stratejileri ana stratejiye göre sırala
                            altStratejilerData.alt_stratejiler.forEach(altStrateji => {
                                const option = document.createElement('option');
                                option.value = altStrateji.id;
                                const anaStratejiAd = altStrateji.ana_strateji ? altStrateji.ana_strateji.ad : '';
                                const anaStratejiCode = altStrateji.ana_strateji ? (altStrateji.ana_strateji.code || '') : '';
                                const altStratejiCode = altStrateji.code || '';

                                // Format: "Ana Strateji Adı - Alt Strateji Adı" (kod varsa kod ekle)
                                let displayText = altStrateji.ad || `Alt Strateji ${altStrateji.id}`;
                                if (anaStratejiAd) {
                                    displayText = `${anaStratejiAd} - ${displayText}`;
                                }
                                if (altStratejiCode) {
                                    displayText = `${altStratejiCode} ${displayText}`;
                                } else if (anaStratejiCode) {
                                    displayText = `${anaStratejiCode}.? ${displayText}`;
                                }

                                option.textContent = displayText;
                                option.dataset.anaStratejiId = altStrateji.ana_strateji ? altStrateji.ana_strateji.id : '';
                                option.dataset.anaStratejiAd = altStrateji.ana_strateji ? altStrateji.ana_strateji.ad : '';
                                select.appendChild(option);
                            });
                            console.log('Kurumun alt stratejileri dropdown\'a eklendi');
                        } else {
                            console.warn('Kurumun alt stratejileri bulunamadı');
                            select.innerHTML = '<option value="">-- Alt Strateji Seçiniz (Alt strateji yok) --</option>';
                        }
                    })
                    .catch(err => {
                        console.error('Kurum alt stratejileri yüklenirken hata:', err);
                        select.innerHTML = '<option value="">-- Alt Strateji Seçiniz (Yükleme hatası) --</option>';
                    });
            })
            .catch(err => {
                console.error('Alt stratejiler yüklenirken hata:', err);
            });
    }

    // Alt strateji seçilince ana stratejiyi göster
    function onAltStratejiChange(mode) {
        const selectId = mode === 'add' ? 'pg_alt_strateji' : 'edit_pg_alt_strateji';
        const bilgiId = mode === 'add' ? 'pg_ana_strateji_bilgi' : 'edit_pg_ana_strateji_bilgi';
        const adId = mode === 'add' ? 'pg_ana_strateji_adi' : 'edit_pg_ana_strateji_adi';

        const select = document.getElementById(selectId);
        const bilgiDiv = document.getElementById(bilgiId);
        const adSpan = document.getElementById(adId);

        if (select && bilgiDiv && adSpan) {
            const selectedOption = select.options[select.selectedIndex];
            if (selectedOption && selectedOption.value) {
                const anaStratejiAd = selectedOption.dataset.anaStratejiAd || '-';
                adSpan.textContent = anaStratejiAd;
                bilgiDiv.style.display = 'block';
            } else {
                bilgiDiv.style.display = 'none';
            }
        }
    }

    function addPerformansGostergesi(e) {
        e.preventDefault();

        if (!mevcutSurecId) {
            showToast('Lütfen önce bir süreç seçiniz!', 'warning');
            return;
        }

        // Başarı puanı kullanılıyor mu kontrol et
        const basariPuaniKullan = document.getElementById('pg_basari_puani_kullan').checked;
        let basariPuaniAraliklari = null;
        let direction = 'Increasing';

        if (basariPuaniKullan) {
            // Başarı puanı aralıklarını topla
            const araliklar = {};
            for (let i = 1; i <= 5; i++) {
                const aralik = document.getElementById(`bp_aralik_${i}`).value.trim();
                if (aralik) {
                    araliklar[i.toString()] = aralik;
                }
            }
            if (Object.keys(araliklar).length > 0) {
                basariPuaniAraliklari = JSON.stringify(araliklar);
            }
            direction = document.getElementById('pg_direction').value || 'Increasing';
        }

        const formData = {
            ad: document.getElementById('pg_ad').value,
            aciklama: document.getElementById('pg_aciklama').value,
            hedef_deger: document.getElementById('pg_hedef').value,
            olcum_birimi: document.getElementById('pg_birim').value,
            periyot: document.getElementById('pg_periyot').value,
            baslangic_tarihi: document.getElementById('pg_baslangic').value,
            bitis_tarihi: document.getElementById('pg_bitis').value,
            veri_toplama_yontemi: document.getElementById('pg_hesaplama_yontemi').value,
            direction: direction,
            basari_puani_araliklari: basariPuaniAraliklari,
            alt_strateji_id: document.getElementById('pg_alt_strateji').value || null,
            gosterge_turu: document.getElementById('pg_gosterge_turu').value,
            target_method: document.getElementById('pg_hedef_yontemi').value
        };

        fetch(`/surec/${mevcutSurecId}/performans-gostergesi/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        })
            .then(r => r.json())
            .then(data => {
                showToast(data.message, data.success ? 'success' : 'error');
                if (data.success) {
                    // Modal'ı kapat
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addPerformansModal'));
                    modal.hide();

                    // Formu temizle
                    document.getElementById('addPerformansForm').reset();

                    // Başarı puanı checkbox'ını ve div'ini sıfırla
                    document.getElementById('pg_basari_puani_kullan').checked = false;
                    document.getElementById('pg_basari_puani_yapilandirma_div').style.display = 'none';

                    // Performans göstergelerini yenile
                    loadPerformansGostergeleri(mevcutSurecId, mevcutYil);
                }
            })
            .catch(err => {
                console.error('Performans göstergesi ekleme hatası:', err);
                showToast('Bir hata oluştu!', 'error');
            });
    }

    // ============ PERFORMANS GÖSTERGESİ DÜZENLEME/SİLME ============

    function editPerformansGostergesi(pgId) {
        const modalElement = document.getElementById('editPerformansModal');

        // Performans göstergesi bilgilerini getir ve modalı doldur
        fetch(`/surec/${mevcutSurecId}/performans-gostergesi/${pgId}`)
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    const pg = data.gosterge;
                    document.getElementById('edit_pg_id').value = pg.id;
                    document.getElementById('edit_pg_ad').value = pg.ad;
                    document.getElementById('edit_pg_aciklama').value = pg.aciklama || '';
                    document.getElementById('edit_pg_hedef').value = pg.hedef_deger || '';
                    document.getElementById('edit_pg_birim').value = pg.olcum_birimi || '';
                    document.getElementById('edit_pg_periyot').value = pg.periyot || 'Aylık';
                    document.getElementById('edit_pg_baslangic').value = pg.baslangic_tarihi || '';
                    document.getElementById('edit_pg_bitis').value = pg.bitis_tarihi || '';
                    document.getElementById('edit_pg_hesaplama_yontemi').value = pg.veri_toplama_yontemi || 'Ortalama';
                    document.getElementById('edit_pg_gosterge_turu').value = pg.gosterge_turu || '';
                    document.getElementById('edit_pg_hedef_yontemi').value = pg.target_method || '';

                    // Modal açıldıktan sonra alt stratejileri yükle ve seçimi yap
                    function onModalShown() {
                        console.log('Edit modal açıldı, alt stratejiler yükleniyor...');
                        loadAltStratejiler('edit').then(() => {
                            console.log('Alt stratejiler yüklendi, seçim yapılıyor...');
                            // Alt strateji seçiliyse işaretle
                            if (pg.alt_strateji_id) {
                                const altStratejiSelect = document.getElementById('edit_pg_alt_strateji');
                                if (altStratejiSelect) {
                                    altStratejiSelect.value = pg.alt_strateji_id;
                                    console.log('Alt strateji seçildi:', pg.alt_strateji_id);
                                    // Ana stratejiyi göster
                                    onAltStratejiChange('edit');
                                }
                            }
                        });
                    }
                    // Önceki event listener'ları temizle
                    modalElement.removeEventListener('shown.bs.modal', onModalShown);
                    modalElement.addEventListener('shown.bs.modal', onModalShown, { once: true });

                    // Başarı puanı kullanılıyor mu kontrol et
                    const basariPuaniKullanCheckbox = document.getElementById('edit_pg_basari_puani_kullan');
                    const basariPuaniDiv = document.getElementById('edit_pg_basari_puani_yapilandirma_div');

                    if (pg.basari_puani_araliklari) {
                        // Başarı puanı var, checkbox'ı işaretle ve div'i göster
                        basariPuaniKullanCheckbox.checked = true;
                        basariPuaniDiv.style.display = 'block';
                        document.getElementById('edit_pg_direction').value = pg.direction || 'Increasing';

                        // Başarı puanı aralıklarını yükle
                        try {
                            const araliklar = typeof pg.basari_puani_araliklari === 'string'
                                ? JSON.parse(pg.basari_puani_araliklari)
                                : pg.basari_puani_araliklari;

                            // Varsayılan açıklamalar
                            const varsayilanAciklamalar = {
                                '1': 'Beklentinin Çok Altında',
                                '2': 'İyileştirmeye Açık',
                                '3': 'Hedefe Ulaşmış',
                                '4': 'Hedefin Üzerinde',
                                '5': 'Mükemmel'
                            };

                            // Her puan için aralık ve açıklama yükle
                            for (let i = 1; i <= 5; i++) {
                                const aralikInput = document.getElementById(`edit_bp_aralik_${i}`);
                                const aciklamaInput = document.getElementById(`edit_bp_aciklama_${i}`);

                                if (araliklar[i] || araliklar[i.toString()]) {
                                    aralikInput.value = araliklar[i] || araliklar[i.toString()] || '';
                                } else {
                                    aralikInput.value = '';
                                }

                                // Açıklama varsa kullan, yoksa varsayılanı kullan
                                if (aciklamaInput) {
                                    aciklamaInput.value = varsayilanAciklamalar[i.toString()];
                                }
                            }
                        } catch (e) {
                            console.error('Başarı puanı aralıkları parse edilemedi:', e);
                        }
                    } else {
                        // Başarı puanı yok, checkbox'ı temizle ve div'i gizle
                        basariPuaniKullanCheckbox.checked = false;
                        basariPuaniDiv.style.display = 'none';
                        document.getElementById('edit_pg_direction').value = 'Increasing';

                        // Varsayılan açıklamaları yükle
                        const varsayilanAciklamalar = {
                            '1': 'Beklentinin Çok Altında',
                            '2': 'İyileştirmeye Açık',
                            '3': 'Hedefe Ulaşmış',
                            '4': 'Hedefin Üzerinde',
                            '5': 'Mükemmel'
                        };
                        for (let i = 1; i <= 5; i++) {
                            const aciklamaInput = document.getElementById(`edit_bp_aciklama_${i}`);
                            if (aciklamaInput) {
                                aciklamaInput.value = varsayilanAciklamalar[i.toString()];
                            }
                            document.getElementById(`edit_bp_aralik_${i}`).value = '';
                        }
                    }

                    const modal = new bootstrap.Modal(modalElement);
                    modal.show();
                } else {
                    showToast('Performans göstergesi bilgileri alınamadı: ' + data.message, 'error');
                }
            })
            .catch(err => {
                console.error('Performans göstergesi bilgileri alınırken hata:', err);
                showToast('Bir hata oluştu!', 'error');
            });
    }

    function deletePerformansGostergesi(pgId, pgAd) {
        showConfirmToast(
            `"${pgAd}" performans göstergesini silmek istediğinizden emin misiniz?<br><br><strong>Bu işlem geri alınamaz!</strong>`,
            () => {
                fetch(`/surec/${mevcutSurecId}/performans-gostergesi/${pgId}/delete`, {
                    method: 'DELETE'
                })
                    .then(r => r.json())
                    .then(data => {
                        showToast(data.message, data.success ? 'success' : 'error');
                        if (data.success) {
                            // Performans göstergelerini yenile
                            loadPerformansGostergeleri(mevcutSurecId, mevcutYil);
                        }
                    })
                    .catch(err => {
                        console.error('Performans göstergesi silme hatası:', err);
                        showToast('Bir hata oluştu!', 'error');
                    });
            }
        );
    }

    function updatePerformansGostergesi(e) {
        e.preventDefault();
        console.log('=== PG GÜNCELLEME BAŞLADI ===');

        if (!mevcutSurecId) {
            showToast('Lütfen önce bir süreç seçiniz!', 'warning');
            return;
        }

        const pgId = document.getElementById('edit_pg_id').value;
        if (!pgId) {
            showToast('PG ID bulunamadı!', 'error');
            return;
        }

        console.log('PG ID:', pgId);
        console.log('Süreç ID:', mevcutSurecId);

        // Başarı puanı kullanılıyor mu kontrol et
        const basariPuaniKullan = document.getElementById('edit_pg_basari_puani_kullan').checked;
        let basariPuaniAraliklari = null;
        let direction = 'Increasing';

        if (basariPuaniKullan) {
            // Başarı puanı aralıklarını topla
            const araliklar = {};
            for (let i = 1; i <= 5; i++) {
                const aralik = document.getElementById(`edit_bp_aralik_${i}`).value.trim();
                if (aralik) {
                    araliklar[i.toString()] = aralik;
                }
            }
            if (Object.keys(araliklar).length > 0) {
                basariPuaniAraliklari = JSON.stringify(araliklar);
            }
            direction = document.getElementById('edit_pg_direction').value || 'Increasing';
        }

        const formData = {
            ad: document.getElementById('edit_pg_ad').value,
            aciklama: document.getElementById('edit_pg_aciklama').value,
            hedef_deger: document.getElementById('edit_pg_hedef').value,
            olcum_birimi: document.getElementById('edit_pg_birim').value,
            periyot: document.getElementById('edit_pg_periyot').value,
            baslangic_tarihi: document.getElementById('edit_pg_baslangic').value,
            bitis_tarihi: document.getElementById('edit_pg_bitis').value,
            veri_toplama_yontemi: document.getElementById('edit_pg_hesaplama_yontemi').value,
            gosterge_turu: document.getElementById('edit_pg_gosterge_turu').value,
            target_method: document.getElementById('edit_pg_hedef_yontemi').value,
            direction: direction,
            basari_puani_araliklari: basariPuaniAraliklari,
            alt_strateji_id: document.getElementById('edit_pg_alt_strateji').value || null
        };

        console.log('Form Data:', formData);

        const url = `/surec/${mevcutSurecId}/performans-gostergesi/${pgId}/update`;
        console.log('API URL:', url);

        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        })
            .then(r => {
                console.log('API Response Status:', r.status);
                if (!r.ok) {
                    return r.json().then(errData => {
                        throw new Error(errData.message || `HTTP ${r.status}: ${r.statusText}`);
                    });
                }
                return r.json();
            })
            .then(data => {
                console.log('API Response Data:', data);

                // Toast'u göster
                if (data && data.message) {
                    showToast(data.message, data.success ? 'success' : 'error');
                }

                // Başarılı ise modal'ı kapat ve yenile
                if (data && data.success === true) {
                    console.log('İşlem başarılı, modal kapatılıyor...');

                    // Modal'ı kapat - önce instance al, yoksa yeni oluştur
                    const modalElement = document.getElementById('editPerformansModal');
                    if (modalElement) {
                        let modal = bootstrap.Modal.getInstance(modalElement);
                        if (!modal) {
                            modal = new bootstrap.Modal(modalElement);
                        }
                        modal.hide();
                    }

                    // Performans göstergelerini yenile
                    setTimeout(() => {
                        loadPerformansGostergeleri(mevcutSurecId, mevcutYil);
                    }, 300);
                }
            })
            .catch(err => {
                console.error('Performans göstergesi güncelleme hatası:', err);
                showToast('Bir hata oluştu: ' + err.message, 'error');
            });
    }

    // ============ FAALİYET DÜZENLEME/SİLME ============

    function editFaaliyet(faaliyetId) {
        // Faaliyet bilgilerini getir ve modalı doldur
        fetch(`/surec/${mevcutSurecId}/faaliyet/${faaliyetId}`)
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    const faaliyet = data.faaliyet;
                    document.getElementById('edit_faaliyet_id').value = faaliyet.id;
                    document.getElementById('edit_faaliyet_ad').value = faaliyet.ad;
                    document.getElementById('edit_faaliyet_aciklama').value = faaliyet.aciklama || '';
                    document.getElementById('edit_faaliyet_baslangic').value = faaliyet.baslangic_tarihi || '';
                    document.getElementById('edit_faaliyet_bitis').value = faaliyet.bitis_tarihi || '';

                    const modal = new bootstrap.Modal(document.getElementById('editFaaliyetModal'));
                    modal.show();
                } else {
                    showToast('Faaliyet bilgileri alınamadı: ' + data.message, 'error');
                }
            })
            .catch(err => {
                console.error('Faaliyet bilgileri alınırken hata:', err);
                showToast('Bir hata oluştu!', 'error');
            });
    }

    function deleteFaaliyet(faaliyetId, faaliyetAd) {
        showConfirmToast(
            `"${faaliyetAd}" faaliyetini silmek istediğinizden emin misiniz?<br><br><strong>Bu işlem geri alınamaz!</strong>`,
            () => {
                fetch(`/surec/${mevcutSurecId}/faaliyet/${faaliyetId}/delete`, {
                    method: 'DELETE'
                })
                    .then(r => r.json())
                    .then(data => {
                        showToast(data.message, data.success ? 'success' : 'error');
                        if (data.success) {
                            // Faaliyetleri yenile
                            loadFaaliyetler(mevcutSurecId, mevcutYil);
                        }
                    })
                    .catch(err => {
                        console.error('Faaliyet silme hatası:', err);
                        showToast('Bir hata oluştu!', 'error');
                    });
            }
        );
    }

    function updateFaaliyet(e) {
        e.preventDefault();

        const faaliyetId = document.getElementById('edit_faaliyet_id').value;
        const formData = {
            ad: document.getElementById('edit_faaliyet_ad').value,
            aciklama: document.getElementById('edit_faaliyet_aciklama').value,
            baslangic_tarihi: document.getElementById('edit_faaliyet_baslangic').value,
            bitis_tarihi: document.getElementById('edit_faaliyet_bitis').value
        };

        fetch(`/surec/${mevcutSurecId}/faaliyet/${faaliyetId}/update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        })
            .then(r => {
                if (!r.ok) {
                    return r.json().then(errData => {
                        throw new Error(errData.message || `HTTP ${r.status}: ${r.statusText}`);
                    });
                }
                return r.json();
            })
            .then(data => {
                // Toast'u göster
                if (data && data.message) {
                    showToast(data.message, data.success ? 'success' : 'error');
                }

                // Başarılı ise modal'ı kapat ve yenile
                if (data && data.success === true) {
                    // Modal'ı kapat - önce instance al, yoksa yeni oluştur
                    const modalElement = document.getElementById('editFaaliyetModal');
                    if (modalElement) {
                        let modal = bootstrap.Modal.getInstance(modalElement);
                        if (!modal) {
                            modal = new bootstrap.Modal(modalElement);
                        }
                        modal.hide();
                    }

                    // Faaliyetleri yenile
                    setTimeout(() => {
                        loadFaaliyetler(mevcutSurecId, mevcutYil);
                    }, 300);
                }
            })
            .catch(err => {
                console.error('Faaliyet güncelleme hatası:', err);
                showToast('Bir hata oluştu: ' + err.message, 'error');
            });
    }

    // ============ SÜREÇ FAALİYET EKLEME ============

    function showAddFaaliyetForm() {
        if (!mevcutSurecId) {
            showToast('Lütfen önce bir süreç seçiniz!', 'warning');
            return;
        }

        const modal = new bootstrap.Modal(document.getElementById('addFaaliyetModal'));
        modal.show();
    }

    function addFaaliyet(e) {
        e.preventDefault();

        if (!mevcutSurecId) {
            showToast('Lütfen önce bir süreç seçiniz!', 'warning');
            return;
        }

        const formData = {
            ad: document.getElementById('f_ad').value,
            aciklama: document.getElementById('f_aciklama').value,
            baslangic_tarihi: document.getElementById('f_baslangic').value,
            bitis_tarihi: document.getElementById('f_bitis').value,
            durum: document.getElementById('f_durum').value,
            ilerleme: document.getElementById('f_ilerleme').value
        };

        fetch(`/surec/${mevcutSurecId}/faaliyet/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        })
            .then(r => r.json())
            .then(data => {
                showToast(data.message, data.success ? 'success' : 'error');
                if (data.success) {
                    // Modal'ı kapat
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addFaaliyetModal'));
                    modal.hide();

                    // Formu temizle
                    document.getElementById('addFaaliyetForm').reset();

                    // Faaliyetleri yenile
                    loadFaaliyetler(mevcutSurecId, mevcutYil);
                }
            })
            .catch(err => {
                console.error('Faaliyet ekleme hatası:', err);
                showToast('Bir hata oluştu!', 'error');
            });
    }

    // ==================== YENİ PG VERİ DETAY FONKSİYONLARI ====================

    function openPGVeriDetay(veriIdleri) {
        // Eğer tek bir ID gelmişse diziye çevir
        if (!Array.isArray(veriIdleri)) {
            veriIdleri = [veriIdleri];
        }
        console.log('PG Veri Detay açılıyor:', veriIdleri);

        // Önce mevcut backdrop'ları temizle (varsa)
        const existingBackdrops = document.querySelectorAll('.modal-backdrop');
        existingBackdrops.forEach(backdrop => backdrop.remove());
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';

        // Önce mevcut modal instance'ını al veya yeni oluştur
        const modalElement = document.getElementById('pgVeriDetayModal');
        let modal = bootstrap.Modal.getInstance(modalElement);
        if (!modal) {
            modal = new bootstrap.Modal(modalElement, {
                backdrop: true,
                keyboard: true,
                focus: true
            });

            // Modal kapatıldığında backdrop'ları temizle (sadece bir kez ekle)
            modalElement.addEventListener('hidden.bs.modal', function () {
                setTimeout(() => {
                    const backdrops = document.querySelectorAll('.modal-backdrop');
                    backdrops.forEach(backdrop => backdrop.remove());
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = '';
                    document.body.style.paddingRight = '';
                }, 100);
            });
        }

        // Modalı göster
        modal.show();

        // Loading göster
        document.getElementById('pgVeriDetayContent').innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Yükleniyor...</span>
            </div>
            <p class="mt-2 text-muted">Veri detayları yükleniyor...</p>
        </div>
    `;

        // Birden fazla veri ID'si varsa toplu endpoint kullan
        if (veriIdleri.length > 1) {
            console.log('Toplu veri detay API çağrısı başlatılıyor:', `/api/pg-veri/detay/toplu`);
            console.log('Gönderilen veri ID\'leri:', veriIdleri, 'Tip:', typeof veriIdleri[0]);

            // Veri ID'lerini integer'a çevir
            const veriIdleriInt = veriIdleri.map(id => parseInt(id)).filter(id => !isNaN(id));
            console.log('Dönüştürülmüş veri ID\'leri:', veriIdleriInt);

            fetch('/api/pg-veri/detay/toplu', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ veri_idleri: veriIdleriInt })
            })
                .then(response => {
                    console.log('API Response Status:', response.status);
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('API Data alındı:', data);
                    if (data.success) {
                        console.log('renderPGVeriDetayToplu çağrılıyor, veriler:', data.veriler, 'yetki:', data.yetki);
                        renderPGVeriDetayToplu(data.veriler || [], data.yetki || {});
                    } else {
                        throw new Error(data.message || 'Veri yüklenemedi');
                    }
                })
                .catch(error => {
                    console.error('Veri detay hatası:', error);
                    document.getElementById('pgVeriDetayContent').innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Veri detayları yüklenirken hata oluştu: ${error.message}
                    </div>
                `;
                });
        } else {
            // Tek veri ID'si varsa mevcut endpoint'i kullan
            const veriId = veriIdleri[0];
            console.log('Tek veri detay API çağrısı başlatılıyor:', `/api/pg-veri/detay/${veriId}`);
            fetch(`/api/pg-veri/detay/${veriId}`)
                .then(response => {
                    console.log('API Response Status:', response.status);
                    if (response.status === 404) {
                        // Veri bulunamadı (silinmiş olabilir)
                        document.getElementById('pgVeriDetayContent').innerHTML = `
                        <div class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Bu veri bulunamadı. Veri silinmiş olabilir.
                        </div>
                    `;
                        // Modal'ı kapat ve karneyi yenile
                        const modal = bootstrap.Modal.getInstance(document.getElementById('pgVeriDetayModal'));
                        if (modal) {
                            setTimeout(() => {
                                modal.hide();
                                if (mevcutSurecId && mevcutYil) {
                                    loadPerformansGostergeleri(mevcutSurecId, mevcutYil);
                                }
                            }, 1500);
                        }
                        return null; // data yerine null döndür
                    }
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (!data) return; // 404 durumunda data yok, zaten uyarı gösterildi
                    console.log('API Data alındı:', data);
                    if (data.success) {
                        console.log('renderPGVeriDetay çağrılıyor, veri:', data.veri, 'yetki:', data.yetki);
                        // Veriye bireysel_pg_id ve surec_pg_id ekle
                        if (data.bireysel_pg_id) {
                            data.veri.bireysel_pg_id = data.bireysel_pg_id;
                        }
                        if (data.surec_pg_id) {
                            data.veri.surec_pg_id = data.surec_pg_id;
                        }
                        renderPGVeriDetay(data.veri, data.audit_log || [], data.yetki || {});
                    } else {
                        throw new Error(data.message || 'Veri yüklenemedi');
                    }
                })
                .catch(error => {
                    console.error('Veri detay hatası:', error);
                    document.getElementById('pgVeriDetayContent').innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Veri detayları yüklenirken hata oluştu: ${error.message}
                    </div>
                `;
                });
        }
    }

    function renderPGVeriDetay(veri, auditLog, yetki) {
        console.log('renderPGVeriDetay çağrıldı', veri, auditLog, yetki);
        const content = document.getElementById('pgVeriDetayContent');
        if (!content) {
            console.error('pgVeriDetayContent bulunamadı!');
            return;
        }
        console.log('İçerik render ediliyor...');

        // Yetki kontrolü
        const canEdit = yetki.can_edit || false;
        const canDelete = yetki.can_delete || false;

        // Silinen veri kontrolü
        const isSilinmis = veri.silinmis || false;

        // Hesaplama yöntemini kontrol et
        const hesaplamaYontemi = veri.hesaplama_yontemi || 'Ortalama';
        const isSonDeger = hesaplamaYontemi === 'Son Değer';

        // Silinen veri için özel stil
        const cardClass = isSilinmis ? 'card border-0 bg-secondary bg-opacity-10 mb-3' : 'card border-0 bg-light mb-3';
        const headerIcon = isSilinmis ? 'fa-trash' : 'fa-chart-line';
        const headerClass = isSilinmis ? 'text-secondary' : 'text-primary';

        let html = `
        ${isSilinmis ? '<div class="alert alert-warning mb-3"><i class="fas fa-exclamation-triangle me-2"></i>Bu veri silinmiş durumda. Sadece görüntüleme amaçlı gösterilmektedir.</div>' : ''}
        <div class="${cardClass}">
            <div class="card-body">
                <h6 class="${headerClass} mb-3">
                    <i class="fas ${headerIcon} me-2"></i>Veri Bilgileri
                    ${isSilinmis ? '<span class="badge bg-danger ms-2">Silindi</span>' : ''}
                </h6>
                <div class="row">
                    <div class="col-md-6 mb-2">
                        <small class="text-muted">Gerçekleşen Değer:</small>
                        <div class="fw-bold">${veri.gerceklesen_deger}</div>
                    </div>
                    <div class="col-md-6 mb-2">
                        <small class="text-muted">Veri Tarihi:</small>
                        <div class="fw-bold">${veri.veri_tarihi}</div>
                    </div>
                    <div class="col-md-6 mb-2">
                        <small class="text-muted">Giriş Periyot Tipi:</small>
                        <div class="fw-bold">${veri.giris_periyot_tipi || '-'}</div>
                    </div>
                    <div class="col-md-6 mb-2">
                        <small class="text-muted">Oluşturan:</small>
                        <div class="fw-bold">${veri.olusturan}</div>
                    </div>
                    <div class="col-md-6 mb-2">
                        <small class="text-muted">Oluşturma Tarihi:</small>
                        <div class="fw-bold">${veri.olusturma_tarihi}</div>
                    </div>
                    ${veri.guncelleyen ? `
                    <div class="col-md-6 mb-2">
                        <small class="text-muted">Son Güncelleyen:</small>
                        <div class="fw-bold">${veri.guncelleyen}</div>
                    </div>
                    ` : ''}
                </div>
                ${veri.aciklama ? `
                <div class="mt-2">
                    <small class="text-muted">Açıklama:</small>
                    <div>${veri.aciklama}</div>
                </div>
                ` : ''}
            </div>
        </div>
        
        <h6 class="text-primary mb-3"><i class="fas fa-history me-2"></i>Değişiklik Geçmişi</h6>
    `;

        if (auditLog && auditLog.length > 0) {
            html += `
            <div class="table-responsive">
                <table class="table table-sm table-hover">
                    <thead class="table-light">
                        <tr>
                            <th>İşlem</th>
                            <th>Değişiklik</th>
                            <th>Yapan</th>
                            <th>Tarih</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

            auditLog.forEach(log => {
                const islemBadge = log.islem_tipi === 'OLUSTUR' ? 'success' :
                    log.islem_tipi === 'GUNCELLE' ? 'info' : 'danger';

                // Badge metnini hesaplama yöntemine göre ayarla
                let badgeText = log.islem_tipi;
                if (isSonDeger && log.islem_tipi === 'GUNCELLE') {
                    badgeText = 'Güncelle';
                } else if (!isSonDeger && log.islem_tipi === 'OLUSTUR') {
                    badgeText = 'Oluştur';
                }

                html += `
                <tr>
                    <td><span class="badge bg-${islemBadge}">${badgeText}</span></td>
                    <td>${log.degisiklik_aciklama || '-'}</td>
                    <td>${log.islem_yapan || 'Bilinmiyor'}</td>
                    <td><small>${log.islem_tarihi || '-'}</small></td>
                </tr>
            `;
            });

            html += `
                    </tbody>
                </table>
            </div>
        `;
        } else {
            html += `<div class="alert alert-info"><i class="fas fa-info-circle me-2"></i>Henüz değişiklik geçmişi bulunmuyor.</div>`;
        }

        // Butonları ekle (silinen veriler için buton yok)
        if (!isSilinmis) {
            html += `
            <div class="mt-3 d-flex gap-2">
                ${canEdit ? `<button class="btn btn-warning btn-sm" onclick="openPGVeriGuncelleModal(${veri.id}, '${(veri.gerceklesen_deger || '').replace(/'/g, "\\'")}', '${(veri.aciklama || '').replace(/'/g, "\\'")}')">
                    <i class="fas fa-edit me-1"></i>Güncelle
                </button>` : ''}
                ${canDelete ? `<button class="btn btn-danger btn-sm" onclick="openPGVeriSilOnayModal(${veri.id})">
                    <i class="fas fa-trash me-1"></i>Sil
                </button>` : ''}
            </div>
        `;
        }

        content.innerHTML = html;

        // Proje görevlerini yükle (eğer bireysel_pg_id varsa)
        if (veri.bireysel_pg_id && veri.veri_tarihi) {
            loadPGProjeGorevleri(veri.bireysel_pg_id, veri.surec_pg_id, veri.veri_tarihi);
        }
    }

    function loadPGProjeGorevleri(bireysel_pg_id, surec_pg_id, periyot_tarih) {
        // Tarih formatını düzelt (YYYY-MM-DD)
        let tarihStr = periyot_tarih;
        if (tarihStr && tarihStr.includes('.')) {
            // DD.MM.YYYY formatından YYYY-MM-DD'ye çevir
            const parts = tarihStr.split('.');
            if (parts.length === 3) {
                tarihStr = `${parts[2]}-${parts[1]}-${parts[0]}`;
            }
        }

        const params = new URLSearchParams({
            periyot_tarih: tarihStr
        });

        if (bireysel_pg_id) {
            params.append('bireysel_pg_id', bireysel_pg_id);
        }
        if (surec_pg_id) {
            params.append('surec_pg_id', surec_pg_id);
        }

        fetch(`/api/pg-veri/proje-gorevleri?${params.toString()}`)
            .then(response => response.json())
            .then(data => {
                const content = document.getElementById('pgProjeGorevleriContent');
                if (!content) return;

                if (data.success && data.gorevler && data.gorevler.length > 0) {
                    let html = '<div class="table-responsive">';
                    html += '<table class="table table-sm table-hover">';
                    html += '<thead class="table-light"><tr>';
                    html += '<th>Görev Adı</th><th>Proje</th><th>Tamamlanma Tarihi</th><th>Etki Değeri</th>';
                    html += '</tr></thead><tbody>';

                    data.gorevler.forEach(gorev => {
                        html += '<tr>';
                        html += `<td><a href="/projeler/${gorev.project_id}/gorevler/${gorev.id}" target="_blank">${gorev.title}</a></td>`;
                        html += `<td>${gorev.project_name}</td>`;
                        html += `<td><small>${formatDate(gorev.completed_at || gorev.due_date)}</small></td>`;
                        html += `<td><strong>${gorev.impact_value}</strong></td>`;
                        html += '</tr>';
                    });

                    html += '</tbody></table></div>';
                    content.innerHTML = html;
                } else {
                    content.innerHTML = '<div class="alert alert-info"><i class="fas fa-info-circle me-2"></i>Bu veriyi besleyen proje görevi bulunmamaktadır.</div>';
                }
            })
            .catch(error => {
                console.error('Proje görevleri yükleme hatası:', error);
                const content = document.getElementById('pgProjeGorevleriContent');
                if (content) {
                    content.innerHTML = '<div class="alert alert-danger"><i class="fas fa-exclamation-triangle me-2"></i>Proje görevleri yüklenirken hata oluştu.</div>';
                }
            });
    }

    function renderPGVeriDetayToplu(veriler, yetki) {
        console.log('renderPGVeriDetayToplu çağrıldı', veriler, yetki);
        const content = document.getElementById('pgVeriDetayContent');
        if (!content) {
            console.error('pgVeriDetayContent bulunamadı!');
            return;
        }

        // Yetki kontrolü
        const canEdit = yetki.can_edit || false;
        const canDelete = yetki.can_delete || false;

        let html = `
        <div class="alert alert-info mb-3">
            <i class="fas fa-info-circle me-2"></i>
            Bu periyot için toplam <strong>${veriler.length}</strong> adet veri girişi bulunmaktadır.
        </div>
    `;

        // Her bir veri için detay kartı oluştur
        veriler.forEach((veriData, index) => {
            const veri = veriData.veri;
            const auditLog = veriData.audit_log || [];
            const veriYetki = veriData.yetki || yetki; // Her verinin kendi yetkisi varsa onu kullan, yoksa genel yetki
            const hesaplamaYontemi = veri.hesaplama_yontemi || 'Ortalama';
            const isSonDeger = hesaplamaYontemi === 'Son Değer';
            const isSilinmis = veri.silinmis || false; // Silinen veri kontrolü

            // Bu veri için yetki kontrolü
            const canEditVeri = veriYetki.can_edit || false;
            const canDeleteVeri = veriYetki.can_delete || false;

            // Silinen veri için özel stil
            const cardClass = isSilinmis ? 'card border mb-3 bg-light' : 'card border mb-3';
            const headerClass = isSilinmis ? 'card-header bg-secondary text-white' : 'card-header bg-light';
            const headerIcon = isSilinmis ? 'fa-trash' : 'fa-chart-line';

            html += `
            <div class="${cardClass}">
                <div class="${headerClass}">
                    <h6 class="mb-0">
                        <i class="fas ${headerIcon} me-2"></i>Veri Girişi #${index + 1}
                        ${isSilinmis ? '<span class="badge bg-danger ms-2">Silindi</span>' : ''}
                    </h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-2">
                            <small class="text-muted">Gerçekleşen Değer:</small>
                            <div class="fw-bold">${veri.gerceklesen_deger}</div>
                        </div>
                        <div class="col-md-6 mb-2">
                            <small class="text-muted">Veri Tarihi:</small>
                            <div class="fw-bold">${veri.veri_tarihi}</div>
                        </div>
                        <div class="col-md-6 mb-2">
                            <small class="text-muted">Giriş Periyot Tipi:</small>
                            <div class="fw-bold">${veri.giris_periyot_tipi || '-'}</div>
                        </div>
                        <div class="col-md-6 mb-2">
                            <small class="text-muted">Oluşturan:</small>
                            <div class="fw-bold">${veri.olusturan}</div>
                        </div>
                        <div class="col-md-6 mb-2">
                            <small class="text-muted">Oluşturma Tarihi:</small>
                            <div class="fw-bold">${veri.olusturma_tarihi}</div>
                        </div>
                        ${veri.guncelleyen ? `
                        <div class="col-md-6 mb-2">
                            <small class="text-muted">Son Güncelleyen:</small>
                            <div class="fw-bold">${veri.guncelleyen}</div>
                        </div>
                        ` : ''}
                    </div>
                    ${veri.aciklama ? `
                    <div class="mt-2">
                        <small class="text-muted">Açıklama:</small>
                        <div>${veri.aciklama}</div>
                    </div>
                    ` : ''}
                    
                    <div class="mt-3">
                        <h6 class="text-secondary mb-2"><i class="fas fa-history me-2"></i>Değişiklik Geçmişi</h6>
        `;

            if (auditLog && auditLog.length > 0) {
                html += `
                <div class="table-responsive">
                    <table class="table table-sm table-hover">
                        <thead class="table-light">
                            <tr>
                                <th>İşlem</th>
                                <th>Değişiklik</th>
                                <th>Yapan</th>
                                <th>Tarih</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

                auditLog.forEach(log => {
                    const islemBadge = log.islem_tipi === 'OLUSTUR' ? 'success' :
                        log.islem_tipi === 'GUNCELLE' ? 'info' : 'danger';

                    let badgeText = log.islem_tipi;
                    if (isSonDeger && log.islem_tipi === 'GUNCELLE') {
                        badgeText = 'Güncelle';
                    } else if (!isSonDeger && log.islem_tipi === 'OLUSTUR') {
                        badgeText = 'Oluştur';
                    }

                    html += `
                    <tr>
                        <td><span class="badge bg-${islemBadge}">${badgeText}</span></td>
                        <td>${log.degisiklik_aciklama || '-'}</td>
                        <td>${log.islem_yapan || 'Bilinmiyor'}</td>
                        <td><small>${log.islem_tarihi || '-'}</small></td>
                    </tr>
                `;
                });

                html += `
                        </tbody>
                    </table>
                </div>
            `;
            } else {
                html += `<div class="alert alert-info"><i class="fas fa-info-circle me-2"></i>Henüz değişiklik geçmişi bulunmuyor.</div>`;
            }

            html += `
                    </div>
                    
                    ${!isSilinmis ? `
                    <div class="mt-3 d-flex gap-2">
                        ${canEditVeri ? `<button class="btn btn-warning btn-sm" onclick="openPGVeriGuncelleModal(${veri.id}, '${(veri.gerceklesen_deger || '').replace(/'/g, "\\'")}', '${(veri.aciklama || '').replace(/'/g, "\\'")}')">
                            <i class="fas fa-edit me-1"></i>Güncelle
                        </button>` : ''}
                        ${canDeleteVeri ? `<button class="btn btn-danger btn-sm" onclick="openPGVeriSilOnayModal(${veri.id})">
                            <i class="fas fa-trash me-1"></i>Sil
                        </button>` : ''}
                    </div>
                    ` : '<div class="mt-3"><small class="text-muted"><i class="fas fa-info-circle me-1"></i>Bu veri silinmiş durumda. Düzenleme yapılamaz.</small></div>'}
                </div>
            </div>
        `;
        });

        content.innerHTML = html;
    }

    // Veri güncelleme modal'ı
    function openPGVeriGuncelleModal(veriId, mevcutDeger, mevcutAciklama) {
        document.getElementById('editVeriId').value = veriId;
        document.getElementById('editGerceklesenDeger').value = mevcutDeger || '';
        document.getElementById('editAciklama').value = mevcutAciklama || '';

        const modal = new bootstrap.Modal(document.getElementById('pgVeriGuncelleModal'));
        modal.show();
    }

    // Veri silme onay modal'ı
    function openPGVeriSilOnayModal(veriId) {
        document.getElementById('silVeriId').value = veriId;

        const modal = new bootstrap.Modal(document.getElementById('pgVeriSilOnayModal'));
        modal.show();
    }

    // Veri güncelleme fonksiyonu
    function kaydetPGVeriGuncelle() {
        const veriId = document.getElementById('editVeriId').value;
        const gerceklesenDeger = document.getElementById('editGerceklesenDeger').value.trim();
        const aciklama = document.getElementById('editAciklama').value.trim();

        if (!gerceklesenDeger) {
            showToast('Gerçekleşen değer boş olamaz!', 'warning', 5000);
            return;
        }

        // Loading göster
        const btn = document.querySelector('#pgVeriGuncelleModal .btn-warning');
        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Güncelleniyor...';

        fetch(`/api/pg-veri/guncelle/${veriId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                gerceklesen_deger: gerceklesenDeger,
                aciklama: aciklama
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Başarı mesajı (toaster)
                    showToast(data.message || 'Veri başarıyla güncellendi!', 'success', 5000);

                    // Tüm açık modal'ları kapat ve backdrop'ları temizle
                    const guncelleModal = bootstrap.Modal.getInstance(document.getElementById('pgVeriGuncelleModal'));
                    if (guncelleModal) {
                        guncelleModal.hide();
                    }
                    const detayModal = bootstrap.Modal.getInstance(document.getElementById('pgVeriDetayModal'));
                    if (detayModal) {
                        detayModal.hide();
                    }

                    // Backdrop'ları temizle (Bootstrap modal'ları bazen backdrop'ı kaldırmaz)
                    setTimeout(() => {
                        const backdrops = document.querySelectorAll('.modal-backdrop');
                        backdrops.forEach(backdrop => backdrop.remove());
                        document.body.classList.remove('modal-open');
                        document.body.style.overflow = '';
                        document.body.style.paddingRight = '';
                    }, 300);

                    // Sayfayı yenile (karne verilerini güncellemek için)
                    // mevcutSurecId ve mevcutYil kontrolü - eğer yoksa sayfa elemanlarından al
                    let surecIdToUse = mevcutSurecId;
                    let yilToUse = mevcutYil;

                    // Eğer mevcutSurecId yoksa, sayfa üzerinden al
                    if (!surecIdToUse) {
                        const surecSelect = document.getElementById('surecSelect');
                        if (surecSelect && surecSelect.value) {
                            surecIdToUse = parseInt(surecSelect.value);
                        }
                    }

                    // Eğer mevcutYil yoksa, sayfa üzerinden al
                    if (!yilToUse) {
                        const yilSelect = document.getElementById('yilSelect');
                        if (yilSelect && yilSelect.value) {
                            yilToUse = parseInt(yilSelect.value);
                        } else {
                            yilToUse = new Date().getFullYear(); // Varsayılan olarak mevcut yıl
                        }
                    }

                    // Global değişkenleri güncelle
                    if (surecIdToUse) {
                        mevcutSurecId = surecIdToUse;
                    }
                    if (yilToUse) {
                        mevcutYil = yilToUse;
                    }

                    // Karne verilerini yükle (modal'lar kapandıktan sonra)
                    if (surecIdToUse && yilToUse) {
                        setTimeout(() => {
                            loadPerformansGostergeleri(surecIdToUse, yilToUse);
                        }, 500);
                    } else {
                        console.warn('Süreç ID veya Yıl alınamadı, sayfa yenileniyor...');
                        setTimeout(() => {
                            location.reload();
                        }, 1000);
                    }
                } else {
                    // Hata mesajı (toaster)
                    showToast('Hata: ' + (data.message || 'Veri güncellenemedi!'), 'error', 7000);
                    btn.disabled = false;
                    btn.innerHTML = originalText;
                }
            })
            .catch(error => {
                console.error('Güncelleme hatası:', error);
                // Hata mesajı (toaster)
                showToast('Veri güncellenirken hata oluştu!', 'error', 7000);
                btn.disabled = false;
                btn.innerHTML = originalText;
            });
    }

    // Veri silme fonksiyonu
    function silPGVeri() {
        const veriId = document.getElementById('silVeriId').value;

        // Loading göster
        const btn = document.querySelector('#pgVeriSilOnayModal .btn-danger');
        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Siliniyor...';

        // Timeout kontrolü (30 saniye) - Tarayıcı uyumluluğu için
        let timeoutId;
        let abortController;

        try {
            // AbortController kullan (eski tarayıcılar için fallback)
            abortController = new AbortController();
            timeoutId = setTimeout(() => {
                if (abortController) {
                    abortController.abort();
                }
                btn.disabled = false;
                btn.innerHTML = originalText;
                showToast('Silme işlemi zaman aşımına uğradı. Lütfen tekrar deneyin.', 'error', 7000);
            }, 30000);
        } catch (e) {
            // Eski tarayıcılar için sadece setTimeout
            timeoutId = setTimeout(() => {
                btn.disabled = false;
                btn.innerHTML = originalText;
                showToast('Silme işlemi zaman aşımına uğradı. Lütfen tekrar deneyin.', 'error', 7000);
            }, 30000);
        }

        const fetchOptions = {
            method: 'DELETE'
        };

        // AbortController varsa signal ekle
        if (abortController) {
            fetchOptions.signal = abortController.signal;
        }

        fetch(`/api/pg-veri/sil/${veriId}`, fetchOptions)
            .then(response => {
                clearTimeout(timeoutId); // Timeout'u iptal et
                if (!response.ok) {
                    return response.json().then(errData => {
                        throw new Error(errData.message || `HTTP ${response.status}: ${response.statusText}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Modal'ı kapat
                    const modal = bootstrap.Modal.getInstance(document.getElementById('pgVeriSilOnayModal'));
                    modal.hide();

                    // Ana modal'ı da kapat
                    const mainModal = bootstrap.Modal.getInstance(document.getElementById('pgVeriDetayModal'));
                    mainModal.hide();

                    // Başarı mesajı (toaster)
                    showToast(data.message || 'Veri başarıyla silindi!', 'success', 5000);

                    // Tüm açık modal'ları kapat (veri detay modalı açık kalabilir)
                    const detayModal = bootstrap.Modal.getInstance(document.getElementById('pgVeriDetayModal'));
                    if (detayModal) {
                        detayModal.hide();
                    }
                    const guncelleModal = bootstrap.Modal.getInstance(document.getElementById('pgVeriGuncelleModal'));
                    if (guncelleModal) {
                        guncelleModal.hide();
                    }

                    // Backdrop'ları temizle
                    setTimeout(() => {
                        const backdrops = document.querySelectorAll('.modal-backdrop');
                        backdrops.forEach(backdrop => backdrop.remove());
                        document.body.classList.remove('modal-open');
                        document.body.style.overflow = '';
                        document.body.style.paddingRight = '';
                    }, 300);

                    // Kısa bir gecikme sonrası karne verilerini güncelle (modal'ların kapanması için)
                    setTimeout(() => {
                        if (mevcutSurecId && mevcutYil) {
                            loadPerformansGostergeleri(mevcutSurecId, mevcutYil);
                        }
                    }, 500);
                } else {
                    // Hata mesajı (toaster)
                    showToast('Hata: ' + (data.message || 'Veri silinemedi!'), 'error', 7000);
                    btn.disabled = false;
                    btn.innerHTML = originalText;
                }
            })
            .catch(error => {
                if (timeoutId) {
                    clearTimeout(timeoutId); // Timeout'u iptal et
                }
                console.error('Silme hatası:', error);

                // Timeout hatası için özel mesaj
                if (error.name === 'TimeoutError' || error.name === 'AbortError' || error.message.includes('aborted')) {
                    showToast('Silme işlemi zaman aşımına uğradı. Lütfen sayfayı yenileyip tekrar deneyin.', 'error', 8000);
                } else {
                    showToast('Veri silinirken hata oluştu: ' + (error.message || 'Bilinmeyen hata'), 'error', 7000);
                }
                btn.disabled = false;
                btn.innerHTML = originalText;
            });
    }

// Süreç Sağlık Skoru Yükleme ve Gauge Chart
    function loadSurecSaglikSkoru(surecId, yil) {
        if (!surecId) {
            document.getElementById('saglikSkoruCard').style.display = 'none';
            return;
        }

        fetch(`/api/surec/${surecId}/saglik-skoru?yil=${yil}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.skor !== undefined) {
                    document.getElementById('saglikSkoruCard').style.display = 'block';
                    window.__lastSaglikSkoruData = { skor: data.skor, detaylar: data.detaylar, durum: data.durum };
                    drawGaugeChart(data.skor, data.detaylar, data.durum);
                } else {
                    document.getElementById('saglikSkoruCard').style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Sağlık skoru yükleme hatası:', error);
                document.getElementById('saglikSkoruCard').style.display = 'none';
            });
    }

    function drawGaugeChart(skor, detaylar, durum) {
        const canvas = document.getElementById('gaugeChart');
        const container = document.getElementById('gaugeChartContainer');
        if (!canvas || !container) return;

        // Responsive canvas size
        const containerWidth = container.clientWidth || 250;
        const size = Math.max(180, Math.min(260, containerWidth));
        const dpr = window.devicePixelRatio || 1;
        canvas.style.width = size + 'px';
        canvas.style.height = size + 'px';
        canvas.width = Math.floor(size * dpr);
        canvas.height = Math.floor(size * dpr);

        const ctx = canvas.getContext('2d');
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.scale(dpr, dpr);

        const padding = Math.max(12, size * 0.06);
        const lineWidth = Math.max(16, size * 0.12);
        const centerX = size / 2;
        // Put circle center near bottom so the semicircle fits nicely
        const centerY = size - padding;
        const radius = (size / 2) - padding - (lineWidth / 2);

        // Canvas'ı temizle
        ctx.clearRect(0, 0, size, size);

        // Renk belirleme
        const veriYok = !!(detaylar && detaylar.veri_yok);
        let color = '#dc3545';
        if (veriYok) {
            color = '#6c757d';
        } else if (durum === 'iyi') {
            color = '#28a745';
        } else if (durum === 'orta') {
            color = '#ffc107';
        }

        const normalizedScore = veriYok ? 0 : Math.max(0, Math.min(100, Number(skor) || 0));

        // Arka plan yayı (gri)
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, 0, true);
        ctx.lineWidth = lineWidth;
        ctx.strokeStyle = '#e9ecef';
        ctx.stroke();

        // Skor yayı (renkli)
        const angle = (normalizedScore / 100) * Math.PI;
        const endAngle = Math.PI - angle;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, endAngle, true);
        ctx.lineWidth = lineWidth;
        ctx.strokeStyle = color;
        ctx.lineCap = 'round';
        ctx.stroke();

        // Skor değerini göster
        document.getElementById('gaugeValue').textContent = veriYok ? '-' : normalizedScore.toFixed(1);
        document.getElementById('gaugeValue').style.color = color;

        // Durum metni
        const durumText = veriYok ? 'Veri yok' : (durum === 'iyi' ? 'İyi' : durum === 'orta' ? 'Orta' : 'Kötü');
        document.getElementById('saglikSkoruDurum').textContent = veriYok ? durumText : `Durum: ${durumText}`;
        document.getElementById('saglikSkoruDurum').style.color = color;

        // Detay progress bar'ları
        const projeTamamlama = (detaylar && detaylar.proje_tamamlama_orani != null) ? detaylar.proje_tamamlama_orani : 0;
        const gecikenGorev = (detaylar && detaylar.geciken_gorev_orani != null) ? detaylar.geciken_gorev_orani : 0;
        const pgHedef = (detaylar && detaylar.pg_hedef_ulasma_orani != null) ? detaylar.pg_hedef_ulasma_orani : 0;

        // Proje Tamamlama
        const projeBar = document.getElementById('projeTamamlamaBar');
        projeBar.style.width = projeTamamlama + '%';
        projeBar.className = 'progress-bar ' + (projeTamamlama >= 80 ? 'bg-success' : projeTamamlama >= 50 ? 'bg-warning' : 'bg-danger');
        document.getElementById('projeTamamlamaText').textContent = projeTamamlama.toFixed(1) + '%';

        // Geciken Görev
        const gecikenBar = document.getElementById('gecikenGorevBar');
        gecikenBar.style.width = gecikenGorev + '%';
        gecikenBar.className = 'progress-bar ' + (gecikenGorev >= 80 ? 'bg-success' : gecikenGorev >= 50 ? 'bg-warning' : 'bg-danger');
        document.getElementById('gecikenGorevText').textContent = gecikenGorev.toFixed(1) + '%';

        // PG Hedef
        const pgBar = document.getElementById('pgHedefBar');
        pgBar.style.width = pgHedef + '%';
        pgBar.className = 'progress-bar ' + (pgHedef >= 80 ? 'bg-success' : pgHedef >= 50 ? 'bg-warning' : 'bg-danger');
        document.getElementById('pgHedefText').textContent = pgHedef.toFixed(1) + '%';
    }

    // Redraw gauge on resize (responsive)
    window.addEventListener('resize', () => {
        if (window.__lastSaglikSkoruData) {
            const d = window.__lastSaglikSkoruData;
            drawGaugeChart(d.skor, d.detaylar, d.durum);
        }
    });

// --- TREND ANALYSIS FUNCTIONS (Chart.js) ---

    function updateTrendChart(gostergeler) {
        if (!gostergeler || gostergeler.length === 0) return;

        // Sadece Çeyrek ve Ay periyotlarında göster
        if (mevcutPeriyot !== 'ceyrek' && mevcutPeriyot !== 'aylik') {
            const card = document.getElementById('trendAnalizCard');
            if (card) card.style.display = 'none';
            return;
        }

        // Varsayılan gizli ise aç
        const card = document.getElementById('trendAnalizCard');
        if (card) card.style.display = 'block';

        const periodScores = {};
        const labels = [];

        // Etiketleri hazırla
        if (mevcutPeriyot === 'ceyrek') {
            for (let i = 1; i <= 4; i++) {
                labels.push(`${i}. Çeyrek`);
                periodScores[i] = [];
            }
        } else if (mevcutPeriyot === 'aylik') {
            const aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"];
            aylar.forEach((ay, index) => {
                labels.push(ay);
                periodScores[index + 1] = [];
            });
        }

        gostergeler.forEach(pg => {
            if (!pg.veriler) return;

            pg.veriler.forEach(veri => {
                let donemKey = null;
                if (mevcutPeriyot === 'ceyrek') {
                    donemKey = veri.ceyrek;
                } else if (mevcutPeriyot === 'aylik') {
                    donemKey = veri.ay;
                }

                // Eğer dönem anahtarı geçerliyse (örn: Q1, Q2)
                if (donemKey && periodScores[donemKey]) {
                    // Değerleri parse et
                    let gerceklesen = parseFloat(veri.gerceklesen_deger);
                    // Hedef: Bu periyot için hedef veride varsa al, yoksa genel hedeften oranla
                    // Basitlik için: Veride hedef varsa al, yoksa PG hedefi / periyot sayısı?
                    // Genelde generatePeriyotVerileri'nde 'hedef_deger' alanı dolduruluyor.
                    let hedef = parseFloat(veri.hedef_deger);

                    // Eğer veri içinde hedef yoksa ana hedefi kullan
                    if (isNaN(hedef) || hedef === 0) hedef = parseFloat(pg.hedef_deger);

                    if (!isNaN(gerceklesen) && !isNaN(hedef) && hedef !== 0) {
                        let yuzde = (gerceklesen / hedef) * 100;
                        // Outlier temizliği (Aşırı uç değerleri %150 ile sınırla)
                        yuzde = Math.min(Math.max(yuzde, 0), 150);
                        periodScores[donemKey].push(yuzde);
                    }
                }
            });
        });

        // Ortalamaları hesapla
        const avgScores = [];

        // periodScores map'ini sıralı array'e dönüştür
        // (JavaScript object keyleri stringdir ama sayısal ise genelde sıralıdır, yine de garanti edelim)
        let keys = Object.keys(periodScores).sort((a, b) => parseInt(a) - parseInt(b));

        keys.forEach(key => {
            const scores = periodScores[key];
            if (scores.length > 0) {
                const sum = scores.reduce((a, b) => a + b, 0);
                avgScores.push(parseFloat((sum / scores.length).toFixed(1)));
            } else {
                avgScores.push(null); // Veri olmayan noktalar boş kalsın (Chart.js connect etmez)
            }
        });

        drawTrendChart(labels, avgScores);
    }

    let trendChartInstance = null;
    function drawTrendChart(labels, data) {
        const ctx = document.getElementById('trendChart');
        if (!ctx) return;

        if (trendChartInstance) {
            trendChartInstance.destroy();
        }

        trendChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Başarı Ortalaması (%)',
                    data: data,
                    borderColor: '#0d6efd', // Bootstrap primary
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    borderWidth: 3,
                    tension: 0.3, // Smooth curve
                    pointBackgroundColor: '#fff',
                    pointBorderColor: '#0d6efd',
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    fill: true,
                    spanGaps: true // Veri olmayan yerleri birleştir
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        suggestedMax: 120, // Min 120 göster
                        grid: {
                            borderDash: [5, 5],
                            color: '#f0f0f0'
                        },
                        ticks: {
                            callback: function (value) { return value + '%'; },
                            font: { size: 10 }
                        }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { font: { size: 11 } }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return `Ortalama Başarı: %${context.raw}`;
                            }
                        },
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        padding: 10
                    }
                }
            }
        });
    }

    // --- HEDEF DAĞITIM SİHİRBAZI MANTIĞI ---
    let currentDistributionPG = null;

    function openHedefDagitimModal(pgId, pgAd, currentHedef) {
        if (!pgId) return;

        const isYonetim = kullaniciRolu && ['admin', 'kurum_yoneticisi', 'ust_yonetim'].includes(kullaniciRolu);
        if (!isYonetim) {
            showToast('Bu işlem için yetkiniz yok!', 'error');
            return;
        }

        // Gelen PG Adı encoded olabilir (unescape işlemi)
        const adDecoded = pgAd.replace(/\\'/g, "'");

        currentDistributionPG = { id: pgId, ad: adDecoded, hedef: currentHedef };

        document.getElementById('dagitim_pg_adi').textContent = adDecoded || 'Seçilen KPI';
        document.getElementById('dagitim_hedef_toplam').value = currentHedef || 0;

        // Yükleniyor...
        const tbody = document.querySelector('#dagitimUserTable tbody');
        tbody.innerHTML = '<tr><td colspan="4" class="text-center py-4"><div class="spinner-border text-primary" role="status"></div><br>Üyeler yükleniyor...</td></tr>';

        const modalEl = document.getElementById('hedefDagitimModal');
        const modal = new bootstrap.Modal(modalEl);
        modal.show();

        // Üyeleri çek
        loadSurecUyeleriForDistribution(pgId);
    }

    function loadSurecUyeleriForDistribution(pgId) {
        if (!mevcutSurecId) return;

        fetch(`/api/surec/${mevcutSurecId}/uyeler`)
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    renderDistributionTable(data.uyeler);
                } else {
                    showToast('Üyeler yüklenemedi: ' + data.message, 'error');
                    document.querySelector('#dagitimUserTable tbody').innerHTML = '<tr><td colspan="4" class="text-center text-danger">Hata: ' + data.message + '</td></tr>';
                }
            })
            .catch(e => {
                showToast('Hata: ' + e.message, 'error');
                document.querySelector('#dagitimUserTable tbody').innerHTML = '<tr><td colspan="4" class="text-center text-danger">Bağlantı hatası.</td></tr>';
            });
    }

    function renderDistributionTable(uyeler) {
        const tbody = document.querySelector('#dagitimUserTable tbody');
        tbody.innerHTML = '';

        if (!uyeler || uyeler.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center py-3">Bu süreçte tanımlı üye bulunamadı.</td></tr>';
            return;
        }

        uyeler.forEach(uye => {
            const tr = document.createElement('tr');
            // Benzersiz ID oluştur
            const uniqueId = `user_Target_${uye.id}`;

            tr.innerHTML = `
            <td class="text-center align-middle">
                <input type="checkbox" class="form-check-input user-select-cb" id="${uniqueId}" value="${uye.id}" checked onchange="hesaplaHedefDagitim()">
            </td>
            <td class="align-middle">
                <label class="form-check-label w-100" for="${uniqueId}" style="cursor: pointer;">
                    ${uye.ad_soyad}
                </label>
            </td>
            <td class="align-middle"><span class="badge bg-light text-dark border">${uye.rol}</span></td>
            <td>
                <input type="number" class="form-control form-control-sm user-target-input text-end" 
                       data-user-id="${uye.id}" value="0" step="0.01" oninput="updateDistributedTotal()">
            </td>
        `;
            tbody.appendChild(tr);
        });

        // Varsayılan hesaplama (Eşit Dağıt)
        setTimeout(hesaplaHedefDagitim, 100);
    }

    function toggleAllUsers(cb) {
        document.querySelectorAll('.user-select-cb').forEach(el => {
            el.checked = cb.checked;
        });
        hesaplaHedefDagitim();
    }

    function hesaplaHedefDagitim() {
        const yontem = document.getElementById('dagitim_yontemi').value;
        const toplamHedef = parseFloat(document.getElementById('dagitim_hedef_toplam').value) || 0;

        const selectedUsers = Array.from(document.querySelectorAll('.user-select-cb:checked'));
        const count = selectedUsers.length;

        // Sayacı güncelle
        document.getElementById('selectedUserCount').textContent = count;

        if (count === 0) {
            updateDistributedTotal();
            return;
        }

        if (yontem === 'esit') {
            const share = toplamHedef / count;
            // 2 hane yuvarla
            const roundedShare = parseFloat(share.toFixed(2));

            selectedUsers.forEach(cb => {
                const row = cb.closest('tr');
                const input = row.querySelector('.user-target-input');
                input.value = roundedShare;
                // Eşit modunda karışıklığı önlemek için disable edebiliriz, ama kullanıcı düzeltmek isteyebilir.
                // Kullanıcı deneyimi açısından açık bırakmak daha iyi, ama 'Eşit' seçiliyken değiştirince yöntem 'Manuel'e dönmeli mi?
                // Şimdilik basit tutalım.
            });

            // Disable inputs for unchecked users
            document.querySelectorAll('.user-select-cb:not(:checked)').forEach(cb => {
                const row = cb.closest('tr');
                row.querySelector('.user-target-input').value = 0;
            });

        } else {
            // Manuel mod - bir şey yapma, kullanıcı girişi beklenir
        }
        updateDistributedTotal();
    }

    function updateDistributedTotal() {
        // Manuel input değişirse yöntemi 'Manuel'e çevir
        // (Opsiyonel UX iyileştirmesi)

        let sum = 0;
        document.querySelectorAll('.user-select-cb:checked').forEach(cb => {
            const row = cb.closest('tr');
            const val = parseFloat(row.querySelector('.user-target-input').value) || 0;
            sum += val;
        });

        const totalEl = document.getElementById('distributedTotal');
        totalEl.textContent = sum.toFixed(2);

        // Toplam hedefi aşıyor mu kontrol et (Görsel uyarı)
        const hedefToplam = parseFloat(document.getElementById('dagitim_hedef_toplam').value) || 0;
        if (sum > hedefToplam) {
            totalEl.className = 'fw-bold fs-5 text-danger'; // Kırmızı
            totalEl.title = 'Hedef toplamını aştınız!';
        } else if (sum < hedefToplam) {
            totalEl.className = 'fw-bold fs-5 text-warning'; // Sarı
        } else {
            totalEl.className = 'fw-bold fs-5 text-success'; // Yeşil (Tam tuttu)
        }
    }

    // Toplam hedef değişince de hesaplama tetiklensin
    document.getElementById('dagitim_hedef_toplam').addEventListener('input', hesaplaHedefDagitim);

    async function distributeTargets() {
        if (!currentDistributionPG) return;

        const isYonetim = kullaniciRolu && ['admin', 'kurum_yoneticisi', 'ust_yonetim'].includes(kullaniciRolu);
        if (!isYonetim) {
            showToast('Bu işlem için yetkiniz yok!', 'error');
            return;
        }

        const btn = document.getElementById('btnDistributeSave');

        // Seçili kullanıcı kontrolü
        const selectedCount = document.querySelectorAll('.user-select-cb:checked').length;
        if (selectedCount === 0) {
            showToast('Lütfen en az bir personel seçin.', 'warning');
            return;
        }

        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> İşleniyor...';

        const targets = [];
        document.querySelectorAll('.user-select-cb:checked').forEach(cb => {
            const row = cb.closest('tr');
            const userId = cb.value;
            const val = row.querySelector('.user-target-input').value; // String olarak al
            targets.push({ user_id: userId, hedef: val });
        });

        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

            const response = await fetch(`/api/surec/${mevcutSurecId}/performans-gostergesi/${currentDistributionPG.id}/dagit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ kullanicilar: targets })
            });

            const result = await response.json();

            if (result.success) {
                showToast(result.message, 'success');
                // Modalı kapat
                const modalEl = document.getElementById('hedefDagitimModal');
                const modal = bootstrap.Modal.getInstance(modalEl);
                modal.hide();
            } else {
                showToast(result.message, 'error');
            }
        } catch (e) {
            showToast('Hata: ' + e.message, 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-save"></i> Hedefleri Dağıt ve Kaydet';
        }
    }

(function () {
        function normalizeTurkish(text) {
            return (text || '')
                .toLowerCase()
                .replace(/ı/g, 'i')
                .replace(/ş/g, 's')
                .replace(/ğ/g, 'g')
                .replace(/ü/g, 'u')
                .replace(/ö/g, 'o')
                .replace(/ç/g, 'c')
                .trim();
        }

        function derivePeriyotTipiFromPg(pg) {
            const p = normalizeTurkish(pg?.periyot);
            if (p.includes('gunluk') || p.includes('daily')) return 'gunluk';
            if (p.includes('haftalik') || p.includes('weekly')) return 'haftalik';
            if (p.includes('aylik') || p.includes('monthly')) return 'aylik';
            if (p.includes('ceyrek') || p.includes('quarter')) return 'ceyrek';
            return 'yillik';
        }

        function fillYears(selectEl) {
            const currentYear = new Date().getFullYear();
            selectEl.innerHTML = '';
            for (let y = currentYear + 1; y >= currentYear - 5; y--) {
                selectEl.add(new Option(String(y), String(y)));
            }
            selectEl.value = String(currentYear);
        }

        function fillMonths(selectEl) {
            const aylar = [
                'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
                'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'
            ];
            selectEl.innerHTML = '<option value="">-- Ay Seçiniz --</option>';
            aylar.forEach((ad, idx) => selectEl.add(new Option(ad, String(idx + 1))));
        }

        function setPeriodOptions(periyotTipi, periodSelect, helpEl) {
            periodSelect.innerHTML = '';
            helpEl.textContent = '';

            if (!periyotTipi) {
                periodSelect.add(new Option('-- Önce gösterge seçiniz --', ''));
                return;
            }

            if (periyotTipi === 'yillik') {
                periodSelect.add(new Option('Yıllık (1)', '1'));
                helpEl.textContent = 'Yıllık periyot için dönem no = 1.';
                return;
            }

            let max = 0;
            let label = 'Dönem';
            if (periyotTipi === 'ceyrek') { max = 4; label = 'Çeyrek'; }
            if (periyotTipi === 'aylik') { max = 12; label = 'Ay'; }
            if (periyotTipi === 'haftalik') { max = 53; label = 'Hafta'; }
            if (periyotTipi === 'gunluk') { max = 31; label = 'Gün'; }

            periodSelect.add(new Option(`-- ${label} Seçiniz --`, ''));
            for (let i = 1; i <= max; i++) {
                periodSelect.add(new Option(`${i}`, String(i)));
            }
        }

        async function initVgs2() {
            const openBtn = document.getElementById('openDataEntryWizard2Btn');
            const modalEl = document.getElementById('dataEntryWizardModal2');
            if (!openBtn || !modalEl) return;

            const modal = new bootstrap.Modal(modalEl);
            const surecSelect = document.getElementById('wizard2-surec-select');
            const pgSelect = document.getElementById('wizard2-pg-select');
            const yilSelect = document.getElementById('wizard2-yil-select');
            const periyotTipiSelect = document.getElementById('wizard2-periyot-tipi');
            const ayContainer = document.getElementById('wizard2-ay-container');
            const aySelect = document.getElementById('wizard2-ay-select');
            const periodSelect = document.getElementById('wizard2-period-select');
            const periodHelp = document.getElementById('wizard2-period-help');
            const degerInput = document.getElementById('wizard2-deger');
            const aciklamaInput = document.getElementById('wizard2-aciklama');
            const saveBtn = document.getElementById('wizard2-save-btn');

            const state = {
                surecId: null,
                pgId: null,
                pgData: null,
            };

            fillYears(yilSelect);
            fillMonths(aySelect);
            setPeriodOptions('', periodSelect, periodHelp);

            async function loadSurecler() {
                surecSelect.innerHTML = '<option value="">Yükleniyor...</option>';
                try {
                    const resp = await fetch('/api/kullanici/sureclerim');
                    const data = await resp.json();
                    if (data.success && Array.isArray(data.surecler) && data.surecler.length) {
                        surecSelect.innerHTML = '<option value="">-- Süreç Seçiniz --</option>';
                        data.surecler.forEach(s => {
                            surecSelect.add(new Option(s.ad || ('Süreç ' + s.id), String(s.id)));
                        });
                    } else {
                        surecSelect.innerHTML = '<option value="">Süreç bulunamadı</option>';
                    }
                } catch (e) {
                    console.error('VGS2 loadSurecler error:', e);
                    surecSelect.innerHTML = '<option value="">Hata oluştu</option>';
                }
            }

            async function loadPgs() {
                const surecId = state.surecId;
                if (!surecId) return;
                const yil = yilSelect.value;

                pgSelect.innerHTML = '<option value="">Yükleniyor...</option>';
                try {
                    const url = `/api/surec/${surecId}/karne/performans?yil=${encodeURIComponent(yil)}&periyot=ceyrek`;
                    const resp = await fetch(url);
                    const data = await resp.json();
                    if (data.success && Array.isArray(data.gostergeler) && data.gostergeler.length) {
                        pgSelect.innerHTML = '<option value="">-- Gösterge Seçiniz --</option>';
                        data.gostergeler.forEach(pg => {
                            const text = `${pg.kodu || ('PG-' + pg.id)}: ${pg.ad}`;
                            const val = String(pg.surec_pg_id || pg.id);
                            const opt = new Option(text, val);
                            opt.dataset.pgData = JSON.stringify(pg);
                            pgSelect.add(opt);
                        });
                    } else {
                        pgSelect.innerHTML = '<option value="">Bu süreçte gösterge yok</option>';
                    }
                } catch (e) {
                    console.error('VGS2 loadPgs error:', e);
                    pgSelect.innerHTML = '<option value="">Hata oluştu</option>';
                }
            }

            function refreshPeriodUi() {
                const forced = periyotTipiSelect.value;
                const derived = derivePeriyotTipiFromPg(state.pgData);
                const periyotTipi = forced || derived;

                // Haftalık/günlük için ay gerekli
                if (periyotTipi === 'haftalik' || periyotTipi === 'gunluk') {
                    ayContainer.style.display = '';
                } else {
                    ayContainer.style.display = 'none';
                    aySelect.value = '';
                }

                setPeriodOptions(periyotTipi, periodSelect, periodHelp);

                if (!forced && periyotTipiSelect.value !== '') {
                    // kullanıcı seçtiyse dokunma
                }
            }

            async function resetModal() {
                state.surecId = null;
                state.pgId = null;
                state.pgData = null;
                surecSelect.value = '';
                pgSelect.innerHTML = '<option value="">Önce süreç seçiniz</option>';
                periyotTipiSelect.value = '';
                aySelect.value = '';
                degerInput.value = '';
                aciklamaInput.value = '';
                fillYears(yilSelect);
                refreshPeriodUi();
                await loadSurecler();
            }

            openBtn.addEventListener('click', async () => {
                await resetModal();
                modal.show();
            });

            yilSelect.addEventListener('change', async () => {
                if (state.surecId) {
                    await loadPgs();
                }
            });

            surecSelect.addEventListener('change', async () => {
                state.surecId = surecSelect.value || null;
                state.pgId = null;
                state.pgData = null;
                periyotTipiSelect.value = '';
                refreshPeriodUi();
                if (state.surecId) {
                    await loadPgs();
                } else {
                    pgSelect.innerHTML = '<option value="">Önce süreç seçiniz</option>';
                }
            });

            pgSelect.addEventListener('change', () => {
                const opt = pgSelect.options[pgSelect.selectedIndex];
                state.pgId = pgSelect.value || null;
                state.pgData = opt?.dataset?.pgData ? JSON.parse(opt.dataset.pgData) : null;
                refreshPeriodUi();
            });

            periyotTipiSelect.addEventListener('change', () => {
                refreshPeriodUi();
            });

            saveBtn.addEventListener('click', async () => {
                const surecId = state.surecId;
                const pgId = state.pgId;
                const yil = yilSelect.value;
                const deger = degerInput.value?.trim();
                const forced = periyotTipiSelect.value;
                const periyotTipi = forced || derivePeriyotTipiFromPg(state.pgData);
                const periyotNo = periodSelect.value;

                if (!surecId || !pgId || !yil || !periyotTipi || !periyotNo || !deger) {
                    showToast('Eksik bilgi var. Süreç, gösterge, yıl, periyot ve değer zorunlu.', 'warning');
                    return;
                }

                const payload = {
                    surec_id: parseInt(surecId),
                    yil: parseInt(yil),
                    pg_verileri: [{
                        pg_id: 0,
                        surec_pg_id: parseInt(pgId),
                        periyot_tipi: periyotTipi,
                        periyot_no: parseInt(periyotNo),
                        field: 'gerceklesen',
                        value: deger
                    }]
                };

                // ay alanı
                if (periyotTipi === 'aylik') {
                    payload.pg_verileri[0].ay = parseInt(periyotNo);
                }
                if ((periyotTipi === 'haftalik' || periyotTipi === 'gunluk')) {
                    if (!aySelect.value) {
                        showToast('Haftalık/Günlük için ay seçmelisiniz.', 'warning');
                        return;
                    }
                    payload.pg_verileri[0].ay = parseInt(aySelect.value);
                }

                if (aciklamaInput.value?.trim()) {
                    payload.pg_verileri[0].aciklama = aciklamaInput.value.trim();
                }

                saveBtn.disabled = true;
                const oldText = saveBtn.textContent;
                saveBtn.textContent = 'Kaydediliyor...';
                try {
                    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
                    const resp = await fetch(`/api/surec/${surecId}/karne/kaydet`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify(payload)
                    });
                    const data = await resp.json();
                    if (data.success) {
                        showToast('Veri başarıyla kaydedildi.', 'success');
                        modal.hide();
                        if (typeof loadSurecKarnesi === 'function') {
                            loadSurecKarnesi();
                        }
                    } else {
                        throw new Error(data.message || 'Veri kaydedilemedi');
                    }
                } catch (e) {
                    console.error('VGS2 save error:', e);
                    showToast(e.message || 'Kaydetme hatası', 'error');
                } finally {
                    saveBtn.disabled = false;
                    saveBtn.textContent = oldText;
                }
            });
        }

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initVgs2);
        } else {
            initVgs2();
        }
    })();
