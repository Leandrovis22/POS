/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";

// Patch del modelo PosOrder para soportar cuenta corriente
patch(PosOrder.prototype, {
    setup() {
        super.setup(...arguments);
        this.has_credit_payment = this.has_credit_payment || false;
        this.credit_amount = this.credit_amount || 0;
        this.cash_amount = this.cash_amount || 0;
    },

    /**
     * Actualiza la información de pagos con crédito
     */
    updateCreditPaymentInfo() {
        let creditAmount = 0;
        let cashAmount = 0;
        let hasCreditPayment = false;

        for (const paymentline of this.payment_ids || []) {
            if (paymentline.payment_method_id && paymentline.payment_method_id.is_credit_payment) {
                creditAmount += paymentline.amount;
                hasCreditPayment = true;
            } else {
                cashAmount += paymentline.amount;
            }
        }

        this.has_credit_payment = hasCreditPayment;
        this.credit_amount = creditAmount;
        this.cash_amount = cashAmount;
    },
});
