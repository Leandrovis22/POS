/** @odoo-module */
import { Orderline } from '@point_of_sale/app/store/models';
import { patch } from '@web/core/utils/patch';

patch(Orderline.prototype, 'pos_temp_products_orderline_patch', {
    export_as_JSON() {
        const json = Orderline.prototype.export_as_JSON.call(this);
        json.is_temp_line = this.is_temp_line || false;
        if (this.temp_name) {
            json.temp_name = this.temp_name;
        }
        return json;
    },

    export_for_printing() {
        const json = Orderline.prototype.export_for_printing.call(this);
        if (this.is_temp_line && this.temp_name) {
            json.product_name = this.temp_name;
            json.full_product_name = this.temp_name;
            json.name = this.temp_name;
        }
        return json;
    },
});
