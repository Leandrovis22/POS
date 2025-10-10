# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Campo principal: saldo de cuenta corriente
    credit_balance = fields.Monetary(
        string='Saldo Cuenta Corriente',
        currency_field='currency_id',
        compute='_compute_credit_balance',
        store=True,
        help='Saldo actual de cuenta corriente. Positivo = debe, Negativo = a favor'
    )
    
    # Relaciones
    credit_movement_ids = fields.One2many(
        'pos.credit.movement',
        'partner_id',
        string='Movimientos de Crédito'
    )
    
    pos_order_credit_ids = fields.One2many(
        'pos.order',
        'partner_id',
        string='Órdenes POS',
        domain=[('has_credit_payment', '=', True)]
    )
    
    # Campos computados adicionales
    total_credit_orders = fields.Integer(
        string='Total Órdenes a Crédito',
        compute='_compute_credit_stats'
    )
    
    pending_credit_amount = fields.Monetary(
        string='Deuda Pendiente',
        currency_field='currency_id',
        compute='_compute_credit_stats',
        help='Solo deuda positiva (sin incluir saldos a favor)'
    )

    @api.depends('credit_movement_ids.amount', 'credit_movement_ids.state')
    def _compute_credit_balance(self):
        """Calcula el saldo de CC sumando todos los movimientos confirmados"""
        for partner in self:
            movements = partner.credit_movement_ids.filtered(lambda m: m.state == 'confirmed')
            partner.credit_balance = sum(movements.mapped('amount'))
    
    @api.depends('pos_order_credit_ids', 'pos_order_credit_ids.credit_amount_due')
    def _compute_credit_stats(self):
        """Calcula estadísticas de crédito del cliente"""
        for partner in self:
            credit_orders = partner.pos_order_credit_ids.filtered(
                lambda o: o.state in ['paid', 'done', 'invoiced']
            )
            partner.total_credit_orders = len(credit_orders)
            partner.pending_credit_amount = max(partner.credit_balance, 0.0)
    
    def action_view_credit_movements(self):
        """Acción para ver todos los movimientos de crédito"""
        self.ensure_one()
        return {
            'name': f'Movimientos de CC - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'pos.credit.movement',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {
                'default_partner_id': self.id,
                'search_default_group_by_order': 1,
            }
        }
    
    def action_view_credit_orders(self):
        """Acción para ver todas las órdenes con crédito"""
        self.ensure_one()
        return {
            'name': f'Órdenes a Crédito - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'pos.order',
            'view_mode': 'list,form',
            'domain': [
                ('partner_id', '=', self.id),
                ('has_credit_payment', '=', True)
            ],
            'context': {'default_partner_id': self.id}
        }
    
    def action_register_payment(self):
        """Acción para registrar un nuevo pago"""
        self.ensure_one()
        return {
            'name': f'Registrar Pago - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'pos.credit.movement',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.id,
                'default_movement_type': 'payment',
                'default_amount': -abs(self.credit_balance) if self.credit_balance > 0 else 0.0,
            }
        }
    
    def get_credit_info_for_pos(self):
        """Retorna info de crédito para mostrar en POS"""
        self.ensure_one()
        
        # Últimos 10 movimientos
        recent_movements = self.credit_movement_ids.filtered(
            lambda m: m.state == 'confirmed'
        ).sorted('date', reverse=True)[:10]
        
        movements_data = [{
            'id': m.id,
            'date': m.date.strftime('%d/%m/%Y %H:%M'),
            'type': m.movement_type,
            'type_label': dict(m._fields['movement_type'].selection).get(m.movement_type),
            'amount': m.amount,
            'description': m.description or '',
            'order_id': m.order_id.id if m.order_id else False,
            'order_name': m.order_id.name if m.order_id else '',
        } for m in recent_movements]
        
        return {
            'partner_id': self.id,
            'partner_name': self.name,
            'credit_balance': self.credit_balance,
            'pending_amount': self.pending_credit_amount,
            'total_orders': self.total_credit_orders,
            'movements': movements_data,
        }
