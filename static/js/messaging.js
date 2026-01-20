/**
 * Skileez Messaging System JavaScript
 * Complete messaging functionality for real-time chat
 */

class MessagingSystem {
    constructor() {
        this.currentConversationId = null;
        this.lastMessageId = null;
        this.updateInterval = null;
        this.unreadCountInterval = null;
        this.typingTimeout = null;
        this.isTyping = false;
        this.isInitialized = false;
        
        // Configuration
        this.config = {
            updateFrequency: 10000, // 10 seconds
            unreadUpdateFrequency: 30000, // 30 seconds
            typingTimeout: 3000, // 3 seconds
            maxMessageLength: 5000,
            autoScrollThreshold: 100
        };
        
        this.init();
    }

    init() {
        if (this.isInitialized) return;
        
        this.setupEventListeners();
        this.startUnreadCountUpdates();
        this.isInitialized = true;
        
        console.log('Messaging system initialized');
    }

    setupEventListeners() {
        // Page visibility change handling
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseUpdates();
            } else {
                this.resumeUpdates();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));

        // Window beforeunload cleanup
        window.addEventListener('beforeunload', () => this.cleanup());
    }

    // ============================================================================
    // CONVERSATION MANAGEMENT
    // ============================================================================

    selectConversation(conversationId) {
        this.currentConversationId = conversationId;
        
        // Update active state in sidebar
        this.updateConversationActiveState(conversationId);
        
        // Navigate to conversation
        window.location.href = `/messages/${conversationId}`;
    }

    updateConversationActiveState(conversationId) {
        // Remove active class from all conversation items
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active class to selected conversation
        const selectedItem = document.querySelector(`[data-conversation-id="${conversationId}"]`);
        if (selectedItem) {
            selectedItem.classList.add('active');
        }
    }

    refreshConversations() {
        this.showLoading();
        window.location.reload();
    }

    // ============================================================================
    // MESSAGE SENDING AND RECEIVING
    // ============================================================================

    async sendMessage(conversationId, content) {
        if (!content.trim()) {
            throw new Error('Message content is required');
        }

        if (content.length > this.config.maxMessageLength) {
            throw new Error(`Message is too long (max ${this.config.maxMessageLength} characters)`);
        }

        try {
            const response = await fetch('/api/messages/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    conversation_id: conversationId,
                    content: content
                })
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Failed to send message');
            }

            return data.message;
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    }

    addMessageToUI(message, isOwn = false, animate = true) {
        const messagesWrapper = document.getElementById('messages-wrapper');
        if (!messagesWrapper) return;

        // Remove no-messages state if present
        const noMessagesState = messagesWrapper.querySelector('.no-messages-state');
        if (noMessagesState) {
            noMessagesState.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message-item mb-3 ${isOwn ? 'message-sent' : 'message-received'}`;
        messageDiv.dataset.messageId = message.id;
        
        if (animate) {
            messageDiv.style.opacity = '0';
            messageDiv.style.transform = 'translateY(20px)';
        }

        // Build message HTML
        const messageHtml = this.buildMessageHTML(message, isOwn);
        messageDiv.innerHTML = messageHtml;

        messagesWrapper.appendChild(messageDiv);

        // Animate message appearance
        if (animate) {
            requestAnimationFrame(() => {
                messageDiv.style.transition = 'all 0.3s ease-out';
                messageDiv.style.opacity = '1';
                messageDiv.style.transform = 'translateY(0)';
            });
        }

        // Update last message ID
        this.lastMessageId = Math.max(this.lastMessageId || 0, message.id);

        // Auto-scroll to bottom
        this.scrollToBottom();

        return messageDiv;
    }

    buildMessageHTML(message, isOwn) {
        const time = this.formatMessageTime(message.created_at);
        const content = this.escapeHtml(message.content).replace(/\n/g, '<br>');
        
        if (isOwn) {
            return `
                <div class="d-flex align-items-start justify-content-end">
                    <div class="flex-grow-1 max-width-70 text-end">
                        <div class="message-bubble sent">
                            <div class="message-content">${content}</div>
                            <div class="message-time">
                                ${time}
                                <i class="fas fa-check ms-1" title="Sent"></i>
                                ${message.edited_at ? '<small class="edited-indicator">(edited)</small>' : ''}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            const profilePic = this.getProfilePicture();
            const participantInitial = this.getParticipantInitial();
            
            return `
                <div class="d-flex align-items-start">
                    <div class="flex-shrink-0 me-2">
                        ${profilePic ? 
                            `<img src="${profilePic}" class="rounded-circle message-avatar" width="30" height="30" alt="Profile">` :
                            `<div class="message-avatar-placeholder rounded-circle">
                                <span class="small text-white">${participantInitial}</span>
                            </div>`
                        }
                    </div>
                    <div class="flex-grow-1 max-width-70">
                        <div class="message-bubble received">
                            <div class="message-content">${content}</div>
                            <div class="message-time">
                                ${time}
                                ${message.edited_at ? '<small class="edited-indicator">(edited)</small>' : ''}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    // ============================================================================
    // REAL-TIME UPDATES
    // ============================================================================

    startMessageUpdates(conversationId) {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }

        this.updateInterval = setInterval(() => {
            this.checkForNewMessages(conversationId);
        }, this.config.updateFrequency);
    }

    stopMessageUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    async checkForNewMessages(conversationId) {
        try {
            const response = await fetch(`/api/messages/check-new?conversation_id=${conversationId}&last_message_id=${this.lastMessageId || 0}`);
            const data = await response.json();

            if (data.success && data.messages && data.messages.length > 0) {
                data.messages.forEach(message => {
                    this.addMessageToUI(message, false);
                });
                
                // Mark messages as read
                this.markMessagesAsRead(conversationId);
            }
        } catch (error) {
            console.error('Error checking for new messages:', error);
        }
    }

    startUnreadCountUpdates() {
        if (this.unreadCountInterval) {
            clearInterval(this.unreadCountInterval);
        }

        this.unreadCountInterval = setInterval(() => {
            this.updateUnreadCount();
        }, this.config.unreadUpdateFrequency);

        // Initial update
        this.updateUnreadCount();
    }

    async updateUnreadCount() {
        try {
            const response = await fetch('/api/messages/unread-count');
            const data = await response.json();

            this.updateUnreadBadges(data.unread_count);
            this.updatePageTitle(data.unread_count);
        } catch (error) {
            console.error('Error updating unread count:', error);
        }
    }

    updateUnreadBadges(count) {
        // Update all unread badges in navigation
        const badges = document.querySelectorAll('.unread-badge, [class*="unread"]');
        
        badges.forEach(badge => {
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        });
    }

    updatePageTitle(count) {
        const title = document.title;
        
        if (count > 0) {
            if (!title.startsWith('(')) {
                document.title = `(${count}) ${title}`;
            } else {
                document.title = title.replace(/^\(\d+\)/, `(${count})`);
            }
        } else {
            if (title.startsWith('(')) {
                document.title = title.replace(/^\(\d+\)\s/, '');
            }
        }
    }

    // ============================================================================
    // MESSAGE ACTIONS
    // ============================================================================

    async markMessagesAsRead(conversationId) {
        try {
            const response = await fetch('/api/messages/mark-read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    conversation_id: conversationId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.updateReadIndicators();
            }
        } catch (error) {
            console.error('Error marking messages as read:', error);
        }
    }

    updateReadIndicators() {
        // Update read status for sent messages
        const sentMessages = document.querySelectorAll('.message-sent .fa-check:not(.fa-check-double)');
        sentMessages.forEach(icon => {
            icon.className = 'fas fa-check-double text-primary ms-1';
            icon.title = 'Read';
        });
    }

    async archiveConversation(conversationId) {
        if (!confirm('Are you sure you want to archive this conversation?')) {
            return false;
        }

        try {
            const response = await fetch(`/api/conversations/archive/${conversationId}`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                this.showSuccess('Conversation archived successfully');
                window.location.href = '/messages';
                return true;
            } else {
                throw new Error(data.error || 'Failed to archive conversation');
            }
        } catch (error) {
            console.error('Error archiving conversation:', error);
            this.showError('Error archiving conversation: ' + error.message);
            return false;
        }
    }

    // ============================================================================
    // CONTRACT ACTIONS
    // ============================================================================

    viewContractFromMessage(messageId) {
        // Find the contract associated with this message
        fetch(`/api/contracts/view/${messageId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.contract_url) {
                    window.open(data.contract_url, '_blank');
                } else {
                    // Fallback: try to find contract through proposals
                    window.location.href = `/contracts/find-from-message/${messageId}`;
                }
            })
            .catch(error => {
                console.error('Error finding contract:', error);
                // Fallback to a general contracts page
                window.location.href = '/contracts';
            });
    }

    acceptContractFromMessage(messageId) {
        if (!confirm('Are you sure you want to accept this contract offer?')) {
            return;
        }

        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (!messageElement) return;

        // Extract contract data from the message
        const contractInfo = messageElement.querySelector('.contract-preview-card .contract-info-grid');
        if (!contractInfo) return;

        const project = contractInfo.querySelector('.info-item:nth-child(1) .value')?.textContent.trim() || 'Learning Project';
        const sessions = contractInfo.querySelector('.info-item:nth-child(2) .value')?.textContent.trim() || 'N/A';
        const amount = contractInfo.querySelector('.info-item:nth-child(3) .value')?.textContent.trim() || 'N/A';
        const startDate = contractInfo.querySelector('.info-item:nth-child(4) .value')?.textContent.trim() || 'N/A';

        const contractData = {
            project: project,
            sessions: sessions,
            amount: amount,
            start_date: startDate
        };

        fetch('/api/contracts/accept', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message_id: messageId,
                contract_data: contractData
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showToast('Contract accepted successfully!', 'success');
                
                // Update message UI to show acceptance
                const messageBubble = messageElement.querySelector('.message-bubble');
                if (messageBubble) {
                    messageBubble.classList.add('contract-accepted');
                    const contractCard = messageBubble.querySelector('.contract-preview-card');
                    if (contractCard) {
                        contractCard.innerHTML = `
                            <div class="contract-header">
                                <div class="contract-icon">
                                    <i class="fas fa-check-circle"></i>
                                </div>
                                <div class="contract-title">
                                    <h4>Contract Accepted</h4>
                                    <span class="contract-status active">Active</span>
                                </div>
                            </div>
                            <div class="contract-details">
                                <div class="contract-info-grid">
                                    <div class="info-item">
                                        <span class="label">Project</span>
                                        <span class="value">${project}</span>
                                    </div>
                                    <div class="info-item">
                                        <span class="label">Status</span>
                                        <span class="value">Active</span>
                                    </div>
                                </div>
                            </div>
                        `;
                    }
                }
            } else {
                this.showToast('Failed to accept contract: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error accepting contract:', error);
            this.showToast('Error accepting contract', 'error');
        });
    }

    declineContractFromMessage(messageId) {
        if (!confirm('Are you sure you want to decline this contract offer?')) {
            return;
        }

        fetch('/api/contracts/decline', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message_id: messageId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showToast('Contract declined successfully.', 'warning');
                
                // Update message UI to show decline
                const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
                const messageBubble = messageElement?.querySelector('.message-bubble');
                if (messageBubble) {
                    messageBubble.classList.add('contract-declined');
                    const contractCard = messageBubble.querySelector('.contract-preview-card');
                    if (contractCard) {
                        contractCard.innerHTML = `
                            <div class="contract-header">
                                <div class="contract-icon">
                                    <i class="fas fa-times-circle"></i>
                                </div>
                                <div class="contract-title">
                                    <h4>Contract Declined</h4>
                                    <span class="contract-status cancelled">Cancelled</span>
                                </div>
                            </div>
                        `;
                    }
                }
            } else {
                this.showToast('Failed to decline contract: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error declining contract:', error);
            this.showToast('Error declining contract', 'error');
        });
    }

    // ============================================================================
    // SEARCH FUNCTIONALITY
    // ============================================================================

    async searchMessages(query) {
        if (!query.trim()) {
            return { conversations: [], messages: [] };
        }

        try {
            const response = await fetch(`/api/messages/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data.success) {
                return {
                    conversations: data.conversations || [],
                    messages: data.messages || []
                };
            } else {
                throw new Error(data.error || 'Search failed');
            }
        } catch (error) {
            console.error('Error searching messages:', error);
            throw error;
        }
    }

    setupSearchInput(inputElement, resultsContainer) {
        let searchTimeout;

        inputElement.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            
            clearTimeout(searchTimeout);
            
            if (query.length < 2) {
                resultsContainer.innerHTML = '';
                return;
            }

            searchTimeout = setTimeout(async () => {
                try {
                    this.showLoading();
                    const results = await this.searchMessages(query);
                    this.displaySearchResults(results, resultsContainer);
                } catch (error) {
                    this.showError('Search failed: ' + error.message);
                } finally {
                    this.hideLoading();
                }
            }, 300);
        });
    }

    displaySearchResults(results, container) {
        let html = '';

        if (results.conversations.length > 0) {
            html += '<h6 class="text-muted mb-2">Conversations</h6>';
            results.conversations.forEach(conv => {
                html += `
                    <div class="search-result-item p-2 mb-1 rounded cursor-pointer" onclick="messaging.selectConversation(${conv.id})">
                        <div class="d-flex align-items-center">
                            <div class="flex-grow-1">
                                <div class="fw-bold">${conv.participant_name}</div>
                                <small class="text-muted">${conv.last_message}</small>
                            </div>
                            ${conv.unread_count > 0 ? `<span class="badge bg-primary">${conv.unread_count}</span>` : ''}
                        </div>
                    </div>
                `;
            });
        }

        if (results.messages.length > 0) {
            html += '<h6 class="text-muted mb-2 mt-3">Messages</h6>';
            results.messages.forEach(msg => {
                html += `
                    <div class="search-result-item p-2 mb-1 rounded cursor-pointer" onclick="messaging.selectConversation(${msg.conversation_id})">
                        <div class="fw-bold">${msg.participant_name}</div>
                        <div class="small">${msg.content.substring(0, 100)}...</div>
                        <small class="text-muted">${msg.created_at}</small>
                    </div>
                `;
            });
        }

        if (results.conversations.length === 0 && results.messages.length === 0) {
            html = '<div class="text-center text-muted py-3">No results found</div>';
        }

        container.innerHTML = html;
    }

    // ============================================================================
    // UTILITY FUNCTIONS
    // ============================================================================

    formatMessageTime(timeString) {
        // Handle both ISO format and server format
        let date;
        if (timeString.includes('T')) {
            // ISO format
            date = new Date(timeString);
        } else {
            // Server format (UTC)
            date = new Date(timeString.replace(' ', 'T') + 'Z');
        }
        
        const now = new Date();
        
        // Get user's timezone from page data or default to local
        const userTimezone = window.userTimezone || Intl.DateTimeFormat().resolvedOptions().timeZone;
        
        // Convert to user's timezone
        const userDate = new Date(date.toLocaleString("en-US", {timeZone: userTimezone}));
        const userNow = new Date(now.toLocaleString("en-US", {timeZone: userTimezone}));
        
        const diffMs = userNow - userDate;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        
        // Check if same day
        if (userDate.toDateString() === userNow.toDateString()) {
            return userDate.toLocaleTimeString([], {
                hour: '2-digit', 
                minute: '2-digit',
                timeZone: userTimezone
            });
        }
        
        // Check if yesterday
        const yesterday = new Date(userNow);
        yesterday.setDate(yesterday.getDate() - 1);
        if (userDate.toDateString() === yesterday.toDateString()) {
            return 'Yesterday';
        }
        
        // Check if within last 7 days
        const weekAgo = new Date(userNow);
        weekAgo.setDate(weekAgo.getDate() - 7);
        if (userDate > weekAgo) {
            return userDate.toLocaleDateString([], {
                weekday: 'short',
                timeZone: userTimezone
            });
        }
        
        // Older than a week
        return userDate.toLocaleDateString([], {
            month: 'short',
            day: 'numeric',
            timeZone: userTimezone
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    scrollToBottom(smooth = true) {
        const container = document.getElementById('messages-container');
        if (container) {
            const scrollTop = container.scrollTop;
            const scrollHeight = container.scrollHeight;
            const clientHeight = container.clientHeight;
            
            // Only auto-scroll if user is near the bottom
            if (scrollHeight - scrollTop - clientHeight < this.config.autoScrollThreshold) {
                container.scrollTo({
                    top: scrollHeight,
                    behavior: smooth ? 'smooth' : 'auto'
                });
            }
        }
    }

    getProfilePicture() {
        // This would be set by the template
        return window.messagingProfilePic || null;
    }

    getParticipantInitial() {
        // This would be set by the template
        return window.messagingParticipantInitial || '?';
    }

    // ============================================================================
    // UI FEEDBACK
    // ============================================================================

    showLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'flex';
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        // Simple notification system - you can enhance this
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 350px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    showToast(message, type = 'info') {
        // Simple toast system - you can enhance this
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0 fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 350px;';
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 3000);
    }

    // ============================================================================
    // KEYBOARD SHORTCUTS
    // ============================================================================

    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('search-input') || document.getElementById('sidebar-search');
            if (searchInput) {
                searchInput.focus();
            }
        }

        // Escape to clear search or close modals
        if (e.key === 'Escape') {
            const searchInput = document.getElementById('search-input');
            if (searchInput && searchInput.value) {
                searchInput.value = '';
                searchInput.dispatchEvent(new Event('input'));
            }
        }
    }

    // ============================================================================
    // LIFECYCLE MANAGEMENT
    // ============================================================================

    pauseUpdates() {
        this.stopMessageUpdates();
        if (this.unreadCountInterval) {
            clearInterval(this.unreadCountInterval);
            this.unreadCountInterval = null;
        }
    }

    resumeUpdates() {
        if (this.currentConversationId) {
            this.startMessageUpdates(this.currentConversationId);
        }
        this.startUnreadCountUpdates();
    }

    cleanup() {
        this.stopMessageUpdates();
        
        if (this.unreadCountInterval) {
            clearInterval(this.unreadCountInterval);
        }
        
        if (this.typingTimeout) {
            clearTimeout(this.typingTimeout);
        }
        
        console.log('Messaging system cleaned up');
    }
}

// Initialize global messaging system
const messaging = new MessagingSystem();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MessagingSystem;
}
