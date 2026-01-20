class NotificationManager {
    constructor() {
        this.notificationBell = null;
        this.notificationDropdown = null;
        this.notificationBadge = null;
        this.notificationList = null;
        this.isDropdownOpen = false;
        this.unreadCount = 0;
        this.lastNotificationId = 0;
        this.pollingInterval = null;
        this.toastContainer = null;
        
        this.init();
    }

    init() {
        this.notificationBell = document.querySelector('.notification-bell');
        this.notificationDropdown = document.querySelector('.notification-dropdown');
        this.notificationBadge = document.querySelector('.notification-badge');
        this.notificationList = document.querySelector('.notification-list');
        
        // Create toast container
        this.createToastContainer();
        
        if (this.notificationBell) {
            this.setupEventListeners();
            this.loadNotifications();
            this.updateUnreadCount();
            this.startPolling();
        }
    }

    createToastContainer() {
        this.toastContainer = document.createElement('div');
        this.toastContainer.id = 'toast-container';
        this.toastContainer.className = 'fixed top-4 right-4 z-50 space-y-2';
        document.body.appendChild(this.toastContainer);
    }

    setupEventListeners() {
        // Toggle dropdown
        this.notificationBell.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggleDropdown();
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.notificationBell.contains(e.target) && !this.notificationDropdown.contains(e.target)) {
                this.closeDropdown();
            }
        });

        // Mark as read functionality
        if (this.notificationList) {
            this.notificationList.addEventListener('click', (e) => {
                if (e.target.classList.contains('mark-read-btn')) {
                    e.preventDefault();
                    const notificationId = e.target.dataset.notificationId;
                    this.markAsRead(notificationId);
                }
            });
        }

        // Mark all as read functionality
        const markAllReadBtn = document.getElementById('mark-all-read');
        if (markAllReadBtn) {
            markAllReadBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.markAllAsRead();
            });
        }
    }

    toggleDropdown() {
        if (this.isDropdownOpen) {
            this.closeDropdown();
        } else {
            this.openDropdown();
        }
    }

    openDropdown() {
        this.notificationDropdown.classList.remove('hidden');
        this.notificationDropdown.classList.add('block');
        this.isDropdownOpen = true;
        this.loadNotifications();
    }

    closeDropdown() {
        this.notificationDropdown.classList.add('hidden');
        this.notificationDropdown.classList.remove('block');
        this.isDropdownOpen = false;
    }

    async loadNotifications() {
        try {
            const response = await fetch('/api/notifications');
            const data = await response.json();
            
            if (data.success) {
                this.renderNotifications(data.notifications);
                this.checkForNewNotifications(data.notifications);
            }
        } catch (error) {
            console.error('Error loading notifications:', error);
            this.showToast('Failed to load notifications', 'error');
        }
    }

    checkForNewNotifications(notifications) {
        if (notifications.length > 0) {
            const latestNotification = notifications[0];
            if (latestNotification.id > this.lastNotificationId && this.lastNotificationId > 0) {
                // Show toast for new notification
                this.showToast(latestNotification.title, 'info', latestNotification.message);
            }
            this.lastNotificationId = Math.max(this.lastNotificationId, ...notifications.map(n => n.id));
        }
    }

    async updateUnreadCount() {
        try {
            const response = await fetch('/api/notifications/unread-count');
            const data = await response.json();
            
            if (data.success) {
                const oldCount = this.unreadCount;
                this.unreadCount = data.count;
                this.updateBadge();
                
                // Show toast for new unread notifications
                if (this.unreadCount > oldCount && oldCount > 0) {
                    const newCount = this.unreadCount - oldCount;
                    this.showToast(`You have ${newCount} new notification${newCount > 1 ? 's' : ''}`, 'info');
                }
            }
        } catch (error) {
            console.error('Error updating unread count:', error);
        }
    }

    updateBadge() {
        if (this.notificationBadge) {
            if (this.unreadCount > 0) {
                this.notificationBadge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
                this.notificationBadge.classList.remove('hidden');
                
                // Add animation for new notifications
                this.notificationBadge.classList.add('animate-pulse');
                setTimeout(() => {
                    this.notificationBadge.classList.remove('animate-pulse');
                }, 2000);
            } else {
                this.notificationBadge.classList.add('hidden');
            }
        }
    }

    renderNotifications(notifications) {
        if (!this.notificationList) return;

        if (notifications.length === 0) {
            this.notificationList.innerHTML = `
                <div class="p-4 text-center text-gray-500">
                    <i data-feather="bell" class="w-8 h-8 mx-auto mb-2 text-gray-400"></i>
                    <p class="text-sm">No notifications yet</p>
                </div>
            `;
            return;
        }

        const notificationsHtml = notifications.map(notification => {
            const timeAgo = this.getTimeAgo(notification.created_at);
            const iconClass = this.getNotificationIcon(notification.type);
            const isUnread = !notification.is_read;
            
            return `
                <div class="notification-item p-4 hover:bg-gray-50 transition-colors ${isUnread ? 'bg-blue-50' : ''}" 
                     data-notification-id="${notification.id}">
                    <div class="flex items-start space-x-3">
                        <div class="flex-shrink-0">
                            <div class="w-8 h-8 rounded-full flex items-center justify-center ${iconClass.bg} ${iconClass.text}">
                                <i data-feather="${iconClass.icon}" class="w-4 h-4"></i>
                            </div>
                        </div>
                        <div class="flex-1 min-w-0">
                            <div class="flex items-center justify-between">
                                <h4 class="text-sm font-medium text-gray-900 ${isUnread ? 'font-semibold' : ''}">
                                    ${notification.title}
                                </h4>
                                <span class="text-xs text-gray-500">${timeAgo}</span>
                            </div>
                            <p class="text-sm text-gray-600 mt-1">${notification.message}</p>
                            ${isUnread ? `
                                <button class="mark-read-btn text-xs text-blue-600 hover:text-blue-800 font-medium mt-2" 
                                        data-notification-id="${notification.id}">
                                    Mark as read
                                </button>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        this.notificationList.innerHTML = notificationsHtml;
        
        // Reinitialize Feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }

    getNotificationIcon(type) {
        const icons = {
            'contract': { icon: 'file-text', bg: 'bg-blue-100', text: 'text-blue-600' },
            'session': { icon: 'video', bg: 'bg-green-100', text: 'text-green-600' },
            'message': { icon: 'message-circle', bg: 'bg-purple-100', text: 'text-purple-600' },
            'job': { icon: 'briefcase', bg: 'bg-orange-100', text: 'text-orange-600' },
            'system': { icon: 'bell', bg: 'bg-gray-100', text: 'text-gray-600' }
        };
        return icons[type] || icons['system'];
    }

    getTimeAgo(dateString) {
        if (!dateString) return 'Recently';
        
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}d ago`;
        
        return date.toLocaleDateString();
    }

    async markAsRead(notificationId) {
        try {
            const response = await fetch(`/api/notifications/${notificationId}/mark-read`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                }
            });
            
            const data = await response.json();
            if (data.success) {
                // Update the notification item styling
                const notificationItem = document.querySelector(`[data-notification-id="${notificationId}"]`);
                if (notificationItem) {
                    notificationItem.classList.remove('bg-blue-50');
                    const markReadBtn = notificationItem.querySelector('.mark-read-btn');
                    if (markReadBtn) markReadBtn.remove();
                }
                
                // Update unread count
                this.updateUnreadCount();
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
            this.showToast('Failed to mark notification as read', 'error');
        }
    }

    async markAllAsRead() {
        try {
            const response = await fetch('/api/notifications/mark-all-read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                }
            });
            
            const data = await response.json();
            if (data.success) {
                // Update all notification items
                const notificationItems = document.querySelectorAll('.notification-item');
                notificationItems.forEach(item => {
                    item.classList.remove('bg-blue-50');
                    const markReadBtn = item.querySelector('.mark-read-btn');
                    if (markReadBtn) markReadBtn.remove();
                });
                
                // Update unread count
                this.updateUnreadCount();
                this.showToast('All notifications marked as read', 'success');
            }
        } catch (error) {
            console.error('Error marking all notifications as read:', error);
            this.showToast('Failed to mark all notifications as read', 'error');
        }
    }

    showToast(message, type = 'info', description = '') {
        const toast = document.createElement('div');
        toast.className = `transform transition-all duration-300 ease-in-out translate-x-full`;
        
        const bgColor = {
            'success': 'bg-green-500',
            'error': 'bg-red-500',
            'warning': 'bg-yellow-500',
            'info': 'bg-blue-500'
        }[type] || 'bg-blue-500';
        
        const icon = {
            'success': 'check-circle',
            'error': 'alert-circle',
            'warning': 'alert-triangle',
            'info': 'info'
        }[type] || 'info';
        
        toast.innerHTML = `
            <div class="flex items-center p-4 ${bgColor} text-white rounded-lg shadow-lg max-w-sm">
                <i data-feather="${icon}" class="w-5 h-5 mr-3 flex-shrink-0"></i>
                <div class="flex-1">
                    <div class="font-medium">${message}</div>
                    ${description ? `<div class="text-sm opacity-90">${description}</div>` : ''}
                </div>
                <button class="ml-3 text-white hover:text-gray-200 transition-colors">
                    <i data-feather="x" class="w-4 h-4"></i>
                </button>
            </div>
        `;
        
        this.toastContainer.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);
        
        // Initialize Feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
        
        // Add click handler for close button
        const closeBtn = toast.querySelector('button');
        closeBtn.addEventListener('click', () => {
            this.removeToast(toast);
        });
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            this.removeToast(toast);
        }, 5000);
    }

    removeToast(toast) {
        toast.classList.add('translate-x-full');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    startPolling() {
        // Update unread count every 30 seconds
        this.pollingInterval = setInterval(() => {
            this.updateUnreadCount();
        }, 30000);
    }

    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }

    // Public method to manually trigger notification check
    checkNotifications() {
        this.loadNotifications();
        this.updateUnreadCount();
    }
}

// Initialize notification manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.notificationManager = new NotificationManager();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationManager;
}
