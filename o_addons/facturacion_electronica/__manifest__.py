# -*- coding: utf-8 -*-
{
    "name": "Facturación Electrónica - Perú",
    "summary": """
        Generación de documentos electrónicos para envío a SUNAT.
        Facturas, boletas, notas de crédito y notas de débito. Comunicación de baja y Resumen de boletas.
        Formato UBL - 2.1
        """,
    "description": """
        Este módulo permite facturar electrónicamente.
    """,
    "author": "KND S.A.C.",
    "website": "http://www.knd.pe",
    "category": "Uncategorized",
    "version": "0.1",
    "depends": [
        "base",
        "sale",
        "account",
        "odoope_einvoice_base",
        "odoope_ruc_validation",
        "odoope_toponyms",
        "backend_theme_v10",
        "web_responsive",
    ],
    "data": [
        "views/views.xml",
        "views/views_stock_picking.xml",
        "views/print_reportes_contabilidad.xml",
        "views/view-activos.xml",
        "data/account_journal.xml",  #falta
        "data/sequences.xml",
    ],
    "external_dependencies": {
        "python": [
            "cryptography",
            "ipaddress",#instalado
            "signxml",# instalado
            "cffi",
            "pytesseract",#instalado 
            "bs4",
            "suds",
        ]
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}#https://poncesoft.blogspot.com/2018/04/instalacion-odoo-11-con-dockers.html
#https://github.com/chafarleston/odooadons  
#sudo pip3 install utils
# contenedor 6ce2d2f851a3
#http://puntotron.com/2018/04/10/instalar-odoo-11-y-facturacion-electronica-con-modulos-de-dansanti/

#transporte http://ayuda.trescloud.com/hc/es/articles/224358267-Generar-Gu%C3%ADas-de-Remisi%C3%B3n-en-OPENERP
#https://repositoriotec.tec.ac.cr/bitstream/handle/2238/11031/propuesta_diseno_software_facturacion_electronica.pdf?sequence=1&isAllowed=y