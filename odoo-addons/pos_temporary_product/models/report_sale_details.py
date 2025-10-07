# -*- coding: utf-8 -*-
from odoo import api, models, _


class ReportPoint_Of_SaleReport_Saledetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_ids=False, session_ids=False, **kwargs):
        """
        Override para usar full_product_name en los reportes cuando esté disponible
        """
        result = super().get_sale_details(date_start, date_stop, config_ids, session_ids, **kwargs)
        
        # Obtener las órdenes del periodo para poder acceder a full_product_name
        domain = self._get_domain(date_start, date_stop, config_ids, session_ids, **kwargs)
        orders = self.env['pos.order'].search(domain)
        
        # Crear un mapa de product_id -> full_product_name para productos temporales
        temp_product_names = {}
        for order in orders:
            for line in order.lines:
                if line.full_product_name and line.full_product_name != line.product_id.display_name:
                    # Usar una clave única por línea para productos temporales con nombres diferentes
                    key = (line.product_id.id, line.price_unit, line.discount, line.full_product_name)
                    temp_product_names[key] = line.full_product_name
        
        # Modificar los nombres de productos en la lista de productos vendidos
        for category_dict in result.get('products', []):
            new_products = []
            for product in category_dict.get('products', []):
                # Buscar si hay un nombre personalizado para este producto
                key = (product['product_id'], product['price_unit'], product['discount'], None)
                
                # Buscar todas las claves que coincidan
                matching_names = [v for k, v in temp_product_names.items() 
                                if k[0] == product['product_id'] and k[1] == product['price_unit'] and k[2] == product['discount']]
                
                if matching_names:
                    # Si hay nombres personalizados, crear un producto separado por cada nombre único
                    product_obj = self.env['product.product'].browse(product['product_id'])
                    if product_obj.default_code == 'TEMP_POS':
                        # Para productos temporales, dividir por cada nombre personalizado
                        grouped_by_name = {}
                        for order in orders:
                            for line in order.lines:
                                if (line.product_id.id == product['product_id'] and 
                                    line.price_unit == product['price_unit'] and 
                                    line.discount == product['discount']):
                                    
                                    name = line.full_product_name if line.full_product_name else product['product_name']
                                    if name not in grouped_by_name:
                                        grouped_by_name[name] = {
                                            'product_id': product['product_id'],
                                            'product_name': name,
                                            'barcode': product['barcode'],
                                            'quantity': 0,
                                            'price_unit': product['price_unit'],
                                            'discount': product['discount'],
                                            'uom': product['uom'],
                                            'total_paid': 0,
                                            'base_amount': 0,
                                            'combo_products_label': product.get('combo_products_label', ''),
                                        }
                                    grouped_by_name[name]['quantity'] += abs(line.qty)
                                    grouped_by_name[name]['total_paid'] += self._get_product_total_amount(line)
                                    grouped_by_name[name]['base_amount'] += line.price_subtotal
                        
                        new_products.extend(grouped_by_name.values())
                    else:
                        new_products.append(product)
                else:
                    new_products.append(product)
            
            category_dict['products'] = sorted(new_products, key=lambda l: l['product_name'])
        
        # Lo mismo para refund_products
        for category_dict in result.get('refund_products', []):
            new_products = []
            for product in category_dict.get('products', []):
                matching_names = [v for k, v in temp_product_names.items() 
                                if k[0] == product['product_id'] and k[1] == product['price_unit'] and k[2] == product['discount']]
                
                if matching_names:
                    product_obj = self.env['product.product'].browse(product['product_id'])
                    if product_obj.default_code == 'TEMP_POS':
                        grouped_by_name = {}
                        for order in orders:
                            for line in order.lines:
                                if (line.product_id.id == product['product_id'] and 
                                    line.price_unit == product['price_unit'] and 
                                    line.discount == product['discount']):
                                    
                                    name = line.full_product_name if line.full_product_name else product['product_name']
                                    if name not in grouped_by_name:
                                        grouped_by_name[name] = {
                                            'product_id': product['product_id'],
                                            'product_name': name,
                                            'barcode': product['barcode'],
                                            'quantity': 0,
                                            'price_unit': product['price_unit'],
                                            'discount': product['discount'],
                                            'uom': product['uom'],
                                            'total_paid': 0,
                                            'base_amount': 0,
                                            'combo_products_label': product.get('combo_products_label', ''),
                                        }
                                    grouped_by_name[name]['quantity'] += abs(line.qty)
                                    grouped_by_name[name]['total_paid'] += self._get_product_total_amount(line)
                                    grouped_by_name[name]['base_amount'] += line.price_subtotal
                        
                        new_products.extend(grouped_by_name.values())
                    else:
                        new_products.append(product)
                else:
                    new_products.append(product)
            
            category_dict['products'] = sorted(new_products, key=lambda l: l['product_name'])
        
        return result

