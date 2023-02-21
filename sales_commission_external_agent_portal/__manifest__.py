# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sales Commission Web Portal for Customer',
    'price': 59.0,
    'version': '7.2.4',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This module allow you view Sale Commision Worksheet and Sale Commission Lines.""",
    'description': """
Sales Commission External Agent Portal
This module allow you view Sale Commision Worksheet and Sale Commission Lines.
Sales Commission by Sales/Invoice/Payment
Sales Commission to Internal Users and External Partners
sales Commission
sale_commission
sales_Commission
sale Commission
sales Commissions
sales order Commission
order Commission
sales person Commission
sales team Commission
sale team Commission
sale person Commission
team Commission
Commission
sales order on Commission
invoice on Commission
payment on Commission
Commission invoice
Commission vendor invoice
sales Commision
Commission sales user invoice
incentive
sales incentive
sales bonus
bonus
commission portal
customer portal sales commission
portal commission
sales portal
sales commission portal
web sales commission
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url' : 'https://probuseappdemo.com/probuse_apps/sales_commission_external_agent_portal/1037',#'https://youtu.be/TIEyDKbjC9g',
    'category': 'Sales',
    'depends': [
                'sales_commission_external_user',
                'portal',
                # 'website',
                ],
    'data':[
        'views/commission_template.xml',
        'views/commission_line_template.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
