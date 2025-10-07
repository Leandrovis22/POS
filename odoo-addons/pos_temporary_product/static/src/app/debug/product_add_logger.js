/** @odoo-module */

import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

// Componente simple que intercepta el pos en el setup
export class ProductLogger extends Component {
    static template = "pos_temporary_product.ProductLogger";
    
    setup() {
        const pos = usePos();
        
        console.log("🔍 Product Logger initialized!");
        console.log("🔍 POS object:", pos);
        
        // Interceptar addLineToCurrentOrder
        if (pos.addLineToCurrentOrder) {
            const original = pos.addLineToCurrentOrder.bind(pos);
            pos.addLineToCurrentOrder = async (...args) => {
                console.log("🔍 === PRODUCT ADD INTERCEPTOR === 🔍");
                console.log("Arguments:", args);
                console.log("arg[0]:", args[0]);
                console.log("arg[1]:", args[1]);
                
                const result = await original(...args);
                
                console.log("🔍 Result:", result);
                if (result) {
                    console.log("  qty:", result.qty);
                    console.log("  price_unit:", result.price_unit);
                    console.log("  product_id:", result.product_id);
                    console.log("  product_id.display_name:", result.product_id?.display_name);
                    console.log("  product_id.name:", result.product_id?.name);
                    console.log("  full_product_name:", result.full_product_name);
                    console.log("  product_name:", result.product_name);
                    console.log("  get_full_product_name():", result.get_full_product_name?.());
                    console.log("  get_product_name():", result.get_product_name?.());
                }
                console.log("===========================================");
                
                return result;
            };
            console.log("✅ Interceptor installed on addLineToCurrentOrder");
        } else {
            console.error("❌ addLineToCurrentOrder not found on pos object");
            console.log("Available methods on pos:", Object.keys(pos));
        }
    }
}
