from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    def write(self, vals):
        """Detectar cambios en facturas de órdenes POS a crédito y ajustar cuenta corriente"""
        result = super().write(vals)
        
        # Si cambian las líneas de la factura
        if 'invoice_line_ids' in vals or 'line_ids' in vals:
            for move in self:
                # Verificar si esta factura viene de una orden POS
                pos_order = self.env['pos.order'].search([
                    ('account_move', '=', move.id)
                ], limit=1)
                
                if pos_order and pos_order.is_credit_sale and pos_order.partner_id:
                    # Buscar el movimiento original de cuenta corriente
                    cc_move = self.env['customer.account.move'].search([
                        ('pos_order_id', '=', pos_order.id),
                        ('state', '=', 'posted'),
                        ('description', 'like', f'Venta POS {pos_order.name}')
                    ], limit=1, order='id asc')
                    
                    if cc_move:
                        old_amount = cc_move.debit
                        new_amount = move.amount_total
                        
                        if old_amount != new_amount:
                            difference = new_amount - old_amount
                            
                            # Crear movimiento de ajuste
                            self.env['customer.account.move'].create({
                                'partner_id': pos_order.partner_id.id,
                                'date': fields.Datetime.now(),
                                'description': f'Ajuste por modificación de factura {move.name} (Orden: {pos_order.name})',
                                'debit': difference if difference > 0 else 0,
                                'credit': abs(difference) if difference < 0 else 0,
                                'pos_order_id': pos_order.id,
                                'reference': f'{pos_order.name}-FADJ',
                                'state': 'posted'
                            })
                            pos_order.partner_id._compute_account_balance()
                            _logger.info(f"Ajuste de cuenta corriente creado por modificación de factura {move.name}: {difference}")
        
        return result
    
    def button_draft(self):
        """Al pasar factura a borrador, cancelar ajustes relacionados"""
        for move in self:
            pos_order = self.env['pos.order'].search([
                ('account_move', '=', move.id)
            ], limit=1)
            
            if pos_order and pos_order.is_credit_sale:
                # Buscar ajustes relacionados con esta factura
                adjustments = self.env['customer.account.move'].search([
                    ('reference', 'like', f'{pos_order.name}-FADJ'),
                    ('state', '=', 'posted')
                ])
                
                if adjustments:
                    adjustments.write({'state': 'cancelled'})
                    pos_order.partner_id._compute_account_balance()
                    _logger.info(f"Ajustes cancelados para factura {move.name}")
        
        return super().button_draft()
    
    def button_cancel(self):
        """Al cancelar factura de orden POS a crédito, cancelar movimiento de CC"""
        for move in self:
            pos_order = self.env['pos.order'].search([
                ('account_move', '=', move.id)
            ], limit=1)
            
            if pos_order and pos_order.is_credit_sale and pos_order.partner_id:
                # Cancelar todos los movimientos relacionados
                cc_moves = self.env['customer.account.move'].search([
                    ('pos_order_id', '=', pos_order.id),
                    ('state', '=', 'posted')
                ])
                
                if cc_moves:
                    cc_moves.write({'state': 'cancelled'})
                    pos_order.partner_id._compute_account_balance()
                    _logger.info(f"Movimientos de CC cancelados por cancelación de factura {move.name}")
        
        return super().button_cancel()
