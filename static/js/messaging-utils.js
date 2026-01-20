/**
 * Messaging Utilities - Additional functionality for the messaging system
 * Provides typing indicators, message status updates, and advanced features
 */

class MessagingUtils {
    constructor(messagingSystem) {
        this.messagingSystem = messagingSystem;
        this.typingUsers = new Map();
        this.messageStatuses = new Map();
        this.notificationSound = null;
        this.init();
    }

    init() {
        this.setupTypingIndicators();
        this.setupMessageStatusUpdates();
        this.setupNotifications();
        this.setupKeyboardShortcuts();
        this.setupDragAndDrop();
    }

    /**
     * Setup typing indicators
     */
    setupTypingIndicators() {
        // Create typing indicator element
        this.createTypingIndicator();
        
        // Listen for typing events from other users
        this.messagingSystem.onMessageReceived((messages) => {
            // Check if any messages indicate typing stopped
            this.handleTypingStopped();
        });
    }

    createTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.innerHTML = `
            <div class="typing-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <small class="typing-text">Someone is typing...</small>
            </div>
        `;
        indicator.style.display = 'none';
        
        // Insert before message input
        const messageInput = document.querySelector('.message-input-container');
        if (messageInput) {
            messageInput.parentNode.insertBefore(indicator, messageInput);
        }
    }

    showTypingIndicator(userName) {
        const indicator = document.querySelector('.typing-indicator');
        if (indicator) {
            const typingText = indicator.querySelector('.typing-text');
            if (typingText) {
                typingText.textContent = `${userName} is typing...`;
            }
            indicator.style.display = 'block';
        }
    }

    hideTypingIndicator() {
        const indicator = document.querySelector('.typing-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }

    handleTypingStopped() {
        // Hide typing indicator after a delay
        setTimeout(() => {
            this.hideTypingIndicator();
        }, 3000);
    }

    /**
     * Setup message status updates
     */
    setupMessageStatusUpdates() {
        // Update message statuses periodically
        setInterval(() => {
            this.updateMessageStatuses();
        }, 5000);
    }

    async updateMessageStatuses() {
        const conversationId = this.messagingSystem.getCurrentConversationId();
        if (!conversationId) return;

        try {
            const response = await this.messagingSystem.makeRequest(`/api/messages/status/${conversationId}`);
            if (response.success) {
                this.updateMessageStatusUI(response.statuses);
            }
        } catch (error) {
            console.error('Error updating message statuses:', error);
        }
    }

    updateMessageStatusUI(statuses) {
        statuses.forEach(status => {
            const messageElement = document.querySelector(`[data-message-id="${status.message_id}"]`);
            if (messageElement) {
                const statusIcon = messageElement.querySelector('.message-status');
                if (statusIcon) {
                    this.updateStatusIcon(statusIcon, status.status);
                }
            }
        });
    }

    updateStatusIcon(icon, status) {
        // Remove existing classes
        icon.classList.remove('fa-check', 'fa-check-double', 'text-muted', 'text-primary');
        
        // Add appropriate classes based on status
        switch (status) {
            case 'sent':
                icon.classList.add('fa-check', 'text-muted');
                break;
            case 'delivered':
                icon.classList.add('fa-check-double', 'text-muted');
                break;
            case 'read':
                icon.classList.add('fa-check-double', 'text-primary');
                break;
        }
    }

    /**
     * Setup notifications
     */
    setupNotifications() {
        // Request notification permission
        if ('Notification' in window) {
            Notification.requestPermission();
        }

        // Setup notification sound
        this.setupNotificationSound();

        // Listen for new messages
        this.messagingSystem.onMessageReceived((messages) => {
            if (document.hidden) {
                this.showNotification(messages);
            }
        });
    }

    setupNotificationSound() {
        // Create audio element for notification sound
        this.notificationSound = new Audio('/static/sounds/notification.mp3');
        this.notificationSound.volume = 0.5;
    }

    showNotification(messages) {
        const lastMessage = messages[messages.length - 1];
        const senderName = lastMessage.sender_name || 'Someone';
        const content = lastMessage.content.length > 50 
            ? lastMessage.content.substring(0, 50) + '...' 
            : lastMessage.content;

        // Browser notification
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('New Message', {
                body: `${senderName}: ${content}`,
                icon: '/static/images/logo.png',
                tag: 'message'
            });
        }

        // Play notification sound
        if (this.notificationSound) {
            this.notificationSound.play().catch(e => console.log('Could not play notification sound'));
        }

        // Update page title
        this.updatePageTitle();
    }

    updatePageTitle() {
        const originalTitle = document.title.replace(/^\(\d+\)\s*/, '');
        const currentTitle = document.title;
        
        if (!currentTitle.startsWith('(')) {
            document.title = `(1) ${originalTitle}`;
        } else {
            const count = parseInt(currentTitle.match(/\((\d+)\)/)[1]) + 1;
            document.title = `(${count}) ${originalTitle}`;
        }
    }

    resetPageTitle() {
        const originalTitle = document.title.replace(/^\(\d+\)\s*/, '');
        document.title = originalTitle;
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Enter to send message
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                this.messagingSystem.sendMessage();
            }

            // Ctrl/Cmd + K to focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.getElementById('searchInput');
                if (searchInput) {
                    searchInput.focus();
                }
            }

            // Escape to clear search or close modals
            if (e.key === 'Escape') {
                const searchInput = document.getElementById('searchInput');
                if (searchInput && searchInput.value) {
                    searchInput.value = '';
                    searchInput.dispatchEvent(new Event('input'));
                }
            }
        });
    }

    /**
     * Setup drag and drop for files
     */
    setupDragAndDrop() {
        const messageInput = document.getElementById('messageInput');
        if (!messageInput) return;

        const container = messageInput.closest('.message-input-container');
        if (!container) return;

        container.addEventListener('dragover', (e) => {
            e.preventDefault();
            container.classList.add('drag-over');
        });

        container.addEventListener('dragleave', (e) => {
            e.preventDefault();
            container.classList.remove('drag-over');
        });

        container.addEventListener('drop', (e) => {
            e.preventDefault();
            container.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleDroppedFiles(files);
            }
        });
    }

    handleDroppedFiles(files) {
        const file = files[0]; // Handle only the first file for now
        if (file) {
            // Create a fake event object
            const fakeEvent = {
                target: {
                    files: [file]
                }
            };
            this.messagingSystem.handleFileUpload(fakeEvent);
        }
    }

    /**
     * Message formatting utilities
     */
    formatMessageContent(content) {
        // Convert URLs to links
        content = this.linkifyUrls(content);
        
        // Convert line breaks to <br> tags
        content = content.replace(/\n/g, '<br>');
        
        return content;
    }

    linkifyUrls(text) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return text.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
    }

    /**
     * Message search utilities
     */
    highlightSearchTerm(text, searchTerm) {
        if (!searchTerm) return text;
        
        const regex = new RegExp(`(${this.escapeRegex(searchTerm)})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    /**
     * Conversation utilities
     */
    getConversationPreview(message) {
        if (message.message_type === 'file') {
            return `📎 ${message.file_name || 'File'}`;
        }
        
        const content = message.content;
        return content.length > 50 ? content.substring(0, 50) + '...' : content;
    }

    formatConversationTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffInMinutes = (now - date) / (1000 * 60);
        
        if (diffInMinutes < 1) {
            return 'Just now';
        } else if (diffInMinutes < 60) {
            return `${Math.floor(diffInMinutes)}m ago`;
        } else if (diffInMinutes < 1440) {
            return `${Math.floor(diffInMinutes / 60)}h ago`;
        } else {
            return date.toLocaleDateString();
        }
    }

    /**
     * File utilities
     */
    getFileIcon(fileName) {
        const extension = fileName.split('.').pop().toLowerCase();
        
        const iconMap = {
            'pdf': 'fa-file-pdf',
            'doc': 'fa-file-word',
            'docx': 'fa-file-word',
            'xls': 'fa-file-excel',
            'xlsx': 'fa-file-excel',
            'txt': 'fa-file-alt',
            'png': 'fa-file-image',
            'jpg': 'fa-file-image',
            'jpeg': 'fa-file-image',
            'gif': 'fa-file-image'
        };
        
        return iconMap[extension] || 'fa-file';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * UI utilities
     */
    showLoadingOverlay(message = 'Loading...') {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">${message}</p>
            </div>
        `;
        
        document.body.appendChild(overlay);
        return overlay;
    }

    hideLoadingOverlay(overlay) {
        if (overlay && overlay.parentNode) {
            overlay.parentNode.removeChild(overlay);
        }
    }

    /**
     * Error handling utilities
     */
    showRetryDialog(message, retryFunction) {
        const dialog = document.createElement('div');
        dialog.className = 'retry-dialog';
        dialog.innerHTML = `
            <div class="retry-content">
                <i class="fas fa-exclamation-triangle text-warning"></i>
                <h5>Connection Error</h5>
                <p>${message}</p>
                <div class="retry-actions">
                    <button class="btn btn-primary retry-btn">Retry</button>
                    <button class="btn btn-secondary cancel-btn">Cancel</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
        
        // Bind events
        dialog.querySelector('.retry-btn').addEventListener('click', () => {
            retryFunction();
            dialog.remove();
        });
        
        dialog.querySelector('.cancel-btn').addEventListener('click', () => {
            dialog.remove();
        });
    }

    /**
     * Performance utilities
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    /**
     * Storage utilities
     */
    saveToLocalStorage(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
        } catch (error) {
            console.error('Error saving to localStorage:', error);
        }
    }

    loadFromLocalStorage(key) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('Error loading from localStorage:', error);
            return null;
        }
    }

    removeFromLocalStorage(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Error removing from localStorage:', error);
        }
    }

    /**
     * Analytics utilities
     */
    trackEvent(eventName, properties = {}) {
        // Send analytics event
        if (window.gtag) {
            window.gtag('event', eventName, properties);
        }
        
        // Log to console in development
        if (process.env.NODE_ENV === 'development') {
            console.log('Analytics Event:', eventName, properties);
        }
    }

    trackMessageSent(messageType) {
        this.trackEvent('message_sent', {
            message_type: messageType,
            conversation_id: this.messagingSystem.getCurrentConversationId()
        });
    }

    trackFileUploaded(fileType, fileSize) {
        this.trackEvent('file_uploaded', {
            file_type: fileType,
            file_size: fileSize
        });
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MessagingUtils;
}

// Add to global scope for easy access
window.MessagingUtils = MessagingUtils;
