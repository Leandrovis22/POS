{
    'name': 'Cuenta Corriente Simple',
    'version': '18.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Sistema simple de cuenta corriente para clientes sin contabilidad',
    'description': """
        Permite manejar cuentas corrientes de clientes:
        - Acumulación de deuda
        - Pagos parciales y totales
        - Vista de saldos
        - Integración con POS
    """,
    'depends': ['point_of_sale', 'sale', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/pos_payment_method_data.xml',
        'views/customer_account_views.xml',
        'views/res_partner_views.xml',
        'views/pos_assets.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'cuenta_corriente_simple/static/src/js/pos_customizations.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
