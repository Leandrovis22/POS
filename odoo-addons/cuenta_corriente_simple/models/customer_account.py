from odoo import models, fields, api
from datetime import datetime

class CustomerAccountMove(models.Model):
    _name = 'customer.account.move'
    _description = 'Movimiento de Cuenta Corriente'
    _order = 'date desc, id desc'
    
    partner_id = fields.Many2one('res.partner', string='Cliente', required=True)
    date = fields.Datetime(string='Fecha', default=fields.Datetime.now, required=True)
    description = fields.Char(string='Descripción', required=True)
    debit = fields.Monetary(string='Debe (Compras)', currency_field='currency_id')
    credit = fields.Monetary(string='Haber (Pagos)', currency_field='currency_id')
    balance = fields.Monetary(string='Saldo', currency_field='currency_id', 
                             compute='_compute_balance', store=False)
    currency_id = fields.Many2one('res.currency', string='Moneda',
                                 default=lambda self: self.env.company.currency_id)
    pos_order_id = fields.Many2one('pos.order', string='Orden POS')
    sale_order_id = fields.Many2one('sale.order', string='Orden de Venta')
    reference = fields.Char(string='Referencia')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('posted', 'Confirmado'),
        ('cancelled', 'Cancelado')
    ], default='posted', string='Estado')
    
    @api.depends('debit', 'credit', 'partner_id', 'date', 'state')
    def _compute_balance(self):
        """Calcular saldo acumulado para cada movimiento"""
        # Agrupar por partner para optimizar
        partners = self.mapped('partner_id')
        
        for partner in partners:
            # Obtener TODOS los movimientos del partner (incluyendo los del recordset actual)
            partner_moves = self.filtered(lambda m: m.partner_id == partner)
            
            # Obtener movimientos adicionales de la BD que no están en el recordset
            existing_moves = self.search([
                ('partner_id', '=', partner.id),
                ('state', '=', 'posted'),
                ('id', 'not in', partner_moves.ids)
            ])
            
            # Combinar todos los movimientos
            all_moves = (partner_moves | existing_moves).filtered(lambda m: m.state == 'posted')
            
            # Ordenar por fecha y ID de forma ascendente (cronológico)
            sorted_moves = all_moves.sorted(lambda m: (m.date, m.id))
            
            # Calcular saldo acumulado
            accumulated_balance = 0
            for move in sorted_moves:
                accumulated_balance += move.debit - move.credit
                # Asignar el saldo a este movimiento
                move.balance = accumulated_balance
        
        # Para movimientos en borrador, solo mostrar su efecto
        for record in self.filtered(lambda m: m.state != 'posted'):
            record.balance = record.debit - record.credit

class CustomerPayment(models.Model):
    _name = 'customer.payment'
    _description = 'Pago de Cliente'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Número', required=True, default='Nuevo')
    partner_id = fields.Many2one('res.partner', string='Cliente', required=True, tracking=True)
    amount = fields.Monetary(string='Monto', required=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Moneda',
                                 default=lambda self: self.env.company.currency_id)
    date = fields.Datetime(string='Fecha', default=fields.Datetime.now, required=True, tracking=True)
    payment_method = fields.Selection([
        ('cash', 'Efectivo'),
        ('bank', 'Transferencia'),
        ('check', 'Cheque'),
        ('other', 'Otro')
    ], string='Método de Pago', default='cash', required=True)
    memo = fields.Char(string='Memo')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('posted', 'Confirmado'),
        ('cancelled', 'Cancelado')
    ], default='draft', string='Estado', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('customer.payment') or 'PAGO/0001'
        return super().create(vals_list)
    
    def action_post(self):
        """Confirmar el pago y crear movimiento en cuenta corriente"""
        for payment in self:
            # Crear movimiento en cuenta corriente
            self.env['customer.account.move'].create({
                'partner_id': payment.partner_id.id,
                'date': payment.date,
                'description': f'Pago {payment.name}',
                'credit': payment.amount,
                'reference': payment.name,
                'state': 'posted'
            })
            payment.state = 'posted'
            # Actualizar saldo del cliente
            payment.partner_id._compute_account_balance()
    
    def action_cancel(self):
        """Cancelar el pago"""
        for payment in self:
            # Cancelar movimiento relacionado
            move = self.env['customer.account.move'].search([
                ('reference', '=', payment.name),
                ('partner_id', '=', payment.partner_id.id)
            ])
            move.state = 'cancelled'
            payment.state = 'cancelled'
            payment.partner_id._compute_account_balance()
