/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { CustomerCreditPopup } from "../components/popups/customer_credit_popup/customer_credit_popup";

patch(PosStore.prototype, {
    async setup() {
        await super.setup(...arguments);
        
        // Registrar popup de cuenta corriente
        this.dialog.register(CustomerCreditPopup);
    },

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

    /**
     * Actualiza el saldo de crédito del cliente actual
     */
    async updateCustomerCreditBalance() {
        const order = this.get_order();
        if (!order) return;

        const partner = order.get_partner();
        if (!partner) return;

        const creditInfo = await this.loadCustomerCreditInfo(partner.id);
        if (creditInfo) {
            partner.credit_balance = creditInfo.credit_balance;
        }
    },
});
