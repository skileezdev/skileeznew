// Simple test script to verify scroll animations work
console.log('Test scroll script loaded!');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, looking for hero icons...');
    
    // Find all elements with hero-icon class
    const icons = document.querySelectorAll('.hero-icon');
    console.log('Found', icons.length, 'hero icons');
    
    if (icons.length === 0) {
        console.log('No hero icons found! Checking for any elements with "hero" in class...');
        const allElements = document.querySelectorAll('[class*="hero"]');
        console.log('Elements with "hero" in class:', allElements);
        return;
    }
    
    // Make icons visible and add test styling
    icons.forEach((icon, index) => {
        console.log(`Icon ${index}:`, icon);
        icon.style.border = '3px solid red';
        icon.style.backgroundColor = 'rgba(255, 0, 0, 0.2)';
        icon.style.zIndex = '9999';
        icon.style.display = 'block'; // Force visibility
    });
    
    // Add scroll animation
    let ticking = false;
    
    function animateOnScroll() {
        if (!ticking) {
            requestAnimationFrame(() => {
                const scrollY = window.pageYOffset;
                const windowHeight = window.innerHeight;
                const scrollProgress = Math.min(scrollY / (windowHeight * 2), 1);
                
                icons.forEach((icon, index) => {
                    const speed = parseFloat(icon.dataset.speed) || 0.5;
                    const moveY = scrollProgress * 100 * speed;
                    const rotate = scrollProgress * 180 * speed;
                    const scale = 1 + (scrollProgress * 0.3 * speed);
                    
                    icon.style.transform = `translate3d(0, ${moveY}px, 0) rotate(${rotate}deg) scale(${scale})`;
                    icon.style.opacity = Math.max(0.3, 1 - scrollProgress * 0.5);
                });
                
                ticking = false;
            });
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', animateOnScroll);
    
    // Initial animation
    animateOnScroll();
    
    console.log('Scroll animation attached! Try scrolling...');
});
