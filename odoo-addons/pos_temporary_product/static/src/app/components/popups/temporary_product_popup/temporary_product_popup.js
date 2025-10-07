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
        console.log("Confirm called, pos:", this.pos);
        
        // Buscar el producto temporal específico (TEMP_POS)
        const allProducts = this.pos.models["product.product"]?.getAll() || [];
        console.log("All products:", allProducts.length);
        
        // Buscar el producto con código TEMP_POS
        let templateProduct = allProducts.find(p => p.default_code === 'TEMP_POS');
        
        // Si no existe, usar el primero como fallback
        if (!templateProduct) {
            console.warn("Producto TEMP_POS no encontrado, usando el primero disponible");
            templateProduct = allProducts[0];
        }
        
        if (!templateProduct) {
            this.notification.add("No hay productos disponibles en el POS", { type: "danger" });
            this.props.close();
            return;
        }

        console.log("Using template product:", templateProduct.display_name);

        for (const prod of this.state.products) {
            if (prod.name && prod.qty > 0 && prod.price >= 0) {
                try {
                    console.log("Agregando producto temporal:", prod.name, "Qty:", prod.qty, "Price:", prod.price);
                    
                    // Agregar producto usando la estructura correcta para Odoo 18
                    // En Odoo 18, addLineToCurrentOrder espera { product_id: producto }
                    const line = await this.pos.addLineToCurrentOrder(
                        { product_id: templateProduct },
                        {}
                    );
                    
                    // Modificar la línea después de crearla
                    if (line) {
                        // Guardar el nombre personalizado (será usado por el patch de getFullProductName)
                        line.custom_product_name = prod.name;
                        
                        // IMPORTANTE: También actualizar full_product_name para que aparezca en el recibo
                        line.full_product_name = prod.name;
                        
                        // Establecer cantidad y precio
                        line.qty = parseFloat(prod.qty);
                        line.price_unit = parseFloat(prod.price);
                        
                        // Copiar los impuestos de otro producto para evitar errores de validación
                        // Buscar un producto con impuestos configurados
                        const productWithTaxes = allProducts.find(p => p.taxes_id && p.taxes_id.length > 0);
                        if (productWithTaxes && productWithTaxes.taxes_id) {
                            line.tax_ids = productWithTaxes.taxes_id;
                            console.log("   Impuestos copiados de:", productWithTaxes.display_name);
                        }
                        
                        // Forzar actualización de la orden
                        const currentOrder = line.order_id;
                        if (currentOrder) {
                            console.log("   full_product_name ANTES de recomputeOrderData:", line.full_product_name);
                            
                            // Marcar la línea como modificada para forzar re-render
                            line._dirty = true;
                            
                            // Recalcular totales de la orden
                            currentOrder.recomputeOrderData();
                            
                            console.log("   full_product_name DESPUÉS de recomputeOrderData:", line.full_product_name);
                            
                            // Forzar actualización de la UI seleccionando la línea (método correcto en Odoo 18)
                            currentOrder.select_orderline(line);
                        }
                        
                        console.log("✅ Producto agregado:");
                        console.log("   custom_product_name:", line.custom_product_name);
                        console.log("   full_product_name:", line.full_product_name);
                        console.log("   qty:", line.qty);
                        console.log("   price_unit:", line.price_unit);
                        console.log("   get_full_product_name():", line.get_full_product_name());
                    }
                } catch (error) {
                    console.error("Error agregando producto:", error);
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
