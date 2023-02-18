# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Helpdesk Support Ticket with CRM',
    'version': '16.0.0.0',
    'category': 'Helpdesk',
    'summary': 'CRM Helpdesk ticket with CRM helpdesk support lead helpdesk ticket CRM support ticket with CRM lead support ticket CRM ticket helpdesk with CRM support ticket website helpdesk ticket all in one helpdesk all on one support all helpdesk pipeline helpdesk',
    'description': """

        Manage CRM With Helpdesk in odoo,
        CRM Helpdesk Ticket in odoo,
        Generate CRM Lead from Ticket in odoo,
        Generate Ticket from CRM Lead in odoo,
        Helpdesk Ticket in odoo,
        CRM Lead in odoo,
        CRM Lead Smart Button in odoo,
        Ticket Smart Button in odoo,

    """,
    'author': 'BrowseInfo',
    "price": 10,
    "currency": 'EUR',
    'website': 'https://www.browseinfo.in',
    'depends': ['base', 'bi_website_support_ticket', 'crm'],
    'data': [
        'security/sample_security.xml',
        'views/models_view.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'live_test_url': 'https://youtu.be/KSIziFwXPb0',
    "images": ['static/description/Banner.gif'],
}
