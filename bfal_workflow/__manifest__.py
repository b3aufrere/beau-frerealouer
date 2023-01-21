# -*- coding: utf-8 -*-
{
    'name': 'Beau-frere a louer Workflow',
    'version': '16.0.0.0.0',
    'license': 'OPL-1',
    
    'author': 'Kamel Benchehida',
    'website': 'https://www.fiverr.com/kamelbenchehida',

    'depends': ['base', 'contacts', 'hr', 'crm', 'sale_project', 'sale_crm', 'sales_team'],
    
    'data': [ 
        'security/ir.model.access.csv',
        'data/mail_template_accept_service.xml',

        'views/entreprise.xml',
        'views/division.xml',
        'views/territory.xml',
        'views/hr_employee.xml',
        'views/crm_lead.xml',
    ],
    
    'installable': True,
    'application' : True,
    'auto_install': False,
}
