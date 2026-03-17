// Ortak JavaScript fonksiyonları

// Standalone kontrol sayfaları için hafif toast (ana uygulamadaki base.html showToast ile çakışmaz)
(function ensureShowToast() {
    if (typeof window.showToast === 'function') return;

    function ensureToastContainer() {
        let container = document.getElementById('toast-container');
        if (container) return container;

        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.position = 'fixed';
        container.style.top = '16px';
        container.style.right = '16px';
        container.style.zIndex = '99999';
        container.style.display = 'flex';
        container.style.flexDirection = 'column';
        container.style.gap = '10px';
        document.body.appendChild(container);
        return container;
    }

    window.showToast = function showToast(type, message, title = null) {
        try {
            const container = ensureToastContainer();
            const toast = document.createElement('div');
            toast.setAttribute('role', 'status');
            toast.style.background = '#ffffff';
            toast.style.color = '#333';
            toast.style.borderRadius = '10px';
            toast.style.padding = '12px 14px';
            toast.style.minWidth = '280px';
            toast.style.maxWidth = '420px';
            toast.style.boxShadow = '0 10px 30px rgba(0,0,0,0.12)';
            toast.style.borderLeft = '4px solid #667eea';
            toast.style.fontFamily = 'inherit';

            const safeTitle = (title || (type ? String(type).toUpperCase() : 'BİLGİ'));
            const safeMessage = message == null ? '' : String(message);

            toast.innerHTML = `
                <div style="font-weight: 700; margin-bottom: 4px; color: #667eea;">${safeTitle}</div>
                <div style="line-height: 1.35;">${safeMessage.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</div>
            `;

            container.appendChild(toast);
            window.setTimeout(() => {
                toast.remove();
            }, 3500);
        } catch (e) {
            console.error('Toast gösterimi başarısız:', e);
            console.log(type, message);
        }
    };
})();

function initializeModule(moduleName, moduleTitle, questions) {
    setCurrentModule(moduleName, questions);

    const saved = localStorage.getItem(`modul_${moduleName}`);
    if (saved) {
        try {
            const savedData = JSON.parse(saved);
            questions.forEach((q, index) => {
                if (savedData.questions && savedData.questions[index]) {
                    q.answer = savedData.questions[index].answer || '';
                    q.explanation = savedData.questions[index].explanation || '';
                }
            });
            setCurrentModule(moduleName, questions);
        } catch (e) {
            console.error('Yükleme hatası:', e);
        }
    }

    renderQuestions(questions);
    updateProgress(moduleName, questions);
}

function renderQuestions(questions) {
    const container = document.getElementById('questions-container');
    container.innerHTML = '';

    questions.forEach((question, index) => {
        const questionEl = document.createElement('div');
        questionEl.className = 'question-item';
        questionEl.innerHTML = `
            <div class="question-header">
                <span class="question-number">${index + 1}</span>
                <h3 class="question-text">${question.text}</h3>
            </div>
            
            <div class="answer-options">
                <label class="option-label">
                    <input type="radio" name="answer-${index}" value="evet" 
                           ${question.answer === 'evet' ? 'checked' : ''} 
                           onchange="updateAnswer(${index}, 'evet')">
                    <span class="option-text option-yes">✓ Evet</span>
                </label>
                <label class="option-label">
                    <input type="radio" name="answer-${index}" value="hayir" 
                           ${question.answer === 'hayir' ? 'checked' : ''} 
                           onchange="updateAnswer(${index}, 'hayir')">
                    <span class="option-text option-no">✗ Hayır</span>
                </label>
                <label class="option-label">
                    <input type="radio" name="answer-${index}" value="kısmen" 
                           ${question.answer === 'kısmen' ? 'checked' : ''} 
                           onchange="updateAnswer(${index}, 'kısmen')">
                    <span class="option-text option-partial">◐ Kısmen</span>
                </label>
            </div>
            
            <div class="explanation-section">
                <label class="explanation-label">Açıklama (İsteğe bağlı):</label>
                <textarea class="explanation-input" 
                          placeholder="Bu soru hakkında notlarınızı buraya yazabilirsiniz..."
                          onchange="updateExplanation(${index}, this.value)"
                          onblur="saveProgress()">${question.explanation || ''}</textarea>
            </div>
        `;
        container.appendChild(questionEl);
    });
}

let currentModule = '';
let currentQuestions = [];

function setCurrentModule(moduleName, questions) {
    currentModule = moduleName;
    currentQuestions = questions;
}

function updateAnswer(index, answer) {
    if (currentQuestions[index]) {
        currentQuestions[index].answer = answer;
        saveProgress();
        updateProgress(currentModule, currentQuestions);
    }
}

function updateExplanation(index, explanation) {
    if (currentQuestions[index]) {
        currentQuestions[index].explanation = explanation;
        saveProgress();
    }
}

function saveProgress() {
    if (currentModule && currentQuestions) {
        const dataToSave = {
            module: currentModule,
            timestamp: new Date().toISOString(),
            questions: currentQuestions
        };
        localStorage.setItem(`modul_${currentModule}`, JSON.stringify(dataToSave));
    }
}

function updateProgress(moduleName, questions) {
    const total = questions.length;
    const answered = questions.filter(q => q.answer && q.answer !== '').length;
    const percentage = total > 0 ? Math.round((answered / total) * 100) : 0;

    const progressEl = document.getElementById('progress-text');
    const progressFillEl = document.getElementById('progress-fill');

    if (progressEl) {
        progressEl.textContent = `${answered} / ${total} soru cevaplandı (${percentage}%)`;
    }
    if (progressFillEl) {
        progressFillEl.style.width = `${percentage}%`;
    }
}

function exportResults(moduleName, moduleTitle) {
    const saved = localStorage.getItem(`modul_${moduleName}`);
    if (!saved) {
        showToast('warning', 'Dışa aktarılacak veri bulunamadı.', 'Uyarı');
        return;
    }

    try {
        const data = JSON.parse(saved);
        const tarih = new Date().toISOString().split('T')[0];
        const saat = new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });

        let mdContent = `# ${moduleTitle} - Kontrol Listesi Raporu\n\n`;
        mdContent += `**Tarih:** ${tarih} ${saat}\n`;
        mdContent += `**Modül Kodu:** ${moduleName}\n\n`;
        mdContent += `---\n\n`;

        if (data.questions && data.questions.length > 0) {
            const total = data.questions.length;
            const answered = data.questions.filter(q => q.answer && q.answer !== '').length;
            const evet = data.questions.filter(q => q.answer === 'evet').length;
            const hayir = data.questions.filter(q => q.answer === 'hayir').length;
            const kısmen = data.questions.filter(q => q.answer === 'kısmen').length;
            const percentage = total > 0 ? Math.round((answered / total) * 100) : 0;

            mdContent += `## Özet İstatistikler\n\n`;
            mdContent += `- **Toplam Soru:** ${total}\n`;
            mdContent += `- **Cevaplanan:** ${answered} (${percentage}%)\n`;
            mdContent += `- **Evet:** ${evet}\n`;
            mdContent += `- **Hayır:** ${hayir}\n`;
            mdContent += `- **Kısmen:** ${kısmen}\n`;
            mdContent += `- **Cevaplanmamış:** ${total - answered}\n\n`;
            mdContent += `---\n\n`;

            mdContent += `## Detaylı Sonuçlar\n\n`;

            data.questions.forEach((q, index) => {
                const num = index + 1;
                let answerEmoji = '⚪';
                let answerText = 'Cevaplanmadı';

                if (q.answer === 'evet') {
                    answerEmoji = '✅';
                    answerText = 'Evet';
                } else if (q.answer === 'hayir') {
                    answerEmoji = '❌';
                    answerText = 'Hayır';
                } else if (q.answer === 'kısmen') {
                    answerEmoji = '🟡';
                    answerText = 'Kısmen';
                }

                mdContent += `### ${num}. ${q.text}\n\n`;
                mdContent += `**Cevap:** ${answerEmoji} ${answerText}\n\n`;

                if (q.explanation && q.explanation.trim()) {
                    mdContent += `**Açıklama:**\n\n${q.explanation}\n\n`;
                }

                mdContent += `---\n\n`;
            });
        } else {
            mdContent += `Henüz cevaplanmış soru bulunmamaktadır.\n`;
        }

        const dataBlob = new Blob([mdContent], {type: 'text/markdown;charset=utf-8'});
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `kontrol-${moduleName}-${tarih}.md`;
        link.click();
        URL.revokeObjectURL(url);
    } catch (e) {
        showToast('error', 'Dışa aktarma hatası: ' + (e && e.message ? e.message : String(e)), 'Hata');
    }
}

function clearResults(moduleName, moduleTitle) {
    if (confirm(`"${moduleTitle}" modülündeki tüm cevapları silmek istediğinizden emin misiniz?`)) {
        localStorage.removeItem(`modul_${moduleName}`);
        location.reload();
    }
}
