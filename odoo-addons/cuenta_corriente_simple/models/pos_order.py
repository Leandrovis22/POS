from odoo import models, fields, api

class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    is_credit_sale = fields.Boolean(string='Venta a Crédito', default=False)
    
    @api.model
    def _process_order(self, order, existing_order):
        """Extender procesamiento para ventas a crédito"""
        order_id = super()._process_order(order, existing_order)
        
        if order_id:
            pos_order = self.browse(order_id)
            
            # Verificar si hay pagos con cuenta corriente
            for payment in order.get('statement_ids', []):
                payment_method = payment[2].get('payment_method_id')
                if payment_method:
                    method = self.env['pos.payment.method'].browse(payment_method)
                    if method.name and 'cuenta' in method.name.lower():
                        # Es un pago con cuenta corriente
                        pos_order.is_credit_sale = True
                        
                        # Crear movimiento en cuenta corriente
                        if pos_order.partner_id:
                            self.env['customer.account.move'].create({
                                'partner_id': pos_order.partner_id.id,
                                'date': pos_order.date_order,
                                'description': f'Venta POS {pos_order.name}',
                                'debit': pos_order.amount_total,
                                'pos_order_id': pos_order.id,
                                'reference': pos_order.name,
                                'state': 'posted'
                            })
                            # Actualizar saldo
                            pos_order.partner_id._compute_account_balance()
        
        return order_id
