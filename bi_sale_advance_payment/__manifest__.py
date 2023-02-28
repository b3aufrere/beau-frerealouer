# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Advance Down Payment on Sales Order',
    'version': '16.0.0.0',
    'category': 'Sales',
    'summary': 'Sale Down payment for sales order advance payment sale advance payment sale order advance payment for sales advance payment for sale order down payment advance down payment for sale order add advance payment from sales add down payment from sales payment',
    'description': """

        Sale Order Advance Payment in odoo,
        Make an Advance Payment from Sale Order in odoo,
        Advance Payment in odoo,
        Advance Payments will be Listed in Payment Advance Tab in odoo.
        Advance Payment Wizard in odoo,
        Outstanding Credit balance in odoo,

    """,
    'author': 'BrowseInfo',
    "price": 9,
    "currency": 'EUR',
    'website': 'https://www.browseinfo.in',
    'depends': ['sale_management', 'account', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/advance_payment_views.xml',
        'views/sale_views.xml',
    
    ],
    'license':'OPL-1',
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url': 'https://youtu.be/dzUb1AJt7o0',
    "images": ['static/description/Banner.gif'],
}
