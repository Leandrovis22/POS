/** @odoo-module */

import { ProductScreen } from '@point_of_sale/app/screens/product_screen/product_screen';
import { _t } from '@web/core/l10n/translation';
import { TempProductPopup } from './temp_popup';
import { patch } from '@web/core/utils/patch';

console.log('[pos_temp_products] Loading add_temp_button.js');

patch(ProductScreen.prototype, {
    setup() {
        super.setup();
        console.log('[pos_temp_products] ProductScreen setup() patched');
    },

    async onClickAddTempProduct() {
        console.log('[pos_temp_products] Button clicked!');
        
        const { confirmed, payload } = await this.popup.add(TempProductPopup, {
            title: _t('Agregar productos temporales'),
        });
        
        if (!confirmed || !payload || !payload.rows?.length) {
            console.log('[pos_temp_products] Popup cancelled or no data');
            return;
        }
        
        console.log('[pos_temp_products] Popup data:', payload);
        
        const pos = this.pos;
        const order = pos.get_order();
        if (!order) {
            console.log('[pos_temp_products] No active order');
            return;
        }

        // Find temp product by name (simple approach)
        const allProducts = pos.db.get_product_by_category(0) || [];
        const tempProduct = allProducts.find(
            (p) => p.display_name === 'Producto temporal POS' || p.name === 'Producto temporal POS'
        );
        
        if (!tempProduct) {
            console.log('[pos_temp_products] Temp product not found in POS');
            alert('Producto temporal no encontrado. Asegúrate de que esté disponible en el POS.');
            return;
        }

        console.log('[pos_temp_products] Found temp product:', tempProduct.name);

        for (const row of payload.rows) {
            if (!row.name || row.qty <= 0 || row.price < 0) continue;
            
            console.log('[pos_temp_products] Adding row:', row);
            
            const line = order.add_product(tempProduct, {
                quantity: row.qty,
                merge: false,
            });
            
            if (line) {
                line.set_unit_price(row.price);
                line.temp_name = row.name;
                line.is_temp_line = true;
                console.log('[pos_temp_products] Line added successfully');
            }
        }
    },
});
