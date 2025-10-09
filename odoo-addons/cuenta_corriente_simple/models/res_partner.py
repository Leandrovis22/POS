from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    account_balance = fields.Monetary(string='Saldo Cuenta Corriente', 
                                     compute='_compute_account_balance', 
                                     store=True,
                                     currency_field='currency_id')
    account_move_ids = fields.One2many('customer.account.move', 'partner_id', 
                                      string='Movimientos de Cuenta')
    account_credit_limit = fields.Monetary(string='Límite de Crédito CC', 
                                  currency_field='currency_id',
                                  default=0.0,
                                  help='Límite de crédito para cuenta corriente. Dejar en 0 para crédito ilimitado.')
    
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
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }
    
    def action_register_payment(self):
        """Abrir wizard para registrar pago"""
        # Buscar la vista simplificada por nombre
        popup_view = self.env['ir.ui.view'].search([
            ('name', '=', 'customer.payment.form.popup'),
            ('model', '=', 'customer.payment')
        ], limit=1)
        
        action = {
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
        
        if popup_view:
            action['view_id'] = popup_view.id
            
        return action
