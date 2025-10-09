from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    account_balance = fields.Monetary(string='Saldo Cuenta Corriente', 
                                     compute='_compute_account_balance', 
                                     store=True,
                                     currency_field='currency_id')
    account_move_ids = fields.One2many('customer.account.move', 'partner_id', 
                                      string='Movimientos de Cuenta')
    credit_limit = fields.Monetary(string='Límite de Crédito', 
                                  currency_field='currency_id',
                                  default=0.0)
    has_credit = fields.Boolean(string='Tiene Crédito', default=False)
    
    @api.depends('account_move_ids', 'account_move_ids.debit', 'account_move_ids.credit', 'account_move_ids.state')
    def _compute_account_balance(self):
        for partner in self:
            moves = partner.account_move_ids.filtered(lambda m: m.state == 'posted')
            total_debit = sum(moves.mapped('debit'))
            total_credit = sum(moves.mapped('credit'))
            partner.account_balance = total_debit - total_credit
    
    def action_view_account_statement(self):
        """Ver estado de cuenta del cliente"""
        return {
            'name': f'Estado de Cuenta - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'customer.account.move',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }
    
    def action_register_payment(self):
        """Abrir wizard para registrar pago"""
        return {
            'name': 'Registrar Pago',
            'type': 'ir.actions.act_window',
            'res_model': 'customer.payment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.id,
                'default_amount': max(0, self.account_balance)
            }
        }
