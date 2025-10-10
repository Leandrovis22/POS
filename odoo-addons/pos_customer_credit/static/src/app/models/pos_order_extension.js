/** @odoo-module */

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
        this.has_credit_payment = false;
        this.credit_amount = 0;
        this.cash_amount = 0;
    },

    /**
     * Override para actualizar información de crédito cuando cambian los pagos
     */
    add_paymentline(payment_method) {
        const paymentline = super.add_paymentline(...arguments);
        this._update_credit_payment_info();
        return paymentline;
    },

    /**
     * Override para actualizar información de crédito cuando se remueven pagos
     */
    remove_paymentline(paymentline) {
        super.remove_paymentline(...arguments);
        this._update_credit_payment_info();
    },

    /**
     * Actualiza la información de pagos con crédito
     */
    _update_credit_payment_info() {
        let creditAmount = 0;
        let cashAmount = 0;
        let hasCreditPayment = false;

        for (const paymentline of this.get_paymentlines()) {
            if (paymentline.payment_method.is_credit_payment) {
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

    /**
     * Override export_as_JSON para incluir información de crédito
     */
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.has_credit_payment = this.has_credit_payment;
        json.credit_amount = this.credit_amount;
        json.cash_amount = this.cash_amount;
        return json;
    },

    /**
     * Override init_from_JSON para restaurar información de crédito
     */
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.has_credit_payment = json.has_credit_payment || false;
        this.credit_amount = json.credit_amount || 0;
        this.cash_amount = json.cash_amount || 0;
    },

    /**
     * Valida si se puede usar cuenta corriente
     */
    can_use_credit_payment() {
        const partner = this.get_partner();
        
        if (!this.pos.config.enable_customer_credit) {
            return {
                ok: false,
                error: 'La cuenta corriente no está habilitada en este POS'
            };
        }

        if (this.pos.config.require_customer_for_credit && !partner) {
            return {
                ok: false,
                error: 'Debe seleccionar un cliente para usar cuenta corriente'
            };
        }

        return { ok: true };
    },

    /**
     * Obtiene información de crédito para mostrar
     */
    get_credit_info() {
        return {
            has_credit: this.has_credit_payment,
            credit_amount: this.credit_amount,
            cash_amount: this.cash_amount,
            total_amount: this.get_total_with_tax(),
        };
    },
});
