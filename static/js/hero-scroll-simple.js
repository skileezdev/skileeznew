/**
 * Simple Hero Icons Scroll Animation
 * Fallback version that should definitely work
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Simple Hero Scroll Animation: Starting...');
    
    // Find all hero icons
    const icons = document.querySelectorAll('.hero-icon');
    console.log('Found icons:', icons.length);
    
    if (icons.length === 0) {
        console.warn('No hero icons found!');
        return;
    }
    
    // Add basic scroll animation
    function updateIcons() {
        const scrollY = window.pageYOffset;
        const windowHeight = window.innerHeight;
        const scrollProgress = Math.min(scrollY / (windowHeight * 2), 1);
        
        icons.forEach((icon, index) => {
            const speed = parseFloat(icon.dataset.speed) || 0.5;
            const parallaxOffset = scrollProgress * 100 * speed;
            const rotation = scrollProgress * 180 * speed;
            const scale = 1 + (scrollProgress * 0.2 * speed);
            const opacity = Math.max(0.3, 1 - (scrollProgress * 0.5));
            
            icon.style.transform = `translate3d(0, ${parallaxOffset}px, 0) rotate(${rotation}deg) scale(${scale})`;
            icon.style.opacity = opacity;
        });
    }
    
    // Throttled scroll handler
    let ticking = false;
    function onScroll() {
        if (!ticking) {
            requestAnimationFrame(() => {
                updateIcons();
                ticking = false;
            });
            ticking = true;
        }
    }
    
    // Bind scroll event
    window.addEventListener('scroll', onScroll);
    
    // Initial update
    updateIcons();
    
    // Add entrance animation
    icons.forEach((icon, index) => {
        icon.style.opacity = '0';
        icon.style.transform = 'translate3d(0, 50px, 0) scale(0.8)';
        
        setTimeout(() => {
            icon.style.transition = 'all 0.8s ease-out';
            icon.style.opacity = '1';
            icon.style.transform = 'translate3d(0, 0, 0) scale(1)';
        }, index * 200);
    });
    
    console.log('Simple Hero Scroll Animation: Initialized!');
});
