/** @odoo-module */
import { _t } from '@web/core/l10n/translation';
import { AbstractAwaitablePopup } from '@point_of_sale/app/utils/abstract_awaitable_popup/abstract_awaitable_popup';
import { registry } from '@web/core/registry';

console.log('[pos_temp_products] Loading temp_popup.js');

export class TempProductPopup extends AbstractAwaitablePopup {
    setup() {
        super.setup();
        console.log('[pos_temp_products] TempProductPopup setup()');
        this.state = {
            rows: [{ name: '', qty: 1, price: 0 }],
        };
    }

    addRow() {
        this.state.rows.push({ name: '', qty: 1, price: 0 });
        this.render();
    }

    removeRow(index) {
        this.state.rows.splice(index, 1);
        if (!this.state.rows.length) this.addRow();
        this.render();
    }

    onEnter(index) {
        if (index === this.state.rows.length - 1) {
            this.addRow();
        }
    }

    onInput(index, field, ev) {
        const val = ev.target.value;
        if (field === 'qty' || field === 'price') {
            const num = Number(val);
            this.state.rows[index][field] = isNaN(num) ? 0 : num;
        } else {
            this.state.rows[index][field] = val;
        }
        this.render();
    }

    confirm() {
        const rows = this.state.rows
            .map((r) => ({
                name: (r.name || '').trim(),
                qty: Number(r.qty) || 0,
                price: Number(r.price) || 0,
            }))
            .filter((r) => r.name && r.qty > 0 && r.price >= 0);
        this.props.close({ confirmed: true, payload: { rows } });
    }
}

TempProductPopup.template = 'pos_temp_products.TempProductPopup';
TempProductPopup.defaultProps = {};

registry.category('popups').add('TempProductPopup', TempProductPopup);
