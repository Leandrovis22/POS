/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";

// Patch del modelo PosOrderline para soportar nombres personalizados
patch(PosOrderline.prototype, {
    // Override para evitar que setFullProductName sobrescriba nombres personalizados
    setFullProductName() {
        // Si ya tiene un nombre personalizado, no sobrescribirlo
        if (this.custom_product_name) {
            this.full_product_name = this.custom_product_name;
            return;
        }
        
        // Comportamiento original
        return super.setFullProductName(...arguments);
    },
    
    // Override para el nombre completo del producto (usado en recibos)
    getFullProductName() {
        if (this.custom_product_name) {
            return this.custom_product_name;
        }
        return super.getFullProductName(...arguments);
    },
    
    // Override para el nombre mostrado en la pantalla de productos
    get orderDisplayProductName() {
        const original = super.orderDisplayProductName;
        
        if (this.custom_product_name) {
            return {
                name: this.custom_product_name,
                attributeString: original.attributeString,
            };
        }
        
        return original;
    }
});
