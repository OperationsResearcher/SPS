/**
 * INLINE EDITING MODULE
 * Sprint 1-2: Frontend Modernizasyonu
 * Hızlı veri girişi için inline editing desteği
 */

class InlineEdit {
    constructor(options = {}) {
        this.options = {
            selector: '[data-inline-edit]',
            saveEndpoint: '/api/kpi-data',
            debounceTime: 500,
            onSave: null,
            onError: null,
            ...options
        };
        
        this.saveTimer = null;
        this.init();
    }
    
    init() {
        this.attachEventListeners();
    }
    
    attachEventListeners() {
        document.addEventListener('blur', (e) => {
            if (e.target.matches(this.options.selector)) {
                this.handleBlur(e.target);
            }
        }, true);
        
        document.addEventListener('keydown', (e) => {
            if (e.target.matches(this.options.selector)) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    e.target.blur();
                } else if (e.key === 'Escape') {
                    this.cancelEdit(e.target);
                }
            }
        });
    }
    
    handleBlur(element) {
        const newValue = element.textContent.trim();
        const oldValue = element.dataset.originalValue || '';
        
        if (newValue === oldValue) {
            return;
        }
        
        this.saveData(element, newValue);
    }

    
    saveData(element, value) {
        const kpiId = element.dataset.kpiId;
        const field = element.dataset.field;
        
        if (!kpiId || !field) {
            console.error('Missing kpiId or field attribute');
            return;
        }
        
        // Show loading state
        element.classList.add('saving');
        element.setAttribute('contenteditable', 'false');
        
        // Debounced save
        clearTimeout(this.saveTimer);
        this.saveTimer = setTimeout(() => {
            this.performSave(element, kpiId, field, value);
        }, this.options.debounceTime);
    }
    
    async performSave(element, kpiId, field, value) {
        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
            
            const response = await fetch(`${this.options.saveEndpoint}/${kpiId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ [field]: value })
            });
            
            if (!response.ok) {
                throw new Error('Save failed');
            }
            
            const data = await response.json();
            
            // Success
            element.classList.remove('saving');
            element.classList.add('saved');
            element.dataset.originalValue = value;
            
            setTimeout(() => {
                element.classList.remove('saved');
                element.setAttribute('contenteditable', 'true');
            }, 1000);
            
            if (this.options.onSave) {
                this.options.onSave(data, element);
            }
            
        } catch (error) {
            // Error
            element.classList.remove('saving');
            element.classList.add('error');
            element.textContent = element.dataset.originalValue;
            
            setTimeout(() => {
                element.classList.remove('error');
                element.setAttribute('contenteditable', 'true');
            }, 2000);
            
            if (this.options.onError) {
                this.options.onError(error, element);
            }
            
            console.error('Save error:', error);
        }
    }
    
    cancelEdit(element) {
        element.textContent = element.dataset.originalValue || '';
        element.blur();
    }
}

// Export for use
window.InlineEdit = InlineEdit;
