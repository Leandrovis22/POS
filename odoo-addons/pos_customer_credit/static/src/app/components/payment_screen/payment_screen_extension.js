/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { CustomerCreditButton } from "@pos_customer_credit/app/components/customer_credit_button/customer_credit_button";

// Registrar el componente del botón
patch(PaymentScreen.prototype, {
    get creditButtonComponent() {
        return CustomerCreditButton;
    }
});

// Extender componentes disponibles
Object.assign(PaymentScreen.components, {
    CustomerCreditButton,
});
