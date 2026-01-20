// Ultra-simple test to verify JavaScript is working
console.log('=== SIMPLE TEST SCRIPT LOADED ===');

// Test 1: Check if DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== DOM IS READY ===');
    
    // Test 2: Look for hero icons
    const icons = document.querySelectorAll('.hero-icon');
    console.log('Found', icons.length, 'hero icons');
    
    if (icons.length === 0) {
        console.log('❌ NO HERO ICONS FOUND!');
        console.log('Looking for any elements with "hero" in class...');
        const allHeroElements = document.querySelectorAll('[class*="hero"]');
        console.log('Elements with "hero" in class:', allHeroElements);
        return;
    }
    
    console.log('✅ Hero icons found! Adding test styling...');
    
    // Test 3: Add visible styling to icons
    icons.forEach((icon, index) => {
        console.log(`Icon ${index}:`, icon);
        icon.style.border = '5px solid red';
        icon.style.backgroundColor = 'yellow';
        icon.style.zIndex = '9999';
        icon.style.position = 'absolute';
        icon.style.display = 'block';
        icon.style.width = '100px';
        icon.style.height = '100px';
    });
    
    // Test 4: Add simple scroll animation
    let scrollCount = 0;
    window.addEventListener('scroll', function() {
        scrollCount++;
        console.log('Scroll event #', scrollCount, 'Scroll Y:', window.pageYOffset);
        
        icons.forEach((icon, index) => {
            const moveY = window.pageYOffset * 0.5;
            const rotate = window.pageYOffset * 0.1;
            icon.style.transform = `translateY(${moveY}px) rotate(${rotate}deg)`;
        });
    });
    
    console.log('✅ Scroll animation attached! Try scrolling now...');
});

// Test 5: Immediate check (before DOM ready)
console.log('Immediate check - Icons found:', document.querySelectorAll('.hero-icon').length);
