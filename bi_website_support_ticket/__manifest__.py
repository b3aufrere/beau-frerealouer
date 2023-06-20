# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "Website Helpdesk Support Ticket in Odoo",
    'version': "16.0.0.0",
    'author': "BrowseInfo",
    'category': "Website",
    'license': 'OPL-1',
    'summary': 'Customer Helpdesk Support Ticket website support ticket Website Help Desk Support Online ticketing system for customer support service desk customer supporting Support Ticketing support Issue tracking system website ticket service request helpdesk ticket',
    'description': '''A helpdesk / support ticket system for your website
    support management from website
    website support ticket
    website helpdesk management
    Support system for your website
    website support management
    submit support request
    Website Helpdesk Support Ticket for Customer
    support form
    technical support
    tech support
    administration
    receptionist
    customer support
    service desk
    Helpdesk Support Ticket
    Helpdesk Ticket
    Help desk Ticket
    request management 
    issue tracking system
     help desk or 
     call center
     Website Help desk Support
     Website tech Support
     service request
      customer services
      Customer support
      Remote support
This Odoo apps almost contain everything you need for Service Desk, 
Technical support team, Call center management, Issue ticketing system which include issue tracking, 
billing payment, tech support portal, service request with timesheet to be managed in Odoo project management app. 
Website customer helpdesk support Ticketing System is used for give customer an interface where he/she can send support ticket request 
and attach documents from website.Support ticket will send by email to customer and admin. 
for Online ticketing system for customer support in Odoo Support. Also its allow to create invoice 
easily from timesheet logged for the project issue/helpdesk support ticketing system. 
Customer can view their ticket from the website portal and easily see stage of the reported ticket also 
customer can communicate with help-desk support team from website communication option.
    Help Desk Reporting Systems
    Ticketing Systems
    Ticket Systems
    Ticket support
    website support ticket
    website issue
    website project issue
    website crm management
    website ticket handling
    support management
    Website Help desk Support ticket
    support ticket
    helpdesk request
    odoo service desk
    customer service

    odoo helpdesk  
    website support ticket
    support ticket 
    helpdesk support ticket
    Online ticketing system for customer support
    Help Desk Ticketing System
    support Help Desk Ticketing System
    support HelpDesk Ticketing System
    support Ticketing System
    project support, crm support, online support management, online support, support product, 
    support services, issue support, fix issue, raise ticket by website, 
    raise support ticket by website, view support request, display support on website, 
    
        

        ''',
    'price': 27,
    'currency': "EUR",
    'depends': ['base_setup',
                'sales_team', 
                 'mail', 
                 'utm' ,
                 'digest',
                 'phone_validation',
                 'sale_management', 
                 'project', 
                 'website', 
                 'bi_subtask',
                 'attachment_indexation',
                 'hr_timesheet_attendance'],    
    'data': [
        'security/website_support_security.xml',    
        'security/ir.model.access.csv',
        'data/support_ticket_stage.xml',
        'views/res_config_setting.xml',
        'views/support_stage.xml',
        'views/support_team.xml',
        'views/task_wizard.xml',   
        'views/support_ticket_stage.xml',
        'views/support_ticket_type.xml',
        'views/support_ticket.xml',
        'views/website_support_templates.xml',
        'report/support_ticket_report_view.xml',
    ],
    'demo': [],
    'live_test_url' : "https://youtu.be/i3J4aZKfEvE",
    "website" : "https://www.browseinfo.in",
    'installable': True,
    'auto_install': False,
    "images":['static/description/Banner.gif'],
     'assets':{
        'web.assets_frontend':[
        'bi_website_support_ticket/static/src/js/ticket_priority.js',
        ]
    },
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
