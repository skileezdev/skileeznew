/**
 * Scheduling System JavaScript
 * Handles dynamic scheduling options, real-time updates, and interactive features
 */

class SchedulingManager {
    constructor() {
        this.currentUser = null;
        this.schedulingOptions = {};
        this.upcomingCalls = [];
        this.init();
    }
    
    init() {
        this.loadCurrentUser();
        this.setupEventListeners();
        this.startPolling();
    }

    loadCurrentUser() {
        // Get current user from page data or API
        const userElement = document.querySelector('[data-user-id]');
        if (userElement) {
            this.currentUser = {
                id: userElement.dataset.userId,
                role: userElement.dataset.userRole,
                isStudent: userElement.dataset.userRole === 'student',
                isCoach: userElement.dataset.userRole === 'coach'
            };
        }
    }
    
    setupEventListeners() {
        // Listen for scheduling option changes
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-schedule-free-consultation]')) {
                this.handleFreeConsultationClick(e);
            } else if (e.target.matches('[data-schedule-paid-session]')) {
                this.handlePaidSessionClick(e);
            } else if (e.target.matches('[data-check-availability]')) {
                this.checkAvailability(e);
            }
        });

        // Listen for form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.matches('#free-consultation-form')) {
                this.handleFreeConsultationSubmit(e);
            } else if (e.target.matches('#paid-session-form')) {
                this.handlePaidSessionSubmit(e);
            }
        });

        // Listen for real-time updates
        this.setupWebSocket();
    }

    async getSchedulingOptions(coachId) {
        try {
            const response = await fetch(`/api/scheduling-options/${coachId}`);
            const data = await response.json();
            
            if (data.success) {
                this.schedulingOptions[coachId] = data.options;
                this.updateSchedulingButtons(coachId);
                return data.options;
            } else {
                console.error('Failed to get scheduling options:', data.error);
                return 'free_consultation';
            }
        } catch (error) {
            console.error('Error getting scheduling options:', error);
            return 'free_consultation';
        }
    }

    updateSchedulingButtons(coachId) {
        const options = this.schedulingOptions[coachId];
        const buttonContainer = document.querySelector(`[data-coach-id="${coachId}"]`);
        
        if (!buttonContainer) return;

        const oldButton = buttonContainer.querySelector('.scheduling-button');
        if (oldButton) {
            oldButton.remove();
        }

        const newButton = this.createSchedulingButton(coachId, options);
        buttonContainer.appendChild(newButton);
    }

    createSchedulingButton(coachId, options) {
        const button = document.createElement('button');
        button.className = 'scheduling-button btn-primary px-6 py-3 rounded-lg transition-all duration-200';

        if (options === 'free_consultation') {
            button.innerHTML = `
                <i data-feather="phone" class="w-4 h-4 mr-2"></i>
                Schedule Free 15-min Call
            `;
            button.setAttribute('data-schedule-free-consultation', coachId);
        } else if (options === 'paid_sessions') {
            button.innerHTML = `
                <i data-feather="calendar" class="w-4 h-4 mr-2"></i>
                Schedule Learning Session
            `;
            button.setAttribute('data-schedule-paid-session', coachId);
        }

        feather.replace();
        return button;
    }

    handleFreeConsultationClick(e) {
        e.preventDefault();
        const coachId = e.target.getAttribute('data-schedule-free-consultation');
        window.location.href = `/schedule/free-consultation/${coachId}`;
    }

    handlePaidSessionClick(e) {
        e.preventDefault();
        const coachId = e.target.getAttribute('data-schedule-paid-session');
        // Get the contract ID from the page or prompt user to select
        const contractId = this.getActiveContractId(coachId);
        if (contractId) {
            window.location.href = `/schedule/paid-session/${contractId}`;
        } else {
            this.showContractSelectionModal(coachId);
        }
    }

    getActiveContractId(coachId) {
        // Look for active contract in the page
        const contractElement = document.querySelector(`[data-contract-coach="${coachId}"][data-contract-status="active"]`);
        return contractElement ? contractElement.dataset.contractId : null;
    }

    showContractSelectionModal(coachId) {
        // Create modal for contract selection
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                <h3 class="text-lg font-semibold mb-4">Select Contract</h3>
                <p class="text-gray-600 mb-4">You need an active contract to schedule paid sessions.</p>
                <div class="flex space-x-3">
                    <button onclick="this.closest('.fixed').remove()" class="btn-secondary px-4 py-2 rounded">
                        Cancel
                    </button>
                    <a href="/contracts" class="btn-primary px-4 py-2 rounded">
                        View Contracts
                    </a>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    async checkAvailability(e) {
        e.preventDefault();
        const form = e.target.closest('form');
        const coachId = form.dataset.coachId;
        const dateInput = form.querySelector('input[name="scheduled_date"]');
        const timeInput = form.querySelector('input[name="scheduled_time"]');
        const timezoneSelect = form.querySelector('select[name="timezone"]');
        const durationSelect = form.querySelector('select[name="duration_minutes"]');

        if (!dateInput.value || !timeInput.value) {
            this.showAvailabilityMessage('Please select date and time', 'error');
            return;
        }
        
        try {
            const response = await fetch(`/api/check-availability/${coachId}?date=${dateInput.value}&time=${timeInput.value}&timezone=${timezoneSelect.value}&duration=${durationSelect?.value || 15}`);
            const data = await response.json();

            if (data.success) {
                if (data.available) {
                    this.showAvailabilityMessage('Time slot is available!', 'success');
                } else {
                    this.showAvailabilityMessage('Coach is not available at this time', 'error');
                }
            } else {
                this.showAvailabilityMessage('Error checking availability', 'error');
            }
        } catch (error) {
            console.error('Error checking availability:', error);
            this.showAvailabilityMessage('Error checking availability', 'error');
        }
    }

    showAvailabilityMessage(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `availability-message p-3 rounded-lg mb-4 ${
            type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`;
        messageDiv.textContent = message;

        const form = document.querySelector('form');
        form.insertBefore(messageDiv, form.firstChild);

        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }

    async handleFreeConsultationSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.innerHTML;

        submitButton.disabled = true;
        submitButton.innerHTML = '<i data-feather="loader" class="w-4 h-4 mr-2 animate-spin"></i>Scheduling...';
        feather.replace();

        try {
            const formData = new FormData(form);
            const response = await fetch('/schedule/free-consultation', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                this.showSuccessMessage('Free consultation scheduled successfully!');
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                const data = await response.json();
                this.showErrorMessage(data.message || 'Failed to schedule consultation');
            }
        } catch (error) {
            console.error('Error scheduling consultation:', error);
            this.showErrorMessage('An error occurred while scheduling');
        } finally {
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
            feather.replace();
        }
    }

    async handlePaidSessionSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.innerHTML;

        submitButton.disabled = true;
        submitButton.innerHTML = '<i data-feather="loader" class="w-4 h-4 mr-2 animate-spin"></i>Scheduling...';
        feather.replace();

        try {
            const formData = new FormData(form);
            const response = await fetch('/schedule/paid-session', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                this.showSuccessMessage('Session scheduled successfully!');
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                const data = await response.json();
                this.showErrorMessage(data.message || 'Failed to schedule session');
            }
        } catch (error) {
            console.error('Error scheduling session:', error);
            this.showErrorMessage('An error occurred while scheduling');
        } finally {
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
            feather.replace();
        }
    }

    showSuccessMessage(message) {
        this.showToast(message, 'success');
    }

    showErrorMessage(message) {
        this.showToast(message, 'error');
    }

    showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
            type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
        }`;
        toast.textContent = message;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 5000);
    }
    
    async loadUpcomingCalls() {
        try {
            const response = await fetch('/api/upcoming-calls');
            const data = await response.json();
            
            if (data.success) {
                this.upcomingCalls = data.calls;
                this.updateUpcomingCallsDisplay();
            }
        } catch (error) {
            console.error('Error loading upcoming calls:', error);
        }
    }

    updateUpcomingCallsDisplay() {
        const container = document.getElementById('upcoming-calls-container');
        if (!container) return;

        if (this.upcomingCalls.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">No upcoming calls</p>';
            return;
        }
        
        const callsHtml = this.upcomingCalls.map(call => this.renderCallCard(call)).join('');
        container.innerHTML = callsHtml;
        feather.replace();
    }

    renderCallCard(call) {
        const callDate = new Date(call.scheduled_at);
        const isReady = call.is_ready;
        
        return `
            <div class="call-card bg-white border border-gray-200 rounded-lg p-4 mb-3">
                <div class="flex items-center justify-between">
                    <div>
                        <h4 class="font-semibold text-gray-900">
                            ${call.type === 'free_consultation' ? 'Free Consultation' : 'Learning Session'}
                        </h4>
                        <p class="text-sm text-gray-600">${callDate.toLocaleDateString()} at ${callDate.toLocaleTimeString()}</p>
                        <p class="text-xs text-gray-500">${call.duration_minutes} minutes</p>
                    </div>
                    <div class="text-right">
                        ${isReady ? 
                            `<a href="/calls/${call.id}/join" class="btn-primary px-3 py-1 text-sm">Join</a>` :
                            `<span class="text-xs text-gray-500">${call.time_until}</span>`
                        }
                    </div>
                </div>
            </div>
        `;
    }

    setupWebSocket() {
        // Set up WebSocket connection for real-time updates
        if (typeof WebSocket !== 'undefined') {
            const ws = new WebSocket(`ws://${window.location.host}/ws/scheduling`);
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        }
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'call_scheduled':
                this.handleCallScheduled(data.call);
                break;
            case 'call_ready':
                this.handleCallReady(data.call);
                break;
            case 'call_updated':
                this.handleCallUpdated(data.call);
                break;
        }
    }

    handleCallScheduled(call) {
        this.showToast(`New call scheduled for ${new Date(call.scheduled_at).toLocaleDateString()}`, 'success');
        this.loadUpcomingCalls();
    }

    handleCallReady(call) {
        this.showToast('Your call is ready to join!', 'success');
        this.loadUpcomingCalls();
    }

    handleCallUpdated(call) {
        this.loadUpcomingCalls();
    }

    startPolling() {
        // Poll for updates every 30 seconds
        setInterval(() => {
            this.loadUpcomingCalls();
        }, 30000);
    }
}

// Initialize scheduling manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.schedulingManager = new SchedulingManager();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SchedulingManager;
}
