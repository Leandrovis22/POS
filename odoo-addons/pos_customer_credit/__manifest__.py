# -*- coding: utf-8 -*-
{
    'name': 'POS Customer Credit (Cuenta Corriente)',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Gestión de cuenta corriente para clientes en POS',
    'description': """
        Módulo de Cuenta Corriente para POS
        ====================================
        
        Características principales:
        * Compras a crédito sin límite por defecto
        * Pago combinado (efectivo + cuenta corriente)
        * Modificación de órdenes (agregar/quitar productos)
        * Ajustes automáticos de inventario
        * Vista detallada de deuda por cliente
        * Vista de productos actuales por compra
        * Popup en POS para ver saldo y movimientos
        * Registrar pagos directamente
        * Generación de PDF con saldo actual
        * Facturación opcional (no afecta saldo)
        * Validaciones inteligentes según tipo de pago
    """,
    'author': 'Tu Empresa',
    'website': 'https://www.tuempresa.com',
    'license': 'LGPL-3',
    'depends': [
        'point_of_sale',
        'account',
        'sale',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/payment_method_data.xml',
        'views/res_partner_views.xml',
        'views/pos_order_views.xml',
        'views/pos_credit_movement_views.xml',
        'views/pos_config_views.xml',
        'views/pos_payment_method_views.xml',
        'views/menus.xml',
        'report/pos_order_credit_report.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_customer_credit/static/src/app/app.js',
            'pos_customer_credit/static/src/app/components/customer_credit_button/customer_credit_button.js',
            'pos_customer_credit/static/src/app/components/customer_credit_button/customer_credit_button.xml',
            'pos_customer_credit/static/src/app/components/popups/customer_credit_popup/customer_credit_popup.js',
            'pos_customer_credit/static/src/app/components/popups/customer_credit_popup/customer_credit_popup.xml',
            'pos_customer_credit/static/src/app/components/popups/customer_credit_popup/customer_credit_popup.css',
            'pos_customer_credit/static/src/app/components/payment_screen/payment_screen_extension.js',
            'pos_customer_credit/static/src/app/models/pos_order_extension.js',
            'pos_customer_credit/static/src/app/models/pos_store_extension.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
