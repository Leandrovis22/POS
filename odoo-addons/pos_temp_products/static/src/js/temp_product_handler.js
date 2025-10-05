/** @odoo-module */

import { _t } from '@web/core/l10n/translation';
import { TempProductPopup } from './temp_popup';
import { sprintf } from '@web/core/utils/strings';

function getTempProductTemplate(pos) {
    const config = pos?.config;
    const tempField = config?.temp_product_id;

    if (!tempField) {
        return null;
    }

    if (typeof tempField === 'object' && 'id' in tempField) {
        return tempField;
    }

    if (Array.isArray(tempField)) {
        const templateId = tempField[0];
        return pos.models?.['product.template']?.get?.(templateId) || null;
    }

    if (typeof tempField === 'number') {
        return pos.models?.['product.template']?.get?.(tempField) || null;
    }

    return null;
}

function ensureTempProductLoaded(pos, template) {
    if (!template) {
        return null;
    }

    const variant = template.product_variant_ids?.[0];
    if (variant) {
        return variant;
    }

    const productModel = pos.models?.['product.product'];
    if (productModel) {
        const existing = productModel
            .getAll?.()
            ?.find((product) => product.product_tmpl_id?.id === template.id);
        if (existing) {
            return existing;
        }
    }

    return null;
}

export async function openTempProductDialog({ pos, popup, notification }) {
    if (!pos) {
        console.warn('[pos_temp_products] POS service unavailable');
        return false;
    }

    const order = pos.getOrder?.() || pos.addNewOrder?.();
    if (!order) {
        notification?.add?.(_t('No hay una orden activa para agregar productos.'), {
            type: 'warning',
        });
        return false;
    }

    if (!popup) {
        console.warn('[pos_temp_products] Popup service unavailable');
        return false;
    }

    const { confirmed, payload } = await popup.add(TempProductPopup, {
        title: _t('Agregar productos temporales'),
    });

    const rows = payload?.rows
        ?.map((row) => ({
            ...row,
            name: row.name ? row.name.trim() : '',
        }))
        ?.filter((row) => row.name && row.qty > 0 && row.price >= 0) || [];

    if (!confirmed || !rows.length) {
        if (!rows.length) {
            notification?.add?.(_t('Agrega al menos un producto válido.'), {
                type: 'warning',
            });
        }
        return false;
    }

    const template = getTempProductTemplate(pos);
    if (!template) {
        notification?.add?.(
            _t('Configura un producto temporal en el Punto de Venta para usar esta función.'),
            {
                type: 'danger',
            }
        );
        return false;
    }

    const tempProduct = ensureTempProductLoaded(pos, template);
    if (!tempProduct) {
        notification?.add?.(
            _t('No se encontró el producto temporal en la sesión del POS. Actualiza los datos.'),
            {
                type: 'danger',
            }
        );
        return false;
    }

    let added = 0;

    for (const row of rows) {
        try {
            const line = await pos.addLineToCurrentOrder({
                product_tmpl_id: tempProduct.product_tmpl_id || template,
                qty: row.qty,
                price_unit: row.price,
            });

            if (!line) {
                continue;
            }

            line.price_type = 'manual';
            line.setUnitPrice(row.price);
            line.setQuantity(row.qty, true);
            line.is_temp_line = true;
            line.temp_name = row.name;
            line.setFullProductName();
            added++;
        } catch (error) {
            console.error('[pos_temp_products] Error adding temp product line', error);
        }
    }

    if (!added) {
        notification?.add?.(
            _t('No se pudieron agregar productos temporales. Revisa la consola para más detalles.'),
            {
                type: 'danger',
            }
        );
        return false;
    }

    notification?.add?.(
        sprintf(_t('%s productos temporales agregados a la orden.'), added),
        {
            type: 'success',
        }
    );

    return true;
}
