from odoo import models

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    def _load_pos_data_fields(self, config_id):
        """Agregar campos personalizados para cargar en el POS"""
        fields = super()._load_pos_data_fields(config_id)
        fields.extend(['account_balance', 'account_credit_limit'])
        return fields
