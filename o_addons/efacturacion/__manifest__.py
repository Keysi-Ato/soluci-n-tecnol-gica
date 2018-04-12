# -*- coding: utf-8 -*-
{
    'name': "Facturación Electrónica para Perú",

    'summary': """
        Generación de Documento XML para Facturación Electrónica

        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','purchase','account','odoope_einvoice_base','odoope_ruc_validation','odoope_toponyms','backend_theme_v10','web_responsive'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'data/account_journal.xml',
        'data/sequences.xml'
    ],
    'external_dependencies':{"python":['cryptography','ipaddress',"signxml","cffi","pytesseract","bs4","suds"]},
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

#docker run -p 8150:8069 -v /addons_odoo/11.0:/mnt/extra-addons -v fullstackDataOdoo:/var/lib/odoo --name fullstackodoo11 --link fullstackdb:db odoo:11.0