/**
 * PWA Manager
 * Handles service worker registration, install prompt, and offline detection
 */

class PWAManager {
  constructor() {
    this.deferredPrompt = null;
    this.isOnline = navigator.onLine;
    this.init();
  }

  init() {
    // Register service worker
    if ('serviceWorker' in navigator) {
      this.registerServiceWorker();
    }

    // Listen for install prompt
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      this.deferredPrompt = e;
      this.showInstallButton();
    });

    // Listen for online/offline events
    window.addEventListener('online', () => this.handleOnline());
    window.addEventListener('offline', () => this.handleOffline());

    // Check initial connection status
    this.updateConnectionStatus();
  }

  async registerServiceWorker() {
    try {
      const registration = await navigator.serviceWorker.register('/static/js/service-worker.js');
      console.log('[PWA] Service Worker registered:', registration.scope);

      // Check for updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            this.showUpdateNotification();
          }
        });
      });
    } catch (error) {
      console.error('[PWA] Service Worker registration failed:', error);
    }
  }

  showInstallButton() {
    const installBtn = document.getElementById('pwa-install-btn');
    if (installBtn) {
      installBtn.style.display = 'block';
      installBtn.addEventListener('click', () => this.promptInstall());
    }
  }


  async promptInstall() {
    if (!this.deferredPrompt) return;

    this.deferredPrompt.prompt();
    const { outcome } = await this.deferredPrompt.userChoice;
    
    console.log('[PWA] Install prompt outcome:', outcome);
    
    if (outcome === 'accepted') {
      this.trackInstall();
    }
    
    this.deferredPrompt = null;
    document.getElementById('pwa-install-btn').style.display = 'none';
  }

  trackInstall() {
    // Track PWA installation
    if (typeof gtag !== 'undefined') {
      gtag('event', 'pwa_install', {
        event_category: 'engagement',
        event_label: 'PWA Installed'
      });
    }
  }

  handleOnline() {
    this.isOnline = true;
    this.updateConnectionStatus();
    this.syncQueuedData();
    this.showNotification('Bağlantı kuruldu', 'İnternet bağlantınız geri geldi', 'success');
  }

  handleOffline() {
    this.isOnline = false;
    this.updateConnectionStatus();
    this.showNotification('Çevrimdışı mod', 'İnternet bağlantınız yok. Veriler senkronize edilecek.', 'warning');
  }

  updateConnectionStatus() {
    const statusEl = document.getElementById('connection-status');
    if (!statusEl) return;

    if (this.isOnline) {
      statusEl.className = 'connection-status online';
      statusEl.innerHTML = '<i class="icon-wifi"></i> Çevrimiçi';
    } else {
      statusEl.className = 'connection-status offline';
      statusEl.innerHTML = '<i class="icon-wifi-off"></i> Çevrimdışı';
    }
  }

  async syncQueuedData() {
    if (!('serviceWorker' in navigator) || !('sync' in ServiceWorkerRegistration.prototype)) {
      return;
    }

    try {
      const registration = await navigator.serviceWorker.ready;
      await registration.sync.register('sync-kpi-data');
      console.log('[PWA] Background sync registered');
    } catch (error) {
      console.error('[PWA] Background sync failed:', error);
    }
  }

  showUpdateNotification() {
    const notification = document.createElement('div');
    notification.className = 'pwa-update-notification';
    notification.innerHTML = `
      <div class="notification-content">
        <p>Yeni bir sürüm mevcut!</p>
        <button onclick="window.location.reload()">Güncelle</button>
      </div>
    `;
    document.body.appendChild(notification);
  }

  showNotification(title, message, type = 'info') {
    // Use existing notification manager if available
    if (window.NotificationManager) {
      window.NotificationManager.show({
        title,
        message,
        type,
        duration: 5000
      });
    } else {
      console.log(`[PWA] ${title}: ${message}`);
    }
  }

  // Queue data for background sync
  async queueData(url, method, data) {
    const db = await this.openDB();
    const tx = db.transaction('sync-queue', 'readwrite');
    const store = tx.objectStore('sync-queue');
    
    await store.add({
      url,
      method,
      data,
      timestamp: Date.now(),
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      }
    });
    
    console.log('[PWA] Data queued for sync');
  }

  openDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('kokpitim-db', 1);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains('sync-queue')) {
          db.createObjectStore('sync-queue', { keyPath: 'id', autoIncrement: true });
        }
      };
    });
  }
}

// Initialize PWA Manager
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.pwaManager = new PWAManager();
  });
} else {
  window.pwaManager = new PWAManager();
}
