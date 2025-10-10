# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PosCreditMovement(models.Model):
    _name = 'pos.credit.movement'
    _description = 'Movimiento de Cuenta Corriente'
    _order = 'date desc, id desc'
    _rec_name = 'description'

    # Información básica
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        ondelete='restrict',
        index=True
    )
    
    order_id = fields.Many2one(
        'pos.order',
        string='Orden POS',
        ondelete='cascade',
        index=True
    )
    
    date = fields.Datetime(
        string='Fecha',
        default=fields.Datetime.now,
        required=True
    )
    
    movement_type = fields.Selection([
        ('sale', 'Venta a Crédito'),
        ('payment', 'Pago Recibido'),
        ('product_add', 'Productos Agregados'),
        ('product_remove', 'Productos Removidos'),
        ('adjustment', 'Ajuste Manual'),
        ('refund', 'Devolución'),
    ], string='Tipo de Movimiento', required=True, default='sale')
    
    amount = fields.Monetary(
        string='Monto',
        currency_field='currency_id',
        required=True,
        help='Positivo = aumenta deuda, Negativo = reduce deuda'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id
    )
    
    description = fields.Char(
        string='Descripción',
        required=True
    )
    
    notes = fields.Text(
        string='Notas'
    )
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('cancelled', 'Cancelado'),
    ], string='Estado', default='draft', required=True)
    
    # Campos de auditoría
    user_id = fields.Many2one(
        'res.users',
        string='Usuario',
        default=lambda self: self.env.user,
        readonly=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        required=True
    )

    @api.constrains('amount')
    def _check_amount(self):
        """Validar que el monto no sea cero"""
        for movement in self:
            if movement.amount == 0:
                raise ValidationError(_('El monto no puede ser cero.'))
    
    def action_confirm(self):
        """Confirma el movimiento"""
        for movement in self:
            if movement.state == 'confirmed':
                continue
            movement.write({'state': 'confirmed'})
        return True
    
    def action_cancel(self):
        """Cancela el movimiento"""
        for movement in self:
            if movement.state == 'cancelled':
                continue
            movement.write({'state': 'cancelled'})
        return True
    
    def action_set_to_draft(self):
        """Vuelve a borrador"""
        for movement in self:
            movement.write({'state': 'draft'})
        return True
    
    @api.model_create_multi
    def create(self, vals_list):
        """Auto-confirmar movimientos de órdenes POS"""
        movements = super().create(vals_list)
        for movement in movements:
            # Auto-confirmar si viene de una orden POS
            if movement.order_id and movement.state == 'draft':
                movement.state = 'confirmed'
        return movements
    
    def name_get(self):
        """Nombre personalizado para el movimiento"""
        result = []
        for movement in self:
            name = f"{movement.date.strftime('%d/%m/%Y')} - {movement.description}"
            if movement.amount > 0:
                name += f" (+{movement.amount:.2f})"
            else:
                name += f" ({movement.amount:.2f})"
            result.append((movement.id, name))
        return result
