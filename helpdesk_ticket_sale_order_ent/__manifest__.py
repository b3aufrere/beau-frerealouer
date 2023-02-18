# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sales Quote from Helpdesk Ticket',
    'price': 59.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'version': '6.2.4',
    'category' : 'Sales/Sales',
    'summary': """Allows your helpdesk team to create sales quotes from helpdesk ticket form view.""",
    'description': """
        Helpdesk Ticket Integrate with Sales Application
        Sales Quote from Helpdesk Ticket
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/helpdesk_ticket_sale_order_ent/165',#'https://youtu.be/U-joU2U1psE',
    'depends': [
        'sale',
        'helpdesk',
                ],
    'data':[
        'security/ir.model.access.csv',
        'views/account_move_view.xml',
        'views/helpdesk_ticket_from_view.xml',
        'views/sale_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
