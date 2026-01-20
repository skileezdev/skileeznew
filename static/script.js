/**
 * Skileez Platform - Main JavaScript File
 * Premium peer-to-peer learning marketplace
 */

// Global Skileez object
window.Skileez = {
    // Configuration
    config: {
        animationDuration: 300,
        toastTimeout: 5000,
        autoSaveDelay: 2000
    },

    // Utility functions
    utils: {},

    // UI components
    ui: {},

    // Form handlers
    forms: {},

    // API helpers
    api: {},

    // Role selection modal
    roleSelection: {}
};

/**
 * Utility Functions
 */
Skileez.utils = {
    // Debounce function for performance
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Smooth scroll to element
    scrollTo: function(element, offset = 0) {
        const targetPosition = element.offsetTop - offset;
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    },

    // Format currency
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    },

    // Format date relative to now
    formatRelativeTime: function(date) {
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);

        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
        if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)} days ago`;

        return date.toLocaleDateString();
    },

    // Validate email
    isValidEmail: function(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    // Generate random ID
    generateId: function() {
        return Math.random().toString(36).substr(2, 9);
    },

    // Local storage helpers
    storage: {
        set: function(key, value) {
            try {
                localStorage.setItem(`skileez_${key}`, JSON.stringify(value));
            } catch (e) {
                console.warn('LocalStorage not available');
            }
        },

        get: function(key) {
            try {
                const item = localStorage.getItem(`skileez_${key}`);
                return item ? JSON.parse(item) : null;
            } catch (e) {
                console.warn('LocalStorage not available');
                return null;
            }
        },

        remove: function(key) {
            try {
                localStorage.removeItem(`skileez_${key}`);
            } catch (e) {
                console.warn('LocalStorage not available');
            }
        }
    }
};

/**
 * UI Components and Interactions
 */
Skileez.ui = {
    // Toast notifications
    showToast: function(message, type = 'info') {
        const toastContainer = this.getToastContainer();
        const toast = document.createElement('div');
        const toastId = Skileez.utils.generateId();

        toast.id = toastId;
        toast.className = `toast-notification transform transition-all duration-300 ${this.getToastClasses(type)}`;
        toast.innerHTML = `
            <div class="flex items-center">
                <i data-feather="${this.getToastIcon(type)}" class="w-5 h-5 mr-3"></i>
                <div class="flex-grow">${message}</div>
                <button onclick="Skileez.ui.hideToast('${toastId}')" class="ml-4 text-current opacity-70 hover:opacity-100">
                    <i data-feather="x" class="w-4 h-4"></i>
                </button>
            </div>
        `;

        toastContainer.appendChild(toast);
        feather.replace();

        // Animate in
        setTimeout(() => {
            toast.classList.add('translate-y-0', 'opacity-100');
            toast.classList.remove('translate-y-2', 'opacity-0');
        }, 10);

        // Auto-hide
        setTimeout(() => {
            this.hideToast(toastId);
        }, Skileez.config.toastTimeout);
    },

    hideToast: function(toastId) {
        const toast = document.getElementById(toastId);
        if (toast) {
            toast.classList.add('translate-y-2', 'opacity-0');
            toast.classList.remove('translate-y-0', 'opacity-100');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }
    },

    getToastContainer: function() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'fixed top-4 right-4 z-50 space-y-2';
            document.body.appendChild(container);
        }
        return container;
    },

    getToastClasses: function(type) {
        const baseClasses = 'toast-notification p-4 rounded-lg shadow-lg max-w-sm translate-y-2 opacity-0';
        const typeClasses = {
            success: 'bg-green-500 text-white',
            error: 'bg-red-500 text-white',
            warning: 'bg-yellow-500 text-white',
            info: 'bg-blue-500 text-white'
        };
        return `${baseClasses} ${typeClasses[type] || typeClasses.info}`;
    },

    getToastIcon: function(type) {
        const icons = {
            success: 'check-circle',
            error: 'alert-circle',
            warning: 'alert-triangle',
            info: 'info'
        };
        return icons[type] || icons.info;
    },

    // Modal functionality
    showModal: function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            document.body.classList.add('overflow-hidden');

            // Focus trap
            const focusableElements = modal.querySelectorAll('button, input, textarea, select, a[href]');
            if (focusableElements.length > 0) {
                focusableElements[0].focus();
            }
        }
    },

    hideModal: function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
            document.body.classList.remove('overflow-hidden');
        }
    },

    // Loading states
    showLoading: function(element) {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        if (element) {
            element.classList.add('loading');
            const spinner = document.createElement('div');
            spinner.className = 'spinner';
            spinner.innerHTML = '<div class="bounce1"></div><div class="bounce2"></div><div class="bounce3"></div>';
            element.appendChild(spinner);
        }
    },

    hideLoading: function(element) {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        if (element) {
            element.classList.remove('loading');
            const spinner = element.querySelector('.spinner');
            if (spinner) {
                spinner.remove();
            }
        }
    },

    // Smooth animations
    animateIn: function(element, animation = 'fadeInUp') {
        element.classList.add('animated', animation);
        element.addEventListener('animationend', function() {
            element.classList.remove('animated', animation);
        }, { once: true });
    },

    // Progress bars
    updateProgress: function(progressId, percentage) {
        const progressBar = document.getElementById(progressId);
        if (progressBar) {
            const fill = progressBar.querySelector('.progress-fill');
            if (fill) {
                fill.style.width = `${percentage}%`;
            }
        }
    }
};

/**
 * Form Handling
 */
Skileez.forms = {
    // Auto-save functionality
    enableAutoSave: function(formId, saveUrl) {
        const form = document.getElementById(formId);
        if (!form) return;

        const debouncedSave = Skileez.utils.debounce(function() {
            const formData = new FormData(form);
            fetch(saveUrl, {
                method: 'POST',
                body: formData
            }).then(response => {
                if (response.ok) {
                    Skileez.ui.showToast('Draft saved', 'success');
                }
            }).catch(() => {
                Skileez.ui.showToast('Failed to save draft', 'error');
            });
        }, Skileez.config.autoSaveDelay);

        form.addEventListener('input', debouncedSave);
    },

    // Real-time validation
    addValidation: function(fieldId, validator, errorMessage) {
        const field = document.getElementById(fieldId);
        if (!field) return;

        field.addEventListener('blur', function() {
            const isValid = validator(this.value);
            this.classList.toggle('border-red-500', !isValid);
            this.classList.toggle('border-green-500', isValid);

            let errorDiv = this.parentNode.querySelector('.field-error');
            if (!isValid) {
                if (!errorDiv) {
                    errorDiv = document.createElement('div');
                    errorDiv.className = 'field-error text-red-500 text-sm mt-1';
                    this.parentNode.appendChild(errorDiv);
                }
                errorDiv.textContent = errorMessage;
            } else if (errorDiv) {
                errorDiv.remove();
            }
        });
    },

    // Character counter
    addCharacterCounter: function(textareaId, maxLength) {
        const textarea = document.getElementById(textareaId);
        if (!textarea) return;

        const counter = document.createElement('div');
        counter.className = 'character-counter text-sm text-gray-500 text-right mt-1';
        textarea.parentNode.appendChild(counter);

        const updateCounter = () => {
            const remaining = maxLength - textarea.value.length;
            counter.textContent = `${remaining} characters remaining`;
            counter.classList.toggle('text-red-500', remaining < 0);
            counter.classList.toggle('text-gray-500', remaining >= 0);
        };

        textarea.addEventListener('input', updateCounter);
        updateCounter();
    },

    // Skills tag input
    initSkillsInput: function(inputId, containerId) {
        const input = document.getElementById(inputId);
        const container = document.getElementById(containerId);
        if (!input || !container) return;

        const skills = [];

        const addSkill = (skill) => {
            if (skill && !skills.includes(skill)) {
                skills.push(skill);
                renderSkills();
                input.value = skills.join(', ');
            }
        };

        const removeSkill = (skill) => {
            const index = skills.indexOf(skill);
            if (index > -1) {
                skills.splice(index, 1);
                renderSkills();
                input.value = skills.join(', ');
            }
        };

        const renderSkills = () => {
            container.innerHTML = skills.map(skill => `
                <span class="skill-tag inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800">
                    ${skill}
                    <button type="button" onclick="removeSkill('${skill}')" class="ml-2 text-primary-600 hover:text-primary-800">
                        <i data-feather="x" class="w-3 h-3"></i>
                    </button>
                </span>
            `).join('');
            feather.replace();
        };

        // Make functions globally accessible
        window.removeSkill = removeSkill;

        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                addSkill(this.value.trim());
                this.value = '';
            }
        });

        // Initialize from existing value
        if (input.value) {
            input.value.split(',').forEach(skill => {
                addSkill(skill.trim());
            });
        }
    }
};

/**
 * API Helpers
 */
Skileez.api = {
    // Generic API call wrapper
    call: function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        };

        const mergedOptions = { ...defaultOptions, ...options };

        return fetch(url, mergedOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            });
    },

    // Save job
    saveJob: function(jobId) {
        return this.call(`/save-job/${jobId}`, { method: 'GET' })
            .then(data => {
                if (data.success) {
                    Skileez.ui.showToast('Job saved successfully!', 'success');
                }
                return data;
            })
            .catch(error => {
                Skileez.ui.showToast('Failed to save job', 'error');
                throw error;
            });
    },

    // Load messages
    loadMessages: function(userId) {
        return this.call(`/messages/${userId}/recent`)
            .then(data => data.messages)
            .catch(error => {
                console.error('Failed to load messages:', error);
                return [];
            });
    }
};

/**
 * Role Selection Modal
 */
Skileez.roleSelection = {
    modal: null,
    content: null,

    init: function() {
        this.modal = document.getElementById('role-selection-modal');
        this.content = document.getElementById('modal-content');
        
        if (!this.modal || !this.content) {
            console.warn('Role selection modal elements not found');
            return;
        }

        this.bindEvents();
    },

    bindEvents: function() {
        // Get Started button handlers (for role selection modal)
        const getStartedButtons = [
            'get-started-btn'
        ];

        getStartedButtons.forEach(buttonId => {
            const button = document.getElementById(buttonId);
            if (button) {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.showModal();
                });
            }
        });

        // Become a Coach button handlers - direct to coach signup
        const becomeCoachButtons = [
            'become-coach-btn',
            'mobile-get-started-btn'
        ];

        becomeCoachButtons.forEach(buttonId => {
            const button = document.getElementById(buttonId);
            if (button) {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    window.location.href = '/signup/coach';
                });
            }
        });

        // Role option handlers
        const coachOption = document.getElementById('coach-option');
        const studentOption = document.getElementById('student-option');
        const closeButton = document.getElementById('close-modal');

        if (coachOption) {
            coachOption.addEventListener('click', () => {
                this.selectRole('coach');
            });
        }

        if (studentOption) {
            studentOption.addEventListener('click', () => {
                this.selectRole('student');
            });
        }

        if (closeButton) {
            closeButton.addEventListener('click', () => {
                this.hideModal();
            });
        }

        // Close modal on backdrop click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.hideModal();
            }
        });

        // Close modal on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !this.modal.classList.contains('hidden')) {
                this.hideModal();
            }
        });
    },

    showModal: function() {
        this.modal.classList.remove('hidden');
        this.modal.classList.add('flex');
        document.body.classList.add('overflow-hidden');

        // Animate in
        setTimeout(() => {
            this.content.classList.remove('scale-95', 'opacity-0');
            this.content.classList.add('scale-100', 'opacity-100');
        }, 10);

        // Focus first focusable element
        const firstButton = this.modal.querySelector('button');
        if (firstButton) {
            firstButton.focus();
        }
    },

    hideModal: function() {
        this.content.classList.add('scale-95', 'opacity-0');
        this.content.classList.remove('scale-100', 'opacity-100');

        setTimeout(() => {
            this.modal.classList.add('hidden');
            this.modal.classList.remove('flex');
            document.body.classList.remove('overflow-hidden');
        }, 300);
    },

    selectRole: function(role) {
        // Add loading state to the selected option
        const selectedButton = document.getElementById(`${role}-option`);
        if (selectedButton) {
            selectedButton.classList.add('loading');
            selectedButton.disabled = true;
        }

        // Redirect to appropriate signup page
        setTimeout(() => {
            if (role === 'coach') {
                window.location.href = '/signup/coach';
            } else if (role === 'student') {
                window.location.href = '/signup/student';
            }
        }, 500);
    }
};

/**
 * Initialize Application
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Feather icons
    feather.replace();

    // Initialize role selection modal
    Skileez.roleSelection.init();

    // Global click handlers
    document.addEventListener('click', function(e) {
        // Modal close on backdrop click
        if (e.target.classList.contains('modal-backdrop')) {
            const modal = e.target.closest('.modal');
            if (modal) {
                Skileez.ui.hideModal(modal.id);
            }
        }

        // Dropdown toggles
        if (e.target.closest('.dropdown-toggle')) {
            const dropdown = e.target.closest('.dropdown');
            if (dropdown) {
                const menu = dropdown.querySelector('.dropdown-menu');
                if (menu) {
                    menu.classList.toggle('hidden');
                }
            }
        }

        // Close dropdowns when clicking outside
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.add('hidden');
            });
        }
    });

    // Global keyboard handlers
    document.addEventListener('keydown', function(e) {
        // Close modals on Escape
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal:not(.hidden)');
            openModals.forEach(modal => {
                Skileez.ui.hideModal(modal.id);
            });
        }
    });

    // Mobile menu toggle for embedded navigation
    const mobileButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileButton && mobileMenu) {
        mobileButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Auto-resize textareas
    document.querySelectorAll('textarea[data-auto-resize]').forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });

    // Initialize tooltips
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip absolute z-50 px-2 py-1 text-sm bg-gray-900 text-white rounded shadow-lg';
            tooltip.textContent = this.dataset.tooltip;
            document.body.appendChild(tooltip);

            const rect = this.getBoundingClientRect();
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
            tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
        });

        element.addEventListener('mouseleave', function() {
            const tooltips = document.querySelectorAll('.tooltip');
            tooltips.forEach(tooltip => tooltip.remove());
        });
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                Skileez.utils.scrollTo(target, 80);
            }
        });
    });

    // Form enhancements
    document.querySelectorAll('form[data-auto-save]').forEach(form => {
        const saveUrl = form.dataset.autoSave;
        Skileez.forms.enableAutoSave(form.id, saveUrl);
    });

    // Progress bars animation
    document.querySelectorAll('.progress-bar').forEach(bar => {
        const targetWidth = bar.dataset.progress || 0;
        setTimeout(() => {
            Skileez.ui.updateProgress(bar.id, targetWidth);
        }, 500);
    });

    // Lazy loading for images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }

    // Portfolio item click handlers
    function expandPortfolioItem(element) {
        // Close any currently expanded items
        document.querySelectorAll('.portfolio-item.expanded').forEach(item => {
            if (item !== element) {
                item.classList.remove('expanded');
            }
        });

        // Expand the clicked item
        element.classList.add('expanded');

        // Scroll to the expanded item
        setTimeout(() => {
            element.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
        }, 300);

        // Re-render feather icons for the newly visible close button
        feather.replace();
    }

    function closePortfolioItem(button) {
        const portfolioItem = button.closest('.portfolio-item');
        portfolioItem.classList.remove('expanded');
    }

    // Make functions globally accessible
    window.expandPortfolioItem = expandPortfolioItem;
    window.closePortfolioItem = closePortfolioItem;

    // Enhanced Hero Section Scroll Indicator
    function initScrollIndicator() {
        const scrollIndicator = document.querySelector('.scroll-indicator');
        const scrollArrow = document.querySelector('.scroll-arrow');
        
        if (scrollIndicator && scrollArrow) {
            // Add click handler for scroll indicator
            scrollArrow.addEventListener('click', function() {
                // Find the next section after the hero
                const heroSection = document.querySelector('section');
                const nextSection = heroSection ? heroSection.nextElementSibling : null;
                
                if (nextSection) {
                    nextSection.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                } else {
                    // Fallback: scroll down by viewport height
                    window.scrollBy({
                        top: window.innerHeight,
                        behavior: 'smooth'
                    });
                }
            });

            // Hide scroll indicator when user scrolls down
            let lastScrollY = window.scrollY;
            const hideScrollIndicator = Skileez.utils.debounce(() => {
                const currentScrollY = window.scrollY;
                
                if (currentScrollY > 100) {
                    scrollIndicator.style.opacity = '0';
                    scrollIndicator.style.transform = 'translateX(-50%) translateY(20px)';
                } else {
                    scrollIndicator.style.opacity = '1';
                    scrollIndicator.style.transform = 'translateX(-50%) translateY(0)';
                }
                
                lastScrollY = currentScrollY;
            }, 100);

            window.addEventListener('scroll', hideScrollIndicator);
        }
    }

    // Initialize scroll indicator when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initScrollIndicator);
    } else {
        initScrollIndicator();
    }

    // Connected Scroll Animation System
    function initConnectedScrollAnimations() {
        const heroIcons = document.querySelectorAll('.hero-icon');
        const stepContainers = document.querySelectorAll('.step-container');
        const howItWorksSection = document.getElementById('how-it-works');
        const sections = document.querySelectorAll('section');
        
        if (!heroIcons.length || !stepContainers.length || !howItWorksSection) {
            console.warn('Connected scroll animation elements not found');
            return;
        }

        // Scroll position tracking
        let lastScrollY = window.scrollY;
        let ticking = false;

        function updateScrollAnimations() {
            const scrollY = window.scrollY;
            const windowHeight = window.innerHeight;
            const heroSectionHeight = windowHeight;
            const howItWorksOffset = howItWorksSection.offsetTop;
            const howItWorksHeight = howItWorksSection.offsetHeight;

            // Calculate scroll progress (0 to 1)
            const heroProgress = Math.min(scrollY / heroSectionHeight, 1);
            const howItWorksProgress = Math.max(0, Math.min((scrollY - howItWorksOffset + windowHeight) / (howItWorksHeight + windowHeight), 1));

            // Update hero icons based on scroll progress
            heroIcons.forEach((icon, index) => {
                const targetStep = parseInt(icon.dataset.targetStep);
                const delay = parseInt(icon.dataset.delay);
                
                // Calculate individual icon progress with staggered timing
                const iconProgress = Math.max(0, Math.min((scrollY - (heroSectionHeight * 0.3) + (delay * 100)) / (heroSectionHeight * 0.7), 1));
                
                // Remove all scroll states
                icon.classList.remove('scroll-state-1', 'scroll-state-2', 'scroll-state-3', 'scroll-state-4');
                
                // Apply appropriate scroll state based on progress
                if (iconProgress < 0.2) {
                    icon.classList.add('scroll-state-1');
                } else if (iconProgress < 0.4) {
                    icon.classList.add('scroll-state-2');
                    // Start flowing animation
                    if (!icon.classList.contains('scroll-flowing')) {
                        icon.classList.add('scroll-flowing');
                    }
                } else if (iconProgress < 0.6) {
                    icon.classList.add('scroll-state-3');
                } else {
                    icon.classList.add('scroll-state-4');
                }

                // Special morphing effect when approaching How It Works section
                if (scrollY > howItWorksOffset - windowHeight * 0.5) {
                    const morphProgress = Math.max(0, Math.min((scrollY - (howItWorksOffset - windowHeight * 0.5)) / (windowHeight * 0.5), 1));
                    
                    // Apply morphing transformation
                    const scale = 1 - (morphProgress * 0.4);
                    const translateY = morphProgress * -50;
                    const opacity = 1 - (morphProgress * 0.6);
                    
                    icon.style.transform = `translateY(${translateY}px) scale(${scale})`;
                    icon.style.opacity = opacity;
                } else {
                    // Reset transform when not morphing
                    icon.style.transform = '';
                    icon.style.opacity = '';
                }
            });

            // Update step containers based on scroll progress
            stepContainers.forEach((container, index) => {
                const stepNumber = parseInt(container.dataset.step);
                const stepProgress = Math.max(0, Math.min((scrollY - (howItWorksOffset - windowHeight * 0.3) + (index * 200)) / (windowHeight * 0.6), 1));
                
                // Remove all scroll states
                container.classList.remove('scroll-visible', 'scroll-highlight');
                
                if (stepProgress > 0.1) {
                    container.classList.add('scroll-visible');
                }
                
                if (stepProgress > 0.5) {
                    container.classList.add('scroll-highlight');
                }

                // Update step numbers
                const stepNumberElement = container.querySelector('.step-number');
                if (stepNumberElement) {
                    if (stepProgress > 0.3) {
                        stepNumberElement.classList.add('scroll-highlight');
                    } else {
                        stepNumberElement.classList.remove('scroll-highlight');
                    }
                }
            });

            // Update section transitions
            sections.forEach((section, index) => {
                const sectionOffset = section.offsetTop;
                const sectionHeight = section.offsetHeight;
                const sectionProgress = Math.max(0, Math.min((scrollY - sectionOffset + windowHeight * 0.5) / (sectionHeight + windowHeight), 1));
                
                // Remove all scroll states
                section.classList.remove('scroll-active', 'scroll-entering', 'scroll-visible');
                
                if (sectionProgress > 0.1) {
                    section.classList.add('scroll-entering');
                }
                
                if (sectionProgress > 0.3) {
                    section.classList.add('scroll-visible');
                }
                
                if (sectionProgress > 0.5) {
                    section.classList.add('scroll-active');
                }
            });

            lastScrollY = scrollY;
            ticking = false;
        }

        // Throttled scroll handler for performance
        function requestTick() {
            if (!ticking) {
                requestAnimationFrame(updateScrollAnimations);
                ticking = true;
            }
        }

        // Add scroll event listener
        window.addEventListener('scroll', requestTick, { passive: true });

        // Initial call
        updateScrollAnimations();

        // Cleanup function
        return function cleanup() {
            window.removeEventListener('scroll', requestTick);
        };
    }

    // Initialize connected scroll animations
    let scrollAnimationCleanup;
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            scrollAnimationCleanup = initConnectedScrollAnimations();
        });
    } else {
        scrollAnimationCleanup = initConnectedScrollAnimations();
    }

    // Add click event listeners to portfolio items
    document.querySelectorAll('.portfolio-item').forEach(item => {
        item.addEventListener('click', function(e) {
            // Don't expand if clicking on a link or the close button
            if (e.target.closest('a') || e.target.closest('.portfolio-close')) {
                return;
            }

            // Don't expand if already expanded
            if (this.classList.contains('expanded')) {
                return;
            }

            expandPortfolioItem(this);
        });
    });

    // Initialize any page-specific functionality
    const pageType = document.body.dataset.page;
    if (pageType && Skileez[pageType] && typeof Skileez[pageType].init === 'function') {
        Skileez[pageType].init();
    }

    console.log('Skileez platform initialized successfully!');
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Skileez;
}