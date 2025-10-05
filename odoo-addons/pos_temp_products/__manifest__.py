# -*- coding: utf-8 -*-
{
    'name': 'POS Temporary Products',
    'summary': 'Agregar productos temporales en el Punto de Venta desde un botón junto al buscador',
    'version': '19.0.1.0.7',
    'category': 'Point of Sale',
    'author': 'Custom',
    'license': 'LGPL-3',
    'depends': ['point_of_sale'],
    'data': [
        'data/product_data.xml',
        'views/pos_config_views.xml',
        'views/pos_assets.xml',
    ],
    'installable': True,
    'application': False,
}
