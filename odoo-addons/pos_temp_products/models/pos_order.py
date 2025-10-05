# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    is_temp_line = fields.Boolean(string='Línea temporal POS', default=False, help='Marcador para líneas agregadas como productos temporales')


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _order_line_fields(self, line, session_id=None):
        """ Map lines from UI; allow custom name for temp lines. """
        # Call super to get default mapping
        res = super()._order_line_fields(line, session_id=session_id)
        # res is a dict of values for pos.order.line
        if line.get('is_temp_line'):
            res['is_temp_line'] = True
            temp_name = line.get('temp_name')
            if temp_name:
                # Force the description of the line to the provided temp_name
                res['name'] = temp_name
        return res
