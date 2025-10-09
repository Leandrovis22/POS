/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";

patch(PaymentScreen.prototype, {
    async validateOrder(isForceValidate) {
        const order = this.currentOrder;
        const partner = order.get_partner();
        
        // Verificar si hay pagos con cuenta corriente
        let hasCreditPayment = false;
        for (const payment of order.get_paymentlines()) {
            const paymentMethod = payment.payment_method;
            if (paymentMethod && paymentMethod.name && paymentMethod.name.toLowerCase().includes('cuenta')) {
                hasCreditPayment = true;
                break;
            }
        }
        
        // Si hay pago con cuenta corriente, verificar cliente y límite
        if (hasCreditPayment) {
            if (!partner) {
                await this.popup.add(ErrorPopup, {
                    title: _t('Cliente Requerido'),
                    body: _t('Debe seleccionar un cliente para pagos con cuenta corriente.'),
                });
                return;
            }
            
            // Verificar límite de crédito si está configurado
            if (partner.credit_limit && partner.credit_limit > 0) {
                const newBalance = (partner.account_balance || 0) + order.get_total_with_tax();
                if (newBalance > partner.credit_limit) {
                    const excedido = this.env.utils.formatCurrency(newBalance - partner.credit_limit);
                    await this.popup.add(ErrorPopup, {
                        title: _t('Límite de Crédito Excedido'),
                        body: _t(`El cliente excedería su límite de crédito en ${excedido}.`),
                    });
                    return;
                }
            }
        }
        
        return super.validateOrder(isForceValidate);
    }
});
