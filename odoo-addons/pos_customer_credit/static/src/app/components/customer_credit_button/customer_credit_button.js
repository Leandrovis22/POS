/** @odoo-module */

import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";

export class CustomerCreditButton extends Component {
    static template = "pos_customer_credit.CustomerCreditButton";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }

    get currentCustomer() {
        return this.pos.get_order()?.get_partner();
    }

    get isVisible() {
        return this.pos.config.enable_customer_credit && this.currentCustomer;
    }

    get creditBalance() {
        if (!this.currentCustomer) return 0;
        return this.currentCustomer.credit_balance || 0;
    }

    get balanceClass() {
        if (this.creditBalance > 0) return 'text-danger';
        if (this.creditBalance < 0) return 'text-success';
        return '';
    }

    get balanceLabel() {
        if (this.creditBalance > 0) return 'Debe';
        if (this.creditBalance < 0) return 'A favor';
        return 'Sin deuda';
    }

    async onClick() {
        if (!this.currentCustomer) {
            await this.popup.add("ErrorPopup", {
                title: "Sin Cliente Seleccionado",
                body: "Debe seleccionar un cliente para ver su cuenta corriente.",
            });
            return;
        }

        // Cargar información actualizada del cliente
        const creditInfo = await this.loadCustomerCreditInfo();
        
        if (creditInfo) {
            await this.popup.add("CustomerCreditPopup", {
                title: `Cuenta Corriente - ${this.currentCustomer.name}`,
                creditInfo: creditInfo,
            });
        }
    }

    async loadCustomerCreditInfo() {
        try {
            const result = await this.pos.data.call(
                'res.partner',
                'get_credit_info_for_pos',
                [this.currentCustomer.id]
            );
            
            // Actualizar saldo en el cliente local
            if (result) {
                this.currentCustomer.credit_balance = result.credit_balance;
            }
            
            return result;
        } catch (error) {
            console.error("Error loading customer credit info:", error);
            await this.popup.add("ErrorPopup", {
                title: "Error",
                body: "No se pudo cargar la información de cuenta corriente.",
            });
            return null;
        }
    }

    async openBackendView() {
        // Abrir vista del backend para control completo
        const url = `/web#id=${this.currentCustomer.id}&model=res.partner&view_type=form`;
        window.open(url, '_blank');
    }
}
