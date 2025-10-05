# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    temp_product_id = fields.Many2one(
        'product.template',
        string='Producto temporal POS',
        help='Producto base (servicio) usado para las líneas temporales creadas desde el botón Agregar producto.',
    )

    @api.onchange('temp_product_id')
    def _onchange_temp_product_id(self):
        if self.temp_product_id and not self.temp_product_id.available_in_pos:
            self.temp_product_id.available_in_pos = True
