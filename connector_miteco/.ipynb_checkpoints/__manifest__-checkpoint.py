# -*- coding: utf-8 -*-

{
    'name': "Send2Mapama",

    'summary': """
        Modulo para enviar Di's generados al Servidor Mapama""",

    'description': """
        Modulo para enviar Di's generados al Servidor Mapama
    """,

    'author': "Pedro BañosGuirao",
    'website': "https://ingenieriacloud.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '1.',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/view_envia_mapama.xml',
        #'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'installable': True,
    'application': True,
    'auto_install': False,
}