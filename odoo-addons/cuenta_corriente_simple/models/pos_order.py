from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    is_credit_sale = fields.Boolean(string='Venta a Crédito', default=False)
    
    def write(self, vals):
        """Crear movimiento de ajuste si cambia el monto de una orden a crédito"""
        result = super().write(vals)
        
        # Si cambian las líneas de una orden a crédito confirmada
        if 'lines' in vals:
            for order in self:
                if order.is_credit_sale and order.partner_id and order.state in ['paid', 'done', 'invoiced']:
                    # Buscar el movimiento original
                    move = self.env['customer.account.move'].search([
                        ('pos_order_id', '=', order.id),
                        ('state', '=', 'posted'),
                        ('description', 'like', f'Venta POS {order.name}')
                    ], limit=1)
                    
                    if move and move.debit != order.amount_total:
                        # Calcular la diferencia
                        difference = order.amount_total - move.debit
                        
                        # Crear un movimiento de ajuste (no modificar el original para mantener auditoría)
                        self.env['customer.account.move'].create({
                            'partner_id': order.partner_id.id,
                            'date': fields.Datetime.now(),
                            'description': f'Ajuste por modificación de {order.name} (Original: {move.debit}, Nuevo: {order.amount_total})',
                            'debit': difference if difference > 0 else 0,
                            'credit': abs(difference) if difference < 0 else 0,
                            'pos_order_id': order.id,
                            'reference': f'{order.name}-ADJ',
                            'state': 'posted'
                        })
                        order.partner_id._compute_account_balance()
                        _logger.info(f"Movimiento de ajuste creado para {order.name}: diferencia de {difference}")
        
        return result
    
    def action_pos_order_cancel(self):
        """Cancelar movimientos de cuenta corriente al cancelar la orden"""
        for order in self:
            if order.is_credit_sale and order.partner_id:
                # Buscar y cancelar movimientos relacionados
                moves = self.env['customer.account.move'].search([
                    ('pos_order_id', '=', order.id),
                    ('state', '=', 'posted')
                ])
                if moves:
                    moves.write({'state': 'cancelled'})
                    order.partner_id._compute_account_balance()
                    _logger.info(f"Movimientos de cuenta corriente cancelados para orden {order.name}")
        
        return super().action_pos_order_cancel()
    
    def refund(self):
        """Crear movimiento de crédito al hacer reembolso"""
        result = super().refund()
        
        # Si la orden original era a crédito, crear movimiento inverso
        for order in self:
            if order.is_credit_sale and order.partner_id:
                # Buscar la orden de reembolso creada
                refund_orders = self.search([
                    ('name', 'like', f'{order.name}%'),
                    ('id', '!=', order.id),
                    ('amount_total', '<', 0)
                ], limit=1, order='id desc')
                
                if refund_orders:
                    refund_order = refund_orders[0]
                    # Crear movimiento de crédito (reversa)
                    self.env['customer.account.move'].create({
                        'partner_id': order.partner_id.id,
                        'date': fields.Datetime.now(),
                        'description': f'Devolución {refund_order.name} (ref: {order.name})',
                        'credit': abs(refund_order.amount_total),
                        'pos_order_id': refund_order.id,
                        'reference': refund_order.name,
                        'state': 'posted'
                    })
                    order.partner_id._compute_account_balance()
                    _logger.info(f"Movimiento de devolución creado para {refund_order.name}")
        
        return result
    
    @api.model
    def _process_order(self, order, existing_order):
        """Extender procesamiento para ventas a crédito"""
        _logger.info("=== CUENTA CORRIENTE: Procesando orden ===")
        _logger.info(f"payment_ids: {order.get('payment_ids', [])}")
        
        # Verificar si hay pagos con cuenta corriente ANTES de procesar
        has_credit_payment = False
        for payment in order.get('payment_ids', []):
            _logger.info(f"Payment completo: {payment}")
            payment_data = payment[2] if len(payment) > 2 else {}
            payment_method_id = payment_data.get('payment_method_id')
            _logger.info(f"Método de pago ID: {payment_method_id}")
            
            if payment_method_id:
                method = self.env['pos.payment.method'].browse(payment_method_id)
                _logger.info(f"Nombre del método: {method.name}")
                
                if method.name and 'cuenta' in method.name.lower():
                    has_credit_payment = True
                    _logger.info("¡Pago con Cuenta Corriente detectado!")
                    
                    # Validar que haya un cliente
                    partner_id = order.get('partner_id')
                    _logger.info(f"Partner ID: {partner_id}")
                    
                    if not partner_id:
                        raise UserError(
                            'No se puede procesar un pago con Cuenta Corriente sin seleccionar un cliente. '
                            'Por favor, seleccione un cliente antes de continuar.'
                        )
                    
                    # Validar que no sea consumidor final anónimo
                    partner = self.env['res.partner'].browse(partner_id)
                    if partner and (not partner.name or 'consumidor final' in partner.name.lower() or 'anónimo' in partner.name.lower() or 'anonimo' in partner.name.lower()):
                        raise UserError(
                            'No se puede procesar un pago con Cuenta Corriente para consumidores finales anónimos. '
                            'Por favor, seleccione un cliente registrado o use otro método de pago.'
                        )
                    break
        
        # Procesar la orden normalmente
        order_id = super()._process_order(order, existing_order)
        _logger.info(f"Orden procesada ID: {order_id}, tiene pago con crédito: {has_credit_payment}")
        
        # Si hay pago con cuenta corriente, crear movimiento
        if order_id and has_credit_payment:
            pos_order = self.browse(order_id)
            pos_order.is_credit_sale = True
            
            # Crear movimiento en cuenta corriente solo si hay cliente
            if pos_order.partner_id:
                _logger.info(f"Creando movimiento para partner {pos_order.partner_id.name}, monto: {pos_order.amount_total}")
                
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
                
                _logger.info("¡Movimiento de cuenta corriente creado!")
        
        return order_id
