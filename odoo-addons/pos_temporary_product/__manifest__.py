{
    'name': 'POS Temporary Product',
    'version': '1.0.0',
    'summary': 'Permite agregar productos temporales en el POS',
    'description': 'Agrega un botón en el POS para crear productos temporales únicos por orden, sin inventario.',
    'author': 'Leandrovis22',
    'category': 'Point of Sale',
    'license': 'LGPL-3',
    'depends': ['point_of_sale'],
    'data': [
        'data/product_data.xml',
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