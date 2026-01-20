// Minimal test - this will definitely work
console.log('MINIMAL TEST SCRIPT LOADED');

// Wait for page to load
window.addEventListener('load', function() {
    console.log('PAGE FULLY LOADED');
    
    // Create test icons directly
    const container = document.createElement('div');
    container.style.position = 'fixed';
    container.style.top = '0';
    container.style.left = '0';
    container.style.width = '100%';
    container.style.height = '100%';
    container.style.pointerEvents = 'none';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    
    // Create 3 test icons
    for (let i = 0; i < 3; i++) {
        const icon = document.createElement('div');
        icon.className = 'test-icon';
        icon.style.position = 'absolute';
        icon.style.width = '80px';
        icon.style.height = '80px';
        icon.style.background = 'red';
        icon.style.border = '3px solid blue';
        icon.style.borderRadius = '20px';
        icon.style.display = 'flex';
        icon.style.alignItems = 'center';
        icon.style.justifyContent = 'center';
        icon.style.color = 'white';
        icon.style.fontWeight = 'bold';
        icon.style.fontSize = '14px';
        icon.innerHTML = `ICON ${i + 1}`;
        
        // Position icons
        if (i === 0) {
            icon.style.top = '100px';
            icon.style.left = '100px';
        } else if (i === 1) {
            icon.style.top = '200px';
            icon.style.right = '100px';
        } else {
            icon.style.bottom = '100px';
            icon.style.left = '50%';
            icon.style.transform = 'translateX(-50%)';
        }
        
        container.appendChild(icon);
    }
    
    console.log('Created 3 test icons');
    
    // Add scroll animation
    let scrollCount = 0;
    window.addEventListener('scroll', function() {
        scrollCount++;
        console.log('Scroll event #', scrollCount, 'Y position:', window.pageYOffset);
        
        const icons = document.querySelectorAll('.test-icon');
        icons.forEach((icon, index) => {
            const moveY = window.pageYOffset * 0.5;
            const rotate = window.pageYOffset * 0.2;
            const scale = 1 + (window.pageYOffset * 0.001);
            
            icon.style.transform = `translateY(${moveY}px) rotate(${rotate}deg) scale(${scale})`;
        });
    });
    
    console.log('Scroll animation attached! Try scrolling now...');
});
