# -*- coding: utf-8 -*-
{
    'name': 'POS Temporary Products',
    'summary': 'Agregar productos temporales en el Punto de Venta desde un botón junto al buscador',
    'version': '19.0.1.0.10',
    'category': 'Point of Sale',
    'author': 'Custom',
    'license': 'LGPL-3',
    'depends': ['point_of_sale'],
    'data': [
        'data/product_data.xml',
        'views/pos_config_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_temp_products/static/src/js/config_fields_patch.js',
            'pos_temp_products/static/src/js/temp_popup.js',
            'pos_temp_products/static/src/js/temp_product_handler.js',
            'pos_temp_products/static/src/js/add_temp_button.js',
            'pos_temp_products/static/src/js/navbar_patch.js',
            'pos_temp_products/static/src/js/orderline_patch.js',
            'pos_temp_products/static/src/scss/pos_temp.scss',
        ],
        'point_of_sale.assets_qweb': [
            'pos_temp_products/static/src/xml/templates.xml',
        ],
    },
    'installable': True,
    'application': False,
}
