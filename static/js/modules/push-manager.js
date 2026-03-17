/**
 * Push Notification Manager
 * Handles web push notifications subscription and management
 */

class PushManager {
  constructor() {
    this.vapidPublicKey = null;
    this.subscription = null;
    this.init();
  }

  async init() {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
      console.warn('[Push] Push notifications not supported');
      return;
    }

    // Get VAPID public key from server
    await this.fetchVapidKey();

    // Check existing subscription
    await this.checkSubscription();
  }

  async fetchVapidKey() {
    try {
      const response = await fetch('/api/push/vapid-key');
      const data = await response.json();
      this.vapidPublicKey = data.public_key;
    } catch (error) {
      console.error('[Push] Failed to fetch VAPID key:', error);
    }
  }

  async checkSubscription() {
    try {
      const registration = await navigator.serviceWorker.ready;
      this.subscription = await registration.pushManager.getSubscription();
      
      if (this.subscription) {
        console.log('[Push] Already subscribed');
        this.updateUI(true);
      } else {
        this.updateUI(false);
      }
    } catch (error) {
      console.error('[Push] Failed to check subscription:', error);
    }
  }

  async subscribe() {
    if (!this.vapidPublicKey) {
      console.error('[Push] VAPID key not available');
      return;
    }

    try {
      const registration = await navigator.serviceWorker.ready;

      
      // Request permission
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') {
        console.log('[Push] Permission denied');
        return;
      }

      // Subscribe to push
      this.subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.urlBase64ToUint8Array(this.vapidPublicKey)
      });

      // Send subscription to server
      await this.sendSubscriptionToServer(this.subscription);
      
      this.updateUI(true);
      console.log('[Push] Subscribed successfully');
    } catch (error) {
      console.error('[Push] Subscription failed:', error);
    }
  }

  async unsubscribe() {
    if (!this.subscription) return;

    try {
      await this.subscription.unsubscribe();
      await this.removeSubscriptionFromServer(this.subscription);
      
      this.subscription = null;
      this.updateUI(false);
      console.log('[Push] Unsubscribed successfully');
    } catch (error) {
      console.error('[Push] Unsubscribe failed:', error);
    }
  }

  async sendSubscriptionToServer(subscription) {
    try {
      await fetch('/api/push/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(subscription)
      });
    } catch (error) {
      console.error('[Push] Failed to send subscription:', error);
    }
  }

  async removeSubscriptionFromServer(subscription) {
    try {
      await fetch('/api/push/unsubscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(subscription)
      });
    } catch (error) {
      console.error('[Push] Failed to remove subscription:', error);
    }
  }

  updateUI(isSubscribed) {
    const subscribeBtn = document.getElementById('push-subscribe-btn');
    const unsubscribeBtn = document.getElementById('push-unsubscribe-btn');
    
    if (subscribeBtn && unsubscribeBtn) {
      subscribeBtn.style.display = isSubscribed ? 'none' : 'block';
      unsubscribeBtn.style.display = isSubscribed ? 'block' : 'none';
    }
  }

  urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/\-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }
}

// Initialize Push Manager
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.pushManager = new PushManager();
  });
} else {
  window.pushManager = new PushManager();
}
