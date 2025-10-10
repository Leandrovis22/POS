# -*- coding: utf-8 -*-
from odoo import models


class PosOrderReport(models.AbstractModel):
    _name = 'report.pos_customer_credit.report_pos_order_credit_document'
    _description = 'Reporte de Orden POS con Saldo'

    def _get_report_values(self, docids, data=None):
        """Prepara los valores para el reporte"""
        orders = self.env['pos.order'].browse(docids)
        
        return {
            'doc_ids': docids,
            'doc_model': 'pos.order',
            'docs': orders,
            'data': data,
        }
