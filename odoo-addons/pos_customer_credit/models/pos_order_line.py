# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    is_removed = fields.Boolean(
        string='Producto Removido',
        compute='_compute_is_removed',
        store=True,
        help='Indica si este producto fue removido de la orden'
    )
    
    original_qty = fields.Float(
        string='Cantidad Original',
        help='Cantidad original antes de modificaciones'
    )

    @api.depends('qty')
    def _compute_is_removed(self):
        """Marca líneas como removidas si qty <= 0"""
        for line in self:
            line.is_removed = line.qty <= 0

    @api.model_create_multi
    def create(self, vals_list):
        """Guardar cantidad original"""
        lines = super().create(vals_list)
        for line in lines:
            if not line.original_qty:
                line.original_qty = line.qty
        return lines
