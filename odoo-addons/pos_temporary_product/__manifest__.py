{
    'name': 'POS Temporary Product',
    'version': '1.0.0',
    'summary': 'Permite agregar productos temporales en el POS',
    'description': 'Agrega un botón en el POS para crear productos temporales únicos por orden, sin inventario.',
    'author': 'Leandrovis22',
    'category': 'Point of Sale',
    'license': 'LGPL-3',
    'depends': ['point_of_sale'],
    # Compatible con Odoo 18.0 y 19.0
    'installable': True,
    'application': False,
    'auto_install': False,
    'data': [
        'data/product_data.xml',
        'views/pos_order_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_temporary_product/static/src/**/*.js',
            'pos_temporary_product/static/src/**/*.xml',
        ],
    },
    'installable': True,
    'application': False,
}