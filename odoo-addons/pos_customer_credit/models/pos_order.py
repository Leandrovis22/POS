# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PosOrder(models.Model):
    _inherit = 'pos.order'

    # Campos de cuenta corriente
    has_credit_payment = fields.Boolean(
        string='Tiene Pago con CC',
        compute='_compute_credit_payment_info',
        store=True,
        help='Indica si esta orden tiene al menos un pago con cuenta corriente'
    )
    
    credit_amount = fields.Monetary(
        string='Monto en CC',
        currency_field='currency_id',
        compute='_compute_credit_payment_info',
        store=True,
        help='Monto total pagado con cuenta corriente en esta orden'
    )
    
    cash_amount = fields.Monetary(
        string='Monto en Efectivo',
        currency_field='currency_id',
        compute='_compute_credit_payment_info',
        store=True,
        help='Monto total pagado con efectivo en esta orden'
    )
    
    credit_amount_due = fields.Monetary(
        string='Deuda Actual de esta Orden',
        currency_field='currency_id',
        compute='_compute_credit_amount_due',
        store=True,
        help='Deuda pendiente de esta orden específica (considerando modificaciones y pagos)'
    )
    
    original_amount_total = fields.Monetary(
        string='Monto Original',
        currency_field='currency_id',
        help='Monto total original de la orden al momento de creación'
    )
    
    current_products_value = fields.Monetary(
        string='Valor Productos Actuales',
        currency_field='currency_id',
        compute='_compute_current_products_value',
        store=True,
        help='Valor actual de los productos en la orden (después de modificaciones)'
    )
    
    # Relaciones
    credit_movement_ids = fields.One2many(
        'pos.credit.movement',
        'order_id',
        string='Movimientos de Crédito'
    )
    
    modification_count = fields.Integer(
        string='Cantidad de Modificaciones',
        compute='_compute_modification_count'
    )
    
    is_modified = fields.Boolean(
        string='Orden Modificada',
        compute='_compute_is_modified',
        store=True,
        help='Indica si la orden ha sido modificada después de su creación'
    )
    
    # Estado de facturación
    invoice_outdated = fields.Boolean(
        string='Factura Desactualizada',
        compute='_compute_invoice_outdated',
        help='La factura está desactualizada respecto a la orden'
    )

    @api.depends('payment_ids', 'payment_ids.payment_method_id', 'payment_ids.amount')
    def _compute_credit_payment_info(self):
        """Calcula información sobre pagos con crédito"""
        for order in self:
            credit_payments = order.payment_ids.filtered(
                lambda p: p.payment_method_id.is_credit_payment
            )
            cash_payments = order.payment_ids.filtered(
                lambda p: not p.payment_method_id.is_credit_payment
            )
            
            order.has_credit_payment = bool(credit_payments)
            order.credit_amount = sum(credit_payments.mapped('amount'))
            order.cash_amount = sum(cash_payments.mapped('amount'))
    
    @api.depends('credit_movement_ids', 'credit_movement_ids.amount', 'credit_movement_ids.state')
    def _compute_credit_amount_due(self):
        """Calcula la deuda actual de esta orden"""
        for order in self:
            movements = order.credit_movement_ids.filtered(lambda m: m.state == 'confirmed')
            order.credit_amount_due = sum(movements.mapped('amount'))
    
    @api.depends('lines', 'lines.price_subtotal_incl', 'lines.qty')
    def _compute_current_products_value(self):
        """Calcula el valor actual de los productos en la orden"""
        for order in self:
            # Solo líneas con cantidad positiva (productos actuales)
            current_lines = order.lines.filtered(lambda l: l.qty > 0)
            order.current_products_value = sum(current_lines.mapped('price_subtotal_incl'))
    
    @api.depends('credit_movement_ids')
    def _compute_modification_count(self):
        """Cuenta las modificaciones de la orden"""
        for order in self:
            modifications = order.credit_movement_ids.filtered(
                lambda m: m.movement_type in ['product_add', 'product_remove']
            )
            order.modification_count = len(modifications)
    
    @api.depends('original_amount_total', 'current_products_value')
    def _compute_is_modified(self):
        """Determina si la orden ha sido modificada"""
        for order in self:
            if not order.original_amount_total:
                order.is_modified = False
            else:
                # Comparar con pequeña tolerancia por redondeos
                order.is_modified = abs(
                    order.original_amount_total - order.current_products_value
                ) > 0.01
    
    @api.depends('is_modified', 'account_move')
    def _compute_invoice_outdated(self):
        """Determina si la factura está desactualizada"""
        for order in self:
            order.invoice_outdated = bool(order.account_move and order.is_modified)

    @api.model_create_multi
    def create(self, vals_list):
        """Override para guardar el monto original"""
        orders = super().create(vals_list)
        for order in orders:
            if not order.original_amount_total:
                order.original_amount_total = order.amount_total
            # Crear movimiento inicial de crédito si aplica
            if order.has_credit_payment:
                order._create_initial_credit_movement()
        return orders
    
    def _create_initial_credit_movement(self):
        """Crea el movimiento de crédito inicial cuando se crea una orden con CC"""
        self.ensure_one()
        if self.credit_amount > 0:
            self.env['pos.credit.movement'].create({
                'partner_id': self.partner_id.id,
                'order_id': self.id,
                'movement_type': 'sale',
                'amount': self.credit_amount,
                'description': f'Venta inicial - {self.name}',
                'state': 'confirmed',
            })
    
    def action_modify_order(self):
        """Acción para modificar la orden (agregar/quitar productos)"""
        self.ensure_one()
        
        # Validar que se pueda modificar
        if self.state in ['cancel']:
            raise UserError(_('No se puede modificar una orden cancelada.'))
        
        if not self.has_credit_payment and self.cash_amount > 0:
            # Pago 100% efectivo: solo puede quitar productos
            return {
                'name': f'Modificar Orden {self.name} (Solo Quitar)',
                'type': 'ir.actions.act_window',
                'res_model': 'pos.order',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'current',
                'context': {
                    'cash_only_mode': True,
                    'can_only_remove': True,
                }
            }
        else:
            # Tiene CC: puede agregar y quitar
            return {
                'name': f'Modificar Orden {self.name}',
                'type': 'ir.actions.act_window',
                'res_model': 'pos.order',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'current',
            }
    
    def add_products_to_order(self, products_data):
        """
        Agrega productos a una orden existente
        products_data: [{'product_id': int, 'qty': float, 'price_unit': float}, ...]
        """
        self.ensure_one()
        
        # Validar que se pueda agregar productos
        if not self.has_credit_payment:
            raise UserError(_(
                'No se pueden agregar productos a una orden pagada 100% en efectivo. '
                'Debe crear una nueva venta.'
            ))
        
        total_added = 0.0
        lines_created = []
        
        for prod_data in products_data:
            product = self.env['product.product'].browse(prod_data['product_id'])
            qty = prod_data['qty']
            price_unit = prod_data.get('price_unit', product.lst_price)
            
            # Crear nueva línea
            line_vals = {
                'order_id': self.id,
                'product_id': product.id,
                'qty': qty,
                'price_unit': price_unit,
                'price_subtotal': qty * price_unit,
                'price_subtotal_incl': qty * price_unit,  # Simplificado, ajustar con impuestos si es necesario
            }
            
            line = self.env['pos.order.line'].create(line_vals)
            lines_created.append(line)
            total_added += line.price_subtotal_incl
            
            # Reducir inventario
            self._update_inventory_on_add(product, qty)
        
        # Crear movimiento de crédito por productos agregados
        if total_added > 0:
            # Calcular proporción de CC en la orden original
            if self.amount_paid > 0:
                credit_proportion = self.credit_amount / self.amount_paid
            else:
                credit_proportion = 1.0
            
            credit_increase = total_added * credit_proportion
            
            self.env['pos.credit.movement'].create({
                'partner_id': self.partner_id.id,
                'order_id': self.id,
                'movement_type': 'product_add',
                'amount': credit_increase,
                'description': f'Productos agregados - {self.name}',
                'state': 'confirmed',
            })
        
        return {
            'success': True,
            'lines_created': len(lines_created),
            'total_added': total_added,
        }
    
    def remove_products_from_order(self, line_ids_to_remove):
        """
        Quita productos de una orden existente
        line_ids_to_remove: [int, int, ...] IDs de pos.order.line
        """
        self.ensure_one()
        
        lines = self.env['pos.order.line'].browse(line_ids_to_remove)
        total_removed = 0.0
        
        for line in lines:
            if line.order_id.id != self.id:
                continue
            
            total_removed += line.price_subtotal_incl
            
            # Devolver al inventario
            self._update_inventory_on_remove(line.product_id, line.qty)
            
            # Marcar línea como removida (qty = 0 o negativa)
            line.write({'qty': 0})
        
        # Crear movimiento de crédito por productos removidos
        if total_removed > 0:
            if self.has_credit_payment:
                # Tiene CC: reduce deuda proporcionalmente
                if self.amount_paid > 0:
                    credit_proportion = self.credit_amount / self.amount_paid
                else:
                    credit_proportion = 1.0
                
                credit_decrease = total_removed * credit_proportion
            else:
                # 100% efectivo: genera crédito a favor
                credit_decrease = total_removed
            
            self.env['pos.credit.movement'].create({
                'partner_id': self.partner_id.id,
                'order_id': self.id,
                'movement_type': 'product_remove',
                'amount': -credit_decrease,  # Negativo para reducir deuda
                'description': f'Productos removidos - {self.name}',
                'state': 'confirmed',
            })
        
        return {
            'success': True,
            'lines_removed': len(lines),
            'total_removed': total_removed,
        }
    
    def _update_inventory_on_add(self, product, qty):
        """Reduce inventario cuando se agregan productos"""
        # Nota: implementación simplificada
        # En producción, usar stock.move o quants según necesites
        if product.type == 'product':
            # Aquí iría la lógica de reducción de inventario
            # Por ahora solo un placeholder
            pass
    
    def _update_inventory_on_remove(self, product, qty):
        """Aumenta inventario cuando se quitan productos"""
        # Nota: implementación simplificada
        if product.type == 'product':
            # Aquí iría la lógica de aumento de inventario
            pass
    
    def action_view_credit_movements(self):
        """Ver movimientos de crédito de esta orden"""
        self.ensure_one()
        return {
            'name': f'Movimientos CC - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'pos.credit.movement',
            'view_mode': 'tree,form',
            'domain': [('order_id', '=', self.id)],
            'context': {'default_order_id': self.id}
        }
    
    def action_print_order_with_balance(self):
        """Imprime PDF de la orden con saldo actual"""
        self.ensure_one()
        return self.env.ref('pos_customer_credit.action_report_pos_order_credit').report_action(self)
    
    def get_order_data_for_pdf(self):
        """Retorna datos de la orden para el PDF"""
        self.ensure_one()
        
        # Líneas actuales (con qty > 0)
        current_lines = self.lines.filtered(lambda l: l.qty > 0)
        
        lines_data = [{
            'product_name': line.product_id.display_name,
            'qty': line.qty,
            'price_unit': line.price_unit,
            'subtotal': line.price_subtotal_incl,
        } for line in current_lines]
        
        return {
            'order_name': self.name,
            'date': self.date_order,
            'partner_name': self.partner_id.name,
            'lines': lines_data,
            'current_total': self.current_products_value,
            'original_total': self.original_amount_total,
            'credit_amount': self.credit_amount,
            'cash_amount': self.cash_amount,
            'order_balance': self.credit_amount_due,
            'partner_balance': self.partner_id.credit_balance,
            'is_modified': self.is_modified,
        }
