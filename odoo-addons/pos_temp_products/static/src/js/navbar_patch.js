/** @odoo-module */

import { Navbar } from '@point_of_sale/app/components/navbar/navbar';
import { patch } from '@web/core/utils/patch';
import { useService } from '@web/core/utils/hooks';
import { openTempProductDialog } from './temp_product_handler';

const originalSetup = Navbar.prototype.setup;
patch(Navbar.prototype, 'pos_temp_products_navbar_patch', {
    setup() {
        originalSetup.apply(this, arguments);
        this.popup = useService('popup');
    },

    get showTempProductButton() {
        const configHasProduct = Boolean(this.pos?.config?.temp_product_id);
        const isProductScreen = this.pos?.router?.state?.current === 'ProductScreen';
        return configHasProduct && isProductScreen;
    },

    async onClickTempProductButton() {
        await openTempProductDialog({
            pos: this.pos,
            popup: this.popup || this.env.services?.popup,
            notification: this.notification || this.env.services?.notification,
        });
    },
});
