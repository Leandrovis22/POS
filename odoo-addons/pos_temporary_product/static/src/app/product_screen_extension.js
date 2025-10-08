/** @odoo-module */

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { TemporaryProductPopup } from "./components/popups/temporary_product_popup/temporary_product_popup";

const originalSetup = Navbar.prototype.setup;

patch(Navbar.prototype, {
    setup() {
        originalSetup.call(this);
        this.dialog = useService("dialog");
    },

    async onClickTemporaryProduct() {
        this.dialog.add(TemporaryProductPopup);
    },
});
