/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    /**
     * Carga información de cuenta corriente para un partner
     */
    async loadCustomerCreditInfo(partnerId) {
        try {
            const result = await this.data.call(
                'res.partner',
                'get_credit_info_for_pos',
                [partnerId]
            );
            return result;
        } catch (error) {
            console.error('Error loading customer credit info:', error);
            return null;
        }
    },
});
