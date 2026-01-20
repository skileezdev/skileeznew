/**
 * Hero Icons Scroll Animation System
 * Creates dynamic, scroll-based animations for hero section icons
 */

class HeroScrollAnimations {
    constructor() {
        this.icons = [];
        this.scrollY = 0;
        this.windowHeight = window.innerHeight;
        this.isAnimating = false;
        this.animationId = null;
        
        // Performance settings
        this.throttleDelay = 16; // ~60fps
        this.lastScrollTime = 0;
        
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    debug() {
        console.log('HeroScrollAnimations Debug:');
        console.log('Icons found:', this.icons.length);
        console.log('Window height:', this.windowHeight);
        console.log('Scroll Y:', this.scrollY);
        this.icons.forEach((icon, index) => {
            console.log(`Icon ${index}:`, icon.element, 'Speed:', icon.speed);
        });
    }

    setup() {
        console.log('HeroScrollAnimations: Setting up...');
        this.collectIcons();
        this.bindEvents();
        this.startAnimation();
        
        // Initial animation state
        this.updateAnimations();
        
        // Debug info
        setTimeout(() => this.debug(), 1000);
    }

    collectIcons() {
        const iconElements = document.querySelectorAll('.hero-icon');
        console.log('Found hero icons:', iconElements.length);
        
        if (iconElements.length === 0) {
            console.warn('No hero icons found! Check if the HTML has .hero-icon class');
            return;
        }
        
        this.icons = Array.from(iconElements).map((icon, index) => ({
            element: icon,
            speed: parseFloat(icon.dataset.speed) || 0.5,
            originalTransform: this.getComputedTransform(icon),
            index: index,
            basePosition: {
                top: icon.offsetTop,
                left: icon.offsetLeft
            }
        }));
        
        console.log('Processed icons:', this.icons.length);
    }

    getComputedTransform(element) {
        const style = window.getComputedStyle(element);
        return style.transform;
    }

    bindEvents() {
        // Throttled scroll handler for performance
        window.addEventListener('scroll', (e) => {
            const now = Date.now();
            if (now - this.lastScrollTime >= this.throttleDelay) {
                this.lastScrollTime = now;
                this.handleScroll();
            }
        });

        // Resize handler
        window.addEventListener('resize', this.debounce(() => {
            this.windowHeight = window.innerHeight;
            this.collectIcons();
        }, 250));

        // Visibility change handler (pause when tab is not visible)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAnimations();
            } else {
                this.resumeAnimations();
            }
        });

        // Reduced motion preference
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            this.disableAnimations();
        }
    }

    handleScroll() {
        this.scrollY = window.pageYOffset;
        this.updateAnimations();
    }

    updateAnimations() {
        if (this.isAnimating) return;
        
        this.isAnimating = true;
        this.animationId = requestAnimationFrame(() => {
            this.icons.forEach(icon => {
                this.animateIcon(icon);
            });
            this.isAnimating = false;
        });
    }

    animateIcon(icon) {
        const { element, speed, index } = icon;
        
        // Calculate scroll progress (0 to 1)
        const scrollProgress = Math.min(this.scrollY / (this.windowHeight * 2), 1);
        
        // Parallax movement
        const parallaxOffset = scrollProgress * 100 * speed;
        
        // Rotation based on scroll
        const rotation = scrollProgress * 360 * speed;
        
        // Scale based on scroll (subtle zoom effect)
        const scale = 1 + (scrollProgress * 0.1 * speed);
        
        // Opacity fade as we scroll down
        const opacity = Math.max(0.3, 1 - (scrollProgress * 0.7));
        
        // 3D perspective effect
        const perspective = 1000 + (scrollProgress * 500);
        
        // Staggered animation delay
        const staggerDelay = index * 0.1;
        const staggeredProgress = Math.max(0, scrollProgress - staggerDelay);
        
        // Apply transformations
        const transform = `
            translate3d(0, ${parallaxOffset}px, 0) 
            rotate(${rotation * staggeredProgress}deg) 
            scale(${scale * staggeredProgress + (1 - staggeredProgress)})
            perspective(${perspective}px)
        `;
        
        element.style.transform = transform;
        element.style.opacity = opacity;
        
        // Add dynamic shadow based on scroll
        const shadowIntensity = 1 + (scrollProgress * 0.5);
        const shadowBlur = 30 + (scrollProgress * 20);
        const shadowSpread = 15 + (scrollProgress * 10);
        
        // Update shadow for the inner div
        const innerDiv = element.querySelector('div');
        if (innerDiv) {
            const currentBoxShadow = innerDiv.style.boxShadow;
            const shadowColor = this.extractShadowColor(currentBoxShadow);
            innerDiv.style.boxShadow = `0 ${shadowBlur}px ${shadowBlur * 2}px -${shadowSpread}px ${shadowColor}, 0 0 0 1px rgba(255, 255, 255, 0.1)`;
        }
    }

    extractShadowColor(boxShadow) {
        // Extract color from existing box-shadow
        const match = boxShadow.match(/rgba?\([^)]+\)/);
        return match ? match[0] : 'rgba(0, 0, 0, 0.3)';
    }

    startAnimation() {
        // Add entrance animation
        this.icons.forEach((icon, index) => {
            icon.element.style.opacity = '0';
            icon.element.style.transform = 'translate3d(0, 50px, 0) scale(0.8)';
            
            setTimeout(() => {
                icon.element.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
                icon.element.style.opacity = '1';
                icon.element.style.transform = 'translate3d(0, 0, 0) scale(1)';
            }, index * 150);
        });
    }

    pauseAnimations() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.isAnimating = false;
        }
    }

    resumeAnimations() {
        this.updateAnimations();
    }

    disableAnimations() {
        this.icons.forEach(icon => {
            icon.element.style.animation = 'none';
            icon.element.style.transition = 'transform 0.3s ease';
        });
    }

    // Utility functions
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
}

// Initialize the animation system
const heroScrollAnimations = new HeroScrollAnimations();

// Export for potential external use
window.HeroScrollAnimations = HeroScrollAnimations;
