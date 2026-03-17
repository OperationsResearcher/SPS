/* Ana kontrol sayfası JavaScript */

(function() {
    const modules = ['surec', 'karne', 'pg'];

    function updateProgress() {
        modules.forEach(function(module) {
            const key = 'modul_' + module;
            const saved = localStorage.getItem(key);
            if (saved) {
                try {
                    const data = JSON.parse(saved);
                    const total = data.questions ? data.questions.length : 0;
                    const answered = data.questions ? data.questions.filter(function(q) { return q.answer && q.answer !== ''; }).length : 0;
                    const percentage = total > 0 ? Math.round((answered / total) * 100) : 0;

                    const progressEl = document.getElementById(module + '-progress');
                    const progressFillEl = document.getElementById(module + '-progress-fill');

                    if (progressEl) {
                        progressEl.textContent = percentage + '% tamamlandı';
                    }
                    if (progressFillEl) {
                        progressFillEl.style.width = percentage + '%';
                    }
                } catch (e) {
                    console.error('Progress update error for ' + module + ':', e);
                }
            }
        });
    }

    function exportAllResults() {
        const moduleTitles = {
            'surec': 'Süreç Yönetimi',
            'karne': 'Süreç Karnesi',
            'pg': 'Performans Göstergesi (PG)'
        };

        const tarih = new Date().toISOString().split('T')[0];
        const saat = new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });

        let mdContent = '# Kokpitim Süreç Modülü - QA Kontrol Listesi Raporu\n\n';
        mdContent += '**Tarih:** ' + tarih + ' ' + saat + '\n\n';
        mdContent += '---\n\n';

        let totalQuestions = 0;
        let totalAnswered = 0;

        modules.forEach(function(module) {
            const key = 'modul_' + module;
            const saved = localStorage.getItem(key);
            if (saved) {
                try {
                    const data = JSON.parse(saved);
                    if (data.questions) {
                        totalQuestions += data.questions.length;
                        totalAnswered += data.questions.filter(function(q) { return q.answer && q.answer !== ''; }).length;
                    }
                } catch (e) {}
            }
        });

        const overallPercentage = totalQuestions > 0 ? Math.round((totalAnswered / totalQuestions) * 100) : 0;
        mdContent += '## Genel Özet\n\n';
        mdContent += '- **Toplam Soru:** ' + totalQuestions + '\n';
        mdContent += '- **Cevaplanan:** ' + totalAnswered + ' (' + overallPercentage + '%)\n\n';
        mdContent += '---\n\n';

        modules.forEach(function(module) {
            const key = 'modul_' + module;
            const saved = localStorage.getItem(key);
            if (saved) {
                try {
                    const data = JSON.parse(saved);
                    if (data.questions && data.questions.length > 0) {
                        mdContent += '## ' + moduleTitles[module] + '\n\n';
                        data.questions.forEach(function(q, index) {
                            if (q.answer && q.answer !== '') {
                                var answerEmoji = '⚪';
                                var answerText = 'Cevaplanmadı';
                                if (q.answer === 'evet') { answerEmoji = '✅'; answerText = 'Evet'; }
                                else if (q.answer === 'hayir') { answerEmoji = '❌'; answerText = 'Hayır'; }
                                else if (q.answer === 'kısmen') { answerEmoji = '🟡'; answerText = 'Kısmen'; }
                                mdContent += '### ' + (index + 1) + '. ' + q.text + '\n\n';
                                mdContent += '**Cevap:** ' + answerEmoji + ' ' + answerText + '\n\n';
                                if (q.explanation && q.explanation.trim()) {
                                    mdContent += '**Açıklama:**\n\n' + q.explanation + '\n\n';
                                }
                                mdContent += '---\n\n';
                            }
                        });
                    }
                } catch (e) {}
            }
        });

        mdContent += '\n*Bu rapor ' + tarih + ' tarihinde oluşturulmuştur.*\n';

        const dataBlob = new Blob([mdContent], {type: 'text/markdown;charset=utf-8'});
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'kokpitim-surec-qa-' + tarih + '.md';
        link.click();
        URL.revokeObjectURL(url);
    }

    function clearAllResults() {
        if (confirm('Tüm kaydedilmiş sonuçları silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.')) {
            modules.forEach(function(module) {
                localStorage.removeItem('modul_' + module);
            });
            updateProgress();
        }
    }

    document.getElementById('export-all-btn').addEventListener('click', exportAllResults);
    document.getElementById('clear-all-btn').addEventListener('click', clearAllResults);

    updateProgress();
})();
