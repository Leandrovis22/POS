# -*- coding: utf-8 -*-
from odoo import models, api


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override para preservar full_product_name cuando viene del frontend.
        """
        lines = super().create(vals_list)
        
        # Restaurar full_product_name si fue enviado en vals
        for line, vals in zip(lines, vals_list):
            if 'full_product_name' in vals and vals.get('full_product_name'):
                if line.full_product_name != vals['full_product_name']:
                    line.full_product_name = vals['full_product_name']
        
        return lines
