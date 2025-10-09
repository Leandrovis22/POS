/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

patch(PaymentScreen.prototype, {
    async validateOrder(isForceValidate) {
        const order = this.currentOrder;
        const partner = order.get_partner();
        
        // Verificar si hay pagos con cuenta corriente
        let hasCreditPayment = false;
        for (const payment of order.payment_ids) {
            const paymentMethod = payment.payment_method_id;
            if (paymentMethod && paymentMethod.name && paymentMethod.name.toLowerCase().includes('cuenta')) {
                hasCreditPayment = true;
                break;
            }
        }
        
        // Si hay pago con cuenta corriente, verificar cliente y límite
        if (hasCreditPayment) {
            if (!partner) {
                this.dialog.add(AlertDialog, {
                    title: _t('Cliente Requerido'),
                    body: _t('Debe seleccionar un cliente para pagos con cuenta corriente.'),
                });
                return;
            }
            
            // Verificar límite de crédito solo si está configurado (mayor a 0)
            if (partner.account_credit_limit && partner.account_credit_limit > 0) {
                const newBalance = (partner.account_balance || 0) + order.get_total_with_tax();
                if (newBalance > partner.account_credit_limit) {
                    const excedido = this.env.utils.formatCurrency(newBalance - partner.account_credit_limit);
                    this.dialog.add(AlertDialog, {
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
