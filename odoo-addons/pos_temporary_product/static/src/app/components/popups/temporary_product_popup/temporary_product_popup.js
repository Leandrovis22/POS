/** @odoo-module */

import { Component, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";

export class TemporaryProductPopup extends Component {
    static template = "pos_temporary_product.TemporaryProductPopup";
    static components = { Dialog };
    static props = {
        close: Function,
        title: { type: String, optional: true },
    };
    
    setup() {
        this.pos = usePos();
        this.notification = useService("notification");
        this.state = useState({
            products: [{ name: "", qty: 1, price: 0 }],
        });
    }
    
    addInput() {
        this.state.products.push({ name: "", qty: 1, price: 0 });
    }
    
    async confirm() {
        // Buscar el producto temporal específico (TEMP_POS)
        const allProducts = this.pos.models["product.product"]?.getAll() || [];
        let templateProduct = allProducts.find(p => p.default_code === 'TEMP_POS');
        
        // Si no existe, usar el primero como fallback
        if (!templateProduct) {
            templateProduct = allProducts[0];
        }
        
        if (!templateProduct) {
            this.notification.add("No hay productos disponibles en el POS", { type: "danger" });
            this.props.close();
            return;
        }

        for (const prod of this.state.products) {
            if (prod.name && prod.qty > 0 && prod.price >= 0) {
                try {
                    // Agregar producto usando la estructura correcta para Odoo 18
                    const line = await this.pos.addLineToCurrentOrder(
                        { product_id: templateProduct },
                        {}
                    );
                    
                    // Modificar la línea después de crearla
                    if (line) {
                        // Guardar el nombre personalizado
                        line.custom_product_name = prod.name;
                        line.full_product_name = prod.name;
                        
                        // Establecer cantidad y precio
                        line.qty = parseFloat(prod.qty);
                        line.price_unit = parseFloat(prod.price);
                        
                        // Los impuestos ya vienen del producto TEMP_POS configurado en XML
                        
                        // Forzar actualización de la orden
                        const currentOrder = line.order_id;
                        if (currentOrder) {
                            line._dirty = true;
                            currentOrder.recomputeOrderData();
                            currentOrder.select_orderline(line);
                        }
                    }
                } catch (error) {
                    console.error("Error agregando producto temporal:", error);
                    this.notification.add(`Error: ${error.message}`, { type: "danger" });
                }
            }
        }
        
        this.notification.add("Productos temporales agregados", { type: "success" });
        this.props.close();
    }
    
    cancel() {
        this.props.close();
    }
}
