# -*- coding: utf-8 -*-
from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override para preservar full_product_name cuando viene del frontend.
        """
        _logger.info("=" * 80)
        _logger.info("POS ORDER LINE CREATE - vals_list:")
        for vals in vals_list:
            _logger.info(f"  - product_id: {vals.get('product_id')}")
            _logger.info(f"  - full_product_name en vals: {vals.get('full_product_name')}")
            _logger.info(f"  - qty: {vals.get('qty')}, price_unit: {vals.get('price_unit')}")
        
        lines = super().create(vals_list)
        
        _logger.info("Después de super().create():")
        for line in lines:
            _logger.info(f"  - Line {line.id}: full_product_name = '{line.full_product_name}'")
        
        # Restaurar full_product_name si fue enviado en vals
        for line, vals in zip(lines, vals_list):
            if 'full_product_name' in vals and vals.get('full_product_name'):
                if line.full_product_name != vals['full_product_name']:
                    _logger.info(f"  - CORRIGIENDO Line {line.id}: '{line.full_product_name}' -> '{vals['full_product_name']}'")
                    line.full_product_name = vals['full_product_name']
        
        _logger.info("Final:")
        for line in lines:
            _logger.info(f"  - Line {line.id}: full_product_name = '{line.full_product_name}'")
        _logger.info("=" * 80)
        
        return lines
