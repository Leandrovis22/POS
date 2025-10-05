/* ULTRA SIMPLE TEST FILE - POS SPECIFIC */
console.log('🔥 ULTRA SIMPLE TEST LOADED 🔥');
console.log('🔥 Current URL:', window.location.href);

// Check if we're in POS
if (window.location.href.includes('/pos/ui/')) {
    console.log('🔥 WE ARE IN POS! 🔥');
    alert('🔥 JS LOADED IN POS! 🔥');
    
    // Try to inject button immediately
    setTimeout(function() {
        const button = document.createElement('button');
        button.innerHTML = '🔥 TEST BUTTON 🔥';
        button.style.cssText = 'position: fixed; top: 10px; right: 10px; z-index: 99999; background: red; color: white; padding: 10px; border: none; cursor: pointer;';
        button.onclick = () => alert('BUTTON WORKS!');
        document.body.appendChild(button);
        console.log('🔥 BUTTON INJECTED IN POS 🔥');
    }, 1000);
} else {
    console.log('🔥 NOT IN POS - URL:', window.location.href);
    alert('🔥 JS LOADED BUT NOT IN POS! 🔥');
}