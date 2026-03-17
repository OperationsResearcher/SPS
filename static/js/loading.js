/**
 * Global Loading State Management
 * Provides consistent loading indicators across the application
 */

(function() {
    'use strict';

    // Global loading overlay HTML
    const loadingHTML = `
        <div id="globalLoadingOverlay" class="global-loading-overlay" style="display: none;">
            <div class="loading-spinner">
                <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                    <span class="visually-hidden">Yükleniyor...</span>
                </div>
                <div class="loading-text mt-3">Yükleniyor...</div>
            </div>
        </div>
    `;

    // Inject loading overlay on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initLoadingSystem);
    } else {
        initLoadingSystem();
    }

    function initLoadingSystem() {
        // Inject loading overlay
        document.body.insertAdjacentHTML('beforeend', loadingHTML);
        
        // Add styles
        injectLoadingStyles();
        
        // Intercept form submissions
        interceptFormSubmissions();
        
        // Intercept AJAX requests
        interceptAjaxRequests();
    }

    function injectLoadingStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .global-loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
                backdrop-filter: blur(3px);
            }
            
            .loading-spinner {
                text-align: center;
                color: white;
            }
            
            .loading-text {
                font-size: 1.1rem;
                font-weight: 500;
                color: white;
            }
            
            .btn-loading {
                position: relative;
                pointer-events: none;
            }
            
            .btn-loading::after {
                content: "";
                position: absolute;
                width: 16px;
                height: 16px;
                top: 50%;
                left: 50%;
                margin-left: -8px;
                margin-top: -8px;
                border: 2px solid transparent;
                border-top-color: currentColor;
                border-radius: 50%;
                animation: btn-loading-spin 0.6s linear infinite;
            }
            
            @keyframes btn-loading-spin {
                to { transform: rotate(360deg); }
            }
            
            .table-loading {
                position: relative;
                opacity: 0.6;
                pointer-events: none;
            }
            
            .inline-spinner {
                display: inline-block;
                width: 1rem;
                height: 1rem;
                border: 2px solid currentColor;
                border-right-color: transparent;
                border-radius: 50%;
                animation: btn-loading-spin 0.6s linear infinite;
            }
        `;
        document.head.appendChild(style);
    }

    function interceptFormSubmissions() {
        document.addEventListener('submit', function(e) {
            const form = e.target;
            
            // Skip if form has data-no-loading attribute
            if (form.hasAttribute('data-no-loading')) {
                return;
            }
            
            // Show loading
            window.showLoading('İşleminiz gerçekleştiriliyor...');
            
            // Add submit button loading state
            const submitBtn = form.querySelector('[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('btn-loading');
                submitBtn.disabled = true;
            }
        });
    }

    function interceptAjaxRequests() {
        // Intercept fetch requests
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            const [url, options = {}] = args;
            
            // Skip if no-loading header is present
            if (options.headers && options.headers['X-No-Loading']) {
                return originalFetch.apply(this, args);
            }
            
            // Show loading for non-GET requests
            if (!options.method || options.method.toUpperCase() !== 'GET') {
                window.showLoading('İşleminiz gerçekleştiriliyor...');
            }
            
            return originalFetch.apply(this, args).finally(() => {
                window.hideLoading();
            });
        };

        // Intercept XMLHttpRequest
        const originalOpen = XMLHttpRequest.prototype.open;
        const originalSend = XMLHttpRequest.prototype.send;
        
        XMLHttpRequest.prototype.open = function(method, url, ...rest) {
            this._method = method;
            this._url = url;
            return originalOpen.call(this, method, url, ...rest);
        };
        
        XMLHttpRequest.prototype.send = function(...args) {
            // Show loading for non-GET requests
            if (this._method && this._method.toUpperCase() !== 'GET') {
                window.showLoading('İşleminiz gerçekleştiriliyor...');
                
                this.addEventListener('loadend', function() {
                    window.hideLoading();
                });
            }
            
            return originalSend.apply(this, args);
        };
    }

    // Global functions
    window.showLoading = function(message) {
        const overlay = document.getElementById('globalLoadingOverlay');
        if (overlay) {
            const textElement = overlay.querySelector('.loading-text');
            if (textElement && message) {
                textElement.textContent = message;
            }
            overlay.style.display = 'flex';
        }
    };

    window.hideLoading = function() {
        const overlay = document.getElementById('globalLoadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    };

    // Button loading helpers
    window.setButtonLoading = function(button, loading) {
        if (loading) {
            button.classList.add('btn-loading');
            button.disabled = true;
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = '<span class="inline-spinner me-2"></span>' + (button.dataset.loadingText || 'İşleniyor...');
        } else {
            button.classList.remove('btn-loading');
            button.disabled = false;
            if (button.dataset.originalText) {
                button.innerHTML = button.dataset.originalText;
            }
        }
    };

    // Table loading helper
    window.setTableLoading = function(table, loading) {
        if (loading) {
            table.classList.add('table-loading');
        } else {
            table.classList.remove('table-loading');
        }
    };

})();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showLoading: window.showLoading,
        hideLoading: window.hideLoading,
        setButtonLoading: window.setButtonLoading,
        setTableLoading: window.setTableLoading
    };
}
