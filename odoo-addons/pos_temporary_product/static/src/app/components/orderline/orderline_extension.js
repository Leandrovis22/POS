/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";

// Patch del modelo PosOrderline para soportar nombres personalizados
patch(PosOrderline.prototype, {
    // Override para evitar que set_full_product_name sobrescriba nombres personalizados (Odoo 18)
    set_full_product_name() {
        // Si ya tiene un nombre personalizado, no sobrescribirlo
        if (this.custom_product_name) {
            this.full_product_name = this.custom_product_name;
            return;
        }
        
        // Comportamiento original
        return super.set_full_product_name(...arguments);
    },
    
    // Override para el nombre completo del producto (usado en recibos) (Odoo 18)
    get_full_product_name() {
        if (this.custom_product_name) {
            return this.custom_product_name;
        }
        return super.get_full_product_name(...arguments);
    }
});
