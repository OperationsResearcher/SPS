/**
 * NOTIFICATION MANAGER
 * Sprint 7-9: Real-Time ve Bildirimler
 * Real-time bildirim yönetimi
 */

class NotificationManager {
    constructor() {
        this.socket = null;
        this.unreadCount = 0;
        this.notifications = [];
        this.init();
    }
    
    init() {
        this.connectWebSocket();
        this.setupEventListeners();
        this.loadNotifications();
    }
    
    connectWebSocket() {
        // Socket.IO bağlantısı
        this.socket = io({
            transports: ['websocket', 'polling']
        });
        
        // Bağlantı olayları
        this.socket.on('connect', () => {
            console.log('WebSocket connected');
            this.onConnect();
        });
        
        this.socket.on('disconnect', () => {
            console.log('WebSocket disconnected');
        });
        
        // Bildirim olayları
        this.socket.on('new_notification', (data) => {
            this.handleNewNotification(data);
        });
        
        this.socket.on('unread_count', (data) => {
            this.updateUnreadCount(data.count);
        });
        
        // Collaboration olayları
        this.socket.on('user_joined', (data) => {
            this.handleUserJoined(data);
        });
        
        this.socket.on('user_left', (data) => {
            this.handleUserLeft(data);
        });
        
        this.socket.on('kpi_updated', (data) => {
            this.handleKpiUpdated(data);
        });
        
        this.socket.on('user_typing', (data) => {
            this.handleUserTyping(data);
        });
    }

    
    setupEventListeners() {
        // Bildirim paneli toggle
        document.addEventListener('click', (e) => {
            if (e.target.matches('.notification-bell')) {
                this.toggleNotificationPanel();
            }
            
            if (e.target.matches('.notification-item')) {
                this.handleNotificationClick(e.target);
            }
            
            if (e.target.matches('.mark-all-read')) {
                this.markAllAsRead();
            }
        });
    }
    
    async loadNotifications() {
        try {
            const response = await fetch('/api/notifications');
            const data = await response.json();
            this.notifications = data.notifications || [];
            this.updateNotificationPanel();
        } catch (error) {
            console.error('Load notifications error:', error);
        }
    }
    
    handleNewNotification(notification) {
        // Yeni bildirim geldi
        this.notifications.unshift(notification);
        this.unreadCount++;
        
        // UI güncelle
        this.updateUnreadCount(this.unreadCount);
        this.updateNotificationPanel();
        
        // Toast göster
        this.showToast(notification);
        
        // Ses çal (opsiyonel)
        this.playNotificationSound();
    }
    
    updateUnreadCount(count) {
        this.unreadCount = count;
        
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'block' : 'none';
        }
    }
    
    updateNotificationPanel() {
        const panel = document.querySelector('.notification-panel');
        if (!panel) return;
        
        const list = panel.querySelector('.notification-list');
        if (!list) return;
        
        if (this.notifications.length === 0) {
            list.innerHTML = '<div class="no-notifications">Bildirim yok</div>';
            return;
        }
        
        list.innerHTML = this.notifications.map(n => this.renderNotification(n)).join('');
    }
    
    renderNotification(notification) {
        const priorityClass = `priority-${notification.priority}`;
        const readClass = notification.is_read ? 'read' : 'unread';
        const icon = this.getNotificationIcon(notification.type);
        
        return `
            <div class="notification-item ${readClass} ${priorityClass}" data-id="${notification.id}">
                <div class="notification-icon">${icon}</div>
                <div class="notification-content">
                    <div class="notification-title">${notification.title}</div>
                    <div class="notification-message">${notification.message}</div>
                    <div class="notification-time">${this.formatTime(notification.created_at)}</div>
                </div>
                ${!notification.is_read ? '<div class="notification-dot"></div>' : ''}
            </div>
        `;
    }
    
    getNotificationIcon(type) {
        const icons = {
            'performance_alert': '⚠️',
            'task_reminder': '📋',
            'collaboration': '👥',
            'achievement': '🏆',
            'system': 'ℹ️'
        };
        return icons[type] || 'ℹ️';
    }
    
    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = Math.floor((now - date) / 1000);
        
        if (diff < 60) return 'Az önce';
        if (diff < 3600) return `${Math.floor(diff / 60)} dakika önce`;
        if (diff < 86400) return `${Math.floor(diff / 3600)} saat önce`;
        if (diff < 604800) return `${Math.floor(diff / 86400)} gün önce`;
        return date.toLocaleDateString('tr-TR');
    }
    
    showToast(notification) {
        const toast = document.createElement('div');
        toast.className = `notification-toast priority-${notification.priority}`;
        toast.innerHTML = `
            <div class="toast-icon">${this.getNotificationIcon(notification.type)}</div>
            <div class="toast-content">
                <div class="toast-title">${notification.title}</div>
                <div class="toast-message">${notification.message}</div>
            </div>
            <button class="toast-close">&times;</button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
        
        // Close button
        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 300);
        });
    }
    
    playNotificationSound() {
        // Basit bildirim sesi
        const audio = new Audio('/static/sounds/notification.mp3');
        audio.volume = 0.3;
        audio.play().catch(() => {
            // Ses çalma hatası (kullanıcı izni gerekebilir)
        });
    }
    
    toggleNotificationPanel() {
        const panel = document.querySelector('.notification-panel');
        if (panel) {
            panel.classList.toggle('open');
        }
    }
    
    async handleNotificationClick(element) {
        const notificationId = element.dataset.id;
        
        // Okundu olarak işaretle
        await this.markAsRead(notificationId);
        
        // Action URL varsa yönlendir
        const notification = this.notifications.find(n => n.id == notificationId);
        if (notification && notification.action_url) {
            window.location.href = notification.action_url;
        }
    }
    
    async markAsRead(notificationId) {
        try {
            this.socket.emit('mark_notification_read', { notification_id: notificationId });
            
            // Local state güncelle
            const notification = this.notifications.find(n => n.id == notificationId);
            if (notification) {
                notification.is_read = true;
                this.updateNotificationPanel();
            }
        } catch (error) {
            console.error('Mark as read error:', error);
        }
    }
    
    async markAllAsRead() {
        try {
            const response = await fetch('/api/notifications/mark-all-read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content
                }
            });
            
            if (response.ok) {
                this.notifications.forEach(n => n.is_read = true);
                this.updateUnreadCount(0);
                this.updateNotificationPanel();
            }
        } catch (error) {
            console.error('Mark all as read error:', error);
        }
    }
    
    // Collaboration methods
    joinProcess(processId) {
        this.socket.emit('join_process', { process_id: processId });
    }
    
    leaveProcess(processId) {
        this.socket.emit('leave_process', { process_id: processId });
    }
    
    broadcastKpiUpdate(processId, kpiId, field, value) {
        this.socket.emit('kpi_data_update', {
            process_id: processId,
            kpi_id: kpiId,
            field: field,
            value: value
        });
    }
    
    handleUserJoined(data) {
        console.log(`User ${data.username} joined process ${data.process_id}`);
        // UI'da göster
        this.showUserPresence(data.user_id, data.username, 'joined');
    }
    
    handleUserLeft(data) {
        console.log(`User ${data.username} left process ${data.process_id}`);
        this.showUserPresence(data.user_id, data.username, 'left');
    }
    
    handleKpiUpdated(data) {
        console.log(`KPI ${data.kpi_id} updated by ${data.updated_by}`);
        // UI'da güncelle
        this.updateKpiInUI(data.kpi_id, data.field, data.value);
    }
    
    handleUserTyping(data) {
        console.log(`User ${data.username} is typing in ${data.field}`);
        // Typing indicator göster
    }
    
    showUserPresence(userId, username, action) {
        // Kullanıcı presence göstergesi
        const message = action === 'joined' 
            ? `${username} sayfaya katıldı` 
            : `${username} sayfadan ayrıldı`;
        
        this.showToast({
            type: 'collaboration',
            title: 'İşbirliği',
            message: message,
            priority: 'low'
        });
    }
    
    updateKpiInUI(kpiId, field, value) {
        // KPI değerini UI'da güncelle
        const element = document.querySelector(`[data-kpi-id="${kpiId}"][data-field="${field}"]`);
        if (element) {
            element.textContent = value;
            element.classList.add('updated-by-other');
            setTimeout(() => element.classList.remove('updated-by-other'), 2000);
        }
    }
    
    onConnect() {
        // Bağlantı kurulduğunda
        console.log('Notification manager connected');
    }
}

// Global instance
window.notificationManager = new NotificationManager();

// Export
window.NotificationManager = NotificationManager;
