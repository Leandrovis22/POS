# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    pos_order_id = fields.Many2one(
        'pos.order',
        string='Orden POS',
        help='Orden POS asociada a esta factura'
    )
    
    is_outdated = fields.Boolean(
        string='Factura Desactualizada',
        compute='_compute_is_outdated',
        help='La orden POS ha sido modificada después de generar esta factura'
    )

    @api.depends('pos_order_id', 'pos_order_id.is_modified')
    def _compute_is_outdated(self):
        """Detecta si la factura está desactualizada"""
        for move in self:
            move.is_outdated = bool(
                move.pos_order_id and 
                move.pos_order_id.is_modified
            )
