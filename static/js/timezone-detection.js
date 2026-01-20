/**
 * Auto Timezone Detection Script
 * Provides automatic timezone detection and selection for forms
 */

class TimezoneDetector {
    constructor(options = {}) {
        this.options = {
            selectId: 'timezone-select',
            messageId: 'timezone-detection-message',
            detectedNameId: 'detected-timezone-name',
            manualBtnId: 'manual-timezone-btn',
            showCurrentTime: true,
            autoHide: true,
            ...options
        };
        
        this.init();
    }

    init() {
        // Check if DOM is already loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.autoDetectTimezone();
                this.setupEventListeners();
            });
        } else {
            this.autoDetectTimezone();
            this.setupEventListeners();
        }
    }

    autoDetectTimezone() {
        const timezoneSelect = document.getElementById(this.options.selectId);
        const detectionMessage = document.getElementById(this.options.messageId);
        const detectedTimezoneName = document.getElementById(this.options.detectedNameId);
        const manualTimezoneBtn = document.getElementById(this.options.manualBtnId);
        
        if (!timezoneSelect || !detectionMessage) {
            return;
        }

        try {
            // Get user's timezone
            const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            
            if (userTimezone) {
                // Find the timezone in the select options
                const timezoneOptions = Array.from(timezoneSelect.options);
                const matchingOption = timezoneOptions.find(option => option.value === userTimezone);
                
                if (matchingOption) {
                    // Set the detected timezone
                    timezoneSelect.value = userTimezone;
                    
                    // Show detection message
                    if (detectedTimezoneName) {
                        detectedTimezoneName.textContent = matchingOption.text;
                    }
                    detectionMessage.classList.remove('hidden');
                    
                    if (manualTimezoneBtn) {
                        manualTimezoneBtn.classList.remove('hidden');
                    }
                    
                    // Add visual feedback
                    timezoneSelect.classList.add('border-green-300', 'bg-green-50');
                    
                    // Hide the select initially if auto-hide is enabled
                    if (this.options.autoHide) {
                        timezoneSelect.style.display = 'none';
                    }
                    
                    // Show timezone info
                    if (this.options.showCurrentTime) {
                        this.showTimezoneInfo(userTimezone);
                    }
                    
                    // Trigger custom event
                    this.dispatchEvent('timezoneDetected', {
                        timezone: userTimezone,
                        displayName: matchingOption.text
                    });
                } else {
                    // Timezone not found in options, show manual selection
                    this.showManualSelection();
                }
            } else {
                // Fallback to manual selection
                this.showManualSelection();
            }
        } catch (error) {
            console.log('Timezone detection failed:', error);
            this.showManualSelection();
        }
    }

    showManualSelection() {
        const timezoneSelect = document.getElementById(this.options.selectId);
        const detectionMessage = document.getElementById(this.options.messageId);
        const manualTimezoneBtn = document.getElementById(this.options.manualBtnId);
        
        // Show the select field normally
        if (timezoneSelect) {
            timezoneSelect.style.display = 'block';
            timezoneSelect.classList.remove('border-green-300', 'bg-green-50');
        }
        
        if (detectionMessage) {
            detectionMessage.classList.add('hidden');
        }
        
        if (manualTimezoneBtn) {
            manualTimezoneBtn.classList.add('hidden');
        }
        
        // Trigger custom event
        this.dispatchEvent('manualSelectionRequired');
    }

    showTimezoneInfo(timezone) {
        try {
            const now = new Date();
            const timeInTimezone = new Intl.DateTimeFormat('en-US', {
                timeZone: timezone,
                hour: '2-digit',
                minute: '2-digit',
                hour12: true
            }).format(now);
            
            const offset = new Intl.DateTimeFormat('en-US', {
                timeZone: timezone,
                timeZoneName: 'longOffset'
            }).formatToParts(now).find(part => part.type === 'timeZoneName')?.value || '';
            
            // Update the detection message with current time
            const detectionMessage = document.getElementById(this.options.messageId);
            if (detectionMessage) {
                const timeInfo = document.createElement('div');
                timeInfo.className = 'text-xs text-blue-600 mt-1';
                timeInfo.innerHTML = `Current time in your timezone: <strong>${timeInTimezone} ${offset}</strong>`;
                
                const existingTimeInfo = detectionMessage.querySelector('.text-xs.text-blue-600.mt-1');
                if (existingTimeInfo) {
                    existingTimeInfo.replaceWith(timeInfo);
                } else {
                    detectionMessage.appendChild(timeInfo);
                }
            }
        } catch (error) {
            console.log('Error showing timezone info:', error);
        }
    }

    setupEventListeners() {
        const timezoneSelect = document.getElementById(this.options.selectId);
        const manualTimezoneBtn = document.getElementById(this.options.manualBtnId);
        
        if (timezoneSelect) {
            // Add better styling and functionality
            timezoneSelect.addEventListener('focus', function() {
                this.size = Math.min(this.options.length, 12);
                this.style.maxHeight = '300px';
                this.style.overflowY = 'auto';
                this.style.borderColor = '#3b82f6';
                this.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
            });
            
            timezoneSelect.addEventListener('blur', function() {
                this.size = 1;
                this.style.maxHeight = 'auto';
                this.style.overflowY = 'visible';
                this.style.borderColor = '#e5e7eb';
                this.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
            });
            
            // Add custom styling for better appearance
            timezoneSelect.style.fontSize = '14px';
            timezoneSelect.style.lineHeight = '1.5';
            timezoneSelect.style.backgroundColor = 'white';
            timezoneSelect.style.color = '#374151';
            timezoneSelect.style.border = '2px solid #e5e7eb';
            timezoneSelect.style.borderRadius = '8px';
            timezoneSelect.style.padding = '12px 16px';
            timezoneSelect.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
            timezoneSelect.style.transition = 'all 0.2s ease';
            
            // Show timezone info when manually changed
            timezoneSelect.addEventListener('change', (e) => {
                if (e.target.value === '__more__') {
                    // Handle "More timezones..." option
                    this.showTimezoneSearch();
                } else if (e.target.value && this.options.showCurrentTime) {
                    this.showTimezoneInfo(e.target.value);
                }
                
                // Trigger custom event
                this.dispatchEvent('timezoneChanged', {
                    timezone: e.target.value
                });
            });
        }
        
        if (manualTimezoneBtn) {
            manualTimezoneBtn.addEventListener('click', () => {
                const timezoneSelect = document.getElementById(this.options.selectId);
                const detectionMessage = document.getElementById(this.options.messageId);
                const manualTimezoneBtn = document.getElementById(this.options.manualBtnId);
                
                if (timezoneSelect) {
                    timezoneSelect.style.display = 'block';
                    timezoneSelect.classList.remove('border-green-300', 'bg-green-50');
                    timezoneSelect.focus();
                }
                
                if (detectionMessage) {
                    detectionMessage.classList.add('hidden');
                }
                
                if (manualTimezoneBtn) {
                    manualTimezoneBtn.classList.add('hidden');
                }
                
                // Trigger custom event
                this.dispatchEvent('manualOverride');
            });
        }
    }

    dispatchEvent(eventName, detail = {}) {
        const event = new CustomEvent(`timezoneDetector:${eventName}`, {
            detail: detail
        });
        document.dispatchEvent(event);
    }

    // Public methods
    getDetectedTimezone() {
        const timezoneSelect = document.getElementById(this.options.selectId);
        return timezoneSelect ? timezoneSelect.value : null;
    }

    setTimezone(timezone) {
        const timezoneSelect = document.getElementById(this.options.selectId);
        if (timezoneSelect) {
            timezoneSelect.value = timezone;
            if (this.options.showCurrentTime) {
                this.showTimezoneInfo(timezone);
            }
        }
    }

    reset() {
        this.showManualSelection();
    }
    
    showTimezoneSearch() {
        // Create a searchable timezone selector
        const timezoneSelect = document.getElementById(this.options.selectId);
        if (!timezoneSelect) return;
        
        // Create beautiful search interface
        const searchContainer = document.createElement('div');
        searchContainer.className = 'timezone-search-container mt-3 p-4 bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-xl shadow-lg';
        searchContainer.innerHTML = `
            <div class="mb-3">
                <div class="flex items-center mb-2">
                    <span class="text-lg mr-2">🔍</span>
                    <label class="text-sm font-semibold text-gray-800">Search All Timezones</label>
                </div>
                <input type="text" id="timezone-search" placeholder="Type city name or timezone..." 
                       class="w-full px-4 py-3 border border-blue-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200">
            </div>
            <div id="timezone-search-results" class="max-h-64 overflow-y-auto border border-blue-200 rounded-lg bg-white shadow-inner">
                <!-- Search results will appear here -->
            </div>
            <div class="mt-3 flex justify-between items-center">
                <span class="text-xs text-gray-500">💡 Tip: Search by city name or timezone code</span>
                <button type="button" id="cancel-timezone-search" 
                        class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors">
                    Cancel
                </button>
            </div>
        `;
        
        // Insert after the timezone select
        timezoneSelect.parentNode.insertBefore(searchContainer, timezoneSelect.nextSibling);
        
        // Load all timezones for search
        this.loadAllTimezonesForSearch();
        
        // Setup search functionality
        const searchInput = document.getElementById('timezone-search');
        const cancelBtn = document.getElementById('cancel-timezone-search');
        
        searchInput.addEventListener('input', (e) => {
            this.searchTimezones(e.target.value);
        });
        
        cancelBtn.addEventListener('click', () => {
            searchContainer.remove();
            timezoneSelect.value = ''; // Reset selection
        });
        
        // Focus search input
        searchInput.focus();
    }
    
    async loadAllTimezonesForSearch() {
        try {
            // Use the comprehensive timezone list from the server
            const response = await fetch('/api/timezones');
            if (response.ok) {
                const timezones = await response.json();
                this.allTimezones = timezones;
            } else {
                // Fallback: use a basic list
                this.allTimezones = [
                    {value: 'UTC', label: 'UTC (Coordinated Universal Time)'},
                    {value: 'America/New_York', label: 'New York (UTC-5/-4)'},
                    {value: 'America/Chicago', label: 'Chicago (UTC-6/-5)'},
                    {value: 'America/Denver', label: 'Denver (UTC-7/-6)'},
                    {value: 'America/Los_Angeles', label: 'Los Angeles (UTC-8/-7)'},
                    {value: 'Europe/London', label: 'London (UTC+0/+1)'},
                    {value: 'Europe/Paris', label: 'Paris (UTC+1/+2)'},
                    {value: 'Asia/Tokyo', label: 'Tokyo (UTC+9)'},
                    {value: 'Asia/Shanghai', label: 'Shanghai (UTC+8)'},
                    {value: 'Australia/Sydney', label: 'Sydney (UTC+10/+11)'}
                ];
            }
        } catch (error) {
            console.log('Error loading timezones:', error);
            // Use fallback list
            this.allTimezones = [
                {value: 'UTC', label: 'UTC (Coordinated Universal Time)'},
                {value: 'America/New_York', label: 'New York (UTC-5/-4)'},
                {value: 'Europe/London', label: 'London (UTC+0/+1)'},
                {value: 'Asia/Tokyo', label: 'Tokyo (UTC+9)'}
            ];
        }
        
        this.searchTimezones(''); // Show all initially
    }
    
    searchTimezones(query) {
        const resultsContainer = document.getElementById('timezone-search-results');
        if (!resultsContainer || !this.allTimezones) return;
        
        const filtered = this.allTimezones.filter(tz => 
            tz.label.toLowerCase().includes(query.toLowerCase()) ||
            tz.value.toLowerCase().includes(query.toLowerCase())
        );
        
        if (filtered.length === 0) {
            resultsContainer.innerHTML = `
                <div class="px-4 py-8 text-center text-gray-500">
                    <div class="text-2xl mb-2">🔍</div>
                    <div class="text-sm">No timezones found for "${query}"</div>
                    <div class="text-xs mt-1">Try searching by city name or timezone code</div>
                </div>
            `;
            return;
        }
        
        resultsContainer.innerHTML = filtered.map(tz => `
            <div class="px-4 py-3 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0 transition-colors duration-150 group" 
                 data-timezone="${tz.value}">
                <div class="flex items-center justify-between">
                    <div class="flex-1">
                        <div class="font-medium text-sm text-gray-900 group-hover:text-blue-700">${tz.label}</div>
                        <div class="text-xs text-gray-500 mt-1">${tz.value}</div>
                    </div>
                    <div class="text-blue-500 opacity-0 group-hover:opacity-100 transition-opacity">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Add click handlers
        resultsContainer.querySelectorAll('[data-timezone]').forEach(item => {
            item.addEventListener('click', () => {
                const timezone = item.dataset.timezone;
                this.selectTimezone(timezone);
            });
        });
    }
    
    selectTimezone(timezone) {
        const timezoneSelect = document.getElementById(this.options.selectId);
        const searchContainer = document.querySelector('.timezone-search-container');
        
        if (timezoneSelect) {
            timezoneSelect.value = timezone;
            
            // Trigger change event
            const event = new Event('change', { bubbles: true });
            timezoneSelect.dispatchEvent(event);
        }
        
        if (searchContainer) {
            searchContainer.remove();
        }
    }
}

// Auto-initialize if data attributes are present
document.addEventListener('DOMContentLoaded', function() {
    const autoDetectElements = document.querySelectorAll('[data-auto-timezone-detect]');
    
    autoDetectElements.forEach(element => {
        const options = {
            selectId: element.dataset.timezoneSelect || 'timezone-select',
            messageId: element.dataset.timezoneMessage || 'timezone-detection-message',
            detectedNameId: element.dataset.timezoneName || 'detected-timezone-name',
            manualBtnId: element.dataset.timezoneBtn || 'manual-timezone-btn',
            showCurrentTime: element.dataset.showCurrentTime !== 'false',
            autoHide: element.dataset.autoHide !== 'false'
        };
        
        new TimezoneDetector(options);
    });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TimezoneDetector;
}
