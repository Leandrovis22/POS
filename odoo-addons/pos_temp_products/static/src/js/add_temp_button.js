/** @odoo-module */

import { ProductScreen } from '@point_of_sale/app/screens/product_screen/product_screen';
import { openTempProductDialog } from './temp_product_handler';
import { patch } from '@web/core/utils/patch';

const originalSetup = ProductScreen.prototype.setup;

patch(ProductScreen.prototype, 'pos_temp_products_product_screen_patch', {
    setup() {
        originalSetup.apply(this, arguments);
    },

    async onClickAddTempProduct() {
        await openTempProductDialog({
            pos: this.pos,
            popup: this.popup || this.env.services?.popup,
            notification: this.notification || this.env.services?.notification,
        });
    },
});
