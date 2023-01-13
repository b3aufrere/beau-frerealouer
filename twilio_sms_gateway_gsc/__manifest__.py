# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#################################################################################
# Author      : Grow Consultancy Services (<https://www.growconsultancyservices.com/>)
# Copyright(c): 2021-Present Grow Consultancy Services
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
#################################################################################
{
    # Application Information
    'name': 'Odoo Twilio SMS Gateway',
    'version': '16.1.0.0',
    'category': 'Tools',
    'license': 'OPL-1',
    
    # Summary: Short
    # Description: Can big
    'summary': """
        Odoo Twilio SMS Gateway helps you integrate & manage Twilio Acct. operations from Odoo. These apps Save your 
        time, Resources, Effort, and Avoid manually manage multiple Twilio Acct(s) to boost your business marketing 
        with this connector.
    """,
    'description': """
        Odoo Twilio SMS Gateway helps you integrate & manage Twilio Account operations from Odoo. These apps Save your 
        time, Resources, Effort, and Avoid manually manage multiple Twilio Accounts to boost your business marketing 
        with this connector.
    """,
    
    # Author Information
    'author': 'Grow Consultancy Services',
    'maintainer': 'Grow Consultancy Services',
    'website': 'http://www.growconsultancyservices.com',
    
    # Application Price Information
    'price': 55,
    'currency': 'EUR',

    # Dependencies
    'depends': ['base', 'mail', 'sale_management', 'stock'],
    
    # Views
    'data': [ 
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/twilio_sms_account_view.xml',
        'wizard/twilio_sms_template_preview_views.xml',
        'views/twilio_sms_template_view.xml',
        'data/ir_sequence.xml',
        'views/twilio_sms_send_view.xml',
        'views/twilio_sms_groups_view.xml',
        'views/twilio_sms_log_history.xml'
        #'views/'
        #'wizard/'
    ],
    
    # Application Main Image    
    'images': ['static/description/app_profile_image.jpg'],

    # Technical
    'installable': True,
    'application' : True,
    'auto_install': False,
    'active': False,
}
