/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class CustomerCreditPopup extends AbstractAwaitablePopup {
    static template = "pos_customer_credit.CustomerCreditPopup";
    static props = {
        ...AbstractAwaitablePopup.props,
        creditInfo: Object,
    };

    setup() {
        super.setup();
        this.pos = usePos();
    }

    get creditInfo() {
        return this.props.creditInfo;
    }

    get balance() {
        return this.creditInfo.credit_balance || 0;
    }

    get balanceClass() {
        if (this.balance > 0) return 'text-danger';
        if (this.balance < 0) return 'text-success';
        return 'text-muted';
    }

    get balanceLabel() {
        if (this.balance > 0) return 'Debe';
        if (this.balance < 0) return 'A favor';
        return 'Sin deuda';
    }

    get movements() {
        return this.creditInfo.movements || [];
    }

    formatCurrency(amount) {
        return this.pos.env.utils.formatCurrency(amount);
    }

    formatDate(dateStr) {
        return dateStr;
    }

    getMovementClass(movement) {
        if (movement.amount > 0) return 'text-danger';
        if (movement.amount < 0) return 'text-success';
        return '';
    }

    getMovementIcon(type) {
        const icons = {
            'sale': 'fa-shopping-cart',
            'payment': 'fa-money',
            'product_add': 'fa-plus-circle',
            'product_remove': 'fa-minus-circle',
            'adjustment': 'fa-edit',
            'refund': 'fa-undo',
        };
        return icons[type] || 'fa-exchange';
    }

    async viewOrder(orderId) {
        if (!orderId) return;
        
        // Cerrar popup y abrir vista de orden en backend
        this.cancel();
        const url = `/web#id=${orderId}&model=pos.order&view_type=form`;
        window.open(url, '_blank');
    }

    async openBackendView() {
        const partnerId = this.creditInfo.partner_id;
        this.cancel();
        const url = `/web#id=${partnerId}&model=res.partner&view_type=form`;
        window.open(url, '_blank');
    }

    async registerPayment() {
        this.cancel();
        const partnerId = this.creditInfo.partner_id;
        const url = `/web#action=point_of_sale.action_pos_credit_movement&active_id=${partnerId}&model=res.partner`;
        window.open(url, '_blank');
    }
}
