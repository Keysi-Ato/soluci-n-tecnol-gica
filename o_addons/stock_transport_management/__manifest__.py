# -*- coding: utf-8 -*-
#, 'report_xlsx' falta
#https://apps.odoo.com/apps/modules/10.0/stock_transport_management/
{
    'name': "Stock Transport Management",
    'version': '10.0.2.0.0',
    'summary': """Manage Stock Transport Management With Ease""",
    'description': """This Module Manage Transport Management Of Stocks""",
    'author': "Cybrosys Techno Solutions",
    'company': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'category': 'Warehouse',
    'depends': ['base', 'sale', 'stock','odoope_einvoice_base'],
    'data': [
        #'security/ir.model.access.csv',
        'views/transport_vehicle_view.xml',
        #'views/transport_vehicle_status_view.xml',
        #'views/transportation_sale_order_view.xml',
        'views/transport_factu_venta_view.xml',
        #'views/transport_wizard_view.xml',
        'views/transport_transportista_view.xml',
        #'views/transport_conductor_view.xml',
        #'views/transport_report.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
