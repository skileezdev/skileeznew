/**
 * MessagingSystem - Complete real-time messaging functionality
 * Handles all messaging operations, real-time updates, and UI interactions
 */
class MessagingSystem {
    constructor(options = {}) {
        // Configuration
        this.config = {
            pollInterval: options.pollInterval || 3000, // 3 seconds
            maxRetries: options.maxRetries || 3,
            retryDelay: options.retryDelay || 1000,
            maxMessageLength: options.maxMessageLength || 1000,
            ...options
        };

        // State management
        this.state = {
            currentConversationId: null,
            lastMessageTimestamp: null,
            isPolling: false,
            isTyping: false,
            retryCount: 0,
            searchTimeout: null,
            typingTimeout: null
        };

        // DOM elements cache
        this.elements = {
            conversationList: null,
            conversationArea: null,
            messageInput: null,
            messagesContainer: null,
            searchInput: null,
            unreadBadge: null
        };

        // Event handlers
        this.handlers = {
            onMessageSent: null,
            onMessageReceived: null,
            onConversationChanged: null,
            onError: null
        };

        // Initialize the system
        this.init();
    }

    /**
     * Initialize the messaging system
     */
    init() {
        this.cacheElements();
        this.bindEvents();
        this.setupPolling();
        this.updateUnreadCount();
        
        // Set up global error handler
        window.addEventListener('error', (e) => {
            this.handleError('JavaScript Error', e.error);
        });

        console.log('MessagingSystem initialized');
    }

    /**
     * Cache frequently used DOM elements
     */
    cacheElements() {
        this.elements = {
            conversationList: document.getElementById('conversationList'),
            conversationArea: document.getElementById('conversationArea'),
            messageInput: document.getElementById('messageInput'),
            messagesContainer: document.getElementById('messagesContainer'),
            searchInput: document.getElementById('searchInput'),
            unreadBadge: document.querySelector('.badge.bg-danger'),
            charCount: document.getElementById('charCount'),
            fileInput: document.getElementById('fileInput'),
            messageForm: document.getElementById('messageForm')
        };
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Message form submission
        if (this.elements.messageForm) {
            this.elements.messageForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.sendMessage();
            });
        }

        // Message input events
        if (this.elements.messageInput) {
            // Character counter
            this.elements.messageInput.addEventListener('input', (e) => {
                this.updateCharacterCounter(e.target.value.length);
            });

            // Typing indicator
            this.elements.messageInput.addEventListener('input', () => {
                this.sendTypingIndicator();
            });

            // Enter key handling
            this.elements.messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        // File input
        if (this.elements.fileInput) {
            this.elements.fileInput.addEventListener('change', (e) => {
                this.handleFileUpload(e);
            });
        }

        // Search functionality
        if (this.elements.searchInput) {
            this.elements.searchInput.addEventListener('input', (e) => {
                this.debounceSearch(e.target.value);
            });
        }

        // Conversation list clicks
        if (this.elements.conversationList) {
            this.elements.conversationList.addEventListener('click', (e) => {
                const conversationItem = e.target.closest('.conversation-item');
                if (conversationItem) {
                    const conversationId = conversationItem.dataset.conversationId;
                    this.loadConversation(conversationId);
                }
            });
        }

        // Filter buttons
        document.querySelectorAll('input[name="filter"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.handleFilterChange(e.target.value);
            });
        });

        // Archive/unarchive buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="archive"]')) {
                e.preventDefault();
                this.archiveConversation(e.target.dataset.conversationId);
            } else if (e.target.matches('[data-action="unarchive"]')) {
                e.preventDefault();
                this.unarchiveConversation(e.target.dataset.conversationId);
            } else if (e.target.matches('[data-action="delete-message"]')) {
                e.preventDefault();
                this.deleteMessage(e.target.dataset.messageId);
            }
        });

        // Page visibility change (pause/resume polling)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pausePolling();
            } else {
                this.resumePolling();
            }
        });

        // Before unload cleanup
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
    }

    /**
     * Send a message via AJAX
     */
    async sendMessage() {
        const content = this.elements.messageInput?.value.trim();
        if (!content || !this.state.currentConversationId) {
            return;
        }

        // Validate message length
        if (content.length > this.config.maxMessageLength) {
            this.showError(`Message too long. Maximum ${this.config.maxMessageLength} characters allowed.`);
            return;
        }

        // Show loading state
        this.setMessageInputState(true);
        const sendButton = this.elements.messageForm?.querySelector('button[type="submit"]');
        if (sendButton) {
            sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            sendButton.disabled = true;
        }

        try {
            const response = await this.makeRequest('/api/messages/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    conversation_id: this.state.currentConversationId,
                    content: content,
                    message_type: 'text'
                })
            });

            if (response.success) {
                // Clear input and update UI
                this.elements.messageInput.value = '';
                this.updateCharacterCounter(0);
                
                // Append message to UI
                this.appendMessage(response.message);
                this.scrollToBottom();
                
                // Update conversation list
                this.updateConversationList();
                
                // Call success handler
                if (this.handlers.onMessageSent) {
                    this.handlers.onMessageSent(response.message);
                }
            } else {
                throw new Error(response.error || 'Failed to send message');
            }
        } catch (error) {
            this.handleError('Error sending message', error);
        } finally {
            // Reset input state
            this.setMessageInputState(false);
            if (sendButton) {
                sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
                sendButton.disabled = false;
            }
        }
    }

    /**
     * Handle file upload
     */
    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Validate file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            this.showError('File size must be less than 10MB');
            return;
        }

        // Validate file type
        const allowedTypes = [
            'text/plain', 'application/pdf', 'image/png', 'image/jpeg', 'image/gif',
            'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ];

        if (!allowedTypes.includes(file.type)) {
            this.showError('File type not allowed. Please upload a text, PDF, image, Word, or Excel file.');
            return;
        }

        // Show loading state
        this.setMessageInputState(true);
        if (this.elements.messageInput) {
            this.elements.messageInput.placeholder = 'Uploading file...';
        }

        try {
            // Upload file
            const formData = new FormData();
            formData.append('file', file);

            const uploadResponse = await this.makeRequest('/api/messages/upload-file', {
                method: 'POST',
                body: formData
            });

            if (uploadResponse.success) {
                // Send file message
                const messageResponse = await this.makeRequest('/api/messages/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        conversation_id: this.state.currentConversationId,
                        content: `File: ${uploadResponse.file_name}`,
                        message_type: 'file',
                        file_path: uploadResponse.file_path,
                        file_name: uploadResponse.file_name,
                        file_size: uploadResponse.file_size
                    })
                });

                if (messageResponse.success) {
                    this.appendMessage(messageResponse.message);
                    this.scrollToBottom();
                    this.updateConversationList();
                }
            } else {
                throw new Error(uploadResponse.error || 'Failed to upload file');
            }
        } catch (error) {
            this.handleError('Error uploading file', error);
        } finally {
            // Reset input state
            this.setMessageInputState(false);
            if (this.elements.messageInput) {
                this.elements.messageInput.placeholder = 'Type your message...';
            }
            if (this.elements.fileInput) {
                this.elements.fileInput.value = '';
            }
        }
    }

    /**
     * Load a conversation
     */
    async loadConversation(conversationId) {
        if (!conversationId || conversationId === this.state.currentConversationId) {
            return;
        }

        // Update active state
        this.updateActiveConversation(conversationId);
        this.state.currentConversationId = conversationId;

        // Show loading state
        if (this.elements.conversationArea) {
            this.elements.conversationArea.innerHTML = `
                <div class="loading-state">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Loading conversation...</p>
                </div>
            `;
        }

        try {
            const response = await fetch(`/messages/conversation/${conversationId}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const html = await response.text();
            if (this.elements.conversationArea) {
                this.elements.conversationArea.innerHTML = html;
            }

            // Re-cache elements after DOM update
            this.cacheElements();
            
            // Initialize conversation
            this.initializeConversation();
            this.markConversationAsRead();
            this.scrollToBottom();

            // Call conversation change handler
            if (this.handlers.onConversationChanged) {
                this.handlers.onConversationChanged(conversationId);
            }

        } catch (error) {
            this.handleError('Error loading conversation', error);
            if (this.elements.conversationArea) {
                this.elements.conversationArea.innerHTML = `
                    <div class="error-state">
                        <i class="fas fa-exclamation-triangle text-danger"></i>
                        <p class="mt-2">Error loading conversation</p>
                        <button class="btn btn-primary btn-sm" onclick="messagingSystem.loadConversation('${conversationId}')">
                            Try Again
                        </button>
                    </div>
                `;
            }
        }
    }

    /**
     * Initialize conversation after loading
     */
    initializeConversation() {
        // Set up message form
        if (this.elements.messageForm) {
            this.elements.messageForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.sendMessage();
            });
        }

        // Set up character counter
        if (this.elements.messageInput && this.elements.charCount) {
            this.elements.messageInput.addEventListener('input', (e) => {
                this.updateCharacterCounter(e.target.value.length);
            });
        }

        // Set up file input
        if (this.elements.fileInput) {
            this.elements.fileInput.addEventListener('change', (e) => {
                this.handleFileUpload(e);
            });
        }

        // Focus on message input
        if (this.elements.messageInput) {
            this.elements.messageInput.focus();
        }
    }

    /**
     * Setup polling for real-time updates
     */
    setupPolling() {
        if (this.state.isPolling) return;

        this.state.isPolling = true;
        this.pollInterval = setInterval(() => {
            this.pollNewMessages();
        }, this.config.pollInterval);

        console.log('Polling started');
    }

    /**
     * Poll for new messages
     */
    async pollNewMessages() {
        if (!this.state.currentConversationId || document.hidden) {
            return;
        }

        try {
            const params = new URLSearchParams();
            if (this.state.lastMessageTimestamp) {
                params.append('last_timestamp', this.state.lastMessageTimestamp);
            }

            const response = await this.makeRequest(`/api/messages/poll/${this.state.currentConversationId}?${params}`);
            
            if (response.success && response.messages.length > 0) {
                response.messages.forEach(message => {
                    this.appendMessage(message);
                });
                
                this.scrollToBottom();
                this.state.lastMessageTimestamp = response.timestamp;
                this.updateUnreadCount();
                
                // Call message received handler
                if (this.handlers.onMessageReceived) {
                    this.handlers.onMessageReceived(response.messages);
                }
            }
        } catch (error) {
            console.error('Polling error:', error);
            this.state.retryCount++;
            
            if (this.state.retryCount >= this.config.maxRetries) {
                this.pausePolling();
                this.showError('Connection lost. Please refresh the page.');
            }
        }
    }

    /**
     * Pause polling
     */
    pausePolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.state.isPolling = false;
            console.log('Polling paused');
        }
    }

    /**
     * Resume polling
     */
    resumePolling() {
        if (!this.state.isPolling) {
            this.setupPolling();
        }
    }

    /**
     * Append a message to the UI
     */
    appendMessage(message) {
        if (!this.elements.messagesContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.sender_id == this.getCurrentUserId() ? 'message-own' : 'message-other'}`;
        messageDiv.setAttribute('data-message-id', message.id);

        const isOwnMessage = message.sender_id == this.getCurrentUserId();
        const messageTime = this.formatTime(message.created_at);

        let messageContent = '';
        if (message.message_type === 'file') {
            messageContent = `
                <div class="message-file">
                    <div class="file-icon">
                        <i class="fas fa-paperclip"></i>
                    </div>
                    <div class="file-info">
                        <a href="${message.file_info.file_path}" target="_blank" class="file-name">
                            ${message.file_info.file_name}
                        </a>
                        <small class="file-size">
                            ${(message.file_info.file_size / 1024).toFixed(1)} KB
                        </small>
                    </div>
                </div>
            `;
        } else {
            messageContent = `<div class="message-text">${this.escapeHtml(message.content)}</div>`;
        }

        messageDiv.innerHTML = `
            <div class="message-content">
                ${messageContent}
                <div class="message-meta">
                    <small class="message-time">${messageTime}</small>
                    ${isOwnMessage ? '<i class="fas fa-check-double message-status"></i>' : ''}
                </div>
                ${isOwnMessage ? `
                    <button class="btn btn-sm btn-link text-muted p-0 message-delete" 
                            data-action="delete-message" 
                            data-message-id="${message.id}"
                            title="Delete message">
                        <i class="fas fa-trash"></i>
                    </button>
                ` : ''}
            </div>
        `;

        this.elements.messagesContainer.appendChild(messageDiv);

        // Add animation
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(10px)';
        setTimeout(() => {
            messageDiv.style.transition = 'all 0.3s ease';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        }, 10);
    }

    /**
     * Delete a message
     */
    async deleteMessage(messageId) {
        if (!confirm('Are you sure you want to delete this message?')) {
            return;
        }

        try {
            const response = await this.makeRequest('/api/messages/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message_id: messageId })
            });

            if (response.success) {
                // Remove message from UI with animation
                const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
                if (messageElement) {
                    messageElement.style.transition = 'all 0.3s ease';
                    messageElement.style.opacity = '0';
                    messageElement.style.transform = 'translateX(-20px)';
                    setTimeout(() => {
                        messageElement.remove();
                    }, 300);
                }
            } else {
                throw new Error(response.error || 'Failed to delete message');
            }
        } catch (error) {
            this.handleError('Error deleting message', error);
        }
    }

    /**
     * Mark conversation as read
     */
    async markConversationAsRead() {
        if (!this.state.currentConversationId) return;

        try {
            await this.makeRequest('/api/messages/mark-read', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    conversation_id: this.state.currentConversationId
                })
            });

            this.updateUnreadCount();
        } catch (error) {
            console.error('Error marking conversation as read:', error);
        }
    }

    /**
     * Archive/unarchive conversation
     */
    async archiveConversation(conversationId, action = 'archive') {
        try {
            const response = await this.makeRequest('/api/messages/archive', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    conversation_id: conversationId,
                    action: action
                })
            });

            if (response.success) {
                // Refresh the page to update conversation list
                window.location.reload();
            } else {
                throw new Error(response.error || `Failed to ${action} conversation`);
            }
        } catch (error) {
            this.handleError(`Error ${action}ing conversation`, error);
        }
    }

    /**
     * Unarchive conversation
     */
    async unarchiveConversation(conversationId) {
        return this.archiveConversation(conversationId, 'unarchive');
    }

    /**
     * Search conversations
     */
    debounceSearch(query) {
        clearTimeout(this.state.searchTimeout);
        this.state.searchTimeout = setTimeout(() => {
            this.performSearch(query);
        }, 300);
    }

    async performSearch(query) {
        if (query.length < 2) return;

        try {
            const response = await this.makeRequest(`/api/messages/search?q=${encodeURIComponent(query)}`);
            
            if (response.success) {
                this.updateConversationList(response.results);
            }
        } catch (error) {
            console.error('Search error:', error);
        }
    }

    /**
     * Update conversation list
     */
    updateConversationList(conversations = null) {
        // This would update the conversation list UI
        // Implementation depends on your specific UI structure
        console.log('Conversation list updated');
    }

    /**
     * Update unread count
     */
    async updateUnreadCount() {
        try {
            const response = await this.makeRequest('/api/messages/unread-count');
            
            if (response.success) {
                this.updateUnreadBadge(response.unread_count);
            }
        } catch (error) {
            console.error('Error updating unread count:', error);
        }
    }

    /**
     * Update unread badge in navigation
     */
    updateUnreadBadge(count) {
        const badge = document.querySelector('.badge.bg-danger');
        
        if (count > 0) {
            if (badge) {
                badge.textContent = count;
            } else {
                // Create new badge
                const newBadge = document.createElement('span');
                newBadge.className = 'badge bg-danger ms-2';
                newBadge.textContent = count;
                const header = document.querySelector('h4');
                if (header) {
                    header.appendChild(newBadge);
                }
            }
        } else if (badge) {
            badge.remove();
        }
    }

    /**
     * Send typing indicator
     */
    sendTypingIndicator() {
        if (this.state.isTyping) return;

        this.state.isTyping = true;
        
        // Clear existing timeout
        if (this.state.typingTimeout) {
            clearTimeout(this.state.typingTimeout);
        }

        // Set timeout to stop typing indicator
        this.state.typingTimeout = setTimeout(() => {
            this.state.isTyping = false;
        }, 2000);

        // Send typing indicator to server (if implemented)
        // this.makeRequest('/api/messages/typing', { method: 'POST', body: JSON.stringify({ conversation_id: this.state.currentConversationId }) });
    }

    /**
     * Update character counter
     */
    updateCharacterCounter(length) {
        if (!this.elements.charCount) return;

        this.elements.charCount.textContent = `${length}/${this.config.maxMessageLength}`;
        
        if (length > this.config.maxMessageLength * 0.9) {
            this.elements.charCount.classList.add('text-warning');
        } else if (length > this.config.maxMessageLength * 0.95) {
            this.elements.charCount.classList.remove('text-warning');
            this.elements.charCount.classList.add('text-danger');
        } else {
            this.elements.charCount.classList.remove('text-warning', 'text-danger');
        }
    }

    /**
     * Update active conversation in UI
     */
    updateActiveConversation(conversationId) {
        // Remove active class from all conversations
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });

        // Add active class to current conversation
        const activeItem = document.querySelector(`[data-conversation-id="${conversationId}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }
    }

    /**
     * Handle filter change
     */
    handleFilterChange(filterValue) {
        const includeArchived = filterValue === 'archived';
        window.location.href = `/messages?archived=${includeArchived}`;
    }

    /**
     * Set message input state (enabled/disabled)
     */
    setMessageInputState(disabled) {
        if (this.elements.messageInput) {
            this.elements.messageInput.disabled = disabled;
        }
        if (this.elements.fileInput) {
            this.elements.fileInput.disabled = disabled;
        }
    }

    /**
     * Scroll to bottom of messages
     */
    scrollToBottom() {
        if (this.elements.messagesContainer) {
            this.elements.messagesContainer.scrollTop = this.elements.messagesContainer.scrollHeight;
        }
    }

    /**
     * Make HTTP request with error handling
     */
    async makeRequest(url, options = {}) {
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    ...options.headers
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            throw error;
        }
    }

    /**
     * Handle errors
     */
    handleError(message, error) {
        console.error(message, error);
        this.showError(`${message}: ${error.message || error}`);
        
        if (this.handlers.onError) {
            this.handlers.onError(message, error);
        }
    }

    /**
     * Show error toast
     */
    showError(message) {
        const toast = document.createElement('div');
        toast.className = 'toast-notification error';
        toast.innerHTML = `
            <i class="fas fa-exclamation-circle me-2"></i>
            ${this.escapeHtml(message)}
        `;
        
        document.body.appendChild(toast);
        
        // Show toast
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        // Remove toast after 5 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (document.body.contains(toast)) {
                    document.body.removeChild(toast);
                }
            }, 300);
        }, 5000);
    }

    /**
     * Show success toast
     */
    showSuccess(message) {
        const toast = document.createElement('div');
        toast.className = 'toast-notification success';
        toast.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            ${this.escapeHtml(message)}
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (document.body.contains(toast)) {
                    document.body.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    /**
     * Utility functions
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffInHours = (now - date) / (1000 * 60 * 60);
        
        if (diffInHours < 24) {
            return date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        } else if (diffInHours < 48) {
            return 'Yesterday';
        } else {
            return date.toLocaleDateString();
        }
    }

    getCurrentUserId() {
        // Get current user ID from a data attribute or global variable
        return document.body.dataset.userId || window.currentUserId;
    }

    /**
     * Event handler setters
     */
    onMessageSent(handler) {
        this.handlers.onMessageSent = handler;
    }

    onMessageReceived(handler) {
        this.handlers.onMessageReceived = handler;
    }

    onConversationChanged(handler) {
        this.handlers.onConversationChanged = handler;
    }

    onError(handler) {
        this.handlers.onError = handler;
    }

    /**
     * Cleanup resources
     */
    cleanup() {
        this.pausePolling();
        
        if (this.state.searchTimeout) {
            clearTimeout(this.state.searchTimeout);
        }
        
        if (this.state.typingTimeout) {
            clearTimeout(this.state.typingTimeout);
        }
        
        console.log('MessagingSystem cleaned up');
    }

    /**
     * Public API methods
     */
    getCurrentConversationId() {
        return this.state.currentConversationId;
    }

    isPolling() {
        return this.state.isPolling;
    }

    getConfig() {
        return { ...this.config };
    }

    updateConfig(newConfig) {
        this.config = { ...this.config, ...newConfig };
    }
}

// Initialize messaging system when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Create global messaging system instance
    window.messagingSystem = new MessagingSystem({
        pollInterval: 3000,
        maxRetries: 3,
        retryDelay: 1000,
        maxMessageLength: 1000
    });

    // Set up event handlers
    messagingSystem.onMessageSent((message) => {
        console.log('Message sent:', message);
    });

    messagingSystem.onMessageReceived((messages) => {
        console.log('Messages received:', messages);
    });

    messagingSystem.onConversationChanged((conversationId) => {
        console.log('Conversation changed:', conversationId);
    });

    messagingSystem.onError((message, error) => {
        console.error('Messaging error:', message, error);
    });
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MessagingSystem;
}
