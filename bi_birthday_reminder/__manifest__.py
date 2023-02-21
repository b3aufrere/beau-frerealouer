# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name' : "Send Customer Birthday Wishes",
    'version' : "16.0.0.2",
    'category' : "Extra Tools",
    'license': 'OPL-1',
    'summary': 'Send Birthday Greetings Email to Partner/Customer',
    'description' : '''
             Module to send an Email to customer on Birthday.
			send birthday wishes to customer, birthday wishes email to customer, Birthday Reminder email, Birthday Greetings email to customer. send birthday wishes to Partner, birthday wishes email to Partner, Birthday Reminder email, Birthday Greetings email to Partner. 
    ''',
    "author": "BrowseInfo",
    'website': 'https://www.browseinfo.in',
    'depends' : ['account'],
    'data': [
             'views/res_partner_view.xml',
             'views/birthday_reminder_cron.xml',
             'edi/birthday_reminder_action_data.xml'
             ],
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/zD25E-rl4kQ',
	"images":['static/description/Banner.gif'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
