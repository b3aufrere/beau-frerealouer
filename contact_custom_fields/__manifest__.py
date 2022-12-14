# -*- coding: utf-8 -*-
{
    'name': "contact_custom_fields",

    'summary': """
        Custom field in contact""",

    'description': """
        Custom fields in contact module
    """,

    'author': "Zoubida Salah",
    

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    #    'views/templates.xml',
    ],
    # only loaded in demonstration mode
    #'demo': [
    #    'demo/demo.xml',
    #],
}
