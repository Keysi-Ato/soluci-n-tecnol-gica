# -*- coding: utf-8 -*-
{
    'name': "Addon - Contabilidad: Resumen diario de boletas de venta",

    'summary': """
        
    """,

    'description': """
        Adiciona opción 'Resumen Diario - BV'
        Listado de resúmenes enviados a SUNAT
    """,

    'author': "KND SAC",
    'website': "http://www.knd.pe",

    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','account'],

    # always loaded
    'data': [
        'views/resumen_menu.xml',
        'views/resumen_view.xml',
        'views/comunicacion_menu.xml',
        'views/comunicacion_view.xml'
    ],
}