/** @odoo-module */
import { PosGlobalState } from '@point_of_sale/app/store/pos_global_state';
import { patch } from '@web/core/utils/patch';

patch(PosGlobalState.prototype, 'pos_temp_products_config_fields', {
    async _loadPosModels() {
        // Before loading, push temp_product_id into config model fields
        const configModel = this.models?.find((m) => m.model === 'pos.config');
        if (configModel) {
            configModel.fields = configModel.fields || [];
            if (!configModel.fields.includes('temp_product_id')) {
                configModel.fields.push('temp_product_id');
            }
        }
        return await super._loadPosModels();
    },
});
