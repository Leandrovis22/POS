/** @odoo-module **/

console.log('[pos_temp_products] POS-SPECIFIC LOADER STARTING');

// Only run in POS interface
function isPOSInterface() {
    return window.location.href.includes('/pos/ui/') || 
           document.querySelector('.pos-content') ||
           document.querySelector('.pos') ||
           document.body.classList.contains('pos');
}

function injectButton() {
    // Only inject in POS
    if (!isPOSInterface()) {
        console.log('[pos_temp_products] Not in POS interface, skipping');
        return;
    }
    
    // Don't inject if button already exists
    if (document.querySelector('.o-btn-add-temp')) {
        console.log('[pos_temp_products] Button already exists');
        return;
    }
    
    console.log('[pos_temp_products] POS detected, injecting button');
    
    // Look for good spots in POS to place the button
    const posContainers = [
        '.product-screen .searchbox',
        '.product-screen .search-bar', 
        '.pos-topheader',
        '.rightpane-header',
        '.leftpane-header',
        '.screen-content'
    ];
    
    let injected = false;
    
    for (const selector of posContainers) {
        const container = document.querySelector(selector);
        if (container) {
            console.log(`[pos_temp_products] Found POS container: ${selector}`);
            
            const button = document.createElement('button');
            button.className = 'btn btn-secondary o-btn-add-temp me-2';
            button.innerHTML = '<i class="fa fa-plus"></i> Agregar producto';
            button.style.cssText = `margin: 5px;`;
            
            button.onclick = function() {
                console.log('[pos_temp_products] Button clicked in POS!');
                alert('¡Botón POS funcionando! Popup se implementará.');
            };
            
            // Insert before or after the container
            if (container.parentNode) {
                container.parentNode.insertBefore(button, container);
            } else {
                container.appendChild(button);
            }
            
            console.log('[pos_temp_products] Button injected in POS successfully');
            injected = true;
            break;
        }
    }
    
    // Fallback: floating button only in POS
    if (!injected) {
        const button = document.createElement('button');
        button.className = 'btn btn-primary o-btn-add-temp';
        button.innerHTML = '+ Producto Temporal';
        button.style.cssText = `
            position: fixed;
            top: 10px;
            left: 10px;
            z-index: 9999;
            padding: 8px 12px;
            font-size: 12px;
        `;
        
        button.onclick = function() {
            console.log('[pos_temp_products] Floating button clicked in POS!');
            alert('¡Botón POS funcionando! Popup próximamente.');
        };
        
        document.body.appendChild(button);
        console.log('[pos_temp_products] Floating button injected in POS');
    }
}

// Multiple injection attempts with POS detection
document.addEventListener('DOMContentLoaded', function() {
    console.log('[pos_temp_products] DOM Content Loaded, checking for POS');
    if (isPOSInterface()) {
        injectButton();
    }
});

// Try after delays (POS may load dynamically)
setTimeout(function() {
    if (isPOSInterface()) {
        console.log('[pos_temp_products] Delayed injection (2s)');
        injectButton();
    }
}, 2000);

setTimeout(function() {
    if (isPOSInterface()) {
        console.log('[pos_temp_products] Delayed injection (5s)');
        injectButton();
    }
}, 5000);

// Watch for URL changes (SPA navigation)
let currentUrl = window.location.href;
setInterval(function() {
    if (window.location.href !== currentUrl) {
        currentUrl = window.location.href;
        console.log('[pos_temp_products] URL changed to:', currentUrl);
        if (isPOSInterface()) {
            setTimeout(injectButton, 500);
        }
    }
}, 1000);

console.log('[pos_temp_products] POS-SPECIFIC LOADER SCRIPT LOADED');