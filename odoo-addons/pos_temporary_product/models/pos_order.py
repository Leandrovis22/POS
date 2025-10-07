# -*- coding: utf-8 -*-
from odoo import models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _get_invoice_lines_values(self, line_values, pos_order_line):
        """
        Override para usar full_product_name en las líneas de factura cuando esté disponible
        """
        res = super()._get_invoice_lines_values(line_values, pos_order_line)
        
        # Si la línea tiene full_product_name y es diferente al nombre del producto,
        # usar el nombre personalizado en la factura
        if pos_order_line.full_product_name and pos_order_line.full_product_name != pos_order_line.product_id.display_name:
            res['name'] = pos_order_line.full_product_name
        
        return res
