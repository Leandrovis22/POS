/** @odoo-module */

import { registry } from '@web/core/registry';
import { Component, onMounted } from '@odoo/owl';

console.log('[pos_temp_products] LOADING SCRIPT - direct injection');

// Simple service to inject the button
class TempProductButtonService {
    start() {
        console.log('[pos_temp_products] TempProductButtonService started');
        this.injectButtonWhenReady();
    }

    injectButtonWhenReady() {
        console.log('[pos_temp_products] Attempting to inject button');
        
        // Try multiple times as the DOM might not be ready
        let attempts = 0;
        const maxAttempts = 50;
        
        const tryInject = () => {
            attempts++;
            console.log(`[pos_temp_products] Inject attempt ${attempts}/${maxAttempts}`);
            
            // Look for various possible containers
            const containers = [
                '.product-screen',
                '.pos-content',
                '.screen-content', 
                '.search-bar',
                '.searchbox',
                '.pos-topheader',
                '.order-widget',
                '.rightpane',
                'body'
            ];
            
            let injected = false;
            
            for (const selector of containers) {
                const container = document.querySelector(selector);
                if (container && !document.querySelector('.o-btn-add-temp')) {
                    console.log(`[pos_temp_products] Found container: ${selector}`);
                    
                    const button = document.createElement('button');
                    button.className = 'btn btn-primary o-btn-add-temp';
                    button.style.cssText = 'position: fixed; top: 10px; right: 10px; z-index: 9999;';
                    button.innerHTML = '+ Agregar Producto Temporal';
                    
                    button.onclick = () => {
                        console.log('[pos_temp_products] Button clicked!');
                        alert('Button works! Popup will be implemented next.');
                    };
                    
                    document.body.appendChild(button);
                    console.log('[pos_temp_products] Button injected successfully!');
                    injected = true;
                    break;
                }
            }
            
            if (!injected && attempts < maxAttempts) {
                setTimeout(tryInject, 200);
            } else if (!injected) {
                console.log('[pos_temp_products] Failed to inject button after all attempts');
            }
        };
        
        // Start trying immediately and also when DOM loads
        tryInject();
        document.addEventListener('DOMContentLoaded', tryInject);
        setTimeout(tryInject, 1000);
        setTimeout(tryInject, 3000);
        setTimeout(tryInject, 5000);
    }
}

// Register the service
registry.category('services').add('pos_temp_products.button_injector', TempProductButtonService);

console.log('[pos_temp_products] Service registered');