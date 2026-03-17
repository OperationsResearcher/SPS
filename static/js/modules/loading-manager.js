/**
 * LOADING MANAGER
 * Sprint 1-2: Frontend Modernizasyonu
 * Loading states ve skeleton screens yönetimi
 */

class LoadingManager {
    constructor() {
        this.overlayElement = null;
        this.init();
    }
    
    init() {
        this.createOverlay();
    }
    
    createOverlay() {
        this.overlayElement = document.createElement('div');
        this.overlayElement.className = 'loading-overlay';
        this.overlayElement.innerHTML = `
            <div class="loading-overlay-content">
                <div class="loading-spinner loading-spinner-lg"></div>
                <div class="loading-overlay-text">Yükleniyor...</div>
            </div>
        `;
        document.body.appendChild(this.overlayElement);
    }
    
    show(message = 'Yükleniyor...') {
        const textElement = this.overlayElement.querySelector('.loading-overlay-text');
        if (textElement) {
            textElement.textContent = message;
        }
        this.overlayElement.classList.add('active');
    }
    
    hide() {
        this.overlayElement.classList.remove('active');
    }
    
    showButtonLoading(button) {
        button.classList.add('btn-loading');
        button.disabled = true;
    }
    
    hideButtonLoading(button) {
        button.classList.remove('btn-loading');
        button.disabled = false;
    }
}

    
    /**
     * Skeleton screen oluştur
     */
    createSkeleton(type = 'card', count = 1) {
        const skeletons = [];
        
        for (let i = 0; i < count; i++) {
            let skeleton;
            
            switch (type) {
                case 'kpi-card':
                    skeleton = this.createKpiCardSkeleton();
                    break;
                case 'table-row':
                    skeleton = this.createTableRowSkeleton();
                    break;
                case 'card':
                default:
                    skeleton = this.createCardSkeleton();
                    break;
            }
            
            skeletons.push(skeleton);
        }
        
        return skeletons;
    }
    
    createKpiCardSkeleton() {
        const div = document.createElement('div');
        div.className = 'skeleton-kpi-card';
        div.innerHTML = `
            <div class="skeleton-kpi-header">
                <div class="skeleton skeleton-kpi-code"></div>
                <div class="skeleton skeleton-kpi-status"></div>
            </div>
            <div class="skeleton skeleton-kpi-title"></div>
            <div class="skeleton-kpi-metrics">
                <div class="skeleton-kpi-metric">
                    <div class="skeleton skeleton-kpi-value"></div>
                    <div class="skeleton skeleton-kpi-label"></div>
                </div>
                <div class="skeleton-kpi-metric">
                    <div class="skeleton skeleton-kpi-value"></div>
                    <div class="skeleton skeleton-kpi-label"></div>
                </div>
            </div>
            <div class="skeleton skeleton-kpi-progress"></div>
            <div class="skeleton-kpi-footer">
                <div class="skeleton skeleton-kpi-trend"></div>
                <div class="skeleton skeleton-kpi-date"></div>
            </div>
        `;
        return div;
    }
    
    createTableRowSkeleton() {
        const div = document.createElement('div');
        div.className = 'skeleton-table-row';
        div.innerHTML = `
            <div class="skeleton skeleton-table-cell"></div>
            <div class="skeleton skeleton-table-cell"></div>
            <div class="skeleton skeleton-table-cell"></div>
            <div class="skeleton skeleton-table-cell"></div>
        `;
        return div;
    }
    
    createCardSkeleton() {
        const div = document.createElement('div');
        div.className = 'skeleton-card';
        div.innerHTML = `
            <div class="skeleton skeleton-title"></div>
            <div class="skeleton skeleton-text"></div>
            <div class="skeleton skeleton-text"></div>
            <div class="skeleton skeleton-text" style="width: 60%;"></div>
        `;
        return div;
    }
    
    /**
     * Container'a skeleton ekle
     */
    showSkeleton(container, type = 'card', count = 3) {
        if (typeof container === 'string') {
            container = document.querySelector(container);
        }
        
        if (!container) return;
        
        container.innerHTML = '';
        const skeletons = this.createSkeleton(type, count);
        skeletons.forEach(skeleton => container.appendChild(skeleton));
    }
    
    /**
     * Skeleton'ı kaldır ve içeriği göster
     */
    hideSkeleton(container, content) {
        if (typeof container === 'string') {
            container = document.querySelector(container);
        }
        
        if (!container) return;
        
        container.innerHTML = '';
        if (typeof content === 'string') {
            container.innerHTML = content;
        } else if (content instanceof HTMLElement) {
            container.appendChild(content);
        }
        
        // Fade in animation
        container.classList.add('fade-in');
    }
}

// Global instance
window.loadingManager = new LoadingManager();

// Export
window.LoadingManager = LoadingManager;
