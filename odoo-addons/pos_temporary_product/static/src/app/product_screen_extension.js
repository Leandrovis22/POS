/** @odoo-module */

import { Navbar } from "@point_of_sale/app/components/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { TemporaryProductPopup } from "./components/popups/temporary_product_popup/temporary_product_popup";
import { ProductLogger } from "./debug/product_add_logger";

const originalSetup = Navbar.prototype.setup;

patch(Navbar.prototype, {
    setup() {
        originalSetup.call(this);
        this.dialog = useService("dialog");
        
        // Instalar el logger
        const logger = new ProductLogger();
        logger.setup.call({ pos: this.pos, env: this.env });
    },

    async onClickTemporaryProduct() {
        this.dialog.add(TemporaryProductPopup);
    },
});

