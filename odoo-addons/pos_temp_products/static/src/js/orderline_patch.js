/** @odoo-module */

import { PosOrderline } from '@point_of_sale/app/models/pos_order_line';
import { patch } from '@web/core/utils/patch';

const proto = PosOrderline.prototype;
const superExportJson = proto.export_as_JSON;
const superExportForPrinting = proto.export_for_printing;
const superSetFullProductName = proto.setFullProductName;
const superGetFullProductName = proto.getFullProductName;
const orderDisplayDescriptor = Object.getOwnPropertyDescriptor(proto, 'orderDisplayProductName');
const orderDisplayGetter = orderDisplayDescriptor?.get;

patch(proto, 'pos_temp_products_orderline_patch', {
    export_as_JSON() {
        const json = superExportJson.apply(this, arguments);
        json.is_temp_line = Boolean(this.is_temp_line);
        if (this.temp_name) {
            json.temp_name = this.temp_name;
        }
        return json;
    },

    export_for_printing() {
        const json = superExportForPrinting.apply(this, arguments);
        if (this.is_temp_line && this.temp_name) {
            json.product_name = this.temp_name;
            json.full_product_name = this.temp_name;
            json.name = this.temp_name;
        }
        return json;
    },

    setFullProductName() {
        superSetFullProductName.apply(this, arguments);
        if (this.is_temp_line && this.temp_name) {
            this.full_product_name = this.temp_name;
        }
    },

    getFullProductName() {
        if (this.is_temp_line && this.temp_name) {
            return this.temp_name;
        }
        return superGetFullProductName.apply(this, arguments);
    },

    get orderDisplayProductName() {
        if (this.is_temp_line && this.temp_name) {
            return {
                name: this.temp_name,
                attributeString: '',
            };
        }
        if (orderDisplayGetter) {
            return orderDisplayGetter.call(this);
        }
        return {
            name: this.product_id?.name,
            attributeString: '',
        };
    },
});
