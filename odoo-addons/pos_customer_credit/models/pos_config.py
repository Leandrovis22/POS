# -*- coding: utf-8 -*-
from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_customer_credit = fields.Boolean(
        string='Habilitar Cuenta Corriente',
        default=True,
        help='Permite el uso de cuenta corriente en este POS'
    )
    
    credit_payment_method_id = fields.Many2one(
        'pos.payment.method',
        string='Método de Pago CC',
        domain=[('is_credit_payment', '=', True)],
        help='Método de pago predeterminado para cuenta corriente'
    )
    
    require_customer_for_credit = fields.Boolean(
        string='Requiere Cliente para CC',
        default=True,
        help='Requiere seleccionar cliente antes de usar cuenta corriente'
    )
