/* Basic vanilla JS - no modules */

console.log('=== POS TEMP PRODUCTS BASIC LOADER ===');

(function() {
    'use strict';
    
    let injectionAttempts = 0;
    const maxAttempts = 20;
    
    function tryInjectButton() {
        injectionAttempts++;
        console.log('POS TEMP: Injection attempt', injectionAttempts, 'of', maxAttempts);
        
        // Check if we're in POS
        const isPOS = window.location.href.includes('/pos/ui/') || 
                     document.querySelector('.pos-content') ||
                     document.querySelector('.pos') ||
                     document.body.classList.contains('o_pos_ui');
                     
        if (!isPOS) {
            console.log('POS TEMP: Not in POS interface');
            return false;
        }
        
        console.log('POS TEMP: In POS interface, looking for injection point');
        
        // Don't inject if button already exists
        if (document.querySelector('.o-btn-add-temp')) {
            console.log('POS TEMP: Button already exists');
            return true;
        }
        
        // Try to find the product screen or any good container
        const containers = [
            '.product-screen',
            '.pos-content',
            '.rightpane',
            '.screen-content',
            'body'
        ];
        
        for (let selector of containers) {
            const container = document.querySelector(selector);
            if (container) {
                console.log('POS TEMP: Found container:', selector);
                
                // Create floating button
                const button = document.createElement('button');
                button.className = 'btn btn-success o-btn-add-temp';
                button.innerHTML = '+ Agregar Producto Temporal';
                button.style.cssText = `
                    position: fixed;
                    top: 10px;
                    right: 10px;
                    z-index: 99999;
                    padding: 10px 15px;
                    font-weight: bold;
                    border: none;
                    border-radius: 5px;
                    background: #28a745;
                    color: white;
                    cursor: pointer;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                `;
                
                button.addEventListener('click', function() {
                    console.log('POS TEMP: Button clicked!');
                    alert('¡Botón funcionando perfectamente!\n\nPróximo paso: implementar el popup para agregar productos temporales.');
                });
                
                document.body.appendChild(button);
                console.log('POS TEMP: Button injected successfully');
                return true;
            }
        }
        
        console.log('POS TEMP: No suitable container found');
        return false;
    }
    
    // Multiple injection strategies
    
    // 1. Immediate attempt
    tryInjectButton();
    
    // 2. DOM Content Loaded
    document.addEventListener('DOMContentLoaded', function() {
        console.log('POS TEMP: DOM Content Loaded');
        tryInjectButton();
    });
    
    // 3. Window load
    window.addEventListener('load', function() {
        console.log('POS TEMP: Window loaded');
        tryInjectButton();
    });
    
    // 4. Intervals
    const intervalId = setInterval(function() {
        if (tryInjectButton() || injectionAttempts >= maxAttempts) {
            clearInterval(intervalId);
            console.log('POS TEMP: Stopping injection attempts');
        }
    }, 1000);
    
    // 5. Mutation observer to detect when POS loads
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                for (let node of mutation.addedNodes) {
                    if (node.nodeType === 1) { // Element node
                        if (node.classList && (node.classList.contains('pos-content') || 
                            node.classList.contains('product-screen') ||
                            node.querySelector && node.querySelector('.pos-content'))) {
                            console.log('POS TEMP: POS content detected via mutation observer');
                            setTimeout(tryInjectButton, 500);
                        }
                    }
                }
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    console.log('POS TEMP: All injection strategies initialized');
    
})();