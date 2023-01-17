# -*- coding: utf-8 -*-
{
    'name': 'Beau-frere a louer Workflow',
    'version': '16.0.0.0.0',
    'license': 'OPL-1',
    
    'author': 'Kamel Benchehida',
    'website': 'https://www.fiverr.com/kamelbenchehida',

    'depends': ['base', 'contacts', 'hr', 'crm', 'sale_project', 'sale_crm', 'industry_fsm_report'],
    
    'data': [ 
        'security/ir.model.access.csv',

        'views/entreprise.xml',
        'views/division.xml',
        'views/territory.xml',
        'views/hr_employee.xml',
        'views/crm_lead.xml',
        'views/x_project_task_worksheet_template_2.xml'
    ],
    
    'installable': True,
    'application' : True,
    'auto_install': False,
}
