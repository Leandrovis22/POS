# -*- coding: utf-8 -*-
from odoo import models, fields


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    is_credit_payment = fields.Boolean(
        string='Es Pago con Cuenta Corriente',
        default=False,
        help='Marca este método de pago como cuenta corriente'
    )
